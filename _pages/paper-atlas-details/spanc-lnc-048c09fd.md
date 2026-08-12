---
layout: default
permalink: /paper-atlas/spanc-lnc-048c09fd/
title: "SPanC-Lnc"
nav: false
description: "SPanC-Lnc 是一个 pan-cancer lncRNA atlas/database。它把单细胞 RNA-seq 和空间转录组数据放在一起，用 TAR-scRNA-seq/HMM 流程先发现未注释的转录活跃区域，再把这些候选 lncRNA 放回癌种、细胞类型、空间位置和功能注释里解释。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>SPanC-Lnc</h1>
    <p>Unraveling lncRNA diversity at a single cell resolution and in a spatial context across different cancer types</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03071-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPanC-Lnc 方法中文解释

### 一句话概括

SPanC-Lnc 是一个 pan-cancer lncRNA atlas/database。它把单细胞 RNA-seq 和空间转录组数据放在一起，用 TAR-scRNA-seq/HMM 流程先发现未注释的转录活跃区域，再把这些候选 lncRNA 放回癌种、细胞类型、空间位置和功能注释里解释。

### 为什么需要这个方法

论文指出，传统 bulk RNA-seq 会丢失细胞类型和组织空间上下文，而 lncRNA 又常常低丰度、强细胞类型特异，并且依赖已有注释 [paper.md:18-27]。因此，作者要解决的不是单个预测任务，而是建立一个可以查询和再分析的候选 lncRNA 资源。论文声称最终得到 219,442 个 potential lncRNAs，其中 94,795 个未注释，并提供 SPanC-Lnc 网站访问 [paper.md:9-12]。

### 核心流程

第一步是数据整合。作者使用 28 个 in-house ST 样本和 24 个 scRNA-seq 样本，覆盖 13 个癌种，并用 STOmics、Takara Bio Seeker、Xenium 和长读长空间测序做验证 [paper.md:33-53]。

第二步是发现 TAR/uTAR。论文采用 TAR-scRNA-seq pipeline：对 10x SpaceRanger/CellRanger 生成的 position-sorted BAM，用 GroHMM 的 two-state HMM 判断基因组 bin 是否 transcriptionally active。论文描述默认 50 bp bin、至少 3 条 reads、500 bp 内合并 TAR，并承认相邻转录本可能被错误合并 [paper.md:258-261]。代码可验证的是，`Snakefile` 从 `cellranger_config.yaml` 读取 `MERGEBP`、`THRESH`，调用 `SingleCellHMM_MW.bash`，再转换 refFlat/GTF、用 Drop-seq 工具标记 reads 和生成 count matrix [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure1/Fig1_Data_Analysis/uTAR_pipeline/spatial_singlecell/Snakefile:24-49, SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure1/Fig1_Data_Analysis/uTAR_pipeline/spatial_singlecell/Snakefile:103-158, SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure1/Fig1_Data_Analysis/uTAR_pipeline/spatial_singlecell/Snakefile:203-223]。

第三步是把 uTAR 合并成 cuTAR。每个样本里不和 GENCODE v43 注释基因重叠的 TAR 被称为 uTAR，跨样本重叠的 uTAR 合并成 cancer-associated uTARs，也就是 cuTARs，作为数据库条目 [paper.md:44-53]。

第四步是给 cuTAR 加证据层。论文声称用 TSS、PAS、splice junction、GENCODE v47、enhancer、GWAS/eQTL、CPAT、RNAsamba、AlphaGenome 等信息判断候选转录本是否像 lncRNA、有无结构和潜在调控意义 [paper.md:56-71, paper.md:264-285]。代码中能直接看到 CPAT/RNAsamba 的运行命令 [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure1/Fig1_Data_Analysis/coding_potential.R:13-32]，也能看到用 BEDTools window 分类 TSS/PAS/splice 证据的脚本 [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure1/Fig1_Data_Analysis/structure_evidence_characterization.sh:42-120]。代码中未找到 AlphaGenome 的直接运行脚本。

### 空间功能推断

SPanC-Lnc 的功能解释主要是关联证据。论文用 bivariate Moran's I 计算 cuTAR 和癌症相关 coding genes 在空间上的局部自相关：

$$
{I}_{\mathrm{T}}=\frac&#123;&#123;\Sigma }_{i}({\Sigma }_{j}{w}_&#123;&#123;ij}}{z}_{j,t-1}\times {z}_{i,t})}&#123;&#123;\Sigma }_{i}{z}_{i,t}^{2}}
$$

其中 $z_{i,t}$ 是中心 spot/cell 的 cuTAR 标准化表达，$z_{j,t-1}$ 是邻近 spot/cell 的 gene 标准化表达，$w_{ij}$ 是空间邻接权重 [paper.md:339-348]。代码可验证的是，`uTAR_Gene_morans_spatial.py` 用 `Queen.from_dataframe` 建邻接权重，调用 `Moran_Local_BV`，用 `p_sim < 0.05` 标记显著，再把 quadrant 映射成 HH/LH/LL/HL [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure3/Data_analysis/uTAR_Gene_morans_spatial.py:38-89]。

