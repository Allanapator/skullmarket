from django import forms
from market.models import TradeOffer
from items.models import Item

class TradeOfferForm(forms.ModelForm):
    class Meta:
        model = TradeOffer
        fields = ['item_offered', 'quantity', 'price_type', 'price_money', 'price_item', 'price_item_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pour ne pas afficher les objets non échangeables
        self.fields['item_offered'].queryset = Item.objects.filter(tradable=True)
        self.fields['price_item'].queryset = Item.objects.filter(tradable=True)

        self.fields['price_money'].required = False
        self.fields['price_item'].required = False
        self.fields['price_item_quantity'].required = False
