---
layout: default
permalink: /paper-atlas/spatopic-a950d2a3/
title: "SpaTopic"
nav: false
description: "SpaTopic 不读取原始表达矩阵，而把每个细胞的类型当作“词”、局部空间区域当作“文档”、组织微环境当作“主题”。它通过锚点近邻和折叠 Gibbs 采样，同时推断每个细胞属于哪个空间区域、哪个主题，从而在多张图像中共享一套可解释的细胞类型组成。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>SpaTopic</h1>
    <p>Scalable topic modelling decodes spatial tissue architecture for large-scale multiplexed imaging analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-61821-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpaTopic">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xiyupeng/SpaTopic" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaTopic">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaTopic 方法解读：用空间主题模型寻找跨切片复现的细胞生态位

### 一句话理解

SpaTopic 不读取原始表达矩阵，而把每个细胞的类型当作“词”、局部空间区域当作“文档”、组织微环境当作“主题”。它通过锚点近邻和折叠 Gibbs 采样，同时推断每个细胞属于哪个空间区域、哪个主题，从而在多张图像中共享一套可解释的细胞类型组成。

### 输入与输出

`SpaTopic_inference()` 接收一张或多张表，每行一个细胞，至少含 `image, X, Y, type`。结果的上限首先受上游分割和细胞类型注释约束：SpaTopic 能汇总已有标签的空间共现，却不能纠正所有系统性错注释，也不能恢复输入中没有的分子状态。

主要输出包括：`Beta`（细胞类型×主题组成）、`Z.trace`（细胞×主题后验频率）、`cell_topics`（逐细胞最大后验硬标签）、`Theta`（区域×主题组成），以及训练集似然/困惑度和 `trace=TRUE` 时的 DIC。主题编号没有跨运行的固定语义，必须结合组成、位置与外部组织学证据解释。

### 为什么需要“可移动的文档”

普通 LDA 已知每个词属于哪个文档；组织中没有天然固定的局部文档。SpaTopic 用边长 $2r$ 的网格分层抽样锚点，再为每个细胞只保留最近的 $m$ 个锚点（默认 5）。区域归属 $D_{gi}$ 不是固定标签，而是采样变量。

$$K(x_{gi}^{c},x_d^d)\propto\mathbf{1}\{d\in\mathcal N_m(i)\}\exp(-\|x_{gi}^{c}-x_d^d\|_2/\sigma).$$

代码在 `src/Gibbs.cpp:391-403` 把这 $m$ 个权重归一化。较小 $\sigma$ 强化局部约束，较大 $\sigma$ 让细胞类型组成更多地决定区域归属。`region_radius` 与 $\sigma$ 都按输入坐标单位解释，像素和微米不能直接共用同一数值。

### 折叠 Gibbs 采样

每个主题有细胞类型分布 $\beta_k$，每个区域有主题分布 $\theta_d$；默认稀疏 Dirichlet 先验在代码中为 `beta=0.05`（论文 $\psi$）和 `alpha=0.01`。采样时把 $\beta$、$\theta$ 积分掉，只更新：

1. 固定区域 $d$，按“区域中的主题计数”乘“主题中的此细胞类型计数”采样 $Z_{gi}$。
2. 固定新主题 $k$，按“候选区域的主题比例”乘空间核采样 $D_{gi}$。

实现先删去当前细胞计数，采样后再加回（`src/Gibbs.cpp:275-327`）。对所有候选主题相同的分母被省略，是合法归一化简化。默认烧入 1000 次，收集 200 个样本，间隔 20 次更新。`Z.trace` 汇总所有样本；`Beta` 与 `Theta` 却由最终状态计算，并非后验样本平均。

### 初始化与模型选择

代码默认做 10 次随机初始化，各跑 100 次短链，保留训练困惑度最低者；这等价于对数似然最高者。主题数 $K$ 仍由用户指定。论文建议对 $K=2\ldots9$ 运行 `trace=TRUE` 并按 DIC 选择，但计算更慢，而且训练数据上的 DIC 选择不等于外部生物学验证。

