---
layout: default
permalink: /paper-atlas/3d-ot-e05ddc6c/
title: "3d-OT"
nav: false
description: "3d-OT 将空间组学切片表示为二维点云：每个 spot 既有坐标，也有 RNA、染色质或蛋白特征。它先用 PointNet++ 风格的局部集合卷积学习同时保留空间几何和分子信号的表示，再用受空间候选约束的 Sinkhorn optimal transport 建立切片间软对应，由软对应重建目标坐标并形成 alignment flow。Chamfer、局部平滑和近零散度三项无监督损失共同约束该流，连续配准相邻切片即可构造三维或时空重建。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>3d-OT</h1>
    <p>3d-OT: a deep geometry-aware framework for heterogeneous slices alignment of spatial multi-omics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03034-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 3d-OT 方法解读：把空间切片看成带分子属性的点云并学习可形变对齐流

### 一句话理解

3d-OT 将空间组学切片表示为二维点云：每个 spot 既有坐标，也有 RNA、染色质或蛋白特征。它先用 PointNet++ 风格的局部集合卷积学习同时保留空间几何和分子信号的表示，再用受空间候选约束的 Sinkhorn optimal transport 建立切片间软对应，由软对应重建目标坐标并形成 alignment flow。Chamfer、局部平滑和近零散度三项无监督损失共同约束该流，连续配准相邻切片即可构造三维或时空重建。

论文为 Dai 等发表于 *Nature Methods*（2026）的 “3d-OT: a deep geometry-aware framework for heterogeneous slices alignment of spatial multi-omics”，DOI `10.1038/s41592-026-03034-9`。工作区保存正文、补充、图像和本地源码；获取合同记录上游 `https://github.com/dbjzs/3d-OT` 的提交 `2c70d184fdc0df1f093814cb018b5d7addb21904`，包 `setup.py` 标记版本 0.1.1。源码目录当前没有独立 `.git`，因此该提交来自 acquisition 元数据，不能由当前目录重新执行 `git rev-parse` 独立验证；外层 PaperCode 提交不是上游代码提交。

### 1. 方法要同时解决三个任务

论文 Fig. 1a 将统一框架分成三个用途：

1. 单组学或多组学空间域识别；
2. 同平台、跨平台、跨模态或多组学切片对齐；
3. 将一系列相邻切片的两两映射串联成 3D/时空重建。

这三项任务共享几何感知表示，但输出不同。空间域识别对编码后的 spot 表示做聚类；切片对齐需要两个切片之间的 OT 计划与流；3D 重建则顺序应用多个 pairwise flow。不要把聚类标签本身误当作 OT 对应，也不要把连续切片堆叠等同于已经完成配准。

### 2. 输入：分子特征、二维坐标和局部空间图

每个切片至少需要：

- spot×feature 矩阵；RNA 常经归一化/HVG/PCA，染色质用 TF–IDF/LSI，ADT 用 CLR/PCA；
- `obsm["spatial"]` 中的二维坐标；
- 基于空间坐标建立的 kNN 图。

本地 `lib_3d_OT/utils.py` 中的 `prepare_data()`/图对象把表达特征、坐标、邻居索引和坐标差组织起来。对齐前的 `dpca()` 还对切片对做共同 SVD 表示，以减轻平台或批次差异。预处理不是无关紧要的前置工作：OT 的 cosine cost 直接来自这些表示，改变特征尺度或共同特征集合会改变对应关系。

### 3. PointNet++ Encoder 如何注入几何

#### 3.1 SetConv 不是普通 GCN

对中心 spot $i$ 及其邻居 $j$，模型把邻居分子特征与二维相对坐标拼接，形成局部集合：

$$
h_{ij}^{(l)}=[x_j^{(l)},\,p_j-p_i].
$$

随后逐点应用 1×1 convolution、归一化与 LeakyReLU，再在邻居维做 max pooling：

$$
x_i^{(l+1)}=\max_{j\in\mathcal N(i)}
\sigma(\operatorname{Norm}(W^{(l)}h_{ij}^{(l)})).
$$

三层 SetConv 将局部结构逐渐编码进更高维表示。几何不是只用于建边；坐标差在每层都与信号拼接，这是它相对只使用邻接矩阵的图编码器更显式的地方。

