---
layout: default
permalink: /paper-atlas/epigeneticcanceratlas-0bde0fcc/
title: "EpigeneticCancerAtlas"
nav: false
wide: true
description: "突变等遗传驱动因素已有较成熟的研究，但肿瘤发生、进展和转移过程中哪些染色质调控元件和转录因子在起作用仍不清楚。本文用单核 ATAC-seq（开放染色质）和单细胞/单核 RNA-seq（表达）构建跨 11 种癌症的图谱，比较正常组织、原发肿瘤和转移瘤。研究规模为 225 个 snATAC-seq 样本（约 101.9 万个细胞核）、206 个 RNA 样本（约 115."
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
      <span>Nature · 2023</span>
    </div>
    <h1>EpigeneticCancerAtlas</h1>
    <p>Epigenetic regulation during cancer transitions across 11 tumour types</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-023-06682-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for EpigeneticCancerAtlas">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ding-lab/PanCan_snATAC_publication" target="_blank" rel="noopener noreferrer" aria-label="Open code for EpigeneticCancerAtlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法说明：跨 11 种肿瘤转变的表观遗传调控

### 研究要解决什么问题？

突变等遗传驱动因素已有较成熟的研究，但肿瘤发生、进展和转移过程中哪些染色质调控元件和转录因子在起作用仍不清楚。本文用单核 ATAC-seq（开放染色质）和单细胞/单核 RNA-seq（表达）构建跨 11 种癌症的图谱，比较正常组织、原发肿瘤和转移瘤。研究规模为 225 个 snATAC-seq 样本（约 101.9 万个细胞核）、206 个 RNA 样本（约 115.8 万个细胞/细胞核），并结合 129 个同细胞 multiome 样本和 bulk WES（paper.md:35-54）。

### 为什么已有方法不够？

bulk ATAC-seq 把多种细胞混在一起，难以区分肿瘤细胞和免疫/基质细胞；单独的表达数据也不能直接定位调控元件。本文因此把单核开放染色质、RNA、TF motif、外部 ChIP-seq/CUT&RUN 和遗传/临床资料放在同一个样本和细胞类型框架中。这里的“epigenetic driver”是与癌症转变相关的调控元件或 TF 活性，属于关联性定义，不等同于已被扰动实验确证的因果驱动因子。

### 计算流程

```text
测序 reads
  -> Cell Ranger/Seurat/Signac 比对、过滤、去 doublet
  -> RNA: SCTransform-PCA；ATAC: TF-IDF-LSI；multiome: WNN
  -> 细胞类型注释和肿瘤-正常相关性
  -> 最近正常细胞（CNC）
  -> DACR/DEG 与通路富集
  -> ACR--基因 LinkPeaks（500 kb、弥散相关校正、CNV 过滤）
  -> SCENIC regulon（10 次运行，保留出现率 >=80%）
  -> motif/ChIP/CUT&RUN 验证
  -> 配对原发-转移 BCA/Slingshot 轨迹、lasso DACR
  -> TCGA 生存、HPV、突变和可成药靶点关联
```

### 关键步骤

1. **质量控制与整合。** RNA 保留 200–10,000 个基因、1,000–80,000 个 UMI、线粒体比例 ≤10%；ATAC 要求 peak fragments 1,000–20,000、reads-in-peaks >15%、blacklist <5%、nucleosome <5、TSS enrichment >2。RNA 用前 30/50 个 PCA，ATAC 用 2:30 LSI；同细胞 RNA PCA 与 ATAC LSI 通过 WNN 融合（paper.md:297-321, 369-390）。
2. **最近正常细胞和 DACR。** 对每个癌种，用肿瘤与组织来源正常细胞的可及性/表达 Pearson 相关定义 CNC（例如 PDAC 的 ductal-like-2、CRC 的 distal stem、ccRCC 的 proximal tubule）。再比较肿瘤与 CNC，得到增加或减少的 DACR，并按最近 TSS 映射基因；论文报告 22,187 个增加、29,074 个减少区域，其中 53% 为 enhancer、37% 为 promoter，约 75% 与邻近基因表达方向一致（paper.md:58-64, 429-452）。
3. **ACR 到基因。** 在同细胞 multiome 肿瘤细胞中，`LinkPeaks` 只考虑基因 TSS ±500 kb 的开放区域，要求相关 *r* >0.05、*P* <0.05。为排除“整个高可及区域都和高表达相关”的弥散效应，论文将染色体分成 100-kb 窗口，对 peak 与窗口相关系数分别 z-score，只保留高于所属窗口的链接，并去掉频繁 CNV 扩增基因（paper.md:537-541）。
4. **SCENIC regulon。** 在 SCT 表达矩阵中每个样本/细胞类型随机取 200 个细胞，GRNBoost2 推断 TF-靶基因关系；运行 10 次后保留至少 8 次出现的 TF，并保留至少 20 个靶基因的 regulon。AUCell 计算活性，再与 TF motif 可及性、ENCODE ChIP-seq 和 CUT&RUN 对照（paper.md:354-360）。
5. **转移轨迹。** 九个 CRC/UCEC 配对病例把正常、原发和转移细胞放入病例对象。BCA 在已知细胞类别监督下最大化类间方差，取前两个分量给 Slingshot；两类细胞的病例改用 LSI。所得 pseudotime 与 663 个 motif 分数做 Pearson 相关，再用 lasso 从大量 peak 中选择稀疏的转移相关 DACR 并做通路过度富集（paper.md:582-606）。

