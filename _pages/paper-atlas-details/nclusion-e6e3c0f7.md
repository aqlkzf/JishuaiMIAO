---
layout: default
permalink: /paper-atlas/nclusion-e6e3c0f7/
title: "NCLUSION"
nav: false
description: "NCLUSION 把“细胞属于哪个簇”和“哪些基因真正推动这个簇”放在同一个贝叶斯模型里联合估计。它直接处理归一化表达矩阵，不先做 PCA；用截断的层次 Dirichlet 过程容纳未知簇数，用 spike-and-slab 先验把无关的“基因 × 簇”效应压到零，再以变分推断获得细胞归属概率和基因后验纳入概率（PIP）。"
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
      <span>Domain Clustering</span>
      <span>Cell Reports Methods · 2026</span>
    </div>
    <h1>NCLUSION</h1>
    <p>Scalable nonparametric clustering with unified marker gene selection for single-cell RNA-seq data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.crmeth.2026.101329" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for NCLUSION">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/microsoft/Nclusion.jl" target="_blank" rel="noopener noreferrer" aria-label="Open code for NCLUSION">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## NCLUSION 中文方法解读

### 一句话理解

NCLUSION 把“细胞属于哪个簇”和“哪些基因真正推动这个簇”放在同一个贝叶斯模型里联合估计。它直接处理归一化表达矩阵，不先做 PCA；用截断的层次 Dirichlet 过程容纳未知簇数，用 spike-and-slab 先验把无关的“基因 × 簇”效应压到零，再以变分推断获得细胞归属概率和基因后验纳入概率（PIP）。

### 1. 为什么要把聚类和 marker 选择合并

常规流程先根据表达差异聚类，再在同一批数据上检验簇间差异。由于簇本来就是用这些差异定义的，后续检验可能发生 data double-dipping。另一方面，PCA 维数、邻居数、resolution 和簇数都需要人工选择。

NCLUSION 的目标不是证明所有后聚类差异分析都无效，而是提供一个统一的生成模型：决定细胞归属的稀疏基因效应本身就是模型参数，因此聚类与 marker 证据在同一次推断中相互约束。

### 2. 生成模型：全局基线加簇特异偏移

对细胞 $n$、基因 $j$，论文以正态混合描述 log-normalized expression：

$$
x_{nj}\sim\sum_{k=1}^{\infty}\pi_k\,\mathcal N(\nu_j+\mu_{jk},\sigma_j^2).
$$

$\nu_j$ 是基因的全局基线，$\mu_{jk}$ 是它在簇 $k$ 中相对基线的偏移，$\sigma_j^2$ 是基因层面的噪声尺度。细胞归属的后验概率在代码中保存为 `cells[n].r[k]`，最终标签取 `argmax(r)`。

这个正态模型作用于预处理后的连续表达值，并不是原始 UMI 计数的负二项或零膨胀计数模型。因而结果会受归一化、HVG 选择和尺度变换影响。

### 3. spike-and-slab 如何同时选择 marker

每个 $\mu_{jk}$ 都有稀疏先验：

$$
\mu_{jk}\sim\eta\,\mathcal N(0,\lambda_{jk}\sigma_j^2)+(1-\eta)\delta_0.
$$

二元变量 $\rho_{jk}$ 表示该效应是否来自 slab。变分后验中的

$$
\operatorname{PIP}(j;k)=\Pr(\rho_{jk}=1\mid X)
$$

在代码里是 `clusters[k].y[j]`。`update_y!` 的 sigmoid 更新综合了稀疏先验、效应均值与不确定性；效应相对于方差越强，PIP 越容易升高。PIP 是“该基因在该簇具有非零模型效应”的后验近似，不等同于传统差异检验的 p 值，也不能单独证明生物学因果。

### 4. “无限簇”在计算中怎样落地

论文使用 stick-breaking 的层次 Dirichlet 过程，使理论模型允许无限多个成分；$\alpha_0$、$\gamma_0$ 控制更偏向少而大的簇还是多而小的簇。实际代码必须在有限 $K_{\max}$ 上截断，`run_nclusion` 默认 `KMax=25`，训练后再移除/重排空簇。

