from django import forms

from project.data import models


class TravelForm(forms.Form):
    travel_between_venues = forms.ChoiceField(
        choices=models.RSVP.TravelBetweenVenues.choices,
        required=False,
        widget=forms.RadioSelect,
    )
