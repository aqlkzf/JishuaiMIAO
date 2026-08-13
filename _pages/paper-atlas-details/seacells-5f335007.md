---
layout: default
permalink: /paper-atlas/seacells-5f335007/
title: "SEACells"
nav: false
description: "单细胞 RNA 和 ATAC 数据很稀疏。逐细胞分析保留了分辨率，却容易被掉零和采样噪声支配；传统聚类通过聚合增强信号，却会把一个连续分化轨迹或同一大类中的细微状态压成少数平均值。SEACells 选择中间尺度：把非常相似的几十个细胞聚成一个 metacell，使聚合计数更稳定，同时让 metacell 数远多于传统簇数。 这里的 metacell 不是新的生物细胞，也不是简单地把 UMAP 切成网格。"
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
      <span>Domain Clustering</span>
      <span>Nature Biotechnology · 2023</span>
    </div>
    <h1>SEACells</h1>
    <p>SEACells infers transcriptional and epigenomic cellular states from single-cell genomics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-023-01716-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SEACells">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/dpeerlab/SEACells" target="_blank" rel="noopener noreferrer" aria-label="Open code for SEACells">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SEACells：在单细胞与传统聚类之间构造“元细胞”

### 1. 它解决的不是普通聚类问题

单细胞 RNA 和 ATAC 数据很稀疏。逐细胞分析保留了分辨率，却容易被掉零和采样噪声支配；传统聚类通过聚合增强信号，却会把一个连续分化轨迹或同一大类中的细微状态压成少数平均值。SEACells 选择中间尺度：把非常相似的几十个细胞聚成一个 metacell，使聚合计数更稳定，同时让 metacell 数远多于传统簇数。

这里的 metacell 不是新的生物细胞，也不是简单地把 UMAP 切成网格。它是低维表型流形上一个局部、紧密细胞状态的统计代表。

### 2. 输入和输出

算法需要三类输入：

1. 原始 RNA 转录本计数或 ATAC peak/bin 计数；
2. 与模态匹配的低维表示，例如 RNA 的 PCA 或 ATAC 的 SVD；
3. 希望得到的 metacell 数量。

论文使用“约每 75 个细胞一个 metacell”作为经验起点，但强调它依赖样本复杂度。一个同质细胞系与一个肿瘤或分化系统即使细胞数相同，也不应机械地使用同一分辨率。

输出包括细胞到各原型的软权重、每个细胞的硬 metacell 标签，以及按硬标签求和得到的 metacell×feature 原始计数矩阵。

### 3. 第一步：把数据变成近邻图

SEACells 不直接在稀疏计数上找组，而是在 PCA/SVD 等嵌入中计算欧氏距离并构建 kNN 图。这个选择建立了明确的证据边界：如果预处理抹掉一个稀有状态、混入强批次效应或选错维度，后面的 metacell 优化无法恢复已经丢失的结构。

论文方法写的是默认 50 个邻居；本地 v0.3.3 API 默认 `n_neighbors=15`。复现时必须显式记录和设置该参数，不能把论文与代码默认值视为相同。

### 4. 第二步：自适应亲和核

论文希望解决不同区域细胞密度差异。高密度成熟细胞区需要较窄的局部尺度，低密度过渡态或稀有群需要较宽的尺度。对每个细胞 $i$，用其第 $l$ 个近邻距离定义局部带宽 $\sigma_i$，再把距离转成相似度。

论文给出的公式是：

$$
M(x_i,x_j)=\frac{1}{\sqrt{2\pi(\sigma_i+\sigma_j)}}
\exp\left[-\frac{1}{2}\frac{\lVert x_i-x_j\rVert^2}{\sigma_i+\sigma_j}\right].
$$

但本地 `SEACells/build_graph.py` 的实际实现为：

$$
M_{ij}=\exp\left[-\frac{\lVert x_i-x_j\rVert^2}{\sigma_i\sigma_j}\right]
$$

并只保留图掩码允许的边。它没有论文公式的归一化前因子，分母是带宽乘积而不是和，也没有额外的 $1/2$。此外，论文文字称 $M_{ij}$ 在互为邻居时非零，而代码默认 `graph_construction="union"`，即只要任一方向把另一方列为邻居就保留边；只有显式选择 `intersection` 才要求双向邻接。

因此，“自适应局部相似度”在概念上匹配，但数值核不是 Exact match。

### 5. 第三步：核原型分析

