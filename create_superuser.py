import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from jobs.models import Company, JobPosting, Candidate, JobApplication

def ensure_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@talentsphere.io')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin@12345')

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")

    # Also ensure a friendly recruiter user exists
    if not User.objects.filter(username='recruiter').exists():
        u = User.objects.create_user(username='recruiter', email='recruiter@talentsphere.io', password='Password@123')
        u.is_staff = True
        u.save()
        print("Recruiter staff account created (username: recruiter, password: Password@123).")


def seed_demo_data():
    if Company.objects.exists() and JobPosting.objects.exists():
        print("Demo data already populated.")
        return

    print("Populating initial demo ATS data...")

    # 1. Companies
    companies_data = [
        {
            "name": "CloudScale Systems",
            "website": "https://cloudscale.io",
            "location": "San Francisco, CA (Remote Friendly)",
            "logo_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=128&auto=format&fit=crop&q=80",
            "description": "Next-generation distributed cloud infrastructure and observability platforms for Fortune 500 enterprises."
        },
        {
            "name": "Nexus AI Labs",
            "website": "https://nexusai.tech",
            "location": "New York, NY",
            "logo_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
            "description": "Building state-of-the-art multimodal AI models and developer tooling for automated code generation."
        },
        {
            "name": "FinWave Technologies",
            "website": "https://finwave.co",
            "location": "Austin, TX (Hybrid)",
            "logo_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=128&auto=format&fit=crop&q=80",
            "description": "Real-time payment orchestration and high-frequency risk modeling engine for global commerce."
        },
        {
            "name": "HealthPulse Digital",
            "website": "https://healthpulse.care",
            "location": "Boston, MA",
            "logo_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=128&auto=format&fit=crop&q=80",
            "description": "HIPAA-compliant telemedicine platforms connecting millions of patients with world-class specialists."
        },
        {
            "name": "Veloce Robotics",
            "website": "https://velocerobotics.com",
            "location": "Seattle, WA (On-site)",
            "logo_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=128&auto=format&fit=crop&q=80",
            "description": "Autonomous warehouse robotics and computer vision systems powering the future of supply chains."
        }
    ]

    company_objs = {}
    for c_data in companies_data:
        comp, _ = Company.objects.get_or_create(
            name=c_data["name"],
            defaults=c_data
        )
        company_objs[c_data["name"]] = comp

    # 2. Job Postings
    jobs_data = [
        {
            "company": company_objs["CloudScale Systems"],
            "title": "Senior Python / Django Backend Engineer",
            "job_type": "Full-time",
            "required_skills": "Python, Django, PostgreSQL, Redis, Docker, REST APIs",
            "salary_range": "$135,000 - $165,000 / yr",
            "description": """We are seeking an experienced Backend Engineer to scale our core API services and distributed job processing pipelines.

Responsibilities:
• Architect robust, high-throughput RESTful endpoints using Django and Django REST framework.
• Optimize SQLite and PostgreSQL database queries, migrations, and caching tiers.
• Collaborate with frontend and DevOps engineers to deploy containerized microservices on AWS and Render.
• Mentor junior software engineers and promote automated testing best practices.

Requirements:
• 4+ years of professional experience with Python and Django.
• Strong foundation in relational database design, indexing, and ORM query optimization.
• Solid grasp of asynchronous workflows (Celery, Redis) and clean API architecture.
• Excellent written communication and problem-solving skills.""",
            "active": True
        },
        {
            "company": company_objs["Nexus AI Labs"],
            "title": "Full-Stack AI Application Developer",
            "job_type": "Remote",
            "required_skills": "Python, Django, JavaScript, React, TailwindCSS, OpenAI API",
            "salary_range": "$125,000 - $155,000 / yr",
            "description": """Nexus AI is looking for a versatile Full-Stack Engineer to build interactive dashboards and user interfaces that harness our generative foundation models.

Responsibilities:
• Develop dynamic web applications using Django backend and responsive frontend technologies.
• Integrate LLM streaming endpoints with sub-second latency for enterprise users.
• Build intuitive workflow visualization and prompt engineering sandboxes.

Qualifications:
• 3+ years experience across modern Python frameworks and JavaScript frontend libraries.
• Experience connecting LLM APIs or vector databases.
• Strong aesthetic sense for clean UI/UX and micro-interactions.""",
            "active": True
        },
        {
            "company": company_objs["FinWave Technologies"],
            "title": "Cloud DevOps & Infrastructure Specialist",
            "job_type": "Full-time",
            "required_skills": "Docker, Kubernetes, AWS, Terraform, CI/CD, Linux",
            "salary_range": "$140,000 - $175,000 / yr",
            "description": """Join our site reliability team managing 99.999% uptime for mission-critical financial transactions.

Key Duties:
• Maintain automated CI/CD pipelines and infrastructure-as-code deployments.
• Monitor application performance, log aggregation, and system health alerts.
• Harden security configurations, compliance postures, and secrets management.

Requirements:
• Proven track record with container orchestration (Docker/K8s) and cloud platforms.
• Deep understanding of Linux internals, networking protocols, and high-availability setups.""",
            "active": True
        },
        {
            "company": company_objs["HealthPulse Digital"],
            "title": "Frontend UI/UX Web Developer",
            "job_type": "Contract",
            "required_skills": "JavaScript, HTML5, CSS3, Bootstrap 5, Web Accessibility (a11y)",
            "salary_range": "$65 - $85 / hr",
            "description": """Help us craft accessible, patient-centered digital health experiences.

You will:
• Build responsive web components conforming to WCAG 2.1 AA accessibility guidelines.
• Translate high-fidelity Figma mockups into reusable HTML5/Bootstrap 5 templates.
• Perform cross-browser testing and performance optimization.

Ideal Candidate:
• 3+ years hands-on HTML, modern CSS, and JavaScript.
• Deep knowledge of responsive design patterns and semantic markup.""",
            "active": True
        },
        {
            "company": company_objs["Veloce Robotics"],
            "title": "Software Engineering Intern (Summer 2026)",
            "job_type": "Internship",
            "required_skills": "Python, Git, Data Structures, Algorithms, Linux",
            "salary_range": "$35 - $45 / hr",
            "description": """Launch your engineering career with our autonomous robotics team in Seattle!

What you will do:
• Write Python test scripts and telemetry analysis modules for real-world robotic fleets.
• Work alongside senior systems engineers on perception algorithms and simulation environments.
• Present capstone project results to the entire engineering organization.

Requirements:
• Currently pursuing a BS/MS in Computer Science, Software Engineering, or related field.
• Proficient with Python and Linux command-line tools.""",
            "active": True
        },
        {
            "company": company_objs["CloudScale Systems"],
            "title": "Part-Time Technical Documentation & API Writer",
            "job_type": "Part-time",
            "required_skills": "Technical Writing, Markdown, Python, REST APIs, Git",
            "salary_range": "$40 - $55 / hr",
            "description": """Maintain and elevate our developer documentation, API tutorials, and architectural guides.

Scope:
• Write comprehensive guides for developer onboarding and API integration.
• Review code samples in Python and curl for accuracy.
• Keep release notes and changelogs up-to-date with sprint cycles.""",
            "active": True
        }
    ]

    job_objs = []
    for j_data in jobs_data:
        job, _ = JobPosting.objects.get_or_create(
            company=j_data["company"],
            title=j_data["title"],
            defaults=j_data
        )
        job_objs.append(job)

    # 3. Candidates
    candidates_data = [
        {
            "full_name": "Alex Morgan",
            "email": "alex.morgan@example.com",
            "phone": "+1 555-234-5678",
            "portfolio_url": "https://github.com/alexmorgan-dev",
            "skills": "Python, Django, PostgreSQL, Docker, AWS, Celery"
        },
        {
            "full_name": "Sarah Connor",
            "email": "sarah.connor@example.com",
            "phone": "+1 555-876-5432",
            "portfolio_url": "https://linkedin.com/in/sarahconnor-tech",
            "skills": "JavaScript, React, CSS3, Bootstrap 5, Figma"
        },
        {
            "full_name": "Marcus Vance",
            "email": "marcus.vance@example.com",
            "phone": "+1 555-345-6789",
            "portfolio_url": "https://marcusvance.dev",
            "skills": "Kubernetes, Docker, Terraform, Linux, CI/CD, Python"
        },
        {
            "full_name": "Elena Rostova",
            "email": "elena.rostova@example.com",
            "phone": "+1 555-901-2345",
            "portfolio_url": "https://github.com/erostova",
            "skills": "Python, Machine Learning, PyTorch, SQL, Pandas"
        },
        {
            "full_name": "David Kim",
            "email": "david.kim@example.com",
            "phone": "+1 555-456-7890",
            "portfolio_url": "https://davidkim-portfolio.vercel.app",
            "skills": "Python, Django, FastAPI, React, TypeScript"
        },
        {
            "full_name": "Chloe Bennett",
            "email": "chloe.bennett@example.com",
            "phone": "+1 555-678-1234",
            "portfolio_url": "https://github.com/chloebennett",
            "skills": "Technical Writing, Python, OpenAPI, Git, Markdown"
        }
    ]

    candidate_objs = {}
    for c in candidates_data:
        cand, _ = Candidate.objects.get_or_create(
            email=c["email"],
            defaults=c
        )
        candidate_objs[c["email"]] = cand

    # 4. Applications across the 4 Stages
    applications_data = [
        # Shortlisted
        {
            "job": job_objs[0], # Senior Python / Django
            "candidate": candidate_objs["alex.morgan@example.com"],
            "cover_letter": "I have over 5 years building scalable web architectures with Django and PostgreSQL. Having led backend rewrites handling millions of daily hits, I am confident I can make an immediate impact on CloudScale's core platforms.",
            "status": "Shortlisted"
        },
        # Under Review
        {
            "job": job_objs[1], # Full-Stack AI
            "candidate": candidate_objs["david.kim@example.com"],
            "cover_letter": "Combining modern Django APIs with fast interactive React frontends is my primary expertise. I have integrated multiple LLM completions and streaming endpoints in production systems.",
            "status": "Under Review"
        },
        # Applied
        {
            "job": job_objs[3], # Frontend UI/UX
            "candidate": candidate_objs["sarah.connor@example.com"],
            "cover_letter": "I am passionate about clean, intuitive user interfaces and strict accessibility compliance. My experience with Bootstrap 5 and modular CSS enables me to quickly prototype and deliver refined web experiences.",
            "status": "Applied"
        },
        # Shortlisted
        {
            "job": job_objs[2], # Cloud DevOps
            "candidate": candidate_objs["marcus.vance@example.com"],
            "cover_letter": "I specialize in Kubernetes clusters and multi-cloud resilience with Terraform. I would love to bring high-availability rigor to FinWave's financial transaction backplane.",
            "status": "Shortlisted"
        },
        # Under Review
        {
            "job": job_objs[0], # Senior Python
            "candidate": candidate_objs["elena.rostova@example.com"],
            "cover_letter": "My background bridges backend Python web services with high-performance data processing pipelines. Excited about CloudScale's mission.",
            "status": "Under Review"
        },
        # Rejected
        {
            "job": job_objs[4], # Intern
            "candidate": candidate_objs["alex.morgan@example.com"],
            "cover_letter": "Applying to test cross-role pipeline management.",
            "status": "Rejected"
        },
        # Applied
        {
            "job": job_objs[5], # Tech Writer
            "candidate": candidate_objs["chloe.bennett@example.com"],
            "cover_letter": "Clear documentation is the hallmark of great software. I have documented complex REST APIs and generated interactive code references for engineering audiences worldwide.",
            "status": "Applied"
        }
    ]

    for app in applications_data:
        JobApplication.objects.get_or_create(
            job=app["job"],
            candidate=app["candidate"],
            defaults={
                "cover_letter": app["cover_letter"],
                "status": app["status"]
            }
        )

    print("Initial demo data successfully seeded!")

if __name__ == '__main__':
    ensure_superuser()
    seed_demo_data()
