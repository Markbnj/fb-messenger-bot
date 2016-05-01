import sys
import json
import os
import unittest
import requests


"""
Get the endpoint from the file in ../config/endpoint.json that was
generated when the gateway was built.
"""
endpoint = None
with open("../config/endpoint.json", "rb") as f:
    endpoint = json.loads(f.read()).get("endpoint")

