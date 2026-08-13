---
layout: default
permalink: /paper-atlas/cellscope-a4826332/
title: "CellScope"
nav: false
description: "CellScope 是面向 scRNA-seq 的“特征选择 + 去噪 + 层次聚类 + 多层可视化”工作流。它先从局部高密度细胞中构造少量可靠小团体，用这些团体间的 ANOVA 挑出能区分潜在群体的基因；再把最低密度的细胞向附近高密度细胞轻度投影；最后在相似图上做平均连接层次聚类，并把多个聚类分辨率画成树。它不是轨迹推断模型，树的分叉表示聚类层级，不应直接解释为真实发育谱系或时间方向。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>CellScope</h1>
    <p>CellScope: High-Performance Cell Atlas Workflow with Tree-Structured Representation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2025.02.15.638400" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellScope">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/zhigang-yao/CellScope" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellScope">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellScope：从流形拟合到多尺度细胞树

### 一句话理解

CellScope 是面向 scRNA-seq 的“特征选择 + 去噪 + 层次聚类 + 多层可视化”工作流。它先从局部高密度细胞中构造少量可靠小团体，用这些团体间的 ANOVA 挑出能区分潜在群体的基因；再把最低密度的细胞向附近高密度细胞轻度投影；最后在相似图上做平均连接层次聚类，并把多个聚类分辨率画成树。它不是轨迹推断模型，树的分叉表示聚类层级，不应直接解释为真实发育谱系或时间方向。

### 1. 论文怎样定义两种噪声

论文把观察矩阵概念化为

$$
Y=(X+N_1)\oplus N_2,
$$

其中 $X$ 是携带细胞状态的低维信号，$N_1$ 是信号空间内的技术扰动，$N_2$ 是被作者称作“housekeeping gene noise”的非分类维度。这个式子是工作假设，不是从测量过程中可辨识出的严格生成模型。尤其是 housekeeping gene 本身具有生物功能；CellScope 实际做的是保留对当前数据分群有区分力的基因，而不是证明未选基因都是 housekeeping genes。

### 2. 输入与归一化边界

输入为 cell × gene 非负矩阵。`Normalization()` 返回原尺度、对数尺度和逐细胞 L2 归一化矩阵。但代码没有显式的“raw/log”参数，而是以最大值是否超过 1000 猜测：大于 1000 才执行 $\log_2(x+1)$；不超过 1000 则当作已经对数化。对常见但最大计数低于 1000 的原始 UMI 矩阵，这个启发式可能误判，用户应先确认输入尺度。

### 3. 第一步流形拟合：怎样选 500 个基因

#### 3.1 在 PCA 空间寻找流形种子

默认先取 100 个 PCA 维度。对每个细胞 $p_i$，用 20 个近邻定义局部密度

$$
\rho_i=\frac{1}{\sum_{j\in\mathcal N_i}d(p_i,p_j)},
$$

再计算到更高密度近邻的最小距离 $\delta_i$；若当前近邻中没有更高密度点，就取最远近邻距离。密度高且与其他密度峰相隔远的点具有较大的 $\gamma_i=\rho_i\delta_i$。

`findCenters()` 先 min–max 归一化 $\rho$、$\delta$，按 $\gamma$ 排序，再把梯度、$\gamma$、$\rho$、$\delta$ 四个高于相应条件的集合相交；若自动种子少于三个，退回前三个 $\gamma$ 点。因此“自适应种子”仍是确定的经验规则，不是估计真实细胞类型数。

#### 3.2 从种子形成可靠 cliques

每个种子取最邻近的五个细胞。若这些小团体发生重叠，代码用连通分量合并；若所有种子最终连成一个分量，就逐步减小团体大小。得到的 clique 标签是伪分组，只用于特征检验。

#### 3.3 ANOVA 排序

对每个基因，在这些可靠 cliques 之间做单因素 ANOVA，按 p 值从小到大选择默认前 500 个基因。直觉是：同一高密度团体内稳定、不同团体间变化大的基因更可能保留群体结构。这里没有多重检验阈值；“500”是固定数量，所以 p 值主要作为排序分数。

### 4. 第二步流形拟合：把低密度细胞向内拉

在 500 基因空间重新计算 5 邻域密度，把最低 5% 的细胞视作 fitting points。每个点寻找第一个不在低密度集合中的近邻，并更新为

