from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import home, no_permission

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('no-permission/', no_permission, name='no-permission'),
    path('event/', include('events.urls')),
    path('user/', include('users.urls')),
] + debug_toolbar_urls()
