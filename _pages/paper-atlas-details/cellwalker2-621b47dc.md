---
layout: default
permalink: /paper-atlas/cellwalker2-621b47dc/
title: "CellWalker2"
nav: false
description: "CellWalker2 把层级标签、不同模态细胞和 bulk 注释放入同一异构图，以随机游走整合跨边证据，再用置换空分布校正结构偏差；它擅长输出层级化的统计关联，但结论依赖 marker、树、图构造、默认参数和置换稳定性，不能被解释为直接的谱系或因果机制。"
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
      <span>Cell Genomics · 2025</span>
    </div>
    <h1>CellWalker2</h1>
    <p>CellWalker2: Multi-omic discovery using hierarchical cell type relationships</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.xgen.2025.100886" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellWalker2：用层级异构图统一细胞注释、多组学映射与批量注释定位

### 核心思想

CellWalker2 不把细胞类型当作彼此独立的平面标签，而把细胞、细胞类型标签、标签层级中的内部祖先节点，以及可选的基因集或基因组注释都放进同一张加权图。随机游走让证据沿细胞相似性、marker、染色质可及性和层级边传播，从而回答三类问题：给细胞注释；比较不同数据集/物种的细胞类型；把 bulk ChIP-seq、pRE、motif 或基因集定位到单细胞类型。

论文为 2025 年 Cell Genomics 原创方法论文（DOI `10.1016/j.xgen.2025.100886`），不是综述。

### 图怎样构造

节点分成三类：细胞节点 $C$、层级标签节点 $L$ 和可选注释节点 $A$。边表示不同证据：

- RNA 细胞间边来自 PCA 表达距离；ATAC 边来自 peak 的 cosine/Jaccard 相似度；multiome 将 RNA 与 ATAC 相似度加权后构造 SNN 图。
- 细胞–标签边是该细胞对标签 marker 的加权表达，marker 权重来自差异表达效应量。
- 标签–标签边来自给定树，允许信息到达叶节点和祖先节点。
- 细胞–注释边来自相应区域的 ATAC reads，或基因集表达。

因此未同时测量所有模态的细胞也可共存：RNA-only 没有 ATAC 注释边，ATAC-only 没有 marker 表达边，multiome 细胞通过两类边桥接它们。这不是对缺失模态作显式生成式插补，而是共享图上的证据传播。

源码中异构块矩阵在 `CellWalkR/R/CellWalkerFunctions.R:15-22` 和 `MapCellTypesFunctions.R:341-343` 组装；RNA/ATAC/multiome 图分别在 `DataParsingFunctions.R` 与 `DataParsingFunctionsExtra.R` 构造。代码默认 multiome 权重为 RNA 0.7、ATAC 0.3，并用 Seurat SNN，而不是简单裸 KNN。

### 随机游走与 influence

邻接矩阵按行归一化为转移矩阵 $W$。随机游走以概率 $r$ 回到起点，以 $1-r$ 沿边传播，其闭式 influence 矩阵为

$$
F=r\left[I-(1-r)W\right]^{-1}.
$$

$F_{ij}$ 表示从节点 $i$ 出发的游走访问节点 $j$ 的长期影响。默认 $r=0.5$；源码 `CellWalkR/R/CellWalkerFunctions.R:76-125` 使用 `solve()` 求闭式解，也保留迭代步数选项。闭式矩阵求逆会带来近似 $O(n^3)$ 的扩展瓶颈，所以大数据需要稀疏化、下采样或迭代路径。

层级树使相近亚型共享证据，也允许当分辨率不足时映射到内部祖先，而不是硬选一个叶子。但向上/向下权重决定证据扩散程度：论文推荐上行 1、下行 0.1，源码 `tree2Mat` 默认却是 1/1；要复现论文意图必须显式传参，不能依赖默认值。

### 置换 Z 分数为什么重要

原始 influence 会受节点度数、细胞数、测序深度和 marker 数影响。CellWalker2 通过保持边权分布区间的置换生成空分布，再计算

