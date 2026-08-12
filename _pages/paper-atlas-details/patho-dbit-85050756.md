---
layout: default
permalink: /paper-atlas/patho-dbit-85050756/
title: "Patho-DBiT"
nav: false
description: "Patho-DBiT 的关键不是单纯提高 mRNA 数量，而是先在组织内给 FFPE 产生的各种 RNA 片段统一加上 poly(A) 尾，再用 DBiT 的二维微流控条形码标记空间位置。这样，同一套测序数据不仅能生成空间基因表达矩阵，还能追踪非编码 RNA、可变剪接、A-to-I RNA 编辑、spliced/unspliced dynamics 和 RNA 层 SNV。"
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
      <span>Cell · 2024</span>
    </div>
    <h1>Patho-DBiT</h1>
    <p>Patho-DBiT enables spatial whole transcriptome sequencing in clinical FFPE tissues</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2024.09.001" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Patho-DBiT 方法解读：在 FFPE 病理切片中同时读取空间表达、RNA 加工与变异

### 一句话理解

Patho-DBiT 的关键不是单纯提高 mRNA 数量，而是先在组织内给 FFPE 产生的各种 RNA 片段统一加上 poly(A) 尾，再用 DBiT 的二维微流控条形码标记空间位置。这样，同一套测序数据不仅能生成空间基因表达矩阵，还能追踪非编码 RNA、可变剪接、A-to-I RNA 编辑、spliced/unspliced dynamics 和 RNA 层 SNV。

它是一套“分子捕获平台 + 空间条形码 + 多分支计算流程”，而不是把所有信号压成一个联合模型。

### 1. 为什么 FFPE 难，又为什么能变成机会

临床病理库大量保存 formalin-fixed paraffin-embedded（FFPE）组织。固定产生核酸—蛋白交联，长期保存导致 RNA 断裂和天然 3' poly(A) 尾丢失。传统 oligo-dT 空间转录组因此容易只捕获残存的 polyadenylated mRNA 末端，难以覆盖短 RNA、非编码 RNA、剪接 junction 和全基因体变异。

Patho-DBiT 的思路是接受“RNA 已经碎了”这一现实：在去石蜡、热解交联和 permeabilization 后，用 *E. coli* poly(A) polymerase 在组织内给可接近的 RNA 片段追加 poly(A)。随后 oligo-dT 引物进行 reverse transcription。原本没有天然 poly(A) 尾的 microRNA、tRNA、snoRNA、snRNA 等片段也可能进入 cDNA library。

这个策略同时会捕获占总 RNA 80%–90% 的 rRNA，所以平台在扩增后选择性去除 rRNA-derived amplicons。论文报告最终 rRNA reads 约 3%，表明“广谱加尾”和“后续减去高丰度无信息分子”必须成对理解。

### 2. 二维 DBiT 空间地址怎样形成

第一次微流控芯片有平行通道 A1–A50 或 A1–A100，第二块芯片旋转 90°，提供 B1–B50 或 B1–B100。两轮条形码在交叉点形成唯一二维地址 $(A_i,B_j)$。每条 cDNA 还携带 UMI，用于去除 PCR duplicate。

因此一个 pixel 的基本输出可写成：

$$
X_{g,ij}=\text{在空间地址 }(A_i,B_j)\text{ 上映射到基因 }g\text{ 的去重 UMI 数}.
$$

50×50 device 产生 2,500 个位置，100×100 device 产生 10,000 个位置。论文使用 50、20 和 10 μm pixel。小 pixel 提高空间分辨率，但每个位置读取的分子更少；50 μm pixel 通常包含多个细胞，不能直接叫 single-cell measurement。

### 3. 从 FASTQ 到表达矩阵

Read 1 保存 cDNA insert，Read 2 保存 spatial barcode A、barcode B 与 UMI。代码 `Sequence alignment/fastq_process.py` 和 `FASTQ_process.sh` 重排 Read 2，使其满足 ST Pipeline 输入契约；`ST_Pipeline.sh` 调用 ST Pipeline/STAR，将 Read 1 比对到人或鼠参考基因组并用 barcode whitelist 解码像素；`Convert_ENSEMBL_to_gene_name.sh` 转换表达矩阵的基因标识。

旧状态把 `code source` 误指向 `Mapping of non-coding RNAs/`，但真实代码范围是整个工作区：sequence alignment、ncRNA、alternative splicing、RNA editing、variant、RNA dynamics 和 visualization 都是论文计算链的一部分。

