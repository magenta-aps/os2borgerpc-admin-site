from django import template
from django.utils.safestring import mark_safe
from django.utils.timesince import timesince
from datetime import datetime
from django.core.files.storage import default_storage

from os2borgerpc_admin import utils as global_utils

import os
import urllib.parse

register = template.Library()


@register.filter
def field_add_attribute(field, args):
    """Modify a form with any custom field and value and return the modified form."""
    attribute_name, attribute_value = args.split(",")
    field.field.widget.attrs[attribute_name] = attribute_value
    return field


@register.filter
def append(input, value_to_append):
    return input + value_to_append


@register.simple_tag
def set_css_class_active(url_name, match):
    """
    Set css class active depending on url_name and match.

    url_name is the 'name' of an entry in urls.py
    match is a string to be matched in url_name
    """
    if match in url_name:
        # Don't highlight Scripts when on Security Scripts page.
        if match == "script" and "security_script" in url_name:
            return
        return "active"


@register.filter
def render_custom_links_markdown(text, site_uid):
    return global_utils.render_custom_links(text, site_uid, True)


@register.filter
def file_basename(value):
    """
    Print out the file name without the full path.
    Used to show file parameters in policies to the user.
    """
    try:
        if not value:
            return "No file"

        file_path = value.file.name
        if not default_storage.exists(file_path):
            return "File not found"

        return os.path.basename(file_path)
    except Exception:
        return "Error: File not found"


@register.filter
def bold(text):
    return mark_safe("<strong>" + text + "</strong>")


@register.filter
def italic(text):
    text = str(text)
    return mark_safe("<em>" + text + "</em>")


@register.filter
def timesince_string(text, string_format="%Y-%m-%d %H:%M"):
    return timesince(datetime.strptime(text, string_format))


@register.filter
def get_model_name(text):
    return text._meta.object_name


# HTMX computers table filters


@register.filter
def params_sort_by_asc_desc_none(params, sort_tag):
    new_params = params.copy()

    # start on first page when resorting
    new_params["page"] = 1

    # flip sort_by output in this cyclus:
    # None|SomeOtherTag -> sort_tag -> -sort_tag -> sort_tag -> -sort_tag ...
    if sort_tag == params["sort"]:
        new_params["sort"] = "-" + sort_tag
    else:
        new_params["sort"] = sort_tag

    return new_params


@register.filter
def params_show_sort_arrow(params, sort_tag):
    if sort_tag == params["sort"]:
        return "\u2191"  # UPWARDS ARROW

    if sort_tag == params["sort"][1:]:  # filter prefix '-' out
        return "\u2193"  # DOWNWARDS ARROW

    return "\u2194"  # LEFT RIGHT ARROW


@register.filter
def params_get(params, params_key):
    # avoid display 'None' in search field
    return params.get(params_key, "")


@register.filter
def params_set_name(params, name):
    new_params = params.copy()
    new_params["name"] = name
    return new_params


@register.filter
def params_set_page(params, page):
    new_params = params.copy()
    new_params["page"] = page
    return new_params


@register.filter
def params_urlencode(params):
    return urllib.parse.urlencode(params)


# CURRENTLY UNUSED


# NOTE: Currently this returns a widget rather than a form, so it can't be passed to e.g. as_crispy_field which expects a form
# field_add_attribute below solves this issue
@register.filter
def add_class(field, class_name):
    """Add CSS classes to tags, e.g. django generated forms."""
    return field.as_widget(attrs={"class": " ".join((field.css_classes(), class_name))})


# Used when you have a dictionary and the key is in a variable
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


### DEBUGGING ###


@register.filter
def is_instance_of(obj, class_name):
    return class_name in str(obj.__class__)


@register.filter
def is_type(obj, obj_type):
    return type(obj) is obj_type


# Useful for investigating what's in the {{context}}
@register.filter
def get_fields(obj):
    return [(field.name, field.value_to_string(obj)) for field in obj._meta.fields]


# Useful for investigating what's in the {{context}}
@register.filter
def get_attrs(value):
    return dir(value)


# Some fields do not have _meta so get_model_name fails.
@register.filter
def get_class(text):
    return text.__class__
