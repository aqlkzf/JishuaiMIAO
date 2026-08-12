---
layout: default
permalink: /paper-atlas/deleakage-b27e2305/
title: "DeLeakage"
nav: false
description: "空间转录组把转录本分配给分割出的细胞，但分到细胞 i 的信号并不一定都由 i 产生：相邻细胞的转录本可能扩散或在分割/分配时落入 i。这会让本应互斥的细胞类型 marker 同时出现，夸大不同细胞类型之间的相似性，并制造空间自相关假象。论文在 MERFISH、Xenium 与 Pixel-seq 中展示了这类现象。 已有的去卷积式去噪将一个细胞的观测表达看成多个细胞类型表达谱的混合（Fig. 3B）。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>DeLeakage</h1>
    <p>Correcting spatial transcriptomics data affected by a prevalent transcript leakage problem across platforms, species, and tissues</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.06.13.732076" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeLeakage：把空间邻居泄漏从细胞自身表达中分开

### 它要解决什么问题？

空间转录组把转录本分配给分割出的细胞，但分到细胞 $i$ 的信号并不一定都由 $i$ 产生：相邻细胞的转录本可能扩散或在分割/分配时落入 $i$。这会让本应互斥的细胞类型 marker 同时出现，夸大不同细胞类型之间的相似性，并制造空间自相关假象。论文在 MERFISH、Xenium 与 Pixel-seq 中展示了这类现象（`paper.md:12-21,33-61`；Fig. 1）。

已有的去卷积式去噪将一个细胞的观测表达看成多个细胞类型表达谱的混合（Fig. 3B）。这不完全适合这里的问题：作者认为待校正的是“邻居细胞带来的信号”，而不是目标细胞本身一定是混合身份。对照方法包括 SPLIT，以及 SpotClean（*Nature Communications*, 2022；论文参考文献 `paper.md:569`）。

### 核心想法

对每个基因 $g$、细胞 $i$，DeLeakage 将观测 $Y_{gi}$ 拆成两部分：

1. 细胞 $i$ 的真实表达：随细胞大小 $\delta_i$ 缩放，并由其未知类型 $Z_i$ 和该类型均值 $\mu_{gZ_i}$ 决定；
2. 邻居泄漏：对每个邻居 $j$，以其大小和类型均值作为信号源，再由基因特异系数 $\gamma_g$ 与随距离 $d_{ij}$ 衰减的权重（涉及 $e^{-\beta d_{ij}}$）调制。

Fig. 3A/C 直观画出了这个分解（`paper.md:70-72`）。HTML 转 Markdown 时丢失了若干显示公式的正文，因此上述是依据图和文字的结构性解释；要逐字复现概率分布与归一化常数，应查阅 article XML 或渲染后的预印本，而不要把这里当作精确公式抄本。

| 符号 | 作用 | 当前主代码中的对应物 |
|---|---|---|
| $Y_{gi}$ | 观测基因表达 | 输入计数矩阵，`src/Contamination.cpp:42-67` |
| $Z_i$ | 潜在细胞类型 | `_update_Z_MB`，`include/MCMC_v8.h:518-715` |
| $\mu_{gk}$ | 类型 $k$ 的基因均值 | `_update_mu`，`:147-202` |
| $\gamma_g$ | 基因特异泄漏/扩散强度 | `_update_gamma`，`:204-290` |
| $\beta$ | 距离衰减参数 | `_update_beta`，`:292-405` |
| $\pi_k$ | 类型比例 | `_update_pi`，`:720-747` |

### 从输入到输出

```text
表达矩阵 Y + 空间邻居/距离 + 细胞大小 + 初始标签/层文件
                         │
                         ▼
初始化 mu, gamma, beta, 方差, pi, Z
                         │
                         ▼
反复 MCMC：更新基因参数 → 更新距离参数 → 更新 Z → 更新 pi
                         │
                         ▼
后验样本与后验汇总 → 非负的去污染表达、类型和参数
```

论文说明用 Gibbs 或 Metropolis–Hastings 更新 $\mu,\gamma,\beta$、方差、$\pi$ 和 $Z$，并用后验汇总得到校正值，负值截断为零（`paper.md:291-312`）。主代码中，`run_contamination` 读取这些文件输入并执行对应的更新顺序（`src/Contamination.cpp:15-214,338-468`），随后写出 `mu`、`gamma`、`beta`、方差、`Z`、`pi` 等抽样结果（`:473-580`）。

一个关键技巧是 $Z_i$ 的并行更新。相邻细胞彼此依赖，不能任意并行；作者先把彼此不在 Markov blanket 内的细胞分层，同层可并行，最后的尾部逐个更新（`paper.md:314-325`）。代码中的 `MB_list`、`_update_Z_MB` 与 tail list 正对应这一 CPU 分层策略（`src/Contamination.cpp:395-414`；`include/MCMC_v8.h:518-715`）。

