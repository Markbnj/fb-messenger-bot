def verify(query, settings):
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

