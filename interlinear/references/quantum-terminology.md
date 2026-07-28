# Quantum terminology reference

Use this reference as a candidate glossary, not as an authority that overrides the paper. Verify paper-specific meanings and time-sensitive hardware claims.

## Contents

- Core concepts
- Error correction
- Algorithms
- Complexity
- Hardware
- Mathematical tools
- Information and cryptography
- Sources

## Core concepts

- qubit / quantum bit → 量子比特（二维量子系统承载的基本信息单元）
- superposition → 叠加态（相对于指定基，一种状态包含多个基态振幅）
- entanglement → 量子纠缠（复合系统状态无法写成各子系统状态的乘积；不允许超光速通信）
- decoherence → 退相干（系统与环境相互作用导致相干信息对局部观察者不可用）
- quantum gate → 量子门（作用于量子态的基本控制操作，理想封闭系统中通常建模为酉变换）
- quantum circuit → 量子电路（按时间或依赖关系排列的量子操作序列）
- circuit depth → 电路深度（从输入到输出经历的串行操作层数）
- gate fidelity → 门保真度（实际量子操作接近目标操作的程度；具体定义依实验协议而异）
- Bloch sphere → 布洛赫球（单量子比特状态的几何表示；纯态在球面，混合态在球内）

## Error correction

- quantum error correction (QEC) → 量子纠错（把逻辑信息编码到更大系统中，通过综合征检测和修正错误）
- fault-tolerant quantum computing (FTQC) → 容错量子计算（设计操作以限制错误传播，并在条件满足时压低逻辑错误）
- surface code → 表面码（在二维局域格点上定义稳定子检查的一类拓扑量子纠错码）
- stabilizer code → 稳定子码（用一组对易泡利算符的共同本征空间定义编码子空间）
- threshold theorem → 阈值定理（在特定噪声与纠错假设下，低于阈值的物理错误可通过增大编码开销被进一步压低）
- logical qubit → 逻辑量子比特（编码在多个物理自由度中的受保护信息单元，仍有非零逻辑错误）
- physical qubit → 物理量子比特（硬件直接实现并参与编码的量子自由度）
- syndrome → 错误综合征（不直接读取逻辑信息而揭示错误模式的测量结果）
- code distance → 码距（造成不可检测逻辑错误所需的最小错误权重）
- decoding → 解码（从综合征推断最可能错误并选择修正的过程）

## Algorithms

- Shor's algorithm → Shor 算法（利用周期查找实现多项式时间整数分解的量子算法）
- Grover's algorithm → Grover 算法（通过振幅放大将无结构搜索的查询复杂度降至平方根量级）
- QAOA → 量子近似优化算法（交替应用问题与混合哈密顿量的变分优化框架）
- VQE → 变分量子本征求解器（用参数化量子态和经典优化估计低能本征值）
- HHL algorithm → HHL 算法（在条件满足时制备与线性方程解向量成比例的量子态，而非直接输出全部经典分量）
- quantum Fourier transform → 量子傅里叶变换（离散傅里叶变换对应的酉变换，是相位估计等算法的组件）
- quantum phase estimation → 量子相位估计（估计酉算符本征相位的算法框架）
- Deutsch–Jozsa algorithm → Deutsch–Jozsa 算法（在承诺条件下区分常值与平衡布尔函数）
- Simon's algorithm → Simon 算法（寻找异或周期的量子算法，展示相对经典的指数级查询优势）
- Bernstein–Vazirani algorithm → Bernstein–Vazirani 算法（通过一次量子查询识别线性布尔函数的隐藏字符串）
- boson sampling → 玻色子采样（对线性光学网络输出分布进行采样的受限量子计算模型）

## Complexity

