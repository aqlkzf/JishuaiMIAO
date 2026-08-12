---
layout: default
permalink: /paper-atlas/tacit-76ef313c/
title: "TACIT"
nav: false
description: "TACIT 先用专家签名把细胞投影成各类型 CTR，再借微簇排序和分段回归为每种类型寻找数据自适应阈值，最后用相关 marker 子空间中的 clean 邻居拆分多重阳性细胞；它无需训练集且可解释，但可靠性仍取决于预处理、签名和阈值稳定性。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>TACIT</h1>
    <p>Deconvolution of cell types and states in spatial multiomics utilizing TACIT</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-58874-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TACIT 方法中文解读：用自适应阈值完成空间单细胞注释

### 1. 方法解决什么问题

TACIT（Threshold-based Assignment of Cell Types from Multiplexed Imaging DaTa）用于空间蛋白组、空间转录组和同切片多模态数据的细胞类型/状态注释。它接收已经完成细胞分割、质量控制和归一化的表达矩阵，因此不是图像分割算法。它不需要带标签训练集，但需要专家提供 marker 签名。

论文图 1 的主线是：微聚类稳定信号；计算 Cell Type Relevance（CTR）；用分段回归从当前数据估计每个类型的阈值；最后用 KNN 拆分多重阳性细胞。当前 R 代码中的 `TACIT()` 与 `threshold_function()` 实现了这条骨架。

### 2. 输入与输出

输入包括：

- 细胞表达矩阵 $A\in\mathbb{R}^{N\times P}$，含 $N$ 个细胞和 $P$ 个蛋白或基因。论文对蛋白使用 z-normalized 值，对 RNA 使用 log-normalized 值。
- 类型签名矩阵 $S\in[0,1]^{K\times P}$，每行代表一个候选类型，非零权重表示 marker 对该类型的支持强度。

输出给出每个细胞的最终标签、各候选类型的二值阳性结果和数据自适应阈值。标签可以是一个明确类型、`Mixed` 或 `Others`。

“无需训练数据”不等于“无需先验”。候选类型与 marker 的完整性、特异性仍然限定了 TACIT 能识别什么。当前代码还把用户传入的矩阵直接用于 CTR，因此输入尺度会直接影响分数和阈值。

### 3. 为什么先做微聚类

逐细胞表达容易受稀疏性和测量噪声影响。TACIT 先形成许多小微簇，再以微簇 CTR 中位数寻找低相关群和高相关群。论文建议平均微簇约占总体的 0.1%–0.5%，以兼顾稳健性和稀有类型。

微聚类只是阈值估计工具，不是最终类型发现。当前代码先对 Seurat 对象做 CLR 标准化，再走 PCA、UMAP、邻接图和聚类；CLR 分支只服务于微聚类，CTR 仍使用用户输入的预处理值。

这里存在一个必须保留的论文—代码差异：论文方法部分称使用 Louvain，当前快照调用 `FindClusters(..., algorithm=4)`，该选项对应 Leiden。复现时应记录实际运行路径，不能把二者写成完全一致。

### 4. CTR：表达与签名的加权匹配

TACIT 用矩阵乘法得到细胞对各类型的相关性：

$$
\Gamma=A S^{\mathsf T},
$$

其中

$$
\Gamma_{ik}=\sum_{p=1}^{P}A_{ip}S_{kp}.
$$

例如，一个细胞在 CD3、CD20、CD68 上的值为 $(2.0,0.2,0.1)$，T 细胞签名为 $(1,0,0)$，B 细胞签名为 $(0,1,0)$，那么 T 与 B 的 CTR 分别为 2.0 和 0.2。若一个类型包含多个非零 marker，CTR 就是对应表达的加权和。

CTR 不是概率，没有天然的 0–1 范围。未经统一预处理时，它也不能直接跨数据集比较。TACIT 的关键因此不是固定 cutoff，而是为当前数据的每个候选类型分别估计阈值。

### 5. 分段回归怎样构造低、高相关群

对一个候选类型，`threshold_function()` 先计算每个微簇的 CTR 中位数并排序。低值端通常由不相关微簇构成，高值端则应富集目标类型。代码分别拟合含 1、2、3 个断点的分段回归模型，以 AIC 选择模型，再依据断点与分段斜率定义低相关组（LRG）和高相关组（HRG）。代码还处理末段斜率小于 0.05 的平坦尾部，避免机械地把它解释为持续增强。

分段回归不是最终分类器，只用于构造两个参考分布。若类型极少、marker 不特异或候选类型高度重叠，微簇排序和断点都可能不稳定。

### 6. 阈值如何确定

代码在 CTR 第 5 到第 99 百分位之间建立 1000 个候选阈值。对每个阈值 $t$，同时计算 LRG 中高于阈值的比例与 HRG 中低于阈值的比例，选择两类误分之和最小者：

