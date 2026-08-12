---
layout: default
permalink: /paper-atlas/hiref-a4e077a3/
title: "HiRef"
nav: false
description: "HiRef（Hierarchical Refinement）用一连串小规模低秩最优传输问题，逐层把两个等大小点集切成互相对应的块，直到每个块只剩一对点，从而得到一对一的 Monge 映射。它避免保存完整的 n\\times n 代价或耦合矩阵，在适用的代价分解与秩计划下实现线性空间和近 O(n\\log n) 时间。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>ICML 2025 (oral) · 2025</span>
    </div>
    <h1>HiRef</h1>
    <p>Hierarchical Refinement: Optimal Transport to Infinity and Beyond</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2503.03025" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HiRef 方法中文解读

### 一句话理解

HiRef（Hierarchical Refinement）用一连串小规模低秩最优传输问题，逐层把两个等大小点集切成互相对应的块，直到每个块只剩一对点，从而得到一对一的 Monge 映射。它避免保存完整的 $n\times n$ 代价或耦合矩阵，在适用的代价分解与秩计划下实现线性空间和近 $O(n\log n)$ 时间。

### 它解决的不是普通低秩近似

给定等大小点集 $X=\{x_i\}_{i=1}^n$ 与 $Y=\{y_j\}_{j=1}^n$，离散 Monge 问题要找置换 $T$，最小化

$$
\frac1n\sum_{i=1}^n c(x_i,T(x_i)).
$$

Sinkhorn 通常处理稠密 $n\times n$ 耦合；低秩 OT 只保存 $O(nr)$ 因子，却会把一个点的质量分给多个目标点，不能直接给出双射。HiRef 不把一次低秩解当最终答案，而把它当成“哪些源点和目标点应进入同一子问题”的分区器。

### 理论支点：低秩因子共同聚类真正配对点

内边缘固定为均匀向量 $g=\mathbf1_r/r$ 时，秩 $r$ 耦合可写成

$$
P=Q\operatorname{diag}(1/g)R^\top.
$$

$Q,R$ 的行分别描述两侧点对潜在簇的归属。Proposition 3.1 说明：在均匀边缘、存在 Monge 映射、代价满足严格 $r$-Monge separability，且最优 $Q^\star,R^\star$ 是硬分区时，真实配对 $x$ 与 $T^\star(x)$ 会获得相同标签。

这不是对任意低秩数值解的无条件保证。命题依赖最优性、代价可分性和硬分区；论文只在 $r=2$ 的特殊情形证明最优因子自动形成硬分区。正确理解是：低秩解在这些条件下提供可递归利用的共簇不变量。

### 层次细分怎样产生双射

初始只有共簇对 $(X,Y)$。第 $t$ 层以秩 $r_t$ 的低秩 OT 将每个现有共簇同时切成 $r_t$ 个子簇，并将两侧同编号子簇配对。有效秩为

$$
\rho_t=\prod_{s=1}^t r_s,
$$

每个块容量为 $n/\rho_t$。若 $\prod_t r_t=n$ 且 `base_rank=1`，最终得到 $n$ 个单元素共簇，每个索引对就是一条双射。

代码 `HR_OT.py:208-308` 直接实现主循环：`F_t` 保存 `(idxX, idxY)`；每个块调用低秩求解器得到 $Q,R$；再生成 `F_tp1`。默认返回索引对列表，只有请求 `return_as_coupling=True` 才物化稠密矩阵。大规模使用若要求稠密返回，会重新引入二次存储。

### 秩计划与输入硬条件

同一个 $n$ 可以使用不同因子分解。大秩减少层数但每次低秩求解更贵，小秩增加层数与子问题数量。`rank_annealing.py:59-108` 用动态规划选择秩序列，最小化部分乘积和对应的调用成本。

当前实现明确要求 $|X|=|Y|$（`HR_OT.py:97,182`），并依赖秩计划使容量可整除。它不是非平衡 OT，也不会自动为不等样本数补点、删除点或重新估计边缘权重。

### 论文黑盒与默认求解器不是一回事

理论算法假定 Problem 7 的最优、均匀 $g$ 的 LROT 黑盒。仓库提供直接固定均匀 $g$ 的 `LR_mini.LROT_opt/LROT_LR_opt`，但主入口默认使用更一般的 FRLC。FRLC 是非凸求解器，默认 `tau_in=100000` 强烈约束内边缘接近均匀，却不等于理论上硬固定 $g$。

