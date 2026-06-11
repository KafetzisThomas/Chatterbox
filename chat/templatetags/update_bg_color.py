from django import template

register = template.Library()

@register.filter
def update_bg_color(content):
    """
    Update background color based on the presence of '@' in message content.
    """
    return "bg-warning" if "@" in content else None
