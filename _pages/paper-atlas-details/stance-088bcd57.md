---
layout: default
permalink: /paper-atlas/stance-088bcd57/
title: "STANCE"
nav: false
description: "空间转录组的一个 spot 往往混有多种细胞。某个基因在组织上呈现空间梯度，可能只是因为不同区域的细胞类型比例不同，也可能因为同一种细胞在不同位置真的改变了表达。传统 SVG 检验通常只能回答“这个基因整体上是否具有空间结构”，不能稳定地区分这两种来源。 STANCE 的目标是：给定基因表达、spot 坐标和每个 spot 的细胞类型比例，同时检验整体空间变异与每一种细胞类型内部的空间变异。"
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
      <span>Spatially Variable Genes</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>STANCE</h1>
    <p>STANCE: A Unified Statistical Model to Detect Cell-Type-Specific Spatially Variable Genes in Spatial Transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-57117-w" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STANCE 方法解读：在混合细胞的空间点位中寻找细胞类型特异的空间变异基因

### 1. STANCE 真正要解决的问题

空间转录组的一个 spot 往往混有多种细胞。某个基因在组织上呈现空间梯度，可能只是因为不同区域的细胞类型比例不同，也可能因为同一种细胞在不同位置真的改变了表达。传统 SVG 检验通常只能回答“这个基因整体上是否具有空间结构”，不能稳定地区分这两种来源。

STANCE 的目标是：给定基因表达、spot 坐标和每个 spot 的细胞类型比例，同时检验整体空间变异与每一种细胞类型内部的空间变异。论文把第一类候选称为 unified-type SVG（utSVG），再从中定位 cell-type-specific SVG（ctSVG）。

### 2. 输入、输出与对象流

输入有三张按 spot 对齐的表：基因 × spot 的计数矩阵、spot × 2 的坐标矩阵、spot × 细胞类型的比例矩阵；还可加入 spot 级协变量。`creatSTANCEobject()`取三者行列名交集并写入 S4 对象（`STANCE_code/R/createSTANCEobject.R:17-70`）。

输出分三层：

1. Stage 1 为每个基因给出整体 score statistic、原始 p 值和默认 BY 校正值；
2. Stage 2 为指定基因和细胞类型给出该细胞类型空间方差是否为零的检验；
3. `varcomp_est()`估计各细胞类型空间方差和残差方差，供机制解释与堆叠图使用。

### 3. 预处理并没有“拆出”细胞类型表达

`data_preprocess()`先缩放坐标、过滤低总计数 spot、去除线粒体与低检出率基因，再用 `SPARK::NormalizeVST`标准化（`STANCE_code/R/data_preprocess.R:19-74`）。细胞类型比例通常来自外部反卷积；STANCE 不在内部重新估计它，也不把混合表达矩阵显式拆成每个细胞类型的表达矩阵。

代码的坐标缩放写成：

$$
s'_{i,d}=\frac{s_{i,d}-\min(S)}{\max(S)-\min(S)},
$$

其中实现对两个轴共同使用整个坐标矩阵的全局最小值和最大值（`data_preprocess.R:31-35`），不是每一轴分别归一化。这一点会影响带宽的数值尺度，但旋转不变性的理论依据仍来自后续欧氏距离核。

### 4. 核心模型：把每种细胞类型的空间效应写成随机效应

对一个基因，在 $n$ 个 spot 上的标准化表达向量为 $\mathbf y$，STANCE 模型是：

$$
\mathbf y(\mathbf s)=\mathbf X(\mathbf s)\boldsymbol\beta+
\sum_{k=1}^{K}\boldsymbol\pi_k\odot\boldsymbol\gamma_k(\mathbf s)+
\boldsymbol\varepsilon.
$$

$\mathbf X$包含截距和协变量；$\boldsymbol\pi_k$是第 $k$ 种细胞在各 spot 的比例；$\boldsymbol\gamma_k$是该细胞类型随位置变化的潜在表达效应。模型规定：

