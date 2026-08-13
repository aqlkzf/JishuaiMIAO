---
layout: default
permalink: /paper-atlas/hotspot-c8f6f98b/
title: "Hotspot"
nav: false
wide: true
description: "Hotspot 不负责学习“什么叫细胞相似”。它接收一个已有的细胞—细胞相似性图，然后问两个问题：某个基因是否沿这张图呈现非随机的局部结构；两个基因是否在图的相同区域共同变化。第一个问题用于筛选信息基因，第二个问题用于把这些基因组织成模块。 这个分工解释了 Hotspot 为什么能跨模态使用。图可以来自转录组低维空间、组织中的物理坐标，也可以来自谱系树；被检验的量仍然可以是基因表达。"
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
      <span>Cell Systems · 2021</span>
    </div>
    <h1>Hotspot</h1>
    <p>Hotspot identifies informative gene modules across modalities of single-cell genomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cels.2021.04.005" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Hotspot">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yoseflab/hotspot" target="_blank" rel="noopener noreferrer" aria-label="Open code for Hotspot">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Hotspot：把任意细胞相似性图翻译成信息基因与基因模块

### 一句话抓住方法

Hotspot 不负责学习“什么叫细胞相似”。它接收一个已有的细胞—细胞相似性图，然后问两个问题：某个基因是否沿这张图呈现非随机的局部结构；两个基因是否在图的相同区域共同变化。第一个问题用于筛选信息基因，第二个问题用于把这些基因组织成模块。

这个分工解释了 Hotspot 为什么能跨模态使用。图可以来自转录组低维空间、组织中的物理坐标，也可以来自谱系树；被检验的量仍然可以是基因表达。因而“高分”的生物学含义取决于图：转录图上的高分表示表达跟随细胞状态，空间图上的高分表示表达跟随组织位置，谱系图上的高分表示表达在近亲细胞间更相似。

### 输入、输出与完整数据流

输入包括细胞×基因计数矩阵、每个细胞的总 UMI，以及一种能够构造近邻关系的表示：低维坐标、预计算距离或谱系树。核心输出依次是：

1. 每个基因的局部自相关统计量、Z 分数、P 值和 FDR；
2. 入选基因之间的局部相关 Z 分数矩阵；
3. 每个基因的模块标签；
4. 每个细胞的模块分数。

代码中的主调用链与论文三步法直接对应：

```text
Hotspot(...)
  -> create_knn_graph()
  -> compute_autocorrelations()
  -> compute_local_correlations(genes)
  -> create_modules()
  -> calculate_module_scores()
```

入口位于 `hotspot/hotspot/hotspot.py`。图构造在 `knn.py`，单基因统计在 `local_stats.py`，基因对统计在 `local_stats_pairs.py`，聚类与模块分数在 `modules.py`。

### 第一步：把“相似”压缩成稀疏图

设细胞为图节点，每个细胞只连接到 $K$ 个近邻。论文通常取 $K\approx30$，但具体分析可以改变；例如低深度 Slide-seq 空间特征选择使用了 300 个空间近邻，随后做模块时又降到 30 个近邻以获得更细的空间分辨率。

论文给出的加权形式是

$$
w_{ij}=\exp\left(-\frac{d_{ij}^{2}}{\sigma_i^{2}}\right),
$$

其中 $\sigma_i$ 是细胞 $i$ 到第 $K/3$ 个近邻的距离，再按行归一化使 $\sum_j w_{ij}=1$。也可以用无权图：若 $j$ 是 $i$ 的近邻，则 $w_{ij}=1$。

当前代码的 `Hotspot.create_knn_graph()` 支持三种来源：低维坐标、预计算距离和谱系树。`knn.py:compute_weights()` 实现高斯核；`knn.py:make_weights_non_redundant()` 把双向重复边合并，避免同一无向关系在统计量中重复计数。需要特别注意，当前 API 的 `weighted_graph=False` 是默认值，所以实际默认使用全 1 权重；若要使用论文描述的高斯权重，需要显式传入 `weighted_graph=True`。谱系树路径只允许均匀权重。

### 第二步：用局部自相关筛选信息基因

#### 2.1 统计量在测什么

对基因 $x$，令 $x_i$ 为细胞 $i$ 中经零模型标准化后的表达，Hotspot 定义

