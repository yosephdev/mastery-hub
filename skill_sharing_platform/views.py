from django.shortcuts import render
from django.http import HttpResponse


def handler404(request, exception):
    """Error Handler 404 - Page Not Found"""
    return render(request, "errors/404.html", status=404)


def test_view(request):
    return HttpResponse("Hello, World!")
