---
layout: default
permalink: /paper-atlas/smart-2b13389b/
title: "SMART"
nav: false
wide: true
description: "SMART 把每个空间 spot（或分割后的单细胞）视为图节点：GraphSAGE 沿空间近邻传播信息，MNN 三元组损失再把“空间上较远、分子特征却相似”的节点拉近。多个组学各自编码后拼接，并通过一个全连接层形成统一嵌入。SMART-MS 在此基础上先按切片做 Harmony 校正，再用跨切片 MNN 三元组连接对应结构。 本文的论文证据来自本工作区 outputpapermd/PMC13031631/paper."
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>SMART</h1>
    <p>SMART: spatial multi-omic aggregation using graph neural networks and metric learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-70821-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SMART">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Xubin-s-Lab/SMART-main" target="_blank" rel="noopener noreferrer" aria-label="Open code for SMART">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SMART 方法中文解读：空间邻域与远距离分子相似性的联合约束

### 一句话抓住方法

SMART 把每个空间 spot（或分割后的单细胞）视为图节点：GraphSAGE 沿空间近邻传播信息，MNN 三元组损失再把“空间上较远、分子特征却相似”的节点拉近。多个组学各自编码后拼接，并通过一个全连接层形成统一嵌入。SMART-MS 在此基础上先按切片做 Harmony 校正，再用跨切片 MNN 三元组连接对应结构。

实现证据来自固定快照 `SMART-main/`（来源记录 commit `75676546a66d48a7ebfd7c5f3a2758a4c538fcfc`）。两者并不完全等价，尤其要注意本文最后的复现边界。

### 1. SMART 要解决什么问题

空间多组学同时给出 RNA、蛋白或染色质可及性以及二维坐标。只拼接分子特征会忽略组织拓扑；只做空间平滑又可能把同一细胞类型的离散结构拆开，或抹去真实边界。SMART 因而同时使用两类关系：

1. **局部空间关系**：坐标上的 KNN 图规定 GraphSAGE 从哪些邻居聚合。
2. **远距离分子关系**：各模态 PCA 空间中的互为近邻（MNN）形成 anchor–positive；同一模态中较远的节点形成 negative。

这解释了 SMART 的设计偏好：它尤其适合组织中重复出现、空间不连续的相同生态位；但论文也承认，对于连续渐变区域，它不一定像强空间平滑方法那样产生平滑边界。

### 2. 从输入到统一嵌入

#### 2.1 各模态独立预处理

- RNA：过滤低频基因，选择 3000 或 5000 个高变基因，按 spot 总量归一到 10,000，`log1p` 后标准化。
- ATAC：TF–IDF、总量归一到 10,000、对数变换和标准化。
- 蛋白：CLR 变换后标准化。

每个模态再独立 PCA。论文把第 $i$ 个模态的降维特征记作 $X_i\in\mathbb{R}^{m\times d_i}$，其中 $m$ 是共同空间单位数。教程通常对 RNA/ATAC 取 30 个主成分，蛋白维数随数据而定；这些是 notebook 级设置，不是 `utils.pca()` 的默认值（默认 10）。

#### 2.2 空间图

用坐标 $S\in\mathbb{R}^{m\times2}$ 建 KNN 图 $G=(V,E)$。规则网格常用四邻域或六邻域；教程具体设置为 $k=4$ 或 $k=6$。代码 `Cal_Spatial_Net()` 本身不自动推断网格类型，而是使用调用方传入的 `n_neighbors`。同一切片的各模态共享空间坐标，因此教程把相同拓扑传给每个模态分支。

对单细胞分割数据，节点含义从 spot 改成细胞，坐标改成细胞质心；代码还支持半径图。这个扩展没有改变网络或损失，但结果会受到分割质量影响。

#### 2.3 模态编码、拼接与融合

每个模态有两层 SAGEConv 编码器：

$$
h_{i,v}^{(l)}=\operatorname{SAGEConv}\!\left(h_{i,v}^{(l-1)},\{h_{i,u}^{(l-1)}:u\in\mathcal N(v)\}\right).
$$

代码在每层使用 `normalize=True`，输出做 $L_2$ 归一化，但两层之间没有显式 ReLU。各模态的 64 维表示按特征维拼接，再由全连接层投影为统一表示：

$$
Z=W[H_1\Vert H_2\Vert\cdots\Vert H_M]+b,
\qquad Z\in\mathbb{R}^{m\times64}.
$$

