/**
 * TalentSphere ATS - Core Interactive Logic
 * Features:
 * 1. Instant keyword & skill filtering without page reload
 * 2. Bootstrap application modal with client-side validation & AJAX submission
 * 3. Recruiter dashboard dynamic status pipeline updates & column moves
 */

document.addEventListener('DOMContentLoaded', function () {
    initJobFiltering();
    initApplicationModal();
    initRecruiterPipeline();
    initDemoLoginHelper();
});

/* ==========================================================================
   1. Real-Time Client-Side Job Filtering (No Page Reload)
   ========================================================================== */
function initJobFiltering() {
    const searchInput = document.getElementById('keyword-filter-input');
    const typeSelect = document.getElementById('type-filter-select');
    const skillBtns = document.querySelectorAll('.skill-filter-btn');
    const resetBtn = document.getElementById('btn-reset-filters');
    const jobCards = document.querySelectorAll('.job-card-item');
    const countDisplay = document.getElementById('jobs-count-display');
    const noResultsState = document.getElementById('no-jobs-found-state');

    if (!jobCards.length) return;

    let activeSkill = '';

    function filterJobs() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const selectedType = typeSelect ? typeSelect.value : '';
        let visibleCount = 0;

        jobCards.forEach(card => {
            const keywords = (card.getAttribute('data-keywords') || '').toLowerCase();
            const skills = (card.getAttribute('data-skills') || '').toLowerCase();
            const jobType = (card.getAttribute('data-job-type') || '');

            const matchesQuery = !query || keywords.includes(query) || skills.includes(query);
            const matchesType = !selectedType || jobType === selectedType;
            const matchesSkill = !activeSkill || skills.includes(activeSkill.toLowerCase());

            if (matchesQuery && matchesType && matchesSkill) {
                card.style.display = '';
                card.classList.add('fade-in-item');
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (countDisplay) {
            countDisplay.textContent = visibleCount;
        }

        if (noResultsState) {
            noResultsState.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterJobs);
    }

    if (typeSelect) {
        typeSelect.addEventListener('change', filterJobs);
    }

    skillBtns.forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const skill = this.getAttribute('data-skill');

            if (activeSkill === skill) {
                activeSkill = '';
                this.classList.remove('active', 'btn-primary');
                this.classList.add('btn-outline-secondary');
            } else {
                skillBtns.forEach(b => {
                    b.classList.remove('active', 'btn-primary');
                    b.classList.add('btn-outline-secondary');
                });
                activeSkill = skill;
                this.classList.add('active', 'btn-primary');
                this.classList.remove('btn-outline-secondary');
            }
            filterJobs();
        });
    });

    if (resetBtn) {
        resetBtn.addEventListener('click', function () {
            if (searchInput) searchInput.value = '';
            if (typeSelect) typeSelect.value = '';
            activeSkill = '';
            skillBtns.forEach(b => {
                b.classList.remove('active', 'btn-primary');
                b.classList.add('btn-outline-secondary');
            });
            filterJobs();
        });
    }
}

/* ==========================================================================
   2. Bootstrap Application Modal & Client-Side Validation
   ========================================================================== */
