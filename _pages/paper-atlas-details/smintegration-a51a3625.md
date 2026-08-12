---
layout: default
permalink: /paper-atlas/smintegration-a51a3625/
title: "SMIntegration"
nav: false
description: "SMIntegration 先让空间转录组和质谱成像在同一几何网格与预处理尺度上可比较，再以空间模式、拼接聚类、ROI 差异、相关网络和通路注释连接两种模态；它的价值在于可追踪的零代码分析链，主要风险则来自配准/插值、简单特征拼接、mass feature 身份不确定、空间伪重复以及隐藏的特征与像素抽样。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>GigaScience · 2026</span>
    </div>
    <h1>SMIntegration</h1>
    <p>SMIntegration: A web tool for comprehensive spatial metabolomics and transcriptomics integrated analysis and visualization</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/gigascience/giag033" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SMIntegration 方法解读：把空间转录组与空间质谱放进同一分析坐标系

### 1. 这是一套分析平台，而不是新的联合生成模型

SMIntegration 是面向空间转录组和空间代谢组/质谱成像的 R/Shiny Web 平台。它解决的是一条端到端分析链：将两种空间数据配准到共同网格，分别做归一化和空间特征识别，再在共同像素上进行联合聚类、区域差异分析、基因—mass feature 相关网络、通路注释和共定位可视化。

这里“integrated analysis”的核心是共同坐标、相容预处理和同像素特征拼接，不是学习一个能生成两个模态的深度潜变量模型。平台降低了交互门槛，但无法消除相邻切片的生物差异、分辨率不匹配、质谱峰鉴定不确定性或空间自相关对统计检验的影响。

### 2. 第一道门槛：空间配准与分辨率统一

两种模态可能来自相邻脑切片：Stereo-seq 的原始分辨率远高于 AFADESI-MS。论文要求先把高分辨率模态聚合到低分辨率尺度，再做几何配准。平台通过 RNiftyReg 提供刚性/线性 block matching 与非线性 free-form deformation；也允许在外部 SpatialData 生态完成配准后导入。

`server/S2_upload.R` 以代谢组 TIC 图和转录组总计数图作为配准图像，可调用 `niftyreg(..., scope='rigid')` 等变换。Python `spatialdata/script/knn_interpolation.py` 则读取已注册 SpatialData 坐标，以 KDTree 查询附近像素，并用距离权重将代谢信号插值到转录组网格。其权重本质上是对邻居距离进行反向缩放后归一化，最多搜索约 9 个代谢邻居。

配准只保证坐标可比较，不保证相邻切片的细胞或分子一一对应。非线性形变还可能制造局部共定位；因此必须用解剖标志、TIC/total-count 图和变换前后叠图检查，而不能把算法重叠自动视为生物共定位。

### 3. 预处理：两种模态不能盲目用同一种归一化

平台接收文本矩阵或 Seurat 对象。对空间代谢组，`RUNSCT()` 支持：

- TIC：每个像素除以该像素总离子强度，再乘 $10^4$；
- RMS：每个像素除以其所有 mass features 的均方根；
- 可选 `log1p` 变换和 scale。

转录组使用按文库深度的 LogNormalize。代码对零和/RMS 做保护，避免除零。随后可由 Seurat `FindVariableFeatures()` 选择高变特征；“前 2000”来自 Seurat 默认值，并非仓库显式固定的论文常数。

质谱矩阵中的一列通常只是 m/z mass feature。只有经过数据库匹配并满足鉴定证据的峰才应称为 metabolite；单同位素质量匹配通常只是较低置信等级。论文评审过程专门要求收紧这一表述，所以未确认峰不能被中文解读自动升级为已鉴定代谢物。

### 4. 空间模式：SpaGene、NMF 与双变量 Moran's I

平台分别在基因和 mass features 上调用 SpaGene。它先从坐标建立 kNN 图，对每个特征寻找高丰度子网络，并用基于 Earth mover's distance 的 EMDg 比较观察空间分布与随机置换背景，从而筛选空间可变特征。随后 NMF 将这些特征分成若干非负空间模式。

对两个模态的模式，代码用 `spdep::moran_bv()` 计算双变量 Moran's I，默认 k=5、99 次模拟。可以把它理解为：一个模态在像素 $i$ 的模式强度，是否与另一个模态在空间邻域中的模式强度共同变化。正值表示相似区域富集，负值表示互补分布。

双变量 Moran's I 是空间关联，不是基因控制代谢物的方向性证据。NMF 模式数、kNN 和置换次数都会影响结果；论文中的“gene pattern 2 与 mass pattern 3”属于该脑切片和参数下的经验模块。

### 5. 联合聚类实际做了什么

