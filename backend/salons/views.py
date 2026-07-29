from rest_framework import generics

from .models import Salon
from .serializers import SalonSerializer
from .permissions import IsAdminOrReadOnlyAll


class SalonListCreateView(generics.ListCreateAPIView):
    """
    GET /api/salons/ — list of all salons, accessible to anyone (even without authorization)
    POST /api/salons/ — create a new salon, only for admins (is_staff)

    TODO: when the master verification system is ready (Master.is_verified) —
    perhaps allow also verified masters, not only is_staff
    """

    queryset = Salon.objects.prefetch_related("masters")
    serializer_class = SalonSerializer
    permission_classes = [IsAdminOrReadOnlyAll]


class SalonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/salons/<id>/ — details of one salon, accessible to anyone
    PATCH /api/salons/<id>/ — editing, only for admins (is_staff)
    DELETE /api/salons/<id>/ — deletion, only for admins (is_staff)
    """

    queryset = Salon.objects.prefetch_related("masters")
    serializer_class = SalonSerializer
    permission_classes = [IsAdminOrReadOnlyAll]
