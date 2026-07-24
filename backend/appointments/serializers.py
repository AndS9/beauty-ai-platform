from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "client",
            "master",
            "salon_id",
            "service_id",
            "promo_id",
            "appointment_date",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "client", "created_at"]
