from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from .managers import UserManager
from phonenumber_field.modelfields import PhoneNumberField

from .services.media_path import generate_upload_path


class GenderChoice(models.TextChoices):
    MAN = "man", "Man"
    WOMAN = "woman", "Woman"


class User(AbstractUser):
    username = None
    first_name = models.CharField(
        _("first name"),
        max_length=150,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
    )
    email = models.EmailField(_("email address"), unique=True)
    phone = PhoneNumberField(
        unique=True,
    )
    photo = models.ImageField(
        upload_to=generate_upload_path,
        null=True,
        blank=True,
    )
    google_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )
    gender = models.CharField(
        max_length=10,
        choices=GenderChoice.choices,
        blank=True,
        null=True,
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
    )
    preferred_salons = models.ManyToManyField(
        "salons.Salon",
        blank=True,
        related_name="followers",
    )
    last_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    last_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    registration_date_user = models.DateTimeField(
        auto_now_add=True,
    )
    last_update_user = models.DateTimeField(
        auto_now=True,
    )

    @property
    def is_master(self):
        return hasattr(self, "master")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})" if self.get_full_name() else self.email


class MasterStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    BLOCKED = "blocked", "Blocked"
    DELETED = "deleted", "Deleted"
    PENDING = "pending", "Pending"


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
    bio = models.TextField(
        null=True,
        blank=True,
    )
    years_of_experience = models.PositiveIntegerField()
    registration_date_master = models.DateTimeField(
        auto_now_add=True,
    )
    last_update_master = models.DateTimeField(
        auto_now=True,
    )
    account_status = models.CharField(
        max_length=20,
        choices=MasterStatus.choices,
        default=MasterStatus.PENDING,
    )

    @property
    def active_services(self):
        return self.services.filter(is_active=True)

    @property
    def average_rating(self) -> float:
        return self.reviews_received.aggregate(
            average=Avg("rating")
        )["average"]

    @property
    def total_reviews(self) -> int:
        return self.reviews_received.count()

    @property
    def is_independent(self):
        return not self.salons.exists()

    def __str__(self):
        name = self.user.get_full_name() or self.user.email
        return (
            f"{name} — {self.specialization}"
            if self.specialization
            else name
        )


class WeekDay(models.IntegerChoices):
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"


class WorkingSchedule(models.Model):
    master = models.ForeignKey(
        "Master",
        on_delete=models.CASCADE,
        related_name="working_schedule",
    )
    weekday = models.PositiveSmallIntegerField(
        choices=WeekDay.choices,
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
    )
    is_day_off = models.BooleanField(default=False)

    def clean(self):
        super().clean()

        if self.is_day_off:
            self.start_time = None
            self.end_time = None
            return

        if self.start_time is None or self.end_time is None:
            raise ValidationError(
                "start_time and end_time are required."
            )

        if self.start_time >= self.end_time:
            raise ValidationError(
                "start_time must be before end_time."
            )

        overlapping = WorkingSchedule.objects.filter(
            master=self.master,
            weekday=self.weekday,
            is_day_off=False,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                "Working schedule overlaps with an existing schedule."
            )

    class Meta:
        ordering = ("weekday", "start_time")

    def __str__(self):
        if self.is_day_off:
            return f"{self.master} - {self.get_weekday_display()} (Day off)"

        return (
            f"{self.master} - "
            f"{self.get_weekday_display()} "
            f"{self.start_time}-{self.end_time}"
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class MasterSalon(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="master_salons",
    )
    salon = models.ForeignKey(
        "salons.Salon",
        on_delete=models.CASCADE,
        related_name="master_salons",
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["master", "salon"],
                name="unique_master_salon",
            )
        ]

    def __str__(self):
        return f"{self.master} @ {self.salon}"


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
