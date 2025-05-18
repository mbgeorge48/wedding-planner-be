from django.urls import path
from .views import home, load_time

app_name = "web"

urlpatterns = [
    path("", home, name="home"),
    path("load-time/", load_time, name="load_time"),
]
