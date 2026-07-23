from celery import shared_task

from services.email_service import send_email


@shared_task
def send_email_task(
        recipient: str,
        subject: str,
        context: dict,
) -> None:
    send_email(
        recipient=recipient,
        subject=subject,
        context=context,
    )