两个模态分别归一化、缩放后，`server/S4_clustering.R` 将共同像素上的矩阵按特征维拼接，形成一个像素×(基因+mass features)矩阵。平台提供 Louvain、LM、SLM、PCA 后 k-means 和 UMAP 后 k-means五种选择，并以 PCA 方差图帮助用户判断维度/聚类数。

因此，联合聚类的增益来自两组互补特征同时参与距离和图构建。它没有显式批次校正或模态权重学习：若一个模态的特征数、缩放或方差占优，联合空间会被该模态主导。论文小鼠脑示例中，代谢组单独识别 PAG，转录组单独识别 SCO，拼接聚类同时恢复两者；这是有力案例，但不是所有数据必然优于单模态的保证。

### 6. 细胞类型、ROI 与差异分析

转录组聚类可通过 SingleR 和本地 mouse/human reference 自动注释，也可由用户上传或手工指定。`server/S5_cell.R:138-154` 在 cluster 层面运行 SingleR，再把标签传播到共同坐标的另一个模态。传播得到的是空间区域标签，不表示质谱像素被直接测成某种单细胞类型。

用户可按聚类、细胞类型或交互 lasso ROI 定义两组像素。差异分析调用 Seurat `FindMarkers` 的 Wilcoxon rank-sum，先以 `min.pct=0`、`logfc.threshold=0` 全量计算，再按 fold change 与校正 P 值筛选。论文示例默认 $|\log_2FC|>0.26$、adjusted $P<0.05$。

这里每个像素被当成一个样本，但相邻像素具有强空间自相关，故有效独立样本数小于像素数；普通 Wilcoxon 的 P 值可能过于乐观。区域边界、配准插值和同一组织切片内的伪重复也需在解释时保留。差异结果更适合作为候选空间特征，而不是独立生物重复下的因果结论。

### 7. 基因—mass feature 网络与通路注释

平台对两组区域分别计算差异基因与差异 mass features 间的 Spearman 相关，并做 Bonferroni 校正。交互网络默认以 $|r|>0.6$、adjusted $P<0.01$ 过滤边；相同随机种子用于网络布局，使两组图的节点位置可对照。边表示共变或反向共变，不表示直接生化反应。

实现还有论文正文未充分展示的计算截断：`source/main_program/runcount.R` 在候选过多时最多保留显著性靠前的 300 个特征，并随机抽取 1000 个像素计算相关，且该抽样没有固定 seed。大型数据上重复运行可能得到略不同网络；缺失的边也可能只是截断所致。

通路模块使用本地 KEGG 106.0 与 HMDB/离子数据库，把差异基因和已注释 mass features 映射到通路，并排除全局 overview maps。它做的是 pathway annotation/共注释计数，而不是基于完整背景集和统计模型的严格富集推断。m/z 到代谢物的多对多或低置信映射会继续传播到通路层。

### 8. 图中证据应怎样理解

图 1 是七个分析模块的总览。图 2 展示联合聚类同时恢复 PAG 与 SCO，并用空间模式间 Moran's I 显示正/负关联。图 3 比较非端脑 astrocytes 与成熟 oligodendrocytes，给出差异特征与组特异相关网络。图 4 用 CA 与 PAG 的手工 ROI 对比，把差异基因和 mass features 注释到谷氨酸、GABA 和内源性大麻素等通路，并以 RGB/共表达图展示空间重叠。

这些结果支持平台能发现已知神经解剖结构和生成可解释假设。诸如 Bex2—spermidine 负相关、GABA—Slc32a1 共定位仍属于区域共变证据；相邻切片、mass feature 鉴定和空间平滑都使“直接调控”解释超出数据边界。

### 9. 版本、补充证据与复现边界

当前嵌套代码仓库 HEAD 是 `fc0756dc17bbf99819d4042b1f89d4ea002c5a35`。代码包含 11 个 Shiny server/UI 模块、R 分析函数、本地数据库、Python SpatialData 工具、示例数据，以及 preprocessing/clustering/differential/figure reproduction 验证脚本。核心平台—论文对应度高。

本地 PMC 目录还保存原稿、修订稿、公开审稿报告和作者回复。评审记录说明注册、TIC/RMS 归一化、参数指导、验证套件和更谨慎的 mass-feature 语言是在修订中强化的；应以最终 `paper.md` 和当前 commit 为准，不能用原稿描述代表当前平台。

完整运行仍需要 R 4.4.2、Shinyproxy/Docker、Seurat、SpaGene、SingleR、RNiftyReg、spdep、HMDB/KEGG 数据和 Python SpatialData 环境。仓库的大型 `.rds` 和数据库是示例/运行资源，但本轮未启动 Web 服务或复算全部论文图。云端 128 CPU/1 TB RAM 是论文部署配置，不是一般用户的最低硬件需求。

