import base64
from django import template

register = template.Library()


@register.filter(name="base64")
def base64_encode(value):
    """
    Encodes a binary image to base64.
    """
    if value:
        return base64.b64encode(value).decode("utf-8")
    return ""