$$
H_x=\sum_{(i,j)\in E}w_{ij}x_i x_j.
$$

从左到右读：遍历图中的近邻边；比较边两端的标准化表达；相乘后按边权累加。若高表达细胞多连向高表达细胞、低表达细胞多连向低表达细胞，乘积多为正，$H_x$ 就大。若表达在图上随机散布，正负贡献趋于抵消。

例如三条等权边上的表达对分别为 $(2,1.5)$、$(1.5,1)$ 和 $(2,-1)$，贡献为 $3+1.5-2=2.5$。前两条边支持同一区域共同升高，第三条边跨越相反状态而削弱总分。

这与只看边际方差不同：一个基因即使检测稀疏，只要阳性细胞集中在图的同一区域，仍可能具有高局部自相关。

#### 2.2 零模型为什么重要

不同细胞测序深度不同，直接使用原始计数会把局部 UMI 深度结构误认成生物结构。Hotspot 先为每个基因、每个细胞估计 $E[x_i]$ 和 $\operatorname{Var}(x_i)$，再标准化：

$$
\hat{x}_i=\frac{x_i-E[x_i]}{\sqrt{\operatorname{Var}(x_i)}}.
$$

标准化后 $E[\hat{x}_i]=0$、$E[\hat{x}_i^2]=1$，于是

$$
Z_x=\frac{\sum_{(i,j)\in E}w_{ij}\hat{x}_i\hat{x}_j}
{\sqrt{\sum_{(i,j)\in E}w_{ij}^{2}}}.
$$

代码在 `local_stats.py:_compute_hs_inner()` 中拟合零模型、中心化、计算图上乘积和，再输出 `C`、`Z`、`Pval`、`FDR`。多基因检验用 Benjamini–Hochberg 校正。

Hotspot 提供两类关键零模型：

- 负二项模型（代码名 `danb`）：均值随细胞总 UMI 变化，适合常规 UMI 计数；
- Bernoulli 模型：只保留是否检测到表达，并让检测概率随总 UMI 变化，适合极稀疏数据。

论文的 Slide-seq 示例每个 barcode 的 UMI 中位数仅 45，因此使用 Bernoulli 模型。代码还包含 `normal` 和 `none` 路径，但它们不是论文主要实验所依赖的两种模型。

### 第三步：用局部相关连接基因对

对两个已入选基因 $x,y$，Hotspot 定义

$$
H_{xy}=\sum_{(i,j)\in E}w_{ij}
\left(\hat{x}_i\hat{y}_j+\hat{y}_i\hat{x}_j\right).
$$

它比较的是不同细胞之间的表达：表达 $x$ 的细胞是否邻近表达 $y$ 的细胞。Pearson 相关要求 $x$ 和 $y$ 在同一个细胞内同时被检测；局部相关允许它们因掉零而在相邻细胞中交替出现，因此对稀疏单细胞数据更敏感。

这里不能用“两个基因都完全独立”的朴素零模型，因为进入本步骤的基因已经具有局部自相关。论文改用条件零模型：先固定 $x$ 的观测值，只让 $y$ 随机；再固定 $y$，只让 $x$ 随机；最后保留绝对值更小、也就是更保守的 Z 分数。`hotspot.py:compute_local_correlations()` 调用 `local_stats_pairs.py:compute_hs_pairs_centered_cond()`，CPU 路径逐对计算，GPU 路径则用稠密矩阵乘法批量计算。

### 第四步：从基因对矩阵得到模块

局部相关 Z 分数形成一个基因×基因相似度矩阵。`modules.py:compute_modules()` 先将高 Z 分数转成低距离，再使用 UPGMA 平均连接层次聚类。两个约束决定何时形成和停止模块：

- `fdr_threshold` 把所有基因对的 Z 分数转为 P 值并做 BH 校正，得到最低显著 Z 阈值；
- `min_gene_threshold` 规定一个分支积累到多少基因后才成为有标签的模块。

为了保留层级结构，两个已有标签的大模块相遇时不会简单合成一个新模块；证据不足或规模不足的基因可保持 `-1` 未分配。

### 第五步：把模块投回每个细胞