$$
t_k^*=\arg\min_t\left[P(\Gamma_{ik}>t\mid i\in\mathrm{LRG})+P(\Gamma_{ik}<t\mid i\in\mathrm{HRG})\right].
$$

然后二值化：

$$
B_{ik}=\mathbf{1}(\Gamma_{ik}>t_k^*).
$$

因此，“自适应”具体指阈值按数据集、按类型重新估计，而不是学习一个可直接迁移到新数据集的分类器。

### 7. Clean、Others 与 Mixed

一行 $B_{i\cdot}$ 中的阳性数决定初始状态：

- 恰好一个阳性：`Clean`，直接赋给该类型；
- 零个阳性：`Others`；
- 两个或以上阳性：`Mixed`，进入 KNN 消歧。

`Others` 不一定是新类型，也可能来自签名缺失、低质量或所有 CTR 都偏低。`Mixed` 也不自动等于真实双细胞，只表示现有 marker 和阈值给出了多重支持。论文还允许父类—子类式层级签名，以先粗分、再在相关 marker 中细分亚型。

### 8. KNN 怎样拆分 Mixed 细胞

对一个同时支持多个候选类型的细胞，TACIT 取这些类型签名中非零的 marker，构造“相关 marker 子空间”，以已经明确归类的 clean 细胞作为有标签邻居执行 KNN。这样可避免大量无关特征稀释真正 marker 的距离信号。

当前代码加入 0 到 0.001 的微小随机扰动以减少并列，邻居数取 10 与可用 clean 细胞数中的较小者。因此代码实际邻居上限为 10，不是旧说明曾写的 30。KNN 只能在已有候选类型间消歧；若关键 marker 未进入签名，它不能补回缺失信息。

### 9. 多模态使用方式

论文在同一切片上比较空间 RNA 与蛋白注释。TACIT 可分别注释各模态，也可在适当归一化后合并特征与签名。论文报告全部 marker 下 RNA/蛋白注释一致率为 34%，只看共同 marker 时为 81%。这说明模态一致性强烈受特征覆盖影响，不能简单解释为某个模态绝对正确。

图 5 展示同切片 RNA/蛋白对照，图 6 聚焦三级淋巴结构区域，图 7 展示组合多模态分析。这些结果支持方法可用于多平台，而不是保证任意归一化与任意签名都能直接跨平台迁移。

### 10. 论文中的主要证据

图 2 在 PCF-CRC 和 PCF-HI 蛋白数据上评估 TACIT。PCF-CRC 包含 235,519 个细胞、56 个抗体和 17 个类型，论文报告 recall、precision、F1 为 0.74、0.79、0.75；PCF-HI 上为 0.73、0.79、0.75。图 3 比较更多近期方法和空间分辨率。图 4 展示 Xenium Sjögren's disease 数据应用。MERFISH 基准中，论文报告 TACIT 的 recall、precision、F1 为 0.85、0.87、0.87。

本工作区也保存了补充材料 `41467_2025_58874_MOESM1_ESM.pdf`；其中的补充图包括基准箱线图和 bootstrap 阈值检查。上述结果支持 TACIT 在论文所选数据、预处理、签名和参考标签下具有竞争力并可扩展到百万级细胞，但不是对所有组织和 panel 的无条件保证。

### 11. 论文与代码的对应

| 环节 | 当前代码证据 | 对应判断 |
|---|---|---|
| 微聚类 | CLR、PCA/UMAP、邻接图、`FindClusters` | Partial：目的相同，论文 Louvain、代码 Leiden |
| CTR | `data_anb_matrix %*% t(Signature_matrix)` | Exact |
| 分段回归 | 1–3 断点拟合与 AIC 选择 | Exact |
| 阈值 | 第 5–99 百分位、1000 候选值、误分和最小化 | Exact |
| clean/mixed/Others | 阳性数为 1、>1、0 的分支 | Exact |
| KNN 消歧 | 相关 marker 子空间、clean 参考、最多 10 邻居 | Exact |
| 输入预处理 | 接受用户预处理矩阵，内部 CLR 仅服务聚类 | Partial：代码不替用户强制复现论文预处理 |

### 12. 复现边界

1. 注释空间由签名矩阵定义，未列类型可能进入 `Others` 或被相近类型吸收。
2. CTR 是加权和而非概率；输入尺度变化会改变分布和阈值。
3. 换组织、平台、panel 或过滤方式后，应重新检查阈值稳定性。
4. 当前源码快照没有可核验的 Git commit；本文只描述本地保存代码。
5. 论文写 Louvain、代码运行 Leiden，应显式记录。
6. 上游分割、质量控制和归一化不属于 TACIT。
7. KNN 不会发现签名外的新类型。
8. 输出是注释和空间分布，不构成因果调控或谱系证据。

