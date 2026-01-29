from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import F
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from accounts.models import Address


@login_required
def cart_view(request):
    """Просмотр корзины"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'product__category').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        quantity = int(request.POST.get('quantity', 1))

        # Проверка наличия товара на складе
        if quantity > product.stock:
            messages.error(request, f'К сожалению, доступно только {product.stock} шт.')
            return redirect(request.META.get('HTTP_REFERER', 'products:catalog'))

        # Добавление или обновление товара в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            # Если товар уже в корзине, увеличиваем количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Максимальное количество: {product.stock} шт.')
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f'{product.name} добавлен в корзину')
        else:
            messages.success(request, f'{product.name} добавлен в корзину')

        # Если AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_items,
                'message': f'{product.name} добавлен в корзину'
            })

        return redirect(request.META.get('HTTP_REFERER', 'products:catalog'))

    return redirect('products:catalog')


@login_required
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Максимальное количество: {cart_item.product.stock} шт.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество обновлено')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = cart_item.cart
            return JsonResponse({
                'success': True,
                'item_total': float(cart_item.total_price) if quantity > 0 else 0,
                'cart_total': float(cart.total_price),
                'cart_items_count': cart.total_items
            })

    return redirect('orders:cart')


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} удален из корзины')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.total_price),
            'cart_items_count': cart.total_items
        })

    return redirect('orders:cart')


@login_required
def clear_cart(request):
    """Очистка корзины"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        messages.success(request, 'Корзина очищена')

    return redirect('orders:cart')


@login_required
def checkout_view(request):
    """Страница оформления заказа"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('product', 'product__category').all()

    # Проверка минимальной суммы
    if cart.total_price < 500:
        messages.error(request, 'Минимальная сумма заказа 500 ₽')
        return redirect('orders:cart')

    # Получаем адреса пользователя
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Получаем данные из формы
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'cash')
        delivery_date = request.POST.get('delivery_date')
        delivery_time = request.POST.get('delivery_time')
        comment = request.POST.get('comment', '')

        # Проверяем адрес
        if not address_id:
            messages.error(request, 'Выберите адрес доставки')
            return redirect('orders:checkout')

        address = get_object_or_404(Address, id=address_id, user=request.user)

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            email=request.user.email,
            phone=request.user.phone,
            delivery_address=address.get_full_address(),
            entrance=address.entrance,
            floor=address.floor,
            apartment=address.apartment,
            total_price=cart.total_price,
            delivery_price=99,
            payment_method=payment_method,
            delivery_time=delivery_time or 'Сегодня с 18:00 до 22:00',
            message=comment,
            status='pending'
        )

        # Создаем позиции заказа
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Уменьшаем остаток на складе
            item.product.stock -= item.quantity
            item.product.save()

        # Очищаем корзину
        cart.items.all().delete()

        messages.success(request, f'Заказ №{order.id} успешно оформлен!')
        return redirect('accounts:orders')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'delivery_price': 99,
        'total_with_delivery': cart.total_price + 99,
    }

    return render(request, 'orders/checkout.html', context)
