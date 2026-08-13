---
layout: default
permalink: /paper-atlas/celllens-8d7b8d11/
title: "CellLENS"
nav: false
description: "CellLENS 的核心不是直接把表达、坐标和像素拼接，而是先从表达建立粗粒度初始细胞群，再把每个细胞周围的群体组成当作自监督目标。LENS-CNN 学习“局部组织图像能否预测邻域组成”，LENS-GNN-duo 则让表达分支在表达相似图上传播、图像分支在空间近邻图上传播，两个分支合并后预测“初始身份 one-hot + 邻域组成”。训练多轮后拼接中间表示并做 SVD，得到用于无监督细胞群划分的稳定 embedding。"
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
      <span>Nature Immunology · 2025</span>
    </div>
    <h1>CellLENS</h1>
    <p>CellLENS enables cross-domain information fusion for enhanced cell population delineation in single-cell spatial omics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41590-025-02163-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellLENS">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/sggao/celllens" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellLENS">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellLENS 方法解读：用邻域组成自监督融合表达、位置和组织图像

### 一句话理解

CellLENS 的核心不是直接把表达、坐标和像素拼接，而是先从表达建立粗粒度初始细胞群，再把每个细胞周围的群体组成当作自监督目标。LENS-CNN 学习“局部组织图像能否预测邻域组成”，LENS-GNN-duo 则让表达分支在表达相似图上传播、图像分支在空间近邻图上传播，两个分支合并后预测“初始身份 one-hot + 邻域组成”。训练多轮后拼接中间表示并做 SVD，得到用于无监督细胞群划分的稳定 embedding。

论文为 Gao、Zhu 等发表于 *Nature Immunology*（2025）的 “CellLENS enables cross-domain information fusion for enhanced cell population delineation in single-cell spatial omics data”，DOI `10.1038/s41590-025-02163-1`。

### 1. CellLENS 所说的三个信息域

对每个细胞，方法使用：

- expression/features：RNA、蛋白或其他空间组学特征；
- location：二维细胞中心坐标及其空间邻域；
- image：以细胞为中心裁剪的核/膜等组织图像通道。

“跨域融合”不是典型的不同细胞多模态对齐。三类信息必须落到同一批细胞上：DataFrame 的行、坐标、裁剪图像编号必须一致。多 FOV 数据尤其需要将坐标变换到不会跨 FOV 错连的全局像素系，且图像坐标必须与裁剪使用的像素位置一致。

最终任务是 population delineation：发现既有分子差异、又有空间/形态语境的细胞亚群。它不是监督式细胞类型分类器，也不保证得到的每个 cluster 都是新的生物类型；cluster 仍需用 marker、位置、组织学和重复样本验证。

### 2. 自监督标签从哪里来

#### 2.1 初始表达身份

`LENS_Dataset.initialize()` 对中心化/缩放后的 feature matrix 做 PCA（论文默认 $d_0=25$），在相关距离上建立 $k_f=15$ 的 feature similarity graph $G_f$，然后以 Leiden（论文 resolution 0.5）生成初始标签 $c_i$。这些标签不是最终答案，而是构造学习目标的粗身份锚点。

#### 2.2 细胞邻域组成

对细胞 $i$ 找 $k_1$ 个空间近邻。若共有 $p$ 个初始群，邻域组成向量为

$$
y_{ig}=\frac1{k_1}\sum_{j\in\mathcal N_s(i)}
\mathbf 1(c_j=g),\qquad g=1,\dots,p.
$$

$y_i$ 描述“这个细胞周围由哪些粗细胞群构成”，而不是该细胞自身表达。方法再将自身初始标签的 one-hot $e(c_i)$ 与 $y_i$ 拼成

$$y_i^{\mathrm{tg}}=[e(c_i),y_i]\in\mathbb R^{2p},$$

作为 GNN-duo 的自监督 target。这样模型既不能完全忽略分子身份，也不能完全忽略局部组织语境。

