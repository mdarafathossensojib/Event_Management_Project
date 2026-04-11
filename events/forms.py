from django import forms
from events.models import Event, Category
from django.contrib.auth.models import Group, Permission


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5 focus:ring-cyan-500 focus:border-cyan-500'}),
            'slug': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'placeholder': 'e.g. tech-events'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'placeholder': 'fas fa-code'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['organizer', 'registered', 'attendees'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'slug': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'category': forms.Select(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'rows': 4}),
            'date': forms.DateInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-black border border-zinc-800 text-white rounded-lg p-2.5'}),
            'image': forms.FileInput(attrs={'class': 'w-full text-gray-400'}),
        }


class AssignRoleForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a Role",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all'
        })
    )


class CreateGroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related('content_type').all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'rounded border-zinc-700 bg-zinc-800 text-cyan-500 focus:ring-0 focus:ring-offset-0'
        }),
        required=False,
        label='Assign Permissions'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-xl text-white focus:ring-2 focus:ring-cyan-500 outline-none transition-all',
                'placeholder': 'Role Name (e.g. Moderator)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'codename')