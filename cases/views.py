import random

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from catalog.models import Case

from .models import UserItem

User = get_user_model()


@login_required
@require_POST
def open_case(request, slug):
    case = get_object_or_404(Case, slug=slug)
    entries = list(case.entries.select_related("item", "item__hero"))
    if not entries:
        return JsonResponse({"error": "В кейсе нет предметов"}, status=400)

    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=request.user.pk)
        if user.balance < case.price:
            return JsonResponse({"error": "Недостаточно средств. Пополните баланс."}, status=400)
        entry = random.choices(entries, weights=[e.weight for e in entries])[0]
        user.balance -= case.price
        user.save(update_fields=["balance"])
        UserItem.objects.create(user=user, item=entry.item, case=case)

    item = entry.item
    return JsonResponse(
        {
            "item": {
                "name": item.name,
                "hero": item.hero.name,
                "rarity": item.rarity,
                "rarity_label": item.get_rarity_display(),
                "image": item.image.url,
            },
            "balance": str(user.balance),
            "pool": [{"image": e.item.image.url, "rarity": e.item.rarity} for e in entries],
        }
    )


@login_required
def inventory(request):
    items = (
        request.user.inventory.filter(is_sold=False)
        .select_related("item", "item__hero", "case")
        .order_by("-obtained_at")
    )
    return render(request, "cases/inventory.html", {"user_items": items})


@login_required
def history(request):
    items = (
        request.user.inventory.select_related("item", "item__hero", "case")
        .order_by("-obtained_at")[:100]
    )
    return render(request, "cases/history.html", {"user_items": items})