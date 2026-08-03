from django.urls import path

from .views import (
    MasterReviewDetailView,
    MasterReviewListView,
    ReviewDetailView,
    ReviewListCreateView,
)

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="review-list-create"),
    path("<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
    path("masters/me/", MasterReviewListView.as_view(), name="master-review-list"),
    path(
        "<int:pk>/masters/me/",
        MasterReviewDetailView.as_view(),
        name="master-review-detail",
    ),
]
