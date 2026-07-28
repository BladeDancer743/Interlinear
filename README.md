# Interlinear：技术论文行间注释器

<div align="center">

[![License](https://img.shields.io/github/license/BladeDancer743/Interlinear)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.3.0-blue)](CHANGELOG.md)
[![Stars](https://img.shields.io/github/stars/BladeDancer743/Interlinear)](https://github.com/BladeDancer743/Interlinear/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/BladeDancer743/Interlinear)](https://github.com/BladeDancer743/Interlinear/commits/main)

</div>

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

### 定义式模式（默认）

**原文：**

> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future. Quantum computers with 50-100 qubits may surpass classical computers, but noise will limit circuit sizes.

**带注释后：**

> Noisy Intermediate-Scale Quantum (NISQ) technology will be available in the near future【Preskill 写于2018年，2019 年 Google Sycamore 兑现了这个预测】. Quantum computers with 50-100 qubits may surpass classical computers, but noise in quantum gates【量子门噪声：操作误差导致量子信息退化，使电路结果不可靠】 will limit the size of circuits【量子电路：量子门操作构成的有向无环图，深度受噪声限制】 that can be run reliably, unless quantum error correction【量子纠错：用多个物理qubit编码一个逻辑qubit，以冗余换取容错——但计算开销巨大】 is used.

### 几何直觉模式

| 术语 | 定义式 | 几何直觉式 |
|:--|:--|:--|
| qubit | 可同时处于0和1叠加态的信息单元 | 一个在球面上自由旋转的箭头——北极是0，南极是1，指向任何方向都是合法态 |
| entanglement | 多粒子间的非经典关联 | 两条绕在一起的绳子，拉一端另一端瞬间同步，不管隔多远 |
| surface code | 仅需近邻连接的拓扑纠错码 | 一张棋盘格——数据qubit住在格子里，测量qubit站在路口检查邻居是否"打架" |
| HHL algorithm | 量子矩阵求逆算法 | 在向量空间里把b的方向沿A⁻¹旋转到x的方向——不是暴力解方程，而是"转过去" |

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
├── SKILL.md              # Skill 定义（决策器 + 术语库 + 格式规范）
├── README.md             # 本文件
├── LICENSE               # MIT License
├── CHANGELOG.md           # 版本变更记录
├── CONTRIBUTING.md        # 贡献指南
└── .github/
    ├── workflows/lint.yml # Markdown 自动检查
    └── ISSUE_TEMPLATE/    # Issue 模板
```

## 兼容平台

| 平台 | 安装路径 | 状态 |
|:--|:--|:--|
| **Claude Code** | `~/.claude/skills/Interlinear/` | ✅ 原生支持 |
| **OpenCode** | `~/.opencode/skills/Interlinear/` | ✅ 兼容 |
| **Codex (OpenAI)** | 导入 SKILL.md 为 prompt | ⚠️ 需手动配置 |
| **Cursor** | 导入 SKILL.md 为 rule | ⚠️ 需手动配置 |
| **Gemini CLI** | `~/.gemini/skills/Interlinear/` | ⚠️ 未经测试 |

## 相关链接

- [Changelog](CHANGELOG.md)
- [贡献指南](CONTRIBUTING.md)
- [Issue 追踪](https://github.com/BladeDancer743/Interlinear/issues)

## License

MIT — 详见 [LICENSE](LICENSE)
