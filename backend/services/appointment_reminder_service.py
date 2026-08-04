import logging
from datetime import timedelta

from appointments.models import Appointment, AppointmentReminder
from django.db import transaction
from django.utils import timezone

from services.email_service import EmailService

logger = logging.getLogger(__name__)


class AppointmentReminderService:
    @staticmethod
    def _send_reminders(
        reminder_type: str = AppointmentReminder.ReminderType.ONE_HOUR,
        delta_time: timedelta = timedelta(hours=1),
        subject: str = "Appointment Reminder - 1 Hour",
    ) -> None:
        now = timezone.now()

        target = now + delta_time
        margin = timedelta(minutes=5)

        window_start = target - margin
        window_end = target + margin

        target_appointments = Appointment.objects.filter(
            status="confirmed",
            start__gte=window_start,
            start__lte=window_end,
        ).select_related(
            "client",
            "master",
            "service",
            "salon",
        )
        for appointment in target_appointments:
            with transaction.atomic():
                reminder, _ = AppointmentReminder.objects.get_or_create(
                    appointment=appointment,
                    reminder_type=reminder_type,
                )
                if reminder.status == AppointmentReminder.Status.SENT:
                    continue
                context = {
                    "appointment_id": appointment.id,
                    "appointment_date": appointment.start.date(),
                    "appointment_time": appointment.start.time(),
                    "service": appointment.service.name,
                    "master": appointment.master.user.get_full_name(),
                    "salon": appointment.salon.name,
                    "address": appointment.salon.address,
                    "status": appointment.status,
                }
                try:
                    EmailService.send_email(
                        recipient=appointment.client.email,
                        subject=subject,
                        context=context,
                    )
                    EmailService.send_email(
                        recipient=appointment.master.user.email,
                        subject=subject,
                        context=context,
                    )
                except Exception:
                    reminder.status = AppointmentReminder.Status.FAILED
                    logger.exception(
                        "Failed to send reminder",
                    )
                else:
                    reminder.status = AppointmentReminder.Status.SENT
                    reminder.sent_at = now
                    logger.info(
                        f"{reminder_type} reminder sent",
                        extra={
                            "appointment": appointment.id,
                            "type": reminder_type,
                        },
                    )
                reminder.save()

    @staticmethod
    def send_1h_reminders() -> None:
        AppointmentReminderService._send_reminders(
            reminder_type=AppointmentReminder.ReminderType.ONE_HOUR,
            delta_time=timedelta(hours=1),
            subject="Appointment Reminder - 1 Hour",
        )

    @staticmethod
    def send_24h_reminders() -> None:
        AppointmentReminderService._send_reminders(
            reminder_type=AppointmentReminder.ReminderType.TWENTY_FOUR_HOURS,
            delta_time=timedelta(hours=24),
            subject="Appointment Reminder - 24 Hours",
        )
