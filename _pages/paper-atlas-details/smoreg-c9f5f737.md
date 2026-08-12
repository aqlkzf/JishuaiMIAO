---
layout: default
permalink: /paper-atlas/smoreg-c9f5f737/
title: "SMOReg"
nav: false
description: "SMOReg 不只把 RNA 和蛋白拼在一起做空间聚类。它先在每个 spot 内，把基因和蛋白分别放进由生物先验定义的图，用图卷积去噪；再学习每个基因—蛋白对的亲和矩阵，让两种分子图交换信息；最后把每个 spot 的融合表示放入“分子相似邻域 + 物理空间邻域”的两层 GAT，并通过对比学习得到用于空间域聚类的表示。训练后保存的 spot 级亲和矩阵再被聚合和置换检验，用于提出域特异的基因—蛋白关系。"
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
      <span>Advanced Science · 2026</span>
    </div>
    <h1>SMOReg</h1>
    <p>Decoding Spatial Heterogeneity and Multi-Omics Regulation with Hierarchical Graph Learning</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1002/advs.75574" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SMOReg：从 spot 内分子网络到组织空间域的分层图学习

### 一句话理解

SMOReg 不只把 RNA 和蛋白拼在一起做空间聚类。它先在每个 spot 内，把基因和蛋白分别放进由生物先验定义的图，用图卷积去噪；再学习每个基因—蛋白对的亲和矩阵，让两种分子图交换信息；最后把每个 spot 的融合表示放入“分子相似邻域 + 物理空间邻域”的两层 GAT，并通过对比学习得到用于空间域聚类的表示。训练后保存的 spot 级亲和矩阵再被聚合和置换检验，用于提出域特异的基因—蛋白关系。

证据入口为 `paper source/auto/SMOReg.md`、同目录主图图片和本地代码快照 `code/SMOReg`。论文 DOI 为 `10.1002/advs.75574`，2026 年发表于 *Advanced Science*。代码仓库 `https://github.com/ByGary/SMOReg` 的快照提交为 `76e50d54fb22c5156462b1520cc83d9c19d06b52`。

### 1. 输入和输出

输入是在同一批空间位置测得的转录组与蛋白组：每个 spot 有 RNA 向量、ADT/蛋白向量和二维坐标。真实数据中，论文保留 3,000 个高变基因，蛋白不做同样的高变筛选；RNA 归一化、对数化并标准化，蛋白做 CLR 和标准化。论文明确说真实数据不预先插补。

主要输出有两类：

1. 每个 spot 的低维表示和空间域标签；
2. 每个 spot 的基因×蛋白亲和矩阵，进一步汇总为域特异候选关系。

“亲和”应理解为模型学习到的统计关联分数，而不是已经实验验证的调控方向或因果边。论文 Discussion 也把这些关系限定为 in silico hypotheses。

### 2. 第一层：在每个 spot 内构建两张分子图

#### 2.1 图结构来自生物先验

基因图（GGI）的节点是高变基因。论文把每个基因映射到 GO biological processes，以 Jaccard 相似度衡量两个基因的 GO 集合重叠：

$$
J_{ij}=\frac{|\mathcal N_i\cap\mathcal N_j|}{|\mathcal N_i\cup\mathcal N_j|},
$$

超过阈值 $\tau$ 时连边。蛋白图（PPI）使用 STRING，置信度阈值为 0.9。每个 spot 共享图拓扑，但节点的一维输入值来自该 spot 的对应基因或蛋白表达量。

本地代码的 `preprocess.py::build_omics_adj` 可以从外部 interaction CSV 建边并加自环；`build_KNN_adj` 还按跨 spot 的分子表达相关性为每个分子寻找一个近邻，`merge_omic_adj` 将其与先验图合并。这里出现论文—代码差异：论文 Methods 只把 GGI 描述为 GO/Jaccard 先验，发布脚本却显式合并了表达 KNN 边。

#### 2.2 GCN 沿先验边传播

论文对两种分子图分别使用一层 GCN：

$$
H^{(l)}=\sigma(\widetilde A H^{(l-1)}W^{(l-1)}+b^{(l-1)}).
$$

直观上，同一个 spot 内某个分子的信号会与其已知功能邻居混合，从而让稀疏/噪声表达借助网络结构得到平滑。代码 `graph_model.py::Siamese_Gconv` 让基因图和蛋白图共享同一个 `Gconv` 权重；`Gconv` 实际执行线性变换后稀疏邻接乘法，未在该函数中加入论文公式所写的 ReLU。因此“GCN 与论文完全一致”不能成立，只能确认消息传播骨架相符。

