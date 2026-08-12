---
layout: default
permalink: /paper-atlas/monocle-3-moca-71547058/
title: "Monocle 3 / MOCA"
nav: false
description: "这篇论文首先是一张小鼠器官发生单细胞图谱：作者用 sci-RNA-seq3 测量 E9.5–E13.5 的 61 个胚胎，得到约 205 万个细胞，定义 38 个主要 cell types、655 个 subtypes，并分析 AER、肢芽间充质和骨骼肌等发育系统。其次，它用一个新版本 Monocle 3 在 152 万高质量细胞上重建 10 个主要轨迹与 56 个子轨迹。 因此，Monocle 3 不是这篇论文全部实验流程的代名词。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature · 2019</span>
    </div>
    <h1>Monocle 3 / MOCA</h1>
    <p>The single-cell transcriptional landscape of mammalian organogenesis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-019-0969-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Monocle 3 中文方法解读：在百万细胞器官发生图谱中学习可分支、可汇合的轨迹

### 1. 先区分论文的两层贡献

这篇论文首先是一张小鼠器官发生单细胞图谱：作者用 sci-RNA-seq3 测量 E9.5–E13.5 的 61 个胚胎，得到约 205 万个细胞，定义 38 个主要 cell types、655 个 subtypes，并分析 AER、肢芽间充质和骨骼肌等发育系统。其次，它用一个新版本 Monocle 3 在 152 万高质量细胞上重建 10 个主要轨迹与 56 个子轨迹。

因此，Monocle 3 不是这篇论文全部实验流程的代名词。sci-RNA-seq3 建库、reads 处理、doublet 检测、细胞类型注释、跨图谱匹配和 WISH 验证都在轨迹软件之外。软件接收的是已经形成的表达矩阵与细胞元数据，输出低维表示、clusters/partitions、principal graph、pseudotime 和沿图变化的基因统计。

### 2. Monocle 3 为什么不同于 Monocle 1

Monocle 1 在二维 ICA 空间对细胞建 MST，主要适合一棵树。器官发生图谱包含百万级细胞、多个彼此断开的系统、分支以及可能的 fate convergence；而且数据从 E9.5 才开始，缺少更早祖先状态。Monocle 3 将问题拆成：

1. 用 PCA/UMAP 表达局部转录几何；
2. 用社区检测与 partition 将不连续流形分开；
3. 在每个 partition 内学习带分支的 principal graph，并允许闭环/汇合；
4. 用户指定根节点后，以图上的 geodesic distance 定义 pseudotime；
5. 用图自相关寻找沿轨迹呈局部结构的基因。

这使它不必强迫内皮、神经、间充质等完全断开的系统通过一棵全局树连接。

### 3. 数据入口与预处理

当前标准软件对象是 `cell_data_set`，内部保存 genes×cells counts、细胞元数据和基因元数据。典型调用链是：

```r
cds <- preprocess_cds(cds, num_dim = 50)
cds <- reduce_dimension(cds)
cds <- cluster_cells(cds)
cds <- learn_graph(cds)
cds <- order_cells(cds, root_pr_nodes = ...)
res <- graph_test(cds, neighbor_graph = "principal_graph")
```

论文 Methods 对 MOCA 分析先过滤低覆盖细胞和低检测基因，做 size-factor normalization、log transformation、选择高变基因并用 PCA 压缩。当前 `R/preprocess_cds.R` 仍提供 PCA/LSI 入口，但软件默认、依赖和大矩阵后端已随版本演化。论文具体的 5,000 HVGs、50 PCs 等参数是 MOCA 运行设置，不应混同为所有数据的永久默认。

预处理确定了“哪些表达差异算作状态差异”。胚胎日龄、批次、细胞周期和测序深度若未处理，都会进入后续邻居图；Monocle 3 不会自动把技术轴与生物发育轴分开。

### 4. UMAP：可扩展的局部状态坐标

Monocle 3 将 PCA 表示投影到低维 UMAP。UMAP 从 kNN 关系构造 fuzzy neighborhood graph，并寻找低维坐标，使局部邻接尽量保留。论文选择它，是因为比 t-SNE 更容易在图中保留相关 cell types 之间的桥梁，而且能扩展到百万级数据。

