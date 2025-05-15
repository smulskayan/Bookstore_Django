from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from .models import Book

User = get_user_model()  # Используем кастомную модель пользователя

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
        help_text='Пароль должен содержать хотя бы 8 символов.'
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
        if cleaned_data['password'] != cleaned_data['password2']:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
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
        fields = ['username', 'first_name', 'last_name', 'email']  # добавлен username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

