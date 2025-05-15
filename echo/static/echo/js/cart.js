document.addEventListener("DOMContentLoaded", function() {
    // Находим все кнопки "Добавить в корзину"
    const buttons = document.querySelectorAll(".add-to-cart-button");

    buttons.forEach(button => {
        button.addEventListener("click", function() {
            let productId = this.getAttribute("data-product-id"); // Получаем ID товара

            fetch(`/add_to_cart/${productId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"), // CSRF-токен для защиты
                },
                body: JSON.stringify({ "product_id": productId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Товар добавлен в корзину!");
                    document.getElementById("cart-count").innerText = data.cart_count;
                } else {
                    alert("Ошибка: " + data.error);
                }
            })
            .catch(error => console.error("Ошибка:", error));
        });
    });
});

// Функция для получения CSRF-токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.split("=")[1]);
                break;
            }
        }
    }
    return cookieValue;
}
