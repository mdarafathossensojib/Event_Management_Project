from django.urls import path
from events.views import events, event_create, event_update, event_delete, details, category

urlpatterns = [
    path('', events, name='events'),
    path('details/<int:id>/', details, name='details'),
    path('event-create/', event_create, name='event-create'),
    path('event-update/<int:id>/', event_update, name='event-update'),
    path('event-delete/<int:id>/', event_delete, name='event-delete'),
    path('category/', category, name='category'),
]