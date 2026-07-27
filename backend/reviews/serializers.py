from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "appointment",
            "client",
            "master",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "client", "master", "created_at"]