但 UMAP 距离不等于真实发育时间，二维/三维空白也不必然表示生物学断裂。随机种子、邻居数、距离度量、batch correction 和采样密度都会改变几何。论文 Fig. 4a 中 radial glia 通向神经元与 oligodendrocytes 的桥，或 early mesenchyme 向多个系统放射，是后续图学习的输入证据，不是单凭视觉就确认的谱系。

版本边界很重要：论文报告通过 Python `umap` 0.3.2/reticulate 运行；当前源码 `R/reduce_dimensions.R:289-320` 使用 `uwot::umap()`，并在 transform 前设置 seed 2016。两者实现、数值坐标和默认值并不相同，所以当前版本能验证“使用 UMAP”这一结构，但不能保证重现论文像素级布局。

### 5. clusters 与 partitions：先判断哪些流形可连

#### 5.1 社区检测

Monocle 3 在 UMAP 或预处理空间建立 kNN graph，再用 Louvain 社区检测得到 clusters。论文使用 Louvain；当前 `cluster_cells()` 默认已转为 Leiden，但仍支持 Louvain。这是又一个 paper-code 版本差异。

cluster 是局部密度社区，不等于最终 trajectory。相邻 clusters 之间若有显著多于随机预期的细胞邻接，会被合并成同一 partition/supergroup。

#### 5.2 PAGA 式连接检验

令 $X$ 是 cell-to-cluster membership matrix，$A$ 是细胞 kNN adjacency，cluster 间边数可写为

$$
M=X^TAX.
$$

当前 `R/cluster_cells.R:603-643` 直接计算该矩阵，建立随机连接的期望与方差，做正态尾概率近似并校正多重检验。显著相连的 clusters 形成一个 partition。论文称这些合并群为 supergroups，并在其中分别学图。

partition 的意义是“当前邻居图支持连续连接”，而不是证明细胞共享谱系祖先。反过来，论文从 E9.5 开始，缺失早期中间态会使真实相连的系统被划成不连续 partitions；论文自己把十条主轨迹间断裂解释为可能缺少祖先/中间状态。

### 6. principal graph：用 SimplePPT 概括流形骨架

#### 6.1 landmark nodes 与软分配

百万细胞不能直接把每个细胞都当图节点。Monocle 3 在每个 partition 选择一组代表性 centers/landmarks，用软分配矩阵 $P$ 表示每个细胞对各 center 的归属。随后交替优化 center 位置与连接结构。

当前 `calc_principal_graph()` 使用两个目标部分：图边总长度 $obj_W$ 与细胞到 centers 的软分配代价 $obj_P$：

$$
\mathcal L = obj_W + \gamma obj_P.
$$

源码 `R/learn_graph.R:1025-1079` 每轮先计算 centers 两两距离，在 centers 上取 MST，得到边矩阵 $W$；再计算 soft assignment $P$；最后更新 centers，直至目标相对变化小于阈值或达到最大迭代数。这是 SimplePPT/reversed graph embedding 的核心实现。

$\gamma$ 决定图短而平滑与贴近细胞云之间的权衡。当前默认 `L1.gamma=0.5`、`L1.sigma=0.01`；这些当前默认不能未经核对就当作论文所有 MOCA 子分析的固定参数。

#### 6.2 剪枝和闭环

仅用 MST 会得到树，无法表示汇合或环。`learn_graph()` 默认剪掉过短末端支路，并可连接满足条件的 tip：低维欧氏距离足够近，但沿现有图 geodesic distance 足够远。当前源码把 `minimal_branch_len` 默认设为 10、`geodesic_distance_ratio` 为 $1/3$、`euclidean_distance_ratio` 为 1。

这允许在局部几何支持时补闭环，表达论文所关心的 fate convergence。但“连上一个 loop”仍是几何判断，不是 lineage tracing。UMAP 把远处状态挤近会产生假闭环；缺失中间态则可能阻止真实汇合。

