---
layout: default
permalink: /paper-atlas/slicedmmot-07a783b7/
title: "SlicedMMOT"
nav: false
description: "给定 P 个概率分布 \\mu1,\\ldots,\\muP，多边最优传输（multi-marginal optimal transport, MMOT）要在所有边缘分布固定的联合耦合 \\pi\\in\\Pi(\\mu1,\\ldots,\\muP) 中寻找最低代价： 论文关注的不是任意代价，而是带权二次重心代价。令 \\betap\\ge0、\\sump\\betap=1，则 这个代价衡量每个样本相对联合加权中心的离散程度。"
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
      <span>arXiv preprint · 2021</span>
    </div>
    <h1>SlicedMMOT</h1>
    <p>Sliced Multi-Marginal Optimal Transport</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2102.07115" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SlicedMMOT 中文方法解读：把多边最优传输化成“投影、排序、同分位对齐”

### 1. 论文解决的计算瓶颈

给定 $P$ 个概率分布 $\mu_1,\ldots,\mu_P$，多边最优传输（multi-marginal optimal transport, MMOT）要在所有边缘分布固定的联合耦合 $\pi\in\Pi(\mu_1,\ldots,\mu_P)$ 中寻找最低代价：

$$
\mathcal{MW}^2(\mu_1,\ldots,\mu_P)
=\inf_{\pi}\int c(x_1,\ldots,x_P)\,d\pi.
$$

论文关注的不是任意代价，而是带权二次重心代价。令 $\beta_p\ge0$、$\sum_p\beta_p=1$，则

$$
c(x_1,\ldots,x_P)
=\sum_{p=1}^P\beta_p\left\lVert x_p-\sum_{j=1}^P\beta_jx_j\right\rVert^2.
$$

这个代价衡量每个样本相对联合加权中心的离散程度。标准离散 MMOT 的联合变量会随 $P$ 指数膨胀；SlicedMMOT 的策略是先在一维获得闭式最优耦合，再用随机投影把它提升到高维。

本工作区没有作者代码，CodeGraph 也没有找到 SlicedMMOT 实现。论文仅说明强化学习实验基于外部 simple-pytorch-r1。因此下文是对 paper source/paper/vlm/paper.md、主图 1–5 和同一预印本内附录的源证据解释，不宣称任何本地数值复现。

### 2. 一维核心：同一个分位数同时抽取所有分布

对一维分布 $\mu_p$，记广义分位函数为 $F^{-1}_{\mu_p}(u)$。命题 1 说明，在上述二次重心代价下，最优联合耦合可写为：

$$
U\sim\mathcal U(0,1),\qquad
(X_1,\ldots,X_P)
=\bigl(F^{-1}_{\mu_1}(U),\ldots,F^{-1}_{\mu_P}(U)\bigr).
$$

直觉是：对所有分布使用同一个分位位置 $U$。图 1 左侧把 $[0,1]$ 上的一条竖线映射到每个直方图相应的 bin；右侧连接由相同分位产生的样本组。它不是把数值最近的点贪心配对，而是保持每个分布内部的累积顺序。

若每个分布都是 $N$ 个等权原子，将每组样本分别排序后，第 $n$ 小的样本在所有 $P$ 个分布之间组成一组。对第 $n$ 组，先算加权中心

$$
\bar x_n=\sum_{p=1}^P\beta_p x^{(p)}_{(n)},
$$

再累加

$$
\sum_{p=1}^P\beta_p\lvert x^{(p)}_{(n)}-\bar x_n\rvert^2.
$$

排序主导复杂度为 $O(PN\log N)$。若样本权重不均，仍可用共同 $U$ 与分位函数，但简单“第 $n$ 个对第 $n$ 个”的数组实现不再充分，需要处理累计质量区间。

### 3. 高维切片：每个方向都做一次一维 MMOT

从单位球面 $S^{d-1}$ 采样方向 $\theta$，把 $x$ 投影为 $\langle x,\theta\rangle$。记投影后的分布为 $\theta_\#\mu_p$。论文定义