$$
\boldsymbol\gamma_k\sim N(\mathbf0,\tau_k\mathbf K),\qquad
\boldsymbol\varepsilon\sim N(\mathbf0,\sigma_e^2\mathbf I).
$$

所以观测表达的协方差为：

$$
\mathbf V=\sum_{k=1}^{K}\tau_k\boldsymbol\Sigma_k+sigma_e^2\mathbf I,
\qquad
\boldsymbol\Sigma_k=\operatorname{diag}(\boldsymbol\pi_k)\mathbf K
\operatorname{diag}(\boldsymbol\pi_k).
$$

左、右两次乘细胞比例对角矩阵意味着：只有在某类细胞比例较高的 spot 对中，该类型的空间协方差才会强。代码逐类型构造的正是这个 $\boldsymbol\Sigma_k$（`STANCE_code/R/build_kernelMatrix.R:71-80`）。

### 5. 为什么核方法带来旋转与平移不变性

补充材料 §1.4 定义高斯空间核：

$$
K_{ij}=\exp\left\{-\frac{\|\mathbf s_i-\mathbf s_j\|^2}{h}\right\}.
$$

平移不会改变点间差，正交旋转也保持欧氏距离，因此核矩阵不变，依赖它的方差分量与 score 检验也不变。Figure 1 展示了从坐标到核、从细胞比例到类型特异协方差，再到两阶段检验的完整结构；旋转模拟则说明把原始坐标直接当固定效应的比较方法可能随组织方向改变结果。

代码使用 `KRLS::gausskernel(X=pos, sigma=bw)`（`build_kernelMatrix.R:67-69`）。若用户不指定带宽，spot 数不超过 5000 时对每个基因用 Sheather–Jones 规则，否则用 Silverman 规则，再取中位数（同文件 `44-64`）。这里带宽由表达分布估计后用于空间坐标核，是论文和实现一致但容易忽略的设计选择。

### 6. Stage 1：先找所有可能含空间信号的 utSVG

第一阶段检验联合原假设：

$$
H_0^{(1)}:\tau_1=\cdots=\tau_K=0.
$$

也就是所有细胞类型的空间随机效应都为零。代码先在只有截距/协变量和独立残差的零模型下构造投影矩阵：

$$
\widetilde{\mathbf P}_0=\mathbf I-\mathbf X(\mathbf X^T\mathbf X)^{-1}\mathbf X^T,
$$

并把各类型核相加为 $\boldsymbol\Sigma=\sum_k\boldsymbol\Sigma_k$。统计量为：

$$
U^{(1)}=\frac{\mathbf y^T\widetilde{\mathbf P}_0
\boldsymbol\Sigma\widetilde{\mathbf P}_0\mathbf y}{2\hat\sigma_e^4}.
$$

这些矩阵和统计量在 `STANCE_code/R/runTest1.R:17-52`直接实现。随后用 Satterthwaite 矩匹配把 $U$近似为 $a\chi_g^2$，其中 $a=v/(2e)$、$g=2e^2/v$（同文件 `94-110`）。`correction=TRUE`时还通过有效信息矩阵扣除估计残差方差造成的信息损失（`56-92`）。默认 `p.adjust(..., method="BY")`适用于基因间任意依赖，但通常比 BH 更保守。

Stage 1 的阳性集合是 SVG 与 ctSVG 的并集型候选，不等于“每个阳性基因都已经定位到某一细胞类型”。

### 7. Stage 2：逐个问某类细胞的空间方差是否存在

对候选基因和细胞类型 $l$，第二阶段检验：

$$
H_0^{(2)}:\tau_l=0,
$$

同时允许其他 $\tau_{k\ne l}$非零。它先用 `gaston::lmm.aireml`拟合排除第 $l$ 个核的约化模型，再构造：

