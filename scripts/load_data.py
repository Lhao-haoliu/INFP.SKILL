from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

try:
    import pymysql
except ImportError:  # pragma: no cover
    pymysql = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data_private" / "processed" / "normalized.jsonl"

PRIVATE_KEY_HINTS = {
    "url",
    "link",
    "href",
    "user",
    "username",
    "nickname",
    "author",
    "avatar",
    "homepage",
    "profile",
    "created",
    "updated",
    "time",
    "date",
    "group",
}
TITLE_KEYS = {"title", "subject", "标题"}
TEXT_KEY_HINTS = {"content", "text", "body", "comment", "comments", "正文", "评论", "reply", "replies"}


def clean_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_private_key(key: str) -> bool:
    key_lower = key.lower()
    return any(hint in key_lower for hint in PRIVATE_KEY_HINTS)


def flatten_text(value: Any, *, skip_private: bool = True) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if raw[:1] in "[{":
            try:
                return flatten_text(json.loads(raw), skip_private=skip_private)
            except Exception:
                return [raw]
        return [raw]
    if isinstance(value, (int, float, bool)):
        return [str(value)]
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            parts.extend(flatten_text(item, skip_private=skip_private))
        return parts
    if isinstance(value, dict):
        parts = []
        for key, inner in value.items():
            if skip_private and is_private_key(str(key)):
                continue
            parts.extend(flatten_text(inner, skip_private=skip_private))
        return parts
    return [str(value)]


def normalize_record(record: dict[str, Any]) -> dict[str, str] | None:
    title = ""
    text_parts: list[str] = []
    saw_comment = False
    saw_post = False

    for key, value in record.items():
        key_text = str(key)
        key_lower = key_text.lower()
        if key_lower in TITLE_KEYS or key_text in TITLE_KEYS:
            title = clean_space(" ".join(flatten_text(value, skip_private=True)))[:500]
            continue
        if is_private_key(key_text):
            continue
        if any(hint in key_lower or hint in key_text for hint in TEXT_KEY_HINTS):
            parts = flatten_text(value, skip_private=True)
            text_parts.extend(parts)
            if "comment" in key_lower or "评论" in key_text or "reply" in key_lower:
                saw_comment = True
            else:
                saw_post = True

    if not text_parts:
        for key, value in record.items():
            if is_private_key(str(key)):
                continue
            text_parts.extend(flatten_text(value, skip_private=True))

    text = clean_space("\n".join(text_parts))
    if not title and not text:
        return None

    if saw_post and saw_comment:
        source_type = "mixed"
    elif saw_comment:
        source_type = "comment"
    else:
        source_type = "post"

    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "text": text,
        "source_type": source_type,
    }


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def iter_json(path: Path) -> Iterable[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                yield item
    elif isinstance(data, dict):
        rows = data.get("data") or data.get("rows") or data.get("items")
        if isinstance(rows, list):
            for item in rows:
                if isinstance(item, dict):
                    yield item
        else:
            yield data


def iter_tabular(path: Path) -> Iterable[dict[str, Any]]:
    if pd is None:
        raise RuntimeError("pandas is required for CSV/XLSX input")
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        frame = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported tabular file: {path}")
    for row in frame.to_dict(orient="records"):
        yield row


def iter_file(path: Path) -> Iterable[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        yield from iter_jsonl(path)
    elif suffix == ".json":
        yield from iter_json(path)
    elif suffix in {".csv", ".xlsx", ".xls"}:
        yield from iter_tabular(path)
    else:
        raise ValueError(f"Unsupported input format: {suffix}")


def iter_mysql() -> Iterable[dict[str, Any]]:
    if pymysql is None:
        raise RuntimeError("PyMySQL is required for MySQL input")
    if load_dotenv:
        load_dotenv(PROJECT_ROOT / ".env")

    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "root")
    database = os.getenv("MYSQL_DATABASE", "db_data")
    table = os.getenv("MYSQL_TABLE", "infp_source_posts")

    query = f"SELECT title, content, comments FROM `{table}`"
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            for row in cursor:
                yield row
    finally:
        connection.close()


def write_jsonl(records: Iterable[dict[str, str]], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize local source data into private JSONL.")
    parser.add_argument("--source", choices=["file", "mysql"], default="file")
    parser.add_argument("--input", type=Path, help="CSV/JSON/JSONL/XLSX file when --source=file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.source == "mysql":
        raw_records = iter_mysql()
    else:
        if not args.input:
            raise SystemExit("--input is required when --source=file")
        raw_records = iter_file(args.input)

    normalized = (item for item in (normalize_record(record) for record in raw_records) if item)
    count = write_jsonl(normalized, args.output)
    print(f"normalized_records={count}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
