from django.core import exceptions

from django.shortcuts import redirect, render


from project.actions import rsvp as rsvp_actions
from project.data import models
from project.interfaces.web.views.rsvp import RSVPMixin


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
                if guest.group:
                    group_members = guest.group.members.exclude(id=guest.id)

        data = {
            "bride": self.bride.firstname,
            "bride_email": self.bride.email,
            "groom": self.groom.firstname,
            "groom_email": self.groom.email,
            "is_rsvp_open": self.wedding.is_rsvp_open,
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

        if code and models.Person.objects.filter(invite_code=code).exists():
            guest = models.Person.objects.filter(invite_code=code).get()
            _, created = rsvp_actions.create_rsvp_for_guest(guest)

            return redirect("rsvp" if not created else "rsvp_basics")


class SwitchGuestView(RSVPMixin):
    def post(self, request):
        guest_id = request.POST.get("guest_id")
        if not guest_id:
            return redirect("rsvp")

        # Security check: ensure the target guest is in the same group
        target_guest = models.Person.objects.filter(
            id=guest_id, group=self.guest.group
        ).first()

        if target_guest:
            request.session["guest_code"] = target_guest.invite_code

        return redirect("rsvp")
