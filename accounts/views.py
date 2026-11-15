from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    payments = request.user.payments.all().order_by("-created_at")
    return render(request, "accounts/profile.html", {"payments": payments})