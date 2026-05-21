import urllib.parse

from django.core.management.base import BaseCommand
from django.urls import reverse

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

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
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
            # Hardcoding /rsvp/ as requested, but joining properly
            url = f"{base_url}/rsvp/?{query_string}"

            self.stdout.write(f"{person.firstname} {person.lastname}: {url}")

        self.stdout.write("-" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"Generated URLs for {people.count()} people.")
        )
