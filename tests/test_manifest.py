import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manifest.parser import parse  # noqa: E402
from manifest.verify import compare  # noqa: E402

SAMPLE = """@core
font.ttf 1024 aaa
# 注释
sfx.wav 2048 bbb
"""


class ParserTest(unittest.TestCase):
    def test_parses_group_and_entries(self):
        groups, errors = parse(SAMPLE)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(groups["core"]), 2)

    def test_parses_default_group(self):
        groups, _ = parse("icon.png 16 ccc\n")
        self.assertEqual(groups["default"][0]["name"], "icon.png")


class VerifyTest(unittest.TestCase):
    def test_missing_is_reported(self):
        groups, _ = parse(SAMPLE)
        report = compare(groups, {"font.ttf": 1024})
        self.assertEqual(report["missing"], ["sfx.wav"])

    def test_all_present(self):
        groups, _ = parse(SAMPLE)
        report = compare(groups, {"font.ttf": 1024, "sfx.wav": 2048})
        self.assertEqual(report["missing"], [])


if __name__ == "__main__":
    unittest.main()