论文默认 $k_1=20$，当前 `LENS_Dataset` 默认 `nbhd_composition=15`；论文复现需显式传 20。若已有人工注释，论文允许用其替代初始聚类，但当前包的 `initialize(celltype!=feature_labels)` 分支只打印类别数，没有给 `self.feature_labels` 赋值，随后仍读取该字段构造 one-hot。因此这个可选 API 路径在当前快照中需要先修复/验证，不能视为开箱即用。

### 3. 图像如何变成局部组织形态编码

#### 3.1 裁剪和二值化

每个细胞从整张组织图像裁剪 $C\times L\times L$ patch。论文默认 $C=2$（核和膜）、$L=512$ 像素，约对应 50–100 μm，并按通道的 $\alpha=0.9$ 分位阈值二值化。这个 patch 刻画的不只是单细胞形状，还包括邻近细胞排列和组织边界。

尺度具有生物意义：窗口过小只看到单个核，过大则混入多个不相关 microenvironment。像素大小随平台变化，所以 512 不能脱离物理分辨率直接复用。

#### 3.2 LENS-CNN 的训练目标

AlexNet-like `LENS_CNN` 使用六个卷积层，前五层带 2×2 max pooling，再经 1024、512、128 三层全连接得到图像编码

$$z_i=\operatorname{enc}(T_i)\in\mathbb R^{128}.$$

顶层线性 head 从 $z_i$ 预测邻域组成 $\tilde y_i$，用

$$L_{\mathrm{CNN}}=\frac1N\sum_i\|y_i-\tilde y_i\|_2^2$$

训练。没有人工形态标签；图像 encoder 被迫提取能解释周边细胞组织的视觉特征。训练后丢掉预测 head，保存 128 维 `cnn_embedding` 作为第二阶段输入。

论文使用 Adam、lr $10^{-4}$、batch 64、400 epochs；当前 `fit_lens_cnn()` 和 wrapper 默认 300 epochs。当前包还提供 ViT 替代，但论文消融显示冻结预训练 ResNet/ViT 并不更好，重训练 ViT 计算更贵；主方法证据基于重新训练的简单 CNN。

### 4. LENS-GNN-duo 为什么是两个不同的图

#### 4.1 feature branch

表达特征 $X$ 先线性投影到 32 维，然后在 feature similarity graph $G_f$ 上做两层 GCN，输出

$$h_i^{(f)}\in\mathbb R^{33}.$$

该图连接表达相近细胞，即使它们空间上相距很远；分支因此侧重分子身份的一致性。

#### 4.2 spatial-image branch

CNN image code $Z$ 先投影到 32 维，然后在 spatial proximity graph $G_s$（论文 $k_s=15$）上做两层 GCN，输出

$$h_i^{(s)}\in\mathbb R^{11}.$$

这里节点特征是局部图像编码，边由细胞位置决定，因此形态和空间被有意绑定。

#### 4.3 融合与预测

两个分支的中间表示拼接：

$$u_i=[h_i^{(f)},h_i^{(s)}]\in\mathbb R^{44}.$$

两层 MLP 将它映射到 $2p$ 维预测 $\hat y_i^{\mathrm{tg}}$，以

$$L_{\mathrm{GNN}}=\frac1N\sum_i
\|y_i^{\mathrm{tg}}-\hat y_i^{\mathrm{tg}}\|_2^2$$

训练。最终用于表征的是 MLP 之前的 $u_i$，不是 2p 维 target prediction。源码 `LENS_GNN_DUO.encoder()` 返回两个 GNN 的 concat，`forward()` 才追加 MLP。

这一设计形成一个信息环：初始标签和邻域组成来自表达/位置，CNN 学习从图像预测邻域，GNN 再把表达和图像—空间表示整合去预测同一双目标。因此它是自监督表示学习，而不是独立于初始聚类的无先验生成模型。初始 Leiden、$k_1$、图构造和图像尺度都会影响最终 embedding。

### 5. 多轮训练与 SVD 稳定化

GNN 随随机初始化会产生旋转或噪声不同的 44 维表示。`get_lens_embedding(round=5,k=32)` 独立训练五轮，将

