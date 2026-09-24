/**
 * script.js - Client-side validation & UI interactions for AuthCore
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Password Visibility Toggle Functionality
    const toggleButtons = document.querySelectorAll(".password-toggle-btn");

    toggleButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetInputId = btn.getAttribute("data-target");
            const targetInput = document.getElementById(targetInputId);
            const iconSpan = btn.querySelector(".toggle-icon");

            if (!targetInput) return;

            if (targetInput.type === "password") {
                targetInput.type = "text";
                if (iconSpan) iconSpan.textContent = "🙈";
                btn.setAttribute("aria-label", "Hide password");
                btn.setAttribute("title", "Hide password");
            } else {
                targetInput.type = "password";
                if (iconSpan) iconSpan.textContent = "👁️";
                btn.setAttribute("aria-label", "Show password");
                btn.setAttribute("title", "Show password");
            }
        });
    });

    // 2. Registration Form Validation
    const form = document.getElementById("registration-form");
    if (!form) return;

    const nameInput = document.getElementById("name");
    const nameError = document.getElementById("name-error");

    const emailInput = document.getElementById("email");
    const emailError = document.getElementById("email-error");

    const dobInput = document.getElementById("dob");
    const dobError = document.getElementById("dob-error");

    const passwordInput = document.getElementById("password");
    const passwordError = document.getElementById("password-error");

    const confirmPasswordInput = document.getElementById("confirm_password");
    const confirmPasswordError = document.getElementById("confirm_password-error");

    // Helper functions for displaying and clearing errors
    function showError(input, errorElement, message) {
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");
        errorElement.textContent = message;
    }

    function showSuccess(input, errorElement) {
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
        errorElement.textContent = "";
    }

    function clearStatus(input, errorElement) {
        input.classList.remove("is-invalid", "is-valid");
        errorElement.textContent = "";
    }

    // Validation Rules
    function validateName() {
        const value = nameInput.value.trim();
        const nameRegex = /^[a-zA-Z\s'-]+$/;

        if (!value) {
            showError(nameInput, nameError, "Full name is required.");
            return false;
        }
        if (value.length < 2) {
            showError(nameInput, nameError, "Name must be at least 2 characters long.");
            return false;
        }
        if (!nameRegex.test(value)) {
            showError(nameInput, nameError, "Name can only contain letters, spaces, hyphens, and apostrophes.");
            return false;
        }
        showSuccess(nameInput, nameError);
        return true;
    }

    function validateEmail() {
        const value = emailInput.value.trim();
        // Standard email format validation regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!value) {
            showError(emailInput, emailError, "Mail ID is required.");
            return false;
        }
        if (!emailRegex.test(value)) {
            showError(emailInput, emailError, "Please enter a valid email address (e.g. user@example.com).");
            return false;
        }
        showSuccess(emailInput, emailError);
        return true;
    }

    function validateDob() {
        const value = dobInput.value;
        if (!value) {
            showError(dobInput, dobError, "Date of birth is required.");
            return false;
        }

        const selectedDate = new Date(value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (isNaN(selectedDate.getTime())) {
            showError(dobInput, dobError, "Please select a valid date.");
            return false;
        }
        if (selectedDate > today) {
            showError(dobInput, dobError, "Date of birth cannot be in the future.");
            return false;
        }
        if (selectedDate.getFullYear() < 1900) {
            showError(dobInput, dobError, "Please enter a realistic year of birth (after 1900).");
            return false;
        }

        showSuccess(dobInput, dobError);
        return true;
    }

    function validatePassword() {
        const value = passwordInput.value;

        if (!value) {
            showError(passwordInput, passwordError, "Password is required.");
            return false;
        }
        if (value.length < 8) {
            showError(passwordInput, passwordError, "Password must be at least 8 characters long.");
            return false;
        }

        showSuccess(passwordInput, passwordError);

        // Re-validate confirm password if it already has a value
        if (confirmPasswordInput.value) {
            validateConfirmPassword();
        }

        return true;
    }

    function validateConfirmPassword() {
        const passwordValue = passwordInput.value;
        const confirmValue = confirmPasswordInput.value;

        if (!confirmValue) {
            showError(confirmPasswordInput, confirmPasswordError, "Please confirm your password.");
            return false;
        }
        if (confirmValue !== passwordValue) {
            showError(confirmPasswordInput, confirmPasswordError, "Passwords do not match.");
            return false;
        }

        showSuccess(confirmPasswordInput, confirmPasswordError);
        return true;
    }

    // Attach real-time / blur event listeners
    nameInput.addEventListener("blur", validateName);
    nameInput.addEventListener("input", () => {
        if (nameInput.classList.contains("is-invalid")) validateName();
    });

    emailInput.addEventListener("blur", validateEmail);
    emailInput.addEventListener("input", () => {
        if (emailInput.classList.contains("is-invalid")) validateEmail();
    });

    dobInput.addEventListener("blur", validateDob);
    dobInput.addEventListener("change", validateDob);

    passwordInput.addEventListener("blur", validatePassword);
    passwordInput.addEventListener("input", () => {
        if (passwordInput.classList.contains("is-invalid")) validatePassword();
    });

    confirmPasswordInput.addEventListener("blur", validateConfirmPassword);
    confirmPasswordInput.addEventListener("input", () => {
        if (confirmPasswordInput.classList.contains("is-invalid")) validateConfirmPassword();
    });

    // Form Submission Handling
    form.addEventListener("submit", (e) => {
        const isNameValid = validateName();
        const isEmailValid = validateEmail();
        const isDobValid = validateDob();
        const isPasswordValid = validatePassword();
        const isConfirmPasswordValid = validateConfirmPassword();

        const isFormValid = isNameValid && isEmailValid && isDobValid && isPasswordValid && isConfirmPasswordValid;

        if (!isFormValid) {
            e.preventDefault();
            // Focus on the first invalid field
            const firstInvalid = form.querySelector(".is-invalid");
            if (firstInvalid) {
                firstInvalid.focus();
            }
        }
    });
});
