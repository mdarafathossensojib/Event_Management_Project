from django.urls import path
from users.views import sign_up, activate_user, ProfileView, EditProfileView, CustomLoginView, CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView, GroupCreateView, GroupListView, AssignRoleView, ParticipantListView, AdminDashboardView, dashboard, save_event, rsvp_event, dashboard_settings, dashboard_saved, dashboard_rsvps, dashboard_notifications
from django.contrib.auth.views import LogoutView, PasswordChangeDoneView

urlpatterns = [
    path('sign-in/', CustomLoginView.as_view(), name='sign-in'),
    path('sign-up/', sign_up, name='sign-up'),
    path('activate/<int:user_id>/<str:token>/', activate_user),
    path('logout/', LogoutView.as_view(next_page='sign-in'), name='logout'),
    path('admin/<int:user_id>/assign-role/', AssignRoleView.as_view(), name="assign-role"),
    path('admin/create-group/', GroupCreateView.as_view(), name="create-group"),
    path('admin/group-list/', GroupListView.as_view(), name="group-list"),
    path('admin/dashboard/', AdminDashboardView.as_view(), name="admin-dashboard"),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('participants/', ParticipantListView.as_view(), name='participants'),
    path('password-change/', CustomPasswordChangeView.as_view(), name="password_change"),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name="password_change_done"),
    path('password-reset/', CustomPasswordResetView.as_view(), name="password-reset"),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),


    # Event Actions
    path('events/<int:id>/rsvp/', rsvp_event, name='rsvp_event'),
    path('events/<int:id>/save/', save_event, name='save_event'),
    
    # Dashboard Views
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/rsvps/', dashboard_rsvps, name='dashboard_rsvps'),
    path('dashboard/saved/', dashboard_saved, name='dashboard_saved'),
    path('dashboard/notifications/', dashboard_notifications, name='dashboard_notifications'),
    path('dashboard/settings/', dashboard_settings, name='dashboard_settings'),
]