$$
Z_{ij}=\frac{F_{ij}-\mu_{ij}^{perm}}{\sigma_{ij}^{perm}}.
$$

源码用累计和与平方和避免保存全部置换矩阵（`CellWalkerFunctionsExtra.R:213-233`），默认约 50 轮，并把负 Z 分数截为 0。因此输出强调正关联；0 不等于“证明无关系”。稀有类型或置换方差很小时 Z 也可能不稳定，应增加置换并检查原始 influence。

细胞注释路径和跨标签比较并不完全相同：`annotateCells` 使用列内标准化 influence 后选标签，而 `mapCellTypes`/bulk annotation 使用置换 Z 分数。不能把所有输出统一称为同一种 permutation significance。

### 三类任务

1. **细胞注释**：查询细胞通过相似图与参考 marker/层级传播，输出最强的叶标签；层级可帮助 dropout、批次或稀有群体。
2. **跨数据集/物种类型比较**：把两套标签都放入图，读取 label–label Z 分数；一个类型可对应多个近缘叶或祖先节点，不被强迫一对一。
3. **bulk 注释定位**：把 ChIP-seq peaks、pRE、motif 或基因集作为节点，通过可及性/表达边传播到类型层级，得到 annotation–label Z 分数。

### 图 1–6 的证据链

- 图 1 定义异构图、边来源、随机游走和三类输出。
- 图 2 用模拟验证注释、层级映射和稀有类型鲁棒性，并用发育脑 pRE 与 CTCF ChIP-seq检验 bulk 注释定位。
- 图 3 在 PBMC 中比较跨研究类型、刺激状态和 TF 特异性，并与 ArchR、Signac、SCENIC+、SIMBA/ChIP-seq证据比较。
- 图 4–5 在人发育皮层验证细胞注释、祖先节点映射和 TF 定位。
- 图 6 扩展到人、狨猴、小鼠皮层，展示保守与物种特异的类型、通路和 TF 关联。

这些是图上统计关联与基准，不是谱系追踪或 TF 因果验证。marker、树结构和图参数本身包含先验；错误层级会系统性改变传播结果。

### 论文–代码与复现边界

- 主算法 R 包位于 `CellWalkR/`；论文图复现脚本在 `CellWalker2_supple_codes/`。两者 `.repo_source` 记录 URL `https://github.com/PFPrzytycki/CellWalkR/tree/cellwalker2` 和提交 `facd2059a9a6403ec58e3937ca05ff2f8d027c38`。
- `CellWalkR/DESCRIPTION` 是本地包版本和依赖的权威来源；Seurat 版本兼容与外部数据仍会影响复现。
- 论文说 KNN 默认 $K=200$，库函数默认 `knn=30`，部分补充脚本还使用 20；树权重默认也不同。结果必须记录实际参数。
- 本地有 `paper.md`、7 张图、R 包、vignettes 和补充脚本，但大型原始数据需外部下载。本轮只做静态论文/图/源码核查，未安装 R 环境、运行脚本或重画结果。

### 一句话总结

CellWalker2 把层级标签、不同模态细胞和 bulk 注释放入同一异构图，以随机游走整合跨边证据，再用置换空分布校正结构偏差；它擅长输出层级化的统计关联，但结论依赖 marker、树、图构造、默认参数和置换稳定性，不能被解释为直接的谱系或因果机制。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellWalker2: Multi-omic Discovery Using Hierarchical Cell Type Relationships

**Paper**: Hu Z, Przytycki PF, Pollard KS. *Cell Genomics* 5, 100886 (2025)
**DOI**: 10.1016/j.xgen.2025.100886
**Code**: https://github.com/PFPrzytycki/CellWalkR/tree/cellwalker2
**Category**: integration_multimodal

---

### Motivation & Novelty

#### The Problem

Single-cell genomics generates high-resolution cell-type annotations, but three persistent gaps limit cross-study integration:

