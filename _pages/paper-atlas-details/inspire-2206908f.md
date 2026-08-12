---
layout: default
permalink: /paper-atlas/inspire-2206908f/
title: "INSPIRE"
nav: false
description: "INSPIRE 同时解决空间转录组多切片的三个问题：用图神经网络保留每张切片的空间邻域，用带截断的对抗学习去除切片或平台差异，再用共享的非负空间因子和基因载荷解释组织结构。输出既有适合聚类和轨迹分析的共享表示 Z，也有每个细胞的空间因子比例 \\beta 与可解释基因程序 \\mu。"
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
    <h1>INSPIRE</h1>
    <p>Interpretable, flexible and spatially aware integration of multiple spatial transcriptomics datasets from diverse sources</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-026-02579-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## INSPIRE 方法中文解读

### 一句话理解

INSPIRE 同时解决空间转录组多切片的三个问题：用图神经网络保留每张切片的空间邻域，用带截断的对抗学习去除切片或平台差异，再用共享的非负空间因子和基因载荷解释组织结构。输出既有适合聚类和轨迹分析的共享表示 $Z$，也有每个细胞的空间因子比例 $\beta$ 与可解释基因程序 $\mu$。

### 为什么普通批次校正不够

多个空间转录组数据集可能来自不同供体、切面、技术、条件或发育时期。真正共享的结构应当对齐，例如不同脑切片中的皮层层次；只在某张切片存在的结构则应保留，例如小脑、嗅球或创伤区域。普通对抗批次校正若强迫所有细胞完全混合，会把这些切片特异生物学错误消除；只做空间 NMF 又不能处理强批次效应。

INSPIRE 将“共享表示”和“可解释分解”放在同一个训练目标中：GNN 编码器读取表达与空间图，对抗器鼓励相邻切片混合，NMF 风格解码器约束表示保留可解释的组织因子。

### 输入预处理与空间图

输入是多个 AnnData 对象。`utils.py:14-110` 执行质控、共同高变基因选择、归一化与对数转换，并保留原始计数和 library size。GAT 路径在半径邻域上构造全图及邻域表达相似度（`112-145`）；LGCN 路径先构图，再预聚合节点特征供小批量训练（`146-249`）。

这意味着结果依赖共同基因集合和距离阈值。跨技术整合若共享基因很少，模型只能利用交集训练；论文中的“基因插补到两万多个基因”还需要从高覆盖数据迁移和额外分析步骤，并不是核心网络凭空生成未输入的基因载荷。

### 两种编码器：GAT 与 LGCN

中等规模数据使用 GAT：注意力沿空间邻接传播表达信息，输出低维 $Z^s$。GAT 全批次版本会把邻接和成对余弦相似矩阵放到设备上，规模较大时内存昂贵。

大数据使用 LGCN：空间邻居信息预先聚合为节点特征，再以 mini-batch 的轻量网络训练，避免保存全局成对矩阵。`Model_GAT` 位于 `model.py:13-243`，`Model_LGCN` 位于 `247-518`；网络结构分别在 `networks.py:133-213` 与 `215-304`。两者共享整体目标，但几何损失的实现并不完全相同，因此不能把 LGCN 仅理解为 GAT 的无损分块版本。

### 对抗整合与 discriminator clamping

对 $S$ 个按顺序输入的切片，标准模型建立 $S-1$ 个判别器，判别相邻切片的表示。判别器学习区分来源，编码器则让后一张切片看起来像前一张，从而消除技术差异。

关键设计是把判别器分数截断在 $[-m,m]$，默认 $m=5$。共享细胞的判别分数处在可优化范围，继续收到对齐梯度；极易区分的切片特异细胞达到边界后，梯度被截断，不再被强制拉向另一切片。这使“可对齐部分”和“应保留部分”能够自适应分开。

代码 `model.py:123-170` 显示前 100 步是 warmup，不截断；之后才对判别器与编码器损失使用 `torch.clamp`。这个 warmup 是实现细节。标准版只连接相邻切片，另有 `Model_GAT_withCS2discriminators` 支持更多成对判别器，但不是默认类。

### 空间因子与共享基因程序

编码后的细胞表示经 softmax 得到 $K$ 维比例

$$
\beta_i^s=\operatorname{softmax}(f_\beta(Z_i^s)),
$$

共享参数矩阵经按基因 softmax 得到非负载荷 $\mu$，每个因子是一套基因分布。期望计数以 library size、因子混合与切片特异基因偏移共同构造：

$$
\lambda_{ig}^s=L_i^s\exp\left[\log((\beta_i^s\mu)_g)+\gamma_g^s\right].
$$

Poisson 负对数似然让 $\beta\mu$ 重建计数；共享 $\mu$ 使同一因子在不同切片具有共同解释。`networks.py:153-205` 和 `240-299` 实现因子、softmax 与解码。

