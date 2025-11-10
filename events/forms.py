from django import forms
from events.models import Event, Participant, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Category Name'}),
            'description': forms.Textarea(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Category Description'}),
        }


class EventForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=Participant.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        required=False
    )

    class Meta:
        model = Event
        fields = ['name', 'category', 'description', 'date', 'time', 'location'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full', 'placeholder': 'Enter Event Name'}),
            'description': forms.Textarea(attrs={'class': 'border-2 border-orange-500 py-2 w-full', 'placeholder': 'Enter Description'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Participant Name'}),
            'email': forms.EmailInput(attrs={'class': 'border-2 border-orange-500 py-2 w-full focus:outline-none', 'placeholder': 'Enter Participant Email'}),
           'events': forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
        }
