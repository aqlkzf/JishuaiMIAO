---
layout: default
permalink: /paper-atlas/descart-a0a71ba1/
title: "Descart"
nav: false
description: "Descart 面向 spatial ATAC-seq：它把物理相邻关系与染色质可及性相似关系融合成 spot/cell 图，再衡量每个 peak 的可及性向量是否沿图边保持一致。图上自相关高的 peak 被排在前面，作为 spatially variable（SV）peaks；同一图还被用于数据平滑、peak modules 和 gene–peak association。 它不是逐 peak 拟合空间概率分布，也不直接输出显著性检验。"
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
      <span>Genome Biology · 2024</span>
    </div>
    <h1>Descart</h1>
    <p>Descart: a method for detecting spatial chromatin accessibility patterns with inter-cellular correlations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-024-03458-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Descart 方法解读：用空间图与染色质图共同寻找 SV peaks

### 一句话定位

Descart 面向 spatial ATAC-seq：它把物理相邻关系与染色质可及性相似关系融合成 spot/cell 图，再衡量每个 peak 的可及性向量是否沿图边保持一致。图上自相关高的 peak 被排在前面，作为 spatially variable（SV）peaks；同一图还被用于数据平滑、peak modules 和 gene–peak association。

它不是逐 peak 拟合空间概率分布，也不直接输出显著性检验。默认做法是按 importance score 排名并截取前 10,000 个 peak。论文说可以进一步对分数拟合分布取得 p 值，但固定代码没有提供统一的分布、p 值和多重检验实现。

### 为什么 spATAC 需要两种邻域

spATAC peak-by-spot 矩阵比空间 RNA 更稀疏。只看物理近邻时，同一组织域中的两个 spot 也可能因 dropout 显得完全不同；只看 ATAC 相似度时，又可能把空间上相距很远、但细胞类型相近的 spot 连在一起。Descart 将两者组合：空间图提供组织连续性，ATAC 图提供细胞状态相似性。

因此 Descart 的“空间变异”不是纯粹的地理 autocorrelation，而是相对于融合图的相关性。高分 peak 同时受到空间结构和表观状态驱动；若目标是区分“纯空间位置效应”和“细胞类型组成效应”，需额外分析两个单图版本或加入协变量。

### 输入和输出

核心 CLI 接收 AnnData `.h5ad`：`.X` 是 spot-by-peak 稀疏计数，`.obsm['spatial']` 是 $N\times2$ 坐标。先删除零 peak 和零 feature cell。输出包括选中 peak 的索引、完整排序/score、融合图以及 ATAC/空间子图；CLI 主要写 `result_idx.csv` 和运行时间/峰值内存。

默认参数是：输出 10,000 peaks、PCA 候选 50,000 peaks、10 PCs、ATAC KNN 的 $k=20$、空间半径倍数 5、四次迭代、空间混合比例 $r=0.4$。

### 第一步：TF–IDF 让稀疏计数可比较

设 $Y\in\mathbb{R}^{M\times N}$ 是 peak-by-spot 计数。默认 `tfidf2` 先按 spot 总 fragments 计算 term frequency，再按 peak 被观测的总体程度计算 inverse-document-frequency，并使用

$$\hat Y_{ij}=\log\left(1+10^4\frac{Y_{ij}}{\sum_kY_{kj}}\frac{N}{\sum_jY_{ij}}\right).$$

这与 Signac 风格的 TF–IDF 目标一致：普遍开放 peak 权重下降，较稀有但有区分度的 peak 权重上升。源码一开始将 sparse matrix 转为 dense，再进行后续 PCA 和矩阵乘法；所以输入虽然是稀疏的，核心内存复杂度并未保持稀疏。

### 第二步：构建空间图

论文定义每个 spot 最近邻距离的均值

$$d_s=\frac1N\sum_i\min_{j\ne i}\mathrm{Dist}(x_i,x_j),$$

并在 $5d_s$ 内连接 spot，边权为

$$w_{ij}^{spatial}=\frac{d_s}{\mathrm{Dist}(x_i,x_j)}.$$

宽于最近邻的一圈空间邻域相当于低通滤波：允许稀疏 accessibility 在一个局部范围内共享证据。

