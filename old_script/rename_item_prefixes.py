from pathlib import Path
from django.core.management.base import BaseCommand
from items.models import Item
import json

class Command(BaseCommand):
    help = "Met à jour les noms des items en capitalisant leur préfixe depuis en_items.json"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'skullandbones'
        items_path = base_dir / 'en_items.json'

        if not items_path.exists():
            self.stderr.write(f"[!] Fichier non trouvé : {items_path}")
            return

        with open(items_path, encoding='utf-8') as f:
            en_items = json.load(f).get("items", {})

        updated = 0

        for item in Item.objects.all():
            item_slug_lower = item.slug.lower()

            for prefix in en_items.keys():
                prefix_lower = prefix.lower()

                if item_slug_lower.startswith(prefix_lower):
                    suffix = item.slug[len(prefix_lower):]  # On coupe sur la longueur du préfixe en minuscule
                    capitalized = en_items[prefix].get("name", prefix)
                    new_name = f"{capitalized}{suffix}"

                    item.name = new_name
                    item.save()
                    updated += 1
                    self.stdout.write(f"[✓] {item.slug} → {new_name}")
                    break

        self.stdout.write(self.style.SUCCESS(f"{updated} noms d’items mis à jour"))
