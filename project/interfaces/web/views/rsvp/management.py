from collections import Counter
from project.data import models
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views import View


class RSVPManageView(View):
    template_name = "rsvp_manage.html"

    def get(self, request):
        code = request.session.get("guest_code")

        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()

        if not admin:
            return redirect("rsvp")

        rsvp_data = (
            models.RSVP.objects.all()
            .select_related("guest", "plus_one", "guest__group")
            .prefetch_related("dietary_requirements")
            .order_by("guest__group__created", "guest__lastname")
        )

        rsvp_data_recent_changes = rsvp_data.order_by("-modified")[:10]

        overall_totals = models.Person.objects.aggregate(
            invited_to_ceremony=Count("id", filter=Q(invited_to_ceremony=True)),
            invited_to_reception_daytime=Count(
                "id",
                filter=Q(invited_to_reception=True) & Q(evening_only_reception=False),
            ),
            invited_to_reception_evening=Count(
                "id",
                filter=Q(invited_to_reception=True) & Q(evening_only_reception=True),
            ),
            evening_only_reception=Count("id", filter=Q(evening_only_reception=True)),
            allowed_to_stay_onsite=Count("id", filter=Q(allowed_to_stay_onsite=True)),
            allowed_to_stay_in_yurt=Count("id", filter=Q(allowed_to_stay_in_yurt=True)),
            allowed_to_stay_night_after_reception=Count(
                "id", filter=Q(allowed_to_stay_night_after_reception=True)
            ),
            guests_invited=Count("id"),
        )
        yet_to_rsvp = (
            models.Person.objects.filter(rsvp__isnull=True, is_active=True)
            .order_by("group__created", "lastname")
            .values("firstname", "lastname", "internal_notes")
        )

        rsvp_totals = rsvp_data.aggregate(
            can_come_to_ceremony=Count("id", filter=Q(can_come_to_ceremony=True)),
            can_come_to_reception_daytime=Count(
                "id",
                filter=Q(can_come_to_reception=True)
                & Q(guest__evening_only_reception=False),
            ),
            can_come_to_reception_eveining=Count(
                "id",
                filter=Q(can_come_to_reception=True)
                & Q(guest__evening_only_reception=True),
            ),
            staying_night_after_reception=Count(
                "id", filter=Q(staying_night_after_reception=True)
            ),
            morning_meal_day_after_reception=Count(
                "id", filter=Q(morning_meal_day_after_reception=True)
            ),
            evening_meal_day_after_reception=Count(
                "id", filter=Q(evening_meal_day_after_reception=True)
            ),
        )

        staying_preferences = dict(
            Counter(rsvp.staying_preference for rsvp in rsvp_data)
        )
        song_suggestions = [
            (r.song_suggestion, f"{r.guest.firstname} {r.guest.lastname}")
            for r in rsvp_data
            if r.song_suggestion and r.guest
        ]

        day_after_reception_suggestions = [
            (
                r.day_after_reception_suggestion,
                f"{r.guest.firstname} {r.guest.lastname}",
            )
            for r in rsvp_data
            if r.day_after_reception_suggestion and r.guest
        ]

        return render(
            request,
            self.template_name,
            {
                "name": admin.firstname,
                "guest_code": request.session.get("guest_code"),
                "rsvp_data": rsvp_data,
                "rsvp_data_recent_changes": rsvp_data_recent_changes,
                "staying_preferences": staying_preferences,
                "song_suggestions": song_suggestions,
                "day_after_reception_suggestions": day_after_reception_suggestions,
                "overall_totals": overall_totals,
                "rsvp_totals": rsvp_totals,
                "yet_to_rsvp": yet_to_rsvp,
            },
        )


class RSVPGroupViewer(View):
    template_name = "components/rsvp/management/group_viewer.html"

    def get(self, request):
        code = request.session.get("guest_code")

        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()

        if not admin:
            return redirect("rsvp")

        groups = models.PersonGroup.objects.all().prefetch_related("members")
        people_not_in_groups = models.Person.objects.filter(group__isnull=True).values(
            "firstname", "lastname", "internal_notes"
        )

        return render(
            request,
            self.template_name,
            {"groups": groups, "people_not_in_groups": people_not_in_groups},
        )