function initApplicationModal() {
    const applyModalEl = document.getElementById('applyModal');
    if (!applyModalEl) return;

    const modalTitleJob = document.getElementById('modal-job-title');
    const modalCompany = document.getElementById('modal-company-name');
    const modalForm = document.getElementById('apply-form');
    const modalErrorAlert = document.getElementById('modal-error-alert');
    const modalSuccessAlert = document.getElementById('modal-success-alert');
    const submitBtn = document.getElementById('modal-submit-btn');

    // Attach data when modal opens from "Apply Now" buttons
    applyModalEl.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        if (button) {
            const jobId = button.getAttribute('data-job-id');
            const jobTitle = button.getAttribute('data-job-title');
            const companyName = button.getAttribute('data-company-name');

            if (jobId && modalForm) {
                modalForm.setAttribute('action', `/jobs/${jobId}/apply/`);
                modalForm.setAttribute('data-job-id', jobId);
            }
            if (modalTitleJob && jobTitle) {
                modalTitleJob.textContent = jobTitle;
            }
            if (modalCompany && companyName) {
                modalCompany.textContent = companyName;
            }
        }

        // Reset previous form state
        if (modalForm) {
            modalForm.classList.remove('was-validated');
        }
        if (modalErrorAlert) modalErrorAlert.classList.add('d-none');
        if (modalSuccessAlert) modalSuccessAlert.classList.add('d-none');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> Submit Application';
        }
    });

    if (modalForm) {
        modalForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (modalErrorAlert) modalErrorAlert.classList.add('d-none');
            if (modalSuccessAlert) modalSuccessAlert.classList.add('d-none');

            // Client-side validations
            let isValid = true;
            const fullName = document.getElementById('applicant-full-name');
            const email = document.getElementById('applicant-email');
            const phone = document.getElementById('applicant-phone');
            const portfolio = document.getElementById('applicant-portfolio');
            const skills = document.getElementById('applicant-skills');
            const coverLetter = document.getElementById('applicant-cover-letter');

            function markField(input, valid, errorMsg = '') {
                if (valid) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                    isValid = false;
                }
            }

            // Name validation
            if (!fullName.value.trim() || fullName.value.trim().length < 2) {
                markField(fullName, false);
            } else {
                markField(fullName, true);
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!email.value.trim() || !emailRegex.test(email.value.trim())) {
                markField(email, false);
            } else {
                markField(email, true);
            }

            // Phone validation: at least 7 digits
            const digits = phone.value.replace(/\D/g, '');
            if (!phone.value.trim() || digits.length < 7) {
                markField(phone, false);
            } else {
                markField(phone, true);
            }

            // Portfolio URL validation (optional, but if filled must start with http/https)
            if (portfolio && portfolio.value.trim()) {
                try {
                    new URL(portfolio.value.trim());
                    markField(portfolio, true);
                } catch (_) {
                    markField(portfolio, false);
                }
            } else if (portfolio) {
                portfolio.classList.remove('is-invalid');
            }

            // Skills validation
            if (!skills.value.trim()) {
                markField(skills, false);
            } else {
                markField(skills, true);
            }

            // Cover letter validation: at least 15 characters
            if (!coverLetter.value.trim() || coverLetter.value.trim().length < 15) {
                markField(coverLetter, false);
            } else {
                markField(coverLetter, true);
            }

            if (!isValid) {
                if (modalErrorAlert) {
                    modalErrorAlert.textContent = "Please correct the highlighted fields before submitting.";
                    modalErrorAlert.classList.remove('d-none');
                }
                return;
            }

            // Send via AJAX
            const actionUrl = modalForm.getAttribute('action');
            const csrfTokenInput = modalForm.querySelector('[name=csrfmiddlewaretoken]');
            const csrfToken = csrfTokenInput ? csrfTokenInput.value : '';

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Submitting...';

            const formData = new FormData(modalForm);

            fetch(actionUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(async response => {
                const data = await response.json();
                if (response.ok && data.success) {
                    if (modalSuccessAlert) {
                        modalSuccessAlert.innerHTML = `<strong>Success!</strong> ${data.message}`;
                        modalSuccessAlert.classList.remove('d-none');
                    }
                    modalForm.reset();
                    // Remove is-valid classes
                    modalForm.querySelectorAll('.is-valid').forEach(el => el.classList.remove('is-valid'));
                    submitBtn.innerHTML = '<i class="bi bi-check-circle me-1"></i> Application Received';

                    setTimeout(() => {
                        const modalInstance = bootstrap.Modal.getInstance(applyModalEl);
                        if (modalInstance) modalInstance.hide();
                    }, 2000);
                } else {
                    let errMsg = 'Application could not be submitted.';
                    if (data.errors) {
                        const messages = [];
                        for (const key in data.errors) {
                            messages.push(`${key}: ${data.errors[key].join(', ')}`);
                        }
                        errMsg = messages.join('<br>');
                    } else if (data.message) {
                        errMsg = data.message;
                    }
                    if (modalErrorAlert) {
                        modalErrorAlert.innerHTML = errMsg;
                        modalErrorAlert.classList.remove('d-none');
                    }
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> Submit Application';
                }
            })
            .catch(error => {
                console.error('Submission error:', error);
                if (modalErrorAlert) {
                    modalErrorAlert.textContent = "Network error. Please try again or submit directly.";
                    modalErrorAlert.classList.remove('d-none');
                }
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> Submit Application';
            });
        });
    }
}

