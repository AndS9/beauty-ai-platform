from tasks.notification import send_email_task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.exceptions import ValidationError


class UserRegistrationService:

    @staticmethod
    def register(validated_data):
        user = get_user_model().objects.create_user(
            **validated_data,
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = (
            f"{settings.BACKEND_URL}/api/user/verify-email/{uid}/{token}/"
        )

        send_email_task.delay(
            recipient=user.email,
            subject="Verify your email",
            context={
                "verification_url": verification_url,
            },
            template_name="emails/verification.html",
        )

        return user


class UserAuthService:

    @staticmethod
    def verify_email(uidb64: str, token: str) -> None:
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=user_id)
        except (
                TypeError,
                ValueError,
                OverflowError,
                get_user_model().DoesNotExist,
        ):
            raise ValidationError("Invalid verification link.")

        if not default_token_generator.check_token(user, token):
            raise ValidationError("Invalid or expired token.")

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        else:
            return
