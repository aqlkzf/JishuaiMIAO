---
layout: default
permalink: /paper-atlas/spamosaic-504843a9/
title: "SpaMosaic"
nav: false
description: "SpaMosaic 处理的不是每个切片都同时测到所有组学的理想数据，而是更常见的马赛克式观测：有的切片有 RNA+ATAC，有的只有 RNA，有的有 RNA+蛋白，另一些又来自不同发育阶段或实验技术。目标是把这些切片放进同一个低维空间，同时保留空间邻域、消除切片批次差异，并给缺失模态提供可解释的邻居插补。"
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
      <span>Nature Genetics · 2026</span>
    </div>
    <h1>SpaMosaic</h1>
    <p>Mosaic integration of spatial multi-omics with SpaMosaic</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-026-02573-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaMosaic：空间多组学“马赛克”如何拼成同一张图

SpaMosaic 处理的不是每个切片都同时测到所有组学的理想数据，而是更常见的**马赛克式观测**：有的切片有 RNA+ATAC，有的只有 RNA，有的有 RNA+蛋白，另一些又来自不同发育阶段或实验技术。目标是把这些切片放进同一个低维空间，同时保留空间邻域、消除切片批次差异，并给缺失模态提供可解释的邻居插补。

本文解读以发表版论文 OCR 文本、主图与扩展图，以及本地官方代码快照 `SpaMosaic/`（commit `cc1336755de8d1ddd1337b3cd67c9d41a61c2cb4`，包版本 1.0.3）为证据。代码目录 `code/` 和根目录 `spamosaic/` 的包内容与该快照相同，但只有 `SpaMosaic/.repo_source` 保存了仓库与提交 provenance，因此下文以它为规范实现。行号会随文件变化，定位时应优先使用函数名。

### 1. 先看清数据结构：真正的桥是“同一批 spot 的共测模态”

设模态为 $m$，切片或批次为 $b$，观测矩阵为 $X_b^m$。不是每个 $(b,m)$ 都存在。一个切片若同时测到两个或更多模态，代码称其为 `bridge_batch`；只有一个模态的切片称为 `non_bridge_batch`。桥接切片里的同一个 spot 在不同模态之间天然配对，这给出了跨模态对齐的正样本。单模态切片没有这种监督，不能强行制造跨模态配对，只能借助同模态跨切片图和重建约束进入共同空间。

这里还有一个容易忽略的可识别性条件：所有模态必须能通过“哪些模态曾在同一切片共测”形成连通图。`SpaMosaic.check_integrity()` 会检查这个模态重叠图；若出现完全不与其他模态桥接的孤立组分，程序直接报错。也就是说，算法可以补齐不完整矩阵，但不能在没有任何桥接证据时凭空确定两个模态空间的相对方向。

### 2. 模态内预处理：先统一尺度，再谈整合

论文与 `spamosaic/preprocessing.py` 对不同模态采用不同变换：

- RNA：库大小归一化、对数变换，默认选 5,000 个高变基因，再做不含 TF-IDF 的 LSI/SVD 表示。
- 染色质或组蛋白标记：TF-IDF 后选默认 100,000 个高变特征，再做 LSI/SVD。
- 蛋白：CLR 归一化。
- 同一模态跨批次还可先用 Harmony/Seurat 做模态内批次校正。

因此模型输入并非直接把原始 count 混在一起，而是每种模态各自得到适合该测量机制的低维特征。模态之间也不是共享一个编码器；每个模态都有自己的 WLGCN 和解码头，跨模态一致性由桥接 spot 的对比损失建立。

### 3. 每个模态的一张复合图：空间边与跨切片 MNN 边

对每个模态 $m$，SpaMosaic 合并两类边：

$$
A^m=A_{\mathrm{intra}}^m+w_gA_{\mathrm{inter}}^m.
$$

$A_{\mathrm{intra}}^m$ 是每张切片内部按空间坐标构建的 kNN 图，默认 $k=10$；它表达“组织中彼此靠近”。$A_{\mathrm{inter}}^m$ 则在拥有同一模态的不同切片之间，根据预处理特征寻找互为近邻（MNN）的 spot；它表达“不同切片中分子状态相似”。代码在 `framework.py` 中把各切片空间图组成块对角矩阵，再加入 `MNN.py` / `build_graph.py` 生成的跨切片边。

论文取 $w_g=0.8$。按公式和代码的实际乘法，它是给**跨切片 MNN 边**乘 0.8，而切片内空间边权重为 1；因此准确说法是跨切片边相对下调，而不是空间边被乘 0.8。MNN 的基础邻居数默认 10；当两批 spot 数量差异较大时可启用不对称邻居数，阈值为 0.8，也可用 isolation forest 去除异常 MNN。需要区分论文提供的能力与默认运行路径：本地 `SpaMosaic.__init__()` 中 `inter_auto_knn=False`、`rmv_outlier=False`，两项都不是无条件开启。

