import json
import logging
import os
import sys
import unittest


"""
Add the parent directory to the path so that we can import the
platform modules.
"""
parent = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent)


from platform import messages, profiles


"""
Adds a console logger to be used during test runs.
"""
logger = logging.getLogger()
if not len([handler for handler in logger.handlers if isinstance(handler,logging.StreamHandler)]):
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)


class TestMakeTextMessage(unittest.TestCase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.expected = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        """
        Tests messages.make_message by checking that the returned dict matches
        self.expected, defined above.
        """
        message = messages.make_message("1789953497899630", "text_message", {"message_text": "This is a basic test message."})
        self.assertEqual(message, self.expected)


class TestMakeImageMessage(unittest.TestCase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.expected = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": "http://some.where/but_not_here.png"
                    }
                }
            }
        }
        """)

    def test(self):
        """
        Tests messages.make_message by checking that the returned dict matches
        self.expected, defined above.
        """
        message = messages.make_message("1789953497899630", "image_message", {"image_url": "http://some.where/but_not_here.png"})
        self.assertEqual(message, self.expected)


class TestMakeButtonMessage(unittest.TestCase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.expected = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": "Here lies a button",
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": "http://some.where/but_not_here",
                                "title": "This is a test title"
                            },
                            {
                                "type": "postback",
                                "title": "This is a test title",
                                "payload": "This is a test payload"
                            }
                        ]
                    }
                }
            }
        }
        """)

    def test(self):
        """
        Tests messages.make_message by checking that the returned dict matches
        self.expected, defined above.
        """
        buttons = []
        buttons.append(messages.make_url_button("This is a test title", "http://some.where/but_not_here"))
        buttons.append(messages.make_postback_button("This is a test title", "This is a test payload"))
        message = messages.make_message("1789953497899630", "button_message", {"prompt_text": "Here lies a button"}, buttons)
        self.assertEqual(message, self.expected)


class TestMakeGenericMessage(unittest.TestCase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.expected = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "This is a test title",
                                "image_url": "http://some.where/but_not_here.png",
                                "item_url": "http://some.where/but_not_here",
                                "subtitle": "This is a test subtitle",
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url": "http://some.where/but_not_here",
                                        "title": "This is a test title"
                                    },
                                    {
                                        "type": "postback",
                                        "title": "This is a test title",
                                        "payload": "This is a test payload"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
        """)

    def test(self):
        """
        Tests messages.make_message by checking that the returned dict matches
        self.expected, defined above.
        """
        message = messages.make_message("1789953497899630", "generic_message")
        buttons = []
        buttons.append(messages.make_url_button("This is a test title", "http://some.where/but_not_here"))
        buttons.append(messages.make_postback_button("This is a test title", "This is a test payload"))
        messages.add_message_element(
            message,
            "This is a test title",
            "This is a test subtitle",
            "http://some.where/but_not_here.png",
            "http://some.where/but_not_here",
            buttons)
        self.assertEqual(message, self.expected)
