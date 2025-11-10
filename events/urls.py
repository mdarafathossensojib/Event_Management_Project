from django.urls import path
from events.views import dashboard, event_create, event_update, event_delete, details, participants, category

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('details/<int:id>/', details, name='details'),
    path('event-create/', event_create, name='event-create'),
    path('event-update/<int:id>/', event_update, name='event-update'),
    path('event-delete/<int:id>/', event_delete, name='event-delete'),
    path('participants/', participants, name='participants'),
    path('category/', category, name='category'),
]