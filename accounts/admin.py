from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['name', 'street', 'house', 'entrance', 'floor', 'apartment', 'is_default']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone']
    inlines = [AddressInline]

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'phone', 'avatar')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('role', 'phone')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'street', 'house', 'apartment', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'street', 'house']
    list_editable = ['is_default']
