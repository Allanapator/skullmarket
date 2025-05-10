from django.contrib import admin
from .models import Item, ItemCategory

@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('image', 'name', 'category', 'tradable')
    list_filter = ('category', 'tradable')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
