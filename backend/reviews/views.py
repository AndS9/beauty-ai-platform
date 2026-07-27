from rest_framework import generics, permissions, serializers

from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
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


class ReviewDetailView(generics.RetrieveAPIView):
    """
    GET /api/reviews/<id>/ — details of one review, available to anyone.
    Editing and deleting reviews is not yet provided.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
