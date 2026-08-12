---
layout: default
permalink: /paper-atlas/pfm-6a8a2bf9/
title: "PFM"
nav: false
description: "时间序列单细胞测量通常不是连续追踪同一批细胞，而是在若干时间点分别破坏性取样。输入因此是 K 个独立细胞群： 其中 \\mathbf x 是基因表达状态。每个时间点只告诉我们边缘分布 p{tk}(\\mathbf x)，并没有告诉我们哪一个早期细胞对应哪一个晚期细胞。"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}">
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>PFM</h1>
    <p>Learning biophysical models of gene regulation with probability flow matching</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2604.25062" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PFM：从离散单细胞快照学习可解释的随机基因调控动力学

### 1. 方法要解决什么问题

时间序列单细胞测量通常不是连续追踪同一批细胞，而是在若干时间点分别破坏性取样。输入因此是 $K$ 个独立细胞群：

$$
\mathcal X_k=\{\mathbf x_{i,t_k}\}_{i=1}^{n_k},
\qquad t_0<t_1<\cdots<t_{K-1},
$$

其中 $\mathbf x$ 是基因表达状态。每个时间点只告诉我们边缘分布 $p_{t_k}(\mathbf x)$，并没有告诉我们哪一个早期细胞对应哪一个晚期细胞。PFM（Probability Flow Matching）要从这些离散边缘分布恢复一个连续时间随机过程，并尽量把其中的漂移项解释为基因调控力、扩散项解释为分子噪声、增长项解释为细胞增殖或死亡。

这是一个非唯一的逆问题：许多不同的漂移和扩散组合都可能把观测分布插值得很好。论文的关键主张不是“插值误差最低的模型一定最好”，而是：**只有给动力学施加合理的生物物理结构，才能更可靠地恢复有符号调控关系，并外推到未见初始状态和基因扰动。**

### 2. 从随机过程到概率流速度

论文用带出生—死亡项的 Fokker–Planck 方程描述细胞状态密度：

$$
\frac{\partial p_t(\mathbf x)}{\partial t}
=-\nabla\cdot\bigl(\mathbf u_t(\mathbf x)p_t(\mathbf x)\bigr)
+g_t(\mathbf x)p_t(\mathbf x),
$$

其中概率流速度为

$$
\mathbf u_t(\mathbf x)
=\mathbf f(\mathbf x)
-\nabla\cdot\mathbf D(\mathbf x)
-\mathbf D(\mathbf x)\nabla\log p_t(\mathbf x).
$$

- $\mathbf f(\mathbf x)$ 是漂移/调控力，描述表达状态在没有随机扰动时如何改变。
- $\mathbf D(\mathbf x)=\mathbf G(\mathbf x)\mathbf G(\mathbf x)^\top$ 是扩散矩阵。
- $\nabla\log p_t(\mathbf x)$ 是 score，指向当前高概率区域。
- $g_t(\mathbf x)$ 是局部净增长率；平衡情形取零。

概率流 ODE 与相应随机微分方程在边缘密度层面一致，因此可以用确定性的速度回归来学习原本随机系统的密度演化。这里必须区分两件事：PFM 回归的是 $\mathbf u_t$，而生物学上想解释的是 $\mathbf f$。只有先估计 score 并指定 $\mathbf D$ 的形式，才能从概率流速度中分离出漂移。

### 3. 三阶段主流程

#### 3.1 阶段一：独立估计时间依赖 score

PFM 先用去噪 score matching（DSM）估计

$$
\mathbf s_\phi(\mathbf x,t)\approx\nabla\log p_t(\mathbf x).
$$

训练时把每个快照样本 $\mathbf x$ 加上不同尺度 $\sigma$ 的高斯噪声，网络输入实际为 $(\tilde{\mathbf x},\sigma,t)$，目标是恢复噪声扰动后的 score。代码 `pfi/score/solvers/_dsm.py` 构造

$$
\mathbf u_{\rm true}=
\frac{\tilde{\mathbf x}-\mathbf x}{\sigma^2},
$$

并最小化网络输出与 $-\mathbf u_{\rm true}$ 的加权平方误差。不同时间点的损失还通过梯度标准差自适应加权，避免某个快照主导训练。

