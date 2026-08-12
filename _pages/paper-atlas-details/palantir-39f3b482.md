---
layout: default
permalink: /paper-atlas/palantir-39f3b482/
title: "Palantir"
nav: false
description: "Palantir 不先把细胞硬切成几条分支，而是把单细胞状态流形变成一个大体沿伪时间向前的 Markov 链。对每个细胞，它计算随机游走最终被各终末状态吸收的概率；这些概率就是 branch/fate probabilities，其 Shannon 熵被定义为 differentiation potential（DP）。"
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
      <span>Nature Biotechnology · 2019</span>
    </div>
    <h1>Palantir</h1>
    <p>Characterization of cell fate probabilities in single-cell data with Palantir</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-019-0068-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Palantir：从单细胞快照估计连续命运概率

论文：*Characterization of cell fate probabilities in single-cell data with Palantir*（Nature Biotechnology, 2019；DOI: 10.1038/s41587-019-0068-4）

### 一句话理解

Palantir 不先把细胞硬切成几条分支，而是把单细胞状态流形变成一个大体沿伪时间向前的 Markov 链。对每个细胞，它计算随机游走最终被各终末状态吸收的概率；这些概率就是 branch/fate probabilities，其 Shannon 熵被定义为 differentiation potential（DP）。

这是一种由转录状态邻近关系推断的“可达性概率”，不是谱系追踪实验直接观测到的后代比例，也不是单细胞真实未来的校准预测概率。

### 1. 输入、输出与先验

核心输入是细胞在多尺度 diffusion-map 空间中的坐标，以及用户指定的一枚 early cell。当前 `run_palantir()` 默认接收 `DM_EigenVectors_multiscaled`，并输出：

- `palantir_pseudotime`：归一化到 0–1 的统一伪时间；
- `palantir_fate_probabilities`：每个细胞到各终末状态的吸收概率；
- `palantir_entropy`：上述概率向量的 Shannon 熵；
- `palantir_waypoints`：用于近似全数据流形的代表细胞。

终末状态可以自动识别，也可以由用户指定。论文的 colon 数据中，稀少且与早期细胞相似的 tuft cells 未被自动识别，作者手动加入了该终末状态。这一实例说明“自动终点”依赖采样密度和流形分离度。

### 2. 从表达矩阵到多尺度扩散空间

论文流程先做过滤、文库大小归一化、log 变换、PCA，再在细胞近邻图上建立自适应 diffusion kernel。扩散算子特征分解得到特征值 $\lambda_l$ 和特征向量 $\psi_l$。Palantir 使用多尺度权重

$$
\frac{\lambda_l}{1-\lambda_l}
$$

缩放各 diffusion component，相当于把不同随机游走时间尺度的扩散距离累加。慢衰减的成分权重大，噪声/快衰减成分权重小；组件数默认由 eigengap 决定。

当前代码 `utils.determine_multiscale_space()` 直接实现该缩放。但 kernel 层存在版本边界：论文描述双侧自适应尺度，当前 `compute_kernel()` 的 scanpy/sklearn 后端在部分路径使用单侧局部尺度。因此论文公式、2019 运行环境和当前 commit `807aba2...` 不能视为逐行完全相同。

### 3. 为什么要采样 waypoints

若只从起点计算一次最短路径，分支密度不均、弯曲和局部捷径会让伪时间不稳。Palantir 在每个 diffusion component 上做 max–min sampling：随机选一个点后，反复加入与已选集合“最近距离最大”的细胞。

若当前已选集合为 $S$，新 waypoint 是

$$
w_{new}=\arg\max_i\min_{w\in S}|x_i-x_w|.
$$

论文公式中的 `argmin` 与算法意图冲突；源码 `core.py:_max_min_sampling()` 使用 `np.argmax(min_dists)`。默认请求 1200 个 waypoints，并额外加入 diffusion-component 边界、起点和用户给定终点。

直观上，waypoint 是从多个观察角度测量同一条流形，而不是聚类中心或生物学里程碑。

### 4. 统一伪时间怎样迭代出来

代码在多尺度空间建立 kNN 距离图，必要时把不连通分量连接到起点可达区域，再用 Dijkstra 计算每个 waypoint 到所有细胞的最短路径距离 $D_{wi}$。

