from django.contrib import admin
from .models import Company, JobPosting, Candidate, JobApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('location',)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'salary_range', 'active', 'posted_date', 'application_count')
    list_filter = ('job_type', 'active', 'company')
    search_fields = ('title', 'company__name', 'required_skills')
    list_editable = ('active',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'portfolio_url', 'created_at')
    search_fields = ('full_name', 'email', 'skills')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'status', 'applied_date')
    list_filter = ('status', 'applied_date', 'job__company')
    search_fields = ('candidate__full_name', 'candidate__email', 'job__title', 'job__company__name')
    list_editable = ('status',)