当前源码有一个重要差异：`utils.py:845` 使用整个非对角距离矩阵的最小值 `np.min(distance_matrix_spatial)`，而不是逐 spot 最近邻距离再取均值。规则网格中两者通常相同；非规则或单细胞坐标中，一个异常近点对会把所有阈值缩小。因此论文公式是 intended method，当前固定实现是 global-min approximation，必须标为 Partial。

### 第三步：构建 ATAC 图

初次迭代按 raw accessibility degree 选 50,000 peaks；后续迭代改用上轮 score 最高的 50,000 peaks。对这些 peak 的 TF–IDF 矩阵做 10-component PCA，计算 spot 间 cosine similarity，并为每行仅保留 top-20 邻居：

$$w_{ij}^{ATAC}=\begin{cases}cos(p_i,p_j),&j\in\mathrm{TopK}(i),\\0,&\text{otherwise}.\end{cases}$$

代码把对角设为负无穷后排序，清除非 top-k 项。top-k 是逐行选择，因此 ATAC 图一般是有向/非对称的：$j$ 是 $i$ 的邻居不保证反向成立。负 cosine 若进入 top-k 也未默认截成零，虽可通过 `cosine_filter` 过滤。

### 第四步：融合图的参数其实怎样对应

论文写成

$$W=W^{spatial}+\alpha W^{ATAC},\qquad\alpha=1.5.$$

代码写成

$$W=rW^{spatial}+(1-r)W^{ATAC},\qquad r=0.4.$$

代入默认值得

$$0.4W^{spatial}+0.6W^{ATAC}=0.4\left(W^{spatial}+1.5W^{ATAC}\right).$$

所以二者只差全局正比例常数。对同一次图构建而言，所有 peak score 同乘 0.4，排序完全相同；不能把它描述成实质公式冲突。只有当使用绝对 score 阈值、跨不同 $r$ 比较未归一化分数或把图用于其他尺度敏感计算时，全局尺度才可能影响解释。

### 第五步：importance score 是融合图上的二次型

对每个 peak 跨 spot 做 z-score，记向量为 $\tilde y_k$。分数是

$$s_k=\tilde y_kW\tilde y_k^T.$$

若一条高权重边连接的两个 spot 对该 peak 同为高/同为低，乘积为正；若一高一低则为负。所有 peak 一次向量化计算：代码用 `W @ X_processed`，再与 `X_processed` 逐元素乘并按 spot 求和，这与取 $\mathrm{diag}(\tilde YW\tilde Y^T)$ 等价，前提只是矩阵方向一致。

该分数与 Moran's I 有相似直觉，但没有 Moran's I 的行标准化与统一归一因子，且 $W$ 融合了 ATAC 邻域。因此 score 大小依赖图密度、边权尺度、spot 数和 peak variance，不宜把不同数据集的原始数值直接比较。

### 第六步：四轮反馈

第一轮用 highest-degree peaks 构建 PCA/ATAC 图，得到所有 peaks 的 score；第二轮起用上轮排名最高的 50,000 peaks 重建 PCA 和 ATAC 图，再融合并重排。默认四轮，没有基于 ranking overlap 的程序化停止条件。论文 Supplementary Fig. S14 展示 successive top-peak overlap 在四轮附近稳定，因此四轮是经验默认而非数学收敛保证。

这种反馈可让初步 SV peaks 改善 embedding，但也可能自我强化初始偏差。若高 accessibility peaks 主要反映测序深度或批次，第一轮图可能把该信号传到后续；TF–IDF、z-score 与空间图缓解但不消除这一风险。

### 图 1：主方法图从左到右怎样读

图 1上半部显示空间坐标生成 $W^{spatial}$，peak-by-cell 矩阵生成 $W^{ATAC}$；两图融合为 inter-cellular correlation graph。对一个 peak，蓝/橙 accessibility 是否在图的局部团块内一致决定 importance score。回箭头表示排名更新 ATAC graph。

下半部不是四个独立模型，而是同一图的四种用途：SV ranking、imputation、peak-module clustering 和 gene–peak interaction。主干核心代码直接完成 SV ranking；其余三项主要由 notebook 演示，软件成熟度不同。

### 图 2–3：多切片 benchmark 的阅读边界

论文在 mouse brain、mixed-species、mouse embryo 等 16 slices 上要求每种方法选相同数量的 peaks，再做 downstream clustering。带标签数据用 NMI/ARI/AMI 与 domain-specific peak overlap（OP1–OP3）；无标签数据用 CHAOS、LISI 和 PAS 评价空间连续性。各指标 min–max 后汇总，因此“overall score”是相对 benchmark score，不是单一生物学量。

