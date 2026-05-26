import urllib.parse

import qrcode
from django.core.management.base import BaseCommand
from qrcode.constants import ERROR_CORRECT_M

from project.data.models import Person


class Command(BaseCommand):
    help = "Generate RSVP URLs for all guests in the Person table"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            default="http://localhost:8000",
            help="Base URL of the site (default: http://localhost:8000)",
        )
        parser.add_argument(
            "--create-qr-codes",
            action="store_true",
            help="Create QR codes for each URL",
        )

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        create_qr_codes = options["create_qr_codes"]
        people = Person.objects.all()

        if not people.exists():
            self.stdout.write(self.style.WARNING("No people found in the database."))
            return

        self.stdout.write(self.style.SUCCESS(f"Generating URLs with base: {base_url}"))
        self.stdout.write("-" * 80)

        for person in people:
            if not person.invite_code:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {person.firstname} {person.lastname}: No invite code"
                    )
                )
                continue

            params = {
                "firstname": person.firstname,
                "code": person.invite_code,
            }
            query_string = urllib.parse.urlencode(params)
            url = f"{base_url}/rsvp/?{query_string}"

            self.stdout.write(f"{person.firstname} {person.lastname}: {url}")
            if create_qr_codes:
                # qr = qrcode.make(url)
                filename = f"{person.firstname}_{person.lastname}_qr.png"
                # qr.save(filename)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_M,
                    box_size=18,
                )
                qr.add_data(url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                with open(filename, "wb") as f:
                    img.save(f)

        self.stdout.write("-" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"Generated URLs for {people.count()} people.")
        )
