---
layout: default
permalink: /paper-atlas/velotree-6699cf6d/
title: "VeloTree"
nav: false
description: "VeloTree 的核心不是直接比较两个细胞当前的表达或速度，而是先从每个细胞沿 RNA 速度场向过去回溯一条积分曲线，再用有向 varifold 距离比较两条曲线共享了多少历史、又从哪里开始分开，最后把两两距离交给 family-joining 重建分化树。 它的输入是每个细胞的表达向量 xi 与 RNA 速度 vi；输出是以观测细胞为节点的树拓扑，以及由树深度归一化得到的伪时间。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>VeloTree</h1>
    <p>VeloTree: Inferring single-cell trajectories from RNA velocity fields with varifold distances</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2604.02380" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeloTree 方法解释：把 RNA 速度场中的“回溯路径”变成细胞树

### 一句话抓住方法

VeloTree 的核心不是直接比较两个细胞当前的表达或速度，而是先从每个细胞沿 RNA 速度场**向过去回溯一条积分曲线**，再用有向 varifold 距离比较两条曲线共享了多少历史、又从哪里开始分开，最后把两两距离交给 family-joining 重建分化树。

它的输入是每个细胞的表达向量 $x_i$ 与 RNA 速度 $v_i$；输出是以观测细胞为节点的树拓扑，以及由树深度归一化得到的伪时间。后者只表达树上的先后层级，不等于真实物理时间，也不等于积分曲线弧长。

### 为什么不能只比较当前状态

两个处于同一分化阶段的细胞，表达位置可能很接近，速度方向也可能相似，但“当前位置的欧氏距离”无法表达树路径的双曲式结构。反过来，仅用速度与细胞间位移的相关性，又容易把同阶段、共同向前运动的细胞误判为很不相似。

VeloTree 把一个细胞从根到当前状态的历史看成一条曲线。若两个细胞属于同一分支，它们的回溯曲线应长时间重合；若属于不同分支，曲线只在较早的祖先部分重合。于是比较整条曲线，比比较一个点更接近“树上两节点之间的路径长度”。

### 从原始速度场到树：四步流水线

#### 1. 降维、平滑并投影速度场

论文先把表达降到 $d<30$ 个 PCA 分量。速度必须用同一个线性映射变换，代码中的等价操作是比较 `PCA(x + v)` 与 `PCA(x)`，而不是重新对速度单独做 PCA。

原始速度含噪，方法用扩散平滑减弱局部波动；随后在每个细胞附近估计数据流形的局部切空间，把速度投影到该空间中，避免积分轨迹离开细胞实际占据的低维流形。邻域由半径 $r$ 定义，不足时补足到至少 $k$ 个近邻。论文建议观察平均局部维度随 $r$ 的变化，在其低点附近选半径；扩散时间也结合半群准则和可视化人工选择。因此这些参数不是完全自动学习出来的。

这一步对应论文图 1–3：图 1 是原始场，图 2 显示平滑后的场，图 3 展示切空间投影后的方向。

#### 2. 从每个细胞向过去积分

对第 $i$ 个细胞，以当前位置 $x_i$ 为起点，沿负速度方向求解

$$
\dot\gamma_i(t)=-\frac{\sum_j K(\gamma_i(t),x_j)v_j}{\sum_j K(\gamma_i(t),x_j)},
\qquad
K(z,x_j)=\exp\!\left(-\frac{\|z-x_j\|^2}{\sigma^2}\right).
$$

负号很关键：RNA 速度指向未来，VeloTree 需要恢复从共同祖先到当前细胞的历史，所以反向积分。分式是 Nadaraya–Watson 核回归：轨迹走到观测点之间时，用附近细胞的速度加权插值。

一个小例子：若当前位置附近两个细胞的平滑速度分别为 $(1,0)$ 和 $(0,1)$，核权重为 $0.8$、$0.2$，插值得到未来方向 $(0.8,0.2)$；反向积分一步则沿 $(-0.8,-0.2)$ 回到更早状态。

`integrate.py` 使用显式 Euler 步进，最多 5000 步；轨迹越出数据边界或速度范数小于 $10^{-3}$ 时停止。最后按弧长重新采样，目标约为每条曲线 100 个点，减少不同积分步数对后续距离的影响。论文图 4 展示每个细胞得到的一条回溯曲线。

