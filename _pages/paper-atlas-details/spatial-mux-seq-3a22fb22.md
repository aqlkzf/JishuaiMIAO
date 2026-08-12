---
layout: default
permalink: /paper-atlas/spatial-mux-seq-3a22fb22/
title: "spatial-Mux-seq"
nav: false
description: "spatial-Mux-seq 把普通 Tn5、携带不同连接序列的 nanobody–Tn5、带 poly(A) DNA 标签的蛋白抗体和带生物素的 poly(dT) 逆转录引物放到同一张组织切片上，再用两轮正交微流控条形码给所有分子写入共同空间坐标。反交联后，gDNA 与 cDNA/抗体标签被物理分开，各自建库；计算端再按像素整合 ATAC、两种组蛋白修饰、RNA 和蛋白。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>spatial-Mux-seq</h1>
    <p>Multiplexed spatial mapping of chromatin features, transcriptome and proteins in tissues</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02576-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## spatial-Mux-seq 中文方法解读：在同一组织像素中读取染色质、RNA 与蛋白

### 一句话理解

spatial-Mux-seq 把普通 Tn5、携带不同连接序列的 nanobody–Tn5、带 poly(A) DNA 标签的蛋白抗体和带生物素的 poly(dT) 逆转录引物放到同一张组织切片上，再用两轮正交微流控条形码给所有分子写入共同空间坐标。反交联后，gDNA 与 cDNA/抗体标签被物理分开，各自建库；计算端再按像素整合 ATAC、两种组蛋白修饰、RNA 和蛋白。

论文为 Guo 等发表于 *Nature Methods*（2025），题为 *Multiplexed spatial mapping of chromatin features, transcriptome and proteins in tissues*，DOI `10.1038/s41592-024-02576-0`。

### 1. 方法想解决什么

单一空间模态只能看到调控链的一层：ATAC 表示染色质可及性，组蛋白修饰提供活化或抑制背景，RNA 是转录输出，表面蛋白更接近细胞表型。spatial-Mux-seq 的目标是在同一组织坐标下同时测量这些层次，从而比较：

- 某个区域是否开放，但仍受 H3K27me3 抑制；
- H3K4me3/H3K27me3 双价状态如何随分化变化；
- 可及性变化是否先于 RNA；
- RNA 与表面蛋白是否在空间上同步；
- 多模态联合聚类是否补充单模态无法区分的组织区域。

“同一像素共测”不等于“同一单细胞内精确共测”。论文使用 20 或 50 μm 像素；20 μm 接近单细胞尺度，但仍可能包含多个细胞。100×100 条形码实验可产生 10,000 个坐标，实际保留像素数还取决于组织覆盖和 QC。

### 2. 五类信号怎样被同时编码

#### 2.1 ATAC：普通 Tn5 标记开放染色质

固定切片首先接受原位 Tn5 转座。Tn5 更容易插入开放染色质，同时带入测序接头和可继续连接空间条形码的通用 linker。因此 ATAC 信号本质上来自可被转座酶接近的基因组片段。

#### 2.2 两种组蛋白修饰：抗体加物种特异 nanobody–Tn5

切片先与针对两种组蛋白修饰的一抗孵育，再加入识别不同一抗物种的 nanobody–Tn5。每种 nanobody–Tn5 携带不同的 ligation linker，测序后可据 linker 区分来自哪种组蛋白标记。

不同实验采用不同组合：例如 H3K27ac/H3K27me3 用于活化—抑制对照，H3K4me3/H3K27me3 用于启动子双价状态。这里的“五模态”表示一个实验最多同时读取 ATAC、两种组蛋白修饰、RNA 和蛋白；并不是所有论文样本都使用同一组五模态。

#### 2.3 RNA 与蛋白：同一次逆转录捕获

表面蛋白由带 poly(A) DNA 标签的抗体识别。带生物素的 poly(dT) 引物既捕获 mRNA，也捕获抗体 DNA 标签（ADT），并在组织内逆转录。这样 RNA 与蛋白标签进入 cDNA/ADT 分支，而 ATAC 和 CUT&Tag 片段留在 gDNA 分支。

#### 2.4 两轮正交条形码写入二维坐标

条形码 A 和 B 沿互相垂直的微流道依次流过组织：

$$
\text{pixel}_{ij}=A_i\times B_j.
$$

