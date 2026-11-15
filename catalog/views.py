from django.shortcuts import render
from .models import Case

def home(request):
    return render(request, "catalog/home.html", {"cases": Case.objects.all()})