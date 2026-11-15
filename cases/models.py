from django.conf import settings
from django.db import models

from catalog.models import Case, Item


class UserItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True)
    obtained_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return "%s: %s" % (self.user, self.item)
