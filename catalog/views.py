from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Case, Hero, Item

def home(request):
    return render(request, "catalog/home.html", {"cases": Case.objects.all()})

def case_detail(request, slug):
    case = get_object_or_404(Case, slug=slug)
    entries = list(case.entries.select_related("item", "item__hero").order_by("-item__price"))
    total = sum(e.weight for e in entries) or 1
    for e in entries:
        e.chance = round(e.weight / total * 100, 2)
    return render(request, "catalog/case_detail.html", {"case": case, "entries": entries})

def item_list(request):
    items = Item.objects.select_related("hero").order_by("-price")
    hero = request.GET.get("hero", "")
    rarity = request.GET.get("rarity", "")
    q = request.GET.get("q", "").strip()
    if hero:
        items = items.filter(hero_id=hero)
    if rarity:
        items = items.filter(rarity=rarity)
    if q:
        items = items.filter(Q(name__icontains=q) | Q(hero__name__icontains=q))
    context = {
        "items": items,
        "heroes": Hero.objects.all(),
        "rarities": Item.RARITIES,
        "sel_hero": hero,
        "sel_rarity": rarity,
        "q": q,
    }
    return render(request, "catalog/item_list.html", context)