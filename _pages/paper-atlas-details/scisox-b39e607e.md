---
layout: default
permalink: /paper-atlas/scisox-b39e607e/
title: "ScIsoX"
nav: false
description: "ScIsoX 是一个用于单细胞 isoform/transcript 水平分析的描述性框架。它输入 gene count、transcript/isoform count、转录本注释和可选的细胞类型标签，输出每个基因的 7 个 isoform 复杂度指标、阈值分类、可视化和共表达结果。"
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
      <span>Representation Models</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>ScIsoX</h1>
    <p>ScIsoX: a multidimensional framework for measuring isoform-level transcriptomic complexity in single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03758-5" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ScIsoX 方法中文解读

### 一句话概览

ScIsoX 是一个用于单细胞 isoform/transcript 水平分析的描述性框架。它输入 gene count、transcript/isoform count、转录本注释和可选的细胞类型标签，输出每个基因的 7 个 isoform 复杂度指标、阈值分类、可视化和共表达结果。核心思想是用 Single-Cell Hierarchical Tensor (SCHT) 把每个基因表示成自己的 isoform-by-cell 矩阵，避免把所有基因硬塞进需要大量 zero padding 的三维张量。

### 1. 生物学问题与建模目标

这篇论文关注的问题是：在单细胞尺度下，同一个基因的多个 isoform 是如何在细胞内、细胞间和细胞类型之间组织的。传统 gene-level 单细胞分析会把多个 isoform 合并成一个基因表达量；transcript-by-cell 矩阵虽然保留 transcript，但缺少按基因组织的结构。ScIsoX 的目标不是预测或因果推断，而是系统地度量 isoform 使用模式的复杂度，帮助发现值得后续验证的基因、细胞类型和 isoform pair。

它能支持的解释是“某个基因在这个数据集中表现出高 isoform diversity、细胞类型特异性或共表达候选模式”。它不能单独证明 isoform 的功能、调控机制或条件间显著差异。论文也明确说明核心复杂度指标没有内置条件比较的 p 值，正式统计检验需要导出指标后按实验设计另做。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 细胞集合 | $\mathcal{C}$ | QC 后保留的单细胞 | `doc_method.md` |
| HVG 集合 | $\mathcal{G}$ / `hvg_result$var_genes` | 进入复杂度分析的高变基因 | `doc_code.md` |
| 基因矩阵 | $\mathbf{X}_g$ / `iso_mat` | 基因 $g$ 的 isoform-by-cell 表达矩阵 | `ScIsoX_code/R/create_scht.R:519-728` |
| 细胞类型矩阵 | $\mathbf{X}_g^{(k)}$ / `cell_type_matrices` | 某个细胞类型内的 isoform-by-cell 子矩阵 | `ScIsoX_code/R/create_scht.R:935-962` |
| 复杂度结果 | `transcriptomic_complexity` | metrics、thresholds、classifications、cell type metrics | `ScIsoX_code/R/complexity_metrics.R:4374-4608` |
| 共表达结果 | correlation/conservation/switching | isoform pair 的相关性、保守性和切换候选 | `doc_code.md` |

### 3. 方法主流程

1. 准备输入：gene count、transcript count、transcript annotation 和可选 `cell_info`。代码中 `create_transcript_info()` 可从 GTF 提取 transcript/gene ID；`generate_gene_counts()` 可在简单命名约定下从 isoform count 汇总 gene count。
2. 做 QC：基因按检测细胞比例和平均表达过滤，细胞按 detected genes 数量上下界过滤。默认参数包括 `n_hvg=3000`、`min_genes_per_cell=200`、`max_genes_per_cell=20000`、`min_cells_expressing=0.02`、`min_expr=1e-4`。
3. 做归一化：raw count 走 CPM + `log2(x+1)`；已经 normalised 的输入只做 `log2(x+1)`。
4. 选 HVG：按 variance-to-mean dispersion 排序，默认取前 3000 个基因。
5. 构建 SCHT：把 transcript matrix 按 gene 拆成每个基因一个 isoform-by-cell 矩阵，去掉全零 transcript 和只剩一个 isoform 的基因。
6. 加入细胞类型层：如果有 cell type metadata，构建 `IntegratedSCHT`，保存全局矩阵和每个 cell type 的子矩阵。
7. 计算 7 个核心指标：intra-cellular diversity、inter-cellular diversity、intra-cell-type heterogeneity、inter-cell-type specificity，以及 3 个 CV 型 variability 指标。
8. 阈值和分类：根据分布形态自适应估计阈值，再给每个指标赋予 high/low 或 insufficient-data 类别。
9. 可视化和共表达：生成 landscape、density、diversity comparison、profile、transition、radar、heatmap 和 co-expression/Shiny 分析。

