from django.db import models


class Hero(models.Model):
    name = models.CharField("Герой", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Item(models.Model):
    RARITIES = [
        ("common", "Common"),
        ("rare", "Rare"),
        ("mythical", "Mythical"),
        ("legendary", "Legendary"),
        ("immortal", "Immortal"),
        ("arcana", "Arcana"),
    ]
    SLOTS = [
        ("weapon", "Оружие"),
        ("head", "Голова"),
        ("shoulders", "Плечи"),
        ("back", "Спина"),
        ("misc", "Прочее"),
    ]
    name = models.CharField("Название", max_length=150)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE, related_name="items")
    slot = models.CharField("Слот", max_length=20, choices=SLOTS)
    rarity = models.CharField("Редкость", max_length=20, choices=RARITIES)
    price = models.DecimalField("Цена продажи", max_digits=8, decimal_places=2)
    image = models.ImageField("Картинка", upload_to="items/")

    def __str__(self):
        return self.name


class Case(models.Model):
    name = models.CharField("Название", max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    image = models.ImageField("Картинка", upload_to="cases/")
    items = models.ManyToManyField(Item, through="CaseItem", related_name="cases")

    def __str__(self):
        return self.name


class CaseItem(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="entries")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField("Вес (шанс)", default=1)

    def __str__(self):
        return "%s -> %s (%s)" % (self.case, self.item, self.weight)
