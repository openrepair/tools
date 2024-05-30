#!/usr/bin/env python3

import unittest
import os
import random
import string
from funcs import cfg


class CfgTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_var(self):

        key = "GET_VAR_TEST"
        val = "foobar"
        os.environ[key] = val
        self.assertEqual(val, cfg.get_envvar(key))
        os.environ.pop(key)
        with self.assertRaises(KeyError):
            cfg.get_envvar(key)

    def test_get_dbvars(self):

        key = "MYPY_DB_FOO"
        dict = {
            "host": "foo",
            "database": "bar",
            "user": "foo",
            "pwd": "bar",
            "collation": "foobar",
        }
        val = f"{dict}"
        os.environ[key] = val
        self.assertEqual(dict, cfg.get_dbvars(key))

        dict = {"foo": "bar"}
        val = f"{dict}"
        os.environ[key] = val
        with self.assertRaises(KeyError):
            cfg.get_dbvars(key)

        val = "foobar"
        os.environ[key] = val
        with self.assertRaises(ValueError):
            cfg.get_dbvars(key)

    def test_init_logger(self):

        logger = cfg.init_logger(__file__)
        self.assertIsNotNone(logger)
        path = f"{cfg.LOG_DIR}/testCfg.log"
        self.assertTrue(os.path.exists(path))
        logger.debug(logger.handlers)

        logdir = cfg.LOG_DIR
        logtmp = "".join(random.choice(string.ascii_letters) for _ in range(3))

        cfg.LOG_DIR = logtmp
        cfg.init_dirs()
        logger = cfg.init_logger(logtmp)
        self.assertIsNotNone(logger)
        path = f"{logtmp}/{logtmp}.log"
        self.assertTrue(os.path.exists(path))
        os.remove(path)
        os.rmdir(logtmp)
        cfg.LOG_DIR = logdir


if __name__ == "__main__":
    unittest.main()
