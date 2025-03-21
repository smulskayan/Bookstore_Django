from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .forms import BookForm
from .models import Book
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
import logging
from .forms import CustomAuthenticationForm
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Book
from .forms import BookForm
from .decorators import role_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm

logger = logging.getLogger(__name__)


def book_list(request):
    books = Book.objects.all()  # Получаем все книги из БД

    per_page = request.GET.get("per_page", 5)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5

    paginator = Paginator(books, per_page)  # ЗДЕСЬ ДОЛЖНО БЫТЬ books, а не book_list!
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "book/book_list.html", {
        "page_obj": page_obj,
        "per_page": per_page,
        "book_count":books.count()
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

# Представление для регистрации пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Входим в систему сразу после регистрации
            return redirect('book_list')  # Направляем пользователя на главную страницу (или на страницу, которую укажешь)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Представление для авторизации пользователя

logger = logging.getLogger(__name__)


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

                return redirect('book_list')  # Перенаправление после успешного входа

        else:
            # Логируем ошибки формы
            logger.warning(f'⚠️ Ошибка валидации формы входа: {form.errors}')

    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'book/book_list.html')

def logout_user(request):
    logout(request)  # Выход пользователя
    return redirect('book_list')  # Перенаправление на главную страницу

@login_required
def user_profile(request):
    # Получаем текущего пользователя
    user = request.user
    return render(request, 'user_profile.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # После сохранения данных, перенаправляем на страницу профиля
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

