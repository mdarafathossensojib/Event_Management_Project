from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Count
from users.forms import CustomRegistrationForm, LoginForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordConfirmForm, EditProfileForm
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView
from datetime import timedelta
from events.models import Event, Category, EventParticipant, SavedEvent, Notification, UserActivity
from django.contrib.auth import update_session_auth_hash


User = get_user_model()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True 
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url
    

def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = False 
            user.save()
            messages.success(request, 'A Confirmation email sent. Please Check Your Email....')
            return redirect('sign-in')
        else:
            print(form.errors)
            print("Form is not valid")

    return render(request, 'registration/signup.html', {'form' : form})

def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Thank you. You successfully activate your Account. Please Sign In.')
            return redirect('sign-in') 
        else:
            return HttpResponse("Invalid Id or Token")
        
    except User.DoesNotExist:
        return HttpResponse("User Not Found!")
    



# Helper function for time ago
def time_ago(dt):
    """Format time difference"""
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 7:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


@login_required
def dashboard(request):
    """Dashboard home page - Unified for User and Admin"""
    user = request.user
    
    # 1. ADMIN CHECK:
    if user.is_superuser or user.groups.filter(name__iexact='Admin').exists():
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()

        for u in users:
            u.group_name = u.all_groups[0].name if u.all_groups else "No Group Assign"

        # Admin extra stats
        total_events = Event.objects.count()
        total_participants = EventParticipant.objects.count()

        context = {
            "users": users,
            "total_users": users.count(),
            "total_events": total_events,
            "total_participants": total_participants,
        }
        return render(request, 'admin/admin_dashboard.html', context)

    # 2. REGULAR USER
    else:
        # Upcoming RSVPs
        upcoming_rsvps = EventParticipant.objects.filter(
            user=user,
            event__date__gte=timezone.now().date(),
            status='going'
        ).select_related('event').order_by('event__date')[:3]
        
        saved_count = SavedEvent.objects.filter(user=user).count()
        attended_count = EventParticipant.objects.filter(
            user=user, event__date__lt=timezone.now().date(), status='attended'
        ).count()
        upcoming_count = EventParticipant.objects.filter(
            user=user, event__date__gte=timezone.now().date(), status='going'
        ).count()
        
        week_ago = timezone.now() - timedelta(days=7)
        new_this_week = EventParticipant.objects.filter(user=user, joined_at__gte=week_ago).count()
        new_saved = SavedEvent.objects.filter(user=user, created_at__gte=week_ago).count()
        
        recent_activities = UserActivity.objects.filter(user=user).select_related('event')[:5]
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        
        formatted_activities = []
        for activity in recent_activities:
            formatted_activities.append({
                'action': activity.get_activity_type_display(),
                'event_title': activity.event.title,
                'time_ago': time_ago(activity.created_at),
            })
        
        context = {
            'upcoming_rsvps': upcoming_rsvps,
            'saved_count': saved_count,
            'attended_count': attended_count,
            'upcoming_count': upcoming_count,
            'new_this_week': new_this_week,
            'new_saved': new_saved,
            'recent_activities': formatted_activities,
            'unread_count': unread_count,
        }
        return render(request, 'dashboard.html', context)


@login_required
def dashboard_rsvps(request):
    """User's RSVPs page"""
    user = request.user
    
    # Get all RSVPs
    upcoming_rsvps = EventParticipant.objects.filter(
        user=user,
        event__date__gte=timezone.now().date()
    ).select_related('event').order_by('event__date')
    
    past_rsvps = EventParticipant.objects.filter(
        user=user,
        event__date__lt=timezone.now().date()
    ).select_related('event').order_by('-event__date')

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'upcoming_rsvps': upcoming_rsvps,
        'past_rsvps': past_rsvps,
        'unread_count': unread_count,
    }
    
    return render(request, 'rsvp.html', context)