### 4. 为什么它能看见更多 RNA 类型

Fig. 1 在 E13 mouse embryo 上展示完整技术链。Patho-DBiT 每个 50 μm pixel 平均检测 5,480 genes 和 15,381 UMIs，重复切片表达相关达到 $R=0.999$。相比 normal DBiT，gene-body coverage 更宽，5' UTR coverage 超过两倍。约 47% reads 映射到 protein-coding RNA，其余覆盖 lncRNA、microRNA、miscRNA、snoRNA、snRNA、scaRNA、tRNA、vault RNA、Y RNA 等；多数非编码 RNA 捕获率提高 10–100 倍。

microRNA 的关键验证不是只看数量。作者把 miR-142 knockout Ba/F3 cells 排成字母 Y，外侧为 wild type。空间 miR-142 信号应避开 Y 区域，得到 86.95% sensitivity、84.19% specificity。这个实验验证“短 read 能否落到正确空间和分子”，但仍受相似 microRNA 序列、多重比对和阈值影响。

代码中的 `Mapping of non-coding RNAs/Build GTFs/` 合并和拆分不同 RNA annotation，`count_ncRNAs.sh` 对各 ncRNA species 计数，`fine_name_human.R`/`fine_name_mouse.R` 整理命名。它是 annotation-driven mapping；未进入参考注释的分子不会凭空被发现。

### 5. 空间可变剪接：先聚合区域，再解释 isoform

Patho-DBiT 的广泛 gene-body coverage 提供 splice-junction reads。论文检测 SE、RI、A3SS、A5SS、MXE 五类事件。候选事件要求全切片聚合后 inclusion 和 skipping junction reads 都至少为 2；区域差异要求 exon inclusion level difference > 0.05 且 FDR ≤ 0.05。

代码 `Spatial alternative splicing/split_bam_by_clu.py` 按 pixel-to-cluster mapping 拆分 BAM，`rMATS_pipeline.sh` 对区域 pseudo-bulk BAM 运行 rMATS-turbo。这里的“空间剪接”主要依赖区域聚合，不是每个 pixel 都有稳定 PSI。论文自己指出 pixel-level coverage 偏低。

Fig. 2 展示 mouse brain 中 3,879 个 splicing events、2,368 个 parental genes，并用 *Myl6*、*Ppp3ca* 等例子显示相同总基因表达下的区域 isoform switching。正确解释是“区域 junction evidence 支持差异 isoform usage”，不是已经重建每个空间点的 full-length transcript。

### 6. A-to-I RNA 编辑：已知位点上的 A/G 计数

作者从 REDIportal V2.0 获得 107,095 个 mouse reference editing sites，用 samtools mpileup 统计每个位点的 A（unedited）和 G（edited）。候选位点要求全样本 coverage ≥10 且至少 1 条 edited read。编辑比例为：

$$
r=\frac{N_G}{N_A+N_G}.
$$

`Spatial A-to-I RNA editing/RNA_editing_pipeline.sh` 组织 mpileup 和后处理；`collecting_editing_sites.py` 将 site-level counts 聚合到 spot、cluster 和 gene。代码设置默认最小总 read count，并利用 spatial cluster annotation 输出统计。

Fig. 2 显示 thalamus 的平均 editing ratio 较高（27.9%），fiber tracts 较低（12.7%）；区域编辑率与 *Adarb1* 表达相关。与 long-read reference 共有的 259 个高覆盖位点相关约 $R=0.86$。这条流程只检查参考 editing sites，并不能自动区分未知 editing、测序错误、SNP 与 mapping artifact；质量阈值和 DNA 对照仍重要。

### 7. RNA dynamics：空间 spliced/unspliced 比例

`Spatial RNA dynamics/RNAdynamics.py` 读取 spliced、unspliced matrices、UMAP coordinates 和 pixel cluster labels，调用 scVelo 构建 velocity field。其生物假设是转录诱导和剪接动力学导致 unspliced/spliced 相位差，可推断状态变化方向。

在 MALT lymphoma 中，论文用 velocity 描述 tumor clusters 之间的 differentiation trajectory，并展示驱动流向的基因 phase portraits。空间邻近和 velocity 方向相互支持，但这仍是模型推断，不等价于 longitudinal lineage tracing；FFPE degradation 还可能对 unspliced 与 spliced reads 产生不同偏差。

### 8. 空间 SNV：从 RNA 变异到肿瘤亚克隆

