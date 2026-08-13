---
layout: default
permalink: /paper-atlas/slingshot-19e4f29d/
title: "Slingshot"
nav: false
wide: true
description: "Slingshot 不直接在单细胞之间连一棵容易受噪声影响的树，而是先在低维空间的细胞簇之间建立最小生成树（MST），把从起始簇到叶簇的路径解释为谱系；随后为每条谱系拟合相互约束的主曲线，用细胞在曲线上的弧长作为伪时间。它把“全局分支拓扑”和“谱系内连续排序”拆成两个问题。"
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
      <span>BMC Genomics · 2018</span>
    </div>
    <h1>Slingshot</h1>
    <p>Slingshot: cell lineage and pseudotime inference for single-cell transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1186/s12864-018-4772-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Slingshot">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/kstreet13/slingshot" target="_blank" rel="noopener noreferrer" aria-label="Open code for Slingshot">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Slingshot 方法解读：先找谱系骨架，再沿平滑分支排伪时间

### 一句话抓住方法

Slingshot 不直接在单细胞之间连一棵容易受噪声影响的树，而是先在低维空间的**细胞簇**之间建立最小生成树（MST），把从起始簇到叶簇的路径解释为谱系；随后为每条谱系拟合相互约束的主曲线，用细胞在曲线上的弧长作为伪时间。它把“全局分支拓扑”和“谱系内连续排序”拆成两个问题。

### 输入与输出

核心输入是同一批 $n$ 个细胞的低维坐标 $X\in\mathbb{R}^{n\times p}$ 与簇标签。标签既可以是硬标签，也可以是 $n\times K$ 的软成员矩阵。用户可指定 `start.clus`，也可用 `end.clus` 把已知终末簇约束为叶节点。

输出包括：簇级 MST、从根到叶的有序簇路径、每条谱系的一条平滑曲线，以及两个 $n\times L$ 矩阵——伪时间与 lineage assignment weights。某个细胞可以同时属于多条共享祖段的谱系，因此可以有多列伪时间。

### 第一阶段：从细胞簇得到谱系拓扑

#### 1. 形状敏感的簇间距离

论文默认采用协方差缩放距离：

$$
d^2(\mathcal C_i,\mathcal C_j)=
(\bar X_i-\bar X_j)^T(S_i+S_j)^{-1}(\bar X_i-\bar X_j),
$$

其中 $\bar X_i$ 是簇中心，$S_i$ 是低维坐标的经验协方差。普通欧氏距离只看两个中心相隔多远；这里还考虑簇沿不同方向的延展形状。若两个细长簇沿同一方向相接，它们可比“中心距离相同但形状不连续”的簇更接近。小簇导致协方差和不可逆时，论文允许退化为对角协方差。

当前源码并未在本仓库重新实现该公式。`getLineages()` 把坐标和成员矩阵交给 `TrajectoryUtils::createClusterMST(..., dist.method="slingshot")`。因此公式与调用点可核实，但依赖包内当前距离实现没有包含在本地代码快照中，不能声称逐行验证。

#### 2. MST 与局部监督

簇作为节点、簇间距离作为边权后，MST 用最小总边权连接各簇。若用户指定终末簇，论文的约束不是预先写死整棵树，而是先在非终末簇上建 MST，再把每个终末簇接到最近的非终末簇。这是一种局部监督：保证已知终态是叶节点，同时仍允许中间分叉由数据决定。

给定根节点后，每条“根到叶”的简单路径就是一条谱系。论文要求用户提供根；本地 2.7.0 代码在未提供时会从每棵树的叶节点中，选择到其他叶节点平均路径长度最大的叶作为启发式根。源码注释也明确说这种自动选择“不推荐”，已知发育起点时应显式指定。

簇数仍决定可发现的拓扑粒度。论文图 5 表明，不同聚类算法下结果相对稳定，但 $K=3$ 时可能根本看不到分叉；$K$ 过高又会产生伪分支。主曲线只能平滑已有骨架，不能补回 MST 已遗漏的拓扑。

### 第二阶段：同时主曲线与伪时间

#### 1. 单条主曲线的投影—平滑循环

每条谱系先由其簇中心依次连接成折线。随后反复执行：

1. 把每个细胞正交投影到曲线，得到投影点与沿曲线从起点累计的弧长 $\lambda_i$；
2. 对每个低维坐标，用 $\lambda_i$ 预测该坐标并平滑，组成更新后的曲线；
3. 再投影，直到细胞到投影点的总距离变化足够小或达到最大迭代数。

曲线采用单位速度参数化，所以参数增量等于弧长增量，伪时间就是 $t_i=\lambda_i$。例如一条二维折线从 $(0,0)$ 到 $(3,0)$，再到 $(3,4)$；若细胞投影在第二段的 $(3,2)$，则伪时间为 $3+2=5$，不是到原点的直线距离 $\sqrt{13}$。因此伪时间表示沿轨迹走过的进程，而非真实分钟或细胞分裂次数。

当前实现以簇中心折线初始化；默认 `extend='y'` 会用很大的 `stretch=9999` 先延展端部，再把所有细胞投影回曲线。每轮以平滑器更新各坐标，默认最多 15 轮；总投影距离的相对变化低于 `0.001` 时收敛。数据超过 150 个细胞时，默认用 150 个曲线点近似以节省计算，最终高精度分析可设 `approx_points=FALSE`。

#### 2. 为什么多条曲线不能独立拟合

若两个命运共享祖细胞，却分别拟合两条普通主曲线，共享细胞可能投影到两个不一致的路径位置。Slingshot 因此构造 simultaneous principal curves：分叉前强制各曲线靠近共同平均曲线，离开共享区域后平滑放松约束。

对同一分叉的 $M$ 条曲线，平均曲线为

$$
\mathbf c_{\mathrm{avg}}(t)=\frac{1}{M}\sum_{m=1}^{M}\mathbf c_m(t).
$$

平均从叶向根递归计算，使早期二分叉的两侧权重相等，不会因为其中一侧后来产生更多末端谱系而偏向它。收缩则反向从根向叶执行：

$$
\mathbf c_m^{\mathrm{new}}(t)=w_m(t)\mathbf c_{\mathrm{avg}}(t)
+[1-w_m(t)]\mathbf c_m(t).
$$

在起点 $w_m(0)=1$，曲线完全重合；经过共享细胞的伪时间区间后，$w_m(t)$ 平滑降到 0，分支自由分开。论文默认用共享细胞非异常伪时间范围和余弦核生存函数构造这一非增权重；源码 `.percent_shrinkage()` 用 boxplot 的 1.5 IQR 边界缩放核生存曲线，`.shrink_to_avg()` 实现上式。

#### 3. 细胞—谱系权重的当前实现

当前代码根据细胞到各曲线的投影距离 $D$ 重加权。它先把距离转换为全局加权秩分位数 $Z$，再计算

$$
W'_{il}=1-Z_{il}^2,\qquad
W_{il}=\frac{W'_{il}}{\max_{l'}W'_{il'}}.
$$

因此一个细胞最贴近的候选谱系权重通常被归一到 1，其他候选按距离秩衰减。默认重分配还会把 $Z<0.5$ 的细胞加入谱系，并在距离高于 90% 分位且权重低于 0.1 时移除共享归属。

这些权重是曲线拟合与谱系归属的几何权重，不是经概率模型校准的“细胞最终走向某命运的概率”，也不是实验观测的祖先—后代关系。下游比较谱系表达趋势时可以使用它们，但解释必须保留这一边界。

### 如何读论文证据

- 图 1 用 HSMM 的 212 个细胞展示单谱系：簇级折线给出方向，主曲线提供连续排序。
- 图 2 的 qNSC 数据在去除异常点后有 101 个细胞，展示共享起始段后分成 IPC 与候选替代终态的两条谱系。
- 图 3 的嗅上皮 616 个细胞展示三个终末命运，并说明少量起点/终点知识如何排除生物学上不合理的 MST。
- 图 4 比较两分支和五分支 Splatter 模拟。评分用修改的 Kendall $\tau$：错误遗漏或多收的 lineage cells 只增加分母，因此同时惩罚排序与归属错误；每条真实谱系取所有推断谱系中的最大值再平均，这又会轻微偏向产生很多分支的方法。
- 图 5 支持“对聚类算法较稳健，但对簇数并非不敏感”的结论。它不是任意数据集上自动找到正确拓扑的保证。

论文还指出 Splatter 的分叉较尖锐，可能不利于假设平滑轨迹的 Slingshot；模拟结果也不是对真实谱系因果关系的验证。

### 论文与本地代码的对应边界

本地仓库是 `slingshot` 2.7.0、提交 `206cc19ca89d985245ca204fbc86772e5c2446d0`，晚于 2018 年论文。

| 机制 | 本地实现 | 对应程度 |
|---|---|---|
| 簇间距离、受约束 MST | `getLineages.R` 调用 `TrajectoryUtils::createClusterMST()` | Partial：调用可见，核心距离在外部依赖 |
| 根到叶路径 | `TrajectoryUtils::defineMSTPaths()`；本地含自动根启发式 | Partial：论文机制存在，现代代码增加行为 |
| 簇中心折线初始化 | `getCurves.R` 的初始化段 | Exact |
| 投影、平滑、重新投影 | `getCurves.R` 主循环与 `princurve::project_to_curve()` | Exact，投影函数来自依赖 |
| 递归平均、收缩 | `.avg_curves()`、`.percent_shrinkage()`、`.shrink_to_avg()` | Exact |
| 伪时间和权重输出 | `TrajectoryUtils::PseudotimeOrdering` 的 assays | 机制一致，输出对象为现代接口 |
| 论文全部基准复现 | 本地包源码 | Not found：没有完整模拟与全部比较方法运行产物 |

CodeGraph 对这批 R 源码没有返回可用符号路径，本次映射因此使用论文正文、图注与直接行号化源码阅读完成。现有证据足以解释算法和实现入口，但没有在本环境重跑论文数据、基准或数值结果。

### 使用时最重要的判断

Slingshot 适合“低维流形大体可信、聚类能表达全局状态、变化沿平滑树状轨迹发生”的问题。实际分析应至少检查：不同降维和簇数下 MST 是否稳定；起始簇是否有实验或标记基因依据；终末监督是否改变关键连接；分叉前不同曲线的伪时间是否一致；以及数据是否存在环、汇合、跳变或彼此独立的多个过程。若这些假设不成立，一条漂亮的曲线仍可能只是几何插值，而不是可信的发育历史。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Slingshot: Summary

### Motivation & Novelty

**Biological problem**: Single-cell RNA-seq data from differentiating cell populations forms a continuum rather than discrete states. Recovering the underlying temporal ordering (pseudotime) and the branching structure of cell fate decisions is essential for understanding development, regeneration, and disease.

**Limitations of prior approaches**:
- **Monocle** (*Nat Biotechnol*, 2014): MST on individual cells → highly unstable under subsampling; requires user to specify number of lineages
- **TSCAN** (*Nucleic Acids Res*, 2016): cluster-based MST (stable) but projects cells onto piecewise linear paths (non-smooth) and uses Euclidean cluster distances (ignores cluster shape)
- **Waterfall** (*Cell Stem Cell*, 2015): similar to TSCAN; requires subsetting data to a single lineage for pseudotime inference
- **Embeddr**: principal curves (smooth and stable) but restricted to a single non-branching lineage
- **Wishbone** (*Nat Biotechnol*, 2016): limited to exactly one branching event (two lineages)
- **DPT** (*Nat Methods*, 2016): many cells receive missing branch assignments (~44% in simulations)
- **Monocle 2** (*Nat Methods*, 2017): finds spurious lineages with increasing cell numbers; 80.3% of datasets with 2 true lineages were assigned 4+ lineages

**Slingshot's novel contributions**:
1. **Two-stage decomposition**: cluster-based MST for lineage topology (stable), simultaneous principal curves for smooth pseudotimes (accurate)
2. **Simultaneous principal curves**: a new algorithm extending single-curve principal curves to arbitrary branching structures while guaranteeing smooth bifurcations and consistent pseudotime values for shared cells
3. **Mahalanobis-like cluster distance**: shape-sensitive distance that accounts for cluster covariance structure when building the MST
4. **Optional local supervision**: user can specify terminal states without restricting discovery of novel lineages — supervision is local, not global
5. **Modular design**: accepts any upstream normalization, dimensionality reduction, and clustering — no lock-in to specific tools

---

### Method Overview

Slingshot operates in two stages:

**Stage 1 — Lineage structure** (`getLineages()`):
- Compute covariance-scaled (Mahalanobis-like) distances between $K$ cluster centroids
- Build a minimum spanning tree on clusters using igraph
- Optional: constrain terminal clusters to a single MST edge (local supervision)
- Extract all root-to-leaf paths as lineages $\mathcal{L}_1, \ldots, \mathcal{L}_L$

**Stage 2 — Pseudotime inference** (`getCurves()`):
- Initialize one curve per lineage as a piecewise linear path through cluster centers
- Iteratively refine curves: smooth each dimension as a function of pseudotime (smooth.spline, df=5), re-project cells, reweight cell assignments using rank-quantile transformation, and shrink branching curves toward their shared average
- Convergence: <0.1% relative change in total projection distance (max 15 iterations)
- Final pseudotimes: arc-length along converged curves; cells not on a lineage receive NA