模块标签描述“哪些基因属于一起”，模块分数则描述“该模块在哪些细胞活跃”。代码先按同一个零模型中心化模块基因，再用近邻图平滑；`modules.py:compute_scores()` 中平滑系数固定为 $\lambda=0.9$，即 90% 邻域信号与 10% 本细胞信号。随后对平滑后的模块表达做单成分 PCA，并在平均载荷为负时翻转符号，使高分方向对应整体较高表达。

这个 $\lambda=0.9$ 是直接代码证据中的实现细节，论文方法段只说明“按近邻加权平均后做单成分 PCA”，没有报告该常数。

### 如何读论文的图

#### Figure 1：方法不是在 UMAP 上做统计

图 1 从左到右展示“相似性来源 → KNN 图 → 单基因筛选 → 基因对 Z 矩阵 → 模块”。UMAP 式布局只是示意；真正参与计算的是图的边和权重。图中表达呈局部色块的基因通过筛选，随机散点式表达的基因被淘汰。

#### Figure 2：转录状态图上的 CD4 T 细胞程序

Hotspot 选出的基因具有更高的 T 细胞相关基因集评分；用这些基因建立的 scVI 表示，也能让未参与建模的表面蛋白呈现较强局部自相关。图 2D 的基因对 Z 矩阵显示 500 个入选基因被分为 12 个模块；图 2E 显示其模块划分在数据拆半后比比较方法更可重复，而且分配了更多基因。这里支持的是“图条件下的模块更稳定”，不是证明 Hotspot 学得了唯一真实的细胞类型。

#### Figure 3：空间图把组织结构转成表达模块

细胞相似性改由二维物理坐标定义。六个模块的空间分数重现小脑层状结构，且分别富集于 Purkinje 神经元、Bergmann 胶质、少突胶质等标记。需要保留论文内部的数字不一致：结果正文写 560 个显著空间自相关基因，而 Figure 3 图注写 845 个；本地材料没有提供可判定哪一个数字为最终版本的独立补充文件。

#### Figure 4：谱系相似与转录相似回答不同问题

在 1,756 个胚胎细胞中，谱系图得到 2,554 个显著基因并形成 5 个模块，分别联系到内胚层、原始血液、滋养层等程序。相反，angioblast/Pecam1 信号在转录相似图上明显、在谱系图上不明显。这个对照说明 Hotspot 不会自动整合不同模态；换一张图就是换一个生物学问题。

### 论文与代码的对应边界

本地 `hotspot/` 是论文声明的官方仓库，固定在提交 `f9855997b0a2e5edbfe8046747be88f556b5ba11`。核心统计与模块流程可以在源代码中直接定位，属于强 paper–code 对应。与此同时应注意：

- 论文写高斯权重为默认，当前提交的公开 API 默认 `weighted_graph=False`；
- 论文的方法图只画三步，代码还显式实现模块分数与 CPU/GPU 两条路径；
- 本地没有独立 supplementary Markdown；补充图号和补充分析仅能从嵌入的正文引用中导航，不能假装已检查缺失的补充文件。

### 实际使用时最容易误解的三点

1. 高局部自相关不等于“差异表达”。它表示表达与指定图一致；换图后含义也随之改变。
2. 高局部相关不等于同细胞 Pearson 相关。它刻画的是相邻细胞之间的基因共结构。
3. Hotspot 不学习相似性度量。低维表示、空间坐标或谱系树的质量与偏差会直接传递到基因排名和模块。

因此，最稳妥的解释方式是始终说清三件事：图由什么定义、采用什么零模型、哪些基因进入了基因对和模块步骤。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Hotspot Summary

**Paper**: Hotspot identifies informative gene modules across modalities of single-cell genomics
**Authors**: David DeTomaso, Nir Yosef
**Journal**: Cell Systems, 2021
**DOI**: 10.1016/j.cels.2021.04.005

---

### Motivation & Novelty

#### Biological Problem

Single-cell genomics generates high-dimensional expression profiles across thousands of cells. Two fundamental tasks arise: (1) identifying which genes vary in a biologically meaningful way (feature selection), and (2) grouping these genes into coordinated expression programs (module detection). These tasks are complicated by technical noise, dropout (undetected expressed genes), and the growing need to integrate multiple data modalities.

#### Limitations of Existing Approaches

