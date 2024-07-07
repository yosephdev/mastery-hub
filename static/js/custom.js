document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.alert');
    const navbar = document.querySelector('.navbar');

    messages.forEach((msg, index) => {
        msg.style.display = 'block';
        msg.style.position = 'fixed';
        msg.style.top = navbar ? navbar.offsetHeight + 'px' : '0';
        msg.style.left = '50%';
        msg.style.transform = 'translateX(-50%)';
        msg.style.zIndex = '9999';
        msg.style.maxWidth = '400px';
        msg.style.width = '100%';
        msg.style.textAlign = 'center';
        msg.style.marginTop = '15px'; 
    });

   
    const content = document.querySelector('main'); 
    if (content && messages.length > 0) {
        content.style.marginTop = (parseInt(messages[0].style.top) + messages[0].offsetHeight + 20) + 'px';
    }
});


document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function () {
            this.closest('.alert').remove();
        });
    });
});