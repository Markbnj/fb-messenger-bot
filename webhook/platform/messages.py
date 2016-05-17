from config import settings
import json
import logging
import os
import re
import requests
from validation import validate_message


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
    validate_message(message)
    url = settings.get("graphSendUrl").format(settings.get("pageToken"))
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(message))
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        logger.error("Send message call failed: {}".format(response.text))
        raise Exception("500 Internal Server Error; graph API call failed with status: {}".format(response.status_code))


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
            elif isinstance(v, list):
                continue
            elif v == "{{{{{}}}}}".format(field_name):
                template[k] = data[field_name]
    for (k,v) in template.items():
        if isinstance(v,(dict,list)):
            continue
        if field_re.match(v):
            del template[k]
    return template


def make_message(recipient_id, template_name, data=None, buttons=None):
    """
    Loads and returns a message template
    Params:

        recipient_id: required, FB page-scoped id of the recipient user
        template_name: required, string name of template to load
        data: optional, dictionary of template values
        buttons: optional, list of buttons to add, template must be "button_message"
    """
    if not template_name.endswith(".json"):
        template_file = os.path.join(templates_dir, "{}.json".format(template_name))
    else:
        template_file = os.path.join(templates_dir, template_name)
    try:
        with open(template_file, "rb") as f:
            template = json.loads(f.read())
        template["recipient"]["id"] = recipient_id
        if data:
            template = _render(template, data)
        if buttons:
            template["message"]["attachment"]["payload"]["buttons"].extend(buttons)
    except Exception as e:
        logger.error("Failed to render template: {}; error: {}".format(template_name, e))
        raise Exception("500 Internal Server Error; failed to render template")
    else:
        return template


def add_message_element(message, title, subtitle="", image_url="", item_url="", buttons=None):
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
    template_file = os.path.join(templates_dir, "_element.json")
    with open(template_file, "rb") as f:
        template = json.loads(f.read())
    template = _render(template, {
        "element_title": title,
        "element_image_url": image_url if image_url else "",
        "element_item_url": item_url if item_url else "",
        "element_subtitle": subtitle if subtitle else ""
    })
    if buttons:
        template["buttons"].extend(buttons)
    message["message"]["attachment"]["payload"]["elements"].append(template)


def make_url_button(title, url):
    """
    Loads and returns a web url button template
    Params:

        title: the button title
        url: the url to open when the button is tapped
    """
    template_file = os.path.join(templates_dir, "_url_button.json")
    with open(template_file, "rb") as f:
        template = json.loads(f.read())
    return _render(template, {"button_url":url, "button_title":title})


def make_postback_button(title, payload):
    """
    Loads and returns a postback button template
    Params:

        title: the button title
        payload: data returned with the postback
    """
    template_file = os.path.join(templates_dir, "_postback_button.json")
    with open(template_file, "rb") as f:
        template = json.loads(f.read())
    return _render(template, {"button_payload":payload, "button_title":title})