### 4. 数学目标与直觉

SCHT 的核心对象是：

$$
\mathbf{X}_g\in\mathbb{R}_+^{I_g\times n}
$$

其中 $I_g$ 是基因 $g$ 的 isoform 数，$n$ 是细胞数。这个矩阵保留“一个基因内部有哪些 isoform、每个细胞表达多少”的结构。

细胞内多 isoform 共表达用归一化 Shannon entropy 衡量：

$$
H_j=\frac{-\sum_i p_{ij}\log_2(p_{ij})}{\log_2(n_j)},\quad
\mathrm{IDI}_{intra}(g)=\frac{\sum_j w_jH_j}{\sum_jw_j}
$$

直觉是：如果一个细胞内多个 isoform 比例均衡，entropy 高；如果只有一个 dominant isoform，entropy 低。$w_j$ 让表达量更高的细胞对基因级指标贡献更大。

群体层面的 isoform 多样性是：

$$
\mathrm{IDI}_{inter}(g)=
\frac{-\sum_i \bar{p}_i\log_2(\bar{p}_i)}{\log_2(I_g)}
$$

它衡量整个细胞群体中是否使用了多个 isoform。若 inter 高但 intra 低，常见解释是不同细胞或细胞类型选择不同 isoform。

细胞内/细胞类型间差异使用 Jensen-Shannon distance。CV 型指标如：

$$
\mathrm{HetVar}(g)=\frac{\sigma(\{\mathrm{Het}_k(g)\})}{\mu(\{\mathrm{Het}_k(g)\})}
$$

用于判断复杂度是否集中在特定 cell type 或 cell-type pair，而不是全局均匀存在。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| SCHT 构建 | `ScIsoX_code/R/create_scht.R:1550-1888` | 输入验证、QC、归一化、log transform、HVG、SCHT 创建 | 高 |
| 基因特异 isoform 矩阵 | `ScIsoX_code/R/create_scht.R:519-728` | 按 gene 提取 transcript，去掉全零和单 isoform 基因 | 高 |
| IntegratedSCHT | `ScIsoX_code/R/create_scht.R:935-962` | 存储 `original_results` 和 `cell_type_matrices` | 高 |
| 7 个核心指标 | `ScIsoX_code/R/complexity_metrics.R:29-452` | entropy、JS distance、CV 指标 | 高 |
| 阈值与分类 | `ScIsoX_code/R/complexity_metrics.R:3074-3739`; `3888-3959` | 分布识别、bootstrap/CV、标签分类 | 高 |
| 共表达分析 | `ScIsoX_code/R/coexpression_analysis.R:91-753` | correlation、switching、conservation、heatmap | 高 |
| Shiny 统计验证 | `ScIsoX_code/R/coexpression_shiny_app.R:1195-1350` | CI、100 次 bootstrap、BH FDR | 高，但主要在 app 路径 |
| 论文图复现脚本 | package source/vignettes/docs | 未找到 Fig. 1/2 和 dropout benchmark 的完整脚本 | 缺失 |

### 6. 结果如何解读

Fig. 1 显示 ScIsoX 的整体框架和三个数据集的 complexity landscape。PBMC 中 inter-cellular diversity 和 inter-cell-type specificity 的相关性很强，而 blood/brain 更分散，说明不同系统的 isoform 复杂度结构不同。

