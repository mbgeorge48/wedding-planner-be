from django.shortcuts import redirect, render
from django.views import View

from project.actions import rsvp as rsvp_actions
from project.data import models
from project.interfaces.web.forms.accommodation import AccommodationForm
from project.interfaces.web.forms.basics import BasicsForm
from project.interfaces.web.forms.dietary import DietaryForm
from project.interfaces.web.views.rsvp import RSVPMixin


class BasicsView(RSVPMixin):
    def get(self, request):
        rsvp = models.RSVP.objects.filter(guest=self.guest).first()

        reception_start_time = self.wedding.reception_start_time
        if self.guest.invited_to_reception and self.guest.evening_only_reception:
            reception_start_time = self.wedding.evening_only_start_time

        data = {
            "step": "Basics",
            "guest_first_name": self.guest.firstname,
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "invited_to_ceremony": self.guest.invited_to_ceremony,
            "invited_to_reception": self.guest.invited_to_reception,
            "evening_only_reception": self.guest.evening_only_reception,
            "allowed_plus_one": self.guest.allowed_plus_one,
            "ceremony_venue": self.ceremony_venue,
            "reception_venue": self.reception_venue,
            "ceremony_start_time": self.wedding.ceremony_start_time,
            "reception_start_time": reception_start_time,
        }

        rsvp_data = {}
        if rsvp:
            rsvp_data["email"] = self.guest.email
            rsvp_data["phone"] = self.guest.phone
            rsvp_data["can_come_to_ceremony"] = rsvp.can_come_to_ceremony
            rsvp_data["can_come_to_reception"] = rsvp.can_come_to_reception
            rsvp_data["song_suggestion"] = rsvp.song_suggestion
            rsvp_data["plus_one"] = rsvp.plus_one
            if rsvp.plus_one:
                rsvp_data["plus_one_firstname"] = rsvp.plus_one.firstname
                rsvp_data["plus_one_lastname"] = rsvp.plus_one.lastname
                rsvp_data["plus_one_email"] = rsvp.plus_one.email
                rsvp_data["plus_one_phone"] = rsvp.plus_one.phone

        data = {**data, **rsvp_data}
        return render(request, "components/rsvp/form/basics.html", data)

    def post(self, request):
        form = BasicsForm(request.POST)

        if form.is_valid():
            rsvp_actions.update_rsvp_basics(
                guest=self.guest,
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                can_come_to_ceremony=form.cleaned_data["can_come_to_ceremony"],
                can_come_to_reception=form.cleaned_data["can_come_to_reception"],
                song_suggestion=form.cleaned_data["song_suggestion"],
                plus_one=form.cleaned_data["plus_one"],
                plus_one_firstname=form.cleaned_data["plus_one_firstname"],
                plus_one_lastname=form.cleaned_data["plus_one_lastname"],
                plus_one_email=form.cleaned_data["plus_one_email"],
                plus_one_phone=form.cleaned_data["plus_one_phone"],
            )
        return redirect("rsvp_dietary")


