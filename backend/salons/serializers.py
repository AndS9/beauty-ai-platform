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
            "opening_time",
            "closing_time",
            "opened_date",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id"]
