import uuid

from django.db import models


class RSVP(models.Model):
    class StayingPreferences(models.TextChoices):
        YURT = "YURT", "Yurt"
        CAMPING = "CAMPING", "Camping"
        HOTEL = "HOTEL", "Hotel"

    class DayAfterReceptionMeal(models.TextChoices):
        SELF = "SELF", "Self-catered"
        MEAL = "MEAL", "Meal in a pub"
        BARN = "BARN", "Barn provided meal"

    class TravelBetweenVenues(models.TextChoices):
        YES = "YES", "Yes, interested in options"
        NO = "NO", "No thanks"
        UNSURE = "UNSURE", "Not sure"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    guest = models.ForeignKey(
        "data.Person",
        on_delete=models.PROTECT,
        default=None,
        related_name="guest",
    )

    can_come_to_ceremony = models.BooleanField(blank=True)
    can_come_to_reception = models.BooleanField(blank=True)
    dietary_requirements = models.ManyToManyField("data.Food", blank=True)

    staying_preference = models.CharField(
        max_length=50,
        choices=StayingPreferences.choices,
        null=False,
        blank=True,
    )

    staying_night_after_reception = models.BooleanField(blank=True)
    evening_meal_day_after_reception = models.CharField(
        max_length=50,
        choices=DayAfterReceptionMeal.choices,
        null=False,
        blank=True,
    )
    day_after_reception_suggestion = models.CharField(max_length=255)

    travel_between_venues = models.CharField(
        max_length=50,
        choices=TravelBetweenVenues.choices,
        null=False,
        blank=True,
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.guest.firstname} {self.guest.lastname}"
