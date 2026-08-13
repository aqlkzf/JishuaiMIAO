---
layout: default
permalink: /paper-atlas/spavgmc-1dcae91a/
title: "SpaVGMC"
nav: false
wide: true
description: "SpaVGMC 解决的是空间转录组中的空间域识别问题：给定每个 spot/cell 的基因表达和空间坐标，学习一个既保留组织空间连续性、又能区分转录语义差异的低维表示，然后用于聚类、可视化、轨迹推断和差异表达分析 [outputpapermd/paper/hybridauto/paper.md:341-345]。 论文认为现有空间聚类方法有三类核心不足。第一，许多基于图的模型强调局部相似性，容易过度平滑，模糊真实的组织边界。"
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
      <span>Journal of Chemical Information and Modeling · 2026</span>
    </div>
    <h1>SpaVGMC</h1>
    <p>SpaVGMC: A Unified Representation Learning Framework via Structural and Semantic Alignment in Spatial Transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1021/acs.jcim.6c01121" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpaVGMC">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/CDMBlab/SpaVGMC" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaVGMC">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaVGMC 中文方法解读

SpaVGMC 解决的是空间转录组中的空间域识别问题：给定每个 spot/cell 的基因表达和空间坐标，学习一个既保留组织空间连续性、又能区分转录语义差异的低维表示，然后用于聚类、可视化、轨迹推断和差异表达分析 [paper source/paper/hybrid_auto/paper.md:341-345]。

### 为什么需要 SpaVGMC

论文认为现有空间聚类方法有三类核心不足。第一，许多基于图的模型强调局部相似性，容易过度平滑，模糊真实的组织边界。第二，已有结构缺少显式拓扑保真机制，学习到的潜在表示可能偏离真实空间组织。第三，一些自监督/对比学习方法依赖启发式数据增强，而图域中的增强不稳定，也可能破坏生物合理性 [paper source/paper/hybrid_auto/paper.md:66-68]。

SpaVGMC 的思路是把三个目标放进同一个表示学习框架：结构化变分表示学习负责建模不确定性和空间依赖；结构信息对齐负责让潜在空间保留空间图拓扑；语义对齐负责让表达相似的 spot 在全局语义上靠近 [paper source/paper/hybrid_auto/paper.md:68-73]。

### 输入、输出和流程

输入包括表达矩阵和空间坐标。论文先过滤低检测基因，选择 top 3,000 高变基因，并用 Scanpy 做归一化和 log 转换 [paper source/paper/hybrid_auto/paper.md:131-135]。然后构建空间图：10X Visium 用半径邻域，论文给出的半径约为 150；高分辨率平台使用 KNN，默认 k 约为 12 [paper source/paper/hybrid_auto/paper.md:137-145]。代码中的 DLPFC 示例确实选择 3,000 HVG、归一化、log1p，并调用 `Cal_Spatial_Net(... rad_cutoff=150)` [SpaVGMC_code/unpacked/SpaVGMC/DLPFC_151671.py:20-35]。

```text
表达矩阵 + 空间坐标
  -> 质控 / HVG / normalize / log
  -> 构建空间图 A
  -> GCN 变分编码器得到 mu, logvar, z
  -> GAT 解码器重构表达
  -> 结构对齐：latent adjacency 对齐真实空间图
  -> 语义对齐：加权正样本 + 负采样的对比学习
  -> L2 归一化 embedding
  -> KMeans 或 Leiden 聚类
```

### 结构化变分图表示

论文把每个 spot 的潜变量建模为高斯分布，均值和方差由图卷积网络根据表达和邻接图推断 [paper source/paper/hybrid_auto/paper.md:147-185]。代码中的 `VGATAE` 直接对应这个模块：`conv1` 是共享第一层，`conv_mu` 和 `conv_logvar` 分别输出均值和 log-variance；训练时用重参数化 `mu + eps * std`，测试时返回 `mu` [SpaVGMC_code/unpacked/SpaVGMC/model/VGATAE.py:23-48]。

解码器方面，论文描述为基于注意力的邻域加权重构 [paper source/paper/hybrid_auto/paper.md:187-205]。代码中用两层 `GATConv` 从潜在表示重构回输入维度 [SpaVGMC_code/unpacked/SpaVGMC/model/VGATAE.py:49-55]。

### 结构信息对齐

论文提出用互信息思想对齐潜在表示和空间图结构。边级别目标让潜在表示的点积邻接矩阵重构真实邻接；邻域级别目标用 KL 散度让局部分布和全局结构先验一致 [paper source/paper/hybrid_auto/paper.md:223-283]。代码中，训练时先计算 `adj_recon = z_proj @ z_proj.T`，再与真实 adjacency 做 BCE 和 KLDiv，并把二者加成 `loss_mi` [SpaVGMC_code/unpacked/SpaVGMC/model/Train.py:64-72]。这与论文的结构目标相符，但代码没有把 edge/local 两项拆成独立函数。

### 语义对齐和对比学习

语义对齐用于捕获空间距离之外的表达相似性。论文先根据 embedding 的余弦相似度选 top-k 正样本候选，再用 k-means 估计语义原型，并对候选正样本做概率加权聚合；负样本则从低相似度候选池中抽样，最后用 InfoNCE 类损失优化 [paper source/paper/hybrid_auto/paper.md:285-329]。

