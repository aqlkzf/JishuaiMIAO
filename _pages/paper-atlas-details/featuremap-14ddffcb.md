---
layout: default
permalink: /paper-atlas/featuremap-14ddffcb/
title: "FeatureMAP"
nav: false
wide: true
description: "FeatureMAP 不只问“哪些细胞彼此接近”，还在每个细胞邻域估计一个局部切空间，记录基因沿局部流形方向如何变化。它把这些信息拆成两个互补的二维图：GEX 保留细胞密度和聚类结构，GVA 保留基因变化模式和轨迹结构；随后用密度、曲率和介数中心性区分稳定核心态与过渡态，并用差异基因变化分析寻找可能驱动状态转换的基因。"
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
      <span>Representation Models</span>
      <span>Nature Computational Science · 2026</span>
    </div>
    <h1>FeatureMAP</h1>
    <p>Feature-preserving manifold approximation and projection to analyze single-cell data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s43588-026-00970-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for FeatureMAP">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/YYT1002/FeatureMAP" target="_blank" rel="noopener noreferrer" aria-label="Open code for FeatureMAP">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## FeatureMAP：把基因变化方向保留在单细胞降维图里

### 一句话理解

FeatureMAP 不只问“哪些细胞彼此接近”，还在每个细胞邻域估计一个局部切空间，记录基因沿局部流形方向如何变化。它把这些信息拆成两个互补的二维图：GEX 保留细胞密度和聚类结构，GVA 保留基因变化模式和轨迹结构；随后用密度、曲率和介数中心性区分稳定核心态与过渡态，并用差异基因变化分析寻找可能驱动状态转换的基因。

### 1. 为什么普通 UMAP 不够

UMAP、t-SNE 很适合显示细胞簇，但二维坐标本身不再直接说明某个基因对局部方向贡献了多少。PCA biplot 可以同时显示样本和载荷，却只适合全局线性结构。FeatureMAP 的思路是：如果高维单细胞数据近似落在一个低维流形上，就在每个细胞附近做一次局部 PCA，把许多局部线性坐标系拼成整张流形的方向信息。

这里必须区分三个量：

- 基因表达是细胞在转录状态空间中的“位置”；
- 局部方差只描述邻域中的无方向散布；
- FeatureMAP 的基因变化量描述基因在局部主方向上的载荷大小，即沿流形方向变化有多强。

因此，FeatureMAP 的“variation”不是 RNA velocity，也不使用剪接/未剪接计数和动力学方程；它是由表达矩阵的局部几何估计出的方向性变化指标。

### 2. 从 kNN 邻域得到局部切空间

对细胞 $x_i$，先构建 UMAP 式加权 kNN 图。把邻居减去中心细胞并按图权重加权，得到局部矩阵 $\hat X_i$，再做

$$
\hat X_i=U_i\Sigma_iV_i^\top.
$$

$V_i$ 的前 $d$ 个右奇异向量近似细胞 $x_i$ 处的切空间基；奇异值描述各局部方向上的尺度。对基因 $f_j$，论文定义其局部 feature variation 为

$$
\lVert f_j\rVert_i=
\left(\sum_{l=1}^{d}|v_{ilj}|^2\right)^{1/2}.
$$

从左到右读：取前 $d$ 个局部主方向中基因 $j$ 的载荷，平方、求和、开根号。数值越大，说明该基因更强地参与细胞附近的主要变化方向。

一个小例子：若某基因在两个局部主方向上的载荷为 $0.6$ 和 $0.8$，变化量为 $\sqrt{0.6^2+0.8^2}=1$；若另一个基因为 $0.1$ 和 $0.2$，则约为 $0.224$。前者在该细胞附近的流形变化中贡献更大，但这本身不证明它具有因果调控作用。

代码对应为 `featuremap_.py::local_svd` 和 `_compute_variation_pc`。当前代码先以累计解释能量阈值估计局部内在维数，再取全体细胞局部维数的中位数作为统一 $d$。

### 3. 为什么需要 GEX 和 GVA 两张图

论文强调两类信息在二维空间中难以同时完整保留：

