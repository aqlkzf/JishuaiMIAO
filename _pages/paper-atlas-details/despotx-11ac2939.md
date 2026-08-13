---
layout: default
permalink: /paper-atlas/despotx-11ac2939/
title: "DeSpotX"
nav: false
description: "DeSpotX 的本质是：用 anchor genes 解决 ST 去污染中的不可辨识性，用跨簇空间邻居估计局部污染，用 diffusion prior 防止低表达真实信号被过度删除；公开代码很好地实现了核心模型和 CLI，但不包含完整论文 benchmark 与下游生物分析复现流程。"
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
      <span>Computational Tools</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>DeSpotX</h1>
    <p>DeSpotX: Identifiability-Based Decontamination for Spatial Transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.05.12.724704" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DeSpotX">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Gentles-lab/DeSpotX" target="_blank" rel="noopener noreferrer" aria-label="Open code for DeSpotX">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeSpotX 方法中文解读

### 1. 这篇论文要解决什么问题？

DeSpotX 解决的是单细胞分辨率空间转录组（spatial transcriptomics, ST）里的转录本污染问题。论文指出，在 Xenium、MERFISH、CosMx、Stereo-seq 等平台中，一个细胞的 RNA 信号可能因为环境扩散、细胞分割误差或组织切片中细胞上下重叠，被错误分配到邻近细胞中。这会导致细胞类型标注混乱、marker 基因空间图谱被“抹开”、以及下游细胞通讯网络出现假阳性信号（`paper.md:18-24`）。

形式上，对每个细胞 *i*，输入包括：

- 观测到的基因计数向量 *x*~*i*~；
- 细胞簇标签 *t*~*i*~；
- 二维空间坐标 *s*~*i*~ ∈ ℝ^2^；
- K 个空间最近邻 𝒩(*i*)（`paper.md:54-56`）。

目标是恢复：

- 该细胞真实/native 的表达谱 ϕ；
- 该位置局部污染表达谱 *χ*~*i*~；
- 该细胞污染比例 *ε*~*i*~；
- 去污染后的计数矩阵（`paper.md:57-66`, `paper.md:122-125`）。

### 2. 为什么已有方法不够？

论文把现有方法的问题分成三类：

1. **不可辨识性（non-identifiability）**：同一个观测计数分布可以由很多组 native 表达、污染表达和污染比例组合生成；没有额外约束时，无法唯一判断哪一部分是真实表达、哪一部分是污染（`paper.md:60-66`）。
2. **空间局部性**：ST 的污染通常来自附近细胞，不是一个全局 ambient profile 能解释的。SoupX、DecontX、CellBender 等 scRNA-seq 方法主要依赖全局 ambient profile，不适合这种空间局部污染（`paper.md:36-39`）。
3. **低表达信号容易被过度校正**：低表达但真实存在的 marker 基因很容易在减污染时被一起减掉（`paper.md:18-24`, `paper.md:89-95`）。

ST 相关方法如 SpaceBender、DenoIST、ResolVI 利用了空间信息，但论文认为它们仍然没有从理论上解决 native/contamination 分解的不可辨识性（`paper.md:42-46`）。

### 3. DeSpotX 的核心思想

DeSpotX 的关键创新是：用 **anchor genes（锚定基因）** 给不可辨识的分解加入外部约束。对于某个细胞簇 *t*，如果基因 *g* 在该簇中不应 native 表达，那么设 *A*~*t,g*~ = 1，并约束 ϕ~*t,g*~ = 0。这样，在这些 anchor 位置上观测到的表达就应主要来自污染，可用于识别污染比例 *ε*（`paper.md:104-113`, `paper.md:308-320`）。

DeSpotX 同时用空间邻域估计污染来源：对每个细胞，只从**不同簇**的空间邻居中按距离加权平均表达谱，得到局部污染 profile *χ*~*i*~。这样可以避免把中心细胞同簇的 native 表达误当成污染（`paper.md:83-86`, `paper.md:341-344`）。

最后，DeSpotX 加入 latent diffusion prior，把 latent state *z* 约束在“合理的细胞簇条件表达分布”附近，从而减少对低表达真实信号的过度删除（`paper.md:89-95`, `paper.md:362-391`）。