`HR_OT.py:315-366` 在代价低秩化时调用 `FRLC_LR_opt`，末端小块则显式计算距离并用完整代价求解器。默认参数包含 `gamma=90`、外循环 30 次及内层 Sinkhorn 上限 300。README 也说明低秩求解器采用随机初始化，结果可能随运行略变。因此，论文保证不能被改写成“默认数值实现一定找到全局最优 Monge map”。

### 默认 soft 分区是工程增强

论文算法按 $Q,R$ 行最大值形成硬标签。代码默认 `clustering_type='soft'`：按每列得分取固定容量 top-k，并移除已经分配的点，以保证两侧子簇等大（`HR_OT.py:261-282`）。选择 `hard` 才执行逐行 argmax，并断言每簇容量正确（`284-298`）。

soft 模式使 FRLC 的软输出能够继续递归，但它是顺序相关的贪心平衡策略，并不满足 Proposition 3.1 原始的最优硬分区假设。它与论文核心流程相容，却不是理论步骤的逐字实现。

### 线性内存来自代价因子化

直接传入完整 $C$ 仍需 $O(n^2)$ 内存。可扩展路径是 `init_from_point_clouds`。平方欧氏距离利用

$$
\|x-y\|^2=\|x\|^2+\|y\|^2-2x^\top y
$$

构造精确低秩因子，并在全局缓存后对子簇索引；普通欧氏距离使用论文引用的随机低秩近似。实现位于 `HR_OT.py:456-512`。因此“线性空间”要求走点云/因子化路径，并输出匹配列表或标量成本，而不是完整代价和耦合矩阵。

### 图与实验的证据链

Figure 1 展示从粗共簇到单点配对的层次结构。Figure 2 在 half-moon/S-curve 上显示 HiRef 在与 Sinkhorn、ProgOT 重叠区间保持相近原始 OT cost，并继续扩展到约一百万点。Figure 3 对照 HiRef、Sinkhorn barycentric map 和小规模 simplex 精确映射，突出双射与熵平滑映射的形态区别。Figure 4 在 MERFISH 脑切片之间仅按空间坐标配对，再迁移 $Slc17a7$ 表达。

补充实验还覆盖 MOSTA 时序切片与 128 万 ImageNet embedding。ImageNet 支持通用可扩展性，不是生物结论；MERFISH 迁移依赖预先空间注册与基因的空间结构，也不能推出任意基因都能准确预测。具体图证据见 `figure_analysis.md`。

### 生物应用边界

HiRef 是通用 OT 求解器，不直接建模基因调控、细胞命运或批次效应。MOSTA 需要先标准化并在共同 PCA 空间定义代价，MERFISH 需要先做切片配准。算法输出点对，生物解释取决于代价、预处理与下游指标。

本地 `preprocess_embryo.py` 默认 PCA 30 维，而论文实验使用 60 维；参数虽可调整，但默认运行不等于论文配置。DeST-OT 等方法可把 HiRef 当可扩展后端，那些上层模型的时空约束不能算作 HiRef 自身组成。

### 版本与复现边界

- 本地 `code/` 没有可核验的 Git commit，不能把快照绑定到某个上游修订。
- 仓库缺少锁定环境；核心需 PyTorch，验证还依赖 JAX/OTT、NumPy/SciPy，生物预处理涉及 Scanpy/AnnData。
- 实验主要在 notebooks 与外部 MOSTA、MERFISH、ImageNet 数据上；当前快照并未提供全部论文产物的统一入口。
- 主类中 `parallel=True` 对应的方法仍抛出 `NotImplementedError`；另有独立并行脚本，但接口没有统一。
- README 明确指出论文精确参数在 OpenReview，且当前默认超参数已经变化。复现论文数值必须使用论文/OpenReview 配置。

### 最终理解

HiRef 的创新是把低秩 OT 从最终近似耦合变成层次分区工具，利用共同聚类性质逐层得到单点双射。可扩展性来自局部子问题、代价因子化和稀疏匹配输出。理论依赖严格条件与最优硬分区，而默认代码采用非凸 FRLC 与 soft top-k 平衡化；所以应表述为“核心层次算法与论文高度对应并有大规模实现”，而不是“任意数据与默认参数下都保证恢复精确 OT”。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## HiRef — Hierarchical Refinement for Scalable Optimal Transport

**Paper:** "Hierarchical Refinement: Optimal Transport to Infinity and Beyond"
**Authors:** Peter Halmos, Julian Gold, Xinhao Liu, Benjamin J. Raphael (Princeton University)
**Venue:** ICML 2025 (oral)
**arXiv:** 2503.03025
**Code:** https://github.com/raphael-group/HiRef

---

### Motivation & Novelty

