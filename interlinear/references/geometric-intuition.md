# Geometric intuition mode

Load this reference only when the user requests geometric, visual, or physical intuition.

## Goal

Create a mental picture that preserves the concept's important structure. Treat the picture as an analogy unless it is a literal representation such as a Bloch sphere.

Use one of three depths:

| Depth | Use | Target |
|:--|:--|:--|
| `brief` | Familiar concept or repeat | Up to 20 Chinese characters |
| `normal` | First occurrence | 20–35 characters |
| `deep` | Concept central to the argument | 35–60 characters |

Default to `normal`.

## Choose the image family

| Concept type | Prefer |
|:--|:--|
| Single-qubit states and gates | Bloch-vector rotations |
| Error correction and stabilizers | Code space, boundaries, parity checks |
| Entanglement and correlations | Linked degrees of freedom or shared constraints |
| Noise and decoherence | Shrinking vectors, diffusion, or information leakage |
| Search and amplitude amplification | Rotations in a two-dimensional subspace |
| Optimization and annealing | Energy landscapes |
| Tensor networks | Connected tensors and contracted indices |
| Density operators | Points inside the Bloch ball for a single qubit |
| Information protocols | Channels, keys, and detectable disturbance |

Stay within one image family for related terms in the same passage.

## Writing rules

- State the picture first, then connect it to the concept.
- Mark nonliteral pictures with “可以想成” or equivalent wording.
- Keep equations out of the inline analogy.
- Do not import a second technical domain merely to explain the first.
- Do not imply faster-than-light signaling, error-free logical qubits, or guaranteed quantum speedups.
- Fall back to a precise definition when no honest picture exists.

## Examples

| Term | Geometric intuition |
|:--|:--|
| qubit | 可以想成布洛赫球里的一支箭头；方向编码状态，测量把它投影到选定轴的两端 |
| quantum gate | 在布洛赫球上精确旋转状态箭头；不同门对应不同旋转轴和角度 |
| superposition | 状态箭头没有停在测量轴两端，测量时才按投影概率得到其中一个结果 |
| decoherence | 状态与环境纠缠后，相位信息向外泄漏；在布洛赫球里常表现为箭头缩短 |
| stabilizer check | 用一组不直接读取逻辑信息的“方向检查”判断状态是否偏离编码子空间 |
| surface code | 在二维格点上反复检查局部奇偶关系；成串错误的端点会留下可定位的综合征 |
| logical qubit | 把一个量子态编码进更大的子空间，让局部错误只把状态轻推离开，再由综合征拉回 |
| threshold theorem | 当物理错误足够低且纠错方案满足条件时，增加编码规模可继续压低逻辑错误 |
| Grover's algorithm | 状态在“正确答案方向”和其余方向构成的平面里逐步旋转，越来越靠近目标 |
| HHL algorithm | 把线性系统的谱分量按特征值重新加权，最终得到与解向量成比例的量子态 |
| quantum annealing | 让系统随能量景观缓慢变化，希望状态跟随到目标低能区域；过快会发生跃迁 |
| density matrix | 对单量子比特，纯态在布洛赫球面，混合态在球内；越靠中心越混合 |
| trace distance | 对单量子比特，它对应布洛赫球内两点的直线距离尺度，反映最佳区分能力 |
| entanglement | 两部分状态不能各自独立指定；它们像共享同一组约束，但不能借此超光速通信 |

## Reject misleading pictures

Avoid:

- “纠缠像两根绳子，拉一端另一端瞬间同步”；
- “逻辑量子比特是无错 qubit”；
- “HHL 直接把经典答案向量完整读出来”；
- “trace distance 是球面测地线距离”；
- “光子没有退相干问题”。

Replace the analogy when it changes a correlation into a causal mechanism or hides a condition required by the theorem.

## Quality check

- Does the picture preserve the relevant relationship?
- Is it clear where the analogy stops?
- Is the depth appropriate for the reader?
- Are repeated related terms using a consistent image family?
- Would a precise definition be safer than the picture?
