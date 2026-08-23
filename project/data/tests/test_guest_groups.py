from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from project.data.models import RSVP, Person, PersonGroup


class GuestGroupsCommandTests(TestCase):
    def test_no_guests(self):
        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()
        self.assertIn("No guests or groups found.", output)

    def test_only_coming_to_ceremony(self):
        p1 = Person.objects.create(
            firstname="Alice",
            lastname="Smith",
            email="alice@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=True,
            can_come_to_reception=False,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Only coming to ceremony ===", output)
        self.assertIn("Alice Smith (alice@example.com) - Other members: None", output)

    def test_coming_to_ceremony_and_reception(self):
        p1 = Person.objects.create(
            firstname="Bob",
            lastname="Jones",
            email="bob@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Coming to ceremony and reception ===", output)
        self.assertIn("Bob Jones (bob@example.com) - Other members: None", output)

    def test_only_coming_to_reception(self):
        p1 = Person.objects.create(
            firstname="Charlie",
            lastname="Brown",
            email="charlie@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=False,
            can_come_to_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Only coming to reception ===", output)
        self.assertIn(
            "Charlie Brown (charlie@example.com) - Other members: None", output
        )

    def test_only_coming_to_reception_in_evening(self):
        p1 = Person.objects.create(
            firstname="Diana",
            lastname="Prince",
            email="diana@example.com",
            evening_only_reception=True,
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=False,
            can_come_to_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Only coming to reception in the evening ===", output)
        self.assertIn("Diana Prince (diana@example.com) - Other members: None", output)

    def test_reception_and_staying_onsite(self):
        # Yurt preference
        p1 = Person.objects.create(
            firstname="Eve",
            lastname="Adams",
            email="eve@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_reception=True,
            staying_preference=RSVP.StayingPreferences.YURT,
        )

        # Hotel preference, but allowed onsite
        p2 = Person.objects.create(
            firstname="Frank",
            lastname="Castle",
            email="frank@example.com",
            allowed_to_stay_onsite=True,
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p2,
            can_come_to_reception=True,
            staying_preference=RSVP.StayingPreferences.HOTEL,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        cat_title = "=== Coming to reception and staying onsite in a yurt or tent (but also hotel if they have been offered to stay onsite) ==="
        self.assertIn(cat_title, output)
        self.assertIn("Eve Adams (eve@example.com) - Other members: None", output)
        self.assertIn("Frank Castle (frank@example.com) - Other members: None", output)

    def test_staying_night_after_reception(self):
        p1 = Person.objects.create(
            firstname="Grace",
            lastname="Hopper",
            email="grace@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            staying_night_after_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Staying the night after the reception ===", output)
        self.assertIn("Grace Hopper (grace@example.com) - Other members: None", output)

    def test_person_group_lead_and_members(self):
        pg = PersonGroup.objects.create()
        p1 = Person.objects.create(
            firstname="Harry",
            lastname="Potter",
            email="harry@example.com",
            group=pg,
            type=Person.Type.STANDARD,
        )
        p2 = Person.objects.create(
            firstname="Ron",
            lastname="Weasley",
            email="ron@example.com",
            group=pg,
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
        )
        RSVP.objects.create(
            guest=p2,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Coming to ceremony and reception ===", output)
        self.assertIn(
            "Harry Potter (harry@example.com) - Other members: Ron Weasley", output
        )

    def test_plus_one_in_group(self):
        host = Person.objects.create(
            firstname="Iris",
            lastname="West",
            email="iris@example.com",
            type=Person.Type.STANDARD,
        )
        guest_plus_one = Person.objects.create(
            firstname="Barry",
            lastname="Allen",
            email="barry@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=host,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
            plus_one=guest_plus_one,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn(
            "Iris West (iris@example.com) - Other members: Barry Allen", output
        )

    def test_summary_by_group_multiple_categories(self):
        p1 = Person.objects.create(
            firstname="John",
            lastname="Wick",
            email="john@example.com",
            type=Person.Type.STANDARD,
        )
        RSVP.objects.create(
            guest=p1,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
            staying_night_after_reception=True,
        )

        out = StringIO()
        call_command("generate_guest_groups", stdout=out)
        output = out.getvalue()

        self.assertIn("=== Summary by Group ===", output)
        self.assertIn("John Wick (john@example.com) - Other members: None", output)
        self.assertIn(
            "  -> Groups: Coming to ceremony and reception, Staying the night after the reception",
            output,
        )
