import sys
import json
import os
import unittest
import requests


class TestBase(unittest.TestCase):
    """
    Provides a common setup for the individual test cases
    """
    def setUp(self):
        # Get the endpoint url from the endpoint.json file in ../config
        self.endpoint = None
        with open("../config/endpoint.json", "rb") as f:
            self.endpoint = json.loads(f.read()).get("endpoint")

        # Read the tokens from the lambda config, tokens.json
        self.tokens = None
        with open("../../lambda/config/tokens.json") as f:
            self.tokens = json.loads(f.read())

    def make_url(self, access_token, verify_token=None, challenge=None):
        url = "{}?access_token={}".format(self.endpoint, access_token)
        if verify_token:
            url = "{}&hub.verify_token={}&hub.challenge={}".format(url, verify_token, challenge)
        return url


class TestVerify(TestBase):
    """
    Tests a call to the webhook for verification with good data.
    """
    def test(self):
        challenge = "abcdefgh"
        url = self.make_url(self.tokens.get("accessToken"), self.tokens.get("verifyToken"), challenge)
        response = requests.get(url)
        self.assertEqual(response.text, challenge)


class TestVerifyBadAccessToken(TestBase):
    """
    Tests a call to the webhook.handler for verification with an incorrect
    access token. Should return http 403 and "403" in the error.
    message.
    """
    def test(self):
        challenge = "abcdefgh"
        url = self.make_url("bad-access-token", self.tokens.get("verifyToken"), challenge)
        response = requests.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.text.startswith("403"))


class TestVerifyMissingAccessToken(TestBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should return http 400 and "400" in the error.
    """
    def test(self):
        challenge = "abcdefgh"
        url = self.make_url("", self.tokens.get("verifyToken"), challenge)
        response = requests.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.text.startswith("400"))


class TestVerifyBadVerificationToken(TestBase):
    """
    Tests a call to the webhook.handler for verification with a bad
    verification token. Should return http 403 with "403" in the error.
    """
    def test(self):
        challenge = "abcdefgh"
        url = self.make_url(self.tokens.get("accessToken"), "bad-verify-token", challenge)
        response = requests.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.text.startswith("403"))


class TestVerifyMissingVerificationToken(TestBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    verification token. Should return http 400 with "400" in the error.
    """
    def test(self):
        challenge = "abcdefgh"
        url = self.make_url(self.tokens.get("accessToken"), "", challenge)
        response = requests.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.text.startswith("400"))


class TestVerifyMissingChallenge(TestBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        challenge = ""
        url = self.make_url(self.tokens.get("accessToken"), self.tokens.get("verifyToken"), challenge)
        response = requests.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.text.startswith("400"))


class TestPostbacksBase(TestBase):
    def setUp(self):
        super(TestPostbacksBase, self).setUp()
        self.test_data = json.loads("""
            {
                "object": "page",
                "entry": []
            }
        """)

    def make_message(self, sender_id, rec_id, timestamp):
        """
        Build and return a single object for the "messaging" array of
        the test data. See:

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
        test data. See:

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
    return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["optin"] = {"ref": "SOME POSTBACK DATA HERE"}
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestReceiveMessagePostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message event. Should
    return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        data["entry"][0]["messaging"][0]["message"]["text"] = "This is a test message."
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestReceiveMultipleEntries(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing multiple
    entries, each with a single message. Should return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        data["entry"][0]["messaging"][0]["message"]["text"] = "Multi-entry test message 1."
        data["entry"].append(self.make_entry(1789953497899630, 1461992760478))
        data["entry"][1]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        data["entry"][1]["messaging"][0]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        data["entry"][1]["messaging"][0]["message"]["text"] = "Multi-entry test message 2."
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestReceiveMultipleMessages(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with an event containing a single
    entry with multiple messages. Should return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["message"] = {"mid":"mid.1461992777559:e8027b338d2b553b73", "seq":75}
        data["entry"][0]["messaging"][0]["message"]["text"] = "Multi-message test message 1."
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992761577))
        data["entry"][0]["messaging"][1]["message"] = {"mid":"mid.1461992761577:e8028b336d2b443c72", "seq":76}
        data["entry"][0]["messaging"][1]["message"]["text"] = "Multi-message test message 2."
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestMessageDeliveredPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a message delivered event.
    Should return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["delivery"] = {"mids":["mid.1461992777559:e8027b338d2b553b73"], "watermark":1234567890, "seq":75}
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestUserPostback(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event.
    Should return http 200.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        data["entry"][0]["messaging"].append(self.make_message(983440235096641, 1789953497899630, 1461992777559))
        data["entry"][0]["messaging"][0]["postback"] = {"payload": "SOME POSTBACK DATA HERE"}
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)


class TestPostbackMissingEntry(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing an entry. Should return http 400 with "400" in the msg.
    """
    def test(self):
        data = self.test_data.copy()
        del data["entry"]
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.text.startswith("400"))


class TestPostbackMissingMessage(TestPostbacksBase):
    """
    Tests a call to the webhook.handler with a user postback event that
    is missing a message. Should return http 400 with "400" in the msg.
    """
    def test(self):
        data = self.test_data.copy()
        data["entry"].append(self.make_entry(1789953497899630, 1461992750443))
        del data["entry"][0]["messaging"]
        url = self.make_url(self.tokens.get("accessToken"))
        response = requests.post(url, data=json.dumps(data))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.text.startswith("400"))


if __name__ == "__main__":
    unittest.main()