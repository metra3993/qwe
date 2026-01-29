from django.contrib import admin
from .models import Category, Product, ProductImage, Favorite


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main', 'order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'brand', 'price', 'discount_percent',
        'stock', 'is_available', 'is_featured', 'is_new', 'is_organic'
    ]
    list_filter = [
        'category', 'is_available', 'is_featured',
        'is_new', 'is_organic', 'unit'
    ]
    search_fields = ['name', 'brand', 'category__name', 'description']
    list_editable = ['is_available', 'is_featured', 'price', 'stock']
    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'brand', 'price')
        }),
        ('Количество и единицы', {
            'fields': ('quantity', 'unit', 'stock')
        }),
        ('Скидки', {
            'fields': ('discount_percent', 'old_price')
        }),
        ('Описание', {
            'fields': ('description', 'ingredients', 'nutritional_value')
        }),
        ('Характеристики', {
            'fields': ('country_origin', 'expiry_date', 'storage_conditions')
        }),
        ('Статус', {
            'fields': ('is_available', 'is_featured', 'is_new', 'is_organic')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_main', 'order', 'uploaded_at']
    list_filter = ['is_main', 'product__category']
    search_fields = ['product__name', 'product__category__name']
    list_editable = ['is_main', 'order']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']
