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
        # Read the tokens from the lambda config, tokens.json
        self.tokens = None
        with open("../config/tokens.json") as f:
            self.tokens = json.loads(f.read())

        # set up the test event
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
        self.test_event['accessToken'] = self.tokens.get("accessToken")
        self.test_event['query']['access_token'] = self.tokens.get("accessToken")


class TestVerifyBase(TestBase):
    def setUp(self):
        super(TestVerifyBase, self).setUp()
        self.test_event['method'] = "GET"
        self.test_event['query']['hub.verify_token'] = self.tokens.get("verifyToken")
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


# receive message with missing entry
# receive message with missing message
# missing data in the message

class TestAuthCallback(TestPostbacksBase):
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


class TestReceiveMessage(TestPostbacksBase):
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


class TestMessageDelivered(TestPostbacksBase):
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


if __name__ == "__main__":
    unittest.main()