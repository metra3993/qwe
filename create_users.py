#!/usr/bin/env python
"""
Скрипт для создания тестовых пользователей:
- Администратор
- Менеджер
- Клиент

Запуск: python create_users.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freshmarket.settings')
django.setup()

from accounts.models import User


def create_test_users():
    """Создание тестовых пользователей"""

    users_data = [
        {
            'email': 'admin@freshmarket.ru',
            'password': 'admin123',
            'first_name': 'Иван',
            'last_name': 'Администратор',
            'phone': '+7 (999) 111-11-11',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'email': 'manager@freshmarket.ru',
            'password': 'manager123',
            'first_name': 'Мария',
            'last_name': 'Менеджер',
            'phone': '+7 (999) 222-22-22',
            'role': 'manager',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'email': 'client@test.ru',
            'password': 'client123',
            'first_name': 'Петр',
            'last_name': 'Клиентов',
            'phone': '+7 (999) 333-33-33',
            'role': 'client',
            'is_staff': False,
            'is_superuser': False,
        },
    ]

    print("🔄 Создание тестовых пользователей...\n")

    for user_data in users_data:
        email = user_data['email']

        # Проверяем, существует ли уже пользователь
        if User.objects.filter(email=email).exists():
            print(f"⚠️  Пользователь {email} уже существует, пропускаем...")
            continue

        # Создаём пользователя
        password = user_data.pop('password')
        user = User.objects.create_user(
            email=email,
            password=password,
            **user_data
        )

        # Выводим информацию
        role_emoji = {
            'admin': '👑',
            'manager': '👔',
            'client': '👤'
        }
        emoji = role_emoji.get(user.role, '👤')

        print(f"{emoji} Создан пользователь:")
        print(f"   Email: {email}")
        print(f"   Пароль: {password}")
        print(f"   Роль: {user.get_role_display()}")
        print()

    print("✅ Готово! Все тестовые пользователи созданы.\n")
    print("📋 Данные для входа:")
    print("=" * 50)
    print("Администратор:")
    print("  Email: admin@freshmarket.ru")
    print("  Пароль: admin123")
    print()
    print("Менеджер:")
    print("  Email: manager@freshmarket.ru")
    print("  Пароль: manager123")
    print()
    print("Клиент:")
    print("  Email: client@test.ru")
    print("  Пароль: client123")
    print("=" * 50)


if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
