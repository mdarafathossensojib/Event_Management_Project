from django.urls import path
from events.views import events_page as events, event_detail

urlpatterns = [
    path('', events, name='events'),
    path('details/<int:id>/', event_detail, name='event_detail'),
    # path('event-create/', EventCreateView.as_view(), name='event-create'),
    # path('event-update/<int:id>/', EventUpdateView.as_view(), name='event-update'),
    # path('event-delete/<int:id>/', EventDeleteView.as_view(), name='event-delete'),
    # # path('category/', category, name='category'),
    # path('category/', CategoryCreateView.as_view(), name='category'),
]