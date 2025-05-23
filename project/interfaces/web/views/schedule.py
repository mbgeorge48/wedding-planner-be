from django.shortcuts import render
from project.data import models


def schedule(request):
    wedding = models.Wedding.objects.get()

    wedding_data = {
        "id": wedding.id,
        "bride": wedding.bride.firstname,
        "groom": wedding.groom.firstname,
        "date": wedding.date,
    }

    context = {
        "page_title": "Welcome to the Wedding Planner",  # placeholders
        "guest_count": 42,  # placeholders
        "show_banner": True,  # placeholders
        **wedding_data,
    }

    return render(request, "schedule.html", context)
