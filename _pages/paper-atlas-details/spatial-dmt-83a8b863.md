---
layout: default
permalink: /paper-atlas/spatial-dmt-83a8b863/
title: "spatial-DMT"
nav: false
description: "Spatial-DMT 的核心不是把两张独立切片事后配准，而是在同一张固定组织切片、同一个二维条形码像素中同时给基因组 DNA 和 cDNA 加上空间坐标；随后再把二者物理分开，分别建立 EM-seq 甲基化文库和 RNA 文库。这样，每个像素最终对应两张矩阵：基因表达矩阵和 DNA 甲基化矩阵，可通过加权最近邻（WNN）联合分析。 论文为 Lee 等发表于 Nature（2025），DOI 10."
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
      <span>Technology Platforms</span>
      <span>Nature · 2025</span>
    </div>
    <h1>spatial-DMT</h1>
    <p>Spatial joint profiling of DNA methylome and transcriptome in tissues</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09478-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spatial-DMT 中文方法解读：同一张组织切片上的 DNA 甲基化与转录组

### 一句话理解

Spatial-DMT 的核心不是把两张独立切片事后配准，而是在**同一张固定组织切片、同一个二维条形码像素**中同时给基因组 DNA 和 cDNA 加上空间坐标；随后再把二者物理分开，分别建立 EM-seq 甲基化文库和 RNA 文库。这样，每个像素最终对应两张矩阵：基因表达矩阵和 DNA 甲基化矩阵，可通过加权最近邻（WNN）联合分析。

论文为 Lee 等发表于 *Nature*（2025），DOI `10.1038/s41586-025-09478-x`。本文依据主文、补充材料、主图与本地代码仓库提交 `206cc19ca89d985245ca204fbc86772e5c2446d0` 重新整理。

### 1. 它解决的具体问题

单细胞甲基化测序能看到细胞间的表观遗传差异，但组织解离会丢失解剖位置；空间转录组保留位置，却不直接测量 DNA 甲基化。Spatial-DMT 希望同时回答：

- 某个组织位置有哪些 RNA；
- 同一位置的 CpG 或 CpH 甲基化状态如何；
- 两种模态单独或联合时，对细胞身份和组织结构的分辨率有何差异；
- 发育阶段、解剖区域或增殖历史是否对应特定的甲基化—表达关系。

它的空间单位是“像素”而不是严格意义上的单细胞。论文使用 10、20 或 50 μm 像素；10 μm 接近胚胎细胞尺度，但像素是否等于一个细胞仍取决于组织、切片和细胞密度。

### 2. 从组织到两套文库

#### 2.1 暴露基因组并进行两轮 Tn5 切割

固定冷冻切片先用 HCl 破坏核小体并去除组蛋白，使 Tn5 更容易接近基因组 DNA。论文采用两轮 tagmentation：目标是在不过度延长处理、避免 RNA 降解的前提下，把大段 gDNA 切成更适合回收和建库的片段，并插入带通用连接区的接头。

#### 2.2 在原位合成带生物素的 cDNA

带 UMI、通用连接序列和生物素修饰的 poly(dT) 引物捕获 mRNA，并在组织内逆转录。这里的生物素非常关键：它不是用于空间定位，而是为稍后的 cDNA/gDNA 物理分流提供抓手。

#### 2.3 两次正交微流控连接生成二维坐标

两组各 50 条空间条形码沿互相垂直的微流道依次流过组织：

$$
\text{pixel}_{ij}=A_i\times B_j,\qquad i,j\in\{1,\ldots,50\}.
$$

因此一个区域最多形成 $50\times50=2{,}500$ 个条形码组合。gDNA 片段和 cDNA 都在原位连接同一像素的 $A_i,B_j$，这才保证两个模态共享坐标。图 1a、1b 展示了从 HCl、Tn5、逆转录、正交条形码连接到两套文库的完整顺序。

#### 2.4 反交联后分开 cDNA 与 gDNA

反交联释放两类分子。带生物素的 cDNA 被链霉亲和素磁珠捕获；gDNA 留在上清。之后：

- cDNA 经模板转换、PCR，形成转录组文库；
- gDNA 经 EM-seq 转换、splint ligation 和 PCR，形成甲基化文库。

#### 2.5 EM-seq 实际测到什么

