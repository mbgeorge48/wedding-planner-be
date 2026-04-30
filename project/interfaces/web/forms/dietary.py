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
    plus_one_dietary_other_detail = forms.CharField(required=False)

    def __init__(self, *args, has_plus_one=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not has_plus_one:
            del self.fields["plus_one_dietary_categories"]
            del self.fields["plus_one_dietary_other_detail"]

    def clean(self):
        cleaned_data = super().clean()

        # Validation for main guest
        if models.Food.Category.OTHER in (
            cleaned_data.get("dietary_categories") or []
        ) and not cleaned_data.get("dietary_other_detail"):
            self.add_error(
                "dietary_other_detail",
                "Please provide details for 'Other' dietary requirements.",
            )

        # Validation for plus one
        if models.Food.Category.OTHER in (
            cleaned_data.get("plus_one_dietary_categories") or []
        ) and not cleaned_data.get("plus_one_dietary_other_detail"):
            self.add_error(
                "plus_one_dietary_other_detail",
                "Please provide details for the plus one's 'Other' dietary requirements.",
            )

        return cleaned_data
