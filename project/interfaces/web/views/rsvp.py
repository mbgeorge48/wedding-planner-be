from django.core import exceptions
from django.shortcuts import redirect, render
from django.views import View

from project.data import models
from project.interfaces.web.forms.basics import BasicsForm
from project.interfaces.web.forms.dietary import DietaryForm


class RSVPView(View):
    template_name = "rsvp.html"

    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        firstname = request.GET.get("firstname", "").strip().title()

        guest_code = request.session.get("guest_code", "")

        context = {
            "guest_code": guest_code,
            "prefill": {
                "code": code,
                "firstname": firstname,
            },
        }
        return render(request, self.template_name, context)

    def post(self, request):
        code = request.POST.get("code", "").strip().upper()
        firstname = request.POST.get("firstname", "").strip().upper()

        try:
            models.Person.objects.filter(
                invite_code=code, firstname__iexact=firstname
            ).get()
        except exceptions.MultipleObjectsReturned:
            return render(
                request,
                self.template_name,
                {"error": "Multiple users found, contact MG"},
            )
        except exceptions.ObjectDoesNotExist:
            return render(
                request,
                self.template_name,
                {"error": "No user matching that name and invite code found"},
            )

        request.session["guest_code"] = code

        # If they haven't rsvpd yet then redirect, otherwise don't let them go to the main menu
        return redirect("rsvp_form")


