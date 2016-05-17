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
