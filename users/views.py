from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
# Create your views here.

def sign_in(request):

    return render(request, 'registration/sign_in.html')

def sign_up(request):

    return render(request, 'registration/sign_up.html')

def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')