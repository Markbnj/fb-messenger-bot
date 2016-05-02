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
    access token. Should raise an exception with "403" in the error.
    message.
    """
    def test(self):
        pass


class TestVerifyMissingAccessToken(TestBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "403" in the error.
    """
    def test(self):
        pass


class TestVerifyMissingChallenge(TestBase):
    """
    Tests a call to the webhook.handler for verification with a missing
    access token. Should raise an exception with "400" in the error.
    """
    def test(self):
        pass


class TestReceiveMessage(TestBase):
    """
    Tests a call to the webhook.handler with a message event. Should
    return nothing.
    """
    def test(self):
        pass


class TestReceiveMessageBadAccessToken(TestBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a bad access token. Should return a string beginning with "403".
    """
    def test(self):
        pass


class TestReceiveMessageMissingAccessToken(TestBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a missing access token. Should return a string beginning with "403".
    """
    def test(self):
        pass


class TestReceiveMessageBadJson(TestBase):
    """
    Tests a call to the webhook.handler with a message event that has
    a missing access token. Should return a string beginning with "400".
    """
    def test(self):
        pass


if __name__ == "__main__":
    unittest.main()