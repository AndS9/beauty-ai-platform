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


class MasterAppointmentListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(source="service.name", read_only=True)
    duration_minutes = serializers.IntegerField(source="service.duration_minutes", read_only=True)
    total_price = serializers.DecimalField(source="service.price", max_digits=8, decimal_places=2, read_only=True)
    salon_name = serializers.CharField(source="salon.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "appointment_date",
            "start_time",
            "client_name",
            "service_name",
            "status",
            "duration_minutes",
            "total_price",
            "salon_name",
            "created_at",
        ]

    def get_client_name(self, obj) -> str:
        return obj.client.get_full_name() or obj.client.email
