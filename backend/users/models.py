from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    google_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    objects = UserManager()
