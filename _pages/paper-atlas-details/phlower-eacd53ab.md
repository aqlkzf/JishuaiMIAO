---
layout: default
permalink: /paper-atlas/phlower-eacd53ab/
title: "PHLOWER"
nav: false
description: "PHLOWER 的独特之处不是简单地把细胞放进另一个低维空间，而是把“细胞到细胞的潜在分化事件”视为图上的有向边，再用一阶 Hodge Laplacian 的调和特征向量给边和整条随机游走路径建立坐标。路径在该空间中聚类后，算法再利用累计坐标随 pseudotime 的分离位置组装多分支树。 它适合单根、树形且分支较多的过程。它需要用户给 root，依赖上游嵌入和人为构造的 simplicial complex，并且计算与内存开销较高。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>PHLOWER</h1>
    <p>PHLOWER leverages single-cell multimodal data to infer complex, multi-branching cell differentiation trajectories</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02870-5" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PHLOWER 方法解读：把细胞分化事件投影到 Hodge 调和空间

### 先说结论

PHLOWER 的独特之处不是简单地把细胞放进另一个低维空间，而是把“细胞到细胞的潜在分化事件”视为图上的有向边，再用一阶 Hodge Laplacian 的调和特征向量给边和整条随机游走路径建立坐标。路径在该空间中聚类后，算法再利用累计坐标随 pseudotime 的分离位置组装多分支树。

它适合单根、树形且分支较多的过程。它需要用户给 root，依赖上游嵌入和人为构造的 simplicial complex，并且计算与内存开销较高。论文中的 kidney organoid 结果还结合了 MOJITOO、chromVAR/scMEGA、Xenium 和三 TF 联合 siRNA；不能把整个生物验证都归因于 PHLOWER 单一步骤。

### 1. 为什么从节点转向边

普通图 Laplacian $L_0$ 作用在节点信号上，适合得到“细胞在哪里”的 diffusion embedding。分化轨迹却更接近连续事件：从细胞状态 $i$ 走到状态 $j$。PHLOWER 因此使用一阶 Hodge Laplacian $L_1$，其信号定义在边上。

直观上：节点嵌入比较两个细胞的位置；边嵌入比较两个变化事件的方向和它们绕过图中空洞的方式。一条完整轨迹是许多带方向边的和，所以可以自然投影到边空间。

### 2. 输入、root 与 pseudotime

输入可以是单模态表达的 PCA，也可以是 RNA+ATAC 的 joint embedding。kidney organoid 使用外部 MOJITOO 结果作为 PHLOWER 输入；PHLOWER 本身不学习 MOJITOO。

在细胞表示上先构造带权图和 diffusion map。给定用户指定的 root cells，扩散算子经过若干步后的访问概率用于定义 pseudotime。论文的 kidney 分析先聚类 joint embedding，再选择 day 7 且表达 TBXT、MESP1、KDR5 的 mesoderm 群体作为 root。

Root 是 PHLOWER 的关键监督信息。若选错，早晚方向、终末细胞、人工闭合边、随机游走方向以及最后的树都会一起改变。

### 3. 为什么要把树“闭合”成有洞的复形

树本身没有一维洞，因此一阶 Hodge Laplacian 的调和空间不能直接为每条树枝产生所需的循环信号。PHLOWER 先用 Delaunay triangulation 和距离过滤构造由节点、边、三角形组成的 simplicial complex，再从高 pseudotime 端点向低 pseudotime/root 附近增加人工边。

这样，每条 root-to-terminal 主路径与人工回边形成一个环或“hole”。这里必须把因果顺序说清楚：

1. 算法先根据 pseudotime 选择端点并人为闭合；
2. 闭合后的拓扑产生调和维度；
3. 调和特征再用于区分候选路径。

因此“一个 hole 对应一条生物分支”不是一般拓扑定理，而是依赖 PHLOWER 构图、root、端点与阈值的建模设计。Extended Data Figs. 4–5 用 persistent homology 检查过滤半径和保留下来的洞，为这一构造提供诊断。

### 4. $B_1$、$B_2$ 与一阶 Hodge Laplacian

节点—边 incidence matrix $B_1$ 记录每条有向边从哪个节点离开、进入哪个节点。边—三角形 incidence matrix $B_2$ 记录一条边是否属于一个三角形以及方向是否一致。

未归一化的一阶 Hodge Laplacian 是

$$
L_1=B_1^\top B_1+B_2B_2^\top.
$$

