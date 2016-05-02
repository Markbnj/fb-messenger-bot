import json
import os
import sys
import unittest


# Needed so we can import the handler from the webhook mod in the
# parent directory
sys.path.insert(1, os.path.join(sys.path[0], ".."))


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
        from webhook import handler
        result = handler(self.test_event, None)
        self.assertEqual(result, self.test_event["query"]["hub.challenge"])


class TestVerifyBadAccessToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with an incorrect
    access token. Should raise an exception with "403" in the error.
    message.
    """
    def test(self):
        from webhook import handler
        event = self.test_event.copy()
        event["accessToken"] = "yadayada"
        self.assertRaises(Exception, handler, event, None)


class TestVerifyMissingAccessToken(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "403" in the error.
    """
    def test(self):
        from webhook import handler
        event = self.test_event.copy()
        del event["accessToken"]
        self.assertRaises(Exception, handler, event, None)


class TestVerifyMissingChallenge(TestVerifyBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        from webhook import handler
        event = self.test_event.copy()
        del event["query"]["hub.challenge"]
        self.assertRaises(Exception, handler, event, None)


class TestReceiveMessageBase(TestBase):
    def setUp(self):
        super(TestReceiveMessageBase, self).setUp()
        self.test_event['method'] = "POST"
        # TBD any other message properties here


class TestReceiveMessage(TestReceiveMessageBase):
    """
    Tests a call to the webhook.handler with a message event. Should
    return nothing.
    """
    def test(self):
        pass


class TestReceiveMessageBadAccessToken(TestReceiveMessageBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a bad access token. Should return a string beginning with "403".
    """
    def test(self):
        pass


class TestReceiveMessageMissingAccessToken(TestReceiveMessageBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a missing access token. Should return a string beginning with "403".
    """
    def test(self):
        pass


class TestReceiveMessageBadJson(TestReceiveMessageBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a missing access token. Should return a string beginning with "400".
    """
    def test(self):
        pass


if __name__ == "__main__":
    unittest.main()