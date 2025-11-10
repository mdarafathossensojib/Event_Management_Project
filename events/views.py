from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from events.forms import EventForm, ParticipantForm, CategoryForm
from events.models import Event, Participant, Category
from django.utils import timezone


def dashboard(request):
    today = timezone.now().date()

    # Base Query
    base_query = Event.objects.select_related('category').prefetch_related('participants')

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


    events = events.annotate(participant_count=Count('participants'))

    # For sidebar upcoming events
    up_events = base_query.filter(date__gt=today).annotate(
        participant_count=Count('participants')
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



def details(request, id):
    # Get event with related category and participants, and annotate participant count

    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants').annotate(participant_count=Count('participants')), id=id)

    return render(request, 'details.html', {'event': event})

def event_create(request):
    # Create Event

    event_form = EventForm()

    if request.method == 'POST':
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save()
            # Add participants to the event
            for p in event_form.cleaned_data['participants']:
                p.events.add(event)
            messages.success(request, 'Event created successfully!')
            return redirect('dashboard')

    context = {'form': event_form}
    return render(request, 'event_form.html', context)

def event_update(request, id):
    # Update Event
    event = Event.objects.get(id=id)
    event_form = EventForm(instance=event)
    event_form.fields['participants'].initial = event.participants.all()

    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        if event_form.is_valid():
            event = event_form.save()
            # Update participants
            event.participants.clear()
            # Add selected participants
            for p in event_form.cleaned_data['participants']:
                p.events.add(event)

            messages.success(request, 'Event updated successfully!')
            return redirect('dashboard')

    return render(request, 'update_form.html', {'form': event_form})

def event_delete(request, id):
    # Delete Event
    if request.method == 'POST':
        event = Event.objects.get(id=id)
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('dashboard')
    else:
        messages.error(request, 'Invalid request method.')

    return render(request, 'dashboard.html')


def participants(request):
    # View and Create Participants
    participants = Participant.objects.all()
    form = ParticipantForm()
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participant created successfully!')
            return redirect('participants')
    return render(request, 'participant.html', {'form': form, 'participants': participants})


def category(request):
    # View and Create Categories
    category = Category.objects.all()
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category')
    return render(request, 'category.html', {'form': form, 'category': category})