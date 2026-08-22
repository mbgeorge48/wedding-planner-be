import urllib.parse
from django.core.management.base import BaseCommand, CommandError

from project.data.models import RSVP


class Command(BaseCommand):
    help = "Generate Monzo me links for guests based on their day-after reception meal choices"

    def add_arguments(self, parser):
        parser.add_argument(
            "monzo_url",
            type=str,
            help="Base Monzo me URL (e.g. https://monzo.me/username/10.00?d={initials}-breakfast%20and%20dinner&h=DMMGdm)",
        )

    def handle(self, *args, **options):
        monzo_url = options["monzo_url"]

        if not monzo_url:
            raise CommandError("monzo_url argument is required.")

        if not monzo_url.startswith(("http://", "https://")):
            monzo_url = "https://" + monzo_url

        parsed = urllib.parse.urlparse(monzo_url)
        path_parts = [p for p in parsed.path.split("/") if p]

        if not parsed.netloc or not path_parts:
            raise CommandError(f"Invalid Monzo me URL provided: {options['monzo_url']}")

        username = path_parts[0]
        base_query_params = dict(urllib.parse.parse_qsl(parsed.query))

        rsvps = RSVP.objects.select_related("guest").order_by(
            "guest__lastname", "guest__firstname"
        )

        combos = [
            (
                "Breakfast no dinner",
                lambda r: r.morning_meal_day_after_reception and not r.evening_meal_day_after_reception,
                12.00,
                "breakfast",
            ),
            (
                "Dinner no breakfast",
                lambda r: r.evening_meal_day_after_reception and not r.morning_meal_day_after_reception,
                10.00,
                "dinner",
            ),
            (
                "Breakfast and dinner",
                lambda r: r.morning_meal_day_after_reception and r.evening_meal_day_after_reception,
                22.00,
                "breakfast and dinner",
            ),
        ]

        total_links = 0

        for category_name, filter_func, amount, meal_desc in combos:
            category_rsvps = [r for r in rsvps if filter_func(r)]

            self.stdout.write(self.style.SUCCESS(f"\n=== {category_name} (£{amount:.2f}) ==="))

            if not category_rsvps:
                self.stdout.write("No guests found in this category.")
                continue

            for rsvp in category_rsvps:
                guest = rsvp.guest
                fn_initial = guest.firstname.strip()[0].upper() if guest.firstname and guest.firstname.strip() else ""
                ln_initial = guest.lastname.strip()[0].upper() if guest.lastname and guest.lastname.strip() else ""
                initials = f"{fn_initial}{ln_initial}"

                query_params = dict(base_query_params)
                query_params["d"] = f"{initials}-{meal_desc}"

                sorted_params = sorted(query_params.items(), key=lambda x: x[0])
                encoded_query = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)

                new_path = f"/{username}/{amount:.2f}"
                url = urllib.parse.urlunparse((
                    parsed.scheme or "https",
                    parsed.netloc,
                    new_path,
                    parsed.params,
                    encoded_query,
                    parsed.fragment,
                ))

                self.stdout.write(f"{guest.firstname} {guest.lastname}: {url}")
                total_links += 1

        self.stdout.write("\n" + "-" * 80)
        self.stdout.write(self.style.SUCCESS(f"Generated Monzo me links for {total_links} guests."))
