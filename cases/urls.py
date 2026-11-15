from django.urls import path
from . import views

app_name = "cases"

urlpatterns = [
    path("open/<slug:slug>/", views.open_case, name="open_case"),
    path("inventory/", views.inventory, name="inventory"),
    path("sell/<int:pk>/", views.sell_item, name="sell_item"),
    path("history/", views.history, name="history"),
]