$$
z_i=0.1y_i+0.9\hat y_i.
$$

这与论文 $t=0.9$ 的写法等价。默认不是删除细胞，而是强烈向一个邻近高密度点靠拢。它可能压低由技术噪声造成的离群，也可能平滑真实过渡态或极稀有群体；“低密度”本身不能区分这两种情形。

### 5. 图聚类的真实代码路径

`construct_graph()` 构建 kNN 图，`compute_umap_similarity_graph()` 用 UMAP 风格的局部尺度生成有向 membership，再通过

$$
w_{ij}=s_{ij}+s_{ji}-s_{ij}s_{ji}
$$

对称化。随后 `Trans_W_D()` 把稀疏相似度转成压缩距离向量 $1-w_{ij}$，未连边对默认距离为 1；`fastcluster.linkage(..., method="average")` 生成一棵平均连接树。

论文与代码在这里有实质差异：

- 论文写 $k=\lceil\log_2N\rceil$；代码在小数据的 Euclidean 路径用 `int(ln N)`，在大数据 Jaccard 路径用 $10\,\mathrm{int}(\ln N)$。
- 论文写 $\exp(-d^2/\sigma_i^2)$；代码使用 UMAP 风格的 $\exp(-(d-\rho_i)/\sigma_i)$ membership，距离和尺度没有平方。
- 超过 100,000 个细胞时，论文描述按对每个簇的平均相似度分配未采样细胞；代码用五近邻标签的多数票。

这些不是仅符号不同，而会改变邻域图和大样本标签，复现时应以代码为准。

### 6. 输出不是一个“自动最佳 K”

`GraphCluster()` 固定输出 49 列：$K=2,3,\ldots,50$ 的全部切树结果。它没有无监督选择最终 $K$ 的函数。教程直接取某一列；评价代码可用真标签计算 ARI。论文对 Scanpy 和 Seurat 在多个 resolution 中选择最高 ARI，属于使用真值的 benchmark oracle，不能当成无标签实际应用的调参方式。

`generate_tree_structured()` 也有同样边界：若用户不给终止层 `step1`，必须提供 `cell_type`，代码用每一层与真标签的 ARI 最大值选择 `step1`。教程则手工传入 `step1=8`。所以树可在无标签时生成，但树展示到哪一层需要用户决定；不能声称代码自动从表达矩阵确定生物学终层。

### 7. 树状图应该怎样读

树状图为每个层次簇独立计算 UMAP，再按相邻切树结果中的包含关系连接父子节点。它能展示“一个粗簇如何在更高 K 下分开”，但各节点 UMAP 坐标系彼此独立，圆之间的距离和方向不能横向比较。分叉是 average-linkage dendrogram 的切割关系，不证明细胞从父节点分化成子节点。

Fig. 3 的 Usoskin 数据用较粗层对应四类神经元，再在更细层区分部分亚型，是这种读法的合适例子。Fig. 4 在 Siletti-1 中展示 midbrain 群体和少量 fibroblast，并提出两个 oligodendrocyte 组件；正文称 OL1/OL2 为 679/1454 个细胞，而 Fig. 4a 图例显示 Oligodendrocyte 1/2 为 541/1592，二者不一致，不能混合引用。

### 8. “动态分子身份”实际怎样计算

对树上每一对 sibling clusters，`Gene_Analysis()` 用 SciPy 的一维 Wasserstein distance 比较某基因的两个表达分布：

$$
W_1(P,Q)=\int_0^1|F_P^{-1}(u)-F_Q^{-1}(u)|\,du.
$$

然后按固定阈值分类：

- $W_1<0.5$：Housekeeper；
- $0.5\le W_1\le1$：Type-Related；
- $W_1>1$：Type-Determining。

论文则规定 $W_1\ge1$ 为 strongly cell-type-related，因此恰好 $W_1=1$ 时存在边界差异。更重要的是，Wasserstein 距离依赖表达尺度，0.5/1 并非跨归一化方法普适的生物学常数。“动态”表示同一基因在不同树层的类别可变，不是时间动态。

### 9. 六幅主图的证据链

