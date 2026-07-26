from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from .managers import UserManager
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    phone = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
    )
    google_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Master(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="master",
    )
    specialization = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    services = models.ManyToManyField(
        "beauty_service.Service",
        through="MasterService",
        related_name="masters",
    )


class MasterService(models.Model):
    master = models.ForeignKey(
        "Master",
        on_delete=models.CASCADE,
        related_name="master_services",
    )

    service = models.ForeignKey(
        "beauty_service.Service",
        on_delete=models.CASCADE,
        related_name="master_services",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["master", "service"],
                name="unique_master_service",
            )
        ]
