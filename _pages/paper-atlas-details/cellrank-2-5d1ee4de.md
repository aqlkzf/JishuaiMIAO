---
layout: default
permalink: /paper-atlas/cellrank-2-5d1ee4de/
title: "CellRank 2"
nav: false
description: "CellRank 2 不是一种新的降维算法，也不直接从表达矩阵中“发现一棵谱系树”。它解决的是更具体的问题：给定单细胞数据以及一种或多种能够指示变化方向的证据，如何把这些证据统一写成细胞之间的转移概率，再用同一套马尔可夫链分析得到初始状态、终末状态、命运概率和与谱系相关的候选基因。 论文的核心设计是把任务拆成两层： kernel（核）层把 RNA velocity、伪时间、发育潜能、实验时间或预先计算的耦合等证据转换成转移矩阵；"
robots: noindex, nofollow
sitemap: false
---

<!-- Generated locally by bin/export_paper_atlas.py. -->
<section class="paper-detail" id="paper-detail">
  <a class="paper-detail__back" href="{{ '/paper-atlas/' | relative_url }}" data-atlas-back>
    <i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Back to Paper Atlas
  </a>
  <header class="paper-detail__hero">
    <div class="paper-detail__chips">
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>CellRank 2</h1>
    <p>CellRank 2: unified fate mapping in multiview single-cell data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02303-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellRank 2">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/cellrank" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellRank 2">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellRank 2 中文方法解读：从多视图局部转移到细胞命运概率

### 1. 它真正解决的是什么问题

CellRank 2 不是一种新的降维算法，也不直接从表达矩阵中“发现一棵谱系树”。它解决的是更具体的问题：给定单细胞数据以及一种或多种能够指示变化方向的证据，如何把这些证据统一写成细胞之间的转移概率，再用同一套马尔可夫链分析得到初始状态、终末状态、命运概率和与谱系相关的候选基因。

论文的核心设计是把任务拆成两层：

1. **kernel（核）层**把 RNA velocity、伪时间、发育潜能、实验时间或预先计算的耦合等证据转换成转移矩阵；
2. **estimator（估计器）层**只读取转移矩阵，不再关心它来自哪种数据视图。

这种拆分比“每种数据模态对应一套完整轨迹算法”更重要。它使同一个 GPCCA estimator 能分析 VelocityKernel、PseudotimeKernel、CytoTRACEKernel、RealTimeKernel 或它们的加权组合。论文 Fig. 1 给出了这条主线；Methods 将其写成“模态特异的转移建模 + 模态无关的轨迹推断”。

### 2. 共同语言：稀疏马尔可夫转移矩阵

设共有 $n$ 个细胞。CellRank 2 把每个细胞视为马尔可夫链中的一个状态，用矩阵

$$
T \in \mathbb{R}^{n\times n}, \qquad T_{ij}\geq 0, \qquad \sum_j T_{ij}=1
$$

表示从细胞 $i$ 向细胞 $j$ 变化的概率。多数 kernel 只允许在 k 近邻图或稀疏运输耦合支持的边上转移，因此 $T$ 通常是稀疏的。

这里有两个必须保留的解释边界。第一，$T_{ij}$ 是由模型和先验构造的局部转移概率，不是实验中直接观察到的谱系边。第二，论文假设变化是渐进且无记忆的，即下一步只依赖当前状态；真实细胞可能存在历史依赖、不可观测调控状态或离开转录组流形的跳跃，这些都不由该马尔可夫描述显式表达。

### 3. 各类 kernel 如何得到方向

#### 3.1 PseudotimeKernel：用已知顺序给邻居图定向

PseudotimeKernel 从无向的 k 近邻图出发。若细胞 $j$ 的伪时间晚于细胞 $i$，边 $i\to j$ 与发展方向一致；反向边则被删除或降权。源码 `kernels/_pseudotime_kernel.py` 的 `compute_transition_matrix()` 提供 hard 和 soft 两种 threshold scheme：hard 方案保留局部半径内的一部分逆向边，避免图被切断；soft 方案连续降低逆向边权重。最后再逐行归一化得到 $T$。