- 局部密度依赖奇异值给出的标量半径；
- 变化轨迹依赖奇异向量给出的方向对齐。

所以 FeatureMAP 不是输出一张“万能图”，而是输出两张配套图。

#### GEX：保留表达拓扑和各向异性密度

GEX 在 UMAP 交叉熵损失上加入各向异性密度保持项：

$$
\mathcal L_{\mathrm{GEX}}
=\mathrm{CE}(P\Vert Q)-\lambda\,\mathrm{Corr}(r^o,r^e).
$$

$P$、$Q$ 分别表示原空间和嵌入空间的邻接概率；$r^o$ 是原空间各局部主方向的对数半径，$r^e$ 是二维嵌入在对应局部方向上的对数半径。相关性越高，二维图越能反映原始邻域是紧密还是稀疏、以及在哪个方向上拉长。论文使用 $\lambda=0.5$，只在最后 $q=0.3$ 比例的优化迭代中加入该项。

图 2 的合成数据中，GEX 的局部半径相关 $R^2=0.660$，UMAP 为 $0.003$。这支持密度保持能力，但不是所有数据上都必然达到该差距。

#### GVA：按基因变化谱组织轨迹

每个细胞都有一个基因变化向量

$$
v_i^f=[\lVert f_1\rVert_i,\ldots,\lVert f_n\rVert_i].
$$

GVA 把这些向量作为新输入，用余弦距离运行 UMAP。于是基因变化模式相似的细胞靠近，常形成论文所称的“结—线”结构：稳定状态是结，过渡细胞沿线连接不同状态。补充图 9 还把它与简单的局部标量方差输入比较；后者不能同样恢复连贯轨迹，说明 GVA 不只是把表达换成任意方差矩阵。

### 4. 基因贡献箭头如何产生

FeatureMAP 还把高维局部载荷投到二维切空间框架。箭头长度表示局部 feature variation 的大小，方向表示该基因在嵌入中的变化方向。这样可以在 GEX 图上查看某个基因从哪里开始起作用、沿哪条分支增强。

需要注意，箭头是局部几何投影，不是带时间单位的速度，也不自动给出调控因果方向。论文在合成 GRN 中用已知真值验证：$g_4$ 的贡献在分叉前出现，而下游 $g_6$ 在分叉后增强，这才为“较早驱动者”解释提供额外证据。

代码中，`features.py::feature_variation` 把平滑后的切空间经全局 SVD 基映射回基因空间；`feature_projection` 再把指定基因载荷投到二维局部框架。调用顺序很重要：必须先完成 FeatureMAP 拟合和 variation 计算，相关中间矩阵才存在。

### 5. 核心态和过渡态

论文联合三种拓扑量：

- 密度：高密度为核心候选，低密度为过渡候选；
- 曲率：低曲率为核心候选，高曲率为过渡候选；
- 介数中心性：低介数为核心候选，高介数为过渡候选。

默认以 0.8/0.2 分位数取两端，再在 GVA 上做 Leiden 聚类，依据簇内核心/过渡候选的多数比例给簇贴共识标签。这里的标签是算法定义的几何状态，不应直接等同于已被实验验证的生物细胞状态。

论文把曲率写成切向量随路径变化的微分几何量；当前 `core_transition_states.py::compute_curvature` 实际使用 variation-PC 空间中的局部 kNN 距离代理。因此这部分论文—代码匹配是 **Partial**，不能把代码输出描述成严格求得论文公式中的连续曲率。密度、介数分位阈值和 Leiden 汇总则有直接代码对应。

### 6. DGV 与 DGE 的区别

DGE 在表达矩阵上比较簇间平均表达；DGV 在基因变化矩阵上比较相邻过渡态和核心态。发布工作流通过 Scanpy `rank_genes_groups` 做统计排序：

- DGE 找“哪个基因在两个状态的平均表达不同”；
- DGV 找“哪个基因的局部方向性变化在过渡区更强”。

在合成分叉数据里，DGE 更偏向表达变化大的下游基因 $g_6$，DGV 把真值调控因子 $g_4$ 排得更高。胰腺数据中，DGV 找到 alpha 和 beta 分支相关的 Arx、Pdx1；两个独立 CD8 T 细胞数据中都识别出 Exh-KLR 相关的 Zeb2。

