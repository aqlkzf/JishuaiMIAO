---
layout: default
permalink: /paper-atlas/ds-pfc-multiome-9d905340/
title: "DS_PFC_multiome"
nav: false
wide: true
description: "本研究询问：21 号染色体三体如何在 0–3 岁这一突触形成和髓鞘发育窗口改变人前额叶皮层。作者联合单核 RNA 与 ATAC，比较 Ctrl 和 Ts21，并用免疫染色验证关键胶质/免疫信号。它与妊娠中期 neocortex companion paper互补，关注出生后持续或新出现的异常。 QC 对 Ts21 使用适应性 UMI 阈值，避免额外 Chr21 剂量抬高 counts 后错误过滤。"
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
      <span>Science · 2026</span>
    </div>
    <h1>DS_PFC_multiome</h1>
    <p>Molecular and cellular processes disrupted in the early postnatal Down syndrome prefrontal cortex</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.aea1549" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DS_PFC_multiome">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DS 早期出生后前额叶皮层多组学图谱解读

### 问题与数据

本研究询问：21 号染色体三体如何在 0–3 岁这一突触形成和髓鞘发育窗口改变人前额叶皮层。作者联合单核 RNA 与 ATAC，比较 Ctrl 和 Ts21，并用免疫染色验证关键胶质/免疫信号。它与妊娠中期 neocortex companion paper互补，关注出生后持续或新出现的异常。

### 分析流程

```text
RNA → SoupX/Scrublet/QC → Seurat integration → NEBULA DEG、hdWGCNA、scCODA
ATAC → Signac/LSI/peaks → DAR、motif/footprint
RNA+ATAC → cell-type programs 与候选 TF 调控
OPC→oligodendrocyte → PHATE/Palantir trajectory
astrocyte/microglia → reactive states、ligand-receptor networks、组织染色验证
```

QC 对 Ts21 使用适应性 UMI 阈值，避免额外 Chr21 剂量抬高 counts 后错误过滤。差异表达使用能处理 donor pseudoreplication 的 NEBULA；组成用 scCODA；ATAC 结果以多种阈值和统计方法检验稳健性。公开 Zenodo v2 归档包含 RNA preprocessing、NEBULA/hdWGCNA/scCODA、Signac ATAC 和 motif 脚本，但缺少一键入口及部分下游分析。

### 核心发现

Ts21 的 HSA21 表达约增加 1.5 倍，但异常遍布全基因组；开放性增加的 DAR 比减少者约多 50 倍，说明并非简单剂量效应。L2/3 IT excitatory neurons 增多，而 excitatory 与 inhibitory neurons 共同下调大量 postsynaptic/AMPA-complex genes，65.5% 的下调突触基因跨两类神经元共享，提示 pan-neuronal synaptic deficit。

少突谱系中，Ts21 OPC 的 Palantir pseudotime 提前，但成熟调控程序不协调：HDAC8 repressor activity 增强，MYRF/NKX6-2 regulons 减弱。这更像异常推进与分化受阻并存，而不是正常加速髓鞘化。

astrocytes 中 AP-1/FOS-JUN 程序驱动反应性状态，Ts21 reactive astrocytes 比例显著升高；microglia 普遍呈 ITGAX、SPP1、SOCS3、FCGR2A 上升及 P2RY12/CX3CR1 等稳态标记下降。RUNX1–IFNGR2 正反馈与补体、抗原呈递和 HLA-DRB1 增强共同支持早期神经炎症；组织免疫荧光验证 HLA-DRB1+ microglia 增多。表达和 motif 网络仍是候选机制，不能替代 RUNX1/IFNGR2 扰动。

作者将代谢失衡、氧化应激、突触丢失、神经炎症、蛋白稳态受损和细胞死亡激活等六类神经退行性 hallmarks 定位到生命早期，提示 DS-associated neurodegeneration 的分子起点远早于临床痴呆。但样本量、尸检因素和横断面设计限制了因果与个体轨迹推断。

### 代码与复现边界

`RNA_preprocessing.zip` 实现 SoupX、Scrublet、QC、批次校正和注释；`RNA_downstream.zip` 包含 NEBULA、hdWGCNA、scCODA；`ATAC_preprocessing.zip` 含 Signac；`Motif_analysis.zip` 含 JASPAR motif enrichment/footprinting。核心预处理为 Exact/Partial，但 Palantir、完整 cell interaction、所有图表及验证统计并未形成完整可运行包。复现需要受控人脑数据、解压后重建路径和环境，并保留 `Not found` 项，不能把脚本归档等同于端到端复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DS_PFC_multiome: Summary

