from django.views.generic import TemplateView

from project.data import models


class ScheduleView(TemplateView):
    template_name = "schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding = models.Wedding.objects.select_related(
            "bride", "groom", "ceremony_venue", "reception_venue"
        ).first()

        context["wedding"] = wedding
        return context