但 DGV 的“潜在调控因子”仍是候选生成，不是单凭统计比较得到的因果证明。当前代码 `features.py::variation_feature_pp` 还包含归一化和过滤步骤，论文方法部分没有完整枚举这些实现阈值，因此 DGV 代码匹配应标为 **Partial**。

### 7. 当前代码真正执行的完整路径

1. `_preprocess_data`：高维输入先做全局截断 SVD；若样本少于 1000，当前代码还会生成高斯样本补足规模。这些是发布代码的额外预处理。
2. `FeatureMAP.fit`：构建 fuzzy kNN 图并保存邻居索引与权重。
3. `tangent_space_approximation`：对每个细胞做加权局部 SVD，得到奇异值和局部框架。
4. `graph_convolution`：在 kNN 图上迭代平均切空间框架，并可用 Procrustes 对齐和变化量收敛准则提前停止。
5. `variation_embedding`：从平滑框架计算 variation matrix，用余弦 UMAP 得到 GVA。
6. `tangent_space_embedding`：把切空间方向嵌入二维，形成基因投影所需的局部坐标框架。
7. GEX 优化：从嵌入初始化开始，先优化 UMAP 拓扑，后段加入各向异性半径相关项。
8. `features.py`：把变化量映射回基因空间，生成基因变化分数和贡献箭头。
9. `core_transition_states.py`：计算密度、曲率代理、介数中心性和 Leiden 共识标签。
10. `variation_feature_pp` 加 `rank_genes_groups`：在变化矩阵上完成 DGV。

其中第 1、4 步以及 GEX 默认从 variation embedding 初始化，是当前代码的重要实现扩展，在论文主算法叙述中没有同等程度展开。正式的切空间成对分布和并行移动公式在代码里则被余弦 UMAP与图平滑近似，整体匹配应写成 **High but mixed Exact/Partial**，不是逐公式完全复现。

### 8. 图证据如何串起方法

- 图 1 展示 kNN、局部切空间、GEX/GVA 双分支和基因投影，是理解方法输入输出的总图。
- 图 2 用已知 GRN 的分叉数据验证密度保持、轨迹和 DGV；$g_4$ 与 $g_6$ 的顺序提供真值核对。
- 图 3 在胰腺发育中显示 Fev+ 向 alpha/beta 分支，并以 Arx、Pdx1 作为生物学一致性证据。
- 图 4 在慢性感染 CD8 T 细胞中追踪 Exh-Int 到 Exh-KLR，并在独立数据中重复找到 Zeb2。
- 图 5 从 DGV 候选得到 Klra9/Gzma 标记组合；流式实验显示 KLRA9+ 过渡群在第 21 天达到峰值，早于第 28 天 Exh-KLR 核心群上升。这是针对该具体过渡群的实验验证，不代表所有 FeatureMAP 几何过渡态都已验证。
- 图 6 与扩展图 8–10 比较状态分离、基因贡献和伪时间；补充图 1–17补充密度、超参数、原始 MNIST 形态、方法比较、局部维数和流式 gating。

本次直接查看了主图关键面板及其图注，并阅读了 `supp1.md` 的补充说明与算法。`supp2.pdf` 没有对应的 Markdown 转换，因此没有据此新增无法核验的内容。

### 9. 使用与解释边界

- 输入通常应是适当预处理的单细胞表达表示；结果会受 kNN 数、PC 数、内在维数和 GVA `min_dist` 影响。
- 论文实践值为 `n_neighbors=15`、`min_dist=0.3`，当前类构造器默认值并不完全相同；复现实验时应显式设置参数。
- 局部 PCA 假设邻域近似线性；稀疏采样、高曲率和区域内在维数变化会使载荷不稳定。
- DGV 衡量变化强度而非变化正负方向，且不取代 DGE、扰动实验或时间序列验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## FeatureMAP Summary

### Citation