@login_required
def dashboard_saved(request):
    """User's saved events page"""
    user = request.user
    
    saved_events = SavedEvent.objects.filter(
        user=user
    ).select_related('event').order_by('-created_at')
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    context = {
        'saved_events': saved_events,
        'unread_count': unread_count,
    }
    
    return render(request, 'rsvp_save.html', context)


@login_required
def dashboard_notifications(request):
    user = request.user
    
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    # mark all as read
    notifications.filter(is_read=False).update(is_read=True)
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'notification.html', context)


@login_required
def dashboard_settings(request):
    user = request.user

    form = EditProfileForm(instance=user)
    password_form = CustomPasswordChangeForm(user)

    if request.method == 'POST':

        # PROFILE UPDATE
        if 'update_profile' in request.POST:
            form = EditProfileForm(request.POST, request.FILES, instance=user)

            if form.is_valid():
                form.save()

                Notification.objects.create(
                    user=user,
                    notification_type='profile_update',
                    title='Profile Updated',
                    message='Your profile information has been updated successfully.'
                )

                messages.success(request, 'Profile updated successfully!')
                return redirect('dashboard_settings')

        # PASSWORD CHANGE
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                Notification.objects.create(
                    user=user,
                    notification_type='password_change',
                    title='Password Changed',
                    message='Your password has been changed successfully.'
                )

                messages.success(request, 'Password changed successfully!')
                return redirect('dashboard_settings')

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, 'accounts/settings.html', {
        'form': form,
        'password_form': password_form,
        'unread_count': unread_count
    })



# Event Action Views
@login_required
def rsvp_event(request, id):
    """Handle RSVP for an event"""
    event = get_object_or_404(Event, id=id)
    user = request.user
    
    # Check if user already RSVP'd
    existing_rsvp = EventParticipant.objects.filter(user=user, event=event).first()
    
    if existing_rsvp:
        # Cancel RSVP
        existing_rsvp.delete()

        # decrease count
        if event.registered and event.registered > 0:
            event.registered -= 1
            event.save()
        messages.success(request, f'You have cancelled your RSVP for {event.title}')
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            event=event,
            activity_type='cancel'
        )
    else:
        # Create new RSVP
        EventParticipant.objects.create(
            user=user,
            event=event,
            status='going'
        )
        
        # Update registered count
        event.registered = event.registered + 1 if event.registered else 1
        event.save()
        
        messages.success(request, f'You have successfully RSVP\'d for {event.title}')
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            event=event,
            activity_type='rsvp'
        )
        
        # Create notification
        Notification.objects.create(
            user=user,
            event=event,
            notification_type='rsvp_confirmation',
            title='RSVP Confirmed',
            message=f'Your RSVP for {event.title} has been confirmed.'
        )
    
    return redirect('event_detail', id=event.id)


@login_required
def save_event(request, id):
    """Handle saving an event"""
    event = get_object_or_404(Event, id=id)
    user = request.user
    
    saved, created = SavedEvent.objects.get_or_create(user=user, event=event)
    
    if created:
        messages.success(request, f'{event.title} has been saved to your list')
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            event=event,
            activity_type='save'
        )
    else:
        saved.delete()
        messages.info(request, f'{event.title} has been removed from your saved list')
    
    return redirect('event_detail', id=event.id)



@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['username'] = user.username
        context['email'] = user.email
        context['name'] = user.get_full_name()
        context['phone'] = user.phone
        context['profile_image'] = user.profile_image
        context['cover_image'] = user.cover_image
        context['bio'] = user.bio
        context['address'] = user.address
        context['member_since'] = user.date_joined
        context['last_login'] = user.last_login
        return context
    

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/reset_password.html'
    form_class = CustomPasswordResetForm
    html_email_template_name = 'registration/reset_email.html'
    success_url = reverse_lazy('password-reset') # Same page-e success message dekhate

    def form_valid(self, form):
        messages.success(self.request, 'A reset link has been sent to your email. Please check your inbox.')
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/reset_password_confirm.html'
    form_class = CustomPasswordConfirmForm
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(self.request, 'Password reset successful! You can now log in.')
        return super().form_valid(form)

    