---
layout: default
permalink: /paper-atlas/spalp-fc1e2290/
title: "SpaLP"
nav: false
wide: true
description: "SpaLP 把空间组学中的图卷积压缩成一个非常简单的自编码器：先用二维坐标为每个细胞保存固定数量的邻居编号，再一次性 gather 邻居分子特征，按特征通道计算注意力并求和，最后重构原始表达。它避免保存 N\\times N 邻接矩阵，也不堆叠多层消息传递，因此能在单 GPU 上处理百万至千万级细胞。"
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
      <span>Representation Models</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>SpaLP</h1>
    <p>A lightweight, ultrafast and general embedding framework for large-scale spatial omics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.02.04.703814" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpaLP">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/dbjzs/SpaLP" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaLP">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaLP 方法解读：用邻居索引和局部池化处理百万级空间组学

### 一句话抓住核心

SpaLP 把空间组学中的图卷积压缩成一个非常简单的自编码器：先用二维坐标为每个细胞保存固定数量的邻居编号，再一次性 gather 邻居分子特征，按特征通道计算注意力并求和，最后重构原始表达。它避免保存 $N\times N$ 邻接矩阵，也不堆叠多层消息传递，因此能在单 GPU 上处理百万至千万级细胞。

### 1. 要解决的任务

高分辨率空间转录组和空间蛋白组常包含数十万到数百万个细胞。分析需要一个同时表达细胞分子状态和局部微环境的低维 embedding，以支持 niche clustering、表达重构、多切片整合、3D atlas 和跨平台标签迁移。

SpaLP 的设计优先级是规模与通用性：不为每个数据集设计复杂图网络，而是把任意预处理后的特征矩阵 $X\in\mathbb R^{N\times F}$ 和空间坐标作为输入。这里 $X$ 可以是 RNA、蛋白，或用户预先拼接的多模态特征。

### 2. 第一步：把空间图改写成邻居索引

对切片 $s$ 的第 $i$ 个细胞，用二维坐标查找空间近邻，并保存为

$$
I^{(s)}\in\mathbb N^{N_s\times K}.
$$

第 $i$ 行不是 $N_s$ 维 one-hot 邻接，而只是 $K$ 个整数索引。若 $K$ 固定，索引存储为 $O(N_sK)$，相对稠密邻接的 $O(N_s^2)$ 显著节省内存。

代码用 `scipy.spatial.cKDTree` 查询近邻（`SpaLP/SpaLP/utils.py:37-44`）。一个容易踩坑的细节是：函数向 KDTree 请求 `k` 个结果，然后删除第一列自身，因此实际返回的非自身邻居数是 `k-1`。调用者若想得到恰好 $K$ 个邻居，需要确认传入值和论文符号的约定。

`prepare_inputs()` 要求 AnnData 中存在 `obsm['spatial']` 和预处理特征 `obsm['feat']`，将二者转为设备上的 `Graph(features, neighbor_idx)`（`utils.py:18-61`）。因此归一化、HVG 选择、多模态拼接不在模型内部完成。

### 3. 编码：每个细胞先独立变换

设输入特征为 $x_i\in\mathbb R^F$。论文用一层 MLP 得到节点特征：

$$
z_i=\operatorname{ReLU}(W x_i+b).
$$

当前代码的 `LocalFeatureAggregation` 将输入投到 `2*out_channels`，而不是直接投到最终 embedding 维度：

$$
z_i\in\mathbb R^{2C}.
$$

对应 `MLP(in_channels, 2*out_channels, ReLU)`（`SpaLP/LP.py:51-65`）。这与论文把中间通道写成 $C$ 的简化方程存在维度差异；最终 `AttentivePooling` 再从 $2C$ 投到 $C$。

### 4. Gather：用整数索引构造局部张量

代码通过高级索引

$$
L_f[i,j,:]=z_{I[i,j]}
$$

把 $N\times 2C$ 节点特征展开成 $N\times K\times 2C$ 的局部特征张量。实现只是 `data[index]`（`LP.py:26-33`），没有图卷积框架的 edge list、scatter message passing 或邻接矩阵乘法。

随后代码在 gather 后的通道维使用 `BatchNorm1d`（`LP.py:55,67-69`）。它在单切片和多切片模式下都会执行，并非只为多切片对齐服务；多切片代码还是逐切片 forward，因此 batch statistics 也不是把所有切片一次性拼接后统一估计。

### 5. 局部注意力：每个通道独立选择邻居