因此“无需指定最终簇数”不等于“计算时没有簇数参数”。用户仍需给出足够大的截断上界，且默认上界、浓度参数、初始化和局部最优都可能影响最终占用簇数。把方法写成自动精确找到“真实最佳 $K$”会超过证据。

### 5. 变分 EM 的实际数据流

代码的核心是 `viCoordinateAscent.jl:cavi`：

1. 更新簇特异偏移、方差和 spike-and-slab PIP；
2. 更新每个细胞对各簇的软归属 `r`；
3. 用软归属汇总 $N_k=\sum_n r_{nk}$ 与表达充分统计量；
4. 更新稀疏率和 stick-breaking 参数；
5. 计算 ELBO，并按收敛条件或最大迭代数停止。

最昂贵的细胞归属更新按细胞多线程，复杂度主要随 $N\times K\times J$ 增长。代码还会在 ELBO 出现 NaN/Inf 时检查并重置异常簇；这提高了运行韧性，但也说明结果可能依赖随机种子和重置路径。

论文实验设置与包默认值不能混用。当前 `run_nclusion` 默认 `KMax=25`、`num_iter=500`、`elbo_ep=10^{-6}`；论文 Methods S1/实验使用的终止配置可能不同，应以具体运行记录为准。

### 6. PIP 之后如何得到簇特异基因模块

一个基因可能在多个簇都有高 PIP。论文先按其跨簇使用频率降低 PIP 权重，再结合正向 effect-size sign（ESS）和 SSMD/效应强度条件筛选上调 marker。

与旧文档不同，当前代码并非完全缺失这一后处理。`processing.jl:posterior_summaries` 会：移除空簇、计算 adjusted PIP、经验与后验 effect size/ESS、通过 Monte Carlo 得到局部错误符号率与 s-value，并输出 gene-cluster summaries。不过它实现的是扩展后的后验汇总路径，变量和阈值不完全逐字对应论文图中的简单三步过滤；论文全部图表仍依赖单独的 figure-reproducibility 仓库。

代码中 Monte Carlo effect-size 表达式的括号位置值得复核：`sampled_y_rho_mu[:,k] .- mean(...) ./ sqrt(...)` 只标准化了“其他簇均值”，而不是显式标准化整个差值。仅凭静态阅读不能确认这是有意定义还是实现偏差，因此使用这些输出做严格 SSMD 解释前应做数值测试。

### 7. 五张结果图支持什么

- 图 1：对比常规工作流与统一工作流，并展示 BRAIN-LARGE 运行时间。NCLUSION 是图中唯一跑到 100 万细胞的方法；这是在 720 个基因和特定硬件/实现下的基准，不是所有数据上的普遍速度保证。
- 图 2：四类模拟中的一个代表场景。scDeepCluster 的聚类最好，NCLUSION 属于前列；marker 检测中 NCLUSION 与 FESTEM 同时保持较高 power 和较低 FDR/FPR。模拟“causal gene”指生成真值，不表示真实数据中的因果基因。
- 图 3：94,615 个 PBMC、5,000 个基因上，NCLUSION 相对参考标签取得最高 NMI/ARI，并比所列基线更快。参考标签结合 FACS 和既有聚类，并非无误差真值。
- 图 4：展示 adjusted PIP、ESS、SSMD、模块表达、与 Seurat marker 的比较和 GO 富集。GO 富集支持功能一致性，不证明这些基因是调控原因。
- 图 5：在 PDAC、AML、IMMUNE 数据上评估可扩展性和聚类一致性，并深入展示 PDAC 模块。肿瘤簇/通路解释是注释和关联证据，不应升级为临床或机制结论。

### 8. 代码与论文的关键边界

- 理论上是无限混合，工程上是有限 `KMax` 截断；默认 25。
- 论文写 base-2 归一化，但仓库中的 `lognormalization` 调用没有本地定义；示例 Python 脚本使用 Scanpy `log1p`（自然对数）。当前快照无法证明所有入口采用同一对数底。
- 当前包已经包含 adjusted PIP 和后验 effect summary，旧文档所称“Eqs. 5–9 完全不在 Julia 包”不再成立。
- `pyproject.toml` 声明 Python 包接口，但快照中没有实际 Python 模块；可靠入口仍是 Julia API/CLI。
- 仓库 README 指向单独的 manuscript figure-reproducibility 仓库；本地代码快照不足以一键重建全部论文结果。

