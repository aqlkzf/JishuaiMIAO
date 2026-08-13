---
layout: default
permalink: /paper-atlas/csplotch-64fc36b3/
title: "cSplotch"
nav: false
wide: true
description: "结肠同时沿三条轴变化：近端到远端的解剖轴、隐窝底到顶端的组织轴，以及出生到衰老的时间轴。空间转录组保留位置，但每个 spot 混合多个细胞；单核 RNA 测序能分辨细胞类型，却丢失组织位置。本文建立覆盖约 1,500 个小鼠结肠空间切片和约 40 万个单核转录组的图谱，并提出 cSplotch，把 H&E 形态、snRNA-seq 参考、spot 细胞组成和多层实验条件联合起来，估计“某个基因在某种细胞、某个组织区室和某个年龄/区域条件…"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>cSplotch</h1>
    <p>Tissue and cellular spatiotemporal dynamics in colon aging</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02830-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for cSplotch">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/adaly/cSplotch" target="_blank" rel="noopener noreferrer" aria-label="Open code for cSplotch">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cSplotch：把结肠的细胞组成、空间位置和年龄放进同一个统计模型

### 论文想解决什么问题

结肠同时沿三条轴变化：近端到远端的解剖轴、隐窝底到顶端的组织轴，以及出生到衰老的时间轴。空间转录组保留位置，但每个 spot 混合多个细胞；单核 RNA 测序能分辨细胞类型，却丢失组织位置。本文建立覆盖约 1,500 个小鼠结肠空间切片和约 40 万个单核转录组的图谱，并提出 cSplotch，把 H&E 形态、snRNA-seq 参考、spot 细胞组成和多层实验条件联合起来，估计“某个基因在某种细胞、某个组织区室和某个年龄/区域条件下的表达率”。

方法由两个相连但不同的阶段组成：先用形态约束的 SPOTlight 推断每个 spot 的细胞组成；再用分层贝叶斯模型估计细胞类型特异的表达率及其空间、区域和年龄差异。

### 1. MROI 是跨切片的共同空间语言

作者根据 H&E 将 spot 标为 morphological region of interest（MROI），例如 crypt base、crypt apex、cross-mucosa 和肌层/肠神经相关区域。MROI 不是像素级配准坐标，而是能在大量不同切片间复用的组织学类别。它让模型可以比较“不同年龄的同一种区室”，同时避免要求 1,500 张切片逐点对齐。

这一设计也给出首要假设：同名 MROI 在不同年龄和结肠区域必须具有足够一致的生物学含义。若人工注释漂移，模型会把标注差异误认为表达差异。

### 2. 用 H&E 约束 spot 细胞组成

SPOTlight 先对 snRNA-seq 的 genes×cells 矩阵做带生物学初始化的非负矩阵分解：

$$V\approx WH,$$

其中 $W$ 是基因—topic，$H$ 是 topic—细胞；topic 数与参考细胞类型数一致，marker 基因和已知细胞标签用于初始化。空间矩阵 $V'$ 再投影到固定的 $W$，得到 spot 的 topic 表示 $H'$；由参考细胞聚合出的 topic—细胞类型矩阵 $Q$ 将其转换成细胞比例 $P$：

$$V'\approx WH',\qquad H'\approx QP.$$

只拟合表达可以得到数学上良好、组织学上不合理的混合比例。作者因此从 H&E patch 经 ilastik 分割和对象分类得到 broad morphology superclass 比例 $L$，并用映射矩阵 $S$ 把细粒度细胞类型合并到这些 superclass。最终优化同时要求

$$H'\approx QP,\qquad L\approx SP,$$

代码以表达重建 MSE 加 $alpha$ 倍形态 MSE，并用 Adam 更新非负比例（`deconv/spotlight.py:251-340,441-493`）。$alpha$ 太小会忽略形态，太大则会把分割错误强加给表达；形态约束是信息来源，也是一条误差传播路径。

