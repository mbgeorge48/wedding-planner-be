from django.core.management.base import BaseCommand

from project.data.models import RSVP, Person, PersonGroup


class Command(BaseCommand):
    help = "Generate lists of guest groups based on RSVP criteria"

    def handle(self, *args, **options):
        # 1. Fetch groups and standalone guests
        person_groups = PersonGroup.objects.prefetch_related(
            "members", "members__rsvp", "members__rsvp__plus_one"
        ).order_by("created")

        groups = []

        for pg in person_groups:
            members = list(
                pg.members.all().order_by("created", "lastname", "firstname")
            )
            if not members:
                continue

            lead = members[0]
            other_members = members[1:]

            # Add any plus-ones of group members to other_members if not already included
            for m in members:
                rsvp = getattr(m, "rsvp", None)
                if (
                    rsvp
                    and rsvp.plus_one
                    and rsvp.plus_one not in members
                    and rsvp.plus_one not in other_members
                ):
                    other_members.append(rsvp.plus_one)

            groups.append(
                {
                    "lead": lead,
                    "other_members": other_members,
                    "all_persons": members
                    + [m for m in other_members if m not in members],
                }
            )

        # Standalone Person objects (no PersonGroup and not a plus_one of anyone)
        standalone_people = Person.objects.filter(
            group__isnull=True, plus_one_of__isnull=True
        ).order_by("created", "lastname", "firstname")

        for person in standalone_people:
            other_members = []
            rsvp = getattr(person, "rsvp", None)
            if rsvp and rsvp.plus_one:
                other_members.append(rsvp.plus_one)

            groups.append(
                {
                    "lead": person,
                    "other_members": other_members,
                    "all_persons": [person] + [m for m in other_members if m != person],
                }
            )

        if not groups:
            self.stdout.write(self.style.WARNING("No guests or groups found."))
            return

        # Criteria definitions
        def only_coming_to_ceremony(p, rsvp):
            return bool(
                rsvp
                and rsvp.can_come_to_ceremony is True
                and not rsvp.can_come_to_reception
            )

        def coming_to_ceremony_and_reception(p, rsvp):
            return bool(
                rsvp
                and rsvp.can_come_to_ceremony is True
                and rsvp.can_come_to_reception is True
            )

        def only_coming_to_reception(p, rsvp):
            return bool(
                rsvp
                and not rsvp.can_come_to_ceremony
                and rsvp.can_come_to_reception is True
            )

        def only_coming_to_reception_in_evening(p, rsvp):
            return bool(
                rsvp and rsvp.can_come_to_reception is True and p.evening_only_reception
            )

        def coming_to_reception_and_staying_onsite(p, rsvp):
            if not (rsvp and rsvp.can_come_to_reception is True):
                return False
            is_yurt_or_camping = rsvp.staying_preference in [
                RSVP.StayingPreferences.YURT,
                RSVP.StayingPreferences.CAMPING,
            ]
            offered_onsite = bool(p.allowed_to_stay_onsite)
            return is_yurt_or_camping or offered_onsite

        def staying_night_after_reception(p, rsvp):
            return bool(rsvp and rsvp.staying_night_after_reception is True)

        categories = [
            ("Only coming to ceremony", only_coming_to_ceremony),
            ("Coming to ceremony and reception", coming_to_ceremony_and_reception),
            ("Only coming to reception", only_coming_to_reception),
            (
                "Only coming to reception in the evening",
                only_coming_to_reception_in_evening,
            ),
            (
                "Coming to reception and staying onsite in a yurt or tent (but also hotel if they have been offered to stay onsite)",
                coming_to_reception_and_staying_onsite,
            ),
            ("Staying the night after the reception", staying_night_after_reception),
        ]

        group_categories_map = {id(g): [] for g in groups}

        for cat_title, check_func in categories:
            self.stdout.write(self.style.SUCCESS(f"\n=== {cat_title} ==="))
            matching_groups = []

            for group_item in groups:
                # Check if any person in the group matches the criterion
                matches = False
                for p in group_item["all_persons"]:
                    r = getattr(p, "rsvp", None)
                    if check_func(p, r):
                        matches = True
                        break

                if matches:
                    matching_groups.append(group_item)
                    group_categories_map[id(group_item)].append(cat_title)

            if not matching_groups:
                self.stdout.write("No groups found in this category.")
                continue

            for g in matching_groups:
                lead = g["lead"]
                lead_name = f"{lead.firstname} {lead.lastname}".strip()
                lead_email = (
                    lead.email.strip()
                    if lead.email and lead.email.strip()
                    else "No email"
                )

                if g["other_members"]:
                    other_names = ", ".join(
                        f"{m.firstname} {m.lastname}".strip()
                        for m in g["other_members"]
                    )
                else:
                    other_names = "None"

                self.stdout.write(
                    f"{lead_name} ({lead_email}) - Other members: {other_names}"
                )

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("=== Summary by Group ==="))

        for g in groups:
            lead = g["lead"]
            lead_name = f"{lead.firstname} {lead.lastname}".strip()
            lead_email = (
                lead.email.strip() if lead.email and lead.email.strip() else "No email"
            )

            if g["other_members"]:
                other_names = ", ".join(
                    f"{m.firstname} {m.lastname}".strip() for m in g["other_members"]
                )
            else:
                other_names = "None"

            cat_list = group_categories_map[id(g)]
            cats_str = ", ".join(cat_list) if cat_list else "None"

            self.stdout.write(
                f"{lead_name} ({lead_email}) - Other members: {other_names}"
            )
            self.stdout.write(f"  -> Groups: {cats_str}")

        self.stdout.write("\n" + "-" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"Processed {len(groups)} guest group(s).")
        )