#### 3. 用有向 varifold 比较曲线

离散曲线被写成一组线段；每段用中点 $c_p$、有向差向量 $u_p$ 与长度 $\|u_p\|$ 表示。两条曲线的内积近似为

$$
\langle\mu_{\gamma_i},\mu_{\gamma_j}\rangle
=\sum_{p,q}\|u_p\|\,\|u_q\|
\exp\!\left(-\frac{\|c_p-c_q\|^2}{\sigma_x^2}\right)
\exp\!\left(-\frac{\|\hat u_p-\hat u_q\|^2}{\sigma_t^2}\right).
$$

第一个核比较线段位置，第二个核比较有向切线；线段长度使表示对曲线参数化和采样密度更稳健。距离矩阵元素是

$$
D_{ij}=\|\mu_{\gamma_i}-\mu_{\gamma_j}\|^2
=\langle\mu_i,\mu_i\rangle-2\langle\mu_i,\mu_j\rangle+
\langle\mu_j,\mu_j\rangle.
$$

若两条历史曲线大部分重合，$D_{ij}$ 小；若它们很早就分开，位置和切向核的共同响应变小，距离增大。论文的理论结果是在几何假设成立且核带宽趋于合适极限时，这个平方距离近似目标树上的可加路径距离。它不是对任意噪声、环或汇聚拓扑的无条件保证。图 5 用理想树解释这种对应，图 6 左列到中列展示距离矩阵如何显出分支结构。

代码 `varifold_distance.py` 与公式直接对应：先构造线段中点与差向量，再用两个高斯核计算所有曲线对。一个实现细节是，只有一个点的退化曲线会随机补一个极短线段；这会让极端退化样本产生随机性。代码对零长度切向量也没有显式保护，因此这类输入需额外检查。

#### 4. 用 family-joining 从距离矩阵建树

标准 neighbor-joining 通常假定观测只在叶节点，但单细胞快照中，早期、中间和末端状态都可能被采样。VeloTree 因此使用 family-joining：它反复寻找最接近的一对节点，并判断两者是兄弟、还是父子关系。

论文原算法允许为兄弟节点引入未观测的共同父节点；本实现明确取消了这个选项，总是从观测细胞中选一个最合适的父节点，以得到较小的全观测节点树。`family_joining.py` 的 `GetTreeTopology(D, eps)` 实现这一过程，示例笔记本取 `eps = mean(D) / 10`。

树得到后，从选定根节点计算每个细胞的图深度，再线性缩放到 $[0,1]$ 作为伪时间。例如深度为 $0,1,2,3$ 的四层节点会得到 $0,1/3,2/3,1$。因此同一层的细胞可有相同伪时间，即使它们的曲线长度不同。图 6 右列展示重建树，图 7 比较伪时间排序。

### 实验告诉我们什么

论文用 dyngen 生成三类数据：二分叉、三分叉和双二分叉，每组 500 个细胞、100 个基因。报告的排序准确率分别为 88.6%、93.1% 和 92.4%，并与 VeTra、CellPath 比较。图 6 说明距离矩阵与树能恢复主要分支；论文同时指出，少数积分失败的异常点会在建树时被接到根附近，dyngen 的局部循环动力学也可能生成次级小枝。

图 8 的小鼠胰腺案例恢复了主要内分泌谱系，但也暴露了树假设的边界：alpha 细胞可能具有双来源/汇聚关系，纯树不能忠实表达“两个来源汇到同一终点”，只能把它们拆到两个分支中。这个结果应理解为主要层级的近似，而不是对所有谱系关系的完整拓扑证明。

### 论文与本地代码的对应

| 机制 | 对应实现 | 结论 |
|---|---|---|
| 反向核插值积分与弧长采样 | `VeloTree_code/integrate.py` | **Exact**：方程、负方向、Euler 停止条件和重采样均可直接定位 |
| 有向 varifold 平方距离 | `VeloTree_code/varifold_distance.py` | **Exact**：位置核、切向核、长度权重和距离展开一致 |
| family-joining，观测节点可作父节点 | `VeloTree_code/family_joining.py` | **Exact**：`GetTreeTopology` 实现论文变体 |
| 模拟与胰腺工作流 | `simulated.ipynb`、`pancreas.ipynb` | **Exact / Notebook**：数据读取、参数和绘图由笔记本串联 |
| 扩散时间、邻域半径等自动调参 | 论文规则与笔记本参数单元 | **Partial**：有诊断准则，但最终仍依赖人工观察和逐数据集设定 |
| 可安装包、命令行入口、自动测试 | 本地代码快照 | **Not found**：仓库是研究笔记本与函数模块，不是封装好的软件包 |

