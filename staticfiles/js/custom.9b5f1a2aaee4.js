document.addEventListener('DOMContentLoaded', function () {
    setupMessageHandling();

    setupInfiniteScroll();
    setupDynamicSearch();
    setupLazyLoading();
    setupFormValidation();
    setupDarkMode();
    setupToggleVisibility();
    setupProfilePicturePreview();
    setupSmoothScroll();
});

function setupInfiniteScroll() {
    let page = 1;
    const content = document.querySelector('.content-container');
    if (content) {
        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
                loadMoreContent(++page);
            }
        });
    }
}

function setupDynamicSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');
    if (searchInput && searchResults) {
        searchInput.addEventListener('input', debounce(() => {
            const query = searchInput.value;
            if (query.length > 2) {
                fetchSearchResults(query);
            } else {
                searchResults.innerHTML = '';
            }
        }, 300));
    }
}

function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const config = {
        rootMargin: '0px 0px 50px 0px',
        threshold: 0
    };

    let observer = new IntersectionObserver((entries, self) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                preloadImage(entry.target);
                self.unobserve(entry.target);
            }
        });
    }, config);

    images.forEach(image => {
        observer.observe(image);
    });
}

function preloadImage(img) {
    const src = img.getAttribute('data-src');
    if (!src) return;
    img.src = src;
}

function setupFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

function setupDarkMode() {
    const darkModeToggle = document.querySelector('#dark-mode-toggle');
    const body = document.body;
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
        });

        if (localStorage.getItem('darkMode') === 'true') {
            body.classList.add('dark-mode');
        }
    }
}

function setupToggleVisibility() {
    const toggleButtons = document.querySelectorAll('.toggle-visibility');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.classList.toggle('hidden');
                this.textContent = targetElement.classList.contains('hidden') ? 'Show More' : 'Show Less';
            }
        });
    });
}

function setupProfilePicturePreview() {
    const profilePictureInput = document.getElementById('id_profile_picture');
    const profilePicturePreview = document.getElementById('profile-picture-preview');

    if (profilePictureInput && profilePicturePreview) {
        profilePictureInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePicturePreview.src = e.target.result;
                    profilePicturePreview.style.display = 'block';
                }
                reader.readAsDataURL(file);
            }
        });
    }
}

function setupSmoothScroll() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}