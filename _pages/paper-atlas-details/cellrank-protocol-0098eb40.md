---
layout: default
permalink: /paper-atlas/cellrank-protocol-0098eb40/
title: "CellRank Protocol"
nav: false
description: "CellRank 不负责从原始 counts 独立发现全部动力学，而是一个“转移矩阵后端”：先把 RNA velocity、pseudotime、CytoTRACE、实验时间/OT 或已有相似图转成细胞间转移概率，再用 GPCCA 把大规模 Markov chain 粗粒化成 macrostates，定义初始/终末状态，并计算每个细胞最终到达各终末状态的概率。"
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
      <span>Nature Protocols · 2026</span>
    </div>
    <h1>CellRank Protocol</h1>
    <p>CellRank: consistent and data view agnostic fate mapping for single-cell genomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41596-025-01314-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellRank Protocol">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/cellrank" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellRank Protocol">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellRank Protocol 中文解读：从多种方向信息到细胞命运概率

### 先给结论

CellRank 不负责从原始 counts 独立发现全部动力学，而是一个“转移矩阵后端”：先把 RNA velocity、pseudotime、CytoTRACE、实验时间/OT 或已有相似图转成细胞间转移概率，再用 GPCCA 把大规模 Markov chain 粗粒化成 macrostates，定义初始/终末状态，并计算每个细胞最终到达各终末状态的概率。后续再用这些概率寻找相关基因或拟合 lineage-specific expression trends。

这篇 Nature Protocols 论文是操作协议，不是新的独立算法 benchmark。它提供四个可复用流程、参数选择、迭代检查和故障排除。工作区包含完整协议 PDF/OCR 和 22 张本地图，但没有协议作者给出的 `cellrank_protocol` 分析仓库快照。可读取的 CellRank 包源码位于父目录 `cellrank/src/cellrank`；它是当前共享仓库中的无独立上游 commit 标记源码。因此下面把“论文协议代码”“当前本地 API 实现”和“缺失的精确复现实验环境”严格分开。

### 1. 三层结构：Kernel、Estimator、Downstream

#### 1.1 Kernel：把证据变成转移概率

所有 kernel 最终都产生一个行归一化矩阵 $T$：

$$
T_{ij}=P(X_{t+1}=j\mid X_t=i).
$$

一行描述从细胞 $i$ 出发，下一小步落到邻居 $j$ 的概率。不同 kernel 的区别是“用什么证据给边定方向”。

- `ConnectivityKernel`：把无向相似图变成基线随机游走；它没有时间方向。
- `PseudotimeKernel`：在 kNN 图上抑制逆 pseudotime 边。hard scheme 删除大部分逆向边但保留局部邻居，soft scheme 连续下调逆向边。
- `CytoTRACEKernel`：从表达基因数和共表达基因计算 stemness score，再复用 pseudotime 思路朝低 potential 方向偏置。
- `VelocityKernel`：比较细胞 velocity $v_i$ 与邻居表达差 $x_j-x_i$ 的 correlation/cosine/dot product，再转为局部概率。
- `RealTimeKernel`：使用不同时点之间的 OT coupling，并在同一时点内加入 connectivity transitions。
- `PrecomputedKernel`：接受外部已经计算好的转移矩阵。

kernel 的“data-view agnostic”是说后续 estimator 只读取 $T$，不是说输入证据没有假设。velocity、pseudotime、CytoTRACE 和 OT 各自的偏差会传递到命运概率。

#### 1.2 Estimator：从 Markov chain 找粗粒化状态

协议使用 GPCCA。它对 $T$ 做 real Schur decomposition，在主导 Schur 子空间寻找近似不变的 cell sets，并给出 soft membership。宏观转移矩阵可概念化为

$$
T_c=(\chi^\top D\chi)^{-1}\chi^\top D T\chi,
$$

其中 $\chi$ 是细胞对 macrostates 的 membership，$D$ 是权重矩阵。这里的关键不是公式本身，而是 macrostates 是 Markov dynamics 的粗粒化，不等同于聚类标签。

用户仍需决定/评估 macrostate 数量。eigengap 是启发式，不是真值；协议 Procedure 1 从 4、7 一直试到 15，才覆盖预期终末类型。这是协议最值得保留的实践信息：自动谱分解不能替代生物学审查。

#### 1.3 Downstream：解释 fate bias

给定 terminal states，fate probability 是从当前细胞出发最终被各终态吸收的概率。若把 transient-to-transient 块写成 $Q$，transient-to-terminal 块写成 $R$，则吸收概率满足

