from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.db.models import Prefetch, Count
from users.forms import CustomRegistrationForm, LoginForm, AssignRoleForm, CreateGroupForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomPasswordConfirmForm, EditProfileForm
from events.models import Event
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import TemplateView, UpdateView, CreateView, FormView

User = get_user_model()

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True 
    success_url = reverse_lazy('home')

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else self.success_url
    
@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/change_password.html'
    form_class = CustomPasswordChangeForm

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
    

@method_decorator([login_required, user_passes_test(is_admin, login_url='no-permission')], name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = "No Group Assign"
        context["users"] = users
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class AssignRoleView(FormView):
    template_name = 'admin/assign_role.html'
    form_class = AssignRoleForm
    success_url = reverse_lazy('admin-dashboard')

    def form_valid(self, form):
        user_id = self.kwargs.get('pk')
        user = User.objects.get(pk=user_id)

        role = form.cleaned_data.get('role')
        user.groups.clear()
        user.groups.add(role)
        messages.success(self.request, f"User {user.username} has been assigned to the {role.name} Role.")
        return super().form_valid(form)
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin, login_url='no-permission'), name='dispatch')
class GroupCreateView(CreateView):
    model = Group
    form_class = CreateGroupForm
    template_name = 'admin/create_group.html'
    success_url = reverse_lazy('group-list')


@method_decorator(login_required, name='dispatch')
class GroupListView(TemplateView):
    template_name = 'admin/group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.prefetch_related('permissions').all()
        return context


def dashboard(request):
    today = timezone.now().date()

    # Base Query
    base_query = Event.objects.select_related('category').prefetch_related('user')

    # Start with base queryset
    events = base_query

    # ---------- TYPE FILTER ----------
    filter_type = request.GET.get('type', 'all')

    if filter_type == "upcoming":
        events = events.filter(date__gt=today)
    elif filter_type == "recent":
        events = events.filter(date__lt=today)
    elif filter_type == "today":
        events = events.filter(date=today)

    # ---------- SEARCH ----------
    name_query = request.GET.get('name', '')
    cat_query = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Search By Name
    if name_query:
        events = events.filter(name__icontains=name_query)

    # Search By Category
    if cat_query:
        events = events.filter(category__name__icontains=cat_query)

    # Search By Date Range
    if date_from and date_to:
        events = events.filter(date__range=[date_from, date_to])
    elif date_from:
        events = events.filter(date__gte=date_from)
    elif date_to:
        events = events.filter(date__lte=date_to)


    events = events.annotate(participant_count=Count('user'))

    # For sidebar upcoming events
    up_events = base_query.filter(date__gt=today).annotate(
        participant_count=Count('user')
    )

    context = {
        'events': events,
        'up_events': up_events,
        'name_query': name_query,
        'cat_query': cat_query,
        'date_from': date_from,
        'date_to': date_to,
        'filter_type': filter_type,
    }

    return render(request, 'dashboard.html', context)

@login_required
def event_rsvp(request, event_id):
    event = Event.objects.get(id=event_id)

    if request.user in event.user.all():
        messages.info(request, "You already RSVPed for this event.")
        return redirect('details', event.id)

    event.user.add(request.user) 

    send_mail(
        subject=f"RSVP Confirmation for {event.name}",
        message=f"Hi {request.user.username}, thanks for RSVPing!",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email],
        fail_silently=False
    )

    messages.success(request, "Your RSVP has been recorded!")
    return redirect('details', event.id)

@method_decorator(login_required, name='dispatch')
class MyRSVPSView(TemplateView):
    template_name = 'rsvp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.request.user.event_users.all()
        return context

@method_decorator(login_required, name='dispatch')
class ParticipantListView(TemplateView):
    template_name = 'admin/user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.prefetch_related(
            Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
        ).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = "No Group Assign"

        context['users'] = users
        return context


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

@method_decorator(login_required, name='dispatch')
class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'accounts/update_profile.html'
    context_object_name = 'form'

    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        form.save()
        return redirect('profile')
    

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/reset_password.html'
    form_class = CustomPasswordResetForm
    html_email_template_name = 'registration/reset_email.html'
    success_url = reverse_lazy('sign-in')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = 'https' if self.request.is_secure() else 'http'
        context['domain'] = self.request.get_host()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'A Reset Email has been sent. Please Check Your Email....')
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/reset_password_confirm.html'
    form_class = CustomPasswordConfirmForm
    success_url = reverse_lazy('sign-in')

    def form_valid(self, form):
        messages.success(self.request, 'Your Password has been reset successfully. Please Sign In.')
        return super().form_valid(form)
        

    