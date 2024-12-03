from django.urls import path
from . import views
from .views import index, about, contact_view, search

app_name = 'home'

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", contact_view, name="contact"),
    path('search/', search, name='search'),
    path('search/', search, name='search_results'),
]