第一项比较共享节点的边，第二项比较共同围成三角形的边。归一化后，PHLOWER 对对称形式 $\mathcal L_1^s$ 做特征分解：

$$
\mathcal L_1^s=Q\Lambda Q^\top.
$$

接近零的特征值对应调和子空间，相关边特征向量组成

$$
H=(u_1,\ldots,u_h)\in\mathbb R^{|E|\times h}.
$$

本地源码直接构造 $B_1/B_2$、归一化 $L_1$，并用 `eigsh(..., which='SM')` 求小特征值。代码与论文有两个值得保留的边界：论文 Eq. 11 的文字符号与后续例子/标准方向约定不一致，而源码采用两条同向边为 $+1$、跨边为 $-1$；源码归一化节点项含 $1/2$ 因子，论文 Eq. 15 的显示式未写出该因子。它们不应被悄悄抹平。

### 5. 一条随机游走怎样变成一个点

算法在 kNN 图上从低 pseudotime 节点出发，只沿 pseudotime/divergence 增加的方向进行 preference random walk。若采样边不在较稀疏的 simplicial complex 中，再用 shortest path 补回 SC 上的路径。

对一条路径 $t$，构造带符号边流 $f^{(t)}$：顺方向经过为 $+1$，逆方向为 $-1$，未经过为 0。投影

$$
H^{(t)}=H^\top f^{(t)}
$$

把整条路径变成 $h$ 维调和坐标。重复采样许多路径后，DBSCAN 在这个 trajectory map 中寻找主要路径群。默认采样数是参数而非固定的生物事实；代码入口支持调整。

MEF 示例有 neuron 和 myocyte 两条主路径。图 1 与 Extended Data Fig. 1 显示两个近零特征值、两组边信号和两个 path clusters，但这种干净的一一对应来自简单示例与构图条件。

### 6. 为什么还需要 cumulative trajectory embedding

整条路径的 $H^\top f$ 忘记了每条边何时被访问。为找 branching point，PHLOWER 对前 $s$ 步累计：

$$
v_s=H^\top\sum_{i=1}^{s}\hat f_{,i}.
$$

每条路径于是变成从原点逐步延伸的曲线。共享祖先阶段的不同路径群在早期靠近，分化后才分开。

算法按 edge pseudotime 对各 trajectory group 同步分箱，在每个 bin 中计算平均 backbone 与组内离散度，再比较归一化组间距离：

$$
d(i,j,k)=\left\|
\frac{\bar b_i^k}{\bar\sigma_i^k}-
\frac{\bar b_j^k}{\bar\sigma_j^k}
\right\|_2.
$$

从晚到早寻找首次距离低于阈值的 bin，作为两组的合并位置；所有 pairwise 分叉点再自底向上组成 tree。源码为估计 bin 内尺度默认有放回抽样 100 个点，因此 Eq. 25 在代码中是近似估计而非对全部点的穷举平均。

### 7. 从路径群到细胞树

构树后，root、terminal points 和 branching points 被转换成 Dynverse milestones。细胞通过其相邻/关联边在 cumulative space 中的位置被分配到 branches，最终可导出 STREAM-compatible tree 进行展示。

这里输出是单根树，意味着方法预设没有真正的环、汇合分化或多个独立 root。即使输入 SC 有许多拓扑结构，最终的生物表示仍被 tree assembly 约束。

### 8. 多模态信息在哪一步发挥作用

PHLOWER 的树主要由 joint embedding 决定。RNA+ATAC 的第二个作用在 regulator prioritization：

- 在树的末端 bins 比较 branch-specific expression；
- 用 chromVAR/scMEGA 类流程得到 TF activity；
- 平滑 gene expression，并计算 activity 与 expression 沿分支的相关性；
- 优先保留两者趋势一致的 TF。

相关性可以减少 motif 相似 TF 带来的歧义，但不能证明 TF 对该分支具有因果作用。论文把 PAX3、RFX4、ZIC2 一起敲低后观察到 neuronal/stromal 减少、tubular/podocyte progenitor 增加以及蛋白标记变化。这支持“三 TF 联合扰动改变 organoid 组成”，不能拆分为三个 TF 各自的独立因果效应，也不能单独验证整棵树的每条边。

### 9. 如何读 benchmark

论文使用 10 个 DLA simulated trees（5–18 branches）和 33 个 Dynverse real datasets。指标分别评估拓扑 HIM、branch 内位置相关性、branch allocation、milestone allocation 和平均 accuracy。