- **Highly Variable Genes (HVG, Seurat v2, *Nat. Biotechnol.* 2015)**: Ranks genes by marginal overdispersion. Misses genes that are informative but not overdispersed — e.g., genes with clear spatial patterns but low variance.
- **NBDisp (M3Drop, *Bioinformatics* 2019)**: Similar marginal approach; same blind spot.
- **PCA-based selection (M3Drop, *Bioinformatics* 2019)**: Works for linear models but cannot interpret non-linear embeddings (scVI, Harmony, UMAP).
- **WGCNA (*BMC Bioinformatics* 2008)**: Uses Pearson correlation for module detection; unreliable at low sequencing depths due to dropout.
- **SpatialDE (*Nat. Methods* 2018)**: Gaussian process model for spatial data; accurate but requires O(N³) matrix inversion — 6.2 days for 10,000 spatial barcodes vs. 93 seconds for Hotspot.

#### Unique Contributions

1. **Graph-based local autocorrelation**: A parametric test statistic that measures whether a gene is expressed similarly by neighboring cells in any similarity graph. Unlike Geary's C (*Inc. Stat.* 1954) and Laplacian Score (*NeurIPS* 2006), Hotspot uses a parametric null model (no permutation tests needed), enabling genome-scale application.

2. **Modality-agnostic design**: The similarity metric is fully decoupled from the statistical test. The same algorithm works for transcriptional KNN, spatial coordinates, or phylogenetic trees — enabling the first method for lineage-associated gene module detection.

3. **Local correlation for module detection**: A pairwise extension of the autocorrelation statistic that detects co-expression in the same graph regions, even when genes are rarely co-detected in the same cell. More sensitive than Pearson correlation at low sequencing depths.

4. **Computational efficiency**: O(NK) per gene for feature selection (vs. O(N²K²) naive); orders of magnitude faster than SpatialDE for spatial data.

---

### Method Overview

Hotspot operates in three main steps:

**Step 1 — Cell similarity graph**: Construct a K-nearest-neighbors graph from any similarity metric (transcriptional latent space, spatial coordinates, or lineage tree). Edges are weighted by a Gaussian kernel with adaptive per-cell bandwidth (σ = distance to the K/3-th neighbor), normalized to sum to 1 per cell.

**Step 2 — Feature selection**: For each gene, compute the local autocorrelation statistic $H_x = \sum_{(i,j)\in E} w_{ij} \hat{x}_i \hat{x}_j$ where $\hat{x}_i$ is the standardized expression under a null model (Depth-Adjusted Negative Binomial for standard scRNA-seq; Bernoulli for ultra-sparse data). Convert to Z-scores using analytically derived moments (no permutation tests). Apply Benjamini-Hochberg FDR correction.

**Step 3 — Module detection**: For significant genes, compute pairwise local correlations $H_{xy} = \sum_{(i,j)\in E} w_{ij}(\hat{x}_i \hat{y}_j + \hat{y}_i \hat{x}_j)$ with a conservative conditional null. Cluster the resulting Z-score matrix using UPGMA hierarchical clustering with FDR-based stopping criterion.

**Key biological assumptions**:
- Biologically informative genes are expressed similarly by cells that are similar in the chosen metric
- Library size variation is the primary technical confounder (addressed by per-cell null model normalization)
- Gene co-expression modules reflect coordinated biological programs

See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Cells | Modality | Application |
|---------|-------|----------|-------------|
| SymSim simulated | 3,000 | scRNA-seq | Feature selection benchmark (known ground truth) |
| 10x PBMC 5k (CD4+ T cells) | 1,500 | scRNA-seq + CITE-seq | Feature selection + module detection |
| 10x PBMC 5k (CD14+ monocytes) | ~1,000 | scRNA-seq | Module detection replication |
| Slide-Seq mouse cerebellum (Rodriques 2019, *Science*) | 32,000 | Spatial transcriptomics | Spatial gene modules |
| Chan 2019 (*Nature*) mouse embryogenesis | 1,756 | scRNA-seq + lineage tracing | Lineage-associated modules |

#### Metrics and Results

**Feature selection (simulated data)**:
- Precision-recall curves: Hotspot > HVG, NBDisp, PCA-based selection (Figure S1B)
- Hotspot identifies 500 biologically varying genes with higher precision at all recall thresholds

