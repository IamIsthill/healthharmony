from django import template

register = template.Library()


@register.filter
def has_error_message(messages):
    return any("error" in message.tags for message in messages)


@register.filter
def has_success_message(messages):
    return any("success" in message.tags for message in messages)


@register.filter
def ordinal(value):
    try:
        value = int(value)
    except ValueError:
        return value
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return str(value) + suffix