Patho-DBiT 的 gene-body coverage 让 RNA reads 覆盖更多 genomic positions。论文用 Strelka germline mode 加 `-rna` flag 找候选 SNV，仅保留 PASS 且 counts ≥10 的位点。每个 pixel/位点编码为：0 无覆盖、1 wild type、2 heterozygous、3 homozygous mutation。

`Spatial variant analysis/pipeline/analyzeVariant.sh` 与 `VCF2Mut/` 将 VCF 和 spatial BAM 转为 mutation-by-pixel matrix；多个 R/Perl scripts 进行过滤、cluster 和可视化。`BWAmap.sh` 处理配对 WGS 供 DNA 层验证。

Fig. 5 的 MALT sample 中，SNV clusters M1/M3 与 transcriptomic tumor B-cell clusters 大量重叠，WGS 验证 RNA-level variants，并展示 *TBL1XR1*、*MAML2* 等空间突变。论文报告约 58.6% RNA-level SNVs 在 DNA 层被确认。剩余不一致可能来自 RNA editing、等位基因表达、coverage、比对偏差或假阳性，因此 RNA SNV matrix 不是完整 DNA genotype map。

### 9. 临床切片展示了什么

#### AITL：五年保存样本

Fig. 3 在 50 μm AITL section 中得到 10 个空间 clusters，平均 5,364 genes、11,989 UMIs/pixel。B/T/macrophage scores 与相邻切片 CODEX protein intensities 的 Pearson correlation 约 0.61–0.64。CXCL13-related interactions 和 AITL signaling 支持已知病理。这说明旧 FFPE 中仍能恢复组织结构，但 50 μm pixel 是混合细胞，cell-cell interaction 仍是表达共现推断。

#### MALT：三年保存样本

Fig. 4 用 20 μm、100×100 device 映射 10,000 spots，并以 IHC/IF 和 iStar super-resolution 对照。Fig. 5–6进一步结合 SNV、ncRNA、microRNA regulation 与 splicing dynamics 描述肿瘤亚区。

#### DLBCL 与病程比较

Fig. 7 比较同一患者更 aggressive 的 DLBCL，讨论 NF-κB、microenvironment 和 microRNA networks。病例展示提供可行性与假设生成，样本数不足以支持普适临床预测或治疗推荐。

### 10. iStar 超分辨率不是直接测量

iStar 将 H&E image tiles 经 vision transformer 提取 histology features，再用 weakly supervised feed-forward network 从 Patho-DBiT top variable genes 预测 superpixel expression，最后聚类 tissue architecture。

高分辨率图像提供形态边界，低分辨率 spatial counts 提供分子监督。输出是模型预测的 super-resolved expression，不是额外测到的 RNA molecules。评价时应区分 measured 20/50 μm pixels 与 inferred single-cell-scale map。

### 11. 代码覆盖和复现边界

本地代码与论文 GitHub `Zhiliang-Bai/Patho-DBiT` 内容匹配，覆盖：

- FASTQ reformat、ST Pipeline alignment、gene-name conversion；
- ncRNA GTF construction 和计数；
- cluster-level BAM splitting 与 rMATS；
- A-to-I site counting；
- scVelo RNA dynamics；
- BWA/Strelka/VCF-to-matrix variant workflow；
- Seurat clustering 和 MATLAB tissue-pixel identification。

但它是脚本集合，不是封装式 workflow。许多脚本有环境特定路径，需要外部 ST Pipeline、STAR、samtools、rMATS、Strelka、BWA、GATK、Seurat、scVelo、cgranges、MATLAB、reference genomes 与 annotation。上游 commit 没有保存在当前快照中，所以版本只能报告为“GitHub source, commit not recorded”。

### 12. 阅读和使用时的检查清单

1. 明确像素是 measured 还是 iStar inferred。
2. 报告 pixel size、tissue area、reads、UMIs、genes 和 mixture cells。
3. 检查 rRNA depletion、mapping category 和 multi-mapping policy。
4. ncRNA 结果注明 reference annotation 与同源序列风险。
5. splicing 优先做 region pseudo-bulk，不夸大 pixel-level PSI。
6. editing 报告 A/G coverage 阈值并排除 known SNP/mapping artifacts。
7. RNA SNV 必须尽可能用 WGS 或 orthogonal assay 验证。
8. velocity 作为方向性模型证据，不叫 lineage proof。
9. 临床 interaction/pathway 结果需要多样本与实验验证。
10. 保存每个脚本、reference 和外部工具版本，才能真正复现。

### 证据边界

