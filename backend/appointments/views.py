from datetime import (
    datetime,
    timedelta
)

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
    GET /api/appointments/available-slots/?salon=1&master=3&service=5&date_from=2026-08-01&date_to=2026-08-03

    Returns a list of available time slots for booking, grouped by date.
    Required query params:
      - salon     — salon id (to get working hours)
      - master    — master id (to get already booked intervals)
      - service   — service id (to get slot duration)
      - date_from — start date, format YYYY-MM-DD
      - date_to   — end date, format YYYY-MM-DD (inclusive; if omitted, same as date_from)

    Response:
      {
        "2026-08-01": [{"start": "10:00", "end": "10:45"}, ...],
        "2026-08-02": []   ← empty list if the salon is closed that day
      }
    """

    permission_classes = [IsAuthenticated]

    # noinspection PyMethodMayBeStatic
    def get(self, request) -> Response:
        salon_id = request.query_params.get("salon")
        master_id = request.query_params.get("master")
        service_id = request.query_params.get("service")
        date_from_str = request.query_params.get("date_from")
        date_to_str = request.query_params.get("date_to") or date_from_str

        if not all([salon_id, master_id, service_id, date_from_str]):
            raise serializers.ValidationError(
                "Потрібно передати параметри: salon, master, service, date_from."
            )

        try:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
        except ValueError:
            raise serializers.ValidationError(
                "Невірний формат дати, очікується YYYY-MM-DD."
            )

        if date_to < date_from:
            raise serializers.ValidationError("date_to не може бути раніше date_from.")

        try:
            salon = Salon.objects.get(pk=salon_id)
        except Salon.DoesNotExist:
            raise serializers.ValidationError("Салон з таким id не знайдено.")

        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Послугу з таким id не знайдено.")

        duration = timedelta(minutes=service.duration_minutes)
        step = timedelta(minutes=15)

        # preload the weekly schedule for this salon once, keyed by weekday number
        # noinspection PyUnresolvedReferences
        working_hours_by_weekday = {
            wh.weekday: wh for wh in salon.working_hours.all()
        }

        result = {}
        current_date = date_from

        while current_date <= date_to:
            weekday = current_date.weekday()  # Monday=0 ... Sunday=6, matches our choices
            schedule = working_hours_by_weekday.get(weekday)

            # if there is no schedule entry for this weekday, or the salon
            # is marked as closed, there are simply no slots that day
            # noinspection PyUnresolvedReferences
            if schedule is None or schedule.is_closed:
                result[current_date.isoformat()] = []
                current_date += timedelta(days=1)
                continue

            # already booked intervals for this master on this date (canceled ones are excluded)
            busy_appointments = (
                Appointment.objects.filter(master_id=master_id, appointment_date=current_date)
                .exclude(status="cancelled")
                .order_by("start_time")
            )

            busy_intervals = [
                (
                    datetime.combine(current_date, a.start_time),
                    datetime.combine(current_date, a.end_time),
                )
                for a in busy_appointments
            ]

            # noinspection PyUnresolvedReferences
            work_start = datetime.combine(current_date, schedule.opening_time)
            # noinspection PyUnresolvedReferences
            work_end = datetime.combine(current_date, schedule.closing_time)

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

                # always move forward by a fixed step, regardless of whether
                # the slot was free or not
                cursor += step

            result[current_date.isoformat()] = slots
            current_date += timedelta(days=1)

        return Response(result)
