from django.db.models import Count, Q
from django.views import generic
from django_filters import OrderingFilter
from users.models import MasterStatus

from .models import Services
from .serializers import ServicesSerializer


class ServicesListView(generic.ListAPIView):
    serializer_class = (ServicesSerializer,)
    filter_backends = (OrderingFilter,)

    ordering_fields = (
        "name",
        "popularity",
        "price",
        "duration_minutes",
    )

    def get_queryset(self):
        return (
            Services.objects.filter(
                is_active=True, masters__account_status=MasterStatus.ACTIVE
            )
            .annotate(
                popularity=Count(
                    "masters__master_appointments",
                    filter=Q(masters__master_appointments__status="completed"),
                    distinct=True,
                )
            )
            .distinct()
        )