50×50 设计产生至多 2,500 个组合；100×100 设计产生至多 10,000 个组合。因为 ATAC、两种 nanobody–Tn5、cDNA 和 ADT 都带兼容 linker，它们在同一像素获得同一对 $A_i,B_j$。图 1a 清楚展示了“一抗 → nanobody–Tn5 → A/B 正交连接 → 反交联建库”的顺序。

#### 2.5 反交联与三类文库分流

反交联释放分子后，链霉亲和素磁珠捕获带生物素的 cDNA/ADT，gDNA 留在上清：

- gDNA 经 PCR 形成 ATAC/nano-CUT&Tag 文库，靠 modality-specific linker 解复用；
- 磁珠上的 cDNA/ADT 经模板转换和 PCR；
- 0.6× SPRI 分离较长 RNA cDNA 与较短 ADT，分别形成 RNA 和蛋白文库。

因此，多模态共定位来自共享空间条形码，模态分辨来自分子类型、linker 和文库分流，而不是把所有信号混在一套读段中再猜测。

### 3. 原始读段如何变成各模态矩阵

#### 3.1 ATAC 与 CUT&Tag 分支

官方 `Data_preprocessing/Snakemake_*_nanoTn5/` 和 `Snakemake_ATAC/` 工作流先用 primer/linker 过滤读段，再抽取条形码。`BC_process.py` 从固定位置取两个 8 nt 条形码；ATAC 版本还从同一读段后部截取基因组序列。之后流程包括 barcode correction/tagging、Trim Galore、BWA 比对、samtools 排序和 sinto fragment 生成。

下游 ArchR 对每个染色质模态建立 Arrow/ArchRProject，进行 TF–IDF/LSI、聚类、UMAP、pseudo-bulk peak calling 与 gene score 计算。论文使用 MACS2 和 501 bp 固定峰窗口进行多模态整合。

#### 3.2 RNA 分支

`Data_preprocessing/Snakemake_RNA/fastq_process.py` 从 Read 2 取：

```python
new_seq = seq[22:30] + seq[60:68] + seq[98:108]
```

即 BC2、BC1 和 10 nt UMI。论文 Methods 说使用 Spatial Transcriptomics pipeline 1.7.2；官方仓库的 Snakemake 则把读段过滤、条形码重排和后续计数步骤具体化。得到 gene × pixel 矩阵后，Seurat 使用 SCTransform、PCA、近邻图、聚类和 UMAP。

#### 3.3 蛋白分支

ADT 的条形码/UMI重排与 RNA 类似，但最终使用 CITE-seq-Count 按抗体标签计数，形成 antibody × pixel 矩阵；Seurat 中使用 centered log-ratio（CLR）归一化。蛋白面板是预先选定抗体集合，不是全蛋白组。

### 4. 多模态怎样联合

官方 `Data_visualization/Multi_omics_integration_prepare.R` 把 ArchR peak matrix 加入 RNA Seurat 对象；`Multi_omics_integration.R` 对 RNA 运行 PCA，对 ATAC/组蛋白 peak assay 运行 TF–IDF 和 LSI，再调用 `FindMultiModalNeighbors`：

```r
dims.list = list(1:30, 2:30, 2:30, 2:30)
```

RNA 使用前 30 个 PCA，染色质模态跳过常与测序深度强相关的 LSI 第 1 维，使用 2–30 维。WNN 为每个像素学习各模态权重，并构建联合近邻图。概念上可写成：

$$
d^{\mathrm{WNN}}_{ij}=\sum_m w_{im}d^{(m)}_{ij},
\qquad \sum_m w_{im}=1,
$$

但这是解释性抽象，Seurat 实现使用跨模态近邻预测亲和度。联合聚类基于 `wsnn` 图；代码尝试多个 resolution，因此“联合得到多少簇”也受人为参数选择影响。

### 5. 三类关键下游推断

#### 5.1 GAS、CSS 与双价分数

ArchR gene score 把基因附近峰信号按到 TSS 的距离加权。对 H3K27ac/H3K4me3，论文称为 gene activity score（GAS）；对 H3K27me3，称为 chromatin silencing score（CSS）。这些是基于染色质信号的基因级摘要，不是 RNA 表达量。

代码中的双价分数使用 H3K4me3 与 H3K27me3 的和与差构造：

