from django.contrib import admin
from .models import Item, ItemCategory
from modeltranslation.admin import TranslationAdmin

@admin.register(ItemCategory)
class ItemCategoryAdmin(TranslationAdmin):
    list_display = ('translated_name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def translated_name(self, obj):
        return obj.name
    translated_name.short_description = "Nom"

@admin.register(Item)
class ItemAdmin(TranslationAdmin):
    list_display = ('id', 'translated_name', 'category', 'tradable', 'image')
    list_filter = ('category', 'tradable')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def translated_name(self, obj):
        return obj.name
    translated_name.short_description = "Nom"