$$
\mathcal{SMW}^2(\mu_1,\ldots,\mu_P)
=\int_{S^{d-1}}
\mathcal{MW}^2(\theta_\#\mu_1,\ldots,
\theta_\#\mu_P)\,d\Theta(\theta).
$$

实际用 $K$ 个随机方向做 Monte Carlo：

1. 采样并归一化 $\theta_k$；
2. 将每个分布的 $N$ 个样本投影到该方向；
3. 每个分布独立排序；
4. 同 rank 对齐，计算加权重心代价；
5. 对 $K$ 个方向平均。

等权、等样本数情况下复杂度为 $O(KPN\log N)$，内存可通过逐方向计算控制。这里“dimension-free”主要指论文给出的统计样本复杂度界不显式指数依赖 $d$；单次投影仍需计算 $d$ 维内积，所以实际算力与内存不是字面上与维数无关。

### 4. 一个关键恒等式：多边量等于两两 sliced-Wasserstein 的加权和

命题 3 给出

$$
\mathcal{SMW}^2(\mu_1,\ldots,\mu_P)
=\frac12\sum_{i,j=1}^P
\beta_i\beta_j\mathcal{SW}^2(\mu_i,\mu_j).
$$

这说明 SMW 对所有分布共同一致性进行度量，也让拓扑、样本复杂度和 barycenter 性质可从 sliced-Wasserstein 推出。它也带来一个重要解释边界：SMW 在这个二次重心代价下可以分解为两两 SW 的加权和；新算法的计算优势来自对每个切片先求共同重心代价，以 $O(P)$ 汇总，而不是朴素枚举 $O(P^2)$ 对。

论文称它为 generalized metric，因为输入不是一对分布而是一个 $P$ 元组；它为零当且仅当所有参与分布相同。不要把它误解成定义在“单个分布对”上的新普通距离。

### 5. 理论结果应怎样读

- **拓扑**：在论文条件下，SMW 为零刻画所有分布相等，并继承弱收敛相关性质。
- **样本复杂度**：命题 5 把 SMW 的经验估计误差归约到一维 Wasserstein 的误差，因此没有标准高维 Wasserstein 的维数灾难形式。
- **投影复杂度**：有限 $K$ 另引入 Monte Carlo 误差，命题 6 给出典型 $O(K^{-1/2})$ 收敛。常数仍可能受分布和维数影响；图 3c 不能推出对所有任务固定 20 或 50 个方向必然足够。
- **Barycenter**：命题 7 表明，将一个待优化分布加入多边距离并最小化，与 sliced-Wasserstein barycenter 问题相关。
- **梯度**：命题 8 在离散原子互异等条件下给出几乎处处光滑的梯度；排序次序改变或投影出现 ties 时是非光滑边界。自动微分如何处理这些边界、是否用解析梯度，因无代码而无法核实。

图 2 展示一个随机高斯初始分布沿 SMW 梯度流逐渐接近四个目标分布的 sliced barycenter。它是二维视觉示例，不是全局优化收敛定理的实验替代。

### 6. 多任务密度估计：局部拟合与全局共享

对每个损坏目标 $\mu_p$ 学习模型 $\nu_p$：

$$
\min_{\nu_1,\ldots,\nu_P}
\sum_{p=1}^P\mathcal{SW}^2(\mu_p,\nu_p)
+\gamma\mathcal{SMW}^2(\nu_1,\ldots,\nu_P).
$$

第一项保留任务特性，第二项鼓励所有模型共享全局几何。图 4 的嵌套椭圆各自缺失不同 support 片段：

- $\gamma=0$ 时，各模型只复制各自损坏目标；
- 中等 $\gamma$ 可借其他任务补出共同的闭合椭圆结构；
- $\gamma=25$ 时共享过强，任务间方向和宽高差异被压平，趋向共同 barycenter。

因此 SMW 正则不是无条件“修复缺失数据”；它依赖多个任务确实共享结构。若真实任务差异很大，强正则会产生负迁移。

### 7. 多动力学强化学习：把轨迹看成分布

论文用五个重力 $g\in\{8,9,10,11,12\}$ 的 pendulum swing-up 环境。第 $p$ 个 agent 的长度 $T$ 轨迹形成经验分布

$$
\mu_p=\frac1T\sum_{t=1}^T\delta_{x_t^{(p)}}.
$$

总 reward 是环境 reward 加共享 reward；等价地，联合目标中减去 $\gamma\mathcal{SMW}^2(\mu_1,\ldots,\mu_P)$。沿每个投影排序后，与当前状态同 rank 的其他 agent 状态形成跨任务参照。非均匀 $\beta_p$ 可通过环境回报的 Boltzmann 权重提高表现好 agent 的影响，并给无 reward agent 设置下界。

图 5 中两个 agent 没有环境 reward：无共享项时失败，有 SMW 共享时可以学习 swing-up。结果为五次运行的均值和标准差，属于一个小型合成控制实验；不能证明在高维、异构动作空间或非同任务环境中同样有效。论文外部基线仓库只说明 RL 框架来源，不等同 SlicedMMOT 作者代码公开。

### 8. 图证据与适用边界

- **图 1**：验证同分位一维耦合的直观结构。
- **图 2**：展示 barycenter 梯度流行为。
- **图 3a–b**：在论文硬件与 Gaussian 模拟设置下展示对 $N$ 的近 $N\log N$、对 $P$ 的近线性趋势；不是跨硬件基准。
- **图 3c**：展示投影数增加时方差缩小；不同维数曲线说明有限投影常数并非完全无维数影响。
- **图 4**：展示正则强度的 bias–sharing trade-off。
- **图 5**：展示特定 pendulum 设置中 reward 缺失 agent 的知识转移。

论文的补充/附录与主文位于同一 PDF 转换中，包含证明和实验参数，但没有独立 supplement 文件，也没有可执行 artifact。

### 9. 实现与复现边界

这个工作区是 **paper-only**。旧 CLAUDE.md 中约 20 行的 PyTorch 函数是分析者依据论文写的示意代码，不是作者发布、运行或测试过的实现。它还默认每个分布具有相同 $N$ 个等权样本，并省略投影复用、随机种子、设备/dtype、ties、非均匀样本权重和梯度验证。

要做可信复现，至少需要：从论文 Algorithm/公式独立实现；用 $P=2$ 检查与常数缩放后的 SW 一致；用命题 3 的 pairwise 恒等式做数值交叉检查；测试置换不变性、所有分布相同时为零、重复点和不同权重；固定方向与 seed；对 $N/P/K/d$ 分别做计时和误差实验。强化学习还需重建论文未完全锁定的训练环境、Q-learning 网络、随机性和权重更新。

因此本工作区可把数学机制和论文证据讲清楚，但不能把“易于实现”替换为“已复现”。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Sliced Multi-Marginal Optimal Transport

### Paper Metadata

| Field | Value |
|-------|-------|
| **Title** | Sliced Multi-Marginal Optimal Transport |
| **Authors** | Samuel Cohen, Alexander Terenin, Yannik Pitcan, Brandon Amos, Marc Peter Deisenroth, K S Sesh Kumar |
| **Affiliations** | UCL, University of Cambridge, UC Berkeley, Facebook AI Research, Imperial College London |
| **arXiv** | 2102.07115 (February 2021) |
| **Code** | Not released (RL experiments extend [simple-pytorch-r1](https://github.com/xtma/simple-pytorch-r1)) |

---

### Motivation & Novelty

#### The Problem

Multi-marginal optimal transport (MMOT) provides a geometrically principled way to compare $P > 2$ probability measures simultaneously — a natural requirement in multi-task learning, multi-modal alignment, and multi-condition biological analysis. However, existing MMOT algorithms are computationally impractical:

- **Linear programming** scales as $O(N^P)$ — exponential in the number of measures
- **Entropic regularization** [Benamou et al., *SIAM J. Sci. Comput.*, 2015] suffers exponential dependence on dimension $d$ and/or number of measures $P$
- **Low-rank approaches** [Altschuler and Boix-Adserà, *arXiv*, 2020] reduce dependence on $P$ but remain exponential in $d$
- **Pairwise sliced Wasserstein** [Bonneel et al., *J. Math. Imaging and Vision*, 2015; Bonnotte, 2013] has excellent computational/statistical properties but only handles $P = 2$ measures

#### Unique Contributions

1. **Closed-form 1D multi-marginal OT**: Derives an explicit formula for the multi-marginal Wasserstein distance in one dimension using quantile functions (Proposition 1), generalizing the classical sorting-based pairwise result. Complexity: $O(PN\log N)$.

2. **Sliced Multi-Marginal Wasserstein (SMW) distance**: Lifts the 1D result to $\mathbb{R}^d$ via random projections, yielding an $O(KPN\log N)$ distance computation — **linear** in the number of measures $P$ and with **dimension-free** sample complexity.

3. **Comprehensive theoretical analysis**: Proves SMW is a generalized metric inducing weak convergence (same topology as Wasserstein), has dimension-free sample complexity, connects to sliced Wasserstein barycenters, and is differentiable almost everywhere.

4. **Multi-task learning applications**: Demonstrates SMW as a regularizer for multi-task density estimation (shared structure recovers corrupted distributions) and multi-dynamics RL (uninformed agents learn through trajectory sharing).

---

### Method Overview

#### Core Idea

The key insight is that **1D multi-marginal OT has a closed-form solution via quantile alignment**: to optimally couple $P$ one-dimensional distributions, simply sort each distribution and match points at the same rank. This extends the well-known result that 1D pairwise OT is solved by sorting.

The **slicing** technique then lifts this 1D result to high dimensions: project all measures onto random directions, compute the cheap 1D distance for each projection, and average. The resulting **Sliced Multi-Marginal Wasserstein (SMW)** distance inherits both the computational efficiency of sorting and the dimension-free statistical properties of slicing.

#### Algorithmic Pipeline

1. **Input**: $P$ discrete measures $\mu_1, \ldots, \mu_P$ in $\mathbb{R}^d$ with $N$ atoms each
2. **Project**: Sample $K$ random unit directions $\theta_k \in S_{d-1}$, project all measures
3. **Sort**: Sort each projected measure ($O(N\log N)$ per measure)
4. **Compute**: Evaluate 1D MW² via the barycentric cost on sorted atoms
5. **Average**: Monte Carlo average over $K$ projections

**Total complexity**: $O(KPN\log N)$ — dramatically better than $O(N^P)$ for LP-based MMOT.

#### Key Theoretical Results

- **Generalized metric**: non-negative, zero iff all measures equal, permutation-equivariant, generalized triangle inequality
- **Topology**: induces weak convergence, same as standard Wasserstein
- **Sample complexity**: dimension-free, bounded by $\frac{1}{2}\rho(N)$ where $\rho(N)$ is the 1D Wasserstein sample complexity
- **Barycenter equivalence**: the SMW-closest measure to a set is their sliced Wasserstein barycenter
- **Decomposition**: $\mathcal{SMW}^2 = \frac{1}{2}\sum_{i,j}\beta_i\beta_j \mathcal{SW}^2(\mu_i, \mu_j)$ (conceptual, but computationally less efficient)

See `doc_method.md` for full mathematical details and algorithm walkthrough.

---

### Evaluation

#### Scalability Experiments (Figure 3)

| Experiment | Setup | Result |
|-----------|-------|--------|
| Time vs. $N$ | $P = 3, 10, 20$; $d = 10$; $K = 10$ | Confirmed $O(N\log N)$ scaling up to $N = 10^7$ |
| Time vs. $P$ | $N = 500, 5000, 50000$; $d = 10$ | Confirmed linear scaling in $P$ |
| Accuracy vs. $K$ | $N = 250$; $P = 5$; $d = 2, 5, 20$ | Variance shrinks as $O(1/\sqrt{K})$; mean converges with few hundred projections |

#### Multi-Task Density Estimation (Figure 4)

- **Dataset**: Corrupted nested ellipses ($P$ target distributions, each with missing support regions)
- **Metric**: Visual quality of learned distributions
- **Result**: $\gamma = 0$ (no sharing) → models collapse to corrupted targets; $\gamma = 0.3$ → shared structure fills missing regions while preserving task-specific features; $\gamma = 25$ → over-regularization collapses all models to barycenter
- **Setup**: 150 atoms, batch 150, SGD, $K = 20$ projections

#### Multi-Dynamics Reinforcement Learning (Figure 5)

- **Dataset**: 5 pendulum tasks (OpenAI Gym [Brockman et al., *arXiv*, 2016]) with gravities $g \in \{8, 9, 10, 11, 12\}$ m/s²
- **Challenge**: 2/5 agents receive no environment reward
- **Metrics**: Cumulative reward (training curves), final state trajectories
- **Results**:
  - Without sharing ($\gamma = 0$): uninformed agents fail to solve their tasks
  - With uniform SMW sharing: all agents learn, including uninformed ones
  - With **non-uniform Boltzmann weights**: significantly outperforms uniform sharing
- **Compared baseline**: Independent training (no SMW regularization)
- **Setup**: Q-learning, 2-layer MLP, tanh, lr=$2.5 \times 10^{-4}$, batch 32, $T = 200$, $K = 50$, $\gamma = 1$, $\alpha = 1/30$, reward transform $f(y) = e^{-5y}$ following [Dadashi et al., *arXiv*, 2020]

#### Gradient Flow (Figure 2)

Gradient flow $\partial\mu_t = -\nabla \mathcal{SMW}^2(\mu_t, \nu_1, \ldots, \nu_P)$ starting from random Gaussian converges to the sliced Wasserstein barycenter, visually confirming Proposition 7.

---

### Reproducibility

#### Rating: 3/5

**Justification**:
- (+) Mathematical framework is fully specified — all definitions, algorithms, and proofs are given
- (+) Experimental details in Appendix B provide hyperparameters, architecture choices, and setup
- (+) RL experiments build on public [simple-pytorch-r1](https://github.com/xtma/simple-pytorch-r1) repo
- (+) Algorithm is simple (sort + project + average) — straightforward to implement from scratch
- (−) **No public code release** — the main barrier to reproducibility
- (−) Density estimation experiment uses custom corrupted ellipse data without exact specification of corruption
- (−) Some RL details are vague (exact $\epsilon$-greedy schedule, replay buffer size, target network update)

#### Practical Notes

**Implementation considerations**:
- The core SMW computation is ~20 lines of Python/NumPy: project → sort → compute barycentric cost → average
- Gradient computation (Proposition 8) requires tracking sorting permutations — compatible with PyTorch/JAX autodiff if implemented via `torch.sort` which returns indices
- For large $P$, the $O(KPN\log N)$ complexity is favorable; the dominant cost is typically the $N\log N$ sorting

**Key hyperparameters**:
- $K$ (projections): 20–50 is sufficient in practice (Figure 3c)
- $\gamma$ (regularization): problem-dependent; moderate values balance local fidelity and shared structure
- $\beta_p$ (weights): uniform for symmetric problems; Boltzmann for asymmetric (RL with variable rewards)

#### Strengths

1. **Elegant mathematical contribution**: extends the sliced Wasserstein framework to the multi-marginal setting with comprehensive theoretical analysis
2. **Dramatic complexity reduction**: from exponential to $O(KPN\log N)$ — makes multi-marginal OT practical
3. **Strong theoretical foundations**: generalized metric, weak convergence, dimension-free complexity, barycenter connection, differentiability
4. **Intuitive applications**: multi-task density estimation and RL clearly demonstrate the value of SMW regularization

#### Weaknesses

1. **Limited experimental scope**: only two application domains (synthetic density estimation, simple RL), no comparison with other multi-marginal OT methods
2. **No code release**: hinders reproducibility and adoption
3. **Barycentric cost assumption**: results are specific to the Agueh-Carlier cost (Eq. 2); the paper does not establish an extension to other multi-marginal costs
4. **No real-world applications**: all experiments are on synthetic/simple tasks; no demonstration on biological data, large-scale generative models, or complex RL environments
5. **Non-uniform measure sizes**: paper assumes all measures have $N$ atoms — real applications often have varying sample sizes
6. **Limited ablation**: no systematic study of sensitivity to $K$, $\beta$, $\gamma$ beyond the examples shown

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