- Fig. 1 是算法概念图，展示两步流形拟合、图聚类、树和基因身份，不是实测结果。
- Fig. 2 汇总 36 个带标签数据集。论文报告 CellScope 平均 ARI 0.88，Scanpy 0.68，Seurat 0.66，并显示运行时间和基因选择比较。由于候选分辨率用真标签选优，这些数字是受监督评测协议下的比较。
- Fig. 3 展示相似类型、稀有类型和 Usoskin 多层聚类。稀有类型 F1 提升是标签驱动评价，不代表每个新数据集都能自动识别罕见类型。
- Fig. 4 用脑图谱说明树与基因身份；OL 亚型与 marker 是计算和文献关联，尚非独立实验验证。
- Fig. 5 对 COVID-19 PBMC 的 monocyte/dendritic 系统分层，显示 interferon/viral-response 基因与疾病组别关联。横断面表达关联不能证明病程轨迹或因果调控。
- Fig. 6 是消融与参数敏感性：自适应种子、两步拟合、距离选择、基因数和 PCA 维度都会影响结果；这也说明默认参数虽总体稳健，并非数据无关。

### 10. 代码可复现性

本地 `CellScope/` 与官方仓库 `zhigang-yao/CellScope` 提交 `eaf153f807e160384020b2c5305b7ab3b7e28dd1` 逐文件一致，包含 Python 包、两个教程和四个小型测试数据集。核心流形拟合、图聚类、树可视化、marker、Wasserstein 分类和聚类指标均可定位。

但完整论文复现仍是 Partial：仓库没有 36 数据集统一 benchmark 驱动脚本、Scanpy/Seurat 批量比较、论文 Wilcoxon 统计或 Fig. 5 专用分析流程；大数据依赖外部下载；Python 被限制为 `<3.11`，而若干依赖最低版本较新；层次聚类在 100k 样本上仍有高内存成本。`Test Data/Readme.md` 把 `GSE59739` 写成 `GSE58739`，属于数据编号文档错误。

### 证据来源

本解读依据本地 bioRxiv PDF/转换 Markdown、六幅主图的直接视觉复核、教程 notebook，以及官方一致快照中的 `cs.py`、`ts.py`、`ga.py`、`fm.py`、`cm.py`。论文主张、图中观察、代码行为和生物学解释分别保留其证据边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellScope: High-Performance Cell Atlas Workflow with Tree-Structured Representation

### Executive Summary

**CellScope** is an innovative computational framework for constructing high-resolution, multi-scale cell atlases from single-cell RNA sequencing data. The method addresses fundamental challenges in single-cell analysis through a two-step manifold fitting process for gene selection and noise reduction, followed by graph-based agglomerative clustering, uniquely integrating UMAP visualization with hierarchical clustering to represent cellular relationships at multiple biological levels.

**Interpretation boundary**: CellScope returns a hierarchy of statistical clusters, not a developmental lineage or an automatically selected biological taxonomy. `GraphCluster()` emits cuts for $K=2$ through 50; users must select a level, and the optional automatic tree endpoint uses supplied true labels and maximum ARI.

**Paper**: Li et al. (2025) bioRxiv 2025.02.15.638400
**Paper markdown source**: `paper source/2025.02.15.638400v1.full (1)/2025.02.15.638400v1.full (1).md`
**Repository**: https://github.com/zhigang-yao/CellScope
**Documentation**: https://cellscope.readthedocs.io/en/latest/
**Code Version**: CellScope-RNA v0.1.4

---

### Motivation and Novelty

#### Biological Problem

Single-cell sequencing enables comprehensive profiling of individual cells, but current analysis frameworks face several critical limitations:

> "Commonly used pipelines, such as Seurat, Scanpy, and SnapATAC, rely on conventional unsupervised learning techniques that may not adequately handle the high-dimensionality, sparsity, and noise inherent in single-cell datasets." (Introduction)

Key challenges include:
1. **Biased gene selection**: HVG methods "can be sensitive to technical noise and may overlook rare cell types with subtle but biologically relevant variations"
2. **Limited hierarchical representation**: Louvain clustering "lacks a hierarchical structure that captures the nested relationships and developmental trajectories between cell types"
3. **Inadequate visualization**: t-SNE/UMAP "emphasize local similarities at the expense of preserving the overall topology"

#### Unique Contributions

