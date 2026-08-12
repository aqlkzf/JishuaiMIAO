---
layout: default
permalink: /paper-atlas/spanorm-7b050e82/
title: "SpaNorm"
nav: false
description: "SpaNorm 可以理解为“空间负二项 GLM 归一化”：对每个基因同时拟合空间 biology 和空间 library-size 效应，然后在生成 PAC/logPAC 时只保留 biology-only 均值，从而尽量去掉区域性 library-size bias，同时保留空间 domain 和 SVG 信号。"
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
      <span>Domain Clustering</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>SpaNorm</h1>
    <p>SpaNorm: spatially-aware normalization for spatial transcriptomics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03565-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaNorm 方法中文解读

### 1. 这篇论文要解决什么问题？

SpaNorm 解决的是空间转录组（spatial transcriptomics, ST）中的归一化问题。传统单细胞 RNA-seq 归一化通常把 library size 当作全局技术因素处理；但在空间数据中，library size 往往和组织区域相关。论文指出，标准全局 library-size 归一化可能在去除技术效应的同时，把空间区域相关的真实生物信号也一起去掉（`paper.md:31-36`）。

SpaNorm 的核心目标是：同时建模 library size 效应和真实空间生物变化，把二者分开，只去除 library-size 相关部分，保留生物学空间结构。论文摘要明确说 SpaNorm “concurrently models library size effects and the underlying biology, segregates these effects”，并在 27 个样本、6 个数据集、4 种平台上评估（`paper.md:25-27`）。

### 2. 为什么已有方法不够？

论文比较和讨论的已有方法包括：不归一化、scran、sctransform、RUV-III-NB、Giotto 和 SpaNorm（`paper.md:145-157`）。这些方法中的许多来自 scRNA-seq 或通用空间分析流程，主要问题是：

1. **忽略空间信息**：只用全局 size factor，无法处理不同组织区域 library-size bias 不同的情况。
2. **可能损失空间 domain 信号**：当某个组织区域天然 library size 较低或较高时，简单校正会把区域差异误认为技术噪音。
3. **影响下游任务**：空间 domain 聚类、区域分割、空间变异基因（SVG）检测都会受影响（`paper.md:31-36`）。

SpaNorm 的创新点是利用空间坐标和基因表达共同建模，把平滑空间变化拆成两部分：一部分是 biology，一部分是和 library size 相关的技术/混杂效应（`paper.md:37-39`）。

### 3. SpaNorm 的数学模型

对基因 $g$ 和 spot/cell $c$，论文假设计数服从负二项分布：

$$z_{gc} \sim \text {Negative Binomial(NB)}(\mu _{gc},\psi _g),$$

其中 $\psi_g$ 是基因特异的离散度参数。均值使用 log-linear 模型（`paper.md:116-118`）：

$$\begin{aligned} \log \mu _{c,g} = \zeta _g + f_g(x_c,y_c; \beta _{\textbf{g}}) + \{\alpha + h_g(x_c,y_c; \gamma _g)\} \log LS_c. \end{aligned}$$

各项含义：

- $\zeta_g$：基因 $g$ 的基线表达。
- $(x_c,y_c)$：spot/cell 的空间坐标。
- $LS_c$：spot/cell 的 library size 或 size factor。
- $f_g(x_c,y_c;\beta_g)$：与 library size 无关的平滑空间生物变化。
- $\alpha\log LS_c$：所有基因共享的全局 library-size 效应。
- $h_g(x_c,y_c;\gamma_g)\log LS_c$：基因特异、位置相关的 library-size 效应。

因此 SpaNorm 的关键思想是：

```text
观测计数 z_gc
   -> 负二项 GLM 拟合 log(mu_gc)
   -> 分解为：基因基线 + 空间 biology + 空间 library-size 效应
   -> 生成调整后数据时只保留 biology，不保留 library-size 项
```

### 4. 空间平滑函数

论文把两个空间函数写成二维 spline 展开（`paper.md:118-120`）：

$$\begin{aligned} f_g(x_c,y_c; \beta _{\textbf{g}}) = \sum \limits _{i=1}^K \sum \limits _{j=1}^K \beta _{g,ij} B_i(x_c)B_j(y_c); \end{aligned}$$

$$\begin{aligned} h_g(x_c,y_c; \gamma _{\textbf{g}}) = \sum \limits _{i=1}^K \sum \limits _{j=1}^K \gamma _{g,ij} B_i(x_c)B_j(y_c). \end{aligned}$$