class DietaryView(RSVPMixin):
    def get(self, request):
        rsvp = models.RSVP.objects.filter(guest=self.guest).first()

        if not rsvp:
            return redirect("rsvp_basics")

        selected_categories = list(
            rsvp.dietary_requirements.values_list("category", flat=True)
        )
        other_food = rsvp.dietary_requirements.filter(
            category=models.Food.Category.OTHER
        ).first()
        selected_other_detail = other_food.detail if other_food else ""

        plus_one_selected_categories = []
        if rsvp.plus_one:
            plus_one_rsvp = models.RSVP.objects.filter(guest=rsvp.plus_one).first()
            if plus_one_rsvp:
                plus_one_selected_categories = list(
                    plus_one_rsvp.dietary_requirements.values_list(
                        "category", flat=True
                    )
                )
                plus_one_other_food = plus_one_rsvp.dietary_requirements.filter(
                    category=models.Food.Category.OTHER
                ).first()
                plus_one_selected_other_detail = (
                    plus_one_other_food.detail if plus_one_other_food else ""
                )

        rsvp_data = {}
        if rsvp:
            rsvp_data["selected_categories"] = selected_categories
            rsvp_data["selected_other_detail"] = selected_other_detail
            rsvp_data["plus_one_selected_categories"] = plus_one_selected_categories
            if rsvp.plus_one:
                rsvp_data["plus_one_selected_other_detail"] = (
                    plus_one_selected_other_detail
                )

        data = {
            "step": "Dietary",
            "guest_first_name": self.guest.firstname,
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "food_categories": models.Food.Category.choices,
            "has_plus_one": rsvp.plus_one is not None,
            **rsvp_data,
        }
        return render(request, "components/rsvp/form/dietary.html", data)

    def post(self, request):
        rsvp = models.RSVP.objects.get(guest=self.guest)
        form = DietaryForm(request.POST, has_plus_one=bool(rsvp.plus_one))

        if form.is_valid():
            rsvp_actions.update_rsvp_dietary(
                rsvp=rsvp,
                dietary_categories=form.cleaned_data["dietary_categories"],
                dietary_other_detail=form.cleaned_data["dietary_other_detail"],
                plus_one_dietary_categories=form.cleaned_data.get(
                    "plus_one_dietary_categories"
                ),
                plus_one_dietary_other_detail=form.cleaned_data.get(
                    "plus_one_dietary_other_detail", ""
                ),
            )

        return redirect("rsvp_accommodation")


class AccommodationView(RSVPMixin):
    def get(self, request):
        rsvp = models.RSVP.objects.get(guest=self.guest)

        data = {
            "step": "Accommodation",
            "guest_first_name": self.guest.firstname,
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "allowed_to_stay_onsite": self.guest.allowed_to_stay_onsite,
            "allowed_to_stay_in_yurt": self.guest.allowed_to_stay_in_yurt,
            "allowed_to_stay_night_after_reception": self.guest.allowed_to_stay_night_after_reception,
            "staying_preference": rsvp.staying_preference,
            "staying_night_after_reception": rsvp.staying_night_after_reception,
            "morning_meal_day_after_reception": rsvp.morning_meal_day_after_reception,
            "evening_meal_day_after_reception": rsvp.evening_meal_day_after_reception,
            "day_after_reception_suggestion": rsvp.day_after_reception_suggestion,
            "staying_preference_choices": models.RSVP.StayingPreferences.choices,
            "staying_preference_choices_no_yurt": [
                c for c in models.RSVP.StayingPreferences.choices if c[0] != "YURT"
            ],
            "meal_choices": models.RSVP.DayAfterReceptionMeal.choices,
            "hotels": models.Venue.objects.filter(type=models.Venue.Type.HOTEL),
        }

        return render(request, "components/rsvp/form/accommodation.html", data)

    def post(self, request):
        rsvp = models.RSVP.objects.get(guest=self.guest)
        form = AccommodationForm(request.POST)

        if form.is_valid():
            rsvp_actions.update_rsvp_accommodation(
                rsvp=rsvp,
                staying_preference=form.cleaned_data["staying_preference"],
                staying_night_after_reception=form.cleaned_data[
                    "staying_night_after_reception"
                ],
                morning_meal_day_after_reception=form.cleaned_data[
                    "morning_meal_day_after_reception"
                ],
                evening_meal_day_after_reception=form.cleaned_data[
                    "evening_meal_day_after_reception"
                ],
                day_after_reception_suggestion=form.cleaned_data[
                    "day_after_reception_suggestion"
                ],
            )

        return redirect("rsvp")


class PlusOneStateView(View):
    def get(self, request):
        plus_one = request.GET.get("plus_one") == "true"

        return render(
            request,
            "components/rsvp/form/partials/plus_one_fields.html",
            {"plus_one": plus_one, "food_categories": models.Food.Category.choices},
        )
