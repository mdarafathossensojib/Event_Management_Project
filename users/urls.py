from django.urls import path
from users.views import sign_up, activate_user, dashboard, event_rsvp, ProfileView, EditProfileView, CustomLoginView, CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView, GroupCreateView, GroupListView, AssignRoleView, ParticipantListView, AdminDashboardView, MyRSVPSView
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
    path('events/', dashboard, name="dashboard"),
    path('rsvp/<int:event_id>', event_rsvp, name='rsvp'),
    path('my-rsvps/', MyRSVPSView.as_view(), name='my-rsvps'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('participants/', ParticipantListView.as_view(), name='participants'),
    path('password-change/', CustomPasswordChangeView.as_view(), name="password_change"),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name="password_change_done"),
    path('password-reset/', CustomPasswordResetView.as_view(), name="password-reset"),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]