初始伪时间是起点到各细胞的距离。随后，每个 waypoint 对细胞 $i$ 给出一个带方向的“视角”：

$$
V_{wi}=t_w+s_{wi}D_{wi},
$$

其中若细胞当前位于 waypoint 之前则 $s_{wi}=-1$，否则为 $+1$；起点视角固定向前。各视角用距离权重平均：

$$
t_i^{new}=\sum_w W_{wi}V_{wi}.
$$

当前代码权重为

$$
W_{wi}\propto \exp\left[-\frac12\left(\frac{D_{wi}}{h}\right)^2\right],
$$

并对每个细胞归一化。带宽 $h$ 使用 Silverman 形式 `std × 1.06 × N^{-1/5}`，这与论文文字中较简化的 $\sigma=std$ 写法不完全一致。新旧伪时间 Pearson 相关系数超过 0.9999 或达到默认 25 次迭代后停止，最后线性缩放到 0–1。

小例子：若某细胞从两个近邻 waypoint 得到视角 0.30 和 0.70，归一化权重分别为 0.8 和 0.2，那么更新伪时间为 $0.8\times0.30+0.2\times0.70=0.38$。它不是某个 waypoint 距离的硬选择。

### 5. 伪时间如何把近邻图变成有方向的 Markov 链

对 waypoint 建 kNN 图后，算法允许向未来走，也允许在局部不确定范围内略微向后走；明显落后于当前细胞的边被删掉。`_construct_markov_chain()` 用第约 $k/3$ 个邻居距离作为局部尺度，并保留满足

$$
t_j\ge t_i-\sigma_i
$$

的邻居。保留边的双侧高斯 affinity 为

$$
A_{ij}=\exp\left(-\frac{d_{ij}^2}{2\sigma_i^2}-\frac{d_{ij}^2}{2\sigma_j^2}\right),
$$

再逐行归一化得到转移矩阵 $T$。

这不是动力学速率模型：转移概率来自表达流形距离、邻域尺度和伪时间方向约束，不代表单位生物时间内真实转分化概率。

### 6. 自动终末状态如何识别

终末状态应是随机游走容易积累、且位于流形边界的状态。代码计算 $T^\top$ 主特征向量作为 stationary ranks，并以中位数和 median absolute deviation 构造极端阈值（Gaussian PPF 0.9999）。超过阈值的 waypoint 先按连通分量合并，每个分量保留伪时间最大的候选，再映射到最近的 diffusion-component 边界。

因此终点识别同时要求：

1. 在定向链中有高稳态质量；
2. 位于/接近 diffusion 空间边界；
3. 能从采样数据中形成足够分离的状态。

它可能漏掉稀少或贴近祖先状态的命运，也可能受起点、$k$、组件数和预处理影响。当前 API 允许显式传入终末细胞，实际分析应结合 marker 和实验知识核查。

### 7. 吸收概率就是 branch probabilities

把终末状态的出边清零、自环设为 1 后，$T$ 成为吸收 Markov 链。按 transient 与 absorbing states 分块：

$$
T=\begin{pmatrix}Q&R\\0&I\end{pmatrix}.
$$

论文写基本矩阵与吸收概率：

$$
F=(I-Q)^{-1},\qquad B=FR.
$$

$B_{ik}$ 是从 transient waypoint $i$ 出发最终到达终点 $k$ 的概率。当前源码不显式求逆，而用 sparse LU 解线性方程

$$
(I-Q)B=R,
$$

数值上等价且通常更稳定；若稀疏求解失败才退回 dense inverse/pseudoinverse。终末状态自己的概率向量设为 one-hot。

最后，waypoint 概率通过前述权重矩阵投影到所有细胞：

$$
B_{all}=W^\top B_{waypoint}.
$$

例如某细胞到 erythroid、monocyte、DC 三个终点的概率为 `(0.7, 0.2, 0.1)`，它更偏向 erythroid，但仍保留其他可达性；Palantir 不在这里强制一个离散 lineage label。

### 8. differentiation potential 是什么

对每个细胞的 fate probability 向量计算 Shannon 熵：

$$
DP_i=-\sum_k B_{ik}\log B_{ik}.
$$

