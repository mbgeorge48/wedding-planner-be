# from django import forms
from django.shortcuts import redirect, render
from project.data import models
from django.core import exceptions


def rsvp(request):
    if request.method == "POST":
        code = request.POST.get("code").strip().upper()
        firstname = request.POST.get("firstname").strip().upper()
        try:
            guest = models.Person.objects.filter(
                invite_code=code, firstname__iexact=firstname
            ).get()
        except exceptions.MultipleObjectsReturned:
            return render(
                request, "rsvp.html", {"error": "Multiple users found, contact MG"}
            )
        except exceptions.ObjectDoesNotExist:
            return render(
                request,
                "rsvp.html",
                {"error": "No user matching that name and invite code found"},
            )

        if guest:
            request.session["guest_code"] = code
            return redirect("rsvp_form")
        else:
            return render(request, "rsvp.html", {"error": "Invalid code"})

    return render(request, "rsvp.html")


def rsvp_form(request):
    code = request.session.get("guest_code")
    guest = models.Person.objects.filter(invite_code=code).first()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "signout":
            request.session.flush()
            return redirect("rsvp")

    if not guest:
        return redirect("rsvp")
    return render(request, "rsvp.html", {"name": guest.firstname})

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
