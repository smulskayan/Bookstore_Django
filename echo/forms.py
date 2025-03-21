from django import forms
from .models import Book
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


# Форма для добавления книги
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'price', 'year', 'genre']
        labels = {
            'title': 'Название книги',
            'author': 'Автор книги',
            'price': 'Цена',
            'year': 'Год',
            'genre': 'Жанр',
        }

# Форма для регистрации пользователя
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль',
        help_text='Ваш пароль не может быть слишком похож на другую личную информацию. Пароль должен содержать хотя бы 8 символов.'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Подтверждение пароля',
        help_text='Введите тот же пароль для проверки.'
    )
    role = forms.ChoiceField(
        choices=[('user', 'Обычный пользователь'), ('admin', 'Администратор')],
        label='Роль'
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name']
        labels = {
            'username': 'Имя пользователя',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }

    def clean_password2(self):
        cleaned_data = self.cleaned_data
        # Проверка на совпадение паролей
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data['password2']

    def save(self, commit=True):
        # Создание пользователя и установка пароля
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Установка роли пользователя
        user.role = self.cleaned_data['role']

        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Редактируемые поля

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User._default_manager.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email