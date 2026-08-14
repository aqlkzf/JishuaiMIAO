---
layout: default
permalink: /paper-atlas/sude-40da97a2/
title: "SUDE"
nav: false
wide: true
description: "高维、海量数据做流形学习时，传统方法容易扭曲簇结构，而且全量邻域和优化的计算/内存成本会随样本数快速增长。论文摘要提出 SUDE（sampling-enabled scalable manifold learning for uniform and discriminative embedding）：先用少量 landmark 建立全数据的低维骨架，再把其余样本放回这个骨架中。 sude."
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>SUDE</h1>
    <p>Sampling-enabled scalable manifold learning unveils the discriminative cluster structure of high-dimensional data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-025-01112-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SUDE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ZPGuiGroupWhu/sude" target="_blank" rel="noopener noreferrer" aria-label="Open code for SUDE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SUDE 方法中文解读

### 它要解决什么问题

高维、海量数据做流形学习时，传统方法容易扭曲簇结构，而且全量邻域和优化的计算/内存成本会随样本数快速增长。论文摘要提出 SUDE（sampling-enabled scalable manifold learning for uniform and discriminative embedding）：先用少量 landmark 建立全数据的低维骨架，再把其余样本放回这个骨架中（`paper source/nature_html/paper.md:9-12`）。

### 核心思路

```text
高维矩阵 X
  -> 去重、可选 min-max 归一化
  -> KNN 与反向邻居计数
  -> PPS（Plum Pudding Sampling）选 landmarks
  -> 在 landmarks 上构造稀疏概率图并优化低维坐标
  -> 为非 landmark 找 d+1 个邻居并用 CLLE 放置
  -> 合并坐标、恢复重复行顺序
```

`sude.m` 的输入是 $N\times D$ 矩阵，输出是 $N\times d$ 嵌入、landmark 索引和参数表。代码先用 `unique` 去除重复行，默认进行逐特征 [0,1] 归一化，并按照数据规模自动设定邻居数（`sude/sude_mat/sude.m:30-54,37-47`）。当 `NumNeighbors>0` 时，KNN 和反向邻居数被交给 PPS；PPS 每次选择反向邻居数高的点，再删除它及其一阶 KNN，直到队列耗尽（`pps.m:1-24`）。

### landmark 学习

对每个 landmark，代码用共享近邻（SNN）修正欧氏距离，再取 $k_2$ 个近邻形成稀疏 $P$ 矩阵：

$$D'_{ij}=(1-\mathrm{SNN}_{ij})^{\gamma}\lVert x_i-x_j\rVert_2,$$

$$P_{ij}=\exp\left(-\frac{(D'_{ij})^2}{2\max(\overline{D_i}^2,\epsilon)}\right).$$

随后对 $P$ 对称化、归一化，用 Laplacian eigenmaps（也可 PCA/MDS）初始化，再迭代优化低维坐标（`learning.m:1-41,55-88,140-184`）。大数据时，代码可按 block 计算 SNN 和梯度以限制内存（`learning.m:90-137,186-244`）。这部分公式是代码逐行转写；由于 Nature 页面只提供订阅预览，论文原始公式编号属于 `Not found`。

### 非 landmark 放置

每个非 landmark 在高维空间找 `d+1` 个最近 landmark，`opt_scale` 估计局部高维/低维距离比例。CLLE 对局部差分矩阵求满足权重和为 1 的重构权重；先得到加权低维位置，再沿最近 landmark 到该位置的方向按目标距离缩放（`sude.m:80-109`, `opt_scale.m:1-17`, `clle.m:1-24`）。这样只需在小骨架上做昂贵的流形优化，其他点通过局部约束补回。

### 实验与复现

六幅图分别展示合成采样、五个真实数据集、13 个数据集的质量/时间、scRNA-seq/CyTOF 和 ECG 异常识别。可见图中 SUDE 通常保持簇的分离和整体形状；摘要还声称对较低采样率具有鲁棒性（`paper.md:58-85`）。代码仓库提供 MATLAB/Python 实现、rice 示例以及 `scRNA-seq/`、`ECG/` 应用目录；数据可用性链接列于 `paper.md:97-106`。详细基线参数、数值指标、补充实验和论文方法正文在本地订阅预览中没有出现，不能据此补写。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SUDE Summary

### Problem and Contribution

Manifold-learning embeddings can distort cluster structure and become expensive as both sample count and feature dimension grow. SUDE addresses this by sampling a representative landmark skeleton, learning the manifold on that smaller set, and placing the remaining observations with constrained locally linear embedding. The abstract reports improved scalability, cluster separation/integrity, global-structure preservation and robustness when the sampling rate decreases (`paper source/nature_html/paper.md:9-12`).

### Method in Brief

The implementation deduplicates and optionally min-max normalizes $X$, constructs KNN/reverse-neighbor context, selects landmarks with Plum Pudding Sampling, learns landmark coordinates using a sparse probability graph and iterative low-dimensional optimization, then uses local scale calibration plus CLLE to place non-landmarks (`sude/sude_mat/sude.m:30-109`, `learning.m:1-41`, `pps.m:1-24`, `clle.m:1-24`). Dense/block learning modes and memory budgeting provide repository-level scalability controls.

### Evaluation Evidence

The six acquired figures cover synthetic sampling tests, five real-world embedding comparisons, 13-dataset quality/runtime comparisons, scRNA-seq/CyTOF analyses and ECG anomaly recognition (`paper.md:58-85`). The visible plots show better coverage and separated groups for SUDE in representative panels. The paper lists UCI, MNIST/CIFAR/FMNIST/news, single-cell/CyTOF and ECG data sources (`paper.md:97-106`), but exact metric definitions, baseline versions, sample counts and numerical results are `Not found` because the publisher HTML is a subscription preview.

### Reproducibility

Code is available in MATLAB and Python through the paper-linked GitHub repository and Code Ocean (`paper.md:103-106`). The clone is `sude` at commit `0a5c95568c2794f5b99ecb2747e9f7d9130a93c5`; README examples cover Python installation and a MATLAB rice benchmark. Core algorithm files are directly inspected and mapped in `doc_code.md`. The full methods body and supplementary PDF were not acquired, so equation-level fidelity and exact experiment reproduction remain incomplete. Reproducibility rating: **3/5** for code availability and readable core implementation, reduced by missing primary-method text and detailed experiment settings.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
