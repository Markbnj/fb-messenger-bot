import logging


logger = logging.getLogger()


def auth(page_id, time, data, tokens):
    """
    Handles the auth callback event.
    Params:
        page_id: the page id, corresponds to $.entry[i].id in the callback data
        time: the update time, corresponds to $.entry[i].time in the callback data
        data: the auth content, $.entry[i].messaging[i] in the callback data
        tokens: contains the page token in "pageToken"
    """
    logger.debug("Auth recv: page_id: {}, time: {}, data: {}".format(page_id, time, data))