$$
\mathbf V_{-l}=\sum_{k\ne l}\hat\tau_k\boldsymbol\Sigma_k+
\hat\sigma_e^2\mathbf I,
$$

以及广义最小二乘投影矩阵 $\mathbf P_{-l}$，最后计算：

$$
U_l^{(2)}=\frac12\mathbf y^T\mathbf P_{-l}
\boldsymbol\Sigma_l\mathbf P_{-l}\mathbf y.
$$

`runTest2()`的串行与并行分支都按这条路径实现：拟合约化 REML、重建 $\mathbf V_{-l}$、求逆、计算 $e/v$和缩放卡方 p 值（`STANCE_code/R/runTest2.R:72-167`、`169-267`）。C++ `invert()`只是 Armadillo 的矩阵求逆薄封装（`STANCE_code/src/matrix_inversion.cpp:1-8`），不是新的统计算法。

Stage 2 保存的是原始 p 值；代码没有在该函数内跨“基因 × 细胞类型”统一做多重校正。因此用户若以大量 Stage 2 检验做发现性结论，必须明确自己的校正族，而不能直接把 `p_value < 0.05`当作全局 FDR 5%。

### 8. 方差分解回答“信号主要来自谁”

检验只回答方差是否显著，效应大小则由完整模型的 AI-REML 估计：

$$
(\hat\tau_1,\ldots,\hat\tau_K,\hat\sigma_e^2)
=\operatorname{AI\mbox{-}REML}(\mathbf y,\mathbf X,
\boldsymbol\Sigma_1,\ldots,\boldsymbol\Sigma_K).
$$

`varcomp_est()`逐基因调用 `gaston::lmm.aireml`并保存所有类型方差与残差（`STANCE_code/R/varcomp_est.R:16-50`）。`CT_topGenes()`再除以分量总和得到相对解释比例并画堆叠图（`STANCE_code/R/CT_topGenes.R:27-82`）。显著性与解释比例是两回事：前者受采样不确定性影响，后者是拟合出的效应构成。

代码中 `CT_topGenes()`先得到显著基因列表，却在排序时没有用该列表过滤，而是对全部已估计基因排序（`CT_topGenes.R:41-48`）。因此输出的 `top_genes`未必都是该细胞类型 Stage 2 显著基因，这是使用时需要复核的实现边界。

### 9. 从用户视角看完整运行顺序

```text
counts + coordinates + cell-type proportions (+ covariates)
    ↓ creatSTANCEobject：按 spot 名称对齐
STANCE S4 object
    ↓ data_preprocess：QC、VST、坐标缩放
normalized expression + scaled coordinates
    ↓ build_kernelMatrix
Gaussian K + 每个类型的 Sigma_k
    ↓ runTest1
utSVG 候选（整体联合检验）
    ↓ runTest2（通常只对候选做）
每个细胞类型的 ctSVG p 值
    ↓ varcomp_est + CT_topGenes / visualizeGenePattern
方差贡献、候选排序和空间表达图
```

Figure 2–4 通过不同零假设、空间效应和细胞比例的模拟检验 I 类错误与功效；Figure 5–7 分析乳腺癌、肾癌和小鼠嗅球；Figure 8 比较把 utSVG/ctSVG 作为空间域识别特征的表现。补充图进一步展示旋转模拟、方差堆叠图、不同反卷积输入的鲁棒性与计算资源。

### 10. 如何理解论文的实验结果

模拟的关键不是“所有空间基因都更容易检出”，而是覆盖三种结构：整体 SVG 与 ctSVG 同时存在、只有细胞类型特异效应、以及不同类型效应在混合后抵消。后两类正是传统整体 SVG 筛选可能漏掉的对象。论文报告 STANCE 在多种离散度和细胞比例条件下保持 I 类错误，并在 ctSVG 功效上优于所比较的 spVC；低比例细胞类型依然更难检出，这是混合数据的信息限制而非算法可完全消除的问题。

