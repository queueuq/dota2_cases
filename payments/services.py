import uuid

from django.conf import settings
from django.db import transaction

from .models import Payment


def _configure_yookassa():
    from yookassa import Configuration

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def start_payment(payment, return_url):
    # Возвращает ссылку на оплату (yookassa) или None (fake-режим)
    if settings.PAYMENT_BACKEND != "yookassa":
        return None
    from yookassa import Payment as YooPayment

    _configure_yookassa()
    yoo = YooPayment.create(
        {
            "amount": {"value": "%.2f" % payment.amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": "Пополнение баланса, платёж #%s" % payment.pk,
        },
        str(uuid.uuid4()),
    )
    payment.external_id = yoo.id
    payment.save(update_fields=["external_id"])
    return yoo.confirmation.confirmation_url


@transaction.atomic
def mark_succeeded(payment):
    payment = Payment.objects.select_for_update().select_related("user").get(pk=payment.pk)
    if payment.status != "pending":
        return payment  # защита от двойного зачисления
    payment.status = "succeeded"
    payment.save(update_fields=["status"])
    user = type(payment.user).objects.select_for_update().get(pk=payment.user_id)
    user.balance += payment.amount
    user.save(update_fields=["balance"])
    return payment


@transaction.atomic
def mark_canceled(payment):
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status == "pending":
        payment.status = "canceled"
        payment.save(update_fields=["status"])
    return payment


def refresh_status(payment):
    # Вебхуки не работают без публичного адреса, поэтому статус спрашиваем сами
    if settings.PAYMENT_BACKEND != "yookassa" or payment.status != "pending" or not payment.external_id:
        return payment
    from yookassa import Payment as YooPayment

    _configure_yookassa()
    yoo = YooPayment.find_one(payment.external_id)
    if yoo.status == "succeeded":
        return mark_succeeded(payment)
    if yoo.status == "canceled":
        return mark_canceled(payment)
    return payment