### 7. pseudotime：从指定根到细胞的图距离

图学习本身没有方向。用户必须提供 root cells 或 root principal nodes，通常根据早期胚胎日龄和已知 progenitor markers 选择。当前 `order_cells()` 将 root 映射到 principal graph，然后在细胞级投影图 `pr_graph_cell_proj_tree` 上计算最短路径：

$$
\tau_i=\min_{r\in R} d_G(r,i).
$$

对应源码 `R/order_cells.R:143-184`。若给多个 roots，每个细胞取到最近 root 的距离。不同 partition 若没有 root，可能得到无限 pseudotime；起点选错也会整体反向或产生不合适的距离。

因此 pseudotime 是“在当前 principal graph、当前 root 和当前低维表示条件下的 geodesic distance”。它不是 E9.5–E13.5 的绝对小时，也不自动区分细胞速度快慢。论文常用真实 embryo stage 着色检查方向是否合理，这属于外部验证。

### 8. graph_test：找沿轨迹形成空间模式的基因

Monocle 3 不只把表达对 pseudotime 拟合一条函数，而是用 Moran's I 检测表达在细胞邻居/主图上的自相关。对表达 $x_i$ 与图权重 $w_{ij}$，

$$
I=\frac{N}{W}
\frac{\sum_{ij}w_{ij}(x_i-\bar x)(x_j-\bar x)}
{\sum_i(x_i-\bar x)^2},
\qquad W=\sum_{ij}w_{ij}.
$$

$I>0$ 表示相邻细胞具有相似表达，可捕捉沿分支、局部区域或环变化的基因。当前 `R/graph_test.R:108-210` 构造 neighborhood weights，将 counts 按 size factor 归一化并 log10 转换，再调用 Moran's I test。

这比只检验单调 pseudotime 趋势更适合复杂图，但显著自相关仍不是因果调控。cluster marker、batch、细胞周期或局部测序深度都可能产生空间结构。论文对 AER、肢芽和肌肉基因的解释还依赖 embryo stage、marker、解剖学与 WISH 等证据。

### 9. 如何读关键图

- **Fig. 1**：面板 a 是 sci-RNA-seq3 三轮索引实验，不是 Monocle 软件步骤；b 展示每胚胎细胞数，c 是 embryo-level pseudotime。
- **Fig. 2–3**：主要建立 atlas 的 cell types/subtypes 与 AER 验证。Fig. 3g–h 才是 AER early-to-late trajectory 和 710 个动态基因。
- **Fig. 4**：a 先把 152 万细胞分成十个主 trajectory groups，并放大神经与间充质；b 是 cell type 到 trajectory 的对应；c 显示 epithelial 内多条子轨迹。
- **Fig. 5**：对十个主系统继续细分，形成论文报告的 56 条 subtrajectories。颜色是作者注释，不是图算法自动提供的器官名称。
- **Fig. 6**：聚焦 skeletal muscle，展示从 somite/dermomyotome 到 muscle progenitor、myoblast、myocyte、myotube 的路径以及 Pax3/Pax7/Myf5/MyoD/Myog/Myh3 等 marker。图中的 Myf5 与 Myod paths 是结合 marker 和几何的生物学解释。
- **Extended Data**：覆盖 QC、subcluster 稳定性、AER、limb bud、各主轨迹与算法参数；Supplementary Note 1 专门讨论肢芽 mesenchyme。

本次直接查看了本地主图 1、4、5、6，并用 `paper.md` 的所有主图和 Extended Data 图注作交叉核对。其余本地图片保留为图证据入口，不把图注本身当作复现实验。

### 10. 图谱结果中的三个代表性案例

#### 10.1 AER

作者在 epithelial subtypes 中识别 1,237 个 AER cells，用 WISH 验证 Fgf8、Fndc3a、Adamts3、Snap91 的远端肢芽表达。pseudotime 显示 Fndc3a 先于 Fgf8/Fgf9/Rspo2，Mki67 和 Igf2 随后下降。这里轨迹得到组织学与真实日龄支持，但“先表达”仍不等同于上游因果。