设细胞数为 $n$，metacell 数为 $s$，亲和矩阵为 $M\in\mathbb{R}^{n\times n}$。SEACells 用两个非负、列和为 1 的矩阵分解它：

$$
M\approx MBA,
$$

其中 $B\in\mathbb{R}^{n\times s}$ 把原始细胞组合成 $s$ 个原型，$A\in\mathbb{R}^{s\times n}$ 表示每个细胞由这些原型重构的权重。优化目标是减小：

$$
\lVert M-MBA\rVert_F^2.
$$

联合优化 $A$ 和 $B$ 是非凸的；固定其中一个时，对另一个是凸问题。代码交替更新 $A$ 与 $B$，每次用 Frank–Wolfe 条件梯度更新，并以重构误差变化决定是否收敛。

### 6. 为什么初始化能覆盖低密度状态

如果随机选择初始原型，高密度区域会获得过多名额。SEACells 先在扩散空间中进行 maximum–minimum waypoint sampling：每次选择离已选集合最远的点，使初始点更均匀地覆盖表型流形。代码还实现了贪心列子集选择作为补充。

本地默认 `waypoint_proportion=1`，所以通常全部使用 waypoint 候选；但随后会调用 `np.random.choice` 对候选做不放回抽样，A 也从随机权重开始。不同随机种子可能落入不同局部最优，正式复现必须设置 NumPy 随机种子并报告多次初始化稳定性。

### 7. 从软权重到真正的聚合计数

硬标签很直接：对每个细胞，在 A 矩阵该列中取最大权重的原型，即 `argmax`，然后 `summarize_by_SEACell()` 把同一标签下的原始计数求和。这条路径对应论文的主要 metacell 计数输出。

需要区分另一个函数 `summarize_by_soft_SEACell()`：它把小于 0.05 的权重置零并重新归一化，再计算加权平均而不是总和。其结果是 pseudo-size/加权表达表示，不能与硬分配后的原始计数求和混称为同一种输出。论文关于“小权重清零”的描述也不意味着 `get_hard_assignments()` 在 argmax 前执行了该阈值；本地硬分配直接使用未阈值化的 A。

### 8. 六幅主图提供了什么证据

- 图 1 从传统簇丢失 GATA2 连续变化开始，展示 waypoint、亲和矩阵、核原型分解和最终 metacell 块结构。
- 图 2 显示 RNA 与 ATAC metacell 对 PBMC 类型的覆盖和纯度，并用 CD34+ 分化轨迹说明聚合后仍能恢复表达与可及性动态。
- 图 3 把 metacell 用于调控推断。TAL1 的 peak–expression 相关在 metacell 层面为 0.82，单细胞层面为 0.03；该数值支持特定数据与流程，不能外推为固定“提升倍数”。
- 图 4 比较 MetaCell、MetaCell-2 和 SuperCell，重点是表型空间覆盖、紧密度、分离度及 peak–expression 相关；不同方法的 metacell 数和离群处理并非始终完全等价。
- 图 5 展示红系分化中 chromatin peaks 逐渐开启或关闭，并得到 GATA 与 PU.1 motif 富集。这是聚合后调控分析的应用证据，不是 SEACells 优化目标的一部分。
- 图 6 先按患者样本分别构造 metacell，再做 Harmony 集成和二级聚合，识别 COVID-19 相关 CD4 T 状态。图中核心子集为 177,242 个细胞；论文另在 119 个样本、超过 60 万细胞的完整 atlas 上得到约 8,000 个 metacell。

### 9. 稀有状态与大队列能力应怎样理解

maximum–minimum 初始化和自适应带宽有利于低密度区域。论文在 PBMC 中恢复 pDC/B-cell precursor，并在小鼠原肠胚数据中保留占比 0.2% 的内皮细胞 metacell。这证明测试设置下的灵敏度，而不是“所有稀有群必然保留”的保证。

大队列的关键工程策略是**按样本分别构造 metacell，再集成聚合结果**。因此“分析 60 万细胞”不等于一次性构造一个 60 万×60 万的稠密核。本地默认 dense CPU 路径会形成矩阵乘积，内存压力与实现后端强相关；大数据应优先评估 sparse CPU/GPU 路径和逐样本拆分。

### 10. 复现清单与结论

至少记录：原始计数层、归一化方法、HVG/peak/bin 选择、PCA/SVD 维度、是否移除 ATAC 第一 SVD 分量、邻居数、union/intersection、metacell 数、随机种子、backend、收敛阈值、依赖版本，以及硬聚合还是软加权聚合。

