from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from .models import Book
from .models import User

# Register your models here.
admin.site.register(Book)
admin.site.register(User)
User = get_user_model()
admin.site.register(LogEntry)