### 3. 第二层：学习基因—蛋白亲和并交换信息

对于一个 spot，经 GCN 得到基因表示 $H^g$ 和蛋白表示 $H^p$。亲和层计算：

$$
B_{ij}=\operatorname{sigmoid}((h_i^g)^TW_{aff}h_j^p),
$$

所以 $B\in(0,1)^{N_g\times N_p}$。本地 `affinity_layer.py::Affinity` 逐字实现 `X @ A @ Y.T` 后 sigmoid。

随后，论文和代码都使用硬匹配：每个基因只选择亲和最高的蛋白，每个蛋白只选择亲和最高的基因；对方表示乘以该最大亲和分数，与本节点表示连接，再经线性层更新。代码 `CGM.forward` 的 `torch.max(..., dim=1/0)`、加权索引和 `cross_graph` 对应这一过程。

这个设计的含义是稠密矩阵用于计分，但跨图消息传递只通过每个节点的 top-1 伙伴。`argmax` 对索引选择不可导；梯度可通过被选中的亲和值和表示传播，但不会对未选候选提供平滑的选择梯度。论文没有系统讨论这种硬选择的稳定性。

### 4. 第三层：把两种组学融合成 spot 表示

代码先沿分子表示的隐藏维取均值，使每个 spot 得到一个基因向量和一个蛋白向量；`AttentionLayer` 再把两者分别线性投影到同维空间，计算两个模态的 softmax 权重：

$$
\alpha^m=\frac{\exp(c^m)}{\sum_{j=1}^{2}\exp(c^j)},\qquad
s=\sum_m\alpha^mp^m.
$$

因此模型能按 spot 调整 RNA 与蛋白的相对贡献，而不是使用固定 1:1 权重。需要注意，这个模态权重不等于某个具体基因—蛋白调控强度；后者来自 $B$。

### 5. 第四层：在 spot 之间串联功能邻域与空间邻域

论文定义两张 spot 图：

- feature proximity graph：由 Seurat WNN 得到跨模态相似邻居；
- spatial proximity graph：由物理坐标邻近得到空间邻居。

两层 GAT 依次聚合。代码 `Typing_Garph.forward` 明确先用 `wnn_list` 做 `conv1`，再用 `spatial_list` 做 `conv2`。这样先聚合功能相似 spot，再让表示服从局部组织连续性。GAT 为不同邻居学习权重，目的是避免在组织边界上无差别平滑。

但当前公开快照不能直接跑通这条论文流程：`preprocess.py` 中 WNN 构造和返回值被注释掉，`build_spot_adj` 只返回两个对象，而 `main_exp_data.py` 仍期待三个；`transfer_pyG_spatialGraph` 定义只接收四个参数，`graph_model.py` 却传入五个。此外仓库缺少被 `utils.py` 导入的 `config/defaults.py`、实验 YAML、Data 和 interaction 文件，多个路径还是空字符串。这是复现阻断，不是文档安装问题。

### 6. 对比学习如何训练整条链

正样本使用原始 spot 特征通过同一个 GAT 得到的表示；负样本把 spot 特征随机打乱但保留图结构，再次通过 GAT。局部表示与邻域平均得到的 summary 通过判别器评分，使用二元交叉熵区分正负。代码中：

- `permutation` 打乱行；
- `AvgReadout` 对图边指示的邻居求平均并 L2 归一化；
- `Discriminator` 实际是 `nn.Bilinear`，不是论文 Methods 后段描述的“两层 MLP”；
- `main_exp_data.py` 使用 `BCEWithLogitsLoss`，论文统一报告训练 100 epochs。

因此论文与发布代码在判别器架构上存在直接不一致。由于配置文件缺失，代码中的 `cfg.train.epochs`、学习率、维度和邻居数也无法从快照解析。

### 7. 从亲和矩阵到“域特异调控对”

训练保存每个 spot 的 $N_g\times N_p$ 矩阵。论文先在每个聚类内求平均，再按绝对亲和值选择候选，并通过跨空间域打乱构造零分布；$p<0.05$ 的关系被称为 domain-distinctive。之后把分子提交 DAVID 2024q4 做 GO、KEGG、Reactome 等富集，只有两端共同出现在显著通路/网络中的关系才被认为获得功能支持。

公开代码只有 `save_all_regl`，把每个 spot 的矩阵逐个写成 CSV；没有找到论文所述“聚类平均—置换检验—DAVID”完整下游实现。因此这一段是 Paper exact / Code not found，无法从仓库重跑论文 chord/Sankey 结果。