**Paper**: Molecular and cellular processes disrupted in the early postnatal Down syndrome prefrontal cortex
**Authors**: Ryan D. Risgaard†, Kalpana Hanthanan Arachchilage†, Sara A. Knaack†, Masoumeh Hosseini†, et al.
**Journal**: Science 392, eaea1549 (2026)
**DOI**: 10.1126/science.aea1549
**Corresponding author**: Andre M. M. Sousa (UW-Madison)

---

### Motivation & Novelty

#### Biological Problem

Down syndrome (Ts21) is the leading genetic cause of intellectual disability, affecting ~1 in 700 live births. Cognitive deficits — in executive function, working memory, language — appear in the first postnatal months and worsen throughout life. Most individuals with DS develop Alzheimer's disease–like dementia by midadulthood. Despite these clinical burdens, the cell type–specific molecular mechanisms underlying early postnatal brain disruption were unknown.

#### Limitations of Prior Approaches

- **Mouse models** (Ts65Dn, TcHV): Incomplete trisomy; human-specific cortical circuit complexity absent. Ts65Dn studies found interneuron imbalance (Contestabile et al., *Frontiers in Cellular Neuroscience* 2017) and OL deficits (Chakrabarti et al., *Nature Neuroscience* 2010), but translational fidelity is limited.
- **iPSC models**: Cannot recapitulate in vivo cellular diversity or neuronal–glial interaction organization (Saha & Jaenisch, *Cell Stem Cell* 2009; Qian et al., *Development* 2019).
- **Prior postmortem bulk studies**: Neuropathological and neuroimaging observations exist, but cell type resolution was unavailable.
- **Single-nucleus RNA-seq only**: Previous atlases lacked simultaneous chromatin accessibility, preventing inference of gene regulatory networks and enhancer-promoter relationships.
- **Lack of early postnatal data**: Existing single-cell transcriptomic data from DS brain focused on midgestation (companion paper: Vuong et al., *Science* 392, eaea1259, 2026) or adolescent/adult tissue. The critical 0–3 year synaptogenic window was uncharted.

#### Key Contributions

1. **First snMultiome atlas of early postnatal DS brain**: 220,956 nuclei from 5 DS/control pairs (0–3 years), simultaneously profiling gene expression + chromatin accessibility
2. **Genome-wide epigenetic rewiring beyond dosage effects**: ~50-fold more DARs gained than lost in Ts21; Chr19 (not just Chr21) shows disproportionate transcriptional dysregulation
3. **Pan-neuronal synaptic deficit**: 65.5% of down-regulated synaptic genes shared between excitatory and inhibitory neurons — PSD membrane–associated proteins including AMPA receptor complexes
4. **OL lineage progression impairment**: Increased Palantir pseudotime in Ts21 OPCs; HDAC8 repressor activity elevated across lineage; MYRF/NKX6-2 regulon attenuation
5. **Neuroinflammation signature with mechanistic dissection**: AP-1 complex drives reactive astrocytes; RUNX1-IFNGR2 positive feedback loop drives microglial activation; vascular-glial-immune feedforward axis
6. **Neurodegenerative hallmarks at postnatal onset**: 6/8 established neurodegeneration hallmarks (metabolic dysfunction, oxidative stress, synaptic loss, neuroinflammation, impaired proteostasis, cell death activation) present in 0–3 year old DS brain — shifting the onset timeline of DS-associated neurodegeneration

---

### Method Overview

#### Algorithmic Framework

Single-nucleus Multiome (RNA + ATAC) sequencing was applied to postmortem dlPFC tissue from 5 age-/sex-matched DS/control pairs. The computational pipeline involves:

1. **Aneuploidy-aware QC**: Genotype-specific adaptive UMI thresholds prevent over-filtering of Ts21 nuclei (extra Chr21 inflates counts by ~1.5×)
2. **Genotype-independent HVG selection**: Top 3,000 HVGs computed separately per condition before clustering to avoid dosage-driven confounding
3. **Ensemble doublet removal**: Consensus of DoubletFinder, Scrublet, and scDblFinder (≥2/3 votes required)
4. **Harmony batch correction** per genotype; joint UMAP after annotation
5. **NEBULA NBGMM-HL** for differential gene expression (accounts for cell-level overdispersion and sample-level random effects); model includes Condition, Sex, Age
6. **Signac + logistic regression** for differentially accessible chromatin regions (DARs); sex/age/peak count as latent variables
7. **SCENIC+ v1.0a1** multiomic GRN inference: topic modeling → enhancer-gene-TF regulatory networks
8. **CellChat v2.1.2** for ligand-receptor-mediated cell-cell communication
9. **hdWGCNA** for weighted coexpression network modules
10. **scCODA** for Bayesian compositional analysis of cell proportions
11. **Palantir + PHATE** for oligodendrocyte developmental trajectory

#### Key Technical Components