### 4. 整体计算流程

可以把 DeSpotX 理解为下面的流程：

```text
原始 h5ad：整数 counts + cell type/cluster + 2D spatial coordinates
        │
        ├─ 计算每个 cluster-gene 的 anchor mask A[t,g]
        │
        ├─ 用空间坐标建立 KNN 邻域
        │
        ├─ 对每个细胞建立 star graph：中心细胞 + K 个邻居
        │
        ├─ Encoder：GATv2 聚合邻域，得到 h_i、z_i、ε_i
        │
        ├─ χ_i：跨簇邻居的距离加权平均污染表达谱
        │
        ├─ Decoder：根据 z_i 和 cell type 生成 native profile ϕ_i
        │
        ├─ 训练目标：NB 重构 + anchor penalty + diffusion loss + ε prior
        │
        └─ 推理：DDIM refine z_i，按 native/(native+ambient) 重加权 counts
```

代码中的 CLI 完整实现了这个流程：读取 `.h5ad`、检查 raw integer counts、计算 anchor、构建 `SpatialDataset`、训练模型、推理并输出去污染矩阵和污染比例（`despotx/cli.py:15-154`）。

### 5. 模型各模块详解

#### 5.1 空间图编码器

论文为每个细胞构建一个 star graph：中心节点是细胞 *i*，叶子节点是 K 个空间最近邻。节点特征是 log-transformed counts 拼接 cluster embedding；边特征是距离核 *w*~*ij*~ = exp(−∥*s*~*j*~ − *s*~*i*~∥ / *ρ*~*i*~)，其中 *ρ*~*i*~ 是邻居距离的中位数（`paper.md:80-83`, `paper.md:329-340`）。

代码中，`SpatialDataset` 用 `cKDTree` 根据坐标构建 KNN，并返回中心细胞与邻居的 counts、cell type、距离和 offset（`despotx/dataset.py:9-58`）。`GATEncoder` 对 counts 做 `log1p`，拼接 cell-type embedding，然后用 `GATv2Conv` 聚合 star graph，最后用线性层得到 latent `z`（`despotx/encoder.py:27-92`）。

#### 5.2 局部污染 profile χ

论文的 *χ*~*i*~ 是“跨簇邻居”的距离加权平均。这样做的目的，是把空间扩散来的其他细胞类型信号当作污染，而不是把同簇细胞的真实相似表达误删（`paper.md:83-86`）。

代码中 `_explicit_chi` 做了三件事（`despotx/encoder.py:94-138`）：

1. 用 `_dist_weights` 计算基于中位距离归一化的指数权重（`despotx/encoder.py:9-14`）；
2. 在 `other_type_hard` 模式下屏蔽同类型邻居；
3. 把邻居 counts 除以各自 library size 变成表达 profile，再加权平均得到 `chi`。

如果没有跨簇邻居，代码会回退到 `global_ambient`；这个 fallback 在 `warm_start_decoder` 中由各 cell type 的均值 profile 平均得到（`despotx/model.py:127-158`）。

#### 5.3 Anchor mask

论文中 anchor genes 是某个 cluster 中“不应 native 表达”的基因。Appendix C.4 说用 per-cluster expression rate *r*~*t,g*~ 构造 mask，并用默认 *κ* = 0.3 的 adaptive threshold（`paper.md:410-416`）。

代码 `compute_anchors` 计算每个 cell type 中每个基因非零表达的比例 `rate[t,g]`，adaptive 模式下阈值是 `adaptive_k * rate.max(axis=0)` 再做上下界裁剪，最后 `rate < threshold` 的位置就是 anchor（`despotx/anchors.py:6-72`）。CLI 默认 `--adaptive-k 0.3` 并传入 `adaptive=True`（`despotx/cli.py:27-29`, `despotx/cli.py:93-101`）。

#### 5.4 Decoder

Decoder 接收 latent `z` 和 cell type，输出 native expression profile ϕ。论文说它是 cluster-conditioned decoder，并使用 cluster-specific logit shift 从 cluster mean expression 初始化（`paper.md:98-101`, `paper.md:392-405`）。

