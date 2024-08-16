document.addEventListener('DOMContentLoaded', () => {
    const forgotPasswordLink = document.getElementById('forgot-password-link');
    const modal = document.getElementById('forgot-password-modal');
    const closeButton = document.querySelector('.close-button');

    forgotPasswordLink.addEventListener('click', (event) => {
        event.preventDefault();
        modal.style.display = 'block';
    });

    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    document.getElementById('forgot-password-form').addEventListener('submit', (event) => {
        event.preventDefault();
        alert('Password reset link sent to your email.');
        modal.style.display = 'none';
    });
});