代码实现也基本一致：`BuildPositivePair.fit` 归一化 embedding、计算相似度、选 top-k、运行 FAISS k-means、根据 centroid 距离生成加权正样本 [SpaVGMC_code/unpacked/SpaVGMC/model/ContrastiveSample.py:41-68]。`NegativeSample.fit` 会屏蔽 KNN 正样本，从低相似度池中随机抽负样本 [SpaVGMC_code/unpacked/SpaVGMC/model/ContrastiveSample.py:69-103]。`contrastive_loss` 计算温度缩放后的正负相似度比例 [SpaVGMC_code/unpacked/SpaVGMC/utils.py:48-60]。

### 总损失和聚类

论文总目标为：

$$
L = L_{MSE} + \lambda_1 L_{KL} + \lambda_2 L_M + \lambda_3 L_{CRC}
$$

其中 MSE/KL 属于变分重构，$L_M$ 是结构对齐，$L_{CRC}$ 是语义对比学习 [paper source/paper/hybrid_auto/paper.md:331-339]。代码中的训练循环直接把这些项相加：`loss_recons + kl_weight * kl_divergence + lambda_mi * loss_mi + alpha * loss_contra` [SpaVGMC_code/unpacked/SpaVGMC/model/Train.py:82-87]。训练结束后，代码保存原始 embedding 和 L2 归一化 embedding；如果给出 `n_cluster` 就用 KMeans，否则扫描 Leiden resolution 并用 CH 指数选择 [SpaVGMC_code/unpacked/SpaVGMC/model/Train.py:101-128]。

### 结果和可复现性

论文报告 SpaVGMC 在 DLPFC、鼠脑冠状切片、MOB、E10.5 胚胎和人乳腺癌数据上优于多个基线。例如 DLPFC 上 mean ARI 为 0.585，slice 151671 上 ARI 为 0.783 [paper source/paper/hybrid_auto/paper.md:797-801]；鼠脑冠状切片上 SC 为 0.456、DB 为 0.862 [paper source/paper/hybrid_auto/paper.md:805-811]；E10.5 胚胎上 ARI/NMI 为 0.354/0.550 [paper source/paper/hybrid_auto/paper.md:1356-1360]；HBC 上 ARI 为 0.594 [paper source/paper/hybrid_auto/paper.md:1362-1364]。

代码可复现性为中等。公开仓库存在，并且核心模型、训练损失和 DLPFC 示例都能对应论文主方法；但仓库只包含一个 DLPFC 示例和核心模块，没有找到其他数据集 benchmark、消融实验、运行时间统计和完整绘图脚本。DLPFC 示例还硬编码了本地数据路径和 `R_HOME` [SpaVGMC_code/unpacked/SpaVGMC/DLPFC_151671.py:9-17]，因此需要整理路径和数据后才能直接运行。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaVGMC Summary

SpaVGMC addresses spatial transcriptomics domain identification, where methods must separate tissue domains while respecting both spatial continuity and transcriptional heterogeneity. The paper argues that prior approaches often oversmooth local neighborhoods, fail to preserve topological fidelity in latent space, or model global transcriptional semantics weakly [paper source/paper/hybrid_auto/paper.md:66-73].

The method builds a spatial graph from expression and coordinates, then learns spot embeddings with a structured variational graph model, structural alignment against the spatial graph, and semantic contrastive alignment. Preprocessing uses filtered genes, top 3,000 highly variable genes, Scanpy normalization, and log transform [paper source/paper/hybrid_auto/paper.md:131-145]. The encoder predicts latent mean/log-variance through graph convolutions, the decoder reconstructs features through attention over neighbors, and the training objective combines MSE reconstruction, KL regularization, structural alignment, and contrastive semantic alignment [paper source/paper/hybrid_auto/paper.md:147-339].

The released code matches the core algorithm at medium fidelity. It implements graph construction, PyTorch Geometric conversion, the GCN variational encoder, GAT decoder, reparameterization, BCE/KL graph-structure alignment, FAISS/KNN-based positive aggregation, negative sampling, contrastive loss, and KMeans/Leiden clustering [SpaVGMC_code/unpacked/SpaVGMC/utils.py:48-107; SpaVGMC_code/unpacked/SpaVGMC/model/VGATAE.py:23-59; SpaVGMC_code/unpacked/SpaVGMC/model/Train.py:64-128; SpaVGMC_code/unpacked/SpaVGMC/model/ContrastiveSample.py:31-103]. The repository is incomplete for full-paper reproduction: only one DLPFC example and core modules are present, while scripts for the remaining benchmark data sets, ablations, and runtime profiling were not found.

The paper reports broad benchmark gains. On DLPFC it reports highest mean ARI 0.585 and median ARI 0.559, plus ARI 0.783 on slice 151671 [paper source/paper/hybrid_auto/paper.md:797-801]. On mouse coronal brain it reports SC 0.456 and DB 0.862 and highlights recovery of hippocampal subfields and RSP [paper source/paper/hybrid_auto/paper.md:805-811]. On E10.5 embryo it reports ARI 0.354 and NMI 0.550 [paper source/paper/hybrid_auto/paper.md:1356-1360]. On HBC it reports ARI 0.594 and tighter tumor-domain separation [paper source/paper/hybrid_auto/paper.md:1362-1364].

Reproducibility is moderate. The public GitHub repository cited in the paper is available and was acquired, but it is a compact reference implementation. The DLPFC sample is runnable in principle given the expected local data paths, but the code hard-codes data/result paths and an R_HOME path in the example script [SpaVGMC_code/unpacked/SpaVGMC/DLPFC_151671.py:9-17]. The paper itself is closed access, so this workspace uses an OCR-derived PDF conversion with usable quality; formulas and some OCR-spaced values should be checked against the PDF before exact reuse.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