### 10. 一句话把握 SMIntegration

SMIntegration 先让空间转录组和质谱成像在同一几何网格与预处理尺度上可比较，再以空间模式、拼接聚类、ROI 差异、相关网络和通路注释连接两种模态；它的价值在于可追踪的零代码分析链，主要风险则来自配准/插值、简单特征拼接、mass feature 身份不确定、空间伪重复以及隐藏的特征与像素抽样。

### 证据入口

- 最终论文与图注：`paper source/PMC13159472/paper.md`
- 主图：`paper source/PMC13159472/images/`
- 公开补充审稿材料：`paper source/PMC13159472/*reviewer*.pdf` 与作者回复 PDF
- Shiny 模块：`SMIntegration/server/`
- 核心分析函数：`SMIntegration/source/`
- SpatialData 配准/插值：`SMIntegration/spatialdata/script/`
- 验证脚本：`SMIntegration/validation_pipeline/`、`SMIntegration/validation_figure/`
- 代码—论文逐项映射：`doc_code.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SMIntegration — Summary

### Motivation & Novelty

#### The Problem

Integrating spatial transcriptomics with spatial metabolomics links gene regulation (genotype) to metabolic output (phenotype) within anatomically defined tissue microenvironments. This is biologically powerful: you can ask not just "which cells are here?" but "what are they making, and why?" Recent experimental studies have demonstrated the value of this approach — Sun et al. 2023 (*Nature Cancer*) profiled gastric cancer metabolic remodeling, and Vicari et al. 2023 (*Nature Methods*) developed a simultaneous dual-modality protocol — but no standardized computational pipeline existed for the downstream joint analysis.

#### Limitations of Existing Tools

| Tool | Year | Limitation |
|---|---|---|
| SpatialGlue (*Nature Methods* 2024) | 2024 | Transcriptomics + proteomics only |
| Giotto (*Genome Biology* 2021) | 2021 | Transcriptomics + proteomics focus; no spatial metabolomics |
| SpaTrio (*Nature Computational Science* 2023) | 2023 | Links scRNA to spatial transcriptomics; not metabolomics |
| SODB (*Nature Methods* 2023) | 2023 | Data loading only; no joint analysis |
| MIIT (*Nucleic Acids Research* 2022) | 2022 | Registration only; no downstream interaction analysis |
| MISO (*Bioinformatics* 2023) / SOAPy | 2023 | Require Python/R programming expertise |

#### What's New

SMIntegration is the first GUI platform for spatial metabolomics + transcriptomics integration. Its core novelty is not in any single algorithm but in the **integration of the complete analytical workflow** — from registration through clustering through differential analysis through network construction — in a zero-code web interface. Key contributions:

1. **Cross-modal spatial registration module** (RNiftyReg + KNN interpolation) as a first-class analysis step within the GUI
2. **Joint clustering by matrix concatenation** — simple but effective for revealing spatial domains missed by single-modality analysis (PAG found by metabolomics, SCO found by transcriptomics, both found jointly)
3. **Group-specific gene–metabolite network construction** with same-layout visualization across conditions for direct comparison
4. **Cell type label transfer from transcriptomics to metabolomics** via coordinate mapping, enabling cell-type-specific metabolic analysis without metabolomics-native annotation

---

### Method Overview

SMIntegration is an R/Shiny web application (shinydashboard + Shinyproxy + Docker) implementing a 7-module spatial multi-omics integration pipeline:

**Module 1: Data upload & registration** — accepts TXT matrices or Seurat RDS; optional RNiftyReg-based image registration; KNN interpolation (Python, SpatialData format) to align metabolomics to transcriptomics pixel coordinates.

**Module 2: Spatial pattern analysis** — SpaGene package applies Earth mover's distance (EMDg) against a permutation null to identify spatially variable genes and metabolites; NMF groups SV features into spatial modules; bivariate Moran's I quantifies cross-modal pattern co-localization.

**Module 3: Clustering** — 5 algorithms (Louvain/LM/SLM via Seurat, PCA-kmeans, UMAP-kmeans); metabolomics-only, transcriptomics-only, and joint (matrix concatenation) clustering run in parallel; Sankey diagram shows concordance.

**Module 4: Cell type annotation** — SingleR with MouseRNAseqData/HumanPrimaryCellAtlasData references; labels transferred to metabolomics by coordinate matching; custom annotation upload supported.

**Module 5: Differential analysis** — ROI selection via lasso/clustering/cell-type; Wilcoxon rank-sum (Seurat FindMarkers, min.pct=0); Bonferroni correction; default |log2FC|>0.26, p<0.05.

**Module 6: Group-specific network** — Spearman correlation of top-300 DEGs and top-300 DAMs; 1000-pixel random sampling; |r|>0.6 and Bonferroni padj<0.01 edge filter; igraph/ggraph visualization with synchronized layout (seed=123).

**Module 7: Functional annotation** — KEGG 106.0 pathway mapping; co-annotation count of genes and metabolites per pathway; KEGG map visualization with spatial distribution overlay; RGB co-localization visualization.

**Biological assumptions**: adjacent tissue sections can be registered; each pixel is an independent sample for differential testing; matrix concatenation reveals joint spatial structure after separate normalization.

---

### Evaluation

#### Dataset
Mouse brain: 7-week-old male mouse coronal sections
- Spatial metabolomics: AFADESI-MS at 50 μm → 13,707 pixels, 560 annotated mass features
- Spatial transcriptomics: Stereo-seq binned to 50 μm → 14,605 pixels, 10,000 HVGs
- After KNN-interpolation and coordinate filtering: 14,530 valid overlapping pixels
- Metabolite annotation: Level 3 (putative, based on monoisotopic mass matching); not definitively identified

#### Key Results

| Analysis | Result |
|---|---|
| Joint clustering vs. single-modality | PAG identified by metabolomics-only; SCO identified by transcriptomics-only; **both identified jointly** |
| Cross-modal patterns | Metabolite pattern 3 + gene pattern 2 correlated (r=0.565, midbrain); both annotated to synaptic vesicle cycle, neuroactive ligand-receptor, cAMP signaling |
| Complementary patterns | Metabolite pattern 2 + gene pattern 4 negatively correlated (r=−0.607) |
| Cell-type specific (NA vs MO) | 1,255 DEGs (NA high), 382 DEGs (MO high); 58 DAMs (NA high), 45 DAMs (MO high) |
| GABA/Slc6a11 finding | Both flagged in GABAergic synapse pathway in NA astrocytes; consistent with astrocyte GABA transport function |
| Bex2/spermidine network | Negative correlation in MO but not NA; potential inhibitory relationship in oligodendrocyte immune context |
| CA vs PAG comparison | 1,484 DEGs → 212 pathways; 193 DAMs → 86 pathways; 54 shared pathways |
| PAG cannabinoid signaling | GABA and Slc32a1 (VGAT) co-upregulated in PAG → retrograde endocannabinoid pathway |
| Hippocampal glutamate | L-Glutamic acid + Grin2a upregulated in CA → NMDAR-dependent synaptic plasticity |

#### Benchmarking
Supplementary Table S1 provides runtime benchmarks across dataset sizes. No quantitative comparison to competing tools (e.g., SpatialGlue, MIIT) is performed — the paper positions SMIntegration as filling a capability gap rather than outperforming alternatives on shared benchmarks.

---

### Reproducibility Rating: 4/5

**Justification**: Code is publicly available (GitHub + Docker), cloud platform is live, example data deposited in CNCB OMIX (accession OMIX011674), validation pipeline (unit tests + figure reproduction scripts) included, WorkflowHub archive provided. The main gap reducing from 5/5:
- The 1000-pixel random sampling in Spearman correlation has no seed set → exact edge lists are non-reproducible between runs
- Metabolite annotation is Level 3 (putative); biological conclusions about specific metabolites should be treated cautiously
- Manuscript figures require specific RDS files from `spatialdata/data/` that are on GitHub but large

**Environment setup**:
```bash
# Docker (recommended)
docker pull mzlabresearch/smintegration
docker run -p 3838:3838 mzlabresearch/smintegration

# Or run locally in R ≥ 4.4.2 with ~70 packages installed
R -e "shiny::runApp('.')"
```

**Common pitfalls**:
1. `options(Seurat.object.assay.version='v3')` must be set — app hard-codes this in app.R:99; Seurat v5 default (v5 assay) will break downstream code
2. `SpaGene` package must be installed separately (Bioconductor or GitHub); not on CRAN
3. For local deployment, 30+ GB RAM recommended (S4 sets `future.globals.maxSize=30GB`)
4. Python ≥3.9 + `spatialdata` package required only if using the KNN interpolation preprocessing script

**Strengths**:
- Docker image makes deployment reproducible
- Modular validation suite (4 unit test scripts + figure reproduction scripts)
- Example data included for end-to-end testing
- WorkflowHub archive provides stable, versioned access

**Weaknesses**:
- No quantitative benchmarking against alternative tools
- 1000-pixel sampling without seed → network results vary between runs
- Top-300 feature cap undocumented; affects reproducibility for high-signal comparisons
- Metabolite Level 3 annotation means pathway findings are exploratory, not definitive

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
