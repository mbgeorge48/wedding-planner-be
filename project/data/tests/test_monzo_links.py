from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from project.data.models import RSVP, Person


class MonzoLinksCommandTests(TestCase):
    def setUp(self):
        # Combo 1: Breakfast no dinner (£12)
        self.p1 = Person.objects.create(
            firstname="Alice",
            lastname="Smith",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=self.p1,
            morning_meal_day_after_reception=True,
            evening_meal_day_after_reception=False,
        )

        # Combo 2: Dinner no breakfast (£10)
        self.p2 = Person.objects.create(
            firstname="Bob",
            lastname="Jones",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=self.p2,
            morning_meal_day_after_reception=False,
            evening_meal_day_after_reception=True,
        )

        # Combo 3: Breakfast and dinner (£22)
        self.p3 = Person.objects.create(
            firstname="Matthew",
            lastname="George",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=self.p3,
            morning_meal_day_after_reception=True,
            evening_meal_day_after_reception=True,
        )

        # Neither (should not be in output)
        self.p4 = Person.objects.create(
            firstname="Charlie",
            lastname="Brown",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=self.p4,
            morning_meal_day_after_reception=False,
            evening_meal_day_after_reception=False,
        )

    def test_generate_monzo_links(self):
        out = StringIO()
        input_url = "https://monzo.me/matthewbenjamingeorge/10.00?d=%7Binitials%7D-breakfast%20and%20dinner&h=DMMGdm"

        call_command("generate_monzo_links", input_url, stdout=out)
        output = out.getvalue()

        # Check Alice Smith (AS): £12.00, d=AS-breakfast
        self.assertIn("Alice Smith: https://monzo.me/matthewbenjamingeorge/12.00?d=AS-breakfast&h=DMMGdm", output)

        # Check Bob Jones (BJ): £10.00, d=BJ-dinner
        self.assertIn("Bob Jones: https://monzo.me/matthewbenjamingeorge/10.00?d=BJ-dinner&h=DMMGdm", output)

        # Check Matthew George (MG): £22.00, d=MG-breakfast and dinner
        self.assertIn("Matthew George: https://monzo.me/matthewbenjamingeorge/22.00?d=MG-breakfast%20and%20dinner&h=DMMGdm", output)

        # Charlie Brown should not appear
        self.assertNotIn("Charlie Brown", output)

    def test_invalid_url_raises_command_error(self):
        with self.assertRaises(CommandError):
            call_command("generate_monzo_links", "invalid_url")
