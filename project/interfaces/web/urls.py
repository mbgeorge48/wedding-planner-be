from django.urls import path
from .views import HomeView, RSVPView, RSVPFormView, RSVPManageView, ScheduleView


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("rsvp/", RSVPView.as_view(), name="rsvp"),
    path("rsvp/form/", RSVPFormView.as_view(), name="rsvp_form"),
    path("rsvp/manage/", RSVPManageView.as_view(), name="rsvp_manage"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
]
