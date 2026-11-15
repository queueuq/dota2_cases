from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("topup/", views.topup, name="topup"),
    path("fake/<int:pk>/", views.fake_pay, name="fake_pay"),
    path("result/<int:pk>/", views.result, name="result"),
]
