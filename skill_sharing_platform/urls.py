"""
URL configuration for skill_sharing_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from accounts.views import CustomGoogleCallbackView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Our custom accounts URLs should come before allauth URLs to override them
    path("accounts/", include("accounts.urls")),
    # Custom Google callback
    re_path(r'^accounts/google/login/callback/$', 
            CustomGoogleCallbackView.as_view(), 
            name='google_callback'),
    # Default allauth URLs
    path("accounts/", include("allauth.urls")),
    path('checkout/', include('checkout.urls', namespace='checkout')),
    path('profiles/', include('profiles.urls', namespace='profiles')),
    path('masteryhub/', include('masteryhub.urls', namespace='masteryhub')),
    path('', include(('home.urls', 'home'), namespace='home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = "skill_sharing_platform.views.handler404"
