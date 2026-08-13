---
layout: default
permalink: /paper-atlas/copro-dae56e1b/
title: "CoPro"
nav: false
wide: true
description: "空间转录组里常见的变化并不总是离散“区域”，而可能是几个重叠的连续梯度：例如结肠隐窝从底到顶的分化、局部炎症斑块、肝小叶分区，以及不同细胞类型沿同一组织轴发生的协同变化。CoPro 的目标是为每个细胞类型找到一个可解释的表达方向，使空间上相邻的不同类型细胞沿这些方向具有最大的协同变化。 它输出的是每种细胞类型的基因权重和逐细胞 co-progression score。这个 score 是空间协调轴，不等同于时间、谱系或因果方向；"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>CoPro</h1>
    <p>Dissecting the coordinated progression of cell states in spatial transcriptomics with CoPro</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.04.17.719309" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CoPro">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Zhen-Miao/CoPro" target="_blank" rel="noopener noreferrer" aria-label="Open code for CoPro">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CoPro 方法解读：从空间邻近中找出跨细胞类型共同推进的连续程序

### CoPro 解决什么问题

空间转录组里常见的变化并不总是离散“区域”，而可能是几个重叠的连续梯度：例如结肠隐窝从底到顶的分化、局部炎症斑块、肝小叶分区，以及不同细胞类型沿同一组织轴发生的协同变化。CoPro 的目标是为每个细胞类型找到一个可解释的表达方向，使空间上相邻的不同类型细胞沿这些方向具有最大的协同变化。

它输出的是每种细胞类型的基因权重和逐细胞 co-progression score。这个 score 是空间协调轴，不等同于时间、谱系或因果方向；只有在外部生物学顺序支持时，才能把它解释为某类进程。

### 输入与输出

输入包括细胞/像素表达矩阵、二维空间坐标、粗粒度细胞类型标签，以及可选的样本/切片标签。推荐先在每个细胞类型内做 PCA 并白化。输出包括多个正交 co-progression 轴、每轴的细胞分数和基因权重、空间带宽选择结果、核归一化相关和 bidirectional spatial correlation（BSC）。多样本模式学习共享权重，无须先把切片做几何配准。

### 核心算法

#### 1. 空间核只作用在坐标，不作用在表达

对细胞类型 $s,t$ 的两群细胞，CoPro 从距离矩阵构造

$$
K_{st}^{(\sigma)}(i,j)=\exp\left[-\frac12\left(\frac{d_{ij}}{\sigma}\right)^2\right].
$$

$\sigma$ 控制“多近才算邻居”。源码 `CoPro/R/12_compute_kernel.R:16-20` 直接实现该式，并把小于 $10^{-7}$ 的权重截为零。这里与表达核 CCA 不同：表达仍保持线性可解释，核只是重新加权哪些跨类型细胞对参与协方差。

#### 2. skrCCA 寻找跨类型共同变化方向

设白化 PC 矩阵为 $X_t$，权重为 $w_t$。单样本目标是

$$
\max_{\{w_t\}}\sum_{s<t}w_s^\top X_s^\top K_{st}^{(\sigma)}X_tw_t,
\qquad \|w_t\|_2=1.
$$

`CoPro/R/04_optimization_function_refactored.R:95-118,153-220` 用块坐标幂迭代更新每种细胞类型的方向。当前代码对 `scalePCs=TRUE` 使用白化 PC 下的单位范数；不白化时则传入 PC 方差作加权归一化，因此旧文档所说“完全没有实现 Eq. 1 约束”已不符合当前快照。

#### 3. 从一个轴扩展到多个重叠轴

第一轴收敛后，代码从跨类型矩阵中扣除已解释的秩一方向，再求下一轴。`apply_deflation()` 位于 `CoPro/R/04_optimization_function_refactored.R:279-320`，并区分普通与方差加权的 deflation。这样同一组织可以同时呈现形态轴和炎症轴，但“正交”是模型空间里的约束，不保证生物机制彼此独立。

#### 4. 选空间尺度并量化协调强度