1. **Cell types are treated as discrete labels**: Existing methods (Seurat [*Cell* 2021], Signac [*Nat Methods* 2021], ArchR [*Nat Genet* 2021], CellTypist [*Science* 2022], SIMBA [*Nat Methods* 2024]) treat cell types as independent categories, ignoring that subtypes of neurons are far more related to each other than to immune cells.

2. **Cross-study comparison lacks statistical rigor**: When datasets use different cell-type naming conventions, no method provides statistically validated mappings across hierarchical ontologies. MARS [*Nat Methods* 2020] maps cell types but cannot use existing hierarchies or produce robust significance estimates. treeArches [*NAR Genom Bioinform* 2023] builds hierarchies but is biased toward prevalent cell types.

3. **Bulk annotations lack single-cell resolution**: TF ChIP-seq peaks, GWAS variants, and eQTLs come from bulk experiments. Assigning them to specific cell types requires bridging bulk and single-cell data in a principled way with quantified uncertainty. CellWalker [*Genome Biol* 2021] made a first attempt but lacked statistical significance and hierarchical structure.

#### What's New in CellWalker2

CellWalker2 significantly extends the original CellWalker graph-diffusion framework with four additions:
1. **Hierarchical ontologies as graph nodes**: Internal nodes of a cell-type tree are included explicitly in the graph, allowing mappings to intermediate cell types when fine-grained resolution isn't possible.
2. **Permutation-based Z-scores**: Node-degree-preserving permutations generate a null distribution, producing statistically rigorous significance estimates robust to cell-type composition, sequencing depth, and marker gene choice.
3. **Multi-omics integration**: scRNA-seq, scATAC-seq, and multi-omics (both modalities) cells coexist in the same graph; multi-omic cells bridge RNA-only and ATAC-only cells.
4. **Three unified applications**: cell annotation, cross-ontology cell-type comparison, and bulk annotation labeling — all from the same framework.

---

### Method Overview

CellWalker2 constructs a heterogeneous graph where **cells**, **cell-type labels** (organized in a hierarchy), and optionally **genomic annotations** are all nodes. Edge weights encode biological relationships: cell-to-cell edges capture transcriptomic/epigenomic similarity; cell-to-label edges measure how well a cell expresses a cell type's marker genes; label-to-label edges encode the phylogenetic cell-type hierarchy; cell-to-annotation edges reflect chromatin accessibility in specific regions.

A **Random Walk with Restarts (RWR)** is solved analytically as $F = r(I - (1-r)W)^{-1}$ (restart probability $r=0.5$), producing an influence matrix where $F_{ij}$ reflects how strongly information flows between any two nodes through the full graph topology.

**Statistical significance** is estimated by permuting cell-to-label edges 50 times (preserving marginal distributions via interval discretization), then computing Z-scores relative to this null distribution.

See `doc_method.md` for full mathematical details and `doc_code.md` for code-level implementation.

---

### Evaluation

#### Simulation Benchmarks

**Cell annotation** (vs. Seurat): CellWalker2 and Seurat perform equally in easy scenarios (no batch effects). With batch effects and dropout (medium scenario), CellWalker2 outperforms Seurat, especially for rare cell types. With batch + heavy dropout (hard), CellWalker2 still outperforms. Downstream DEG identification accuracy follows cell annotation quality (Jaccard index comparison, 50 repetitions × 4 scenarios).

**Cell-type comparison** (vs. treeArches, MARS): Across four scenarios (divergent, ancestral, altered, convergent cell types), CellWalker2 Z-scores correctly identify the closest cell type and differentiate all four scenarios. MARS correctly detects ancestral types but cannot distinguish divergent/altered/convergent. treeArches struggles with divergent vs. convergent. CellWalker2 Z-scores are robust to varying cell-type proportions; treeArches and MARS assign the new cell type to the most prevalent type in the reference.

#### Biological Benchmarks

