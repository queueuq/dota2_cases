from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Case, CaseItem, Hero, Item

# (герой, название, слот, редкость, цена продажи)
ITEMS = [
    ("Pudge", "Dragonclaw Hook", "weapon", "immortal", 500),
    ("Pudge", "Hook of Delicacies of Butchery", "weapon", "common", 5),
    ("Pudge", "Bloodstained Britches", "misc", "rare", 20),
    ("Kunkka", "Red Mist Reaper's Axe", "weapon", "legendary", 150),
    ("Kunkka", "Carronade Corsair - Head", "head", "rare", 25),
    ("Kunkka", "Ye Olde Pipe", "misc", "common", 8),
    ("Juggernaut", "Bladeform Legacy", "weapon", "arcana", 900),
    ("Juggernaut", "Sigil Mask of the Bladekeeper", "head", "mythical", 60),
    ("Juggernaut", "Seven-Sealed the Fur Bracer", "misc", "common", 6),
    ("Phantom Assassin", "Manifold Paradox", "weapon", "arcana", 1000),
    ("Phantom Assassin", "Gleaming Seal", "head", "legendary", 120),
    ("Phantom Assassin", "Valkyrie's Shade Head", "misc", "rare", 18),
    ("Crystal Maiden", "Frost Avalanche", "misc", "arcana", 800),
    ("Crystal Maiden", "Sceptre of Icewrack", "head", "mythical", 55),
    ("Crystal Maiden", "Tails of the Tundra Warden", "shoulders", "common", 7),
    ("Sven", "Vigil Odyssey", "weapon", "immortal", 450),
    ("Sven", "Commander's Pauldron of the Flameguard", "head", "rare", 22),
    ("Sven", "Meranth Dragoon Finblade", "shoulders", "mythical", 50),
]

# Вес выпадения по редкости (чем больше, тем чаще)
WEIGHTS = {"common": 60, "rare": 30, "mythical": 15, "legendary": 6, "immortal": 2, "arcana": 1}

# (название, slug, цена, описание, какие редкости входят)
CASES = [
    ("Starter Case", "starter", 50, "Для новичков: много обычных предметов и шанс на редкие.",
     {"common", "rare", "mythical"}),
    ("Legends Case", "legends", 150, "Редкие, мифические и легендарные предметы.",
     {"rare", "mythical", "legendary", "immortal"}),
    ("Arcana Case", "arcana", 500, "Только лучшее: шанс выбить Arcana.",
     {"mythical", "legendary", "immortal", "arcana"}),
]


def find_image(folder, slug):
    # Ищем картинку в media/<folder>/ с любым расширением (jpg/webp приоритетнее заглушки .png)
    for ext in ("jpg", "jpeg", "webp", "png"):
        if (Path(settings.MEDIA_ROOT) / folder / ("%s.%s" % (slug, ext))).exists():
            return "%s/%s.%s" % (folder, slug, ext)
    return "%s/%s.png" % (folder, slug)


class Command(BaseCommand):
    help = "Загружает демо-героев, предметы и кейсы (картинки берутся из media/)"

    def handle(self, *args, **options):
        created_items = {}
        for hero_name, name, slot, rarity, price in ITEMS:
            hero, _ = Hero.objects.get_or_create(name=hero_name)
            item, _ = Item.objects.update_or_create(
                name=name,
                hero=hero,
                defaults={
                    "slot": slot,
                    "rarity": rarity,
                    "price": price,
                    "image": find_image("items", slugify(name)),
                },
            )
            created_items[name] = item

        for name, slug, price, desc, rarities in CASES:
            case, _ = Case.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "price": price,
                    "description": desc,
                    "image": find_image("cases", slug),
                },
            )
            for item in created_items.values():
                if item.rarity in rarities:
                    CaseItem.objects.update_or_create(
                        case=case, item=item, defaults={"weight": WEIGHTS[item.rarity]}
                    )
        self.stdout.write(self.style.SUCCESS("Демо-данные загружены"))
