from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import home, subscribe
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('no-permission/', home, name='no-permission'),
    path("subscribe/", subscribe, name="subscribe"),
    path('event/', include('events.urls')),
    path('user/', include('users.urls')),
] + debug_toolbar_urls()

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