/* ==========================================================================
   3. Recruiter Dashboard Status Pipeline Management
   ========================================================================== */
function initRecruiterPipeline() {
    const statusSelects = document.querySelectorAll('.applicant-status-select');
    if (!statusSelects.length) return;

    statusSelects.forEach(select => {
        select.addEventListener('change', function () {
            const appId = this.getAttribute('data-app-id');
            const newStatus = this.value;
            const csrfToken = getCookie('csrftoken');
            const applicantCard = document.getElementById(`applicant-card-${appId}`);

            this.disabled = true;

            fetch(`/dashboard/application/${appId}/status/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(res => res.json())
            .then(data => {
                this.disabled = false;
                if (data.success) {
                    // Update card status border & badge
                    if (applicantCard) {
                        // Move card to target column
                        const targetColId = getColumnIdForStatus(newStatus);
                        const targetColumn = document.getElementById(targetColId);
                        if (targetColumn) {
                            targetColumn.querySelector('.pipeline-cards-list').appendChild(applicantCard);
                        }

                        // Update border class
                        applicantCard.className = applicantCard.className.replace(/border-start-\w+/g, '');
                        const borderClass = getBorderClassForStatus(newStatus);
                        applicantCard.classList.add(borderClass);

                        // Flash highlight
                        applicantCard.style.backgroundColor = '#ecfdf5';
                        setTimeout(() => {
                            applicantCard.style.backgroundColor = '';
                        }, 1000);
                    }

                    // Update count badges
                    updatePipelineCounts();
                    showToastNotification(`Status updated to "${newStatus}"!`, 'success');
                } else {
                    showToastNotification(data.message || 'Status update failed', 'danger');
                }
            })
            .catch(err => {
                this.disabled = false;
                console.error(err);
                showToastNotification('Network error while updating status.', 'danger');
            });
        });
    });

    function getColumnIdForStatus(status) {
        switch (status) {
            case 'Applied': return 'column-applied';
            case 'Under Review': return 'column-under-review';
            case 'Shortlisted': return 'column-shortlisted';
            case 'Rejected': return 'column-rejected';
            default: return 'column-applied';
        }
    }

    function getBorderClassForStatus(status) {
        switch (status) {
            case 'Applied': return 'border-start-applied';
            case 'Under Review': return 'border-start-review';
            case 'Shortlisted': return 'border-start-shortlisted';
            case 'Rejected': return 'border-start-rejected';
            default: return 'border-start-applied';
        }
    }

    function updatePipelineCounts() {
        ['applied', 'under-review', 'shortlisted', 'rejected'].forEach(stage => {
            const col = document.getElementById(`column-${stage}`);
            const countBadge = document.getElementById(`count-${stage}`);
            if (col && countBadge) {
                const count = col.querySelectorAll('.applicant-card').length;
                countBadge.textContent = count;
            }
        });
    }
}

/* ==========================================================================
   4. Helper Utilities: Cookies & Toast
   ========================================================================== */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showToastNotification(message, type = 'info') {
    let toastContainer = document.getElementById('global-toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'global-toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1090';
        document.body.appendChild(toastContainer);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type === 'danger' ? 'danger' : 'dark'} border-0 shadow`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${type === 'success' ? 'bi-check-circle-fill text-success' : 'bi-info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function initDemoLoginHelper() {
    // If URL contains ?demo=1 on login page, automatically select demo
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('demo') === '1') {
        const demoBtn = document.getElementById('btn-demo-login-submit');
        if (demoBtn) {
            demoBtn.scrollIntoView({ behavior: 'smooth' });
        }
    }
}
