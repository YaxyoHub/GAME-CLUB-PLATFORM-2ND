from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    """
    Telefon raqami orqali foydalanuvchi yaratuvchi Custom Manager
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqami kiritilishi shart!")
        
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Bot orqali kirganda parol shart emas
            
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    phone_number = models.CharField(max_length=13, unique=True, verbose_name="Telefon raqami")
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ism va Familiya")
    
    # Telegram Bot va qo'shimcha maydonlar
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Telegram ID")
    address = models.TextField(blank=True, null=True, verbose_name="Manzil")
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name="Roli")

    # Django admin va xavfsizlik maydonlari
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.phone_number} - {self.full_name or 'Noma\'lum'}"

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('club manager', 'Club Manager'),
        ('superadmin', 'Super Admin'),
    )

    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
    )

    phone_number = models.CharField(max_length=13, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    telegram_chat_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    payment = models.CharField(max_length=10, choices=PAYMENT_CHOICES, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    tg_username = models.CharField(max_length=150, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.phone_number} - {self.full_name} - {self.role}"
    

class OtpCode(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    phone_number = models.CharField(max_length=13)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        import random
        new_code = str(random.randint(100000, 999999))
        return new_code

    def is_valid(self):
        """Kodni hali amal qilayotgani va ishlatilmaganini tekshirish"""
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