### 图 1–6 的证据链

- 图 1 展示锚点、区域/主题交替采样及 LDA 图模型，直接对应实现主线。
- 图 2 在 CosMx NSCLC 中报告七个主题，并用 KRT17、IL7R、MS4A1 辅助解释肿瘤和 TLS；KRT17 一致性是特定标记物指标，不是通用分割精度。
- 图 3 以 H&E 和 CD3/CD20/PanCK-SOX10 支持 mIF 黑色素瘤的 TLS 主题；这是作者的组织学对应，不是盲法病理诊断试验。
- 图 4 在 26 个健康肺 IMC ROI 上与人工区域比较，SpaTopic ARI 与 UTAG 大致相当；它不支持“全面优于 UTAG”。
- 图 5 联合分析九张小鼠脾 CODEX 图，展示疾病阶段相关主题变化。共现提示相互作用假说，但不能直接建立细胞通讯或因果关系。
- 图 6 是指定硬件、参数和数据规模下的运行时间；“分钟级”不能直接外推到任意数据或 `trace=TRUE`。

### 论文与代码差异

核心模型、指数核、$Z/D$ 条件采样、$\beta/\theta$ 估计、困惑度和 DIC 均有直接实现，但需保留边界：

1. 论文说 $\sigma$ 可以在 Gibbs 中采样；代码在循环前一次性构造核，未实现 $\sigma$ 学习。
2. `Beta`、`Theta` 使用最终状态；只有 `Z.trace` 跨样本累计。
3. 论文使用 SpaTopic 1.1.0；本地 `DESCRIPTION` 是开发版 1.2.0.9000，含论文主方法之外的 3D/接口更新。
4. 快照只有 GitHub coverage 工作流，未发现单元测试目录，不能据此确认当前测试覆盖率。
5. `do.parallel` 只并行多图像锚点初始化；主 Gibbs 链没有实现多链并行。
6. 多图输入必须使用列表且 image ID 唯一，主函数会拒绝列表数量与 ID 数不一致的输入。
7. 从同主题只能得到空间共定位假说，不能推出分子通讯或因果关系。

### 可复现边界

本地包足以核对并运行核心算法；论文完整 benchmark 代码位于另一个 `SpatialTopic_Analysis_codes` 仓库，不在当前快照中。完整复现还需下载平台数据、固定上游注释、按坐标单位调节 $r/\sigma$、为多个 $K$ 重跑并检查收敛。因此结论是“核心实现高度对应”，不是“论文全部结果一键复现”。

### 直接证据

- 论文/图：`paper source/PMC12274411/paper.md`、`paper source/PMC12274411/images/`
- R 入口：`SpaTopic/R/Gibbs_sampler.R:1-503`
- C++ 核心：`SpaTopic/src/Gibbs.cpp:77-475`
- 锚点抽样：`SpaTopic/R/spatial_func.R`
- 教程：`SpaTopic/vignettes/`
- 快照：`https://github.com/xiyupeng/SpaTopic`，提交 `8704c78`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaTopic: Scalable Spatial Topic Modelling for Multiplexed Tissue Imaging

**Paper**: Scalable topic modelling decodes spatial tissue architecture for large-scale multiplexed imaging analysis
**Journal**: *Nature Communications* 16 (2025)
**DOI**: 10.1038/s41467-025-61821-y
**Code**: https://github.com/xiyupeng/SpaTopic (CRAN R package SpaTopic)

---

### Motivation & Novelty

Multiplexed tissue imaging platforms (CODEX, mIF, IMC, Nanostring CosMx, 10× Xenium) generate spatial maps of millions of single cells profiled for tens to thousands of markers. A key analytical goal is identifying **recurrent spatial patterns of cell types** — tissue microenvironments (TMEs) like tumor nests, immune zones, and tertiary lymphoid structures (TLSs) — across multiple patient samples, and linking them to clinical outcomes.

#### Why existing methods fall short

