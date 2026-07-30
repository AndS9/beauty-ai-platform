from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "master",
        "salon",
        "service",
        "appointment_date",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = ("status", "appointment_date")
    search_fields = ("client__email", "master__user__email")
