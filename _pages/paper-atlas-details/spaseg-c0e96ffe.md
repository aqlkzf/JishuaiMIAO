---
layout: default
permalink: /paper-atlas/spaseg-c0e96ffe/
title: "SpaSEG"
nav: false
description: "SpaSEG 面向空间转录组数据的多任务分析。空间转录组不仅有基因表达矩阵，还有每个 spot 或细胞在组织切片上的空间坐标。论文关心的核心问题包括：如何识别连续、边界清楚、具有生物意义的空间结构域；如何把相邻切片整合成一致的三维组织结构；如何在空间结构域内发现空间变异基因；以及如何在组织空间背景下分析配体-受体相互作用和细胞共定位。 已有方法的不足主要有三类。第一，普通聚类方法如 Leiden 主要看表达相似性，空间连续性不足；"
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
      <span>Genome Biology · 2025</span>
    </div>
    <h1>SpaSEG</h1>
    <p>SpaSEG: unsupervised deep learning for multi-task analysis of spatially resolved transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03697-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpaSEG">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/y-bai/SpaSEG" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaSEG">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaSEG 方法中文解读

### 1. 这篇论文要解决什么问题

SpaSEG 面向空间转录组数据的多任务分析。空间转录组不仅有基因表达矩阵，还有每个 spot 或细胞在组织切片上的空间坐标。论文关心的核心问题包括：如何识别连续、边界清楚、具有生物意义的空间结构域；如何把相邻切片整合成一致的三维组织结构；如何在空间结构域内发现空间变异基因；以及如何在组织空间背景下分析配体-受体相互作用和细胞共定位（`paper.md:42-42`）。

已有方法的不足主要有三类。第一，普通聚类方法如 Leiden 主要看表达相似性，空间连续性不足；第二，部分空间方法或配准方法在多切片整合时可能引入旋转、翻转或变形，破坏真实组织结构；第三，SVG 和 CCI 分析常常依赖单细胞场景的方法，不能充分利用组织中的空间邻近关系（`paper.md:33-39`）。

### 2. SpaSEG 的核心思想

SpaSEG 的关键想法是把空间转录组转换成“图像”，再把空间域识别看成无监督图像分割问题。具体来说，每个 spot 对应图像中的一个像素位置；每个 spot 的低维表达特征，也就是 PCA 后的前 `d` 个主成分，对应图像的 `d` 个通道；空白位置用 0 填充。这样，空间坐标和表达特征被统一放进一个多通道张量里（`paper.md:51-51`, `paper.md:254-260`）。

模型本身是一个很小的 CNN：先做 batch normalization，然后经过两个 3x3 卷积块，再经过 1x1 卷积 refinement 模块，输出每个 spot 的潜在表示 `y_n`。每个 spot 的伪标签由 `argmax(y_n)` 得到（`paper.md:263-284`）。代码中的 `SegNet` 直接实现了这个结构：`BatchNorm2d -> Conv2d(3x3) -> BatchNorm2d -> LeakyReLU(0.2)`，循环构造卷积块，最后接 `Conv2d(1x1)` 和 batch norm（`spaseg/spaseg_model.py:7-27`）。

### 3. 从输入到输出的计算流程

```text
原始 SRT 表达矩阵 + 空间坐标
        |
        v
过滤低质量基因/spot -> library-size 归一化 -> log1p -> PCA -> z-score
        |
        v
按平台缩放坐标，多切片时对齐到共同 H 和 W
        |
        v
构造 H x W x d 的图像式张量，空白像素填 0
        |
        v
CNN 学习每个 spot 的潜在表示
        |
        v
MSE 预训练 -> 伪标签交叉熵 + 边缘强度损失
        |
        v
空间域标签 + latent embedding
        |
        +--> 多切片整合
        +--> SVG 检测
        +--> 配体-受体 spot-wise 打分
        +--> 细胞共定位和 IDC 肿瘤微环境分析
```

预处理部分，论文描述了基因过滤、spot 过滤、归一化、log 转换、PCA 和 z-score 标准化（`paper.md:234-237`）。代码在 `data_processing/scanpy_processing.py` 中实现了 Scanpy 的过滤、归一化、log 和 PCA；在构造三维表达矩阵时对 `X_pca` 做 scale（`data_processing/scanpy_processing.py:34-93`, `spaseg/_utils.py:34-46`）。

对于非规则网格平台，例如 MERFISH、seqFISH、Slide-seqV2 和部分 Stereo-seq 数据，论文用平台相关的系数缩放坐标，以减少巨大空白像素（`paper.md:240-248`）。代码中 `add_spot_pos` 根据平台设置 scale 和 spot size（`data_processing/scanpy_processing.py:120-168`）。