### 8. 五张主图的证据链

- Fig. 1 定义层级结构：spot 内分子图、跨图匹配、双模态 attention、spot 间双上下文 GAT、对比学习与下游解释。
- Fig. 2 在模拟数据中给出已知空间域和预设基因—蛋白块。作者报告在 $\sigma_5$ 下 ARI=0.99，并恢复 91.06% 真值关系；这验证的是特定仿真设定。
- Fig. 3 在有人工注释的人淋巴结上，SMOReg 的 ARI=0.33，高于图中其他方法，并结合 CXCL13–CXCR5、CCL21–CCR7/CD4 解释 capsule/paracortex。
- Fig. 4 在无真值的人扁桃体上使用 Moran’s I、Silhouette 和 Calinski–Harabasz 等内部指标，报告 SMOReg 分开 GC light/dark zones，并提出 STAT3–CD151 与 VPREB3–CD19 等关系。
- Fig. 5 在小鼠胸腺 Stereo-CITE-seq 中得到六层空间结构，并用 RAG1、SATB1、PCNA、CD106、CD79B、KRT5 等 marker 解释。

这些图支持“作者数据上的聚类和候选机制”，不能把亲和弦图直接表述为分子 A 调控分子 B 的实验事实。

### 9. 论文—代码对应表

| 机制 | 代码入口 | 对应程度 |
|---|---|---|
| 分子图读取、表达 KNN 合并 | `preprocess.py` | Partial；GO/STRING 文件未提供，且代码多一层表达 KNN |
| 一层共享 GCN | `graph_model.py::Siamese_Gconv/Gconv` | Partial；传播存在，论文 ReLU 未见于实现 |
| 双线性 affinity | `affinity_layer.py::Affinity` | Exact |
| top-1 跨图卷积 | `graph_model.py::CGM` | Exact |
| 双模态 attention | `graph_model.py::AttentionLayer` | Exact 骨架 |
| WNN→空间两层 GAT | `Typing_Garph` | 设计 Exact；公开输入管线断裂 |
| 打乱负样本 + BCE | `Typing_Garph`、`main_exp_data.py` | Partial；代码判别器是 bilinear，论文写两层 MLP |
| 域特异置换检验和 DAVID | Not found | 只有 spot affinity CSV 导出 |

### 10. 当前复现结论

本工作区已取得论文正文、39 张 OCR 图像和公开源码快照，但 Wiley 补充 PDF `advs75574-sup-0001-SuppMat.pdf` 仍返回 403。代码快照证明核心亲和、硬匹配、attention、GAT 和对比骨架真实存在；同时也暴露缺配置、缺数据/先验文件、函数签名不一致和 WNN 路径被注释等阻断。故合理结论是：**机制可核对，发布快照不可直接端到端复现，数值结果未重跑**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SMOReg: Summary

**Full title**: Decoding Spatial Heterogeneity and Multi-Omics Regulation with Hierarchical Graph Learning
**Journal**: Advanced Science | **Year**: 2026 | **DOI**: 10.1002/advs.75574
**Authors**: Jiazhou Chen, Jiahui Xie, Yi Liao, Junyu Li, Longqi Liu, Xin Gao, Hongmin Cai
**Affiliations**: Guangdong University of Technology, South China University of Technology, BGI-Shenzhen, KAUST

---

### Motivation & Novelty

#### Biological Problem

Tissues are organized into spatial domains — functionally distinct compartments defined by characteristic cell types, molecular states, and intercellular signaling programs. These domains underlie fundamental biological processes ranging from immune responses (germinal center B cell maturation, T cell zone organization) to developmental patterning (thymus cortex-medulla layers). Disruption of these spatial compartments drives pathologies including cancer and chronic inflammation.

Spatial multi-omics technologies (DBiT-seq, SM-Omics, SPOTS, Stereo-CITE-seq, spatial-CITE-seq) now enable simultaneous measurement of RNA and protein from the same tissue section. The key insight SMOReg addresses: **spatial heterogeneity is not just about expression differences within a single modality — domain boundaries often arise from coordinated cross-omics regulatory behavior** (e.g., CCL21–CCR7 in lymph node paracortex, VPREB3–CD19 in germinal center dark zone). Existing methods fail to reveal this regulatory logic.

#### Why Prior Methods Fall Short

