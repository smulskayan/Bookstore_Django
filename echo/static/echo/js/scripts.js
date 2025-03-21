// static/echo/js/script.js

document.addEventListener("DOMContentLoaded", function() {
    const emailField = document.getElementById("email");
    const usernameField = document.getElementById("username");
    const passwordField = document.getElementById("password");
    const password2Field = document.getElementById("password2");

    // Функция для проверки email
    function validateEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    }

    // Функция для проверки пароля
    function validatePassword(password) {
        return password.length >= 6;
    }

    // Функция для проверки совпадения паролей
    function validatePasswordsMatch() {
        return passwordField.value === password2Field.value;
    }

    // Проверка email на лету
    emailField.addEventListener("blur", function() {
        const email = emailField.value;
        if (!validateEmail(email)) {
            document.getElementById("emailError").innerText = "Неверный формат email.";
        } else {
            document.getElementById("emailError").innerText = "";
        }

        // AJAX запрос для проверки уникальности email
        fetch(`/check-email/?email=${email}`)
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    document.getElementById("emailError").innerText = "Этот email уже занят.";
                }
            });
    });

    // Проверка пароля на лету
    passwordField.addEventListener("blur", function() {
        if (!validatePassword(passwordField.value)) {
            document.getElementById("passwordError").innerText = "Пароль должен быть не менее 6 символов.";
        } else {
            document.getElementById("passwordError").innerText = "";
        }
    });

    // Проверка совпадения паролей на лету
    password2Field.addEventListener("blur", function() {
        if (!validatePasswordsMatch()) {
            document.getElementById("password2Error").innerText = "Пароли не совпадают.";
        } else {
            document.getElementById("password2Error").innerText = "";
        }
    });
});
