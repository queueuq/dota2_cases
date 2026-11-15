from django.contrib import admin

from .models import UserItem


@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "case", "obtained_at", "is_sold")
    list_filter = ("is_sold",)
