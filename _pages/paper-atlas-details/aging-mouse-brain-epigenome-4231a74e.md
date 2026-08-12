---
layout: default
permalink: /paper-atlas/aging-mouse-brain-epigenome-4231a74e/
title: "Aging Mouse Brain Epigenome"
nav: false
description: "脑衰老会伴随 DNA 甲基化漂移、转座元件解除抑制、染色质三维结构变化和炎症反应，但以往研究通常只测一种组学、少数脑区或混合细胞。这样难以区分：变化是某一类细胞真正发生的，还是细胞组成改变造成的；同一种细胞在不同脑区是否以同样方式衰老；局部甲基化和三维接触变化能否解释年龄相关基因表达。 本研究建立跨年龄、脑区和模态的单核图谱，把 2、9、18 月龄小鼠作为连续时间点。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Cell · 2026</span>
    </div>
    <h1>Aging Mouse Brain Epigenome</h1>
    <p>Cell-type-specific transposon demethylation and TAD remodeling in aging mouse brain</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.02.015" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 衰老小鼠脑的细胞类型特异转座子去甲基化与 TAD 重塑

### 1. 论文要回答什么问题

脑衰老会伴随 DNA 甲基化漂移、转座元件解除抑制、染色质三维结构变化和炎症反应，但以往研究通常只测一种组学、少数脑区或混合细胞。这样难以区分：变化是某一类细胞真正发生的，还是细胞组成改变造成的；同一种细胞在不同脑区是否以同样方式衰老；局部甲基化和三维接触变化能否解释年龄相关基因表达。

本研究建立跨年龄、脑区和模态的单核图谱，把 2、9、18 月龄小鼠作为连续时间点。2 月龄被用作 young baseline，但作者明确提醒它更接近青春晚期/成年早期而非完全成熟成年期，因此 2→9 月的部分变化可能包含发育成熟成分。论文只把随 2→9→18 月单调变化的信号作为主要年龄轨迹，以降低这一混杂。

### 2. 数据规模与互补模态

- **snmC-seq3**：132,551 个单核全基因组甲基化谱，来自雄性小鼠 8 个脑区；同时测 mCG 和神经元中丰富的 mCH。
- **snm3C-seq**：72,666 个雌性单核，同一个细胞内联合测 DNA 甲基化和染色质接触。
- **snATAC-seq / 10x Multiome companion data**：提供开放染色质和 RNA，用于解释 DMR 与表达变化。
- **MERFISH**：500 基因 panel，7 张冠状切片，共 895,296 个细胞，提供空间表达和前后轴差异。

覆盖脑区包括前/后海马、额叶皮层、杏仁核、伏隔核、导水管周围灰质/脑桥中央灰质、内嗅皮层和尾状壳核。多模态经 CCA/anchor 框架对齐，最终聚焦每个年龄和数据集都至少有 100 个细胞的 36 个 major cell types。

```text
snmC / snm3C 单核数据
  → mapping、ALLC、MCDS tensor、聚类与细胞注释
  → cell type × age × sex pseudo-bulk
      ├─ DMG / DMR / motif / methylation hotspot
      ├─ TE 甲基化矩阵 → LSI → 年龄与细胞类型分离
      └─ 3C 矩阵 → compartment / TAD / loop / ABC enhancer

snATAC + 10x Multiome ───────────────┐
MERFISH 空间表达 ────────────────────┼→ 区域异质性与 age-DEG
7 类表观特征 ───────────────────────┘→ EAT 预测 age-DEG
```

### 3. 从单细胞甲基化到年龄 DMR

单细胞 bisulfite 数据先经 HISAT-3N 映射，保存为 ALLC，再用 ALLCools 构建 cell-by-feature 的 MCDS/Zarr 张量。聚类使用 100 kb genome bins 上的 mCG/mCH，经过特征过滤、后验甲基化率、PCA、t-SNE/UMAP 和 Leiden。snmC 与 snm3C 的整合先选 cluster-enriched features，再做 CCA，寻找 mutual nearest-neighbor anchors；为控制规模，最多抽取每个数据集 100,000 个细胞拟合 CCA，再投影其余细胞。

