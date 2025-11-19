from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.db.models import Prefetch, Count
from users.forms import CustomRegistrationForm, LoginForm, AssignRoleForm, CreateGroupForm
from events.models import Event
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home') 

    return render(request, 'registration/sign_in.html', {'form' : form})

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

    return render(request, 'registration/sign_up.html', {'form' : form})

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

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Successfully Logout')
        return redirect('sign-in')
    
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = "No Group Assign"

    return render(request, 'admin/admin_dashboard.html', {"users" : users})


@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()
    if request.method == 'POST':
        form = AssignRoleForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get('role')
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"User {user.username} is has been assigned to the {role.name} role")
            return redirect('admin-dashboard')
    return render(request, 'admin/assign_role.html', {"form": form})


@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    form = CreateGroupForm()

    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created Successfully!")
            return redirect('create-group')
    
    return render(request, 'admin/create_group.html', {"form" : form})


@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()

    return render(request, 'admin/group_list.html', {'groups' : groups})


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


@login_required
def my_rsvps(request):
    events = request.user.event_users.all()
    return render(request, "rsvp.html", {"events": events})

@login_required
def account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.groups:
        user.group_name = user.groups.first().name
    else:
        user.group_name = "No Group Assign"

    return render(request, "account.html", {"user": user})

def participants(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = "No Group Assign"

    return render(request, 'admin/user_list.html', {"users" : users})