from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    serializers
)
from rest_framework.permissions import IsAuthenticated

from .models import Appointment
from .serializers import AppointmentSerializer


class ClientAppointmentListView(generics.ListAPIView):
    """
    GET /api/appointments/my/

    List of reservations for the currently authenticated client.
    Supports:
      - filter by status:  ?status=confirmed
      - sort:         ?ordering=appointment_date  (або -appointment_date)
      - pagination:          ?page=2
    """

    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["appointment_date", "start_time", "created_at"]
    ordering = ["-appointment_date"]  # default sorting: newest first

    def get_queryset(self) -> QuerySet[Appointment]:
        # show only the bookings of the client who is currently logged in
        return Appointment.objects.filter(client=self.request.user)


class RescheduleAppointmentView(generics.UpdateAPIView):
    """
    PATCH /api/appointments/<id>/reschedule/

    Moves an existing customer reservation to a new date/time.
    Request body: {"appointment_date": "2026-08-01", "start_time": "14:00", "end_time": "15:00"}
    """

    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self) -> QuerySet[Appointment]:
        # customer can only transfer their own bookings
        return Appointment.objects.filter(client=self.request.user)

    def perform_update(self, serializer) -> None:
        appointment = self.get_object()
        if appointment.status in ["cancelled", "completed"]:
            raise serializers.ValidationError(
                "Неможливо перенести бронювання зі статусом '%s'."
                % appointment.status
            )
        serializer.save(status="pending")


class CancelAppointmentView(generics.UpdateAPIView):
    """
    PATCH /api/appointments/<id>/cancel/

    Cancels the customer's upcoming booking (sets the status to "canceled").
    The request body is optional.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self) -> QuerySet[Appointment]:
        # a customer can only cancel their own bookings
        return Appointment.objects.filter(client=self.request.user)

    def perform_update(self, serializer) -> None:
        appointment = self.get_object()
        if appointment.status in ["cancelled", "completed"]:
            raise serializers.ValidationError(
                "Бронювання зі статусом '%s' вже неможливо скасувати."
                % appointment.status
            )
        serializer.save(status="cancelled")
