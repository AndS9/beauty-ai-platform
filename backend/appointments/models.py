from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("in_progress", "In progress"),
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
    start = models.DateTimeField(
        null=True,
        blank=True,
    )
    end = models.DateTimeField(
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    cancellation_reason = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "appointments"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="appointments_check",
            ),
        ]

    # class Meta:
    #     db_table = "appointments"
    #     constraints = (
    #         models.CheckConstraint(
    #             condition=models.Q(end__gt=models.F("start")),
    #             name="appointments_check",
    #         ),
    #     )

    # def __str__(self) -> str:
    #     return f"Appointment #{self.id} — ({self.start} to {self.end})"

    def __str__(self) -> str:
        return f"Appointment #{self.id} — {self.appointment_date} {self.start_time}"

    def save(self, *args, **kwargs):  # костиль
        self.start = timezone.make_aware(
            datetime.combine(self.appointment_date, self.start_time)
        )
        self.end = timezone.make_aware(
            datetime.combine(self.appointment_date, self.end_time)
        )

        super().save(*args, **kwargs)


class AppointmentReminder(models.Model):
    class ReminderType(models.TextChoices):
        ONE_HOUR = "1h", "1 hour"
        TWENTY_FOUR_HOURS = "24h", "24 hours"

    class Status(models.TextChoices):
        PENDING = "pending"
        SENT = "sent"
        FAILED = "failed"

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="reminders",
    )

    reminder_type = models.CharField(
        max_length=10,
        choices=ReminderType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["appointment", "reminder_type"],
                name="unique_reminder_type_per_appointment",
            ),
        )
