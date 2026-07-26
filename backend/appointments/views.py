from datetime import datetime, timedelta

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    serializers
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    RescheduleSerializer,
    CancelSerializer
)

from beauty_service.models import Service
from salons.models import Salon


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

    serializer_class = RescheduleSerializer
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

    serializer_class = CancelSerializer
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


class AvailableSlotsView(APIView):
    """
    GET /api/appointments/available-slots/?salon=1&master=3&service=5&date=2026-08-01

    Returns a list of available time slots for booking.
    Required query params:
      - salon   — salon id (to get working hours)
      - master  — master id (to get already booked intervals)
      - service — service id (to get slot duration)
      - date    — date in YYYY-MM-DD format

    Response: [{"start": "10:00", "end": "10:45"}, {"start": "10:45", "end": "11:30"}, ...]
    """

    permission_classes = [IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def get(self, request) -> Response:
        salon_id = request.query_params.get("salon")
        master_id = request.query_params.get("master")
        service_id = request.query_params.get("service")
        date_str = request.query_params.get("date")

        if not all([salon_id, master_id, service_id, date_str]):
            raise serializers.ValidationError(
                "Потрібно передати параметри: salon, master, service, date."
            )

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise serializers.ValidationError("Невірний формат date, очікується YYYY-MM-DD.")

        try:
            salon = Salon.objects.get(pk=salon_id)
        except Salon.DoesNotExist:
            raise serializers.ValidationError("Салон з таким id не знайдено.")

        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Послугу з таким id не знайдено.")

        duration = timedelta(minutes=service.duration_minutes)

        # already booked intervals for this master on this date (canceled ones are excluded)
        busy_appointments = Appointment.objects.filter(
            master_id=master_id,
            appointment_date=target_date,
        ).exclude(status="cancelled").order_by("start_time")

        busy_intervals = [
            (
                datetime.combine(target_date, a.start_time),
                datetime.combine(target_date, a.end_time),
            )
            for a in busy_appointments
        ]

        work_start = datetime.combine(target_date, salon.opening_time)
        work_end = datetime.combine(target_date, salon.closing_time)

        slots = []
        cursor = work_start

        while cursor + duration <= work_end:
            slot_end = cursor + duration

            # check whether this slot overlaps with any busy interval
            overlaps = any(
                cursor < busy_end and slot_end > busy_start
                for busy_start, busy_end in busy_intervals
            )

            if not overlaps:
                slots.append(
                    {
                        "start": cursor.time().strftime("%H:%M"),
                        "end": slot_end.time().strftime("%H:%M"),
                    }
                )
                cursor = slot_end
            else:
                # shift forward by 5 minutes and try again
                cursor += timedelta(minutes=5)

        return Response(slots)