$$
B=(I-Q)^{-1}R,
$$

实际代码用直接或迭代线性求解器计算。它回答“在这个 Markov 模型下最终到哪个终态”，不返回一条唯一最可能路径，也不证明真实克隆后代。

协议再计算 lineage drivers：基因表达与某 lineage fate probability 的相关性。高相关基因是 putative drivers，可能是下游 marker、共变因子或混杂变量，不是因果调控证据。GAM trend 用 fate probability 作为 lineage weight，展示随 pseudotime 的加权表达趋势，同样是条件关联。

### 2. Procedure 1：CytoTRACEKernel

输入是处理好的 human bone marrow AnnData。CytoTRACE score 以检测到的基因数为 stemness proxy，再把高 stemness 到低 stemness的方向写入图。

流程为：计算 CytoTRACE → 构建转移矩阵 → GPCCA Schur → 多次尝试 macrostates → TSI 检查 → 人工设置 terminal states → fate probabilities → CBC。

本例故意展示失败过程：4 和 7 个 macrostates 都不能覆盖预期终态，15 个才包含 monocyte 等状态。终态随后按已有 cell-type knowledge 人工设置。因此最终 fate probabilities 不是完全无监督发现；它们是“CytoTRACE 转移 + 选择的 macrostates + 人工终态”的条件结果。

CytoTRACE 的表达基因数假设在造血等分化系统常有用，但受到测序深度、细胞大小、RNA complexity 和批次影响。协议要求用已知终态和转移评价，而不能把 stemness score 当作普适发育时间。

### 3. Procedure 2：PseudotimeKernel

Pseudotime 已由 Palantir 等上游方法计算并存入 `adata.obs`。CellRank 不重新验证 pseudotime 的 root、拓扑或单调性，只把 kNN edges 朝递增时间偏置。

本地当前源码 `src/cellrank/kernels/_pseudotime_kernel.py:79-157` 默认 `threshold_scheme="hard"`；协议示例显式使用 soft scheme。因此“协议参数”不能等同于“包默认值”。hard 保留部分逆向近邻防止图断裂；soft 用连续函数降权逆向边。两者会改变 $T$ 的不可约性、macrostates 和 fate probabilities。

本例用 5 个 macrostates 时缺失 cDC，改为 6 后恢复；自动稳定性阈值 0.96 又可能遗漏终态，协议演示人工修正。随后 MEP fate probability 揭示一个 cluster 内部的 bias，并用相关基因/GAM 做解释。这里“未观察到 megakaryocyte 终态”的推断尤其依赖手工终态定义和已知生物学，不能单凭圆形投影证明新命运。

### 4. Procedure 3：VelocityKernel 与 kernel combination

VelocityKernel 要求 upstream velocity 已经存入 `adata.layers` 或 `obsm`，还要有对称邻接图。当前源码 `src/cellrank/kernels/_velocity_kernel.py:24-160` 支持 deterministic、stochastic、monte_carlo 和 correlation/cosine/dot-product 等选择。

协议在 spermatogenesis 数据上计算 velocity transitions，再用

$$
T=0.8T_{velocity}+0.2T_{connectivity}
$$

加入相似图正则。这个 4:1 权重是示例选择，不是由模型自动学习。ConnectivityKernel 常改善数值条件并避免 velocity 噪声导致断裂，但也会稀释方向。论文明确说组合权重是全局的，未来 cell-specific weighting 可能更合理。

VelocityKernel 不修复 RNA velocity 本身的恒速率、内部引物、平滑和基因选择偏差。它只是把已有 velocity 映射成 neighbor transitions。因此 Fate probability 的不确定性至少包含两层：velocity inference 与 CellRank Markov analysis。

### 5. Procedure 4：RealTimeKernel 与 OT

RealTimeKernel 使用实验时间点。协议先用 moscot `TemporalProblem` 计算相邻时点 OT coupling，再 `RealTimeKernel.from_moscot()` 导入，并加入同一时间点的 connectivity transitions。

跨时间 coupling 受 OT cost、低维表示、entropic regularization、unbalanced mass 和时间采样影响。相邻时点间隔太大时，中间状态没有被观测，任何 coupling 都无法恢复缺失过程；太密或批次不平衡也会改变 transport。CellRank 的 RealTimeKernel 不是自己解决这些辨识问题，而是组合 inter-time OT 和 intra-time graph。

