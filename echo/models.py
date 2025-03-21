from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100)  # Название книги
    author = models.CharField(max_length=100)  # Автор
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена
    year = models.IntegerField()  # Год выпуска
    genre = models.CharField(max_length=100)  # Жанр

    class Meta:
        db_table = 'book'  # Указываем имя таблицы в базе данныхclass Meta:

    def __str__(self):
        return self.title

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Создает суперпользователя с ролью 'admin' по умолчанию
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  # Роль admin по умолчанию

        if not email:
            raise ValueError("The Email field must be set")

        # Создаем пользователя через метод create_user
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    ROLE_CHOICES = (
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Добавляем это поле
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # Добавляем роль

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.username