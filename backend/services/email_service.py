from tasks.notification import send_email_task


class EmailService:
    @staticmethod
    def send_email(
            recipient: str,
            subject: str,
            context: dict,
            template_name: str = "emails/notification.html",
            body: str | None = None,
    ) -> None:
        send_email_task.delay(
            recipient=recipient,
            subject=subject,
            context=context,
            template_name=template_name,
            body=body,
        )


if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    EmailService.send_email(
        recipient="example@gmail.com",
        subject="Test email",
        context={
            "customer_name": "Oleksandr",
            "booking_status": "Confirmed",
            "salon_name": "Beauty Studio",
            "master_name": "Anna",
            "service_name": "Haircut",
            "booking_date": "2026-07-23",
            "booking_time": "15:30",
            "duration": "1 hour",
            "price": "500 UAH",
            "notification_message": "Your booking has been confirmed.",
        },
    )
