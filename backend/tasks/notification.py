from celery import shared_task

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email_task(
        recipient: str,
        subject: str,
        context: dict,
        template_name: str = "emails/notification.html",
        body: str | None = None,
) -> None:
    html = render_to_string(template_name, context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=body or "Your email client does not support HTML emails.",
        to=[recipient],
    )

    message.attach_alternative(html, "text/html")
    message.send()
