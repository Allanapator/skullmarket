# items/management/commands/fetch_and_associate_images.py

import re
import time
import unicodedata
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.utils.text import slugify
from items.models import Item
from playwright.sync_api import sync_playwright

ROMAN_MAP = {"I": "1", "II": "2", "III": "3", "IV": "4", "V": "5"}
ARABIC_MAP = {v: k for k, v in ROMAN_MAP.items()}

def clean_filename(name: str):
    name = name.replace("Image_of_", "").replace("_in_codex_search.", "")
    name = name.replace("_", " ").replace("-", " ").replace("’", "").replace("'", "")
    name = re.sub(r"\s+", " ", name).strip()
    name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("utf-8")
    for roman, arabic in ROMAN_MAP.items():
        name = re.sub(rf"\b{roman}\b", arabic, name, flags=re.IGNORECASE)
    return name

def to_roman_variant(name: str):
    for arabic, roman in ARABIC_MAP.items():
        name = re.sub(rf"\b{arabic}\b", roman, name, flags=re.IGNORECASE)
    return name

class Command(BaseCommand):
    help = "Scrape et associe les images aux items depuis skullandbonestools.de"

    BASE_URL = "https://skullandbonestools.de/en/codex"
    CATEGORIES = {
        "Carpenter": ["Upgrade Tools", "Offensive Furniture", "Utility Furniture", "Major Furniture", "Repair Kits"],
        "Blacksmith": ["All Deck Weapons", "Top Deck Weapons", "Bow Weapons", "Auxiliary Weapons", "Armor", "Ammunition"],
        "Cookery": ["Cookery"],
    }

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / "item_images"
        media_dir.mkdir(parents=True, exist_ok=True)

        total_downloaded = 0
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.BASE_URL)
            page.wait_for_load_state('networkidle')

            for tab, subcats in self.CATEGORIES.items():
                self.stdout.write(f"[•] Onglet: {tab}")
                try:
                    page.locator(f"span.ps-menu-label:has-text('{tab}')").first.click(timeout=3000)
                    time.sleep(1.5)
                except Exception as e:
                    self.stderr.write(f"[!] Échec clic onglet {tab} : {e}")
                    continue

                for cat in subcats:
                    self.stdout.write(f"  └─> Catégorie: {cat}")
                    try:
                        locator = page.locator(f"a.ps-menu-button:not(.ps-open) span.ps-menu-label:has-text('{cat}')").first
                        locator.hover()
                        locator.click()
                        page.wait_for_selector(".itemLinkContainer", timeout=10000)
                        time.sleep(1.5)
                    except Exception as e:
                        self.stderr.write(f"[!] Échec affichage catégorie {cat} : {e}")
                        continue

                    for img in page.locator(".itemLinkContainer img").all():
                        src = img.get_attribute("src")
                        alt = img.get_attribute("alt") or "unknown"

                        if not src or not alt:
                            continue

                        if src.startswith("/"):
                            src = f"https://skullandbonestools.de{src}"

                        filename = alt.replace("/", "-").replace(" ", "_") + ".png"
                        save_path = media_dir / filename

                        if not save_path.exists():
                            try:
                                response = page.request.get(src)
                                with open(save_path, "wb") as f:
                                    f.write(response.body())
                                total_downloaded += 1
                                self.stdout.write(f"    [✓] {filename} téléchargé")
                            except Exception as e:
                                self.stderr.write(f"[!] Échec téléchargement {src} : {e}")

        # Association locale
        count = 0
        for file in media_dir.glob("*.png"):
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
                self.stdout.write(f"[✓] Image liée à {item.name}")
                count += 1
            else:
                self.stderr.write(f"[✗] Aucun item trouvé pour : {file.name} → {item_name}")

        self.stdout.write(self.style.SUCCESS(f"Scraping terminé : {total_downloaded} images téléchargées, {count} liées."))
