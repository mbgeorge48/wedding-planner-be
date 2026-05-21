from django import template

register = template.Library()


@register.inclusion_tag("components/common/form_field.html")
def form_field(
    name,
    label=None,
    type="text",
    value=None,
    choices=None,
    errors=None,
    help_text=None,
    required=False,
    **kwargs
):
    """
    Renders a consistent form field.
    Supports interpolation in label and help_text using {key} syntax.
    Example: {% form_field label="Hello {name}" name="user" name_val="John" %}
    """

    # Handle interpolation for label and help_text
    if label and "{" in label:
        try:
            label = label.format(**kwargs)
        except (KeyError, ValueError):
            pass

    if help_text and "{" in help_text:
        try:
            help_text = help_text.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return {
        "name": name,
        "label": label,
        "type": type,
        "value": value,
        "choices": choices,
        "errors": errors,
        "help_text": help_text,
        "required": required,
        "extra_classes": kwargs.get("class", ""),
        "attrs": kwargs,
    }
