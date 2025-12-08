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
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
    
        widgets = {
                'username': forms.TextInput(attrs={
                    'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
                    'placeholder': 'Username'
                }),
                'first_name': forms.TextInput(attrs={
                    'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
                    'placeholder': 'First Name'
                }),
                'last_name': forms.TextInput(attrs={
                    'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
                    'placeholder': 'Last Name'
                }),
                'email': forms.EmailInput(attrs={
                    'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
                    'placeholder': 'Email Address'
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
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset = Group.objects.all(),
        empty_label = "Select a Role"
    )


class CreateGroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset = Permission.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permission'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

        widgets = {
                'name': forms.TextInput(attrs={
                    'class': 'w-full px-3 py-2 mt-1 mb-2 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-orange-500',
                    'placeholder': 'Enter Group Name'
                })
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Re-enter new password'
        })
    )

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter your email'
        })
    )
class CustomPasswordConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 rounded border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
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
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500',
                'rows': 4
            }),
            'address': forms.TextInput(attrs={
                'class': 'border p-2 w-full rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500'
            }),
        }