**Feature selection (CD4+ T cells)**:
- Gene Relevance (GR) score (number of CD4+ T cell MSigDB gene sets containing each gene): Hotspot > HVG at all thresholds; Hotspot > NBDisp for top >200 genes (Figure 2A)
- Protein autocorrelation (independent validation via CITE-seq surface proteins): Hotspot-selected genes produce scVI latent space with higher protein autocorrelation than HVG/NBDisp/PCA (Figure 2B; differences not statistically significant, p > 0.05 rank-sums)

**Module detection (CD4+ T cells)**:
- Reproducibility (proportion of gene pairs assigned to same module in both halves of split dataset): Hotspot > WGCNA, GRNBoost, ICA, Pearson (Figure 2E)
- Hotspot detects more modules and assigns more genes than alternatives
- Identified biologically coherent modules: naive T cells (CCR7, SELL), activated T cells (IL7R, S100A4), Th1 (IFNG, TBX21), cytotoxic (PRF1, GZMB), Treg (FOXP3, IL2RA, CTLA4, TIGIT)

**Spatial analysis (mouse cerebellum)**:
- 560 genes with significant spatial autocorrelation (FDR < 0.05) at K=300 neighbors
- 6 spatial modules corresponding to known cerebellar cell types (Purkinje, granular, oligodendrocyte layers)
- vs. SpatialDE: comparable precision-recall and IDR reproducibility; 93s vs. 6.2 days for 10,000 barcodes (Figure S2C)

**Lineage analysis (mouse embryogenesis)**:
- 2,554 genes with significant lineage autocorrelation (FDR < 0.05)
- 5 lineage modules: visceral/definitive endoderm (Cubn, Amot), primitive blood (Hbb-bh1, Gata1), parietal endoderm (Srgn), trophoblasts (Plac1, Ascl2)
- Angioblast signature detectable by transcriptional but not lineage similarity — demonstrates complementarity of the two metrics

---

### Reproducibility

**Rating: 4/5**

**Justification**: The main Hotspot package is well-implemented, documented, and installable via pip (`hotspotsc`). The core statistical methods are fully implemented and match the paper. However, the comparative analysis scripts (benchmarks against HVG, NBDisp, WGCNA, GRNBoost, SpatialDE) are in a separate repository (`github.com/deto/hotspot_analysis`) and require specific versions of R packages (Seurat v2.3.4, M3Drops v3.10.4, WGCNA v1.69) that may be difficult to install.

**Environment setup**:
```bash
pip install hotspotsc  # or: pip install hotspotsc[gpu] for GPU support
# Dependencies: numpy, scipy, pandas, scikit-learn, numba, anndata, pynndescent
```

**Data availability**: All datasets are publicly available:
- 10x PBMC 5k: https://support.10xgenomics.com/single-cell-gene-expression/datasets/3.1.0/5k_pbmc_protein_v3
- Slide-Seq cerebellum: https://portals.broadinstitute.org/single_cell/study/slide-seq-study
- Mouse embryogenesis: NCBI GEO GSE117542

**Common pitfalls**:
1. **Default graph is unweighted**: `create_knn_graph()` uses `weighted_graph=False` by default — all edge weights are 1.0. The Gaussian kernel weights described in the paper require `weighted_graph=True`. For most use cases, the unweighted graph works well, but results may differ from the paper's description.
2. For Slide-Seq or other ultra-sparse data, use `model='bernoulli'` not `model='danb'`
3. Tree-based KNN uses uniform weights (not Gaussian) — results may differ from Euclidean KNN
4. Approximate KNN (pynndescent) is default — use `approx_neighbors=False` for exact reproducibility
5. Module detection is sensitive to `min_gene_threshold` and `fdr_threshold` — paper uses 15-50 and 0.05 respectively
6. The `hotspot_analysis` repo (benchmarks) requires R 3.5.1 and specific package versions

**Strengths**:
- Clean Python API with AnnData integration
- GPU acceleration via CuPy for large datasets
- Modality-agnostic design (transcriptional, spatial, lineage)
- Parametric null model avoids slow permutation tests
- Well-tested (unit tests for all core statistical functions)

**Weaknesses**:
- Pairwise correlation computation is O(G²NK) on CPU — slow for large gene sets (>2000 genes)
- Tree KNN uses uniform weights (not Gaussian) — may be suboptimal for lineage analysis
- No built-in support for batch correction in the similarity graph
- Comparative analysis code in separate repo with older R dependencies

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