对于中心细胞 $i$、邻居 $j$、通道 $c$，SpaLP 在邻居维归一化权重：

$$
a_{ijc}=\operatorname{softmax}_{j}(\ell_{ijc}).
$$

聚合后得到

$$
h_{ic}=\sum_{j=1}^{K}a_{ijc}L_{f,ijc}.
$$

不同于常见图注意力用一个标量控制整条邻居消息，这里每个特征通道都可以偏好不同邻居。当前代码先对局部特征做一个无 bias 的 `Linear(2C,2C)`，再在 `dim=1` 即邻居维 softmax；随后逐元素相乘并求和（`LP.py:36-49`）。论文公式看起来像直接对局部特征 softmax，代码则增加了可学习投影，这是重要的 paper-code 差异。

求和后的 $2C$ 向量还经过一个额外线性层映射为最终 $C$ 维 embedding。该投影位于 `AttentivePooling.mlp`，论文的直接加权求和表达式没有单独强调它。

### 6. 解码与训练目标

最终 embedding $h_i\in\mathbb R^C$ 通过单层 decoder 重构输入：

$$
\tilde x_i=\operatorname{ReLU}(W_dh_i+b_d),
$$

并最小化

$$
\mathcal L_{rec}=\frac{1}{NF}\sum_i\lVert x_i-\tilde x_i\rVert_2^2.
$$

`SpatialLocalPooling.forward()` 返回 reconstruction 和 embedding（`LP.py:82-96`）；`Train()` 使用 Adam、默认学习率 $10^{-3}$、MSE 和 200 epochs（`LP.py:99-125`）。论文对 8.4 million-cell atlas 使用 20 epochs，其余实验为 200 epochs（paper.md 第 299 行）。

这个目标鼓励 embedding 保存可重构的局部分子信号，但没有直接优化 Leiden clustering、ARI、批次混合或标签迁移。下游指标改善是实验结果，不是损失函数的显式保证。

### 7. 单切片与多切片在代码中有什么不同

论文 Methods 写出不同切片的索引矩阵和特征矩阵拼接，并用共享模型学习共同空间。当前代码的 `multi-slices` 模式并没有构造论文 Eqs. 2–3 的大拼接矩阵；它在每个 epoch 内遍历切片，对每张图分别 `zero_grad → forward → backward → step`（`LP.py:127-150`）。

因此共享的是模型参数，但每个切片产生一次独立优化步。这样确实能把不同切片映射到同一参数化空间，却不等价于一次 batch 中联合计算所有切片，也不会直接建立跨切片空间边。跨切片对齐来自共享权重、相似预处理和训练序列，而不是显式跨切片邻居。

### 8. “训练迭代扩大感受野”需要谨慎理解

论文文字和 Extended Data Fig. 1a 表示，多次 local weighting 的累积效应让信息向外扩展。但当前 `forward()` 只有一次 gather 和一次池化；无论训练 20、200 还是更多 epochs，某个样本在单次推断中的输出始终只直接依赖其固定一跳邻居。

训练迭代会改变共享权重，使模型从全部局部样本中学习统计规律，却不会像堆叠 GNN layer 那样把二跳、三跳节点加入同一次前向传播的计算图。因而 SpaLP 的实际优势是高效的一跳微环境编码，而不是在推断时拥有整图感受野。

### 9. 为什么它快，以及复杂度边界

主要张量是邻居索引 $N\times K$ 和 gather 后局部特征 $N\times K\times2C$。当 $K,C$ 固定时，模型计算和显存近似随 $N$ 线性增长。cKDTree 建图也避免了显式生成全距离矩阵。

但“线性”不表示常数成本为零：完整局部张量可能仍很大，BatchNorm 和 attention 都要访问它；高维输入先投到 $2C$，而 GPU 峰值还取决于 autograd、中间激活和数据拷贝。论文所有效率实验使用 A800 80 GB；对消费级 GPU 的可处理规模不能直接从 8.4 million-cell 结果外推。

### 10. 重构表达应如何解释

decoder 输出是从局部聚合 embedding 重构的分子特征。它可能平滑噪声并增强空间一致性，因此论文用 marker spatial pattern、Moran's I 和 SCimilarity embedding 比较原始与重构表达。

这不意味着重构值是新的实验测量，也不应把更平滑的图自动解释为更真实。重构目标本身偏好局部可预测信号，可能削弱孤立但真实的细胞状态；稀有 niche 的有效性仍需 marker、组织学和独立注释支持。

### 11. 跨平台迁移怎么做

