---
layout: default
permalink: /paper-atlas/npod-fae1c7e3/
title: "nPOD"
nav: false
description: "1 型糖尿病（T1D）不是只在确诊后发生的 beta 细胞丢失。自身抗体阳性（AAB+）阶段已经出现免疫和细胞状态变化，但以往研究常只分析纯化胰岛、单一组学或长期 T1D，难以区分哪些变化发生在什么细胞、何时出现、由哪些调控元件支持以及位于何种组织邻域。 本文分析 32 位 nPOD 全胰腺供体：11 位非糖尿病（ND）、9 位 ND AAB+、7 位近期 T1D（病程 5 年）。"
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
      <span>Atlases &amp; Resources</span>
    </div>
    <h1>nPOD</h1>
    <p>Single-cell multiome and spatial profiling reveals pancreas cell type-specific gene regulatory programs driving type 1 diabetes progression</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Gaulton-Lab/nPOD" target="_blank" rel="noopener noreferrer" aria-label="Open code for nPOD">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## nPOD 胰腺多组学图谱：从细胞状态到 T1D 调控网络

### 研究问题与数据设计

1 型糖尿病（T1D）不是只在确诊后发生的 beta 细胞丢失。自身抗体阳性（AAB+）阶段已经出现免疫和细胞状态变化，但以往研究常只分析纯化胰岛、单一组学或长期 T1D，难以区分哪些变化发生在什么细胞、何时出现、由哪些调控元件支持以及位于何种组织邻域。

本文分析 32 位 nPOD 全胰腺供体：11 位非糖尿病（ND）、9 位 ND AAB+、7 位近期 T1D（病程 <1 年）和 5 位长期 T1D（>5 年）。所有样本进行 snRNA-seq 和 snATAC-seq，8 位增加 joint multiome，6 位（3 ND、3 近期 T1D）进行 CosMx 空间转录组。最终得到 276,906 个表达核、203,348 个染色质核和 392,248 个空间细胞（论文 Results “A comprehensive, multimodal…”）。设计重点是用疾病阶段近似进展顺序，并非同一患者的纵向随访。

### 1. 建立统一的细胞类型表达图谱

snRNA 数据经 Cell Ranger、DoubletFinder、SoupX、SCTransform 和 Harmony 处理。Harmony 控制样本、性别和技术来源后进行图聚类，根据 marker 标注 12 类胰腺细胞及多个亚型，包括 beta/alpha/delta、ductal、acinar、免疫、stellate、endothelial 和 Schwann。acinar 又分 basal、high-enzyme、signaling、signaling/differentiation；这使外分泌系统不再被当作单一背景。

差异表达不把每个细胞当独立重复，而是按 donor×cell type 聚合成 pseudobulk，再用 DESeq2 比较 ND AAB+、近期和长期 T1D 对 ND。分析通常要求每个供体至少 20 个该类细胞，基因在每个条件至少两个样本表达；multiome 样本及质量异常样本 MM_426 从部分 DE 中排除。本地 notebook 记录了这些门槛，但 notebook 路径和预计算对象较多，复现需重建输入。

这里的疾病阶段差异应读为供体间关联。供体年龄、病程和组织质量虽被匹配或建模，仍不能像纵向实验一样证明时间因果。

### 2. snATAC 处理和跨模态标签转移

ATAC 管线先从 BAM 的 `CB` tag 提取 barcode，按 mapping quality 过滤，进行 fixmate、排序和 duplicate removal，再生成 tagAlign、MACS2 peaks、FRiP、promoter/TSS、mitochondrial 和 duplication 指标（`scripts/snATAC_pipeline_10X.py:15-136`）。通过 blacklist 后按基因组窗口生成稀疏可及性矩阵（`:139-174`）。

自定义 multiplet 清理利用片段端点邻接：共享片段连接的 barcode 形成 linkage，且不同 GEM group 不互相连接（`scripts/clean_barcode_multiplets_1.1.py:121-199`）；之后结合 AMULET 去除双细胞。此代码来自较旧 Python 生态，含 `iteritems`、`time.clock` 等版本敏感写法，不能假设在当前环境原样可运行。

snATAC 的细胞身份通过 Seurat anchor 从 snRNA 转移。8 位 joint multiome 中 RNA 与 ATAC 来自同一核，因此可作为内部真值检查；论文报告 cell-type 层面 >97% 一致，低于 0.5 的预测被过滤。跨模态标签仍依赖 RNA 参考是否覆盖真实 ATAC 状态，97% 并不保证所有细亚型同样准确。

