---
layout: default
permalink: /paper-atlas/spcorr-d5e041e0/
title: "spCorr"
nav: false
wide: true
description: "空间转录组中，两个基因的表达关系可能随组织位置改变：在一个区域同向、另一个区域无关甚至反向。传统 SVG 方法只看单个基因的边缘表达，难以直接回答这个问题。已有的 scHOT（Genome Biology, 2020）、SpatialCorr（Nature Methods, 2022）和 SpatialDM（Nature Communications, 2023）可估计局部相关性，但论文指出它们通常不把相关性写成坐标的显式函数，协变量调…"
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
      <span>Spatially Variable Genes</span>
      <span>Genome Research · 2026</span>
    </div>
    <h1>spCorr</h1>
    <p>Flexible and scalable inference of spatially varying correlation in spatial transcriptomics with spCorr</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/chexjiang/spCorr" target="_blank" rel="noopener noreferrer" aria-label="Open code for spCorr">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spCorr：学习版方法解读

### 它解决什么问题？

空间转录组中，两个基因的表达关系可能随组织位置改变：在一个区域同向、另一个区域无关甚至反向。传统 SVG 方法只看单个基因的边缘表达，难以直接回答这个问题。已有的 scHOT（*Genome Biology*, 2020）、SpatialCorr（*Nature Methods*, 2022）和 SpatialDM（*Nature Communications*, 2023）可估计局部相关性，但论文指出它们通常不把相关性写成坐标的显式函数，协变量调整和计算检验也受限（`paper.md:28-31`）。

spCorr 的目标是：对指定基因对 $(j,k)$，在每个 spot $i$ 输出局部相关性 $\rho_{i,jk}$，并检验它是否随连续空间变化（SVC）或在离散区域间不同（DC）。输入是表达矩阵 $\mathbf Y$、空间坐标 $\mathbf S$ 和可选 spot 协变量 $\mathbf X$（如文库大小、区域标签）（`paper.md:148-154`）。

### 核心想法：先处理边缘分布，再建模相关性

计数数据的多元联合分布难以直接建模。spCorr 因而采用 Gaussian copula：每个基因先按协变量建模自己的分布，再把两个基因转换到共同的标准正态尺度；它们的依赖关系由空间相关参数描述（`paper.md:157-163`）。它只逐对分析用户关心的基因对，不估计完整的大相关矩阵（`paper.md:43-49`）。

```text
Y（基因×spot 计数） + X（协变量） + t(S)（空间预测变量）
       │
       ├─ 每个基因：拟合条件边缘分布 F_j(. | x_i)
       ├─ 计数 → 随机化 CDF → 标准正态值 z_ij
       ├─ 每个基因对：p_i,jk = z_ij × z_ik
       ├─ Quasi-GAM：atanh(rho_i,jk) = beta_0,jk + h_jk(t(s_i))
       └─ 输出局部 rho、全局 p 值、BH-FDR 与可选区间
```

### 四个计算步骤

#### 1. 边缘分布建模

对每个基因 $j$，用 GLM/GAM 建模 $Y_{ij}\mid\mathbf{x}_i$。这一步把文库大小、区域标签等会同时影响表达的因素放入边缘模型，而不是错误地当作基因间依赖（`paper.md:172-175`）。代码用 `formula1` 构造 `y ~ formula1`，支持 Poisson、NB 和 ZINB；ZINB 不可用时会退回 NB（`spCorr/R/fit_marginals.R:96-205`）。

#### 2. 高斯变换

计数是离散的。代码计算观测计数和前一个计数的 CDF，用随机数在两者之间抽取一个连续概率 $u_{ij}$，再取 $z_{ij}=\Phi^{-1}(u_{ij})$；最后裁剪极端概率，避免 `qnorm(0)` 或 `qnorm(1)`（`paper.md:178-181`; `fit_marginals.R:257-298`）。这不是简单的 log-normalization，而是为 copula 相关性构造近似标准正态变量。

#### 3. 乘积把双变量问题变成单变量问题

对基因对 $(j,k)$，构造

$$p_{i,jk}=z_{ij}z_{ik}.$$

在 Gaussian copula 下，该乘积的条件均值对应局部相关性，方差也有简单的均值关系，因此可拟合单变量 quasi-likelihood 模型（`paper.md:184-196`）。代码的实际操作就是 `z <- g1 * g2`（`spCorr/R/check_products.R:96-104`）。

#### 4. 用空间 Quasi-GAM 得到局部相关性

论文使用

$$\operatorname{atanh}(\rho_{i,jk})=\beta_{0,jk}+h_{jk}(\mathbf t(\mathbf s_i)).$$