年龄 DMR 在 cell type × age 的 pseudo-bulk ALLC 上用 DSS beta-binomial multi-factor model 计算。核心过滤包括：$p<0.01$、区域内至少 50% CpG 显著、相邻不足 50 bp 的区域合并、最大与最小年龄的 $\Delta mCG>0.20$，并要求年龄方向单调：

- age-hypo：$mCG_{2m}>mCG_{9m}>mCG_{18m}$；
- age-hyper：$mCG_{2m}<mCG_{9m}<mCG_{18m}$。

雌雄分别调用后，再以均衡覆盖的合并 pseudo-bulk 复核；两性重叠且方向一致才标为 sex-shared。论文主要解释这些较稳健的 sex-shared DMR。

全局 mCG 随年龄只轻微变化，但局部 DMR 高度细胞类型特异：83.6% 的 age-hypo DMR 只见于一种细胞类型。非神经元的 DMR 更多、更长，OPC 尤为突出；88% 的 glutamatergic excitatory neuron 类型有更高比例的 age-hypo DMR。神经元 age-hypo DMR 富集 AP-1/Fos/Jun motifs，胶质 age-hyper DMR 富集 Sox family motifs。这里的 motif 富集提示潜在结合因子，并不等同于直接测得 TF 占位或因果调控。

### 4. 为什么转座元件是关键年龄信号

作者把 mm10 划成不重叠 500 bp windows，汇总所有细胞类型的显著 age-DMS；包含超过 10 个 age-DMS 的窗口定义为 methylation hotspot。3,519 个 age-hypo hotspots 中，染色体 13 的强热点落在 LTR-ERV1-MuRRS-int，GAT 的 10,001 次置换显示约 13 倍富集。

对 RepeatMasker 的每个 TE 区域，论文将 mCG 简化为二值特征：

$$
z_{cell,TE}=\begin{cases}
1,&mCG<0.75\\
0,&mCG\ge 0.75
\end{cases}
$$

只保留至少在一种细胞类型中低甲基化的 TE，再用 LSI/Scanpy 降维。图 3 显示，仅凭 intergenic LINE 甲基化就能同时区分细胞类型和年龄；DG Glut 的年龄分离最明显。420 个 retrotransposon subfamilies 呈细胞类型特异去甲基化，并伴随 ATAC 可及性和 RNA 增加；excitatory neurons 的 LTR 去甲基化强于 inhibitory neurons。代表性 chr13 LTR 热点在两性、多脑区 excitatory neurons 中显示 mCG 下降、ATAC/RNA 上升，而 mCH 较稳定。

TE 去甲基化区域同时丢失 H3K9me3，支持异染色质松动。论文还观察到 microglia 的 $Nfkb1$、$Stat1$、$Il18$ 等 innate-immune genes 上调，与“TE 解除抑制可能通过胞质核酸/cGAS-STING 促进炎症”的模型一致；但该研究没有直接扰动 TE 或测定 cGAS-STING 因果链，因此应称为相关机制线索。

### 5. 三维基因组如何随年龄重塑

snm3C 的接触矩阵按目的采用不同分辨率：100 kb 分析 A/B compartments，25 kb 分析 TAD，10 kb 分析 loops/enhancers。scHiCluster 先做 Gaussian convolution，再 random walk with restart 填补稀疏接触；不同年龄比较时按组平衡细胞数，并要求每组至少 100 个 nuclei。

#### 5.1 compartment

作者用 distance-normalized contact correlation matrix 的 PC1 定义 A/B compartment，并以

$$
\text{compartment strength}=\frac{AA+BB}{AB+BA}
$$

量化同类 compartment 相互作用。发现 897 个 cell-type-specific age-differential compartments，其中 58.9% 为 A→B；多数 cell types 的 compartment strength 增强。Oligo NN 的一个 A→B 区域伴随早期髓鞘相关基因 $Bcas1$ 下调，但区域转换与表达变化仍是关联证据。