Descart 在 mouse brain 的聚类、domain signal 与运行时间综合较好；SpatialDE/SOMDE 等更慢，部分方法在大矩阵上超时或内存失败。公平性边界包括：所有方法被迫选 10,000 features；下游 cluster 数通过搜索匹配标签数量；domain-specific peaks 本身由 epiScanpy/Signac/snapATAC2 等方法定义，不是无偏真值。

### 图 4：单细胞 melanoma 说明什么

图 4将 Descart 用于单细胞分辨率 metastatic melanoma。上部汇总 clustering 和 cell-type-specific signal，下面热图比较各方法 peaks 与 T cell、myeloid、tumor 等类型的重叠；空间图与 UMAP 图展示排名信号。Descart 保持较好综合表现，但单细胞类型在组织中可相互重叠，纯空间方法的优势不像规则组织域那样稳定。

这也放大了 `d_s` 实现差异：非规则单细胞坐标中全局最小距离更可能受局部密集点影响，复现论文 intended radius 时应检查/修正为 mean nearest-neighbor distance。

### 图 5–6：下游应用

数据 imputation 比较 ATAC-only、spatial-only、fused graph 以及加回原始矩阵的版本；论文在 E13.5-S1 以 clustering NMI 和 meta-spot correlation 评估平滑收益。平滑改善局部 signal 也可能跨真实边界传播，不能把 imputed 值视为直接观测。

peak modules 使用

$$S^{peak-peak}=\tilde Y\frac{W+W^T}{2}\tilde Y^T$$

再做 percentile 变换和 Ward clustering。当前 `peak_modules_()` 却把 `X^T W X` 相同项加了两次，并未直接计算 $W^T$；99.5th-percentile 距离变换主要在 notebook。这是 Partial/Notebook 边界，尤其因 ATAC KNN 图通常非对称，不能假设两式自然相同。

gene–peak association 将标准化 RNA 与 ATAC features 堆叠，用同一图计算 feature–feature 二次型。该值是图加权共变/相似度，不是染色质 peak 调控 gene 的因果证据。论文用 Hi-C overlap 提供部分验证，但方向性和直接调控仍需额外实验。

### 论文与本地实现的 Exact / Partial / Notebook

Exact 的主链包括：TF–IDF、50k peak 初始化/反馈、10-PC PCA、top-20 cosine graph、图融合默认权重、z-score 二次型 score、四轮迭代和 top-N 输出。固定代码 commit 为 `87c81ac0780006c8b05b3fc865143e576a2ae6b6`。

Partial 包括：论文 mean-nearest-neighbor $d_s$ 对代码 global minimum；ATAC KNN 有向且可保留负 similarity；score 无显著性模型；peak-module helper 未实现显式 symmetrization。论文 additive $\alpha=1.5$ 与代码 convex $r=0.4$ 在默认值下仅差整体尺度，应标作等价参数化而非 mismatch。

Notebook-only 包括：四种 imputation case、peak distance 的 99.5 percentile 处理、完整 gene–peak matrix 处理和大部分论文作图。核心仓库没有统一 pipeline 重跑所有 baseline；`knn_graph.o` 是 Linux 预编译评估二进制，缺少源码/构建说明。

### 最重要的限制

1. 核心持有多个 dense $N\times N$ 图，时间和内存约 $O(N^2)$，大规模单细胞空间数据会迅速受限。
2. 迭代固定四轮，没有数据驱动停止规则。
3. top-N 是人为选择；score 不是现成 p 值，也没有默认 FDR。
4. 高分可来自细胞类型与空间位置共同作用，不能自动区分二者。
5. 图平滑可能模糊真实锐利边界或稀有状态。
6. 坐标尺度、异常近点和不同切片单位会影响空间图，尤其当前 global-min 实现。
7. gene–peak 和 peak-module 结果是关联假设，需要 motif、Hi-C、扰动或独立样本验证。

### 直接证据入口

- 论文：`paper source/PMC11686967/paper.md`
- 主图：`paper source/PMC11686967/images/13059_2024_3458_Fig1_HTML.jpg` 至 `Fig6_HTML.jpg`
- 补充 PDF：`paper source/PMC11686967/13059_2024_3458_MOESM1_ESM.pdf`
- 核心实现：`Descart/code/descart.py` 与 `Descart/code/utils.py`
- 下游流程：`Descart/code/*.ipynb`
- 细粒度映射：`doc_code.md`；图解：`figure_analysis.md`

