---
layout: default
permalink: /paper-atlas/clusterde-bafcc087/
title: "ClusterDE"
nav: false
description: "ClusterDE 处理的是单细胞 RNA-seq 和空间转录组分析里很常见的一个问题：先用同一份表达矩阵做聚类，再用同一份表达矩阵在聚类之间做差异表达检验。这样会产生 double-dipping bias，也就是“用同一份数据先发现结构、再验证结构”。如果聚类算法把一个本来同质的细胞群或一个平滑空间区域过度切成两个簇，普通 DE 检验仍然可能给出显著 marker gene，造成假阳性和错误注释。"
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
      <span>Computational Tools</span>
      <span>Journal of Computational Biology · 2025</span>
    </div>
    <h1>ClusterDE</h1>
    <p>ClusterDE: A Statistical Software Package for Removing Double-Dipping Bias in Post-Clustering Differential Expression Analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1177/15578666251383562" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ClusterDE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/SONGDONGYUAN1994/ClusterDE" target="_blank" rel="noopener noreferrer" aria-label="Open code for ClusterDE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ClusterDE 方法中文解析

### 这篇文章要解决什么问题？

ClusterDE 处理的是单细胞 RNA-seq 和空间转录组分析里很常见的一个问题：先用同一份表达矩阵做聚类，再用同一份表达矩阵在聚类之间做差异表达检验。这样会产生 double-dipping bias，也就是“用同一份数据先发现结构、再验证结构”。如果聚类算法把一个本来同质的细胞群或一个平滑空间区域过度切成两个簇，普通 DE 检验仍然可能给出显著 marker gene，造成假阳性和错误注释（`paper.md:8-16`）。

ClusterDE 的目标不是替代 Seurat、BayesSpace 这类流程，而是在已有聚类和 DE 流程后面加一个负对照。它重点回答的问题是：这两个候选 cluster/domain 的 marker gene 信号，是否明显强于一个“本来就不应该有真实离散边界”的 synthetic null 数据里产生的信号？

### 为什么普通流程不够？

普通流程大致是：

```text
表达矩阵 -> 降维/邻居图/聚类 -> 选择两个 cluster -> DE test -> marker genes
```

问题在于，聚类和 DE test 都使用同一批基因表达数据。聚类步骤已经根据表达差异把细胞或 spot 分开，后面再用这些表达差异去检验 cluster 间差异，p-value 会被过度乐观地解释。论文特别强调，over-clustering 会把人工 cluster 误认为真实 cell type 或 spatial domain（`paper.md:8-16`）。

ClusterDE 的想法是给这个流程加一个平行负对照：

```text
真实数据 target data -----------------> target DE score
        |                                  |
        | 构造 synthetic null data         | 对比
        v                                  v
无真实离散结构的 null data ----------> null DE score
```

如果某个基因在真实数据里显著，但在 synthetic null 里也很显著，那么它可能只是聚类/DE 流程本身带来的假信号。真正可靠的 marker 应该在真实数据里强，在 null 数据里弱。

### ClusterDE 的核心假设

论文把 null data 分成两类（`paper.md:22-22`）：

1. **scRNA-seq:** null data 表示一个同质细胞群。它和真实数据有相同数量的 synthetic cells，并尽量保留每个基因的均值、方差以及基因之间的 rank correlation。
2. **spatial transcriptomics:** null data 表示一个平滑的空间 domain。基因表达可以随空间位置平滑变化，但不能有清晰的 domain boundary。

这个假设很重要：ClusterDE 不是要生成完全随机的噪声数据，而是生成一个“保留真实数据低层统计结构、但没有真实离散分群”的负对照。

### 方法流程

```text
输入：两个待比较的 cluster/domain 的 target data
  |
  | 1. 对 target data 做普通 DE test，得到每个基因的 target p-value
  v
target DE score
  |
  | 2. 根据 target data 构造 synthetic null data
  v
一个同质细胞群或平滑空间 domain
  |
  | 3. 用相同类型的流程处理 null data，并让 null data 最终分成两个 cluster/domain
  v
null DE score
  |
  | 4. 对每个基因计算 contrast score
  v
contrast score = target score - null score
  |
  | 5. 用 FDR 阈值选择可靠 marker
  v
输出：更可信的 marker gene 表
```

### 第一步：target data 上的 DE test

论文的 scRNA-seq 示例使用 PBMC3K 数据，先按照 Seurat 标准流程做 NormalizeData、FindVariableFeatures、ScaleData、RunPCA、FindNeighbors、FindClusters，然后选择 cluster 4 和 5 做 DE test（`paper.md:64-90`）。论文说明这两个 cluster 都是 CD14+ monocytes，因此预期没有真正 DE genes（`paper.md:80-80`）。

空间转录组示例使用 LIBD DLPFC slice 151673，选择 L6 和 WM spatial domains，用 BayesSpace 做空间聚类，再用 Seurat 的 Wilcoxon rank-sum test 得到 target p-values（`paper.md:158-160`, `paper.md:208-242`）。

