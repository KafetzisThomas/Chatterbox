import re
from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def convert_to_link(value):
    """
    Convert text urls to clickable links.
    """
    url_pattern = re.compile(r"((http|https)://[^\s]+)")
    return url_pattern.sub(lambda match: format_html(
        '<a href="{}" target="_blank" rel="noopener noreferrer" class="text-white">{}</a>', match.group(0), match.group(0)),
        value,
    )
