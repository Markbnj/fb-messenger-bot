import json
import logging
import os
import sys
import unittest


"""
Add the parent directory to the path so that we can import the
webhook and tests can access the entrypoint.
"""
parent = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent)


from webhook import handler
from config import settings


"""
Adds a console handler to the logger to be used during test runs.
"""
log_level = eval("logging.{}".format(settings["logLevel"]))
logger = logging.getLogger()
logger.setLevel(log_level)
if not len([handler for handler in logger.handlers if isinstance(handler,logging.StreamHandler)]):
    sh = logging.StreamHandler()
    sh.setLevel(log_level)
    logger.addHandler(sh)


class TestBase(unittest.TestCase):
    """
    Provides a test event for use by the individual test cases
    """
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        # set up the test event, derived classes will fill out the
        # rest for their specific test cases
        self.test_event = json.loads("""
        {
            "accessToken": "",
            "method": "",
            "body": {},
            "headers": {},
            "params": {},
            "query": {
                "access_token": ""
            }
        }
        """
        )

        # needed for all test cases
        self.test_event['accessToken'] = settings.get("accessToken")
        self.test_event['query']['access_token'] = settings.get("accessToken")


class TestVerifyBase(TestBase):
    def setUp(self):
        super(TestVerifyBase, self).setUp()

        # specialize the test event for the verification calls
        self.test_event['method'] = "GET"
        self.test_event['query']['hub.verify_token'] = settings.get("verifyToken")
        self.test_event['query']['hub.challenge'] = "abcdefgh"


class TestVerify(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with good data.
    """
    def test(self):
        result = handler(self.test_event, None)
        self.assertEqual(result, self.test_event["query"]["hub.challenge"])


class TestVerifyBadAccessToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with an incorrect
    access token. Should raise an exception with "403" in the error.
    message.
    """
    def test(self):
        self.test_event["accessToken"] = "yadayada"
        self.assertRaises(Exception, handler, self.test_event, None)


class TestVerifyMissingAccessToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        del self.test_event["accessToken"]
        self.assertRaises(Exception, handler, self.test_event, None)


class TestVerifyBadVerificationToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a bad
    verification token. Should raise an exception with "403" in the error.
    """
    def test(self):
        self.test_event["query"]["hub.verify_token"] = "bad-verify-token"
        self.assertRaises(Exception, handler, self.test_event, None)


class TestVerifyMissingVerificationToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    verification token. Should raise an exception with "400" in the error.
    """
    def test(self):
        del self.test_event["query"]["hub.verify_token"]
        self.assertRaises(Exception, handler, self.test_event, None)


class TestVerifyMissingChallenge(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        del self.test_event["query"]["hub.challenge"]
        self.assertRaises(Exception, handler, self.test_event, None)


class TestPostbacksBase(TestBase):
    def setUp(self):
        super(TestPostbacksBase, self).setUp()
        self.test_event['method'] = "POST"
        self.test_event['body'] = json.loads("""
            {
                "object": "page",
                "entry": []
            }
        """)

    def make_message(self, sender_id, rec_id, timestamp):
        """
        Build and return a single object for the "messaging" array of
        the test event. See:

        https://developers.facebook.com/docs/messenger-platform/webhook-reference
        """
        message = json.loads("""
            {
                "sender":{
                    "id":""
                },
                "recipient":{
                    "id":""
                },
                "timestamp":0
            }
        """)
        message["sender"]["id"] = sender_id
        message["recipient"]["id"] = rec_id
        message["timestamp"] = timestamp
        return message

    def make_entry(self, page_id, time):
        """
        Build and return a single object for the "entry" array of the
        test event. See:

        https://developers.facebook.com/docs/messenger-platform/webhook-reference
        """
        entry = json.loads("""
            {
                "id":"",
                "time":"",
                "messaging":[]
            }
        """)
        entry["id"] = page_id
        entry["time"] = time
        return entry


class TestAuthPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an auth event. Should
    return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["optin"] = {"ref": "PASS_THROUGH_PARAM"}
        handler(self.test_event, None)


class TestReceiveMessagePostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message event. Should
    return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        self.test_event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "This is a test message."
        handler(self.test_event, None)


class TestReceiveMultipleEntries(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing multiple
    entries, each with a single message. Should return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        self.test_event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "Multi-entry test message 1."
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992760478))
        self.test_event["body"]["entry"][1]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        self.test_event["body"]["entry"][1]["messaging"][0]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        self.test_event["body"]["entry"][1]["messaging"][0]["message"]["text"] = "Multi-entry test message 2."
        handler(self.test_event, None)


class TestReceiveMultipleMessages(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing a single
    entry with multiple messages. Should return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        self.test_event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "Multi-message test message 1."
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        self.test_event["body"]["entry"][0]["messaging"][1]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        self.test_event["body"]["entry"][0]["messaging"][1]["message"]["text"] = "Multi-message test message 2."
        handler(self.test_event, None)


class TestMessageDeliveredPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message delivered event.
    Should return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["delivery"] = {"mids":["mid.1461992777559:e8027b338d2b553b73"], "watermark":1234567890, "seq":75}
        handler(self.test_event, None)


class TestUserPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event.
    Should return nothing.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        self.test_event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        self.test_event["body"]["entry"][0]["messaging"][0]["postback"] = {"payload": "SOME POSTBACK DATA HERE"}
        handler(self.test_event, None)


class TestPostbackMissingEntry(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing an entry. Should raise an exception with "400" in the msg.
    """
    def test(self):
        del self.test_event["body"]["entry"]
        self.assertRaises(Exception, handler, self.test_event, None)


class TestPostbackMissingMessage(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing a message. Should raise an exception with "400" in the msg.
    """
    def test(self):
        self.test_event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        del self.test_event["body"]["entry"][0]["messaging"]
        self.assertRaises(Exception, handler, self.test_event, None)


if __name__ == "__main__":
    unittest.main()