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


class InheritanceTest(unittest.TestCase):
    def test_child_sees_parent_entries(self):
        groups, errors = parse("@base\nfont.ttf 1024 aaa\n@ui : base\nicon.png 16 bbb\n")
        self.assertEqual(errors, [])
        report = Verifier(groups).compare("ui", {"icon.png": 16})
        self.assertEqual(report["missing"], ["font.ttf"])

    def test_child_overrides_parent_entry(self):
        groups, _ = parse("@base\nfont.ttf 1024 aaa\n@ui : base\nfont.ttf 2048 ccc\n")
        effective = Verifier(groups).effective("ui")
        self.assertEqual(effective["font.ttf"]["size"], 2048)
        self.assertEqual(effective["font.ttf"]["hash"], "ccc")

    def test_cycle_is_reported(self):
        groups, errors = parse("@a : b\n@b : a\n")
        verifier = Verifier(groups)
        self.assertEqual(len(errors) + len(verifier.errors()), 1)

    def test_missing_parent_is_reported(self):
        groups, _ = parse("@ui : ghost\nicon.png 16 bbb\n")
        self.assertEqual(len(Verifier(groups).errors()), 1)

    def test_results_do_not_depend_on_group_order(self):
        forward, _ = parse("@base\nfont.ttf 1024 aaa\n@ui : base\nicon.png 16 bbb\n")
        backward, _ = parse("@ui : base\nicon.png 16 bbb\n@base\nfont.ttf 1024 aaa\n")
        actual = {"icon.png": 16}
        self.assertEqual(
            Verifier(forward).compare("ui", actual),
            Verifier(backward).compare("ui", actual),
        )
        self.assertEqual(Verifier(forward).errors(), Verifier(backward).errors())


class CompareTest(unittest.TestCase):
    def test_extra_is_reported_sorted(self):
        groups, _ = parse("@core\nfont.ttf 1024 aaa\n")
        report = Verifier(groups).compare(
            "core", {"font.ttf": 1024, "z.tmp": 1, "a.tmp": 2}
        )
        self.assertEqual(report["extra"], ["a.tmp", "z.tmp"])

    def test_size_mismatch_is_reported(self):
        groups, _ = parse("@core\nfont.ttf 1024 aaa\nsfx.wav 2048 bbb\n")
        report = Verifier(groups).compare(
            "core", {"font.ttf": 4096, "sfx.wav": 2048}
        )
        self.assertEqual(report["size_mismatch"], ["font.ttf"])

    def test_repeat_compare_is_stable(self):
        groups, _ = parse(SAMPLE)
        verifier = Verifier(groups)
        actual = {"font.ttf": 1024, "leftover.tmp": 8}
        self.assertEqual(verifier.compare("core", actual), verifier.compare("core", actual))

    def test_work_scales_with_entries_not_groups(self):
        text = "".join("@g%d\nfile-%d.bin 16 h\n" % (i, i) for i in range(3000))
        groups, _ = parse(text)
        verifier = Verifier(groups)
        for name in list(groups):
            verifier.effective(name)
        self.assertLessEqual(verifier.work_count(), 6000)


class ParserErrorTest(unittest.TestCase):
    def test_bad_line_is_reported(self):
        _, errors = parse("@core\nfont.ttf 1024 aaa\nsfx.wav 2048\n")
        self.assertEqual(len(errors), 1)

    def test_unparsable_size_is_reported(self):
        _, errors = parse("@core\nfont.ttf abc aaa\n")
        self.assertEqual(len(errors), 1)

    def test_duplicate_keeps_first_and_reports(self):
        groups, errors = parse("@core\nfont.ttf 1024 aaa\nfont.ttf 2048 bbb\n")
        self.assertEqual(len(errors), 1)
        self.assertEqual(groups["core"]["entries"][0]["size"], 1024)
        self.assertEqual(len(groups["core"]["entries"]), 1)


if __name__ == "__main__":
    unittest.main()
