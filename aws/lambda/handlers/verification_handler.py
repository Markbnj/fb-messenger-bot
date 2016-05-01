import logging


logger = logging.getLogger()


def verify(event, context, tokens):
    my_verify_token = tokens.get("verifyToken")
    verify_token = event['query'].get("hub.verify_token")
    challenge = event['query'].get("hub.challenge")
    if verify_token == my_verify_token:
        if not challenge:
            return "400 Bad Request; missing challenge"
        else:
            return challenge
    else:
        return "403 Forbidden; verification token mismatch"