$$\bar U=[U_{[1]},\dots,U_{[m]}]\in\mathbb R^{N\times 44m}$$

横向拼接，再做 SVD：

$$\bar U=L D V^\top,qquad E=L_{:,1:k}D_{1:k,1:k}.$$

当前默认输出 32 维 `lens_embedding`。论文先定义单轮 $p_0=44$，再通过多轮分解提取共同结构；最终 32 维是包实现选择，不应说“最终表示必然是 44 维”。SVD 稳定的是跨轮共同变化，并不能纠正所有轮共享的系统性偏差，例如错误的 FOV 邻接。

### 6. 完整模式和 LITE 模式是两种不同方法边界

`CellLENS(..., cnn_model="LITE")` 是当前默认。此时不训练 CNN，也不创建 dual GNN；`LENS_GNN_LITE` 只用 feature 表示和 feature graph，输出维度由 `gnn_latent_dim` 决定。它不融合 image domain，空间信息只通过自监督 neighborhood target 间接进入。

要运行论文主张的三域全模型，必须显式使用 `cnn_model="CNN"`（或实验性 `"ViT"`），准备 image patches，调用 `fit_lens_cnn()`、`get_cnn_embedding()`，再运行多轮 GNN。把默认 LITE 结果称为“表达+位置+图像完整 CellLENS”是不准确的。

当前 `fit_transform()` wrapper 还有直接调用风险：它把 `self` 再次作为位置实参传入已经绑定的 `fit_lens_cnn()`、`get_cnn_embedding()` 和 `get_lens_embedding()`，同时又给后续参数命名赋值，按 Python 绑定规则会产生重复参数/错误类型。因此当前快照更安全的可验证路径是逐步调用这些方法；wrapper 在修复和测试前不应作为复现入口。

### 7. 下游聚类与 refinement

`get_lens_clustering()` 在最终 embedding 上 scale、建 15-NN、Leiden（默认 resolution 1），随后按初始 feature labels 做 cluster refinement。refinement 检查 cluster 内初始标签熵和集中度，可拆分混杂 cluster，并移除很小群体。

这意味着最终 cluster 并非只由 embedding + Leiden 决定，还受初始标签与 refinement 阈值影响。发现稀有群体时必须报告 `resolution`、entropy/concentration threshold、`max_breaks` 和 `size_lim`。若用已知类型 marker 验证同一数据上的 cluster，需避免把后验解释误写成独立 ground truth。

### 8. 如何理解论文结果

- Fig. 1 是两阶段模型图：图像 patch 预测 neighborhood composition；expression-GNN 与 spatial-image-GNN 合流预测 dual target，再产生 embedding 与 clusters。
- Fig. 2 在 CODEX mouse spleen 中展示 benchmark 和 B-cell subpopulation；更高 CH/更好空间一致性支持表示分离能力，但不自动证明每个细分群有独立功能。
- Fig. 3–4 在 tonsil/CODEX/Xenium 等数据中展示 germinal center、稀有免疫群和跨切片稳定性。
- Fig. 5 在 CosMx HCC 中将 macrophage 亚群与肿瘤空间关系、差异基因结合解释。
- Extended Data 系列检查更多基线、图像通道/模型、参数敏感性、相邻切片和 10k–1.5M 细胞扩展性。

论文用 silhouette、Calinski–Harabasz、Davies–Bouldin 和 modularity 等无监督指标。它们奖励紧致/分离或图社区结构，却不是生物真值；尤其空间融合方法可能因为强制局部连续而提高某些指标。论文的 marker、组织区室和重复切片证据需要与这些数值共同阅读。

### 9. 论文—代码匹配与差异

