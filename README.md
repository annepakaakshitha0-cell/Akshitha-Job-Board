# TalentSphere — Job Board & Applicant Tracking System (ATS)

**CAPSTONE PROJECT 4: Django Full-Stack Final Project**

A modern recruitment platform and Applicant Tracking System (ATS) built with Python, Django, Bootstrap 5, SQLite, and WhiteNoise, ready for deployment on Render.

---

## 🌟 Key Features

1. **Job Board & Discovery**:
   - High-aesthetic responsive job cards showing company logos, location, salary range, and job type badges.
   - **Real-Time Client-Side Filtering**: Filter jobs by keyword and skill tags instantly with zero page reload.
   - Server-side fallback search and filtering for query persistence.

2. **Application Submission Workflow**:
   - Embedded Bootstrap 5 application modal.
   - **Client-Side Form Validation**: Real-time validation for email, phone (minimum 7 digits), skills, and cover letter length.
   - **Duplicate Application Prevention**: Business logic strictly blocks candidates from applying to the same job more than once.
   - Supports both standard POST and seamless AJAX submission.

3. **Recruiter ATS Pipeline (Staff Only)**:
   - Dedicated hiring dashboard organized into 4 recruitment stages:
     - 📥 **Applied**
     - ⏳ **Under Review**
     - ⭐ **Shortlisted**
     - ❌ **Rejected**
   - Quick one-click status transitions via AJAX that move candidate cards between stages dynamically.
   - Interactive Candidate Cover Letter viewer modal.
   - Metric overview cards tracking total applications, stages, and active listings.
   - Job posting management (create, edit, toggle active/inactive).

4. **Candidate Application Tracker**:
   - Candidate portal to look up submitted applications by email, view stage status, and review company details.

5. **Authentication & Authorization**:
   - Recruiter/Staff access protection using Django's `@staff_member_required`.
   - Built-in **1-Click Recruiter Demo Login** for rapid evaluation.
   - Full Django Admin integration at `/admin/` with custom filters and search.

6. **Production & Render Deployment Ready**:
   - WhiteNoise static asset compression.
   - Ephemeral SQLite database with automated superuser and demo data initialization (`create_superuser.py`).
   - Production blueprint configured in `render.yaml`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **Production Server**: Gunicorn, WhiteNoise
- **Deployment Platform**: Render

---

## 📂 Project Structure

```text
.
├── manage.py
├── requirements.txt
├── render.yaml
├── db.sqlite3
├── create_superuser.py
├── README.md
├── .gitignore
├── venv/
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── jobs/
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── __init__.py
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    ├── tests.py
    ├── templates/
    │   ├── base.html
    │   └── jobs/
    │       ├── candidate_portal.html
    │       ├── job_detail.html
    │       ├── job_form.html
    │       ├── job_list.html
    │       ├── login.html
    │       ├── recruiter_dashboard.html
    │       └── includes/
    │           └── applicant_card.html
    └── static/
        ├── css/
        │   └── styles.css
        └── js/
            └── main.js
```

---

## 🚀 Local Development Setup

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Migrations & Seed Sample Data
```bash
python manage.py migrate
python create_superuser.py
```
*`create_superuser.py` creates default accounts and populates realistic demo companies, job listings, candidates, and multi-stage applications.*

### 4. Run Automated Test Suite
```bash
python manage.py test
```

### 5. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Default Credentials

- **Admin / Staff Superuser**:
  - Username: `admin`
  - Password: `Admin@12345`
- **Recruiter Account**:
  - Username: `recruiter`
  - Password: `Password@123`
- **1-Click Demo Login**: Available directly on the `/login/` page for instant access without typing credentials.

---

## 🌐 Render Deployment Guide

1. **Commit and Push Code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for TalentSphere ATS Capstone"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create Render Service**:
   - Log in to [Render](https://render.com/).
   - Click **New +** → **Blueprint** (or **Web Service**).
   - Connect your GitHub repository.
   - If using **Blueprint**, Render will automatically detect `render.yaml`.
   - If setting up a **Web Service** manually:
     - **Runtime**: Python 3
     - **Build Command**:
       ```bash
       pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py
       ```
     - **Start Command**:
       ```bash
       python manage.py migrate && python create_superuser.py && gunicorn myproject.wsgi:application
       ```
     - **Environment Variables**:
       - `SECRET_KEY`: `<generate-a-random-secret-key>`
       - `PYTHON_VERSION`: `3.11.0`
       - `RENDER`: `True`

3. **Verify Deployment**:
   - Access the generated `https://<your-service>.onrender.com` URL.
   - Test the live Job Board, client-side filtering, application modal, candidate tracking, recruiter dashboard, and `/admin/`.