score 训练完成后，`freeze_dsm_score()` 把噪声条件固定在训练噪声序列的最小值，而不是数学上的 $\sigma=0$。这给后续流模型一个稳定的近似 score。论文解释了“先估计、再冻结”可减少 score、漂移和扩散互相吸收误差造成的可辨识性问题。算法表把它称作 sliced score matching，但当前主入口默认使用 DSM；仓库同时保留 `_ssm.py`，因此文档应把“论文算法措辞”和“默认代码路径”区分开。

#### 3.2 阶段二：用多边缘 OT 组装跨时间条件轨迹

各时间点没有细胞配对，PFM 在每个 mini-batch 上计算多边缘耦合 $\pi^*$。当前 `pairwise_OT()` 实现通过相邻时间点的 $K-1$ 个 OT 计划串接轨迹。抽到一条条件轨迹

$$
\mathbf z=(\mathbf x_{t_0},\ldots,\mathbf x_{t_{K-1}})
$$

后，需要构造在这些节点之间连续、可微的均值路径 $\boldsymbol\mu_t(\mathbf z)$。

简单分段线性插值会在观测时间点产生速度跳变；局部三次样条在高维少样本条件下也可能不稳定。PFM 用 Chebyshev 多项式表示全局路径：

$$
Q(t)=\sum_{m=0}^{M}c_mT_m(s(t)),\qquad s(t)\in[-1,1].
$$

代码 `batched_chebyshev_interpolate()` 解带正则的最小二乘：

$$
\min_{\mathbf c}\|V\mathbf c-\mathbf x\|^2
+\lambda\mathbf c^\top R\mathbf c,
$$

并用第二类 Chebyshev 多项式解析计算 $\dot Q(t)$。`penalty="curvature"` 时对高阶系数施加近似 $m^4$ 权重，以抑制不必要的高频弯曲。图 2 的 OU 和 Waddington 型合成系统表明，在论文测试的高维、少样本范围内，Chebyshev 路径的漂移重建和数值收敛优于线性及三次样条。这个结论是特定基准结果，不应外推为 Chebyshev 在所有数据上必然最优。

随后以 $Q_t(\mathbf z)$ 为均值、固定方差构造条件高斯路径 $p_t(\mathbf x\mid\mathbf z)$。其条件速度可解析得到，因此无需在每次训练迭代中从起点数值积分到时间 $t$。

#### 3.3 阶段三：回归具有指定生物物理结构的概率流

平衡情形的条件 flow matching 损失可写为

$$
\mathcal L_{\rm CFM}
=\mathbb E_{t,\mathbf z\sim\pi^*,
\mathbf x\sim p_t(\cdot\mid\mathbf z)}
\left\|\mathbf u_t(\mathbf x\mid\mathbf z)
-\mathbf u_t^\theta(\mathbf x)\right\|^2.
$$

`pfi/flow/solvers/_pfm.py` 的训练循环执行：按时间点取 batch、计算 OT 耦合、采样轨迹与时间、拟合插值器、采样条件高斯点、计算目标条件速度，再更新网络。用户可以替换流模型，从而在同一训练框架下比较不同的漂移/扩散假设。

`PFI.fit()` 的当前组合入口明确体现两阶段顺序：先拟合 score，DSM 情形冻结 score，再将它挂到 flow 模型；默认还可以从 score 模型生成样本来训练 flow。这里类名 `PFI` 是软件 API 的历史命名，论文方法仍称 PFM，不应把两者误写成不同论文方法。

### 4. 不同动力学假设到底差在哪里

论文在同一 PFM 回归框架下比较若干模型：

- **TrajectoryNet++ / 非自治 ODE**：$\mathbf D=0$，漂移可显式依赖时间；表达力强，插值常很好，但不保证对应稳定的基因调控机制。
- **自治 ODE**：漂移只依赖 $\mathbf x$，仍没有扩散。
- **Additive Langevin**：加入常数扩散矩阵。
- **Multiplicative**：噪声幅度随状态变化；代码 `MultiplicativeFlow` 使用 $\sqrt{\mathbf x}$ 型随机项及相应概率流修正。
- **CLE（Chemical Langevin Equation）**：把转录生产与降解同时写入漂移和计数噪声，是论文最强调的生物物理模型。
- **PRESCIENT 型保守力**：$\mathbf f=-\nabla\phi$，约束很强；本地包中存在通用梯度流类，但没有发现论文评估所用 PRESCIENT 外部流程的完整封装与结果脚本。

