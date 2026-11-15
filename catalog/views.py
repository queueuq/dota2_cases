from django.shortcuts import get_object_or_404, render
from .models import Case

def home(request):
    return render(request, "catalog/home.html", {"cases": Case.objects.all()})

def case_detail(request, slug):
    case = get_object_or_404(Case, slug=slug)
    entries = list(case.entries.select_related("item", "item__hero").order_by("-item__price"))
    total = sum(e.weight for e in entries) or 1
    for e in entries:
        e.chance = round(e.weight / total * 100, 2)
    return render(request, "catalog/case_detail.html", {"case": case, "entries": entries})