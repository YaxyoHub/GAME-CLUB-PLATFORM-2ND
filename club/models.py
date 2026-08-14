import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Club(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='ID'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clubs',
        verbose_name='Egasi'
    )
    name = models.CharField(max_length=255, verbose_name='Klub nomi')
    region = models.CharField(max_length=100, verbose_name='Viloyat')
    city = models.CharField(max_length=100, verbose_name='Shahar')
    address = models.CharField(max_length=255, verbose_name='Manzil')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Kenglik (latitude)')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Uzunlik (longitude)')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    phone2 = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Telefon 2 (ixtiyoriy)'
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    profile_photo = models.ImageField(
        upload_to='clubs/photos/',
        blank=True,
        null=True,
        verbose_name='Profil rasmi'
    )
    working_hours_from = models.TimeField(verbose_name='Ish vaqti (boshlanish)')
    working_hours_to = models.TimeField(verbose_name='Ish vaqti (tugash)')
    is_active = models.BooleanField(default=True, verbose_name='Faolmi?')

    class Meta:
        verbose_name = 'Klub'
        verbose_name_plural = 'Klublar'
        ordering = ['-id']

    def __str__(self):
        return f"{self.name} ({self.city})"


class Seat(models.Model):

    class SeatType(models.TextChoices):
        PS = 'ps', 'PlayStation'
        PC = 'pc', 'PC'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='ID'
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='seats',
        verbose_name='Klub'
    )
    name = models.CharField(max_length=100, verbose_name='Nomi')
    type = models.CharField(
        max_length=2,
        choices=SeatType.choices,
        verbose_name='Turi'
    )
    hourly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Soatlik narx'
    )
    is_booked = models.BooleanField(default=False, verbose_name='Bron qilinganmi?')
    is_active = models.BooleanField(default=True, verbose_name='Faolmi?')

    class Meta:
        verbose_name = "O'rindiq"
        verbose_name_plural = "O'rindiqlar"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.club.name}"


class Booking(models.Model):

    class Status(models.TextChoices):
        BOOKED   = 'booked',   'Bron qilingan'
        PLAYING  = 'playing',  "O'ynalmoqda"
        FINISHED = 'finished', 'Tugagan'

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        verbose_name='ID'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Foydalanuvchi'
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="O'rindiq"
    )
    date = models.DateField(verbose_name='Sana')
    start_time = models.TimeField(verbose_name='Boshlanish vaqti')
    end_time = models.TimeField(verbose_name='Tugash vaqti')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BOOKED,
        verbose_name='Holat'
    )
    payment_method = models.CharField(max_length=50, verbose_name="To'lov usuli")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')

    class Meta:
        verbose_name = 'Bron'
        verbose_name_plural = 'Bronlar'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.id} - {self.status}"