概率均匀分散时熵高，表示模型下仍可达多个终点；概率集中于一个终点时熵低。对三个终点，`(1/3,1/3,1/3)` 的 DP 为 $\log 3$，`(1,0,0)` 为 0。

这里有两个解释边界：DP 未除以 $\log K$，因此不同终点数目的分析之间不能直接比较绝对值；DP 是模型命运不确定性的摘要，不是细胞分子层面的 potency 实验测量。

### 9. gene trends 如何利用概率而非硬分支

论文沿统一伪时间为每个命运拟合加权 GAM：细胞在某分支上的权重就是它到该终点的 branch probability。这样过渡细胞可以同时贡献给多个趋势，而不是先被硬分群。

论文分析使用 GAM/MAGIC 等当时流程；当前仓库已演化，gene-trend 新路径默认使用 `mellon` function estimator，legacy pyGAM 仍可选，趋势聚类也不再等同于论文全部 R/PhenoGraph 步骤。因此核心 fate inference 与下游绘图/趋势后端要分开评价，不能声称当前 `pip install palantir` 会逐字复现论文图。

### 10. 主图和补充图提供了什么证据

- **图 1**：展示真实分化流形缺少清晰二叉分叉，并给出 Markov chain、terminal state、branch probability 和 DP 的概念关系。
- **图 2**：在人 CD34+ 骨髓数据上得到六个终末方向及统一伪时间/DP，并恢复典型 marker 趋势。
- **图 3–4**：用 DP 的快速下降定位早期造血状态变化，并关联代谢程序和 PU.1/GATA2 调控；这是基于关联的生物学解释，不是 Palantir 本身证明调控因果。
- **图 5**：迁移到鼠造血和结肠；tuft 终点需要人工指定，直接暴露自动终点的边界。
- **补充图 5–8**：waypoint、$k$、diffusion components 和 lineage subsampling 的相关性敏感性分析。论文报告多数比较中伪时间/DP/branch probability 相关较高，但 pDC 在低连接度设置下变差。

这些结果证明方法在所测试数据和扰动范围内稳定，不等于对任意批次效应、缺失中间态或错误起点都稳健。

### 11. 论文与当前代码的对应

| 环节 | 当前源码 | 对应程度 | 关键边界 |
|---|---|---|---|
| diffusion eigendecomposition | `utils.py:454-495` | Exact | kernel 构造有版本差异 |
| multi-scale scaling | `utils.py:893-905` | Exact | 实现 $\lambda/(1-\lambda)$ |
| max–min waypoints | `core.py:252-312` | Exact | 源码 argmax 修正论文公式笔误 |
| waypoint 伪时间迭代 | `core.py:315-401` | Partial | 当前带宽公式与论文简写不同 |
| 定向 Markov 链 | `core.py:494-563` | Exact | 是流形随机游走，不是生物速率 |
| 自动终末状态 | `core.py:566-649` | Exact | 稀少/不分离终点可漏检 |
| 吸收概率 | `core.py:652-765` | Exact/Partial | sparse solve 等价替代显式逆 |
| DP entropy | `core.py:755-763`, `core.py:223-230` | Exact | 未归一化，依赖终点集合 |
| gene trends | `presults.py` | Partial | 当前默认 mellon；论文为 GAM 路径 |
| f-scLVM、MAST、部分 TF/ATAC 分析 | 外部 R/分析流程 | Not found | 不属于 Palantir 主包 |

### 12. 实际使用最容易犯的错误

- 把 pseudotime 当作真实时间或分裂次数；它只是流形上的相对顺序。
- 把 branch probability 当作谱系追踪得到的频率；它是模型吸收概率。
- 忽略起点方向：起点错误会改变伪时间、删边方向、终点和所有下游结果。
- 只看自动终点不做 marker 检查；论文自己就有 tuft 漏检实例。
- 在不同终点数的数据间直接比较 DP；未归一化熵的上限随终点数变化。
- 用当前代码版本复现论文时忽略 kernel、带宽、GAM/mellon 和外部 R 步骤的漂移。
- 在 kNN 图缺少中间状态或批次形成断裂时，把图连接和随机游走结果解释为生物连续性。

### 建议阅读顺序

