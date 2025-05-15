from django.core.paginator import Paginator
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
import logging
from .forms import CustomAuthenticationForm
import json
from .forms import UserUpdateForm
from .forms import BookForm
from .decorators import role_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Book, Order, OrderItem

logger = logging.getLogger(__name__)


def book_list(request):
    books = Book.objects.all()
    per_page = request.GET.get("per_page", 5)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    cart_items = []
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('book')

    paginator = Paginator(books, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "book/book_list.html", {
        "page_obj": page_obj,
        "per_page": per_page,
        "book_count": books.count(),
        'cart_items': cart_items
    })


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})


@role_required('admin')
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})


@role_required('admin')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            logger.info(f"Попытка входа с именем пользователя: {username}")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
        else:
            logger.warning(f'Ошибка валидации формы входа: {form.errors}')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def home(request):
    return render(request, 'book/book_list.html')


def logout_user(request):
    logout(request)
    return redirect('book_list')


@login_required
def user_profile(request):
    user = request.user
    return render(request, 'user_profile.html', {'user': user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    return render(request, "cart.html", {"items": items, "total": total})


@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    logger.debug(f"Added book {book.title} to cart for user {request.user.username}")
    return redirect("cart")


@login_required
def checkout(request):
    logger.debug(
        f"Checkout view called with method: {request.method}, user: {request.user.username}, user_id: {request.user.id}")

    if request.method == 'POST':
        logger.debug("Processing POST request for checkout")
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        logger.debug(f"Cart items count: {items.count()}")
        for item in items:
            logger.debug(
                f"Item: {item.book.title}, Quantity: {item.quantity}, Price: {item.book.price}, Total: {item.total_price()}")

        if not items:
            logger.warning("Cart is empty, redirecting to cart")
            return redirect('cart')

        try:
            total = sum(item.total_price() for item in items)
            logger.debug(f"Calculated total: {total}")
            order = Order.objects.create(user=request.user, total=total)
            logger.debug(f"Created order: {order.id} for user {request.user.username}")

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    price=item.book.price
                )
                logger.debug(f"Created OrderItem: {item.quantity} x {item.book.title}")

            items.delete()
            logger.debug("Cart items deleted")
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            return render(request, 'checkout.html', {'error': f'Ошибка при создании заказа: {str(e)}'})

        logger.debug("Redirecting to checkout after successful order creation")
        return redirect('checkout')

    logger.debug("Processing GET request for checkout")
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    logger.debug(f"Found {orders.count()} orders for user {request.user.username}")
    return render(request, "checkout.html", {
        "orders": orders,
        "cart_items": items,
        "cart_total": total
    })


def update_cart(request):
    if request.method != 'POST':
        logger.error("Неверный метод запроса: требуется POST")
        return JsonResponse({'success': False, 'error': 'Требуется POST-запрос'}, status=400)
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action')
        logger.debug(f"Получены данные: item_id={item_id}, action={action}")
        if not item_id or not action:
            logger.error("Отсутствует item_id или action")
            return JsonResponse({'success': False, 'error': 'Отсутствует item_id или action'}, status=400)
        if action not in ['increase', 'decrease']:
            logger.error(f"Недопустимое действие: {action}")
            return JsonResponse({'success': False, 'error': 'Недопустимое действие'}, status=400)
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        logger.debug(f"Найден элемент корзины: id={item.id}, book={item.book.title}, quantity={item.quantity}")
        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
            else:
                item.delete()
                logger.debug("Элемент корзины удалён")
                cart_total = sum(
                    item.quantity * float(item.book.price) for item in CartItem.objects.filter(cart__user=request.user))
                return JsonResponse({
                    'success': True,
                    'quantity': 0,
                    'total_price': 0,
                    'cart_total': float(cart_total)
                })
        item.save()
        logger.debug(f"Элемент обновлён: quantity={item.quantity}")
        total_price = item.quantity * float(item.book.price)
        cart_total = sum(
            item.quantity * float(item.book.price) for item in CartItem.objects.filter(cart__user=request.user))
        logger.debug(f"Вычислены суммы: total_price={total_price}, cart_total={cart_total}")
        return JsonResponse({
            'success': True,
            'quantity': item.quantity,
            'total_price': float(total_price),
            'cart_total': float(cart_total)
        })
    except json.JSONDecodeError:
        logger.error("Неверный формат JSON")
        return JsonResponse({'success': False, 'error': 'Неверный формат JSON'}, status=400)
    except CartItem.DoesNotExist:
        logger.error(f"Элемент корзины не найден: item_id={item_id}")
        return JsonResponse({'success': False, 'error': 'Элемент корзины не найден'}, status=404)
    except AttributeError as e:
        logger.error(f"Ошибка атрибута: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Ошибка модели: {str(e)}'}, status=500)
    except TypeError as e:
        logger.error(f"Ошибка типа: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Ошибка типа данных: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"Внутренняя ошибка: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Внутренняя ошибка: {str(e)}'}, status=500)