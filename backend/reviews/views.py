from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    generics,
    permissions,
    serializers
)
from rest_framework.filters import OrderingFilter
from users.permissions import IsMaster

from reviews.filters import MasterReviewFilter

from .models import Review
from .serializers import (
    MasterReviewSerializer,
    ReviewSerializer
)


class ReviewListCreateView(
    generics.ListCreateAPIView
):  # Перевірити, чи дісно потрібна ця view
    """
    GET /api/reviews/ — list of all reviews, available to anyone (even without authorization)
    POST /api/reviews/ — leave a review for your completed booking, authorization required

    Request body for POST: {"appointment": 5, "rating": 4, "comment": "..."}
    client and master are determined automatically from appointment, they do not need to be passed.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self) -> list:
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer) -> None:
        appointment = serializer.validated_data.get("appointment")

        if appointment.client_id != self.request.user.id:
            raise serializers.ValidationError(
                "Можна залишити відгук тільки на власне бронювання."
            )

        if appointment.status != "completed":
            raise serializers.ValidationError(
                "Відгук можна залишити тільки на завершене бронювання."
            )

        serializer.save(client=self.request.user, master=appointment.master)


class ReviewDetailView(
    generics.RetrieveAPIView
):  # Перевірити, чи дісно потрібна ця view
    """
    GET /api/reviews/<id>/ — details of one review, available to anyone.
    Editing and deleting reviews is not yet provided.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]


class MasterReviewQuerysetMixin:
    def get_queryset(self) -> QuerySet[Review]:
        return Review.objects.filter(
            appointment__master=self.request.user.master,
            appointment__status="completed",
        ).select_related(
            "appointment",
            "appointment__client",
            "appointment__service",
        )


class MasterReviewListView(MasterReviewQuerysetMixin, generics.ListAPIView):
    serializer_class = MasterReviewSerializer
    permission_classes = (IsMaster,)
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )
    filterset_class = MasterReviewFilter
    ordering_fields = (
        "created_at",
        "rating",
    )
    ordering = ("-created_at",)


class MasterReviewDetailView(MasterReviewQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = MasterReviewSerializer
    permission_classes = (IsMaster,)
