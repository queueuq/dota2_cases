from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("case/<slug:slug>/", views.case_detail, name="case_detail"),
    path("items/", views.item_list, name="item_list"),
]
