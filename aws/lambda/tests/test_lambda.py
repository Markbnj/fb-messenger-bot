import json
import os
import sys
import unittest


# Needed so we can import the handler from the webhook mod in the
# parent directory
sys.path.insert(1, os.path.join(sys.path[0], ".."))


from webhook import handler


class TestBase(unittest.TestCase):
    """
    Provides a test event for use by the individual test cases
    """
    def setUp(self):
        # Read the settings from the lambda config, settings.json
        self.settings = None
        with open("../config/settings.json") as f:
            self.settings = json.loads(f.read())

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
                "access_token": "",
                "hub.verify_token": "",
                "hub.challenge": ""
            }
        }
        """
        )

        # needed for all test cases
        self.test_event['accessToken'] = self.settings.get("accessToken")
        self.test_event['query']['access_token'] = self.settings.get("accessToken")


class TestVerifyBase(TestBase):
    def setUp(self):
        super(TestVerifyBase, self).setUp()

        # specialize the test event for the verification calls
        self.test_event['method'] = "GET"
        self.test_event['query']['hub.verify_token'] = self.settings.get("verifyToken")
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
        event = self.test_event.copy()
        event["accessToken"] = "yadayada"
        self.assertRaises(Exception, handler, event, None)


class TestVerifyMissingAccessToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        event = self.test_event.copy()
        del event["accessToken"]
        self.assertRaises(Exception, handler, event, None)


class TestVerifyBadVerificationToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a bad
    verification token. Should raise an exception with "403" in the error.
    """
    def test(self):
        event = self.test_event.copy()
        event["query"]["hub.verify_token"] = "bad-verify-token"
        self.assertRaises(Exception, handler, event, None)


class TestVerifyMissingVerificationToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    verification token. Should raise an exception with "400" in the error.
    """
    def test(self):
        event = self.test_event.copy()
        del event["query"]["hub.verify_token"]
        self.assertRaises(Exception, handler, event, None)


class TestVerifyMissingChallenge(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        event = self.test_event.copy()
        del event["query"]["hub.challenge"]
        self.assertRaises(Exception, handler, event, None)


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

    def make_entry(self, page_id, time, messages=[]):
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
        entry["messaging"] = messages
        return entry


class TestAuthPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an auth event. Should
    return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["optin"] = {"ref": "SOME POSTBACK DATA HERE"}
        handler(event, None)


class TestReceiveMessagePostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message event. Should
    return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "This is a test message."
        handler(event, None)


class TestReceiveMultipleEntries(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing multiple
    entries, each with a single message. Should return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "Multi-entry test message 1."
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992760478))
        event["body"]["entry"][1]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        event["body"]["entry"][1]["messaging"][0]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        event["body"]["entry"][1]["messaging"][0]["message"]["text"] = "Multi-entry test message 2."
        handler(event, None)


class TestReceiveMultipleMessages(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing a single
    entry with multiple messages. Should return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        event["body"]["entry"][0]["messaging"][0]["message"]["text"] = "Multi-message test message 1."
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        event["body"]["entry"][0]["messaging"][1]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        event["body"]["entry"][0]["messaging"][1]["message"]["text"] = "Multi-message test message 2."
        handler(event, None)


class TestMessageDeliveredPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message delivered event.
    Should return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["delivery"] = {"mids":["mid.1461992777559:e8027b338d2b553b73"], "watermark":1234567890, "seq":75}
        handler(event, None)


class TestUserPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event.
    Should return nothing.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        event["body"]["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        event["body"]["entry"][0]["messaging"][0]["postback"] = {"payload": "SOME POSTBACK DATA HERE"}
        handler(event, None)


class TestPostbackMissingEntry(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing an entry. Should raise an exception with "400" in the msg.
    """
    def test(self):
        event = self.test_event.copy()
        del event["body"]["entry"]
        self.assertRaises(Exception, handler, event, None)


class TestPostbackMissingMessage(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing a message. Should raise an exception with "400" in the msg.
    """
    def test(self):
        event = self.test_event.copy()
        event["body"]["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        del event["body"]["entry"][0]["messaging"]
        self.assertRaises(Exception, handler, event, None)


if __name__ == "__main__":
    unittest.main()