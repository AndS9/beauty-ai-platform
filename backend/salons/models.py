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