### 3. 从开放染色质到候选调控元件

作者按细胞类型聚合 ATAC reads，用 MACS2 peak calling 定义候选 cis-regulatory elements（cRE），合并后得到 368,688 个 cRE，平均每类约 94.3k。细胞类型特异 cRE 由 logistic regression 比较目标类型和其他类型，同时控制测序深度等因素。

chromVAR 根据每个细胞的 motif 可及性偏差寻找潜在 TF 活性。结果恢复 endocrine 的 RFX/FOXA、ductal 的 HNF1/ONECUT/TEAD、T cell 的 RUNX/ETS 等已知程序，也分出 acinar 亚型。motif 表示某结构家族可能结合，不能仅凭 motif 区分高度相似的 TF；作者再要求同家族 TF 的表达与 motif 模式一致以缩小候选。

疾病差异 cRE 使用供体层面/混合模型控制伪重复。motif differential accessibility 将 donor 作为随机效应。本地 chromVAR 和 differential notebook 可追踪这一流程，但精确运行依赖外部对象与 notebook 状态。

### 4. ABC 如何把 cRE 连到靶基因

距离最近的 peak 不一定调控最近基因。Activity-by-Contact（ABC）将元件活性与三维接触频率结合，为 enhancer–gene 对计算分数；本研究平均每细胞类型得到 46,474 条 cRE–gene link，并以约 0.015 阈值保留候选。代码说明需要 hg19 Hi-C contact，因而在 hg38 分析坐标与 hg19 contact 间 liftover（`downstream_analysis/ABC_analysis.md`）。

ABC link 是基于活性和通用接触图的预测，不是该供体、该细胞中的直接 3C 测量。坐标转换、contact 参考和阈值都会影响边集合，应把它称为候选调控联系。

### 5. 构建细胞类型特异 GRN

每条 TF→gene 边需组合三类证据：目标基因有 ABC/promoter cRE；该 cRE 含 TF motif；TF 和靶基因在对应细胞类型表达。由此为 366 个 TF 建立细胞类型特异模块。模块进一步与 pathway gene set 做 Fisher exact test，将 TF 网络注释到 antigen presentation、interferon、代谢等过程。

网络过滤会去除异常大的 TF 模块（高于 gene count 的 90th percentile），并要求 TF 表达 TPM>5。该策略减少泛化 motif 产生的巨型网络，但也可能漏掉低表达、强效调控因子。

作者再用 CosMx 中观测到的靶基因表达和 TF–gene 权重拟合单变量模型，估计空间细胞中的 TF 活性，即使 TF 本身未被空间 panel 测量。NEUROD1/PAX6、BHLHA15、RUNX3 等结果提供空间一致性支持；它验证的是网络靶基因共同变化，而不是 TF 蛋白结合。

### 6. 空间细胞、邻域和 niche

CosMx 对 1,010 个基因成像，共 71 个 FOV、82.6M transcripts。初始无监督聚类后，作者用 moscot 从 snRNA 参考转移细粒度标签，并用 squidpy 检查邻域富集。随后以每个细胞周围 30 个细胞的 gene–gene covariance 定义局部状态，聚成六类 recurrent niche：三类 exocrine、endocrine、endo-exo 和 connective。niche 的 spatially variable genes 以 Moran's I>0.2、$P<0.05$ 筛选。

本地仓库没有 moscot 标签转移和 envi/covariance niche 构建代码；这些步骤只能由论文方法与外部软件说明支持，不能宣称在当前代码快照中复现。空间样本也只有 6 位供体，因此 niche abundance 的 T1D 比较应视为小样本证据。

### 7. 遗传风险如何提高“因果优先级”

作者把疾病差异 pathway 对应的 cRE/GRN 与 T1D GWAS fine-mapped variants 做 fgwas/FINRICH enrichment。若某细胞类型的某路径既在 AAB+/T1D 改变，又富集遗传风险变异，它比单纯疾病相关表达更接近上游机制。beta cell antigen presentation/interferon 及 IRF1 网络因此成为重点。

遗传富集支持“这些调控区域可能参与疾病易感”，但不会自动证明某一条 TF→gene 边或某个疾病阶段变化是因果。分析还依赖外部 GWAS summary/fine-mapping 数据，本地代码只能部分复现。

### 8. 细胞通信和功能实验

CellChat 从表达推断 1,939 对 ligand–receptor，论文报告 87,650 个显著交互，并用 100 次 permutation 比较疾病阶段。胰腺环境中 INS、GCG 等高丰度 RNA 容易形成 ambient contamination；代码显式将这些标志物在非来源细胞中列入 ligand blacklist，这是重要的实现修正。

