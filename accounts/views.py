from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from .models import User, Address
from products.models import Favorite
from orders.models import Order


def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('products:catalog')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Валидация
        if not all([first_name, last_name, email, phone, password, password2]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже зарегистрирован')
            return render(request, 'accounts/register.html')

        # Создание пользователя
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='client'
        )

        # Автоматический вход
        login(request, user)
        messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
        return redirect('products:catalog')

    return render(request, 'accounts/register.html')


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('products:catalog')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
            next_url = request.GET.get('next', 'products:catalog')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('products:catalog')


@login_required
def profile_view(request):
    """Личный кабинет пользователя"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', '')

        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('accounts:profile')

    # Статистика пользователя
    orders_all = Order.objects.filter(user=request.user)
    recent_orders = orders_all.prefetch_related('items__product', 'items__product__category').order_by('-created_at')[:3]
    recent_favorites = Favorite.objects.filter(user=request.user).select_related('product', 'product__category').order_by('-added_at')[:4]
    addresses = Address.objects.filter(user=request.user)

    context = {
        'orders_count': orders_all.count(),
        'favorites_count': Favorite.objects.filter(user=request.user).count(),
        'completed_orders': orders_all.filter(status='completed').count(),
        'pending_orders': orders_all.filter(status='pending').count(),
        'recent_orders': recent_orders,
        'recent_favorites': recent_favorites,
        'addresses': addresses,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def favorites_view(request):
    """Избранные продукты"""
    favorites = Favorite.objects.filter(user=request.user).select_related('product', 'product__category')

    context = {
        'favorites': favorites
    }

    return render(request, 'accounts/favorites.html', context)


@login_required
def orders_view(request):
    """История заказов пользователя"""
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'items__product', 'items__product__category'
    ).order_by('-created_at')

    context = {
        'orders': orders
    }

    return render(request, 'accounts/orders.html', context)


@login_required
def toggle_favorite(request, car_id):
    """Добавить/удалить из избранного"""
    from products.models import Product
    from django.http import JsonResponse

    if request.method == 'POST':
        try:
            product = Product.objects.get(id=car_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

            if not created:
                favorite.delete()
                is_favorite = False
                message = 'Удалено из избранного'
            else:
                is_favorite = True
                message = 'Добавлено в избранное'

            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'is_favorite': is_favorite,
                    'message': message
                })

            messages.success(request, message)

        except Product.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Продукт не найден'
                }, status=404)
            messages.error(request, 'Продукт не найден')

    return redirect(request.META.get('HTTP_REFERER', 'products:catalog'))


@login_required
def add_address(request):
    """Добавление нового адреса"""
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            street=request.POST.get('street'),
            house=request.POST.get('house'),
            entrance=request.POST.get('entrance', ''),
            floor=request.POST.get('floor', ''),
            apartment=request.POST.get('apartment', ''),
            comment=request.POST.get('comment', ''),
            is_default=request.POST.get('is_default') == 'on'
        )
        messages.success(request, 'Адрес добавлен')
    return redirect('accounts:profile')


@login_required
def edit_address(request, address_id):
    """Редактирование адреса"""
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.street = request.POST.get('street')
        address.house = request.POST.get('house')
        address.entrance = request.POST.get('entrance', '')
        address.floor = request.POST.get('floor', '')
        address.apartment = request.POST.get('apartment', '')
        address.comment = request.POST.get('comment', '')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        messages.success(request, 'Адрес обновлен')

    return redirect('accounts:profile')


@login_required
def delete_address(request, address_id):
    """Удаление адреса"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Адрес удален')
    return redirect('accounts:profile')