### 论文如何评估？

- **模拟数据**：Fig. 4 对比真实表达、泄漏后表达和校正结果，并与 SPLIT、SpotClean 比较；图中还给出残差、细胞类型间余弦相似度及 FDR 表。
- **真实空间数据**：Fig. 5 的小鼠脑 MERFISH 图显示，DeLeakage 后 `Slc17a7`、`Aqp4` 的非目标区域弥散信号下降；Fig. 6 展示四个数据集的 ARI 条形图，以及意外 marker 的 Moran's I 热图。
- **规模**：补充 Fig. 10 报告 CPU/GPU 版本在不同细胞数/基因数下的时间和内存，以及与 SPLIT 的比较（`paper.md:476-482,533-535`）。这些是作者报告的结果，当前工作区未重跑。

### 应如何理解边界？

该模型依赖 marker 基因和空间异质性等可识别性条件，且只可识别到标签置换（`paper.md:276-290`）；$K$ 也是调用者显式传入的参数，而非例程自动选择（`src/python_bindings.cpp:20-37`）。

当前主代码快照可直接验证 pybind 入口、OpenMP MCMC、Markov-blanket 更新和样本输出，但有三项不能补写成“已实现”：

- **Not found**：该主快照没有 CUDA/GPU 源文件；论文的 GPU 结果不能据此反推出具体实现。
- **Partial**：未在已核对的 `src/`、`include/`、`post/` 和绑定中找到最终去污染表达矩阵的计算/写出；只确认了后验样本输出。
- **Not verified**：示例脚本指向缺失的 `../dcuda/data/` 路径（`test/test_decontamination.py:22-58`），因此这里没有声称已完成端到端复现。

想深入追踪：方法细节见 `doc_method.md`，纸码对应见 `doc_code.md`，图像证据见 `figure_analysis.md`。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeLeakage — quick summary

### Problem and contribution

DeLeakage addresses transcript leakage in cell-resolved spatial transcriptomics: signal assigned to a cell may originate in nearby cells. The paper argues that this confounds marker specificity, cell-type separation, differential expression, and spatial analyses across MERFISH, Xenium, and Pixel-seq data (`paper.md:12-21,33-61`). It introduces a reference-free Bayesian hierarchical model that explains each observed gene count as endogenous, size-scaled expression plus distance-weighted leakage from neighbours (`paper.md:64-96`; Fig. 3).

Unlike a conventional deconvolution/denoising view, the method keeps a cell's latent identity and attributes contamination to surrounding cells. It learns latent labels, cell-type gene means, gene-specific diffusion coefficients, a global distance-decay parameter, variances, and type proportions by MCMC; posterior summaries yield nonnegative corrected expression (`paper.md:267-325`). The principal assumption is that marker genes and spatial heterogeneity make this separation identifiable up to label switching (`paper.md:276-290`).

### Evidence and evaluation

The authors compare DeLeakage with SPLIT and SpotClean on simulations, and with SPLIT on several real spatial datasets. In Fig. 4, the image shows recovered simulated marker maps, lower-looking residual distributions, and reported FDR tables; Fig. 5 shows cleaner mouse-brain MERFISH marker patterns and lower between-type cosine similarities; Fig. 6 displays higher ARI than raw/SPLIT in the illustrated datasets and lower unexpected-marker Moran's I in the Xenium heatmap. Supplementary Fig. 10 reports roughly linear scaling and favourable GPU benchmark numbers. These are reported paper results, not locally rerun experiments.

### Reproducibility assessment: 3/5

The primary GitHub snapshot is available at commit `3bff930a2793b0dff916b7320a1bddf9865d3180`. Its pybind entry point accepts all input paths and dimensions (`src/python_bindings.cpp:17-39`), and the C++ driver implements OpenMP MCMC updates, Markov-blanket label layers, and sample-file output (`src/Contamination.cpp:338-580`; `include/MCMC_v8.h:131-747`). This yields a **medium** paper-code fidelity assessment.

Important limits remain. The biorxiv HTML-to-Markdown conversion loses several display equations; the primary code tree contains no CUDA/GPU source despite paper-level GPU results; and no end-to-end corrected-expression writer was found in the verified primary source. The included example also points to absent `../dcuda/data/` paths. A separate acquired reproduction repository may address some workflow needs, but it was not treated as evidence for primary-package claims.

For the full method and boundaries, read `doc_method.md`; for exact code correspondence, read `doc_code.md`; for image-specific evidence, read `figure_analysis.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
