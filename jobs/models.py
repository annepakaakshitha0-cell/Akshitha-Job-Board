from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, validate_email
import re


class Company(models.Model):
    name = models.CharField(max_length=200, help_text="Company name")
    website = models.URLField(max_length=300, help_text="Official company website")
    location = models.CharField(max_length=200, help_text="Headquarters or location (e.g. San Francisco, CA or Remote)")
    logo_url = models.URLField(max_length=500, blank=True, help_text="Direct URL to company logo image")
    description = models.TextField(blank=True, help_text="Brief company background or mission")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def display_logo(self):
        if self.logo_url:
            return self.logo_url
        # Clean SVG-based fallback avatar
        initial = self.name[:1].upper() if self.name else "C"
        return f"https://ui-avatars.com/api/?name={self.name}&background=6366f1&color=fff&size=128"


class JobPosting(models.Model):
    JOB_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote'),
        ('Internship', 'Internship'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=250, help_text="Position title (e.g. Senior Python Developer)")
    job_type = models.CharField(max_length=50, choices=JOB_TYPES, default='Full-time')
    required_skills = models.CharField(max_length=500, help_text="Comma-separated skills (e.g. Python, Django, REST API, Docker)")
    salary_range = models.CharField(max_length=100, help_text="e.g. $110,000 - $140,000 / yr or $60/hr")
    description = models.TextField(help_text="Detailed job description and responsibilities")
    active = models.BooleanField(default=True, help_text="Active flag indicating if the role is currently open")
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    @property
    def skills_list(self):
        """Returns list of trimmed skills for tags/badges."""
        if not self.required_skills:
            return []
        return [skill.strip() for skill in self.required_skills.split(',') if skill.strip()]

    @property
    def application_count(self):
        return self.applications.count()


class Candidate(models.Model):
    full_name = models.CharField(max_length=200, help_text="Candidate's full legal name")
    email = models.EmailField(unique=True, help_text="Primary email address")
    phone = models.CharField(max_length=30, help_text="Contact telephone number")
    portfolio_url = models.URLField(max_length=300, blank=True, null=True, help_text="GitHub, LinkedIn, or personal website")
    skills = models.CharField(max_length=500, help_text="Comma-separated technical/professional skills")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()
        # Candidate details validation
        if self.email:
            validate_email(self.email)
        if self.phone:
            # Strip spaces, dashes, parentheses
            cleaned_phone = re.sub(r'[\s\-\(\)\+]', '', self.phone)
            if not cleaned_phone.isdigit() or len(cleaned_phone) < 7:
                raise ValidationError({'phone': 'Please provide a valid phone number with at least 7 digits.'})
        if self.portfolio_url:
            URLValidator()(self.portfolio_url)

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    @property
    def skills_list(self):
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(help_text="Candidate's statement of interest and qualifications")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Applied')
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent the same candidate from applying to the same job more than once
        unique_together = ('job', 'candidate')
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title} [{self.status}]"

    @property
    def badge_color(self):
        mapping = {
            'Applied': 'primary',
            'Under Review': 'warning',
            'Shortlisted': 'success',
            'Rejected': 'danger',
        }
        return mapping.get(self.status, 'secondary')
