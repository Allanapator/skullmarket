import os
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from items.models import Item

class Command(BaseCommand):
    help = "Met à jour les noms et descriptions des items depuis les fichiers en_*.json"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'skullandbones'

        sources = {
            "en_items.json": "items",
            "en_materials.json": "materials",
            "en_commodities.json": "commodities",
        }

        translations = {}

        for filename, root_key in sources.items():
            path = base_dir / filename
            if not path.exists():
                self.stderr.write(f"[!] Fichier non trouvé : {path}")
                continue

            with open(path, encoding='utf-8') as f:
                content = json.load(f)
                translations.update(content.get(root_key, {}))

        updated = 0
        for item in Item.objects.all():
            slug = item.slug
            data = translations.get(slug)

            if data:
                name = data.get("name")
                description = data.get("description", "")

                if isinstance(description, dict):
                    description = (
                        description.get("general")
                        or description.get("5")
                        or description.get("4")
                        or description.get("3")
                        or description.get("2")
                        or next(iter(description.values()), "")
                    )

                item.name = name or item.name
                item.description = description or item.description
                item.save()
                updated += 1
                self.stdout.write(f"[✓] {slug} mis à jour")

        self.stdout.write(self.style.SUCCESS(f"{updated} items mis à jour avec succès"))
