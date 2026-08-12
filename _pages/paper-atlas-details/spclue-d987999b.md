---
layout: default
permalink: /paper-atlas/spclue-d987999b/
title: "spCLUE"
nav: false
description: "空间相邻 spot 往往属于同一区域，但表达相似的 spot 也可能跨越物理距离。spCLUE 分别构建空间 KNN 图与表达相关性 KNN 图，用共享 GCN 编码两视图，再以实例级和簇级对比损失对齐。输出是 spot 嵌入；论文最终空间域来自外部 mclust 和可选邻域多数投票，不是网络伪簇头直接给出的标签。 输入是 spot×gene 计数及 adata.obsm[\"spatial\"]。"
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
    <h1>spCLUE</h1>
    <p>spCLUE: a contrastive learning approach to unified spatial transcriptomics analysis across single-slice and multi-slice data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03636-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spCLUE 方法解读：让空间图与表达图在同一个嵌入中达成一致

### 核心问题

空间相邻 spot 往往属于同一区域，但表达相似的 spot 也可能跨越物理距离。spCLUE 分别构建空间 KNN 图与表达相关性 KNN 图，用共享 GCN 编码两视图，再以实例级和簇级对比损失对齐。输出是 spot 嵌入；论文最终空间域来自外部 `mclust` 和可选邻域多数投票，不是网络伪簇头直接给出的标签。

### 输入、图与预处理

输入是 spot×gene 计数及 `adata.obsm["spatial"]`。默认预处理过滤空基因/spot、总量归一到 10,000、`log1p`、缩放，教程再计算 PCA。空间图按欧氏距离选近邻；表达图在 `prepare_graph(..., "expr")` 内另做 PCA，再按 Pearson 相关性选边，并删除相关性不高于 0.1 的边。两图加入权重 0.3 的自环并对称归一化。

模型输入 PCA 通常由 notebook 缓存为 `X_pca`，表达图却内部重算 PCA；两者概念相同但不是同一个对象。图构建还生成全体 spot 的稠密距离/相关矩阵，所以尽管输出稀疏，预处理有 $O(n^2)$ 内存边界。

### 两视图 GCN 与损失

两视图共用两层 GCN 权重。每次前向对特征加入高斯噪声和 dropout，并分别 dropout 图边，得到 $Z_{spa}$ 和 $Z_{expr}$。实例损失拉近同一 spot 的跨视图投影；簇损失让跨视图同名伪簇相似、不同伪簇分离，并以熵项防塌缩。

`n_clusters` 决定训练期伪簇头宽度，最终 `mclust` 也需要外部给定域数，因此模型没有自动发现空间域数量。

两视图 L2 归一化表示经逐 spot 注意力融合为 $Z$，解码器重建 PCA 输入：

$$\gamma\mathcal L_{rec}+\beta\mathcal L_{cls}+\kappa\mathcal L_{ins},$$

默认权重 1、1、0.1。解码器使用编码权重的 `.data.T`，故重建路径不会以常规 tied-weight 方式经解码器反向更新这些权重；编码路径仍更新它们。

### 多切片与 batch prompt

多切片把各切片两类图拼成块对角矩阵，没有跨切片图边。共享网络与 batch prompt 对齐切片：输入减去 PCA prompt，重建端给潜在表示加回另一组 prompt。代码把二者固定缩放为 0.01，未暴露为参数。

若 `batch_train=True`，实例/簇损失每轮最多随机使用 20,000 spot；第 100 轮后代码把 `kappa=0`，后续不再优化实例对比项。这比论文静态总损失公式多了一段未显式描述的训练日程。

### 停止与最终标签

单切片每 100 轮计算两个视图伪标签之间的 ARI。小数据达到阈值会早停；超过 10,000 spot 时阈值设为 1.1，ARI 不可能达到，因而跑满 epoch。该 ARI 是视图一致性，不是相对人工组织标签的准确率。

多切片早停会返回字符串 `"hello"` 与嵌入；字符串只是占位。分析使用融合嵌入调用 R `mclust`（经 `rpy2`），纯 Python 环境不能原样获得论文标签。

### 图 1–7 的证据链

- 图 1：双图、对比头、注意力、prompt 和重建架构。
- 图 2–4：DLPFC、BRCA/MOSTA/BARISTA 与小鼠嗅球单切片比较。代表切片的高 ARI 不能替代跨数据集不确定性。
- 图 5：12 张 DLPFC 多切片整合；跨切片邻近并非直接建图得到。
- 图 6：多切片排名和 scIB 指标；需同时读 batch correction 与 bio conservation。
- 图 7：损失、prompt、注意力的论文级消融，本地没有完整消融脚本。

### 论文—代码差异与复现边界

1. batch prompt 固定乘 0.01，论文公式未突出该缩放。
2. batch 模式第 100 轮关闭实例损失，与静态总损失不同。
3. 图在 prompt 校正前预先构建；prompt 不会重建表达图。
4. `__all__` 声明 `symm_norm`，但入口未导入；`from spCLUE import symm_norm` 会失败。
5. HVG 模式硬编码 `adata.layers["count"]`，缺失会报错。
6. 无 `setup.py`/`pyproject.toml` 与自动化测试，主要可运行证据是四个 notebook。
7. 完整基准、scIB、运行时和消融流水线未随快照提供，论文图不是本地一键复现。
8. 空间连续、ARI/NMI 更高支持特定参考标签上的一致性，但不能证明域具有因果或唯一生物学边界。

### 直接证据

