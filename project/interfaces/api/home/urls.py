from django.urls import path
from project.interfaces.api.home import views

urlpatterns = [
    path("", views.HomeInfoView.as_view()),
]