本地代码来自 `https://github.com/elodiemaignant/VeloTree`，快照提交为 `8a78c0b8bb17a7adcf9291d1fd6e64529cff9cd5`。工作区 CodeGraph 用于定位核心调用路径，最终判断仍由论文原文和上述直接源文件核对。

### 使用时最容易忽略的边界

1. VeloTree 假定一个共同根的分化树；环、汇聚轨迹和多个独立根不在当前模型内。
2. 好的树依赖先得到可信 RNA 速度。速度估计的偏差会依次影响平滑、积分、曲线距离和建树。
3. 多个带宽、邻域和离散化参数按数据集人工选择，论文结果不能被理解为完全无监督、免调参。
4. 积分场远离观测点时，高斯权重可能同时下溢；当前代码没有分母保护。退化曲线的随机补线段也会影响严格复现。
5. family-joining 强制内部节点由观测细胞承担，得到的是紧凑近似树，不等于证明真实生物学祖先恰好被测到。
6. 工作区没有独立补充材料 Markdown；本解释使用主论文（含其后部材料）、图注和提交快照代码，没有把缺失证据补写成确定事实。

### 推荐阅读顺序

先看论文图 1–4，理解“场如何变成每个细胞的一条历史曲线”；再看图 5 和上面的 varifold 公式，理解共享历史为何转成树距离；最后看图 6–8，区分模拟数据上的结构恢复与真实数据中树假设的边界。代码阅读则按 `integrate.py` → `varifold_distance.py` → `family_joining.py` → 两个主笔记本的顺序最清楚。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeloTree summary.md

### Motivation & Novelty

**Biological problem**: Reconstructing differentiation trees from single-cell RNA sequencing data is a fundamental challenge in developmental biology. The goal is to determine how progenitor cells branch into specialized cell types, and to order cells along these developmental trajectories (pseudotime inference).

**Why existing methods fall short**:
- **Slingshot** (BMC Genomics, 2018) and **Monocle** (Nature Methods, 2017) use minimum spanning trees of k-NN graphs, which are highly sensitive to noise and require supplementary principal curve fitting.
- **VeTra** (Bioinformatics, 2021) and **CellPath** (Cell Reports Methods, 2021) use RNA velocity but rely on Pearson correlation-based dissimilarity measures that over-separate cells at the same developmental stage, and fail to assign pseudotime to a significant fraction of cells.
- **CellRank** (Nature Methods, 2022) and **Palantir** (Nature Biotechnology, 2019) identify branches or leaf probabilities but do not directly reconstruct the full differentiation tree topology.
- None of these methods use distance-based tree inference, which is well-established in phylogenetics and theoretically more robust to noise.

**Unique contributions**:
1. First application of distance-based tree inference (from phylogenetics) to single-cell trajectory inference.
2. Novel cell dissimilarity measure: squared varifold distance between integral curves of the RNA velocity field — with theoretical guarantees that it approximates path distances on the target tree.
3. Comprehensive preprocessing pipeline for RNA velocity fields (diffusion smoothing + tangent projection) with data-driven parameter selection.
4. Adaptation of the family-joining algorithm (Molecular Biology and Evolution) to handle observed internal nodes (all cells, not just leaves).

---

### Method Overview

VeloTree is a four-step pipeline:

1. **Dimensionality reduction**: PCA to $d < 30$ components, projecting both expression profiles and RNA velocities.

2. **Velocity field preprocessing**:
   - *Diffusion smoothing*: Apply a heat operator (diffusion map, Markov normalization) to average velocities of nearby cells. Diffusion time $t_{\text{diff}}$ selected by the semigroup criterion.
   - *Tangent projection*: Project velocities onto the local tangent bundle of the expression point cloud. Neighborhood radius $r$ chosen to minimize average local dimension (targeting the 1D trajectory regime).

