import json
import os

"""
Read in the the settings from config/settings.json.
"""
settings = None

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(current_dir, "settings.json"), "rb") as f:
    settings = json.loads(f.read())