多切片分析时，论文要求使用共同基因并把多个切片转换成同样大小的张量（`paper.md:249-260`）。代码用 `ad.concat(..., join="inner")` 取交集基因，再计算所有切片的共同最大 `H,W` 并堆叠成 batch（`data_processing/scanpy_processing.py:70-83`, `spaseg/spaseg.py:61-72`）。

### 4. 损失函数和训练方式

SpaSEG 的训练分两步。第一步是 MSE 预训练，用潜在输出 `y_n` 重构输入特征 `s_n`，让模型参数有较稳定的初始化。论文写的是前 400 个 epoch 用 MSE；代码中 `batch_idx < self.pretrain_epochs` 时调用 `MSELoss`，默认 `pretrain_epochs=400`（`paper.md:329-332`, `spaseg/spaseg.py:149-151`）。

第二步是无监督伪标签训练。模型每轮前向传播后，对每个 spot 的输出向量取 `argmax` 作为当前伪标签，然后用交叉熵让输出进一步贴近这个伪标签（`paper.md:277-296`, `spaseg/spaseg.py:125-140`, `spaseg/spaseg.py:152-154`）。这个过程类似自训练：标签不是人工给的，而是模型当前表示诱导出来的。

论文还加入了 L2 正则和边缘强度损失。代码里的 L2 不是手动写进 loss 公式，而是通过 Adam 的 `weight_decay=1e-5` 实现（`spaseg/spaseg.py:116-116`）。边缘强度损失则直接计算相邻行、相邻列 latent 表示的差，并用 L1 loss 惩罚这些差异，让空间域更连续、边界更平滑（`paper.md:299-326`, `spaseg/spaseg.py:144-155`）。

总体损失可以理解为：

```text
loss = alpha * 伪标签交叉熵 + beta * 边缘强度损失
```

默认单切片参数是 `alpha=0.4`、`beta=0.7`；论文建议多切片可用 `alpha=0.2`、`beta=0.4`，并说明不同任务会调参（`paper.md:335-335`, `spaseg/spaseg.py:38-40`, `spaseg_main.py:120-125`）。

论文还描述了 2000 个 epoch 后的额外 100 epoch 合并过程：如果还没达到目标空间域数，就合并相似域（`paper.md:329-332`）。代码默认 `iterations=2100`，在 2000-2100 之间调用 `merge_outlier`；该函数计算各 label 的均值向量和欧氏距离，并在特定 outlier 条件下合并最近的 label 对（`spaseg/spaseg.py:132-142`, `spaseg/_utils.py:73-109`）。这与论文方向一致，但实现细节比论文文字更具体。

### 5. 多切片整合

SpaSEG 的多切片整合不是先做复杂空间变换，而是把多个相邻切片作为 batch 同时输入同一个 CNN。这样模型在共同表达空间中学习切片间和切片内的结构，同时保留原始空间坐标关系（`paper.md:204-204`, `paper.md:329-335`）。代码路径是：`spaseg_main.py` 读取多个样本，判断 `n_batch > 1`，预处理后堆叠输入，训练同一个 `SpaSEG` 模型，再把 embedding 和 label 映射回各个 AnnData（`spaseg_main.py:46-90`）。

论文用 ARI、NMI、`F1_LISI` 和 `F1_SC` 评价多切片整合，并在 DLPFC、mouse olfactory bulb、MERFISH 和拼接 mouse brain 切片上展示结果（`paper.md:106-129`）。代码包里有 LISI 计算函数（`downstream/multisection/_metrics.py:24-129`），但 `F1_LISI` 和 `F1_SC` 的聚合公式主要在 notebooks 中实现，而不是封装成非 notebook 的 Python API。

### 6. SVG 检测

SpaSEG 识别空间域后，用这些空间域来检测 domain-specific SVG。论文的 SVG 流程分为两层：先用 Scanpy 的 `rank_genes_groups` 做目标域 vs 其他域的 Wilcoxon 差异分析，再用 log2FC、目标域表达比例、目标域 vs 最大 out-domain 的表达比例、CV 等规则筛选（`paper.md:338-350`）。

代码中 `downstream/svg/svg.py` 基本直接实现了这套流程。`detect_svg` 负责遍历目标 domain；`_rank_gene` 调用 `sc.tl.rank_genes_groups(... method="wilcoxon")`；`_ranks_svg` 计算 log2FC、表达比例、最大 out-domain、CV 等指标；`_find_svg` 用论文规则筛选最终 SVG（`downstream/svg/svg.py:19-293`）。

