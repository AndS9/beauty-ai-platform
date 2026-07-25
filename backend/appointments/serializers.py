from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            "id",
            "client",
            "master",
            "salon",
            "service",
            "promo_id",
            "appointment_date",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "client", "created_at"]


class RescheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["appointment_date", "start_time", "end_time"]


class CancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = []
