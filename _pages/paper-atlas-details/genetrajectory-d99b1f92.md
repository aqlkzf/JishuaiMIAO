---
layout: default
permalink: /paper-atlas/genetrajectory-d99b1f92/
title: "GeneTrajectory"
nav: false
description: "GeneTrajectory 要解决的问题不是“给每个细胞分配一个统一的伪时间”，而是：当同一批细胞同时经历分化、细胞周期等多个过程时，能否把参与不同过程的基因程序拆开，并分别给这些基因排序。 这一区别很重要。若分化轴和细胞周期轴彼此独立，细胞实际位于一个至少二维的状态空间中；强行压成一条细胞伪时间会把两个过程混在一起。GeneTrajectory 转而比较每个基因在整个细胞流形上的空间分布。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>GeneTrajectory</h1>
    <p>Gene trajectory inference for single-cell data by optimal transport metrics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-024-02186-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GeneTrajectory">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/KlugerLab/GeneTrajectory" target="_blank" rel="noopener noreferrer" aria-label="Open code for GeneTrajectory">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeneTrajectory 中文方法解读

### 先说清楚：它排序的是基因，不是细胞

GeneTrajectory 要解决的问题不是“给每个细胞分配一个统一的伪时间”，而是：当同一批细胞同时经历分化、细胞周期等多个过程时，能否把参与不同过程的基因程序拆开，并分别给这些基因排序。

这一区别很重要。若分化轴和细胞周期轴彼此独立，细胞实际位于一个至少二维的状态空间中；强行压成一条细胞伪时间会把两个过程混在一起。GeneTrajectory 转而比较每个基因在整个细胞流形上的空间分布。分布相近、且能以较低代价相互搬运的基因，在“基因空间”中也应靠近，由此形成线性、分支或环形的基因轨迹。

因此，最终得到的 gene pseudoorder 表示一个基因程序内部的相对表达次序。它不是细胞年龄，不自动等同于转录调控因果链，也不能仅凭排序断言前一个基因调控后一个基因。

### 第一步：把细胞状态空间变成运输地图

论文先对表达矩阵做常规预处理和降维，再在细胞嵌入上构造 $k$ 近邻图。两个细胞 $u,v$ 的距离不是环境空间中的直线距离，而是图上的最短路径距离 $d_G(u,v)$。

直观上，细胞图像一张有道路的地图。即使两个细胞在二维投影上看起来很近，只要中间没有真实细胞状态连接，运输就不能穿过空白区域抄近路。论文希望这个图距离近似细胞流形上的测地距离，并把它作为后续最优传输的单位成本。

本地 R 代码中，`GetGraphDistance()` 用 `FNN::get.knn()` 建图，再用 igraph 计算无向图的全对最短路径；若图不连通则直接报错并提示增大 $K$（`GeneTrajectory/R/GetGraphDistance.R:18-38`）。这说明 $K$ 不只是平滑参数，也决定运输空间是否连通。

### 第二步：把每个基因变成细胞图上的概率分布

对基因 $i$，论文将其在细胞 $u$ 中的表达量 $g_i(u)$ 归一化为

$$
\rho_i(u)=\frac{g_i(u)}{\sum_{v=1}^{m}g_i(v)}.
$$

这样，一个基因不再只是长度为 $m$ 的表达向量，而成为细胞图上的概率质量。若某基因主要在某一段状态中表达，它的概率质量就集中在那一片细胞节点上。实际使用前必须过滤总表达为零或证据极弱的基因，否则该归一化没有定义或非常不稳定。

两个基因 $i,j$ 的差异定义为 Wasserstein-$p$ 距离：

$$
\delta^{(p)}(\rho_i,\rho_j)
=\min_{F\in\Pi_{\rho_i,\rho_j}}\langle F,C\rangle^{1/p},
\qquad C_{uv}=d_G(u,v)^p.
$$

