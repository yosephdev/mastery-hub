document.addEventListener('DOMContentLoaded', function () {
    initializeCarousel();
    initializeTooltips();
    setupSmoothScrolling();
});

// Function to initialize the carousel
function initializeCarousel() {
    $('#skillCarousel').carousel({
        interval: 5000,
        wrap: true,
        keyboard: true
    });
}

// Function to initialize tooltips
function initializeTooltips() {
    $('[data-toggle="tooltip"]').tooltip();
}

// Function to add smooth scrolling to all anchor links
function setupSmoothScrolling() {
    $('a[href*="#"]').on('click', function (e) {
        if (this.hash !== '') {
            e.preventDefault();
            const hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800);
        }
    });
}
