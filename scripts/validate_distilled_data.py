from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "__pycache__", "data_private", "dist"}
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".txt", ".py", ".yaml", ".yml", ".gitignore"}

CHECKS = [
    ("url", re.compile(r"https?://[^\s)]+|www\.[^\s)]+", re.I)),
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)),
    ("phone", re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")),
    ("qq", re.compile(r"\bQQ[:：]?\s*\d{5,12}\b", re.I)),
    ("wechat", re.compile(r"\b(?:vx|wechat|weixin|微信|微信号)[:：\s]+[a-zA-Z][-_a-zA-Z0-9]{5,19}\b", re.I)),
    ("username", re.compile(r"@[A-Za-z0-9_\-\u4e00-\u9fff]{2,30}")),
]

ALLOWLIST_URLS = ("https://json-schema.org/", "http://json-schema.org/", "localhost")
PUBLIC_CODE_HINTS = ("re.compile", "OPENAI_BASE_URL", "ALLOWLIST_URLS")


def should_scan(path: Path, include_dist: bool) -> bool:
    parts = set(path.relative_to(PROJECT_ROOT).parts)
    excludes = set(DEFAULT_EXCLUDES)
    if include_dist:
        excludes.remove("dist")
    if parts & excludes:
        return False
    return path.is_file() and path.suffix in TEXT_SUFFIXES


def is_allowed(match: str, line: str) -> bool:
    if any(allowed in match for allowed in ALLOWLIST_URLS):
        return True
    if any(hint in line for hint in PUBLIC_CODE_HINTS):
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Warn about possible privacy leakage in public artifacts.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--include-dist", action="store_true")
    parser.add_argument("--max-line-chars", type=int, default=360)
    args = parser.parse_args()

    warnings: list[str] = []
    for path in args.root.rglob("*"):
        if not should_scan(path, args.include_dist):
            continue
        relative = path.relative_to(args.root)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(lines, start=1):
            for name, pattern in CHECKS:
                for match in pattern.findall(line):
                    if isinstance(match, tuple):
                        match = "".join(match)
                    if is_allowed(str(match), line):
                        continue
                    warnings.append(f"{relative}:{line_no}: possible {name}: {str(match)[:80]}")
            if len(line) > args.max_line_chars and path.suffix in {".md", ".json", ".jsonl", ".txt"}:
                warnings.append(f"{relative}:{line_no}: long line may contain source-like text ({len(line)} chars)")

    if warnings:
        print("privacy_warnings")
        for warning in warnings:
            print(f"- {warning}")
        raise SystemExit(1)

    print("privacy_warnings=0")


if __name__ == "__main__":
    main()
