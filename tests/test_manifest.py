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

INHERIT_SAMPLE = """@base
font.ttf 1024 aaa
shared.cfg 10 old
@ui : base
icon.png 16 bbb
shared.cfg 20 new
"""

CYCLE_SAMPLE = """@a : b
@b : a
"""


class InheritanceTest(unittest.TestCase):
    def test_child_sees_parent_entries(self):
        groups, _ = parse(INHERIT_SAMPLE)
        report = Verifier(groups).compare("ui", {"icon.png": 16, "font.ttf": 1024})
        self.assertEqual(report["missing"], ["shared.cfg"])

    def test_child_overrides_same_name(self):
        groups, _ = parse(INHERIT_SAMPLE)
        entries = Verifier(groups).effective("ui")
        self.assertEqual(entries["shared.cfg"]["size"], 20)
        self.assertEqual(entries["shared.cfg"]["hash"], "new")
        self.assertEqual(len(entries), 3)

    def test_extra_files_reported(self):
        groups, _ = parse(SAMPLE)
        report = Verifier(groups).compare(
            "core", {"font.ttf": 1024, "sfx.wav": 2048, "leftover.tmp": 8}
        )
        self.assertEqual(report["extra"], ["leftover.tmp"])

    def test_size_mismatch_reported(self):
        groups, _ = parse(SAMPLE)
        report = Verifier(groups).compare("core", {"font.ttf": 4096, "sfx.wav": 2048})
        self.assertEqual(report["size_mismatch"], ["font.ttf"])

    def test_all_three_sorted(self):
        groups, _ = parse(INHERIT_SAMPLE)
        report = Verifier(groups).compare(
            "ui", {"icon.png": 99, "shared.cfg": 20, "zzz.tmp": 1}
        )
        self.assertEqual(report["missing"], ["font.ttf"])
        self.assertEqual(report["extra"], ["zzz.tmp"])
        self.assertEqual(report["size_mismatch"], ["icon.png"])


class CycleTest(unittest.TestCase):
    def test_cycle_is_one_error(self):
        groups, _ = parse(CYCLE_SAMPLE)
        verifier = Verifier(groups)
        self.assertEqual(len(verifier.errors()), 1)
        self.assertEqual(verifier.effective("a"), {})

    def test_cycle_error_independent_of_order(self):
        groups1, _ = parse(CYCLE_SAMPLE)
        groups2, _ = parse("@b : a\n@a : b\n")
        self.assertEqual(Verifier(groups1).errors(), Verifier(groups2).errors())

    def test_missing_parent_is_error(self):
        groups, _ = parse("@a : ghost\nx 1 h\n")
        self.assertEqual(len(Verifier(groups).errors()), 1)

    def test_repeated_verification_stable(self):
        groups, _ = parse(INHERIT_SAMPLE)
        verifier = Verifier(groups)
        first = verifier.compare("ui", {"icon.png": 16, "font.ttf": 1024, "shared.cfg": 20})
        second = verifier.compare("ui", {"icon.png": 16, "font.ttf": 1024, "shared.cfg": 20})
        self.assertEqual(first, second)


class ParseErrorTest(unittest.TestCase):
    def test_bad_line_bad_size_dup(self):
        text = "@core\nfont.ttf 1024 aaa\nbad.wav 2048\nx.bin abc h\nfont.ttf 1 h\n"
        _, errors = parse(text)
        self.assertEqual(len(errors), 3)
        groups, _ = parse(text)
        self.assertEqual(groups["core"]["entries"][0]["hash"], "aaa")