$$
B=\frac{K4+K27}{|K4-K27|+1}.
$$

两种标记同时高且接近时分数较高。高分表示数据与“双价”一致，并不单独证明两个修饰存在于同一个核小体或同一个细胞中，尤其在多细胞像素内。

#### 5.2 Slingshot/ArchR 拟时序

论文沿 radial glia → postmitotic premature neuron → excitatory neuron 研究分化。代码从低维嵌入推断 Slingshot 或 ArchR trajectory，再用 LOESS 展示 ATAC、H3K4me3、H3K27me3 和 RNA 的趋势。拟时序是横截面像素在分子状态空间中的排序，不是对同一细胞的真实追踪。

#### 5.3 FigR、DORC 与候选 GRN

FigR 将 ATAC peak 与 RNA 做相关，至少有 5 个显著 peak linkage 的基因定义为 DORC，再结合 TF motif 和 TF 表达提出候选调控关系。论文观察 Neurod2 DORC 可及性趋势早于 RNA，解释为 lineage priming。这里的“早于”和“调控网络”依赖拟时序、相关性和 motif，属于候选机制而不是直接因果验证。

### 6. 主图从左到右怎样读

- **图 1**：H3K27me3/H3K27ac 双模态证明 nanobody–Tn5 的模态特异性、重复性及 WNN 的组织分区增益。
- **图 2**：E13 胚胎同时读取 ATAC、H3K4me3、H3K27me3、RNA；Sox2 轨迹展示开放/活化信号下降、抑制标记上升，DORC 用于提出神经分化调控候选。
- **图 3**：20 μm 胚胎后脑同时分析 H3K4me3、H3K27me3、RNA 和七种表面蛋白，比较 radial glia 到分化神经元的双价变化。
- **图 4**：P21 海马的 H3K27ac、H3K27me3 与 RNA 联合图分出 DG-sg 与 DG-sgz，并比较 Igfbpl1 的激活/抑制染色质和表达。
- **扩展数据图 8–10**：5 月龄 EAE 脑使用 100×100、20 μm 网格，同时测 ATAC、H3K27ac、H3K27me3、RNA、蛋白，是论文“五模态”能力的直接示例。

这些图证明多模态信号可在共享坐标中形成合理空间结构；它们不意味着 WNN 在所有数据上必然优于单模态，也不证明相关的染色质变化必然驱动 RNA 或蛋白变化。

### 7. 论文代码与本地代码的真实对应

#### 官方快照中直接存在

- 四类 Snakemake 预处理：ATAC、mouse/rabbit nanobody–Tn5、RNA、protein；
- 图像到组织像素坐标的 Python 脚本；
- ArchR/Seurat 单模态处理、WNN、RCTD、GO、FigR、ADT 和空间绘图脚本；
- `Fig1_joint_analysis.Rmd`，对应论文明确提供的图 1 联合分析教程。

#### 必须保留的复现边界

- 官方脚本大量使用 `[local path omitted]`、实验室服务器路径和内部样本名，不能直接在新环境运行；
- `Multi_omics_integration.R` 含未在脚本内赋值的 `seurat.wnn.peak.sub` 等交互式对象；
- 顶层没有一键从 GSE263333 重建所有主图的入口，也没有完整锁定的软件环境；
- 论文明确指向 Fig.1 的联合教程，不能据此推断每个主图都有同等完整的可执行教程；
- 工作区 `analysis/` 下的 Python 文件是后续本地数据探索/复图尝试，带旧绝对路径，不是论文官方仓库的核心实现证据。

因此更准确的结论是：官方仓库覆盖核心预处理和主要分析方法，且提供一个重点教程，但当前快照仍是实验室脚本集合，不是端到端、环境锁定、所有图均自动复现的软件包。

### 8. 四个解释边界

1. **pixel 不是 cell**：共享坐标保证模态共定位，但不能保证每个信号来自同一细胞。
2. **score 不是直接测量**：GAS、CSS、bivalency、DORC 都是从原始信号派生的摘要或推断。
3. **相关和拟时序不是因果时间链**：它们用于生成机制假设，需要扰动或时间实验验证。
4. **protein 是靶向面板**：ADT 只能测预先选择的抗体，不等于无偏全蛋白组。

### 证据入口

