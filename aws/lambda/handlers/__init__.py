import logging
import verification_handler
import message_handler
import auth_handler
import postback_handler
from validation import validate_postback


logger = logging.getLogger()


def dispatch_postback(body):
    """
    Recieves a postback event and walks the entry and messaging lists
    passing the data to the proper handlers.
    """
    validate_postback(body)

    entries = body["entry"]
    for entry in entries:
        page_id = entry["id"]
        time = entry["time"]
        messages = entry["messaging"]
        for envelope in messages:
            if "optin" in envelope:
                return auth_handler.auth(page_id, time, envelope)
            elif "message" in envelope:
                return message_handler.received(page_id, time, envelope)
            elif "delivery" in envelope:
                return message_handler.delivered(page_id, time, envelope)
            else:
                return postback_handler.postback(page_id, time, envelope)


def dispatch(method, query, body):
    """
    Receives all events from the webhook entrypoint and figures out which
    handler method to call.
    """
    logger.debug("{} method received; query={}, body={}".format(method, query, body))
    if method == "GET":
        return verification_handler.verify(query)
    elif method == "POST":
        return dispatch_postback(body)
    else:
        raise Exception("400 Bad Request; unhandled method {}".format(method))
