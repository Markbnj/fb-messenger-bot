from config import settings
import importlib
import logging


logger = logging.getLogger()


active_bot = "dialog.bots.{}".format(settings["activeBot"], fromlist=["*"])
try:
    bot = importlib.import_module(active_bot)
    bot.ping()
except Exception as e:
    logger.error("Failed to load bot: {}, error: {}".format(active_bot, e))
    raise


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
    logger.debug("dialog.user_selected: source: {}, sender_id: {}, time: {}, pass_through: {}".format(
        source, sender_id, time, pass_through))
    bot.user_selected(source, sender_id, time, pass_through)


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
    logger.debug("dialog.open: source: {}, sender_id: {}, time: {}, pass_through: {}".format(
        source, sender_id, time, pass_through))
    bot.open(source, sender_id, time, pass_through)


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
    logger.debug("dialog.message_in: source: {}, sender_id: {}, time: {}, message: {}".format(
        source, sender_id, time, message))
    bot.message_in(source, sender_id, time, message)


def message_seen(source, message_ids, message_seq, watermark, time):
    """
    Called when the delivery platform confirms delivery of a message. In the case
    of messenger this corresponds to the message having been displayed on the
    user's chat window.

    Params:
        source: name of the source application, for messenger it is the page ID
        message_id : the list of the unique IDs of the delivered messages
        message_seq : the message sequence number
        watermark: high water value, all messages with earlier values have been seen
        time: the time of the event

    """
    logger.debug("dialog.message_seen: source: {}, message_ids: {}, message_seq: {}, watermark: {}, time: {}".format(
        source, message_ids, message_seq, watermark, time))
    bot.message_seen(source, message_ids, message_seq, watermark, time)