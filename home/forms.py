from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    reason = forms.ChoiceField(
        label=_("Raison du contact"),
        choices=[
            ("bug", _("Bug sur le site")),
            ("missing", _("Il manque un élément")),
            ("other", _("Autre")),
        ],
        widget=forms.Select(attrs={"class": "form-select"})
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={"rows": 5, "class": "form-control"})
    )
    captcha = CaptchaField()