读图 1a 时可从左到右理解为：模态 PCA → 同一空间图上的独立编码器 → 拼接 → dense layer → 统一嵌入。所谓“模态无关、可堆叠”指分支数量可以随模态数增加，并不表示模型显式学习了组学间调控关系。论文明确把缺少跨模态相互作用建模列为局限。

#### 2.4 解码与重构

统一嵌入 $Z$ 经每个模态各自的两层 SAGEConv 解码器重建 PCA 特征 $\hat X_i$。重构项要求统一表示仍保留每个模态的信息：

$$
\mathcal L_{\mathrm{rec}}=\sum_i \alpha_i\lVert X_i-\hat X_i\rVert_F^2.
$$

当前代码实际使用逐模态 `F.mse_loss`（均值）再乘 `weights[i]`，与论文写出的 Frobenius 平方和只在缩放上相似，并非逐字等价。

### 3. MNN 三元组如何补上远距离关系

对每个模态，在 PCA 特征空间寻找互为近邻的 $(a,p)$。这对节点可能空间上相距很远，却具有相似分子状态。负样本 $n$ 从与 anchor 距离较远的一部分候选中随机抽取。损失为：

$$
\mathcal L_{\mathrm{tri}}=
\sum_{(a,p,n)}\max\bigl(d(Z_a,Z_p)-d(Z_a,Z_n)+\tau,0\bigr).
$$

其直觉是让正样本至少比负样本近一个 margin。论文消融支持 $\tau=0.5$，教程也使用该值。论文公式写平方欧氏距离，而代码 `TripletMarginLoss(p=2)` 使用未平方的欧氏距离，因此优化几何不完全相同。

论文报告默认 MNN 邻居数 3、远端候选比例 60%。函数默认值却分别是 1 和 50%，但主要单切片教程显式传入 `n_nearest_neighbors=3, farthest_ratio=0.6`；P22 教程使用 0.4。由此应把“论文实验设置”和“函数默认值”分开理解。

### 4. 总损失与可调权衡

论文用

$$
\mathcal L=\lambda\mathcal L_{\mathrm{rec}}+(1-\lambda)\mathcal L_{\mathrm{tri}}
$$

描述空间连续性与分子类型分离之间的权衡。当前训练函数没有名为 `lambda` 的参数，而是使用长度为 $2M$ 的 `weights`：前 $M$ 个权重控制各模态重构，后 $M$ 个控制各模态三元组项，最后直接相加。教程通常传全 1。因此数学思想可以通过权重比表达，但论文参数与代码接口不是一一同名映射。

优化器为 Adam（默认学习率 $10^{-4}$、weight decay $10^{-5}$）。每 10 个 epoch 检查最近 20 个记录点中重构损失或三元组损失的线性斜率；任一绝对斜率低于 $10^{-4}$ 就可能停止。代码还提供默认关闭的图 Laplacian 正则项，论文主方法没有把它列为标准损失。

### 5. SMART-MS 如何处理多切片

图 1b–c 给出三个变化：

1. 各切片同一模态的矩阵纵向合并，联合 PCA 后用 Harmony 去除切片效应。
2. 各切片空间图组成块对角大图，所以 GraphSAGE 不直接跨切片传消息。
3. positive 从另一切片的 MNN 中选，negative 仍从 anchor 所在切片的远端节点中选。

因此真正连接切片的不是空间边，而是 Harmony 后特征与跨切片三元组。`train_SMART_MS()` 的网络与 `train_SMART()` 基本相同；差异主要发生在调用前的数据、图和 triplet 构造。当前 tonsil 教程使用 `far_frac=0.8, top_k=1`，也不同于 `MMN_batch()` 的默认 0.6/2。

SMART-MS 要求切片间有可比较的模态。论文明确说它尚不能处理完全不重叠的模态组合，例如一张只有 RNA、另一张只有蛋白，或不同切片拥有不同组学组合。

### 6. 六张主图能支持什么

- **图 1**：支持架构、单切片/多切片数据流和三元组构造，不是性能证据。
- **图 2**：模拟三组学中，SMART 在多项监督聚类指标、空间自相关和模态距离保持上表现领先；模拟数据有清晰真值，不能直接等同真实组织泛化。
- **图 3**：人淋巴结 RNA+蛋白中，以人工解剖标注和 marker 作为证据，展示细小滤泡及髓质结构的区分。
- **图 4**：MISAR-seq 发育脑 RNA+ATAC，展示不同胚胎阶段和区域的聚类表现；并非所有切片、所有指标都由 SMART 单独最优。
- **图 5**：P22 脑和 Stereo-CITE-seq 多分辨率实验支持效率与规模扩展。论文报告最大 756,430 spots、单 GPU 约 56 秒；该数值依赖论文硬件、预处理和计时口径，不能仅凭本地源码复现确认。
- **图 6**：三张 tonsil 切片中，SMART-MS 同时比较生物保留与 batch correction，并用 RNA/蛋白 marker 验证空间域。未标注数据集上的扩展主要依赖结构、marker、Moran's I 或批次指标，而非统一 ground truth。

