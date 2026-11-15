from django.conf import settings
from django.db import models


class Payment(models.Model):
    STATUSES = [
        ("pending", "Ожидает оплаты"),
        ("succeeded", "Оплачен"),
        ("canceled", "Отменён"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    external_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Платёж #%s (%s)" % (self.pk, self.get_status_display())
