from django.shortcuts import render
from django.views import View

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer, GoogleLoginSerializer
from users.services.auth_service import UserAuthService


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        print(request.headers.get("Authorization"))
        print(request.user)
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


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