论文公式写 BatchNorm，而当前 `multi_modialty.py::SetConv` 和 `single_modialty.py::SetConv` 实际使用 `InstanceNorm2d(affine=True)`。两者在小批量和逐样本统计上不同，属于明确的实现差异，不能把论文符号直接当作当前运行行为。

#### 3.2 多组学融合与重建训练

多组学模式为两个模态分别运行编码器，再拼接并通过两层 MLP 得到融合表示 $Z_{\mathrm{fused}}$。两个模态专属 decoder 分别从融合表示重建输入：

$$
L_{\mathrm{enc}}=|X^{(1)}-\hat X^{(1)}|_2^2+
\|X^{(2)}-\hat X^{(2)}|_2^2.
$$

这样训练使融合空间不能只保留一个模态。`multi_modialty.py::extractModel` 直接实现双 encoder、`fusion_mlp`、双 decoder 和两项 MSE。单组学路径有独立实现，且当前源码在三层 SetConv 后加入 Transformer encoder，这一结构在主论文方法概述中没有同等清楚地展开。

#### 3.3 实际训练是两阶段

从源码调用关系看，编码器由 `train_graph_extractor()` 先以 MSE 训练并保存最佳 state dict；`UnifiedModel` 随后加载两个切片的已训练编码器，在 `get_encoder_results()` 中用 `torch.no_grad()` 提取特征，再训练 OT/flow 参数。也就是说当前实现不是从原始分子矩阵到 OT 损失完全端到端地联合更新全部参数，而是先表示学习、后配准。论文把它们呈现为统一框架，但未明确描述这一冻结式两阶段执行，因此复现必须跟随代码而不是仅凭框架图猜测。

### 4. SCOT：从分子相似度得到软对应

#### 4.1 特征 cost

两个切片的表示先分别做 min–max 归一化；`sinkhorn()` 内再按向量 L2 归一化并计算 cosine similarity：

$$
S_{ij}=\frac{z_i^\top z'_j}{\|z_i\|\|z'_j\|},
\qquad C_{ij}=1-S_{ij}.
$$

注意这里的 cost 来自分子/融合表示，不是纯坐标距离。坐标用于限制候选支持集。

#### 4.2 空间支持筛选

`ottools/ot.py::sinkhorn()` 对每个源 spot 先找目标切片中 `dist_k` 个欧氏近邻，再在这些候选中选 `sim_k` 个特征最相似 spot，将其余 OT kernel 位置置零。这一步将“允许去哪里”的几何约束与“更像谁”的分子相似度分开。

参数必须满足 `sim_k <= dist_k`，否则当前 `torch.topk` 会请求超过候选数的元素。论文 Methods 建议平滑结构使用约 50 个空间候选、复杂或分辨率差异大时使用 500–1,000 个，再保留 top 5；代码中的具体 notebook/入口参数应一并记录。

#### 4.3 非平衡式 Sinkhorn 更新

在候选支持上构造

$$K_{ij}=\exp(-C_{ij}/\epsilon)\,M_{ij},$$

其中 $M$ 为候选 mask。迭代缩放向量 $a,b$ 时使用

$$q=\frac{\gamma}{\gamma+\epsilon}$$

作为幂指数，最后

$$T=\operatorname{diag}(a)K\operatorname{diag}(b).$$

`UnifiedModel` 用 `exp(log_epsilon)`、`exp(log_gamma)` 保证这两个可学习参数为正。$\epsilon$ 控制熵平滑，$\gamma$ 调节边缘约束/更新强度；$T$ 是软运输权重，不是离散一对一匹配。

### 5. 从 OT plan 到 alignment flow

对每个源 spot，从运输计划取 top-$L$ 目标候选并对权重归一化，重建目标位置：

$$
y_i^*=\sum_{j\in\mathcal C_i}w_{ij}y_j,
\qquad
F_i=y_i^*-x_i.
$$

`reconstruction.py::get_s_t_neighbors()` 取候选，`reconstruct()` 做加权坐标和，`UnifiedModel.get_recon_flow()` 计算 $F$。因此输出 flow 表示在归一化二维坐标系中，源 spot 应移动到哪里才能与目标切片对应。

soft correspondence 对切片分辨率不同或不存在严格一对一关系更自然，但也意味着一个源 spot 的终点可落在多个目标 spot 的加权中心，而非某个实际观测点。后续标签转移若再用最近邻，会额外引入离散化步骤。

### 6. 三项自监督损失各管什么

#### 6.1 Chamfer reconstruction

