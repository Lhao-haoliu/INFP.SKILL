# Self Pattern Identification Prompt

根据用户描述，识别 1-2 个可能的自我模式。不要把模式当成诊断或固定人格标签。

## 输入

```text
{{user_input}}
```

## 参考

优先参考：

- `references/self_patterns.md`
- `references/emotion_need_map.md`
- `references/response_style.md`
- `references/safety_rules.md`

## 任务

请输出：

1. 可能的自我模式
2. 为什么像这个模式
3. 表层情绪
4. 深层需求
5. 可能的核心信念
6. 这个模式背后的优势
7. 这个模式带来的代价
8. 一个温和的成长方向
9. 2-3 个反思问题

## 风格约束

- 使用 "可能"、"从你的描述看"、"更像是"。
- 不说 "INFP 都这样"。
- 不替用户判断他人真实意图。
- 不把敏感、慢热、内省写成缺陷。
- 成长方向要小、具体、低压力。
