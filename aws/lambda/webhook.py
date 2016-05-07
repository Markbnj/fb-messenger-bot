from config import settings
import inspect
import json
import logging
import os
import sys


"""
Set up the logger.
TBD: Should move the level to a stage variable.
"""
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


"""
Add the libs directory to the path so we can access installed packages
"""
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(2, os.path.join(current_dir, "libs"))


"""
This causes installed packages (like requests) to be imported to is has
to be placed after the path fix above.
"""
import handlers


def handler(event, context):
    """
    Called for all requests against the attached API gateway
    endpoint. Expects the request data to be mapped to a json event
    record as defined by aws/api-gateway/request-mapping.json.
    """
    logger.debug("AWS request context: {}".format(context))
    my_access_token = settings.get("accessToken")
    access_token = event.get("accessToken")
    if not access_token:
        logger.debug("Missing access token")
        raise Exception("400 Bad Request; missing access token")
    if access_token != my_access_token:
        logger.debug("Access token check failed")
        raise Exception("403 Forbidden; bad access token")
    else:
        return handlers.dispatch(event, settings)

