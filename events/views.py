from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from events.forms import EventForm, CategoryForm
from events.models import Event, Category
from django.utils import timezone
from users.views import is_admin
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy


def events(request):
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

    return render(request, 'events.html', context)


class DetailsView(TemplateView):
    template_name = 'details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('id')
        event = get_object_or_404(Event.objects.select_related('category').prefetch_related('user').annotate(participant_count=Count('user')), id=event_id)
        context['event'] = event
        return context

@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = reverse_lazy('events')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.user.add(*form.cleaned_data['user'])
        messages.success(self.request, 'Event created successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'update_form.html'
    success_url = reverse_lazy('events')
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.user.set(form.cleaned_data['user'])
        messages.success(self.request, 'Event Updated successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('events')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category.html'
    success_url = reverse_lazy('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)