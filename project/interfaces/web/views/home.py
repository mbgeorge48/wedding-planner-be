from django.shortcuts import render
from project.data import models


def home(request):
    wedding = models.Wedding.objects.get()

    wedding_data = {
        "id": wedding.id,
        "bride": wedding.bride.firstname,
        "groom": wedding.groom.firstname,
        "date": wedding.date,
    }

    context = {
        "page_title": "Welcome to the Wedding Planner",
        "guest_count": 42,
        "show_banner": True,
        **wedding_data,
    }
    print(context)
    return render(request, "index.html", context)
