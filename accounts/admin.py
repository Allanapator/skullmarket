from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'ubisoft_username', 'discord_username', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Infos Ubisoft', {'fields': ('ubisoft_username', 'discord_username')}),
    )