协议还依赖外部 `moscot`。当前 CellRank 源码中 `RealTimeKernel.from_moscot` 存在，但精确复现需要与论文兼容的 moscot、ott-jax、AnnData 和数据版本。协议只说安装“latest compatible versions”，没有冻结完整 lockfile，长期复现存在漂移风险。

### 6. TSI 和 CBC 到底衡量什么

TSI 比较随着 macrostate 数增加，已知 terminal states 被恢复的速度，并把曲线下面积相对于理想曲线归一化。它需要一个先验终态集合，因此不能用于完全未知系统中证明终态是真的。

CBC 衡量 source cluster 到 target cluster 边界附近的 transition direction 是否符合已知转移。单个 CBC 没有自然基线，协议更推荐比较两个 kernel 的 log ratio。本例 PseudotimeKernel 在特定 hematopoiesis 数据上优于 CytoTRACEKernel，不是跨数据集的普适排序。

两者都用 prior knowledge 进行相对模型检查，这是优点；但如果“ground truth”来自同一套 marker/annotation，可能产生循环验证。

### 7. 图像证据如何阅读

本地 22 张图已逐张检查。

- Figure 1 是模块流程图，说明 kernel → estimator → downstream，不是性能证据。
- Figure 2 展示 CytoTRACE 的 eigenvalues、4/7/15 macrostates、TSI 和人工 terminal states。最重要的证据是解对 state-number choice 很敏感。
- Figure 3 展示 pseudotime workflow、自动/人工 terminal states、fate probabilities、MEP-correlated genes 和 GAM trends。驱动基因图是相关排序。
- Figure 4 直接比较 PTK 与 CTK 的 TSI/CBC，只支持本数据及指定 prior transitions。
- Figure 5 展示 weighted kernels 和 time-resolved dataset；主要是协议可组合性说明。
- Extended Data Figure 1 展示不同 terminal-state 选择下 fate maps 的变化，进一步说明 terminal definition 是结果条件。

UMAP 上颜色连续不等于真实物理连续；macrostates 的轮廓和 fate gradients 是高维 Markov 结果在二维上的显示。

### 8. 协议自身列出的限制

论文明确承认：

- RNA velocity 有实验与动力学模型偏差；
- pseudotime 常假设单向分化并可能需要 root；
- time-series 需要合适采样间隔；
- Markov memorylessness 忽略 delayed/protein accumulation 和 rare states；
- CellRank 不给出 most probable path，难处理 convergence；
- lineage drivers 是 correlation，缺乏 causality；
- 自动 terminal-state number 在噪声数据上不稳定；
- kernel weights 是 global；
- destructive sequencing 缺乏真实单细胞 fate ground truth。

这些不是附带免责声明，而是解释输出的核心条件。

### 9. paper–code 对应

#### Exact / 当前源码直接存在

- PseudotimeKernel hard/soft schemes；
- VelocityKernel 的多种 similarity 和 velocity models；
- CytoTRACEKernel score → pseudotime inheritance；
- RealTimeKernel.from_moscot 与 intra-time transitions；
- kernel arithmetic 的 weighted sum；
- GPCCA Schur、macrostates、terminal states、fate probabilities；
- TSI、CBC、lineage drivers 和 plotting modules。

#### Partial

- 协议代码块与当前 API 大体一致，但本地源码是共享父目录中的当前快照，无协议发表时 commit/tag 元数据；API/default 可能已漂移。
- Protocol 提到 CellRank 1/2 兼容性，但“其余 Python 包不变”是重要条件；不同 scvelo/pygpcca/scipy 会改变数值结果。

#### Not found / MISSING

- 论文所说 `theislab/cellrank_protocol` 分析仓库的本地快照；
- 协议使用数据和每图输出的固定 commit、完整 lockfile、seed 和运行记录；

因此最诚实的模式仍是 `paper+code`，但 `code source` 是只读外部同仓源码，不是 protocol workspace 内的已获取快照。

### 10. 最安全的分析实践

一个可信的 CellRank 分析应留下完整审计链：上游 velocity/pseudotime/OT 的版本与参数；邻接图；kernel 参数和组合权重；Schur spectrum；尝试过的 macrostate 数；自动与人工 terminal states；solver/tolerance；TSI/CBC 的 prior definition；以及 fate probability 对这些选择的敏感性。

结果表述应使用条件语言：“在给定 kernel、macrostate 和 terminal-state 定义下，细胞对某终态具有较高吸收概率。”不要写成“该细胞必然分化成 X”。Driver ranking 用于提出实验候选，不能替代 perturbation 或 lineage tracing。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellRank Protocol -- Summary