论文先用少量多平台切片训练共享 SpaLP，冻结参数后对新平台生成 embedding，再以 cosine similarity 从参考细胞转移标签。代码将两边 embedding L2 归一化，计算完整相似度矩阵，选择最大相似度参考标签；还以 temperature $0.02$ 汇总类别概率并给出 confidence/entropy（`utils.py:288-317`）。

这是 nearest-reference label transfer，不是端到端分类器。它要求参考与新数据使用兼容的特征空间和基因/蛋白处理；若 gene panel 不一致，必须先做论文所述的 common-feature selection，而当前核心包不会自动解决。

### 12. 图 1–7 和 Extended Data 支持什么

- **图 1**：index matrix、local pooling、decoder、复杂度和应用总览，是理解方法最关键的图。
- **图 2**：模拟、乳腺癌、鼠脑和 CODEX spleen 的单样本 niche/reconstruction 比较。
- **图 3**：mouse pup、testis 和 spatial proteomics 展示复杂组织结构的局部解析。
- **图 4**：同平台与跨平台多切片整合，以及 2 million-cell CRC 中的稀有 niche。
- **图 5**：239 slices、8.4 million cells 的 mouse brain embedding 和 3D atlas。
- **图 6**：低质量 kidney cancer、gastric cancer 和 RCC RNA+protein 案例。
- **图 7**：冻结模型后的跨平台 zero-shot embedding 与 cosine label transfer。
- **Extended Data 1–8**：数据清单、重构/marker、proteomics、多组织细节、CRC 稀有 niche、brain atlas 和低质量样本补充证据。

本地 `paper.pdf` 共 44 页，主文 Methods、主图和 Extended Data 均在同一文件中。正文还引用 Supplementary Figures/Tables/Notes，但没有独立 supplementary PDF 存入工作区；涉及它们的细粒度指标不能声称已逐项本地复核。

### 13. 论文结果的适用边界

论文报告 SpaLP 在 1.35 million-cell mouse embryo 上约 47 seconds、在 8.4 million cells 上少于 4 minutes，并在 niche identification 中获得明显 ARI 改善。这些数字依赖作者硬件、预处理、特征数、$K$、embedding size 和计时口径；Methods 明确只统计 embedding generation，不含 Leiden clustering（paper.md 第 299 行）。

跨 20+ datasets、9 platforms 的结果说明方法具有广泛经验适用性，但“general framework”仍是空间组学证据下的结论。把 LP 推广到任意非空间图领域，需要重新定义邻居、特征与重构目标并重新验证。

### 14. 论文—代码对应程度

| 机制 | 对应程度 | 证据与边界 |
|---|---|---|
| cKDTree 邻居索引与 gather | Exact | `utils.py:37-61`; `LP.py:26-33` |
| 按通道 attention、加权和 | Partial | 核心一致；代码多一个 learned linear projection |
| encoder/decoder + MSE | Partial/Exact | 目标一致；代码中间维为 $2C$ 并有额外输出投影 |
| Adam、默认 200 epochs | Exact | `LP.py:99-125` |
| 多切片联合拼接 Eqs. 2–3 | Not found | 当前代码逐切片分别优化 |
| 多模态特征拼接 | External | 用户需在 `obsm['feat']` 中预先准备 |
| Leiden、Moran's I、完整 benchmark | External | 不在核心包中 |
| cosine 标签迁移 | Exact | `utils.py:288-317` |
| 全部论文结果重现 | Not rerun | 本次恢复未运行训练或 benchmark |

### 15. 最容易误解的四点

第一，SpaLP 不是 linear programming；LP 指 Local Pooling。第二，索引矩阵并不表示模型看见全图，每次前向仍是一跳邻域。第三，训练 epoch 增加不会像堆叠 GNN layer 那样扩展单样本感受野。第四，重构后空间图更平滑不自动等于生物学更真实，必须结合 marker、病理和独立注释验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaLP: A Lightweight, Ultrafast and General Embedding Framework for Large-Scale Spatial Omics Data

**Authors**: Bingjie Dai, Yuchao Liang, Litai Yi, et al.
**Journal**: bioRxiv (preprint), 2026
**DOI**: 10.64898/2026.02.04.703814
**Code**: https://github.com/dbjzs/SpaLP
**Data**: https://zenodo.org/records/18483604

---

### Motivation & Novelty

#### Biological Problem

High-resolution spatial omics technologies (MERFISH, CosMx, Xenium, Visium HD, Stereo-seq, CODEX) now generate datasets containing millions of cells with spatially resolved molecular profiles. A central analytical need is to produce cell embeddings that encode both molecular identity and spatial neighborhood context, enabling tasks such as niche identification, expression imputation, multi-slice integration, and cross-platform generalization.