### 主要发现与如何理解

增强子可及性比启动子更能区分癌种和组织来源；约一半显著 ACR-基因链接位于 EpiMap enhancer，许多链接在 GeneHancer 中没有先例。跨癌种信号包括 *ABCC1*、*VEGFA* 调控区域以及 GATA/FOX motif；癌种特异例子包括 *ASAP2*、*EN1*、*FGF19* 和 PBX3。转移阶段富集 EMT、雌激素反应、apical junction、缺氧、TNF/KRAS 等通路。TCGA 中的 regulon 活性与生存或 HPV 状态相关，但这些结果是观察性关联，不是干预因果。

### 代码对应和限制

公开代码直接显示 multiome 的 SCTransform/PCA、TF-IDF/SVD、WNN（`Fig2/make_mutliome_objects/...R:18-45`）、500-kb `LinkPeaks`（`Fig2/ACR-to-gene_links/Compute_links_to_genes_v7.0.R:52-103`）、肿瘤-CNC logistic 回归 DACR（`Fig1/Cancer_DACRs/Tumor_normal_DACRs.CohortObj.R:55-128`）和十次 SCENIC 结果的 ≥8 次过滤（`Fig3/Post_SCENIC/Filter_regulons.R:15-58`）。但原始数据、注释 RDS、loom、`/diskmnt` 路径和完整轨迹/临床脚本不在快照中；因此端到端复现目前只能标为 Partial/MISSING（doc_code.md）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Epigenetic regulation during cancer transitions across 11 tumour types

### Problem

Cancer-associated epigenetic drivers are difficult to define from bulk averages and are less understood than mutations. This Nature 2023 study builds a single-nucleus chromatin-accessibility and transcriptomic atlas spanning normal, primary and metastatic states across 11 tumour types (paper.md:1-12, 35-54).

### What the study introduces

The atlas integrates 225 snATAC-seq samples (1.019 million nuclei), matched sc/snRNA-seq from 206 samples (1.158 million cells/nuclei), 129 same-cell snMultiome instances and bulk WES for 195 samples. It identifies closest normal cells (CNCs), differential accessible chromatin regions (DACRs), enhancer ACR-to-gene links, TF regulons and transition-associated pathways. Recurrent signals include *ABCC1*/*VEGFA* regulatory regions and GATA/FOX motifs; cancer-specific examples include *FGF19*, *ASAP2*, *EN1* and PBX3 (paper.md:1-12, 58-64, 67-106).

### High-level method

Cell Ranger/Seurat/Signac preprocessing yields RNA PCA, ATAC TF-IDF/LSI and WNN multiome representations. Tumour–normal correlations define CNCs; logistic/Wilcoxon differential tests identify DACRs/DEGs and pathway enrichments. Signac `LinkPeaks` links accessible regions to nearby genes, with 100-kb diffuse-correlation and copy-number controls. Ten stochastic SCENIC runs are filtered for reproducible regulons, scored by AUCell and checked against motifs, ChIP-seq and CUT&RUN. Nine paired CRC/UCEC cases use BCA plus Slingshot pseudotime, lasso-selected DACRs and pathway over-representation. TCGA regulon scores are evaluated with Kaplan–Meier/Cox models (doc_method.md; paper.md:297-606).

### Main evidence and evaluation

- The atlas separates tumour, immune, stromal and normal epithelial populations and reports 22,187 increased plus 29,074 decreased tumour-versus-CNC DACRs; 53% are enhancer-annotated and 37% promoter-annotated, with ~75% matching nearest-gene expression direction (paper.md:58-64).
- Enhancer accessibility is more cancer/tissue-specific than promoter accessibility and correlates more strongly with expression. Nearly half of significant links overlap EpiMap enhancers, while only 25–35% overlap GeneHancer interactions, suggesting many novel candidate links (paper.md:67-84).
- SCENIC yields 258 concordant regulons (20–4,310 targets; median 372), including 87 highly specific regulons. Motif accessibility and public binding data provide orthogonal support (paper.md:87-106).
- Metastatic analyses identify EMT, oestrogen-response, apical-junction, hypoxia, TNF and KRAS-associated programs; genetic-driver, survival, HPV and CIViC druggability panels extend the atlas to clinical hypotheses (paper.md:107-164).

### Reproducibility and limitations

The `PanCan_snATAC_publication` repository matches core multiome normalization/WNN, DACR testing, LinkPeaks and regulon filtering (doc_code.md). Fidelity is **medium**: scripts are figure-oriented, depend on `/diskmnt/...` and empty path variables, and require unavailable RDS/loom/annotation/data stores. The complete Cell Ranger/QC, BCA–Slingshot, survival/HPV and some clinical/figure workflows are not runnable from this snapshot; those claims remain paper-grounded or partial. No local supplementary Markdown was available, so supplementary tables/notes were not independently re-read. Reproducibility rating: **3/5** (core transformations inspectable; end-to-end regeneration blocked).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