默认 $K=6$。论文还说明对 $\beta_{g,ij}$ 和 $\gamma_{g,ij}$ 使用 $L_2$ penalty，默认 $\lambda=10^{-4}N$，其中 $N$ 是细胞数（`paper.md:120-120`）。

代码中对应实现位于 `R/mainSpaNorm.R`：

- `fitSpaNorm()` 缩放坐标，构建 biology spline 和 library-size spline（`R/mainSpaNorm.R:207-215`）。
- 设计矩阵是 `~ logLS + bs.xy.bio + logLS:bs.xy.ls`（`R/mainSpaNorm.R:226-226`）。
- `wtype` 把设计矩阵列标记为 `biology`、`ls` 或 `batch`（`R/mainSpaNorm.R:228-231`）。
- 代码中的 spline 是 `splines::ns()` 自然样条的二维乘积，并按组织长宽比例调整 x/y 方向自由度（`R/mainSpaNorm.R:303-335`）。这是一个实现细节：论文主文称 B-splines，代码实际用 natural spline product。

### 5. PAC：如何生成归一化后的表达矩阵？

论文使用 percentile-invariant adjusted count（PAC）。直观理解：

1. 在完整模型（包含 library-size 效应）下，看观测计数处于该负二项分布的哪个分位数。
2. 再在只含 biology、不含 library-size 效应的负二项分布中，取同样分位数对应的计数。
3. 这样保留“这个观测在模型中的相对位置”，但去掉 library-size 对均值的影响。

论文公式为（`paper.md:122-124`）：

$$\begin{aligned} F_{NB}^{-1}\left( \frac{l_{gc}+u_{gc} }{2}; \mu _{gc} = \exp \{\hat{\zeta }_g + f_g(x_c,y_c; \hat{\beta }_{\textbf{g}})\},\psi =\hat{\psi }_g\right) . \end{aligned}$$

其中 $l_{gc}$ 和 $u_{gc}$ 是在包含 library-size 效应的完整模型下计算的负二项 CDF 上下界。论文说 log PAC 是 $\log(PAC+1)$。

代码中 `normaliseLogPAC()` 的直接行为（`R/fitSpaNormNB.R:307-329`）：

- 先计算完整模型均值 `mu`。
- 再用 `wtype == "biology"` 的列计算 biology-only 均值 `mu.2`。
- 对过大的 dispersion 做 winsorization。
- 计算 `lb`、`ub` 和中点概率 `p=(lb+ub)/2`。
- 把 `p` 截断到 `[0.001,0.999]`。
- 返回 `log2(qnbinom(p, mu=scale.factor*mu.2, size=1/psi)+1)`。

因此，代码和论文核心公式一致，但代码有几个主文未写明的实现细节：base-2 log、概率截断、dispersion 截断，以及 `scale.factor`。

### 6. 代码中的完整计算流程

已验证代码目录：`[local path omitted]`，commit `49138bf4e18584d04a04ad40586c2f5d16120119`。

#### 6.1 输入与对象接口

`SpaNorm()` 支持 `SpatialExperiment` 和 `Seurat`：

- SpatialExperiment 方法读取 `counts`、`spatialCoords` 和 `sizeFactors`，拟合模型后写入 `logcounts`（`R/mainSpaNorm.R:73-115`）。
- Seurat 方法读取默认 assay 的 `counts`，提取空间坐标，拟合模型后写入 `data` layer（`R/mainSpaNorm.R:129-167`）。

#### 6.2 建模

`fitSpaNorm()` 做以下事情（`R/mainSpaNorm.R:176-260`）：

1. 检查 `sample.p`、`lambda.a`、`gene.model`。
2. 缩放坐标。
3. 构建 biology spline 和 library-size spline。
4. 如果没有外部 size factor，则用 scran 计算 sum factors。
5. 构建设计矩阵 `W`。
6. 标记 `wtype`。
7. 随机抽样部分 cells/spots 用于拟合，默认 `sample.p=0.25`。
8. 调用 `fitSpaNormNB()` 拟合负二项模型。
9. 返回 `SpaNormFit` 对象。

#### 6.3 参数估计

`fitSpaNormNB()` 外层循环估计基因离散度并调用 `fitNBGivenPsi()` 拟合均值参数（`R/fitSpaNormNB.R:4-103`）。离散度用 `edgeR::estimateDisp(..., tagwise=TRUE, robust=TRUE)` 估计（`R/fitSpaNormNB.R:49-60`）。

`fitNBGivenPsi()` 是 IRLS-like 更新（`R/fitSpaNormNB.R:106-304`）：