CLE 中网络输出生产率 $\mathbf h(\mathbf x)$，线性降解为 $\ell\mathbf x$：

$$
\mathbf f(\mathbf x)=\mathbf h(\mathbf x)-\ell\mathbf x,
\qquad
\mathbf D(\mathbf x)\propto
\operatorname{diag}(\mathbf h(\mathbf x)+\ell\mathbf x).
$$

`CLEFlow.forward()` 直接实现这两个量，并计算 $\nabla\cdot\mathbf D$ 与 $\mathbf D\,\text{score}$ 的修正。因为漂移网络输出可解释为生产率，局部雅可比/响应矩阵可用于推断基因 $j$ 的变化对基因 $i$ 动力的影响。这比在 PCA/UMAP 低维空间中学到的速度更容易做基因级扰动，但仍是模型导出的局部响应，不等同于真实分子结合实验。

### 5. 为什么“插值得好”不等于“机制正确”

图 3 使用外周血生成体系的 24 个关键转录因子。PFM 比较多种动力学模型的留一时间点 energy distance。TrajectoryNet++ 等灵活确定性模型可以获得很低插值误差；然而对推断调控网络做验证时，结论发生变化：

1. 对 ChIP-seq 的无符号有向边比较，各模型都能捕捉部分细胞类型特异依赖。
2. 对需要同时恢复方向和激活/抑制符号的响应矩阵比较，包含分子随机性的 CLE 更能复现实验支持的红系与巨核系调控。

这正是论文的中心反例：两个模型可能生成几乎同样的观测边缘分布，却在分布之外拥有完全不同的力场。插值指标主要检验“能否连接快照”，而有符号网络、未见初态和扰动外推检验“是否学到了可迁移的机制”。

### 6. 未见条件外推与 in-silico knockout

图 4 把模型训练在一种 HSPC 起始分布上，再从独立数据中的 HSC/HSPC 状态出发预测终末细胞。预测细胞先与实验终点做 OT 对齐，再以配对表达的 Pearson 相关评价。论文报告 CLE 对红细胞和巨核细胞终态的外推较稳定。

基因敲除实验在模型内把 `KLF1` 或 `FLI1` 表达固定为零，再积分到终点。预期分别损害红系或巨核系命运。随机、尤其 CLE 模型更好地复现这种非对称结果；部分确定性模型错误地同时破坏两条谱系。

但这不是新的湿实验 knockout：它是依据既有生物学预期评估模型的计算干预。代码库包含冻结某一变量的网络机制，但公开快照没有论文全部数据预处理、训练配置和图 3–5 评估 notebook，因此本地包能证明模型具备干预接口，不能单独端到端重画所有结果。

### 7. 非平衡 PFM：同时学习流和细胞数量变化

细胞会增殖或死亡，各时间点总细胞质量不应总被归一化为 1。论文引入沿条件轨迹演化的质量

$$
\dot m_t(\boldsymbol\mu_t)
=m_t(\boldsymbol\mu_t)g(\boldsymbol\mu_t),
$$

并用质量权重修改 CFM：

$$
\mathcal L_{\rm CFM}
=\mathbb E\left[
\frac{m_t(\mathbf z)}{M_t}
\left\|\mathbf u_t-\mathbf u_t^\theta\right\|^2
\right].
$$

同时加入观测总质量匹配项

$$
\mathcal L_{g}
=\sum_k\left|\widehat M_{t_k}-M_{t_k}\right|,
\qquad
\mathcal L_{\rm total}
=\mathcal L_{\rm CFM}+\lambda_g\mathcal L_g.
$$

代码通过沿插值轨迹对增长网络积分得到质量权重，并根据两个损失的梯度尺度自适应更新 $\lambda_g$。这与论文目标一致，但具体数值实现并非逐字照搬定理中的 $m_t(\mathbf z)/M_t$ 抽样表达，因此代码映射应标为 Partial，而不是无条件 Exact。

图 5 先在带增长的双基因 toggle switch 上验证，再用于具有克隆条形码的中性粒细胞/单核细胞分化数据。不同模型得到相近的增长率图，却给出不同的命运概率；只有 CLE 在两类克隆细胞上都超过 50% 的随机二分类基线。它说明总量变化相似并不保证命运机制相同，也再次支持联合检查动力学结构和预测结果。