`computeNormalizedCorrelation()` 以核谱范数归一化目标值，并用第一成分在细胞类型对之间的平均值选择 $\sigma$（`CoPro/R/15_compute_norm_corr.R:107-205`）。BSC 则从两个方向计算邻域平滑分数与另一类型分数的 Pearson 相关再取平均。当前实现还默认支持核的行/列归一化和低连接度过滤（`CoPro/R/16_compute_bidirectional_corr.R:309-377`），所以它比论文展示的紧凑公式多了数值处理步骤。

#### 5. 显著性和跨样本转移

论文用边长约 $2\sigma$ 的空间 patch 置换来保留单类型内部空间自相关、打破跨类型协调，从而构造零分布；对应实现位于 `CoPro/R/D_spatial_CCA_permutation.R`。已学习的基因权重还可投射到新样本，在不依赖形态配准的情况下得到同一生物轴上的分数；`CoPro/R/H_extrapolate.R` 提供转移与可选分位数标准化。

### 八张主图的证据链

1. **图 1**定义输入、skrCCA、多个轴、监督模式、跨样本转移和 BSC。
2. **图 2**用真实单细胞表达构造模拟空间布局，评估单轴、比例不平衡和双正交轴；这些性能数字来自论文，模拟脚本不在当前 R 包快照。
3. **图 3**用方向性核拆分纹状体 dorsal–ventral 与 medial–lateral 梯度，说明核设计可编码有方向的空间先验。
4. **图 4**在结肠同时提取隐窝形态梯度与局部 immediate-early-gene 炎症轴。
5. **图 5**把一个切片学到的疾病轴转移到 25 个切片；论文报告其 90% 分位分数与 MU8 丰度相关 $R=0.774$，这是关联验证而非因果标尺。
6. **图 6**在 iSTAR 推断的肝脏超像素上恢复肝小叶分区，并以独立 pcRNA-seq/标记基因验证肝细胞—内皮协调。
7. **图 7**从六个衰老肝样本的多个成分中归纳可复现的 ECM、免疫和分区模块。
8. **图 8**用已知肾单位顺序监督肾小管轴，再发现相邻血管程序；这展示的是受先验锚定的空间协同，而不是纯无监督轨迹。

### 论文—代码匹配与复现边界

本地 `CoPro/` 是 v0.6.1 R 包，含 S4 数据结构、距离/核、PCA、skrCCA、NCorr、BSC、置换、转移、vignettes 和 testthat 测试。旧元数据中的固定 commit 因而不能继续使用。工作区还有一个较早的 `code/CoPro_R/` 副本，两者存在源码差异；本解读以顶层 `CoPro/` v0.6.1 为当前实现证据。

论文分析复现脚本和部分预处理不在 R 包中，也没有在本轮重跑大型数据。因此，公式与软件行为是直接核验，图 2–8 的生物学结果和数值是 paper-reported 证据。

### 使用时的主要风险

- 结果依赖细胞类型注释、PCA 表示、距离定义和候选 $\sigma$；这些不是无关紧要的预处理。
- 空间共变可能来自共同微环境、组织形态或未测混杂，不能自动推出细胞间调控。
- 多轴 deflation 会改变后续成分；轴的符号也可整体翻转，解释应依赖基因权重和外部标记。
- 跨样本转移要求表达特征和标准化具有可比性；无几何配准不等于无批次效应。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CoPro: Dissecting Spatially Coordinated Progression of Cell States

**Paper**: Dissecting the coordinated progression of cell states in spatial transcriptomics with CoPro
**Authors**: Zhen Miao, Yilong Qu, Sijia Huang, et al.
**Journal**: bioRxiv (2026-04-17) | DOI: 10.64898/2026.04.17.719309
**Code**: https://github.com/Zhen-Miao/CoPro (R), https://github.com/Zhen-Miao/copro_python (Python)

---

### Motivation & Novelty

