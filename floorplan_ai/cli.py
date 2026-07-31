from __future__ import annotations

import argparse
from .pipeline import analyze


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="floorplan", description="아파트 평면도 OCR/기하 분석")
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("analyze", help="PNG/JPG/PDF 분석")
    cmd.add_argument("input", help="입력 파일")
    cmd.add_argument("--output-dir", default="out")
    cmd.add_argument("--lang", default="kor+eng")
    cmd.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args(argv)
    if args.command == "analyze":
        for path in analyze(args.input, args.output_dir, args.lang, args.dpi): print(path)
    return 0
