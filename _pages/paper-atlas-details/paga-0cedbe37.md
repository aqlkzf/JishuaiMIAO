---
layout: default
permalink: /paper-atlas/paga-0cedbe37/
title: "PAGA"
nav: false
description: "PAGA 不直接把所有细胞强行拟合成一棵轨迹树。它先在单细胞 kNN 图上划分群体，再统计群体之间跨边是否足够多，得到一个加权的群体图 G^。这个图可以同时表示连续连接、分支、环和断开的区域；沿高置信群体路径再结合 DPT，才得到细胞级顺序和基因变化。"
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
      <span>Genome Biology · 2019</span>
    </div>
    <h1>PAGA</h1>
    <p>PAGA: graph abstraction reconciles clustering with trajectory inference through a topology preserving map of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-019-1663-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PAGA 方法解读：把单细胞邻接图压缩成保拓扑的群体地图

### 一句话抓住核心

PAGA 不直接把所有细胞强行拟合成一棵轨迹树。它先在单细胞 kNN 图上划分群体，再统计群体之间跨边是否足够多，得到一个加权的群体图 $G^*$。这个图可以同时表示连续连接、分支、环和断开的区域；沿高置信群体路径再结合 DPT，才得到细胞级顺序和基因变化。

### 1. 它解决的不是“聚类还是轨迹”二选一

聚类回答“哪些细胞相似”，但把连续分化切成离散块；传统轨迹方法回答“细胞沿什么顺序变化”，但常预设一个连通树。真实数据可能因采样不足而缺少中间细胞，也可能确实包含互不连接的组织或状态。此时把所有群体连成树，会把数据没有支持的边解释成生物轨迹。

PAGA 的策略是保留两个尺度：

- 单细胞图 $G=(V,E)$ 保存局部邻居；
- 分区图 $G^*$ 保存群体之间的粗粒度拓扑。

它不要求 $G^*$ 是树。若数据支持断开，图就可以断开；若支持复杂连接，也不必删成单一路径。

### 2. 输入从哪里来

论文流程是：过滤和归一化表达矩阵，选高变基因，必要时回归混杂并标准化，再在 PCA 空间以欧氏距离建立 UMAP 风格的 kNN-like graph。随后用 Louvain 或已有注释把细胞分组。

这意味着 PAGA 的结果继承上游选择。若批次效应制造了邻居边，PAGA 可能总结出假连接；若稀疏采样切断真实桥梁，它也可能判断为断开。PAGA 是邻接图的抽象器，不会修复一个生物含义错误的邻接图。

### 3. 连通性分数如何计算

对群体 $i,j$，记：

- $n_i,n_j$：两个群体的细胞数；
- $e_i,e_j$：从两个群体出发的边数；
- $\epsilon^{\mathrm{sym}}_{ij}$：实际观察到的双向跨群体边数；
- $n$：总细胞数。

若边随机连接到其他节点，跨群体边的期望为

$$
\widehat\epsilon^{\mathrm{sym}}_{ij}
=\frac{e_i n_j+e_j n_i}{n-1}.
$$

补充材料 Eq. 11 定义

$$
c_{ij}=\min\left(
\frac{\epsilon^{\mathrm{sym}}_{ij}}
{\widehat\epsilon^{\mathrm{sym}}_{ij}},1
\right).
$$

例子：若两个群体之间观察到 12 条跨边，随机期望为 30 条，则 $c=0.4$；若观察到 45 条而期望 30 条，则分数截断为 1。

这个数应读成“相对于随机边期望的归一化连接强度”，而不是“存在生物谱系的 40% 或 100% 概率”。补充材料明确指出，随机分区的 null 并不等于 Louvain 分区的校准 null，所以画图时仍需要阈值。

### 4. 从分数到 PAGA 图

每个群体变成一个节点，$c_{ij}$ 变成边权。低权边可被阈值去除，以减少由技术噪声产生的细弱连接。阈值不是全局常数：本地 notebook 中可看到 0.003、0.01、0.02、0.03、0.12、0.2 等不同选择，它们服务于不同数据和图板。

最小生成树（对逆连通性）或等价的最大连通性生成树可以显示一个 backbone，但这是可选视图，不是 PAGA 的定义。Planaria 工作里曾用树突出谱系；论文这里也展示不强制树的完整图。

### 5. PAGA path 为什么仍能回到单细胞分辨率

先在 $G^*$ 上选一条高置信群体路径，再在每个连通区域内从 root cell 计算扩展 DPT。跨断开分量的距离设为无穷，避免伪造一条穿过采样空洞的顺序。