### 4. WLGCN：不用深层消息传递，而是把 0 到 K 跳一起交给 MLP

对加入自环并对称归一化的邻接矩阵

$$
\hat A=\tilde D^{-1/2}(A+I)\tilde D^{-1/2},
$$

WLGCN 依次计算 $X,\hat AX,\hat A^2X,\ldots,\hat A^KX$，拼接后送入模态专属 MLP：

$$
\tilde X^m=[X^m\|\hat A^mX^m\|\cdots\|(\hat A^m)^KX^m],\qquad
Z^m=f_{\mathrm{MLP}}^m(\tilde X^m).
$$

这样每个 spot 同时保留自身特征、近邻平均和更远邻域信息，避免把多个 GCN 层简单堆叠造成过度平滑。`architectures/wlgcn.py` 的默认配置使用两次传播（$K=2$）、128 维隐藏层和 32 维输出，配合 LeakyReLU、BatchNorm、0.2 dropout；输出向量做 L2 归一化，因此后续点积就是余弦相似度。编码器旁边还有线性解码器，从 $Z^m$ 重建该模态输入特征。

### 5. 两种样本、两种约束共同训练

#### 5.1 桥接切片：对比学习决定跨模态坐标系

在桥接切片中，同一 spot 的不同模态嵌入是正样本，不同 spot 是负样本。温度参数默认 $\tau=0.01$。`loss.py` 实现的不只是一对模态的 NT-Xent，而是可接受两个以上视图的扩展版本：每个模态都要与同一 spot 的其他模态接近，同时与批内其他 spot 分开。这个约束提供“竖向”跨模态对齐。

#### 5.2 单模态切片：重建让无配对样本仍参与训练

没有跨模态配对的切片不参与上述对比项。`train_utils.train_model()` 对它们计算解码重建 MSE，使编码仍需保留本模态信息；与此同时，同模态的跨切片 MNN 边已经把它们接到桥接切片上。两者合起来，单模态切片就能沿着“同模态跨批次连接 → 桥接切片跨模态配对”进入统一空间。

总损失在实现中是桥接批次对比损失的平均与非桥接批次重建损失的平均之和。代码还支持图重建项，但 `SpaMosaic.train()` 的默认 `w_rec_g=0`，所以默认路径是特征重建，并不能把图重建描述成每次训练都发生。优化器为 Adam，默认学习率 0.01、weight decay $5\times10^{-4}$、训练 100 epoch。

### 6. 推断与插补：统一嵌入是模型输出，缺失表达是邻居估计

`infer_emb()` 对一个 spot 已观测到的多个模态嵌入默认取等权平均，得到统一 32 维表示。论文公式可写成带 $w_m$ 的加权组合，但当前代码用 `np.mean`，没有学习模态权重；这是论文一般表达与公开实现之间的明确边界。

`impute()` 不是训练一个生成式解码器来“预测”缺失模态。若目标切片缺少模态 $m_t$，代码先在统一嵌入中寻找已测 $m_t$ 的 spot，取默认 10 个近邻并平均其真实 $m_t$ 特征。若目标 spot 同时有多个已测模态，代码分别以这些模态的嵌入查找，再对多条插补结果取平均。因此插补质量依赖共同空间中确实存在可比邻居，也受参考批次覆盖范围限制；对参考数据从未出现的状态，它没有外推保证。

### 7. 图应当怎样读

Figure 1 是整套方法的证据地图：左侧是模态覆盖不完整的多个切片；中间每个模态各建“切片内空间边 + 切片间 MNN 边”的图并送入模态专属 GNN；桥接切片做跨模态对比，单模态切片做重建；右侧得到整合嵌入、空间域和缺失模态插补。沿图从左到右读，关键不是把缺失块先填上，而是先利用真实共测块确定坐标系，再让单模态块通过图与重建进入该坐标系。

后续主图从不同难点验证这条链路。Figure 2 用模拟数据分别改变空间因子、非空间因子与缺失模式，检验整合是否保留生物结构而非只追求批次混合。Figure 3 在出生后小鼠脑的 RNA、ATAC 和组蛋白标记马赛克中，同时展示空间域与跨模态插补。Figure 4 把不同技术、发育阶段和分辨率的小鼠脑数据放在一起，重点检验跨技术/跨尺度连接。Figure 5 扩展到胚胎图谱的七张切片、五种模态和四种技术，说明模态桥接图连通时可以沿多跳关系整合，而不要求每对模态直接共测。扩展图补充参数、消融和更细的结果；它们支持适用范围，但不能消除“桥接连通”和“参考状态覆盖”两个结构性前提。

### 8. 论文机制与本地代码的对应边界