EM-seq 先用 TET2 氧化并保护修饰胞嘧啶，再用 APOBEC 将未修饰 C 脱氨为 U；PCR 后未修饰位点表现为 C→T，而受保护的 5mC/5hmC 保留为 C。因此一个位点的甲基化比例可写为：

$$
m_s=\frac{n_{C,s}}{n_{C,s}+n_{T,s}},
$$

其中 $n_{C,s}$ 和 $n_{T,s}$ 是像素 $s$ 在该位点支持保留 C 与转换 T 的读段数。重要边界是：该化学流程把 5mC 与 5hmC 合并为“修饰 C”，不能区分二者。

论文说明条形码经过设计以避免 C→T 后串扰，并使用把 C 改成 T 的 N70X-HT 扩增引物。本地整合代码还显式将 RNA 条形码中的 C 替换为 T，再与甲基化条形码匹配；所以不能简单理解成“条形码完全不含 C”。

### 3. 原始测序如何变成两个像素矩阵

#### 3.1 RNA 分支

`Data_preprocess/Spatial-RNA/Snakefile` 先用 bbduk 检查引物和两段 linker，再调用 `fastq_process.py`。后者从 Read 2 固定位置抽取：

```python
new_seq = seq[22:30] + seq[60:68] + seq[98:108]
```

即两个 8 nt 空间条形码加一个 10 nt UMI。随后 STARsolo 以 `CB_UMI_Simple` 模式将 Read 1 比对到 mm10，并按条形码/UMI 生成 gene × pixel 计数矩阵。bbduk 预过滤和这些固定切片位置是代码级实现细节，主文方法没有完整展开。

#### 3.2 DNA 甲基化分支

`spatialmeth_trimadapters.py` 在 Read 2 中以允许编辑距离的方式寻找两段 linker，从各 linker 前取 8 nt，拼成 16 nt 空间条形码。它同时修剪 Read 1 接头并输出条形码频数和 QC 统计。Snakemake 工作流随后：

1. 按条形码拆成最多 2,500 组 FASTQ；
2. 用 BISCUIT 对 mm10 做 EM-seq 感知比对；
3. 标记重复并 pileup；
4. 计算每个像素的 CG/CH 甲基化分数；
5. 用外部 MethSCAN 识别 VMR。

主文将 VMR 定义为甲基化方差位于前 2% 的融合基因组区间。`min-sites` 并非固定常数，而是依据覆盖度 knee plot 设定。因此从新样本复现时，这一步仍包含数据依赖的人工选择。

### 4. 为什么要用 VMR 和迭代 PCA

单个 CpG 在单个像素中的覆盖极稀疏，直接构建“位点 × 像素”矩阵会充满缺失值。Spatial-DMT 先把相邻、共同变化的位点聚合为 variably methylated regions（VMR），再对每个 VMR 计算甲基化水平或残差。

`Utility_function.R::prcomp_iterative()` 对残差矩阵的缺失值先填 0，然后重复：

$$
X^{(t+1)}_{\text{miss}}=
\left(U_k^{(t)}D_k^{(t)}V_k^{(t)\top}\right)_{\text{miss}},
$$

直到重建误差改善低于阈值或达到迭代上限。0 初始化与“残差以 0 为中心”相符；它不是对原始甲基化比例的生物学断言。填补值是低秩估计，不能当成该像素真实测到的单个位点证据。

### 5. 单模态与 WNN 联合分析

RNA 分支使用 SCTransform、30 个主成分、近邻图、Leiden 聚类和 UMAP。甲基化分支把预先得到的 VMR 残差作为 DNAm assay，使用 10 个主成分。主分析脚本再调用 `FindMultiModalNeighbors` 构建 WNN 图。

直观地说，对像素 $i$，WNN 不要求 RNA 与 DNAm 永远同等可靠，而是学习模态权重：

$$
d_{ij}^{\mathrm{WNN}}
=w_i^{R}d_{ij}^{R}+w_i^{M}d_{ij}^{M},
\qquad w_i^{R}+w_i^{M}=1.
$$

这里是帮助理解的抽象形式；Seurat 实际实现基于各模态近邻预测亲和度。代码以 RNA PCA 1–30 维和 DNAm PCA 1–10 维构图，再对 `wsnn` 图做 Leiden 聚类。图 1f 显示联合聚类比任一单模态更细地对应胚胎解剖结构，但这属于数据结果，不保证所有组织都一定由联合分析获得更高分辨率。

### 6. 论文结果应该怎样读

