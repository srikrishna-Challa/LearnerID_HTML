function setTheme(theme) {
    const html = document.documentElement;
    html.classList.remove('light', 'dark');
    html.classList.add(theme);
    localStorage.setItem('theme', theme);
    
    // Update icon
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// Initialize theme and add event listeners
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
            setTheme(currentTheme);
        });
    }

    // Update search input and button selectors
    const searchInput = document.querySelector('.search-box input');
    const searchButton = document.querySelector('.search-box button');

    if (searchInput && searchButton) {
        searchInput.addEventListener('input', (e) => {
            searchButton.disabled = !e.target.value.trim();
            if (e.target.value.trim()) {
                searchButton.classList.remove('opacity-50');
            } else {
                searchButton.classList.add('opacity-50');
            }
        });
        
        searchButton.addEventListener('click', () => {
            if (searchInput.value.trim()) {
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

// Modal functionality
const modal = document.getElementById('learningLevelModal');
const searchGoBtn = document.querySelector('.search-box .btn-primary');
const modalCloseBtn = document.querySelector('.modal-close');
const nextBtn = document.getElementById('nextButton');
function showQuestionnaire() {
    currentStep = 1;
    showSlide(currentStep);
    updateProgressIndicator();
    updateNavigationButtons();
    showModal();
}

// Update theme icon with null check
function updateThemeIcon() {
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = document.documentElement.getAttribute('data-theme') === 'light' ? '🌙' : '☀️';
    }
}

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
    currentSlide.style.display = 'block';
}

function updateNavigationButtons() {
    prevBtn.style.display = currentStep > 1 ? 'block' : 'none';
    nextBtn.textContent = currentStep === totalSteps ? 'Finish' : 'Next';
}

function showModal() {
    modal.classList.add('show');
    currentStep = 1;
    showSlide(currentStep);
    updateProgressIndicator();
    updateNavigationButtons();
}

function hideModal() {
    modal.classList.remove('show');
    currentStep = 1;
}

function saveAnswers() {
    const contentLanguageRadio = document.querySelector('input[name="contentLanguage"]:checked');
    const otherLanguageInput = document.querySelector('#otherLanguageInput input');
    const languageValue = contentLanguageRadio.value === 'other' && otherLanguageInput
        ? otherLanguageInput.value
        : contentLanguageRadio.value;

    const answers = {
        level: document.querySelector('input[name="level"]:checked').value,
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

if (searchGoBtn) {
    searchGoBtn.addEventListener('click', showModal);
}

if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', hideModal);
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

// Add animation to search box on focus
const searchInput = document.querySelector('.search-box input');
const searchButton = document.querySelector('.search-action-btn');

if (searchInput && searchButton) {
    searchInput.addEventListener('input', (e) => {
        searchButton.disabled = !e.target.value.trim();
    });
    
    searchButton.addEventListener('click', showQuestionnaire);
}

if (searchInput) {
    searchInput.addEventListener('focus', () => {
        searchInput.parentElement.style.transform = 'scale(1.02)';
        searchInput.parentElement.style.transition = 'transform 0.3s ease';
    });

    searchInput.addEventListener('blur', () => {
        searchInput.parentElement.style.transform = 'scale(1)';
    });
}

// Close modal when clicking outside
if (modal) {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideModal();
        }
    });
}

// Add scroll functionality for arrows
document.querySelectorAll('.scroll-arrow').forEach(arrow => {
    arrow.addEventListener('click', () => {
        const container = arrow.closest('.scroll-container-wrapper').querySelector('.scroll-container');
        const scrollAmount = container.offsetWidth * 0.8;
        
        if (arrow.classList.contains('left-arrow')) {
            container.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        } else {
            container.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        }
    });
});

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