Fig. 2 展示具体分析方式：多数基因 inter-cellular diversity 高于 intra-cellular diversity，说明“不同细胞选择不同 isoform”比“同一细胞内共同表达多个 isoform”更常见；Irf8 heatmap 显示正负相关的 isoform 模块；Alt1、MS4A1、IKZF2 和脑发育 heatmap 展示 transition/profile/radar/heatmap 等解释方式。

重要的是，这些结果更适合作为 hypothesis generation。比如 Irf8 的 retained intron、NMD、nuclear detention、dominant-negative 等机制解释来自 ScIsoX 结果加公共注释和文献，不是论文中的直接功能实验。

### 7. 局限性与未验证部分

- 代码中未找到完整复现主文 Fig. 1/2 和 Fig. S10 dropout perturbation 的脚本；公共包实现了核心函数和图类型，但缺少 manuscript-level pipeline。
- 本地环境没有 `R`/`Rscript`，因此这次分析没有运行 R package check 或源码 parse test。
- 核心指标依赖上游 isoform quantification、batch correction、cell type annotation 的质量。
- 阈值和分类是 dataset-relative 的启发式边界，不应当当作跨研究通用生物状态。
- 共表达相关性不能证明因果调控；Shiny app 的 FDR/bootstrap 能增强统计描述，但不能替代功能验证。
- 代码实现中有一个潜在不一致：`IntegratedSCHT` 使用 `cell_type_matrices`，但 `calculate_ct_scht_sparsity()` 似乎读取 `cell_type_specific`。

### 8. 快速阅读路线

1. `summary.md`：先看论文解决什么问题、主要结果和复现评分。
2. `doc_method.md`：读完整数学定义、算法流程和计算框架。
3. `figure_analysis.md`：理解 Fig. 1/2 每个 panel 支持什么结论。
4. `doc_code.md`：查看论文-代码映射、精确源码位置和缺失脚本。
5. `claude_notes.md`：需要追溯证据、公式、假设和开放问题时读。
6. `paper source/PMC12455757/paper.md`：作为原文依据按需回查。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ScIsoX Summary

### Motivation And Novelty

ScIsoX addresses a gap in single-cell isoform analysis: isoform-resolved sequencing can measure transcript diversity inside individual cells, but common analysis workflows still treat expression as either gene-by-cell or transcript-by-cell matrices. Those formats make it awkward to ask whether one gene co-expresses multiple isoforms in the same cell, switches isoforms between cell types, or shows cell-type-specific heterogeneity.

The novelty is a framework rather than a predictive model. ScIsoX combines a Single-Cell Hierarchical Tensor (SCHT), seven isoform complexity metrics, adaptive thresholding, classification labels, visualization tools, and co-expression analysis. The SCHT stores one isoform-by-cell matrix per gene, avoiding the extensive zero padding required by a naive cell-by-gene-by-isoform tensor.

Compared with prior work, ScIsoX is complementary to isoform discovery and differential transcript usage methods. Isosceles (*Nature Communications*, 2024) focuses on long-read transcript discovery and quantification. Sierra (*Genome Biology*, 2020) and DTUrtle (*Bioinformatics*, 2021) test differential transcript usage between conditions. ScIsoX asks a different descriptive question: what isoform complexity patterns characterize a dataset before or alongside formal differential testing?

### Method Overview

Inputs are gene counts, transcript/isoform counts, transcript annotation, and optional cell type metadata. Raw counts are CPM-normalized and log-transformed; already normalized inputs are log-transformed. Genes and cells are filtered by QC thresholds, highly variable genes are selected by dispersion, and transcript rows are grouped by gene to form SCHT matrices.

The seven core metrics are:

| Metric | Meaning |
|---|---|
| Intra-cellular isoform diversity | Whether individual cells co-express multiple isoforms of a gene |
| Inter-cellular isoform diversity | How diverse isoform usage is across the whole cell population |
| Intra-cell-type heterogeneity | Cell-to-cell variation in isoform usage within a cell type |
| Inter-cell-type specificity | How different isoform profiles are across cell types |
| Intra-cell-type heterogeneity variability | Whether heterogeneity is concentrated in particular cell types |
| Inter-cell-type difference variability | Whether cell-type differences are concentrated in specific cell-type pairs |
| Cell-type-specific co-expression variability | Whether co-expression patterns differ by cell type |

