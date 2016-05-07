import logging
import verification_handler
import message_handler
import auth_handler
import postback_handler
from validation import validate_postback


logger = logging.getLogger()


def dispatch_postback(event, settings):
    """
    Recieves a postback event and walks the entry and messaging lists
    passing the data to the proper handlers.
    """
    validate_postback(event["body"])

    entries = event["body"]["entry"]
    for entry in entries:
        page_id = entry["id"]
        time = entry["time"]
        messages = entry["messaging"]
        for envelope in messages:
            if "optin" in envelope:
                return auth_handler.auth(page_id, time, envelope, settings)
            elif "message" in envelope:
                return message_handler.received(page_id, time, envelope, settings)
            elif "delivery" in envelope:
                return message_handler.delivered(page_id, time, envelope, settings)
            else:
                return postback_handler.postback(page_id, time, envelope, settings)


def dispatch(event, settings):
    """
    Receives all events from the webhook entrypoint and figures out which
    handler method to call.
    """
    method = event.get("method")
    if method == "GET":
        logger.debug("GET method received; event={}".format(event))
        return verification_handler.verify(event['query'], settings)
    elif method == "POST":
        logger.debug("POST method received; event={}".format(event))
        return dispatch_postback(event, settings)
    else:
        raise Exception("400 Bad Request; unhandled method {}".format(method))
