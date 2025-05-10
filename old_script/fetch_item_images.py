import time
from pathlib import Path
from django.core.management.base import BaseCommand
from items.models import Item
from django.conf import settings
from playwright.sync_api import sync_playwright


class Command(BaseCommand):
    help = "Scrape et associe les images d'items depuis skullandbonestools.de"

    BASE_URL = "https://skullandbonestools.de/en/codex"
    CATEGORIES = {
        "Carpenter": [
            "Upgrade Tools",
            "Offensive Furniture",
            "Utility Furniture",
            "Major Furniture",
            "Repair Kits"
        ],
        "Blacksmith": [
            "All Deck Weapons",
            "Top Deck Weapons",
            "Bow Weapons",
            "Auxiliary Weapons",
            "Armor",
            "Ammunition"
        ],
        "Cookery": [
            "Cookery",
        ]
    }

    def handle(self, *args, **options):
        media_dir = Path(settings.MEDIA_ROOT) / "item_images"
        media_dir.mkdir(parents=True, exist_ok=True)

        total_downloaded = 0
        items_to_update = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
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
                        locator = page.locator(
                            f"a.ps-menu-button:not(.ps-open) >> span.ps-menu-label:has-text('{cat}')"
                        ).first
                        locator.hover()
                        locator.click()
                        page.wait_for_selector(".itemLinkContainer", timeout=10000)
                        time.sleep(1.5)
                    except Exception as e:
                        self.stderr.write(f"[!] Échec affichage catégorie {cat} : {e}")
                        continue

                    images = page.locator(".itemLinkContainer img").all()
                    if not images:
                        self.stderr.write("    [!] Aucune image trouvée.")
                        continue

                    for img in images:
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

                        items_to_update.append((alt, f"item_images/{filename}"))

            browser.close()

        for alt, image_path in items_to_update:
            item = Item.objects.filter(name__icontains=alt).first()
            if item and not item.image:
                item.image = image_path
                item.save()
                self.stdout.write(f"    [★] Image liée à {item.name}")

        self.stdout.write(self.style.SUCCESS(f"Scraping terminé : {total_downloaded} images téléchargées."))
