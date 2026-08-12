---
layout: default
permalink: /paper-atlas/proteinvelocity-42e91e15/
title: "ProteinVelocity"
nav: false
description: "RNA velocity 能用单细胞 RNA-seq 中的未剪接 RNA（unspliced RNA, u）和已剪接 RNA（spliced RNA, s）推断细胞状态的未来方向。但在多组学实验中，同一个细胞还可以测到蛋白/ADT 丰度。Gorin、Svensson 和 Pachter 的核心问题是：当前蛋白水平是否能反推出细胞在更早时刻的转录状态，从而把单时间点数据扩展成“过去—现在—未来”的动态解释。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Genome Biology · 2020</span>
    </div>
    <h1>ProteinVelocity</h1>
    <p>Protein velocity and acceleration from single-cell multiomics experiments</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-020-1945-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Protein velocity and acceleration：中文方法解释

### 这篇文章要解决什么问题？

RNA velocity 能用单细胞 RNA-seq 中的未剪接 RNA（unspliced RNA, $u$）和已剪接 RNA（spliced RNA, $s$）推断细胞状态的**未来方向**。但在多组学实验中，同一个细胞还可以测到蛋白/ADT 丰度。Gorin、Svensson 和 Pachter 的核心问题是：当前蛋白水平是否能反推出细胞在更早时刻的转录状态，从而把单时间点数据扩展成“过去—现在—未来”的动态解释（paper.md:12-27）。

### 为什么已有方法不够？

经典 RNA velocity（La Manno et al., *Nature*, 2018）只使用未剪接和已剪接 RNA 的相对位置来预测未来 spliced RNA 的变化方向。它不能直接利用蛋白丰度中保留的历史信息。本文提出：蛋白是由过去的 spliced RNA 翻译而来，所以当前蛋白 $p$ 可以提供关于过去 spliced RNA 的信息（paper.md:20-27）。这使得 paired RNA+protein 单细胞数据可以同时产生：

- RNA velocity：指向未来；
- protein velocity：指向过去；
- protein acceleration：把过去、现在、未来三个点连成曲线，用来定性表示细胞状态轨迹的弯曲。

### 核心模型

RNA velocity 的一阶模型是：

$$
\frac{ds}{dt}=\beta u-\gamma s
$$

其中 $u$ 是 unspliced RNA，$s$ 是 spliced RNA，$\gamma$ 是 RNA 降解率。平衡线为：

$$u=\gamma s.$$

本文把同样思想扩展到蛋白：

$$
\frac{dp}{dt}=\beta_p s-\gamma_p p
$$

其中 $p$ 是蛋白丰度，$\gamma_p$ 是蛋白降解率。平衡线为：

$$s=\gamma_p p.$$

偏离平衡线的方向就是速度方向：RNA 的偏离给出未来 spliced RNA 趋势；蛋白的偏离给出过去状态的估计（paper.md:24-27; supplementary_note.md:41-130）。

### 计算流程

```text
paired RNA/protein 单细胞数据
        |
        v
匹配 RNA 与 protein 共有细胞，过滤过稀疏细胞
        |
        v
kNN 平滑/插补（protein velocity 默认用 protein 空间找邻居）
        |
        +------------------------------+
        |                              |
        v                              v
RNA velocity 分支               Protein velocity 分支
拟合 u~s 极端分位点             拟合 s~p 极端分位点（手工选择蛋白对）
计算 Δs                         计算 Δp
        |                              |
        +--------------+---------------+
                       v
根据高维速度与邻居位移的相关性计算嵌入空间转移概率
                       |
                       v
在 20×20 网格上用 Gaussian kernel 聚合速度箭头
                       |
                       v
组合 backward protein velocity 与 forward RNA velocity，绘制 acceleration curve
```

代码中，`protaccel.py` 对应这些步骤：

- `import_prot_data` 读取 feature-barcoding 蛋白 CSV（`GSP_2019/protaccel.py:17-31`）。
- `shared_cells_filter` 保留 RNA 与 protein 共有细胞并保存 `vlm.P`（`GSP_2019/protaccel.py:52-94`）。
- `impute` 用 kNN 平滑，默认在 protein 空间建邻居图，并产生 `Px/Sx/Ux`（`GSP_2019/protaccel.py:116-164`）。
- `gamma_fit` 用 phase plot 极端分位点拟合降解斜率；RNA 分支自动按 R² 和正斜率筛选，protein 分支使用手工提供的 marker pair（`GSP_2019/protaccel.py:357-468`）。
- `extrapolate` 计算 `delta_S` 和 `delta_P`（`GSP_2019/protaccel.py:470-482`）。
- `calculate_embedding_delta` 根据速度和邻居位移相关性计算嵌入空间方向（`GSP_2019/protaccel.py:484-542`）。
- `calculate_grid_arrows` 与 `plot_grid_arrows` 生成网格箭头（`GSP_2019/protaccel.py:598-687`）。
- `plot_bezier` 构造过去/现在/未来三个点并绘制曲线，但它使用 `degree=1`，而论文写的是二阶 Bézier 曲线；这是一个需要注意的代码-论文差异（`GSP_2019/protaccel.py:692-746`）。

### 评估结果

论文在六个 PBMC 数据集上运行该框架：CITE-seq、REAP-seq、ECCITE-seq control、ECCITE-seq CTCL、10X 1k、10X 10k（paper.md:31-55）。主要结论是：

