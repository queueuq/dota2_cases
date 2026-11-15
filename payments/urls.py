from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("topup/", views.topup, name="topup"),
]