| Method | Limitation |
|--------|-----------|
| Seurat v5 (*Nat. Biotechnol.* 2024) | K-means clustering of per-cell KNN neighborhoods; O(n log n) KNN construction is prohibitive for >100k cells per image |
| Spatial-LDA (v0.1.3) | Spatial priors incorporated but per-cell neighborhood extraction still required; does not scale to millions of cells |
| UTAG (*Nat. Methods* 2022) | Uses raw gene expression as input (not cell-type annotations); relies on homogeneous expression assumptions that fail for heterogeneous structures like TLSs; high memory usage |
| BankSY (*Nat. Genet.* 2024) | Expression-based spatial features; requires batch correction that can over-correct, masking biologically real differences between normal and diseased tissue |
| CytoCommunity (*Nat. Methods* 2024) | Graph neural network requiring GPU; cannot handle multi-image joint analysis in unsupervised mode; impractical for labs without HPC |

All neighborhood-based methods extract per-cell features before clustering, which scales poorly. None of them can identify topics jointly across multiple images in a principled probabilistic framework.

#### What SpaTopic contributes

1. **Spatial LDA with overlapping regions**: Instead of one document per image (standard LDA used in the authors' prior work on flow cytometry, *Cell Rep. Methods* 2023), SpaTopic partitions each image into overlapping spatial regions anchored at stratified-sampled anchor cells. Cells are soft-assigned to regions weighted by spatial proximity.

2. **Scalability via anchor-based KNN**: By building the KNN graph only between $n$ cells and $m \ll n$ anchor cells (not among all $n$ cells), KNN construction drops from $O(n \log n)$ to $O(n \log m)$. Gibbs sampling is linear in cells. Result: 100k cells in ~1 min on a MacBook Air.

3. **Joint multi-image analysis**: All images are analyzed simultaneously in a single model, enabling topics to be shared across patients and conditions. This directly enables disease progression analysis.

4. **Cell-type input (not raw expression)**: This makes topics directly interpretable and avoids modeling expression-space batch effects, but transfers dependence to the accuracy and cross-image consistency of upstream phenotyping.

---

### Method Overview

SpaTopic adapts the **Latent Dirichlet Allocation (LDA)** model to spatial cell-type data. The fundamental analogy:

| NLP | SpaTopic |
|-----|---------|
| Document corpus | Set of tissue images |
| Document | Spatial region (anchored at a cell) |
| Word | Cell type |
| Topic | Tissue microenvironment (TME) signature |

**Key innovation**: Standard LDA treats each image as one document with fixed word-document membership. SpaTopic introduces a latent region assignment variable $D_{gi}$ for each cell, weighted by an exponential spatial kernel $K(\mathbf{x}^c_{gi}, \mathbf{x}^d_d) \propto \exp(-\|\mathbf{x}^c - \mathbf{x}^d\|_2 / \sigma)$. This allows spatial proximity to influence group membership while preserving the probabilistic structure of LDA.

**Algorithm**:
1. **Initialization**: Stratified sampling of anchor cells (grid $2r \times 2r$); kd-tree KNN to find $m=5$ nearest anchors per cell; warm start (10 random initializations × 100 iterations, keep lowest perplexity)
2. **Collapsed Gibbs sampling**: Jointly samples topic assignments $Z_{gi}$ and region assignments $D_{gi}$ for each cell, with parameters $\beta_k$ (topic-celltype distributions) and $\theta_d$ (region-topic distributions) integrated out analytically
3. **Output**: $\hat\beta_{kv}$ (topic content = cell-type composition), posterior $P(Z_{gi} = k)$ per cell, topic assignments, region-topic distributions
4. **Model selection**: DIC (Deviance Information Criterion) used to select number of topics $K$ (typically tested over K=2–9)

**Computational defaults**: burnin=1000, niter=200, thin=20; implemented in C++ via RcppArmadillo.

---

### Evaluation

#### Datasets

| Dataset | Platform | Cells | Images | Cell types | Purpose |
|---------|----------|-------|--------|-----------|---------|
| NSCLC (Lung5-1) | Nanostring CosMx | ~100k | 1 | 38 | Primary benchmark; TLS detection |
| mIF Melanoma | Multiplexed IF | ~400k | 1 (whole-slide) | 7 | TLS detection, whole-slide analysis |
| IMC Healthy Lung | Imaging Mass Cytometry | ~20k (26 ROIs) | 26 | 7 | Domain recovery, ARI comparison |
| CODEX Mouse Spleen | CODEX | ~700k | 9 | 27 | Multi-image, disease progression |
| Simulated | — | 10k–360k | 1 | 5 | Scalability benchmarking |

#### Results

**Quality**: On the NSCLC dataset, SpaTopic and UTAG are the only two methods achieving >0.8 consistency between identified tumor domains and KRT17 (tumor marker) expression. SpaTopic distinctly identifies TLS as a separate topic (B cells + CD4 T cells + dendritic cells), which BankSY and UTAG miss because they do not use cell-type annotations as input and assume homogeneous expression in neighborhoods.

**TLS detection**: Consistently identified across platforms (CosMx 960-plex, 12-plex mIF), with topic composition (B cells + CD4 T cells + small fractions of CD8 T and Treg) matching established TLS biology (Schumacher & Thommen, *Science* 2022).

**Disease progression** (mouse spleen, CODEX): SpaTopic identifies 6 topics across 9 images spanning normal, early, intermediate, and late lupus stages. Key findings: Topic 6 (Erythromyeloid niche) replaces Topic 1 (Red pulp) in lupus; Topic 5 (Double Negative T cell niche) appears at late disease stage. Other methods (Spatial-LDA, UTAG, BankSY) failed to detect this transition, partly due to over-correction of batch effects.

**Domain recovery** (healthy lung, IMC): SpaTopic achieves ARI comparable to UTAG (which uses raw expression, not cell types) while using only cell-type annotations.

**Scalability**: On simulated datasets, SpaTopic runtime scales linearly, while Seurat v5 scales super-linearly ($O(n^2)$ for KNN). At 360k cells, SpaTopic completes in ~200s vs. Seurat v5 at ~2100s. On the 700k-cell CODEX spleen dataset, SpaTopic runs in ~10 min while Seurat v5 and UTAG require minutes to tens of minutes; CytoCommunity required an HPC server.

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- R package on CRAN (SpaTopic v1.1.0); easy installation: `install.packages("SpaTopic")`
- All 4 benchmark datasets publicly available with download links in Methods
- Analysis code is available in a separate GitHub repository, not included in this local package snapshot
- Detailed Methods section with exact parameters used per dataset
- Vignettes cover basic usage, model selection, 3D analysis

**Limitations**:
- No automated parameter selection for σ and r (user must tune manually, guided only by the heuristic σ ≈ √r)
- Running time with `trace=TRUE` (needed for DIC) is substantially longer
- Benchmark code is in a separate repository from the package and requires installing all compared methods
- σ-sampling mentioned in paper but not implemented — users cannot adaptively learn the spatial scale
- `Beta` and `Theta` come from the final Gibbs state; only `Z.trace` accumulates across posterior samples
- The local snapshot is development version 1.2.0.9000, whereas the paper reports v1.1.0

**Environment**:
```r
install.packages("SpaTopic")     # CRAN
library(SpaTopic)
# Dependencies: RANN, sf, Rcpp, RcppArmadillo, foreach (see DESCRIPTION)
# Optional parallel: install.packages("doParallel")
```

**Common pitfalls**:
- Setting `region_radius` without accounting for image resolution (pixels vs. microns can differ 10-100×)
- Setting `sigma` independently of `region_radius` — start with σ ≈ √r and tune
- Forgetting `trace=TRUE` when DIC model selection is needed (adds substantial compute)
- On complex images (e.g., 26 small ROIs), increasing `ninit` (e.g., to 200) is critical for stable results
- Multi-image datasets: each image MUST have a unique ID in the `image` column

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