本文依据本地 Cell 论文 Markdown、主图与补图图像、README、workspace-local CodeGraph 和直接脚本核读重新编写。论文 DOI 为 `10.1016/j.cell.2024.09.001`，代码来源为 `https://github.com/Zhiliang-Bai/Patho-DBiT`。本次未重跑 GSE274641、WGS、rMATS、Strelka、scVelo 或 iStar，也不把论文报告的临床发现表述为本地复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Patho-DBiT Paper Summary

**Publication**: Cell, November 2024 (Volume 187, Pages 6760-6779)
**DOI**: https://doi.org/10.1016/j.cell.2024.09.001
**Data**: GEO accession GSE274641
**Code**: https://github.com/Zhiliang-Bai/Patho-DBiT

### 1. Motivation and Novelty

#### Biological Problem Addressed
- **Core Challenge**: Current spatial transcriptomics methods primarily focus on mRNA expression, missing the rich diversity of RNA biology including splicing variants, non-coding RNAs, and RNA editing events
- **Clinical Gap**: Limited ability to spatially profile RNA in formalin-fixed paraffin-embedded (FFPE) tissues, which represent the vast majority of clinical pathology samples
- **Technical Limitations**:
  - RNA degradation and fragmentation in FFPE samples
  - Loss of poly(A) tails preventing oligo-dT primed reverse transcription
  - Chemical modifications resisting enzymatic reactions
  - Inability to capture small RNAs and splicing dynamics

> "The transcriptome in eukaryotic cells is a myriad of all dynamic and diverse RNA molecules, encompassing not only mature mRNAs encoding protein synthesis but also splicing variants, small RNAs, and other non-coding RNAs with regulatory functions." (Paper, Introduction)

#### Unique Contributions and Innovations
- **In situ polyadenylation strategy**: E. coli Poly(A) Polymerase adds poly(A) tails to all RNA fragments in situ, enabling capture of diverse RNA species regardless of original 3' end status
- **Pathology-compatible platform**: First comprehensive spatial transcriptomics method optimized for clinical FFPE samples stored for years
- **Multi-modal RNA profiling**: Simultaneous spatial mapping of:
  - Gene expression (mRNA)
  - Alternative splicing isoforms (5 event types: SE, RI, A3SS, A5SS, MXE)
  - Non-coding RNAs (microRNA, lncRNA, tRNA, snoRNA, snRNA, scaRNA, vault RNA, Y RNA)
  - A-to-I RNA editing events (validated against 107,095 reference sites from REDIportal)
  - Single-nucleotide variants (SNVs) via Strelka variant calling
  - RNA velocity/dynamics via scVelo
- **Clinical applicability**: Successfully profiled archival FFPE samples stored at room temperature for 3-5 years
- **Super-resolution integration**: Combined with iStar algorithm for single-cell level mapping

> "Patho-DBiT integrates in situ polyadenylation, microfluidic in tissue barcoding, and computational innovations to decode rich RNA biology inherent in FFPE samples." (Paper, Introduction)

#### Significance for Bioinformatics Community
- **Translational impact**: Unlocks vast biobanks of FFPE tissues for spatial genomics research
- **Comprehensive RNA biology**: Provides unprecedented spatial resolution of post-transcriptional regulation
- **Cancer research advancement**: Enables spatial discrimination of malignant subclones and tumor evolution
- **Diagnostic potential**: Could revolutionize pathology by adding molecular spatial context to histology

### 2. Method Overview

#### Algorithmic Framework and Core Ideas
- **Deterministic barcoding in tissue (DBiT)**: Microfluidic-based spatial barcoding using orthogonal channel arrays
- **Enzymatic polyadenylation**: E. coli Poly(A) Polymerase adds poly(A) tails to all RNA fragments
- **Spatial indexing**: Two-dimensional barcoding creates unique spatial addresses (50×50 or 100×100 grid)
- **rRNA depletion**: Selective removal of ribosomal RNA amplicons before sequencing

#### Key Technical Components

##### Molecular Biology Pipeline
1. **Tissue preparation**: Deparaffinization and heat-induced crosslink reversal
2. **In situ reactions**: Permeabilization → polyadenylation → reverse transcription
3. **Spatial barcoding**: Sequential ligation of DNA barcodes A and B using perpendicular microfluidic channels
4. **Library preparation**: Tissue lysis → cDNA extraction → template switch → PCR amplification

