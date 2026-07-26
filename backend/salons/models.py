from django.db import models


class Salon(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    opened_date = models.DateField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = "salons"
        constraints = [
            models.UniqueConstraint(fields=["name", "address"], name="unique_salon_name_address"),
        ]

    def __str__(self) -> str:
        return self.name


class SalonWorkingHours(models.Model):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    WEEKDAY_CHOICES = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]

    salon = models.ForeignKey(
        Salon,
        related_name="working_hours",
        on_delete=models.CASCADE,
    )
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    is_closed = models.BooleanField(default=False)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "salon_working_hours"
        constraints = [
            models.UniqueConstraint(
                fields=["salon", "weekday"], name="unique_salon_weekday"
            ),
        ]

    # noinspection PyUnresolvedReferences
    def __str__(self) -> str:
        if self.is_closed:
            return f"{self.salon.name} — {self.get_weekday_display()}: closed"
        return f"{self.salon.name} — {self.get_weekday_display()}: {self.opening_time}-{self.closing_time}"
