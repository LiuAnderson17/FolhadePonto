from django import template
from datetime import timedelta

register = template.Library()

@register.filter(name='timedeltaformat')
def timedeltaformat(td):
    if td is None or td.total_seconds() == 0:
        return "0h 0min"
    
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours == 0:
        return f"{minutes}min"
    return f"{hours}h {minutes}min"