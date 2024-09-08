import re
from django import template
from django.utils.html import format_html

register = template.Library()

# Regular expression to match URLs
url_pattern = re.compile(r"((http|https)://[^\s]+)")


@register.filter(name="make_links")
def make_links(value):
    """
    Convert URLs in text to clickable links.
    """
    return url_pattern.sub(
        lambda match: format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer" class="text-white">{}</a>',
            match.group(0),
            match.group(0),
        ),
        value,
    )


@register.filter(name="update_bg_color")
def update_bg_color(content):
    """
    Update background color based on the presence of '@' in the message content.
    """
    return "bg-warning" if "@" in content else None