代码还会平衡 snRNA-seq 各细胞类型的数量、按 $10^4$ 深度归一化并缩放（`deconv/spotlight.py:59-82`）；空间 spot 至少保留 100 counts（`:174-186`）。这些步骤避免高丰度参考细胞或测序深度主导分解。

### 3. cSplotch 的表达率分解

对基因 $i$、切片 $j$、spot $k$，模型将观测计数 $y_{ijk}$ 的均值写成 size factor $s_{jk}$ 与潜在表达率 $\lambda_{ijk}$ 的乘积。代码支持 Poisson、negative binomial、ZIP 和 ZINB，用过度离散项与零膨胀项区分技术噪声和真实表达变化。

核心分解是：

$$
\log\lambda_{ijk}=B_{ijk}+\psi_{ijk}+\epsilon_{ijk}.
$$

$B$ 是由 MROI、细胞比例和年龄/区域/性别等条件决定的 characteristic expression；$\psi$ 是局部空间相关；$\epsilon$ 是 spot 级残差。对于混合 spot，$B$ 是各细胞类型 beta 按比例加权的结果。于是 beta 可以被读成：在给定条件和 MROI 下，某细胞类型对该基因表达率的贡献，而不是直接观测到的单细胞表达。

Stan 代码完整实现计数分支、三层 beta 层级、组成加权、CAR 和残差（`stan/comp_splotch_stan_model.stan:30-32,85-223,248-280`）。Pyro 版本也清楚展示 `log_lambda = beta + psi + epsilon` 以及 zero-inflated Poisson likelihood（`pyro/comp_splotch_pyro_model.py:113-189`）。

### 4. 分层 beta 如何跨大量切片借力

beta 最多有三层嵌套，例如年龄、结肠区域和性别。下层参数以对应上层参数为均值：

$$
\beta^{(2)}\sim N(\beta^{(1)},\sigma_2),\qquad
\beta^{(3)}\sim N(\beta^{(2)},\sigma_3).
$$

这叫 partial pooling：数据少的条件会向上层均值收缩，数据充分的条件仍可偏离。它使跨上千切片的比较比逐切片独立差异分析更稳定，但层级顺序本身是科学建模选择；“先年龄后区域”和“先区域后年龄”不完全等价。

局部空间项使用 conditional autoregressive（CAR）先验。相邻 spot 的 $\psi$ 倾向接近，相关强度由 $\alpha\in(0,1)$ 控制，精度由 $\tau$ 控制。发布实现直接根据稀疏邻接矩阵计算 CAR log density（`pyro/comp_splotch_pyro_model.py:20-71`）。CAR 用于吸收局部连续结构，不应理解为把所有差异简单平滑掉；如果真实边界很锐利，过强空间先验仍可能造成过度平滑。

### 5. 从 posterior 到差异表达

每个基因分别拟合，得到 beta posterior。两个条件的差异为 $\Delta=\beta_A-\beta_B$；论文用 Savage–Dickey density ratio 比较零点处的先验密度与后验密度，构造 Bayes factor。BF 越大，表示数据让“差异为零”越不可信。代码用 KDE 估计 posterior difference 在零点的密度（`splotch/utils.py:259-268`）。

BF 支持统计差异，不代表效应大、可重复于所有个体或具有因果性。解释时还应同时查看 posterior 均值、不确定区间、spot/动物覆盖和是否有正交实验验证。

论文的 HMC 报告每链 250 warmup 和 250 samples；CLI 能运行和汇总多链，但 250 不是固定默认值，需要调用者传入 `-n 250`（`bin/splotch:128-149`）。因此核心推断匹配，精确采样合同属于 Partial。

### 6. 从细胞类型表达进入 multicellular program

作者把多个细胞类型的 posterior mean beta 矩阵送入 DIALOGUE/MultiCCA，寻找在年龄和区域条件间协同变化的稀疏基因集合，即 multicellular programs（MCP）。它回答“哪些细胞类型的哪些基因活动一起升降”，适合发现上皮、免疫、基质共同参与的衰老程序。