| Method | Journal | Year | Limitation |
|--------|---------|------|-----------|
| SpatialGlue | Nature Methods | 2024 | Fuses modalities via dual-attention but does not infer cross-omics regulatory mechanisms |
| COSMOS | Nature Communications | 2025 | Assigns modality weights via static Seurat WNN; no regulatory inference |
| MISO | Nature Methods | 2025 | Outer-product modality fusion; no explicit regulatory output |
| spaMultiVAE | Nature Methods | 2024 | Dependency-aware generative model; captures spatial correlations but not regulatory relationships |
| Seurat WNN | Cell | 2021 | Non-spatial; no regulatory inference |
| totalVI | Nature Methods | 2021 | Non-spatial probabilistic model; no cross-omics regulatory output |
| MultiVI | Nature Methods | 2023 | Non-spatial; no regulatory inference |
| STAGATE | Nature Communications | 2022 | Single-modality (transcriptomics); GNN-based spatial domain ID only |
| MENDER | Nature Communications | 2024 | Single-modality; fast but no multi-omics or regulatory output |
| SEDR | Genome Medicine | 2024 | Single-modality; no multi-omics or regulatory inference |
| SFINN | Bioinformatics | 2024 | Spatial GRN inference but transcriptomics-only |
| SCRIPro | Bioinformatics | 2024 | Multi-omics GRN but relies on predefined epigenomic reference motifs |
| CeSpGRN | bioRxiv | 2022 | Spatial context as distance-based smoothing, not explicit regulatory modeling |

The fundamental gap: **no existing method jointly identifies spatial domains AND infers interpretable cross-omics (gene–protein) regulatory mechanisms specific to each domain** from spatial multi-omics data without predefined reference motifs or manual labels.

#### Key Contributions

1. **Hierarchical graph modeling**: explicitly connects intracellular regulatory mechanisms (intra-spot) to tissue-level spatial organization (inter-spot) in a single framework
2. **Cross-graph matching**: automatically learns domain-specific gene–protein interaction strengths via a bilinear affinity layer — no predefined motif databases required
3. **Dual-context contrastive learning**: uses both spatial proximity and functional (WNN) proximity as complementary views, enabling sharp delineation of fine-grained structures (e.g., GC light vs dark zones) that are spatially ambiguous

---

### Method Overview

SMOReg (Spatial Multi-Omics Regulation) is a hierarchical graph learning framework with two coupled modules:

#### Intra-Spot Module (per-spot cross-omics regulation)
For each tissue spot containing $N_g$ highly variable genes and $N_p$ proteins:
- **GCN encoders**: separate Graph Convolutional Networks on biologically curated GGI (Gene Ontology Jaccard similarity) and PPI (STRING > 0.9 confidence) graphs refine expression signals through established molecular pathway topology — effectively performing graph-based denoising without explicit imputation
- **Cross-graph affinity matching**: a trainable bilinear layer $B_{i,j} = \sigma((h_i^g)^\top W_\text{aff} h_j^p)$ computes pairwise gene–protein affinity scores, assembling a $N_g \times N_p$ affinity matrix $\mathbf{B}$. Hard argmax selection propagates the most regulatory-relevant cross-omics features bidirectionally (cross-graph convolution)
- **Dual-attention fusion**: learned attention weights $\alpha^g, \alpha^p$ adaptively combine gene- and protein-derived spot representations, making the model robust to modality-specific noise

#### Inter-Spot Module (spatial domain learning)
- **Dual-context graphs**: spatial proximity graph (radius-based Euclidean neighbors) + feature proximity graph (WNN on both omics layers)
- **GAT encoding**: two-layer Graph Attention Network with layer-specific graph use (Layer 1: feature neighbors; Layer 2: spatial neighbors) — attention mechanism prevents over-smoothing at domain boundaries
- **Self-supervised contrastive training**: DGI-style objective over 100 epochs; negatives from shuffled node features; no cluster labels required

#### Downstream Analysis
After training: per-domain affinity matrices averaged → permutation test ($p < 0.05$) identifies spatially specific gene–protein pairs → DAVID enrichment maps to KEGG/GO/Reactome pathways → visualized as chord diagrams (pairwise pairs) and Sankey-bubble plots (pathway enrichment).

Key biological assumption: the affinity matrix $\mathbf{B}$ receives top-down gradient signals from the inter-spot contrastive objective — regulatory pairs emerge as those most predictive of spatial domain identity, not those with highest raw correlation.

---

### Evaluation

