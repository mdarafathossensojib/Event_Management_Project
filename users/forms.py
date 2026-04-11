from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
import re
from django.contrib.auth.models import Group, Permission
from django import forms
from users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
            'placeholder': 'Enter Your Password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
    
        widgets = {
                'username': forms.TextInput(attrs={
                    'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
                    'placeholder': 'Enter Your Username'
                }),
                'first_name': forms.TextInput(attrs={
                    'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
                    'placeholder': 'Enter Your First Name'
                }),
                'last_name': forms.TextInput(attrs={
                    'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
                    'placeholder': 'Enter Your Last Name'
                }),
                'email': forms.EmailInput(attrs={
                    'class': 'w-full h-12 px-4 mb-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
                    'placeholder': 'Enter Your Email Address'
                }),
            }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email=email).exists()

        if email_exists:
            raise forms.ValidationError("Email already exists")
        
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number.")

        if not re.search(r'[@#$%^&+=]', password):
            errors.append("Password must contain at least one special character (@, #, $, %, ^, &, +, =).")

        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password does not match"
            )
        
        return cleaned_data

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full h-12 px-4 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full h-12 px-4 pr-12 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:outline-none',
            'placeholder': 'Enter password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500',
            'placeholder': 'Enter current password'
        })
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500',
            'placeholder': 'Enter new password'
        })
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500',
            'placeholder': 'Re-enter new password'
        })
    )



class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all',
            'placeholder': 'Enter your registered email'
        })
    )

class CustomPasswordConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all',
            'placeholder': 'Re-enter new password'
        })
    )

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'profile_image',
            'cover_image',
            'first_name',
            'last_name',
            'email',
            'phone',
            'bio',
            'address',
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500',
                'rows': 4
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
        }