- 论文/图：`paper source/PMC12183872/paper.md`、`paper source/PMC12183872/images/`
- 图构建：`spCLUE_code/spCLUE/preprocess.py:9-88`
- 网络：`spCLUE_code/spCLUE/network.py:8-245`
- 损失：`spCLUE_code/spCLUE/loss.py:375-484`
- 训练：`spCLUE_code/spCLUE/spCLUE.py:12-230`
- 聚类：`spCLUE_code/spCLUE/utils.py:131-181`
- 快照提交：`bbd2c342e7a67c1617275f721cec2e3f4c23a799`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## spCLUE Summary

### Motivation and Novelty

spCLUE addresses spatial domain identification in single-slice and multi-slice spatial transcriptomics. The motivating problem is that spatial proximity and expression similarity are both useful but can disagree. Existing methods often use either non-spatial expression clustering, one fused spatial-expression graph, or batch correction as a preprocessing step. spCLUE instead learns from two separate graph views and uses contrastive learning to align them.

The main novelty is the combination of:

- separate **spatial KNN** and **expression KNN** graph views,
- a shared two-layer GCN encoder for each view,
- an **instance contrastive loss** aligning the same spot across views,
- a **cluster contrastive loss** encouraging pseudo-cluster structure without labels,
- an **attention module** that fuses spatial-view and expression-view embeddings,
- a **batch prompting module** for multi-slice integration.

The method is positioned as a unified framework for both single-slice domain detection and multi-slice integration, including unaligned slices.

### Method Overview

spCLUE first preprocesses expression data with Scanpy-style filtering, library-size normalization, log transform, scaling, and PCA. It then builds two normalized graphs over spots: a spatial graph from Euclidean-coordinate KNN and an expression graph from Pearson-correlation KNN. Graph preparation materializes dense all-pairs matrices, giving it a quadratic memory boundary even though the returned graphs are sparse. Each graph is corrupted by edge dropout and encoded with a two-layer GCN. Feature noise/dropout is also applied during training.

The spatial and expression embeddings are trained with two contrastive objectives. The instance objective aligns each spot's two view-specific representations, while the cluster objective aligns pseudo-cluster probability columns across views and discourages collapse. An attention module fuses the two view embeddings into a single spot representation. A decoder reconstructs the input expression features, so the embedding is trained by reconstruction, cluster contrast, and instance contrast jointly.

For multi-slice data, spCLUE constructs block-diagonal per-slice graphs and learns batch prompt embeddings. These prompts are subtracted from input PCA features before encoding and added back to latent embeddings before reconstruction. The final fused embedding is clustered with `mclust`, and tutorials optionally apply spatial neighbor majority-vote refinement.

### Evaluation

The paper evaluates spCLUE on six single-slice datasets spanning 10x Visium, Slide-seqV2, Stereo-seq, and BaristaSeq: DLPFC, BRCA, MOSTA, BARISTA, MOB1, and MOB2. It compares against Seurat (Cell 2019), BayesSpace (Nature Biotechnology 2021), BASS (Genome Biology 2022), SpaGCN (Nature Methods 2021), STAGATE (Nature Communications 2022), CCST (Nature Computational Science 2022), SpaceFlow (Nature Communications 2022), GraphST (Nature Communications 2023), and SEDR (Genome Medicine 2024). Metrics include ARI, NMI, silhouette coefficient, and Calinski-Harabasz score.

For multi-slice integration, the paper compares spCLUE against Harmony (Nature Methods 2019), BayesSpace, BASS, STAGATE, GraphST, STAligner (Nature Computational Science 2023), and SEDR across DLPFC, MOSTA, and BARISTA multi-slice settings. It also reports scIB-derived batch-correction and bio-conservation scores. spCLUE ranks strongly in aggregate, including first or near-first positions across many multi-slice metrics, but some dataset-specific comparisons are close, such as BARISTA where SEDR is slightly higher in one ARI summary.

Ablation experiments support the contribution of instance contrast, cluster contrast, batch prompting, and attention fusion. The public code, however, does not include the full benchmark and ablation scripts, so these results are paper-level claims rather than directly reproducible from the cloned repository alone.

### Reproducibility

**Rating: 3 / 5.**

The core method is reproducible at the package level: the repository provides compact Python modules for preprocessing, graph construction, the GCN models, losses, training wrappers, clustering utilities, requirements, and four tutorial notebooks. The paper's declared GitHub repository was accessible, and the code maps closely to the mathematical method.

The main limitations are full-paper reproducibility gaps. The repository does not include scripts for the complete six-dataset single-slice benchmark, seven multi-slice benchmark, ablation suite, scIB scoring, runtime profiling, or memory profiling. It also depends on R `mclust` through `rpy2`, has no packaging metadata such as `setup.py` or `pyproject.toml`, and contains hidden training details such as fixed batch-prompt scale, batch-mode loss subsampling, and a mid-training change that sets `kappa=0` after epoch 100.

Overall, a user can run the method on representative datasets with the tutorials, but reproducing the exact paper figures and aggregate rankings would require additional data-preparation and benchmarking code beyond the public repository.

### Key Takeaways

- spCLUE is best understood as a two-view graph contrastive representation learner for spatial domains.
- The cluster contrastive head shapes embeddings but is not the final clustering algorithm; final labels come from `mclust` plus optional spatial refinement.
- Multi-slice integration does not rely on explicit cross-slice graph edges; it relies on shared model parameters, block-diagonal per-slice graphs, and batch prompts.
- The paper's strongest evidence is aggregate benchmarking across many datasets and ablations, but the public code supports method execution more than full benchmark reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