### 下游分析

hdWGCNA 用于 gene-cuTAR count matrix 的 coexpression module 分析。代码中能看到 `SetupForWGCNA`、`MetaspotsByGroups`、`ConstructNetwork`、`ModuleEigengenes` 和 `ModuleConnectivity` 等步骤 [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure3/Data_analysis/hdWGCNA.R:103-219]。

edgeR 用于细胞类型特异和治疗相关差异表达。论文写的是 pseudobulk edgeR，并用 `~celltype + sample` 控制 sample batch effect [paper.md:360-369]；代码中 melanoma 脚本把 Seurat 对象转 pseudobulk，过滤 library size 和 uTAR，构造 `model.matrix(~cluster+donor)`，再做 `glmQLFit`/`glmQLFTest` [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure4/Data_analysis/mel_vs_others_DE_manhattan_edger.R:1-68]。

Xenium 验证部分用 Seurat v5、SCTransform、PCA、Harmony/label transfer 等流程。代码中 `label_transfer_example_GBM.R` 直接实现了 `FindTransferAnchors` 和 `TransferData` 的标签迁移 [SPanc_Lnc_PanCancer_LncRNA_Atlas/Manuscript_files/Figure6/Data_analysis/label_transfer_example_GBM.R:16-90]。

### 代码边界

这个 repo 更像 manuscript analysis scripts，而不是完整软件包。TAR pipeline、结构证据、Moran、hdWGCNA、edgeR、Xenium label transfer 都有直接代码证据。代码中未找到 SPanC-Lnc website backend/frontend 的实现；root README 只是链接了两个外部仓库。HLPI-Ensemble 也只有环境文件，未找到直接 run script。因此，读这个 workspace 时应该把 SPanC-Lnc 理解为“资源构建和分析流程”，而不是可一键复现的工程产品。

### 如何理解结果

SPanC-Lnc 最强的价值是把候选 lncRNA 放到细胞类型、空间区域、癌种和验证平台中。Fig. 1 支持 atlas 构建，Fig. 2 支持 tumor-region 和跨平台验证，Fig. 3 支持空间共表达/功能假设，Fig. 4-5 展示 melanoma 和 medulloblastoma case studies，Fig. 6 展示 Xenium 和 survival examples。需要注意的是，共表达、RBP prediction、eQTL/GWAS overlap 和 survival association 都是候选功能证据，不等于因果机制证明。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPanC-Lnc Summary

### What Problem It Solves

SPanC-Lnc addresses the lack of cell-type and spatial context in lncRNA discovery. Existing lncRNA analyses are often annotation-dependent or bulk-tissue based; this paper uses single-cell RNA-seq and spatial transcriptomics to discover and annotate candidate lncRNAs across cancer tissues [paper.md:18-27].

### Core Contribution

The paper builds a pan-cancer lncRNA atlas/database from 28 ST and 24 scRNA-seq samples across 13 cancer types. It reports 219,442 potential lncRNAs, including 94,795 unannotated lncRNAs, and layers structural, coding-potential, regulatory, spatial, cell-type, validation and survival evidence onto the resulting cuTAR annotations [paper.md:9-12, paper.md:33-71].

### Method Overview

The discovery pipeline adopts TAR-scRNA-seq: aligned 10x BAMs are processed by GroHMM to identify transcriptionally active regions, which are overlapped with reference annotations to separate aTARs from uTARs; uTAR count matrices are generated with Drop-seq DigitalExpression [paper.md:258-261]. Overlapping uTARs across samples are merged into cuTARs and characterized using CPAT/RNAsamba, TSS/PAS/splice evidence, enhancer/eQTL/GWAS overlaps, AlphaGenome splice predictions, spatial coexpression, hdWGCNA, edgeR pseudobulk differential expression, Xenium validation and TCGA survival analysis.

### Code and Reproducibility

The acquired GitHub repository is a manuscript-analysis snapshot, not the complete database/website codebase. It exactly supports several analysis components: Snakemake TAR calling and Drop-seq count extraction, CPAT/RNAsamba runs, structural-evidence BEDTools windows, bivariate Moran labels, hdWGCNA, edgeR pseudobulk DE and Xenium label transfer. Important gaps remain: website backend/frontend code is only linked externally, and HLPI-Ensemble has an environment file but no located run script. Reproducibility rating: **3/5**. The major analyses are traceable, but many scripts use absolute paths and notebooks/HTML artifacts.

### Main Evidence

Fig. 1 supports atlas construction and cuTAR characterization. Fig. 2 supports tumor-region enrichment and cross-platform validation. Fig. 3 supports spatial coexpression and functional hypothesis generation. Figs. 4-5 show cell-type and therapy/drug-response examples. Fig. 6 supports Xenium validation and survival association examples.

### Limitations

Most cuTAR functional interpretations are associative. Spatial coexpression, RBP prediction, enhancer/eQTL/GWAS overlaps and survival curves nominate candidates rather than proving causal lncRNA functions. Transcript boundaries are estimated from short-read and spatial data, and the paper itself notes that merging nearby TARs can incorrectly combine adjacent transcripts [paper.md:258-261].

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
