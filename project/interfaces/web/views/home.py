from django.views.generic import TemplateView
from project.data import models


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding = models.Wedding.objects.first()
        if wedding:
            context.update(
                {
                    "id": wedding.id,
                    "bride": wedding.bride.firstname,
                    "groom": wedding.groom.firstname,
                    "date": wedding.date,
                }
            )

        # placeholders
        context.update(
            {
                "page_title": "Welcome to the Wedding Planner",
                "guest_count": 42,
                "show_banner": True,
            }
        )

        return context
