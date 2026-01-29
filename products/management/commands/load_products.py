from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductImage
from accounts.models import User


class Command(BaseCommand):
    help = 'Загрузка тестовых данных продуктов'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание категорий и продуктов...')

        # Очистка старых данных
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Создание категорий
        categories_data = [
            {'name': 'Фрукты', 'slug': 'fruits', 'icon': '🍎'},
            {'name': 'Овощи', 'slug': 'vegetables', 'icon': '🥕'},
            {'name': 'Молочные продукты', 'slug': 'dairy', 'icon': '🥛'},
            {'name': 'Мясо и птица', 'slug': 'meat', 'icon': '🍖'},
            {'name': 'Хлеб и выпечка', 'slug': 'bakery', 'icon': '🍞'},
            {'name': 'Напитки', 'slug': 'drinks', 'icon': '🧃'},
            {'name': 'Бакалея', 'slug': 'grocery', 'icon': '🌾'},
            {'name': 'Сладости', 'slug': 'sweets', 'icon': '🍬'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon']
                }
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'Создана категория: {cat.name}')
            else:
                self.stdout.write(f'Категория уже существует: {cat.name}')

        # Создание продуктов
        products_data = [
            # Фрукты
            {'category': 'Фрукты', 'name': 'Яблоки Гала', 'brand': 'Фермерские', 'price': 89.90, 'unit': 'kg', 'quantity': 1, 'is_organic': True, 'stock': 50},
            {'category': 'Фрукты', 'name': 'Бананы', 'brand': 'Эквадор', 'price': 69.90, 'unit': 'kg', 'quantity': 1, 'stock': 100},
            {'category': 'Фрукты', 'name': 'Апельсины', 'brand': 'Марокко', 'price': 99.90, 'unit': 'kg', 'quantity': 1, 'stock': 75},
            {'category': 'Фрукты', 'name': 'Киви', 'brand': 'Новая Зеландия', 'price': 149.90, 'unit': 'kg', 'quantity': 1, 'is_new': True, 'stock': 30},

            # Овощи
            {'category': 'Овощи', 'name': 'Помидоры черри', 'brand': 'Местные', 'price': 129.90, 'unit': 'kg', 'quantity': 1, 'is_organic': True, 'stock': 40},
            {'category': 'Овощи', 'name': 'Огурцы свежие', 'brand': 'Фермерские', 'price': 79.90, 'unit': 'kg', 'quantity': 1, 'stock': 60},
            {'category': 'Овощи', 'name': 'Морковь', 'brand': '', 'price': 49.90, 'unit': 'kg', 'quantity': 1, 'stock': 80},
            {'category': 'Овощи', 'name': 'Салат Айсберг', 'brand': 'Свежий Урожай', 'price': 89.90, 'unit': 'pcs', 'quantity': 1, 'is_new': True, 'stock': 25},

            # Молочные продукты
            {'category': 'Молочные продукты', 'name': 'Молоко 3.2%', 'brand': 'Простоквашино', 'price': 89.90, 'unit': 'l', 'quantity': 1, 'stock': 100},
            {'category': 'Молочные продукты', 'name': 'Творог 5%', 'brand': 'Домик в деревне', 'price': 119.90, 'unit': 'g', 'quantity': 200, 'stock': 50},
            {'category': 'Молочные продукты', 'name': 'Сыр Российский', 'brand': 'Valio', 'price': 449.90, 'unit': 'g', 'quantity': 200, 'old_price': 499.90, 'discount_percent': 10, 'stock': 30},
            {'category': 'Молочные продукты', 'name': 'Йогурт натуральный', 'brand': 'Активия', 'price': 45.90, 'unit': 'g', 'quantity': 150, 'stock': 80},

            # Мясо и птица
            {'category': 'Мясо и птица', 'name': 'Куриное филе', 'brand': 'Приосколье', 'price': 299.90, 'unit': 'kg', 'quantity': 1, 'stock': 40},
            {'category': 'Мясо и птица', 'name': 'Говядина вырезка', 'brand': 'Мираторг', 'price': 799.90, 'unit': 'kg', 'quantity': 1, 'old_price': 899.90, 'discount_percent': 11, 'stock': 20},
            {'category': 'Мясо и птица', 'name': 'Фарш говяжий', 'brand': '', 'price': 349.90, 'unit': 'kg', 'quantity': 1, 'stock': 35},

            # Хлеб и выпечка
            {'category': 'Хлеб и выпечка', 'name': 'Хлеб Бородинский', 'brand': 'Хлебный дом', 'price': 49.90, 'unit': 'pcs', 'quantity': 1, 'stock': 50},
            {'category': 'Хлеб и выпечка', 'name': 'Батон нарезной', 'brand': 'Хлебный дом', 'price': 39.90, 'unit': 'pcs', 'quantity': 1, 'stock': 60},
            {'category': 'Хлеб и выпечка', 'name': 'Круассаны', 'brand': '7Days', 'price': 129.90, 'unit': 'g', 'quantity': 300, 'is_new': True, 'stock': 40},

            # Напитки
            {'category': 'Напитки', 'name': 'Сок апельсиновый', 'brand': 'Добрый', 'price': 89.90, 'unit': 'l', 'quantity': 1, 'stock': 70},
            {'category': 'Напитки', 'name': 'Вода минеральная', 'brand': 'Borjomi', 'price': 79.90, 'unit': 'l', 'quantity': 0.5, 'stock': 100},
            {'category': 'Напитки', 'name': 'Чай зеленый', 'brand': 'Greenfield', 'price': 199.90, 'unit': 'g', 'quantity': 100, 'is_organic': True, 'stock': 45},

            # Бакалея
            {'category': 'Бакалея', 'name': 'Рис круглозерный', 'brand': 'Мистраль', 'price': 129.90, 'unit': 'kg', 'quantity': 1, 'stock': 80},
            {'category': 'Бакалея', 'name': 'Гречка', 'brand': 'Ангстрем', 'price': 99.90, 'unit': 'kg', 'quantity': 1, 'stock': 90},
            {'category': 'Бакалея', 'name': 'Макароны', 'brand': 'Barilla', 'price': 149.90, 'unit': 'g', 'quantity': 500, 'stock': 60},

            # Сладости
            {'category': 'Сладости', 'name': 'Шоколад молочный', 'brand': 'Milka', 'price': 89.90, 'unit': 'g', 'quantity': 90, 'old_price': 109.90, 'discount_percent': 18, 'stock': 100},
            {'category': 'Сладости', 'name': 'Печенье овсяное', 'brand': 'Юбилейное', 'price': 69.90, 'unit': 'g', 'quantity': 300, 'stock': 80},
            {'category': 'Сладости', 'name': 'Мармелад', 'brand': 'Ударница', 'price': 119.90, 'unit': 'g', 'quantity': 250, 'is_new': True, 'stock': 50},
        ]

        for prod_data in products_data:
            category = categories[prod_data['category']]

            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                category=category,
                defaults={
                    'brand': prod_data.get('brand', ''),
                    'price': prod_data['price'],
                    'unit': prod_data.get('unit', 'pcs'),
                    'quantity': prod_data.get('quantity', 1),
                    'stock': prod_data.get('stock', 0),
                    'is_available': True,
                    'is_featured': prod_data.get('is_featured', False),
                    'is_new': prod_data.get('is_new', False),
                    'is_organic': prod_data.get('is_organic', False),
                    'discount_percent': prod_data.get('discount_percent', 0),
                    'old_price': prod_data.get('old_price'),
                    'description': f'Свежий продукт: {prod_data["name"]}. Высокое качество!',
                }
            )
            if created:
                self.stdout.write(f'Создан продукт: {product.name}')
            else:
                self.stdout.write(f'Продукт уже существует: {product.name}')

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {Product.objects.count()} продуктов в {Category.objects.count()} категориях'))

        # Создание тестовых пользователей если их нет
        if not User.objects.filter(email='admin@freshmarket.ru').exists():
            User.objects.create_superuser(
                email='admin@freshmarket.ru',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
                phone='+7 (999) 000-00-01',
                role='admin'
            )
            self.stdout.write('Создан пользователь admin@freshmarket.ru')

        if not User.objects.filter(email='manager@freshmarket.ru').exists():
            User.objects.create_user(
                email='manager@freshmarket.ru',
                password='manager123',
                first_name='Иван',
                last_name='Менеджеров',
                phone='+7 (999) 000-00-02',
                role='manager'
            )
            self.stdout.write('Создан пользователь manager@freshmarket.ru')

        if not User.objects.filter(email='client@example.com').exists():
            User.objects.create_user(
                email='client@example.com',
                password='client123',
                first_name='Мария',
                last_name='Клиентова',
                phone='+7 (999) 000-00-03',
                role='client'
            )
            self.stdout.write('Создан пользователь client@example.com')

        self.stdout.write(self.style.SUCCESS('Готово!'))
