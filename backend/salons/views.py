from rest_framework import generics, permissions

from .models import Salon
from .serializers import SalonSerializer


class SalonListCreateView(generics.ListCreateAPIView):
    """
    GET /api/salons/ — list of all salons, accessible to anyone (even without authorization)
    POST /api/salons/ — create a new salon, authorization required

    TODO: when the master verification system is ready (Master.is_verified) —
    replace permission with POST from IsAuthenticated to check for a verified master.
    """

    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    def get_permissions(self) -> list:
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class SalonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/salons/<id>/ — details of one salon, accessible to anyone
    PATCH /api/salons/<id>/ — editing, requires authorization
    DELETE /api/salons/<id>/ — deletion, requires authorization

    TODO: the same remark about master verification applies to this view.
    """

    queryset = Salon.objects.all()
    serializer_class = SalonSerializer

    def get_permissions(self) -> list:
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
