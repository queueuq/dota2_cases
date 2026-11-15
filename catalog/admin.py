from django.contrib import admin

from .models import Case, CaseItem, Hero, Item


class CaseItemInline(admin.TabularInline):
    model = CaseItem
    extra = 1


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CaseItemInline]


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "hero", "slot", "rarity", "price")
    list_filter = ("rarity", "slot", "hero")
    search_fields = ("name",)


admin.site.register(Hero)