因此该 kernel 的信息来源不是表达矩阵本身，而是用户提供的伪时间及其起点假设。它适合起始状态较可靠、RNA velocity 假设可能失效的系统。论文 Fig. 2 的造血案例正是这个用法：DPT 给出顺序，PseudotimeKernel 将顺序变成局部转移，再由 GPCCA 求终末状态与命运概率。它不能反过来证明输入伪时间正确；伪时间错误会系统性地进入 $T$。

#### 3.2 CytoTRACEKernel：先估发育潜能，再复用伪时间核

CytoTRACEKernel 首先计算每个细胞表达的基因数，寻找与该数量正相关的基因，并聚合其中排名靠前基因的插补表达，得到 CytoTRACE score。高分被解释为更高的可塑性，随后构造

$$
p_{\mathrm{CytoTRACE}}=1-c_{\mathrm{CytoTRACE}},
$$

并交给 PseudotimeKernel 给邻居图定向。源码 `kernels/_cytotrace_kernel.py` 明确让 `CytoTRACEKernel` 继承 `PseudotimeKernel`；`compute_cytotrace()` 也明确记录 score、pseudotime、每细胞表达基因数和基因相关性。

这个设计避免了必须预先指定起始细胞，但代价是接受“未分化细胞平均表达更多基因”的假设。测序深度、归一化、插补与组织特异性都可能改变该信号。源码还明确说明其实现允许不同归一化和插补方法，因而不保证与原始 CytoTRACE 完全一致。论文 Fig. 3 和 Extended Data Figs. 4–5 支持它在所测系统中的表现，而不是对所有组织都成立的普遍保证。

#### 3.3 VelocityKernel：把 RNA velocity 变成邻居转移

VelocityKernel 比较细胞 $i$ 的速度向量与其指向邻居 $j$ 的状态差向量；方向越一致，转移权重越高。这样，RNA velocity 的连续向量场被离散为邻居图上的概率。它继承 velocity 模型的全部前提，包括剪接动力学、速率稳定性、测量噪声和邻居选择。论文造血案例中特意展示了这些前提被破坏时，velocity 给出的方向可能劣于可靠伪时间。

论文的代谢标记案例需要再划清一层：转录和降解速率以及 labeled velocity 是先在 scVelo 侧估计，然后作为 velocity 输入 CellRank 的 VelocityKernel；CellRank 2 在此承担下游转移和命运映射，而不是在当前 CellRank 源码中独立完成全部动力学速率估计。

#### 3.4 RealTimeKernel：把跨时间运输与时间点内相似性拼起来

离散时间序列中，不同时间点的细胞不是同一批细胞。RealTimeKernel 接收相邻时间点之间由 WOT、moscot 或用户预计算得到的 optimal-transport coupling，把它们放在全局矩阵的非对角块；同时把时间点内的 connectivity transitions 放在对角块。源码 `kernels/_real_time_kernel.py` 的构造器接受 couplings，`compute_transition_matrix()` 暴露 `self_transitions`、`conn_weight` 和 threshold 参数。

因此它与仅使用跨时间 pullback 的 WOT 分析不同：时间点内的转移让同一采样时刻的异步细胞也能沿表型流形移动。论文 Fig. 4 与 Extended Data Figs. 6–7 展示了这种组合如何提高状态分辨率。

熵正则 OT 往往产生稠密耦合。RealTimeKernel 的自适应阈值把很小的元素设为零，并选择不会让任何一行完全失去转移的阈值，再做归一化。这是计算加速与近似，不是新生物学证据。结果仍依赖 OT cost、增长率、批次校正、采样时间和时间点内 connectivity 权重。

#### 3.5 kernel 组合：显式合并证据，也显式引入权重判断

若已有两个逐行归一化的转移矩阵，可以构造

$$
T=\alpha T^{(1)}+(1-\alpha)T^{(2)}, \qquad 0\leq\alpha\leq1.
$$