论文进一步用 Moran's I 和 adjusted Geary's C 评价 SVG 的空间自相关（`paper.md:500-528`）。当前仓库证据显示这些统计是在 SVG notebooks 中调用 Squidpy `spatial_autocorr` 完成的，并计算 `adj_C = 1 - C`；没有在非 notebook `.py` 文件中找到可复用 helper。

### 7. 配体-受体和细胞互作分析

SpaSEG 的 CCI 分析先基于空间域找显著的 ligand-receptor 对，再结合 cell2location 的细胞类型丰度估计、spot 邻居和表达共现，计算每个 spot 的 LR score（`paper.md:359-389`）。

论文定义 spot 异质性为细胞类型丰度的 entropy：

```text
E_n = - sum_k p_{k,n} log2(p_{k,n})
```

代码中如果提供了 cell-type abundance 矩阵，就用 `scipy.stats.entropy(..., base=2)` 计算；否则 heterogeneity 设为 1（`downstream/cci/cci.py:182-188`）。

LR score 的核心是邻域内 ligand 和 receptor 表达的几何均值。论文公式是：当 ligand 和 receptor 表达都大于阈值时，取 `sqrt(L_i * R_j)`，再对中心 spot 和邻居 spot 的两个方向求平均，并乘以 heterogeneity（`paper.md:373-389`）。代码实现与这个公式高度一致：用 `min_expr` 阈值过滤表达，计算 `sqrt(i_spot_lr_expr * i_nbs_rl_expr)`，对邻居平均，乘以 `spot_hetero`，最后把 L->R 和 R->L 两个方向取均值（`downstream/cci/cci.py:252-314`）。

需要注意的是，代码默认调用 Squidpy `ligrec` 时使用 `CellPhoneDB` resource；论文文字说 CellPhoneDB 还补充了 Omnipath 注释（`paper.md:362-362`, `downstream/cci/cci.py:106-119`）。因此，如果要完全复现论文 LR 数据库范围，可能需要检查 notebook 或外部传入的 LR p-value 表。

### 8. 细胞共定位和 IDC 应用

论文把细胞共定位定义为细胞类型丰度向量之间的 Spearman correlation coefficient（SCC）（`paper.md:398-409`）。直接检查代码后，没有在非 notebook `.py` 中找到封装好的 cell-colocalization API。notebook 证据显示，mouse brain 分析中用 `scipy.stats.spearmanr` 计算细胞类型两两相关，并把结果保存为 CSV；另有 colocalization notebooks 读取这些 SCC 矩阵做空间可视化（`notebook/CCI/Mouse_brain_bin200_LR_CT_corr_heatmap.ipynb:685-732`, `notebook/CCI/CCI_colocalization_MB.ipynb:79-84`, `notebook/CCI/CCI_colocalization_IDC.ipynb:127-130`）。

IDC 应用中，论文先用 SpaSEG 划分肿瘤区域，再用 OpenCV Canny 边缘、dilation、contour 和 Shapely buffer 构建 tumor-normal borderline 及 400/800 微米 margin 区域（`paper.md:412-418`）。代码中 `downstream/edge/_boundary.py` 实现了阈值化、Gaussian blur、Canny、dilation、contour、smooth boundary 和 Shapely line split 等基础函数（`downstream/edge/_boundary.py:18-172`）。不过完整的 ESTIMATE、GSVA、IDC margin 统计流程没有作为一个单独的非 notebook API 出现。

### 9. 论文结果如何理解

从结果上看，SpaSEG 的主张不是只在一个数据集上提高聚类分数，而是展示一个统一的空间域框架可以贯穿多个任务。DLPFC 结果显示它在 12 个 10x Visium 切片上取得最高 ARI 和 NMI（`paper.md:62-68`）；跨平台结果覆盖 Stereo-seq、seqFISH、MERFISH 和 Slide-seqV2（`paper.md:71-103`）；多切片结果展示它能在不强行扭曲空间结构的前提下对齐相邻切片（`paper.md:106-129`）；SVG 和 CCI 结果则说明空间域可以作为后续功能解释的基础（`paper.md:132-172`）。

### 10. 代码复现层面的结论

核心 SpaSEG 模型和训练流程是代码可验证的：预处理、张量构造、CNN、MSE 预训练、伪标签交叉熵、边缘损失、ARI/NMI、SVG 检测和 LR score 都有明确源码路径。完整论文复现则依赖更多 notebook、上游数据、结果 CSV 和补充表参数。当前 workspace 没有 supplementary markdown，因此论文中 Additional File 1 的表格和伪代码不能在这里直接核对。

