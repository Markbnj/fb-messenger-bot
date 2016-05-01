import logging
import verification_handler
import message_handler


logger = logging.getLogger()


def dispatch(event, context, tokens):
    """
    Receives all events from the webhook entrypoint and figures out which
    handler method to call.
    """
    method = event.get("method")
    if method == "GET":
        logger.debug("GET method received; event={}".format(event))
        return verification_handler.verify(event, context, tokens)
    elif method == "POST":
        logger.debug("POST method received; event={}".format(event))
        return message_handler.receive(event, context, tokens)
    else:
        raise Exception("400 Bad Request; unhandled method {}".format(method))