from django.urls import path
from .views import home, load_time, rsvp, rsvp_form, schedule

# app_name = "web"

urlpatterns = [
    path("", home, name="home"),
    path("rsvp", rsvp, name="rsvp"),
    path("rsvp/form", rsvp_form, name="rsvp_form"),
    path("schedule", schedule, name="schedule"),
    path("load-time/", load_time, name="load_time"),
]
