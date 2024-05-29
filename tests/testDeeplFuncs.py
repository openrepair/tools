#!/usr/bin/env python3

import unittest
from funcs import deeplfuncs


class DeeplFuncsTestCase(unittest.TestCase):

    mock = True

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_deeplWrapper(self):

        langdict = deeplfuncs.deeplWrapper.langdict
        self.assertIs(type(dict()), type(langdict))
        self.assertEqual(langdict, langdict | {"en": "en-gb"})

        languages = deeplfuncs.deeplWrapper.get_languages()
        self.assertIs(type(list()), type(languages))
        self.assertIn("en-gb", languages)

        columns = deeplfuncs.deeplWrapper.get_columns()
        self.assertIs(type(list()), type(columns))
        self.assertIn("en", columns)

        object = deeplfuncs.deeplWrapper(self.mock)
        self.assertIsInstance(object, deeplfuncs.deeplWrapper)
        self.assertIsInstance(object.translator, deeplfuncs.mockDeepLTranslator)

        text = object.translate_text("foo", "fr")
        self.assertIsInstance(text, str)


if __name__ == "__main__":
    unittest.main()