- **图 1**验证技术流程、覆盖度、重复性和 E11 胚胎的单/双模态空间结构。10 μm 图证明可在更细像素上工作，但不是逐像素的单细胞纯度证明。
- **图 2**展示 VMR、基因表达和 TF motif 富集的空间关系。相关性可为调控假设提供线索，但正相关或负相关都不自动等于甲基化对该基因的直接因果调控。
- **图 3**把 E11 与 E13 胚胎整合，并沿拟时序比较甲基化和表达变化。拟时序是从分子相似性推断的顺序，不是对同一细胞的真实时间追踪。
- **图 4**在 P21 脑中联合 mCG、mCA 与 RNA，显示不同甲基化上下文具有不同空间关系。
- **图 5**用差异区域和 PMD 讨论区域表观遗传差异与有丝分裂历史。PMD 甲基化是增殖历史的间接表征，不是直接记录每个像素经历的分裂次数。

补充表 5 给出实际数据规模：不同样本约 1,699–2,493 个像素，每像素平均约 136,639–281,447 个 mCG 位点；P21 脑还报告 mCH。原始 DNA 数据达到每样本数十亿 reads，说明其计算和测序成本不能从“2,500 像素”这一数字简单推断为轻量流程。

### 7. 代码—论文对应与复现边界

#### 可直接对应

- RNA：bbduk → 固定位置 barcode/UMI 抽取 → STARsolo；
- DNAm：模糊 linker 搜索 → 条形码拆分 → BISCUIT → CG/CH pileup；
- VMR：迭代 PCA 填补函数；
- 联合分析：Seurat WNN、30 维 RNA PCA、10 维 DNAm PCA、Leiden；
- E11/E13：发布的 Rmd 包含整合与拟时序分析片段；
- 空间绘图与 VMR-overlapping-gene 映射工具函数。

#### Partial / Not found

- MethSCAN 和 HOMER 是外部工具，仓库没有把所有样本参数及完整运行封装成可直接重放的流程；
- 图 5 的 PMD 分析与 knowYourCG 富集代码未找到；
- 图 4 的 mCA 专用下游可视化、相关分析脚本未找到，尽管预处理工作流能生成 CH pileup；
- 脚本包含 `[local path omitted]`、`~/...` 等实验室路径，需手工改写；
- 没有锁定环境或一键重建全部主图的顶层入口，原始数据规模也要求 HPC。

因此，论文“分析管线和代码可用”可理解为核心预处理、WNN 和部分下游分析已发布；不能据此声称每张主图都能由当前仓库端到端复现。

### 8. 最容易混淆的四个边界

1. **同一像素不等于同一单细胞。** 两种模态共享空间条形码，但 20/50 μm 像素通常含多个细胞。
2. **相关不等于因果。** VMR—gene Pearson 相关和 motif 富集提出候选关系，不能单独证明调控方向。
3. **填补不等于测量。** 迭代 PCA 恢复的是低秩估计，必须与实测覆盖区分。
4. **EM-seq 不区分 5mC 与 5hmC。** 论文报告的“DNA methylation”在该化学读出中是两类修饰胞嘧啶的合并信号。

### 证据入口

- 主文：`paper source/paper/vlm/paper.md`
- 补充材料：`output_paper_supp_md/paper_supp/vlm/paper_supp.md`
- 主图解读：`figure_analysis.md`
- 代码匹配：`doc_code.md`
- 直接代码：`Data_preprocess/`、`Data_analysis/` 和 `Spatial-DMT-2024-code/`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial-DMT: Spatial Joint Profiling of DNA Methylome and Transcriptome in Tissues

**Paper**: Lee et al., *Nature* 2025. DOI: 10.1038/s41586-025-09478-x
**Method**: spatial-DMT
**Category**: datasource / technology_platforms
**Code**: https://github.com/zhou-lab/Spatial-DMT-2024

---

### Motivation & Novelty

#### Biological Problem

DNA methylation is a canonical epigenetic mark that modulates gene expression across cell types, developmental stages, and disease states. Its spatial organization within tissues — which regions of the genome are methylated in which anatomical zones — is fundamental to understanding how gene regulation is coordinated in vivo. Abnormal methylation patterns underlie cancer, autoimmune disease, and aging.