先读论文图 1 掌握概率命运框架，再读 Methods 中 diffusion maps、waypoint pseudotime、Markov chain 和 absorbing states 四节；结合补充图 5–8 看稳定性，再看图 5 的 tuft 失败案例。源码依次读 `utils.run_diffusion_maps()`、`determine_multiscale_space()`、`core.run_palantir()`、`_compute_pseudotime()`、`_construct_markov_chain()`、`_terminal_states_from_markov_chain()` 和 `_differentiation_entropy()`。

### 证据范围

本文基于本地论文 Markdown、补充材料 Markdown/图、已有分析文档和 Palantir 源码快照（commit `807aba253f7727f0b4899e42b5b83acc7804e5a2`）整理。本次没有重新运行原始 CD34+、鼠造血或结肠数据，也没有独立复算论文中的稳健性相关系数和生物学统计检验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Palantir — Paper Summary

### Metadata

- **Title**: Characterization of cell fate probabilities in single-cell data with Palantir
- **Authors**: Manu Setty, Vaidotas Kiseliovas, Jacob Levine, Adam Gayoso, Linas Mazutis, Dana Pe'er
- **Journal**: *Nature Biotechnology* 37(4), 2019
- **DOI**: [10.1038/s41587-019-0068-4](https://doi.org/10.1038/s41587-019-0068-4)
- **Code**: [github.com/dpeerlab/Palantir](https://github.com/dpeerlab/Palantir)

---

### Motivation & Novelty

Single-cell RNA sequencing reveals that cellular differentiation occurs along continuous state spaces rather than through discrete bifurcations. Yet existing trajectory inference methods — Monocle2 (*Nature Methods*, 2017), DPT (*Nature Methods*, 2016), PAGA (*Genome Biology*, 2019), Slingshot (*BMC Genomics*, 2018) — treat lineage decisions as deterministic, discrete events. These approaches cannot quantify the **probability** of a cell reaching each terminal fate or measure **cell plasticity** along the trajectory.

Palantir introduces three key innovations:

1. **Probabilistic cell fate modeling**: Models differentiation as an absorbing Markov chain, assigning each cell a probability distribution over terminal fates rather than a single lineage assignment
2. **Differentiation potential (DP)**: Defines plasticity as Shannon entropy of the fate probability vector, providing the first quantitative, continuous measure of how many fates remain accessible from each cell state
3. **Unified pseudo-time**: Computes a single ordering across all lineages using multi-scale distances and waypoint-refined shortest paths, enabling direct comparison of gene expression dynamics across branches

Together, these features enable Palantir to detect key differentiation events — such as the metabolic switch in hematopoietic stem cells — that are invisible to methods modeling fate as discrete choices.

---

### Method Overview

Palantir takes scRNA-seq data and a user-specified start cell as input, then executes five stages:

1. **Manifold construction**: Builds diffusion maps using an adaptive anisotropic kernel that corrects for variable cell density, then computes multi-scale distances (λ/(1-λ) eigenvalue scaling) for a robust, scale-free representation

2. **Pseudo-time inference**: Selects waypoints via max-min sampling across diffusion components, computes shortest-path distances from all waypoints, and iteratively refines the ordering via weighted perspective averaging (convergence at Pearson r > 0.9999)

3. **Markov chain construction**: Converts the kNN graph to directed using pseudo-time and adaptive uncertainty thresholds, then constructs transition probabilities for a Markov chain over waypoint cells

4. **Fate characterization**: Identifies terminal states as diffusion component boundary cells that are outliers in the Markov chain's stationary distribution. Converts to absorbing chain; solves for branch probabilities via sparse LU decomposition of (I-Q)B=R. Projects waypoint results to all cells.

5. **Gene expression trends**: Fits generalized additive models (or mellon function estimators in current code) weighted by branch probabilities along pseudo-time, using MAGIC-imputed expression

See doc_method.md for full mathematical details and doc_code.md for implementation mapping.

---

### Evaluation

#### Datasets

| Dataset | Species | Cells | Source | Terminal States |
|---------|---------|-------|--------|----------------|
| CD34+ bone marrow (3 replicates) | Human | ~25,000 | 10X Chromium, this study | Mono, Ery, Mega, CLP, cDC, pDC |
| Sorted myeloid/erythroid precursors | Mouse | ~2,700 | MARS-seq2 (Paul et al., *Cell* 2015) | Mono, Neutro, Baso, Mega, Ery |
| Colon epithelium (Lgr5+ stem) | Mouse | ~1,800 | InDrop (Herring et al., *Cell Systems* 2018) | Colonocytes, Goblet, Reg4+ Goblet, Tuft |

#### Compared Methods

| Method | Journal | Year | Unified Pseudotime | Fate Probs | Auto Terminal | Topology |
|--------|---------|------|-------------------|------------|---------------|----------|
| **Palantir** | *Nat Biotechnol* | 2019 | ✓ | ✓ | ✓ | — |
| Monocle2 | *Nat Methods* | 2017 | ✓ | — | — | — |
| DPT | *Nat Methods* | 2016 | ✓ | — | — | — |
| PAGA | *Genome Biol* | 2019 | ✓ | — | — | ✓ |
| Slingshot | *BMC Genomics* | 2018 | — | — | ✓ | — |
| FateID | *Nat Methods* | 2018 | — | ✓ | — | — |
| PBA | *PNAS* | 2018 | — | ✓ | — | — |

#### Key Results

- **Lineage identification**: Palantir was the only method to correctly distinguish all 6 terminal states in human hematopoiesis, including the two rare DC populations and separate megakaryocyte lineage
- **Gene expression trends**: Palantir correctly recovered dynamics of all 6 canonical marker genes (CD34, MPO, CD79B, GATA1, CSF1R, CD41). Other methods failed on at least 2
- **Robustness**: Comprehensive parameter sensitivity analysis:
  - Waypoint sampling: pseudo-time correlations > 0.98, DP correlations > 0.85 (75% > 0.9), BP correlations > 0.85 (90% > 0.9)
  - kNN parameter k: correlations > 0.97 for pseudo-time and DP; > 0.94 for BP (except pDC with k=25)
  - Diffusion components: pseudo-time and DP > 0.96; BP > 0.94
  - Cell subsampling (25-75% of lineage cells): all correlations > 0.94
  - Cross-replicate: pseudo-time and DP highly reproducible across 3 independent donors
- **Biological discoveries**:
  - DP identifies the **metabolic switch** (LT-HSC → ST-HSC transition) without prior knowledge
  - Hierarchical lineage commitment: lymphoid → erythroid/megakaryocytic → myeloid
  - GATA2 (not GATA1) identified as the key agonist of PU.1 in erythroid specification
  - PU.1/GATA2 expression ratio and TF activity difference predict erythroid commitment
- **Generalization**: Successfully applied to mouse hematopoiesis (paucity of early cells) and mouse colon (different tissue type, InDrop platform)

---

### Reproducibility

**Rating: 4/5** (Good)

#### Strengths
- Code is publicly available as a well-maintained Python package on GitHub with active development
- Sample notebook (`Palantir_sample_notebook.ipynb`) provides end-to-end walkthrough with bone marrow data
- Code Ocean capsule provides a fully reproducible computational environment
- Raw data available through Human Cell Atlas portal
- Extensive robustness analysis across parameters and replicates

#### Weaknesses
- The original paper's preprocessing used f-scLVM for cell cycle correction and R's `gam` package for trends — neither is part of the Palantir package, and both are difficult to set up
- Current code has evolved significantly: default gene trend method changed from pyGAM to mellon; kernel backend options differ from paper
- Some key parameters (k = "10% of total cells") are not automatically applied — user must calculate and set knn manually
- External dependencies (MAST for differential expression, bulk ATAC-seq data for TF activity) are not bundled
- pyGAM has scipy ≥1.13 compatibility issues (sparse matrix `.A` attribute removed)

#### Practical Notes
- **Environment**: `pip install palantir` with `palantir[gam]` for legacy GAM trends
- **Data**: Bone marrow data downloadable from HCA portal; sample data included in repo
- **Key parameters**: `knn=30`, `num_waypoints=1200`, `max_iterations=25`, `scale_components=True`, `seed=20`
- **Common pitfall**: Start cell selection matters — choose a cell in the most primitive population; Palantir will snap to nearest DC boundary
- **AnnData integration**: All results stored in `.obs`, `.obsm`, `.uns`; compatible with scanpy workflows

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
