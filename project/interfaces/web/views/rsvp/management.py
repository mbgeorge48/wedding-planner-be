from collections import Counter

from django.http import HttpResponseForbidden
from project.data import models
from django.db.models import Count, Q, Max
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


class RSVPTableArrangements(View):
    template_name = "components/rsvp/management/table_arrangement.html"

    def _get_context(self):
        tables = models.ReceptionTable.objects.all().prefetch_related("table_guests")
        
        # Get all guests who are invited to the daytime reception and haven't declined
        breakfast_guests = models.Person.objects.filter(
            invited_to_reception=True,
            evening_only_reception=False
        ).exclude(
            rsvp__can_come_to_reception=False
        )
        
        total_guests = breakfast_guests.count()
        assigned_guests = breakfast_guests.filter(table_number__isnull=False).count()
        unassigned_guests = total_guests - assigned_guests
        unassigned_list = breakfast_guests.filter(table_number__isnull=True)
        
        return {
            "tables": tables,
            "total_guests": total_guests,
            "assigned_guests": assigned_guests,
            "unassigned_guests": unassigned_guests,
            "total_tables": tables.count(),
            "unassigned_list": unassigned_list,
        }

    def get(self, request):
        code = request.session.get("guest_code")
        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()
        if not admin:
            return redirect("rsvp")

        context = self._get_context()
        return render(request, self.template_name, context)

    def post(self, request):
        code = request.session.get("guest_code")
        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()
        if not admin:
            return HttpResponseForbidden()

        action = request.POST.get("action")
        
        if action == "add_table":
            max_table = models.ReceptionTable.objects.aggregate(Max('table_number'))['table_number__max']
            next_table = (max_table or 0) + 1
            models.ReceptionTable.objects.create(table_number=next_table)
            
        elif action == "delete_table":
            table_id = request.POST.get("table_id")
            if table_id:
                models.ReceptionTable.objects.filter(id=table_id).delete()
                
        elif action == "assign_guest":
            guest_id = request.POST.get("guest_id")
            table_id = request.POST.get("table_id")
            if guest_id and table_id:
                try:
                    guest = models.Person.objects.get(id=guest_id)
                    table = models.ReceptionTable.objects.get(id=table_id)
                    guest.table_number = table
                    guest.save()
                except (models.Person.DoesNotExist, models.ReceptionTable.DoesNotExist):
                    pass
                    
        elif action == "remove_guest":
            guest_id = request.POST.get("guest_id")
            if guest_id:
                try:
                    guest = models.Person.objects.get(id=guest_id)
                    guest.table_number = None
                    guest.save()
                except models.Person.DoesNotExist:
                    pass

        context = self._get_context()
        return render(request, "components/rsvp/management/tables_content.html", context)


class RSVPTableSearchGuests(View):
    def get(self, request):
        code = request.session.get("guest_code")
        admin = models.Person.objects.filter(
            invite_code=code, type=models.Person.Type.BRIDE_GROOM.value
        ).first()
        if not admin:
            return HttpResponseForbidden()

        q = request.GET.get("q", "").strip()
        table_id = request.GET.get("table_id")

        # Get all guests who are invited to the daytime reception and haven't declined
        breakfast_guests = models.Person.objects.filter(
            invited_to_reception=True,
            evening_only_reception=False
        ).exclude(
            rsvp__can_come_to_reception=False
        )

        if q:
            guests = breakfast_guests.filter(
                Q(firstname__icontains=q) | Q(lastname__icontains=q)
            )
        else:
            # Show first 5 unassigned guests as suggestions
            guests = breakfast_guests.filter(table_number__isnull=True)[:5]

        return render(
            request,
            "components/rsvp/management/search_results.html",
            {"guests": guests, "table_id": table_id},
        )