重建点云 $Y^*=X+F$ 应覆盖真实目标点云 $Y$。对称形式为

$$
L_{\mathrm{ch}}=\frac1{|Y^*|}\sum_{y^*}\min_{y\in Y}\|y^*-y\|^2+
\frac1{|Y|}\sum_y\min_{y^*\in Y^*}\|y-y^*\|^2.
$$

当前 `chamfer_loss()` 通过 `backward_dist_weight` 控制第二项，既可对称，也可只用前向项；`threeDrecon.py` 的示例参数设为 1.0，而不同 notebook 可能不同。这比简单说“代码一定是单向 Chamfer”更准确。

#### 6.2 局部平滑

相邻源 spot 的 flow 不应剧烈跳变：

$$
L_{\mathrm{smooth}}=\frac1N\sum_i
\frac1{|\mathcal N(i)|}\sum_{k\in\mathcal N(i)}
\|F_i-F_k\|_1.
$$

它鼓励组织局部连续形变，但过强会把真实边界或局部复杂变形抹平。

#### 6.3 近零散度

论文希望减少不合理的局部膨胀/压缩。由于 spot 不规则分布，`Lattice` 先用逆距离平方权重把稀疏 flow splat 到规则网格，再用 `torch.gradient` 估计

$$
\nabla\cdot F=\frac{\partial F_x}{\partial x}+
\frac{\partial F_y}{\partial y},
$$

并最小化平均绝对散度。它只限制体积变化的总和，不要求每个邻居 flow 平行，因此比逐边平滑更允许旋转或剪切。但“零散度”是正则化偏好，不是组织真实变形必然满足的物理定律。

总损失为

$$
L=L_{\mathrm{ch}}+\lambda_sL_{\mathrm{smooth}}+
\lambda_dL_{\mathrm{div}}.
$$

当前 `compute_loss_unsupervised()` 直接实现这三项；权重、邻居数和 lattice resolution 来自运行参数而非包内唯一固定值。

### 7. 空间域识别与对齐共享表示，但不是同一优化目标

空间域任务使用单模态编码或多模态融合表示，再通过 R 的 `mclust` 聚类。类别数在 benchmark 中人工指定，论文也提到为捕获已知结构迭代测试 cluster 数。因此报告 ARI 等性能时必须区分“使用真值类别数”和完全无监督地决定类别数。

对齐任务则优化两个切片间的 flow。论文使用 Cell-Type Matching Index 检查匹配生物一致性，用 Chamfer distance 检查几何接近性。Chamfer 对具有相似整体形状的错误对应可能不敏感；论文 Discussion 也承认单独使用它难以区分部分方法，不能将较低 Chamfer 自动等价为更正确的细胞身份映射。

### 8. 3D 与时空重建的实际含义

`threeDrecon.py` 对相邻 AnnData 切片逐对执行共同表示、编码器训练和反向对齐，再把每个 pair 的 flow 串联。图中沿 z 轴分层显示的是连续 2D 配准结果；若切片来自不同发育时间，连线可被解释为候选时空对应。

但这种“trajectory”是由 pairwise soft correspondence 传递得到的，不是单细胞谱系追踪，也没有显式细胞增殖/死亡模型。误差会沿切片链累积；切片顺序、z 间距、方向选择和是否存在共同组织结构都是额外先验。论文 Fig. 6 展示心脏、血管、肾和卵巢等结构在两个胚胎阶段间的映射，支持其可视化与组织对应能力，而非证明每条连接具有克隆谱系含义。

### 9. 如何阅读主要结果

- Fig. 1 给出从 PointNet++ 表示到域识别、soft OT alignment 和 3D reconstruction 的总体框架。
- Fig. 2–3 比较单组学与多组学空间域，强调显式几何编码和融合表示对边界恢复的贡献。
- Fig. 4 用表观修饰与 RNA 的空间结构展示跨模态关联；单个 Garnl3 局部图是机制例子，不代表全基因普遍规律。
- Fig. 5 覆盖同平台、跨平台、跨模态和不同分辨率切片，结合几何与细胞类型指标比较对齐。
- Fig. 6 将多对相邻胚胎切片串联，展示 3D/发育对应及器官连接。

评价应结合正文统计、补充消融和视觉边界，而不能只凭单个裁剪图。工作区 `figure_analysis.md` 已对六个主图逐图记录证据。

### 10. 论文—代码映射与边界