PHLOWER 在作者这套筛选和参数化的复杂树 benchmark 上平均排名领先。但有三条限制：

- 真实集只有 4 个 gold-standard，另 29 个是 silver-standard；
- 仅纳入 single-root 且至少三分支的数据，结论不能外推到 cycle、convergence 或多根结构；
- DLA ground truth 的构建还借助 PHATE 二维表示并人工/算法确定 branch points。

Extended Data Fig. 3 显示资源成本很高：桌面 benchmark 总体约 0.5–12 h、12–40 GB。HPC 子采样图中 30% 数据为 17.7 min/5.6 GB，全量为 151.3 min/35.6 GB，即约 8.6 倍与六分之一内存。图注写 “half” 与图中 0.3 对比不一致，应以主文和绘图数值明确这一文字冲突。

### 10. 全部图像证据怎样串起来

- Figs. 1、Extended 1：算法从 graph、SC、harmonics、path sampling 到 tree 的链条。
- Fig. 2、Extended 2：模拟/真实 benchmark 与具体 pancreas、neurogenesis topology。
- Extended 3：time/memory 与 downsampling trade-off。
- Extended 4–5：persistent homology 对 triangulation threshold 和人工 holes 的诊断。
- Fig. 3、Extended 6–9：kidney multiome tree、markers、TF activity/expression。
- Fig. 4、Extended 10：Xenium 空间数据；树只在每 cluster 2,000 cells 的子集上运行，并非直接处理全部 105,092 cells。
- Fig. 5：三 TF 联合 siRNA、细胞比例和免疫荧光结果。

### 11. 代码与复现边界

本地 `code/` 包含 PHLOWER 0.1.5 的直接 Python 实现、文档 notebook 和 bundled STREAM/third-party code。关键函数与论文路径可逐项对应，但本地快照没有 `.git` provenance，所以 commit SHA 无法确认；`analysis_meta` 应保持 `code_repo_commit=null`。

安装名是 `phlowerpy`，不是 `phlower`：README 与 `setup.py` 都给出 `pip install phlowerpy`。系统还需要 SuiteSparse/CHOLMOD、Graphviz/pygraphviz 等依赖。完整 benchmark 的 reproducibility repository、Zenodo 数据与 R/Dynverse 环境不在本地快照内；本轮没有重新执行高内存 notebook 或全 benchmark。

### 最稳妥的使用边界

PHLOWER 把人为闭合的 SC holes 转成 edge harmonic coordinates，再用随机路径和累计分离重建复杂树。它的优势是直接建模分化事件与路径，而不是只嵌入细胞节点。它的主要风险是 root、图构造、hole creation、harmonic dimension、随机采样、DBSCAN/outlier filtering 与 branch threshold 会级联影响最终树。实际使用时应对这些选择做稳定性分析，并用实验时间、已知 markers、独立模态和 perturbation 分层验证，而不是把零特征值数量直接当作真实分支数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PHLOWER: Hodge Laplacian Trajectory Inference for Complex Multi-Branching Differentiation Trees

**Paper**: Cheng M, Jansen J, Reimer KC, et al. "PHLOWER leverages single-cell multimodal data to infer complex, multi-branching cell differentiation trajectories." *Nature Methods* **22**(11), 2025. DOI: 10.1038/s41592-025-02870-5

**Code**: https://github.com/CostaLab/phlower (v0.1.5, Python)

**Data**: Zenodo 10.5281/zenodo.13860460; GEO accessions GSE302266 (multiome) and GSE302264 (Xenium)

---

### Motivation & Novelty

#### Biological Problem

Cell differentiation produces elaborate trees of cell fates. In kidney organoids, for example, iPSC progenitors give rise to podocytes, tubular epithelial cells, stromal cells, and — undesirably — neuronal and muscle "off-target" cells. Identifying which transcription factors (TFs) govern each lineage decision is critical for improving organoid protocols. Single-cell multiomics (simultaneous RNA and ATAC measurement) provides the richest window into these decisions, but computational methods must be able to (1) recover complex multi-branching trees, and (2) leverage the chromatin accessibility signal.

#### Limitations of Existing Approaches