简言之，SpaSEG 的核心贡献是：把 SRT 转成图像式张量，用小型无监督 CNN 加边缘约束学习连续空间域，再把这些空间域作为多切片整合、SVG、LR/CCI 和肿瘤微环境分析的共同坐标系。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaSEG Summary

### What Problem It Solves

SpaSEG targets spatially resolved transcriptomics (SRT) analysis, where researchers need to identify coherent tissue domains, integrate adjacent sections, find spatially variable genes (SVGs), and infer spatial cell-cell interactions from gene expression and spot coordinates. The paper argues that prior clustering and integration methods can lose spatial contiguity, distort tissue structure during registration, or fail to scale cleanly across SRT platforms and resolutions (`paper.md:33-42`).

### Proposed Method

SpaSEG reframes SRT analysis as unsupervised image segmentation. It preprocesses each SRT section into PCA features, maps those features onto a spatial grid as a multi-channel image-like tensor, then trains a CNN to produce spot-wise latent representations and pseudo-labels. The training objective uses MSE pretraining, pseudo-label cross entropy, L2 regularization via optimizer weight decay, and an edge-strength loss that penalizes abrupt horizontal/vertical latent changes (`paper.md:51-51`, `paper.md:254-335`; `spaseg/spaseg_model.py:7-27`, `spaseg/spaseg.py:75-169`).

The same learned domains support four downstream analyses: multi-section integration, SVG detection, ligand-receptor interaction scoring, and cell-type colocalization. SVG detection is implemented as domain-wise differential expression plus filtering by log fold change, spot-expression fractions, and coefficient of variation (`downstream/svg/svg.py:19-293`). LR scoring is implemented as a neighbor-aware, entropy-weighted geometric mean of ligand/receptor expression across focal and neighboring spots (`downstream/cci/cci.py:27-314`).

### Main Results

The paper reports SpaSEG as the top performer on 12 human DLPFC 10x Visium sections, with ARI `0.527 +/- 0.061` and NMI `0.643 +/- 0.021`, and a representative section score of ARI `0.554`, NMI `0.674` (`paper.md:62-68`). It also shows cross-platform domain identification across Stereo-seq, seqFISH, MERFISH, and Slide-seqV2, plus high-resolution whole mouse brain Stereo-seq up to 526,716 spots (`paper.md:71-103`).

For multi-section integration, the paper reports stronger ARI/NMI and `F1_SC`/`F1_LISI` than Harmony, LIGER, BayesSpace, GPSA, and PASTE on several adjacent-section settings, including mouse olfactory bulb `F1_LISI = 0.889 +/- 0.250` and `F1_SC = 0.651 +/- 0.020` (`paper.md:106-129`). For SVGs, SpaSEG detects biologically localized markers in DLPFC and mouse embryo, with elevated Moran's I and adjusted Geary's C and lower runtime than competing SVG methods (`paper.md:132-152`). For LR/CCI, SpaSEG identifies hundreds of significant LR pairs in adult mouse brain and IDC and benchmarks favorably against COMMOT by downstream-gene SCC and computational cost (`paper.md:155-172`, `paper.md:192-192`).

### Code-Paper Match

The core segmentation method is source-backed. The repository implements preprocessing, PCA-to-tensor construction, the SegNet CNN, MSE pretraining, pseudo-label cross entropy, edge loss, optimizer weight decay, label mapping, ARI/NMI metrics, SVG filtering, LISI utility, LR scoring, and tumor-boundary helpers.

The match is medium rather than high because several figure-level analyses are notebook-backed rather than packaged Python APIs: `F1_LISI`, `F1_SC`, Moran's I, adjusted Geary's C, and cell-type colocalization SCC. The LR helper math is directly verified in `downstream/cci/cci.py`, but the package's default Squidpy LR resource is `CellPhoneDB`, while the paper describes CellPhoneDB plus Omnipath annotations.

### Reproducibility Notes

The paper states that code is available on GitHub and Zenodo under an MIT license (`paper.md:570-573`). The repository README provides dependency versions and example commands for single-section and multi-section SpaSEG runs (`README.md:7-93`). The workspace has no supplementary markdown (`SUPP_MD=none`), so paper references to Additional File 1 tables and pseudocode could not be directly checked here.

Reproducibility rating: **3.5/5**. Core model behavior is implemented in readable package code with examples, but full paper reproduction depends on notebooks, large upstream datasets, retained acquired data files, result CSVs, and supplementary parameters not available as a separate local markdown file.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