代码 `CellTypeDecoder` 把 `z` 和 type embedding 拼接，通过 Softplus MLP，再加可选 `type_logit_shift`，最后 softmax 得到基因概率分布（`despotx/decoder.py:8-28`）。`warm_start_decoder` 用训练数据中每个 cell type 的归一化平均表达初始化 logit shift（`despotx/model.py:127-150`）。

#### 5.5 Diffusion prior

论文认为污染估计误差会放大低表达基因的相对误差，因此用 diffusion prior 约束 latent `z`（`paper.md:89-95`）。训练时，score network 预测加到 `z` 上的噪声，并且使用 stop-gradient，防止 encoder 为了让 diffusion loss 更容易而塌缩到无意义分布（`paper.md:374-386`）。

代码 `LatentScoreNet` 输入 noised latent、时间步 embedding、encoder context `h` 和 cell type embedding，输出噪声预测（`despotx/model.py:21-43`）。`training_step` 中，如果 `diff_detach=True`，会对 `z` 和 `h` 调用 `detach()`，实现 stop-gradient；loss 是预测噪声与真实噪声的 MSE（`despotx/model.py:191-200`）。推理时，`adjust_counts` 从 `z_enc` 加噪到 `refine_t_frac*T` 附近，再做 deterministic DDIM-like reverse steps（`despotx/model.py:231-268`）。

### 6. 训练目标

论文的联合目标包括（`paper.md:116-119`, `paper.md:422-443`）：

- 负二项分布重构损失：拟合 observed counts；
- anchor penalty：惩罚 anchor 位置的 native contribution；
- diffusion loss：训练 score network；
- contamination fraction regularizer：把 *ε* 拉向可学习的全局目标 *µ*~*ε*~。

代码中 `training_step` 的核心为（`despotx/model.py:165-227`）：

```text
mu = d * ((1 - eps) * phi + eps * chi)
loss_recon = - NB(mu, theta).log_prob(x)
loss_anchor = anchor_weight * native_contrib_at_anchor
loss_diff = MSE(pred_noise, noise)
loss_eps_prior = Beta prior penalty on eps
total = loss_recon + loss_anchor + diff_weight*loss_diff + loss_eps_prior
```

默认超参数也与论文一致：`anchor_weight=50`、`diff_loss_weight=1`、`eps_prior_weight=1`、anchor warm-up 3 epochs、Adam、学习率 1e-3、batch size 128、训练 10 epochs、梯度裁剪 10（`paper.md:422-449`; `despotx/model.py:46-126`; `despotx/train.py:18-83`; `despotx/cli.py:30-54`）。

### 7. 推理和输出

训练完成后，DeSpotX 的推理公式可以理解为：

```text
native  = (1 - ε_i) * ϕ_i
ambient = ε_i * χ_i
p_native = native / (native + ambient)
adjusted_count = observed_count * p_native * (1 - anchor_mask)
```

代码 `DeSpotX.adjust_counts` 正是这样实现：先可选 DDIM refine `z`，再 decode `phi`，计算 `p_native`，最后得到 `adjusted = x * p_native * (1.0 - anchor_per_cell)`（`despotx/model.py:231-278`）。`despotx/inference.py` 负责对整个 dataset 分 batch 推理并返回 `adjusted` 和 `epsilon`（`despotx/inference.py:12-35`）。CLI 会写出 `adjusted.mtx`、`adjusted_float.npy`、`anchor_mask.npy`、`genes.tsv`、`cells.tsv`、`contamination.tsv` 和 `adjusted.h5ad`（`despotx/cli.py:136-154`）。

### 8. 实验结果怎么支持方法？

论文在五个公开 ST 数据集上评估，覆盖 Xenium、Xenium 5K Prime、CosMx、MERFISH、Stereo-seq，panel size 从 313 到 18,582 个基因（`paper.md:129-136`）。因为真实 ST 没有污染 ground truth，论文构造 spike-in benchmark：抽样 40,000 个细胞，按空间局部 ambient profile 注入污染，并保留真实 native counts、污染标签和污染比例（`paper.md:142-151`）。

