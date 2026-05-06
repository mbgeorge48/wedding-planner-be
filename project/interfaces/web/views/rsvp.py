from typing import TYPE_CHECKING, cast

from django.core import exceptions
from django.shortcuts import redirect, render
from django.views import View

from project.data import models

if TYPE_CHECKING:
    from project.data.models.person import Person
    from project.data.models.venue import Venue
    from project.data.models.wedding import Wedding

from project.actions import rsvp as rsvp_actions
from project.interfaces.web.forms.accommodation import AccommodationForm
from project.interfaces.web.forms.basics import BasicsForm
from project.interfaces.web.forms.dietary import DietaryForm


class RSVPMixin(View):
    """
    Mixin to provide common guest and wedding objects for RSVP views.
    Handles redirection if the session is invalid or the wedding is not setup.
    """

    guest: "Person"
    wedding: "Wedding"

    def dispatch(self, request, *args, **kwargs):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        wedding = models.Wedding.objects.first()

        if not (wedding and wedding.ceremony_venue and wedding.reception_venue):
            return redirect("rsvp")

        self.guest = cast("Person", guest)
        self.wedding = cast("Wedding", wedding)
        self.bride = cast("Person", self.wedding.bride)
        self.groom = cast("Person", self.wedding.groom)

        return super().dispatch(request, *args, **kwargs)

    @property
    def ceremony_venue(self) -> "Venue":
        return cast("Venue", self.wedding.ceremony_venue)

    @property
    def reception_venue(self) -> "Venue":
        return cast("Venue", self.wedding.reception_venue)


class RSVPView(RSVPMixin):
    template_name = "rsvp.html"

    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        firstname = request.GET.get("firstname", "").strip().title()

        guest_code = request.session.get("guest_code", "")

        guest = None
        rsvp = None
        group_members = models.Person.objects.none()
        if guest_code:
            guest = models.Person.objects.filter(invite_code=guest_code).first()
            if isinstance(guest, models.Person):
                rsvp = models.RSVP.objects.filter(guest=guest).first()
                # Get other members from the guest's group
                group_members = models.Person.objects.none()
                if guest.group:
                    group_members = guest.group.members.exclude(id=guest.id)

        data = {
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "guest": guest,
            "rsvp": rsvp,
            "group_members": group_members,
        }

        context = {
            "guest_code": guest_code,
            "prefill": {
                "code": code,
                "firstname": firstname,
            },
        }
        data = {**data, **context}
        return render(request, self.template_name, data)

    def post(self, request):
        code = request.POST.get("code", "").strip().upper()
        firstname = request.POST.get("firstname", "").strip()
        wedding = models.Wedding.objects.first()

        try:
            models.Person.objects.filter(
                invite_code=code, firstname__iexact=firstname
            ).get()
        except exceptions.MultipleObjectsReturned:
            groom_name = (
                wedding.groom.firstname if wedding and wedding.groom else "the groom"
            )
            return render(
                request,
                self.template_name,
                {"error": f"Multiple users found, contact {groom_name}"},
            )
        except exceptions.ObjectDoesNotExist:
            return render(
                request,
                self.template_name,
                {"error": "No user matching that name and invite code found"},
            )

        request.session["guest_code"] = code

        guest = None
        if code:
            guest = models.Person.objects.filter(invite_code=code).first()
            if (
                isinstance(guest, models.Person)
                and models.RSVP.objects.filter(guest=guest).exists()
            ):
                return redirect("rsvp")

        # If they haven't rsvpd yet then redirect, otherwise don't let them go to the main menu
        return redirect("rsvp_basics")


# class RSVPManageView(View):
#     template_name = "rsvp_form.html"

#     def get(self, request):
#         code = request.session.get("guest_code")
#         guest = models.Person.objects.filter(invite_code=code).first()
#         wedding = models.Wedding.objects.first()

#         if not guest or not (
#             wedding and wedding.ceremony_venue and wedding.reception_venue
#         ):
#             return redirect("rsvp")

#         data = {
#             "invited_to_ceremony": guest.invited_to_ceremony,
#             "invited_to_reception": guest.invited_to_reception,
#             "allowed_plus_one": guest.allowed_plus_one,
#             "allowed_to_stay_onsite": guest.allowed_to_stay_onsite,
#             "allowed_to_stay_in_yurt": guest.allowed_to_stay_in_yurt,
#             "allowed_to_stay_night_after_reception": guest.allowed_to_stay_night_after_reception,
#             "food_categories": models.Food.Category.choices,
#             "ceremony_venue": wedding.ceremony_venue.name,
#             "reception_venue": wedding.reception_venue.name,
#         }
#         return render(request, self.template_name, {"name": guest.firstname, **data})

#     def post(self, request):

#         # If user somehow POSTs without session, redirect
#         code = request.session.get("guest_code")
#         guest = models.Person.objects.filter(invite_code=code).first()
#         if not guest:
#             return redirect(
#                 "rsvp",
#                 {"error": "unable to find guest with that code/name combination"},
#             )

