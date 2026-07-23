from typing import Any, Mapping

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email(
        recipient: str,
        subject: str,
        context: Mapping[str, Any],
        template_name: str = "emails/notification.html",
        body: str | None = None,
) -> None:
    """
    Send an HTML email using the configured SMTP server.

    Args:
        recipient: Recipient email address.
        subject: Email subject.
        context: Context passed to the Django template.
        template_name: Path to the HTML template.
        body: Plain-text fallback for email clients without HTML support.
    """
    html = render_to_string(template_name, context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=body or "Your email client does not support HTML emails.",
        to=[recipient],
    )

    message.attach_alternative(html, "text/html")
    message.send()


if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    send_email(
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