一个关键操作是关闭常见 DE 预过滤，让每个基因都有 p-value。论文示例关闭了 `min.pct`、`logfc.threshold`、`min.cells.feature`、`min.cells.group`（`paper.md:82-90`, `paper.md:138-142`, `paper.md:240-242`, `paper.md:286-288`）。

代码里 `findMarkers()` 也关闭了 `min.pct` 和 `logfc.threshold`，但它还额外保留 `avg_log2FC > 0` 的 target markers（`ClusterDE/R/find_markers.R:26-35`）。这点是代码实现细节，论文示例没有明确写出。

### 第二步：构造 synthetic null data

论文层面的描述是：null data 应该保留真实数据的均值、方差和近似 rank correlation，但不包含真实的两个离散群体或尖锐空间边界（`paper.md:22-22`）。

代码中的 `constructNull()` 有几条实现路径：

- 函数入口从 Seurat object 读取 count layer：`Seurat::GetAssayData(obj, layer = "counts")`（`ClusterDE/R/construct_null.R:35-52`）。
- 如果传入空间坐标列名，代码会构造 `s(x, y, bs = 'gp', k = 4)` 形式的 Gaussian-process 平滑均值公式；否则用常数均值公式 `"1"`（`ClusterDE/R/construct_null.R:59-64`）。
- 非 fast scDesign3 分支使用一个假的 cell type 变量，让所有细胞属于同一类，并调用 `scDesign3::scdesign3()` 生成 null data（`ClusterDE/R/construct_null.R:172-196`）。
- fast 分支会先拟合每个基因的边际分布，再选择表达足够多的基因建模相关结构，用 pseudo-observation、normal transform 和相关矩阵采样生成 correlated null counts（`ClusterDE/R/construct_null.R:198-345`, `ClusterDE/R/construct_null.R:443-691`）。

这里有一个重要的 paper-code 差异：论文示例直接把 count matrix 传给 `constructNull()`，空间示例还传了 `formula` 和 `extraInfo`（`paper.md:94-100`, `paper.md:244-250`）。但当前代码快照的函数签名是 `constructNull(obj, family = "nb", spatial = NULL, ...)`，并要求 `obj` 是 Seurat object（`ClusterDE/R/construct_null.R:35-52`, `ClusterDE/man/constructNull.Rd:6-24`）。因此，论文示例和当前 GitHub 快照不是完全一致的可运行接口。

### 第三步：null data 上跑同类流程

论文要求 null data 也经过同样的 preprocessing、dimensionality reduction、clustering 和 DE-testing 流程。对于 Louvain/Leiden 这类通过 resolution 间接控制 cluster 数量的方法，还要调 resolution，使 null data 最终恰好得到两个 clusters（`paper.md:24-26`, `paper.md:102-136`）。

代码中 `calcNullPval()` 把这个原则实现成两个固定分支：

- **非空间数据:** 创建 Seurat object，NormalizeData，FindVariableFeatures，ScaleData，RunPCA，FindNeighbors，然后通过增加和二分搜索 resolution，使 Seurat 聚类结果变成两个 clusters（`ClusterDE/R/calc_null_pval.R:54-95`）。
- **空间数据:** 用 BayesSpace `spatialPreprocess()` 和 `spatialCluster(q = 2)` 得到两个空间 cluster，再用 Seurat 做 DE test（`ClusterDE/R/calc_null_pval.R:32-53`, `ClusterDE/R/calc_null_pval.R:97-111`）。

所以论文的“same pipeline”在代码里不是任意 callback，而是内置的 Seurat 或 BayesSpace+Seurat 路径。

### 第四步：contrast score

论文定义每个基因有一个 target DE score 和一个 null DE score，默认 score 是 DE p-value 的负对数；然后用 target score 减去 null score 得到 contrast score（`paper.md:28-30`, `paper.md:144-154`, `paper.md:290-300`）。

用符号写就是：

$$
score^{target}_g = -\log_{10}(p^{target}_g)
$$

$$
score^{null}_g = -\log_{10}(p^{null}_g)
$$

$$
cs_g = score^{target}_g - score^{null}_g
$$

代码中 `callDE()` 先把 target 和 null p-value 按基因名合并，如果 `nlogTrans = TRUE` 就做 `-log10` 变换，然后在默认 `contrastScore = "diff"` 下计算 `cs = target - null`（`ClusterDE/R/call_de.R:25-66`）。

直觉是：真正的 marker gene 应该在 target data 里很强，在 null data 里不强，所以 `cs_g` 应该很大且为正。

### 第五步：FDR 控制

论文说可靠 markers 是 contrast score 超过 Clipper 选择的数据自适应 cutoff 的基因，并控制用户指定的 FDR，例如 0.05（`paper.md:28-30`）。

代码里 `callDE()` 调用 `cs2q()` 把 contrast score 转成 q-value，然后选择 `q <= FDR` 的 genes（`ClusterDE/R/call_de.R:78-82`）。`cs2q()` 会用正负 contrast score 的计数关系估计 empirical FDP，并支持 `"BC"` 和 `"DS"` 两种 threshold 公式（`ClusterDE/R/call_de.R:104-142`）。

