from django.urls import path
from users.views import sign_in, sign_up, sign_out, activate_user, assign_role, create_group, group_list, admin_dashboard, dashboard, my_account, my_rsvps, event_rsvp

urlpatterns = [
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-up/', sign_up, name='sign-up'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('logout/', sign_out, name='logout'),
    path('admin/<int:user_id>/assign-role/', assign_role, name="assign-role"),
    path('admin/create-group/', create_group, name="create-group"),
    path('admin/group-list/', group_list, name="group-list"),
    path('admin/dashboard/', admin_dashboard, name="admin-dashboard"),
    path('dashboard/', dashboard, name="dashboard"),
    path('account/', my_account, name="account"),
    path('my-rsvps/', my_rsvps, name='my-rsvps'),
    path('rsvp/<int:event_id>', event_rsvp, name='rsvp'),
]