from django import forms


class RegistrationForm(forms.Form):
    nickname = forms.CharField(max_length=255)
