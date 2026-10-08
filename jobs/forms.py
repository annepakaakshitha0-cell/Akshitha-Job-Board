from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
import re
from .models import Company, JobPosting, Candidate, JobApplication


class JobApplicationForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Jane Doe',
            'required': 'required',
            'id': 'applicant-full-name'
        }),
        label="Full Name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. jane.doe@example.com',
            'required': 'required',
            'id': 'applicant-email'
        }),
        label="Email Address"
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +1 (555) 234-5678',
            'required': 'required',
            'id': 'applicant-phone'
        }),
        label="Phone Number"
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://github.com/janedoe or https://linkedin.com/in/...',
            'id': 'applicant-portfolio'
        }),
        label="Portfolio / GitHub / LinkedIn URL (Optional)"
    )
    skills = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Python, Django, PostgreSQL, Docker, AWS',
            'required': 'required',
            'id': 'applicant-skills'
        }),
        label="Your Key Skills"
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell the hiring team why you are a great fit for this position...',
            'required': 'required',
            'id': 'applicant-cover-letter'
        }),
        label="Cover Letter / Note to Hiring Manager"
    )

    def __init__(self, *args, job=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = job

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
        if not cleaned.isdigit() or len(cleaned) < 7:
            raise ValidationError("Please provide a valid phone number with at least 7 digits.")
        return phone

    def clean_skills(self):
        skills = self.cleaned_data.get('skills', '').strip()
        if len(skills) < 2:
            raise ValidationError("Please enter your skills (separated by commas).")
        return skills

    def clean_cover_letter(self):
        cover = self.cleaned_data.get('cover_letter', '').strip()
        if len(cover) < 15:
            raise ValidationError("Please provide a short cover note (at least 15 characters).")
        return cover

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email and self.job:
            # Prevent duplicate application by candidate email for this specific job
            try:
                candidate = Candidate.objects.get(email__iexact=email.strip())
                if JobApplication.objects.filter(job=self.job, candidate=candidate).exists():
                    raise ValidationError(
                        f"You have already submitted an application for '{self.job.title}' with the email {email}."
                    )
            except Candidate.DoesNotExist:
                pass
        return cleaned_data

    def save(self, job=None):
        target_job = job or self.job
        if not target_job:
            raise ValueError("A job must be provided to save the application.")

        email = self.cleaned_data['email'].strip().lower()
        candidate, _ = Candidate.objects.update_or_create(
            email=email,
            defaults={
                'full_name': self.cleaned_data['full_name'].strip(),
                'phone': self.cleaned_data['phone'].strip(),
                'portfolio_url': self.cleaned_data.get('portfolio_url') or None,
                'skills': self.cleaned_data['skills'].strip(),
            }
        )

        application = JobApplication.objects.create(
            job=target_job,
            candidate=candidate,
            cover_letter=self.cleaned_data['cover_letter'].strip(),
            status='Applied'
        )
        return application


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['company', 'title', 'job_type', 'required_skills', 'salary_range', 'description', 'active']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lead Django Engineer'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'required_skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, AWS, React'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '$120,000 - $150,000 / yr'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'website', 'location', 'logo_url', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acme Technologies'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://acme.io'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA or Remote'}),
            'logo_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/... or leave blank for auto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ApplicationStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
