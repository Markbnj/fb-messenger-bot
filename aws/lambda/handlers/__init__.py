import logging
import verification_handler
import message_handler
import auth_handler
import postback_handler


logger = logging.getLogger()

# (message received) $.entry[i].messaging[i].message
# (message delivered) $.entry[i].messaging[i].delivery
# (authentication) $.entry[i].messaging[i].optin
# (postback) $.entry[i].messaging[i].postback


def dispatch_callback(event, tokens):
    """
    Recieves a callback event and walks the entry and messaging lists
    passing the data to the proper handlers.
    """
    entries = event.get("entry")
    try:
        for entry in entries:
            page_id = entry.get("id")
            time = entry.get("time")
            messages = entry.get("messaging")
            for message in messages:
                if "optin" in message:
                    return auth_handler.auth(page_id, time, message, tokens)
                elif "message" in message:
                    return message_handler.received(page_id, time, message, tokens)
                elif "delivery" in message:
                    return message_handler.delivered(page_id, time, message, tokens)
                elif "postback" in message:
                    return postback_handler.postback(page_id, time, message, tokens)
                else:
                    logger.warning("Cannot process message: {}".format(message))
    except:
        logger.debug("Error processing event: {}".format(event))
        raise Exception("400 Bad Request; missing or bad data in event")



def dispatch(event, tokens):
    """
    Receives all events from the webhook entrypoint and figures out which
    handler method to call.
    """
    method = event.get("method")
    if method == "GET":
        logger.debug("GET method received; event={}".format(event))
        return verification_handler.verify(event['query'], tokens)
    elif method == "POST":
        logger.debug("POST method received; event={}".format(event))
        return dispatch_callback(event, tokens)
    else:
        raise Exception("400 Bad Request; unhandled method {}".format(method))
