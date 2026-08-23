import datetime
from django.test import TestCase, Client
from django.urls import reverse
from project.data import models


class GuestRSVPClosedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.bride = models.Person.objects.create(
            firstname="Jane",
            lastname="Doe",
            email="jane@example.com",
            type=models.Person.Type.BRIDE_GROOM,
        )
        self.groom = models.Person.objects.create(
            firstname="John",
            lastname="Smith",
            email="john@example.com",
            type=models.Person.Type.BRIDE_GROOM,
        )
        self.ceremony_venue = models.Venue.objects.create(name="St Mark Church")
        self.reception_venue = models.Venue.objects.create(name="Grand Barn")
        self.wedding = models.Wedding.objects.create(
            bride=self.bride,
            groom=self.groom,
            ceremony_venue=self.ceremony_venue,
            reception_venue=self.reception_venue,
            date=datetime.date(2025, 9, 20),
            ceremony_start_time=datetime.time(13, 0),
            reception_start_time=datetime.time(15, 0),
            evening_only_start_time=datetime.time(19, 0),
            is_rsvp_open=False,
        )
        self.guest = models.Person.objects.create(
            firstname="Alice",
            lastname="Wonderland",
            email="alice@example.com",
            phone="1234567890",
            invite_code="ALICE123",
            invited_to_ceremony=True,
            invited_to_reception=True,
            allowed_plus_one=True,
        )
        self.rsvp = models.RSVP.objects.create(
            guest=self.guest,
            can_come_to_ceremony=True,
            can_come_to_reception=True,
            song_suggestion="Bohemian Rhapsody",
            day_after_reception_suggestion="Picnic in the park",
            staying_preference=models.RSVP.StayingPreferences.HOTEL,
        )
        food_veg = models.Food.objects.create(category=models.Food.Category.VEGETARIAN)
        self.rsvp.dietary_requirements.add(food_veg)

    def test_login_when_rsvp_closed_redirects_to_rsvp_summary(self):
        response = self.client.post(
            reverse("rsvp"),
            {"code": "ALICE123", "firstname": "Alice"},
        )
        self.assertRedirects(response, reverse("rsvp"))
        self.assertEqual(self.client.session.get("guest_code"), "ALICE123")

    def test_logged_in_summary_page_displays_details_when_closed(self):
        session = self.client.session
        session["guest_code"] = "ALICE123"
        session.save()

        response = self.client.get(reverse("rsvp"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RSVP is currently closed")
        self.assertContains(response, "Your RSVP Summary")
        self.assertContains(response, "Bohemian Rhapsody")
        self.assertContains(response, "Picnic in the park")
        self.assertContains(response, "alice@example.com")
        self.assertContains(response, "1234567890")
        # Ensure edit form links are NOT rendered
        self.assertNotContains(response, reverse("rsvp_basics"))
        self.assertNotContains(response, reverse("rsvp_dietary"))
        self.assertNotContains(response, reverse("rsvp_accommodation"))

    def test_edit_pages_redirect_to_rsvp_when_rsvp_closed(self):
        session = self.client.session
        session["guest_code"] = "ALICE123"
        session.save()

        for url_name in ("rsvp_basics", "rsvp_dietary", "rsvp_accommodation"):
            url = reverse(url_name)
            response_get = self.client.get(url)
            self.assertRedirects(response_get, reverse("rsvp"))

            response_post = self.client.post(url, {})
            self.assertRedirects(response_post, reverse("rsvp"))

    def test_unauthenticated_user_accessing_edit_pages_redirects_to_rsvp(self):
        for url_name in ("rsvp_basics", "rsvp_dietary", "rsvp_accommodation"):
            url = reverse(url_name)
            response_get = self.client.get(url)
            self.assertRedirects(response_get, reverse("rsvp"))


class GuestRSVPOpenTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.bride = models.Person.objects.create(
            firstname="Jane",
            lastname="Doe",
            email="jane@example.com",
            type=models.Person.Type.BRIDE_GROOM,
        )
        self.groom = models.Person.objects.create(
            firstname="John",
            lastname="Smith",
            email="john@example.com",
            type=models.Person.Type.BRIDE_GROOM,
        )
        self.ceremony_venue = models.Venue.objects.create(name="St Mark Church")
        self.reception_venue = models.Venue.objects.create(name="Grand Barn")
        self.wedding = models.Wedding.objects.create(
            bride=self.bride,
            groom=self.groom,
            ceremony_venue=self.ceremony_venue,
            reception_venue=self.reception_venue,
            date=datetime.date(2025, 9, 20),
            ceremony_start_time=datetime.time(13, 0),
            reception_start_time=datetime.time(15, 0),
            evening_only_start_time=datetime.time(19, 0),
            is_rsvp_open=True,
        )
        self.guest = models.Person.objects.create(
            firstname="Bob",
            lastname="Builder",
            invite_code="BOB12345",
            invited_to_ceremony=True,
            invited_to_reception=True,
        )
        self.rsvp = models.RSVP.objects.create(guest=self.guest)

    def test_edit_pages_accessible_when_rsvp_open(self):
        session = self.client.session
        session["guest_code"] = "BOB12345"
        session.save()

        response = self.client.get(reverse("rsvp_basics"))
        self.assertEqual(response.status_code, 200)

        response_summary = self.client.get(reverse("rsvp"))
        self.assertContains(response_summary, reverse("rsvp_basics"))
        self.assertContains(response_summary, "Please complete each section below")
