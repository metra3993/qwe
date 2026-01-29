from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Min, Max
from .models import Product, Category, Favorite


def catalog_view(request):
    """Каталог продуктов с фильтрацией"""
    products = Product.objects.filter(is_available=True).select_related('category').prefetch_related('images')

    # Фильтры
    category_filter = request.GET.get('category')
    is_organic = request.GET.get('organic')
    is_new = request.GET.get('new')
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    search_query = request.GET.get('search')

    # Применение фильтров
    if category_filter:
        products = products.filter(category__slug=category_filter)

    if is_organic:
        products = products.filter(is_organic=True)

    if is_new:
        products = products.filter(is_new=True)

    if price_from:
        products = products.filter(price__gte=price_from)

    if price_to:
        products = products.filter(price__lte=price_to)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Сортировка
    sort = request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'name', '-created_at']:
        products = products.order_by(sort)

    # Данные для фильтров
    categories = Category.objects.all().order_by('name')
    price_range = Product.objects.filter(is_available=True).aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )

    # Избранное пользователя
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = list(Favorite.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True))

    context = {
        'products': products,
        'categories': categories,
        'price_range': price_range,
        'user_favorites': user_favorites,
        # Текущие фильтры
        'current_category': category_filter,
        'current_sort': sort,
    }

    return render(request, 'products/catalog.html', context)


def car_detail_view(request, pk):
    """Детальная страница продукта"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        pk=pk
    )

    # Проверка, в избранном ли
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # Похожие продукты
    similar_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(pk=product.pk).select_related('category').prefetch_related('images')[:4]

    context = {
        'product': product,
        'is_favorite': is_favorite,
        'similar_products': similar_products,
    }

    return render(request, 'products/detail.html', context)


@login_required
def create_order_view(request, pk):
    """Добавление продукта в корзину (упрощенная версия)"""
    product = get_object_or_404(Product, pk=pk, is_available=True)

    if request.method == 'POST':
        # Здесь будет логика добавления в корзину
        messages.success(request, f'{product.name} добавлен в корзину!')
        return redirect('products:catalog')

    return redirect('products:detail', pk=pk)
