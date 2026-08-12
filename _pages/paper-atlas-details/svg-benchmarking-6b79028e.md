---
layout: default
permalink: /paper-atlas/svg-benchmarking-6b79028e/
title: "SVG_Benchmarking"
nav: false
description: "空间转录组数据同时记录基因表达和空间坐标。一个核心任务是找出表达模式与空间位置显著相关的基因，即 spatially variable genes，简称 SVG。已有方法很多，但不同方法在模拟数据、真实组织、统计校准、计算规模和下游聚类任务中的表现并不一致。本文的目标不是提出一个新的 SVG 模型，而是系统比较 14 个已有 SVG 检测方法，并给出方法选择建议。"
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
      <span>Spatially Variable Genes</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>SVG_Benchmarking</h1>
    <p>Systematic benchmarking of computational methods to identify spatially variable genes</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法解读：SVG Benchmarking

### 这篇文章解决什么问题？

空间转录组数据同时记录基因表达和空间坐标。一个核心任务是找出表达模式与空间位置显著相关的基因，即 spatially variable genes，简称 SVG。已有方法很多，但不同方法在模拟数据、真实组织、统计校准、计算规模和下游聚类任务中的表现并不一致。本文的目标不是提出一个新的 SVG 模型，而是系统比较 14 个已有 SVG 检测方法，并给出方法选择建议（`paper.md:59-62`, `paper.md:68-89`）。

本文评估的方法包括 Moran's I、Spanve、scGCO、SpaGCN、SpaGFT、Sepal、SpatialDE、SpatialDE2、SPARK、BOOST-GP、GPcounts、SPARK-X、nnSVG 和 SOMDE。论文把这些方法大致分成图/KNN/自相关类、核函数/协方差类，以及混合或神经网络类（`paper.md:68-77`）。

### 为什么需要新的基准？

真实空间转录组通常没有已知的 SVG 真值，因此直接评价方法准确性很困难。过去的 benchmark 往往方法数量少、技术平台覆盖不全，或者使用过于简单的模拟模式，不能充分反映真实组织中复杂的空间表达图案（`paper.md:59-62`, `paper.md:86-89`）。

本文的关键思路是：用真实空间转录组数据作为参考，通过 scDesign3 生成更接近真实数据分布的模拟数据，并控制每个基因的空间信号强度。这样可以在已知真值的条件下比较方法的排序能力、分类能力和稳定性。

### 整体计算流程

```text
真实空间组学数据
        |
        |-- 模拟数据任务：scDesign3 拟合真实数据，再混合空间/非空间信号
        |      -> 运行 14 个 SVG 方法 -> Kendall 排序、auPRC、空间模式分析
        |
        |-- 统计校准任务：构造 null 或弱空间信号数据
        |      -> 检查 p 值 QQ 图和 KS 距离
        |
        |-- 可扩展性任务：模拟不同 spot 数量
        |      -> Snakemake benchmark 记录内存和运行时间
        |
        |-- 空间结构域聚类任务：用 top SVG 做特征
        |      -> Leiden / BayesSpace / Banksy -> ARI 评价
        |
        |-- 空间 ATAC 任务：把 peak 当作特征，寻找 SVP
        |      -> top 20,000 peaks -> TF-IDF / LSI / Leiden -> CHAOS / LISI
        |
        -> 汇总每个任务的排名，得到总体推荐
```

### 模拟数据设计

论文用 scDesign3 对真实空间转录组数据拟合负二项高斯过程模型，得到具有空间结构的平均表达函数。然后打乱均值参数，破坏空间相关性，得到非空间模型。最终模拟均值是两者的线性混合（`paper.md:266-278`）：

```text
mu(s) = alpha * mu_s(s) + (1 - alpha) * mu_ns(s)
```

其中：

- `mu_s(s)` 表示带空间结构的均值；
- `mu_ns(s)` 表示打乱后的非空间均值；
- `alpha` 控制空间信号强度，从 0 到 1。

论文使用 50 个真实空间转录组数据集，覆盖 9 种空间技术和 18 种组织类型，用来生成模拟数据（`paper.md:266-278`）。代码仓库中确实有 `generate_simulate_data/` 和 `prepare_reference_data/` 两组 notebook，并且 README 说明了模拟数据和 Zenodo 预生成数据（`pinellolab-SVG_Benchmarking/README.md:20-26`）。但是，本次本地分析没有在可读 notebook 文本中定位到完整的 `fit_marginal`、`fit_copula`、`simu_new` 或上述混合公式实现，所以这一部分是论文层面的可靠描述，但代码实现仍属于部分未核实。

### 运行 SVG 方法