**pRE labeling (developing cortex)**: 19,151 predicted regulatory elements (pREs) from micro-dissected cortical regions were used. CellWalker2 correctly assigns basal ganglia pREs to inhibitory neurons/progenitors/RG and cortical plate pREs to excitatory neurons. Three comparison methods (Wilcoxon test, Fisher's exact test on DARs, original CellWalker) all fail to make this distinction.

**CTCF ChIP-seq**: CellWalker2 correctly maps brain CTCF ChIP-seq peaks to neurons/interneurons (glutamatergic/GABAergic) and blood CTCF peaks to B/T/monocyte cell lines — matching known cell-type specificity (10× Genomics PBMC multi-omics, 10K cells).

**TF mapping** (PBMC): CellWalker2 identifies known cell-type-specific TFs (*TBX21*, *EOMES* in NK/CD8 TEM; *EBF1* in B cells; *LEF1*, *TCF7* in T cells). Benchmarked by: (a) known TF roles, (b) correlation with TF expression, (c) Spearman/Pearson correlation with ChIP-seq peak counts (CellWalker2 and ArchR rank highest). Compared to ArchR [*Nat Genet* 2021], Signac [*Nat Methods* 2021], SCENIC+ [*Nat Methods* 2023], SIMBA [*Nat Methods* 2024].

**Cross-species motor cortex**: Applied to BICCN scRNA-seq + SNARE-seq2 from human, marmoset, mouse. Human-marmoset Z-scores are generally stronger than human-mouse (as expected from phylogeny). Identifies both conserved TFs (stripe factors) and species-specific ones (*NPAS2*, *MYC*, *VSX1* in human Vip/Sncg cells).

#### Datasets Used
| Dataset | Type | Cells | Species | Used For |
|---|---|---|---|---|
| Ren/Yoshida PBMC (CellTypist) | scRNA | 42,484 (subsampled 20%) | Human | Cell-type comparison |
| 10× PBMC multiome | RNA+ATAC | 10K | Human | TF mapping |
| Nowakowski + Polioudakis cortex | scRNA | ~34,000 | Human | Cell annotation + type comparison |
| Trevino cortex multiome | RNA+ATAC | 8,981 | Human | pRE labeling, TF mapping |
| BICCN motor cortex | scRNA + SNARE-seq2 | ~30K/species | Human/marmoset/mouse | Cross-species comparison |

---

### Reproducibility

**Rating: 3/5**

**Justification**: Code is publicly available with documentation and vignettes. The supplementary scripts (81 R files) cover all major paper figures. However:
- All large data files require separate download from public repositories (GEO, NEMO, 10× Genomics)
- The analysis pipelines involve Seurat integration steps that are not fully automated
- Package requires Seurat 4.x (<5.0), limiting compatibility with recent Seurat 5 installations
- Zenodo archive exists (doi:10.5281/zenodo.15106832) ensuring code persistence
- Simulations use `set.seed` and Splatter, making them reproducible

**Practical Notes**:
- Install: `devtools::install_github("PFPrzytycki/CellWalkR@cellwalker2")`
- Seurat 4.3 required (not 5.x): `install.packages("Seurat", version="4.3.0")`
- `foreach`/`doParallel` registration required before calling `mapCellTypes` for parallel permutations
- For sparse matrix performance: ensure Matrix package ≥ 1.5.3
- `randomWalk()` uses `solve()` for exact matrix inversion: for >30K cells, pre-subsample via `sampleDepth` or use iterative `steps` parameter
- Tree weights: paper recommends `wtrees = matrix(c(1, 0.1), 1, 2)` but default is `matrix(c(1,1), 1, 2)` — users should set explicitly

**Strengths**:
- Conceptually unified framework covering three distinct use cases
- Statistically principled (permutation-based null distribution)
- Well-integrated with standard single-cell toolchain (Seurat, Signac, ArchR)
- Handles mixed-modality datasets without requiring paired data for all cells

**Weaknesses**:
- $O(n^3)$ matrix inversion limits scalability beyond ~50,000 cells without subsampling
- Z-scores for rare cell types can be inflated (small sample SD issue — authors recommend more permutations)
- Requires marker genes as input (not a de novo clustering method)
- Strong batch effects can disrupt cross-dataset information flow

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