例如论文按 CellRank 1 流程组合 0.8 的 VelocityKernel 与 0.2 的 ConnectivityKernel。组合的价值是把互补视图放入同一马尔可夫链；但 $\alpha$ 不是由 CellRank 自动识别出的“真实生物学贡献”。它是分析者选择，必须做敏感性检查，尤其是在两个视图方向冲突时。

### 4. GPCCA 如何从 $T$ 得到宏状态与终末状态

GPCCA estimator 使用转移矩阵的实 Schur 分解寻找近似不变的细胞集合，即 metastable macrostates。直观地说，如果一组细胞之间频繁互相转移、离开该组的概率较低，它会表现为一个稳定宏状态。源码入口在 `estimators/terminal_states/_gpcca.py`：`compute_macrostates()` 计算宏状态，随后根据粗粒化转移的稳定性及方向判断 initial/terminal states。

这一步不是简单地把现有聚类重命名为终末状态。宏状态来自 $T$ 的长期结构，但宏状态数量、谱结构、稳定性阈值和用户对终末状态的设定会影响结果。论文在多个案例中有时依据已知 cluster 选择终末状态，因此复现时必须区分“算法自动预测”与“论文基于已知生物学标签设定”。

### 5. 命运概率就是吸收概率

终末状态确定后，把其余细胞记为 transient states。按 transient/terminal 分块，可写为

$$
T=\begin{pmatrix}Q&S\\0&I\end{pmatrix}.
$$

到各终末谱系的命运概率矩阵 $X$ 满足

$$
(I-Q)X=S.
$$

源码 `estimators/mixins/_fate_probabilities.py` 的 `compute_fate_probabilities()` 先构造 transient block $Q$ 与通向各终末类别的 $S$，然后调用线性求解器。实现不是对每个终末细胞分别求解，而是先按终末类别聚合右端项，所以论文报告相对 CellRank 1 的约 30 倍加速；实际速度仍依赖矩阵稀疏度、求解器、硬件与问题条件数。

某细胞对谱系 $k$ 的概率高，准确含义是：在当前 $T$ 和当前终末状态定义下，从该细胞出发的随机游走最终被谱系 $k$ 吸收的概率高。它不是单细胞未来的实验确定结局，也不是对替代 kernel、权重或终末定义保持不变的客观常数。

### 6. lineage drivers 是相关性排名，不是因果调控网络

`compute_lineage_drivers()` 将基因表达与某条谱系的 fate probability 做相关分析，并可限制细胞群和谱系。随后可用 GAM 沿伪时间拟合表达趋势。它适合筛出与命运倾向共同变化的候选基因，例如论文中的 pDC、endoderm 和 mTEC 候选调控因子。

但“driver”是工作流中的候选名称。高相关可能来自细胞类型标记、共同上游因子、时间共变或技术混杂，不能单凭该排名断言基因导致了谱系选择。因果结论仍需扰动、谱系追踪或独立机制证据。

### 7. 图应该怎样读

- **Fig. 1**：从左到右读为数据视图 → kernel → 转移矩阵/组合 → estimator → 初末状态、命运概率和基因趋势。这是软件架构图，不是一次实验结果。
- **Fig. 2**：比较伪时间与 velocity 在造血中的方向证据。关键结论是 kernel 应按系统假设选取，而不是 velocity 必然更接近真实时间。
- **Fig. 3**：展示 CytoTRACE score 如何替代外部起点形成方向，并将命运概率用于 endoderm 相关基因排序。
- **Fig. 4**：重点比较仅跨时间 OT 与加入时间点内转移的 RealTimeKernel；mTEC fate probability 是后续候选基因排名的条件变量。
- **Extended Data Fig. 2**：支持可扩展性主张，但运行时间数字受数据规模、稀疏度、求解器和硬件约束。

随机游走和 embedding 上的流线都只是 $T$ 的可视化：它们让高维概率流更容易观察，但投影会压缩维度，单条模拟游走也不是实测细胞谱系。

### 8. 对应当前源码时的最短阅读路径