$F_{uv}$ 表示把多少表达质量从细胞 $u$ 搬到细胞 $v$；它的行和、列和分别受两个基因分布约束。这个距离同时考虑“表达在哪里”和“沿真实细胞流形要搬多远”。两基因即使逐细胞相关性不高，只要其表达峰沿同一生物过程相邻，运输代价仍可能较小。

这里的 R 代码可以粗粒化输入或载入 Python 预计算的 `emd.csv`，却不能仅靠当前代码目录从表达矩阵生成完整 Wasserstein 距离矩阵（`coarse.grain.R:19-50`；`LoadGeneDistMat.R:16-22`）。

为降低最优传输成本，论文提供两种近似：

1. 将细胞按嵌入聚成 meta-cells，并以 $M^TCM$ 得到粗粒化运输成本；本地 `coarse.grain()` 对表达矩阵和图距离执行这一聚合。
2. 先在粗粒度上估计基因近邻，只在候选近邻间计算精细 Wasserstein 距离。后者属于缺失的 Python 后端。

meta-cell 数越少计算越快，但会丢失局部状态分辨率；稀疏化越强，越可能漏掉应相连的基因。它们是精度与成本的权衡，而非无损加速。

### 第三步：从基因距离构造基因几何

有了基因间距离后，论文使用局部自适应高斯核：

$$
A_{ij}=\frac12\left[
\exp\!\left(-\frac{\delta_{ij}^2}{\sigma_i^2}\right)
+\exp\!\left(-\frac{\delta_{ij}^2}{\sigma_j^2}\right)
\right],
$$

其中 $\sigma_i$ 是基因 $i$ 到第 $K$ 个近邻的距离。局部带宽使高密度区和低密度区可以采用不同尺度。`diffusion.map()` 逐行计算核、对称化，并对称归一化后做特征分解；扩散坐标还乘以特征值的 $t$ 次幂（`diffusion.map.R:25-70`）。`GetGeneEmbedding()` 去掉平凡特征向量，留下可视化和端点搜索所用的非平凡坐标。

这里得到的是基因的流形表示：线性过程应形成一条路径，分化过程可形成分支，周期过程可形成环。图 2 的模拟展示了环、分叉、圆柱上的线性加周期，以及多级分支加周期；关键证据不是“细胞被排成一条线”，而是不同生成过程在基因嵌入中被拆成不同拓扑。

### 第四步：逐条抽取轨迹，再在轨迹内排序

对树状基因图，`ExtractGeneTrajectory()` 顺序提取轨迹：

1. 在尚未分配的基因中，选扩散嵌入到原点最远者作为端点种子。
2. 将单位概率质量放在种子上，沿行归一化随机游走矩阵扩散 $t$ 步。
3. 保留扩散质量大于 `quantile × 最大质量` 的基因；默认阈值为 0.02。
4. 移除已选基因，在剩余图上重复，直到取得用户指定的 $N$ 条轨迹或提前耗尽基因。

这些操作可直接在 `ExtractGeneTrajectory.R:22-70` 对照。$N$ 和每条轨迹的 `t.list` 都由用户给定，因此轨迹数量与覆盖范围不是完全由数据自动决定：$t$ 越大，扩散通常覆盖更宽；阈值越低，纳入的基因通常更多。顺序提取也意味着先提取的轨迹会影响后续候选集合。

每条轨迹内部再截取 Wasserstein 距离子矩阵、重算 diffusion map，并按第二个特征向量排序。`GetGenePseudoorder()` 若发现端点种子落在排序前半段，就把特征向量方向翻转（`GetGenePseudoorder.R:19-39`）。因此正向和反向本来是谱坐标的符号不确定性；代码用选定端点统一方向，并不是从数据中识别出绝对时间箭头。

### 如何从图中读证据

