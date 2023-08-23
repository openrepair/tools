#!/usr/bin/env python3

import unittest
from wkdfuncs import wikidataRestApi, wikidataSparqlAPI


class wkdFuncsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_class_sparql_api(self):
        obj = wikidataSparqlAPI()
        self.assertIsInstance(obj, wikidataSparqlAPI, 'Incorrect class')
        headers = obj.get_headers(oauth=False)
        self.assertEqual(2, len(headers), 'Wrong number of headers')
        headers = obj.get_headers(oauth=True)
        self.assertEqual(3, len(headers), 'Wrong number of headers')

    def test_class_rest_api(self):
        obj = wikidataRestApi()
        self.assertIsInstance(obj, wikidataRestApi, 'Incorrect class')
        headers = obj.get_headers(oauth=False)
        self.assertEqual(2, len(headers), 'Wrong number of headers')
        headers = obj.get_headers(oauth=True)
        self.assertEqual(3, len(headers), 'Wrong number of headers')


if __name__ == '__main__':
    unittest.main()