本地 R 代码运行 permutation 和 MultiCCA，并输出权重、表达和 MCP score（`mcp/dialogue_betas.R:33-61`, `mcp/DIALOGUE.R:199-228`）。MCP 是跨条件相关结构，不是配体–受体方向，也不能单独证明细胞间信号传递。

### 7. 主图如何构成证据链

- Fig. 1：展示出生到 2 年、近中远端结肠的空间与单核图谱，定义数据规模和 MROI 坐标系。
- Fig. 2：验证形态约束的 deconvolution 与 cSplotch 表达率；人工细胞计数、表达重建和 Epcam、Tff3、Acta2/SMA、Cd48 免疫荧光提供不同层面的检查。
- Fig. 3：解析成年结肠的近端—远端组成差异、细胞类型特异表达以及隐窝轴梯度。
- Fig. 4：把年龄加入模型，展示细胞比例、beta 差异与 DIALOGUE MCP，连接上皮更新、免疫和基质变化。

论文还用模拟数据、外部 snRNA-seq、SpatialDE2/SPARK-X 比较、KL divergence 下采样功效分析和 Visium 示例验证模型。验证栈较完整，但只有少数 marker 获得 IF 直接验证，大量 beta 和 MCP 仍是模型生成的假设。

### 8. 主要生物学结论和边界

图谱显示成年结肠沿近端—远端存在稳定的细胞组成和功能差异，隐窝底到顶端呈现再生与分化梯度；衰老伴随 goblet cell 减少、progenitor/colonocyte 重塑以及上皮—免疫—基质协同程序改变。

最强的方法学贡献不是某一个衰老 marker，而是能在大量组织切片上同时控制解剖区室、细胞混合、层级条件和局部空间相关。边界同样明确：结果依赖 MROI、H&E 分类、snRNA 参考和 deconvolution；beta 是混合数据下的后验估计；MCP 是相关而非因果；仓库虽覆盖核心模型和工具，却没有一个从全部原始数据到所有论文图的单命令工作流，部分 notebook 依赖硬编码路径和预计算文件。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## cSplotch Summary

### Paper

**Title:** Tissue and cellular spatiotemporal dynamics in colon aging
**Journal:** Nature Biotechnology
**Year:** 2025
**DOI:** `10.1038/s41587-025-02830-6`
**Code:** `https://github.com/adaly/cSplotch`

### Motivation

The colon changes across multiple biological scales: proximal-to-distal anatomy, crypt base-to-apex histology and age. Existing single-cell atlases capture cell types but lose spatial context. Existing spatial transcriptomics methods often analyze one tissue section at a time, smooth local expression at the risk of erasing real niche-specific signals, or deconvolve spots without enough histological constraint.

The paper's goal is to build a large mouse colon aging atlas and provide a computational framework that can compare cell-type-specific expression across many tissue sections, anatomical regions and ages. The biological endpoint is not just "which genes are expressed"; it is where, in which cell type, under which age/region/sex condition, and whether the inferred expression difference is statistically supported.

### Main Contribution

The study combines approximately 1,500 mouse colon spatial transcriptomics sections and approximately 400,000 snRNA-seq profiles across three colon regions and 11 time points. It introduces **cSplotch**, a workflow with two linked computational stages:

1. **Morphology-informed deconvolution:** SPOTlight/NMF deconvolution is constrained by H&E-derived broad cell morphology proportions, so inferred fine cell-type mixtures are more anatomically plausible.
2. **Hierarchical Bayesian expression modeling:** a Stan model estimates posterior distributions over cell-type-specific expression rates $\beta$ across MROI, age, colon region and sex, with optional local spatial autocorrelation and zero-inflated/NB count likelihoods.

The final beta posteriors support spatial and temporal comparisons, including proximal-distal gradients, crypt-axis gradients and aging-associated multicellular programs.

### Method Overview

cSplotch first assigns every spatial spot to a morphological region of interest and estimates broad morphology class proportions from H&E images. It then uses snRNA-seq reference profiles to deconvolve each ST spot into cell-type proportions, adding a morphology loss so pooled cell types match the H&E-derived superclass mixture.

