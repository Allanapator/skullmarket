import re
import unicodedata
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from items.models import Item
from django.utils.text import slugify
from django.core.files import File

ROMAN_MAP = {
    "I": "1",
    "II": "2",
    "III": "3",
    "IV": "4",
    "V": "5",
}
ARABIC_MAP = {v: k for k, v in ROMAN_MAP.items()}


def clean_filename(name: str):
    name = name.replace("Image_of_", "").replace("_in_codex_search.", "")
    name = name.replace("_", " ").replace("-", " ").replace("’", "").replace("'", "")
    name = re.sub(r"\s+", " ", name).strip()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")

    # Convertit les chiffres romains → arabes
    for roman, arabic in ROMAN_MAP.items():
        name = re.sub(rf"\b{roman}\b", arabic, name, flags=re.IGNORECASE)

    return name


def to_roman_variant(name: str):
    # Convertit les chiffres arabes → romains
    for arabic, roman in ARABIC_MAP.items():
        name = re.sub(rf"\b{arabic}\b", roman, name, flags=re.IGNORECASE)
    return name


class Command(BaseCommand):
    help = "Associe les images aux items en nettoyant les noms de fichiers"

    def handle(self, *args, **options):
        image_dir = Path(settings.MEDIA_ROOT) / "item_images"
        if not image_dir.exists():
            self.stderr.write("[!] Dossier 'item_images' introuvable.")
            return

        count = 0

        for file in image_dir.glob("*.png"):
            base_name = file.stem
            item_name = clean_filename(base_name)
            item_name_roman = to_roman_variant(item_name)

            slug_guess = slugify(item_name)
            slug_guess_roman = slugify(item_name_roman)
            slug_guess_flat = slug_guess.replace("-", "")
            slug_guess_roman_flat = slug_guess_roman.replace("-", "")

            item = (
                Item.objects.filter(slug=slug_guess).first()
                or Item.objects.filter(slug=slug_guess_roman).first()
                or Item.objects.filter(slug=slug_guess_flat).first()
                or Item.objects.filter(slug=slug_guess_roman_flat).first()
                or Item.objects.filter(name__iexact=item_name).first()
                or Item.objects.filter(name__iexact=item_name_roman).first()
                or Item.objects.filter(name__icontains=item_name).first()
                or Item.objects.filter(name__icontains=item_name_roman).first()
            )

            if item:
                with open(file, 'rb') as f:
                    item.image.save(file.name, File(f), save=True)
                item.save()
                self.stdout.write(f"[✓] Image liée à {item.name}")
                count += 1
            else:
                self.stderr.write(f"[✗] Aucun item trouvé pour : {file.name} -> {item_name}")

        self.stdout.write(self.style.SUCCESS(f"{count} images associées avec succès."))
