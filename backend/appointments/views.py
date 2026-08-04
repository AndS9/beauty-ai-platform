from datetime import (
    datetime,
    timedelta
)

from django.db.models import QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    serializers
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework import status as http_status

from users.permissions import IsMaster
from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    RescheduleSerializer,
    CancelSerializer,
    MasterStatusUpdateSerializer,
    MasterAppointmentListSerializer,
)
from .filters import MasterAppointmentFilter

from beauty_service.models import Service
from salons.models import Salon

from tasks.notification import send_email_task


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
                "Неможливо перенести бронювання зі статусом '%s'." % appointment.status
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
        working_hours_by_weekday = {wh.weekday: wh for wh in salon.working_hours.all()}

        result = {}
        current_date = date_from

        while current_date <= date_to:
            weekday = (
                current_date.weekday()
            )  # Monday=0 ... Sunday=6, matches our choices
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
                Appointment.objects.filter(
                    master_id=master_id, appointment_date=current_date
                )
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


class StatusTransitionConflict(APIException):
    status_code = http_status.HTTP_409_CONFLICT
    default_detail = "Недопустимий перехід статусу."
    default_code = "status_transition_conflict"


class MasterUpdateAppointmentStatusView(generics.UpdateAPIView):
    """
    PATCH /api/appointments/<id>/status/

    Allows a master to update the status of their booking.
    Request body: {"status": "confirmed"}
    For status "canceled", cancellation_reason is required.

    Allowed transitions:
    pending -> confirmed, canceled
    confirmed -> completed, canceled
    completed -> (nothing, status final)
    canceled -> (nothing, status final)
    """

    ALLOWED_TRANSITIONS = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["in_progress", "cancelled"],
        "in_progress": ["completed"],
        "completed": [],
        "cancelled": [],
    }

    serializer_class = MasterStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self) -> QuerySet[Appointment]:
        # master can update only appointments assigned to them
        return Appointment.objects.filter(master__user=self.request.user)

    def perform_update(self, serializer) -> None:
        appointment = self.get_object()
        new_status = serializer.validated_data.get("status")
        current_status = appointment.status

        allowed_next_statuses = self.ALLOWED_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_next_statuses:
            raise StatusTransitionConflict(
                "Неможливо перевести бронювання зі статусу '%s' у статус '%s'."
                % (current_status, new_status)
            )

        if new_status == "completed":
            serializer.save(completed_at=timezone.now())
        else:
            serializer.save()

        send_email_task.delay(
            recipient=appointment.client.email,
            subject="Оновлення статусу вашого запису",
            context={
                "customer_name": appointment.client.get_full_name() or appointment.client.email,
                "booking_status": appointment.get_status_display(),
                "salon_name": appointment.salon.name,
                "master_name": appointment.master.user.get_full_name() or appointment.master.user.email,
                "service_name": appointment.service.name,
                "booking_date": appointment.appointment_date.isoformat(),
                "booking_time": appointment.start_time.strftime("%H:%M"),
                "notification_message": "Статус вашого запису оновлено на '%s'." % appointment.get_status_display(),
            },
        )


class MasterAppointmentListView(generics.ListAPIView):
    """
    GET /api/appointments/master/active/

    Returns active appointments (pending, confirmed, in_progress) assigned to
    the currently authenticated master.

    Filters: ?appointment_date=2026-08-01&status=confirmed&client=<email substring>&service=<name substring>
    Sorting: ?ordering=appointment_date | created_at | status | service__price (add "-" for descending)
    Pagination: ?page=2
    """

    serializer_class = MasterAppointmentListSerializer
    permission_classes = [IsMaster]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MasterAppointmentFilter
    ordering_fields = ["appointment_date", "created_at", "status", "service__price"]
    ordering = ["-appointment_date"]

    def get_queryset(self) -> QuerySet[Appointment]:
        return Appointment.objects.filter(
            master__user=self.request.user,
            status__in=["pending", "confirmed", "in_progress"],
        ).select_related("client", "service", "salon")

    def filter_queryset(self, queryset) -> QuerySet[Appointment]:
        # validate filter params explicitly, so invalid values return 400
        # instead of being silently ignored
        filterset = self.filterset_class(self.request.query_params, queryset=queryset)
        if not filterset.is_valid():
            raise serializers.ValidationError(filterset.errors)
        queryset = filterset.qs

        # validate the "ordering" param against the allowed fields
        ordering_param = self.request.query_params.get("ordering")
        if ordering_param:
            requested_fields = [f.lstrip("-") for f in ordering_param.split(",")]
            invalid_fields = [f for f in requested_fields if f not in self.ordering_fields]
            if invalid_fields:
                raise serializers.ValidationError(
                    {"ordering": "Недопустимі поля сортування: %s" % ", ".join(invalid_fields)}
                )

        return super().filter_queryset(queryset)
