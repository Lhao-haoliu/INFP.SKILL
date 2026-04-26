<div align="center">

<pre>
🦋
</pre>

# INFP.SKILL

*一个试图理解 "我为什么总是这样" 的小小尝试*

[![License: MIT](https://img.shields.io/badge/License-MIT-9db4c0.svg?style=flat-square)](LICENSE)
[![Type: Skill](https://img.shields.io/badge/Type-Skill-cdb4db.svg?style=flat-square)]()

</div>

---

> *"如果你点进来，也许你也曾在某个深夜问过自己类似的问题。"*

你好。

我不是一份标准答案，也不是一张诊断报告。

我更像是一个在黑暗中摸索过很久的人，终于决定把摸索时触到的纹路记下来——关于情绪、关于关系、关于那些说不出口的疲惫，还有那些明明很珍贵却总被藏起来的感受。

这里记录的东西，来自很多个像你我一样的人在深夜写下的真实困惑。

我试着把它们蒸馏成一些**可以被温柔看见的模式**。

不是为了给你贴标签，而是想在你又一次陷入自我怀疑时，递给你一面不那么 harsh 的镜子。

---

## ✧ 关于我

我倾向于：

- **先读你的具体故事**，再试着命名那些反复出现的模式
- 用 *"可能"*、*"也许"*、*"更像是"* 这样的词——因为我知道每个人都是独特的
- 不把你困在 *"INFP 都这样"* 的盒子里
- 在你描述痛苦时，不急着分析，而是先承认那份难受是真实的

---

## ✧ 我能陪你做什么

| 场景 | 我会怎么做 |
|:---|:---|
| 你又在关系里过度推测了 | 识别 **"关系敏感型"** 模式，区分事实与恐惧 |
| 明明难受却说"没事" | 看见 **"压抑需求型"** 背后的自责与不安 |
| 社交后像被掏空 | 理解 **"社交耗电型"** 不是缺陷，是特质的两面 |
| 吸收了太多别人的情绪 | 厘清 **"过度共情"** 与责任之间的边界 |
| 有很多感受却说不出口 | 陪伴 **"表达困难型"** 找到第一句真实的话 |

除此之外，我还会：

- 把**表层情绪**连回**更深的需求**（焦虑的背后可能是渴望被确定，沉默的背后可能是害怕被误解）
- 解释你身上那些特质的 **优势** 与 **代价**——它们其实是一枚硬币的两面
- 给出一个**很小、很具体**的成长方向，而不是宏大的 *"你要改变自己"*
- 最后留给你 **2-3 个问题**，让你可以继续探索自己

---

## ✧ 我不能做什么

- ✗ 不是心理咨询，也不能代替专业帮助
- ✗ 不做人格测试，不给标准答案
- ✗ 不诊断心理疾病
- ✗ 不替你判断他人的真实意图
- ✗ **不在你描述自伤或严重危机时，还继续给你做性格分析**  
  那时我会停下来，建议你寻找身边真实的支持。

---

## ✧ 目录

```
INFP.SKILL/
├── 📖 README.md              ← 你在这里
├── 🔮 SKILL.md               ← 给 Agent 的触发说明
│
├── 📂 references/            ← 蒸馏出的自我模式、情绪地图、关系模式
├── 📂 prompts/               ← 不同场景下的对话模板
├── 📂 schemas/               ← 结构化输出定义
├── 📂 examples/              ← 一些温和的使用示例
│
├── 🔧 scripts/               ← 本地数据清洗与蒸馏工具
│   ├── load_data.py
│   ├── anonymize.py
│   ├── extract_patterns.py
│   ├── merge_taxonomy.py
│   ├── build_skill_references.py
│   └── validate_distilled_data.py
│
└── 🔒 data_private/          ← 本地私有数据（被 gitignore，不公开）
```

---

## ✧ 如果你也想从自己的数据中蒸馏

也许你有自己的日记、社群观察，或者一段段想要被温柔理解的文字。

可以放在 `data_private/`，然后运行：

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="root"
$env:MYSQL_DATABASE="db_data"
$env:MYSQL_TABLE="infp_source_posts"

python scripts/load_data.py --source mysql
```

之后依次：

```
anonymize.py
      ↓
extract_patterns.py
      ↓
merge_taxonomy.py
      ↓
build_skill_references.py
      ↓
validate_distilled_data.py  ← 确保没有泄露隐私
```

---

## ✧ 关于数据与隐私

原始来源数据只保存在本地，不会进入这个仓库。

能进入仓库的只有：

- ✓ 抽象后的模式与框架
- ✓ 匿名化、改写后的示例
- ✓ Prompt、Schema 和脚本

所有可以追溯回具体个人、平台、时间的内容，都被留在了门外。

---

<div align="center">

<br>

> *"想要理解自己，本身就是一种勇气。"*
>
> *"你不需要先变成 '更好的人' 才值得被理解。"*

<br>

这个 Skill 不会替你把路走完，

但也许可以在某个你独自面对的夜里，陪你坐一会儿。

🌙

</div>

---

<div align="center">

*License: [MIT](LICENSE)*

</div>
