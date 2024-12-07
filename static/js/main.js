// Theme management
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const icon = document.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// Initialize theme
const savedTheme = localStorage.getItem('theme') || 'dark';
setTheme(savedTheme);

// Theme toggle functionality
document.getElementById('theme-toggle')?.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    setTheme(currentTheme === 'light' ? 'dark' : 'light');
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

function showModal() {
    modal.classList.add('show');
}

function hideModal() {
    modal.classList.remove('show');
}

function handleNext() {
    const selectedLevel = document.querySelector('input[name="level"]:checked').value;
    localStorage.setItem('learningLevel', selectedLevel);
    hideModal();
    // TODO: Implement next steps after level selection
}

if (searchGoBtn) {
    searchGoBtn.addEventListener('click', showModal);
}

if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', hideModal);
}

if (nextBtn) {
    nextBtn.addEventListener('click', handleNext);
}

// Add animation to search box on focus
const searchInput = document.querySelector('.search-box input');
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
