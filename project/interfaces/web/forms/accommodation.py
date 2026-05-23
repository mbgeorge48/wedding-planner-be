from django import forms

from project.data import models


class AccommodationForm(forms.Form):
    staying_preference = forms.ChoiceField(
        choices=models.RSVP.StayingPreferences.choices,
        required=False,
    )
    staying_night_after_reception = forms.BooleanField(required=False)

    morning_meal_day_after_reception = forms.BooleanField(required=False)
    evening_meal_day_after_reception = forms.BooleanField(required=False)
    day_after_reception_suggestion = forms.CharField(required=False, max_length=255)
