from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data_private" / "processed" / "anonymized.jsonl"
DEFAULT_OUTPUT = PROJECT_ROOT / "dist" / "distilled_patterns.jsonl"


PATTERNS: dict[str, dict[str, Any]] = {
    "关系敏感型": {
        "keywords": ["回复", "冷淡", "忽冷忽热", "关系", "朋友", "喜欢", "在意", "细节", "消息", "语气"],
        "abstract_summary": "用户容易从关系中的细节变化推测亲密度和安全感。",
        "common_scenarios": ["对方回复变慢", "语气变化", "关系状态不明确"],
        "common_inner_monologues": ["是不是我不重要了", "是不是我做错了"],
        "surface_emotions": ["焦虑", "失落", "委屈"],
        "deeper_needs": ["稳定回应", "被重视", "关系安全感"],
        "strengths": ["敏锐", "重视关系质量"],
        "costs": ["容易把细节解释成关系风险", "反复推测会消耗自己"],
        "growth_direction": "把事实和推测分开，再用低压力方式确认在意。",
    },
    "压抑需求型": {
        "keywords": ["麻烦", "不好意思", "不敢说", "拒绝", "忍", "委屈", "需求", "打扰", "怕别人"],
        "abstract_summary": "用户倾向于压抑自己的需求，以避免让别人失望或觉得自己麻烦。",
        "common_scenarios": ["想拒绝但怕对方失望", "不舒服却说没事", "需要帮助却不开口"],
        "common_inner_monologues": ["我这样会不会太麻烦", "是不是忍一下比较好"],
        "surface_emotions": ["纠结", "自责", "委屈"],
        "deeper_needs": ["被允许表达", "被认真对待", "关系中的安全感"],
        "strengths": ["体贴", "能照顾他人感受"],
        "costs": ["容易忽略自己", "委屈长期累积"],
        "growth_direction": "从低风险小事开始表达真实需求。",
    },
    "社交耗电型": {
        "keywords": ["社交", "聚会", "群聊", "不合群", "聊天", "人多", "独处", "尴尬", "消耗"],
        "abstract_summary": "用户在多人、浅层或持续回应的社交场景里消耗较快。",
        "common_scenarios": ["多人聚会", "群聊互动", "连续社交安排"],
        "common_inner_monologues": ["我是不是不合群", "我想安静一下"],
        "surface_emotions": ["疲惫", "尴尬", "内疚"],
        "deeper_needs": ["独处恢复", "可控节奏", "被允许安静"],
        "strengths": ["重视真实连接", "不轻易敷衍关系"],
        "costs": ["容易误解自己不合群", "社交后过度自责"],
        "growth_direction": "提前设置社交边界和恢复时间。",
    },
    "过度共情型": {
        "keywords": ["共情", "情绪", "心疼", "内疚", "愧疚", "照顾", "责任", "拖累", "替别人"],
        "abstract_summary": "用户容易吸收他人的情绪，并把理解误认为自己必须负责。",
        "common_scenarios": ["朋友倾诉", "伴侣低落", "家人情绪不好"],
        "common_inner_monologues": ["如果我不帮是不是很冷漠", "我是不是应该多承担一点"],
        "surface_emotions": ["心疼", "内疚", "疲惫"],
        "deeper_needs": ["情绪边界", "有限度地支持别人", "自我恢复"],
        "strengths": ["善于理解别人", "能提供细腻支持"],
        "costs": ["容易把别人的情绪背到自己身上"],
        "growth_direction": "区分我理解他和我需要负责他。",
    },
    "表达困难型": {
        "keywords": ["表达", "说不出口", "开口", "解释", "沉默", "不知道怎么说", "说出来", "沟通"],
        "abstract_summary": "用户内心感受很多，但在真正表达需求或边界时容易卡住。",
        "common_scenarios": ["表达喜欢", "提出不满", "说明边界"],
        "common_inner_monologues": ["我还没想好怎么说", "说出来会不会变严重"],
        "surface_emotions": ["紧张", "羞耻", "委屈"],
        "deeper_needs": ["被理解", "表达安全", "允许不完美表达"],
        "strengths": ["重视语言准确性", "不想伤害别人"],
        "costs": ["错过表达时机", "别人难以看见真实感受"],
        "growth_direction": "从完整表达改成先说一句真实感受。",
    },
    "自我怀疑型": {
        "keywords": ["自卑", "不够好", "怀疑自己", "讨厌自己", "否定", "价值", "失败", "比较", "配不上"],
        "abstract_summary": "用户容易把外界反馈转化为对自身价值的怀疑。",
        "common_scenarios": ["被拒绝", "关系冷淡", "工作学习受挫", "与他人比较"],
        "common_inner_monologues": ["是不是我不够好", "是不是我哪里很差"],
        "surface_emotions": ["自责", "焦虑", "羞耻"],
        "deeper_needs": ["稳定自我价值", "被肯定", "允许犯错"],
        "strengths": ["自省强", "愿意修正自己"],
        "costs": ["容易把普通挫折扩大成自我否定"],
        "growth_direction": "把事件评价和自我价值分开。",
    },
    "理想落差型": {
        "keywords": ["理想", "现实", "未来", "迷茫", "意义", "工作", "目标", "热爱", "人生", "价值感"],
        "abstract_summary": "用户有强烈意义感和理想标准，面对现实复杂度时容易失望或停滞。",
        "common_scenarios": ["职业选择", "人生方向", "创作停滞", "现实与期待不一致"],
        "common_inner_monologues": ["如果没有意义为什么要开始", "现实为什么这么粗糙"],
        "surface_emotions": ["迷茫", "失望", "无力"],
        "deeper_needs": ["意义感", "价值一致", "可持续的现实路径"],
        "strengths": ["有精神追求", "重视价值和审美"],
        "costs": ["容易因现实不够理想而迟迟不行动"],
        "growth_direction": "把理想拆成小的现实行动。",
    },
    "逃避冲突型": {
        "keywords": ["冲突", "吵架", "争执", "拒绝", "算了", "边界", "不舒服", "怕关系变坏"],
        "abstract_summary": "用户倾向于避免直接冲突，以保护关系或避免场面失控。",
        "common_scenarios": ["被冒犯", "需要拒绝", "观点不同", "边界被越过"],
        "common_inner_monologues": ["说了会不会更麻烦", "是不是我太计较"],
        "surface_emotions": ["压抑", "烦躁", "紧张"],
        "deeper_needs": ["安全表达", "边界被尊重", "关系能承受分歧"],
        "strengths": ["愿意维持关系", "减少不必要伤害"],
        "costs": ["边界被反复压缩", "真实感受难以被看见"],
        "growth_direction": "练习不攻击对方地表达边界。",
    },
    "情绪后知后觉型": {
        "keywords": ["后知后觉", "当时没感觉", "回去才", "事后", "复盘", "反复想", "才发现", "没反应过来"],
        "abstract_summary": "用户当下可能先配合或讲道理，事后才意识到自己受伤或生气。",
        "common_scenarios": ["当场说没事", "回家后反复想", "事后才发现不舒服"],
        "common_inner_monologues": ["我刚才为什么没有说", "现在才难过是不是太晚了"],
        "surface_emotions": ["麻木", "后悔", "懊恼"],
        "deeper_needs": ["及时觉察感受", "允许自己有反应"],
        "strengths": ["不急着爆发", "能维持场面"],
        "costs": ["情绪延迟处理后变成内耗"],
        "growth_direction": "练习用身体信号识别情绪。",
    },
    "自我保护型": {
        "keywords": ["退开", "撤退", "消失", "断联", "躲", "冷下来", "保护自己", "受伤", "不想再解释"],
        "abstract_summary": "用户受伤后倾向撤退、沉默或减少暴露，避免再次被刺痛。",
        "common_scenarios": ["被误解", "被冷落", "表达后没有回应"],
        "common_inner_monologues": ["我不想再解释了", "既然不被理解就收回来"],
        "surface_emotions": ["失望", "疲惫", "疏离"],
        "deeper_needs": ["被珍惜", "被认真回应", "安全地靠近"],
        "strengths": ["能保护自己", "不轻易暴露脆弱"],
        "costs": ["别人可能不知道真实受伤点"],
        "growth_direction": "在完全退开前，尝试表达一个边界或事实。",
    },
    "完美幻想型": {
        "keywords": ["完美", "幻想", "想象", "理想中", "不够好", "拖延", "开始不了", "标准"],
        "abstract_summary": "用户容易构建理想版本，并因现实达不到标准而迟迟无法开始。",
        "common_scenarios": ["创作", "择业", "关系期待", "自我规划"],
        "common_inner_monologues": ["如果做不到想象中的样子就没有意义"],
        "surface_emotions": ["拖延", "沮丧", "焦虑"],
        "deeper_needs": ["完整性", "意义感", "允许从不完美开始"],
        "strengths": ["想象力强", "追求美好和真实"],
        "costs": ["容易把开始门槛抬得太高"],
        "growth_direction": "允许草稿版的真实先出现。",
    },
    "被误解敏感型": {
        "keywords": ["误解", "看不懂我", "不被理解", "曲解", "解释", "真实想法", "没人懂", "孤独"],
        "abstract_summary": "用户很在意自己的真实意图是否被准确看见，被误解时会格外受伤。",
        "common_scenarios": ["好意被曲解", "沉默被理解成冷漠", "边界被理解成不在乎"],
        "common_inner_monologues": ["我不是那个意思", "为什么没人看见我真正想表达的东西"],
        "surface_emotions": ["委屈", "愤怒", "孤独"],
        "deeper_needs": ["被准确理解", "被信任", "表达空间"],
        "strengths": ["重视真实", "认真对待关系"],
        "costs": ["容易为证明自己而过度解释"],
        "growth_direction": "区分我想被理解和我必须让所有人理解。",
    },
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def heuristic_extract(record: dict[str, Any], top_n: int, min_score: int) -> list[dict[str, Any]]:
    text = clean_text(f"{record.get('title', '')} {record.get('text', '')}")
    scored: list[tuple[int, str]] = []
    for name, spec in PATTERNS.items():
        score = sum(text.count(keyword) for keyword in spec["keywords"])
        if score >= min_score:
            scored.append((score, name))
    scored.sort(reverse=True)

    outputs = []
    for _, name in scored[:top_n]:
        spec = PATTERNS[name]
        outputs.append(
            {
                "pattern_name": name,
                "abstract_summary": spec["abstract_summary"],
                "source_signal_type": "single_case",
                "common_scenarios": spec["common_scenarios"],
                "common_inner_monologues": spec["common_inner_monologues"],
                "surface_emotions": spec["surface_emotions"],
                "deeper_needs": spec["deeper_needs"],
                "strengths": spec["strengths"],
                "costs": spec["costs"],
                "growth_direction": spec["growth_direction"],
            }
        )
    return outputs


def openai_compatible_extract(record: dict[str, Any]) -> list[dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when --provider=openai-compatible")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    text = clean_text(f"{record.get('title', '')} {record.get('text', '')}")[:3000]

    prompt = (
        "你将看到已经匿名化的 INFP 社区文本。只输出 JSON 数组，不要保留原句，"
        "只抽象总结自我模式、情绪、需求、优势、代价和成长方向。"
        "每个对象必须包含 pattern_name, abstract_summary, source_signal_type, "
        "common_scenarios, common_inner_monologues, surface_emotions, deeper_needs, "
        "strengths, costs, growth_direction。文本：\n"
        + text
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You extract safe, abstract self-understanding patterns. Never copy source text."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - user-selected endpoint
        data = json.loads(response.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.M).strip()
    parsed = json.loads(content)
    if not isinstance(parsed, list):
        raise ValueError("LLM output must be a JSON array")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract abstract INFP-like self patterns.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--provider", choices=["heuristic", "openai-compatible"], default="heuristic")
    parser.add_argument("--top-n", type=int, default=2)
    parser.add_argument("--min-score", type=int, default=1)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped = 0
    with args.input.open("r", encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if args.provider == "heuristic":
                extracted = heuristic_extract(record, args.top_n, args.min_score)
            else:
                extracted = openai_compatible_extract(record)
            if not extracted:
                skipped += 1
                continue
            for item in extracted:
                dst.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1

    print(f"distilled_patterns={written}")
    print(f"skipped_records={skipped}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
