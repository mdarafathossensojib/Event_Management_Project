from django.urls import path
from events.views import events_page as events, event_detail, how_it_works, categories_list, contact, category_detail, AdminEventListView, AdminCategoryListView, AdminRolePermissionView, delete_category, delete_event

urlpatterns = [
    path('', events, name='events'),
    path('details/<int:id>/', event_detail, name='event_detail'),
    path('how-it-works/', how_it_works, name='how-it-works'),
    path('categories/', categories_list, name='categories'),
    path('category/<int:category_id>/', category_detail, name='category_detail'),
    path('contact/', contact, name='contact'),
    path('admin-dashboard/events/', AdminEventListView.as_view(), name='admin-events'),
    path('event-delete/<int:id>/', delete_event, name='event-delete'),
    path('admin-dashboard/categories/', AdminCategoryListView.as_view(), name='admin-categories'),
    path('category-delete/<int:id>/', delete_category, name='category-delete'),
    path('manage-users/', AdminRolePermissionView.as_view(), name='admin-users'),
]