##### Computational Pipeline
1. **Sequence alignment**: ST Pipeline for spatial barcode decoding and genome mapping
2. **Non-coding RNA mapping**: Custom GTF building for various ncRNA species
3. **Alternative splicing**: rMATS for differential splicing analysis
4. **RNA editing detection**: Variant calling pipeline for A-to-I editing sites
5. **SNV analysis**: Genome-wide variant profiling for clonal discrimination
6. **RNA velocity**: scVelo for splicing dynamics and cell state transitions
7. **Super-resolution**: iStar integration for single-cell level mapping

#### Biological Assumptions and Model Design
- **RNA fragmentation as opportunity**: Leverages FFPE-induced fragmentation for comprehensive capture
- **Universal poly(A) tailing**: Assumes enzymatic access to 3' ends of all RNA fragments
- **Spatial coherence**: Adjacent pixels share biological similarity
- **Clonal architecture**: Malignant cells accumulate distinct SNV patterns
- **Splicing dynamics**: Unspliced/spliced RNA ratios indicate developmental trajectories

### 3. Evaluation Strategy

#### Datasets Used

##### Validation Datasets
- **Mouse embryo (E13)**: FFPE sections for method development and validation
- **Mouse brain**: Coronal sections for splicing and RNA editing analysis
- **Knockout cell lines**: miR-142 KO Ba/F3 cells for microRNA detection accuracy

##### Clinical Samples
- **AITL lymphoma**: 5-year archived FFPE tissue
- **MALT lymphoma**: 3-year archived gastric biopsy
- **DLBCL**: High-grade lymphoma for progression analysis
- **Healthy lymph node**: Control tissue for SNV baseline

#### Evaluation Metrics and Biological Relevance
- **Sensitivity metrics**:
  - Genes detected per pixel: 2,000-6,700 (varies by pixel size)
  - UMIs per pixel: 3,400-31,000
  - Non-coding RNA capture: 10-100× improvement over standard methods
- **Specificity validation**:
  - microRNA detection: 86.95% sensitivity, 84.19% specificity
  - Tissue-specific markers confirmed by ISH, IHC, and IF
  - RNA editing sites correlation with published long-read data (r=0.82)
- **Clinical relevance**:
  - Identified known lymphoma drivers (BCL2, TBL1XR1, MAML2)
  - Detected clonal evolution patterns
  - Revealed tumor microenvironment interactions

#### Comparative Results Against Baselines
- **vs. Visium FFPE**: Superior gene detection (5,480 vs. 3,000 genes at 50μm)
- **vs. Frozen tissue methods**: Better performance despite FFPE degradation
- **vs. scRNA-seq**: Higher genomic coverage for variant detection
- **vs. Standard DBiT**: Dramatically improved non-coding RNA capture
- **Cross-platform validation**:
  - CODEX protein imaging confirmed cell type assignments
  - WGS validated DNA-level SNVs
  - Long-read sequencing confirmed splicing isoforms

#### Biological Validation Experiments
- **Functional validation**:
  - Pathway analysis revealed cancer-specific signatures
  - microRNA regulatory networks matched known biology
  - Cell state transitions aligned with differentiation
- **Orthogonal techniques**:
  - H&E staining for morphology
  - Multi-color IHC for protein markers
  - ISH for RNA localization
  - IF for specific cell types
- **Clinical correlation**:
  - Ki67 staining confirmed proliferation differences
  - CD206 validated M2 macrophage polarization
  - Kappa/lambda chains verified clonality

#### Key Biological Insights
- **Lymphomagenesis mechanisms**: Spatial mapping of PI3K/AKT, NF-κB, and c-Myc activation
- **Tumor evolution**: Molecular trajectory from indolent MALT to aggressive DLBCL
- **Microenvironment remodeling**: Macrophage polarization and spatial redistribution
- **RNA regulatory networks**: microRNA-mRNA interactions driving tumorigenesis
- **Clonal architecture**: SNV and CNV patterns distinguishing malignant subclones

### 4. Paper-Code Mapping

#### Code Repository Structure
| Paper Section | Code Location | Description |
|--------------|---------------|-------------|
| Sequence alignment (Methods) | `Sequence alignment/` | FASTQ processing, ST Pipeline |
| Non-coding RNA mapping (Methods) | `Mapping of non-coding RNAs/` | GTF building, ncRNA quantification |
| Alternative splicing (Fig 2, Methods) | `Spatial alternative splicing/` | BAM splitting, rMATS pipeline |
| A-to-I RNA editing (Fig 2, Methods) | `Spatial A-to-I RNA editing/` | Editing site detection and quantification |
| SNV analysis (Fig 5, Methods) | `Spatial variant analysis/` | BWA mapping, Strelka variant calling |
| RNA dynamics (Fig S5, Methods) | `Spatial RNA dynamics/` | scVelo velocity analysis |
| Visualization (All figures) | `Spatial data visualization/` | Seurat clustering, spatial plots |

