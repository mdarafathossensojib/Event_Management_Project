from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from django.db.models import Count
# Create your views here.

def home(request):
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
    return render(request, 'home.html', context)

def no_permission(request):
    return render(request, 'no_permission.html')