- 主文：`paper source/paper/paper.md`
- 图证据：`figure_analysis.md` 与主文图像
- 方法细节：`doc_method.md`
- 代码匹配：`doc_code.md`
- 官方代码快照：`Data_preprocessing/`、`Data_visualization/`
- 本地后续探索：`analysis/`（仅辅助，不作为论文官方实现来源）

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial-Mux-seq: Multiplexed Spatial Multi-omics Paper Summary

### Paper Information
**Title**: Multiplexed spatial mapping of chromatin features, transcriptome and proteins in tissues
**Authors**: Pengfei Guo, Liran Mao, Yufan Chen, Chin Nien Lee, Angelysia Cardilla, Mingyao Li, Marek Bartosovic, Yanxiang Deng
**Published**: Nature Methods, 2025
**DOI**: 10.1038/s41592-024-02576-0

### 1. Motivation and Novelty

#### 1.1 Biological Problem Addressed
The phenotypic and functional states of cells are regulated by a complex molecular hierarchy spanning multiple omics layers (genome, epigenome, transcriptome, proteome, metabolome). Understanding how these layers interact within tissue context is critical for deciphering cellular identity and function. However, existing spatial omics approaches face significant limitations:

- **Single or dual modality limitation**: Current spatial methods can only profile 1-2 molecular modalities simultaneously (e.g., ATAC+RNA, CUT&Tag+RNA, protein+RNA)
- **Incomplete cellular representation**: Limited modalities provide fragmented views of cellular states
- **Missing regulatory interactions**: Unable to capture the interactive effects of multiple epigenetic factors on gene/protein expression
- **Lack of comprehensive tissue context**: Cannot study the complete molecular hierarchy within native tissue architecture

#### 1.2 Limitations of Existing Approaches
- **Single-cell technologies**: While capable of trimodal measurements (RNA+ATAC+proteins, H3K27me3+H3K27ac+protein), they lose spatial context
- **Current spatial methods**: Limited to bimodal profiling, missing the complex interplay between chromatin states, gene expression, and protein levels
- **Incomplete epigenetic landscape**: Cannot simultaneously assess multiple histone modifications that work synergistically or antagonistically
- **Technical constraints**: Previous methods required separate experiments for different modalities, introducing batch effects and preventing direct correlation analysis

#### 1.3 Unique Contributions and Innovations
**Spatial-Mux-seq** represents a major technological breakthrough by enabling:

1. **Unprecedented multiplexing capability**: Simultaneous profiling of up to 5 modalities:
   - Chromatin accessibility (ATAC)
   - Two histone modifications (e.g., H3K27me3/H3K27ac, H3K4me3/H3K27me3)
   - Whole transcriptome (RNA-seq)
   - Large panels of surface proteins (up to 122 antibodies)

2. **Technical innovations**:
   - Integration of microfluidic in situ barcoding for spatial encoding
   - Nanobody-tethered transposition chemistry for multimodal chromatin profiling
   - Sequential capture strategy preserving all modalities from the same tissue pixel
   - Species-specific nanobody-Tn5 fusion proteins for demultiplexing histone modifications

3. **Biological insights enabled**:
   - Direct analysis of bivalent chromatin states and their effects on gene/protein expression
   - Spatiotemporal tracking of epigenetic dynamics during cell differentiation
   - Discovery of novel cell types and states invisible to unimodal approaches
   - Comprehensive regulatory network inference from integrated multi-omics data

#### 1.4 Significance for Bioinformatics Community
This work is transformative for several reasons:

- **Comprehensive molecular profiling**: Provides the most complete view of cellular states within tissue context to date
- **Regulatory mechanism elucidation**: Enables direct study of how epigenetic marks control gene expression spatially
- **Developmental biology applications**: Reveals spatiotemporal relationships during tissue development and cell differentiation
- **Disease research potential**: Demonstrated application in neuroinflammation (EAE model), applicable to cancer and other diseases
- **Methodological advancement**: Sets new standard for spatial multi-omics integration and analysis

### 2. Method Overview

#### 2.1 Algorithmic Framework
The spatial-Mux-seq workflow employs a sophisticated multi-step molecular and computational framework:

