from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total_price']
    can_delete = False
    fields = ['product', 'quantity', 'price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'comment', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'status', 'total_price',
        'delivery_price', 'payment_method', 'manager', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at', 'manager']
    search_fields = [
        'user__username', 'user__email', 'full_name',
        'email', 'phone', 'delivery_address'
    ]
    list_editable = ['status', 'manager']
    readonly_fields = ['created_at', 'updated_at', 'final_total']
    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'status', 'manager')
        }),
        ('Контакты клиента', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Адрес доставки', {
            'fields': ('delivery_address', 'entrance', 'floor', 'apartment')
        }),
        ('Финансы', {
            'fields': ('total_price', 'delivery_price', 'final_total', 'payment_method')
        }),
        ('Время доставки', {
            'fields': ('delivery_date', 'delivery_time')
        }),
        ('Дополнительно', {
            'fields': ('message', 'manager_notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Автоматически записывать изменения статуса
        if change and 'status' in form.changed_data:
            super().save_model(request, obj, form, change)
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                changed_by=request.user,
                comment=f'Статус изменен через админ-панель'
            )
        else:
            super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'product__category']
    search_fields = ['order__id', 'product__name']
    readonly_fields = ['total_price']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__id', 'comment']
    readonly_fields = ['order', 'status', 'changed_by', 'created_at']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'total_price', 'added_at']
    fields = ['product', 'quantity', 'total_price', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'total_price', 'added_at']
    list_filter = ['added_at', 'product__category']
    search_fields = ['cart__user__email', 'product__name']
    readonly_fields = ['total_price', 'added_at']