#         return render(
#             request,
#             self.template_name,
#             {"name": guest.firstname},
#         )


# class RSVPContactView(View):
#     template_name = "rsvp_form.html"

#     def get(self, request):
#         code = request.session.get("guest_code")
#         guest = models.Person.objects.filter(invite_code=code).first()
#         wedding = models.Wedding.objects.first()

#         if not guest or not (
#             wedding and wedding.ceremony_venue and wedding.reception_venue
#         ):
#             return redirect("rsvp")

#         data = {
#             "invited_to_ceremony": guest.invited_to_ceremony,
#             "invited_to_reception": guest.invited_to_reception,
#             "allowed_plus_one": guest.allowed_plus_one,
#             "allowed_to_stay_onsite": guest.allowed_to_stay_onsite,
#             "allowed_to_stay_in_yurt": guest.allowed_to_stay_in_yurt,
#             "allowed_to_stay_night_after_reception": guest.allowed_to_stay_night_after_reception,
#             "food_categories": models.Food.Category.choices,
#             "ceremony_venue": wedding.ceremony_venue.name,
#             "reception_venue": wedding.reception_venue.name,
#         }
#         return render(request, self.template_name, {"name": guest.firstname, **data})

#     def post(self, request):

#         # If user somehow POSTs without session, redirect
#         code = request.session.get("guest_code")
#         guest = models.Person.objects.filter(invite_code=code).first()
#         if not guest:
#             return redirect(
#                 "rsvp",
#                 {"error": "unable to find guest with that code/name combination"},
#             )

#         return render(
#             request,
#             self.template_name,
#             {"name": guest.firstname},
#         )


class RSVPManageView(View):
    template_name = "rsvp_manage.html"

    def get(self, request):
        code = request.session.get("guest_code")

        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()

        if not admin:
            return redirect(
                "rsvp",
                {"error": "incorrect permissions to access the manage page"},
            )

        rsvp_data = models.RSVP.objects.all()

        return render(
            request,
            self.template_name,
            {
                "name": admin.firstname,
                "guest_code": request.session.get("guest_code"),
                "rsvp_data": rsvp_data,
            },
        )


class BasicsView(RSVPMixin):
    def get(self, request):
        rsvp = models.RSVP.objects.filter(guest=self.guest).first()

        reception_start_time = self.wedding.reception_start_time
        if not self.guest.invited_to_ceremony and self.guest.invited_to_reception:
            reception_start_time = self.wedding.evening_only_start_time

        data = {
            "guest_first_name": self.guest.firstname,
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "invited_to_ceremony": self.guest.invited_to_ceremony,
            "invited_to_reception": self.guest.invited_to_reception,
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
            rsvp_data["plus_one"] = rsvp.plus_one
            if rsvp.plus_one:
                rsvp_data["plus_one_firstname"] = rsvp.plus_one.firstname
                rsvp_data["plus_one_lastname"] = rsvp.plus_one.lastname
                rsvp_data["plus_one_email"] = rsvp.plus_one.email

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
                plus_one=form.cleaned_data["plus_one"],
                plus_one_firstname=form.cleaned_data["plus_one_firstname"],
                plus_one_lastname=form.cleaned_data["plus_one_lastname"],
                plus_one_email=form.cleaned_data["plus_one_email"],
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
            "food_categories": models.Food.Category.choices,
            "has_plus_one": rsvp.plus_one is not None,
            **rsvp_data,
        }
        return render(request, "components/rsvp/form/dietary.html", data)

    def post(self, request):
        # TODO need to raise validation errors
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
            "bride": self.bride.firstname,
            "groom": self.groom.firstname,
            "allowed_to_stay_onsite": self.guest.allowed_to_stay_onsite,
            "allowed_to_stay_in_yurt": self.guest.allowed_to_stay_in_yurt,
            "allowed_to_stay_night_after_reception": self.guest.allowed_to_stay_night_after_reception,
            "staying_preference": rsvp.staying_preference,
            "staying_night_after_reception": rsvp.staying_night_after_reception,
            "evening_meal_day_after_reception": rsvp.evening_meal_day_after_reception,
            "day_after_reception_suggestion": rsvp.day_after_reception_suggestion,
            "staying_preference_choices": models.RSVP.StayingPreferences.choices,
            "staying_preference_choices_no_yurt": [
                c for c in models.RSVP.StayingPreferences.choices if c[0] != "YURT"
            ],
            "meal_choices": models.RSVP.DayAfterReceptionMeal.choices,
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
                evening_meal_day_after_reception=form.cleaned_data[
                    "evening_meal_day_after_reception"
                ],
                day_after_reception_suggestion=form.cleaned_data[
                    "day_after_reception_suggestion"
                ],
            )

        return redirect("rsvp")