1. **Tissue preparation and fixation**: Cryosections fixed with formaldehyde to preserve molecular interactions
2. **Sequential molecular profiling**: Orchestrated capture of different modalities through chemical modifications
3. **Spatial barcoding**: Two-dimensional grid system using microfluidic channels (50×50 or 100×100 pixels)
4. **Library separation**: Physical separation of gDNA and cDNA for independent processing
5. **Computational integration**: Multi-modal data analysis using advanced bioinformatics pipelines

#### 2.2 Key Technical Components

##### 2.2.1 Nanobody-based Multimodal Chromatin Profiling
- **Species-specific nanobody-Tn5 fusion proteins**: Enable simultaneous profiling of multiple histone modifications
- **Unique ligation linkers**: Allow demultiplexing of different epigenetic marks
- **In situ transposition**: Direct chromatin tagmentation within tissue sections

##### 2.2.2 Spatial Encoding System
- **Microfluidic barcoding**: Sequential ligation of two barcode sets (A1-A100, B1-B100)
- **2D spatial grid**: Creates 2,500-10,000 spatially resolved pixels
- **Shared spatial coordinates**: All modalities from same pixel share identical barcodes

##### 2.2.3 Multi-modal Capture Strategy
- **ATAC-seq**: Wild-type Tn5 for chromatin accessibility
- **Histone modifications**: Primary antibodies + nanobody-Tn5 fusion proteins
- **RNA capture**: In situ reverse transcription with biotinylated poly-T primers
- **Protein detection**: Oligo-conjugated antibodies (ADTs) with poly-A tails

#### 2.3 Computational Pipeline

##### 2.3.1 Data Processing
- **Alignment**: BWA for genomic data, STAR for transcriptomic data
- **Peak calling**: MACS2 for chromatin features
- **Quantification**: Fragment counting for chromatin, UMI counting for RNA/proteins
- **Quality control**: TSS enrichment scores, fragment size distribution, sequencing depth metrics

##### 2.3.2 Integration and Analysis
- **Normalization**: Latent Semantic Indexing (LSI) for chromatin, SCTransform for RNA
- **Dimension reduction**: PCA for RNA, SVD for chromatin features
- **Multi-modal integration**: Weighted Nearest Neighbor (WNN) analysis
- **Cell type identification**: Label transfer from reference scRNA-seq datasets
- **Trajectory analysis**: Slingshot for pseudotime, ArchR for chromatin dynamics

#### 2.4 Biological Assumptions and Model Design

1. **Chromatin state relationships**: H3K27me3 and H3K27ac are mutually exclusive marks representing repressed and active states
2. **Bivalent chromatin**: Co-occurrence of H3K4me3/H3K27me3 indicates poised developmental genes
3. **Spatial coherence**: Adjacent tissue pixels share similar molecular profiles
4. **Multi-layer regulation**: Gene expression results from integrated effects of chromatin accessibility, histone modifications, and transcription factors

### 3. Evaluation Strategy

#### 3.1 Datasets Used

##### 3.1.1 Experimental Datasets
- **Mouse embryo sections (E13)**: Sagittal sections at 50μm and 20μm resolution
- **Mouse brain tissues**:
  - Juvenile (P21) hippocampus at 20μm resolution
  - Adult (5 months) EAE model brain at 20μm resolution
- **Replicate experiments**: Multiple biological replicates for reproducibility assessment

##### 3.1.2 Reference Datasets for Validation
- **ENCODE H3K27me3/H3K27ac ChIP-seq**: Gold standard for histone modification peaks
- **Mouse Organogenesis Cell Atlas (MOCA)**: E13.5 scRNA-seq for cell type annotation
- **Allen Mouse Brain Atlas**: Anatomical and expression references
- **Published spatial omics data**: spatial-CUT&Tag and spatial-ATAC-RNA-seq for benchmarking

#### 3.2 Evaluation Metrics

##### 3.2.1 Technical Performance Metrics
- **Data quality indicators**:
  - Median unique fragments per pixel: 1,500-40,000 depending on modality
  - TSS enrichment scores: Comparable to published single-modality methods
  - Gene/UMI detection: 1,200-1,500 genes, 2,000-3,000 UMIs per pixel
  - Protein detection: 80-90 proteins, 700+ protein UMIs per pixel