1. **Two-step manifold fitting** for simultaneous gene selection and noise reduction
2. **Density-based manifold seed identification** for constructing "highly reliable cliques"
3. **Tree-structured visualization** combining UMAP with hierarchical clustering
4. **Dynamic molecular identity system** categorizing genes as Housekeeping (HG), Moderately Cell-Type-Related (MCTRG), or Strongly Cell-Type-Related (SCTRG)

---

### Method Overview

#### Core Algorithmic Framework

CellScope operates under the manifold assumption:

> "The true biological structure of single-cell data lies on a low-dimensional manifold... However, the observed single-cell data does not directly reflect this manifold due to two types of noise." (Results - Overview of CellScope workflow)

**Two noise types addressed:**
1. **Housekeeping gene noise**: Ubiquitous expression irrelevant to cell classification
2. **Technical noise**: mRNA loss, inefficient molecule capturing, sequencing errors

#### Workflow Components

| Step | Function | Key Innovation |
|------|----------|----------------|
| **A. Manifold Fitting 1** | Gene selection via ANOVA on reliable cliques | Density-based seed identification |
| **B. Manifold Fitting 2** | Project low-density outliers to high-density regions | 5% lowest density cells projected with $t=0.9$ |
| **C. Graph Clustering** | Agglomerative clustering on UMAP-like similarity graph | Size-based Jaccard/Euclidean switch |
| **D. Tree Visualization** | Hierarchical UMAP representation | Color propagation from leaves to roots |
| **E. Gene Characterization** | Wasserstein distance-based classification | Three-category dynamic identity system |

#### Key Mathematical Formulations

**Local density and relative distance (Methods A2):**

$$\rho(p_i) = \frac{1}{\sum_{j \in \mathcal{N}_i} d(p_i, p_j)}, \quad \delta(p_i) = \min_{j \in \mathcal{N}_i, \rho(p_j) > \rho(p_i)} d(p_i, p_j)$$

**Manifold seed selection criterion:**

$$\gamma(p_i) = \rho(p_i)\delta(p_i)$$

**Normalization (Methods A2):**

$$\rho'(p_i) = \frac{\rho(p_i) - \min(\rho)}{\max(\rho) - \min(\rho)}, \quad \delta'(p_i) = \frac{\delta(p_i) - \min(\delta)}{\max(\delta) - \min(\delta)}$$

**Seed selection set $C$ (Methods A2):**

$$C = \left\{ p_i \;\middle|\; \rho'(p_i) > \overline{\rho'},\; \delta'(p_i) > \overline{\delta'},\; \gamma'(p_i) > \overline{\gamma'},\; R_{I(p_i)} < \overline{R} \right\}$$

**Outlier projection (Methods B):**

$$z_i = t\hat{y}_i + (1 - t)y_i,\quad t=0.9$$

**UMAP similarity with Gaussian kernel (Methods C):**

$$s_{ij} = \exp\left(-\frac{\|z_i - z_j\|^2}{\sigma_i^2}\right)$$

**Symmetric similarity (Methods C):**

$$w_{ij} = s_{ij} + s_{ji} - s_{ij} \cdot s_{ji}$$

**Gene classification via Wasserstein distance (Methods E):**

$$W_1(P,Q) = \int_0^1 |F_P^{-1}(x) - F_Q^{-1}(x)| dx$$

| Wasserstein Distance | Gene Category |
|---------------------|---------------|
| $W_1 < 0.5$ | Housekeeping Gene |
| $0.5 \leq W_1 < 1$ | Moderately Cell-Type-Related |
| $W_1 \geq 1$ | Strongly Cell-Type-Related |

---

### Evaluation Summary

#### Benchmark Performance

**Dataset scope**: 36 scRNA-seq datasets, 90-265,767 cells, 3-20 cell types

| Metric | CellScope | Seurat | Scanpy |
|--------|-----------|--------|--------|
| **Mean ARI** | 0.88 +/- 0.01 | 0.66 +/- 0.03 | 0.68 +/- 0.04 |
| **Rank 1 (out of 36)** | 32 | - | - |
| **Runtime** | 1x (baseline) | >4x | >2x |

> "CellScope significantly outperformed the other methods... The Wilcoxon signed-rank test confirmed CellScope's superiority over Seurat ($p = 2.91 \times 10^{-10}$) and Scanpy ($p = 2.56 \times 10^{-9}$)." (Results)