于是 $(G^*,d)$ 成为两层坐标：$G^*$ 决定允许走哪些群体路线，$d$ 决定路线内部的相对距离。沿顺序平滑表达，可以观察 Gata、Klf1、Elane、Irf8 等标记基因的连续变化。

需要注意：DPT 距离不是实验钟表时间，root 的选择会改变方向和数值；PAGA 图本身也没有自动赋予时间箭头。

### 6. PAGA 如何帮助二维可视化

普通 UMAP 或 ForceAtlas2 从随机位置开始时，局部邻域可能保留得很好，但远距离群体会错误重叠或断开。PAGA 先给群体节点一个粗布局，再把每个群体的细胞放在对应节点附近的不重叠小矩形中，作为细胞级布局初值。

图 1 的虚线箭头正体现双向关系：单细胞图被抽象成 PAGA 图；PAGA 图又初始化细胞布局。Box 1 的 $\mathrm{KL}_{\mathrm{geo}}$ 同时惩罚应连接却断开的区域和不应连接却重叠的区域，用来评价全局拓扑，而不仅是局部邻居。

### 7. RNA velocity 提供方向，PAGA 只做抽象

普通 PAGA 基于无向邻接图，只说明两个群体相连。若已有 RNA velocity transition graph，PAGA 可聚合群体间箭头，输出 directed coarse graph。图 3 对 Planaria epidermis 和 muscle 同时展示单细胞箭头、无向拓扑和有向群体图。

方向信息来自 velocity 模型，不是 PAGA 从静态表达自动推断出来的。velocity 错误、动力学假设或稀疏性都会传递到 directed PAGA；PAGA 的贡献是降噪和汇总，而不是独立证明谱系方向。

### 8. 五幅主图的证据链

1. **图 1**：从高维表达、kNN 图、分区到 PAGA 图，再到 path 和基因趋势。
2. **图 2**：四个造血数据中比较 PAGA+embedding、群体图和路径基因变化；共同结构较稳定，而 basophil 路线随采样密度变化。
3. **图 3**：Planaria 从 tissue 到 cell type、single cell 的多分辨率地图，并加入 RNA velocity 抽象。
4. **图 4**：zebrafish 由胚胎日链到细粒度细胞图；与独立参考拓扑比较的 ROC AUC 为 0.9739。阈值图说明 precision/recall 需要权衡，不给出普适阈值。
5. **Box 1**：用 geodesic-weighted KL 评价二维嵌入是否错误断开或重叠。

这些结果证明作者工作流在所选数据上有用，但不等于所有数据、预处理和聚类下都保拓扑。

### 9. 代码证据的真实边界

本地 `paga/` 是论文复现 notebook 仓库，commit 为 `d5688a38d9054c6fcea7302023afa0510cd3577a`。它验证了作者怎样调用 `sc.tl.paga`、`sc.pl.paga`、`sc.tl.dpt`、`sc.pl.paga_path`、`init_pos='paga'` 和 `use_rna_velocity=True`，并保存了大量图和版本输出。多数 notebook 记录 Scanpy 1.2.0 环境。

但真正的生产实现位于当时的 Scanpy，本地没有 `scanpy/tools/_paga.py` 或 DPT 源码。因此不能把外部或后来版本的 `_paga.py` 行号当作本地证据，也不能在未核验的情况下声称当前 Scanpy 内部实现、默认值或兼容性与 2019 年完全相同。

### 10. 使用 PAGA 前最重要的检查

- 改变 PCA/latent representation 或 neighbor 参数后，核心连接是否稳定？
- 改变分区 resolution 后，粗拓扑是否保持？
- 弱边是否由批次、doublet 或极少细胞驱动？
- 阈值变化是否改变科学结论？
- 方向结论是否有 velocity 之外的实验或时间证据？
- pseudotime root 是否有明确生物依据？

最稳妥的结论是：PAGA 提供了一个统计归一化、可多分辨率探索的群体邻接图。它把“哪些群体连通”与“群体内部怎样排序”分开，从而避免无条件强迫所有细胞进入一棵树；但它仍依赖上游表示、邻接图、分区、阈值和方向信息。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PAGA: Partition-Based Graph Abstraction

**Paper:** Wolf FA et al. "PAGA: graph abstraction reconciles clustering with trajectory inference through a topology preserving map of single cells." *Genome Biology* 20 (2019). DOI: 10.1186/s13059-019-1663-x

**Code:** https://github.com/theislab/paga | Integrated into Scanpy: `sc.tl.paga`

---

### Motivation & Novelty

#### The Problem

