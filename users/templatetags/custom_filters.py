from django import template
from datetime import datetime
from django.utils import timezone


register = template.Library()

@register.filter
def humanised_date(value):
    if value:
        today = datetime.now().date()
        value = timezone.localtime(value)
        if value.date() == today:
            return f"Today at : {value.strftime('%I:%M %p')}"
        elif value.date() == today.replace(day=today.day - 1):
            return f"Yesterday at {value.strftime('%I:%M %p')}"
        else:
            return value.strftime('%I:%M %p')
    return "No Login Information"
