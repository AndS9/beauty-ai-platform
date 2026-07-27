from django.urls import path

from .views import SalonListCreateView, SalonDetailView

urlpatterns = [
    path("", SalonListCreateView.as_view(), name="salon-list-create"),
    path("<int:pk>/", SalonDetailView.as_view(), name="salon-detail"),
]
