from config import settings
import json
import logging
import os
import re


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


templates_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")


"""
Title: 45 characters
Subtitle: 80 characters
Call-to-action title: 20 characters
Call-to-action items: 3 buttons
Bubbles per message (horizontal scroll): 10 elements

Image ratio is 1.91:1
"""

def send_message(message):
    """
    Sends a structured or unstructured message to a specific page-scoped
    user ID.
    Params:

        message: dictionary containing rendered message template

    Returns:
        stuff
    """
    pass


def _render(template, data):
    """
    Performs substitution and pruning of a template by replacing
    all matching values in the template with the values in data,
    and then removing any unmatched patterns. Calls itself
    recursively if the value of a key is a dict.
    """
    field_re = re.compile("{{.+}}")
    for field_name in data:
        for (k,v) in template.items():
            if isinstance(v, dict):
                template[k] = _render(v, data)
                if len(template[k]) == 0:
                    del template[k]
            elif v == "{{{{{}}}}}".format(field_name):
                template[k] = data[field_name]
    for (k,v) in template.items():
        if not isinstance(v,dict) and field_re.match(v):
            del template[k]
    return template


def make_message(recipient_id, template_name, data):
    """
    Loads and returns a message template
    Params:

        recipient_id: FB page-scoped id of the recipient user
        template_name: string name of template to load
        data: dictionary of template values
    """
    if not template_name.endswith(".json"):
        template_file = os.path.join(templates_dir, "{}.json".format(template_name))
    else:
        template_file = os.path.join(templates_dir, template_name)
    try:
        with open(template_file, "rb") as f:
            template = json.loads(f.read())
            template["recipient"]["id"] = recipient_id
            return _render(template, data)
    except Exception as e:
        logger.error("Failed to render template: {}; error: {}".format(template_name, e))
        raise Exception("500 Internal Server Error; failed to render template")


def add_message_element(message, title, subtitle=None, image_url=None, item_url=None, buttons=None):
    """
    Adds a message element to an existing message and returns it
    Params:

        message: an existing message created using make_message()
        title: required, string title for the element
        subtitle: optional, string subtitle
        image_url: optional, string url to element image
        item_url: optional, string url to open when element is tapped
        buttons: optional, list of buttons created with make_message_button()
    """
    pass


def make_url_button(title, url):
    """
    Loads and returns a web url button template
    Params:

        title: the button title
        url: the url to open when the button is tapped
    """
    pass


def make_postback_button(title, payload):
    """
    Loads and returns a postback button template
    Params:

        title: the button title
        payload: data returned with the postback
    """
    pass