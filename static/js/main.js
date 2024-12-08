// Search functionality
document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-box');
    const searchInput = searchForm?.querySelector('input');
    const searchButton = searchForm?.querySelector('button');
    
    if (searchForm && searchInput && searchButton) {
        // Initial state
        searchButton.disabled = true;
        searchButton.classList.add('opacity-50');
        
        // Enable/disable button based on input
        searchInput.addEventListener('input', () => {
            const hasValue = searchInput.value.trim().length > 0;
            searchButton.disabled = !hasValue;
            searchButton.classList.toggle('opacity-50', !hasValue);
        });
        
        // Handle form submission
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!searchButton.disabled && typeof showQuestionnaire === 'function') {
                showQuestionnaire();
            }
        });
    }
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Questionnaire functionality
function showQuestionnaire() {
    const modal = document.getElementById('learningLevelModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        currentStep = 1;
        showSlide(currentStep);
        updateProgressIndicator();
        updateNavigationButtons();
    }
}

// Modal functionality
const modal = document.getElementById('learningLevelModal');
const modalCloseBtn = document.querySelector('.modal-close');
const nextBtn = document.getElementById('nextButton');
const prevBtn = document.getElementById('prevButton');

let currentStep = 1;
const totalSteps = 7;

function updateProgressIndicator() {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });

    document.querySelectorAll('.progress-line').forEach((line, index) => {
        line.classList.toggle('completed', index < currentStep - 1);
    });
}

function showSlide(slideNumber) {
    document.querySelectorAll('.question-slide').forEach(slide => {
        slide.style.display = 'none';
    });
    const currentSlide = document.querySelector(`.question-slide[data-step="${slideNumber}"]`);
    if (currentSlide) {
        currentSlide.style.display = 'block';
    }
}

function updateNavigationButtons() {
    if (prevBtn && nextBtn) {
        prevBtn.style.display = currentStep > 1 ? 'block' : 'none';
        nextBtn.textContent = currentStep === totalSteps ? 'Finish' : 'Next';
    }
}

function hideModal() {
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        currentStep = 1;
    }
}

function saveAnswers() {
    const contentLanguageRadio = document.querySelector('input[name="contentLanguage"]:checked');
    const otherLanguageInput = document.querySelector('#otherLanguageInput input');
    const languageValue = contentLanguageRadio?.value === 'other' && otherLanguageInput
        ? otherLanguageInput.value
        : contentLanguageRadio?.value;

    const answers = {
        level: document.querySelector('input[name="level"]:checked')?.value,
        goal: document.querySelector('input[name="goal"]:checked')?.value,
        style: document.querySelector('input[name="style"]:checked')?.value,
        timeCommitment: document.querySelector('input[name="timeCommitment"]:checked')?.value,
        targetOutcome: document.querySelector('input[name="targetOutcome"]:checked')?.value,
        contentLanguage: languageValue,
        budget: document.querySelector('input[name="budget"]:checked')?.value
    };
    localStorage.setItem('learningPreferences', JSON.stringify(answers));
}

function handleNext() {
    if (currentStep < totalSteps) {
        currentStep++;
        showSlide(currentStep);
        updateProgressIndicator();
        updateNavigationButtons();
    } else {
        saveAnswers();
        hideModal();
        // TODO: Implement next steps after questionnaire completion
    }
}

function handlePrevious() {
    if (currentStep > 1) {
        currentStep--;
        showSlide(currentStep);
        updateProgressIndicator();
        updateNavigationButtons();
    }
}

// Handle "Other" language option
const languageRadios = document.querySelectorAll('input[name="contentLanguage"]');
const otherLanguageInput = document.getElementById('otherLanguageInput');

if (languageRadios && otherLanguageInput) {
    languageRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            otherLanguageInput.style.display = e.target.value === 'other' ? 'block' : 'none';
        });
    });
}

// Event listeners
if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', hideModal);
}

if (nextBtn) {
    nextBtn.addEventListener('click', handleNext);
}

if (prevBtn) {
    prevBtn.addEventListener('click', handlePrevious);
}

// Add click handlers for suggestion tags
document.querySelectorAll('.topic-pill').forEach(tag => {
    tag.addEventListener('click', showQuestionnaire);
});

// Close modal when clicking outside
if (modal) {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideModal();
        }
    });
}

// Mobile menu toggle functionality
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const leftSidebar = document.querySelector('.left-sidebar');

if (mobileMenuToggle && leftSidebar) {
    mobileMenuToggle.addEventListener('click', () => {
        leftSidebar.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!leftSidebar.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
            leftSidebar.classList.remove('active');
        }
    });
}