#### Biological Validation

1. **Human Brain Cell Atlas (Siletti-1)**: Identified 2 novel oligodendrocyte subtypes (OL1: 679 cells, OL2: 1454 cells) distinguished by *RBFOX1* (mature terminal state) and *OPALIN* (active myelination)

2. **COVID-19 PBMC analysis**: Identified 8 marker genes (*IFIT1, OAS2, OAS3, RNASE2, SIGLEC1, IFI44, IFI27, HLA-DRB5*) distinguishing disease severity states in monocyte-dendritic cell system

3. **Rare cell detection**: Significantly higher F1 scores for cell types comprising <5% of population

#### Gene Selection Comparison

> "30% of CellScope-specific genes showed strong differential expression (variance ratio > 1) between cell classes, whereas only 3% of Seurat-specific genes exhibited such pronounced differences." (Results)

---

### Paper-Code Mapping Table

#### Core Algorithm Implementation

| Paper Element | Code Location | Fidelity | Notes |
|--------------|---------------|----------|-------|
| **Manifold Fitting Step 1** | | | |
| Log normalization (A1) | `cs.py:176-200` | EXACT | Handles sparse matrices; skips if max<=1000 |
| L2 normalization (per cell) | `cs.py:181-189` (sparse), `cs.py:198` (dense) | EXACT | Row-wise L2 norm |
| PCA reduction (n1=100) | `cs.py:305-310` | EXACT | Default 100, uses randomized_svd for sparse |
| Local density rho(pi) = 1/sum(d) | `cs.py:316` | EXACT | `rho = 1. / np.sum(D_NB, axis=1)` |
| Relative distance delta(pi) | `cs.py:317-327` | EXACT | Iterates over neighbors with higher density |
| gamma'(pi) = rho' * delta' (normalized) | `cs.py:236-240` in `findCenters()` | EXACT | Min-max normalization applied |
| Gradient-based seed selection | `cs.py:245-251` | EXACT | Intersects 4 conditions: rho', delta', gamma', R |
| Highly reliable cliques (k1=5 neighbors) | `cs.py:338-355` | EXACT | Default k1=5, connected components |
| ANOVA gene selection | `cs.py:255-270`, `cs.py:360-363` | EXACT | `scipy.stats.f_oneway` parallelized with joblib |
| Select top D1=500 genes | `cs.py:363-364` | EXACT | Default 500 genes |
| **Manifold Fitting Step 2** | | | |
| Outlier detection (5% lowest density) | `cs.py:397-403` | EXACT | `fitting_prop=0.05` default |
| Projection z = t*y_hat + (1-t)*y | `cs.py:406-409` | EXACT | Code uses `coeff=0.1` (equivalent to t=0.9 paper) |
| **Graph-Based Clustering** | | | |
| k = ceil(log2(N)) neighbors (Euclidean) | `cs.py:144` | PARTIAL | `knn = int(np.log(fea.shape[0]))` |
| k = 10*log(N) neighbors (Jaccard) | `cs.py:131` | PARTIAL | Different from paper's log2(N) |
| Gaussian kernel similarity | `cs.py:54-88`, `cs.py:90-108` | PARTIAL | Uses linear exp(-d/sigma), not squared exp(-d^2/sigma^2) |
| Symmetric similarity wij | `cs.py:46-51` | EXACT | `W + W.T - W*W.T` |
| Average linkage clustering | `cs.py:496`, `cs.py:513` | EXACT | `fastcluster.linkage(..., method='average')` |
| Adaptive distance (Euclidean/<10k, Jaccard/>=10k) | `cs.py:472-475` | EXACT | Threshold at 10,000 cells |
| Large dataset subsampling (>100k) | `cs.py:477-508` | EXACT | Random 100k sample, KNN-based label assignment |
| **Tree Visualization** | | | |
| Initial UMAP embedding | `ts.py:76-77` | EXACT | `n_neighbors=min(15,N-1), min_dist=0.1` |
| Per-cluster UMAP | `ts.py:91-96` | EXACT | Independent UMAP for each cluster |
| Hierarchical tree construction | `ts.py:107-134` | EXACT | Tracks cluster splits via mapping |
| **Gene Characterization** | | | |
| Wasserstein distance calculation | `ga.py:27-32` | EXACT | Uses `scipy.stats.wasserstein_distance` |
| Gene classification thresholds | `ga.py:39-48` | EXACT | HG: <0.5, MCTRG: 0.5-1, SCTRG: >1 |
| **Evaluation Metrics** | | | |
| ARI calculation | `cm.py:102` | EXACT | `sklearn.metrics.adjusted_rand_score` |
| Label alignment (Hungarian) | `cm.py:41-73` | EXACT | `scipy.optimize.linear_sum_assignment` |