### 8. “simulation-free”应如何准确理解

PFM 的 simulation-free 是训练层面的术语：条件路径速度有解析形式，回归过程中不必像旧 PFI 那样每次迭代都求解高维 ODE 并计算边缘 Wasserstein 距离。图 S2 在论文的合成基准上报告约一个数量级的时间和内存改善。

它不表示：

- 不使用 OT；PFM 用 mini-batch 多边缘 OT 建立条件轨迹。
- 不使用合成模拟；论文的 OU、Waddington 景观和 toggle switch 基准来自模拟。
- 预测时不积分；从初态生成未来轨迹仍需调用 flow 的采样/积分器。
- 逆问题变得唯一；漂移与扩散的可辨识性仍取决于 score 质量、模型结构和数据覆盖。

### 9. 五张主图与补充材料的证据链

1. **图 1**：从单细胞边缘分布、随机基因表达过程到 PFM 的整体概念。
2. **图 2**：证明条件路径参数化会影响力场恢复；Chebyshev 在所测高维范围更稳。
3. **图 3**：在红系—巨核系分化中区分“插值最好”与“有符号调控机制最好”。
4. **图 4**：以独立初态和 KLF1/FLI1 计算 knockout 检验分布外泛化。
5. **图 5**：扩展到带增长/死亡的非平衡数据，并用克隆命运检验模型。

补充材料并非独立文件，而是同一 `paper.md` 后半部分的 Appendix A–C、Algorithm 1、表格和图 S1–S6。它给出非平衡 CFM 推导、OU 可辨识性分析、训练架构，以及 PFI 时间/内存比较和扰动结果。阅读主文时不能跳过这些部分，因为 Eq. (1) 的质量权重与 score objective 的精确定义主要在附录展开。

### 10. 论文—代码对应与复现边界

| 论文组件 | 本地代码 | 证据判断 |
|---|---|---|
| DSM score 估计与冻结 | `pfi/score/solvers/_dsm.py` | **Exact/直接实现**：噪声条件、损失、自适应权重和冻结入口可见 |
| 多边缘 OT 条件轨迹 | `pfi/flow/couplings.py` | **Partial**：以连续 pairwise OT 串接，属于论文 MMOT 的具体近似实现 |
| Chebyshev 路径及导数 | `pfi/flow/interpolants.py` | **Exact/直接实现**：基函数、正则线性系统和解析导数可见 |
| CFM 训练循环 | `pfi/flow/solvers/_pfm.py` | **Exact/直接实现**：耦合、插值、条件采样和速度回归齐全 |
| CLE 概率流 | `pfi/flow/models.py` | **Exact/直接实现**：生产、降解、扩散散度和 score 修正齐全 |
| 非平衡质量权重/增长损失 | `_pfm.py` 与 growth 网络 | **Partial**：目标一致，质量积分和加权是工程化离散实现 |
| PFM 两阶段组合 API | `pfi/_pfi.py` | **Exact/直接实现**：score → freeze → flow 顺序明确 |
| 图 3–5 数据预处理、ChIP AUPR、跨数据集评估 | 当前包内未发现 | **Not found**：论文有结果，库代码不足以重画全部图 |
| PRESCIENT 基线完整实现 | 当前包内未发现 | **Not found**：通用梯度流不能自动等同于论文基线流程 |

代码仓库更接近一个可安装的方法库，而不是论文复现实验仓库。`pyproject.toml`、测试和核心模型均存在，可验证基础 API 与关键公式；但 README 也说明单细胞数据分析将后续补充。缺少论文数据管道、固定环境、完整运行配置和作图脚本，因此“方法实现完整度”较高，“论文结果端到端复现度”只能评为中等。

### 11. 使用与解释时的限制

- 快照数据不能唯一确定真实细胞轨迹；OT 耦合是建模选择，不是谱系追踪。
- score 误差会通过概率流分解传播到漂移和扩散；先冻结只能减少耦合，不会消除误差。
- 论文在精选 TF 子空间中建模，不是全转录组无筛选地恢复完整 GRN。
- 模型雅可比是状态依赖的计算响应，ChIP-seq 是结合证据，两者并非同一测量对象。
- 计算 knockout 的正确方向支持泛化，却不能替代真实扰动实验的定量验证。
- 约一个数量级的加速、Chebyshev 优势和 CLE 最优结论都应限定在论文数据、参数和指标范围内。
- 非平衡增长需要可靠的相对群体质量或克隆信息；普通 scRNA-seq 每个时间点的捕获细胞数本身不等于真实组织细胞总量。

