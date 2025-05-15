# Modifications pour load_all_items.py avec gestion des traductions en/fr

import json
import re
import unicodedata
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from items.models import Item, ItemCategory

ROMAN_SUFFIXES = {
    "1": " I", "2": " II", "3": " III", "4": " IV", "5": " V",
    "6": " VI", "7": " VII", "8": " VIII", "9": " IX", "10": " X",
}

class Command(BaseCommand):
    help = "Importe et enrichit tous les items avec traductions en/fr."

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'skullandbones'

        sources = [
            ('items.json', 'type'),
            ('materials.json', 'category'),
            ('commodities.json', 'category'),
        ]

        for file_name, cat_key in sources:
            path = base_dir / file_name
            if not path.exists():
                self.stderr.write(f"[ERREUR] Fichier introuvable : {path}")
                continue

            with open(path, encoding='utf-8') as f:
                data = json.load(f)

            for slug, item_data in data.items():
                name = item_data.get("id", slug)
                description = f"{file_name.replace('.json', '')} : {slug}"
                category_slug = item_data.get(cat_key, "autre").lower()
                category_name = category_slug.replace("_", " ").capitalize()
                category, _ = ItemCategory.objects.get_or_create(slug=category_slug, defaults={"name_fr": category_name})

                Item.objects.update_or_create(
                    slug=slug.lower(),
                    defaults={
                        "name_fr": name,
                        "description_fr": description,
                        "category": category,
                        "tradable": True,
                    }
                )

        self.stdout.write("[✓] Import FR terminé.")

        # Import EN
        translation_sources = {
            "en_items.json": "items",
            "en_materials.json": "materials",
            "en_commodities.json": "commodities",
        }
        translations = {}
        for file, root_key in translation_sources.items():
            path = base_dir / file
            if not path.exists(): continue
            with open(path, encoding='utf-8') as f:
                translations.update(json.load(f).get(root_key, {}))

        for item in Item.objects.all():
            data = translations.get(item.slug)
            if not data: continue

            item.name_en = data.get("name", item.name_fr)
            desc = data.get("description", "")
            if isinstance(desc, dict):
                desc = desc.get("general") or next(iter(desc.values()), "")
            item.description_en = desc or item.description_fr
            item.save()

        self.stdout.write("[✓] Traductions EN appliquées.")

        # Suffixes romains sur name_fr et name_en
        for item in Item.objects.all():
            for digit, roman in ROMAN_SUFFIXES.items():
                if item.name_fr.endswith(digit):
                    item.name_fr = item.name_fr[:-len(digit)].rstrip() + roman
                if item.name_en and item.name_en.endswith(digit):
                    item.name_en = item.name_en[:-len(digit)].rstrip() + roman
            item.save()

        self.stdout.write(self.style.SUCCESS("[✓] Tous les items ont été enrichis."))