当前直接代码证据位于共享源码树 `[local path omitted]`，读取时的 Git commit 为 `206cc19ca89d985245ca204fbc86772e5c2446d0`。该目录是 CellRank 主仓库的当前开发快照，并非论文 Zenodo 归档的冻结副本，因此只能用于验证当前实现结构，不能把当前行号等同于论文发布版本。

建议按以下顺序读：

1. `kernels/_pseudotime_kernel.py` 与 `kernels/utils/_pseudotime_scheme.py`：邻居图定向；
2. `kernels/_cytotrace_kernel.py`：表达基因数、score 与伪时间；
3. `kernels/_real_time_kernel.py`：OT block、时间点内转移和稀疏化；
4. `kernels/_velocity_kernel.py`：velocity 到邻居转移；
5. `estimators/terminal_states/_gpcca.py`：宏状态与终末状态；
6. `estimators/mixins/_fate_probabilities.py`：吸收概率线性系统；
7. `estimators/mixins/_lineage_drivers.py`：基因—命运相关性。

### 9. 一个最小心智模型

可以把 CellRank 2 看成三句话：

1. 用最适合当前实验的证据给局部邻接关系加方向，形成稀疏 $T$；
2. 用 GPCCA 从 $T$ 的长期结构定义宏状态和终末状态；
3. 在这些条件固定后求吸收概率，并把它与表达相关联生成候选基因。

因此，可信结果不只取决于最后的线性求解。邻居图、kernel 假设、组合权重、OT 耦合、宏状态数和终末状态定义共同构成证据链。最有价值的验证不是只看 UMAP 箭头是否顺眼，而是改变这些选择后检查终末状态、命运概率排序和候选基因是否稳定，并用已知生物学或独立实验作外部检验。

### 10. 来源与复现边界

- 论文：`paper source/cellrank/cellrank.md`，包含正文、Methods、图注、Extended Data 与 Code availability。
- 图像：`paper source/cellrank/` 中的页面图像；OCR 图注存在少量排版噪声，面板解释以正文和图注交叉核对。
- 当前代码：共享 CellRank 主仓库 commit `206cc19ca89d985245ca204fbc86772e5c2446d0`，工作树非干净状态；本次仅只读核对，没有修改源码。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellRank 2: Unified Fate Mapping in Multiview Single-Cell Data

### Executive Summary

**Publication**: Nature Methods, Vol 21, pp. 1196-1205, June 2024 (doi: 10.1038/s41592-024-02303-9)
**Authors**: Philipp Weiler, Marius Lange, Michal Klein, Dana Pe'er, Fabian Theis
**Code Repository**: https://github.com/theislab/cellrank (BSD-3-Clause)
**Reproducibility Repository**: https://github.com/theislab/cellrank2_reproducibility
**Data**: FigShare collection at https://doi.org/10.6084/m9.figshare.c.6843633.v1
**Reproducibility Rating**: 5/5 (Excellent)

CellRank 2 is a modular, scalable framework for studying cellular fate decisions from multiview single-cell data. It generalizes the original CellRank (which was limited to RNA velocity) to handle diverse biological priors -- pseudotime, developmental potential, experimental time points via optimal transport, and metabolic labeling data -- through a unified kernel-estimator architecture that processes up to millions of cells.

### Motivation and Novelty

#### Problem Statement

Single-cell trajectory inference methods are each designed for a single data modality: CellRank v1 requires RNA velocity, WOT requires experimental time points, CytoTRACE estimates developmental potential but does not resolve trajectories, and dynamo handles metabolic labeling but relies on deterministic analysis. When the assumptions of any individual method are violated -- as they are for adult hematopoiesis with RNA velocity -- the analysis fails entirely. No framework existed that could:

1. Flexibly accommodate different data views (velocity, pseudotime, time points, metabolic labels)
2. Combine multiple views into a unified analysis
3. Scale to atlas-level datasets (>100K cells)
4. Provide consistent downstream analysis regardless of input modality

#### What CellRank 2 Changes (vs CellRank 1)