##### 3.2.2 Biological Validation Metrics
- **Reproducibility**: Pearson correlation r>0.91 between replicates
- **Peak overlap**: Consistent peak detection across experiments
- **Cell type concordance**: Agreement with reference scRNA-seq annotations
- **Marker gene validation**: Expected spatial patterns for known markers
- **Functional enrichment**: GO terms consistent with anatomical regions

#### 3.3 Comparative Results

##### 3.3.1 Performance Against Baseline Methods
- **Data quality parity**: Matched or exceeded single-modality spatial methods
- **No quality compromise**: Adding modalities didn't reduce individual modality performance
- **Enhanced clustering**: WNN integration revealed 20-30% more clusters than single modalities
- **Improved cell type resolution**: Identified rare populations like radial glia niches

##### 3.3.2 Key Biological Discoveries
1. **Neural development trajectory**: Mapped epigenetic dynamics from radial glia to neurons
2. **Bivalent chromatin dynamics**: Quantified changes during differentiation
3. **Gene regulatory networks**: Identified 411 DORC genes with regulatory relationships
4. **Tissue heterogeneity**: Discovered spatially restricted subclusters (e.g., DG-sgz vs DG-sg)

#### 3.4 Biological Validation Experiments

##### 3.4.1 Known Biology Confirmation
- **Mutually exclusive marks**: H3K27me3 and H3K27ac showed expected anticorrelation
- **Anatomical accuracy**: Clusters aligned with tissue histology
- **Developmental markers**: Correct spatial expression of Hand2, Sox2, Prox1

##### 3.4.2 Novel Findings Validation
- **Radial glia niche**: Confirmed by multiple modalities and marker genes
- **E2F bivalency**: Explained discrepancy between chromatin accessibility and expression
- **Isoform-specific regulation**: CD140a isoforms showed differential H3K27me3 regulation

#### 3.5 Application Demonstrations

##### 3.5.1 Developmental Biology
- Tracked neural differentiation with integrated epigenome-transcriptome dynamics
- Revealed spatiotemporal gene regulation during embryonic development

##### 3.5.2 Disease Research
- Successfully profiled EAE mouse model of neuroinflammation
- Detected immune cell infiltration and regional molecular changes

##### 3.5.3 Tissue Architecture
- Mapped complex brain regions with enhanced resolution
- Identified functionally distinct tissue compartments

### Key Strengths and Impact

1. **Technical robustness**: Comprehensive validation across tissues, resolutions, and modalities
2. **Biological relevance**: Discoveries aligned with known biology while revealing novel insights
3. **Broad applicability**: Demonstrated across development, adult tissues, and disease models
4. **Data quality**: Maintained high standards despite multiplexing complexity
5. **Future potential**: Platform for studying any tissue requiring multi-modal spatial analysis

The work demonstrates unusually broad spatial multimodal profiling in a shared tissue coordinate system. Its biological conclusions should still be read with pixel-mixture, score-derived, correlation, and pseudotime boundaries in mind.

### 4. Reproducibility Assessment

#### 4.1 Rating: 3/5 (Moderate)

**Strengths:**
- Core Snakemake preprocessing and downstream analysis scripts are released
- A detailed Fig. 1 tutorial and broad R analysis coverage are available
- Published vignette (Fig1_joint_analysis.Rmd) with tutorial
- Data available on Figshare (DOI: 10.6084/m9.figshare.27265410)

**Limitations:**
- Hardcoded file paths require user modification
- Some interactive R scripts have incomplete object references
- Large intermediate files not provided (users must reprocess from FASTQ)
- Reference datasets (MOCA, ENCODE) require separate download
- No locked environment or single end-to-end workflow rebuilds every paper figure; some scripts depend on undefined interactive objects

#### 4.2 Documentation Quality
- **doc_method.md**: Detailed methodology with equations and biological context
- **doc_code.md**: Complete code-paper mapping with verified fidelity
- **doc_analysis.md**: Comprehensive Chinese documentation of analysis workflow
- **figure_analysis.md**: Panel-by-panel analysis of all figures

### Related Documentation

| Document | Description |
|----------|-------------|
| doc_method.md | Detailed methodology, equations, and biological interpretation |
| doc_code.md | Code architecture and paper-code mapping |
| doc_analysis.md | Step-by-step analysis tutorial (Chinese) |
| figure_analysis.md | Comprehensive figure-by-figure analysis |
| README.md | Original repository documentation |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