本解释以 PMC 正文、六张主图、补充 PDF 和固定代码快照为证据边界。未在核心脚本定位到的 benchmark orchestration 与 notebook 参数不会被补写成核心 API。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Descart — Summary

### Motivation & Novelty

**Biological problem**: Spatial ATAC-seq (spATAC-seq) captures both chromatin accessibility and tissue location simultaneously, enabling spatially resolved epigenomics. A fundamental first step is identifying *spatially variable (SV) peaks* — genomic regions whose chromatin accessibility differs meaningfully across tissue regions and cell types. Without reliable SV peak selection, all downstream analyses (cell clustering, trajectory, gene regulation) are compromised.

**Why existing approaches fall short**:

| Method type | Representative methods | Limitation for spATAC-seq |
|---|---|---|
| spRNA-seq SV methods | SpatialDE (*Nat Methods* 2018), SPARK-X (*Genome Biol* 2021), SOMDE (*Bioinformatics* 2021), Moran's I (via Squidpy, *Nat Methods* 2022), scGCO (*Nat Commun* 2022), Sepal (*Bioinformatics* 2021) | Assume (near-)continuous values; spATAC-seq is far sparser; inappropriate distributional assumptions |
| scATAC-seq feature selection | HDA (Cistrome, *Nat Mach Intell* 2022; RA3, *Nat Commun* 2021; etc.), Cofea (*Nat Commun* 2021), Signac (*Nat Methods* 2021), epiScanpy (*Nat Commun* 2021) | Ignore spatial information entirely |
| spRNA-seq + scATAC hybrid | None existed | Gap: no method jointly models spatial location AND chromatin accessibility |

Additionally, M=500k peaks × N spots datasets make per-feature modeling (as done by SpatialDE, SPARK) computationally infeasible (hours to days), while simpler methods run in seconds but discard spatial structure.

**Descart's unique contributions**:
1. First method specifically designed for SV peak identification from spATAC-seq data
2. Dual-graph fusion: spatial proximity + epigenomic neighborhood → graph of inter-cellular correlations
3. Iterative feedback: peak importance scores refine the PCA embedding for the next graph construction cycle
4. Single unified framework for four spATAC-seq analysis tasks: SV peaks, imputation, peak modules, gene-peak interactions
5. Competitive efficiency: fewer than 20 matrix operations total; 2-10× faster than other spatial methods

---

### Method Overview

Descart builds a fused graph of inter-cellular correlations, then evaluates each peak by how consistently it is co-accessible among neighboring spots in that graph.

**Five-step pipeline**:

1. **Spatial graph** $W^{(spatial)}$: The paper connects spots within 5× mean nearest-neighbor distance ($d_s$); code instead uses the global minimum pairwise distance. Edge weights are $d_s/\text{distance}$.

2. **ATAC-seq graph** $W^{(ATAC)}$: Apply Signac-style TF-IDF → PCA (50k peaks, 10 PCs) → cosine similarity → KNN (k=20). Captures epigenomic cell neighborhood.

3. **Fused graph** $W = (1-r) W^{(ATAC)} + r W^{(spatial)}$, r=0.4. At defaults this is a global 0.4 rescaling of the paper notation $W^{(spatial)}+1.5W^{(ATAC)}$, so rankings agree.

4. **Importance score**: Z-score all peaks, then $\mathbf{s} = \text{diag}(\tilde{Y} W \tilde{Y}^T)$. High score = peak's accessibility profile aligns with the inter-cellular neighborhood structure.

5. **Iterative refinement**: Updated peak rankings improve the PCA embedding for the next cycle; converges in 4 iterations.

**Downstream extensions** (all using the same graph):
- *Imputation*: $\tilde{Y}^{(enhanced)} = \text{Scale}(\tilde{Y} \cdot W)$
- *Peak modules*: Peak-peak similarity matrix → Ward hierarchical clustering
- *Gene-peak interactions*: Apply same formula to combined RNA + ATAC matrix

---

### Evaluation

#### Datasets

