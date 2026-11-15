
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