PFM 的真正价值不只是更快地连接几个时间点，而是把生成式 flow matching 变成一个可以放入漂移、扩散和增长假设的模型比较框架。论文最值得保留的实践原则是：**先用分布拟合筛除明显失败的模型，再用调控符号、未见初态、基因扰动和克隆命运检验动力学是否真的具有生物学可迁移性。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PFM — summary.md

### Motivation & Novelty

#### Biological Problem

Cellular differentiation is governed by gene regulatory networks (GRNs) — stochastic biochemical systems that determine cell fate. Single-cell RNA sequencing provides cross-sectional snapshots of the transcriptome, but inferring the underlying dynamics from these population-level observations is an ill-posed inverse problem. The challenge is compounded by high dimensionality, intrinsic noise, and the fact that individual cells cannot be tracked over time.

#### Limitations of Existing Approaches

| Method | Limitation |
|---|---|
| **RNA velocity** (La Manno et al., *Nature* 2018; Bergen et al., *Nature Biotechnology* 2020) | Assumes decoupled gene dynamics; ignores nonlinear regulatory interactions |
| **TrajectoryNet** (Tong et al., ICML 2020) | Deterministic ODE; no intrinsic noise; operates in PCA space |
| **PRESCIENT** (Yeo et al., *Nature Communications* 2021) | Conservative force (gradient of potential); isotropic diffusion; limited expressivity |
| **TIGON** (Sha et al., *Nature Machine Intelligence* 2024) | Simulation-based; requires repeated ODE solves; computationally expensive |
| **PFI** (Maddu et al., *PNAS* 2025) | Biophysically consistent but simulation-based; restricted to ~tens of genes and ~thousands of cells |
| **Schrödinger Bridge methods** (Bunne et al., AISTATS 2023) | Ignore stochasticity; work in reduced spaces |

#### Unique Contributions

1. **Simulation-free biophysical inference**: PFM learns stochastic dynamics directly from multi-marginal data without ODE solves during training, achieving ~10× speedup and ~10× memory reduction vs PFI.
2. **Chebyshev conditional paths**: Spectrally regularized Chebyshev interpolants for smooth multi-marginal conditional paths, outperforming linear and cubic spline interpolants in accuracy and convergence.
3. **Biophysical consistency matters**: Demonstrates that models with similar interpolation accuracy can encode fundamentally different dynamics — only CLE (Chemical Langevin) models accurately recover signed GRN interactions and generalize to unseen conditions.
4. **Unbalanced extension**: Extends flow matching to unbalanced populations, enabling simultaneous inference of gene-regulatory and cell proliferation/death dynamics.
5. **TF gene space**: Operates in transcription factor gene space (not generic PCA), providing mechanistically interpretable coordinates for gene regulation.

---

### Method Overview

PFM is a three-stage simulation-free framework:

**Stage 1 — Score Estimation**: Estimate the time-dependent score function $\nabla \log p_t(\mathbf{x})$ from snapshot data using denoising score matching (DSM). The score is estimated independently at each time point and frozen before flow regression.

**Stage 2 — MMOT Coupling**: Approximate the multi-marginal optimal transport coupling by chaining $K-1$ independent pairwise OT problems. This samples consistent cell trajectories $\mathbf{z} = (\mathbf{x}_0, \ldots, \mathbf{x}_{K-1})$ across all time points.

**Stage 3 — Flow Matching Regression**: Parameterize conditional paths using Chebyshev polynomial interpolants through the trajectory points. Regress the probability flow velocity field $\mathbf{u}_t^\theta(\mathbf{x})$ against the analytically available conditional velocities $\dot{\boldsymbol{\mu}}_t(\mathbf{z})$.

**Key biological assumption**: Dynamics operate in transcription factor (TF) gene space — a small subset of ~24 TF genes captures the essential regulatory architecture of hematopoietic differentiation.

