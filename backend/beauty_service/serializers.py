from rest_framework import serializers
from salons.models import Salon
from users.models import Master

from .models import Service


class SalonServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = (
            "id",
            "name"
        )

class MasterServicesSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    class Meta:
        model = Master
        fields = (
            "id",
            "first_name",
            "last_name",
            "average_rating",
        )


class ServicesSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)
    salons = SalonServiceSerializer(source="masters.salons", many=True, read_only=True)
    masters = MasterServicesSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "category",
            "price",
            "duration_minutes",
            "salons",
            "masters",
            "image",
        )
