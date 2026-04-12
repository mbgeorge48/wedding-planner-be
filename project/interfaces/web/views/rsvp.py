from django.core import exceptions
from django.shortcuts import redirect, render
from django.views import View

from project.data import models


class RSVPView(View):
    template_name = "rsvp.html"

    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        firstname = request.GET.get("firstname", "").strip().title()

        context = {
            "prefill": {
                "code": code,
                "firstname": firstname,
            }
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

    # class RSVPForm(forms.ModelForm):
    #     class Meta:
    #         model = models.Person
    #         fields = ["attending", "dietary", "notes"]

    # if request.method == "POST":
    #     form = RSVPForm(request.POST, instance=guest)
    #     if form.is_valid():
    #         form.save()
    #         return render(request, "rsvp_thankyou.html")
    # else:
    #     form = RSVPForm(instance=guest)

    # return render(request, "rsvp_form.html", {"form": form, "guest": guest})


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
