#!/usr/bin/env python3

import unittest
import pandas as pd
import textfuncs

# https://wiki.python.org/moin/PythonTestingToolsTaxonomy
# https://docs.python.org/3/library/unittest.html


class TextFuncsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_clean_text_sentences(self):

        data = [
            "Sentence one. Sentence two.",
            "Sentence three.Sentence four.",
            "Serial no. 1234. Model A.1",
        ]
        expect = [
            "Sentence one. Sentence two.",
            "Sentence three. Sentence four.",
            "Serial no. 1234. Model A.1",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_sentences(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text_html_tags(self):

        data = [
            "Foo &gt;bar&lt;",
            "Foo <em>bar</em>",
            """Foo <em id="x">bar</em>""",
            "Foo <em></em>",
            "Foo > bar",
        ]
        expect = [
            "Foo &gt;bar&lt;",
            "Foo bar",
            "Foo bar",
            "Foo ",
            "Foo > bar",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_html_tags(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text_html_symbols(self):

        data = [
            "Foo &gt;bar&lt;",
            "Foo &gt; bar &lt;",
            "Foo <em>bar</em>",
            "Foo <foo></foo>",
            "Bang & Olufsen",
        ]
        expect = [
            "Foo bar",
            "Foo  bar ",
            "Foo <em>bar</em>",
            "Foo <foo></foo>",
            "Bang & Olufsen",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_html_symbols(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text_weights(self):

        data = [
            "Foo 5kg",
            "Foo 5 kg",
            "Foo 5.0kg",
            "Foo .5kg",
            "Foo 0.5kg",
            "Foo 10.5kg",
            "Foo 10.50kg",
            "Foo 10.50 kg",
            "Foo 5kg bar",
            "Foo 5 kg bar",
            "Foo 5.0kg bar",
            "Foo .5kg bar",
            "Foo 0.5kg bar",
            "Foo 10.5kg bar",
            "Foo 10.50kg bar",
            "Foo 10.50 kg bar",
            "5kg foo",
            "5 kg foo",
            "5.0kg foo",
            ".5kg foo",
            "10.5kg foo",
            "10.50kg foo",
            "10.50 kg foo",
        ]
        expect = [
            "Foo",
            "Foo",
            "Foo ",
            "Foo ",
            "Foo ",
            "Foo ",
            "Foo ",
            "Foo ",
            "Foo bar",
            "Foo bar",
            "Foo  bar",
            "Foo  bar",
            "Foo  bar",
            "Foo  bar",
            "Foo  bar",
            "Foo  bar",
            " foo",
            " foo",
            " foo",
            " foo",
            " foo",
            " foo",
            " foo",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_weights(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text_code_prefixes(self):

        data = [
            "Foo 34096",
            "Foo34096",
            "34096 Foo",
            "34096Foo",
            "Foo #34096",
            "Foo#34096",
            "34096:Foo",
            ":34096 Foo",
        ]
        expect = [
            "Foo 34096",
            "Foo34096",
            "Foo",
            "Foo",
            "Foo #34096",
            "Foo#34096",
            "Foo",
            "Foo",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_code_prefixes(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text_missing_newline(self):

        data = [
            "Foo fooBar bar",
            "Foobar999",
            "Foo bar999",
        ]
        expect = [
            "Foo foo. Bar bar",
            "Foobar999",
            "Foo bar999",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_missing_newline(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def clean_text_nonprinting_chars(self):

        data = [
            "Foo\rbar",
            "Foo\nbar",
            "Foo\r\nbar",
            "Foo\\rbar",
            "Foo\\nbar",
            "Foo\\r\\nbar",
            "Foobar.\r",
            "Foobar.\n",
            "Foobar.\r\n",
            "Foobar.\\r",
            "Foobar.\\n",
            "Foobar.\\r\\n",
        ]
        expect = [
            "Foo bar",
            "Foo bar",
            "Foo bar",
            "Foo bar",
            "Foo bar",
            "Foo bar",
            "Foo bar.",
            "Foo bar.",
            "Foo bar.",
            "Foo bar.",
            "Foo bar.",
            "Foo bar.",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text_nonprinting_chars(df, column="problem")
        self.assertEqual(list(result["problem"]), expect)

    def test_clean_text(self):

        data = [
            "999:Foo &gt;bar&lt; <em>!</em> 10.5kg ",
            "999:Foo &gt;bar&lt; <em>!</em> 10.5kg ",
            "999: &gt; &lt; <em></em> 10.5kg ",
            "999: &gt; &lt; <em></em> 10.5kg ",
        ]
        expect = [
            "Foo bar !",
        ]
        df = pd.DataFrame(data=data, columns=["problem"])
        result = textfuncs.clean_text(df, column="problem", strip=True, dropna=True, dedupe=True)
        self.assertEqual(list(result["problem"]), expect)


if __name__ == "__main__":
    unittest.main()