### Paper Information

| Field | Value |
|-------|-------|
| **Title** | CellRank: consistent and data view agnostic fate mapping for single-cell genomics |
| **Authors** | Philipp Weiler, Fabian J. Theis |
| **Journal** | Nature Protocols |
| **Year** | 2026 |
| **DOI** | 10.1038/s41596-025-01314-w |
| **Code** | https://github.com/theislab/cellrank |
| **Protocol Repo** | https://github.com/theislab/cellrank_protocol |
| **Data** | https://doi.org/10.6084/m9.figshare.c.7752290.v1 |

### One-Sentence Summary

A step-by-step practical guide for applying CellRank's modular kernel-estimator-analysis framework to infer cell fate probabilities from single-cell RNA sequencing data across diverse data views including pseudotime, RNA velocity, stemness scores, and experimental time points.

### Practical Value and Target Audience

This Protocol targets computational biologists and bioinformaticians with basic Python and single-cell genomics knowledge who need to perform trajectory inference and fate mapping on scRNA-seq data. It provides concrete, reproducible workflows that bridge the gap between CellRank's method papers (CellRank 1, Nature Methods 2022; CellRank 2, Nature Methods 2024) and practical application. The Protocol does not introduce new methodology but instead delivers four end-to-end procedures with explicit parameter choices, troubleshooting, and timing benchmarks.

### What This Adds Beyond CellRank 1 and CellRank 2 Papers

