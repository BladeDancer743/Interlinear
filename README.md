# Interlinear：技术论文行间注释器

> 读英文论文时，自动在术语旁插入「翻译：解释」，就像古籍的夹注一样。

## 这是什么

用 AI 读技术论文时，最烦的就是满篇缩写和黑话——`NISQ`、`stoquastic`、`FTQC`、`surface code`……每个词都要中断阅读去查。

Interlinear 是一个 LLM skill，它会在你读论文时**自动检测**需要解释的术语，在原文行间嵌入简短的 `【中文翻译：一句话解释】`，让你不用离开论文就能读懂。

## 快速开始

### 1. 安装

```bash
git clone https://github.com/BladeDancer743/Interlinear.git ~/.claude/skills/Interlinear/
```

### 2. 使用

在对话中说：

```
帮我通读这篇论文，加行间注释：https://arxiv.org/abs/1801.00862
```

或者指定想看的章节：

```
只看 Preskill NISQ 论文的 §2 和 §6，加上注释
```

---

## 效果预览

**原文：**

> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future. Quantum computers with 50-100 qubits may surpass classical computers, but noise will limit circuit sizes.

**带注释后：**

> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future【Preskill 写于2018年，2019 年 Google Sycamore 兑现了这个预测】. Quantum computers with 50-100 qubits【量子比特：可同时处于 0 和 1 叠加态的量子信息基本单元】 may surpass classical computers, but noise【量子门噪声：操作误差导致信息退化，是 NISQ 时代最大的限制因素】 will limit circuit sizes【电路规模：指量子电路的深度（时间步数）和宽度（qubit 数）】.

---

## 决策器：什么词需要注释？

不是每个术语都注释——注释太多反而干扰阅读。Interlinear 按以下规则自动判断：

| 应该注释 | 不应注释 |
|:--|:--|
| 领域专有缩写（NISQ, QEC, BQP） | 作者已在括号里给出全称的缩写 |
| 外行不懂的技术黑话（stabilizer code, stoquastic） | 高中数学/物理常识（eigenvalue, probability） |
| 用名字指代的概念（Shor's algorithm, Gottesman-Knill） | 标题中的术语 |
| 对理解论文核心论证必不可少的概念 | 已在前面注释过的术语（后续用简注 `⤴`） |
| 领域特有的历史/文化引用（Solvay Conference） | 已在同一句中清晰解释的概念 |

**去重规则**：同一章内，术语只注释首次出现；后续用 `【⤴量子纠错】` 简注。

**密度控制**：每句最多 3 个注释，每段保持至少一半的原文不被注释打断。

---

## 注释格式

```
原文术语【中文翻译：一句话解释】
```

| 场景 | 格式 |
|:--|:--|
| 缩写首次出现 | `NISQ【含噪中等规模量子：50~几百 qubit，有噪声，不做纠错】` |
| 概念首次出现 | `decoherence【退相干：量子系统与外界环境交互导致量子信息丢失】` |
| 人名指代 | `Shor's algorithm【Shor 算法：多项式时间分解大整数的量子算法】` |
| 同一概念再现 | `QEC【⤴量子纠错】` |

---

## 内置知识库

目前内置完整的**量子计算**术语知识库，覆盖 200+ 术语，分八大类：

- 量子计算核心概念（qubit, entanglement, decoherence...）
- 量子纠错（QEC, surface code, stabilizer, threshold...）
- 量子算法（Shor, Grover, QAOA, VQE, HHL...）
- 复杂度理论（BQP, NP-hard, quantum supremacy...）
- 硬件平台（superconducting, trapped ion, topological...）
- 量子信息与密码（QKD, PQC, QRAM, no-cloning...）
- 数学工具（Hamiltonian, tensor network, SDP...）
- 物理概念（quantum chaos, Gibbs state, Majorana...）

扩展到其他领域：在 SKILL.md 的「领域术语知识库」章节追加即可。

---

## 项目结构

```
Interlinear/
├── SKILL.md    # Skill 定义（决策器 + 术语库 + 格式规范）
└── README.md   # 本文件
```

## License

MIT