#### Equations Verification Summary

| Paper Equation | Code Location | Status |
|----------------|---------------|--------|
| Eq.1: $\rho(p_i) = 1/\sum_{j} d(p_i,p_j)$ | `cs.py:316` | EXACT |
| Eq.1: $\delta(p_i) = \min$ to higher-rho neighbor | `cs.py:317-327` | EXACT |
| Eq.2: $\gamma(p_i) = \rho(p_i)\delta(p_i)$ | `cs.py:240` | EXACT |
| Eq.3: Min-max normalization | `cs.py:236-237` | EXACT |
| Eq.4: Gradient $R_j$ | `cs.py:245` | EXACT |
| Eq.5: Seed selection criteria $C$ | `cs.py:246-251` | EXACT |
| Eq.6: Projection $z_i = t\hat{y}_i + (1-t)y_i$ | `cs.py:406-409` | EXACT (coeff=0.1 = t=0.9) |
| Eq.7: Gaussian similarity $s_{ij}$ | `cs.py:102-103` | UMAP-style linear kernel |
| Eq.8: $\sigma_i$ calibration | `cs.py:54-88` | EXACT |
| Eq.9: Symmetric similarity $w_{ij}$ | `cs.py:46-51` | EXACT |
| Eq.10: Average linkage | `cs.py:496,513` | EXACT |
| Eq.11-12: Wasserstein distance | `ga.py:27-32` | EXACT via scipy |
| Eq.13: Gene classification thresholds | `ga.py:39-42` | EXACT |

---

### Technical Discrepancies Identified

| Paper Claim | Code Reality | Impact | Code Location |
|-------------|--------------|--------|---------------|
| $s_{ij} = \exp(-\|z_i-z_j\|^2/\sigma_i^2)$ | Uses UMAP-style fuzzy membership `exp(-dist/sigma)` (no square) | Medium - changes similarity decay; follows UMAP convention | `cs.py:102-103` |
| $k = \lceil\log_2(N)\rceil$ neighbors | Uses `int(log(N))` for Euclidean, `10*int(log(N))` for Jaccard | Low/Medium - neighbor count differs; may affect graph connectivity | `cs.py:131,144` |
| Paper large-N assignment (max avg similarity to clusters) | Uses KNN majority vote (mode) for unselected points when subsampling | Medium - assignment rule differs from paper Methods C | `cs.py:505-508` |
| Gene identity thresholds: SCTRG if $W_1\ge 1$ | Code treats $W_1=1$ as "Type-Related" ($0.5\le W\le 1$), SCTRG only for $W>1$ | Low - boundary-case mismatch at exact threshold | `ga.py:40-41` |
| Gene category names HG/MCTRG/SCTRG | Code labels: Housekeeper / Type-Related / Type-Determining | None - naming mismatch only | `ga.py:46-48` |

---

### Reproducibility Assessment

#### Rating: 4/5 (Good)

#### Strengths
- Complete Python implementation available on GitHub (CellScope-RNA package v0.1.4)
- Comprehensive documentation at ReadTheDocs
- Tutorial notebooks provided (2 Jupyter notebooks)
- Default parameters well-documented with sensitivity analysis (Figure 6 in paper)
- Fixed random seed (83) for reproducibility (`cs.py:21-23`)
- Core pipeline is implemented with 20/22 equations verified exact
- Parallel processing via joblib for ANOVA and Wasserstein calculations

#### Potential Blockers

| Issue | Severity | Notes |
|-------|----------|-------|
| Python version constraint | Low | Requires 3.7-3.10 (setup.py specifies <3.11) |
| Random seed handling | Low | Fixed seed (83) for reproducibility |
| Large dataset handling | Medium | Subsampling for >100k cells to 100,000 |
| No explicit GPU support | Low | Relies on sklearn/numba parallelization |
| Sparse matrix handling | Low | Converts to dense for `Manifold_Fitting_2` |
| Memory usage | Medium | Hierarchical clustering is O(N^2) memory |

