from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    ubisoft_username = models.CharField(max_length=100, unique=True)
    discord_username = models.CharField(max_length=100, blank=True, null=True)
    psn_username = models.CharField(max_length=100, blank=True, null=True)
    xbox_username = models.CharField(max_length=100, blank=True, null=True)
    steam_username = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.ubisoft_username or self.username
