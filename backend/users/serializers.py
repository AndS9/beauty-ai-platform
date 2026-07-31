from django.contrib.auth import get_user_model
from rest_framework import serializers

from beauty_service.models import Service
from users.models import Master, WorkingSchedule
from users.services.auth_service import UserRegistrationService
from phonenumber_field.serializerfields import PhoneNumberField

from salons.models import Salon


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "phone",
        )
        read_only_fields = ("is_staff", "is_active")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return UserRegistrationService.register(validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "photo",
            "is_active",
            "is_staff",
            "birth_date",
            "date_joined",
            "is_master",
            "registration_date_user",
            "last_update_user",
        )
        read_only_fields = (
            "id",
            "is_active",
            "is_staff",
            "date_joined",
            "is_master",
            "registration_date_user",
            "last_update_user",
        )


class AssignedSalonsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = (
            "id",
            "name",
        )


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
        )


class WorkingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingSchedule
        fields = (
            "id",
            "start_time",
            "end_time",
        )


class MasterProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone = PhoneNumberField(source="user.phone")
    photo = serializers.ImageField(source="user.photo")
    assigned_salons = AssignedSalonsSerializer(
        source="salons",
        many=True,
        read_only=True,
    )
    active_services = ServiceSerializer(
        many=True,
        read_only=True,
    )
    working_schedule = WorkingScheduleSerializer(read_only=True, many=True)

    class Meta:
        model = Master
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "bio",
            "years_of_experience",
            "average_rating",
            "total_reviews",
            "assigned_salons",
            "active_services",
            "account_status",
            "registration_date_master",
            "last_update_master",
            "working_schedule",
            "photo",
        )
        read_only_fields = (
            "id",
            "registration_date_master",
            "last_update_master",
            "average_rating",
            "total_reviews",
            "account_status",
            "working_schedule",
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password.")

        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()
