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


class MasterStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status", "cancellation_reason"]

    def validate(self, attrs):
        status = attrs.get("status")
        cancellation_reason = attrs.get("cancellation_reason")

        if status == "cancelled" and not cancellation_reason:
            raise serializers.ValidationError(
                {"cancellation_reason": "Причина скасування обов'язкова при статусі 'cancelled'."}
            )

        return attrs