| 机制 | 本地实现 | 判断 |
|---|---|---|
| 坐标逐层注入 SetConv | `multi_modialty.py`, `single_modialty.py` | Exact 主机制 |
| 归一化层 | 两文件均为 `InstanceNorm2d` | Partial：论文公式写 BatchNorm |
| 多组学编码、融合与双重建 | `multi_modialty.py::extractModel` | Exact |
| 两阶段训练 | `train_graph_extractor()` → `UnifiedModel` 的 `no_grad()` encoder | 代码明确；论文未清楚说明 |
| cosine cost、候选支持、Sinkhorn | `ottools/ot.py` | Exact 主机制；支持筛选是实现细化 |
| 软位置重建与 flow | `ottools/reconstruction.py`, `UnifiedModel.get_recon_flow()` | Exact |
| Chamfer + smooth + divergence | `ottools/losses.py`, `lattice.py` | Exact 主机制；Chamfer 对称权重可配置 |
| 3D 串联 | `threeDrecon.py` | Partial：提供 pairwise pipeline，运行脚本/数据参数仍需逐实验确认 |
| 论文全部 benchmark 复现 | notebooks、依赖代码和数据链接部分可用 | Partial：无锁文件，一些指标/参数在 notebook，GPU/R/mclust 环境未在本次重跑验证 |

### 11. 实际使用时要保存什么

- 每个模态的过滤、归一化、降维和共同特征集合；
- 空间坐标归一化、kNN 数、切片方向和 pair 顺序；
- 编码器 hidden size、epochs、seed 与最佳权重；
- `simk`、`otk`、top-$L$、$\epsilon$、$\gamma$、Sinkhorn iterations；
- 三项 loss 权重、Chamfer backward weight、smooth/divergence 邻居及网格大小；
- Python、PyTorch、PyG、CUDA、R/rpy2/mclust 版本；
- acquisition 记录的上游 commit，并注明当前源码目录不再含独立 Git 元数据。

### 证据入口

- 正文：`paper source/paper/vlm/paper.md`
- 补充：`output_paper_supp_md/paper_supp1/auto/paper_supp1.md`（另有 supp2/supp3 PDF）
- 主图：`paper source/paper/vlm/images/`
- 多/单模态编码与训练：`3d-OT/lib_3d_OT/multi_modialty.py`, `single_modialty.py`
- OT：`3d-OT/lib_3d_OT/ottools/ot.py`
- 重建与损失：`ottools/reconstruction.py`, `losses.py`, `lattice.py`
- 3D 串联：`3d-OT/lib_3d_OT/threeDrecon.py`
- 包元数据：`3d-OT/setup.py`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## 3d-OT: Deep Geometry-Aware Spatial Multi-Omics Alignment

**Paper**: "3d-OT: a deep geometry-aware framework for heterogeneous slices alignment of spatial multi-omics"
**Journal**: Nature Methods (2026)
**DOI**: 10.1038/s41592-026-03034-9
**Authors**: Bingjie Dai, Litai Yi, Peizhuo Wang, et al. (Yongchun Zuo lab)
**Code**: https://github.com/dbjzs/3d-OT

---

### Motivation & Novelty

#### Biological Problem

Spatial multi-omics technologies simultaneously measure transcriptomic, epigenomic, and proteomic information at spatially resolved locations within tissue sections. Understanding how these molecular layers interact — and how they change across tissue slices from different time points, technologies, or modalities — requires computational methods that can:
1. Identify biologically meaningful spatial domains using all available molecular information
2. Align heterogeneous slices that differ in resolution, technology platform, or measured modality
3. Reconstruct 3D spatiotemporal trajectories from 2D serial sections

#### Limitations of Existing Methods

**For spatial domain identification:**
- STAGATE (*Nature Communications* 2022), GraphST (*Nature Communications* 2023), SpaNCMG (*Briefings in Bioinformatics* 2024): Graph-based methods capture spatial proximity but not the full geometric distribution of spots. They treat spatial coordinates only as graph structure, not as geometric features.
- SpatialGlue (*Nature Methods* 2024), COSMOS (*Nature Communications* 2025): Multi-omics methods using multi-encoder GCN design. GCN frameworks may miss global geometrical features, leading to over-merged region boundaries.
- MISO: Requires H&E histology images, limiting applicability.

