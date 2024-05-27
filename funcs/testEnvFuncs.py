#!/usr/bin/env python3

import unittest
import os
import envfuncs


class EnvFuncsTestCase(unittest.TestCase):

    envvar_name = "FUNCS_TEST"
    envvar_val = "foobar"

    def setUp(self):
        os.environ[self.envvar_name] = self.envvar_val

    def tearDown(self):
        os.environ.pop(self.envvar_name)

    def test_get_var(self):
        self.assertEqual(
            self.envvar_val, envfuncs.get_var(self.envvar_name), "wrong key value"
        )


if __name__ == "__main__":
    unittest.main()
