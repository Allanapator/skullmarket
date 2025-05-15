from modeltranslation.translator import translator, TranslationOptions
from .models import Item, ItemCategory

class ItemCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

class ItemTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)

translator.register(ItemCategory, ItemCategoryTranslationOptions)
translator.register(Item, ItemTranslationOptions)
