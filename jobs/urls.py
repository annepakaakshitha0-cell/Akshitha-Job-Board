from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('dashboard/application/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('dashboard/job/new/', views.recruiter_create_job, name='recruiter_create_job'),
    path('dashboard/job/<int:pk>/edit/', views.recruiter_edit_job, name='recruiter_edit_job'),
    path('dashboard/job/<int:pk>/toggle/', views.recruiter_toggle_job, name='recruiter_toggle_job'),
    path('my-applications/', views.candidate_profile_lookup, name='candidate_portal'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
