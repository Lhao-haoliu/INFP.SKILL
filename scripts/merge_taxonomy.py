from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "dist" / "distilled_patterns.jsonl"
DEFAULT_PATTERN_OUTPUT = PROJECT_ROOT / "dist" / "self_patterns_draft.md"
DEFAULT_EMOTION_OUTPUT = PROJECT_ROOT / "dist" / "emotion_need_map_draft.md"


def read_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def unique(values: Iterable[str], limit: int = 12) -> list[str]:
    seen = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
        if len(seen) >= limit:
            break
    return seen


def bullet_list(values: list[str]) -> str:
    if not values:
        return "- 暂无"
    return "\n".join(f"- {value}" for value in values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge distilled patterns into taxonomy drafts.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--patterns-output", type=Path, default=DEFAULT_PATTERN_OUTPUT)
    parser.add_argument("--emotion-output", type=Path, default=DEFAULT_EMOTION_OUTPUT)
    args = parser.parse_args()

    grouped: dict[str, list[dict]] = defaultdict(list)
    emotion_needs: dict[str, Counter] = defaultdict(Counter)

    for record in read_jsonl(args.input):
        name = record.get("pattern_name", "未命名模式")
        grouped[name].append(record)
        for emotion in record.get("surface_emotions", []):
            for need in record.get("deeper_needs", []):
                emotion_needs[emotion][need] += 1

    args.patterns_output.parent.mkdir(parents=True, exist_ok=True)
    args.emotion_output.parent.mkdir(parents=True, exist_ok=True)

    pattern_counter = Counter({name: len(items) for name, items in grouped.items()})
    pattern_lines = [
        "# 自我模式草案",
        "",
        "本文件由抽象蒸馏结果合并生成，不包含原始帖子、评论、链接、昵称或发布时间。",
        "",
        "## 高频模式概览",
        "",
    ]
    for name, count in pattern_counter.most_common():
        pattern_lines.append(f"- {name}: {count}")

    for name, count in pattern_counter.most_common():
        items = grouped[name]
        summaries = unique(item.get("abstract_summary", "") for item in items)
        scenarios = unique(value for item in items for value in item.get("common_scenarios", []))
        monologues = unique(value for item in items for value in item.get("common_inner_monologues", []))
        emotions = unique(value for item in items for value in item.get("surface_emotions", []))
        needs = unique(value for item in items for value in item.get("deeper_needs", []))
        strengths = unique(value for item in items for value in item.get("strengths", []))
        costs = unique(value for item in items for value in item.get("costs", []))
        growth = unique((item.get("growth_direction", "") for item in items), limit=4)

        pattern_lines.extend(
            [
                "",
                f"## {name}",
                "",
                f"**出现次数**：{count}",
                "",
                "### 模式说明",
                summaries[0] if summaries else "暂无",
                "",
                "### 常见场景",
                bullet_list(scenarios),
                "",
                "### 常见内心独白",
                bullet_list(monologues),
                "",
                "### 表层情绪",
                bullet_list(emotions),
                "",
                "### 深层需求",
                bullet_list(needs),
                "",
                "### 优势",
                bullet_list(strengths),
                "",
                "### 代价",
                bullet_list(costs),
                "",
                "### 成长方向",
                bullet_list(growth),
            ]
        )

    emotion_lines = [
        "# 情绪-需求映射草案",
        "",
        "本文件由抽象蒸馏结果合并生成，只保留情绪标签与需求标签。",
        "",
    ]
    for emotion, needs in sorted(emotion_needs.items(), key=lambda item: sum(item[1].values()), reverse=True):
        emotion_lines.extend(
            [
                f"## {emotion}",
                "",
                "可能需求：",
            ]
        )
        for need, count in needs.most_common(8):
            emotion_lines.append(f"- {need}: {count}")
        emotion_lines.append("")

    args.patterns_output.write_text("\n".join(pattern_lines) + "\n", encoding="utf-8")
    args.emotion_output.write_text("\n".join(emotion_lines) + "\n", encoding="utf-8")

    print(f"patterns={len(grouped)}")
    print(f"patterns_output={args.patterns_output}")
    print(f"emotion_output={args.emotion_output}")


if __name__ == "__main__":
    main()