#### 10.2 多系统轨迹图谱

在去除部分 doublet 后，作者迭代分析十个主轨迹，得到 56 个 subtrajectories。它们涵盖 CNS、PNS、上皮、间充质、造血等系统。某些断裂可能是真实组织隔离，也可能来自 E9.5 之前状态缺失或浅测序。

#### 10.3 骨骼肌

Fig. 6 把 Pax3/Pax7 progenitors 与 Myf5、MyoD 路径以及成熟肌细胞连接。大量细胞覆盖使较细的分叉可见，但 principal graph 仍是表达几何模型。要证明不同调控路径的 lineage relationship，需要遗传示踪或扰动数据。

### 11. 当前代码与论文版本边界

本地代码 commit 为 `4f4239a0afb0dd1941a0359ba6bec95eb0ccf628`，`DESCRIPTION` 版本 1.4.26。它是论文发表后的现代 Monocle 3 快照，不是 2019 MOCA 分析环境的冻结副本。

结构上可直接验证：

- `R/preprocess_cds.R:61`：标准化/PCA 或 LSI 入口；
- `R/reduce_dimensions.R:80,289-320`：当前 UMAP 入口与 uwot 实现；
- `R/cluster_cells.R:86,603-643`：社区检测与 partition 连接检验；
- `R/learn_graph.R:115-220,1025-1079`：图学习参数与 SimplePPT 目标；
- `R/order_cells.R:57,143-184`：root 与 geodesic pseudotime；
- `R/graph_test.R:108-210`：Moran's I 图自相关。

主要差异包括：论文用 Python UMAP，当前用 `uwot`；论文主要写 Louvain，当前默认 Leiden；partition 的阈值默认也可能不同。当前包还加入 BPCells、大矩阵、模型保存/投影等后续能力。`doc_code.md` 中 paper-code 状态必须因此保留 Exact/Partial/Not found，而不能简单说“当前版本完全复现论文”。

MOCA 特有的跨 atlas NNLS matching 和某些组合公式不在通用 Monocle 3 包中，属于论文分析代码边界；仅看到论文公式不能假定它们由当前 package API 实现。

### 12. 复现与解释检查单

重做类似分析时，应固定并报告：counts/QC/doublet 阈值、size factors、HVG 与 PC 数、batch alignment、UMAP 实现和 seed、kNN 参数、Louvain/Leiden 与 resolution、partition 显著性阈值、principal graph 的 centers/剪枝/闭环参数、每个 partition 的 root、Moran's I 邻居图与 FDR。

还应做敏感性分析：不同 root 是否改变结论；去除 embryo/batch 后轨迹是否保持；subsampling 后细分支是否稳定；真实 stage 是否沿 pseudotime总体单调；已知 marker 是否按预期出现。图看起来连续不是充分验证。

本工作区没有重跑 200 万细胞 atlas、Supplementary Note 分析或全部图表，因此不声称数值级复现。它完成的是论文、补充、主图与当前直接源码的证据对应，并明确记录版本漂移。

### 13. 证据入口

- 主文：`paper source/PMC6434952/paper.md`
- 论文 PDF：`paper source/PMC6434952/nihms-1518381.pdf`
- 补充：`NIHMS1518381-supplement-Supplement_note_1.pdf` 与 Reporting Summary PDF
- 图像：`paper source/PMC6434952/images/nihms-1518381-f0001.jpg` 至 `f0018.jpg`
- 当前源码：`code/` commit `4f4239a0afb0dd1941a0359ba6bec95eb0ccf628`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## The Single-Cell Transcriptional Landscape of Mammalian Organogenesis

**Paper**: Cao et al., *Nature* 566:496–502 (2019)
**DOI**: 10.1038/s41586-019-0969-x
**Method**: sci-RNA-seq3 + Monocle 3

---

### Motivation & Novelty

#### The Biological Problem

Mouse organogenesis (E9.5–E13.5) is the 4-day window in which most major organ systems emerge from three germ layers. Understanding the transcriptional programs driving this transformation requires profiling cells at the right depth and at the right scale — but previous atlasing efforts had two critical gaps:

