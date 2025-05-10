from django.shortcuts import render, redirect
from market.models import TradeOffer, PurchaseIntent
from items.models import ItemCategory, Item
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from .forms import TradeOfferForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.http import JsonResponse, HttpResponse


@login_required
def offer_list(request):
    search = request.GET.get('search', '').strip()
    intents = PurchaseIntent.objects.filter(offer=OuterRef('pk'))
    offers = TradeOffer.objects.annotate(
        has_buyer=Exists(intents)
    ).filter(status='open', has_buyer=False).select_related('item_offered', 'seller')

    if search:
        offers = offers.filter(item_offered__name__icontains=search)

    categories = ItemCategory.objects.all()
    return render(request, 'market/offer_list.html', {
        'offers': offers,
        'categories': categories,
        'show_buy_button': True,
    })


@login_required
def create_offer(request):
    if request.method == 'POST':
        form = TradeOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.seller = request.user
            offer.save()
            return redirect('offer_list')
    else:
        form = TradeOfferForm()
    return render(request, 'market/create_offer.html', {'form': form})


@login_required
def my_offers(request):
    offers = TradeOffer.objects.filter(seller=request.user).select_related('item_offered', 'seller')
    categories = ItemCategory.objects.all()
    return render(request, 'market/offer_list.html', {
        'offers': offers,
        'categories': categories,
        'show_buy_button': False,
    })


@login_required
def my_purchases(request):
    # On récupère toutes les offres où l'utilisateur a fait un achat
    offer_ids = PurchaseIntent.objects.filter(buyer=request.user).values_list('offer_id', flat=True)
    offers = TradeOffer.objects.filter(id__in=offer_ids).select_related('item_offered', 'seller')
    categories = ItemCategory.objects.all()
    return render(request, 'market/offer_list.html', {
        'offers': offers,
        'categories': categories,
        'show_buy_button': False,
    })


@login_required
def purchase_offer(request):
    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        message = request.POST.get('message', '')
        consent = request.POST.get('consent')

        if not consent:
            messages.error(request, "Vous devez accepter le partage de vos coordonnées.")
            return redirect('offer_list')

        try:
            offer = TradeOffer.objects.get(id=offer_id)
        except TradeOffer.DoesNotExist:
            messages.error(request, "Cette offre n'existe pas.")
            return redirect('offer_list')

        # Création de l'intention d'achat
        PurchaseIntent.objects.create(
            buyer=request.user,
            offer=offer,
            message=message
        )

        # Fermeture de l'offre
        offer.status = 'closed'
        offer.save()

        # Envoi d'un email au vendeur
        subject = f"[Skull Market] {request.user.ubisoft_username} souhaite acheter votre objet"
        seller_email = offer.seller.email

        context = {
            'offer': offer,
            'buyer': request.user,
            'message': message,
        }

        email_body = render_to_string('emails/purchase_notification.txt', context)

        send_mail(
            subject,
            email_body,
            settings.DEFAULT_FROM_EMAIL,
            [seller_email],
            fail_silently=False
        )

        messages.success(request, "Votre intention d'achat a été envoyée au vendeur par email.")
        return redirect('offer_list')

    return redirect('offer_list')

@login_required
def ajax_filtered_offers(request):
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category')

    offers = TradeOffer.objects.filter(status='open')
    if search:
        offers = offers.filter(item_offered__name__icontains=search)
    if category_id:
        offers = offers.filter(item_offered__category_id=category_id)

    offers = offers.select_related('item_offered', 'seller')

    html = render_to_string('market/_offers_table.html', {
        'offers': offers,
        'show_buy_button': True,
        'request': request
    })
    return HttpResponse(html)

@login_required
def ajax_items(request):
    category = request.GET.get('category')
    search = request.GET.get('search', '').strip()

    queryset = Item.objects.all()
    if category:
        queryset = queryset.filter(category_id=category)
    if search:
        queryset = queryset.filter(name__icontains=search)

    results = [
        {
            'id': item.id,
            'name': item.name,
            'image': item.image.url if item.image else '',
        }
        for item in queryset[:50]
    ]
    return JsonResponse(results, safe=False)