- 手工选择的一部分 spliced RNA/protein phase plot 近似线性，支持一阶蛋白生成模型，但不同细胞类型有偏离（paper.md:57-58）。
- protein velocity 比 RNA velocity 更噪，因为蛋白 panel 只有几十个 marker，而 RNA gene panel 有上千个基因（paper.md:60-64）。
- RNA 与 protein velocity 的方向一致性和细胞类型相关；二者组合后可观察到 B 细胞、单核细胞等区域的 acceleration/curvature 模式（paper.md:60-68）。
- CITE-seq 和 10X feature barcoding 信号较可靠；ECCITE-seq RNA 过稀疏，动态图更弱（paper.md:70-72）。

### 适用性与局限

这个方法的定位是**定性动态几何**，不是完全定量的动力学参数估计。它依赖若干假设：ADT/protein 计数能代表真实蛋白水平；splicing/translation rate 的相对尺度不会破坏方向判断；protein velocity 的 marker pair 需要手工挑选；嵌入空间的转移概率由高维速度和邻居位移相关性决定（supplementary_note.md:164-226）。

因此，ProteinVelocity 最适合用于 paired RNA+protein 单细胞数据中的假设生成：它能把 RNA velocity 的未来方向和 protein velocity 的过去方向放在同一嵌入图上，帮助研究者观察细胞状态轨迹是否存在弯曲、加速或细胞类型相关的动态差异。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Protein velocity and acceleration from single-cell multiomics experiments — Summary

### Problem

This paper addresses a limitation of RNA velocity: unspliced/spliced RNA dynamics can extrapolate a future transcriptomic direction, but they do not directly use paired protein measurements to infer where a cell came from. Gorin, Svensson, and Pachter propose that current protein abundance carries information about past spliced RNA abundance, allowing a single snapshot of paired RNA/protein single-cell data to support a past-present-future view of cell state (paper.md:12-27).

### Proposed method

The method extends RNA velocity's first-order ODE logic into translation. RNA velocity uses

$$\frac{ds}{dt}=\beta u-\gamma s$$

while protein velocity uses

$$\frac{dp}{dt}=\beta_p s-\gamma_p p.$$

The equilibrium lines $u=\gamma s$ and $s=\gamma_p p$ define deviations interpreted as RNA and protein velocity directions (paper.md:24-27; supplementary_note.md:41-130). RNA velocity gives a forward estimate; protein velocity gives a backward estimate. The paper combines these into **protein acceleration** by placing past, present, and future points in a shared embedding and drawing a curved trajectory (paper.md:82-84; supplementary_note.md:155-162).

### Pipeline at a glance

1. Pair RNA and protein counts from the same cells.
2. Smooth unspliced RNA, spliced RNA, and protein counts over nearest neighbors, with protein-space neighbor smoothing preferred for protein velocity (paper.md:78-80; supplementary_note.md:69-78).
3. Fit phase-plot extrema to estimate RNA and protein degradation slopes (paper.md:80-81; supplementary_note.md:83-107).
4. Compute deviations from equilibrium lines as RNA/protein velocity vectors (supplementary_note.md:108-130).
5. Embed high-dimensional velocity directions using neighbor transition probabilities and aggregate them onto a grid (paper.md:82-84; supplementary_note.md:133-153).
6. Combine backward protein velocity and forward RNA velocity into a qualitative acceleration curve (paper.md:60-64, 82-84).

### Evaluation

The paper analyzes six PBMC datasets from CITE-seq, REAP-seq, ECCITE-seq control/CTCL, and 10X feature barcoding (paper.md:31-55). It reports that manually selected spliced RNA/protein phase plots are often approximately linear, but with deviations by cell type (paper.md:57-58). Protein velocity fields are noisier than RNA velocity because protein panels are much smaller than gene panels, yet combined RNA/protein velocity fields reveal cell-type-associated acceleration patterns such as high-acceleration B-cell subsets and mobile monocytes (paper.md:60-68). CITE-seq and 10X feature barcoding appear more reliable than very sparse ECCITE-seq RNA measurements (paper.md:70-72).

### Code and reproducibility

The paper links scripts at `https://github.com/pachterlab/GSP_2019`, acquired here at commit `61926a471186bdd64989359628b34e0ba8deb0b0` (paper.md:86-87, 118-123). The core code file `GSP_2019/protaccel.py` implements the main algorithmic steps: protein import and paired-cell filtering, kNN smoothing, extrema slope fitting, velocity extrapolation, embedding transition probabilities, grid aggregation, and plotting (`doc_code.md`). Dataset notebooks call these functions for individual experiments.

Code-paper fidelity is **medium-high**. The mathematical workflow is well represented in `protaccel.py`, but the reproducibility snapshot is notebook-heavy and old, with no modern environment lockfile found. One material discrepancy is that the paper describes a second-order Bézier curve, while `plot_bezier` constructs three past-present-future nodes but calls `bezier.Curve(..., degree=1)` (`GSP_2019/protaccel.py:692-746`).

### Main limitations

The authors explicitly frame protein acceleration as qualitative. It relies on assumptions about observed protein counts, approximately comparable positive rate scales, manually selected protein/RNA pairs, and embedding-neighbor transition probabilities (supplementary_note.md:164-226). The method is therefore most useful as a visual and hypothesis-generating temporal geometry for paired RNA/protein data, not as a fully calibrated kinetic estimator.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
