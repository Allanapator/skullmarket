from django.db import models
from django.conf import settings
from items.models import Item

class TradeOffer(models.Model):
    STATUS_CHOICES = (
        ('open', 'En cours'),
        ('closed', 'Fermée'),
    )

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    item_offered = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='offers')
    quantity = models.PositiveIntegerField()

    PRICE_TYPE_CHOICES = (
        ('money', 'Argent'),
        ('item', 'Objet'),
    )
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    price_money = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='reverse_offers')
    price_item_quantity = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_offered.name} x{self.quantity} par {self.seller}"

class PurchaseIntent(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchase_intents')
    offer = models.ForeignKey(TradeOffer, on_delete=models.CASCADE, related_name='interests')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} → {self.offer}"
