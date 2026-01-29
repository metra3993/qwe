from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для модели пользователя с email вместо username"""

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с ролями"""

    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('manager', 'Менеджер заказов'),
        ('admin', 'Администратор'),
    ]

    # Делаем username необязательным, используем email для входа
    username = models.CharField('Логин', max_length=150, blank=True, null=True)
    email = models.EmailField('Email', unique=True)

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )
    phone = models.CharField(
        'Телефон',
        max_length=20,
        blank=True,
        default=''
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_role_display()})"

    def is_client(self):
        return self.role == 'client'

    def is_manager(self):
        return self.role == 'manager'

    def is_admin_user(self):
        return self.role == 'admin'


class Address(models.Model):
    """Адрес доставки пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Пользователь'
    )
    name = models.CharField('Название адреса', max_length=100, help_text='Например: Дом, Работа')
    street = models.CharField('Улица', max_length=200)
    house = models.CharField('Дом', max_length=20)
    entrance = models.CharField('Подъезд', max_length=10, blank=True)
    floor = models.CharField('Этаж', max_length=10, blank=True)
    apartment = models.CharField('Квартира/Офис', max_length=20, blank=True)
    comment = models.TextField('Комментарий к адресу', blank=True, help_text='Например: домофон не работает')
    is_default = models.BooleanField('Адрес по умолчанию', default=False)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name}: {self.street}, д.{self.house}"

    def get_full_address(self):
        """Полный адрес строкой"""
        parts = [f"{self.street}, д.{self.house}"]
        if self.entrance:
            parts.append(f"подъезд {self.entrance}")
        if self.floor:
            parts.append(f"этаж {self.floor}")
        if self.apartment:
            parts.append(f"кв./оф. {self.apartment}")
        return ", ".join(parts)

    def save(self, *args, **kwargs):
        # Если адрес помечен как основной, снимаем метку с остальных
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