### 13. 一句话理解

TACIT 先用专家签名把细胞投影成各类型 CTR，再借微簇排序和分段回归为每种类型寻找数据自适应阈值，最后用相关 marker 子空间中的 clean 邻居拆分多重阳性细胞；它无需训练集且可解释，但可靠性仍取决于预处理、签名和阈值稳定性。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## TACIT — Paper Summary

### Method Overview

**TACIT** (Threshold-based Assignment of Cell Types from Multiplexed Imaging DaTa) is an unsupervised cell type annotation algorithm for spatial multi-omics data that requires **no training data**. It operates on two inputs — a CELLxFEATURE expression matrix and a TYPExMARKER expert signature matrix — and assigns cell identities through a multi-step pipeline of microclustering, Cell Type Relevance (CTR) scoring, data-driven thresholding via segmented regression, and KNN deconvolution of ambiguous cells.

**Key algorithmic components**:
1. Microclustering: Groups cells into 0.1–0.5% micro-communities using graph clustering for noise reduction
2. CTR scoring: Matrix multiplication Γ = A × S projects each cell into a cell-type relevance space
3. Segmented regression: Fits piecewise-linear curves to ordered MC medians to identify expression breakpoints (LRG vs. HRG)
4. Threshold optimization: Grid search minimizing combined false-positive and false-negative rates
5. KNN deconvolution: Resolves cells positive for multiple types using clean anchor cells in marker-relevant subspace

The method runs without deep learning, generalizes across assay types (proteomics, transcriptomics, multi-modal), species, organs, and disease states, and scales to 2M+ cells on a 16GB laptop.

---

### Motivation & Novelty

#### Biological Problem

Spatial biology technologies (CODEX/PhenoCycler, Xenium, MERFISH) capture single-cell molecular profiles while preserving tissue architecture, enabling study of cellular neighborhoods, niches, and spatial interactions. The central challenge is **cell type annotation**: mapping each cell to a biologically meaningful identity from sparse multiplex data with 56–280 markers (vs. 20,000 genes in scRNA-seq).

#### Limitations of Existing Approaches

| Method | Type | Limitation | Journal/Year |
|---|---|---|---|
| Louvain | Unsupervised clustering | Resolution-sensitive; language-dependent; fails on rare types with 1 marker | *J. Stat. Mech.*, 2008 |
| CELESTA | Statistical model | Requires extensive per-sample parameter tuning; fails on large datasets (labeled all as Unknown in PCF-HI) | *Nat. Methods*, 2022 |
| SCINA | Semi-supervised signature | Designed for scRNA-seq; collapses under spatial proteomics data scale | *Genes*, 2019 |
| Seurat label transfer | Reference-based | RNA–protein correlation low for immune markers; requires scRNA-seq reference | *Nat. Methods*, 2021 |
| Astir, Tangram, Spatial-ID, STELLAR | Deep learning | Require diverse, comprehensive training data; difficult to generalize | *Cell Syst.*, 2021; *Nat. Methods*, 2021; *Nat. Commun.*, 2022; *Nat. Methods*, 2022 |
| TYPEx | Statistical (benchmark) | Best prior unsupervised method; F1 0.45–0.59 on PCF-CRC | *Nat. Commun.*, 2024 |

#### Unique Contributions

1. **No training data needed**: Uses expert-defined signatures (literature/scRNA-seq), not labeled spatial data
2. **Unbiased thresholding**: Automated data-driven threshold per cell type via segmented regression — no per-marker manual gating
3. **Subspace deconvolution**: Resolves mixed cells using only relevant marker dimensions, suppressing noise from unrelated markers
4. **Multimodal compatibility**: Single framework handles protein, RNA, and combined RNA+protein matrices
5. **Scalability**: FastRunUMAP + parallel thresholding handles 2M cells; designed for standard hardware

---

### Evaluation

#### Datasets

| Dataset | Technology | Cells | Markers | Tissue | Cell types |
|---|---|---|---|---|---|
| PCF-CRC | PhenoCycler (CODEX) | 235,519 | 56 antibodies | Colorectal cancer (140 TMAs) | 17 |
| PCF-HI | PhenoCycler (CODEX) | 2,603,217 | 56 antibodies | Human intestine (64 sections) | 22 |
| MERFISH | Mouse brain spatial transcriptomics | 505,961 (post-filter) | 170 genes | Hypothalamic preoptic region | ~50 |
| Xenium-SjD | Xenium (10x) | ~360,000 | 280 ISH genes | Minor salivary gland, Sjögren's disease | 24 |
| Xenium-GVHD + PCF | Xenium + PhenoCycler same slide | 424,638 | 280 RNA + 36 proteins | Minor salivary gland, GVHD | 22 (RNA), 18 (protein) |