二维坐标可用薄板样条，一维形态曲线可用三次样条，离散区域可用分类效应（`paper.md:196-205`）。代码把用户的 `formula2` 组成 `z ~ formula2`，交给 `mgcv::gam`（`spCorr/R/fit_products.R:118-140`）；自定义族以 `atanh` 为 link、`tanh` 为 inverse link，并把结果限制在接近 $[-1,1]$ 的范围（`quasiproductr.R:10-37`）。

### 如何做检验和下游分析？

连续空间时，SVC 问的是平滑项是否随空间改变；离散区域时，DC 问的是不同区域系数是否不同（`paper.md:211-232`）。代码可用 LRT（与 `z ~ 1` 比较）或平滑项的 Wald 式 p 值，并对所有基因对做 BH 校正（`fit_products.R:143-166`; `spCorr.R:154-161`）。输出的 `res_local` 是每个基因对在各 spot 的拟合值；可用于 SVC/DC 筛选、基于局部相关矩阵的聚类和网络分析（`paper.md:244-265`）。

### 论文结果该怎样理解？

Fig. 2 可见零假设校准、FDR、ROC、局部估计精度和时间比较；论文据此报告 spCorr 在其模拟设置下有较好的 FDR 控制和功效（`paper.md:52-66`）。Fig. 3–5 把方法用于 OSCC、鼠皮层和海马，展示相关性图、相关性聚类、空间/形态曲线和区域比较。它们说明方法可发现与组织结构一致的关联模式，但相关性本身不能证明调控或因果关系。

### 代码核对后的边界

- 论文提出可用 spot 特异的不确定性权重（`paper.md:193-196`）；在本快照检查的 `spCorr()` 和 `fit_product()` 调用中没有找到传入 `weights` 的路径，故标为 **Not found in this snapshot**。
- 论文讨论 DC；代码允许用分类 `formula2`，但 `spCorr/R/` 中没有找到专门的 DC 对比辅助函数，具体对比流程需使用者核实。
- `spCorr()` 虽有 `family2` 参数，却固定把 `quasiproductr()` 传入拟合器（`spCorr/R/spCorr.R:137-152`）。要使用其它 product family，不能假定该顶层参数已经生效。
- 本地没有单独转换的补充材料；`paper.md` 也遗漏部分 display MathML。上面的公式仅在正文文字和保留 HTML 可核对时写出。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## spCorr: spatially varying gene-pair correlation

### What problem does it solve?

Spatial transcriptomics workflows commonly identify spatially variable genes, but a gene pair can change its coordination without either marginal expression pattern revealing that change. Existing SVC approaches such as scHOT (Genome Biology, 2020), SpatialCorr (Nature Methods, 2022), and SpatialDM (Nature Communications, 2023) rely on local nonparametric estimates and permutation/analytic tests; the paper argues these can be hard to express as coordinate functions, awkward for covariate adjustment, and expensive or restrictive (`paper.md:28-31`).

### Contribution

spCorr is a regression framework for selected gene pairs. It fits conditional gene-level count models, Gaussianizes residual variation, models each transformed cross-product with a spatial quasi-GAM, and returns spot-level correlation estimates plus global SVC/DC-style significance tests (`paper.md:37-49,172-241`). This makes the local correlation an explicit function of coordinates, a curve, or domain labels rather than only a kernel-weighted local summary.

### Evidence and evaluation

- In semi-synthetic DLPFC simulations (200 pairs, 30 repeats), the authors compare spCorr with scHOT, SpatialDM, and SpatialCorr using null-p-value calibration, FDR, power, AUROC, cosine similarity of local estimates, and runtime (`paper.md:52-66`). Figure 2 visibly contains all of these comparison panels.
- The paper reports that spCorr controlled FDR at the target 5% level and had the highest power/AUROC in its stated comparisons; this is an author-reported simulation conclusion, not an independent rerun (`paper.md:58-61`).
- Applications cover OSCC, mouse cortex, and mouse hippocampus, with correlation-based clustering, coordinate/curve patterns, and region-specific correlation/network analyses (`paper.md:67-120`; Figs. 3–5 visually inspected).

### Reproducibility assessment: 3/5

**What is available.** The workspace includes an R-package snapshot at commit `b3495faac6e43e0cca3ee6b6041b1d796dd6309e`. The core pipeline is source-backed: conditional marginals and randomized Gaussianization (`fit_marginals.R:88-298`), pair products (`check_products.R:87-106`), quasi-GAMs/tests/intervals (`fit_products.R:107-220`), and BH correction (`spCorr.R:154-161`).

**What remains limited.** This analysis did not execute an end-to-end example or reproduce simulations. The publisher DC1 supplement was not acquired locally. The Markdown conversion drops display MathML, though the preserved article HTML retains it. In the inspected snapshot, paper-described observation-specific weighting and a dedicated DC helper are **Not found**, and `spCorr()` ignores its user-supplied `family2` argument by passing `quasiproductr()` directly to the product fitter (`spCorr.R:137-152`). These are implementation boundaries, not evidence against the paper's statistical proposal.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