- 图 1 给出“细胞图 → 基因分布间 OT → 基因图 → 基因轨迹”的完整桥接关系。
- 图 2 是方法能力的核心受控证据：在单一周期、分叉以及多个并发过程的模拟中，基因嵌入恢复相应的环、树或相互分离的程序。论文用已知真值的基因顺序评估，而不是只凭视觉判断。
- 图 3 在髓系数据中得到三条与不同细胞状态相关的基因程序；gene-bin score 把有序基因分箱后再映射回细胞 UMAP，用于观察程序沿细胞状态空间的分布。
- 图 4–5 在胚胎皮肤数据中分离 dermal condensate 分化、lower dermis 分化和细胞周期，并比较 WT 与 Wls 缺失条件。这里的生物学结论还依赖 FISH、EdU 和已知 Wnt/SHH 标志物，不是排序算法单独提供的因果证明。
- 图 6 将 GeneTrajectory 与先推断细胞伪时间、再按表达峰给基因排序的方法比较。论文报告其在同时含线性与周期过程的模拟上更稳健；这支持“并发过程下直接建模基因几何”的设计，但不等于对所有数据集都必然优于所有轨迹方法。

`AddGeneBinScore()` 将每条轨迹按伪序等分为若干基因箱，并计算每个细胞中该箱基因的非零表达比例（`AddGeneBinScore.R:21-60`）。因此这些图上的 bin score 是下游可视化摘要，不是新的细胞轨迹推断结果。

### 代码与论文的真实对应边界

当前 R 仓库对论文步骤 1、3、4 的实现对应较清楚：细胞图最短路径、局部自适应 diffusion map、端点扩散式轨迹提取、EV2 基因排序和 gene-bin 可视化均能找到直接代码。模拟函数也覆盖论文使用的 cyclic、bifurcation、cylinder 和 coral 结构。

但完整复现仍有三个边界：

- 最核心的基因概率归一化、Wasserstein 求解和基因稀疏化不在本地 R 仓库，而在外部 Python 项目。
- 本地仓库未见自动化测试套件。这里验证的是论文—代码映射与静态实现逻辑，不是数值结果复算。

### 使用时最值得检查的参数

- 细胞图 $K$：过小会断图；过大可能跨越局部流形结构。
- meta-cell 数 $N$：越小越快，但运输成本近似越粗。
- 基因核 $K$：决定局部带宽和基因图连接尺度。
- 轨迹数 `N`、扩散步数 `t.list`、阈值 `quantile`：共同决定提取多少程序以及每条程序纳入哪些基因。
- 排序方向：需要借助端点标志物或外部生物学知识解释，不能把谱向量符号当成天然时间方向。

最稳妥的使用方式，是先把 GeneTrajectory 当作“并发基因程序的候选分解器”，再用已知标志物、独立实验、条件扰动和重复数据验证每条轨迹的身份、方向与生物学含义。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeneTrajectory — Summary

**Paper**: "Gene trajectory inference for single-cell data by optimal transport metrics"
**Journal**: Nature Biotechnology, 2024
**DOI**: 10.1038/s41587-024-02186-3
**Authors**: Rihao Qu, Xiuyuan Cheng, ..., Richard A. Flavell, Peggy Myung, Yuval Kluger (Yale)

---

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing enables reconstruction of gene expression dynamics by ordering cells along developmental or activation trajectories ("pseudotime"). A fundamental assumption of all cell trajectory methods (Monocle 2/3, Slingshot, PAGA, CellRank) is that the underlying biological process can be parameterized by a single latent variable — i.e., the cell manifold is effectively one-dimensional.

This assumption breaks down when cells simultaneously undergo **multiple independent processes** (e.g., differentiation + cell cycle, or differentiation + circadian rhythm). In these cases, cells form a product manifold (intrinsic dimension > 1) — a cylinder (linear × cyclic) or more complex shapes. No single pseudotime can describe all cells fairly; inferring gene dynamics from such a mixed pseudotime yields erroneous or blurred gene orderings.

#### Limitations of Prior Approaches

