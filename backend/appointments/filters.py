import django_filters

from .models import Appointment


class MasterAppointmentFilter(django_filters.FilterSet):
    appointment_date = django_filters.DateFilter()
    status = django_filters.CharFilter()
    client = django_filters.CharFilter(
        field_name="client__email",
        lookup_expr="icontains",
    )
    service = django_filters.CharFilter(
        field_name="service__name",
        lookup_expr="icontains",
    )

    class Meta:
        model = Appointment
        fields = ["appointment_date", "status", "client", "service"]


class MasterAppointmentHistoryFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="appointment_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="appointment_date", lookup_expr="lte")
    status = django_filters.CharFilter()
    client = django_filters.CharFilter(
        field_name="client__email",
        lookup_expr="icontains",
    )
    service = django_filters.CharFilter(
        field_name="service__name",
        lookup_expr="icontains",
    )

    class Meta:
        model = Appointment
        fields = ["date_from", "date_to", "status", "client", "service"]