仓库的 `snakemake_simulate_data/` 是主要方法运行流程。其 Snakefile 引入了 14 个方法的 rule 文件，并列出 50 个模拟数据集（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/Snakefile:6-83`）。

直接核实到的几个方法 wrapper 包括：

- MoranI：读取 h5ad，用 Squidpy 构建 Delaunay 空间邻接图，运行 Moran 自相关，并输出 `adata.uns["moranI"]`（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/methods/run_MoranI.py:28-43`）。
- SPARK-X：从 h5ad 读 counts 和空间坐标，调用 `sparkx(..., numCores=10, option="mixture")`（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/methods/run_SPARK-X.R:16-34`）。
- SpatialDE2：先用 NaiveDE 做稳定化和回归，再调用 `sd.fit(..., normalized=True, control=None)`（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/methods/run_SpatialDE2.py:47-66`）。
- scGCO：归一化表达矩阵、构建细胞图、拟合 GMM，然后调用 vendored `identify_spatial_genes` 图割函数（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/methods/run_scGCO.py:32-47`; `pinellolab-SVG_Benchmarking/utils/scGCO/code/scGCO_code/scGCO_source/Graph_cut.py:773-799`）。

需要注意：当前仓库快照中的多个 Snakefile 有临时缩小方法列表的 override。例如主模拟 Snakefile 前面列出 14 个方法，但后面把 `method_list` 改成了 `['Spanve']`（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/Snakefile:21-23`, `pinellolab-SVG_Benchmarking/snakemake_simulate_data/Snakefile:77-79`）。因此这个仓库更适合被描述为 benchmark scaffold，而不是无需修改即可一键复现实验的最终版本。

### 评价指标

#### 排序能力和分类能力

论文用 Kendall tau 衡量方法分数与真实空间信号强度之间的排序一致性，用 auPRC 衡量空间变量基因与非空间基因的分类能力（`paper.md:410-419`）。

代码中，`eval_simulate_data/01_compute_correlation.ipynb` 为每个方法选择对应分数字段，并计算该字段与 `spatial_var` 的 Kendall 相关（`pinellolab-SVG_Benchmarking/eval_simulate_data/01_compute_correlation.ipynb:48-98`）。`eval_simulate_data/02_compute_aupr.ipynb` 把 `spatial_var > 0` 作为正类，并用 `average_precision_score` 计算 auPRC（`pinellolab-SVG_Benchmarking/eval_simulate_data/02_compute_aupr.ipynb:47-115`）。

论文结果显示，SPARK-X 在模拟数据中排序能力最好，平均 Kendall 相关为 0.88；SpatialDE2、nnSVG 和 Moran's I 紧随其后。SPARK-X 也有最高平均 auPRC（`paper.md:95-106`）。

#### 统计校准

很多方法会输出 p 值，但 p 值是否可靠需要单独检查。论文在 null 条件下用 QQ 图和 Kolmogorov-Smirnov 距离评估 p 值是否接近均匀分布（`paper.md:112-129`, `paper.md:422-431`）。

论文结论是 SPARK 和 SPARK-X 的 p 值校准最好，而许多其他方法存在保守或反保守问题（`paper.md:112-129`）。仓库中存在 `statistical_calibration/` 工作流和每个方法的 rule，但当前 Snakefile 也包含方法/数据集缩减 override，因此本地代码证据支持其框架存在，而不是完整冻结的所有方法校准执行命令。

#### 可扩展性

论文通过模拟不同 spot 数量的数据集评估内存和运行时间。每个数据集包含 100 个基因，spot 数从 100 到 40,000（`paper.md:132-149`）。代码的 Snakemake rule 中包含 `benchmark:` 字段，可记录内存/时间指标，例如 MoranI 和 SPARK-X 的 rule（`pinellolab-SVG_Benchmarking/snakemake_simulate_data/rules/MoranI.smk:1-12`; `pinellolab-SVG_Benchmarking/snakemake_simulate_data/rules/SPARKX.smk:1-12`）。

论文报告 SOMDE 计算效率最好，SPARK-X 也较好；SPARK 和 SpatialDE 内存消耗较高；BOOST-GP 和 GPcounts 运行时间随 spot 数增加明显变慢（`paper.md:132-149`）。

### 下游空间结构域聚类

论文进一步问：用 SVG 作为特征，是否能改善空间结构域聚类？它在 DLPFC、OSCC 和 HER2 数据集上选择每个方法排名前 2000 的 SVG，作为 Leiden、BayesSpace 和 Banksy 的输入，并用 ARI 与人工注释结构域比较（`paper.md:152-168`, `paper.md:434-449`）。

