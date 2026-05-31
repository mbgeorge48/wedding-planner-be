from django.views.generic import TemplateView

from project.data import models


class FAQView(TemplateView):
    template_name = "faq.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wedding = models.Wedding.objects.first()
        faqs = models.WeddingFAQ.objects.all()

        wedding_data = {}
        if wedding and wedding.bride and wedding.groom:
            wedding_data = {
                "id": wedding.id,
                "bride": wedding.bride.firstname,
                "groom": wedding.groom.firstname,
                "date": wedding.date,
            }

        context.update(
            {
                "faqs": faqs,
                **wedding_data,
            }
        )

        return context
