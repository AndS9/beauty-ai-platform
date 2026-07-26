from django.conf import settings
from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No show"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="client_appointments",
        on_delete=models.CASCADE,
    )
    master = models.ForeignKey(
        "users.Master",
        related_name="master_appointments",
        on_delete=models.CASCADE,
    )
    salon = models.ForeignKey(
        "salons.Salon",
        related_name="appointments",
        on_delete=models.CASCADE,
        db_column="salon_id",
    )
    service = models.ForeignKey(
        "beauty_service.Service",
        related_name="appointments",
        on_delete=models.CASCADE,
        db_column="service_id",
    )
    promo_id = models.IntegerField(null=True, blank=True)
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "appointments"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="appointments_check",
            ),
        ]

    def __str__(self) -> str:
        return f"Appointment #{self.id} — {self.appointment_date} {self.start_time}"
