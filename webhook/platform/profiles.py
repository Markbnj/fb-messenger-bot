from config import settings
import json
import logging
import os
import requests


logger = logging.getLogger()


default_fields = "first_name,last_name,locale,timezone,gender"


def get(user_id, fields=default_fields):
    """
    Calls the graph API to return the user profile for a specific
    page-scoped user ID.
    Params:
        user_id: the page-scoped user id.
        fields: comma-delimited list of fields to return
    """
    url = settings.get("graphProfileUrl").format(user_id, fields, settings.get("pageToken"))
    logger.debug("Calling {}".format(url))
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("500 Internal Server Error; graph API call failed with status: {}; message: {}".format(response.status_code, response.text))