Yang, Y., Gong, J., Sun, H., et al. Feature-preserving manifold approximation and projection to analyze single-cell data. *Nature Computational Science* (2026). https://doi.org/10.1038/s43588-026-00970-6

---

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing generates high-dimensional transcriptomic data across thousands of cells. Standard visualization methods are essential for understanding cell identity and developmental trajectories. However, existing tools trade off biological interpretability for structural clarity.

#### Why Existing Methods Fall Short

- **UMAP** (*J. Open Source Software*, 2018): Excellent cluster structure but loses gene-level information in embedding. No way to read off which genes drive the visualization.
- **t-SNE** (*JMLR*, 2008; *Nature Communications*, 2019): Similarly opaque — good clustering, no feature interpretability.
- **densMAP** (*Nature Biotechnology*, 2021): Extends UMAP to preserve local density, but still isotropic (spherical neighborhoods) and gene-blind.
- **PHATE** (*Nature Biotechnology*, 2019): Preserves local and global nonlinear structure but lacks gene-level visualization.
- **RNA velocity** (*Nature*, 2018; scVelo: *Nature Biotechnology*, 2020): Captures transcriptional dynamics but requires unspliced/spliced counts and cannot directly project arbitrary gene contributions.
- **Monocle** (*Nature Methods*, 2017; *Nature*, 2019): Trajectory inference but no direct visualization of what genes drive trajectories.

None of these methods retain the principal directions (tangent spaces) that tell you which genes are changing directionally across the manifold.

#### Unique Contributions

1. **Feature-preserving dual embedding**: First method to co-embed cells AND gene variation vectors in the same 2D space, without requiring a separate post-hoc analysis pipeline.

2. **GEX + GVA complementary embeddings**: GEX (preserves density, for clusters) and GVA (preserves directional gene change, for trajectories) are mathematically orthogonal — density depends on scalar radii (singular values), trajectories on vector alignment (singular vectors). Both cannot be captured in one embedding, motivating the dual design.

3. **Core/transition state classification**: Principled, geometry-aware classification using density + curvature + betweenness centrality. Previous methods define core states statistically (e.g., MuTrans [*Nature Communications*, 2021], Mellon [*Nature Methods*, 2024]) but do not directly visualize them in a feature-aware embedding.

4. **DGV analysis**: Differential gene *variation* (not expression) between transition and core states. Identifies regulatory genes that are dynamically changing during state transitions, even if their mean expression doesn't differ significantly. Complementary to DGE.

5. **Experimental validation of transition states**: Computationally-predicted Klra9⁺ transition cells in the Exh-Int → Exh-KLR trajectory were validated in vivo by flow cytometry — rare experimental confirmation of a computationally-defined transient population.

---

### Method Overview

FeatureMAP builds on UMAP's kNN graph topology but adds a *tangent space* layer: at each cell, local PCA (via weighted SVD) identifies the principal directions of transcriptional variation. These tangent spaces are (1) smoothed via graph convolution (undocumented in paper), (2) used to compute per-gene variation scores, and (3) embedded to define local coordinate frames for feature projection.

Two embeddings are produced:
- **GEX**: Optimizes UMAP's cross-entropy loss + anisotropic density correlation (extending densMAP to ellipsoidal neighborhoods). λ=0.5 balances topology vs. density.
- **GVA**: UMAP with cosine distance on the feature variation matrix. Trajectories emerge from clustering cells with similar directional gene change profiles.

Core/transition states are defined by three topological metrics (density, curvature, betweenness centrality) with 80th/20th percentile thresholds, refined by Leiden clustering. DGV analysis then identifies regulatory genes by comparing variation scores between transition and core clusters using `rank_genes_groups` (Scanpy).

