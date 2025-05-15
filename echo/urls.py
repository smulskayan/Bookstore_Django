from django.urls import path, include
from .views import *

urlpatterns = [
    path('', book_list, name='book_list'),
    path('book/add/', book_create, name='book_create'),
    path('book/<int:pk>/edit/', book_update, name='book_update'),
    path('book/<int:pk>/delete/', book_delete, name='book_delete'),
    #пути для авторизации/регистрации/выхода пользователя
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', user_profile, name='user_profile'),
    path("edit-profile/", edit_profile, name="edit_profile"),
    path('cart/', cart_view, name='cart'),
    path("add_to_cart/<int:book_id>/", add_to_cart, name="add_to_cart"),
    path('update_cart/', update_cart, name='update_cart'),
    path('checkout/', checkout, name='checkout'),
]