Despite this importance, **no prior technology could map DNA methylation in intact tissues with spatial resolution**. All existing single-cell methylation methods (sciMETv2, *Nat. Commun.* 2022; snmC-seq2, *Nat. Methods* 2019; Snm3C-seq, *Nature* 2023) require tissue dissociation, destroying the spatial context. Meanwhile, spatial multi-omics technologies existed for transcriptomics, chromatin accessibility, and histone modifications — but not for DNA methylation.

#### Limitations of Existing Approaches

- **Single-cell methylome methods** (sciMETv2, *Nat. Commun.* 2022): lose tissue architecture; no RNA
- **Spatial transcriptomics** (DBiT-seq, *Cell* 2020; spatial-ATAC-RNA, *Nature* 2023): no methylation layer
- **Bisulfite-based spatial approaches**: conceptually possible but bisulfite's harsh chemistry (DNA degradation >99%) is incompatible with tissue preservation required for spatial barcoding
- **Bulk methylation arrays**: no single-cell resolution, no spatial information
- **Spatial epigenomics** (Spatial-CUT&Tag, *Nat. Biotechnol.* 2022): only histone modifications

#### What spatial-DMT Provides

1. **First spatial DNA methylation technology**: whole-genome CpG and CpH methylation profiling in intact tissue sections
2. **Simultaneous RNA**: same tissue section, same pixels, enabling direct methylation-expression correlation
3. **Near single-cell resolution**: 10 μm pixel size approaches single-cell granularity
4. **EM-seq chemistry**: enzymatic methylation detection (TET2+APOBEC) is gentle enough to preserve RNA integrity, enabling co-profiling
5. **Scalable barcoding**: 50×50 microfluidic grid = 2,500 spatially barcoded pixels per experiment

---

### Method Overview

#### Experimental Framework

Spatial-DMT uses deterministic microfluidic barcoding to assign 2D spatial coordinates to molecular events. The key innovations over prior spatial methods are:

1. **HCl histone removal before Tn5**: gentle acid treatment exposes chromatin without degrading RNA (previous ATAC methods struggled to co-profile with RNA)
2. **EM-seq instead of bisulfite**: enzymatic conversion (TET2 oxidizes 5mC/5hmC → 5caC; APOBEC deaminates unmodified C → U) achieves >99% conversion with minimal DNA damage
3. **Multi-tagmentation strategy**: two rounds of Tn5 at 37°C (60 min each) reduce fragment size and improve gDNA yield
4. **Streptavidin bead separation**: biotinylated poly-dT primer captures cDNA; gDNA remains in supernatant, enabling clean modality separation
5. **Deamination-compatible barcodes**: barcode sequences were designed to avoid barcode crosstalk after C→T conversion; modified P7 primers (N70X-HT, C→T) amplify EM-seq-processed libraries, and the released integration code explicitly harmonizes RNA barcode C to T before matching

#### Computational Pipeline

The computational pipeline handles two distinct data types with different properties:

**RNA** (sparse count matrix): bbduk pre-filtering → barcode/UMI extraction from Read2 → STARsolo alignment → Seurat SCTransform normalization → PCA(30d) → Leiden clustering → UMAP

**DNA methylation** (continuous fractions, highly sparse coverage): fuzzy adapter trimming → awk demultiplexing into 2,500 per-barcode FASTQs → BISCUIT alignment + pileup → MethSCAN VMR identification (top 2% methylation variance) → iterative PCA imputation → Seurat PCA(10d) → Leiden clustering

**Integration** (Seurat WNN): Weighted Nearest Neighbor analysis learns per-pixel modality weights, building a joint neighbor graph that combines RNA PCA (30 dim) and DNAm PCA (10 dim). Leiden clustering on the WNN graph produces anatomically meaningful spatial clusters.

#### Key Biological Assumptions

- VMRs (top 2% variance) capture biologically informative methylation variation, filtering noise from low-coverage CpGs
- DNA methylation and RNA provide complementary (not redundant) information about cell identity
- The 50 μm pixel size includes multiple cells; the 10 μm size approaches single-cell resolution in embryonic tissue (~10 μm cell diameter)
- EM-seq measures 5mC + 5hmC combined (cannot distinguish; noted as a limitation)

---

### Evaluation

#### Datasets Profiled