The method is designed to be modular — it accepts any upstream dimensionality reduction and clustering and returns pseudotime as an $n \times L$ matrix (one column per lineage).

See `doc_method.md` for full mathematical derivation and `doc_code.md` for code-level implementation details.

---

### Evaluation

#### Datasets

| Dataset | Cells | Lineages | Source |
|---|---|---|---|
| HSMM (human skeletal muscle myoblasts) | 212 | 1 | Trapnell et al., *Nat Biotechnol* 2014; GEO GSE52529 |
| qNSC (hippocampal quiescent neural stem cells) | 101 | 2 | Shin et al., *Cell Stem Cell* 2015; GEO GSE71485 |
| OE (olfactory epithelium) | 616 | 3 | Fletcher et al., *Cell Stem Cell* 2017; GEO GSE95601 |
| Splatter simulations (2-lineage) | 120–1500 | 2 | 1,200 synthetic datasets |
| Splatter simulations (5-lineage) | 220–1320 | 5 | 300 synthetic datasets |

#### Evaluation Metric

Modified Kendall's $\tau$: average over lineages of the maximum rank correlation between true and inferred pseudotimes, with denominator expanded to $|\mathcal{S}_0 \cup \mathcal{S}_1|$ pairs (penalizes wrong cell assignments).

#### Key Results

**Stability (HSMM single lineage)**: Monocle paths were highly variable across 50 bootstrap subsamples (Fig. 2). Cluster-based MST methods (TSCAN/Waterfall) and principal curve methods (Embeddr/Slingshot) were both highly stable.

**Multi-lineage accuracy (OE dataset)**: With minimal supervision (HBC as root, mSus as terminal), Slingshot correctly identified all three lineages and the order of bifurcations — later validated experimentally. Monocle 2 identified only 2 lineages with GBC (a transition state) as a terminal. TSCAN also produced only 2 lineages. Wishbone failed even when restricted to 2 lineages.

**Simulation study**:
- **2-lineage case**: Slingshot achieved consistently higher accuracy than Monocle, Monocle 2, DPT, and TSCAN across different upstream dimensionality reductions (Fig. 4c). Monocle had 20% error rate at large sample sizes. Monocle 2 found ≥4 lineages 80.3% of the time.
- **5-lineage case**: Slingshot and TSCAN outperformed other methods. Methods without cluster-based MST (Monocle, Monocle 2, DPT) performed poorly (Fig. 4d).
- **Robustness to clustering** (Fig. 5): Slingshot produced similar accuracy distributions across hierarchical, k-means, and GMM clustering; robust to K (number of clusters) from 4–10. K=3 occasionally misses branching events; very high K introduces spurious branches.

#### Biological Validation

The OE lineage structure inferred by Slingshot (with minimal supervision) matched later experimental validation: sustentacular cells arise via direct conversion from HBCs, while neuronal and microvillous cells require the GBC intermediate state.

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Mature Bioconductor R package (`slingshot`); installable via `BiocManager::install("slingshot")`
- Well-documented with vignettes (two vignettes: standard and conditions)
- All datasets publicly available on GEO (GSE52529, GSE71485, GSE95601)
- Simulation using `splatter` (Bioconductor package `splatter`) is reproducible
- Core algorithm clean and well-tested (testthat suite)

**Weaknesses / Practical Notes**:
- Paper's Eq 1 (Mahalanobis distance) is not in the `slingshot` repo — it's in `TrajectoryUtils`. For full algorithm understanding, users need to also look at that package.
- The paper was published in 2018 (package version ~0.99.x); current package (v2.x) uses `PseudotimeOrdering` output class from `TrajectoryUtils` and has additional features (`embedCurves`, `slingBranchID`) not described in the paper.
- Cell weight formula and reassignment criteria (hidden tricks) are not described in the paper; they affect results but are only discoverable via code reading.
- No simulation code distributed — the paper's simulation comparison requires substantial implementation effort to reproduce.

**Environment setup**:
```r
# R >= 4.0, Bioconductor >= 3.13
BiocManager::install("slingshot")
# Or from GitHub (development version):
devtools::install_github("kstreet13/slingshot")
```

**Key parameters to tune**:
- `start.clus`: always specify if known (strongly affects trajectory direction)
- `end.clus`: optional but improves accuracy when terminal states are known
- `approx_points`: set to FALSE for final analysis (default 150 saves time but slightly reduces precision)
- `shrink`: set to 0 if all lineages are truly independent (no shared progenitor)
- Upstream: K (number of clusters) should be ≥ 4 for reliable branching detection; PCA with ≥ 4 dimensions often outperforms 2D

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