| 机制 | 当前源码 | 判断 |
|---|---|---|
| feature graph、初始 Leiden、neighborhood composition | `datasets.py`, `graph.py`, `utils.py` | Exact 主机制 |
| 图像裁剪/阈值 | `preprocessing.py` | Exact |
| 六层 LENS-CNN + MSE | `models.py::LENS_CNN`, `fit_lens_cnn()` | Exact；默认 300 vs 论文 400 epochs |
| dual GNN 与 44D concat | `models.py::LENS_GNN_DUO` | Exact |
| dual target MSE | `fit_lens_gnn()` | Exact；该方法默认 lr $10^{-4}$，论文为 $10^{-3}$；wrapper 显式传 $10^{-3}$ |
| 五轮 concat + SVD 32D | `get_lens_embedding()` | Exact 当前实现；注意单轮 44D/最终 32D |
| 完整三域默认 | `CellLENS.__init__()` | Not default：默认是 LITE，无 CNN |
| 一键 `fit_transform()` | `celllens.py` | Broken/Not verified：绑定方法重复传 self |
| 人工注释替代初始 Leiden | `LENS_Dataset.initialize()` | Broken/Not verified：未设置 `self.feature_labels` |
| 论文全部 benchmark | Manuscript archive、数据、R/Python 脚本 | Partial：硬编码历史路径、外部环境和大数据/GPU 依赖 |

### 10. 版本与复现边界

- acquisition 记录 upstream commit `4b33bb6…`，package version 0.1.0；本地无独立上游 Git 元数据。
- 论文代码可用性段给出的 URL 拼作 `cellens`，工作区/metadata 使用实际 `celllens` 仓库，应以 acquisition 路径为准。
- `environment.yml` 和依赖下限存在，但不是完整跨平台锁定；PyTorch/PyG/Scanpy/Leiden 版本会影响图、训练和聚类。
- 论文与包默认在 CNN epochs、GNN learning rate、neighborhood composition k 上不一致。
- 主包 wrapper 和人工注释分支存在当前源码级问题；本次未修改代码，也未进行 GPU 全流程训练。
- Manuscript archive 包含大量绝对路径和实验脚本，不能直接等价为可移植 end-to-end benchmark runner。

### 11. 建议的可复现分步调用

1. 创建 `LENS_Dataset`，显式设 `nbhd_composition=20`, `feature_neighbor=15`, `spatial_neighbor=15`；
2. `initialize()` 用默认 feature-derived labels，并检查 FOV 边界；
3. `prepare_images(size=512,truncation=0.9,...)`；
4. `CellLENS(..., cnn_model="CNN")`；
5. `fit_lens_cnn(n_epochs=400, learning_rate=1e-4)` 后 `get_cnn_embedding()`；
6. `get_lens_embedding(round=5,k=32,learning_rate=1e-3,n_epochs=3000)`；
7. 记录 Leiden/refinement 全参数并用 marker、组织位置和重复样本验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellLENS Paper Summary

### Motivation & Novelty

#### Biological Problem
Delineating cell populations in their tissue context is fundamental to understanding immune function in health and disease. Spatial omics technologies such as CODEX (Cell Segmentation by the Oligonucleotide-directed Optical DEtection of antibodies), CosMx SMI, and Xenium can simultaneously measure dozens to thousands of molecular features at single-cell resolution within intact tissue. However, the data contains three complementary information domains that current methods fail to fully exploit:

1. **Expression**: molecular biomarker levels (the only input to conventional pipelines)
2. **Location**: relative positions of cells, encoding the spatial microenvironment
3. **Image**: local tissue architecture and cell morphology

#### Limitations of Existing Methods
Existing methods fall into two camps:

- **Purely expression-based** (feature-only): Standard clustering on expression profiles (Leiden, FlowSOM). Misses spatial context entirely. Cannot distinguish functionally distinct cells with identical molecular profiles located in different microenvironments.
- **Supervised classification** (STELLAR, *Nat Methods* 2022; CellSighter, *Nat Commun* 2023): Classify cells into predefined categories using spatial context. Cannot discover *new* populations unseen in training data.
- **Partial spatial integration**: MUSE (*Nat Biotechnol* 2022) integrates individual cell morphology (cell shape) but not neighborhood/tissue context. SPICEMIX (*Nat Genet* 2023) uses spot-level spatial adjacency but lacks image information. Both remain limited to one additional domain.
- **Domain methods not designed for single-cell**: SpaGCN (*Nat Methods* 2021), stLearn (*Nat Commun* 2023), SEDR (*Genome Med* 2024), BANKSY (*Nat Genet* 2024), CellCharter (*Nat Genet* 2024) target spatial domain identification or spot-level data, not single-cell population delineation.

