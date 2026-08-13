---
layout: default
permalink: /paper-atlas/stihc-f3f9bf4f/
title: "stIHC"
nav: false
description: "stIHC 的核心是：先把每个基因在组织上的表达模式变成平滑函数的系数向量，再用能处理 imbalanced clusters 的迭代层次聚类去找空间共表达模块。论文的模式证据和核心 R 源码支持这个主线；完整 benchmark、GO/anatomy 解释和真实数据 preprocessing 则依赖仓库外证据或未提供脚本。"
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
      <span>Spatially Variable Genes</span>
      <span>Quantitative Biology · 2025</span>
    </div>
    <h1>stIHC</h1>
    <p>Spatial transcriptomics iterative hierarchical clustering (stIHC): A novel method for identifying spatial gene co-expression modules</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/CatherineH1/stIHC" target="_blank" rel="noopener noreferrer" aria-label="Open code for stIHC">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## stIHC 方法中文解读

### 这篇论文要解决什么问题？

空间转录组（spatial transcriptomics, ST）可以在保留组织空间位置的同时测量基因表达。很多已有方法主要解决“哪些基因是空间变异基因（SVG）”的问题，但论文指出：把这些 SVG 进一步聚成有生物意义的空间共表达模块，仍然不充分。SpatialDE、SPARK、SPARK-X、MERINGUE 等方法虽然也有下游聚类步骤，但在模块大小不均衡、存在很小或稀有空间模式时，容易把小模块合并进大模块，漏掉稀有模式（`paper.md:31-48`）。

stIHC 的目标不是聚类 spot/cell，而是聚类基因。也就是说，每个 cluster 表示一组基因在整个组织切片上有相似的空间表达形状（`paper.md:31-37`）。

### 方法总览

stIHC 是一个两步方法（`paper.md:56-98`）：

```text
空间坐标 + 基因表达矩阵
        |
        v
Step 1: 在二维组织区域上平滑每个基因的空间表达
        |
        v
得到每个基因的基函数系数向量
        |
        v
Step 2: 用 funIHC 对这些系数向量做迭代层次聚类
        |
        v
输出每个基因的模块标签、每个模块的均值模式、模块内基因集合
```

论文的核心思想是：不要直接在 noisy 的原始表达值上聚类，而是先把每个基因看成组织切片上的一个平滑空间函数，再用这些函数的系数表示去比较基因之间的空间模式相似性（`paper.md:44-48`; `paper.md:56-74`）。

### Step 1：把每个基因表达建模为空间平滑函数

论文设第 $j$ 个空间位置为 $s_j=(s_{j1},s_{j2})^\top$，第 $i$ 个基因在该位置的表达为 $y_{ji}$（`paper.md:56-60`）。组织区域 $\Omega$ 先用 Delaunay triangulation 划分成三角网格，再在网格上定义 piecewise linear basis functions（`paper.md:60-68`）。

论文中的空间函数展开为：

$$g(\mu_i)=f_i(\mathbf{s})=\mathbf{\phi}(\mathbf{s})\mathbf{c}_{\mathbf{i}},$$

其中 $\mathbf{c}_{\mathbf{i}}$ 是第 $i$ 个基因的基函数系数（`paper.md:64-68`）。

系数估计使用带 Laplacian 平滑惩罚的 penalized likelihood：

$$\mathcal{L}_{s}(\mathbf{c}_{\mathbf{i}})=
\sum_{j=1}^{n}l(y_{ji};\mathbf{c}_{\mathbf{i}})
-\lambda\int_{\Omega}(\Delta f_i(\mathbf{s}))^2\,d\mathbf{s}.$$

这里 $\lambda$ 控制平滑程度，论文说用 GCV 在所有基因上选择统一的 $\lambda$，从而得到所有基因的系数矩阵 $\mathbf{C}$（`paper.md:70-74`）。

#### 代码里如何实现？

本地代码中，`stIHC(data)` 先用 `data$x` 和 `data$y` 建立 2D mesh，再建立 FEM basis（`stIHC/stIHC.R:1-4`）。这比 README 的“前两列是 xy 坐标”更严格：代码实际要求列名为 `x` 和 `y`（`stIHC/README.md:20-22`; `stIHC/stIHC.R:1-4`）。