所有比较结果都应理解为论文给定数据、预处理、聚类数和 benchmark 实现下的结果；主图不能证明对任意新数据必然最优。

### 7. 直接代码检查揭示的关键复现边界

#### 7.1 当前快照存在参数注册问题

`model.py` 把编码器和解码器保存为普通列表：

```python
self.encoders = [Conv_Encoder(...) for ...]
self.decoders = [Conv_Decoder(...) for ...]
```

它们不是 `nn.ModuleList`，所以 PyTorch 不会把这些子模块加入 `model.parameters()`、`state_dict()` 或 `.to(device)` 的递归管理。虽然构造时每个子模块被单独 `.to(device)`，前向传播仍能运行，但 `Adam(model.parameters())` 通常只会得到已注册的 `self.fc` 参数。结果是当前快照所示训练循环不能证明它在更新 GraphSAGE 编码器/解码器。这是核心实现级复现阻断，不是轻微公式差异。

#### 7.2 当前快照不等于论文完整复现分支

论文 Code availability 指向 `Xubin-s-Lab/SMART-main`，并明确说论文结果 notebook 位于 `SMART-reproduce` 分支；但快照 README 的安装链接又写成 `ws6tg/SMART-main`，并把复现工作再次指向 `SMART-reproduce`。本地仅保存当前源码、教程与 benchmark notebooks，不能据此断言它就是生成全部发表图的精确环境或分支。

#### 7.3 大数据 MNN 与“线性扩展”要分开

GraphSAGE 图传播可以随稀疏边近似线性扩展，但单切片 `Mutual_Nearest_Neighbors()` 先构造完整 pairwise distance matrix。代码对超过 20,000 个节点的数据随机抽 20,000 个再构造 triplet；因此论文的大规模效率不等于全数据精确 MNN 也是线性的。抽样节点以外的节点仍参与重构和图传播，但不会成为该函数产生的 triplet anchor。

### 8. 复现结论

当前快照足以对应 SMART 的概念数据流、图构造、MNN 采样、损失接口、Harmony 和教程调用方式；但它不能被评为“与论文完整高保真实现”。最重要的原因是未注册 encoder/decoder 参数，其次是论文复现分支未被固定、仓库地址不一致、公式与代码距离/权重存在差异，以及大规模 MNN 使用隐式抽样。

若要验证论文数值，最低限度应：固定 `SMART-reproduce` 的具体 commit 与数据版本；确认作者实际训练版本是否使用 `nn.ModuleList`；记录环境和随机种子；逐图运行对应 notebook；保存损失曲线、可训练参数清单、聚类设置、硬件与计时边界。修复参数注册后得到的是“合理实现”，但在作者确认前不能自动视为论文原始实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SMART: Spatial Multi-Omic Aggregation using Graph Neural Networks and Metric Learning

**Paper**: Du et al., Nature Communications 17, 2026
**DOI**: 10.1038/s41467-026-70821-5
**Code**: https://github.com/Xubin-s-Lab/SMART-main
**Category**: integration_multimodal

---

### Motivation & Novelty

#### Biological Problem

Spatial multi-omics technologies simultaneously measure multiple molecular layers (transcriptomics, proteomics, epigenomics) with spatial coordinates, enabling unprecedented characterization of tissue microenvironments. The core computational challenge is integrating heterogeneous omics layers — which have fundamentally different data distributions, dimensionalities, and noise profiles — with spatial context to identify biologically meaningful spatial domains such as anatomical structures, cell niches, and functional microenvironments.

#### Why Existing Methods Fall Short