**For slice alignment:**
- SLAT (*Nature Communications* 2023): Cannot align multi-omics or cross-modal slices
- Harmony (*Nature Methods* 2019): Integration method adapted for alignment; lacks spatial geometry awareness
- PASTE (*Nature Methods* 2022): Gromov-Wasserstein OT for alignment; collapses on large datasets
- PASTE2 (*Genome Research* 2023): Partial alignment fix for PASTE; still no cross-modal support
- SANTO (*Nature Communications* 2024): Coarse-to-fine alignment; no multi-omics support

**Key gap**: No method provides a unified framework for both multi-omics domain identification and heterogeneous multi-modal slice alignment, nor handles nonrigid deformations across varying resolutions.

#### Unique Contributions

1. **First explicit geometric encoding for spatial omics**: PointNet++ (originally for 3D point cloud segmentation) is adapted to concatenate spatial (x,y) coordinates at every encoder layer — treating spots as geometric point clouds, not just graph nodes.

2. **First end-to-end multi-omics slice alignment**: SCOT module achieves cross-platform, cross-modal, and multi-omics alignment without requiring pre-computed fused representations from external methods.

3. **Chamfer distance as alignment evaluation metric**: Adapts a well-established point cloud metric (previously unused in spatial omics) to provide a geometry-aware evaluation that complements the microscopic Cell-Type Matching Index.

4. **Self-supervised zero-divergence constraint**: Adapted from 3D fluid dynamics (particle tracking, *NeurIPS 2024*), the splat-based divergence loss ensures biologically plausible, continuous alignment flows.

---

### Method Overview

3d-OT has two core modules trained sequentially:

#### Module 1: PointNet++ Encoder

Encodes each spot's neighborhood features augmented with explicit spatial coordinates. Three successive SetConv layers (each: Conv2d → InstanceNorm2d → LeakyReLU → MaxPool) extract local-to-global geometric features. For multi-omics data, two modality-specific encoders feed into an MLP fusion layer to produce a unified representation $Z_\text{fused}$. For single-omics, a Transformer is appended after the SetConv layers.

Trained with MSE reconstruction loss: decoders must reconstruct the original expression profiles from $Z_\text{fused}$.

#### Module 2: SCOT (Soft Correspondence OT)

Takes the learned representations from two slices and:
1. Computes pairwise cosine similarity $S_{i,j}$, yielding cost $C = 1 - S$
2. Solves entropy-regularized Sinkhorn OT with **learnable** $\epsilon$ (entropy strength) and $\gamma$ (convergence modulator)
3. Extracts top-$L$ candidate correspondences per source spot
4. Reconstructs estimated target positions as weighted sums
5. Optimizes three self-supervised losses: chamfer reconstruction, smoothness, and zero-divergence

See `doc_method.md` for full mathematical derivation.

---

### Evaluation

#### Datasets

**Spatial domain identification — single-omics:**
- Human DLPFC (12 slices, 10x Visium): layered cortex, 7 regions
- Human breast cancer (10x Visium): 20 annotated regions
- Mouse visual cortex (STARmap): 7 layers
- Mouse brain (P22) spatial ATAC-RNA-seq (Zhang et al. *Nature* 2023): 18 clusters

**Spatial domain identification — multi-omics:**
- Simulated data (5 parameter distributions, zero-inflated NB + NB)
- Human lymph node A1 (10x Visium RNA-protein, GEO GSE263617): 10 clusters
- Mouse brain (P22) spatial CUT&Tag-RNA-seq (H3K27ac, H3K4me3, H3K27me3)

**Slice alignment:**
- DLPFC slices 151673/151674 (within-platform)
- STARmap PLUS 8-month mouse brain (within-platform)
- E15.5 Stereo-seq mouse embryo (within-platform, 7 regions)
- seq-FISH E8.75 + Stereo-seq E9.5 mouse embryo (cross-platform)
- P22 mouse brain RNA + CUT&Tag vs. ATAC-RNA (cross-modal / multi-omics)

**3D reconstruction:**
- Stereo-seq E11.5–E16.5 mouse embryo (6 time points)

#### Metrics

- **Clustering**: NMI, ARI (supervised), Moran's I (unsupervised spatial autocorrelation)
- **Alignment**: Chamfer distance (geometric accuracy), Cell-Type Matching Index / CI (label-level accuracy)

#### Comparative Results

**DLPFC clustering**: 3d-OT outperforms all 7 methods across 12 slices. First method to achieve ARI > 0.70 on slices 151673/151674. ARI of 0.849 on slice 151671 (best reported).

