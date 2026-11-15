from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from . import services
from .forms import TopUpForm
from .models import Payment


@login_required
def topup(request):
    form = TopUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        payment = Payment.objects.create(user=request.user, amount=form.cleaned_data["amount"])
        return_url = request.build_absolute_uri(reverse("payments:result", args=[payment.pk]))
        url = services.start_payment(payment, return_url)
        if url:
            return redirect(url)
        return redirect("payments:fake_pay", pk=payment.pk)
    return render(request, "payments/topup.html", {"form": form})


@login_required
def fake_pay(request, pk):
    if settings.PAYMENT_BACKEND != "fake":
        raise Http404
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    if payment.status != "pending":
        return redirect("payments:result", pk=payment.pk)
    if request.method == "POST":
        if "pay" in request.POST:
            services.mark_succeeded(payment)
        else:
            services.mark_canceled(payment)
        return redirect("payments:result", pk=payment.pk)
    return render(request, "payments/fake_pay.html", {"payment": payment})


@login_required
def result(request, pk):
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    payment = services.refresh_status(payment)
    return render(request, "payments/result.html", {"payment": payment})