- 构造 working vector `Z`。
- 用加权最小二乘更新 `alpha`。
- 当 `is.spanorm=TRUE` 时，把第一列 library-size 系数设为所有基因共享的平均值，对应论文中的全局 $\alpha$（`R/fitSpaNormNB.R:167-221`）。
- 对系数异常值做 median ± 4 MAD 截断。
- 更新 `gmean`。
- 如果 log-likelihood 变差，则 step halving。
- 根据相对 log-likelihood 收敛或最大迭代停止。

#### 6.4 输出

`getAdjustmentFun()` 把 `auto` 和 `logpac` 映射到 `normaliseLogPAC`；还支持 `pearson`、`medbio`、`meanbio`（`R/mainSpaNorm.R:339-350`）。论文主方法对应 PAC/logPAC，其他输出是包提供的附加功能。

### 7. 论文如何评估 SpaNorm？

论文评估了 6 个数据集、27 个样本、4 个平台：Visium、Xenium、STOmics、CosMx（`paper.md:25-27`, `paper.md:126-131`）。主要评估包括：

1. **区域特异 library-size 效应**：比较全局 LS 模型和区域/空间变化 LS 模型，估计需要 region-specific LS 效应的基因比例（`paper.md:158-170`）。
2. **网格特异 LS 异质性**：把组织划分为 rectangular grids，用 Cochran’s Q 检验不同 grid 的 LS 效应异质性（`paper.md:172-176`）。
3. **空间 domain 聚类**：用 graph-based、BayesSpace、SpaGCN 聚类，并用 ARI 与人工注释区域比较（`paper.md:190-200`）。
4. **空间变异基因检测**：用 MERINGUE 对不同归一化结果做 SVG 检测，并比较模拟真值、真实 marker 和 replicate concordance（`paper.md:202-206`）。
5. **分割和体积归一化鲁棒性**：在 Xenium breast cancer 数据中比较不同 segmentation 和 library-size/area-volume normalization（`paper.md:216-226`）。

### 8. 主图告诉我们什么？

- **Fig. 1**：可视化展示 library size 的区域差异、sctransform 与 SpaNorm 的 UMAP 差别，以及 SpaNorm 工作流。图中公式直接对应 NB GLM 分解。
- **Fig. 2**：Panel A 显示很多数据集中有较高比例基因存在 region-specific LS effect；Panel B 用 ARI 展示不同归一化对空间聚类的影响。
- **Fig. 3**：展示 mouse hippocampus 中多个 marker/SVG 在不同归一化方法下的空间表达图；SpaNorm 对 CA 区域 marker 的空间信号较清楚。
- **Fig. 4**：展示 SVG 统计量在 replicate 间的一致性和相对排名，说明 raw/no normalization 可能受到 library-size 效应影响。
- **Fig. 5**：MOBP 是 DLPFC white matter marker；图中 white matter 区域 library size 低。其他方法很难恢复 WM 中 MOBP 信号，而 SpaNorm、SpaNorm(sf=4)、Mean Bio/Med Bio 显示更符合预期的 WM 信号。

这些结论来自本地读取主图图片，并结合论文正文 `paper.md`。

### 9. 局限性与复现注意事项

论文明确指出：如果 log library size 的空间自相关非常高，SpaNorm 可能更难区分真实 biology 和 LS smooth variation（`paper.md:104-105`）。此外，FOV/batch effect 可能有不连续空间模式，而 SpaNorm 依赖平滑分解；作者说正在扩展模型处理 FOV effect（`paper.md:106-109`）。

代码复现方面：

- 已获得的 Bioconductor 包实现了 SpaNorm 核心算法、测试和 vignette。
- 未在该包快照中找到完整 27 个样本 benchmark 脚本；已搜索 `R/`、`tests/`、`vignettes/`、`README.md`。
- 论文提到分析代码存放在 Zenodo（`paper.md:260-267`），但这不等同于当前包目录包含全部 benchmark pipeline。
- Additional file 2 是 PDF，没有 `SUPP_MD`，所以这里不展开未从主文或代码直接验证的算法细节。

### 10. 一句话总结

SpaNorm 可以理解为“空间负二项 GLM 归一化”：对每个基因同时拟合空间 biology 和空间 library-size 效应，然后在生成 PAC/logPAC 时只保留 biology-only 均值，从而尽量去掉区域性 library-size bias，同时保留空间 domain 和 SVG 信号。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaNorm — Summary

### What problem does the paper solve?

