from django import forms


class BasicsForm(forms.Form):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)

    can_come_to_ceremony = forms.BooleanField(required=False)
    can_come_to_reception = forms.BooleanField(required=False)

    plus_one = forms.BooleanField(required=False)
    plus_one_firstname = forms.CharField(required=False)
    plus_one_lastname = forms.CharField(required=False)
    plus_one_email = forms.EmailField(required=False)
    plus_one_phone = forms.CharField(required=False)