- **Monocle 2** (Nat. Methods 2017): DDRTree dimensionality reduction; requires specifying starting cell; fails on multi-process data.
- **Monocle 3** (Nature 2019): Learns principal graphs; handles branching but not orthogonal co-occurring processes.
- **Slingshot** (BMC Genomics 2018): Fits principal curves to clusters; sensitive to mixing of concurrent processes.
- **PAGA** (Genome Biol. 2019): Graph abstraction at cluster level; loses intra-cluster gene dynamics.
- **CellRank** (Nat. Methods 2022): Uses RNA velocity; computationally expensive; requires spliced/unspliced counts.
- **Regression-based CC correction**: Regressing out cell cycle effects does not reliably disentangle gene programs — validated experimentally in this paper (Extended Data Fig. 5).

#### What's New

1. **Gene-space trajectory inference**: GeneTrajectory constructs trajectories of genes rather than cells, bypassing the need for cell pseudotime entirely.
2. **Optimal transport on cell graph**: Using graph-based Wasserstein distances between gene expression distributions leverages cell geometry without requiring one-dimensional parameterization of the cell manifold.
3. **Automatic process deconvolution**: Multiple concurrent processes (even orthogonal ones like differentiation + cell cycle) naturally emerge as separate gene trajectories in the gene embedding.
4. **No specification of start/end states**: Unlike cell trajectory methods, GeneTrajectory requires no user-specified initial or terminal cell states.

---

### Method Overview

GeneTrajectory operates in four steps:

1. **Cell graph construction**: Build a kNN graph of cells in reduced-dimensional space (PCA → diffusion map). Compute all-pairs shortest-path distances as the ground metric for optimal transport.