#### Limitations of Existing Approaches

Graph Neural Networks (GNNs) are the dominant paradigm for spatial embedding but face three fundamental limitations at scale:

1. **Memory**: The adjacency matrix scales quadratically ($O(N^2)$) or requires complex sparse formats, making million-cell datasets impractical on a single GPU.
2. **Speed**: Message passing over large graphs is computationally expensive. Methods like NicheCompass (Nat Genet, 2025) take >4 hours for 1.35M cells; HERGAST (Nat Commun, 2025) requires >1200GB CPU memory.
3. **Graph integrity**: Sampling strategies (mini-batch, DIC) that mitigate memory issues destroy global graph structure, disrupting the continuous spatial information needed for biological interpretation.

BANKSY (Nat Genet, 2024) avoids GNNs but is still slower (~30 min for 1.35M cells) and lacks the embedding framework needed for tasks like multi-slice integration or zero-shot generalization.

#### Unique Contributions

SpaLP introduces the **Local Pooling (LP)** framework with three key innovations:

1. **Neighbor index matrix**: Replaces adjacency with a dense integer tensor $(N \times K)$ that scales linearly with cell count. No sparse operations needed.
2. **Local attention pooling**: Learns per-channel attention weights over $K$ spatial neighbors, aggregating neighborhood information without message passing.
3. **Full-graph processing**: The index matrix enables processing entire tissue slices (millions of cells) without sampling, preserving global spatial structure.

The framework achieves up to **300-fold speedup** over GNN methods while improving accuracy (>30% ARI increase in niche identification benchmarks).

---

### Method Overview

SpaLP is a spatial autoencoder that learns cell embeddings by reconstructing gene/protein expression from neighborhood-aggregated representations.

**Pipeline**:
1. **Preprocess**: Log-normalize, z-score scale, (optional) HVG selection
2. **Build index matrix**: KNN from spatial coordinates via cKDTree
3. **Encode**: MLP projects features to latent space → gather neighbors → BatchNorm → local attention pooling → embedding
4. **Decode**: Linear + ReLU reconstructs expression
5. **Train**: MSE reconstruction loss with Adam optimizer
6. **Downstream**: Leiden clustering, UMAP, multi-slice integration, label transfer

The architecture is deliberately minimal — a single MLP layer, one round of neighbor aggregation, one attention pooling step, and one decoder layer. This simplicity is the source of its speed: the entire model has far fewer parameters and computations than multi-layer GNNs.

For detailed equations and code mapping, see doc_method.md and doc_code.md.

---

### Evaluation

#### Datasets

Over 20 datasets spanning 9 technology platforms (MERFISH, CosMx, Xenium, Visium HD, Stereo-seq, Stereo CITE-seq, STARmap PLUS, CODEX, MERSCOPE), covering:
- Simulated data (640K cells)
- Single tissues: breast cancer (167K), mouse brain (48K), mouse spleen (80K×3), mouse embryo (1.35M), mouse testis (198K), kidney cancer (1.24M), gastric cancer (696K)
- Multi-slice: MERSCOPE brain (734K, 9 slices), STARmap brain (423K, 3 slices), VisiumHD tonsil (1.22M, 2 slices), CODEX tonsil (1.40M, 3 slices)
- Cross-platform: mouse brain (3 platforms), colorectal cancer (2M, 5 slices, 3 platforms)
- Whole-brain atlas: MERFISH 8.4M cells, 239 sections
- Multi-omics: RCC (465K cells, RNA + protein)

#### Compared Methods

| Method | Journal | Year | Type |
|---|---|---|---|
| NicheCompass | Nat Genet | 2025 | GNN-based, niche quantification |
| HERGAST | Nat Commun | 2025 | GNN with DIC strategy |
| BANKSY | Nat Genet | 2024 | Non-GNN spatial embedding |
| SpatialGlue | Nat Methods | 2024 | Spatial multi-omics (GNN) |
| COSMOS | Nat Commun | 2025 | Spatial multi-omics integration |
| SCimilarity | Nature | 2025 | Omics foundation model (used for evaluation) |

#### Key Results

**Computational efficiency**:
- 1.35M cells (mouse embryo): 47 seconds (vs. BANKSY 30 min, NicheCompass 4+ hours, HERGAST infeasible at >1200GB CPU)
- 8.4M cells (239 brain sections): 3 min 40 sec on a single GPU (24GB VRAM)