| Feature | CellRank 1 (2022) | CellRank 2 (2024) |
|---------|-------------------|-------------------|
| Input modalities | RNA velocity only | Velocity, pseudotime, CytoTRACE, time-series OT, metabolic labels |
| Architecture | Monolithic | Modular kernel + estimator |
| Scalability | Slow fate probabilities | 30x faster via pseudo-state aggregation |
| CytoTRACE | Not supported | Scales to 1.3M cells (original fails >80K) |
| Time-series | Not supported | RealTimeKernel with intra+inter-timepoint dynamics |
| Metabolic labeling | Not supported | Cell-specific transcription/degradation rate estimation |
| Kernel combination | Not supported | Weighted linear combination of arbitrary kernels |
| Visualization | Velocity projection only | Random walks, generalized projection for any k-NN kernel |

#### Key Innovation

The central insight is to decompose trajectory inference into two independent components:
- **Kernels**: Convert modality-specific biological signals into row-stochastic cell-cell transition matrices
- **Estimators**: Analyze any transition matrix via GPCCA to identify initial/terminal states, compute fate probabilities, and find lineage drivers

This decomposition means that adding a new data modality only requires writing a new kernel -- all downstream analysis is automatically available.

### Method Overview

#### Markov Chain Framework

CellRank 2 models cellular dynamics as a discrete-time Markov chain where each cell is a state and edges represent transition probabilities. The transition matrix $T \in \mathbb{R}^{n_c \times n_c}$ is row-stochastic ($\sum_j T_{ij} = 1$), encoding the probability that a cell in state $i$ transitions to state $j$.

#### Kernel Classes

1. **PseudotimeKernel**: Biases k-NN graph edges toward increasing pseudotime using soft ($f(\Delta t) = 2/(1+e^{b\Delta t})^{1/\nu}$) or hard thresholding. Works with any precomputed pseudotime (DPT, Palantir, etc.).

2. **CytoTRACEKernel**: Computes developmental potential from gene expression diversity (number of expressed genes per cell), converts to pseudotime, then applies PseudotimeKernel. Re-implemented with sparse operations for atlas-scale.

3. **RealTimeKernel**: Combines WOT-computed inter-timepoint transport maps with intra-timepoint k-NN similarity in a block transition matrix. Includes adaptive thresholding for sparsification of dense OT couplings.

4. **VelocityKernel**: Computes transitions from RNA velocity via cosine similarity, correlation, or dot product with softmax normalization. Supports deterministic, stochastic (JAX Hessian), and Monte Carlo models.

5. **ConnectivityKernel** and **PrecomputedKernel**: For basic k-NN transitions or user-provided matrices.

#### Estimator (GPCCA)

The Generalized Perron Cluster Cluster Analysis estimator:
1. Computes Schur decomposition of the transition matrix
2. Identifies macrostates via soft membership optimization
3. Classifies macrostates as initial, intermediate, or terminal (stability threshold >= 0.96)
4. Computes fate probabilities by solving $(I - Q)x = S$ (absorption probabilities)
5. Identifies lineage driver genes via correlation with fate probabilities

#### Kernel Combination

Kernels support algebra: $T = \alpha T^{(1)} + (1-\alpha) T^{(2)}$ with automatic normalization of weights.

### Evaluation and Benchmarks

#### Datasets and Quantitative Results

| Dataset | n_cells | Application | Best Kernel | TSI Score | Comparator | Comparator TSI |
|---------|---------|-------------|-------------|-----------|------------|----------------|
| Human hematopoiesis (PBMC) | 24,440 | Pseudotime fate mapping | PseudotimeKernel | 0.90 | VelocityKernel | 0.81 |
| Embryoid bodies | 31,029 | CytoTRACE dev. potential | CytoTRACEKernel | 10/11 terminal states | Palantir/DPT | Compressed pseudotime |
| MEF reprogramming | 165,892 | Time-series fate mapping | RealTimeKernel | 1.0 | VelocityKernel | 0.79 |
| Pharyngeal endoderm | 55,044 | Time-series, mTEC lineage | RealTimeKernel | 0.92 | VelocityKernel | 0.46 |
| Mouse organogenesis atlas | 1,300,000 | Scalability benchmark | CytoTRACEKernel | <2 min | Orig. CytoTRACE | Fails >80K |
| Intestinal organoids (scEU-seq) | ~10,000 | Metabolic labeling | VelocityKernel (labeling) | 0.81 | CellRank 1 / dynamo | 0.71 / 1 of 4 |

