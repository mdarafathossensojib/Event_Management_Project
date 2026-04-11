from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from events.models import Event, Category
from django.contrib import messages
from events.models import Category
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from events.forms import EventForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.contrib import messages
from events.forms import AssignRoleForm, CreateGroupForm

User = get_user_model()


def events_page(request):
    events = Event.objects.select_related('category').all()
    categories = Category.objects.all()

    context = {
        "events": events,
        "categories": categories
    }
    return render(request, "events.html", context)


def event_detail(request, id):
    related_events = Event.objects.filter(is_featured=True).annotate(
        participant_count=Count('participants')
    )[1:4]
    event = get_object_or_404(Event, id=id)
    schedules = event.schedules.all().order_by('day', 'time')
    speakers = event.speakers.all()

    context = {
        'event': event,
        'schedules': schedules,
        'speakers': speakers,
        'related_events': related_events
    }
    return render(request, 'events/event_details.html', context)


def how_it_works(request):
    return render(request, 'how_it_works.html')

def categories_list(request):
    categories = Category.objects.annotate(event_count=Count('events'))
    return render(request, 'category.html', {'categories': categories})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect('contact')
        
    return render(request, 'contact.html')

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    events = Event.objects.filter(category=category).order_by('-date')
    
    context = {
        'category': category,
        'events': events,
    }
    return render(request, 'category_detail.html', context)




class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Admin').exists()

# --- EVENT VIEWS ---
class AdminEventListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Event
    template_name = 'admin/admin_event.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event_id = self.request.GET.get('edit_id')
        if event_id:
            instance = Event.objects.get(id=event_id)
            context['form'] = EventForm(instance=instance)
            context['edit_mode'] = True
            context['edit_id'] = event_id
        else:
            context['form'] = EventForm()
            context['edit_mode'] = False
            
        return context

    def post(self, request, *args, **kwargs):
        event_id = request.POST.get('event_id')
        if event_id: # Update logic
            instance = Event.objects.get(id=event_id)
            form = EventForm(request.POST, request.FILES, instance=instance)
        else: # Create logic
            form = EventForm(request.POST, request.FILES)
        
        if form.is_valid():
            event = form.save(commit=False)
            if not event_id:
                event.organizer = request.user
            event.save()
            return redirect('admin-events')
        
        return self.get(request, *args, **kwargs)



# --- CATEGORY VIEWS ---
class AdminCategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Category
    template_name = 'admin/admin_category.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        edit_id = self.request.GET.get('edit_id')
        if edit_id:
            instance = get_object_or_404(Category, id=edit_id)
            context['form'] = CategoryForm(instance=instance)
            context['edit_mode'] = True
            context['edit_id'] = edit_id
        else:
            context['form'] = CategoryForm()
            context['edit_mode'] = False
            
        return context

    def post(self, request, *args, **kwargs):
        edit_id = request.POST.get('category_id')
        if edit_id: # Update
            instance = get_object_or_404(Category, id=edit_id)
            form = CategoryForm(request.POST, instance=instance)
        else: # Create
            form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('admin-categories')
        
        return self.get(request, *args, **kwargs)
    

@login_required
def delete_event(request, id):
    if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
        event = get_object_or_404(Event, id=id)
        event.delete()
    return redirect('admin-events')

@login_required
def delete_category(request, id):
    if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
        category = get_object_or_404(Category, id=id)
        category.delete()
    return redirect('admin-categories')



class AdminRolePermissionView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/admin_user.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.prefetch_related('permissions__content_type').all()
        
        # User Assignment Form logic
        assign_user_id = self.request.GET.get('assign_user')
        if assign_user_id:
            user_inst = get_object_or_404(User, id=assign_user_id)
            context['assign_form'] = AssignRoleForm(initial={'role': user_inst.groups.first()})
            context['target_user'] = user_inst
            context['mode'] = 'assign'

        # Group Create/Update Form logic
        edit_group_id = self.request.GET.get('edit_group')
        if edit_group_id:
            group_inst = get_object_or_404(Group, id=edit_group_id)
            context['group_form'] = CreateGroupForm(instance=group_inst)
            context['mode'] = 'group_form'
        else:
            context['group_form'] = CreateGroupForm()
            
        return context

    def post(self, request, *args, **kwargs):
        # Handle Role Assignment to User
        if 'submit_assign' in request.POST:
            user_id = request.POST.get('target_user_id')
            user = get_object_or_404(User, id=user_id)
            form = AssignRoleForm(request.POST)
            if form.is_valid():
                user.groups.clear()
                user.groups.add(form.cleaned_data['role'])
                messages.success(request, f"Role updated for {user.username}")
                
        # Handle Group Creation/Update
        elif 'submit_group' in request.POST:
            group_id = request.POST.get('group_id')
            if group_id:
                instance = get_object_or_404(Group, id=group_id)
                form = CreateGroupForm(request.POST, instance=instance)
            else:
                form = CreateGroupForm(request.POST)
                
            if form.is_valid():
                form.save()
                messages.success(request, "Group/Role saved successfully!")

        return redirect('admin-users')