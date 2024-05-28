#!/usr/bin/env python3

import unittest
from funcs import datefuncs


class DateFuncsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_curr_date(self):

        from datetime import datetime

        format = "%Y%m%d"
        expect = str(datetime.now().strftime(format))
        result = datefuncs.format_curr_date()
        print(result)
        self.assertEqual(expect, result)

        format = "%Y-%m-%d"
        expect = str(datetime.now().strftime(format))
        result = datefuncs.format_curr_date(format)
        print(result)
        self.assertEqual(expect, result)

    def test_format_curr_datetime(self):

        from datetime import datetime

        format = "%Y%m%d%H%M%S"
        expect = str(datetime.now().strftime(format))
        result = datefuncs.format_curr_datetime()
        print(result)
        self.assertEqual(expect, result)

        format = "%Y-%m-%d %H:%M"
        expect = str(datetime.now().strftime(format))
        result = datefuncs.format_curr_datetime(format)
        print(result)
        self.assertEqual(expect, result)


if __name__ == "__main__":
    unittest.main()
