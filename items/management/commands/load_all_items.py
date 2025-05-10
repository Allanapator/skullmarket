# items/management/commands/load_all_items.py

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
    help = "Importe et enrichit tous les items depuis les JSON, en mettant à jour noms, descriptions, catégories, suffixes et préfixes."

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'skullandbones'

        # --- 1. Import de base ---
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
                category, _ = ItemCategory.objects.get_or_create(name=category_name, slug=category_slug)

                Item.objects.update_or_create(
                    slug=slug.lower(),
                    defaults={
                        "name": name,
                        "description": description,
                        "category": category,
                        "tradable": True,
                    }
                )

        self.stdout.write("[✓] Import initial terminé.")

        # --- 2. Enrichissement ---
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

            item.name = data.get("name", item.name)
            desc = data.get("description", "")
            if isinstance(desc, dict):
                desc = desc.get("general") or next(iter(desc.values()), "")
            item.description = desc or item.description
            item.save()

        self.stdout.write("[✓] Traductions appliquées.")

        # --- 3. Majuscules sur préfixes ---
        en_prefixes_path = base_dir / 'en_items.json'
        if en_prefixes_path.exists():
            en_prefixes = json.load(open(en_prefixes_path, encoding='utf-8')).get("items", {})
            for item in Item.objects.all():
                for prefix_key, prefix_data in en_prefixes.items():
                    if item.slug.lower().startswith(prefix_key.lower()):
                        suffix = item.slug[len(prefix_key):]
                        capitalized = prefix_data.get("name", prefix_key)
                        item.name = f"{capitalized}{suffix}"
                        item.save()
                        break
            self.stdout.write("[✓] Préfixes capitalisés.")

        # --- 4. Chiffres romains ---
        for item in Item.objects.all():
            for digit, roman in ROMAN_SUFFIXES.items():
                if item.name.endswith(digit):
                    item.name = item.name[:-len(digit)].rstrip() + roman
                    item.save()
                    break

        self.stdout.write(self.style.SUCCESS("[✓] Tous les items ont été importés et enrichis."))