Single-cell RNA-seq data captures a spectrum of cellular states that are simultaneously discrete (distinct cell types) and continuous (differentiation gradients). Existing methods forced a choice:

- **Clustering** (Louvain, SPADE [*Nat Biotechnol*, 2011], StemID [*Cell Stem Cell*, 2016]): treats all variation as discrete, imposing artificial boundaries on continuous processes. Cannot represent developmental trajectories.
- **Trajectory inference** (Monocle 2 [*Nat Methods*, 2017], DPT [*Nat Methods*, 2016], Wishbone [*Nat Biotechnol*, 2016], Slingshot [*BMC Genomics*, 2018]): often models a connected manifold or tree. The paper shows that such assumptions can be misleading when sampling gaps or distinct populations make the observed graph disconnected; it does not establish that every trajectory method fails on every such dataset.

Additionally, no existing method provided a principled way to (1) determine whether two clusters are actually connected or merely proximate by chance, (2) explore data at multiple resolutions simultaneously, or (3) initialize embeddings that preserve global topology.

#### PAGA's Unique Contributions

1. **Statistical connectivity measure**: A principled test for whether two clusters are connected beyond random chance, based on comparing observed inter-cluster edges to the expected number under a null model. This produces a continuous confidence score $c_{ij} \in [0, 1]$ for each cluster pair.

2. **Topology preservation**: Unlike tSNE and standard UMAP, which faithfully preserve *local* structure but distort *global* topology, PAGA-initialized embeddings accurately represent global structure. Disconnected clusters remain disconnected; connected trajectories remain connected.

3. **Multi-resolution exploration**: The same kNN graph can be analyzed at multiple Louvain resolutions, generating a hierarchy of PAGA graphs from coarse tissue-level to fine cell-subtype level.

4. **Scalability**: abstraction and coarse visualization are much cheaper than laying out every cell. The paper reports 90 seconds versus 191 minutes for UMAP on 1.3 million neurons; it does not give an end-to-end complexity proof independent of cell number.

5. **First whole-organism lineage tree**: PAGA enabled the first reconstruction of a complete cellular lineage tree for an adult animal — the flatworm *Schmidtea mediterranea* — published in *Science*, 2018 (Plass et al.).

---

### Method Overview

PAGA generates an abstracted graph $G^* = (V^*, E^*)$ from the single-cell kNN graph $G = (V, E)$:

1. **Graph construction**: Build a symmetrized kNN-like graph in PCA space using the UMAP neighborhood construction used in the manuscript.

2. **Partitioning**: Apply Louvain community detection to $G$ at a chosen resolution. Any partition works (including experimental cell-type labels).

3. **PAGA connectivity**: For each cluster pair $(i, j)$, compute:
   $$c_{ij} = \min\left(\frac{\epsilon_{ij}}{\hat{\epsilon}_{ij}}, 1.0\right), \quad \hat{\epsilon}_{ij} = \frac{e_i n_j + e_j n_i}{n - 1}$$
   where $\epsilon_{ij}$ = observed inter-cluster edges, $\hat{\epsilon}_{ij}$ = expected under random null, $e_i$ = total edges from cluster $i$, $n_i$ = cluster size. High $c_{ij}$ = high confidence in biological connection.

4. **Optional connectivity tree**: A maximum-connectivity spanning tree can provide a backbone or tree layout, but the full PAGA graph may be non-tree-like or disconnected.

5. **PAGA-initialized embedding**: Initialize UMAP/ForceAtlas2 with PAGA node coordinates. Fine-grained cells are placed in non-overlapping rectangles around their parent PAGA node, producing topology-preserving single-cell embeddings.

6. **Gene expression tracing**: Order cells within each cluster by DPT pseudotime. Smooth gene expression along PAGA paths to visualize gene dynamics across complex trajectories.

7. **RNA velocity integration**: PAGA can also abstract directed RNA velocity graphs, orienting edges in $G^*$ to indicate the direction of differentiation.

The method is fully integrated into Scanpy as `sc.tl.paga()`, `sc.pl.paga()`, `sc.pl.paga_path()`, and accessible via `init_pos='paga'` in embedding functions.

---

### Evaluation

#### Datasets

