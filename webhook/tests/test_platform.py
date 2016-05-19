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


from config import settings

# just importing this to set up the library paths
import webhook

from platform import messages, profiles, validation


"""
Adds a console logger to be used during test runs.
"""
log_level = eval("logging.{}".format(settings["logLevel"]))
logger = logging.getLogger()
logger.setLevel(log_level)
if not len([handler for handler in logger.handlers if isinstance(handler,logging.StreamHandler)]):
    sh = logging.StreamHandler()
    sh.setLevel(log_level)
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


class TestValidationBase(unittest.TestCase):
    def assertRaisesWithMsg(self, exc_type, test_func, content, *args, **kwargs):
        """
        Calls the callable in test_func, passing args and kwargs, and raises
        assertion error if the called function does not raise an exception of
        type exc_type. If content is not none or empty then it raises an assertion
        error if the raised exception doesn't contain content in its message.
        """
        try:
            test_func(*args, **kwargs)
        except exc_type as e:
            logger.debug("{} raised: {}".format(test_func, e))
            if content and not content in str(e):
                raise AssertionError("'{}' not found in '{}'".format(content, e))
        except Exception as e:
            logger.debug("Unexpected: {}".format(e))
        else:
            raise AssertionError("{} did not raise an exception of type {}".format(test_func, exc_type))


class TestValidationTextMessage(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
        validation.validate_message(self.test_msg)


class TestValidationTextMessageWithPhone(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "phone_number": "9085551212"
            },
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        validation.validate_message(self.test_msg)


class TestValidationNoRecipient(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.recipient",
            self.test_msg)


class TestValidationEmptyRecipient(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
            },
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.recipient must contain either 'id' or 'phone_number'",
            self.test_msg)


class TestValidationEmptyRecipientId(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "id": ""
            },
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.recipient.id cannot be 'None' or empty",
            self.test_msg)


class TestValidationEmptyRecipientPhone(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "phone_number": ""
            },
            "message": {
                "text": "This is a basic test message."
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.recipient.phone_number cannot be 'None' or empty",
            self.test_msg)


class TestValidationTextMessageEmptyMessage(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message cannot be 'None' or empty",
            self.test_msg)


class TestValidationTextMessageEmptyText(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "text":""
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.text cannot be 'None' or empty",
            self.test_msg)


class TestValidationButtonMessage(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
        validation.validate_message(self.test_msg)


class TestValidationButtonMessageMissingTitle(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
        {
            "recipient": {
                "id": "1789953497899630"
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.message.attachment.payload.text",
            self.test_msg)


class TestValidationButtonMessageMissingButtonType(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.message.attachment.payload.button[].type",
            self.test_msg)


class TestValidationButtonMessageEmptyButtonType(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "type": "",
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.attachment.payload.button[].type must contain either 'web_url' or 'postback'",
            self.test_msg)


class TestValidationButtonMessageMissingButtonTitle(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "url": "http://some.where/but_not_here"
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.message.attachment.payload.button[].title",
            self.test_msg)


class TestValidationButtonMessageEmptyButtonTitle(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "title": ""
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.attachment.payload.button[].title cannot be 'None' or empty",
            self.test_msg)


class TestValidationButtonMessageMissingButtonUrl(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.message.attachment.payload.button[].url",
            self.test_msg)


class TestValidationButtonMessageEmptyButtonUrl(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "url": "",
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
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.attachment.payload.button[].url cannot be 'None' or empty",
            self.test_msg)


class TestValidationButtonMessageMissingButtonPayload(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "title": "This is a test title"
                            }
                        ]
                    }
                }
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "missing property: $.message.attachment.payload.button[].payload",
            self.test_msg)


class TestValidationButtonMessageEmptyButtonPayload(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
                                "payload": ""
                            }
                        ]
                    }
                }
            }
        }
        """)

    def test(self):
        self.assertRaisesWithMsg(
            Exception,
            validation.validate_message,
            "$.message.attachment.payload.button[].payload cannot be 'None' or empty",
            self.test_msg)


class TestValidationGenericMessage(TestValidationBase):
    def setUp(self):
        logger.info("\n\n>>>>TEST CASE: {}".format(self.id()))

        self.test_msg = json.loads("""
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
        validation.validate_message(self.test_msg)


if __name__ == "__main__":
    unittest.main()