from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Главная страница панели
    path('', views.dashboard_index, name='index'),

    # Управление заказами
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Управление пользователями (только админы)
    path('users/', views.users_list, name='users_list'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),

    # Управление продуктами (менеджеры и админы)
    path('products/', views.products_list, name='products_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
]
