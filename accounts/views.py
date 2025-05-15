from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from .models import User
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from captcha.fields import CaptchaField

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_("Mot de passe")
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label=_("Confirmer le mot de passe")
    )
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = [
            'username', 'email', 'ubisoft_username',
            'discord_username', 'psn_username', 'xbox_username', 'steam_username',
            'password', 'password_confirm'
        ]
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _("Adresse email"),
            'ubisoft_username': _("Pseudo Ubisoft"),
            'discord_username': _("Pseudo Discord"),
            'psn_username': _("Pseudo PSN"),
            'xbox_username': _("Pseudo Xbox"),
            'steam_username': _("Pseudo Steam"),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password_confirm')
        if pwd or pwd2:
            if pwd != pwd2:
                self.add_error('password_confirm', _("Les mots de passe ne correspondent pas."))
            elif len(pwd) < 8:
                self.add_error('password', _("Le mot de passe doit contenir au moins 8 caractères."))
        return cleaned_data


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            subject = _("Bienvenue sur Skull Market ⚓")
            message = render_to_string('emails/welcome.txt', {
                'user': user,
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            login(request, user)
            return redirect('offer_list')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def edit_account(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # ← garde l'utilisateur connecté
            messages.success(request, _("Vos informations ont bien été mises à jour."))
            return redirect('offer_list')
    else:
        form = SignupForm(instance=request.user)
    return render(request, 'accounts/edit_account.html', {'form': form})