#### 5.2 TAD boundary

25 kb imputed matrices 用 TopDom、10-bin window 调用 domain。每个 bin 的 boundary probability 是该组中把它识别为边界的细胞比例；三个年龄组成 3×2 contingency table 做 $\chi^2$ 检验，要求 FDR $<10^{-3}$ 且最大概率差 $>0.05$。

图 4 显示 TAD 数量增加、平均大小下降，2,469 个 age-differential boundaries 中 93.7% 随年龄增强，80.8% 来自 excitatory neurons。15,797 个边界 CTCF peaks 中 8,783 个 ATAC 可及性增加，支持“CTCF 位点更开放→边界更强→大 TAD 分割成更小 TAD”的结构模型。ABC 分析进一步显示，年轻脑中跨越未来增强边界的 enhancer-promoter links 较多；边界增强后这些联系可能被隔离，并与部分基因下调相关。

### 6. 同一种细胞并非在所有脑区同步衰老

MERFISH 将 age-DEG 放回冠状切片。图 5 比较同为 DG Glut 的 anterior hippocampus 与 posterior hippocampus：前部有更多 DMR、DMG、DEG、differential loops 和 boundaries；$Ighm$ 的表达与局部 3C contact 只在前部明显增加。Oligo NN 的 $C4b$ 则主要在 posterior/subcortical 和 corpus callosum 区域上调。

这说明 cell-type label 不足以概括衰老反应，脑区环境是独立维度。MERFISH panel 只有 500 个预选基因，因此能高通量定位候选信号，却不能替代全转录组发现。

### 7. EAT 模型怎样连接表观特征与 age-DEG

EpiAgingTransformer 把每个基因分为 age-up、age-down 或 non-DEG。输入包括 7 类特征：DMR、gene-body mCG、mCH、ATAC peaks、3C loops，以及以 ATAC 或 hypomethylated DMR 定义 activity 的 enhancer-contact features。每类特征先经独立 transformer 编码，再由 self-attention 聚合，最后用 MLP 分类并以 5-fold cross-validation 评估。

论文报告 10 种细胞类型中 age-DEG 平均准确率 $74.5\%\pm8.5\%$，高于 logistic regression 的 61.4%。注意力提示 mCH 在 neurons 权重更高、mCG 在 non-neurons 更高；ATAC 更常解释 age-up，enhancer features 更常解释 age-down。注意力权重是模型内归因，不是生物因果效应。EAT 主模型代码位于另一个未克隆的 `aging-gene-prediction` 仓库；当前代码快照只有输入准备和结果可视化，因此该部分在本地属于 `Not found/Partial`。

### 8. 论文与本地代码的对应

本地 `aging-mouse-brain/analysis_code/` 是按日期组织的 notebook/Snakemake 工作流，整体 fidelity 为 **medium-high**：

- `Exact`：snm3C 两遍 HISAT-3N mapping、snmC/snm3C CCA integration、TE 二值化与 LSI、TopDom TAD、compartment/loop、ABC、MERFISH panel design 等核心流程；
- `Partial/Notebook`：DSS 命令由 notebooks 动态生成并提交集群，许多步骤依赖原始数据、硬编码 Salk 路径和外部环境；
- `Not found`：EAT architecture/training 与 logistic baseline 的实际代码不在该快照；完整 MERFISH-scRNA integration 也未形成一个本地端到端入口。

关键源码锚点包括：`230531_female_mapping/m3c.smk` 的两遍 mapping；`230712_m3c-mc-integration/Snakefile` 的五步整合；`230907-call-dmr/` 的 DMR 工作流；`241115_te_clustering/` 的 TE 分析；`240205-domain/boundary.sh` 的 25 kb TopDom；`240204-redo-compartment/`、`240213-loop/` 和两个 ABC 目录的三维结构分析。

### 9. 如何正确解读这份资源