本地代码对 DLPFC 部分证据最完整。README 明确描述 12 个 DLPFC 样本、spatialLIBD 标签和 Leiden/K-means/BayesSpace/Banksy 聚类（`pinellolab-SVG_Benchmarking/README.md:277-350`）。`02_get_genes.ipynb` 提取不同数量的 top genes，并生成 HVG baseline（`pinellolab-SVG_Benchmarking/snakemake_clustering/02_get_genes.ipynb:146-177`）。Leiden runner 读取 h5ad 和基因列表，做 PCA、neighbors、Leiden 聚类，然后输出 `spatialLIBD` 与 clusters（`pinellolab-SVG_Benchmarking/snakemake_clustering/clustering_methods/run_Leiden.py:25-36`）。`03_eva_clustering.ipynb` 用 adjusted rand score 计算 ARI（`pinellolab-SVG_Benchmarking/snakemake_clustering/03_eva_clustering.ipynb:68-97`）。

论文结果显示，MoranI、SpatialDE2 和 nnSVG 在空间结构域聚类任务中表现最好（`paper.md:152-168`）。但本地代码阅读没有完整核实 OSCC/HER2 的 Snakemake 输入路径，所以这部分代码匹配度是 partial。

### 空间 ATAC-seq 扩展

论文把 SVG 方法迁移到空间 ATAC-seq，把 peak 作为特征，寻找 spatially variable peaks，简称 SVP。流程是选择每个方法排名前 20,000 的 peaks，然后用 TF-IDF、LSI 和 Leiden 聚类，最后用 CHAOS 和 LISI 相关分析评价空间连续性和聚类质量（`paper.md:169-185`, `paper.md:452-464`）。

仓库的 `spatial_atac/` 目录与这个流程基本对应。直接核实到的证据包括：

- `00_spatial_atac.smk` 列出方法规则和 5 个胚胎数据集，但当前快照把 `methods` 覆盖成 `['Spanve']`（`pinellolab-SVG_Benchmarking/spatial_atac/00_spatial_atac.smk:6-31`）。
- MoranI ATAC wrapper 调用 Squidpy Moran 自相关（`pinellolab-SVG_Benchmarking/spatial_atac/methods/run_MoranI.py:29-36`）。
- `01_get_peaks.ipynb` 按方法输出字段排序并写出 top peaks，默认 `n_svgs=20000`（`pinellolab-SVG_Benchmarking/spatial_atac/01_get_peaks.ipynb:62-159`）。
- `03_clustering_svps.ipynb` 对选中 peaks 做 TF-IDF、LSI、neighbors、UMAP 和 Leiden（`pinellolab-SVG_Benchmarking/spatial_atac/03_clustering_svps.ipynb:403-426`）。
- `04_LISI.ipynb` 和 `05_CHAOS.ipynb` 计算 LISI/CHAOS 相关指标（`pinellolab-SVG_Benchmarking/spatial_atac/04_LISI.ipynb:23-55`; `pinellolab-SVG_Benchmarking/spatial_atac/05_CHAOS.ipynb:45-67`, `pinellolab-SVG_Benchmarking/spatial_atac/05_CHAOS.ipynb:106-124`）。

论文结果显示 SpatialDE2 的 CHAOS 最好，all peaks baseline 排第二，说明把现有 SVG 方法直接用于空间 ATAC 仍不理想，需要专门的 SVP 方法（`paper.md:169-185`）。

### 总体结论和使用建议

论文按多个指标汇总排名，SPARK-X 平均 rank 最好，为 4.3；SpaGFT 第二，MoranI 第三（`paper.md:186-200`）。作者强调不存在单一最优方法，选择应依赖分析目标：

- 如果目标是 SVG 排序，优先考虑 SPARK-X 或 MoranI。
- 如果数据规模很大，优先考虑 SOMDE 或 SPARK-X。
- 如果 SVG 要用于空间结构域聚类，MoranI、SpatialDE2 或 nnSVG 表现较好。
- 如果依赖 p 值筛选，需要特别注意方法校准问题；固定 top-rank 阈值可能比直接使用名义 p 值更稳妥（`paper.md:203-221`）。

### 代码复现性评价

本地代码-论文匹配度为 **medium**。强项是仓库确实包含 benchmark workflow、方法 wrapper、聚类/ATAC notebook 和指标计算 notebook。弱项是：

- 多个 Snakefile 有临时缩小方法列表的 override；
- 许多结果汇总和绘图依赖 notebook，而不是统一测试过的包接口；
- 一些 rule 中有绝对 `/data/pinello/PROJECTS/...` 路径；
- supplementary DOCX/XLSX 没有在本地解析；
- Open Problems 平台包装代码没有在本地 repo 中找到；
- scDesign3 混合模拟公式的精确实现没有从可读 notebook 文本中核实。

