from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data_private" / "processed" / "normalized.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "data_private" / "processed" / "anonymized.jsonl"

REPLACEMENTS = [
    (re.compile(r"https?://\S+|www\.\S+", re.I), "[链接已移除]"),
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I), "[邮箱已移除]"),
    (re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)"), "[手机号已移除]"),
    (re.compile(r"\bQQ[:：]?\s*\d{5,12}\b", re.I), "[QQ已移除]"),
    (re.compile(r"\b(?:vx|wechat|weixin|微信|微信号)[:：\s]+[a-zA-Z][-_a-zA-Z0-9]{5,19}\b", re.I), "[微信已移除]"),
    (re.compile(r"@[A-Za-z0-9_\-\u4e00-\u9fff]{2,30}"), "[用户名已移除]"),
    (re.compile(r"\b\d{4}[-/.年]\d{1,2}[-/.月]\d{1,2}日?\b"), "[具体日期已移除]"),
    (re.compile(r"\b\d{1,2}[:：]\d{2}\b"), "[具体时间已移除]"),
    (re.compile(r"[\u4e00-\u9fff]{2,20}(?:大学|学院|中学|小学|公司|集团|医院|小区|街道|区|县|市|省)"), "[具体地点/机构已移除]"),
]

DETAIL_MARKERS = re.compile(r"(具体|去年|前年|今年|昨天|今天|明天|某年|某月|学校|公司|地址|楼|宿舍|城市|小区|生日|身份证)")
SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?；;])")


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def replace_sensitive(text: str) -> str:
    for pattern, replacement in REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return text


def abstract_unique_details(text: str) -> str:
    sentences = [part.strip() for part in SENTENCE_SPLIT.split(text) if part.strip()]
    if not sentences:
        return text

    output: list[str] = []
    detail_replaced = False
    for sentence in sentences:
        too_specific = len(sentence) > 160 and (DETAIL_MARKERS.search(sentence) or re.search(r"\d", sentence))
        if too_specific:
            if not detail_replaced:
                output.append("[一段具体经历已摘要化]")
                detail_replaced = True
            continue
        output.append(sentence)
    return " ".join(output)


def anonymize_text(text: str, max_chars: int) -> str:
    text = replace_sensitive(text)
    text = abstract_unique_details(text)
    text = clean_space(text)
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + " [后续内容已摘要化]"
    return text


def anonymize_record(record: dict[str, Any], max_chars: int) -> dict[str, Any]:
    return {
        "id": record.get("id", ""),
        "title": anonymize_text(str(record.get("title", "")), 240),
        "text": anonymize_text(str(record.get("text", "")), max_chars),
        "source_type": record.get("source_type", "mixed"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove identifiers and summarize high-risk details.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-chars", type=int, default=2400)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.input.open("r", encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            safe_record = anonymize_record(record, args.max_chars)
            dst.write(json.dumps(safe_record, ensure_ascii=False) + "\n")
            count += 1

    print(f"anonymized_records={count}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
