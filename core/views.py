from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils import timezone

from events.models import Event, Category
from core.models import Testimonial, SiteStats, Newsletter


def home(request):
    # Featured Events
    featured_events = Event.objects.filter(is_featured=True).annotate(
        participant_count=Count('participants')
    )[:5]

    # Categories
    categories = Category.objects.annotate(
        event_count=Count('events')
    )

    stats = SiteStats.objects.first()

    if not stats:
        stats = {
            "events_count": Event.objects.count(),
            "users_count": Event.objects.values('participants__user').distinct().count(),
            "cities_count": Event.objects.values('location').distinct().count(),
            "satisfaction_rate": 98,
        }

    # Testimonials
    testimonials = Testimonial.objects.all()[:3]

    context = {
        "featured_events": featured_events,
        "categories": categories,
        "stats": stats,
        "testimonials": testimonials,
    }

    return render(request, "home.html", context)

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            Newsletter.objects.get_or_create(email=email)

    return redirect("home")