真实数据部分用 HER2+ 乳腺癌、肾癌和小鼠嗅球展示不同细胞类型的 ctSVG 及通路富集，并把 utSVG/ctSVG 输入多种空间域方法。论文中某些组合的 ARI 提升支持这些特征有下游价值，但不能推广为对任意数据、任意聚类器都必然提升。

### 11. 论文—代码对应与复现边界

| 环节 | 本地实现 | 证据判断 |
|---|---|---|
| 输入对齐与 S4 对象 | `createSTANCEobject.R:17-70` | Exact |
| QC、VST、坐标缩放 | `data_preprocess.R:19-74` | Exact |
| 高斯核与 $\Sigma_k$ | `build_kernelMatrix.R:24-82` | Exact |
| Stage 1 score test | `runTest1.R:9-122` | Exact |
| Stage 2 类型检验 | `runTest2.R:1-268` | Exact |
| AI-REML 方差估计 | `varcomp_est.R:16-50` | Exact |
| 矩阵求逆加速 | `src/matrix_inversion.cpp:1-8` | Exact |
| 堆叠图与空间图 | `CT_topGenes.R:27-82`, `visualizeGenePattern.R:21-67` | Partial：展示函数存在，需注意筛选行为 |
| 论文全部模拟 | 当前 R 包不含完整模拟脚本 | Not found |
| 三个真实数据的全部反卷积结果 | 包内只附示例数据/教程 | Partial |

本地代码足以核对和运行核心统计方法；它不是论文所有仿真、数据准备和制图脚本的完整快照。外部依赖尤其包括 SPARK、KRLS 与 gaston，复现时还需要相容的 R 包版本。

### 12. 最容易误读的四点

1. utSVG 是 Stage 1 联合原假设的阳性集合，不是新的互斥生物学类别。
2. 旋转不变来自点间距离核；若输入比例或表达预处理随旋转改变，整个外部流程仍可能改变。
3. 比例矩阵的不确定性没有被 STANCE 核心检验显式传播，论文的稳健性实验不能替代每个数据集的反卷积质控。
4. Stage 2 的逐项 p 值与 `CT_topGenes()`的展示排序都需要用户在报告前自行做多重检验和显著基因过滤。

### 证据入口

