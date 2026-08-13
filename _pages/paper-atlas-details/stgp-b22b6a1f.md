---
layout: default
permalink: /paper-atlas/stgp-b22b6a1f/
title: "stGP"
nav: false
wide: true
description: "空间转录组如果在多个年龄、发育阶段或损伤时间点采样，同一种细胞的表达变化往往同时包含两件事：不同样本之间随时间改变的共同趋势，以及每张组织切片内部的解剖位置或局部微环境差异。传统 PCA、NMF 可以找低维因子，却不能告诉我们一个因子主要是时间变化、空间结构，还是二者叠加；"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>stGP</h1>
    <p>Characterizing dynamic tissue architectures by identifying cell-type-specific spatiotemporal gene programs with stGP</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.07.03.736035" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for stGP">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/YangLabHKUST/stGP" target="_blank" rel="noopener noreferrer" aria-label="Open code for stGP">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## stGP：把时间变化与切片内空间结构分开的基因程序模型

### 它要回答什么问题？

空间转录组如果在多个年龄、发育阶段或损伤时间点采样，同一种细胞的表达变化往往同时包含两件事：不同样本之间随时间改变的共同趋势，以及每张组织切片内部的解剖位置或局部微环境差异。传统 PCA、NMF 可以找低维因子，却不能告诉我们一个因子主要是时间变化、空间结构，还是二者叠加；SpatialPCA、Popari、STAMP、MEFISTO 分别覆盖空间、多样本或协变量平滑的一部分，但论文认为它们没有同时给出“细胞类型特异、可解释基因权重、时间—空间可分活动”的统一模型（`paper.md:18-24`）。

stGP（spatiotemporal Gene Programs）针对一个已注释的目标细胞类型单独建模。输入是每个样本的细胞×基因表达矩阵、该样本的时间/年龄标签、以及细胞在该切片中的二维坐标；输出是基因程序、随时间的轨迹、每张切片内的空间活动图，以及二者的方差贡献（`paper.md:33-50`；Fig. 1）。

### 核心直觉

把一个“基因程序”理解为一组始终共享的高权重基因；但是这个程序在不同年龄和不同组织位置可以有不同活性。stGP 不要求把所有切片配准到同一坐标系：它只在每一张切片内部度量空间邻近性，再用样本的时间标签连接切片之间的共同变化（`paper.md:44`）。

```text
同一细胞类型的多张切片
  表达矩阵 + 年龄/阶段 + 切片内坐标
                 │
                 ▼
      共享的基因程序权重 W（每个程序像一个加权基因集）
                 │
                 ▼
    每个细胞的程序活性 h = 时间共同趋势 α + 空间局部偏离 b
                 │
                 ├── α：不同样本之间随年龄/阶段平滑变化
                 └── b：同一张切片中按空间距离平滑变化
```

### 数学模型：每个符号是什么意思？

对第 $t$ 个样本，stGP 使用

$$
Y^t = H^tW + E^t.
$$

- $Y^t\in\mathbb{R}^{n_t\times G}$：该样本内 $n_t$ 个目标细胞、$G$ 个基因的（中心化）表达矩阵；
- $H^t\in\mathbb{R}^{n_t\times p}$：每个细胞在 $p$ 个程序上的活性；
- $W\in\mathbb{R}^{p\times G}$：每个程序的基因权重；
- $E^t$：未被程序解释的残差。

第 $j$ 个程序的基因权重满足

$$
w_{jg}\geq0,\qquad \sum_g w_{jg}=1.
$$

所以 $w_j$ 是非负、和为 1 的基因权重向量；它比可正可负的 PCA loading 更容易解释成“这个程序由哪些基因构成”（Fig. 1a；`paper.md:36-39`）。

对样本 $t$ 中细胞 $i$ 的程序 $j$，活性拆为

$$
h^t_{ij}=\alpha_{tj}+b^t_{ij}.
$$

$\alpha_{tj}$ 是该样本内所有目标细胞共享的时间部分；$b^t_{ij}$ 是细胞在本切片坐标上的空间部分。图 1 给出两个高斯过程先验：

$$
\alpha_j\sim\mathcal N(0,\sigma_j^2K_{\rm age}),\qquad
B_j^t\sim\mathcal N(0,\tau_j^2K_{\rm spa}^t).
$$

其中 $K_{\rm age}$ 让相近年龄/阶段的样本有相近 $\alpha$，$K_{\rm spa}^t$ 让同一切片内坐标相近的细胞有相近 $b$。$\sigma_j^2$ 与 $\tau_j^2$ 分别量化模型中时间和空间部分的变化量（Fig. 1b）。这是一种依赖核函数与采样设计的统计分解，**不是**“时间或空间导致了表达变化”的因果证明。

### 实际如何拟合？

1. 对一个细胞类型整理每张切片的表达、时间标签和坐标；表达需要中心化，坐标/核带宽采用数据集特异的预处理。
2. 构造时间核 $K_{\rm age}$ 与每张切片自己的空间核 $K_{\rm spa}^t$。代码提供 RBF 时间核以及 AR(1) 时间核；空间核是切片内 RBF 核（`stGP_code/stgp/kernels.py:178-358`）。
3. 先在残差上拟合一个 rank-1 程序：更新细胞活性，再把活性分成 $\alpha$ 与 $b$；更新基因权重时投影到 simplex；随后更新噪声、时间和空间方差。
4. 继续从残差中加入程序，并反复 backfitting，使程序不会只依赖最初的提取顺序；可自动停止并删除能量很低的程序（`paper.md:47`, `183-192`）。