随后代码分两轮调用 `smooth.FEM()`：

1. 第一轮：对每个基因在 lambda grid 上运行 `smooth.FEM()`，记录每个基因自己的 `lambda_solution`（`stIHC/stIHC.R:8-22`）。
2. 第二轮：令 `lambda <- mean(lambdas)`，用这个平均 lambda 重新拟合每个基因，并提取 `fit.FEM$coeff`（`stIHC/stIHC.R:31-55`）。

因此，论文中“统一 $\lambda$”这个思想在代码中是 **Partial** 匹配：代码确实用共享 lambda 重新拟合所有基因，但这个共享 lambda 是“每个基因 GCV 最优 lambda 的平均值”，不是本地代码中显式写出的“所有基因联合 GCV 目标”（`paper.md:74-74`; `stIHC/stIHC.R:21-41`）。

另外，论文中的 exponential family、link function 和 Laplacian penalty 是方法定义的一部分；本地代码只显示调用 `smooth.FEM()` 及其 GCV/lambda 参数，并没有在仓库代码中显式暴露 family/link/Laplacian 细节。因此这部分应写作论文方法 + 外部 `fdaPDE::smooth.FEM()` 调用，而不是说本仓库代码完整展开了这些统计细节（`paper.md:60-74`; `stIHC/stIHC.R:12-18`; `stIHC/stIHC.R:35-41`）。

### Step 2：用 funIHC 聚类基因的系数向量

论文定义基因 $i$ 和 $j$ 的距离为：

$$d_{i,j}=1-\rho_{i,j},$$

其中 $\rho_{i,j}$ 是两个基因系数向量之间的 Spearman correlation（`paper.md:78-82`）。然后论文在 $\alpha_{\min}$ 到 $\alpha_{\max}$ 之间构造 alpha grid，对每个 $\alpha_u$ 执行层次聚类、cluster center 合并、低相关基因剪枝、重复直到收敛，并用平均 silhouette 选择 $\alpha_{\text{opt}}$（`paper.md:80-98`）。

#### IHC 循环的直观含义

对一个给定的 $\alpha_u$：

1. 先用平均连接层次聚类，把相似基因放到一起。
2. 把每个 cluster 的中心 $\mu_p$ 当作新的对象，再看 cluster center 之间是否还应该合并。
3. 对每个 cluster，检查每个基因和 cluster mean 的 Spearman correlation；如果低于 $\alpha_u$，就把这个基因剪出来，变成 singleton cluster。
4. 重复合并和剪枝，直到分配稳定。
5. 最后再做 cluster-center 合并，使不同 cluster 的中心不要过于相似。

论文附录解释了为什么这个循环最后追求的是 within-cluster correlation 接近 $\alpha_u$，而不是强行每次都大于 $\alpha_u$（`paper.md:345-347`）。

#### 代码里如何实现？

`IHC()` 的主体和论文思路基本对应：

- 初始聚类：`hclust(as.dist(1 - cor(t(data), method = "spearman")), method = "average")`，再用 `cutree(h = 1 - alpha)` 切树（`stIHC/stIHC.R:117-122`）。
- 合并 cluster center：对 `mean_clusters_mat` 再做 Spearman/average-linkage 聚类（`stIHC/stIHC.R:156-173`）。
- 剪枝：计算每个基因和 cluster mean 的 Spearman correlation；低于 `alpha` 的基因被移出并追加为 singleton cluster（`stIHC/stIHC.R:179-209`）。
- 停止：代码用当前/上一轮标签的 adjusted Rand index 判断收敛；ARI 为 1、四舍五入后大于 0.9、迭代过多或最近 ARI 变化很小时停止（`stIHC/stIHC.R:225-240`）。
- 输出标签：最后把 gene index cluster 转为每个基因的 label（`stIHC/stIHC.R:281-288`）。

这里也有两个需要保留的代码差异：

