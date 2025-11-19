from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from users.forms import CustomRegistrationForm, LoginForm, AssignRoleForm, CreateGroupForm

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

def sign_out(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Successfully Logout')
        return redirect('sign-in')
    
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


def create_group(request):
    form = CreateGroupForm()

    if request.method == 'POST':
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created Successfully!")
            return redirect('create-group')
    
    return render(request, 'admin/create_group.html', {"form" : form})

def group_list(request):
    groups = Group.objects.prefetch_related('permissions').all()

    return render(request, 'admin/group_list.html', {'groups' : groups})

def my_account(request, user_id):

    return render(request, 'admin/user_list.html')

def dashboard(request, user_id):

    return render(request, 'dashboard.html')