结论：SEACells 的核心思想和 $M\approx MBA$ 优化在论文与代码间吻合，metacell 也确实为稀疏调控数据和大队列分析提供了有效中间尺度。但亲和核公式、邻居默认值和邻接规则存在实质差异，代码快照仅能追溯到 v0.3.3、不能追溯到具体上游 commit。因此代码—论文匹配应标为 **Partial/Medium**，而不是 Exact。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Answer First

SEACells compresses sparse single-cell measurements into finer-grained, biologically coherent metacells. It builds an adaptive cell-affinity graph in a modality-appropriate embedding, applies kernel archetypal analysis, assigns each cell to an archetype, and sums raw counts within each hard assignment. The result occupies a useful middle scale: denser than individual cells but more granular than conventional clusters.

The paper and local package agree on this architecture, but the checked v0.3.3 source does **not** implement the paper's affinity-kernel equation literally. The paper describes 50 neighbors by default, mutual-neighbor edges, a bandwidth sum and a normalization prefactor. The package defaults to 15 neighbors, uses the union of directed kNN edges, and computes `exp(-distance² / (sigma_i * sigma_j))` without that prefactor. Code-paper fidelity is therefore **partial/medium**, despite a strong match for archetypal decomposition and hard aggregation.

### Inputs and Outputs

Inputs are an AnnData object with raw counts, a low-dimensional representation such as PCA for RNA or SVD for ATAC, and a user-specified number of metacells. The paper recommends about one metacell per 75 cells as a heuristic, not a universally optimal choice.

The fitted model exposes soft archetype weights and hard labels in `ad.obs['SEACell']`. `summarize_by_SEACell()` sums counts for hard groups into a metacell-by-feature matrix. The separate soft summarizer thresholds weights below 0.05, renormalizes them and computes weighted averages; it should not be confused with raw-count summation.

### Evidence

Figures 1–2 establish the main algorithm and show coverage, purity, rare-state recovery and trajectory preservation in RNA and ATAC. Figure 3 uses metacell aggregation for peak–gene association, NFR peak analysis and TF activity; the reported TAL1 peak–expression correlation is 0.82 across metacells versus 0.03 across single cells. Figure 4 compares state coverage and compactness/separation with MetaCell, MetaCell-2 and SuperCell. Figure 5 uses metacell resolution to reveal gradual opening and closing of chromatin during erythroid differentiation. Figure 6 demonstrates sample-wise aggregation and downstream integration in a 177,242-cell COVID-19 subset; the broader atlas analysis summarized more than 600,000 cells from 119 samples into roughly 8,000 metacells.

Rare-state support includes pDC and B-cell precursor recovery and a mouse-gastrulation downsampling experiment in which endothelial cells represented 0.2% of the population. These results support sensitivity in the tested settings, not a general guarantee that every rare state will survive an embedding or an incorrectly chosen metacell count.

### Reproducibility Boundary

Rating: **4/5 for rerunning the public package and tutorials; partial for an exact paper-method reproduction**.

The local snapshot contains package v0.3.3, CPU sparse/dense and GPU implementations, tutorial notebooks and downstream ATAC utilities. Exact reruns require a random seed because waypoint subsampling and initial A weights use NumPy randomness. They also require recording the embedding, `n_neighbors`, graph construction mode, metacell count, CPU/GPU/sparse backend and package/dependency versions.

No unsupported fixed claims such as “100× faster,” “10× less memory,” or universal 100% cell retention are made here. The paper states orders-of-magnitude downstream compute reduction in the large cohort and documents method-specific outlier behavior, but those statements are not interchangeable with a benchmark of core SEACells fitting time or a universal retention guarantee.

### Direct Evidence

- Paper: `paper source/s41587-023-01716-9/s41587-023-01716-9.md`
- PDF and extracted figures: `s41587-023-01716-9.pdf`, `paper source/s41587-023-01716-9/`
- API and aggregation: `SEACells/core.py`
- Kernel construction: `SEACells/build_graph.py`
- Optimization: `SEACells/cpu.py`, `SEACells/cpu_dense.py`, `SEACells/gpu.py`
- Tutorials and regulatory utilities: `notebooks/`, `SEACells/accessibility.py`, `SEACells/genescores.py`, `SEACells/tfactivity.py`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