2. **Gene-gene Wasserstein distances**: Normalize each gene's expression to a probability distribution over cells. Compute the Wasserstein-p distance (default: Earth Mover's Distance, p=1) between all pairs of gene distributions, using the cell graph distances as the transport cost. Cell graph coarse-graining (k-means, m'=1000 meta-cells) and gene graph sparsification (αk nearest neighbors) accelerate this step from infeasible to minutes.

3. **Gene embedding and trajectory extraction**: Transform gene-gene Wasserstein distances into a diffusion map embedding. Extract gene trajectories sequentially by diffusing probability mass from the most "extreme" gene (farthest from origin in spectral space) through the gene graph. Genes receiving mass above a threshold (τ₀=0.02) belong to that trajectory. Repeat iteratively.

4. **Gene ordering**: Recompute diffusion map on the Wasserstein submatrix for each extracted trajectory. The second (first non-trivial) eigenvector provides the pseudotemporal ordering of genes along that trajectory.

**Key biological assumption**: A progressive biological process is governed by a temporally ordered gene cascade — genes are activated and deactivated in sequence. This temporal sequencing implies that consecutive genes share similar expression patterns (overlapping distributions) → small Wasserstein distance.

See `doc_method.md` for mathematical details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Simulation Experiments

Four simulation scenarios with ground-truth gene pseudoorders (10 replicates each):
- Cyclic process (CC): ring-shaped cell manifold, 500 genes
- Linear differentiation with bifurcation: tree-shaped manifold, 1000 genes
- Linear differentiation + CC (cylinder, intrinsic dim=2): 5000 cells, 1000 genes
- Multi-level lineage + CC (coral, intrinsic dim=2): 10500 cells, 800+ genes

**Metric**: Spearman correlation between inferred and ground-truth gene order.

**Results** (Fig. 6a,b): GeneTrajectory achieves the highest Spearman correlation across all cell counts (500–2500) and sparsity levels (2.5%–20% nonzero entries). Advantage is especially pronounced for the cyclic process, where cell trajectory methods fail fundamentally. Also tested with negative binomial count model across dispersion levels (Supp. Fig. 1): robust across all settings.

**Wasserstein vs other metrics** (Supp. Fig. 4): Earth Mover's Distance outperforms Euclidean, Pearson, Spearman, Cosine, Total Variation, Jensen-Shannon, and Hellinger distances for gene ordering at all sequencing depths.

#### Real-World Example 1: Human Myeloid Differentiation

- **Dataset**: 10× PBMC 10k v3 (public), ~myeloid cells extracted, 4 cell types
- **Result**: 3 gene trajectories identified — (1) early CD14+ monocyte maturation, (2) CD16+ monocyte differentiation, (3) dendritic cell (type-2) differentiation
- **Biological validation**: Known markers (CLEC5A, CCR2 for early monocytes; CSF1R, ICAM2 for CD16+; CCR5, CD1C, CLEC10A for dendritic cells) appear at the expected pseudotemporal positions
- **Key advantage**: No need to specify starting cell states; processes deconvolved automatically

#### Real-World Example 2: Mouse Skin Dermal Condensate Genesis

- **Dataset**: Novel scRNA-seq from E14.5 mouse embryonic skin (WT and Wls knockout), n=8 WT and n=9 KO embryos
- **Result**: 3 trajectories — dermal condensate (DC) differentiation, lower dermis (LD) differentiation, cell cycle (CC)
- **Biological validation**: DC trajectory correctly orders Wnt targets (Dkk1, Grem1, Lef1), SHH targets (Gli1, Ptch1), and mature DC markers (Sox2, Sox18, Foxd1)
- **Key finding**: Wls KO cells fail to progress past stage 4 of DC differentiation (when Wnt/SHH signaling activates), with higher G1 fraction and lower EdU incorporation — validated by FISH (n=4 embryos)
- **Comparison**: Slingshot, Monocle 2/3, PAGA, and CellRank all failed to correctly order DC differentiation genes; CC regression did not resolve the issue

---

### Reproducibility: 3/5

**Justification**: The method is clearly described and the R package is functional. However, several barriers reduce reproducibility:

**Strengths**:
- R package (KlugerLab/GeneTrajectory) is publicly available with detailed vignettes
- Processed Seurat objects available on Figshare (doi: 10.6084/m9.figshare.25243225)
- Novel mouse skin dataset on GEO (GSE255534)
- Simulation functions cover all paper scenarios

**Barriers**:
- **R/Python split**: Step 2 (Wasserstein distances) requires a separate Python package (`pip install gene-trajectory`), not obvious from paper text
- **Interactive parameter tuning**: Number of trajectories N and diffusion time `t` per trajectory must be determined interactively by inspecting the gene embedding — no automated procedure
- **Version discrepancy**: Paper reports v0.1.0, GitHub has v1.0.0 — changes between versions are undocumented
- **ALRA imputation**: Used in visualization scripts but not mentioned in paper
- **Environment**: Seurat 4.x, mgcv 1.9-0, etc. (specific versions in reporting summary); R ≥ 4.0 required

**Setup** (estimated 30–60 min for new user):
1. `devtools::install_github("KlugerLab/GeneTrajectory")` (R package)
2. `pip install gene-trajectory` (Python OT package)
3. `reticulate::use_virtualenv('gene_trajectory')` (R-Python bridge)
4. Download processed Seurat objects from Figshare
5. Run `human_myeloid_example.R` or `mouse_dermal_example.R`

**Common pitfalls**:
- Cell kNN graph disconnected → increase K (error raised by code)
- Wrong diffusion steps t → too few: truncated trajectory; too many: absorbs noise genes
- Gene filter too strict/lenient → too few genes for trajectory, or too many uninformative ones
- Python POT version: README recommends installing from GitHub master branch (latest version)

---

### Strengths and Weaknesses

**Strengths**:
- Mathematically principled: Wasserstein distance respects cell manifold geometry
- Works without cell pseudotime or specification of start/end states
- Naturally handles concurrent orthogonal processes
- Provides both gene ordering AND gene-to-cell-state mapping (gene bin plots)
- R package is well-structured with simulation functions for benchmarking

**Weaknesses**:
- Directionality of trajectories is not inferred — must be determined biologically post-hoc
- Branch identification is interactive and potentially unstable when branches differ in length/size
- Genes participating in multiple processes colocalize with uninformative genes in gene embedding
- Computational cost is still significant for large datasets without coarse-graining
- No automated selection of number of trajectories or diffusion time parameters
- Limited to sequential processes; cannot model oscillatory dynamics within a single trajectory

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
