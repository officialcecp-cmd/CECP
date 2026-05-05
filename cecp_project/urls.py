# ==============================================================================
# CECP Project — Root URL Configuration
# ==============================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from landing.views import ping

urlpatterns = [
    path('admin/', admin.site.urls),
    # Allauth URLs for Social Login
    path('accounts/', include('allauth.urls')),
    path('api/ping/', ping, name='ping'),
    # Landing page handles the root URL and all public-facing pages
    path('', include('landing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
