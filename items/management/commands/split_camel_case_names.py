import re
from django.core.management.base import BaseCommand
from items.models import Item

def split_camel_case(name):
    words = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name).split()
    return ' '.join(word.capitalize() for word in words)

class Command(BaseCommand):
    help = "Convertit les noms en CamelCase comme 'vengefulEssence' → 'Vengeful Essence' pour les champs name_fr et name_en."

    def handle(self, *args, **options):
        updated = 0

        for item in Item.objects.all():
            modified = False

            for lang in ['fr', 'en']:
                field_name = f'name_{lang}'
                original_value = getattr(item, field_name, None)

                # fallback sur name si vide
                if not original_value:
                    original_value = item.name

                if original_value and ' ' not in original_value and re.search(r'[A-Z]', original_value):
                    new_value = split_camel_case(original_value)
                    if new_value != original_value:
                        self.stdout.write(f"[✓] {field_name} : {original_value} → {new_value}")
                        setattr(item, field_name, new_value)
                        modified = True

            if modified:
                item.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"{updated} noms modifiés."))
