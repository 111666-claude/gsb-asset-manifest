"""命令行入口：跑清单校验样例。"""

import argparse

from .parser import parse
from .verify import Verifier

INHERIT = "@base\nfont.ttf 1024 aaa\n@ui : base\nicon.png 16 bbb\n"
CYCLE = "@a : b\n@b : a\n"
ONE = "@core\nfont.ttf 1024 aaa\n"
BAD_LINE = "@core\nfont.ttf 1024 aaa\nsfx.wav 2048\n"
DUP_NAME = "@core\nfont.ttf 1024 aaa\nfont.ttf 2048 bbb\n"


def build_parser():
    parser = argparse.ArgumentParser(prog="asset-manifest", description="资源清单校验")
    parser.add_argument("--sample", default="inherit", help="inherit / cycle / extra / size / badline / dup / work")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "inherit":
        groups, _ = parse(INHERIT)
        report = Verifier(groups).compare("ui", {"icon.png": 16})
        print("missing=%d" % len(report["missing"]))
    elif args.sample == "cycle":
        groups, errors = parse(CYCLE)
        verifier = Verifier(groups)
        print("errors=%d" % (len(errors) + len(verifier.errors())))
    elif args.sample == "extra":
        groups, _ = parse(ONE)
        report = Verifier(groups).compare("core", {"font.ttf": 1024, "leftover.tmp": 8})
        print("extra=%d" % len(report["extra"]))
    elif args.sample == "size":
        groups, _ = parse(ONE)
        report = Verifier(groups).compare("core", {"font.ttf": 4096})
        print("size=%d" % len(report["size_mismatch"]))
    elif args.sample == "badline":
        _, errors = parse(BAD_LINE)
        print("errors=%d" % len(errors))
    elif args.sample == "dup":
        _, errors = parse(DUP_NAME)
        print("errors=%d" % len(errors))
    elif args.sample == "work":
        text = "".join("@g%d\nfile-%d.bin 16 h\n" % (index, index) for index in range(3000))
        groups, _ = parse(text)
        verifier = Verifier(groups)
        for name in list(groups):
            verifier.effective(name)
        print("work=%d" % verifier.work_count())
    else:
        raise SystemExit("需要 --sample inherit|cycle|extra|size|badline|dup|work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
