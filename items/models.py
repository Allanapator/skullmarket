from django.db import models

class ItemCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    tradable = models.BooleanField(default=True)

    def __str__(self):
        return self.name
