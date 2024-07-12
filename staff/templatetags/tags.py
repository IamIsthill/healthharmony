from django import template

register = template.Library()

@register.filter
def has_error_message(messages):
    return any('error' in message.tags for message in messages)