**Biological problem:** Optimal transport is a principled method for aligning cell populations across time points, conditions, or biological replicates in single-cell and spatial transcriptomics. It is used for trajectory inference (Waddington-OT, Cell 2019), spatiotemporal atlas alignment (DeST-OT, Cell Systems 2025), and cell perturbation prediction (moscot, Nature 2025). However, all these methods are fundamentally constrained by the scalability of the underlying OT solver.

**Why existing methods fall short:**
- **Sinkhorn algorithm** (NeurIPS 2013): quadratic space $O(n^2)$ and time $O(n^2 \log n)$. A 100k-cell dataset requires ~80 GB for the coupling matrix. Sinkhorn and ProgOT (NeurIPS 2024) cannot run beyond ~18k cells.
- **Mini-batch OT** (AISTATS 2018; ICML 2020, 2021): linear complexity but incurs significant bias — each mini-batch alignment is a poor approximation of the global coupling, accumulating errors across batches.
- **Neural OT methods** (ICML 2020; Nature Methods 2023): parametrize the Monge map as a neural network, avoiding the coupling matrix, but have noted limitations recovering faithful maps.
- **Low-rank OT / LOT** (ICML 2021; NeurIPS 2022, 2023): linear space and time with $O(nr)$ complexity, but by definition computes a rank-$r$ coupling — cannot produce a bijection. A rank-40 coupling fractionally assigns each cell to 40 others.

**What HiRef contributes:**
1. **Theoretical:** Proposition 3.1 proves that optimal low-rank OT factors co-cluster source-target Monge pairs — a structural invariant that allows iterative refinement to converge to the bijective Monge map.
2. **Algorithmic:** The Hierarchical Refinement (HiRef) algorithm uses this invariant to build a multiscale partition hierarchy via repeated low-rank OT sub-calls, culminating in an exact bijection.
3. **Practical:** $O(n)$ space and $O(n \log n)$ time with no approximation bias, scaling to over 1 million points — two orders of magnitude beyond Sinkhorn.

**Key distinction from Gerber & Maggioni (JMLR 2017):** That work also uses multiscale OT but (i) requires pre-specified multiscale partitions (e.g., dyadic cubes), (ii) assumes geometric structure in the data. HiRef constructs partitions adaptively from the data itself using low-rank OT, operating intrinsically without a fixed mesh.

---

### Method Overview

HiRef solves the assignment problem between two equally-sized point clouds $X, Y \subset \mathbb{R}^d$ with $|X| = |Y| = n$.

**Core idea:** Run low-rank OT with fixed uniform inner marginal $\mathbf{g} = (1/r)\mathbf{1}_r$ between $X$ and $Y$. The optimal factors $(\mathbf{Q}^\star, \mathbf{R}^\star)$ simultaneously cluster $X$ into $r$ groups and $Y$ into $r$ groups, such that group $k$ in $X$ maps (under $T^\star$) exactly to group $k$ in $Y$. Recurse on each paired group until singletons are reached.

**Algorithm (5 steps):**
1. Compute rank schedule $(r_1,\ldots,r_\kappa)$ with $\prod r_i = n$ via dynamic programming, minimizing the total number of LROT solver calls.
2. Initialize trivial partition $\Gamma_0 = \{(X, Y)\}$.
3. At each scale $t$: for every co-cluster pair $(X_q, Y_q) \in \Gamma_{t-1}$, solve a rank-$r_t$ LR-OT sub-problem to obtain $(\mathbf{Q}, \mathbf{R})$.
4. Assign each point to a cluster via argmax of $\mathbf{Q}$ (resp. $\mathbf{R}$) rows, creating $r_t$ child pairs per co-cluster.
5. Final $\Gamma_\kappa$ contains $n$ singleton pairs $(x_i, T^\star(x_i))$ — the bijective Monge map.

**Implementation:** LROT sub-solver is the FRLC algorithm (Halmos et al., NeurIPS 2024). Low-rank cost factorization for squared Euclidean ($d+2$ exact factors) or Euclidean distance (Indyk et al., COLT 2019 approximation) avoids storing the $n \times n$ cost matrix.

**Key assumptions:** Both datasets must have the same number of points. The cost must be strictly convex (or more generally, satisfy $r$-Monge separability) for the theoretical guarantee.

---

### Evaluation

#### Datasets

| Dataset | Size | Task |
|---|---|---|
| Synthetic (Half-moon/S-curve, Checkerboard, MAF Moons/Rings) | 64–1,048,576 pts | Scalability and primal OT cost benchmark |
| MOSTA mouse organogenesis (spatial transcriptomics) | 5.9k–121k cells per stage | Temporal alignment E9.5–E16.5 |
| MERFISH mouse brain (Vizgen) | ~84k spots per slice | Cross-replicate expression transfer |
| ImageNet ILSVRC (ResNet50 embeddings) | 1.28M × 2048-d | Large-scale alignment benchmark |