#### Biological Problem
Tissue function depends on spatially coordinated interactions between distinct cell types. In the intestinal crypt, epithelial differentiation along the base-to-tip axis is accompanied by parallel transcriptional transitions in adjacent fibroblasts and macrophages. In the liver lobule, hepatocyte metabolic zonation is reinforced by endothelial Wnt signaling from neighboring cells. In the aging liver, multiple senescence-associated programs emerge superimposed on the same anatomical zonation. These are inherently **continuous, multi-cell-type, spatially structured** phenomena.

#### Why Existing Methods Fall Short

| Method | Limitation | Reference |
|--------|-----------|-----------|
| DIALOGUE (Jerby-Arnon & Regev, *Nat. Biotechnol.* 2022) | Aggregates cells into spatial bins; no explicit single-cell spatial model | — |
| SpaceFlow (Ren et al., *Nat. Commun.* 2022) | Identifies a single spatial manifold; cannot resolve overlapping gradients | — |
| ONTraC (Wang et al., *Genome Biol.* 2025) | Models cell type composition trajectories; not gene-expression-level programs | — |
| GASTON (Chitra et al., *Nat. Methods* 2025) | Neural manifold learning; single dominant axis; no multi-cell-type coupling | — |
| Domain clustering methods (SpaGCN, etc.) | Impose discrete partitions on continuous variation | — |

#### Unique Contributions
1. **Spatial kernel-restricted CCA (skrCCA)**: introduces spatial proximity as a kernel operating on coordinates (not expression) into a classical CCA objective — enables linear, interpretable gene programs
2. **Multi-axis orthogonal decomposition**: sequential deflation recovers multiple overlapping biological gradients from the same tissue (e.g., morphological and inflammatory gradients simultaneously)
3. **Flexible kernel design**: axis-specific (directional) kernels for isolating gradients along specified anatomical axes (e.g., dorsal-ventral independently from medial-lateral)
4. **Cross-sample integration without registration**: learned gene weights transferred to target samples define a common biological axis robust to morphological variation
5. **Supervised mode**: known anatomical ordering (e.g., nephron segment types) anchors discovery of co-progressing programs in neighboring cell types

---

### Method Overview

CoPro models spatial transcriptomics data by finding **cell-type-specific weight vectors** $w_t$ in PCA-reduced expression space that maximize the **kernel-weighted cross-cell-type covariance**:

$$\max_{\{w_t\}} \sum_{i < j} w_i^\top X_i^\top K_{ij}^{(\sigma)} X_j w_j$$

The kernel $K_{ij}^{(\sigma)}(a,b) = \exp(-d_{ab}^2/2\sigma^2)$ encodes spatial proximity between cell $a$ (type $i$) and cell $b$ (type $j$). Optimization is via block-coordinate power iteration; multiple components are extracted by sequential deflation. The result is per-cell **co-progression scores** $s_{t,k} = X_t w_{t,k}$ and interpretable **gene weights** per component.

**Key technical components**:
- PCA whitening (scale PC scores by sdev) for variance normalization
- Bandwidth $\sigma$ selected by maximizing mean kernel-normalized correlation across cell-type pairs
- Patch-based permutation test (patches of size $2\sigma$) for significance assessment
- Cross-sample score transfer via optional quantile normalization + z-score standardization using reference statistics
- Both R and Python implementations; R package installable from GitHub

For full mathematical details see doc_method.md. For code mapping see doc_code.md.

---

### Evaluation

#### Simulations (Realistic, Based on Liver Cell Atlas)

| Scenario | CoPro | Best Competitor | Dataset |
|----------|-------|----------------|---------|
| 2-cell-type, single gradient | r = 0.93 | DIALOGUE r = 0.70 | Liver Cell Atlas (scRNA-seq simulation) |
| 3-cell-type, varying proportions | r = 0.87 | Competitors 0.40–0.60 | Same, ternary design |
| Two orthogonal axes | r = 0.84 per axis | Others: single axis only | Same |

CoPro is the only method capable of recovering two independent overlapping axes in Scenario 3 (SpaceFlow and GASTON recover one axis; DIALOGUE has limited multi-axis capability).

#### Real Data Demonstrations

