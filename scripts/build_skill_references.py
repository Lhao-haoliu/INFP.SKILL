from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "dist" / "distilled_patterns.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "references" / "generated"


def read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def unique(values: Iterable[str], limit: int = 10) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
        if len(seen) >= limit:
            break
    return seen


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- 暂无"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build safe generated reference drafts from distilled data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--overwrite-curated",
        action="store_true",
        help="Write generated self/emotion references over curated reference file names after manual review.",
    )
    args = parser.parse_args()

    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in read_jsonl(args.input):
        grouped[item.get("pattern_name", "未命名模式")].append(item)

    counter = Counter({name: len(items) for name, items in grouped.items()})
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pattern_lines = [
        "# Generated Self Patterns",
        "",
        "Generated from safe distilled abstractions only. Review before using as a stable reference.",
        "",
    ]
    emotion_need: dict[str, Counter] = defaultdict(Counter)

    for name, count in counter.most_common():
        items = grouped[name]
        pattern_lines.extend(
            [
                f"## {name}",
                "",
                f"**抽象信号数**：{count}",
                "",
                "### 模式说明",
                unique((item.get("abstract_summary", "") for item in items), limit=1)[0],
                "",
                "### 常见场景",
                bullets(unique(v for item in items for v in item.get("common_scenarios", []))),
                "",
                "### 表层情绪",
                bullets(unique(v for item in items for v in item.get("surface_emotions", []))),
                "",
                "### 深层需求",
                bullets(unique(v for item in items for v in item.get("deeper_needs", []))),
                "",
                "### 优势",
                bullets(unique(v for item in items for v in item.get("strengths", []))),
                "",
                "### 代价",
                bullets(unique(v for item in items for v in item.get("costs", []))),
                "",
                "### 成长方向",
                bullets(unique((item.get("growth_direction", "") for item in items), limit=3)),
                "",
            ]
        )
        for item in items:
            for emotion in item.get("surface_emotions", []):
                for need in item.get("deeper_needs", []):
                    emotion_need[emotion][need] += 1

    emotion_lines = [
        "# Generated Emotion Need Map",
        "",
        "Generated from safe distilled abstractions only. Review before using as a stable reference.",
        "",
    ]
    for emotion, needs in sorted(emotion_need.items(), key=lambda pair: sum(pair[1].values()), reverse=True):
        emotion_lines.extend([f"## {emotion}", "", "可能需求："])
        for need, count in needs.most_common(8):
            emotion_lines.append(f"- {need}: {count}")
        emotion_lines.append("")

    if args.overwrite_curated:
        pattern_path = PROJECT_ROOT / "references" / "self_patterns.md"
        emotion_path = PROJECT_ROOT / "references" / "emotion_need_map.md"
    else:
        pattern_path = args.output_dir / "self_patterns_from_dist.md"
        emotion_path = args.output_dir / "emotion_need_map_from_dist.md"

    pattern_path.write_text("\n".join(pattern_lines) + "\n", encoding="utf-8")
    emotion_path.write_text("\n".join(emotion_lines) + "\n", encoding="utf-8")

    print(f"self_patterns_reference={pattern_path}")
    print(f"emotion_need_reference={emotion_path}")


if __name__ == "__main__":
    main()