3. **Backward integration**: For each cell, integrate the preprocessed velocity field backward using Nadaraya-Watson kernel regression (Eq. 8), recovering the cell's developmental history as an integral curve $\gamma_i$.

4. **Varifold distance + tree inference**: Compute the pairwise squared varifold distance matrix $\Delta_{ij} = d_{W^*}(\gamma_i, \gamma_j)^2$ (Eq. 9), then infer the differentiation tree using family-joining with threshold $\varepsilon = \text{mean}(\Delta)/10$.

**Key biological assumption**: The integral curves of the RNA velocity field, integrated backward, converge toward a common root — reflecting the assumption that all observed cells originate from a common progenitor.

**Key technical assumption**: The tree embedding satisfies three geometric conditions (Assumptions 1-3): spatial separation increases along paths, angular separation increases at branches, and branches deviate fast enough from their initial direction.

---

### Evaluation

#### Datasets

| Dataset | Type | N cells | n genes | Source |
|---|---|---|---|---|
| Bifurcating | Simulated (dyngen) | 500 | 100 | dyngen library (Nature Communications, 2021) |
| Trifurcating | Simulated (dyngen) | 500 | 100 | dyngen library |
| Double bifurcating | Simulated (dyngen) | 500 | 100 | dyngen library |
| Mouse pancreatic endocrine | Real scRNA-seq | ~1000 | ~2000 | Bastidas-Ponce et al., Development 2019 |

#### Metrics

- **Average % well-ordered cells**: For each branch, compute the fraction of cell pairs correctly ordered by pseudotime. Average over all branches. This metric avoids the parameterization mismatch between dyngen pseudotime (arc length) and VeloTree pseudotime (tree depth).

#### Results

| Method | Bifurcating | Trifurcating | Double bifurcating |
|---|---|---|---|
| VeloTree (ours) | **88.6%** | **93.1%** | **92.4%** |
| VeTra (Bioinformatics, 2021) | 36.4% | 57.2% | 70.1% |
| CellPath (Cell Reports Methods, 2021) | 44.8% | 78.5% | 74.4% |

VeloTree substantially outperforms both baselines. The gap is partly explained by VeTra and CellPath failing to assign pseudotime to a significant fraction of cells (shown in gray in Fig. 7), which automatically counts as wrong ordering for those cells.

#### Real data (pancreas)

On the mouse pancreatic endocrine dataset, VeloTree correctly identifies the major differentiation branches (pre-endocrine → β-cells; ε-cells → α-cells) and provides evidence for the dual origin of α-cells (from both pre-endocrine cells and ε-cells), consistent with prior biological knowledge (Yu et al., Cell Research, 2021).

---

### Reproducibility

**Rating: 3/5**

**Justification**: The core algorithm is fully implemented and the code is publicly available. However, the pipeline is entirely notebook-based with no installable package or CLI, and several key parameters require manual tuning via visual inspection of diagnostic plots.

**Strengths**:
- All four core modules (`integrate.py`, `varifold_distance.py`, `family_joining.py`, `visualization.py`) are clean, well-structured Python.
- Simulated datasets are provided as `.rds` files in the repository.
- The pancreas dataset is available via scVelo's built-in data loader.
- Parameter settings for all experiments are documented in Table 2.

**Weaknesses**:
- No installable package (no `setup.py`, `pyproject.toml`, or pip-installable structure).
- Full pipeline only accessible via Jupyter notebooks — no standalone scripts.
- Semigroup criterion for $t_{\text{diff}}$ requires visual inspection of the SGE curve; no automatic threshold.
- Discretization step must be set manually per dataset (no automatic computation from data).
- Requires R (via `rpy2`) for reading `.rds` files and for the VeTra comparison.
- No unit tests.

**Environment setup**:
```bash
conda env create -f environment.yml
conda activate velotree
# Also requires R with princurve package for VeTra comparison
```

**Common pitfalls**:
- The `rdata` Python package is needed to read `.rds` files without R.
- The `rpy2` patch (`VeTra.patch`) must be applied for VeTra compatibility with newer rpy2 versions.
- For real datasets (e.g., pancreas), choosing the radius $r$ is significantly harder than for simulated data due to higher noise levels — the local dimension curve may not show a clear minimum.
- Integration can be slow for large N (O(N²T) complexity) — the bifurcating dataset with N=500 takes several minutes.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