论文的强项是把局部甲基化、TE、3D genome、空间 RNA 和表达预测放到同一细胞分类框架中。主要结论不是“整个脑普遍去甲基化”，而是全局平均相对稳定之下，特定细胞和区域发生局部、连续且多模态一致的变化。边界增强、TE 活化和炎症基因上调提供可检验机制，但仍需 TE 抑制、CTCF/cohesin 操作或区域特异干预来建立因果。

复现方面，原始数据和大量分析 notebooks 已公开，但目录依赖日期和机构路径、数据量可达数百 TB，且 EAT 模型位于外部仓库。因此当前工作区能高可信复核大部分分析逻辑与图表生成链，不能视为单命令完整复现包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cell-type-specific transposon demethylation and TAD remodeling in aging mouse brain

### Motivation & Novelty

#### Biological Problem

Aging is the primary risk factor for neurodegenerative diseases, yet the epigenetic mechanisms underlying brain aging remain poorly characterized at single-cell resolution. Prior studies have examined either transcriptomic changes (Jin et al., *Nature* 2025; Allen et al., *Cell* 2023) or selected epigenetic marks (Zhang et al., *Cell Research* 2022; Tan et al., *Science* 2023; Chien et al., *Neuron* 2024) but have lacked a comprehensive multi-omic atlas that simultaneously profiles DNA methylation, 3D genome organization, and spatial transcriptomics across multiple brain regions and cell types during aging.

#### Limitations of Existing Approaches

- **Bulk or array-based studies** (Morandini et al., *Nature Aging* 2025; Ventham et al., *Nature Communications* 2016) cannot resolve cell-type-specific methylation changes
- **Single-modality studies** capture only one layer of epigenetic regulation at a time
- **Limited brain regions** — most prior work focused on cortex or hippocampus, missing cross-regional heterogeneity
- **No whole-genome TE methylation** at cell-type resolution — TE reactivation during aging was only known from bulk studies
- **Sparse 3D genome data** — only cerebellar granule cells (Tan et al., *Science* 2023) and human hippocampal neurons (Zemke et al., *bioRxiv* 2024) had been profiled

#### Unique Contributions

1. **Largest single-cell brain aging epigenome dataset**: 132,551 methylomes + 72,666 joint methylome/chromatin conformation profiles + 895,296 spatial transcriptomic cells across 8 brain regions at 3 ages
2. **First genome-wide TE methylation analysis at cell-type resolution**: revealing cell-type-specific transposon demethylation patterns that distinguish both cell types and ages
3. **Comprehensive 3D genome aging characterization**: systematic analysis of compartments, TAD boundaries, and loops across 36 cell types
4. **Spatial regional heterogeneity**: demonstrating that identical cell types age differently across brain regions
5. **Interpretable deep learning model (EAT)**: integrating 7 epigenetic features to predict age-related gene expression changes with attention-based interpretation

### Method Overview

The study generates three complementary datasets:

- **snmC-seq3**: base-resolution whole-genome DNA methylation from single nuclei (8 brain regions, C57BL/6 male mice at 2/9/18 months)
- **snm3C-seq**: joint DNA methylation and chromatin conformation from single nuclei (same regions, female mice)
- **MERFISH**: spatial transcriptomics (500-gene panel, 7 coronal sections per age)

These are integrated with companion snATAC-seq and 10x Multiome data using a CCA-based framework (modified Seurat) with 100K cell downsampling for scalability, yielding 36 major cell types with 5-modality pseudo-bulk profiles.

**Key analytical components** (see doc_method.md for details):

- **Differential methylation**: DSS beta-binomial regression with monotonic trend and sex-stratification filters
- **TE analysis**: Binarized methylation matrix (mCG < 0.75), LSI dimensionality reduction, showing TE methylation encodes both cell identity and aging status
- **3D genome**: scHiCluster imputation → compartment, TAD, loop analysis at 3 resolutions; Activity-by-Contact enhancer model
- **Spatial analysis**: MERFISH with scRNA-seq integration for cell type annotation; slice-specific DEG analysis reveals regional heterogeneity
- **Machine learning**: EpiAgingTransformer (EAT) — 7 transformer modules + self-attention aggregator + MLP classifier, predicting age-DEGs from multi-modal epigenetic features

