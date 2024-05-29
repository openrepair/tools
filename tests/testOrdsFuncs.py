#!/usr/bin/env python3

import unittest
import os
import shutil
import random
import string
import polars as pl
from funcs import cfg
from funcs import ordsfuncs


class OrdsFuncsTestCase(unittest.TestCase):

    testroot = "foo"

    def setUp(self):
        cfg.ORDS_DIR = self.testroot
        cfg.DATA_DIR = self.testroot
        if os.path.exists(self.testroot):
            shutil.rmtree(self.testroot)
        if os.path.exists(self.testroot):
            print("SETUP FAILED TO REMOVE PREVIOUS TEST ROOT")
            exit()
        os.mkdir(self.testroot)

    def tearDown(self):
        if os.path.exists(self.testroot):
            shutil.rmtree(self.testroot)

    def test_csv_path_ords(self):
        filename = self._rndStr()
        result = ordsfuncs.csv_path_ords(filename)
        expect = f"{self.testroot}/{filename}.csv"
        self.assertEqual(expect, result)

    def test_csv_path_quests(self):
        filename = f"{self._rndStr()}/{self._rndStr()}"
        result = ordsfuncs.csv_path_quests(filename)
        expect = f"{self.testroot}/quests/{filename}.csv"
        self.assertEqual(expect, result)

    def test_get_categories(self):
        expect = pl.DataFrame(
            {"product_category_id": ["1", "2"], "product_category": ["foo", "bar"]},
            schema={
                "product_category_id": pl.Int64,
                "product_category": pl.String,
            },
        )
        filename = self._rndStr()
        expect.write_csv(f"{self.testroot}/{filename}.csv")
        result = ordsfuncs.get_categories(filename)
        self.assertTrue(expect.equals(result))

    def test_get_data(self):
        expect = pl.DataFrame(
            {
                "id": ["abc-123", "def-456"],
                "data_provider": ["Abc", "Def"],
                "country": ["GBR", "DEU"],
                "partner_product_category": ["foo~bar", "bar~foo"],
                "product_category": ["foo", "bar"],
                "product_category_id": ["1", "2"],
                "brand": [self._rndStr(4), self._rndStr(3)],
                "year_of_manufacture": ["2000", "2"],
                "product_age": ["0.5", "20"],
                "repair_status": ["Fixed", "Repairable"],
                "repair_barrier_if_end_of_life": ["foo", "bar"],
                "group_identifier": ["a", "b"],
                "event_date": ["2024-01-01", "2023-01-01"],
                "problem": [self._rndStr(24), self._rndStr(32)],
            },
            schema=ordsfuncs.polars_schema(),
        )
        filename = self._rndStr()
        expect.write_csv(f"{self.testroot}/{filename}.csv")
        result = ordsfuncs.get_data(filename)
        self.assertTrue(expect.equals(result))

    def test_extract_products(self):
        expect = pl.DataFrame(
            {
                "partner_product_category": [
                    "foo",
                    "bar",
                    "foo~bar",
                    "foo ~bar",
                    "foo~ bar",
                    " foo~bar",
                    "foo~bar ",
                ],
                "product": [
                    "foo",
                    "bar",
                    "bar",
                    "bar",
                    "bar",
                    "bar",
                    "bar",
                ],
            },
        )
        result = ordsfuncs.extract_products(
            expect.select(pl.col("partner_product_category"))
        )
        self.assertTrue(expect.equals(result))

    # To Do.
    def test_table_schemas(self):
        self.assertTrue(True)

    def _rndStr(self, len=6):
        return "".join(random.choice(string.ascii_letters) for _ in range(len))


if __name__ == "__main__":
    unittest.main()
