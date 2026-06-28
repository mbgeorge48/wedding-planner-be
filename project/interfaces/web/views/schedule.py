from django.views.generic import TemplateView

from project.data import models


class ScheduleView(TemplateView):
    template_name = "schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding = models.Wedding.objects.first()

        if not wedding or not wedding.bride or not wedding.groom:
            return context

        wedding_data = {
            "id": wedding.id,
            "bride": wedding.bride.firstname,
            "groom": wedding.groom.firstname,
            "date": wedding.date,
        }

        # Placeholders
        context = {
            "page_title": "Welcome to the Wedding Planner",  # placeholders
            "guest_count": 42,  # placeholders
            "show_banner": True,  # placeholders
            **wedding_data,
        }

        return context
