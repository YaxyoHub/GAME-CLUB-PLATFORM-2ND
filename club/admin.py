from django.contrib import admin
from .models import (
    Club,
    Seat,
    Type_Seat,
    Type_Room,
    Booking,
    Images,
    Card
)


class ImagesInline(admin.TabularInline):
    model = Images
    extra = 1


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'region',
        'city',
        'phone',
        'working_hours_from',
        'working_hours_to',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'region', 'city', 'created_at')
    search_fields = ('name', 'city', 'region', 'address', 'owner__username', 'phone')
    ordering = ('-created_at',)
    list_editable = ('is_active',)
    inlines = [ImagesInline]

    fieldsets = (
        ("Asosiy Ma'lumotlar", {
            'fields': ('name', 'owner', 'profile_photo', 'description', 'is_active')
        }),
        ("Joylashuv va Aloqa", {
            'fields': ('region', 'city', 'address', 'latitude', 'longitude', 'phone', 'phone2')
        }),
        ("Ish vaqti", {
            'fields': ('working_hours_from', 'working_hours_to')
        }),
    )


@admin.register(Type_Seat)
class TypeSeatAdmin(admin.ModelAdmin):
    list_display = ('type_title', 'club')
    list_filter = ('club',)
    search_fields = ('type_title', 'club__name')


@admin.register(Type_Room)
class TypeRoomAdmin(admin.ModelAdmin):
    list_display = ('type_title', 'club')
    list_filter = ('club',)
    search_fields = ('type_title', 'club__name')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'type_seat', 'type_room', 'hourly_price', 'is_booked', 'is_active')
    list_filter = ('is_active', 'is_booked', 'club', 'type_seat', 'type_room')
    search_fields = ('name', 'club__name')
    list_editable = ('is_booked', 'is_active', 'hourly_price')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'seat',
        'date',
        'start_time',
        'end_time',
        'status',
        'payment_method',
        'created_at'
    )
    list_filter = ('status', 'date', 'payment_method', 'created_at')
    search_fields = ('user__username', 'seat__name', 'seat__club__name')
    list_editable = ('status',)
    ordering = ('-created_at',)


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'club', 'created_at')
    list_filter = ('club',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment')