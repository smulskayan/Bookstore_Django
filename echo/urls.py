from django.urls import path, include
from .views import book_list, book_create, book_update, book_delete
from .views import book_list
from . import views
from .views import edit_profile

urlpatterns = [
    path('', book_list, name='book_list'),
    path('book/add/', book_create, name='book_create'),
    path('book/<int:pk>/edit/', book_update, name='book_update'),
    path('book/<int:pk>/delete/', book_delete, name='book_delete'),
    #пути для авторизации/регистрации/выхода пользователя
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path("edit-profile/", edit_profile, name="edit_profile"),
]