指标包括 AUROC、per-cell calibration error (PCE) 和 global calibration error (GCE)（`paper.md:162-166`）。论文报告 DeSpotX 在所有数据集和指标上最好，AUROC 都超过 0.94（`paper.md:169-180`）。

本地图片读取也支持主要视觉结论：

- Figure 1 展示 DeSpotX 的 encoder-diffusion-decoder-anchor 架构；
- Figure 2 显示 DeSpotX 后 UMAP cluster 更分离，marker dotplot 的 off-target 表达减少；
- Figure 3 显示 marker 空间表达更集中，很多基因 Moran's *I* 高于 raw；
- Figure 5 的 ablation 显示去掉 identifiability constraints 损失最大；
- Figure 6 显示 diffusion prior 对多个低表达 marker 有正 retention gain；
- Figure 12 显示不同污染水平下 AUROC 仍然很高；
- Figure 15 显示 DeSpotX 比 ResolVI 和 SpaceBender 这类深度 ST 方法快得多。

### 9. 代码复现性与缺口

**核心算法代码匹配度高。** 直接源码读取确认了 KNN 数据集、GAT encoder、跨簇 `χ`、anchor mask、decoder、NB mixture loss、diffusion stop-gradient、DDIM-like refinement、native-fraction reweighting 和 CLI 输出。

**可运行入口明确。** README 提供 conda/pip 安装和 MERFISH example；CLI 输入 `.h5ad`，要求 `.X` 是 raw integer counts，`obs` 有 cell type，`obsm` 有二维 spatial 坐标。

**主要缺口。** 仓库没有找到完整 spike-in simulation/benchmark 脚本、Table/Figure 复现实验脚本，也没有找到论文中 iterative CellTypist/CellChat 工作流。也没有 supplementary markdown。biorxiv 转换得到的 `paper.md` 中部分公式显示不完整，因此复杂公式只能按论文上下文和源码实现解释。

### 10. 一句话总结

DeSpotX 的本质是：用 anchor genes 解决 ST 去污染中的不可辨识性，用跨簇空间邻居估计局部污染，用 diffusion prior 防止低表达真实信号被过度删除；公开代码很好地实现了核心模型和 CLI，但不包含完整论文 benchmark 与下游生物分析复现流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeSpotX Summary

### Problem

DeSpotX addresses contamination in single-cell-resolution spatial transcriptomics (ST), where transcripts from one cell can be assigned to neighboring cells because of ambient diffusion, segmentation errors, or vertical overlap. The paper frames this as a deconvolution problem: from observed counts, cell-cluster labels, spatial coordinates, and K-nearest spatial neighbors, recover each cell's native expression profile, local contamination profile, and contamination fraction (`paper.md:18-24`, `paper.md:54-66`).

The core difficulty is non-identifiability. The same observed count distribution can arise from multiple combinations of native expression, contamination profile, and contamination fraction; the paper proves that without external constraints, the likelihood is constant over a continuum of decompositions (`paper.md:60-66`, `paper.md:266-287`).

### Existing-method limitations

The paper argues that standard ambient RNA correction methods for dissociated scRNA-seq use global ambient profiles and therefore miss spatially local contamination: DecontX (Genome Biology, 2020), SoupX (GigaScience, 2020), and CellBender (Nature Methods, 2023) are discussed in this category (`paper.md:36-39`, references `12-14`). ST-specific or ST-adapted methods such as DenoIST (bioRxiv, 2025), ResolVI (bioRxiv, 2025), and SpaceBender (bioRxiv, 2026) incorporate spatial context, but the paper argues that they do not resolve the native-versus-contaminant non-identifiability and may rely on smoothing or priors rather than anchor-based constraints (`paper.md:42-46`, references `8-10`).

### Proposed method

DeSpotX is an identifiability-based deep generative model for decontaminating single-cell-resolution ST. It combines four components (`paper.md:69-77`):

1. **Spatial graph encoder**: builds a star graph around each cell, uses log counts plus cluster embeddings and GATv2 attention to produce latent state `z_i` and contamination fraction `ε_i`.
2. **Local contamination profile `χ_i`**: estimates contamination from a cluster-masked, distance-weighted average over cross-cluster spatial neighbors.
3. **Cluster-conditioned decoder**: maps latent state and cluster label to native expression profile `ϕ`.
4. **Anchor constraints + diffusion prior**: anchor genes define cluster/gene positions where native expression should be zero, restoring identifiability; a latent diffusion prior regularizes low-expression signal and is used for DDIM-style inference refinement.