- alpha 搜索范围在代码中由 `PCorR <- as.vector(1 - cor(t(C), method = "spearman"))` 生成；由于 `all_coefs` 在代码中是“系数行 × 基因列”，这和论文“所有基因对 Spearman correlation”的文字定义不是完全同一个表达（`paper.md:80-80`; `stIHC/stIHC.R:43-70`）。
- 论文说用平均 silhouette 选择最优 alpha；代码确实计算 silhouette，但还先偏向出现次数最多的 cluster 数量，再在该子集里选 silhouette 最大值（`paper.md:98-98`; `stIHC/stIHC.R:90-101`; `stIHC/stIHC.R:107-114`）。

### 论文评估结果怎么支持这个方法？

论文做了三组模拟。第一组是四个大小相同、空间模式清楚的模块，所有方法都表现很好（`paper.md:106-115`）。第二组是 imbalanced modules：4 个模块大小分别为 6、2、16、25。stIHC 是唯一恢复全部四个模块的方法，ARI=1.00，DBI=0.49；SPARK、SPARK-X、MERINGUE 把两个基因的小模块合并掉，SpatialDE 表现更差（`paper.md:119-141`）。第三组是 sparse imbalanced simulation，空间位置减少到 260 个；stIHC 把最小的 Ttr 模块分成两个 singleton，但仍然保留了稀有模式，并取得最高 ARI 和最低 DBI（`paper.md:145-167`）。

真实数据部分，论文在 10x Visium mouse brain、10x Xenium mouse brain 和 10x Visium human lung cancer 上展示了空间共表达模块，并用 GO enrichment 和 anatomical/disease-region interpretation 解释这些模块（`paper.md:171-232`; `paper.md:364-397`）。在 mouse olfactory bulb 数据中，stIHC 被放在 MERINGUE 或 SpatialDE 的 SVG detection 之后，用来聚类不同 SVG 集合，说明它可以作为下游模块聚类工具（`paper.md:236-287`）。

本地图片也支持这些模式层面的结论：Figure 3/4 的图像显示 stIHC 行保留了小模块空间模式，而其他方法行有合并或扭曲；Figure 5/6/7 把 cluster mean、代表基因、GO 结果和解剖/疾病解释放在一起；Figure 9/10 展示了 MERINGUE/SpatialDE SVG 集合作为输入时的 olfactory bulb 模块（`figure_analysis.md`）。

### 代码复现边界

本地仓库是核心算法仓库，不是完整论文复现仓库。

**可以从本地代码直接看到：**

- `stIHC(data)` 的核心实现（`stIHC/stIHC.R:1-59`）。
- `funIHC()` 和 `IHC()` 的 alpha search、silhouette、merge/prune、ARI stopping、标签输出（`stIHC/stIHC.R:63-289`）。
- 三个模拟数据的 stIHC 运行和 ARI/DBI 计算脚本（`stIHC/simulations.R:10-45`）。

**Not found in `code source`：**

- scDesign3 模拟数据生成 workflow（论文把它指向外部教程；`paper.md:303-305`）。
- 100 次重复稳定性实验 loop（论文描述在 `paper.md:102-102`，本地脚本未包含）。
- SpatialDE、SPARK、SPARK-X、MERINGUE 的 benchmark wrapper（`paper.md:309-315`）。
- 真实数据 GO enrichment 和 anatomical mapping 脚本（`paper.md:171-232`; `paper.md:364-397`）。
- olfactory bulb 的 MERINGUE/SpatialDE preprocessing 和 SVG detection 脚本（`paper.md:236-287`）。

**代码层面的运行风险：**

`funIHC()` 的返回值包含 `fd = fd`，但在本地 `README.md`、`stIHC.R`、`simulations.R` 中没有找到 `fd` 的定义（`stIHC/stIHC.R:103-103`）。由于当前主机没有 `Rscript`，这里没有做运行验证；只能说从源码看这是一个需要修复或确认的 runnability risk。

### 一句话理解 stIHC

stIHC 的核心是：先把每个基因在组织上的表达模式变成平滑函数的系数向量，再用能处理 imbalanced clusters 的迭代层次聚类去找空间共表达模块。论文的模式证据和核心 R 源码支持这个主线；完整 benchmark、GO/anatomy 解释和真实数据 preprocessing 则依赖仓库外证据或未提供脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## stIHC Summary

### Problem

