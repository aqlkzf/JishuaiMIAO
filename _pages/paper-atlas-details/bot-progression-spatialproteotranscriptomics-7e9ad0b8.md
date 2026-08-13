---
layout: default
permalink: /paper-atlas/bot-progression-spatialproteotranscriptomics-7e9ad0b8/
title: "BOT_Progression_SpatialProteoTranscriptomics"
nav: false
description: "这篇论文用 Deep Visual Proteomics (DVP) 和 GeoMX spatial transcriptomics 研究卵巢 serous borderline tumor (SBT) 如何经过 micropapillary SBT (SBT-MP) 走向 invasive low-grade serous carcinoma (LGSC) 及其转移。"
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
      <span>Cancer Cell · 2025</span>
    </div>
    <h1>BOT_Progression_SpatialProteoTranscriptomics</h1>
    <p>Spatial proteo-transcriptomic profiling reveals the molecular landscape of borderline ovarian tumors and their invasive progression</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.ccell.2025.06.004" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for BOT_Progression_SpatialProteoTranscriptomics">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## BOT Progression Spatial Proteo-Transcriptomics 方法中文解读

### 一句话概览

这篇论文用 Deep Visual Proteomics (DVP) 和 GeoMX spatial transcriptomics 研究卵巢 serous borderline tumor (SBT) 如何经过 micropapillary SBT (SBT-MP) 走向 invasive low-grade serous carcinoma (LGSC) 及其转移。它不是提出一个新的软件算法，而是构建一个空间蛋白组-转录组整合流程，从组织切片、细胞类型分区、组学矩阵、统计分析到功能验证，最后提出 LGSC 的潜在治疗靶点。

### 1. 生物学问题与建模目标

LGSC 对传统 platinum/taxane 化疗反应差，但它的前体 SBT 通常预后较好。已有突变研究提示 SBT 和 LGSC 有共同来源，尤其与 MAPK 通路有关，但单靠基因突变无法解释非侵袭性病变如何变成侵袭和转移性肿瘤。

本文把这个问题建模为一个空间多组学比较任务：在 SBT、SBT-MP、LGSC-PT、LGSC-Met 四个病理阶段中，分别测量 epithelial tumor compartment 和 stromal compartment 的蛋白与转录本变化。输出不是一个单一预测分数，而是一组 progression markers、microenvironment programs、multi-omics latent factors 和可实验验证的候选靶点。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 病理阶段 | SBT, SBT-MP, LGSC-PT, LGSC-Met | 从非侵袭性边界瘤到原发和转移 LGSC 的假定进展轴 | `doc_method.md`, `claude_notes.md` |
| 空间蛋白组 | DVP protein matrix | AI 分割和激光显微切割后得到的细胞类型分辨蛋白丰度 | `doc_method.md` |
| 空间转录组 | GeoMX WTA counts | 串联切片 ROI 中的 compartment-resolved RNA counts | `doc_method.md` |
| 组学整合 | MOFA+ latent factors | 蛋白和转录本共同/特异变化的潜在因子 | `doc_method.md` |
| 功能验证 | siRNA, inhibitor, mouse model | 检验候选基因和药物组合是否影响迁移、增殖、侵袭和肿瘤负荷 | `figure_analysis.md` |

### 3. 方法主流程

1. 选择 FFPE 肿瘤切片，覆盖 SBT、SBT-MP、LGSC-PT 和匹配的 LGSC-Met。
2. 用免疫荧光和病理 ROI 标注区分 epithelial tumor 和 stroma。
3. DVP 分支：AI segmentation -> laser microdissection -> DIA-PASEF mass spectrometry -> DIA-NN quantification，得到 compartment-specific protein abundance matrix。
4. GeoMX 分支：在串联切片中选择匹配 ROI，进行 whole transcriptome probe hybridization、UV barcode release、NGS 和 QC/Q3 normalization。
5. 统计分析：对蛋白和转录本矩阵做 PCA、limma differential analysis、progression regression 和 GSEA。
6. 整合分析：匹配 DVP/GeoMX ROI，用 Pearson correlation 和 MOFA+ 找出跨模态或模态特异的 progression drivers。
7. 功能验证：用 IHC、siRNA knockdown、inhibitor testing、CAF conditioned media 和 mouse intervention 验证候选靶点。

