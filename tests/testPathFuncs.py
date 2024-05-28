#!/usr/bin/env python3

import unittest
import os
import shutil
import random
import string
from pathlib import Path
from funcs import pathfuncs


class PathFuncsTestCase(unittest.TestCase):

    testroot = "foo"

    def setUp(self):
        if os.path.exists(self.testroot):
            shutil.rmtree(self.testroot)
        if os.path.exists(self.testroot):
            print("SETUP FAILED TO REMOVE PREVIOUS TEST ROOT")
            exit()
        os.mkdir(self.testroot)

    def tearDown(self):
        if os.path.exists(self.testroot):
            shutil.rmtree(self.testroot)

    # def test_join_path(self):
    #     expect = self.testroot + "/bar/foo"
    #     result = pathfuncs.join_path(self.testroot, "bar", "foo")
    #     self.assertEqual(expect, result)

    def test_check_path(self):
        result = pathfuncs.check_path(self.testroot)
        self.assertTrue(result)

    def test_get_path(self):
        expect = Path(self.testroot + "/bar/foo")
        path_list = [self.testroot, "bar", "foo"]
        result = pathfuncs.get_path(path_list)
        self.assertEqual(expect, result)

    def test_get_filename(self):
        expect = self._rndStr(6) + ".foo"
        result = pathfuncs.get_filename(self.testroot + "/bar/" + expect)
        self.assertEqual(expect, result)

    def test_get_filestem(self):
        expect = self._rndStr(6)
        result = pathfuncs.get_filestem(self.testroot + "/bar/" + expect + ".foo")
        self.assertEqual(expect, result)

    def test_rm_file(self):
        path = self.testroot + "/" + self._rndStr(6) + ".foo"
        result = pathfuncs.rm_file(path)
        self.assertTrue(result)
        if os.path.exists(path):
            self.assertTrue(False, "RM_FILE() PASSED BUT FAILED")

    def test_copy_file(self):
        source = self.testroot + "/" + self._rndStr(6) + ".foo"
        dest = self.testroot + "/" + self._rndStr(6) + ".bar"
        write = self._rndStr(16)
        with open(source, "w") as f:
            f.write(write)
        if os.path.exists(dest):
            os.rm_file(dest)
        result = pathfuncs.copy_file(source, dest)
        self.assertIsNone(result)
        if not os.path.exists(source):
            self.assertTrue(False, "COPY_FILE() PASSED BUT FAILED: OLD FILE NOT FOUND")
        if not os.path.exists(dest):
            self.assertTrue(
                False, "RENAME_FILE() PASSED BUT FAILED: NEW FILE NOT FOUND"
            )
        with open(dest, "r") as f:
            read = f.readline()
        self.assertEqual(write, read)

    def test_file_list(self):
        print("****test_file_list****")
        files = self._mkTree()
        files.sort()
        result = pathfuncs.file_list(self.testroot)
        self.assertEqual(3, len(result))
        result.sort()
        print(result)
        for i in range(0, 2):
            self.assertEqual(result[i][0], self.testroot)
            self.assertEqual(result[i][1], files[i])

    def _mkTree(self):
        files = [
            f"a{self._rndStr(6)}.txt",
            f"b{self._rndStr(6)}.txt",
            f"c{self._rndStr(6)}.txt",
        ]
        for file in files:
            with open(f"{self.testroot}/{file}", "w") as f:
                f.write(file)
        return files

    def _rndStr(self, len=6):
        return "".join(random.choice(string.ascii_letters) for _ in range(len))


if __name__ == "__main__":
    unittest.main()
