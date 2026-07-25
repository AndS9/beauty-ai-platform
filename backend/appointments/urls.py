from django.urls import path

from .views import (
    ClientAppointmentListView,
    RescheduleAppointmentView,
    CancelAppointmentView,
    AvailableSlotsView,
)

urlpatterns = [
    path("my/", ClientAppointmentListView.as_view(), name="client-appointments-list"),
    path(
        "<int:pk>/reschedule/",
        RescheduleAppointmentView.as_view(),
        name="appointment-reschedule",
    ),
    path(
        "<int:pk>/cancel/", CancelAppointmentView.as_view(), name="appointment-cancel"
    ),
    path(
        "available-slots/", AvailableSlotsView.as_view(), name="available-slots"
    ),
]