空间共表达和邻近性为通信候选增加组织证据。作者进一步在 EndoC-BH1 beta 细胞中处理 BMP5 和 granulin：BMP5 引起 1,926 个 DEGs 并增强 TGF-beta 程序，granulin引起 491 个 DEGs并关联 beta 功能。功能实验说明这些配体能改变该细胞系表达，但不能完全重现人类胰腺中的来源、浓度和长期病程。

### 9. 主图的证据顺序

- Figure 1：样本、多模态细胞图谱、CosMx 空间标签、六类 niche 及疾病阶段组成变化。
- Figure 2：ATAC 图谱、motif/cRE、ABC–GRN 以及空间 TF 活性。
- Figure 3：各细胞类型在 AAB+、近期和长期 T1D 的表达与 pathway 变化，重点是 beta cell antigen presentation/interferon。
- Figure 4：疾病差异 cRE、motif 与 GRN，把表达改变连接到潜在调控机制和遗传风险。
- Figure 5：细胞间通信重连、空间支持及 BMP5/granulin 功能验证。

当前 OCR 工作区未提取独立 figure image 文件，因此 `figure_analysis.md` 的解读来自正文、图注和面板引用，而非本轮像素级复核；这一证据边界已明确保留。

### 总结与边界

这项工作的核心价值是把同一疾病进展框架中的 RNA、chromatin、joint multiome 和空间信息串成可检验链条：细胞状态变化 → cRE/motif → TF–gene 网络 → 遗传富集 → 组织 niche/通信 → 选定配体实验。最强结论是 beta 细胞 antigen presentation/IFN 调控以及外分泌和免疫系统在临床确诊前后已发生细胞类型特异变化。

需要避免三种过度解释：横断面阶段不等于真实纵向轨迹；ABC/GRN/CellChat 是预测网络而非直接结合或信号测量；空间分析供体少且关键 moscot/envi 代码不在本地仓库。复现时应把本地脚本可验证、paper-only、external dependency 三种证据分开。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Research Summary: Single-cell multiome and spatial profiling reveals pancreas cell type-specific gene regulatory programs driving type 1 diabetes progression

### Reproducibility Rating: 4/5

**Strengths:**
- Complete code repository with well-organized notebooks covering all major analyses
- Clear documentation of preprocessing steps and parameter choices
- Multiple modalities (snRNA-seq, snATAC-seq, multiome, spatial) with consistent processing pipelines
- Pseudobulk strategies properly account for pseudo-replication

**Limitations:**
- Some external data dependencies (ABC analysis requires Hi-C data in hg19 format)
- Raw data files require access to nPOD biorepository (PRJNA1141467)
- Spatial analysis partially relies on external moscot/squidpy packages without full parameter documentation
- Some hardcoded file paths in notebooks require modification

---

### Executive Summary

This study provides the most comprehensive single-cell multiomics atlas of the human pancreas across type 1 diabetes (T1D) progression stages, revealing cell type-specific regulatory programs driving disease. By integrating snRNA-seq (276,906 nuclei), snATAC-seq (203,348 nuclei), multiome data, and spatial transcriptomics (392,248 cells), the authors identified causal pathways including antigen presentation in beta cells that harbor T1D genetic variants.

---

### Motivation and Novelty

#### Biological Problem Addressed
Type 1 diabetes (T1D) is a complex autoimmune disorder involving the destruction of pancreatic beta cells, but the cell type-specific regulatory programs driving disease progression remain poorly understood. Previous single-cell studies have been limited by:

1. **Restricted disease stages**: Limited coverage of autoantibody-positive (AAB+) donors, particularly those with multiple AABs representing higher T1D risk
2. **Temporal limitations**: Focus on long-standing T1D rather than recent-onset disease with active pathogenic processes
3. **Cellular scope**: Emphasis on purified islets, missing exocrine pancreas involvement in T1D pathogenesis
4. **Technical limitations**: Lack of epigenomic profiling and spatial context needed to understand gene regulatory networks

#### Unique Contributions and Innovations

**Comprehensive Disease Stage Coverage**: Analysis of 32 nPOD donors across the full T1D progression spectrum:
- 11 non-diabetic (ND) controls
- 9 non-diabetic autoantibody-positive (ND AAB+), primarily multiple AAB+ donors
- 12 T1D donors (7 recent-onset <1 year, 5 long-duration >5 years)