#### Unique Contributions
CellLENS is the first **unsupervised** method to fuse **all three domains** (expression, location, image) for single-cell spatial omics. Key innovations:

1. **LENS-GNN-duo architecture**: Two parallel GCN streams — one on expression similarity graph, one on spatial proximity graph — that share node representations and are jointly trained
2. **LENS-CNN as self-supervised image encoder**: An AlexNet-like CNN trained to predict neighborhood composition from cell image patches, without any manual labels
3. **Multi-domain self-supervision**: The training target is a *combination* of spatial context (neighborhood composition) and expression-based identity (one-hot cluster label), forcing the model to integrate both
4. **Multi-round SVD stabilization**: Repeated training with different random seeds followed by truncated SVD extracts consistent embedding components

---

### Method Overview

CellLENS is a two-stage self-supervised geometric deep learning pipeline:

**Stage 1 — LENS-CNN** trains a 6-layer AlexNet-like CNN that predicts a cell's cellular neighborhood context vector (the composition of surrounding cell types) from its local tissue image patch. The learned CNN encoding encapsulates tissue morphology information without any manual annotation.

**Stage 2 — LENS-GNN-duo** trains a dual-GNN architecture with an MLP head. Two parallel GCNs process expression information (on a cell expression-similarity graph) and image information (on a spatial proximity graph, initialized with CNN encodings) simultaneously. The concatenated output of both GCNs before the MLP forms the final cell representation, which encodes expression profile, spatial microenvironment, and tissue morphology in a unified 44-dimensional vector (further compressed to 32 dimensions via SVD).

Downstream Leiden clustering on these representations produces cell populations with markedly improved spatial coherence and fine-grained resolution compared to expression-only approaches.

For a detailed mathematical description, see `doc_method.md`. For code-paper mapping, see `doc_code.md`.

---

### Evaluation

#### Datasets
CellLENS was benchmarked on 5 diverse spatial omics datasets:

| Dataset | Technology | Cells | Features | Tissue/Disease |
|---|---|---|---|---|
| Mouse spleen | CODEX | 53,500 | 30 proteins | Healthy spleen |
| Human tonsil | CODEX | 102,574 | 46 proteins | Healthy tonsil |
| Human tonsil | Xenium | 158,259 | 377 genes | Healthy tonsil |
| Human LN | Xenium (5k panel) | ~100k | 5,000 genes | Healthy lymph node |
| Human tonsil (2 sections) | CODEX | ~100k | 46 proteins | Adjacent sections |
| Human cHL TME | CODEX | 143,730 | 45 proteins | Classic Hodgkin lymphoma |
| Human HCC liver | CosMx SMI | 54,867 | 997 genes | Hepatocellular carcinoma |

#### Quantitative Metrics (unsupervised, no ground truth)
Four clustering quality metrics were used (all computed on 5 random batches of 10,000 cells each):
- Silhouette score (higher = better separation)
- Calinski-Harabasz index (higher = better)
- Davies-Bouldin index (lower = better)
- Modularity score (higher = better community structure)

#### Comparative Results
CellLENS was compared against 11 methods across 5 datasets (Extended Data Fig. 6):
- **Feature**: raw expression PCA (30 PCs) + Leiden
- **Concat**: PCA + neighborhood composition concatenated
- **CCA**: cross-decomposition of expression + neighborhood (sklearn)
- **MOFA+**: multi-modal factor analysis (Genome Biol, 2020)
- **SPICEMIX**: spatial cell identity modeling (Nat Genet, 2023)
- **MUSE**: morphology + expression integration (Nat Biotechnol, 2022)
- **SpaGCN**: GCN for spatial domains (Nat Methods, 2021)
- **stLearn**: spatial trajectory learning (Nat Commun, 2023)
- **SEDR**: spatial deep representation (Genome Med, 2024)
- **BANKSY**: spatial omics analysis (Nat Genet, 2024)
- **CellCharter**: spatial niche identification (Nat Genet, 2024)

