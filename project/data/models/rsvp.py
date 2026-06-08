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
        NO = "NO", "No, thanks"
        UNSURE = "UNSURE", "Not sure"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    guest = models.OneToOneField(
        "data.Person",
        on_delete=models.PROTECT,
        default=None,
        related_name="guest",
    )

    can_come_to_ceremony = models.BooleanField(blank=True, null=True)
    can_come_to_reception = models.BooleanField(blank=True, null=True)
    song_suggestion = models.CharField(max_length=255)

    dietary_requirements = models.ManyToManyField(
        "data.Food", blank=True, related_name="rsvp_dietary_requirements"
    )

    plus_one = models.OneToOneField(
        "data.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="plus_one_of",
    )

    staying_preference = models.CharField(
        max_length=50,
        choices=StayingPreferences.choices,
        null=False,
        blank=True,
    )

    staying_night_after_reception = models.BooleanField(blank=True, null=True)
    morning_meal_day_after_reception = models.BooleanField(blank=True, null=True)
    evening_meal_day_after_reception = models.BooleanField(blank=True, null=True)
    day_after_reception_suggestion = models.CharField(max_length=255)

    class Meta:
        ordering = ["guest__lastname"]
