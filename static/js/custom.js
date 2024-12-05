document.addEventListener('DOMContentLoaded', function () {
    setupDynamicSearch();
    setupLazyLoading();
    setupFormValidation();
    setupDarkMode();
    setupToggleVisibility();
    setupProfilePicturePreview();
    setupSmoothScroll();
    setupTooltips();
    setupMentorSort();
    initializeToasts();
    initializeAnnouncementCarousel();
    initializeDropdowns();
    setActiveNavItem();
    initializeMobileNavigation();
    setupHeaderScrollEffect();
});

function initializeToasts() {
    try {
        const toastElList = [].slice.call(document.querySelectorAll('.toast'));
        const toastList = toastElList.map(toastEl => new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 }));
        toastList.forEach(toast => toast.show());
    } catch (error) {
        console.warn('Toast initialization failed:', error);
    }
}

function initializeAnnouncementCarousel() {
    const announcements = [
        "Follow your dream!&nbsp;&nbsp;<i class='fa-solid fa-trophy text-warning'></i>",
        "Connect with expert mentors&nbsp;&nbsp;<i class='fa-solid fa-users text-warning'></i>",
        "Learn at your own pace&nbsp;&nbsp;<i class='fa-solid fa-clock text-warning'></i>",
        "Achieve your goals&nbsp;&nbsp;<i class='fa-solid fa-star text-warning'></i>"
    ];
    let currentIndex = 0;
    const carouselText = document.getElementById('carousel-text');
    if (carouselText) {
        function updateAnnouncement() {
            $(carouselText).fadeOut(400, function () {
                $(this).html(announcements[currentIndex]).fadeIn(400);
                currentIndex = (currentIndex + 1) % announcements.length;
            });
        }
        setInterval(updateAnnouncement, 4000);
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
    const config = { rootMargin: '0px 0px 50px 0px', threshold: 0 };
    const observer = new IntersectionObserver((entries, self) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                preloadImage(entry.target);
                self.unobserve(entry.target);
            }
        });
    }, config);
    images.forEach(image => observer.observe(image));
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
    const navLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
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

function setupTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
}

function setupMentorSort() {
    const sortSelect = document.querySelector('select[onchange="sortMentors(this.value)"]');
    if (sortSelect) {
        sortSelect.addEventListener('change', function () {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('sort', this.value);
            window.location.search = urlParams.toString();
        });
    }
}

function initializeDropdowns() {
    if (window.innerWidth > 992) {
        document.querySelectorAll('.navbar .dropdown').forEach(dropdown => {
            dropdown.addEventListener('mouseover', function () {
                this.querySelector('.dropdown-menu').classList.add('show');
            });
            dropdown.addEventListener('mouseout', function () {
                this.querySelector('.dropdown-menu').classList.remove('show');
            });
        });
    }
}

function setActiveNavItem() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

function initializeMobileNavigation() {
    const mobileSearch = document.getElementById('mobile-search');
    if (mobileSearch) {
        mobileSearch.addEventListener('shown.bs.collapse', function () {
            mobileSearch.querySelector('input').focus();
        });
    }
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.mobile-user-menu')) {
            const dropdowns = document.querySelectorAll('.mobile-dropdown-menu.show');
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
    document.querySelectorAll('.mobile-dropdown-menu .dropdown-item').forEach(item => {
        item.addEventListener('touchstart', function () {
            this.style.backgroundColor = '#f8f9fa';
        });
        item.addEventListener('touchend', function () {
            this.style.backgroundColor = '';
        });
    });
}

function setupHeaderScrollEffect() {
    const header = document.querySelector('.header-main');
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 50) {
            header.classList.add('sticky');
        } else {
            header.classList.remove('sticky');
        }
        lastScroll = currentScroll;
    });
}
