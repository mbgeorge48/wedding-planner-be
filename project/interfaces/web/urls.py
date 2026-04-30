from django.urls import path

from .views import (  # RSVPFormView,
    AccommodationView,
    BasicsView,
    DietaryView,
    HomeView,
    PlusOneStateView,
    RSVPManageView,
    RSVPView,
    ScheduleView,
    SignoutView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("rsvp/", RSVPView.as_view(), name="rsvp"),
    # path("rsvp/form/", RSVPFormView.as_view(), name="rsvp_form"),
    path("rsvp/manage/", RSVPManageView.as_view(), name="rsvp_manage"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path("signout/", SignoutView.as_view(), name="signout"),
    path("plus-one/", PlusOneStateView.as_view(), name="plus-one-state"),
    path("rsvp/basics/", BasicsView.as_view(), name="rsvp_basics"),
    path("rsvp/dietary/", DietaryView.as_view(), name="rsvp_dietary"),
    path("rsvp/accommodation/", AccommodationView.as_view(), name="rsvp_accommodation"),
]