- Adaptive QC: Q3 + 3(Q3−Q1) threshold formula applied per genotype
- MACS2 peak calling per cell subclass × genotype (captures subpopulation-specific peaks)
- ATAC barcodes drawn from RNA-QC–filtered set (multiome paired design)
- SCENIC+ uses direct eRegulons: TF binding → chromatin change + gene expression change in same direction
- Ribosomal gene filtering (three HGNC gene groups) before NEBULA analysis

#### Biological Assumptions

- Cell type annotations are conserved enough across genotypes to allow direct comparison
- Endothelial cells serve as a stable compositional reference (scCODA)
- prOPCs at postnatal day 60 represent the developmental root of the oligodendrocyte trajectory
- Postmortem interval effects are captured by reactive astrocyte marker enrichment in controls (P53 pathway, hypoxia) vs. Ts21-specific reactivity patterns

---

### Evaluation

#### Datasets

- **Primary cohort**: 5 DS + 5 control postmortem dlPFC; ages 0–1,095 days (0–3 years); 3M/2F per group
- **Validation cohort (ddPCR/Western)**: Expanded cohort with additional biological samples (specific n not stated)
- **Cytokine validation cohort**: 10 DS + 10 control frozen frontal cortex samples (multiplexed immunoassay)

#### Metrics and Results

| Analysis | Key Finding | Statistical Support |
|---|---|---|
| Cell composition | ExN L2-3 IT significantly expanded in Ts21 | FDR < 0.05, scCODA |
| Chromatin accessibility | ~50-fold more DARs gained than lost in Ts21 | Robust to 3 statistical methods + multiple thresholds |
| Chr21 gene expression | ~1.5-fold average increase in Ts21 | P < 0.001, Mann-Whitney U |
| Chr19 dysregulation | Chr19 shows DARs + DEGs paralleling Chr21 | Fig. 2B-C |
| ExN L2-3 IT synaptic genes | PSD membrane down-regulation; CASP3 up | adj. P < 0.01, NEBULA |
| Pan-neuronal synaptic deficit | 65.5% down-regulated synaptic genes shared ExN/InN | SynGO analysis |
| OL pseudotime | OPCs show significantly higher pseudotime in Ts21 | P < 0.0001, unpaired t-test |
| Astrocyte reactivity | 51.8% Ts21 astrocytes reactive vs. 0.5% control | Marker-based classification |
| HSPB1 protein | Significantly increased in Ts21 cortex | P < 0.05, Western blot |
| Microglia activation | All Ts21 microglia show activation markers | ITGAX, SOCS3, FCGR2A up; SORL1, P2RY12, CX3CR1 down |
| HLA-DRB1+ microglia | Significantly increased in dlPFC | P < 0.0001, immunofluorescence |

#### Comparative Context

- **Companion paper** (Vuong et al., *Science* 392, eaea1259, 2026): Mid-gestational neocortex; confirms ExN L2-3 IT compositional expansion persists from prenatal to postnatal
- **Adult Ts21 dataset** (Palmer et al., *PNAS* 2021): Cross-validates ExN composition shifts extend through adolescence/adulthood
- **AD literature**: TREM2-APOE axis dysregulation, HLA-DRB1 elevation, and complement overexpression in DS microglia parallel AD-associated microglial states — supporting early-onset neurodegeneration model

---

### Reproducibility Rating: 3 / 5

**Justification**:
- **Strengths**: R and Python code for key analyses archived on Zenodo; clear parameter reporting; multiple orthogonal validation approaches; data available on dbGaP (phs004098.v1.p1); interactive Shiny app at daifengwanglab.shinyapps.io/DS_PFC/
- **Weaknesses**:
  - Raw alignment pipeline (BICAN WARP Multiome on AWS) not in archive; would require recreation
  - SCENIC+ and CellChat scripts not archived; only described in Methods
  - Chromosome-scale visualization (karyoploteR) not in archive
  - dbGaP controlled access requires application and approval (~months)
  - Hardcoded local Windows paths in R scripts (e.g., `setwd("C:/Users/hakma/Desktop/DS/")`) would need adaptation
  - No Docker/conda environment files for reproducibility
  - Some intermediate .RDS files referenced but not available

**Practical Notes**:
- Start from pre-processed fragment files if possible (WARP pipeline output)
- Install Seurat v5.1.0 (not v4.x — JoinLayers API changed significantly)
- SCENIC+ v1.0a1 is alpha; installation can be complex (pycisTopic dependencies)
- dbGaP access required; typical timeline 2–6 months for human postmortem data
- Shiny app allows exploration without data access

**Common Pitfalls**:
- Using standard UMI thresholds on Ts21 samples (loses ~20-30% of cells)
- Running FindVariableFeatures on merged control+Ts21 data (inflates Ts21-dosage genes as HVGs)
- Using LSI component 1 in ATAC batch correction (correlates with depth, not biology)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
