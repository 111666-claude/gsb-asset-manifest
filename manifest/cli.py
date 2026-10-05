"""命令行入口：跑清单校验样例。"""

import argparse

from .parser import parse
from .verify import compare

BAD_LINE = "@core\nfont.ttf 1024 aaa\nsfx.wav 2048\n"
DUP_NAME = "@core\nfont.ttf 1024 aaa\nfont.ttf 2048 bbb\n"
EXTRA_ACTUAL = {"font.ttf": 1024, "leftover.tmp": 8}
SIZE_ACTUAL = {"font.ttf": 4096}
SIZE_MANIFEST = "@core\nfont.ttf 1024 aaa\n"


def build_parser():
    parser = argparse.ArgumentParser(prog="asset-manifest", description="资源清单校验")
    parser.add_argument("--sample", default="badline", help="badline / dup / extra / size")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "badline":
        _, errors = parse(BAD_LINE)
        print("errors=%d" % len(errors))
    elif args.sample == "dup":
        _, errors = parse(DUP_NAME)
        print("errors=%d" % len(errors))
    elif args.sample == "extra":
        groups, _ = parse("@core\nfont.ttf 1024 aaa\n")
        print("extra=%d" % len(compare(groups, EXTRA_ACTUAL)["extra"]))
    elif args.sample == "size":
        groups, _ = parse(SIZE_MANIFEST)
        print("size=%d" % len(compare(groups, SIZE_ACTUAL)["size_mismatch"]))
    else:
        raise SystemExit("需要 --sample badline|dup|extra|size")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