| 机制 | 直接代码入口 | 判断 |
|---|---|---|
| 空间 kNN 与跨切片 MNN 复合图 | `spamosaic/framework.py`, `build_graph.py`, `MNN.py` | Exact；`w_g` 实际乘在 MNN 边上 |
| $0\ldots K$ 跳拼接的 WLGCN | `spamosaic/architectures/wlgcn.py` | Exact |
| 桥接 spot 多模态对比 | `spamosaic/loss.py`, `train_utils.py` | Exact；代码扩展到多于两模态 |
| 单模态批次特征重建 | `spamosaic/train_utils.py` | Exact；图重建默认关闭 |
| 多个已测模态合并为统一嵌入 | `spamosaic/framework.py::infer_emb` | Partial；实现为等权均值，不学习 $w_m$ |
| 统一空间 kNN 插补 | `spamosaic/framework.py::impute` | Exact；属于邻居平均而非生成模型 |
| 自动不对称 MNN、异常边过滤 | `spamosaic/framework.py` | 可选能力；默认均关闭 |

### 9. 复现时最重要的检查清单

1. 先画出“批次 × 模态”覆盖表，并确认模态共测图连通；不连通就不是调参能够解决的问题。
2. 保存每种模态预处理后的特征维度、空间坐标单位和 spot 顺序，避免图节点与矩阵行错位。
3. 分开报告切片内空间边、切片间 MNN 边和可选异常边过滤，尤其不要把 $w_g=0.8$ 的作用对象写反。
4. 同时评估生物结构保留与批次混合；仅凭 UMAP 混合良好不能证明正确整合。
5. 插补验证应遮蔽真实已测模态，并与简单同模态邻居基线比较；不能把可视化平滑当成定量准确。
6. 固定官方快照 commit `cc1336755de8d1ddd1337b3cd67c9d41a61c2cb4` 和包版本 1.0.3。本文确认了静态代码—论文机制映射，但没有在当前工作区重跑全部数据集、GPU 训练或论文数值，因此不声称逐图数值复现。

SpaMosaic 最核心的思想可以压缩成一句话：用**同模态跨切片的图边**传递横向信息，用**桥接切片的同 spot 对比**确定纵向模态坐标，再用**单模态重建**保住没有配对的样本信息。它能处理“缺块”的马赛克，但证据链必须是连通的。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaMosaic: Mosaic Integration of Spatial Multi-Omics

**Paper**: Mosaic integration of spatial multi-omics with SpaMosaic
**Authors**: Xuhua Yan, Zhaoyu Fang, Kok Siong Ang, et al.
**Journal**: Nature Genetics (2026). DOI: 10.1038/s41588-026-02573-3
**Code**: https://github.com/JinmiaoChenLab/SpaMosaic

---

### Motivation & Novelty

Spatial multi-omics technologies can profile RNA, chromatin accessibility, histone modifications, and proteins from tissue sections, but acquiring all modalities from a single section is technically challenging. In practice, different sections are profiled with different subsets of modalities, creating a "mosaic" data matrix with systematic missing entries. Integrating these heterogeneous datasets requires simultaneously solving modality alignment (vertical), batch correction (horizontal), and missing modality imputation — all while preserving spatial tissue architecture.

Existing methods address only subsets of this problem:
- **Single-cell mosaic integration** methods (Cobolt, Genome Biol 2021; scMoMaT, Nat Commun 2023; StabMap, Nat Biotechnol 2024; MIDAS, Nat Biotechnol 2024; CLUE/scGLUE, Nat Biotechnol 2022; UINMF, Nat Biotechnol 2022; MultiVI, Nat Methods 2023) ignore spatial information entirely
- **Spatial integration** methods (BANKSY, Nat Genet 2024; CellCharter, Nat Genet 2024) handle only same-modality or fully-paired settings
- **SpatialGlue** (Nat Methods 2024) requires all modalities measured on every section

SpaMosaic is the first method to address the full spatial mosaic integration problem. Its key contributions:
1. A heterogeneous graph combining spatial proximity (intra-section kNN) with omics similarity (inter-section MNN), weighted to favor the more reliable spatial signal
2. A contrastive learning framework that generalizes to N≥2 modalities, with bridge sections providing alignment and test sections receiving reconstruction-only training
3. Cross-modal imputation via kNN in the aligned latent space, enabling complete multi-omics profiles for all spots

---

### Method Overview

SpaMosaic operates in five stages:

1. **Preprocessing**: Modality-specific normalization (log-norm for RNA, TF-IDF+LSI for epigenome, CLR for protein), feature selection, SVD/PCA to 50 dimensions, and Harmony batch correction

2. **Graph construction**: Per-modality graphs combining spatial kNN edges (intra-section, $k=10$) with MNN edges (inter-section, $k_0=10$), merged as $A^m = A^{\text{intra}} + 0.8 \cdot A^{\text{inter}}$. Optional asymmetric $k$-adjustment for imbalanced sections and Isolation Forest outlier removal

