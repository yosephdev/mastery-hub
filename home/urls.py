from django.urls import path
from . import views
from .views import home, contact_view, search

urlpatterns = [
    path("", views.index, name="home"),
    path("", home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", contact_view, name="contact"),
    path("search/", search, name="search"),
]
