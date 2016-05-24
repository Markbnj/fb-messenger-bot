import logging


def ping():
    """
    Called from the dialog module to ensure that the bot is loaded and callable
    """
    pass


def user_selected(source, sender_id, time, pass_through):
    """
    Called when the user selects an option from a structured set of choices,
    as in the messenger postback call for tapping on a button in a structured
    message.

    Params:
        source: name of the source application, for messenger it is the page ID
        sender_id: name or ID of the sending user, for messenger a page-scoped user ID
        time: the time of the event
        pass_through: any pass-through data attached to the selected control
    """
    logger.debug("test_bot.user_selected: source: {}, sender_id: {}, time: {}, pass_through: {}".format(
        source, sender_id, time, pass_through))


def open(source, sender_id, time, pass_through):
    """
    Called when the user opens the chat window to initiate dialog with the bot.
    For example this method handlers the Facebook "optin" authentication event
    that occurs when the user clicks the "send to messagenger" plugin button.

    Params:
        source: name of the source application, for messenger it is the page ID
        sender_id: name or ID of the sending user, for messenger a page-scoped user ID
        time: the time of the event
        pass_through: any pass-through data from the source application
    """
    logger.debug("test_bot.open: source: {}, sender_id: {}, time: {}, pass_through: {}".format(
        source, sender_id, time, pass_through))


def message_in(source, sender_id, time, message):
    """
    Called when the user sends the bot a message, which may be text, or an attachment
    containing a url point to an audio, video, or image file.

    Params:
        source: name of the source application, for messenger it is the page ID
        sender_id: name or ID of the sending user, for messenger a page-scoped user ID
        time: the time of the event
        message: the message content container

            'message' is a dictionary having the following form:
                message = {
                    "id" : "the-message-id",                # required
                    "seq" : the-message-sequence-number,    # optional
                    "text" : "the-text-message",            # optional
                    "attachments": [                        # optional
                        {
                            "type": "image/video/audio",
                            "url": "url-to-the-content"
                        }
                    ]
                }
    """
    logger.debug("test_bot.message_in: source: {}, sender_id: {}, time: {}, message: {}".format(
        source, sender_id, time, message))


def message_seen(source, message_id, message_seq, watermark, time):
    """
    Called when the delivery platform confirms delivery of a message. In the case
    of messenger this corresponds to the message having been displayed on the
    user's chat window.

    Params:
        source: name of the source application, for messenger it is the page ID
        message_id : the unique ID of the delivered message
        message_seq : the message sequence number
        watermark: high water value, all messages with earlier values have been seen
        time: the time of the event

    """
    logger.debug("test_bot.message_seen: source: {}, message_id: {}, message_seq: {}, watermark: {}, time: {}".format(
        source, message_id, message_seq, watermark, time))
