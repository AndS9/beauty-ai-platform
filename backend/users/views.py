from django.shortcuts import render
from django.views import View

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken

from users.permissions import IsMaster
from users.serializers import (
    UserSerializer,
    GoogleLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    SetPasswordSerializer, MasterProfileSerializer,
)
from users.services.auth_service import UserAuthService


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsMaster,)

    def get_object(self):
        return self.request.user


class ManageMasterView(generics.RetrieveUpdateAPIView):
    serializer_class = MasterProfileSerializer
    permission_classes = (IsMaster,)

    def get_object(self):
        return self.request.user.master


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not request.user.has_usable_password():
            raise ValidationError(
                {"detail": "Password has not been set. Use the set-password endpoint."}
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(generics.GenericAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if request.user.has_usable_password():
            raise ValidationError(
                {
                    "detail": (
                        "Password has already been set. "
                        "Use the change-password endpoint."
                    )
                }
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, uidb64, token):
        UserAuthService.verify_email(uidb64, token)

        return Response(
            {"detail": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class GoogleLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserAuthService.authenticate_google_user(
            google_token=serializer.validated_data["id_token"],
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class GoogleTestView(View):
    def get(self, request):
        return render(request, "test-google/test-google.html")