- BQP → 有界误差量子多项式时间（量子计算机以有界错误概率在多项式时间内求解的问题类）
- NP-hard → NP 困难（至少与 NP 中最难问题同样困难；不存在已知的通用量子高效算法）
- quantum supremacy → 量子计算优越性（量子设备完成经典方法在可行资源内难以复现的采样或计算任务）
- quantum advantage → 量子优势（量子方法在明确任务和指标上优于相关经典基线）
- QMA → 量子 Merlin–Arthur（允许量子证明和量子验证器的复杂度类）
- postBQP → 后选择 BQP（允许后选择的量子多项式时间复杂度类，等于 PP）

## Hardware

- superconducting qubit / transmon → 超导量子比特 / transmon（用超导电路能级编码量子信息的平台）
- trapped ion → 离子阱量子比特（用电磁场囚禁离子，并以内部能级编码和操控量子信息）
- topological qubit → 拓扑量子比特（利用非局域拓扑自由度保护信息的拟议方案）
- Majorana zero mode → 马约拉纳零模（拓扑超导候选体系中的零能准粒子激发，是若干拓扑量子计算方案的候选基础）
- dilution refrigerator → 稀释制冷机（为部分固态量子硬件提供毫开尔文温区的制冷设备）
- quantum annealer → 量子退火器（通过受控哈密顿量演化求解优化或采样问题的专用设备）
- adiabatic quantum computing → 绝热量子计算（利用足够缓慢的哈密顿量演化跟随瞬时本征态的计算模型）
- photonic quantum computing → 光量子计算（以光子自由度编码信息的平台，主要挑战包括损耗、源、探测和相互作用）
- neutral atom → 中性原子量子计算（用光镊阵列囚禁中性原子并通过受控相互作用实现计算）
- quantum dot → 量子点量子比特（在半导体量子点中编码和操控自旋或电荷自由度）

## Mathematical tools

- Hamiltonian → 哈密顿量（生成封闭系统时间演化并表示能量可观测量的算符）
- Hermitian matrix → 厄米矩阵（等于自身共轭转置、具有实特征值的矩阵）
- tensor network → 张量网络（用相连张量及指标缩并表示多体态或计算）
- Gibbs state / thermal state → 吉布斯态 / 热态（由哈密顿量和温度定义的平衡统计态）
- semidefinite programming (SDP) → 半正定规划（在线性矩阵不等式约束下优化线性目标的凸优化）
- density matrix / operator → 密度矩阵 / 密度算符（统一描述纯态、混合态和子系统状态的正半定迹一算符）
- unitary operator / matrix → 酉算符 / 酉矩阵（保持内积的线性变换）
- Pauli matrices → 泡利矩阵（`σx`、`σy`、`σz`，单量子比特算符和稳定子形式的基本构件）
- trace distance → 迹距离（衡量两个量子态可区分程度的度量）
- fidelity → 保真度（衡量量子态或量子操作相似程度的一族指标）

## Information and cryptography

- QKD (quantum key distribution) → 量子密钥分发（利用量子态测量扰动等性质建立可检测窃听的密钥协议）
- PQC (post-quantum cryptography) → 后量子密码学（设计为抵抗已知量子攻击的经典密码算法）
- QRAM (quantum random-access memory) → 量子随机存取存储器（允许地址叠加查询数据的理论存储模型）
- no-cloning theorem → 不可克隆定理（任意未知量子态不能被完美复制）
- quantum teleportation → 量子隐形传态（借助共享纠缠和经典通信传递未知量子态）
- superdense coding → 超密编码（借助预共享纠缠，用一个量子比特传递两个经典比特）
- Bell inequality → 贝尔不等式（局域隐变量理论满足的相关性界；量子实验可违反该界）
- EPR paradox → EPR 悖论（Einstein、Podolsky、Rosen 用于质疑量子力学完备性的思想论证）

## Sources

- Nielsen and Chuang, *Quantum Computation and Quantum Information*
- Preskill, *Quantum Computing in the NISQ era and beyond*
- Gottesman, *Stabilizer Codes and Quantum Error Correction*
- IBM Quantum Learning
- The Quantum Algorithm Zoo and original algorithm papers where applicable

Use these as starting points. For a paper-specific definition, prefer the paper and its cited primary source.