#### Key Scripts and Paper Methods
| Script | Paper Method Section |
|--------|---------------------|
| `fastq_process.py` | "Sequence alignment and generation of mRNA expression matrix" |
| `ST_Pipeline.sh` | ST Pipeline V1.7.6 with STAR V2.7.7a |
| `Build_GTF_Pipeline.sh` | "Read mapping of non-coding RNA species" (GENCODE, GtRNAdb, RNAcentral) |
| `split_bam_by_clu.py` | "Spatial alternative splicing analysis" - pseudo-bulk BAM generation |
| `rMATS_pipeline.sh` | rMATS-turbo V4.1.2 with "-t single -allow-clipping" |
| `collecting_editing_sites.py` | "Spatial adenosine-to-inosine (A-to-I) RNA editing analysis" |
| `RNAdynamics.py` | "Spatial RNA splicing dynamics" - scVelo analysis |
| `BWAmap.sh` | "WGS data alignment and analysis" - BWA V0.7.17, GATK |
| `analyzeVariant.sh` | "Spatial single nucleotide variant (SNV) analysis" - Strelka V2.9.10 |
| `Patho-DBiT_Clustering.Rmd` | "Gene data normalization and unsupervised clustering analysis" - Seurat V4 |

### 5. Performance Benchmarks

#### Detection Sensitivity
| Metric | Value | Condition |
|--------|-------|-----------|
| Genes per pixel | 5,480 (mean) | E13 mouse embryo, 50μm |
| UMIs per pixel | 15,381 (mean) | E13 mouse embryo, 50μm |
| Genes per pixel | 6,786 (mean) | Mouse brain, 50μm |
| UMIs per pixel | 31,063 (mean) | Mouse brain, 50μm |
| microRNA detection | 86.95% sensitivity, 84.19% specificity | miR-142 KO validation |
| microRNAs detected | 1,063 (embryo), 1,352 (MALT) | Different tissue types |
| RNA editing correlation | r=0.82 | vs. long-read nanopore sequencing |

#### Comparison with Existing Methods
| Comparison | Patho-DBiT | Competitor |
|------------|------------|------------|
| vs. Visium FFPE (55μm) | 5,480 genes/pixel | ~3,000 genes/pixel |
| vs. Normal DBiT-seq | 10-100× higher ncRNA capture | Baseline |
| vs. scRNA-seq | Higher genomic coverage | Limited to 3' end |
| Gene body coverage | ~2× higher at 5' UTR | Standard methods |

### 6. Key Equations and Formulas

#### Overlap Score for ncRNA Mapping
$$
\text{Overlap Score} = \frac{L_o - L_{no}}{L_a}
$$
Where:
- $L_o$ = overlapped length between query RNA fragment and annotation
- $L_{no}$ = non-overlapped length of query RNA fragment
- $L_a$ = total length of genomic annotation

#### A-to-I Editing Ratio
$$
\text{Editing Ratio} = \frac{N_{edited}}{N_{edited} + N_{reference}}
$$

#### Evolutionary Distance Between Clusters
$$
\text{Distance} = \frac{N_d}{N_v}
$$
Where:
- $N_d$ = number of sites with different genotypes between two clusters
- $N_v$ = number of valid sites in both clusters

### 7. Clinical Applications Demonstrated

#### AITL (5-year archived sample)
- 10 spatially organized clusters identified
- CXCL13-CXCR5 interaction validated as diagnostic marker
- PI3K/AKT, NF-κB, JAK/STAT pathway activation detected

#### MALT Lymphoma (3-year archived sample)
- 20 clusters at 20μm resolution (100×100 grid = 10,000 spots)
- Tumor discrimination via unsupervised SNV clustering (clusters M1, M3)
- 58.6% of RNA-level SNVs confirmed as DNA-level variants by WGS
- BCL2, TBL1XR1, MAML2 driver mutations identified

#### DLBCL Progression Analysis
- Cellular-level mapping at 10μm pixel size
- NF-κB signaling upregulation vs. MALT (p53, PTEN inhibition)
- M2 macrophage polarization (CD206+) in tumor microenvironment
- TGFB1-integrin family interactions identified

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