1. **Adult focus**: The two major existing mouse atlases — the Mouse Cell Atlas (MCA, *Cell* 2018) and Tabula Muris (*Nature* 2018) — cover adult organs, not the embryo when fate decisions are being made
2. **Scale ceiling**: Existing single-cell methods required per-cell library preparation costs that made profiling millions of embryonic cells in a single experiment economically and logistically prohibitive

#### Why Existing Methods Fall Short

**For data collection**:
- Prior sci-RNA-seq (*Science* 2017) required Tn5 tagmentation and cell-by-cell FACS sorting, limiting throughput
- 10x Chromium: high per-cell cost (~$0.10/cell) makes 2M-cell experiments infeasible for academic labs
- Methods requiring single-cell dissociation with enzymes lose nuclear RNA and damage sensitive cell types

**For trajectory analysis**:
- Monocle 2 (*Nature Methods* 2017): assumes a single connected manifold; fails when ancestral states are missing
- PAGA (*Nature Methods* 2019): provides a coarse community-level graph but doesn't resolve within-community trajectories; not designed for millions of cells
- URD (*Science* 2018): tree-based, cannot model convergent fates (multiple progenitors → single terminal type)
- t-SNE: does not preserve global distances, making cross-cluster relationships uninformative for trajectory learning

#### Novel Contributions

1. **sci-RNA-seq3**: A dramatically improved split-pool barcoding protocol achieving <$0.01/cell cost:
   - Fixed nuclei (not live cells) — compatible with freezing and batch processing
   - Hairpin ligation replaces Tn5 tagmentation at the third indexing level
   - FACS-free dilution approach
   - Library prep completable by a single person in one week
   - 384×384×768 = ~113 million combinatorial barcode possibilities

2. **Mouse Organogenesis Cell Atlas (MOCA)**: The first single-cell atlas of mouse organogenesis:
   - 2,058,652 cells, 61 embryos, E9.5–E13.5 in one experiment
   - 38 major cell types, 655 subtypes
   - 56 developmental subtrajectories spanning every major organ system
   - Publicly available with interactive website

3. **Monocle 3**: A computational framework for trajectory inference at millions-of-cells scale:
   - Handles **discontinuous** trajectories (missing ancestral states)
   - Handles **convergent** fates (multiple progenitors → single terminal type)
   - Handles **loops** in developmental trajectories
   - Scales to O(N) via UMAP + landmark-cell SimplePPT
   - Moran's I test for trajectory-dependent gene expression (adapts spatial statistics)

---

### Method Overview

Monocle 3 is an R package implementing a 4-step trajectory inference pipeline:

#### 1. Dimensionality Reduction (UMAP)
Cells are projected from high-dimensional gene expression space into a 2D or 3D UMAP embedding (top 5,000 HVG → 50 PCs → UMAP). Unlike t-SNE, UMAP preserves global distances — developmentally related cell types are placed near one another, making trajectory learning possible. UMAP processed 2M cells in ~3 CPU hours; t-SNE would require >64 hours.

#### 2. PAGA Cell Partitioning
A PAGA-inspired significance test determines which Louvain/Leiden communities are genuinely connected (more kNN edges than expected by chance under a null binomial model) and which are disconnected. The result is a set of **supergroups** or **partitions** — each representing one independent trajectory (e.g., neural tube, mesenchyme, epithelial, hematopoietic). The 2M cells resolved into 10 major partitions.

#### 3. SimplePPT Principal Graph
Within each partition, a **principal graph** (not just a tree) is learned using the SimplePPT algorithm. The graph is embedded in the UMAP space and represents all possible developmental paths. Key innovations over prior methods:
- **Landmark cells** (K ≈ 2000) reduce the problem from N cells to K representative points
- **MST of centers** provides the backbone topology
- **Branch pruning** removes noisy short branches
- **Loop closure** connects distant leaf nodes that are close in UMAP space, enabling detection of cyclic trajectories