**Key technical assumption**: The Chemical Langevin Equation (CLE) provides the correct biophysical model: production and degradation are Poisson processes, so diffusion is state-dependent and tied to the regulatory function.

For details, see `doc_method.md`.

---

### Evaluation

#### Datasets

| Dataset | Description | Time Points | Cells | Genes |
|---|---|---|---|---|
| Ex vivo CD34+ HSC (10X) | Human HSPC → erythroid/megakaryocytic | Days 2,4,6,8,11 | ~10K | 24 TFs |
| CITE-seq CD34+ HSC | Human HSPC differentiation (independent) | Multiple | ~10K | 24 TFs |
| Mouse HSPC (LARRY) | In vitro HSPC → neutrophil/monocyte, with lineage tracing | 6 days | ~10K | 24 TFs |
| Synthetic OU process | 2D Ornstein-Uhlenbeck (ground truth known) | 4 time points | 1000 | 2 |
| Synthetic Waddington | High-dimensional bifurcating landscape | 5 time points | Variable | 10-50 |

#### Metrics

- **Leave-one-out energy distance**: Interpolation accuracy (lower = better)
- **AUPR vs ChIP-seq**: GRN inference accuracy (unsigned directed interactions)
- **Cosine similarity**: Signed GRN interaction recovery (activation/inhibition)
- **Pearson correlation**: Generalization to unseen initial conditions (terminal cell identity)
- **Fate prediction accuracy**: Fraction of clonally tracked cells correctly assigned (vs LARRY barcoding)
- **RMSE**: Force field recovery on synthetic data

#### Key Results

1. **Interpolation**: TrajectoryNet+ and ODE achieve lowest leave-one-out energy distance; CLE is second; PRESCIENT is worst (overconstrains dynamics).

2. **GRN inference**: All models achieve similar AUPR vs ChIP-seq (unsigned). Only CLE recovers signed directed interactions (cosine similarity significantly higher for erythroid and megakaryocytic lineages).

3. **Generalization**: CLE maintains high Pearson correlation when initialized from unseen HSC populations (not in training data); deterministic models (TrajectoryNet+, ODE) show sharp correlation drop.

4. **In-silico KO**: CLE correctly predicts asymmetric lineage effects: KLF1-KO disrupts erythroid ($p=0.11$ vs megakaryocytes) while FLI1-KO disrupts megakaryocytic ($p=0.28$ vs erythrocytes). Deterministic models predict loss of both lineages.

5. **Growth dynamics**: CLE correctly predicts fate of >50% of clonally tracked cells (above random); TIGON++ is more deterministic in fate assignment.

6. **Scalability**: PFM achieves ~10× lower RMSE than PFI on synthetic data with ~10× less memory and ~10× faster training.

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is publicly available and well-structured as a Python package. Core algorithm (PFM training loop, CLE model, Chebyshev interpolation) is fully implemented and matches the paper. However, the main biological experiments (hematopoiesis generalization, GRN inference vs ChIP-seq) are in Jupyter notebooks that require downloading data from Zenodo and are not fully automated. Preprocessing steps (scanpy HVG selection, bi-whitening, TF gene selection) are described in the paper but not in the `pfi` package.

**Strengths**:
- Clean, modular Python package (`pfi`) with good documentation
- Data available on Zenodo (https://zenodo.org/records/19237708)
- Multiple model variants implemented (CLE, ODE, Additive, Multiplicative)
- Test suite covers core functionality

**Weaknesses**:
- Preprocessing pipeline not in library (requires manual scanpy steps)
- Main biological experiments in notebooks, not scripts
- PRESCIENT comparison requires external package
- Hyperparameter sensitivity not documented (which λ_g, which Chebyshev degree)
- No pre-trained models provided

**Environment setup**:
```bash
git clone https://github.com/vchz/pfi
cd pfi
pip install -e .
# Dependencies: torch, numpy, POT, geomloss, torchcubicspline, tqdm, optuna
```

**Common pitfalls**:
- `torchcubicspline` must be installed from git (not PyPI)
- Score estimation must complete before flow regression (two-stage pipeline)
- Chebyshev lambda auto-selection can be slow for large batches; pre-specify `reg` if known
- For CLE model, ensure `PositiveCLEFlow` (not `CLEFlow`) when h(x) can be negative

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
