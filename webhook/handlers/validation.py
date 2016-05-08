def raise_error(message):
    raise Exception("400 Bad Request; {}".format(message))


def validate_auth_postback(auth):
    if not auth:
        raise_error("missing property: $.entry[].messaging[].optin")
    s = auth.get("ref")
    if not s:
        raise_error("missing property: $.entry[].messaging[].optin.ref")


def validate_attachment(attachment):
    if not attachment:
        raise_error("missing property: $.entry[].messaging[].message.attachment[]")
    s = attachment.get("type")
    if not s in ["image", "video", "audio"]:
        raise_error("bad value: {}, property: $.entry[].messaging[].message.attachment[].type".format(s))
    if not "payload" in attachment:
        raise_error("missing property: $.entry[].messaging[].message.attachment[].payload")
    s = attachment["payload"].get("url")
    if not s:
        raise_error("missing property: $.entry[].messaging[].message.attachment[].payload.url")


def validate_message_postback(message):
    if not message:
        raise_error("missing property: $.entry[].messaging[].message")
    s = message.get("mid")
    if not s:
        raise_error("missing property: $.entry[].messaging[].message.mid")

    s = message.get("seq")
    if not s:
        raise_error("missing property: $.entry[].messaging[].message.seq")

    if "text" in message:
        s = message.get("text")
        if not s:
            raise_error("missing property: $.entry[].messaging[].message.text")
    elif "attachments" in message:
        if not len(message["attachments"]):
            raise_error("items expected, property: $.entry[].messaging[].message.attachments")
        for attachment in message["attachments"]:
            validate_attachment(attachment)
    else:
        raise_error("missing property: $.entry[].messaging[].message must have one of: text, attachments")


def validate_delivery_postback(delivery):
    if not delivery:
        raise_error("missing property: $.entry[].messaging[].delivery")
    n = delivery.get("watermark")
    if not n:
        raise_error("missing property: $.entry[].messaging[].delivery.watermark")

    n = delivery.get("seq")
    if not n:
        raise_error("missing property: $.entry[].messaging[].delivery.seq")

    if not "mids" in delivery:
        raise_error("missing property: $.entry[].messaging[].delivery.mids")

    if not len(delivery["mids"]):
        raise_error("items expected, property: $.entry[].messaging[].delivery.mids")

    for mid in delivery["mids"]:
        if not mid:
            # TBD validate the actual mid format. Example:
            # mid.1461992777559:e8027b338d2b553b73
            raise_error("missing property: $.entry[].messaging[].delivery.mids[]")


def validate_user_postback(postback):
    if not postback:
        raise_error("missing property: $.entry[].messaging[].postback")
    s = postback.get("payload")
    if not s:
        raise_error("missing property: $.entry[].messaging[].postback.payload")


def validate_postback(data):
    """
    Validates that the data received from facebook in a postback
    is complete and well-formed.
    """
    s = data.get("object")
    if not s in ["page"]:
        raise_error("bad value: {}, property: $.object".format(s))

    if not "entry" in data:
        raise_error("missing property: $.entry")

    if not len(data["entry"]):
        raise_error("items expected, property: $.entry")

    for entry in data["entry"]:
        n = entry.get("id")
        if not n:
            raise_error("missing property: $.entry[].id")

        n = entry.get("time")
        if not n:
            raise_error("missing property: $.entry[].time")

        if not "messaging" in entry:
            raise_error("missing property: $.entry[].messaging")

        if not len(entry["messaging"]):
            raise_error("items expected, property: $.entry[].messaging")

        for envelope in entry["messaging"]:
            if not "sender" in envelope:
                raise_error("missing property: $.entry[].messaging[].sender")

            n = envelope["sender"].get("id")
            if not n:
                raise_error("missing property: $.entry[].messaging[].sender.id")

            if not "recipient" in envelope:
                raise_error("missing property: $.entry[].messaging[].recipient")

            n = envelope["recipient"].get("id")
            if not n:
                raise_error("missing property: $.entry[].messaging[].recipient.id")

            if "optin" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    raise_error("missing property: $.entry[].messaging[].timestamp")
                validate_auth_postback(envelope["optin"])
            elif "message" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    raise_error("missing property: $.entry[].messaging[].timestamp")
                validate_message_postback(envelope["message"])
            elif "delivery" in envelope:
                validate_delivery_postback(envelope["delivery"])
            elif "postback" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    raise_error("missing property: $.entry[].messaging[].timestamp")
                validate_user_postback(envelope["postback"])
            else:
                raise_error("unknown message in $.entry[].messaging[]")