#### 4. Pseudotime and Trajectory-Dependent Genes
Each cell is projected onto the nearest principal graph edge and assigned a pseudotime equal to its geodesic distance from a user-specified root. Trajectory-dependent genes are identified using **Moran's I** — a spatial autocorrelation statistic that tests whether nearby cells on the trajectory have correlated expression.

---

### Evaluation

#### Datasets
- **Primary**: 61 C57BL/6 mouse embryos at E9.5 (n=12), E10.5 (n=12), E11.5 (n=13), E12.5 (n=12), E13.5 (n=12)
- **Control**: Human HEK293T + mouse NIH/3T3 mixture (species-coherence QC, 3% collisions)
- **Validation**: Whole-mount in situ hybridization (WISH) of 9 selected marker genes

#### Key Results

| Finding | Metric |
|---------|--------|
| Cells profiled | 2,058,652 cells (median 671 UMIs, 519 genes per cell) |
| Doublet rate | 4.3% detected (10.3% estimated including within-cluster) |
| Major cell types | 38 (manually annotated from 40 Louvain clusters) |
| Cell subtypes | 655 total; 572 non-doublet; median 1,869 cells each |
| Marker genes | 2,863 cell-type-specific (>2-fold), 932 (>5-fold) |
| Differential expression | 17,789/26,183 genes (68%) differ across major cell types |
| Trajectory groups | 10 major partitions → 56 subtrajectories |
| Cross-atlas matching | 96/130 MCA fetal cell types matched to 58 MOCA subtypes (NNLS) |
| WISH validation | 4/4 novel markers (Tox2, Fndc3a, Adamts3, Snap91) confirmed |

#### Biological Validation

**Erythroid lineage dynamics**: primitive erythroid (Hbb-bh1+, yolk sac origin) progressively displaced by definitive erythroid (Hbb-bs+, fetal liver origin) — consistent with known biology.

**AER characterization**: Identified 1,237 apical ectodermal ridge cells (0.06% of MOCA), confirmed 4 novel markers by WISH. AER cell numbers peak E10.5–E11.5, with pseudotime showing proliferative program downregulation.

**Myogenesis**: Reconstructed the convergent myogenic trajectory — Pax3+ dermomyotome → two parallel Myf5+ and Myod+ paths → converge at Myog+ myocytes. The Myf5+ path shows higher Robo/Slit signaling (pioneer myoblasts for embryonic myofibers).

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Full data release on GEO (GSE119945) and interactive atlas (atlas.gs.washington.edu/mouse-rna/)
- Monocle 3 R package publicly available on GitHub (cole-trapnell-lab/monocle3)
- sci-RNA-seq3 library preparation code available (github.com/JunyueC/sci-RNA-seq3_pipeline)
- Clear protocol and reagent descriptions

**Practical challenges**:
- Reproducing the full 2M-cell experiment requires significant resources (one Illumina NovaSeq run ~$5,000+; 61 mouse embryo time-points)
- Critical analysis parameters (ncenter overrides, minimal_branch_len adjustments for ~25% of subtrajectories) were chosen manually and are not fully documented
- The cross-atlas NNLS matching code (β formula) is NOT included in the monocle3 R package — only described in Methods
- Shallow per-cell sequencing (median 671 UMIs) limits re-analysis capability
- UMAP implementation changed from Python `umap/v0.3.2` (paper) to R `uwot` (current code) — exact embedding reproduction unlikely

**Environment setup**:
- R ≥ 4.0.0 with Bioconductor (SingleCellExperiment, Biobase)
- Key dependencies: `uwot`, `igraph`, `spdep`, `irlba`, `leidenbase`
- Full DESCRIPTION in `code/DESCRIPTION`
- BPCells recommended for large datasets (on-disk matrix support)

**Common pitfalls**:
- `learn_graph()` only accepts `reduction_method="UMAP"` — cannot use tSNE or PCA coordinates
- `order_cells()` fails silently when >10,000 principal graph nodes — reduce `ncenter`
- UMAP non-determinism when `umap.fast_sgd=TRUE` or `cores>1`
- Manual root node selection is required unless using the automatic early-stage heuristic

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