### Evaluation

#### Datasets
- 132,551 snmC-seq3 nuclei (51,141 from BICCN + 81,410 new)
- 72,666 snm3C-seq nuclei
- 895,296 MERFISH cells (7 coronal sections × 3 ages)
- Integration with companion snATAC-seq and 10x Multiome (same dissections)

#### Key Results

**Methylation**: Global methylation is largely stable (ΔmCG = 0.008 ± 0.005), but cell-type-specific DMRs are abundant. Non-neurons (especially OPCs) show more DMRs than neurons. 83.6% of age-hypo DMRs are unique to one cell type. Neuronal age-hypo DMRs are enriched for AP-1 motifs; glial age-hyper DMRs for Sox family motifs.

**Transposable elements**: TE methylation alone clusters cells by type and age. 13-fold enrichment of LTR-ERV1-MuRRS-int in methylation hotspots. Excitatory neurons show greater TE demethylation than inhibitory neurons (p < 0.05 for LTRs). TE demethylation correlates with H3K9me3 loss, increased accessibility, and innate immune gene upregulation.

**3D genome**: TAD boundary number increases and domain size decreases with age (FDR < 10^-10). 93.7% of age-differential boundaries show increased strength. 80.8% occur in excitatory neurons. Boundary strengthening correlates with increased CTCF accessibility (8,783/15,797 CTCF peaks). Boundary-proximal genes enriched in amyloid-beta formation (DG Glut).

**Spatial**: DG Glut shows stronger aging in anterior hippocampus (AHC) vs posterior (PHC). *Ighm* upregulated only in AHC. *C4b* upregulated only in posterior oligodendrocytes. *Nlrp3* specifically upregulated in posterior microglia.

**EAT model**: 74.5% ± 8.5% accuracy for age-DEGs across 10 cell types (1.21× vs logistic regression baseline at 61.4%). mCH carries greater weight in neurons; mCG in non-neurons. ATAC contributes mainly to upregulation; enhancers to downregulation.

#### Biological Validation
- Batch effects confirmed minimal (alignment score 0.86 ± 0.07)
- TE findings consistent across sexes
- 3D genome changes parallel human hippocampal observations (Zemke et al.)
- AP-1 enrichment consistent with prior reports in kidney, liver, and hematopoietic stem cells

### Reproducibility

**Rating: 3.5/5**

**Strengths**:
- All raw data deposited in GEO (GSE132489, GSE213262, GSE313770, GSE292803) and AWS
- Analysis code publicly available (github.com/rachelzeng98/aging-mouse-brain)
- Detailed STAR Methods section with software versions (Table S9)
- Online browsers for exploration (neomorph.salk.edu)
- Mapping pipeline formally defined in Snakemake workflows

**Weaknesses**:
- Analysis code is notebook-based (Jupyter) rather than a packaged library — difficult to run without original directory structure and data paths
- All paths reference Salk Institute infrastructure (`/home/qzeng_salk_edu/`)
- EAT model code in separate repository (github.com/Michaelvll/aging-gene-prediction) — disconnected from main analysis
- DSS DMR calling partially externalized via `qsub` scripts (exact R commands not fully captured)
- MERFISH integration notebooks not included in analysis repo
- SkyPilot cloud configuration not provided
- Massive data volume (hundreds of TB of ALLC files) makes full reproduction impractical without comparable infrastructure

**Practical notes**:
- Core dependencies: ALLCools (v1.0.8+), scHiCluster (v1.3.2), YAP/cemba-data (v1.6.8), DSS (v2.42.0 in R)
- GPU not required for main analyses (CPU-intensive); EAT model requires GPU
- Zarr format requires xarray + dask for large-scale tensor operations
- MERSCOPE proprietary software for initial MERFISH processing

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