#### Quantitative Results

**Benchmarking (PCF-CRC, compared to CELESTA/SCINA/Louvain):**
- TACIT: Weighted Recall = 0.74, Precision = 0.79, F1 = 0.75 (p < 0.05 vs. all methods)
- Louvain missed 6/17 rare cell types; SCINA identified only 5 total
- Rare cell type correlation: TACIT R = 0.58 vs CELESTA R = 0.24 vs Louvain R = NA

**Benchmarking (PCF-HI, scalability; compared to Louvain only):**
- TACIT: Recall = 0.73, Precision = 0.79, F1 = 0.75
- Louvain: Recall = 0.66, Precision = 0.64, F1 = 0.63
- Rare cell type correlation: TACIT R = 0.76 vs Louvain R = 0.62

**Benchmarking (MERFISH):**
- TACIT: Recall = 0.85, Precision = 0.87, F1 = 0.87
- Rare cell types: TACIT R = 0.94 vs Louvain R = 0.64

**Comparison to 11 recent methods (PCF-CRC, F1):**
- TACIT: 0.74 (Group A), 0.76 (Group B)
- Best alternative: 0.59; range: 0.45–0.59

**MERFISH comparison to 11 methods**: TACIT F1 = 87% (best overall)

**Entropy/Purity**: TACIT consistently achieves lowest entropy and highest purity across all tested resolutions (Leiden/Louvain at multiple r values)

#### Biological Validation

- **Xenium-SjD**: TACIT identified 4 distinct T cell subtypes (CD4+, CD8+, CD8+ Exhausted, T cell progenitors) that Louvain missed; correlation with scRNA-seq R = 0.84 vs Seurat transfer R = 0.49
- **GVHD multimodal**: TACIT identified 22 cell types (RNA) and 18 (protein) vs Louvain's 18 and 14; uniquely identified TRegs, NK cells, vascular/lymphatic endothelial cells critical for GvHD pathophysiology
- **Multimodal agreement**: 34% agreement using all RNA+protein markers; 81% when restricting to markers common to both modalities
- **TLS ROI**: TACIT revealed expected T cell–dendritic cell proximity and PD-1/PD-L1 interactions; Louvain produced only structural cell neighborhoods

---

### Reproducibility

**Rating: 3/5**

**Justification**: The paper provides public benchmark datasets and a GitHub R package, but several reproducibility barriers exist:

**Strengths**:
- Public code: `https://github.com/huynhkl953/TACIT` under CC BY-NC 4.0
- Benchmark datasets publicly downloadable (PCF-CRC at Mendeley, PCF-HI + MERFISH at Dryad)
- Paper reproduction scripts in `Code generate figure/` folder
- Detailed Methods section with equations

**Weaknesses**:
- **No renv/lockfile respected**: `renv.lock` is present but Seurat v5 + segmented v2 + caret dependencies are notoriously difficult to install consistently; no Docker or Conda environment provided
- **Algorithm mismatch**: Code uses Leiden (`algorithm=4`) but paper says "Louvain" throughout — exact microcluster reproducibility requires clarification
- **In-house datasets not available**: Xenium-SjD, Xenium-GVHD are proprietary NIH/USP samples — ~4 of 7 figures are not fully reproducible
- **Source data incomplete**: Zenodo record (https://zenodo.org/records/11397609) contains source data for figures but not the full cell-level annotations needed to reproduce benchmarks
- **R version sensitivity**: Package requires R ≥ 4.0; Seurat 5 API changed significantly from Seurat 4

**Practical notes**:
- Install via `devtools::install_github("huynhkl953/TACIT")` or clone and `R CMD INSTALL`
- Recommended hardware: i5+ CPU, 16GB RAM, 10GB disk
- Common pitfall: supplying un-normalized data — user must pre-normalize (z-score for proteins, log-norm for RNA) before passing to TACIT
- Resolution `r` requires tuning per dataset; paper guidance (0.1–0.5% cells per MC) must be translated to a numeric value manually
- Large datasets (>100k cells): FastRunUMAP path activates automatically

---

### Significance

TACIT fills a practical gap for spatial biology labs that have expert marker knowledge but no labeled training data. It outperforms prior unsupervised methods by ~0.15–0.30 F1 points on benchmark datasets and is the first published tool to handle combined RNA+protein single-slide spatial multi-omics annotation natively. The discovery of under/overrepresented immune populations in GvHD tertiary lymphoid structures — specifically TRegs, NK cells, and PD-1+ T cells — demonstrates translational potential for immunotherapy patient stratification.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