#### Biological Discoveries

1. **Hematopoiesis** (PseudotimeKernel): Correctly recovered pDC, cDC, monocyte, normoblast lineages; identified RUNX2 and TCF4 as pDC lineage drivers, outperforming VelocityKernel (6/8 CBC transitions).

2. **Embryoid body endoderm** (CytoTRACEKernel): Recovered LINC00458 -> NODAL -> FOXA2 temporal activation cascade; identified 9 TFs peaking before FOXA2/SOX17, all validated in mouse endodermal literature.

3. **Pharyngeal endoderm mTEC** (RealTimeKernel): Discovered putative mTEC progenitor population that WOT missed entirely. Recovered Grhl3, Sfn, Perp (p53 pathway), Pvrl4, Cd9 as mTEC drivers. RealTimeKernel found substantially more relevant drivers than WOT pullback or classical differential expression.

4. **Intestinal organoids** (metabolic labeling): Revealed cooperative (increased transcription, decreased degradation) and destructive (both rates increase) regulatory strategies for goblet cell differentiation.

#### Performance Metrics

- **30x faster** fate probability computation vs CellRank v1 (pseudo-state aggregation)
- **9x faster** macrostate computation with thresholded vs dense transport maps
- **56x faster** fate probability computation with thresholded RealTimeKernel
- CytoTRACEKernel: **1.3M cells in <2 minutes** (original fails at 80K)
- Thresholding preserves fate probabilities: Pearson $r > 0.99$ per lineage on MEF data

#### Cross-Boundary Correctness (CBC) Score

$$\beta^{(\kappa)}(j) = \text{corr}(v(j), v^{(\kappa)}(j))$$

Measures alignment between kernel-derived and empirical cell transitions.

#### Terminal State Identification (TSI) Score

$$\text{TSI}(\kappa) = \frac{\sum_{n=1}^{N_{\max}} f_\kappa(n)}{\sum_{n=1}^{N_{\max}} f_{\text{opt}}(n)} = \frac{2}{m(1+N_{\max}-m)} \sum_{n=1}^{N_{\max}} f_\kappa(n)$$

Quantifies terminal state recovery relative to an optimal identification strategy.

### Code-Paper Correspondence

#### Verified Equation Implementations

| Paper Equation | Code Location | Status |
|----------------|---------------|--------|
| Soft threshold $f(\Delta t)$ | `_pseudotime_scheme.py:202-211` | Exact match |
| Hard threshold (Palantir-style) | `_pseudotime_scheme.py:118-168` | Exact match |
| GEC calculation | `_cytotrace_kernel.py:180` | Exact match |
| CytoTRACE normalization | `_cytotrace_kernel.py:196-197` | Exact match |
| CytoTRACE pseudotime $1 - c$ | `_cytotrace_kernel.py:200` | Exact match |
| Velocity projection | `_velocity_kernel.py:112-180` | Exact match |
| Kernel combination $\alpha T^{(1)} + (1-\alpha)T^{(2)}$ | `_base_kernel.py:927-957` | Exact match |
| CBC score | `_base_kernel.py:553-588` | Exact match |
| Embedding projection | `_projection.py:90-106` | Exact match |
| TSI score formula | `_gpcca.py:541-620` | Exact match |
| Absorption probability solver $(I-Q)x=S$ | `_fate_probabilities.py:441-488` | Exact match |
| RealTimeKernel block matrix | `_real_time_kernel.py:349-454` | Exact match |
| Adaptive threshold | `_real_time_kernel.py:457-515` | Exact match |

#### Hidden Implementation Details

1. **Complex conjugate eigenvalue handling** (`_gpcca.py:204-214`): Automatically increments n_states by 1 when GPCCA optimization would split conjugate eigenvalue pairs. Not documented in paper.