1. **Concrete step-by-step instructions** with numbered procedures, code blocks, and expected outputs, rather than algorithmic descriptions.
2. **Iterative macrostate selection workflow** -- demonstrates the practical challenge of choosing the number of macrostates through eigenvalue analysis and iterative refinement (4 -> 7 -> 15 macrostates in Procedure 1).
3. **Systematic kernel comparison** -- shows how to quantitatively compare kernel performance using TSI and CBC scores with statistical testing (Welch's t-test on log CBC ratios).
4. **Troubleshooting table** -- documents common numerical failures and their solutions based on community experience.
5. **Timing benchmarks** -- concrete runtimes on consumer hardware (MacBook Pro, 14-core, 48GB RAM).
6. **RealTimeKernel workflow** -- first detailed protocol for combining OT-based (moscot) inter-time-point couplings with intra-time-point similarity.

### Three-Stage Architecture

CellRank divides into three modular stages:

#### Stage 1: Kernels (Cell-Cell Transition Probabilities)

Six kernels translate different data views into cell-cell transition matrices:

| Kernel | Input | Use Case |
|--------|-------|----------|
| **CytoTRACEKernel** | GEX + kNN graph | No prior ordering; uses gene count as stemness proxy |
| **PseudotimeKernel** | Pseudotime + kNN graph | When pseudotime is available (Palantir, DPT, etc.) |
| **VelocityKernel** | RNA velocity + kNN graph | Splicing dynamics accessible (standard scRNA-seq) |
| **RealTimeKernel** | OT couplings + time points | Time-resolved experiments |
| **ConnectivityKernel** | kNN graph | Regularization; combines with other kernels |
| **PrecomputedKernel** | User-supplied matrix | External transition matrices |

Kernels can be combined via weighted sums: e.g., `0.8 * VelocityKernel + 0.2 * ConnectivityKernel`.

#### Stage 2: Estimators (Markov Chain Analysis)

The GPCCA estimator coarse-grains the transition matrix via Schur decomposition:
1. Compute Schur decomposition (eigenvalues guide macrostate count)
2. Identify macrostates (coarse-grained cell populations)
3. Classify terminal states (by stability threshold >= 0.96 or manual selection)
4. Compute fate probabilities (absorption probabilities in the Markov chain)

#### Stage 3: Downstream Analysis

- **Lineage drivers**: genes whose expression correlates with fate probabilities
- **Gene trends**: GAM-fitted expression over pseudotime, weighted by fate probabilities
- **TSI score**: quantifies terminal state recovery quality
- **CBC score**: measures kernel fidelity to known state transitions

### Four Procedures

#### Procedure 1: CytoTRACEKernel on Hematopoiesis (CD34+ Human Bone Marrow)
- Demonstrates iterative macrostate selection (4 -> 7 -> 15) driven by biological expectation of 5 terminal states
- Shows TSI score computation and manual terminal state setting
- Highlights CytoTRACE's bias toward erythroid lineage

#### Procedure 2: PseudotimeKernel on Hematopoiesis
- Uses Palantir pseudotime; eigengap suggests 5-6 macrostates
- Automatic terminal state prediction (stability >= 0.96) identifies 6 states including MEP
- Discovers MEP as biologically meaningful terminal state via lineage driver analysis (ITGA2B, VWF, PLEK)
- Quantitative comparison with CytoTRACEKernel via CBC log odds ratio (PseudotimeKernel outperforms)

#### Procedure 3: VelocityKernel on Spermatogenesis
- Demonstrates kernel combination: 80% VelocityKernel + 20% ConnectivityKernel
- Shows velocity-based transition matrix setup; subsequent steps equivalent to Procedures 1-2

#### Procedure 4: RealTimeKernel on Time-Resolved Hematopoiesis (LARRY)
- Uses moscot OT for inter-time-point couplings
- Incorporates intra-time-point dynamics via self_transitions="all" and conn_weight=0.2
- Most computationally expensive procedure (39.4s for OT coupling alone)

### Key Parameters and Defaults

| Parameter | Default | Protocol Value | Effect |
|-----------|---------|---------------|--------|
| threshold_scheme (PseudotimeKernel) | "hard" | "soft" | Edge removal vs. down-weighting |
| nu (soft scheme) | 0.5 | 0.5 | Controls pseudotime sensitivity |
| b (soft scheme) | 10.0 | 10.0 | Controls exponential decay steepness |
| frac_to_keep (hard scheme) | 0.3 | -- | Fraction of backward edges kept |
| n_components (Schur) | -- | 20 | Number of Schur vectors |
| stability_threshold | 0.96 | 0.96 | Minimum macrostate stability for terminal classification |
| solver (fate probs) | "gmres" | "gmres" | Linear system solver |
| tol (fate probs) | 1e-6 | 1e-6 | Convergence tolerance |
| n_genes (CytoTRACE) | 200 | 200 | Top correlated genes for score |
| conn_weight (RealTimeKernel) | None | 0.2 | Weight for intra-time-point connections |

### Limitations

1. **Data quality dependence**: CellRank inherits noise from upstream methods (velocity inference, pseudotime, etc.)
2. **No automatic macrostate count**: eigengap heuristic is approximate; manual iteration often needed
3. **RNA velocity limitations**: gene structure bias, simplistic kinetic models, polyadenylation issues
4. **Pseudotime unidirectionality**: assumes monotonic differentiation
5. **Time series sampling**: insufficient temporal resolution leads to missed state transitions
6. **Markov memoryless assumption**: cannot capture protein accumulation or delayed effects
7. **Correlation-based drivers**: no causal inference; requires experimental validation
8. **No most-probable path**: limits analysis of transcriptional convergence

### Reproducibility Assessment

| Criterion | Rating |
|-----------|--------|
| **Code availability** | Excellent -- open-source (BSD-3), GitHub + Zenodo |
| **Data availability** | Excellent -- Figshare collection with all datasets |
| **Environment specification** | Good -- conda environment, Python 3.11, but no exact package versions pinned |
| **Step reproducibility** | Excellent -- numbered steps with code blocks, expected outputs shown in figures |
| **Timing information** | Excellent -- per-step timing on specified hardware |
| **Troubleshooting** | Good -- common issues documented with solutions |
| **Overall** | 9/10 -- comprehensive protocol with minor gap in version pinning |

### Compared/Referenced Methods

| Method | Journal | Year | Relationship |
|--------|---------|------|-------------|
| Palantir | Nat. Biotechnol. | 2019 | Pseudotime + fate inference alternative |
| Slingshot | BMC Genomics | 2018 | Pseudotime + lineage weight alternative |
| Velocyto | Nature | 2018 | RNA velocity pioneer; Markov simulation approach |
| scVelo | Nat. Biotechnol. | 2020 | Dynamical RNA velocity; used for preprocessing |
| Dynamo | Cell | 2022 | Metabolic labeling velocity + vector field |
| Waddington-OT | Cell | 2019 | OT-based trajectory inference |
| moscot | Nature | 2025 | OT framework; used by RealTimeKernel |
| moslin | Genome Biol. | 2024 | Lineage tracing + OT extension |
| tradeSeq | Nat. Commun. | 2020 | Downstream differential expression |
| pyGPCCA | -- | 2019 | Core Markov chain analysis algorithm |
| EpiTrace | Nat. Biotechnol. | 2025 | scATAC-seq clock loci + CellRank |
| veloVI | Nat. Methods | 2024 | Deep learning RNA velocity |
| RegVelo | bioRxiv | 2024 | Gene-regulatory velocity |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
