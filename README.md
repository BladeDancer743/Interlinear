# Interlinear: 技术论文行间注释器

一个 LLM skill，用于在阅读英文技术论文时，自动检测领域术语、缩写和生僻概念，在原文中内嵌中文注释（翻译 + 一句话解释）。

## 安装

将此仓库克隆到 `~/.claude/skills/paper-zh-annotator/`（或你的 AI 工具对应的 skills 目录）。

```bash
git clone https://github.com/你的用户名/Interlinear.git ~/.claude/skills/Interlinear/
```

## 使用方法

在对话中使用 skill：

```
帮我通读这篇论文，加上中文注释：https://arxiv.org/abs/1801.00862
```

AI 会自动：
1. 获取论文全文
2. 识别需要注释的技术术语
3. 在原文中插入 `【中文：解释】` 格式的注释

## 决策器逻辑

术语是否需要注释，按以下类别判断：

| 类别 | 判断标准 | 示例 |
|------|----------|------|
| 领域缩写 | 大写字母组合，非日常词汇 | NISQ, QEC, FTQC, HHL, QAOA |
| 技术术语 | 该领域特有概念，外行不懂 | decoherence, stabilizer code, surface code |
| 人名指代 | 用名字指代的概念/算法/定理 | Shor's algorithm, Feynman's proposal |
| 历史/文化引用 | 非该领域读者可能不认识的引用 | Solvay Conference |
| 关键概念 | 对理解本文核心论证必不可少 | threshold theorem, overhead cost |

重复过滤：同一术语在同章内只注释首次出现，后续用简注 `【⤴量子纠错】`。

## 示例

**原文：**
> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future. Quantum computers with 50-100 qubits may surpass classical computers, but noise will limit circuit sizes.

**带注释后：**
> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future【Preskill写于2018年，2019年Google Sycamore兑现了】. Quantum computers with 50-100 qubits【量子比特：可同时处于0和1叠加态的量子信息单元】 may surpass classical computers, but noise【量子门噪声：门操作误差导致信息退化，NISQ最大限制】 will limit circuit sizes.

## 领域支持

目前内置完整的量子计算术语知识库（200+ 术语），可扩展到其他技术领域。

## License

MIT