#### Compared Methods

| Method | Venue | Type |
|---|---|---|
| Sinkhorn | NeurIPS 2013 | Full-rank, entropic |
| ProgOT | NeurIPS 2024 | Full-rank, progressive entropic |
| Mini-batch OT | AISTATS 2018; ICML 2020, 2021 | Mini-batch approximation |
| LOT (Low-rank Sinkhorn) | ICML 2021 | Low-rank |
| FRLC | NeurIPS 2024 | Low-rank (LC-factorization) |
| MOP (Gerber & Maggioni) | JMLR 2017 | Multiscale |
| Dual revised simplex | Mathematical Programming Computation 2018 | Exact LP (≤512 pts) |

#### Key Results

**Synthetic scalability (Fig. 2):**
- HiRef matches Sinkhorn and ProgOT in primal OT cost on all sample sizes where all methods run (64–16,384 pts).
- Sinkhorn and ProgOT fail beyond 16,384 points (memory).
- HiRef scales linearly to **1,048,576 points** — >2 orders of magnitude beyond Sinkhorn.
- HiRef outputs exactly $n$ non-zero coupling entries (bijection); Sinkhorn outputs 600k–680k for $n=1024$.

**Synthetic quality (Fig. 3):**
- HiRef achieves competitive primal cost vs. dual revised simplex (exact solver) on small instances.
- HiRef slightly lower primal cost on 4/6 synthetic benchmarks vs. Sinkhorn.
- MOP (Gerber & Maggioni) has 2× higher cost on Checkerboard and significantly worse on other datasets.

**MOSTA temporal alignment (Table 1):**
- Sinkhorn/ProgOT cannot run beyond E10.5 (18,408 cells).
- HiRef achieves **lowest OT cost across all 4 late-stage timepoints** (E12–E16.5, 51k–122k cells).
- HiRef cost consistently below mini-batch OT (all batch sizes 128–2048) and FRLC/LOT.

**MERFISH brain alignment (Fig. 4, Table S7):**
- HiRef cosine similarity for $Slc17a7$ gene transfer: **0.8098** vs. FRLC 0.2373, LOT 0.3390, MOP 0.5211, mini-batch 0.7434.
- HiRef achieves highest cosine similarity across all 5 tested genes.

**ImageNet (Table 2):**
- 1.281M × 2048-d embeddings; HiRef OT cost **18.97** vs. FRLC 24.12, mini-batch (best) 19.58.
- ProgOT, Sinkhorn, LOT cannot run due to memory constraints.

---

### Reproducibility

**Rating: 3/5**

**Justification:**
- Code is publicly available and well-structured; core algorithm is fully implemented in `src/`.
- All experiments are in Jupyter notebooks, not in library code — individual experiment reproducibility requires knowing the correct notebook and parameters.
- No `requirements.txt` or `setup.py`; dependencies must be inferred from imports (PyTorch, NumPy, SciPy, scikit-learn, ott-jax, scanpy, anndata).
- MOSTA data available from the original Chen et al. (Cell 2022) paper; MERFISH data available from Vizgen public datasets. Preprocessing scripts provided.
- Paper reports PCA dimension as 60 for MOSTA; code default in `preprocess_embryo.py` is 30 (configurable).
- A recommended JAX port exists (https://github.com/peterhalmos/HiRef) which may have additional optimizations.

**Strengths:**
- Clean, modular code structure; easy to swap LROT solvers.
- The `soft` clustering mode handles imperfect convergence gracefully in practice.
- Point-cloud interface avoids materializing large cost matrices.

**Weaknesses:**
- Parallelized version (`HR_OT_parallelized.py`) raises `NotImplementedError` in the main class.
- FRLC solver is nonconvex — guarantees from Proposition 3.1 require an optimal LROT, which is not provided.
- Memory-efficient factored distance computation requires selecting appropriate `distance_rank_schedule`; documentation on choosing this is limited.
- Large-scale GPU experiments (>100k points) are sensitive to `max_iter`, `gamma`, `tau_in` settings; no hyperparameter guidance beyond defaults.

**Common pitfalls:**
- n must not be prime (rank schedule requires factorization). Use `max_rank=n` for prime n but this defeats scalability.
- `clustering_type='hard'` can fail with an assertion error if LROT does not converge to a hard partition at the chosen number of iterations. Default `soft` mode is safer.
- MOSTA preprocessing requires h5ad files from the MOSTA database; only the preprocessing script is provided, not the data.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