- 主论文：`paper source/paper/paper.md`
- 补充推导与旋转模拟：`output_paper_supp_md/paper_supp/paper_supp.md`
- 主图图片：`paper source/paper/_page_*_Figure_2.jpeg`
- R/C++ 实现：`STANCE_code/R/`、`STANCE_code/src/`
- 详细公式与逐图说明：`doc_method.md`、`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STANCE: A Unified Statistical Model to Detect Cell-Type-Specific Spatially Variable Genes in Spatial Transcriptomics

**Paper**: Su, H., Wu, Y., Chen, B. & Cui, Y. *Nature Communications* 16, 1793 (2025)
**DOI**: [10.1038/s41467-025-57117-w](https://doi.org/10.1038/s41467-025-57117-w)
**Code**: [https://github.com/Cui-STT-Lab/STANCE](https://github.com/Cui-STT-Lab/STANCE) (R package, GPL-3.0)

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) technologies (10x Visium, Slide-Seq, MERFISH) enable profiling the transcriptome at spatial resolution. A key challenge is detecting **spatially variable genes (SVGs)** — genes whose expression displays non-random spatial patterns in tissue sections. Many SVGs correlate with cell-type compositions, giving rise to **cell-type-specific spatially variable genes (ctSVGs)** — genes with non-random spatial expression within specific cell types.

Critically, an SVG is not necessarily a ctSVG, and vice versa. A gene can be spatially variable overall but uniform within each cell type (SVG but not ctSVG). Conversely, a gene can show cell-type-specific spatial patterns that cancel out when cell types are mixed (ctSVG but not SVG).

#### Limitations of Existing Approaches

Three existing methods for ctSVG detection all treat cell-type-specific spatial effects as **fixed effects**, leading to a critical flaw: results are **not invariant to tissue rotation**. Since tissue sections are often randomly oriented during sample preparation, this dependency produces unreliable results.

| Method | Journal & Year | Limitation |
|--------|---------------|------------|
| **CTSV** | *Bioinformatics*, 2022 | ZINB regression with spatial coordinates as fixed effects; rotation-dependent; computationally expensive |
| **C-SIDE** | *Nature Methods*, 2022 | Poisson regression with basis expansion; choice of L=15 basis functions may overfit; tightly coupled to RCTD deconvolution |
| **spVC** | *Genome Biology*, 2024 | Two-stage Poisson regression; first stage filters for SVGs, missing ctSVGs that are not SVGs; rotation-dependent |

Additionally, SVG detection methods **SPARK** (*Nature Methods*, 2020), **SPARK-X** (*Genome Biology*, 2021), and **nnSVG** (*Nature Communications*, 2023) detect SVGs but cannot identify ctSVGs.

#### Unique Contributions

1. **Rotation invariance**: Uses distance-based kernel matrices (Gaussian kernel) that depend only on pairwise Euclidean distances, which are invariant under rotation
2. **Unified framework**: A two-stage testing procedure that captures both SVGs and ctSVGs through a single model, introducing "unified-type SVGs" (utSVGs)
3. **Variance decomposition**: Decomposes spatial variance into cell-type-specific components, enabling visualization of relative variance contributions
4. **Improved downstream analysis**: utSVGs and ctSVGs as input features improve spatial domain detection over traditional SVGs

---

### Method Overview

#### Algorithmic Framework

STANCE models gene expression as a **linear mixed-effect model** integrating three data sources:
- Gene expression (normalized counts)
- Spatial coordinates of spots
- Cell-type composition from deconvolution

The model decomposes gene expression into:
1. **Non-spatial fixed effects** $\mathbf{X}(\mathbf{s})\boldsymbol{\beta}$ (intercept and covariates)
2. **Cell-type-specific spatial random effects** $\boldsymbol{\pi}_k \odot \boldsymbol{\gamma}_k(\mathbf{s})$ for each cell type $k$
3. **Residual error** $\boldsymbol{\varepsilon}(\mathbf{s})$

Each cell-type spatial effect follows $\boldsymbol{\gamma}_k(\mathbf{s}) \sim \text{MVN}(\mathbf{0}, \tau_k \mathbf{K})$, where $\mathbf{K}$ is a Gaussian kernel matrix and $\tau_k$ is the variance component.

#### Two-Stage Testing

- **Stage 1 (Overall Test)**: Tests $H_0: \tau_1 = \cdots = \tau_K = 0$ using a score statistic approximated by a scaled chi-square distribution. Genes passing this test are "utSVGs" (union of SVGs and ctSVGs).
- **Stage 2 (Individual Test)**: For each cell type $k$, tests $H_0: \tau_k = 0$ by fitting a reduced model excluding cell type $k$ and computing a score statistic. Identifies ctSVGs from utSVGs.

#### Computational Pipeline

1. Data preprocessing: spot/gene QC, VST normalization, coordinate scaling
2. Kernel construction: Gaussian kernel with automatic bandwidth selection (Sheather-Jones or Silverman's rule)
3. Stage 1 test: score test for all genes → FDR control → utSVG list
4. Stage 2 test: per-gene per-cell-type score tests → ctSVG list
5. Variance component estimation via REML (AI-REML from `gaston`)
6. Downstream: stacked variance plots, spatial domain detection, gene set enrichment analysis

---

### Evaluation

#### Datasets

| Dataset | Technology | Spots | Genes (after QC) | Cell Types | Source |
|---------|-----------|-------|-------------------|------------|--------|
| HER2+ Breast Cancer | 10x Visium | 607 | 2,816 | 8 | Andersson et al., *Nat. Commun.*, 2021 |
| Kidney Cancer | 10x Visium | 2,917 | 7,270 | 12 | Li et al., *Cancer Cell*, 2022 |
| Mouse Olfactory Bulb | ST (100 μm²) | 260 | 7,365 | 12 | Ståhl et al., *Science*, 2016 |

#### Metrics

- **Type I error control**: Q-Q plots of $-\log_{10}(p)$ with 95% error bands
- **Testing power**: Power vs FDR curves across different dispersion and cell-type proportion settings
- **Domain detection accuracy**: Adjusted Rand Index (ARI) using SpatialPCA, BayesSpace, stLearn, SpaceFlow, SeuratPCA
- **Biological validation**: Gene set enrichment analysis of ctSVGs per cell type

#### Key Results

| Comparison | Result |
|-----------|--------|
| STANCE vs SPARK-G/SPARK-X (SVG detection) | STANCE ≥ SPARK-G > SPARK-X in detecting SVGs (Simulation Alt. Case 3) |
| STANCE vs spVC (ctSVG detection) | STANCE outperforms spVC across all dispersion/proportion settings; spVC fails on HER2+ and MOB datasets |
| Rotation invariance | STANCE results unchanged under rotation; spVC produces inconsistent ctSVG lists at 0°, 30°, 60° |
| Domain detection (ARI) | utSVGs (0.45) > ctSVGs (0.42) > SPARK-G SVGs (0.39) with SpatialPCA on breast cancer data |
| Robustness to deconvolution | STANCE-RCTD ≈ STANCE-oracle; robust even under misspecified cell-type compositions |

#### Computational Performance (MOB dataset: 7,365 genes, 260 spots, 12 cell types)

| Method | Time | Memory |
|--------|------|--------|
| SPARK-X | 9.84 s | 170 MB |
| STANCE Stage 1 | 31.58 s (incl. 14.27 s preprocessing) | 448 MB |
| SPARK-G | 1.65 min | 3.63 GB |
| STANCE Stage 2 | 16.4 min (828 utSVGs × 12 cell types) | 95.6 GB |
| spVC | 1.13 h (excl. triangulation setup) | 117 GB |
| CTSV | ~63 h (estimated from 10-gene subset) | N/A |

Stage 1 is fast (comparable to SPARK-G); Stage 2 is the bottleneck due to per-gene per-cell-type REML fits. Computational cost scales $O(n^3)$ with spot count due to kernel matrix operations.

#### Benchmarked Methods

| Method | Journal & Year | Type |
|--------|---------------|------|
| SPARK-G | *Nature Methods*, 2020 | SVG detection |
| SPARK-X | *Genome Biology*, 2021 | SVG detection (nonparametric) |
| spVC | *Genome Biology*, 2024 | ctSVG detection |
| CTSV | *Bioinformatics*, 2022 | ctSVG detection |
| C-SIDE | *Nature Methods*, 2022 | ctSVG detection |

---

### Reproducibility

#### Rating: 4/5

**Strengths**:
- R package publicly available on GitHub with clear documentation and tutorial
- Example dataset (mouse olfactory bulb) included in the package
- Clean, well-structured codebase with ~570 lines of R + C++ code
- Dependencies are standard R packages (gaston, KRLS, SPARK, ggplot2)
- All three real datasets are from public sources (Zenodo, Mendeley, spatialresearch.org)

**Potential Blockers**:
- SPARK package dependency requires `devtools::install_github("xzhoulab/SPARK")` (not on CRAN)
- No simulation scripts included in the repository — only the R package for real data analysis
- Specific deconvolution results (Stereoscope, CARD, STdeconvolve) used in the paper are not provided; users must run deconvolution themselves
- Computational cost may be high for large datasets (>5000 spots) due to $n \times n$ kernel matrix operations

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
