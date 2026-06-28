from typing import cast

from django.shortcuts import redirect
from django.views import View

from project.data import models
from project.data.models.person import Person
from project.data.models.venue import Venue
from project.data.models.wedding import Wedding


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

        self.guest = cast("Person", guest)
        self.wedding = cast("Wedding", wedding)
        self.bride = cast("Person", self.wedding.bride)
        self.groom = cast("Person", self.wedding.groom)

        if self.wedding and not self.wedding.is_rsvp_open:
            if request.resolver_match and request.resolver_match.url_name not in (
                "rsvp",
                "rsvp_switch",
            ):
                return redirect("rsvp")

        return super().dispatch(request, *args, **kwargs)

    @property
    def ceremony_venue(self) -> "Venue":
        return cast("Venue", self.wedding.ceremony_venue)

    @property
    def reception_venue(self) -> "Venue":
        return cast("Venue", self.wedding.reception_venue)