**CellLENS consistently outperformed all 11 methods across all 5 datasets on all 4 metrics.**

#### Biological Validation
Key biological discoveries enabled by CellLENS but missed by expression-only clustering:

1. **Mouse spleen B cells**: CellLENS identified 7 B cell subpopulations including germinal center (CD21/CD35-high), CD21/CD35-negative GC B cells, splenic zone B cells, and two distinct marginal zone populations. Feature-only clustering produced mixed clusters.

2. **Tonsil replicating non-GC B cells**: CellLENS distinguished GC-proliferating B cells (cc7, inside GC spatially) from non-GC proliferating B cells (cc15, outside GC) despite nearly identical Ki-67 expression profiles. Differential expression confirmed distinct TCL1A/BASP1/CD79A expression levels between spatially distinct populations.

3. **LN rare cell types (5k Xenium panel)**: CellLENS uniquely identified follicular helper T cells (TFH), tingible body macrophages (TBMs), and follicular dendritic cells (FDCs) — even with 5,000 genes, these low-frequency populations were invisible to expression-only clustering.

4. **cHL CD4 T cells**: CellLENS identified 6 CD4 T cell subpopulations with distinct tumor-relative spatial locations. Tumor-infiltrating CD4 T cells (cc20) showed elevated LAG3 and PD-1 (exhaustion markers) vs. tumor-boundary T cells (cc8), linking spatial position to functional state.

5. **HCC macrophages**: CellLENS identified a tumor-boundary macrophage subpopulation (cc6) with enriched C1QA/C1QB/C1QC expression and M1-like pro-inflammatory phenotype, distinct from immunoregulatory macrophages. Spatial ligand-receptor analysis (SpatialDM) confirmed enriched interactions at the tumor interface.

#### Scalability
CellLENS was tested on synthetically scaled datasets (10k to 1.5M cells). Running on NVIDIA A5000 GPU, CellLENS processes 1.5M cells within a reasonable timeframe for biological labs (Extended Data Fig. 10). The bottleneck is the full-batch GNN step; future work could address this with neighborhood sampling.

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Code fully available at https://github.com/sggao/celllens with pip-installable package
- 4 Jupyter notebooks covering CODEX, Xenium, LITE mode, and ViT variant
- All datasets publicly available via Zenodo (https://doi.org/10.5281/zenodo.14617085) and 10x Genomics
- Extensive benchmarking against 11 methods across 5 datasets

**Limitations**:
- **Hyperparameter discrepancies**: Three default values in code differ from paper (CNN epochs 300 vs 400, GNN lr 1e-4 vs 1e-3, neighborhood k 15 vs 20). Results may not exactly reproduce paper figures with stock code
- **LITE mode as default**: The default `cnn_model='LITE'` skips the CNN image step — users may unknowingly run a two-domain analysis (expression + spatial) rather than the three-domain method described in the paper
- **No random seed control**: Multi-round SVD partially addresses reproducibility, but no fixed seeds are set for GNN initialization by default; results can vary slightly run-to-run
- **Image preprocessing not scriptable**: `prepare_images()` requires a correctly formatted whole-tissue image array — pre-processing from raw TIF files is dataset-specific and not automated in the package
- **GPU required**: LENS-CNN training requires GPU; large datasets (>100k cells) may require significant VRAM (>16GB)

**Environment setup**:
```bash
pip install celllens  # or conda
# Key deps: torch>=1.12, torch_geometric>=2.3, scanpy>=1.10, leidenalg>=0.9.1
```

**Common pitfalls**:
1. Forgetting to set `cnn_model='CNN'` — the default LITE mode skips images
2. Cell coordinates must be in global pixel space (not per-FOV) when multiple FOVs exist
3. For multi-FOV datasets, spatial graph construction must respect FOV boundaries
4. Image window size L=512 needs to match the spatial resolution of the platform (50–100 μm)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