| Sample | Pixel size | Pixels | Avg CpGs/pixel | Avg genes/pixel | Modalities |
|---|---|---|---|---|---|
| E11 mouse embryo (×2 replicates) | 50 μm | ~1,950 | 238,000–281,000 | 2,417–4,626 | mCG + RNA |
| E11 mouse embryo (zoomed) | 10 μm | 2,493 | 136,639 | 1,890 | mCG + RNA |
| E13 mouse embryo | 50 μm | 1,699 | 255,402 | 3,788 | mCG + RNA |
| P21 mouse brain | 20 μm | 2,235 | 194,224 | 2,525 | mCG + mCA + RNA |

#### Reproducibility

- Pearson r = 0.9836 (DNA methylation) and r = 0.9752 (RNA expression) between E11 replicate experiments
- Co-embedding of replicates shows interleaved pixels from matched body parts
- CpG retention rates 70-80% (consistent with published single-cell methylation data)
- >99% cytosine conversion efficiency (mitochondrial DNA retention <1%)

#### Comparison to Existing Methods

Coverage per pixel (136K–281K CpGs) is comparable to published single-cell methylation datasets:
- Mouse muscle stem cells (Hernando-Herraez et al., *Nat. Commun.* 2019): median ~similar
- Human brain (sciMETv2, Nichols et al., *Nat. Commun.* 2022): 1,049–1,920 cells
- Mouse brain atlas (Liu et al., *Nature* 2021): 103,560 single cells

Genes detected per pixel (1,890–4,626) are comparable to published spatial transcriptomics of mouse embryo and brain (DBiT-seq ref. 1; spatial-ATAC-RNA ref. 2).

#### Biological Validation

1. **Anatomical correspondence**: WNN clusters match histological structures (craniofacial, hindbrain/spinal cord, heart at E11)
2. **Known methylation biology**: CpG retention 70-80% in embryo; mCA ≈ 3-4% in postnatal neurons (matches published scMethyl atlases)
3. **Marker gene validation**: Frem1 (face), Ank3 (brain), Trim55 (heart) — spatial patterns match Allen Mouse Brain Atlas
4. **Integration with scRNA-seq**: Integration with Qiu et al. 2024 (*Nature*) embryo atlas shows strong concordance
5. **Positive and negative methylation-expression correlations**: Both documented (Ank3 positive; Mapt, Runx2 negative) — consistent with literature on gene body methylation and enhancer regulation

#### Key Findings

- **WNN integration resolves finer anatomy than either modality alone**: e.g., separates cortical layers and hippocampal subfields that RNA alone misses
- **mCG vs mCA regulate different genes**: Prox1 (DG) correlated with both; Ntrk3 (CA1/2) only with mCG; Cux1 (CA3) correlates with mCA but not mCG in certain regions
- **PMD methylation as mitotic history marker**: forebrain/hindbrain have high PMD methylation (low proliferation); heart has low PMD (active cardiogenesis)
- **Epigenetically primed subpopulations**: Same RNA cluster (R3) contains D0/D4 DNA methylation subclusters with distinct regulatory element accessibility but nearly identical transcription
- **Oligodendrocyte migration**: Pseudotime analysis spatially maps migration from subpallium to pallium; coupled demethylation-gene activation patterns

---

### Reproducibility

**Rating: 3.5/5**

**Justification**:
- Data deposited in GEO (GSE270498) — all raw FASTQ and processed matrices available
- Core preprocessing, WNN, QC, and E11/E13 analysis code is available at GitHub and Zenodo, but not every reported downstream figure path is present
- Detailed protocol in Methods and Extended Data Fig. 1 (reagent tables in Supplementary Tables 1-4)
- All analysis software versions specified (Seurat 5.1.0, BISCUIT 0.3.14, STARsolo 2.7.10b, etc.)

**Limitations**:
- Snakemake pipelines contain hardcoded CHOP HPC paths — require modification for new environments
- PMD analysis R scripts not in repository (Fig 5c-e cannot be reproduced from code alone)
- mCA analysis R scripts missing (Fig 4 analyses require unreleased code)
- MethSCAN min-sites parameter must be set manually per sample from knee plot
- 2.8–3.9 billion raw reads per sample (10 μm data) requires significant HPC resources
- Wet lab protocol requires PDMS microfluidic device fabrication (photolithography)

**Strengths**:
- Very detailed Methods section with all reagent concentrations and incubation times
- Barcode sequences provided (Supplementary Tables 2-3)
- Computational workflow diagram (Supplementary Fig. 1)
- All key reagents catalogued with vendor/catalog numbers (Supplementary Table 4)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