**Multimodal Single-Cell Approach**: Integration of three cutting-edge technologies:
- Single-nucleus RNA-seq (snRNA-seq): 276,906 gene expression profiles
- Single-nucleus ATAC-seq (snATAC-seq): 203,348 chromatin accessibility profiles
- Single-cell multiome: Joint RNA+ATAC profiling in same nuclei
- Spatial transcriptomics: CosMx profiling of 392,248 cells in tissue context

**Whole Pancreas Profiling**: First comprehensive study of complete pancreatic cellular ecosystem including 12 cell types and multiple subtypes, revealing previously uncharacterized exocrine involvement in T1D.

**Causal Pathway Integration**: Novel combination of epigenomic changes with T1D genetic association data to identify pathways playing causal roles in disease development.

---

### Code-Paper Map

| Paper Section/Claim | Code Location | Verification Status |
|---------------------|---------------|---------------------|
| **snRNA-seq processing (DoubletFinder, SoupX)** | `Data_proccessing/snRNA_01_indSample_processing_SinglomeAndMultiome.ipynb` | Verified |
| **snATAC-seq processing** | `scripts/snATAC_pipeline_10X.py`, `Data_proccessing/snATAC_01_indSample_processing.ipynb` | Verified |
| **AMULET doublet detection** | `Data_proccessing/snATAC_02_AMULET_singlecellFile_singlomeOnly.ipynb` | Verified |
| **Harmony batch correction** | `Data_proccessing/snRNA_02_mergeSamples_clusterRNA.ipynb` | Verified |
| **Label transfer (RNA to ATAC)** | `Data_proccessing/snATAC_05_labelTransfer_github.ipynb` | Verified |
| **DESeq2 differential expression** | `downstream_analysis/RNA_differential_expression.ipynb` | Verified |
| **Pseudo-bulk creation** | `downstream_analysis/RNA_differential_expression.ipynb:43-90` | Verified |
| **fGSEA pathway enrichment** | `downstream_analysis/RNA_fGSEA_analysis.ipynb` | Verified |
| **chromVAR motif analysis** | `downstream_analysis/chromVAR/240209_WE_ChromVAR_01_Run_ChromVAR.ipynb` | Verified |
| **Motif differential accessibility** | `downstream_analysis/chromVAR/240209_WE_ChromVAR_02b_By_Condition_Analysis_lmer_Looped.ipynb` | Verified |
| **ABC cRE-gene linking** | `downstream_analysis/ABC_analysis.md` (external tool) | Partially Verified |
| **GRN construction** | `downstream_analysis/GRN/02_Final_GRN_Analysis_Commented-OnlyGRN.ipynb` | Verified |
| **TF-pathway Fisher's test** | `downstream_analysis/TFmodules_drivingPathways_FishersExact.ipynb` | Verified |
| **Differential cRE accessibility** | `downstream_analysis/Disease_differential_CREs_logisticRegression.ipynb` | Verified |
| **Marker cRE identification** | `downstream_analysis/Marker_CREs_logisticRegression_github.ipynb` | Verified |
| **CellChat cell-cell communication** | `downstream_analysis/CellChat/*.ipynb` | Verified |
| **fgwas genetic enrichment** | `downstream_analysis/file_prep_and_run_FINRICH.ipynb` | Partially Verified |
| **Spatial niche detection (envi)** | Not in repository (external tool) | Not Verified |
| **Spatial label transfer (moscot)** | Not in repository (external tool) | Not Verified |

---

### Method Overview

#### Algorithmic Framework and Core Ideas

**Integrated Multi-Scale Analysis Pipeline**:
1. **Cell Type Discovery**: Harmony-based integration followed by graph-based clustering to identify 12 pancreatic cell types and subtypes
2. **Epigenome-Transcriptome Linking**: Activity-by-contact (ABC) method to connect cis-regulatory elements (cREs) to target genes
3. **Gene Regulatory Network Construction**: Integration of (i) cRE-target gene links, (ii) TF sequence motifs, and (iii) expression levels to build cell type-specific GRNs
4. **Spatial Niche Detection**: Covariance-based neighborhood analysis identifying 6 recurrent multicellular niches
5. **Causal Inference**: fgwas enrichment testing to identify pathways with T1D genetic risk variants

#### Key Technical Components

**Chromatin Accessibility Analysis**:
- MACS2 peak calling on pseudo-bulk profiles per cell type
- chromVAR motif enrichment analysis across 366 transcription factors
- 368,688 total cREs identified with cell type-specific activity patterns

