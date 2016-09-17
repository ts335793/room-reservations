from django.contrib import admin
from room_reservations.models import Room, FreeTerm, Reservation


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'description')


class FreeTermAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'from_hour', 'to_hour')


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'date', 'from_hour', 'to_hour')


admin.site.register(Room, RoomAdmin)
admin.site.register(FreeTerm, FreeTermAdmin)
admin.site.register(Reservation, ReservationAdmin)