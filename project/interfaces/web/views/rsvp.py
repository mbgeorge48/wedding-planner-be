# from django import forms
from django.shortcuts import redirect, render
from project.data import models
from django.core import exceptions


from django.views import View


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
    template_name = "rsvp.html"

    def get(self, request):
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()

        if not guest:
            return redirect("rsvp")

        return render(request, self.template_name, {"name": guest.firstname})

    def post(self, request):
        action = request.POST.get("action")
        if action == "signout":
            request.session.flush()
            return redirect("rsvp")

        # If user somehow POSTs without session, redirect
        code = request.session.get("guest_code")
        guest = models.Person.objects.filter(invite_code=code).first()
        if not guest:
            return redirect("rsvp")

        return render(request, self.template_name, {"name": guest.firstname})

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