**Multi-omics (simulated)**: Best across 6 supervised metrics in all 5 parameter configurations.

**Human lymph node**: Only method to identify the capsule region completely.

**Mouse brain (P22 CUT&Tag-RNA)**: Uniquely resolves L6a/L6b sublayer boundary and lateral septal nucleus — regions with similar transcriptional profiles that other methods merge. Discovers Garnl3 as a novel potential L6a marker, supported by H3K27ac/H3K4me3 epigenetic validation.

**Within-platform alignment (DLPFC, STARmap, Stereo-seq)**: Best chamfer distance and CI across all 3 platforms.

**Cross-platform alignment (seq-FISH vs Stereo-seq)**: 3d-OT successfully tracks neural crest nonrigid morphological deformations; all competing methods (SLAT, Harmony, PASTE, PASTE2) produce physically incorrect alignments.

**3D embryo reconstruction**: Successfully captures heart ring structure at E13.5, heart contraction E11.5→E14.5, liver divergence, and kidney/ovary emergence from urogenital ridge at E11.5–E12.5.

---

### Reproducibility

**Rating: 3/5**

#### Justification

The code is available on GitHub and the main library is reasonably organized. However, several factors reduce reproducibility:

**Positives:**
- GitHub repository with library structure (`lib_3d_OT/`)
- Documentation website (https://3d-ot.readthedocs.io/)
- Zenodo data deposit (doi:10.5281/zenodo.15089426)
- Fixed random seed (7) enforced throughout

**Challenges:**
- **Notebook-dependent**: Most dataset-specific preprocessing (HVG selection, epoch counts, parameter choices per dataset) lives in notebooks, not documented in the library. No unified config file.
- **Two-stage training not documented**: The critical dependency — train encoder first, then SCOT with frozen encoder — is not described in the paper Methods. New users must discover this from code.
- **R dependency**: mclust requires R + rpy2. The `mclust` R package must be installed separately.
- **Competitor benchmarks bundled**: Competing methods (COSMOS, PASTE, etc.) are included as modified local copies — version inconsistencies are possible.
- **Dataset preprocessing heterogeneity**: Different datasets use different combinations of HVG counts (3000 vs full matrix), PCA dimensions, epoch counts, and k values. These are in separate notebooks without clear mapping to paper figures.

#### Environment Setup

```bash
# Python 3.10.13 with conda/mamba
conda create -n 3dot python=3.10
pip install torch==2.2.0 torch_geometric
pip install scanpy anndata scipy scikit-learn squidpy rpy2 anndata
# R 4.3.1 with mclust
R -e "install.packages('mclust')"
```

Key versions: numpy 1.26.3, scipy 1.12.0, torch 2.2.0, torch_geometric 2.4.0, rpy2 3.5.11, mclust 6.1.1

#### Data Availability

All benchmark datasets available via Zenodo (doi:10.5281/zenodo.15089426) and individual accession codes listed in the paper Data Availability section (GEO GSE263617, AtlasXplore, CNGB MOSTA, etc.).

#### Common Pitfalls

1. **R_HOME not set**: `utils.py` tries to auto-detect R home via rpy2, but this may fail in conda environments. Set `os.environ['R_HOME']` explicitly before import.
2. **GPU memory**: Chamfer loss computed in 2048-chunk batches; large slices (>10000 spots) may need smaller chunks.
3. **Lattice grid mismatch**: Spatial coords normalized to [0,1] but Lattice grid spans [0,2π] — divergence loss magnitude depends on this mismatch; don't compare absolute divergence values across setups.
4. **Encoder must be trained before SCOT**: The paper does not state this. Always run `train_graph_extractor` first and load the returned `best_model` state dict before training SCOT.

#### Strengths and Weaknesses

**Strengths:**
- Modular design: domain identification and alignment are independent modules
- Strong empirical performance across diverse platforms and modalities
- Explainable alignment flow (can visualize F as vectors on tissue)
- Self-supervised alignment (no manual correspondences needed)

**Weaknesses:**
- Quadratic memory in chamfer loss (mitigated by chunking)
- Sequential per-pair training for 3D reconstruction (scales as O(T) for T time points)
- No batch correction for multi-omics representations across slices (acknowledged as future work)
- Single-omics and multi-omics models are completely separate code paths — model size differs substantially
- mclust R dependency adds significant complexity for Python-only users

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