#### Datasets
| Dataset | Technology | N spots | Genes | Proteins | Ground Truth |
|---------|-----------|---------|-------|----------|-------------|
| Human lymph node (SpatialGlue, Long et al. 2024; GSE263617) | 10x Visium CytAssist | 3,484 | 18,085 → 3,000 HVGs | 31 | Expert H&E annotation (7 anatomical compartments) |
| Human tonsil (Liu et al. 2023; GSE213264) | Spatial-CITE-seq | 2,492 | 28,417 → 3,000 HVGs | 273 | None (unsupervised metrics) |
| Mouse thymus (new; STOmics portal) | Stereo-CITE-seq | 3,393 | 27,445 → 3,000 HVGs | 106 | None (unsupervised metrics) |

#### Baselines (10 methods)
Spatial multi-omics: SpatialGlue, COSMOS, MISO, spaMultiVAE
Non-spatial multi-omics: Seurat WNN, totalVI, MultiVI
Spatial transcriptomics-only: STAGATE, SEDR, MENDER

#### Quantitative Results

**Simulated data** (5 domains, σ1–σ8 noise, 3000 genes, 200 proteins):
- SMOReg ARI = 0.99 at σ5 (moderate noise); best-in-class at every noise level (σ1–σ8)
- SMOReg retains ARI ~0.85 at σ8 (200% noise); next-best drops to ~0.45
- Regulatory recovery: 91.06% of ground-truth gene–protein pairs recovered (unique capability — no baseline provides this)

**Human lymph node** (7-metric evaluation, k=6–10 clusters):
- SMOReg ARI = 0.33 (vs. SpatialGlue 0.29, next-best; all others ≤ 0.25)
- SMOReg best across all 7 metrics (AMI, ARI, NMI, Homogeneity, Completeness, V-measure, MI) in box-plot analysis

**Human tonsil** (unsupervised metrics):
- Moran's I = 0.91 (vs. spaVAE 0.63, second-best); 1.4× improvement over next-best
- Silhouette Index = 0.45 (vs. spaVAE ~0.21)
- Calinski-Harabasz Index = 1.06 (vs. MENDER ~0.79)
- **Key biological result**: only SMOReg separates germinal center light zone (STAT3-CD151) and dark zone (VPREB3-CD19) — a histologically validated yet computationally inaccessible two-layer structure

**Mouse thymus** (unsupervised metrics):
- Moran's I = 0.84 (vs. STAGATE 0.65, second-best)
- Six anatomically accurate layers from subcapsular to medulla, validated by PCNA, RAG1, SATB1, CD106, CD79B, KRT5 markers

#### Biological Validation Highlights
- **Lymph node**: CXCL13–CXCR5 (capsule B cell activation), CCL21–CCR7 (paracortex T cell chemotaxis), CCL21–CD4 (ERK1/2 cascade), CD22–FABP4/CD19 (adipose-immune link)
- **Tonsil GC dark zone**: VPREB3–CD19 (pre-BCR signaling, SHM initiation) — supported by STRING database and pre-BCR biology
- **Tonsil GC light zone**: STAT3–CD151 (B cell migration for affinity selection) — supported by GeneCards transcriptional evidence
- **Thymus capsule**: COL1A1–CD49d (ECM-receptor interaction, KEGG pathway)
- **Thymus medulla**: H2-D1–LY108 (MHC I–SLAM receptor, central tolerance), CD74–CD63 (MVB antigen processing)

#### Ablation Study
Ablation without cross-graph matching (SMOReg_wo_cross_matching) shows significant quantitative decline and loss of fine-grained anatomical resolution (Figs S15-16, suppmat inaccessible). Sensitivity to WNN neighbor number k is low across a reasonable operational range (Fig S17, suppmat inaccessible).

---

### Reproducibility Rating: 2/5

**Rationale**: The method is described with sufficient mathematical detail to reimplement from the paper alone. All three validation datasets are publicly available (two via GEO accessions, one via STOmics portal). However:
- **No code released** as of May 2026 — the paper was accepted April 2026 and lacks a code availability statement
- **Critical hyperparameters not reported** in the main text: Jaccard threshold τ for GGI edges, embedding dimension d, learning rate, optimizer type, WNN neighbor number k — all deferred to supplementary Notes S1/S4/S5
- **Supplementary materials inaccessible** (HTTP 403 from Wiley) — ablation numbers, sensitivity analysis, and implementation details cannot be verified
- **Argmax operation in cross-graph convolution** is non-differentiable; the paper does not describe how gradient flow is handled in practice, which would require code to verify
- **Simulation details** (Note S1) are inaccessible, so the benchmark cannot be independently reproduced

A researcher could implement SMOReg from the paper but would need to make several undisclosed design choices and cannot verify hyperparameter values against the published experiments. Code release would raise this to 4/5.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
