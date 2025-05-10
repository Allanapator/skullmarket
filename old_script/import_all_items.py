import os
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from items.models import Item, ItemCategory

class Command(BaseCommand):
    help = "Importe tous les items depuis les fichiers JSON du dossier skullandbones"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'skullandbones'
        files = [
            ('items.json', 'type'),  # clé 'type' -> catégorie
            ('materials.json', 'category'),
            ('commodities.json', 'category'),
        ]

        for file_name, category_key in files:
            json_path = base_dir / file_name

            if not json_path.exists():
                self.stderr.write(f"[ERREUR] {file_name} non trouvé.")
                continue

            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)

            for item_id, item_data in data.items():
                slug = item_id.lower()
                name = item_data.get("id", item_id)  # ou fallback vers item_id
                description = f"{file_name.replace('.json', '')} : {item_id}"
                image = ""
                tradable = True

                category_slug = item_data.get(category_key, "autre").lower()
                category_name = category_slug.replace("_", " ").capitalize()
                category, _ = ItemCategory.objects.get_or_create(name=category_name, slug=category_slug)

                obj, created = Item.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "description": description,
                        "image": image,
                        "category": category,
                        "tradable": tradable,
                    }
                )
                self.stdout.write(f"[{file_name}] {'Ajouté' if created else 'Mis à jour'} : {name}")
