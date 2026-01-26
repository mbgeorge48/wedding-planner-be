from django.shortcuts import render
from project.data import models

from django.views import View


class PlusOneStateView(View):
    def get(self, request):
        plus_one = request.GET.get("plus_one") == "true"

        return render(
            request,
            "components/rsvp/form/partials/plus_one_fields.html",
            {"plus_one": plus_one, "food_categories": models.Food.Category.choices},
        )