Spatial transcriptomics data often have library sizes that vary by tissue region. Standard single-cell-style normalization methods typically apply global library-size correction and can remove biological spatial-domain signals when library size is spatially confounded with tissue structure (`paper.md:31-36`). SpaNorm is proposed as a spatially aware normalization method that models library-size effects and underlying biology together, separates them, and outputs adjusted data intended to remove library-size effects without removing biological information (`paper.md:25-27`, `paper.md:37-39`).

### Method in one paragraph

SpaNorm fits a gene-wise negative-binomial GLM to counts $z_{gc}$ using spatial coordinates and library size. The mean model decomposes $\log \mu_{c,g}$ into a gene intercept $\zeta_g$, a smooth biology term $f_g(x_c,y_c;\beta_g)$, and a spatially varying library-size term $\{\alpha+h_g(x_c,y_c;\gamma_g)\}\log LS_c$ (`paper.md:116-120`). It then generates percentile-invariant adjusted counts (PAC) by mapping observed counts through the full fitted NB distribution and back through a biology-only NB distribution without the library-size component (`paper.md:122-124`). In the verified R package, `SpaNorm()` constructs spline bases, fits the NB model with dispersion estimation and IRLS-like updates, and writes default logPAC output to `logcounts` or Seurat `data` (`R/mainSpaNorm.R:41-167`, `R/fitSpaNormNB.R:4-329`).

### Why existing methods are insufficient

The paper argues that normalization methods developed for scRNA-seq often ignore spatial information and may remove spatial-domain signals together with library-size effects (`paper.md:31-36`). In the reported comparisons, methods include no normalization, scran, sctransform, RUV-III-NB, Giotto, and SpaNorm (`paper.md:145-157`). The main novelty is not another global size factor, but a local, gene- and location-specific separation of biology-like smooth spatial variation from library-size-related smooth variation.

### Evaluation and main findings

The study evaluates 27 samples from 6 datasets across 4 platforms: Visium, Xenium, STOmics, and CosMx (`paper.md:25-27`, `paper.md:126-131`). Evaluation includes region/grid-specific library-size-effect tests, spatial-domain clustering with ARI, SVG detection/ranking, and robustness to segmentation/volume normalization (`paper.md:158-226`).

Key results:

- Region-specific library-size effects are common: Fig. 2A shows proportions spanning roughly 25% to almost 100% across datasets, matching the paper text (`paper.md:44-52`).
- For spatial-domain clustering, SpaNorm is often competitive or best, especially with spatially aware clustering methods; the paper states SpaNorm had the best maximum ARI for 9 of 25 samples, followed by standard LS normalization for 7, mostly Visium (`paper.md:53-64`).
- For SVG analysis, SpaNorm improves simulated true-SVG recovery and real marker-gene signals, including hippocampal CA markers in Fig. 3 (`paper.md:65-82`).
- In the MOBP DLPFC example, Fig. 5 visually shows low library size in white matter and stronger SpaNorm/biology-only MOBP signal in that region than with other normalizations (`paper.md:83-91`).

### Code and reproducibility

Code source analyzed here is the Bioconductor package snapshot at `[local path omitted]`, commit `49138bf4e18584d04a04ad40586c2f5d16120119`, URL `https://git.bioconductor.org/packages/SpaNorm`. The paper states SpaNorm is available as a Bioconductor package and that analysis code is deposited in Zenodo (`paper.md:260-267`).

**Code-paper match**: high for the core SpaNorm method implementation. The package directly implements the public API, NB model, spline basis design, regularization, IRLS-like fitting, PAC/logPAC adjustment, model storage, and example usage (`doc_code.md`). Important implementation details not explicit in the main paper include base-2 logPAC, probability clipping to `[0.001,0.999]`, dispersion winsorization, default cell/spot subsampling, and `scale.factor` in PAC generation (`R/fitSpaNormNB.R:307-329`, `R/mainSpaNorm.R:237-254`).

**Reproducibility limitations**:

- The acquired package snapshot does not contain full benchmark scripts for all 27 samples and all figures; searched `R/`, `tests/`, `vignettes/`, and `README.md` under `code source`.
- Additional file 2, which the paper cites for detailed estimation, was acquired only as a PDF/no `SUPP_MD`; detailed algorithm claims here rely on paper main text plus direct R source.
- CodeGraph existed locally but did not index R symbols; direct source reads were used instead.

### Practical takeaway

SpaNorm is best understood as a spatial NB-GLM normalization framework: fit smooth spatial biology and smooth local library-size effects jointly, then remove only the library-size part when generating adjusted counts. It is particularly motivated for spatial technologies where library size is region-specific and where downstream tasks depend on retaining spatial-domain or SVG signals.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