class RSVPFormView(View):
    template_name = "rsvp_form.html"

    def get(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        wedding = models.Wedding.objects.first()

        if not guest or not (
            wedding and wedding.ceremony_venue and wedding.reception_venue
        ):
            return redirect("rsvp")

        data = {
            "invited_to_ceremony": guest.invited_to_ceremony,
            "invited_to_reception": guest.invited_to_reception,
            "allowed_plus_one": guest.allowed_plus_one,
            "allowed_to_stay_onsite": guest.allowed_to_stay_onsite,
            "allowed_to_stay_in_yurt": guest.allowed_to_stay_in_yurt,
            "allowed_to_stay_night_after_reception": guest.allowed_to_stay_night_after_reception,
            "food_categories": models.Food.Category.choices,
            "ceremony_venue": wedding.ceremony_venue.name,
            "reception_venue": wedding.reception_venue.name,
        }
        return render(request, self.template_name, {"name": guest.firstname, **data})

    def post(self, request):

        # If user somehow POSTs without session, redirect
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        if not guest:
            return redirect(
                "rsvp",
                {"error": "unable to find guest with that code/name combination"},
            )

        return render(
            request,
            self.template_name,
            {"name": guest.firstname},
        )


class RSVPContactView(View):
    template_name = "rsvp_form.html"

    def get(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        wedding = models.Wedding.objects.first()

        if not guest or not (
            wedding and wedding.ceremony_venue and wedding.reception_venue
        ):
            return redirect("rsvp")

        data = {
            "invited_to_ceremony": guest.invited_to_ceremony,
            "invited_to_reception": guest.invited_to_reception,
            "allowed_plus_one": guest.allowed_plus_one,
            "allowed_to_stay_onsite": guest.allowed_to_stay_onsite,
            "allowed_to_stay_in_yurt": guest.allowed_to_stay_in_yurt,
            "allowed_to_stay_night_after_reception": guest.allowed_to_stay_night_after_reception,
            "food_categories": models.Food.Category.choices,
            "ceremony_venue": wedding.ceremony_venue.name,
            "reception_venue": wedding.reception_venue.name,
        }
        return render(request, self.template_name, {"name": guest.firstname, **data})

    def post(self, request):

        # If user somehow POSTs without session, redirect
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        if not guest:
            return redirect(
                "rsvp",
                {"error": "unable to find guest with that code/name combination"},
            )

        return render(
            request,
            self.template_name,
            {"name": guest.firstname},
        )


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


class BasicsView(View):
    def get(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        rsvp = models.RSVP.objects.filter(guest=guest).get()

        wedding = models.Wedding.objects.first()
        if not guest or not (
            wedding and wedding.ceremony_venue and wedding.reception_venue
        ):
            return redirect("rsvp")

        data = {
            "invited_to_ceremony": guest.invited_to_ceremony,
            "invited_to_reception": guest.invited_to_reception,
            "allowed_plus_one": guest.allowed_plus_one,
            "ceremony_venue": wedding.ceremony_venue.name,
            "reception_venue": wedding.reception_venue.name,
        }

        rsvp_data = {}
        if rsvp:
            rsvp_data["email"] = guest.email
            rsvp_data["phone"] = guest.phone
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
            person = models.Person.objects.get(
                invite_code=request.session["guest_code"]
            )
            person.email = form.cleaned_data["email"]
            person.phone = form.cleaned_data["phone"]
            person.save()

            rsvp, _ = models.RSVP.objects.get_or_create(guest=person)
            rsvp.can_come_to_ceremony = form.cleaned_data["can_come_to_ceremony"]
            rsvp.can_come_to_reception = form.cleaned_data["can_come_to_reception"]
            if form.cleaned_data["plus_one"]:
                plus_one_person = models.Person.objects.create(
                    firstname=form.cleaned_data["plus_one_firstname"],
                    lastname=form.cleaned_data["plus_one_lastname"],
                    email=form.cleaned_data["plus_one_email"],
                    type=models.Person.Type.STANDARD,
                    allowed_plus_one=False,
                    invited_to_ceremony=person.invited_to_ceremony,
                    invited_to_reception=person.invited_to_reception,
                    allowed_to_stay_onsite=person.allowed_to_stay_onsite,
                    allowed_to_stay_in_yurt=person.allowed_to_stay_in_yurt,
                    allowed_to_stay_night_after_reception=person.allowed_to_stay_night_after_reception,
                )
                rsvp.plus_one = plus_one_person
            rsvp.save()

        # rsvp_exists = models.RSVP.objects.filter(guest=person).exists()
        # return render(request, "components/rsvp/form/basics.html", {
        #     "return_to_menu": rsvp_exists,
        #     ...
        # })
        return redirect("rsvp_dietary")


class DietaryView(View):
    def get(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        wedding = models.Wedding.objects.first()
        rsvp = models.RSVP.objects.filter(guest=guest).get()

        if not guest or not (
            wedding and wedding.ceremony_venue and wedding.reception_venue
        ):
            return redirect("rsvp")

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
            rsvp_data["plus_one_selected_other_detail"] = plus_one_selected_other_detail

        data = {
            "food_categories": models.Food.Category.choices,
            "has_plus_one": rsvp.plus_one is not None,
            **rsvp_data,
        }
        return render(request, "components/rsvp/form/dietary.html", data)

    def post(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        rsvp = models.RSVP.objects.filter(guest=guest).get()
        form = DietaryForm(request.POST, has_plus_one=bool(rsvp.plus_one))

        if form.is_valid():
            categories = form.cleaned_data["dietary_categories"]
            other_detail = form.cleaned_data["dietary_other_detail"]

            foods = []
            for category in categories:
                if category == "OTHER":
                    food, _ = models.Food.objects.get_or_create(
                        category=category,
                        detail=other_detail,
                    )
                else:
                    food, _ = models.Food.objects.get_or_create(
                        category=category,
                        detail="",
                    )
                foods.append(food)

            rsvp.dietary_requirements.set(foods)
            rsvp.save()

            if rsvp.plus_one:
                plus_one_rsvp, _ = models.RSVP.objects.get_or_create(
                    guest=rsvp.plus_one,
                    defaults={
                        "can_come_to_ceremony": rsvp.can_come_to_ceremony,
                        "can_come_to_reception": rsvp.can_come_to_reception,
                    },
                )
                plus_one_categories = form.cleaned_data["plus_one_dietary_categories"]
                plus_one_other_detail = form.cleaned_data[
                    "plus_one_dietary_other_detail"
                ]
                plus_one_foods = []
                for category in plus_one_categories:
                    if category == "OTHER":
                        food, _ = models.Food.objects.get_or_create(
                            category=category,
                            detail=plus_one_other_detail,
                        )
                    else:
                        food, _ = models.Food.objects.get_or_create(
                            category=category,
                            detail="",
                        )
                    plus_one_foods.append(food)

                plus_one_rsvp.dietary_requirements.set(plus_one_foods)
                plus_one_rsvp.save()

        return redirect("rsvp_accommodation")


class AccommodationView(View):
    def get(self, request):
        return render(request, "components/rsvp/form/accommodation.html")

    def post(self, request):
        return redirect("rsvp_travel")


class TravelView(View):
    def get(self, request):
        return render(request, "components/rsvp/form/travel.html")

    def post(self, request):
        return redirect("rsvp_done")
