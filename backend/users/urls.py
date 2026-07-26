from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import (
    CreateUserView,
    ManageUserView,
    VerifyEmailView,
    GoogleTestView,
    GoogleLoginView,
)

app_name = "users"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("google-test/", GoogleTestView.as_view(), name="google-test"),
]