The Bayesian model treats observed counts $y_{i,j,k}$ as depth-scaled observations of expression rate $\lambda_{i,j,k}$. On the log scale, $\lambda$ is decomposed into characteristic expression $B$, local spatial autocorrelation $\psi$ and residual spot variation $\epsilon$. $B$ is computed from MROI, cell composition and hierarchical beta coefficients. Differential expression is evaluated by comparing beta posteriors with a Savage-Dickey Bayes factor.

For aging programs, posterior mean beta matrices are passed to DIALOGUE/MultiCCA to find multicellular programs whose gene activities covary across cell types and conditions.

### Key Findings

- The atlas spans juvenile, adult and aged mouse colon across proximal, middle and distal regions.
- Morphology-aware deconvolution improves anatomical plausibility of inferred cell composition while preserving expression reconstruction.
- cSplotch recovers expected marker localization and cell-type expression patterns, including IF-supported markers such as Epcam, Tff3, Acta2/Sma and Cd48.
- The adult colon shows cell-type-specific proximal-distal expression differences and crypt-axis gradients tied to digestive, structural and regenerative functions.
- Aging is associated with goblet-cell decline, progenitor/colonocyte remodeling, inflammatory states and MCPs involving epithelial, immune and stromal cell types.
- MCPs nominate coordinated aging programs but should be interpreted as correlation over inferred expression rates, not causal signaling.

### Evaluation

The paper validates cSplotch through several complementary checks:

- manual/pathologist comparison of deconvolved cell fractions in selected spots;
- H&E semantic segmentation train/test evaluation;
- IF validation of selected spatial marker genes;
- correlation between cSplotch beta profiles and external snRNA-seq profiles;
- synthetic ST simulations with known cell compositions;
- comparison to SpatialDE2 and SPARK-X on known marker genes;
- subsampling/power analysis using KL divergence from full-data beta posteriors;
- Visium demonstration on a 10x dataset.

This is a strong validation stack for atlas-scale observational modeling. It does not prove causal mechanisms of aging, and only selected markers/genes receive orthogonal experimental validation.

### Code Match And Reproducibility

**Overall code fidelity:** high for the core cSplotch method, medium for full paper reproduction.

The public repository contains direct implementations of the main algorithmic claims:

- compositional Stan model with Poisson/ZIP/NB/ZINB branches;
- three-level beta hierarchy;
- optional sparse CAR spatial prior;
- morphology-aware SPOTlight deconvolution using Adam, learning rate 0.01 and 100,000 iterations;
- segmentation and composition-quantification utilities;
- input-generation wrappers and posterior-summary utilities;
- DIALOGUE/MCP scripts;
- figure notebooks and selected derived data files.

Important caveats:

- The paper's HMC setting of 250 warmup and 250 samples is not hardcoded; it depends on wrapper invocation.
- `splotch-vinit` is implemented as a CmdStan Pathfinder initialization workflow.
- Figure notebooks often contain hardcoded local paths and assume precomputed/downloaded AnnData, beta or MCP files.
- I did not find a single public end-to-end workflow that downloads all raw data and regenerates every figure from scratch.

**Reproducibility rating:** **3.5/5 overall**.

Justification: the core cSplotch method implementation is source-backed and fairly complete, including Stan models, deconvolution, segmentation utilities, input generation and MCP scripts. Complete paper reproduction is weaker because figure notebooks assume local/precomputed data paths and I did not find a single raw-data-to-all-figures public workflow.

### Practical Takeaway

cSplotch is best understood as an atlas-scale statistical framework for turning multicellular spatial spots into cell-type-, niche- and condition-specific posterior expression estimates. Its strongest contribution is the combination of histology-constrained deconvolution and hierarchical Bayesian sharing across many tissue sections. Its main limitation is interpretability: beta differences and MCPs are powerful hypothesis generators, but they remain observational and depend on MROI annotation, cell-composition accuracy and snRNA-seq reference quality.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
