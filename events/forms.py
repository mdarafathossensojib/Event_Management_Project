from django import forms
from events.models import Event, Category
from django.contrib.auth.models import User, Group, Permission

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Category Name'}),
            'description': forms.Textarea(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Category Description'}),
        }


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['name', 'category', 'description', 'date', 'time', 'location', 'asset', 'user'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Event Name'}),
            'description': forms.Textarea(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Description'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Location'}),
            'user' : forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        }

