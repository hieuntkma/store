document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginFormEl = document.getElementById('login');
    const registerFormEl = document.getElementById('register');
    const toggleButtons = document.querySelectorAll('.toggle-form');
    const passwordToggles = document.querySelectorAll('.toggle-password');

    // Toast elements
    const toast = document.getElementById('toast');
    const toastInstance = new bootstrap.Toast(toast);
    const toastBody = toast.querySelector('.toast-body');

    // Toggle between login and register forms
    toggleButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const targetForm = button.dataset.form;

            if (targetForm === 'register') {
                loginForm.classList.add('d-none');
                registerForm.classList.remove('d-none');
            } else {
                registerForm.classList.add('d-none');
                loginForm.classList.remove('d-none');
            }
        });
    });

    // Toggle password visibility
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            const input = toggle.previousElementSibling;
            const icon = toggle.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });

    // Validate email format
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Validate password strength
    function isValidPassword(password) {
        return password.length >= 8;
    }

    // Show toast message
    function showToast(message, success = true) {
        toastBody.textContent = message;
        toast.classList.remove('bg-success', 'bg-danger', 'text-white');
        toast.classList.add(success ? 'bg-success' : 'bg-danger', 'text-white');
        toastInstance.show();
    }

    // Handle login form submission
    loginFormEl.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail');
        const password = document.getElementById('loginPassword');
        let isValid = true;

        // Reset validation
        loginFormEl.classList.remove('was-validated');

        // Validate email
        if (!email.value || !isValidEmail(email.value)) {
            email.setCustomValidity('Please enter a valid email address');
            isValid = false;
        } else {
            email.setCustomValidity('');
        }

        // Validate password
        if (!password.value) {
            password.setCustomValidity('Password is required');
            isValid = false;
        } else {
            password.setCustomValidity('');
        }

        loginFormEl.classList.add('was-validated');

        if (isValid) {
            // Simulate API call
            setTimeout(() => {
                showToast('Login successful!');
                loginFormEl.reset();
                loginFormEl.classList.remove('was-validated');
            }, 1000);
        }
    });

    // Handle register form submission
    registerFormEl.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = document.getElementById('registerName');
        const email = document.getElementById('registerEmail');
        const password = document.getElementById('registerPassword');
        const confirmPassword = document.getElementById('confirmPassword');
        const agreeTerms = document.getElementById('agreeTerms');
        let isValid = true;

        // Reset validation
        registerFormEl.classList.remove('was-validated');

        // Validate name
        if (!name.value.trim()) {
            name.setCustomValidity('Please enter your name');
            isValid = false;
        } else {
            name.setCustomValidity('');
        }

        // Validate email
        if (!email.value || !isValidEmail(email.value)) {
            email.setCustomValidity('Please enter a valid email address');
            isValid = false;
        } else {
            email.setCustomValidity('');
        }

        // Validate password
        if (!password.value || !isValidPassword(password.value)) {
            password.setCustomValidity('Password must be at least 8 characters');
            isValid = false;
        } else {
            password.setCustomValidity('');
        }

        // Validate confirm password
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity('Passwords do not match');
            isValid = false;
        } else {
            confirmPassword.setCustomValidity('');
        }

        // Validate terms agreement
        if (!agreeTerms.checked) {
            agreeTerms.setCustomValidity('You must agree to the terms');
            isValid = false;
        } else {
            agreeTerms.setCustomValidity('');
        }

        registerFormEl.classList.add('was-validated');

        if (isValid) {
            // Simulate API call
            setTimeout(() => {
                showToast('Registration successful!');
                registerFormEl.reset();
                registerFormEl.classList.remove('was-validated');
                // Switch to login form
                registerForm.classList.add('d-none');
                loginForm.classList.remove('d-none');
            }, 1000);
        }
    });
});