| Dataset | Cells | Technology | Biology | Figure |
|---|---|---|---|---|
| Paul et al. [*Cell*, 2015] | 2,730 | MARS-seq | Mouse hematopoiesis | 2b |
| Nestorowa et al. [*Blood*, 2016] | 1,654 | Smart-seq2 | Mouse hematopoiesis | 2c |
| Dahlin et al. [*Blood*, 2018] | 44,802 | 10x Genomics | Mouse hematopoiesis | 2d |
| Simulated (Krumsiek GRN) | ~500 | Simulation | Hematopoiesis ground truth | 2a |
| Plass et al. [*Science*, 2018] | 21,612 | — | Planaria (whole adult) | 3 |
| Wagner et al. [*Science*, 2018] | 53,181 | — | Zebrafish embryo | 4 |
| 10x Genomics neurons | 1.3M | 10x Chromium | Mouse neurons | S12 |
| Eulenberg et al. [*Nat Commun*, 2017] | 30,000 | Microscopy images | Jurkat cell cycle | S14 |

#### Key Results

**Cross-dataset consistency (hematopoiesis):** PAGA recovers known features of hematopoiesis consistently across all three experimental datasets despite vastly different cell numbers (1,654–44,802), protocols, and laboratories. The erythroid, neutrophil, and monocyte trajectories are identified in all datasets. The controversial basophil origin (either erythroid-megakaryocyte-basophil or neutrophil-monocyte-basophil progenitor) is correctly shown to be ambiguous in smaller datasets and resolved in the largest (Dahlin, 44k cells).

**Zebrafish prediction accuracy:** AUC = 0.9739 (Fig. 4b) when comparing PAGA-predicted topology to the experimentally validated reference graph from Wagner et al. 2018.

**Robustness:** PAGA connectivity is robust to wide variation in Louvain resolution parameters (Supp. Fig. S5). While clustering alone is ill-posed (many quasi-optimal solutions), PAGA topology remains stable because it measures connectivity between arbitrary partition sets, not the partitioning itself.

**Qualitative comparison vs Monocle 2 [*Nat Methods*, 2017]:** Monocle 2 incorrectly assigns disconnected clusters (cluster 19 in Paul et al. data) to a tree when it should recognize them as disconnected. PAGA correctly identifies the disconnection (Supp. Fig. S8).

**Embedding quality (KL_geo):** PAGA-initialized UMAP/ForceAtlas2 converges ~6× faster and produces embeddings with lower KL_geo (Supp. Fig. S10), indicating better preservation of the global topology.

**Scalability:** 1.3M neurons: PAGA 90s vs UMAP 191 min vs tSNE ~10h on 3 CPU cores.

---

### Reproducibility

**Rating: 3/5** — Strong historical notebooks, incomplete self-contained implementation.

The authors provide notebooks for the main and supplementary analyses, with recorded outputs and mostly Scanpy 1.2.0 environments. However, the local repository does not contain Scanpy's production PAGA or DPT source, several data artifacts are external, and the notebooks were not rerun in this analysis.

**Environment:** Most notebook outputs record Scanpy 1.2.0, NumPy 1.13.1, SciPy 1.0.0 and Python-igraph 0.7.1; the velocity notebook records a Scanpy 1.1 development build. Compatibility with current Scanpy is Not assessed.

**Data availability:**
- Planaria: NCBI GEO GSE103633
- Zebrafish: NCBI GEO GSE112294
- Paul/Nestorowa/Dahlin: accessible via `sc.datasets.*` or original publications
- All datasets pre-processed and cached in notebooks

**Common pitfalls:**
1. **Threshold selection**: PAGA connectivity values are dataset-dependent. Local notebooks use values from roughly 0.003 to 0.2 depending on the dataset and panel; no universal threshold is supported.
2. **Resolution sensitivity**: Louvain resolution must be chosen before PAGA, but PAGA can be run at multiple resolutions — this is one of its key features, not a limitation.
3. **Root cell for DPT**: Pseudotime requires a manually specified root cell (`adata.uns['iroot']`). The choice of root affects pseudotime values but not the PAGA graph.
4. **Historical model choice**: Some notebooks explicitly use `model='v1.0'`, while others use defaults; one Planaria comment reports only minor consequences for that graph. Exact internal differences require the absent historical Scanpy source.

**Strengths:**
- Historical integration with the Scanpy ecosystem
- Multi-resolution capability requires no extra code
- PAGA-initialized embeddings available as a single parameter change (`init_pos='paga'`)
- The main abstraction has few visible choices, but results also depend on preprocessing, representation, neighborhood graph, grouping, threshold and optional root/velocity inputs

**Weaknesses:**
- Connectivity measure is interpretable but does not provide a calibrated p-value
- Pseudotime (DPT) requires a user-specified root cell
- The full PAGA graph can represent non-tree topology; whether a cycle is recovered depends on the neighborhood graph, partition and threshold
- RNA velocity integration requires separate RNA velocity computation first

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