代码还学习每细胞的 $\alpha$ 偏移并截断至 $[-0.1,0.1]`（`networks.py:183,272`），但主重建式使用的是切片标签索引到的 $\gamma$；这类额外网络输出与论文简化公式需要分开描述。

### 完整训练目标

代码目标由五部分组成：

$$
\mathcal L=\mathcal L_{feature}+\mathcal L_{Poisson}
+\lambda_{geom}\mathcal L_{geom}
+\mathcal L_{factor}+\mathcal L_{adv}.
$$

- feature autoencoder 保留节点表达信息；
- Poisson 重建连接空间因子与原始计数；
- geometry loss 让 $Z$ 的余弦关系接近输入空间邻域关系；
- factor prior 避免所有细胞只使用少数因子；
- adversarial loss 对齐切片。

`model.py:135-172` 是 GAT 版本的直接组合，默认 `coef_geom=0.02`，其余主要系数为 1。优化器对主网络使用 Adamax、对判别器使用 Adam。记录最终损失时，`model.py:185` 错把 `gan_loss` 写入 `geom_loss` 字段；这不改变训练，但会污染诊断日志。

LGCN 在 `model.py:368-404` 以 batch 内输入特征余弦矩阵作为几何目标。旧分析指出 beta prior 的归一化含硬编码 `batch_size * 4`；这使切片数不是 4 时量纲不一致，属于可复现边界而不是论文方法本身。

### 输出该怎样使用

`eval` 把拼接后的 $Z$ 写入 `adata.obsm['latent']`，将每个 $\beta_k$ 写入 obs，并返回基因载荷表。$Z$ 用于邻居图、聚类、UMAP、PAGA 或切片配准；$\beta$ 作为连续空间因子图；$\mu$ 的高载荷基因用于标记、GO 和通路解释。

空间因子并非预定义细胞类型。一个因子可能代表细胞群、组织层、状态或过程，必须结合空间分布、载荷基因与外部注释验证。因子数 $K$ 是用户参数；论文建议用 factor diversity 等指标避免因子高度重复，但不存在对所有组织通用的唯一最优 $K$。

### 图与应用证据链

Fig. 1 说明 GNN、clamped adversarial integration 与 NMF 输出。Fig. 2 用模拟和 DLPFC 检查批次校正、层结构与因子解释。Fig. 3 用部分重叠脑切片展示共享皮层被对齐而小脑/嗅球被保留。Fig. 4 检查跨 MERFISH、Slide-seqV2、seqFISH 和 Stereo-seq 的技术整合与插补。Fig. 5–6 展示 Xenium 乳腺癌微环境和多时期胚胎的大规模分析。后续图覆盖跨条件创伤、发育动态和 3D 重建。

这些应用支持模型的灵活性，但下游 COMMOT、差异表达、GO、组织配准和 3D 重建不是 `Model_GAT/Model_LGCN.train()` 自动完成的核心步骤。详细主图及补图证据见 `figure_analysis.md`。

### 版本与复现边界

- 本地 `.repo_source` 记录克隆提交 `005d447374fea2820789d82936194690a40f69f0`，但当前嵌套仓库 HEAD 为 `206cc19ca89d985245ca204fbc86772e5c2446d0`；本工作区分析以当前 HEAD 源码为准，并保留来源漂移。
- `environment.yml` 锁定的是 Python 3.8.15、PyTorch 1.12.1 等较旧环境；在新 CUDA/Python 上重建可能需要调整。
- 论文含大量补充图和分析流程，仓库核心包加 benchmark scripts 并不等于完整的一键复现；数据下载、R 工具和特定图表脚本仍是外部依赖。
- GAT 的全矩阵内存和 LGCN 的近似/归一化差异决定了两种规模路径不能直接期待数值完全一致。
- 跨平台 `different_platforms=True` 会改变 LGCN 解码输入；用户必须明确设置，代码不会自动可靠推断平台差异。

### 最终理解

INSPIRE 的关键不是单独发明 GNN、对抗学习或 NMF，而是让三者互相约束：空间图保护局部组织结构，截断判别器只对齐可共享部分，NMF 解码把整合表示还原成可解释空间因子与基因程序。它适合多切片、多平台和大规模 ST，但结果仍依赖基因交集、空间图、因子数、切片顺序和选择的 GAT/LGCN 路径；完整生物结论需要核心模型之外的下游验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## INSPIRE: Summary

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) technologies profile gene expression with spatial context, enabling mapping of tissue architecture, cell-type organization, and biological processes. As ST datasets multiply across technologies, donors, conditions, and developmental time points, integrating them becomes essential for building comprehensive tissue atlases and discovering shared biological principles.

The core challenge is that **unwanted technical variation** (batch effects, platform differences, sequencing depth) confounds **biological signal** when combining multiple ST sections. This is especially difficult when:
- Sections come from different technologies with different gene panels (MERFISH vs Slide-seqV2)
- Sections contain partially overlapping spatial structures (sagittal vs coronal brain)
- Sections have condition-specific biology that should be preserved (wound vs uninjured skin)

#### Limitations of Existing Methods

| Method | Journal/Year | Limitation |
|--------|-------------|------------|
| SpiceMix | Nature Genetics 2023 | Interpretable NMF but no batch correction; fails with strong batch effects |
| NSFH | Nature Methods 2023 | Spatial NMF but restricted to single/replicate sections |
| Harmony | Nature Methods 2019 | No spatial modeling; suboptimal for ST |
| Seurat | Cell 2021 | No spatial modeling; suboptimal for ST |
| LIGER | Cell 2019 | NMF-based but no spatial modeling |
| PRECAST | Nature Communications 2023 | Shared Gaussian mixture model; limited under strong section-specific effects |
| GraphST | Nature Communications 2023 | Requires prior spatial registration |
| MEFISTO | Nature Methods 2022 | Weak integration; high computational cost |
| PASTE | Nature Methods 2022 | Alignment only; no interpretable factors |

#### INSPIRE's Unique Contributions

1. **Adversarial learning with discriminator clamping**: Adaptively separates shared biological variation from section-unique signals. The clamping mechanism (m=5) prevents incorrect mixing of section-unique cell populations — a key innovation over standard domain adversarial training.

2. **Integrated NMF across sections**: Combines adversarial alignment with NMF to produce interpretable spatial factors and gene programs that are consistent across sections and unconfounded by batch effects.

3. **Scalability**: Lightweight GCN variant enables analysis of datasets with hundreds of thousands to millions of cells (demonstrated on 560K Stereo-seq spots, 280K Xenium cells).

4. **Versatility**: Single framework handles within-technology, cross-technology, cross-condition, and cross-developmental-stage integration.

---

### Method Overview

INSPIRE is a deep learning framework that unifies adversarial learning and non-negative matrix factorization (NMF) for interpretable, spatially aware integration of multiple ST datasets.

**Key components:**
- **GNN encoder** ($f_Z$): Maps gene expression + spatial neighborhood graph to a 32-dimensional shared latent space. Two variants: Graph Attention Network (GAT) for moderate datasets, Lightweight GCN (LGCN) for large datasets.
- **Adversarial integration**: S-1 discriminators guide the encoder to align representations across sections while preserving section-unique biology via discriminator clamping.
- **Integrated NMF**: Decoder $f_\beta$ produces K spatial factor proportions (β) per cell; shared gene loading matrix μ encodes gene signatures. Poisson likelihood models count data.
- **Batch correction**: Section-specific gene offsets γ absorb residual technical variation.

**Outputs:**
- Latent representations Z (for clustering, trajectory inference)
- Spatial factor maps β (for fine-grained tissue architecture)
- Gene loading matrix μ (for biological interpretation, pathway enrichment)

See `doc_method.md` for mathematical details and `doc_code.md` for implementation specifics.

**Computational pipeline:**
1. Preprocess: QC filter → HVG selection (top 6000, intersection) → log-normalize
2. Build spatial graphs (radius-based adjacency)
3. Train: 10,000 steps, Adamax optimizer, adversarial + NMF + AE + geometry losses
4. Evaluate: extract Z, β, μ for downstream analysis

---

### Evaluation

#### Datasets

| Dataset | Technology | Cells/Spots | Genes | Application |
|---------|-----------|-------------|-------|-------------|
| Human DLPFC | Visium | 47,322 spots | 33,525 | Benchmarking, cortical layers |
| Mouse brain (3 sections) | Visium | 8,820 spots | 14,801–31,040 | Partially overlapping structures |
| Mouse brain | MERFISH + Slide-seqV2 | 44,950 + 29,866 | 1,077 shared | Cross-technology integration |
| Mouse embryo | seqFISH + Stereo-seq | 14,185 + 5,880 | 347 shared | Cross-technology, gene imputation |
| Mouse skin (wound healing) | Visium | 948 + 1,671 spots | 32,272 | Condition-specific biology (uninjured vs day 7 wound) |
| Human breast cancer | Xenium | 283,063 cells | 313 | Tumor microenvironment, scalability |
| Mouse organogenesis | Stereo-seq (8 sections) | 514,415 spots | >220,000 | Spatiotemporal atlas |
| Mouse hypothalamus | MERFISH (2 sections) | 5,557 + 5,488 cells | 155 | 3D reconstruction |
| Mouse hippocampus | STARmap PLUS (2 sections) | 8,202 + 8,186 cells | 2,766 | 3D reconstruction |
| Mouse embryo (3D) | Stereo-seq (5 sections) | 567,381 spots | >270,000 | 3D reconstruction |

#### Metrics

- **ARI** (Adjusted Rand Index): Agreement between predicted domains and manual annotations
- **NMI** (Normalized Mutual Information): Correlation between predicted and annotated labels
- **ASW** (Average Silhouette Width): Cluster separation in latent space
- **iLISI**: Integration performance — effective number of datasets in neighborhood (higher = better mixing)
- **cLISI**: Biological variation preservation — effective number of cell types in neighborhood (lower = better)
- **Factor diversity**: % unique genes in top-10 across factors (higher = less redundancy)
- **Factor coherence**: NPMI of top-10 gene pairs per factor (higher = more interpretable)
- **Spatial discontinuity**: % spots without same-domain neighbors (lower = more spatially coherent)

#### Key Results

**Simulation benchmarking (Fig. 2a,b):** INSPIRE consistently achieved best ARI, ASW, and factor recovery across all batch effect levels. SpiceMix and NSFH showed declining performance as batch effects increased.

**Human DLPFC (Fig. 2c,f,g):** INSPIRE achieved best ARI and ASW in both within-donor (4 sections) and across-donor (12 sections) integration. Recovered L1-L6 cortical layers with high accuracy. Factor diversity and coherence scores exceeded SpiceMix and NSFH.

**Mouse brain (Fig. 3):** Successfully integrated sagittal anterior, sagittal posterior, and coronal sections with only partially overlapping structures. Discriminators were active on shared isocortex, inactive on section-unique cerebellum — demonstrating adaptive alignment. iLISI scores significantly higher than SpiceMix, NSFH, PRECAST.

**Cross-technology (Fig. 4):** MERFISH + Slide-seqV2 integration enabled cortical layer detection in Slide-seqV2 data by leveraging MERFISH's higher quality. Gene imputation from Stereo-seq to seqFISH expanded coverage from 351 to >20,000 genes, enabling differential expression analysis.

**Xenium breast cancer (Fig. 5):** Identified 3 pathologist-annotated tumor domains (DCIS 1, DCIS 2, invasive tumor) and revealed fine-grained myoepithelial and endothelial subpopulations with distinct gene signatures. Completed analysis of 280K cells in 8 minutes.

**Mouse organogenesis (Fig. 6):** Integrated 8 Stereo-seq sections (E9.5–E16.5), identified consistent spatial regions across developmental stages, quantified organ-level dynamics, and uncovered developmental programs (choroid plexus, smooth muscle cells).

**3D reconstruction (Fig. 7):** INSPIRE achieved best rigid alignment performance vs PASTE, Moscot, CAST across MERFISH, Visium, and STARmap PLUS benchmarks. INSPIRE embeddings also improved nonrigid alignment when used as input to Moscot and CAST.

---

### Reproducibility

**Rating: 4/5**

**Justification:** Code is publicly available on GitHub (https://github.com/jiazhao97/INSPIRE) and Zenodo (doi:10.5281/zenodo.18330972). All datasets are publicly available. The paper provides detailed hyperparameter settings. The main limitation is that some large datasets (Stereo-seq organogenesis, Xenium breast cancer) require significant GPU memory and compute time.

**Environment setup:**
```bash
conda env create -f environment.yml
conda activate INSPIRE
pip install INSPIRE
```
Key dependencies: Python 3.8.15, PyTorch 1.12.1, Scanpy 1.8.2, AnnData 0.9.2

**Data availability:** All 11 datasets are publicly available (see paper Data Availability section). Links provided for DLPFC (spatialLIBD), 10X Genomics, Brain Image Library, Broad Single Cell Portal, CNGB STOMICS, GEO (GSE178758, GSE147747), Zenodo, Dryad.

**Common pitfalls:**
- For large datasets (>100K cells), use `Model_LGCN` with `calculate_node_features_LGCN()` preprocessing — `Model_GAT` will run out of GPU memory
- The `different_platforms=True` flag is needed when integrating datasets with very different data quality (e.g., MERFISH + Slide-seqV2)
- HVG intersection can be very small when integrating imaging-based (limited gene panel) with sequencing-based data — use `limit_num_genes=True` in `preprocess()`
- LGCN beta_loss has a hardcoded `batch_size * 4` denominator — may need adjustment for non-4-section analyses

**Strengths:**
- Clean, well-documented Python package with clear API
- Two model variants for different scales
- Comprehensive benchmark scripts for all compared methods
- Detailed tutorial website (inspire-tutorial.readthedocs.io)

**Weaknesses:**
- No automated K selection (requires manual tuning based on factor diversity)
- Integration relies on shared genes — dataset-specific genes are excluded
- No uncertainty quantification for integration results
- LGCN beta_loss denominator bug for S≠4 sections

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
