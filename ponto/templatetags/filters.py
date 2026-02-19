from django import template
from datetime import timedelta

register = template.Library()

@register.filter(name='timedeltaformat')
def timedeltaformat(td):
    if td is None or td.total_seconds() == 0:
        return "0h 0min"
    
    total_seconds = int(td.total_seconds())

    # Trata sinal corretamente
    sign = '-' if total_seconds < 0 else ''
    total_seconds = abs(total_seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    if hours == 0:
        return f"{sign}{minutes}min"
    
    return f"{sign}{hours}h {minutes:02}min"