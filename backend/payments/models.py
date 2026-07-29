from django.db import models


class PaymentMethod(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    APPLE_PAY = "apple_pay", "Apple Pay"
    GOOGLE_PAY = "google_pay", "Google Pay"


class Payment(models.Model):
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="UAH")
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return (
            f"Appointment #{self.appointment_id} - "
            f"{self.amount} {self.currency} "
            f"({self.get_payment_method_display()})"
        )
