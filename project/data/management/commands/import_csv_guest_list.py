from django.core.management.base import BaseCommand
from project.actions.person import create_person
import os
import csv

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
    help = "Upload a CSV guest list"

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)
        parser.add_argument("force_update", type=bool, nargs="?", default=False)

    def handle(self, *args, **options):
        force_update = options["force_update"]
        file_name = options["file_name"]

        if not os.path.exists(file_name):
            self.stdout.write(self.style.ERROR(f"CSV file not found: {file_name}"))
            raise SystemExit

        guests = []
        with open(file_name, mode="r") as file:
            csv_file = csv.DictReader(file)

            # Clean the header names
            headers = csv_file.fieldnames = [h.strip() for h in csv_file.fieldnames]

            for line in csv_file:
                cleaned = {}
                for k, v in line.items():
                    key = k.strip()  # clean the key

                    # Clean string values
                    if isinstance(v, str):
                        value = v.strip()
                    else:
                        value = v

                    # Convert boolean keys
                    if key in boolean_keys:
                        cleaned[key] = (
                            value.lower() == "y" if isinstance(value, str) else False
                        )
                    else:
                        cleaned[key] = value

                guests.append(cleaned)

        missing = set(required_keys) - set(headers)
        if missing:
            print("Missing keys:", missing)
            self.stdout.write(
                self.style.ERROR(
                    "Ensure all headings are supplied. The order of the keys does not matter",
                )
            )
            self.stdout.write(self.style.WARNING(f"Missing: {", ".join(missing)}"))
            raise SystemExit

        for guest in guests:
            try:
                person, created = create_person(update_existing=force_update, **guest)
                print(
                    f"{person.firstname} {person.lastname} => {"created" if created else "updated"}"
                )
            except TypeError as e:
                print(e, f"function called with {guest}")
