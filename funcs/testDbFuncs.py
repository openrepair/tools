#!/usr/bin/env python3

import unittest
import os
import csv
import dbfuncs


class DbFuncsTestCase(unittest.TestCase):

    tablename = "testdbfuncs"

    def setUp(self):
        pass

    def tearDown(self):
        # return
        sql = """DROP TABLE IF EXISTS `{}`""".format(self.tablename)
        dbfuncs.execute(sql)
        file = "./out/{}.csv".format(self.tablename)
        if os.path.exists(file):
            os.remove(file)

    def test_dbvars(self):
        expect = {
            "host": "{ORDS_DB_HOST}".format(**os.environ),
            "database": "{ORDS_DB_DATABASE}".format(**os.environ),
            "collation": "{ORDS_DB_COLLATION}".format(**os.environ),
            "user": "{ORDS_DB_USER}".format(**os.environ),
            "pwd": "{ORDS_DB_PWD}".format(**os.environ),
        }
        result = dbfuncs.dbvars
        self.assertEqual(expect, result, "Wrong dbvars")

    def test_dbconnect(self):
        result = dbfuncs.mysql_con()
        self.assertTrue(result.is_connected(), "Connection failed")
        if result.is_connected():
            result.close()

    def test_dbfuncs(self):
        sql = """
            CREATE TABLE `{0}` (
                `id` int NOT NULL AUTO_INCREMENT,
                `title` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                `desc` text COLLATE utf8mb4_unicode_ci,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            ALTER TABLE `{0}` ADD KEY `title` (`title`);
            ALTER TABLE `{0}` ADD FULLTEXT KEY `desc` (`desc`);
            """.format(
            self.tablename
        )
        result = dbfuncs.execute(sql)

        sql = """INSERT INTO `{}` (`title`, `desc`) VALUES ('Title 1', 'desc one')""".format(
            self.tablename
        )
        result = dbfuncs.execute(sql)
        self.assertEqual(1, result, "Wrong number of rows")
        sql = """SELECT * FROM `{}`""".format(self.tablename)
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(1, len(result), "Wrong number of records")
        sql = """SELECT * FROM `{}` WHERE `title`='Title 1'""".format(self.tablename)
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(1, len(result), "Record not found")

        sql = """DELETE FROM `{}` WHERE id=1""".format(self.tablename)
        result = dbfuncs.execute(sql)
        self.assertEqual(1, result, "Wrong number of rows")
        sql = """SELECT * FROM `{}`""".format(self.tablename)
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(0, len(result), "Wrong number of records")

        vals = [
            ("Title Two", "desc two"),
            ("Title Three", "desc three"),
            ("Title Four", "desc four"),
        ]
        sql = """INSERT INTO `{}` (`title`, `desc`) VALUES (%s, %s)""".format(
            self.tablename
        )
        result = dbfuncs.executemany(sql, vals)
        self.assertEqual(3, result, "Wrong number of rows")
        sql = """SELECT * FROM `{}`""".format(self.tablename)
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(3, len(result), "Wrong number of records")

        sql = """UPDATE `{}` SET `title`='Title 2' WHERE id=2""".format(self.tablename)
        result = dbfuncs.execute(sql)
        self.assertEqual(1, result, "Wrong number of rows")
        sql = """SELECT * FROM `{}` WHERE `title`='Title 2'""".format(self.tablename)
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(1, len(result), "Wrong number of records")

        vals = [("Title 3", 3), ("Title 4", 4)]
        sql = """UPDATE `{}` SET `title`=%s WHERE id=%s""".format(self.tablename)
        result = dbfuncs.executemany(sql, vals)
        self.assertEqual(2, result, "Wrong number of rows")
        sql = """SELECT * FROM `{}` WHERE `title` IN ('Title 3','Title 4')""".format(
            self.tablename
        )
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(2, len(result), "Wrong number of records")

        dbfuncs.dump_table_to_csv(self.tablename, "./out")
        file = "./out/{}.csv".format(self.tablename)
        self.assertTrue(os.path.exists(file), "File not found: {}".format(file))
        cols = []
        rows = []
        with open(file, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            cols = next(csvreader)
            self.assertEqual(3, len(cols), "Wrong number of columns")
            for row in csvreader:
                rows.append(row)
            self.assertEqual(4, csvreader.line_num, "Wrong number of lines")

        expect = ["id", "title", "desc"]
        self.assertEqual(expect, cols, "Wrong column headings")

        vals = [(3, "Title Three", "test 3"), (4, "Title Four", "test 4")]
        sql = """REPLACE INTO `{}` (`{}`) VALUES ({})""".format(
            self.tablename, "`,`".join(cols), ",".join(["%s"] * len(cols))
        )
        print(sql)
        result = dbfuncs.executemany(sql, vals)
        print(result)
        sql = """SELECT * FROM `{}` WHERE `id` IN (3,4) AND `title` IN ('Title Three','Title Four')""".format(
            self.tablename
        )
        result = dbfuncs.query_fetchall(sql)
        self.assertEqual(2, len(result), "Wrong number of records")


if __name__ == "__main__":
    unittest.main()
