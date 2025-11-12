from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("components/common/button.html")
def button(**kwargs):
    """
    Renders a button or link, depending on whether `href` or `url_name` is provided.

    Usage examples:
      {% button text="RSVP Now" href=rsvp_url %}
      {% button text="Go Home" url_name="home" %}
      {% button text="Edit" url_name="user_edit" pk=user.id %}
    """
    context = {
        "text": kwargs.get("text", "Click"),
        "type": kwargs.get("type", "button"),
    }

    if "href" in kwargs:
        context["href"] = kwargs["href"]
    elif "url_name" in kwargs:
        url_args = kwargs.get("args", [])
        url_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in {"text", "type", "url_name", "args", "href"}
        }
        context["href"] = reverse(kwargs["url_name"], args=url_args, kwargs=url_kwargs)
    else:
        context["href"] = None

    return context
