document.addEventListener('DOMContentLoaded', () => {
    const getCookie = name => document.cookie.split('; ').find(c => c.startsWith(`${name}=`))?.split('=')[1] || null;

    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        alert('Ошибка: CSRF-токен не найден.');
        return;
    }

    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', () => {
            const action = button.dataset.action;
            const itemId = button.dataset.itemId;
            const cartBook = button.closest('.cart_book');
            const quantityElement = cartBook.querySelector('.quantity');
            const totalPriceElement = cartBook.querySelector('.item-total strong');
            const cartTotalElement = document.querySelector('.cart-total strong');

            button.classList.add('loading');
            fetch('/update_cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ item_id: itemId, action })
            })
            .then(res => res.ok ? res.json() : Promise.reject('Ошибка сервера'))
            .then(data => {
                if (!data.success) throw new Error(data.error || 'Ошибка корзины');

                if (data.quantity === 0) {
                    cartBook.remove();
                    if (!document.querySelector('.cart_book:not(.total-section)')) {
                        document.querySelector('.left-container').innerHTML = '<p>Ваша корзина пуста.</p>';
                    }
                } else {
                    quantityElement.textContent = data.quantity;
                    if (totalPriceElement) {
                        totalPriceElement.textContent = `Сумма: ${data.total_price.toFixed(2)} руб.`;
                    }
                }
                if (cartTotalElement) {
                    cartTotalElement.textContent = `Итого: ${data.cart_total.toFixed(2)} руб.`;
                }
            })
            .catch(err => alert(`Ошибка: ${err.message}`))
            .finally(() => button.classList.remove('loading'));
        });
    });
});