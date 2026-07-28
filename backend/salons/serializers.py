from rest_framework import serializers

from .models import Salon


class SalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = [
            "id",
            "name",
            "city",
            "district",
            "address",
            "phone",
            "opened_date",
            "latitude",
            "longitude",
            "owner"
        ]
        read_only_fields = ["id"]
