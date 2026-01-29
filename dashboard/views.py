from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import User
from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem, OrderStatusHistory


def is_staff_user(user):
    """Проверка, что пользователь - менеджер или админ"""
    return user.is_authenticated and (user.is_manager() or user.is_admin_user())


@login_required
@user_passes_test(is_staff_user)
def dashboard_index(request):
    """Главная страница панели управления"""

    # Статистика
    total_products = Product.objects.count()
    available_products = Product.objects.filter(is_available=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_users = User.objects.filter(role='client').count()

    # Последние заказы
    recent_orders = Order.objects.prefetch_related(
        'items__product', 'items__product__category'
    ).order_by('-created_at')[:10]

    # Популярные продукты (с наибольшим количеством заказов)
    popular_products = Product.objects.annotate(
        orders_count=Count('order_items')
    ).filter(orders_count__gt=0).order_by('-orders_count')[:5]

    context = {
        'total_products': total_products,
        'available_products': available_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'popular_products': popular_products,
    }

    return render(request, 'dashboard/index.html', context)


@login_required
@user_passes_test(is_staff_user)
def orders_list(request):
    """Список всех заказов"""
    orders = Order.objects.select_related(
        'user', 'manager'
    ).prefetch_related('items__product').order_by('-created_at')

    # Фильтры
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'current_status': status_filter,
    }

    return render(request, 'dashboard/orders_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def order_detail(request, pk):
    """Детальная информация о заказе"""
    order = get_object_or_404(
        Order.objects.select_related('user', 'manager').prefetch_related('items__product'),
        pk=pk
    )

    # История изменения статусов
    history = order.status_history.all().select_related('changed_by')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        manager_notes = request.POST.get('manager_notes', '')

        # Обновление заказа
        order.status = new_status
        order.manager = request.user
        order.manager_notes = manager_notes

        if new_status == 'completed':
            order.completed_at = timezone.now()

        order.save()

        # Запись в историю
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            changed_by=request.user,
            comment=manager_notes or f'Статус изменен на {order.get_status_display()}'
        )

        messages.success(request, 'Заказ успешно обновлен')
        return redirect('dashboard:order_detail', pk=pk)

    context = {
        'order': order,
        'history': history,
    }

    return render(request, 'dashboard/order_detail.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin_user())
def users_list(request):
    """Список пользователей (только для админов)"""
    users = User.objects.annotate(
        orders_count=Count('orders')
    ).order_by('-date_joined')

    # Фильтр по роли
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    context = {
        'users': users,
        'current_role': role_filter,
    }

    return render(request, 'dashboard/users_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_admin_user())
def user_edit(request, pk):
    """Редактирование пользователя (только для админов)"""
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.role = request.POST.get('role', user.role)
        user.is_active = request.POST.get('is_active') == 'on'

        user.save()
        messages.success(request, 'Пользователь успешно обновлен')
        return redirect('dashboard:users_list')

    context = {
        'edited_user': user,
    }

    return render(request, 'dashboard/user_edit.html', context)


@login_required
@user_passes_test(is_staff_user)
def products_list(request):
    """Список продуктов (для менеджеров и админов)"""
    products = Product.objects.select_related('category').prefetch_related('images').order_by('-created_at')

    # Фильтры
    category_filter = request.GET.get('category')
    available_filter = request.GET.get('available')
    search_query = request.GET.get('search', '')

    if category_filter:
        products = products.filter(category__slug=category_filter)

    if available_filter == '1':
        products = products.filter(is_available=True)
    elif available_filter == '0':
        products = products.filter(is_available=False)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
    }

    return render(request, 'dashboard/products_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def product_edit(request, pk):
    """Редактирование продукта (для менеджеров и админов)"""
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, pk=category_id)
        product.name = request.POST.get('name', product.name)
        product.brand = request.POST.get('brand', '')
        product.price = float(request.POST.get('price', product.price))
        product.quantity = float(request.POST.get('quantity', product.quantity))
        product.unit = request.POST.get('unit', product.unit)
        product.stock = int(request.POST.get('stock', product.stock))
        product.discount_percent = int(request.POST.get('discount_percent', 0))
        product.description = request.POST.get('description', '')
        product.ingredients = request.POST.get('ingredients', '')
        product.nutritional_value = request.POST.get('nutritional_value', '')
        product.country_origin = request.POST.get('country_origin', '')
        product.expiry_date = request.POST.get('expiry_date', '')
        product.storage_conditions = request.POST.get('storage_conditions', '')
        product.is_available = request.POST.get('is_available') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_new = request.POST.get('is_new') == 'on'
        product.is_organic = request.POST.get('is_organic') == 'on'

        product.save()
        messages.success(request, 'Продукт успешно обновлен')
        return redirect('dashboard:products_list')

    context = {
        'product': product,
        'categories': categories,
    }

    return render(request, 'dashboard/product_edit.html', context)


@login_required
@user_passes_test(is_staff_user)
def product_create(request):
    """Создание нового продукта (для менеджеров и админов)"""
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, pk=category_id)

        product = Product.objects.create(
            category=category,
            name=request.POST.get('name'),
            brand=request.POST.get('brand', ''),
            price=float(request.POST.get('price')),
            quantity=float(request.POST.get('quantity', 1)),
            unit=request.POST.get('unit', 'pcs'),
            stock=int(request.POST.get('stock', 0)),
            discount_percent=int(request.POST.get('discount_percent', 0)),
            description=request.POST.get('description', ''),
            ingredients=request.POST.get('ingredients', ''),
            nutritional_value=request.POST.get('nutritional_value', ''),
            country_origin=request.POST.get('country_origin', ''),
            expiry_date=request.POST.get('expiry_date', ''),
            storage_conditions=request.POST.get('storage_conditions', ''),
            is_available=request.POST.get('is_available') == 'on',
            is_featured=request.POST.get('is_featured') == 'on',
            is_new=request.POST.get('is_new') == 'on',
            is_organic=request.POST.get('is_organic') == 'on',
        )

        messages.success(request, 'Продукт успешно создан')
        return redirect('dashboard:product_edit', pk=product.pk)

    context = {
        'categories': categories,
    }

    return render(request, 'dashboard/product_create.html', context)


@login_required
@user_passes_test(is_staff_user)
def product_delete(request, pk):
    """Удаление продукта (для менеджеров и админов)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Продукт "{product_name}" успешно удален')
        return redirect('dashboard:products_list')

    context = {
        'product': product,
    }

    return render(request, 'dashboard/product_delete.html', context)