### 9. 建议的源码阅读顺序

1. `src/processing.jl`：公开入口、预处理、模型初始化、输出和 `posterior_summaries`。
2. `src/viCoordinateAscent.jl`：CAVI 更新顺序、收敛与异常簇重置。
3. `src/viVariationalUpdates.jl`：`r`、`y`、均值、方差和超参数更新。
4. `src/viExpectations.jl`：各个变分期望量。
5. `src/viElboCalculations.jl`：ELBO 各项。
6. `src/viSurragateHdpUpdates.jl`：stick-breaking 参数的代理下界优化。

### 结论

NCLUSION 的核心价值是把聚类解释性变成模型内部对象：细胞归属与稀疏基因效应在同一近似后验中更新。它减少了先降维、再选 $K$、再做 marker 检验的流程割裂，并在论文基准中展现出良好扩展性。正确使用时仍要保留四个边界：有限截断并非真正无限计算、结果依赖预处理与超参数、PIP/ESS 是模型证据而非因果证据，以及当前快照的后处理实现与论文公式需要数值级复核。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## NCLUSION: Scalable Nonparametric Clustering with Unified Marker Gene Selection for Single-Cell RNA-seq Data

### Paper Information

- **Authors**: Chibuikem Nwizu, Madeline Hughes, Michelle L. Ramseier, Andrew W. Navia, Alex K. Shalek, Nicolo Fusi, Srivatsan Raghavan, Peter S. Winter, Ava P. Amini, Lorin Crawford
- **Journal**: Cell Reports Methods, 6(3), 2026
- **DOI**: [10.1016/j.crmeth.2026.101329](https://doi.org/10.1016/j.crmeth.2026.101329)
- **Code**: [github.com/microsoft/Nclusion.jl](https://github.com/microsoft/Nclusion.jl) (Julia)

---

### Motivation & Novelty

#### Problem
Standard scRNA-seq clustering workflows require multiple user-defined heuristics: choosing the number of clusters $K$, selecting dimensionality reduction parameters, and performing post-hoc differential expression analysis between clusters. The post-hoc approach — testing for expression differences between groups that were *defined* by expression differences — leads to inflated false discovery rates through "data double-dipping."

#### Limitations of Existing Approaches
- **Seurat** (Cell, 2015): Requires PCA embedding, user-specified resolution parameter, and post-hoc Wilcoxon rank-sum tests for marker genes
- **scLCA** (2022): Uses SVD-based embedding with spectral clustering; requires $K$ specification
- **KNN+Leiden** (Genome Biology, 2018): Graph-based clustering dependent on neighbor count and resolution
- **SOUP** (2019): Semi-soft clustering; requires $K$ and produces overlapping assignments
- **scCCESS-SIMLR** (2021): Ensemble spectral method; most computationally expensive of benchmarked methods
- **SC3** (Nature Methods, 2017): Consensus clustering requiring $K$ and iterative merging
- **scDeepCluster** (2019): Deep learning-based; dependent on initialization quality and Leiden pre-clustering

For marker gene detection:
- **DUBStepR** (2021) and **singleCellHaystack** (2020): High power but also high FDR
- **FESTEM** (2023): Requires separate clustering step; uses Scott-Knott test for cluster assignment

#### Unique Contributions
1. **Unified framework**: Simultaneously performs clustering and marker gene selection directly on the selected expression matrix, without a PCA embedding
2. **Nonparametric**: Automatically learns the number of clusters via a Dirichlet process prior, eliminating $K$ selection
3. **Principled variable selection**: Spike-and-slab priors provide posterior inclusion probabilities (PIPs) with well-calibrated false discovery control
4. **Scalability**: Variational EM with coordinate ascent scales to 1 million cells — the only benchmarked method to reach this scale

---

### Method Overview

NCLUSION models log-normalized gene expression as a sparse hierarchical Dirichlet process (HDP) normal mixture. Each cell's expression is explained by a global gene-level baseline plus a cluster-specific shift, where a spike-and-slab prior on the shift automatically selects marker genes with nonzero effects.

**Key components**:
- **Sparse HDP mixture model**: Infinite mixture of Gaussians with per-gene sparsity
- **Stick-breaking Dirichlet process**: Learns cluster count from data ($\alpha_0 = \gamma_0 = 1.0$)
- **Variational EM**: Coordinate ascent variational inference (CAVI) approximates the posterior via mean-field factorization
- **Post-hoc marker filtering**: Adjusted PIPs, effect size sign (ESS), and strictly standardized mean difference (SSMD) identify cluster-specific up-regulated genes

The algorithm operates directly on normalized expression matrices without PCA or other dimensionality reduction. See `doc_method.md` for full mathematical details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | N cells | J genes | Cell types | Source |
|---------|---------|---------|------------|--------|
| Simulations (scDesign3) | 10,000 | 1,000 | 5 | Gaussian copula from PBMC reference |
| BRAIN-LARGE | 1.3M (subsampled) | 720 | N/A (runtime only) | 10x Genomics |
| PBMC | 94,615 | 5,000 | 10 | Zheng et al. (FACS-sorted) |
| PDAC | 23,042 | 5,000 | 11 + malignant | Raghavan et al. |
| AML | 43,690 | 5,000 | 33 | van Galen et al. |
| IMMUNE | 88,057 | 5,000 | 33 | Dominguez Conde et al. |

#### Clustering Performance

- **PBMC**: NCLUSION NMI = 0.80 (vs Seurat 0.77, $p = 1.08 \times 10^{-3}$; scLCA 0.62, $p = 1.90 \times 10^{-6}$). ARI = 0.67 (vs Seurat 0.62, $p = 1.17 \times 10^{-3}$)
- **Simulations**: Competitive with scDeepCluster (best performer) across all 4 scenarios, with NCLUSION in top 4 consistently
- **Generalization**: Statistically significantly better than or comparable to baselines across PDAC, AML, and IMMUNE datasets

#### Marker Gene Selection

- **Simulations**: NCLUSION and FESTEM are the only methods with high true-positive rate while maintaining low FDR and FPR. DUBStepR and singleCellHaystack have comparable TPR but dramatically higher FDR
- **PBMC**: 96% of NCLUSION's markers overlap with Seurat's much larger DE gene sets (e.g., 134 vs 1,780 for NK cells). NCLUSION identifies more refined, specific gene modules
- **GO enrichment**: NCLUSION gene modules recover known cell-type biology (B cell receptor signaling, NK cell cytotoxicity, T cell receptor signaling) including pathways missed by Seurat's larger gene sets

#### Scalability

- NCLUSION and KNN+Leiden are the only methods scaling past 100K cells
- NCLUSION is the only method reaching 1M cells
- On PBMC (94K cells): NCLUSION finishes 4.2 min faster than Seurat, 3.6 hours faster than scLCA, 11.5 hours faster than scCCESS-SIMLR

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Open-source code on GitHub with Zenodo archive (DOI: 10.5281/zenodo.18049775)
- All datasets publicly available with links
- Documentation website with tutorials
- Simulation framework clearly described with scDesign3

**Weaknesses**:
- Julia implementation (less accessible to bioinformatics community vs Python/R)
- Python wrapper (`nclusionpy`) is declared but has no actual Python module code
- Current Julia code contains adjusted-PIP and posterior effect/sign summaries, but their exact correspondence to the paper's Eqs. 5-9 and figure filters needs numerical verification
- Log-normalization function called but not defined in the repository (likely from a missing dependency)
- `lognormalization` base ambiguity: paper says $\log_2$, Python data script uses `ln` (natural log via `sc.pp.log1p`)

- “Infinite” clustering is implemented with a finite `KMax` ceiling (default 25); the model estimates occupied clusters below that ceiling rather than eliminating this computational choice.

**Practical notes**:
- Requires Julia 1.9+ with ~35 dependencies
- Default settings ($K_{\max}=25$, $\alpha_0=\gamma_0=1.0$, $\epsilon=10^{-6}$, max 500 iterations) work well for datasets up to ~100K cells
- For 1M+ cells, expect convergence to take longer; may need to increase `num_iter`
- Input: H5AD files; output: JLD2 files with cluster assignments and PIPs

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