| Method | Limitation | Reference |
|--------|-----------|-----------|
| MOFA+ | No spatial coordinates | *Genome Biol.* 2020 |
| MEFISTO | No spatial coordinates; computationally heavy | *Nat. Methods* 2022 |
| Seurat WNN | No spatial coordinates; noisy spatial segmentation | *Cell* 2021 |
| totalVI | No spatial coordinates | *Nat. Methods* 2021 |
| MultiVI | No spatial coordinates | *Nat. Methods* 2023 |
| scMM | No spatial coordinates | *Cell Rep. Methods* 2021 |
| SNF | No spatial coordinates | *Nat. Methods* 2014 |
| CiteFuse | No spatial coordinates | *Bioinformatics* 2020 |
| SpatialGlue | Separate RNA and spatial graphs; dual-attention O(M²) complexity; limited multi-section support | (ref not retrieved) |
| CellCharter | Only neighborhood aggregation; misses spatially distant similar regions | *Nat. Genet.* 2024 |
| MISO | Simple concatenation of omics | *Nat. Methods* 2025 |
| SpaMultiVAE | Basic operations for omics integration | *Nat. Methods* 2024 |
| COSMOS | Local spatial adjacency only; misses functionally similar distant regions | *Nat. Commun.* 2025 |
| PRESENT | Specific to certain omics; computationally intensive; no multi-section support | (ref not retrieved) |

#### Unique Contributions

1. **Unified spatial-omic graph**: Constructs a single KNN graph from spatial coordinates, integrates all modalities through this shared graph using GraphSAGE — avoiding the complexity of separate graphs per modality
2. **Modular stacking design**: Each modality gets an independent SAGEConv encoder/decoder, making SMART naturally extensible to any number of omics layers without architectural changes
3. **Metric learning via triplets**: MNN-based triplets identify molecularly similar but spatially distant spots, adjusting the latent embedding to pull them together regardless of spatial distance — addressing the critical "spatially discrete niches" problem
4. **SMART-MS for multi-section integration**: Cross-section triplets (positive from different sections, negative from same section) combined with Harmony batch correction enables coherent multi-section analysis
5. **Linear scalability**: SAGEConv's neighbor sampling enables analysis of >750,000 spots — 56 seconds on a single GPU for the largest tested dataset

---

### Method Overview

SMART is an unsupervised deep learning framework with five core components:

1. **Preprocessing + PCA**: Each modality is normalized independently (RNA: normalize+log+scale; Protein: CLR+scale; ATAC: TF-IDF+log+scale) then compressed via PCA to 30 dimensions (RNA/ATAC) or full ADT dimensions (protein)

2. **Spatial KNN graph**: Spatial coordinates → KNN graph with k=4 (square grids) or k=6 (hexagonal lattice). This graph is shared across all modalities

3. **SAGEConv encoder-decoder**: Two-layer GraphSAGE encoder per modality projects PCA features to 64-dim embeddings using spatial neighborhood aggregation with L2 normalization; a fully connected layer integrates all modality embeddings into a single shared Z ∈ ℝ^(m×64); two-layer decoder reconstructs PCA features from Z

4. **MNN triplet loss**: Pairwise distances in PCA space identify mutually nearest neighbor pairs as anchor-positive; top-60% farthest spots as negatives; triplet margin loss (τ=0.5) with L2 distance

5. **Joint optimization**: Reconstruction loss (MSE) + triplet loss, Adam optimizer (lr=0.0001), early stopping on loss slope < 0.0001

SMART-MS extends this by adding horizontal feature concatenation across sections, Harmony batch correction, diagonal block spatial graph, and cross-section triplet sampling.

See `doc_method.md` for detailed equations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Technology | Modalities | Spots | Application |
|---------|-----------|-----------|-------|-------------|
| Simulated | Townes et al. | RNA+ADT+ATAC | 1,296 | Ground-truth benchmarking |
| Human lymph node A1, D1 | 10x Visium CytAssist | RNA+Protein | 3,484 / 3,359 | Transcriptome-proteome (7 regions) |
| Mouse fetal brain (E11-E18) | MISAR-seq | RNA+ATAC | 1,263–2,248 per section | Chromatin-transcriptome (5–10 regions) |
| P22 mouse brain | CUT&Tag-RNA-seq | RNA+H3K27me3 | 9,752 | Efficiency benchmarking |
| Mouse spleen | Stereo-CITE-seq | RNA+Protein | 2,001–756,430 (6 resolutions) | Scalability benchmarking |
| Human tonsil (3 sections) | 10x CytAssist | RNA+Protein | ~4,450/section | Multi-section integration |
| Mouse spleen (2 sections) | SPOTS | RNA+Protein | 2,647 / 2,759 | Multi-section replication |

#### Metrics

**Supervised** (require ground truth): ARI, AMI, NMI, Homogeneity, MI, FMI, V-Measure
**Unsupervised spatial**: Moran's I (spatial autocorrelation)
**Batch correction** (multi-section only): iLISI, kBET
**Embedding quality**: Pearson correlation coefficient between pairwise distance matrices of original PCA features and integrated embeddings

#### Key Results