Entropy measures diversity, Jensen-Shannon distance measures profile differences, and coefficients of variation measure context concentration. ScIsoX fits data-adaptive thresholds based on distribution shape and assigns biological labels such as "Strong Isoform Co-expression", "High Isoform Diversity", or "Cell-Type-Specific Isoform Expression". Undefined values are preserved for biologically meaningful boundary cases such as insufficient cell-type data.

### Evaluation

The paper evaluates ScIsoX on three public single-cell isoform datasets:

| Dataset | Technology / Source | Biological System | Main Use |
|---|---|---|---|
| Murine hematopoietic development | Nanopore, Wang et al. (*Science Advances*, 2022), GSE185555 / Zenodo | Early blood development | Complexity landscapes, Sox17, Alt1, Irf8 examples |
| Mouse/human brain development | Nanopore, Joglekar et al. (*Nature Neuroscience*, 2024) | Brain regions and developmental stages | Stage/region complexity patterns and heatmaps |
| Human PBMC | PacBio Kinnex, Al'Khafaji et al. (*Nature Biotechnology*, 2024) | Immune cell types | PBMC landscape, MS4A1, IKZF2 examples |

Key findings:

- Complexity landscapes differ across systems. PBMCs show a tight positive relationship between inter-cellular isoform diversity and inter-cell-type specificity, while blood and brain datasets have broader distributions.
- Most genes show higher inter-cellular than intra-cellular diversity, suggesting cell-type or cell-state isoform specialization is common. Genes below the diagonal are highlighted as co-expression candidates.
- Irf8 shows multiple isoform co-expression regimes. The Shiny app analysis reports FDR-corrected and bootstrap-supported patterns, but the biological mechanisms remain hypotheses supported by annotation and literature rather than direct perturbation.
- Isoform profile, transition, radar, and heatmap views reveal gene-level examples such as Alt1, MS4A1, IKZF2, and stage-specific brain clusters.
- Sparsity analysis supports the SCHT design: a naive 3D tensor would be over 98% sparse in the reported datasets, while SCHT avoids much of that zero padding.
- Runtime was reported on an Apple M1 Pro with 32 GB RAM: 147.9 s for blood, 177.9 s for brain, and 2498.0 s for PBMC across the reported workflow.
- Dropout perturbation on the brain dataset showed robust metric distributions; at 50% additional random dropout, the mean overlap coefficient across seven metrics remained 0.789 with negligible-to-small Cliff's delta.

### Reproducibility

**Rating: 4/5.**

Positive evidence:

- The paper is open access and converted cleanly from PMC.
- Public R package code is available at `https://github.com/ThaddeusWu/ScIsoX`, analyzed here at commit `cc5c1bd96c965e20b478f210f53efdb642c443dd`.
- Core functions match the paper closely: `create_scht()` implements preprocessing and SCHT construction; `calculate_isoform_complexity_metrics()` implements the seven metrics, adaptive thresholds, and classifications; visualization and co-expression functions cover the manuscript's plot types.
- Public datasets are listed with accessions or download sources.

Limitations:

- Exact scripts for reproducing the manuscript's full Fig. 1/2 panels and Fig. S10 dropout perturbation were not found in the public package.
- Runtime/package checks could not be run in this container because `R` and `Rscript` are unavailable.
- The framework depends on upstream isoform quantification, QC, batch correction, and cell type annotation quality.
- Core metrics are descriptive and exploratory; they do not provide built-in p-values for condition comparisons.

### Practical Takeaway

Use ScIsoX when the goal is to characterize isoform-level complexity patterns within a single-cell isoform dataset and nominate genes, cell types, or isoform pairs for follow-up. Treat its labels and visualizations as dataset-relative discovery tools. For formal condition comparisons or functional claims, export the metrics and apply an experimental design-specific statistical or validation workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