### Method overview

The implemented pipeline is:

```text
.h5ad raw integer counts + cell labels + 2D spatial coordinates
  -> compute adaptive anchor mask A[t,g]
  -> build KNN spatial neighborhoods
  -> train DeSpotX with NB reconstruction + anchor + diffusion + epsilon-prior losses
  -> refine latent z at inference
  -> adjusted count = observed count × native/(native + ambient) × non-anchor mask
```

Code reads verify the core method implementation. `SpatialDataset` builds KNN neighborhoods and returns center/neighbor counts, types, and distances (`despotx/dataset.py:9-58`). `GATEncoder` implements log-count/type features, GATv2 star-graph aggregation, and explicit cross-cluster `χ` estimation (`despotx/encoder.py:27-138`). `compute_anchors` builds per-cluster/gene anchor masks from expression rates (`despotx/anchors.py:6-72`). `DeSpotX.training_step` implements the NB mixture, anchor penalty, diffusion MSE with stop-gradient, and epsilon prior (`despotx/model.py:165-227`). `DeSpotX.adjust_counts` implements DDIM-style refinement and native-component count reweighting (`despotx/model.py:231-278`). The CLI provides an end-to-end `.h5ad` workflow and writes adjusted matrices, anchor mask, contamination estimates, and adjusted `.h5ad` (`despotx/cli.py:15-154`).

### Evaluation and main results

The paper evaluates on five public ST datasets spanning Xenium, Xenium 5K Prime, CosMx, MERFISH, and Stereo-seq, with four tissue contexts and panel sizes from 313 to 18,582 genes (`paper.md:129-136`). In spike-in simulations, the paper injects local ambient counts and evaluates AUROC, per-cell calibration error (PCE), and global calibration error (GCE) against SoupX, DecontX, ResolVI, and SpaceBender (`paper.md:142-166`). It reports DeSpotX as best on every metric and dataset, with AUROC above 0.94 on every dataset and improved PCE/GCE calibration (`paper.md:169-180`).

Local figure reads support the main visual claims:

- Figure 1 shows the model architecture and data flow.
- Figure 2 shows improved UMAP cluster separation and marker specificity after DeSpotX.
- Figure 3 shows more localized marker maps and many genes above the raw-vs-DeSpotX Moran's *I* diagonal.
- Figure 5 shows the largest ablation degradation when identifiability constraints are removed.
- Figure 6 shows positive retention gains from the diffusion prior for many low-expression markers.
- Figure 12 shows high AUROC across contamination levels.
- Figure 15 shows DeSpotX faster than ResolVI and SpaceBender in the reported deep-learning-method runtime comparison.

### Reproducibility notes

**Code-paper match:** high for the core model, loss, inference, and CLI. Direct source reads confirm implementation of the paper's key components. `doc_code.md` records 8 Exact, 3 Partial, and 2 Not found mappings.

**Runnable path:** the repository includes package metadata, a `despotx` CLI, README install instructions, and a MERFISH example workflow. The CLI requires raw integer counts in `.X`, cell labels in `obs`, and 2D spatial coordinates in `obsm`.

**Missing workflows:** the acquired repository does not include the full spike-in simulation/benchmark reproduction scripts, Table/Figure generation pipeline, or iterative CellTypist/CellChat downstream workflows. The paper results are therefore documented as paper claims, while code reproducibility is strongest for running DeSpotX itself on input `.h5ad` data.

**Other gaps:** no supplementary markdown was acquired; several biorxiv markdown equations are partially/raggedly rendered; large example-output files over 10 MB require publish-prep keep/ignore review.

### Bottom line

DeSpotX's main contribution is to turn spatial transcriptomics decontamination into an identifiable native-versus-contaminant decomposition by combining anchor genes, cross-cluster spatial contamination estimation, and diffusion-regularized latent decoding. The public code closely implements the core algorithm and CLI, but does not fully reproduce the paper's benchmark and downstream biological analysis workflows.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