因此，这个工作区可以支持“论文方法和代码 scaffold 的可靠解读”，但不能声称当前克隆版本无需修改即可完整一键复现所有论文结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

Spatial transcriptomics produces gene-expression measurements tied to tissue coordinates, and a common downstream task is to identify spatially variable genes (SVGs). Many SVG methods exist, but prior benchmarks were limited in method count, technologies, simulation realism, or downstream tasks. This paper benchmarks 14 SVG detection methods across simulated spatial transcriptomics, statistical calibration, scalability, spatial-domain clustering, spatial ATAC-seq peak selection, and overall method ranking (`paper.md:59-62`, `paper.md:68-89`).

### What The Paper Contributes

The work is a benchmark framework, not a new SVG model. It uses scDesign3 and 50 real spatial transcriptomics datasets to simulate realistic spatial expression with controlled spatial variability, then evaluates methods by ranking accuracy, auPRC, p-value calibration, memory/runtime scaling, downstream clustering utility, spatial ATAC-seq SVP utility, and aggregate rank (`paper.md:86-89`, `paper.md:186-200`).

The benchmark covers 14 methods: Moran's I, Spanve, scGCO, SpaGCN, SpaGFT, Sepal, SpatialDE, SpatialDE2, SPARK, BOOST-GP, GPcounts, SPARK-X, nnSVG, and SOMDE (`paper.md:68-77`).

### How The Benchmark Works

The main simulation mixes a fitted spatial mean and a shuffled non-spatial mean:

```text
mu(s) = alpha * mu_s(s) + (1 - alpha) * mu_ns(s)
```

Alpha controls spatial signal strength, giving ground-truth variation for ranking/classification evaluation (`paper.md:266-278`). Scalability is assessed with separate synthetic datasets varying spot count from 100 to 40,000 while holding 100 genes fixed (`paper.md:132-149`, `paper.md:281-308`).

For downstream utility, the paper selects top SVGs and evaluates spatial clustering by ARI against annotated domains in DLPFC, OSCC, and HER2 datasets (`paper.md:152-168`). For spatial ATAC-seq, it treats peaks as features, selects top 20,000 SVPs, clusters with TF-IDF/LSI/Leiden, and evaluates spatial coherence by CHAOS and LISI-related analyses (`paper.md:169-185`, `paper.md:452-464`).

### Main Results

SPARK-X is the strongest general-purpose method in the benchmark: it has the highest average Kendall correlation in simulation, the highest average auPRC, good p-value calibration, and the best overall average rank of 4.3 (`paper.md:95-106`, `paper.md:186-200`).

P-value calibration is uneven. SPARK and SPARK-X are reported as well calibrated, while many other methods are conservative or anti-conservative under null conditions (`paper.md:112-129`).

Scalability changes method choice. SOMDE is best by memory/runtime, SPARK-X also scales favorably, SPARK and SpatialDE become memory-heavy, and BOOST-GP/GPcounts are slow for large spot counts (`paper.md:132-149`).

For spatial-domain clustering, SVGs usually improve over HVGs, with MoranI, SpatialDE2, and nnSVG performing best by mean rank (`paper.md:152-168`). For spatial ATAC-seq, existing SVG methods transfer poorly overall; SpatialDE2 is best by CHAOS, and the all-peaks baseline is nearly as strong (`paper.md:169-185`).

### Practical Guidance

The paper recommends SPARK-X or MoranI for SVG ranking, SOMDE or SPARK-X when scalability dominates, and MoranI/SpatialDE2/nnSVG when selected genes feed spatial clustering. It also warns against relying on nominal p-value thresholds for many methods because calibration is method-dependent; fixed-rank feature selection is often safer (`paper.md:203-221`).

### Reproducibility And Code Match

Code-paper fidelity is **medium**. The repository is a benchmark scaffold with direct Snakemake wrappers for the method runs and notebooks for metrics/plots. Directly verified code includes MoranI, SPARK-X, SpatialDE2, scGCO wrappers, DLPFC clustering runners, ATAC peak/clustering notebooks, LISI/CHAOS notebooks, and Snakemake benchmark rules (`doc_code.md`).

Important caveats: several checked-in Snakefiles contain reduced method-list overrides; many analysis steps are notebook-driven; absolute `/data/pinello/PROJECTS/...` paths appear in rules; supplementary DOCX/XLSX files were not parsed; the exact scDesign3 mixture implementation was not recovered from readable notebook text; and local Open Problems packaging code was not found (`doc_code.md`).

Overall, the paper is a useful reference benchmark for SVG method selection, but this workspace should not be described as a turnkey one-command reproduction of every result without first repairing paths, restoring method lists, fetching external data/results, and parsing supplementary materials.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