| Method | Journal/Year | Limitation |
|--------|-------------|------------|
| Monocle3 | *Nature*, 2019 | Fails to connect branches in complex trees (e.g., epsilon/delta pancreas branches disconnected) |
| PAGA tree | *Genome Biol.*, 2019 | Produces false-positive branches on complex data |
| Slingshot | *BMC Genomics*, 2018 | Best for bifurcations; underestimates large tree size |
| STREAM | *Nat. Commun.*, 2019 | Competitive but node-based embedding |
| TSCAN | *Nucleic Acids Res.*, 2016 | Good cell-placement, weaker topology recovery |
| Palantir, MIRA | *Nat. Biotechnol.* 2019; *Nat. Methods* 2022 | Do not infer tree topology |

No prior method was evaluated on trees with >9 branches; the best comprehensive benchmark (*Nat. Biotechnol.* 2019, Saelens et al.) focused on 4–5 branch trees.

#### PHLOWER's Unique Contributions

1. **Hodge Laplacian on simplicial complexes**: First trajectory method to use the first-order HL (operating on edges/transitions) rather than the zero-order graph Laplacian (operating on nodes/cells).

2. **Harmonic eigenvectors as trajectory signatures**: Zero-eigenvalue eigenvectors of the Hodge-1 Laplacian encode one-dimensional holes in the constructed simplicial complex. PHLOWER deliberately creates main-path holes by adding terminal-to-root edges, then uses their harmonic coordinates to separate sampled paths. A generic hole is not automatically a biological branch.

3. **Edge-level trajectory embedding**: Trajectories are embedded as flows (edge-level), not node positions. This naturally handles convergent paths, shared progenitors, and multi-branch topologies.

4. **Multimodal-native**: Directly takes MOJITOO joint RNA+ATAC embeddings as input; no modification required.

5. **First systematic benchmark on complex trees**: Evaluates 12 methods on DLA trees with 5–18 branches and 33 Dynverse datasets with ≥3 branches.

---

### Method Overview

PHLOWER operates in seven phases:

1. **Joint embedding**: MOJITOO (RNA+ATAC) or PCA (RNA-only) produces low-dimensional cell embedding $X^l$.

2. **Diffusion graph + pseudotime**: Self-tuning Gaussian kernel → kNN graph → diffusion process pseudotime $u$ (root cells specified by user).

3. **Simplicial complex**: Delaunay triangulation of graph embedding → distance filtering → artificial terminal→root edges creating $h$ topological holes (one per branch).

4. **Hodge Laplacian decomposition**: Assemble $B_1$ (node-edge), $B_2$ (edge-triangle) → normalized symmetric $\mathcal{L}_1^s$ → `eigsh` → $h$ harmonic eigenvectors $\mathbf{H} \in \mathbb{R}^{|\mathcal{E}| \times h}$.

5. **Trajectory sampling and embedding**: 10,000 KNN preference random walks → edge-flow matrix $F^{(t)}$ → trajectory embedding $H^{(t)} = H^\top F^{(t)}$ → DBSCAN clustering into $m$ groups.

6. **Tree inference**: Cumulative embedding $\mathbf{v}_s$ tracks trajectory divergence over pseudotime → pairwise normalized distance per bin → branching points → bottom-up tree assembly.

7. **Regulator detection**: Branch-specific t-test on high-pseudotime cells (weighted by edge visit count) + chromVAR TF activity correlation filter → ranked list of TFs per branch.

---

### Evaluation

#### Datasets

| Dataset | Cells | Type | Purpose |
|---------|-------|------|---------|
| DLA trees (×10) | 3,000 each | Simulated, 5–18 branches | Benchmark topology recovery |
| Dynverse 33 datasets | 100–30K each | Real scRNA-seq, gold/silver standard | Benchmark cell placement |
| Pancreas progenitor | 3,696 | Real scRNA-seq (Bastidas-Ponce 2019) | Tree quality + runtime |
| Neurogenesis (dentate gyrus) | 18,213 | Real scRNA-seq (La Manno 2018) | Tree quality + runtime |
| Kidney organoid multiome | 13,751 | Real RNA+ATAC (days 7,12,19,25) | Multimodal + biology |
| Xenium kidney organoid | 105,092 | Spatial (100-gene panel) | Spatial validation |
| siRNA organoids | ~25K | Xenium, PAX3/RFX4/ZIC2 knockdown | Perturbation validation |

#### Benchmark Metrics (Dynverse framework)

