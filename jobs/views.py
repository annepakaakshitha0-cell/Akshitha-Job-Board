from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.contrib.auth.models import User
import json

from .models import Company, JobPosting, Candidate, JobApplication
from .forms import JobApplicationForm, JobPostingForm, CompanyForm, ApplicationStatusUpdateForm


def job_list(request):
    """
    Active job listing page with real-time and server-side filters.
    Includes keyword, skill, and job type filtering.
    """
    query = request.GET.get('q', '').strip()
    job_type = request.GET.get('job_type', '').strip()
    skill_filter = request.GET.get('skill', '').strip()

    jobs_qs = JobPosting.objects.filter(active=True).select_related('company')

    if query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(company__name__icontains=query) |
            Q(company__location__icontains=query) |
            Q(required_skills__icontains=query)
        )

    if job_type:
        jobs_qs = jobs_qs.filter(job_type=job_type)

    if skill_filter:
        jobs_qs = jobs_qs.filter(required_skills__icontains=skill_filter)

    # Extract all unique popular skills for quick filter tags
    all_jobs = JobPosting.objects.filter(active=True)
    all_skills = set()
    for j in all_jobs:
        for s in j.skills_list:
            all_skills.add(s)
    top_skills = sorted(list(all_skills))[:12]

    # Quick overview metrics
    total_active_jobs = all_jobs.count()
    total_companies = Company.objects.count()
    remote_jobs_count = all_jobs.filter(job_type='Remote').count()

    context = {
        'jobs': jobs_qs,
        'query': query,
        'job_type': job_type,
        'skill_filter': skill_filter,
        'job_types': [choice[0] for choice in JobPosting.JOB_TYPES],
        'top_skills': top_skills,
        'total_active_jobs': total_active_jobs,
        'total_companies': total_companies,
        'remote_jobs_count': remote_jobs_count,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    """
    Job detail page showing company info, job requirements, salary,
    and the application modal trigger.
    """
    job = get_object_or_404(JobPosting.objects.select_related('company'), pk=pk)
    related_jobs = JobPosting.objects.filter(
        active=True,
        company=job.company
    ).exclude(pk=job.pk)[:3]

    if not related_jobs.exists():
        related_jobs = JobPosting.objects.filter(
            active=True,
            job_type=job.job_type
        ).exclude(pk=job.pk)[:3]

    form = JobApplicationForm(job=job)
    context = {
        'job': job,
        'related_jobs': related_jobs,
        'form': form,
    }
    return render(request, 'jobs/job_detail.html', context)


@require_POST
def apply_job(request, pk):
    """
    Application submission workflow.
    Handles standard POST or AJAX submissions.
    Enforces business logic:
    - Candidate validation
    - Duplicate application prevention for the same job
    """
    job = get_object_or_404(JobPosting, pk=pk, active=True)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

    # Support JSON payload or form payload
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            form = JobApplicationForm(data, job=job)
        except Exception:
            return JsonResponse({'success': False, 'errors': {'__all__': ['Invalid JSON format.']}}, status=400)
    else:
        form = JobApplicationForm(request.POST, job=job)

    if form.is_valid():
        application = form.save(job=job)
        success_msg = f"Application submitted successfully for {job.title}! We have recorded your interest."
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': success_msg,
                'application_id': application.id,
                'candidate_name': application.candidate.full_name,
                'job_title': job.title
            })
        messages.success(request, success_msg)
        return redirect('job_detail', pk=job.pk)
    else:
        # Form validation errors
        if is_ajax:
            errors_dict = {}
            for field, errs in form.errors.items():
                errors_dict[field] = [str(e) for e in errs]
            return JsonResponse({'success': False, 'errors': errors_dict}, status=400)

        # Standard form error redirect
        for field, errs in form.errors.items():
            for e in errs:
                messages.error(request, f"{field.replace('_', ' ').capitalize()}: {e}")
        return redirect('job_detail', pk=job.pk)


