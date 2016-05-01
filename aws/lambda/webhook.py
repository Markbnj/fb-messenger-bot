import handlers
import inspect
import json
import logging
import os
import sys


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, current_dir)


tokens = None
config_path = os.path.join(current_dir, "config")
with open("{}/tokens.json".format(config_path), "rb") as f:
    tokens = json.loads(f.read())


def handler(event, context):
    """
    Called for all requests against the attached API gateway
    endpoint.
    """
    logger.debug("Entering webhook handler")
    my_access_token = tokens.get("accessToken")
    access_token = event.get("accessToken")
    if access_token != my_access_token:
        logger.debug("Access token check failed")
        return "403 Forbidden; bad access token"
    else:
        return handlers.dispatch(event, context, tokens)

