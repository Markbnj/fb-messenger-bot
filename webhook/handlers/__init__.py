from config import settings
import logging
from validation import validate_postback


logger = logging.getLogger()


def postback_received(page_id, time, data):
    """
    Handles a postback event.
    Params:
        page_id: the page id, corresponds to $.entry[i].id in the callback data
        time: the update time, corresponds to $.entry[i].time in the callback data
        data: the postback content, $.entry[i].messaging[i] in the callback data
        settings: contains the page token in "pageToken"
    """
    logger.debug("Postback recv: page_id: {}, time: {}, data: {}".format(page_id, time, data))


def auth_received(page_id, time, data):
    """
    Handles the auth callback event.
    Params:
        page_id: the page id, corresponds to $.entry[i].id in the callback data
        time: the update time, corresponds to $.entry[i].time in the callback data
        data: the auth content, $.entry[i].messaging[i] in the callback data
        settings: contains the page token in "pageToken"
    """
    logger.debug("Auth recv: page_id: {}, time: {}, data: {}".format(page_id, time, data))


def message_received(page_id, time, envelope):
    """
    Processes a single received message.
    Params:
        page_id: the page id, corresponds to $.entry[i].id in the callback data
        time: the update time, corresponds to $.entry[i].time in the callback data
        envelope: the message content container, $.entry[i].messaging[i] in the callback data
        settings: contains the page token in "pageToken"
    """
    logger.debug("Message recv: page_id: {}, time: {}, envelope: {}".format(page_id, time, envelope))


def message_delivered(page_id, time, receipt):
    """
    Processes a single message delivery receipt (callback)
    Params:
        page_id: the page id, corresponds to $.entry[i].id in the callback data
        time: the update time, corresponds to $.entry[i].time in the callback data
        receipt: the delivery receipt, $.entry[i].messaging[i] in the callback data
        settings: contains the page token in "pageToken"
    """
    logger.debug("Message delivered: page_id: {}, time: {}, receipt: {}".format(page_id, time, receipt))


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
                return auth_received(page_id, time, envelope)
            elif "message" in envelope:
                return message_received(page_id, time, envelope)
            elif "delivery" in envelope:
                return message_delivered(page_id, time, envelope)
            else:
                return postback_received(page_id, time, envelope)


def verify_webhook(query):
    """
    Handles the API verification step from Facebook, which consists of a GET
    to the webhook with the following querystring args:

        hub.verify_token = the verification token you supplied when setting up
        the web hook.

        hub.challenge = the challenge value Facebook expects back.

    The expected value for the verify_token is stored in config/settings.json,
    which is read in webhook.pay and passed in the settings param to this call.
    """
    my_verify_token = settings.get("verifyToken")
    verify_token = query.get("hub.verify_token")
    if not verify_token:
        raise Exception("400 Bad Request; missing verification token")

    if verify_token == my_verify_token:
        challenge = query.get("hub.challenge")
        if not challenge:
            raise Exception("400 Bad Request; missing challenge")
        else:
            return challenge
    else:
        raise Exception("403 Forbidden; verification token mismatch")


def dispatch(method, query, body):
    """
    Receives all events from the webhook entrypoint and figures out which
    handler method to call.
    """
    logger.debug("{} method received; query={}, body={}".format(method, query, body))
    if method == "GET":
        return verify_webhook(query)
    elif method == "POST":
        return dispatch_postback(body)
    else:
        raise Exception("400 Bad Request; unhandled method {}".format(method))