3. **WLGCN encoding**: Weighted Light GCN with $K=2$ hops concatenates multi-scale neighborhood features, followed by MLP projection to 32-dim L2-normalized embeddings. Each modality has its own encoder

4. **Contrastive + reconstruction training**: Bridge sections (≥2 modalities) receive NT-Xent contrastive loss ($\tau=0.01$) to align modality embeddings; test sections (1 modality) receive MSE reconstruction loss. Adam optimizer, lr=0.01, 100 epochs

5. **Inference + imputation**: Per-modality embeddings are averaged into a unified representation for clustering. Missing modalities are imputed via kNN in the aligned latent space

See doc_method.md for mathematical details and doc_code.md for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Sections | Modalities | Technology | Spots |
|---|---|---|---|---|
| Simulated | 3 per set × 5 sets × 3 seeds | RNA + protein | Synthetic (ggblocks) | 1,296/section |
| Postnatal mouse brain (spRA+spRH) | 4 | RNA, ATAC, H3K4me3, H3K27me3, H3K27ac | Spatial RNA-Epigenomics | ~3,000-5,000/section |
| Embryonic mouse brain (Misar+Stereo) | 6 | RNA, ATAC | Misar-seq + Stereo-seq | ~5,000-20,000/section |
| Mouse embryo atlas | 7 | RNA, ATAC, H3K4me3, H3K27ac, protein | 4 technologies | ~2,000-10,000/section |
| Human lymph node + tonsil | Multiple | RNA, protein | Visium + CITE-seq | Variable |
| Cross-technology (Visium HD + Visium + Mux-seq) | Multiple | RNA | Different spatial platforms | Up to 800k+ spots |

#### Metrics

- **Spatial domain identification**: ARI (Adjusted Rand Index)
- **Spatial continuity**: PAS (percentage of spots differing from ≥6/10 spatial neighbors), CHAOS (average minimal intra-cluster spatial distance)
- **Batch integration**: graph iLISI (0=separated, 1=mixed)
- **Modality alignment**: FOSCTTM (fraction of samples closer than true match), matching score (MNN-based), label transfer F1

#### Key Results

- **Simulation**: SpaMosaic achieves highest ARI across all 5 parameter sets (mean ARI ~0.95), outperforming all 7 compared methods. Best spatial continuity (lowest PAS and CHAOS) and modality alignment (F1 ≈ 0.93-0.95)
- **Postnatal mouse brain**: Successfully integrates 5 epigenomic modalities across 4 sections, identifying 10 spatial domains consistent with known brain anatomy. Imputed GAS/CSS profiles show strong correlation with measured values
- **Cross-technology**: Handles sections with vastly different spot counts (Visium HD ~800k vs Visium ~3k) via asymmetric MNN
- **Ablation**: Spatial information contributes significantly — SpaMosaic (nonspatial) shows degraded performance, confirming the value of the spatial graph

#### Compared Methods

| Method | Journal | Year | Spatial? | Mosaic? |
|---|---|---|---|---|
| CLUE/scGLUE | Nat Biotechnol | 2022 | No | Yes |
| Cobolt | Genome Biol | 2021 | No | Yes |
| scMoMaT | Nat Commun | 2023 | No | Yes |
| StabMap | Nat Biotechnol | 2024 | No | Yes |
| MIDAS | Nat Biotechnol | 2024 | No | Yes |
| UINMF | Nat Biotechnol | 2022 | No | Yes |
| MultiVI | Nat Methods | 2023 | No | Yes |
| BANKSY | Nat Genet | 2024 | Yes | No |
| CellCharter | Nat Genet | 2024 | Yes | No |

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Complete open-source implementation with pip-installable package
- Comprehensive documentation with tutorials for mosaic, vertical, horizontal integration and imputation
- All datasets publicly available (GEO, Zenodo, 10x Genomics)
- Deterministic training (`torch.use_deterministic_algorithms(True)`)
- Default hyperparameters match paper exactly

**Weaknesses**:
- MClust clustering requires R + rpy2 (cross-language dependency)
- Preprocessing is external to the package — users must run modality-specific pipelines separately
- Some paper claims don't exactly match code (weighted embedding merge described as learned $w_m$ but implemented as equal-weight mean; spatial graph described as using Annoy but uses sklearn ball_tree)
- Isolation Forest contamination parameter differs from paper description

**Practical notes**:
- GPU recommended but CPU supported
- Key dependencies: torch_geometric, torch_scatter (version-sensitive), harmony-pytorch, annoy, hnswlib
- For large datasets (>8000 spots/section), mini-batch contrastive learning is automatically enabled
- The `w_g=0.8` default works well across diverse datasets; the authors recommend this as a starting point

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
