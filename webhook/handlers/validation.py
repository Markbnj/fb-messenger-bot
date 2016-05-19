def _raise_error(message):
    raise Exception("400 Bad Request; {}".format(message))


def _raise_missing_property(property_path):
    _raise_error("missing property: {}".format(property_path))


def _raise_bad_value(property_path, description):
    _raise_error("bad value: {} {}".format(property_path, description))


def _raise_empty_value(property_path):
    _raise_bad_value(property_path, "cannot be 'None' or empty.")


def validate_auth_postback(auth):
    if not auth:
        _raise_missing_property("$.entry[].messaging[].optin")
    s = auth.get("ref")
    if not s:
        _raise_missing_property("$.entry[].messaging[].optin.ref")


def validate_attachment(attachment):
    if not attachment:
        _raise_missing_property("$.entry[].messaging[].message.attachment[]")
    s = attachment.get("type")
    if not s in ["image", "video", "audio"]:
        _raise_bad_value("$.entry[].messaging[].message.attachment[].type",
            "must be one of 'image', 'video' or 'audio'")
    if not "payload" in attachment:
        _raise_missing_property("$.entry[].messaging[].message.attachment[].payload")
    s = attachment["payload"].get("url")
    if not s:
        _raise_missing_property("$.entry[].messaging[].message.attachment[].payload.url")


def validate_message_postback(message):
    if not message:
        _raise_missing_property("$.entry[].messaging[].message")
    s = message.get("mid")
    if not s:
        _raise_missing_property("$.entry[].messaging[].message.mid")

    s = message.get("seq")
    if not s:
        _raise_missing_property("$.entry[].messaging[].message.seq")

    if "text" in message:
        s = message.get("text")
        if not s:
            _raise_missing_property("$.entry[].messaging[].message.text")
    elif "attachments" in message:
        if not len(message["attachments"]):
            _raise_empty_value("$.entry[].messaging[].message.attachments")
        for attachment in message["attachments"]:
            validate_attachment(attachment)
    else:
        _raise_missing_property("$.entry[].messaging[].message must have one of: text, attachments")


def validate_delivery_postback(delivery):
    if not delivery:
        _raise_missing_property("$.entry[].messaging[].delivery")
    n = delivery.get("watermark")
    if not n:
        _raise_missing_property("$.entry[].messaging[].delivery.watermark")

    n = delivery.get("seq")
    if not n:
        _raise_missing_property("$.entry[].messaging[].delivery.seq")

    if not "mids" in delivery:
        _raise_missing_property("$.entry[].messaging[].delivery.mids")

    if not len(delivery["mids"]):
        _raise_empty_value("$.entry[].messaging[].delivery.mids")

    for mid in delivery["mids"]:
        if not mid:
            # TBD validate the actual mid format. Example:
            # mid.1461992777559:e8027b338d2b553b73
            _raise_missing_property("$.entry[].messaging[].delivery.mids[]")


def validate_user_postback(postback):
    if not postback:
        _raise_missing_property("$.entry[].messaging[].postback")
    s = postback.get("payload")
    if not s:
        _raise_missing_property("$.entry[].messaging[].postback.payload")


def validate_postback(data):
    """
    Validates that the data received from facebook in a postback
    is complete and well-formed.
    """
    s = data.get("object")
    if not s in ["page"]:
        _raise_bad_value("$.object", "must be set to 'page'")

    if not "entry" in data:
        _raise_missing_property("$.entry")

    if not len(data["entry"]):
        _raise_empty_value("$.entry")

    for entry in data["entry"]:
        n = entry.get("id")
        if not n:
            _raise_missing_property("$.entry[].id")

        n = entry.get("time")
        if not n:
            _raise_missing_property("$.entry[].time")

        if not "messaging" in entry:
            _raise_missing_property("$.entry[].messaging")

        if not len(entry["messaging"]):
            _raise_empty_value("$.entry[].messaging")

        for envelope in entry["messaging"]:
            if not "sender" in envelope:
                _raise_missing_property("$.entry[].messaging[].sender")

            n = envelope["sender"].get("id")
            if not n:
                _raise_missing_property("$.entry[].messaging[].sender.id")

            if not "recipient" in envelope:
                _raise_missing_property("$.entry[].messaging[].recipient")

            n = envelope["recipient"].get("id")
            if not n:
                _raise_missing_property("$.entry[].messaging[].recipient.id")

            if "optin" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    _raise_missing_property("$.entry[].messaging[].timestamp")
                validate_auth_postback(envelope["optin"])
            elif "message" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    _raise_missing_property("$.entry[].messaging[].timestamp")
                validate_message_postback(envelope["message"])
            elif "delivery" in envelope:
                validate_delivery_postback(envelope["delivery"])
            elif "postback" in envelope:
                n = envelope.get("timestamp")
                if not n:
                    _raise_missing_property("$.entry[].messaging[].timestamp")
                validate_user_postback(envelope["postback"])
            else:
                _raise_bad_value("$.entry[].messaging[]",
                    "must contain one of 'optin', 'message', 'delivery' or 'postback'")

