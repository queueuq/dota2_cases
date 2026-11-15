from django.urls import path

from . import views

app_name = "cases"

urlpatterns = [
    path("inventory/", views.inventory, name="inventory"),
    path("history/", views.history, name="history"),
]