**Mouse colon (MERFISH, 940 genes; Cadinu et al., *Cell* 2024)**:
- Day 0: Recovers crypt base-to-tip differentiation axis across epithelial cells, fibroblasts, macrophages (BSC consistent across all pairs)
- Day 3: Simultaneously resolves crypt morphology (Axis 1) and patchy IEG-driven inflammation (Axis 2)
- Day 9: Transfers homeostatic weights to disease samples; unified disease axis correlates with MU8 neighborhood abundance (R = 0.774 across 25 sections); variance decomposition: cell-level 68.5%, mouse 18.7%, slice 12.8%

**Mouse brain (MERFISH; Zhang et al., *Nature* 2023)**:
- Striatum D1/D2 neurons: decomposes into dorsal-ventral (Reln, Coch, Sox1) and medial-lateral (Rasgrp2, Pde1a, Crym) axes via directional kernels; existing methods capture only the dominant DV axis

**Mouse liver — healthy (iSTAR histology-imputed at 8 µm; in-house Visium data)**:
- Recovers hepatocyte lobular zonation despite lacking discrete cell boundaries; endothelial zonation (Wnt2, Wnt9b, Rspo3) validated against independent paired-cell RNA-seq data (pcRNA-seq; Halpern et al., *Nat. Biotechnol.* 2018; 96% concordance with 24 known markers)

**Mouse liver — aging (Ercc1−/Δ mutant; 6 samples)**:
- Identifies 3 reproducible aging modules: Module 1 (ECM/fibrosis + SASP), Module 4 (structural ECM, minimal immune), Module 5 (immune-driven ECM remodeling)
- Zonation transfer from healthy: aging causes expansion of midlobular zone 2 and blurring of zonal boundaries

**Mouse kidney (seqFISH, 1298 genes, 3 replicates; Polonsky et al., *Nat. Commun.* 2024)**:
- Supervised mode with ordinal nephron segment labels (Kendall τ = 0.74–0.78)
- Recovers full corticomedullary vascular specialization hierarchy without endothelial subtype annotation
- 3,485 concordant vascular axis genes; 23/24 (96%) known vascular zone markers correctly assigned
- Transferred to scRNA-seq atlas (31,265 cells; Ransick et al., *Dev. Cell* 2019): resolves 6 endothelial clusters

---

### Reproducibility

**Rating: 3/5** — Strong R software and methods; paper-level reproduction remains incomplete

**Strengths**:
- Open-source R package on GitHub; Python package on PyPI (`copro`)
- Both single-slide and multi-slide analyses supported in clean S4 OOP framework
- Vignettes and example data via `copro_download_data()`
- Four public datasets available for download (colon, brain, liver atlas, kidney)
- Methods section provides detailed simulation procedures and analysis parameters

Numerical results below are paper-reported.

**Practical notes**:
- R package installation: `devtools::install_github("Zhen-Miao/CoPro")`
- Core dependencies: irlba, fields, Matrix, ggplot2
- Key parameter to tune: `sigma` bandwidth (auto-selected via NCorr grid search; can manually override)
- For large datasets (>10⁵ cells per type), kernel computation memory-intensive; `upperQuantile` parameter clips long-range interactions

**Weaknesses / limitations**:
- Aging liver Visium data not yet public (companion paper pending); must contact corresponding authors
- Simulation benchmarking scripts not included in the R package (separate analysis repository)
- Assumes linear co-variation — strongly nonlinear patterns not captured by CCA
- Transfer strategy anchors all samples to a single reference frame; may obscure sample-specific deviations
- Quality dependent on input cell type annotations accuracy
- Computational cost scales with $O(n_i \cdot n_j)$ cell pairs; very large datasets require subsampling

**Common pitfalls**:
- Run `computeKernelMatrix()` before `runSkrCCA()`; check `sigmaValues` is populated
- Default `scalePCs=TRUE` makes the unit-norm update consistent with the whitened-PC parameterization; the current code also uses squared-PC-SD weighted normalization when `scalePCs=FALSE`
- For permutation testing, patch size defaults to $2\sigma$ — verify this is biologically appropriate for your tissue scale
- Multi-sample analysis: use `CoProMulti` class, not repeated `CoProSingle`; shared weights are estimated jointly

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