@staff_member_required(login_url='login')
def recruiter_dashboard(request):
    """
    Recruiter hiring pipeline dashboard.
    Shows applications organized by stages:
    Applied, Under Review, Shortlisted, Rejected.
    Restricted to staff users.
    """
    job_filter = request.GET.get('job_id', '')
    search_query = request.GET.get('search', '').strip()

    applications_qs = JobApplication.objects.select_related('candidate', 'job', 'job__company').all()

    if job_filter and job_filter.isdigit():
        applications_qs = applications_qs.filter(job_id=int(job_filter))

    if search_query:
        applications_qs = applications_qs.filter(
            Q(candidate__full_name__icontains=search_query) |
            Q(candidate__email__icontains=search_query) |
            Q(candidate__skills__icontains=search_query) |
            Q(job__title__icontains=search_query)
        )

    # Separate applications into the four pipeline stages
    applied_apps = applications_qs.filter(status='Applied')
    under_review_apps = applications_qs.filter(status='Under Review')
    shortlisted_apps = applications_qs.filter(status='Shortlisted')
    rejected_apps = applications_qs.filter(status='Rejected')

    total_apps_count = applications_qs.count()
    all_jobs = JobPosting.objects.select_related('company').all()
    active_jobs_count = all_jobs.filter(active=True).count()

    context = {
        'applied_apps': applied_apps,
        'under_review_apps': under_review_apps,
        'shortlisted_apps': shortlisted_apps,
        'rejected_apps': rejected_apps,
        'total_apps_count': total_apps_count,
        'active_jobs_count': active_jobs_count,
        'all_jobs': all_jobs,
        'selected_job_id': job_filter,
        'search_query': search_query,
        'status_choices': [choice[0] for choice in JobApplication.STATUS_CHOICES],
    }
    return render(request, 'jobs/recruiter_dashboard.html', context)


@staff_member_required(login_url='login')
@require_POST
def update_application_status(request, pk):
    """
    Recruiter action: Updates status of an application.
    Supports AJAX or POST redirect.
    """
    application = get_object_or_404(JobApplication, pk=pk)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

    if request.content_type == 'application/json':
        try:
            body = json.loads(request.body)
            new_status = body.get('status')
        except Exception:
            new_status = None
    else:
        new_status = request.POST.get('status')

    valid_statuses = [c[0] for c in JobApplication.STATUS_CHOICES]
    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        msg = f"Updated application status for {application.candidate.full_name} to '{new_status}'."
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': msg,
                'status': new_status,
                'badge_color': application.badge_color,
                'application_id': application.id
            })
        messages.success(request, msg)
    else:
        err_msg = f"Invalid status: '{new_status}'."
        if is_ajax:
            return JsonResponse({'success': False, 'message': err_msg}, status=400)
        messages.error(request, err_msg)

    return redirect('recruiter_dashboard')


@staff_member_required(login_url='login')
def recruiter_create_job(request):
    """Recruiter page to post a new job."""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"New job posting '{job.title}' created successfully!")
            return redirect('recruiter_dashboard')
    else:
        form = JobPostingForm()

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Post a New Job Opportunity',
        'is_edit': False
    })


@staff_member_required(login_url='login')
def recruiter_edit_job(request, pk):
    """Recruiter page to edit an existing job posting."""
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job posting '{job.title}' updated successfully!")
            return redirect('recruiter_dashboard')
    else:
        form = JobPostingForm(instance=job)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'title': f"Edit Job: {job.title}",
        'is_edit': True
    })


@staff_member_required(login_url='login')
def recruiter_toggle_job(request, pk):
    """Toggle job active/inactive status."""
    job = get_object_or_404(JobPosting, pk=pk)
    job.active = not job.active
    job.save()
    status_str = "activated" if job.active else "deactivated"
    messages.info(request, f"Job '{job.title}' was {status_str}.")
    return redirect('recruiter_dashboard')


def candidate_profile_lookup(request):
    """
    Candidate application tracking & management portal.
    Allows candidates to enter their email and view their profile & application statuses.
    """
    email = request.GET.get('email', '').strip().lower()
    candidate = None
    applications = []

    if email:
        try:
            candidate = Candidate.objects.get(email=email)
            applications = candidate.applications.select_related('job', 'job__company').all()
        except Candidate.DoesNotExist:
            messages.warning(request, f"No candidate profile found for email '{email}'.")

    return render(request, 'jobs/candidate_portal.html', {
        'candidate': candidate,
        'applications': applications,
        'searched_email': email,
    })


def login_view(request):
    """Authentication view for recruiter staff login with a 1-click demo login option."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('recruiter_dashboard')
        return redirect('job_list')

    if request.method == 'POST':
        # Check for demo login button click
        if request.POST.get('demo_login') == 'true':
            # Find or create demo staff user
            staff_user = User.objects.filter(is_staff=True).first()
            if not staff_user:
                staff_user = User.objects.create_superuser(
                    username='recruiter_admin',
                    email='recruiter@example.com',
                    password='Password@123'
                )
            login(request, staff_user)
            messages.success(request, f"Welcome, {staff_user.username}! Signed in via Recruiter Demo Access.")
            return redirect('recruiter_dashboard')

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('recruiter_dashboard' if user.is_staff else 'job_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'jobs/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('job_list')