**Gene Regulatory Networks**:
- Average 46,474 cRE-target gene links per cell type using ABC method
- 366 TF regulatory networks constructed per cell type
- Spatial validation using univariate linear models predicting gene expression from TF-gene interaction weights

**Differential Analysis Framework**:
- DESeq2-based pseudo-bulk differential expression testing
- Linear mixed models for chromatin accessibility changes accounting for pseudo-replication
- Pathway enrichment using fGSEA with KEGG/Reactome databases

**Cell-Cell Communication Analysis**:
- CellChat inference using 1,939 ligand-receptor pairs
- 87,650 significant cell-cell interactions identified
- Spatial co-expression analysis using Moran's bivariate extension

---

### Key Findings

#### Beta Cell Antigen Presentation in T1D
- Up-regulation of MHC class I/II and interferon signaling pathways in AAB+ and T1D
- Strongest genetic enrichment (log enrich=4.48-6.00) for antigen presentation pathways
- IRF1 identified as key regulator with T1D risk variants at its locus

#### Exocrine Involvement
- Novel identification of altered metabolism and immune pathways in acinar cell subtypes
- T1D variant enrichment in acinar metabolic pathways
- Multiple acinar subtypes: basal, high-enzyme, signaling, signaling/differentiation

#### Spatial Niche Disruption
- Significant changes in endocrine and MUC5b+ ductal niches in T1D (p<0.05)
- Six recurrent multicellular niches identified

#### Cell Communication Rewiring
- 87,650 altered cell-cell interactions
- Novel ligands BMP5 and granulin functionally validated in EndoC-BH1 cells
- BMP5 exposure: 1,926 DEGs, upregulation of TGF-beta signaling
- Granulin treatment: 491 DEGs, enhanced beta cell function genes

---

### Evaluation Strategy

#### Datasets and Validation Approaches

**Primary Dataset**: 32 nPOD whole pancreas donors with comprehensive clinical characterization including autoantibody status, disease duration, age, sex, and BMI matching.

**Validation Cohort**: Integration with 48 additional donors from HPAP consortium (purified islets) to increase statistical power for endocrine cell analysis.

**Technical Validation**:
- Multiome data used as ground truth for label transfer accuracy assessment (>97% concordance)
- Spatial transcriptomics validation of cell-cell interaction predictions
- Known cell type marker gene expression confirmation across all modalities

#### Evaluation Metrics

**Cell Type Discovery Metrics**:
- Silhouette scores for cluster quality assessment
- Marker gene specificity (FDR<0.10) for biological validation
- Cross-modal correlation (r=0.98) between expression and chromatin cell type proportions

**Functional Validation**:
- TF motif enrichment in cell type-specific cREs (FDR<0.01)
- Pathway enrichment in marker gene sets (FDR<0.10)
- Gene regulatory network validation through spatial TF activity inference

**Disease Association Testing**:
- Differential expression/accessibility testing (FDR<0.10)
- Pathway enrichment for T1D genetic variants using fgwas
- Cell-cell interaction changes (permutation test, FDR<0.10)

---

### Data and Code Availability

- **Raw Data**: GEO (upon publication), BioProject PRJNA1141467
- **Spatial Data**: Zenodo
- **Code Repository**: https://github.com/Gaulton-Lab/nPOD and https://github.com/theislab/spatial_pancreas
- **Data Browser**: http://t1d-pancreas.isletgenomics.org

---

### Discrepancies and Hidden Details

1. **ABC Analysis Genome Build**: The paper uses ABC v0.2 which requires hg19 Hi-C data. Code includes liftover steps between hg38 and hg19 (see `downstream_analysis/ABC_analysis.md`).

2. **Sample Exclusions**: Multiome samples and sample MM_426 (nPOD id 6278) are excluded from differential expression analysis due to quality concerns.

3. **Gene Filtering**: Genes must be expressed in at least 2 samples per condition to be tested for differential expression.

4. **Cell Number Thresholds**: Minimum 20 cells per cell type per sample required for analysis, except for late T1D beta cells where all donors are included.

5. **chromVAR Variability Filter**: Motifs with variability >1.2 considered highly variable (178 of 692 motifs pass this threshold).

6. **GRN Filtering**: TF modules filtered to those with gene counts below 90th percentile and TF expression TPM >5.

7. **CellChat Blacklist**: Highly expressed cell-type specific genes (INS in beta, GCG in alpha, etc.) are blacklisted as ligands in non-expressing cell types to remove ambient contamination artifacts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