这部分是 paper-code 最直接匹配的地方：论文给出原则，代码给出具体 empirical FDP/q-value 实现。

### 怎么理解输出？

当前代码的 `callDE()` 返回按 contrast score 排序的表，核心列包括：

- `gene`: 基因名。
- `cs`: 平均 contrast score；多个 null replicate 时会取平均。
- `record`: 该基因在各 null replicate/FDR 判断中被选中的平均记录值（`ClusterDE/R/call_de.R:82-101`）。

如果只看普通 DE p-value，容易把 over-clustering 产生的差异当成 marker。ClusterDE 的输出应该被理解为“真实数据 DE 信号相对于 synthetic null 负对照仍然突出的基因”。

### 这篇文章的验证方式

这篇文章更像软件说明和教程，不是完整 benchmark paper。它展示了两个使用场景：

1. **PBMC3K scRNA-seq:** 比较 Seurat clusters 4 和 5，最后示例结果为 `## no DE genes`（`paper.md:50-156`）。
2. **DLPFC spatial transcriptomics:** 比较 L6 和 WM spatial domains，展示 BayesSpace+Seurat 目标流程、smooth spatial null data 构造和 `callDE()` 调用（`paper.md:158-300`）。

本 workspace 没有取得论文图像文件，也没有 supplementary markdown。因此这里的理解主要来自论文文字和代码源码，不来自图像证据。

### 需要特别记住的局限

- **接口不完全一致:** 论文中的 `constructNull(count_matrix, formula=..., extraInfo=...)` 示例和当前代码快照的 Seurat-object API 不完全一致。
- **“same pipeline”是原则，不是任意流程接口:** 当前代码实现的是 Seurat 和 BayesSpace+Seurat 内置路径。
- **没有编号公式或算法块:** 论文没有正式给出算法伪代码；上面的公式是对论文文字和代码行为的解释性整理。
- **本次没有运行 R 包:** 这里验证的是源码和论文之间的对应关系，不是执行复现实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ClusterDE Summary

ClusterDE is an R package for reducing double-dipping bias in post-clustering differential expression analysis. The problem is that common single-cell and spatial transcriptomics workflows use the same data to create clusters and then test genes between those clusters; when clustering over-splits a homogeneous population or smooth spatial region, ordinary DE tests can produce false-positive marker genes (`paper.md:8-16`).

The proposed fix is to build a synthetic null dataset from the target data and use it as a negative control. For scRNA-seq, the null represents one homogeneous cell population with the same number of cells and approximately preserved gene means, variances, and gene-gene rank correlations. For spatial transcriptomics, the null represents one smooth spatial domain with no sharp boundary (`paper.md:22-22`). Target and null data are then processed through comparable preprocessing, clustering, and DE steps, with the null constrained to two clusters/domains so it can be contrasted against the two target clusters under examination (`paper.md:24-26`).

The central score is a target-minus-null DE contrast. By default, ClusterDE converts target and null DE p-values to `-log10(p)` scores, subtracts the null score from the target score for each gene, and selects reliable markers using a data-adaptive FDR cutoff inspired by Clipper (`paper.md:28-30`). The implementation matches this core logic in `callDE()`, which transforms scores, computes contrast scores, converts them to q-values, and returns selected/ranked genes (`ClusterDE/R/call_de.R:25-142`).

The paper demonstrates usage on two workflows rather than presenting a broad quantitative benchmark. In the scRNA-seq walkthrough, it applies a Seurat PBMC3K workflow to clusters 4 and 5, generates null data, tunes null clustering to two clusters, and reports no DE genes for the tested monocyte pair (`paper.md:50-156`). In the spatial transcriptomics walkthrough, it applies BayesSpace plus Seurat to LIBD DLPFC slice 151673, compares Layer 6 and white matter spatial domains, generates a smooth null domain, and calls `callDE()` at FDR 0.05 (`paper.md:158-300`).

Code availability is good but paper-code fidelity is **medium**. The cloned package exposes `findMarkers()`, `constructNull()`, `calcNullPval()`, and `callDE()` (`ClusterDE/NAMESPACE:1-8`), and the main source files implement the synthetic-null, null-pipeline, contrast-score, and empirical FDR steps. The main gap is API drift: the article examples call `constructNull()` on raw count matrices and use `formula`/`extraInfo` style spatial arguments, while this source snapshot expects a Seurat object and optional `spatial` metadata column names (`paper.md:94-100`, `paper.md:244-250`; `ClusterDE/R/construct_null.R:35-64`; `ClusterDE/man/constructNull.Rd:6-24`).

Reproducibility status: source-level method mapping is strong for the statistical core, but this author pass did not install or run the R package. The workspace has no supplementary markdown and no acquired paper figure images, so figure-grounded evidence is unavailable. The strongest reading path is `doc_method.md` for the algorithm, `doc_code.md` for paper-code fidelity and API drift, and `figure_analysis.md` for the missing-image boundary.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