2. **Auto-softmax scale** (`_velocity_kernel.py:248-256`): Estimates `softmax_scale = 1/median(|logits|)` when not provided. Critical for numerical stability.

3. **Velocity model fallback** (`_velocity_kernel.py:199-212`): STOCHASTIC mode requires JAX for Hessian; falls back to MONTE_CARLO. Backward mode only supports DETERMINISTIC.

4. **KernelAdd weight normalization** (`_base_kernel.py:935-943`): Constants auto-normalized to sum to 1 in kernel addition, and child normalization is disabled.

5. **30x speedup mechanism** (`_fate_probabilities.py:424-428`): Sums S matrix columns for all representative cells into one pseudo-state column before solving, reducing from $n_f$ linear systems to 1.

### Compared Methods

| Method | Journal | Year | Relationship to CellRank 2 |
|--------|---------|------|---------------------------|
| CellRank v1 | Nature Methods | 2022 | Predecessor; RNA velocity only |
| WOT | Cell | 2019 | Inter-timepoint OT; no intra-timepoint dynamics |
| Palantir | Nature Biotechnology | 2019 | Pseudotime + fate; inspired hard threshold |
| dynamo | Cell | 2022 | Metabolic labeling; deterministic, steady-state |
| CytoTRACE | Science | 2020 | Developmental potential; does not scale |
| DPT | Nature Methods | 2016 | Diffusion pseudotime input |
| scVelo | Nature Biotechnology | 2020 | RNA velocity estimation |
| VIA | Nature Communications | 2021 | Soft threshold inspiration |
| UniTVelo | Nature Communications | 2022 | CBC score definition |
| velvet | bioRxiv | 2023 | Metabolic labeling; no transcription rates |
| storm | bioRxiv | 2023 | Metabolic labeling; cell-specific only in post-processing |
| PAGA | Genome Biology | 2019 | Graph abstraction TI |
| Slingshot | BMC Genomics | 2018 | TI baseline |
| LineageOT | Nature Communications | 2021 | Lineage tracing + OT |
| CoSpar | Nature Biotechnology | 2022 | Lineage tracing fate bias |
| moslin | bioRxiv | 2023 | Lineage tracing + CellRank 2 |
| moscot | bioRxiv | 2023 | Spatiotemporal OT + CellRank 2 |

### Reproducibility Assessment

#### Strengths

1. Complete open-source code under BSD-3-Clause with active development
2. Dedicated reproducibility repository with all analysis notebooks
3. All datasets deposited on FigShare with DOIs
4. Comprehensive documentation with tutorials for each kernel
5. All paper equations verified in code with exact correspondence
6. Integration with scverse ecosystem (Scanpy, scVelo, AnnData)

#### Potential Limitations

1. **PETSc dependency**: Optional but recommended for large-scale; installation can be complex
2. **scVelo dependency**: Metabolic labeling rates inferred via scVelo
3. **Random seed sensitivity**: Monte Carlo models and iterative solvers
4. **Schur decomposition**: O($n^2$) memory limits practical size to ~1M cells
5. **k-NN graph quality**: All kernels depend on neighbor graph quality

#### Rating Justification: 5/5

- Every equation verified in code with exact correspondence
- Complete data availability with DOIs
- Reproducibility notebooks provided
- Active maintenance and broad community adoption
- Metabolic labeling integration validates new experimental modalities

### Usage Recommendations

**Choose PseudotimeKernel** when: initial state is known, differentiation is unidirectional, RNA velocity assumptions are violated.

**Choose CytoTRACEKernel** when: initial state is unknown, early developmental system, gene count diversity correlates with stemness.

**Choose RealTimeKernel** when: time-course data is available, within-timepoint resolution is needed, WOT transport maps can be computed.

**Choose VelocityKernel** when: RNA velocity assumptions are satisfied, strong transcriptional dynamics exist.

**Combine kernels** when: multiple signals are available and complementary; use biological knowledge to set weights.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
