import unittest
from unittest.mock import patch

from outils import reparer


class TestAccolades(unittest.TestCase):
    @patch("outils.reparer.shutil.which", return_value=None)
    def test_recognizes_uppercase_script_tags(self, _which):
        self.assertEqual([], reparer.d_accolades("<SCRIPT>const ok = true;</SCRIPT>"))

    @patch("outils.reparer.shutil.which", return_value=None)
    def test_recognizes_whitespace_in_uppercase_script_end_tag(self, _which):
        constats = reparer.d_accolades("<SCRIPT>if (true) {</SCRIPT >")
        self.assertTrue(any("accolade(s) non appariée(s)" in c for c in constats))

    @patch("outils.reparer.shutil.which", return_value=None)
    def test_ignores_braces_in_regex_literals(self, _which):
        self.assertEqual([], reparer.d_accolades("<script>const re = /[{}]+/g;</script>"))

    @patch("outils.reparer.shutil.which", return_value=None)
    def test_handles_long_unterminated_regex_without_backtracking(self, _which):
        code = "<script>const re = /" + "[]" * 50000 + "\n</script>"
        self.assertEqual([], reparer.d_accolades(code))


if __name__ == "__main__":
    unittest.main()
