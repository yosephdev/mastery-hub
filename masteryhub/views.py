from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def home(request):
    """
    A view to return the home page for the masteryhub app
    """
    return HttpResponse("Welcome to MasteryHub!")
