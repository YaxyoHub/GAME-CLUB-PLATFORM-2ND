from django.contrib import admin
from .models import (
    Club,
    Seat,
    Type_Seat,
    Type_Room,
    Booking,
    Images
)

# Register your models here.
admin.site.register(Club)
admin.site.register(Seat)
admin.site.register(Type_Seat)
admin.site.register(Type_Room)
admin.site.register(Booking)
admin.site.register(Images)