import csv
import os

from django.core.management.base import BaseCommand

from project.actions.person import create_person
from project.data import models

required_keys = [
    "firstname",
    "lastname",
    "email",
    "type",
    "invited_to_ceremony",
    "invited_to_reception",
    "allowed_plus_one",
    "allowed_to_stay_onsite",
    "allowed_to_stay_in_yurt",
    "allowed_to_stay_night_after_reception",
    "postal_index",
]

boolean_keys = [
    "invited_to_ceremony",
    "invited_to_reception",
    "allowed_plus_one",
    "allowed_to_stay_onsite",
    "allowed_to_stay_in_yurt",
    "allowed_to_stay_night_after_reception",
]


class Command(BaseCommand):
    help = "Upload a CSV guest list and automatically group them"

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update existing guests if they already exist",
        )

    def handle(self, *args, **options):
        force_update = options["force"]
        file_name = options["file_name"]

        if not os.path.exists(file_name):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {file_name}"))
            raise SystemExit

        # Cache groups created during this run to avoid multiple lookups
        group_cache = {}

        guests = []
        with open(file_name, mode="r", encoding="utf-8-sig") as file:
            csv_file = csv.DictReader(file)
            if not csv_file.fieldnames:
                return

            # Clean the header names
            headers = csv_file.fieldnames = [h.strip() for h in csv_file.fieldnames]

            missing = set(required_keys) - set(headers)
            if missing:
                self.stdout.write(self.style.ERROR("Missing headings in CSV:"))
                self.stdout.write(self.style.WARNING(f"{', '.join(missing)}"))
                self.stdout.write(
                    self.style.NOTICE(
                        "Ensure all headings are supplied. The order of the keys does not matter. 'phone' is optional."
                    )
                )
                raise SystemExit

            for line in csv_file:
                cleaned = {}
                for k, v in line.items():
                    key = k.strip()
                    value = v.strip() if isinstance(v, str) else v

                    if key in boolean_keys:
                        cleaned[key] = value.lower() in ["y", "yes", "true", "1"]
                    else:
                        cleaned[key] = value

                guests.append(cleaned)

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(guests)} guests. Starting import...")
        )

        for guest in guests:
            postal_index = guest.pop("postal_index", None)

            # Handle Grouping
            group = None
            if postal_index:
                if postal_index not in group_cache:
                    group = models.PersonGroup.objects.create()
                    group_cache[postal_index] = group
                else:
                    group = group_cache[postal_index]

            guest["group"] = group

            try:
                # Extract core fields required by action
                firstname = guest.pop("firstname")
                lastname = guest.pop("lastname")
                email = guest.pop("email")
                person_type = guest.pop("type")

                person, created = create_person(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    type=person_type,
                    update_existing=force_update,
                    **guest,
                )

                status = "created" if created else "updated"
                group_status = f" (Group: {postal_index})" if postal_index else ""
                self.stdout.write(
                    f"✓ {person.firstname} {person.lastname} => {status}{group_status}"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Error importing {guest.get('firstname', 'Unknown')}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(
            self.style.SUCCESS(f"Import complete. Groups processed: {len(group_cache)}")
        )
