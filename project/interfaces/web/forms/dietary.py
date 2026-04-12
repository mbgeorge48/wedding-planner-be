from django import forms

from project.data import models


class DietaryForm(forms.Form):
    dietary_categories = forms.MultipleChoiceField(
        choices=models.Food.Category.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    dietary_other_detail = forms.CharField(required=False)

    plus_one_dietary_categories = forms.MultipleChoiceField(
        choices=models.Food.Category.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    # TODO: This field is only required if the choice selected is OTHER
    plus_one_dietary_other_detail = forms.CharField(required=False)

    def __init__(self, *args, has_plus_one=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not has_plus_one:
            del self.fields["plus_one_dietary_categories"]
            del self.fields["plus_one_dietary_other_detail"]
