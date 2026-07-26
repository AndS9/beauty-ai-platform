from celery import shared_task

from services.email_service import send_email


@shared_task
def send_email_task(
        recipient: str,
        subject: str,
        context: dict,
        template_name: str = "emails/notification.html",
        body: str | None = None,
) -> None:
    send_email(
        recipient=recipient,
        subject=subject,
        context=context,
        template_name=template_name,
        body=body,
    )
