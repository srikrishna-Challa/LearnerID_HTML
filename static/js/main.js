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
            if (!searchButton.disabled) {
                showQuestionnaire();
            }
        });
    }

    // Radio button click handler
    const radioGroups = document.querySelectorAll('.space-y-4');
    radioGroups.forEach(group => {
        const labels = group.querySelectorAll('label');
        labels.forEach(label => {
            label.addEventListener('click', () => {
                // Remove selected state from all labels in group
                labels.forEach(l => {
                    l.classList.remove('selected');
                    const radio = l.querySelector('input[type="radio"]');
                    const indicator = l.querySelector('.w-3.h-3');
                    if (indicator) indicator.classList.add('hidden');
                });
                
                // Add selected state to clicked label
                label.classList.add('selected');
                const radio = label.querySelector('input[type="radio"]');
                const indicator = label.querySelector('.w-3.h-3');
                if (radio && indicator) {
                    radio.checked = true;
                    indicator.classList.remove('hidden');
                }
            });
        });
    });
});

// Questionnaire functionality
let currentStep = 1;
const totalSteps = 7;

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

function updateProgressIndicator() {
    const steps = document.querySelectorAll('[data-step]');
    const progressLine = document.querySelector('.absolute.h-0.5.bg-white\\/20');
    
    steps.forEach((step, index) => {
        const stepNum = parseInt(step.getAttribute('data-step'));
        if (stepNum <= currentStep) {
            step.classList.remove('bg-white/10');
            step.classList.add('bg-primary');
            step.classList.remove('text-white/70');
            step.classList.add('text-white');
        } else {
            step.classList.remove('bg-primary');
            step.classList.add('bg-white/10');
            step.classList.add('text-white/70');
            step.classList.remove('text-white');
        }
    });
    
    if (progressLine) {
        const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
        progressLine.style.background = `linear-gradient(to right, 
            #0052CC ${progress}%, 
            rgba(255, 255, 255, 0.2) ${progress}%)`;
    }
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
    const prevBtn = document.getElementById('prevButton');
    const nextBtn = document.getElementById('nextButton');
    
    if (prevBtn && nextBtn) {
        // Show Previous button from question 2 onwards
        prevBtn.style.display = currentStep > 1 ? 'inline-flex' : 'none';
        nextBtn.textContent = currentStep === totalSteps ? 'Finish' : 'Next';
    }
}

function hideModal() {
    const modal = document.getElementById('learningLevelModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        currentStep = 1;
    }
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
document.addEventListener('DOMContentLoaded', () => {
    const languageRadios = document.querySelectorAll('input[name="contentLanguage"]');
    const otherLanguageInput = document.getElementById('otherLanguageInput');

    if (languageRadios && otherLanguageInput) {
        languageRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                otherLanguageInput.style.display = e.target.value === 'other' ? 'block' : 'none';
            });
        });
    }

    // Event listeners for modal
    const modal = document.getElementById('learningLevelModal');
    const closeBtn = modal?.querySelector('.fa-times')?.parentElement;
    const nextBtn = document.getElementById('nextButton');
    const prevBtn = document.getElementById('prevButton');

    if (closeBtn) {
        closeBtn.addEventListener('click', hideModal);
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', handleNext);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', handlePrevious);
    }

    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal();
            }
        });
    }

    // Add click handlers for topic buttons
    document.querySelectorAll('button[onclick="showQuestionnaire()"]').forEach(button => {
        button.addEventListener('click', showQuestionnaire);
    });
});

// Save questionnaire answers
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
