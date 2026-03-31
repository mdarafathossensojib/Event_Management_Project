from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from events.models import Event, Category

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