### 4. 数学目标与直觉

论文没有提出新的封闭形式目标函数，核心是统计分析链：

- 对 protein intensities 和 GeoMX counts 做 log2 transformation，使不同样本的丰度比较更稳定。
- 用 limma 在组间比较中筛选差异分子，阈值为 adjusted *p* <= 0.05 且 logFC > 1.5。
- 用线性回归沿 SBT -> SBT-MP -> LGSC-PT -> LGSC-Met 轴寻找渐进变化。
- 用 PCA 判断样本在低维空间中是否按病理阶段分离。
- 用 MOFA+ 学习 latent factors，输入是已筛选的差异蛋白和转录本，输出是可以解释主要 variation 的因子和 feature weights。

直觉上，DE 和 regression 找到"哪些分子变了"，PCA/MOFA+回答"这些变化是否构成阶段结构"，功能实验回答"这些候选分子是否可能影响肿瘤行为"。

### 5. 复现与实现注意点

论文提供了 PRIDE `PXD046354` 和 GEO `GSE289044`，但没有本研究的完整分析脚本。因此代码层面不能直接验证 limma、MOFA+、CIBERSORTx、绘图和统计检验的具体实现。

复现时至少需要补齐：supplementary tables S1-S4、样本与 ROI 映射、DVP 和 GeoMX 原始/归一化矩阵、imputation 参数、DE feature 选择、MOFA+ 输入矩阵、CIBERSORTx reference 和各功能实验的完整统计设置。

### 6. 结果如何解读

`figure_analysis.md` 显示主线很清楚：Figure 2 支持 epithelial compartment 中 SBT-MP 是中间状态；Figure 3 支持 invasive LGSC 的 stroma 出现 ECM、adhesion、MMP 和 NNMT/CAF 重塑；Figure 4 说明 transcriptomics 补充了 c-MET、AP-1、VEGFA/HIF1A 等通路；Figure 5 用 MOFA+ 整合蛋白和 RNA 并提出靶点；Figure 6 和 Figure 7 把候选靶点推进到 siRNA、抑制剂和 mouse model。

需要注意的是，MOFA+ 的高权重 feature 不是因果证明，只是候选排序。真正的功能证据来自后续 knockdown、inhibitor 和 in vivo 实验。mirvetuximab soravtansine + milciclib 的结果是强 preclinical evidence，但还不是临床疗效证明。

### 7. 局限性与未验证部分

- 论文声称的计算分析没有 paper-specific code 可验证。
- supplementary tables 未在本地转换成 markdown，精确样本信息和靶点表仍缺失。
- SBT -> SBT-MP -> LGSC 的轴主要来自横截面队列和匹配转移样本，不能等同于每个病人的纵向轨迹。
- DVP 和 GeoMX 来自串联切片和匹配 ROI，仍可能受空间配准误差影响。
- cell line、CAF conditioned media 和 mouse model 支持功能假设，但不等于患者中的治疗效果。

### 8. 快速阅读路线

1. `summary.md`：先看问题、主要发现和复现评级。
2. `doc_method.md`：理解完整计算/实验流程和关键假设。
3. `figure_analysis.md`：按图理解每个证据链支持什么、不能支持什么。
4. `claude_notes.md`：查看证据 ledger、缺失代码和未解决问题。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Motivation and Novelty

Low-grade serous ovarian carcinoma (LGSC) is clinically distinct from high-grade serous ovarian cancer, but it is often treated with the same platinum/taxane chemotherapy despite poor response. Serous borderline tumors (SBTs) are considered LGSC precursors, and micropapillary SBT is associated with increased recurrence risk, yet the molecular transition from non-invasive SBT to invasive and metastatic LGSC has remained poorly understood.

