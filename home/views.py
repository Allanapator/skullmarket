# home/views.py
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from .forms import ContactForm
from django.views.decorators.http import require_http_methods

def homepage(request):
    if request.user.is_authenticated:
        return redirect('offer_list')
    return render(request, 'home/homepage.html')


@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Tu peux traiter ici et envoyer un email si besoin
            messages.success(request, _("Votre message a été envoyé."))
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})