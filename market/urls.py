from django.urls import path
from .views import offer_list, create_offer, my_offers, my_purchases, purchase_offer, ajax_filtered_offers, ajax_items


urlpatterns = [
    path('', offer_list, name='offer_list'),
    path('nouvelle-vente/', create_offer, name='create_offer'),
    path('mes-ventes/', my_offers, name='my_offers'),
    path('mes-achats/', my_purchases, name='my_purchases'),
    path('acheter/', purchase_offer, name='purchase_offer'),
    path('ajax-filter/', ajax_filtered_offers, name='ajax_filtered_offers'),
    path('ajax-items/', ajax_items, name='ajax_items'),
]
