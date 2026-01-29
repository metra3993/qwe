from django.db import models
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    """Модель категории продуктов"""
    name = models.CharField('Категория', max_length=100, unique=True)
    slug = models.SlugField('URL', unique=True)
    icon = models.CharField('Иконка (emoji)', max_length=10, default='🛒')
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель продукта"""

    UNIT_CHOICES = [
        ('kg', 'кг'),
        ('g', 'г'),
        ('l', 'л'),
        ('ml', 'мл'),
        ('pcs', 'шт'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    name = models.CharField('Название', max_length=200)
    brand = models.CharField('Производитель', max_length=100, blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    # Единица измерения и количество
    unit = models.CharField(
        'Единица измерения',
        max_length=10,
        choices=UNIT_CHOICES,
        default='pcs'
    )
    quantity = models.DecimalField(
        'Количество/Вес',
        max_digits=8,
        decimal_places=2,
        default=1
    )

    # Скидки
    discount_percent = models.IntegerField('Скидка (%)', default=0)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, blank=True, null=True)

    # Описание
    description = models.TextField('Описание', blank=True)
    ingredients = models.TextField('Состав', blank=True)
    nutritional_value = models.TextField('Пищевая ценность', blank=True)

    # Характеристики
    country_origin = models.CharField('Страна происхождения', max_length=100, blank=True)
    expiry_date = models.CharField('Срок годности', max_length=100, blank=True)
    storage_conditions = models.CharField('Условия хранения', max_length=200, blank=True)

    # Наличие
    stock = models.IntegerField('Остаток на складе', default=0)
    is_available = models.BooleanField('В наличии', default=True)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    is_new = models.BooleanField('Новинка', default=False)
    is_organic = models.BooleanField('Органический продукт', default=False)

    # Даты
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.get_unit_display()})"

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'pk': self.pk})

    @property
    def main_image(self):
        """Получить главное изображение"""
        return self.images.filter(is_main=True).first() or self.images.first()

    @property
    def final_price(self):
        """Получить финальную цену с учетом скидки"""
        if self.discount_percent > 0:
            return self.price * (100 - self.discount_percent) / 100
        return self.price


class ProductImage(models.Model):
    """Модель изображения продукта"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Продукт'
    )
    image = models.ImageField('Изображение', upload_to='products/')
    is_main = models.BooleanField('Главное изображение', default=False)
    order = models.IntegerField('Порядок', default=0)
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'Изображение продукта'
        verbose_name_plural = 'Изображения продуктов'
        ordering = ['order', '-is_main']

    def __str__(self):
        return f"Изображение {self.product}"

    def save(self, *args, **kwargs):
        # Если это главное изображение, убрать флаг у остальных
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """Модель избранных продуктов"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Продукт'
    )
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product}"