| Dataset | Slices | Resolution | Labels | Source |
|---|---|---|---|---|
| Mouse brain | 4 (E11.0–E18.5) | Spot-level | Manual anatomical (11 domains) | Nat Methods 2023, OEP003285 |
| Mixed-species A | 4 | Spot-level | Clustering labels from original study | Nature 2023, GSE205055 |
| Mouse embryo | 6 (E12.5–E15.5) | Spot-level | None (spatial continuity metrics) | Nat Biotechnol 2023, GSE214991 |
| Mixed-species B | 5 | Spot-level | None | Nature 2022, GSE171943 |
| Metastatic melanoma | 1 | Single-cell | Cell type labels (9 types) | Nature 2024, GSE244355 |

Total: 16 slices from 4 datasets used in comprehensive benchmark.

#### Metrics

**For labeled datasets**: NMI, ARI, AMI (clustering against ground-truth domains); OP1/OP2/OP3 (overlap proportion of SV peaks with domain-specific peaks from epiScanpy/Signac/snapATAC2).

**For unlabeled datasets**: CHAOS (spatial compactness), LISI (local inverse Simpson index), PAS (percentage of abnormal spots). Lower = more spatially continuous clusters.

**Evaluation design**: All methods select exactly 10,000 SV peaks. Downstream clustering uses Signac Leiden with binary search to match ground-truth cluster count. Min-max scaling per metric then averaging per perspective.

#### Comparative Results

**Mouse brain dataset (NMI, 4 slices)**:
- Descart: highest overall score; best in both clustering and domain-specific signal metrics
- SOMDE: 2nd in clustering but 10× slower; fails on larger datasets (>24h)
- SpatialDE: 2nd in some unlabeled metrics but requires ≥10h (100× slower)
- HDA, epiScanpy, Signac: faster than Descart but ignore spatial info → lower domain-specific signal
- SPARK/SpatialDE2: memory overflow on even the smallest dataset

**Efficiency** (mouse brain): Descart runs in <1 min. Next-fastest comparable method: ~2-5 min. SOMDE: ~15 min. SpatialDE: >10 h.

**Melanoma (single-cell resolution)**: Descart maintains advantages in cell type-specific signals; spatial methods don't dominate as strongly because cell type spatial distributions overlap.

**Ablation findings**:
- α=1.5 (r=0.4) outperforms ATAC-only or spatial-only variants
- ATAC-only > spatial-only for spATAC-seq (discrete spatial patterns make spatial-only noisy)
- 4 iterations optimal; diminishing returns beyond 4
- 5×$d_s$ neighborhood superior to smaller (3×, 2×) or larger (7×) thresholds

**Imputation** (E13_5-S1): Cases 3 and 4 (fused graph) improve NMI by ~0.05-0.10 over raw; higher Pearson correlation with meta-spot signals across all domains.

**Gene-peak interaction** (E13_5-S1): Descart outperforms UnitedNet, Polarbear, epiScanpy, Seurat in cosine similarity for RNA→ATAC translation; second to UnitedNet for ATAC→RNA.

---

### Reproducibility

**Rating: 3/5**

**Justification**:
- Core algorithm (SV peaks) is fully reproducible: single Python file, clear dependencies, CLI entry point
- Four tutorial notebooks demonstrate all four downstream applications with pre-computed data
- Pre-computed benchmark results provided in `result/mouse_brain/`
- Sample dataset available at Tsinghua Cloud link

**Limitations**:
- Downstream applications (peak modules, gene-peak interactions, imputation nuances) live in notebooks only, not modular library
- Tsinghua Cloud link for sample data may become inaccessible; no Zenodo DOI for data
- `knn_graph.o` binary for LISI metric is pre-compiled for Linux only; no build instructions
- Python 3.8 + scanpy==1.9.6 (pinned, not latest); may conflict with newer environments
- The `decare` PyPI package is mentioned in README but not in requirements.txt; its relation to the repository code is not documented

**Environment setup**:
```bash
conda create -n Descart python=3.8
conda activate Descart
pip install -r requirements.txt
# Run:
cd code/
python descart.py -fp ../data/scanpy.h5ad -sp ../result -n 10000 -sb 1 -pc 10 -k 20 -iter 4 -nb 5 -r 0.4
```

**Common pitfalls**:
- Must provide `obsm['spatial']` in input AnnData — code will fail silently if missing
- All intermediate matrices are dense; for N>8,000 spots may exceed 16GB RAM
- `knn_graph.o` must be in `./code/` working directory for LISI evaluation
- The `-r` parameter (default 0.4) corresponds to α≈1.5 in paper; these are different parameterizations

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
