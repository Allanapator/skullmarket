from django.contrib import admin
from .models import TradeOffer, PurchaseIntent

@admin.register(TradeOffer)
class TradeOfferAdmin(admin.ModelAdmin):
    list_display = ('item_offered', 'quantity', 'price_type', 'price_money', 'price_item', 'price_item_quantity', 'seller', 'status', 'created_at')
    list_filter = ('status', 'price_type')
    search_fields = ('item_offered__name', 'seller__ubisoft_username')

@admin.register(PurchaseIntent)
class PurchaseIntentAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'offer', 'created_at')
    search_fields = ('buyer__ubisoft_username', 'offer__item_offered__name')