This study builds a spatial proteo-transcriptomic atlas of SBT, SBT-MP, LGSC primary tumors, and matched metastases. Its novelty is not a new algorithm, but the integration of cell-type-resolved Deep Visual Proteomics, GeoMX spatial transcriptomics, MOFA+ multi-omics factor analysis, and functional validation to connect tissue architecture, compartment-specific molecular changes, and therapeutic hypotheses.

### Method Overview

The workflow starts with FFPE ovarian tumor sections reviewed by pathologists. Epithelial tumor and stromal compartments are profiled separately. DVP uses immunofluorescence, AI-based segmentation, laser microdissection, DIA-PASEF mass spectrometry, and DIA-NN quantification to measure thousands of proteins from small spatially resolved cell collections. GeoMX whole-transcriptome profiling measures RNA from matched serial-section ROIs.

The authors analyze protein and transcript matrices with PCA, limma differential abundance, regression across ordered histologic stages, GSEA, protein-transcript correlation, CIBERSORTx deconvolution, and MOFA+ factor analysis. The integrated target panel is then tested with IHC, siRNA knockdown, inhibitor assays, co-culture experiments, and an intraperitoneal mouse model.

Key biological findings:

- Epithelial proteomics supports SBT-MP as an intermediate state between SBT and LGSC.
- Invasive LGSC shows activation of MAPK, c-MET, CDK, FOLR1, and other targetable programs.
- NOVA2 is detected at the protein level in invasive LGSC but not SBT/SBT-MP, illustrating the value of proteomics.
- Stromal progression involves ECM remodeling, integrin/fibronectin adhesion, MMP/TIMP3 activity, gluconeogenesis, VEGFA/HIF1A, and NNMT.
- Knockdown and inhibitor experiments support functional roles for several omics-derived candidates.
- Mirvetuximab soravtansine plus milciclib reduces tumor weight, ascites, and tumor number in a mouse model.

### Evaluation

The discovery cohort includes SBT, SBT-MP, LGSC-PT, and matched LGSC-Met samples. DVP quantified a median of 5,456 proteins in epithelium and 3,919 in stroma. Spatial transcriptomics detected 9,872 targets after QC. Differential analysis found 963 epithelial proteins and 1,386 epithelial transcripts differing between SBT and LGSC-PT, plus 629 stromal proteins and 1,013 stromal transcripts.

The study uses several validation layers: IHC for markers including NOVA2, c-MET, ITGB1, FN1, NNMT, and FOLR1; siRNA screens and validation assays in LGSC cell lines; CAF conditioned-media experiments for NNMT; inhibitor testing in epithelial-only and co-culture settings; and in vivo treatment in a VOA6406ip1 intraperitoneal mouse model.

The main baselines are biological rather than algorithmic: SBT versus LGSC-PT, SBT-MP as a putative intermediate, LGSC-PT versus matched metastasis, control siRNA/shRNA, vehicle or single-agent treatment, and epithelial-only versus co-culture assay formats.

### Reproducibility

**Rating: 3/5.**

Strengths:

- The paper provides a detailed STAR Methods section with software names, versions, thresholds, and experimental protocols.
- Public data accessions are listed: PRIDE `PXD046354` for proteomics and GEO `GSE289044` for GeoMX transcriptomics.
- Main figures and the converted paper text are available locally in this workspace.

Limitations:

- No paper-specific code repository or analysis scripts were found during acquisition.
- Supplementary tables were not acquired as markdown, leaving exact sample metadata, target lists, and inhibitor-dose tables outside the local workspace.
- Several computational details, including full plotting scripts, all batch-handling choices, and exact MOFA+/CIBERSORTx execution scripts, are not code-verifiable here.

The paper is reproducible in principle from public data and methods, but reproducing the exact figures would require recovering supplementary tables and reconstructing unpublished analysis scripts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
