from config import settings
import logging


logger = logging.getLogger()


"""
FB recommends ...

Title: 45 characters
Subtitle: 80 characters
Call-to-action title: 20 characters
Call-to-action items: 3 buttons
Bubbles per message (horizontal scroll): 10 elements

Image ratio is 1.91:1
"""


_title_warn_len = 45
_subtitle_warn_len = 80
_button_title_warn_len = 20
_buttons_warn_count = 3
_elements_warn_count = 10


def _raise_error(message):
    raise Exception("Invalid message: {}".format(message))


def _raise_missing_property(property_path):
    _raise_error("missing property: {}".format(property_path))


def _raise_bad_value(property_path, description):
    _raise_error("bad value: {} {}".format(property_path, description))


def _raise_empty_value(property_path):
    _raise_bad_value(property_path, "cannot be 'None' or empty.")


def _validate_button(button, base_property_path):
    if not button:
        _raise_empty_value(base_property_path)

    if not "title" in button:
        _raise_missing_property("{}.title".format(base_property_path))

    if not button["title"]:
        _raise_empty_value("{}.title".format(base_property_path))

    if len(button["title"]) > _button_title_warn_len:
        logger.warn("button title length of {} exceeds the recommended maximum of {}".format(
            len(button["title"]), _button_title_warn_len))

    if not "type" in button:
        _raise_missing_property("{}.type".format(base_property_path))

    if button["type"] == "web_url":
        if not "url" in button:
            _raise_missing_property("{}.url".format(base_property_path))

        if not button["url"]:
            _raise_empty_value("{}.url".format(base_property_path))

    elif button["type"] == "postback":
        if not "payload" in button:
            _raise_missing_property("{}.payload".format(base_property_path))

        if not button["payload"]:
            _raise_empty_value("{}.payload".format(base_property_path))

    else:
        _raise_bad_value("{}.type", "must contain either 'web_url' or 'postback'")


def _validate_element(element, base_property_path):
    if not element:
        _raise_empty_value(base_property_path)

    if not "title" in element:
        _raise_missing_property("{}.title".format(base_property_path))

    if not element["title"]:
        _raise_empty_value("{}.title".format(base_property_path))

    if len(element["title"]) > _title_warn_len:
        logger.warn("element title length of {} exceeds the recommended maximum of {}".format(
            len(element["title"]), _title_warn_len))

    if "subtitle" in element and len(element["subtitle"]) > _subtitle_warn_len:
        logger.warn("element subtitle length of {} exceeds the recommended maximum of {}".format(
            len(element["subtitle"]), _subtitle_warn_len))

    if "buttons" in element:
        if len(element["buttons"]) > _buttons_warn_count:
            logger.warn("element button count of {} exceeds the recommended maximum of {}".format(
                len(element["buttons"]), _buttons_warn_count))

        for button in element["buttons"]:
            _validate_button(button, "{}.button[]".format(base_property_path))


def _validate_button_template(template, base_property_path):
    if not "text" in template:
        _raise_missing_property("{}.text".format(base_property_path))

    if not template["text"]:
        _raise_empty_value("{}.text".format(base_property_path))

    if len(template["text"]) > _button_title_warn_len:
        logger.warn("button title length of {} exceeds the recommended maximum of {}".format(
            len(template["text"]), _button_title_warn_len))

    if "buttons" in template:
        if len(template["buttons"]) > _buttons_warn_count:
            logger.warn("tmeplate button count of {} exceeds the recommended maximum of {}".format(
                len(template["buttons"]), _buttons_warn_count))

        for button in template["buttons"]:
            _validate_button(button, "{}.button[]".format(base_property_path))



def _validate_template(template, base_property_path):
    if not "template_type" in template:
        _raise_missing_property("{}.template_type".format(base_property_path))

    if not template["template_type"]:
        _raise_empty_value("{}.template_type".format(base_property_path))

    if template["template_type"] == "button":
        _validate_button_template(template, base_property_path)

    elif template["template_type"] == "generic":
        if not "elements" in template:
            _raise_missing_property("{}.elements".format(base_property_path))

        if len(template["elements"]) > _elements_warn_count:
            logger.warn("tmeplate element count of {} exceeds the recommended maximum of {}".format(
                len(template["elements"]), _elements_warn_count))

        for element in elements:
            _validate_element(element, "{}.elements[]".format(base_property_path))

    else:
        _raise_bad_value("{}.payload.template_type", "must contain either 'button' or 'generic'")


def _validate_attachment(attachment, base_property_path):
    if not attachment:
        _raise_empty_value(base_property_path)

    if not "payload" in attachment:
        _raise_missing_property("{}.payload".format(base_property_path))

    if not attachment["payload"]:
        _raise_empty_value("{}.payload".format(base_property_path))

    if not "type" in attachment:
        _raise_missing_property("{}.type".format(base_property_path))

    if not attachment["type"]:
        _raise_empty_value("{}.type".format(base_property_path))

    if attachment["type"] == "image":
        if not "url" in attachment["payload"]:
            _raise_missing_property("{}.payload.url".format(base_property_path))

        if not attachment["payload"]["url"]:
            _raise_empty_value("{}.payload.url".format(base_property_path))

    elif attachment["type"] == "template"
        _validate_template(attachment["payload"], "{}.payload".format(base_property_path))

    else:
        _raise_bad_value("$.message.attachment.type", "must contain either 'image' or 'template'")


def validate_message(message):
    if not message:
        _raise_empty_value("$")

    if not "recipient" in message:
        _raise_missing_property("$.recipient")

    if "id" in message["recipient"]:
        if not message["recipient"]["id"]:
            _raise_empty_value("$.recipient.id")

    elif "phone_number" in message["recipient"]:
        if not message["recipient"]["phone_number"]:
            _raise_empty_value("$.recipient.phone_number")

    else:
        _raise_bad_value("$.message.recipient", "must contain either 'id' or 'phone_number'")

    if not "message" in message:
        _raise_missing_property("$.message")

    if not message["message"]:
        _raise_empty_value("$.message")

    if "text" in message["message"]:
        if not message["message"]["text"]:
            _raise_empty_value("$.message.text")
    elif "attachment" in message["message"]:
        _validate_attachment(message["message"]["attachment"], "$.message.attachment")
    else:
        _raise_bad_value("$.message", "must contain either 'text' or 'attachment'")