For detailed equations and code mapping, see `doc_method.md` and `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Cells | Application |
|---------|-------|-------------|
| Synthetic bifurcation (BoolODE) | ~5000 | GRN validation (ground truth known) |
| Mouse E15.5 pancreas (GSE132188) | ~3696 | Alpha/beta cell development |
| CD8+ T cell LCMV cl13, Giles et al. (GSE199565) | ~12000 | T cell exhaustion |
| CD8+ T cell LCMV cl13, Daniel et al. (GSE188670) | ~8000 | Independent validation |
| MNIST, Fashion-MNIST, COVID-19, Embryoid body, PBMC68k, Tabula Muris | Various | Benchmarking |

#### Key Results

| Metric | FeatureMAP GEX | UMAP | densMAP |
|--------|---------------|------|---------|
| Density R² (synthetic) | 0.660 | 0.003 | 0.660 |
| Density R² (pancreas) | 0.62 | 0.09 | 0.54 |
| Gene contribution visualization | ✓ (coherent biplot) | ✗ (scattered) | ✗ (scattered) |
| Pseudotime R² | >0.9 | N/A | N/A |
| Core/transition silhouette | highest | lower | lower |

**Key biological validations:**
- Synthetic: DGV correctly ranks g4 (true regulator) above g6 (downstream effector), while DGE incorrectly ranks g6 first (higher fold change)
- Pancreas: Arx (alpha lineage) and Pdx1 (beta lineage) recovered as top DGV genes, consistent with known biology
- CD8+ T cells: Zeb2 (validated Exh-KLR driver [*Nature Immunology*, 2022]) ranked top by DGV in both independent datasets
- Flow cytometry: Klra9⁺ transition-state cells (Exh-Int → Exh-KLR) experimentally detected and shown to peak at day 21, preceding Exh-KLR core-state rise by day 28

---

### Reproducibility

**Rating: 4/5** — Code is clean and installable; tutorials available; main results are reproducible with provided notebooks.

**Strengths:**
- GitHub: https://github.com/YYT1002/FeatureMAP (BSD-3 license)
- ReadTheDocs tutorials for synthetic and real datasets
- Zenodo archival: https://doi.org/10.5281/zenodo.17983246
- All scRNA-seq datasets publicly available (GEO accessions provided)
- Flow cytometry source data available in paper supplements

**Weaknesses / Caveats:**
- Critical parameters differ between paper and code defaults (paper: n_neighbors=15, min_dist=0.3; code: n_neighbors=30, min_dist=0.5) — use paper values for bioinformatics
- Graph convolution (the most important preprocessing step) is completely undocumented in paper; convergence can vary
- Global SVD preprocessing also undocumented — `svd_vh` matrix needed for `feature_variation` to project back to gene space
- Feature projection requires `feature_variation` to be run first; workflow not fully automated
- Curvature implementation diverges significantly from paper formulation (avg distance vs. differential geometry)
- DGV thresholds (20% zero-out) undocumented; may affect results for sparse data

**Environment:**
- Python, umap-learn, scanpy, networkx, leidenalg, numba
- `pip install featuremap` (after setup.py)
- Notebooks in `docs/notebook/` (test_pancreas.ipynb, test_cd8.ipynb, test_bifurcation_dgv.ipynb)

**Common pitfalls:**
1. Input should be PCA-reduced (30 PCs recommended for bioinformatics), not raw counts
2. Run `_preprocess_data` before fitting if n_genes > 100 (or rely on library's internal call)
3. `feature_variation()` requires `vh_smoothed` and `svd_vh` in adata — only available after full FeatureMAP fit
4. DGV needs `variation_feature_pp()` before `rank_genes_groups`
5. Core/transition state computation requires both GEX embedding (`X_featmap`) and GVA object

---

### Limitations

1. **Local linearity assumption**: Local PCA assumes manifold is locally flat. Breaks at high-curvature regions or with sparse sampling, leading to unreliable tangent estimates.

2. **Fixed intrinsic dimension**: One global $d$ applied everywhere. Datasets with regionally varying intrinsic dimension (quiescent vs. differentiating cells) may have inaccurate feature loadings.

3. **First-order only**: Feature variation captures directional change but not gene-gene covariance or combinatorial regulatory interactions.

4. **Scalability**: Local SVD + graph convolution scales approximately linearly, but memory scales with `m × 2k × n`. Challenging for cell atlases with millions of cells without approximation.

5. **Curvature proxy**: Code uses avg kNN distance in variation_pc space instead of proper differential geometry — interpretability of this metric as geometric curvature is approximate.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