**Niche identification** (ARI):
- Simulated 640K: ARI = 0.9 (best among all methods)
- >30% average ARI increase across simulated and realistic settings
- Correctly identified all three breast cancer regions (ER+, TN, TP) — only method to do so
- Resolved ring-like spermatogenesis gradient in mouse testis (Stereo-seq)

**Multi-slice integration**:
- Superior spatial conservation metrics (CAS, GCS) indicating better preservation of spatial structure
- Cross-platform integration of 2M colorectal cancer cells (3 platforms) in 57 seconds
- Detected rare niche (0.1% of cells) — intestinal neuron-enriched region in CRC

**Cross-platform generalization**:
- Pre-trained on 3 platforms (CosMx, MERFISH, STARmap PLUS), frozen parameters
- Zero-shot inference on unseen MERFISH and Stereo-seq brain slices
- High-quality label transfer via cosine similarity

#### Metrics Used

- **Supervised**: ARI, NMI, Homogeneity, Completeness, V-measure, F1-score
- **Spatial**: CAS (Cell-type Affinity Similarity), GCS (Graph Connectivity Similarity), Moran's I
- **Integration**: MLAMI, PCR (batch correction), iLISI/cLISI
- **Reconstruction**: Spatial autocorrelation score via Squidpy

---

### Reproducibility

#### Rating: 3.5 / 5

**Strengths**:
- Code is public (MIT license) and installable via pip
- All 25 benchmark datasets are available on Zenodo
- Jupyter tutorials are available at ReadTheDocs
- Hardware requirements clearly documented (GPU memory table per dataset)
- Simple architecture with few hyperparameters

**Weaknesses**:
- **Paper-code discrepancies**: Multiple divergences between paper equations and implementation (see doc_code.md): attention mechanism uses learned projection vs. paper's direct softmax; multi-slice training iterates per-slice vs. paper's batch concatenation; MLP dimension is 2×C vs. paper's C. These make it difficult to reproduce results from the paper's method description alone.
- **Preprocessing ambiguity**: Paper says 5000 HVGs, README says 2000/3000. Z-score scaling step omitted from paper Methods.
- **No config files**: Hyperparameters (K, C, epochs) are not documented per-experiment in the repo — must be inferred from README tables and paper text.
- **Evaluation code not included**: Only the model is packaged; benchmark scripts, metric computation, and visualization code are not in the repository (referenced to ReadTheDocs tutorials).
- **Single hardware configuration**: All experiments on A800-80GB; no guidance for adapting to consumer GPUs.

#### Practical Notes

- **Environment**: Python 3.10, PyTorch 2.2.0, CUDA required for large datasets
- **Key hyperparameters**: K (neighbors, 3-8), C (embedding dim, typically 64), epochs (200), lr (0.001)
- **Common pitfall**: The `k` parameter in `build_neighbor_idx` includes self in KNN query, then removes self — actual neighbors = k-1
- **Memory**: GPU memory proportional to N × K × 2C × 4 bytes (float32)
- **Data format**: AnnData with `obsm['spatial']` and `obsm['feat']` (preprocessed features)

---

### Strengths and Weaknesses

#### Strengths

1. **Dramatic computational efficiency**: Orders of magnitude faster than GNN competitors, enabling single-GPU processing of million-cell datasets
2. **Full-graph processing**: No sampling artifacts that plague GNN methods at scale
3. **Versatile**: Works across transcriptomics and proteomics, single- and multi-slice, within- and cross-platform
4. **Simple architecture**: Easy to understand, implement, and modify
5. **Strong empirical results**: Consistently outperforms baselines across diverse benchmarks

#### Weaknesses

1. **Single-hop aggregation**: Only one round of neighbor aggregation — multi-layer GNNs capture higher-order spatial patterns (e.g., tissue-level organization beyond immediate neighbors) through stacked message-passing layers. The paper argues that training iterations expand information outward (Extended Fig. 1a), but this is through gradient updates, not receptive field expansion within a single forward pass
2. **Paper-code gap**: Significant discrepancies between described and implemented method weaken scientific rigor
3. **No theoretical analysis**: Why local pooling works as well as message passing is not formally justified
4. **Limited to spatial data**: While paper claims generality, all experiments are spatial omics — extension to non-spatial domains is speculative
5. **Autoencoder limitation**: Reconstruction-based objective may not optimize for all downstream tasks equally (e.g., clustering vs. imputation vs. integration may benefit from different objectives)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
