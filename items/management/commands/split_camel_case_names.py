import re
from django.core.management.base import BaseCommand
from items.models import Item


def split_camel_case(name):
    words = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name).split()
    return ' '.join(word.capitalize() for word in words)


class Command(BaseCommand):
    help = "Convertit les noms en CamelCase comme 'vengefulEssence' → 'Vengeful Essence'"

    def handle(self, *args, **options):
        updated = 0

        for item in Item.objects.all():
            if not item.name:
                continue

            if ' ' not in item.name and re.search(r'[A-Z]', item.name):
                new_name = split_camel_case(item.name)
                if new_name != item.name:
                    self.stdout.write(f"[✓] {item.name} → {new_name}")
                    item.name = new_name
                    item.save()
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"{updated} noms modifiés."))
