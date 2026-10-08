from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Company, JobPosting, Candidate, JobApplication
from .forms import JobApplicationForm


class ATSModelAndLogicTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_recruiter',
            password='StaffPassword123!',
            is_staff=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='UserPassword123!'
        )

        # Create sample company
        self.company = Company.objects.create(
            name='Acme Corp',
            website='https://acme.example.com',
            location='Austin, TX',
            description='Innovating widgets since 1990.'
        )

        # Create sample job posting
        self.job = JobPosting.objects.create(
            company=self.company,
            title='Backend Python Developer',
            job_type='Full-time',
            required_skills='Python, Django, SQLite, Docker',
            salary_range='$110,000 - $135,000 / yr',
            description='Join our core backend engineering unit.',
            active=True
        )

        # Create inactive job posting
        self.inactive_job = JobPosting.objects.create(
            company=self.company,
            title='Archived Position',
            job_type='Contract',
            required_skills='Legacy skills',
            salary_range='$50/hr',
            description='Inactive job.',
            active=False
        )

    def test_company_and_job_creation(self):
        self.assertEqual(str(self.company), 'Acme Corp')
        self.assertEqual(str(self.job), 'Backend Python Developer at Acme Corp')
        self.assertEqual(len(self.job.skills_list), 4)
        self.assertIn('Python', self.job.skills_list)

    def test_job_list_view(self):
        response = self.client.get(reverse('job_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Python Developer')
        # Inactive job should not appear in active listing
        self.assertNotContains(response, 'Archived Position')

    def test_job_detail_view(self):
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Python Developer')
        self.assertContains(response, 'Acme Corp')
        self.assertContains(response, '$110,000 - $135,000 / yr')

    def test_application_submission_and_duplicate_prevention(self):
        apply_url = reverse('apply_job', kwargs={'pk': self.job.pk})
        form_data = {
            'full_name': 'Jordan Lee',
            'email': 'jordan.lee@example.com',
            'phone': '+1 (555) 987-6543',
            'portfolio_url': 'https://jordanlee.dev',
            'skills': 'Python, Django, SQL',
            'cover_letter': 'I am thrilled to apply for the Backend Python Developer role at Acme Corp.'
        }

        # 1. First application should succeed
        response = self.client.post(apply_url, data=form_data)
        self.assertEqual(response.status_code, 302) # redirect on standard POST

        # Verify Candidate and JobApplication created
        candidate = Candidate.objects.get(email='jordan.lee@example.com')
        self.assertEqual(candidate.full_name, 'Jordan Lee')
        self.assertEqual(JobApplication.objects.filter(job=self.job, candidate=candidate).count(), 1)
        app = JobApplication.objects.get(job=self.job, candidate=candidate)
        self.assertEqual(app.status, 'Applied')

        # 2. Second application with the same candidate email to the same job MUST BE PREVENTED
        response_dup = self.client.post(apply_url, data=form_data)
        # Should redirect back with error message and NOT create a second application
        self.assertEqual(JobApplication.objects.filter(job=self.job, candidate=candidate).count(), 1)

    def test_ajax_application_submission(self):
        apply_url = reverse('apply_job', kwargs={'pk': self.job.pk})
        form_data = {
            'full_name': 'Taylor Swift',
            'email': 'taylor.swift@example.com',
            'phone': '5551234567',
            'portfolio_url': '',
            'skills': 'Music, Management, Python',
            'cover_letter': 'Excited to apply with over 15 characters of enthusiasm.'
        }

        response = self.client.post(
            apply_url,
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['success'])
        self.assertIn('Application submitted successfully', json_data['message'])

        # Try duplicate via AJAX
        response_dup = self.client.post(
            apply_url,
            data=form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_dup.status_code, 400)
        dup_json = response_dup.json()
        self.assertFalse(dup_json['success'])

    def test_recruiter_dashboard_access_control(self):
        dash_url = reverse('recruiter_dashboard')

        # Anonymous user should be redirected to login
        response_anon = self.client.get(dash_url)
        self.assertEqual(response_anon.status_code, 302)
        self.assertIn(reverse('login'), response_anon.url)

        # Regular non-staff user should be redirected or blocked
        self.client.login(username='regular_user', password='UserPassword123!')
        response_user = self.client.get(dash_url)
        self.assertEqual(response_user.status_code, 302)

        # Staff user should get 200 OK
        self.client.login(username='staff_recruiter', password='StaffPassword123!')
        response_staff = self.client.get(dash_url)
        self.assertEqual(response_staff.status_code, 200)
        self.assertContains(response_staff, 'Applicant Tracking Pipeline')

    def test_status_update_view(self):
        # Create candidate and application
        cand = Candidate.objects.create(
            full_name='Casey Smith',
            email='casey.smith@example.com',
            phone='5551234567',
            skills='Python'
        )
        app = JobApplication.objects.create(
            job=self.job,
            candidate=cand,
            cover_letter='Testing status progression.',
            status='Applied'
        )

        status_url = reverse('update_application_status', kwargs={'pk': app.pk})

        # Staff user updates status to 'Shortlisted'
        self.client.login(username='staff_recruiter', password='StaffPassword123!')
        response = self.client.post(
            status_url,
            data={'status': 'Shortlisted'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, 'Shortlisted')

    def test_candidate_tracking_portal(self):
        portal_url = reverse('candidate_portal')

        # Lookup non-existent email
        response_empty = self.client.get(f"{portal_url}?email=nobody@example.com")
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, "No candidate profile found")

        # Create candidate and application
        cand = Candidate.objects.create(
            full_name='Morgan Freeman',
            email='morgan@example.com',
            phone='5559876543',
            skills='Narration, Python'
        )
        JobApplication.objects.create(
            job=self.job,
            candidate=cand,
            cover_letter='Testing candidate tracking lookup.',
            status='Under Review'
        )

        response_found = self.client.get(f"{portal_url}?email=morgan@example.com")
        self.assertEqual(response_found.status_code, 200)
        self.assertContains(response_found, 'Morgan Freeman')
        self.assertContains(response_found, 'Backend Python Developer')
        self.assertContains(response_found, 'Under Review')
