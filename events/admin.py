from django.contrib import admin

from .models import Event, Location, Registration


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'created_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'start_time', 'end_time', 'location', 'seats', 'available_seats', 'created_by', 'created_at'
    )
    list_filter = ('location', 'created_at', 'deleted_at')
    search_fields = ('title', 'description')


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'status', 'created_at')
    list_filter = ('status', 'created_at')

