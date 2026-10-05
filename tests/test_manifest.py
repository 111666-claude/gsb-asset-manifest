import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manifest.parser import parse  # noqa: E402
from manifest.verify import Verifier  # noqa: E402

SAMPLE = """@core
font.ttf 1024 aaa
# 注释
sfx.wav 2048 bbb
"""


class ParserTest(unittest.TestCase):
    def test_parses_group_and_entries(self):
        groups, errors = parse(SAMPLE)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(groups["core"]["entries"]), 2)

    def test_parses_default_group(self):
        groups, _ = parse("icon.png 16 ccc\n")
        self.assertEqual(groups["default"]["entries"][0]["name"], "icon.png")


class VerifierTest(unittest.TestCase):
    def test_missing_is_reported(self):
        groups, _ = parse(SAMPLE)
        report = Verifier(groups).compare("core", {"font.ttf": 1024})
        self.assertEqual(report["missing"], ["sfx.wav"])

    def test_all_present(self):
        groups, _ = parse(SAMPLE)
        report = Verifier(groups).compare("core", {"font.ttf": 1024, "sfx.wav": 2048})
        self.assertEqual(report["missing"], [])

    def test_effective_keeps_group_entries(self):
        groups, _ = parse(SAMPLE)
        self.assertEqual(sorted(Verifier(groups).effective("core")), ["font.ttf", "sfx.wav"])

    def test_work_starts_at_zero(self):
        groups, _ = parse(SAMPLE)
        self.assertEqual(Verifier(groups).work_count(), 0)


if __name__ == "__main__":
    unittest.main()