Spatial transcriptomics methods often detect spatially variable genes (SVGs), but the paper argues that clustering those genes into meaningful co-expression modules remains underdeveloped. Existing SVG pipelines such as SpatialDE, SPARK, SPARK-X, and MERINGUE include downstream clustering steps, yet those steps can miss rare or small spatial expression modules, especially when module sizes are imbalanced (`paper.md:31-48`).

### Proposed Method

Spatial transcriptomics iterative hierarchical clustering (stIHC) is a two-step gene-level clustering method. First, it smooths each gene's expression over the 2D tissue domain with a generalized penalized regression/FEM basis model. Second, it clusters the resulting coefficient vectors using functional iterative hierarchical clustering (funIHC), where dissimilarity is one minus Spearman correlation and the alpha threshold is selected by silhouette score (`paper.md:56-98`).

The intended output is a set of gene co-expression modules: genes in the same module should have similar spatial expression patterns across the tissue, not merely similar expression magnitudes at individual spots (`paper.md:33-44`). The cloned R code implements the core path as `stIHC(data)`: mesh/basis construction, two-pass `smooth.FEM`, coefficient extraction, `funIHC()`, and final labels/cluster means (`stIHC/stIHC.R:1-59`; `stIHC/stIHC.R:63-289`).

### Evaluation

The paper evaluates stIHC with three simulations and applications to 10x Visium, 10x Xenium, and Spatial Transcriptomics datasets. In the imbalanced simulation, stIHC is reported as the only method to recover all four modules, with ARI 1.00 and DBI 0.49 (`paper.md:119-132`). In the sparse imbalanced simulation, stIHC splits the smallest two-gene module into two singleton clusters but still achieves the best ARI/DBI and preserves the rare spatial pattern (`paper.md:145-167`).

For real ST data, the paper reports spatially coherent modules in Visium mouse brain, Xenium mouse brain, and Visium lung cancer data, with GO enrichment and anatomical/disease-region interpretations (`paper.md:171-232`; `paper.md:364-397`). In mouse olfactory bulb data, stIHC is applied downstream of MERINGUE and SpatialDE SVG detection and produces modules matching granular and glomerular spatial features (`paper.md:236-287`).

### Figure Evidence

The local figures support the main pattern-level claims. Figures 2-4 show the balanced, imbalanced, and sparse imbalanced simulation patterns and visually support the rare-module recovery story (`figure_analysis.md`; `paper.md:106-167`). Figures 5-7 show cluster mean maps, representative genes, GO panels, and anatomical/disease interpretations for the real-data applications (`paper.md:177-232`). Figures 8-10 support the olfactory bulb downstream-SVG-detection workflow (`paper.md:236-287`).

### Reproducibility Status

Full-paper reproducibility is **partial**. The cloned repository contains the core R implementation and a simulation driver for running stIHC on three provided simulation CSVs (`stIHC/README.md:9-26`; `stIHC/simulations.R:10-45`). It does not contain the scDesign3 simulation-generation workflow, the 100-repeat stability loop, competing-method wrappers for SpatialDE/SPARK/SPARK-X/MERINGUE, GO enrichment scripts, anatomical mapping scripts, or olfactory bulb preprocessing workflows (`paper.md:303-315`; `paper.md:335-339`).

Code-paper fidelity is **medium**. The core algorithm is present, but several details are partial from local source: generalized-family/link/Laplacian behavior is delegated to `smooth.FEM`, shared $\lambda$ is implemented as the mean of per-gene GCV-selected lambdas, alpha-search behavior differs from the paper description, and `funIHC()` contains a source-level runnability risk because it returns `fd = fd` although `fd` is not defined in the local R files (`doc_code.md`; `stIHC/stIHC.R:8-18`; `stIHC/stIHC.R:31-41`; `stIHC/stIHC.R:63-103`).

### Main Gaps

- **MISSING**: supplementary markdown.
- **Not found in `code source`**: real-data GO/anatomical mapping scripts.
- **Not found in `code source`**: benchmark wrappers for SpatialDE, SPARK, SPARK-X, and MERINGUE.
- **Not executed here**: R runtime validation, because `Rscript` was not available on this host.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
