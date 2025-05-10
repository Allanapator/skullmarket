from django.core.management.base import BaseCommand
from items.models import Item

ROMAN_SUFFIXES = {
    "1": " I",
    "2": " II",
    "3": " III",
    "4": " IV",
    "5": " V",
    "6": " VI",
    "7": " VII",
    "8": " VIII",
    "9": " IX",
    "10": " X",
}

class Command(BaseCommand):
    help = "Remplace les suffixes numériques 1/2/3 par les équivalents romains avec un espace"

    def handle(self, *args, **options):
        updated = 0

        for item in Item.objects.all():
            for digit, roman in ROMAN_SUFFIXES.items():
                if item.name.endswith(digit):
                    base_name = item.name[:-len(digit)].rstrip()
                    new_name = f"{base_name}{roman}"

                    if new_name != item.name:
                        item.name = new_name
                        item.save()
                        self.stdout.write(f"[✓] {item.slug} → {new_name}")
                        updated += 1
                    break

        self.stdout.write(self.style.SUCCESS(f"{updated} items renommés en chiffres romains"))
