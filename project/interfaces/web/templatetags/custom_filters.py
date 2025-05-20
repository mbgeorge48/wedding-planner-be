from django import template

register = template.Library()


@register.filter
def ordinal_date(value):
    if not hasattr(value, "day"):
        return value  # not a date

    day = value.day
    suffix = (
        "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    )
    return value.strftime(f"%-d{suffix} of %B %Y")