代码层面，`fit_rank1` 对应核心单程序循环（`stGP_code/stgp/estimation.py:1031-1198`），`fit_pfactor` 对应多程序 backfitting（`1364-1605`），`fit_pfactor_auto` 负责自动加程序、回拟合与剪枝（`1635-1815`）。给定权重后，代码用 $z=Yw/\lVert w\rVert^2$ 做高斯后验计算，并以 Woodbury 形式避免直接求大协方差矩阵的逆（`estimation.py:53-71`, `137-238`；`paper.md:195-201`）。

### 怎么读输出？

- 看 $W$ 的高权重基因：它定义程序的分子身份。
- 看 $\alpha$ 及其区间：它描述该程序在样本时间轴上的拟合趋势与后验不确定性。
- 看 $b^t$ 的空间图：它描述程序在每张切片内部的局部富集/缺失。
- 看 $\sigma_j^2$ 与 $\tau_j^2$：它们比较该程序在此模型下更偏时间还是更偏空间。

例如，论文在模拟中比较 stGP、PCA、NMF、SpatialPCA、Popari、STAMP 和 MEFISTO；Fig. 2 显示 stGP 的程序恢复、基因检测和细胞 embedding 指标在该模拟设定中居前（`paper.md:53-70`）。在人 DLPFC MERFISH 中，作者以 ARI、NMI 和层标记基因相关性评价层状结构恢复（`paper.md:73-87`; Fig. 3）。这些结果支持模型在作者数据与评估设定中的表现，不自动推广到未见组织或不同采样设计。

### 代码可复现性与边界

论文的 Code availability 指向公开的 YangLabHKUST/stGP 仓库（`paper.md:270-273`）；核心估计器和核函数与论文的主要算法对应关系为 **Exact**，但每个真实数据 notebook 的逐单元调用没有逐一核对或运行，因此预处理与图复现属于 **Partial**。在已检查的范围内，**Not found**：一个带齐所有输入数据、可一键重现全部六张主图的端到端命令。

如果要继续学习：先看 `summary.md` 建立全局图景，再看 `doc_method.md` 的代码变量与公式说明，最后用 `doc_code.md` 区分已验证对应关系与尚未验证的 notebook/复现部分。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## stGP — compact analysis summary

### Problem and contribution

Spatial transcriptomic studies sampled across ages, stages, or injury time points mix between-sample temporal change with within-section anatomy. PCA/NMF do not separate those sources; SpatialPCA, Popari, STAMP, and MEFISTO each address only part of the combination of spatial structure, time, multi-sample design, and interpretable cell-type-specific programs (`paper.md:18-24`).

stGP is a statistical framework that fits one annotated cell type at a time. It factorizes centered expression into shared nonnegative, sum-one gene-program weights and program activities, then splits each activity into a sample-level temporal GP trajectory and a within-section spatial GP field (`paper.md:33-50`; Fig. 1). The outputs are gene weights, temporal trajectories with uncertainty, section-specific spatial embeddings, and temporal/spatial variance components.

### How it works

For each target cell type, inputs are per-sample cell-by-gene matrices, sample ages/stages, and 2D coordinates. A rank-1 blockwise fit alternates activity, simplex loading, and variance updates; residual components are added and backfit, with an optional automatic program-count procedure (`paper.md:47`, `168-201`). The checked repository implements these central paths in `stGP_code/stgp/estimation.py:1031-1815`, with RBF/AR(1) temporal and section-local spatial kernels in `stGP_code/stgp/kernels.py:178-358`.

### Evaluation and main findings

- Simulations compare stGP with PCA, NMF, SpatialPCA, Popari, STAMP, and MEFISTO at four true programs. Across 50 replicates, the paper reports superior program similarity, top-$k$ gene detection, and embedding recovery, with separate temporal and spatial outputs (`paper.md:53-70`; Fig. 2).
- In 12 human DLPFC MERFISH sections from donors aged 15–87, stGP identifies four excitatory-neuron programs and reports better layer recovery than the listed baselines using ARI, NMI, and marker-expression correlation (`paper.md:73-87`; Fig. 3).
- Further case studies connect an oligodendrocyte program to a NicheScope-derived shared niche (Fig. 4), a late-life microglial program to local cellular context (Fig. 5), and matched injury/recovery programs across left and right kidneys (Fig. 6; `paper.md:90-152`). These are model-based and observational interpretations, not causal demonstrations.

### Reproducibility assessment: 3/5

**Strengths.** The paper's Code availability section points to the public YangLabHKUST/stGP repository (`paper.md:270-273`), which is present here at commit `120e5fec23c6d7651fcfff064d6b647cb9fb3194`. Core estimator, kernel, preprocessing, simulations, and figure/real-data notebooks are included. The core paper–code match is high at source level; see `doc_code.md`.

**Limits.** The analysis did not run notebooks or reproduce figures; per-figure preprocessing remains **Partial**. A single end-to-end command plus all input data for all six article figures was **Not found** in the inspected repository scope. The paper is a 2026 bioRxiv preprint, so claims should be read as author-reported pending peer review. Exact display-math transcription is limited by Markdown conversion; the source XML/supplementary PDF remain the typeset reference.

### Reading map

- `doc_method.md`: model, equations, inference, and interpretation limits.
- `doc_code.md`: Exact/Partial/Not found paper–code connections.
- `figure_analysis.md`: visual evidence and figure-specific boundaries.
- `Chinese method notes`: self-contained Chinese learning-oriented explanation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
