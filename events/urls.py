from django.urls import path
from events.views import events, DetailsView, EventCreateView, EventUpdateView, EventDeleteView, CategoryCreateView

urlpatterns = [
    path('', events, name='events'),
    path('details/<int:id>/', DetailsView.as_view(), name='details'),
    path('event-create/', EventCreateView.as_view(), name='event-create'),
    path('event-update/<int:id>/', EventUpdateView.as_view(), name='event-update'),
    path('event-delete/<int:id>/', EventDeleteView.as_view(), name='event-delete'),
    # path('category/', category, name='category'),
    path('category/', CategoryCreateView.as_view(), name='category'),
]