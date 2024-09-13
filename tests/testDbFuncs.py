#!/usr/bin/env python3

import unittest
from funcs import cfg
from funcs import dbfuncs

dbfuncs.dbvars = cfg.get_dbvars("ORDS_DB_TEST")

class DbFuncsTestCase(unittest.TestCase):

    tablename = "testdbfuncs"

    def setUp(self):
        pass

    def tearDown(self):
        dbfuncs.mysql_execute(f"DROP TABLE IF EXISTS `{self.tablename}`")

    def test_mysql_connection(self):
        result = dbfuncs.mysql_connection()
        self.assertTrue(result.is_connected())
        if result.is_connected():
            result.close()

    def test_mysql_execute(self):
        result = dbfuncs.mysql_execute(
            f"DROP TABLE IF EXISTS `{self.tablename}`", rowcount=False
        )
        self.assertTrue(result)

    def test_mysql_create_table(self):
        result = dbfuncs.mysql_create_table(self._table_stru())
        self.assertTrue(result)

    def test_mysql_show_create_table(self):
        dbfuncs.mysql_create_table(self._table_stru())
        result = dbfuncs.mysql_show_create_table(self.tablename)
        self.assertTrue(result.startswith("CREATE TABLE `testdbfuncs`"))
        self.assertIs(type(result), type("str"))

    def test_mysql_executemulti(self):
        dbfuncs.mysql_create_table(self._table_stru())
        sql = [
            f"INSERT INTO `{self.tablename}` (`title`, `desc`) VALUES ('Title Two', 'desc two')",
            f"INSERT INTO `{self.tablename}` (`title`, `desc`) VALUES ('Title Three', 'desc three')",
            f"INSERT INTO `{self.tablename}` (`title`, `desc`) VALUES ('Title Four', 'desc four')",
        ]
        sql = ";\n".join(sql)
        result = dbfuncs.mysql_execute_multi(sql)
        self.assertEqual(3, len(result))

    def test_mysql_executemany(self):
        dbfuncs.mysql_create_table(self._table_stru())
        vals = [
            ("Title Two", "desc two"),
            ("Title Three", "desc three"),
            ("Title Four", "desc four"),
        ]
        # sql = f"INSERT INTO `{self.tablename}` (`title`, `desc`) VALUES (%s, %s)"
        result = dbfuncs.mysql_executemany(f"INSERT INTO `{self.tablename}` (`title`, `desc`) VALUES (%s, %s)", vals)
        self.assertEqual(3, result)

    def test_mysql_query_fetchall(self):
        dbfuncs.mysql_create_table(self._table_stru())
        # sql = f"INSERT INTO `{self.tablename}`  (`title`, `desc`) VALUES ('FOO', 'BAR')"
        result = dbfuncs.mysql_execute(f"INSERT INTO `{self.tablename}`  (`title`, `desc`) VALUES ('FOO', 'BAR')")
        self.assertEqual(1, result)
        # sql = f"SELECT * FROM `{self.tablename}`"
        result = dbfuncs.mysql_query_fetchall(f"SELECT * FROM `{self.tablename}`")
        self.assertEqual(1, len(result))

    def _table_stru(self):

        return f"""CREATE TABLE `{self.tablename}` (
`id` int NOT NULL AUTO_INCREMENT,
`title` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
`desc` text COLLATE utf8mb4_unicode_ci,
PRIMARY KEY (`id`),
KEY `title` (`title`),
FULLTEXT KEY `desc` (`desc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


if __name__ == "__main__":
    unittest.main()