#### Data Availability
All 36 benchmark datasets available via GEO, ENA, dbGaP, and BRAIN Initiative Cell Census Network with specific accession numbers provided in Supplementary Table S2.

#### Missing/Not Implemented in Code
- Wilcoxon signed-rank test p-values (Figure 2a statistics) - NOT FOUND in core code
- Silhouette score calculation - Used in paper benchmarks but not implemented as standalone function
- Disease-control pipeline (Figure 5) - Analysis workflow not implemented as dedicated function
- Benchmarking against Seurat/Scanpy - Comparison code not included

---

### Key Insights for Implementation

#### Default Parameters (from code verification)

| Parameter | Default | Location | Notes |
|-----------|---------|----------|-------|
| `num_pca` | 100 | `cs.py:273` | PCA dimensions |
| `num_Selected_Gene` | 500 | `cs.py:273` | Genes to select via ANOVA |
| `knn` | 20 | `cs.py:273` | Neighbors for density estimation |
| `fitting_prop` | 0.05 | `cs.py:367` | 5% outlier proportion |
| `coeff` | 0.1 | `cs.py:367` | Projection coefficient (paper uses t=0.9) |
| `num_center` | 0 | `cs.py:273` | Auto-detect manifold seeds |
| `num_cell_thre` | 100,000 | `cs.py:442` | Subsampling threshold |

#### Robustness Findings (paper)

> "CellScope offers robust performance and ease of use across various settings... the ARI remained stable across different dimensions of PCA."

- **PCA dimensions**: Stable ARI across 50-150 dimensions (optimal ~100)
- **Gene selection**: Robust across 100-1000 genes (optimal ~500)
- **Manifold seeds**: Adaptive method outperforms fixed-number approaches

---

### Code Architecture

#### Module Structure

```
CellScope/
├── __init__.py          # Module exports
├── cs.py                # Core algorithms (545 lines)
│   ├── Normalization()           # Log + L2 normalization
│   ├── Manifold_Fitting_1()      # Gene selection via ANOVA
│   ├── Manifold_Fitting_2()      # Outlier projection
│   ├── GraphCluster()            # Agglomerative clustering
│   └── Visualization()           # UMAP/t-SNE/PCA embedding
├── cm.py                # Clustering metrics (113 lines)
│   ├── process_labels()          # Label preprocessing
│   ├── best_map()                # Hungarian algorithm
│   └── calculate_metrics()       # ARI, NMI, ACC, F1, Jaccard
├── fm.py                # Find marker genes (155 lines)
│   └── FindMarker()              # Differential expression
├── ga.py                # Gene analysis (127 lines)
│   ├── Gene_Analysis()           # Wasserstein distance
│   └── plot_sankey()             # Sankey diagrams
├── gev.py               # Gene expression visualization
│   ├── scatter_gene_expression()
│   ├── plot_mean_expression_heatmap()
│   └── compare_violin_plot_between_classes()
└── ts.py                # Tree-structured visualization (850 lines)
    ├── generate_tree_structured()
    ├── visualize_tree_structured()
    ├── tree_structure_visualization_static()
    └── tree_structure_visualization_dynamic()
```

#### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >=1.26.4, <2.2 | Array operations |
| scipy | >=1.13.1 | Statistics, clustering, sparse matrices |
| scikit-learn | >=1.6.1 | PCA, KNN, metrics |
| umap-learn | >=0.5.7 | UMAP dimensionality reduction |
| fastcluster | >=1.2.6 | Hierarchical clustering |
| numba | >=0.61.2 | JIT compilation for performance |
| matplotlib | >=3.10.1 | Visualization |
| plotly | >=6.0.1 | Interactive Sankey diagrams |
| networkx | >=3.4.2 | Tree graph construction |

---

### References

- GitHub: https://github.com/zhigang-yao/CellScope
- Documentation: https://cellscope.readthedocs.io/en/latest/
- Paper: Li et al. (2025) CellScope: High-Performance Cell Atlas Workflow with Tree-Structured Representation (bioRxiv 2025.02.15.638400)
- Code Version: CellScope-RNA v0.1.4

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