**Simulated tri-omics (Fig. 2)**:
- SMART and CellCharter were the only methods to accurately identify all 5 spatial factors with correct boundaries
- SMART achieved highest scores across all 7 metrics (ARI, AMI, NMI, Homo, MI, FMI, V-Measure); MOFA+ second overall but poorest spatial autocorrelation
- SMART highest modality preservation (PCC between original and embedded distance matrices)

**Human lymph node A1 RNA+Protein (Fig. 3)**:
- SMART identified 7 distinct regions including cortex, medullary sinuses, medullary cords, capsule, follicles, and pericapsular adipose tissue
- Significant advantage over 13 comparison methods on all metrics at k=7 clusters
- Performance advantage robust across cluster numbers 5–10
- Validated by marker genes (*CD3E*, *CCR7* in cortex T-cell zone; *CCN1* in medullary sinus)

**MISAR-seq mouse brain (Fig. 4)**:
- Best overall supervised metrics across all 4 developmental stages (E11–E18)
- Detected small structures (cartilage-1) missed by SpatialGlue
- Only exception: E11.0_S1 where MOFA+ outperformed SMART

**Computational efficiency (Fig. 5)**:
- Shortest training time and lowest memory usage among all methods on P22 mouse brain (9,752 spots)
- Only method that completed on Bin10 Stereo-CITE-seq dataset (756,430 spots); 56 seconds total training time
- All other methods failed at ~190,000 spots (Bin20) due to memory exhaustion

**SMART-MS multi-section tonsil (Fig. 6)**:
- Highest ARI across all cluster numbers (4–8) on individual and combined sections
- Highest Moran's I for spatial coherence
- Best combined biological conservation + batch correction (iLISI + kBET) among all multi-section methods

#### Compared Methods (Full List)

- SpatialGlue, CellCharter (*Nat. Genet.* 2024), COSMOS (*Nat. Commun.* 2025), MISO (*Nat. Methods* 2025), SpaMultiVAE (*Nat. Methods* 2024), PRESENT
- MOFA+ (*Genome Biol.* 2020), MEFISTO (*Nat. Methods* 2022), SNF (*Nat. Methods* 2014), Seurat WNN (*Cell* 2021), scMM (*Cell Rep. Methods* 2021)
- totalVI (*Nat. Methods* 2021), MultiVI (*Nat. Methods* 2023), CiteFuse (*Bioinformatics* 2020), StabMap, MEFISTO

---

### Reproducibility

**Rating: 4/5**

**Environment setup**:
- Python 3.9.23, R 4.3.0, PyTorch 2.4.1, torch-geometric 2.3.0 — all pinned versions in requirements.txt
- R package mclust must be installed separately (`install.packages("mclust")` via rpy2)
- PyTorch Geometric scatter/sparse wheels must be installed from PyG's own CDN (not standard pip)
- `conda` recommended; micromamba also works but R installation from conda-forge must precede rpy2

**Data availability**:
- All datasets publicly available via GEO (GSE263617, GSE205055, GSE198353), NGDC (OEP003285), BGI STOmics Cloud, Zenodo
- Preprocessed data uploaded to Zenodo (10.5281/zenodo.17093158) — ready to run without re-downloading raw data

**Code quality**:
- Well-documented with docstrings for all functions
- 5 tutorial notebooks covering each main experiment
- `set_seed()` function enables reproducibility (seed=2024 default)
- Benchmarking notebooks provided for all 13 comparison methods

**Pitfalls**:
1. **R dependency**: `rpy2` requires a matching R installation; failure to install mclust before running will give cryptic errors at clustering step
2. **MNN subsampling**: For datasets >20,000 spots, the `max_samples=20000` parameter in `Mutual_Nearest_Neighbors()` introduces randomness in triplet construction; results may vary slightly even with `set_seed()`
3. **Hyperparameter sensitivity**: k (spatial neighbors) and τ (margin) significantly affect results. Default k=6 for Visium; setting k=4 for square-grid datasets is critical
4. **Graph directedness**: `Cal_Spatial_Net()` produces a directed graph (sklearn's `kneighbors_graph`), not a symmetric undirected graph as typical GNNs assume

**Strengths**: Modular design makes it easy to add a new omics modality; clear code structure; comprehensive tutorial coverage.

**Weaknesses**:
- Cannot integrate sections with non-overlapping modalities (e.g., RNA-only in one section, RNA+Protein in another)
- Limited explicit inter-modality relationship modeling (each modality's encoder operates independently on the same spatial graph)
- R dependency (mclust) adds installation complexity; leiden/louvain alternatives available in the clustering function

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
