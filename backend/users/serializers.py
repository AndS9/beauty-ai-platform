from typing import ClassVar

from appointments.models import Appointment
from beauty_service.models import Service
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from salons.models import Salon

from users.models import DayOff, Master, WorkingSchedule
from users.services.auth_service import UserRegistrationService


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
        extra_kwargs: ClassVar[dict] = {
            "password": {"write_only": True, "min_length": 5}
        }

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
            "weekday",
            "start_time",
            "end_time",
            "is_working_day",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        instance = self.instance or WorkingSchedule()

        for attr, value in attrs.items():
            setattr(instance, attr, value)

        if instance.pk is None:
            instance.master = self.context["request"].user.master

        try:
            instance.clean()
        except DjangoValidationError as e:
            if hasattr(e, "message_dict"):
                raise serializers.ValidationError(e.message_dict)
            raise serializers.ValidationError(e.messages)

        return attrs

    def create(self, validated_data):
        if not validated_data["is_working_day"]:
            WorkingSchedule.objects.filter(
                master=validated_data["master"],
                weekday=validated_data["weekday"],
            ).delete()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not validated_data.get("is_working_day", instance.is_working_day):
            WorkingSchedule.objects.filter(
                master=validated_data.get("master", instance.master),
                weekday=validated_data.get("weekday", instance.weekday),
            ).exclude(pk=instance.pk).delete()

        return super().update(instance, validated_data)


class DayOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayOff
        fields = (
            "id",
            "start_date",
            "end_date",
            "reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        master = self.context["request"].user.master
        instance = self.instance

        start_date = attrs.get(
            "start_date",
            instance.start_date if instance else None,
        )
        end_date = attrs.get(
            "end_date",
            instance.end_date if instance else None,
        )

        if start_date is None or end_date is None:
            raise serializers.ValidationError("Start date and end date are required.")

        if start_date > end_date:
            raise serializers.ValidationError(
                "Start date cannot be greater than end date."
            )

        overlapping = DayOff.objects.filter(
            master=master,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if instance:
            overlapping = overlapping.exclude(pk=instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError(
                "This period overlaps with another day off."
            )

        appointments = Appointment.objects.filter(
            master=master,
            appointment_date__range=(start_date, end_date),
            status="confirmed",
        )

        if appointments.exists():
            raise serializers.ValidationError(
                "There are confirmed appointments within this period."
            )

        return attrs


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