- **HIM** (Hamming–Ipsen–Mikhailov): tree topology similarity
- **Correlation**: geodesic distance correlation within branches
- **F1 branches**: cell assignment to correct branches
- **F1 milestones**: cell assignment to correct branching points
- **Accuracy**: average of above four

#### Results

| Scenario | PHLOWER | 2nd best | 3rd best |
|----------|---------|----------|----------|
| Simulated data — HIM | **Best** | PAGA | RaceID |
| Simulated data — F1 branches | **Best** | Monocle3 | PAGA |
| Simulated data — Accuracy | **Best** | PAGA | RaceID |
| Real data — HIM | **Best** | Monocle3 | PAGA |
| Real data — F1 branches | **Best** | Slice | Slingshot |
| Real data — Accuracy | **Best** | Monocle3 | pCreode |

Statistical significance confirmed by Friedman–Nemenyi post-hoc test.

**Computational requirements** (Intel i5-10400, 64GB RAM):
- Pancreas (3,696 cells): ~150 min, ~15 GB RAM
- Neurogenesis (18,213 cells): ~600 min (~10h), ~40 GB RAM
- Paper states "0.5–12h and 12–40 GB" for both datasets combined
- With 30% downsampling on the HPC benchmark: 8.6× speedup (151.3 to 17.7 min) and about one-sixth memory (35.6 to 5.6 GB). The Extended Data caption says “half” despite the plotted 0.3 comparison; the plot and main text support 30%.
- Bottleneck: `eigsh` eigendecomposition of the |E|×|E| sparse Hodge Laplacian

**Kidney organoid** (biological validation):
- 9 branches identified from 13,751 multiome cells: 2 podocyte, 1 tubular epithelial, 4 stromal, 1 muscle, 1 neuronal
- TFs WT1, MAFB (podocytes), HNF1B, GRHL2 (tubular) recovered — all literature-validated
- Novel finding: PAX3, RFX4, ZIC2 predicted as neuronal off-target regulators

**siRNA validation**:
- Knockdown of PAX3 + RFX4 + ZIC2 (25–30% reduction in mRNA)
- Xenium spatial profiling: significant decrease in neuronal/stromal cells
- Significant increase in tubular cells and podocyte progenitors
- Immunofluorescence: 50% increase in tubular E-cadherin, increased podocyte nephrin

---

### Reproducibility

**Rating: 3.5/5**

**Strengths**:
- Well-organized Python package (pip installable, v0.1.5 on PyPI)
- Comprehensive readthedocs documentation with tutorials
- 8 Jupyter notebooks covering all major use cases
- Data deposited in Zenodo (Anndata objects with pre-processed results) and GEO (raw)
- Benchmarking data available in Zenodo
- Code is well-structured with AnnData-based API consistent with Scanpy ecosystem

**Weaknesses / Practical considerations**:
- **Memory**: Full analysis requires 40GB RAM for 18K cells — impractical on standard workstations. Downsampling tutorial provided.
- **Runtime**: the paper reports roughly 0.5–12 h and 12–40 GB across the 3.7K- and 18K-cell desktop benchmarks. On a separate HPC node, 30% of the 18K dataset took 17.7 min versus 151.3 min for all cells; hardware differs, so these timings should not be mixed.
- **Root cells must be specified manually**: No automatic root detection. Wrong root = inverted pseudotime + incorrect tree. Users need domain knowledge or prior clustering.
- **`h` selection**: Automatic `knee_eigen` works well for clean datasets but may fail on noisy data; manual override often needed.
- **MOJITOO dependency**: Multimodal analysis requires running MOJITOO (R/Python package) separately. The tutorial notebooks use pre-computed MOJITOO embeddings.
- **chromVAR dependency**: TF activity requires ATAC data processed through ArchR → chromVAR (R packages). Python wrapper available but requires R installation.
- **Reproducibility of benchmark**: Dynverse wrapper requires Docker + R environment for 8 competing methods. The Zenodo archive contains pre-computed results, which simplifies reproduction.
- **scikit-sparse dependency**: Requires system-level CHOLMOD library; can be difficult to install on non-Linux systems.

**Environment setup**:
```bash
pip install phlowerpy  # package name in setup.py/README, version 0.1.5
# Also requires: libsuitesparse-dev (system)
# Optional: R with ArchR, chromVAR for multimodal TF analysis
```

**Data download**:
```python
# Pre-processed AnnData objects with PHLOWER results:
# zenodo.org/records/13860460
# Raw data: GEO GSE302266, GSE302264
```

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
