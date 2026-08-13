---
layout: default
permalink: /paper-atlas/cellrank-91fc27a4/
title: "CellRank"
nav: false
wide: true
description: "CellRank 不把二维 UMAP 上的速度流线当作发育路线，而是在高维表达邻域中建立一个有方向的马尔可夫链：RNA velocity 决定“更可能往哪个邻居走”，表达相似性限制“只能沿细胞流形走”；随后用 GPCCA 把数千个细胞粗粒化成初始、中间和终末宏状态，再计算每个细胞最终被不同终末状态吸收的概率。 输入是单细胞表达矩阵、KNN 图和 RNA velocity（也可换成其他方向信息）；"
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
      <span>Nature Methods · 2022</span>
    </div>
    <h1>CellRank</h1>
    <p>CellRank for directed single-cell fate mapping</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-021-01346-6" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellRank">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/cellrank" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellRank">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellRank 方法解释：把局部 RNA 速度累积成全局命运概率

### 一句话理解

CellRank 不把二维 UMAP 上的速度流线当作发育路线，而是在高维表达邻域中建立一个有方向的马尔可夫链：RNA velocity 决定“更可能往哪个邻居走”，表达相似性限制“只能沿细胞流形走”；随后用 GPCCA 把数千个细胞粗粒化成初始、中间和终末宏状态，再计算每个细胞最终被不同终末状态吸收的概率。

输入是单细胞表达矩阵、KNN 图和 RNA velocity（也可换成其他方向信息）；核心输出是细胞间转移矩阵、宏状态及软归属、初始/终末状态、每个细胞对各终末命运的概率，以及由这些概率支持的谱系驱动基因和表达趋势。

### 为什么“看速度箭头”不够

RNA velocity 是局部的一阶预测：它告诉我们一个细胞此刻表达变化的方向，却不直接给出几百步以后会到哪个终点。把高维速度投影到 UMAP/t-SNE 还会扭曲距离和方向，平滑后的流线容易显得比原始证据更确定。CellRank 的思路是只在高维 KNN 邻域内使用速度，把很多局部、带噪的转移连续累积成全局到达概率。

论文明确依赖四个假设：状态变化通常是渐进的；采样覆盖了中间状态而没有大缺口；平均动力学可近似为无记忆马尔可夫过程；RNA velocity 至少对足够多的关键驱动基因近似表达的一阶导数。CellRank 能缓冲局部噪声，但不能从系统性错误的 velocity 或缺失的中间细胞中恢复真实轨迹。

### 1. 从表达邻域和速度得到有向转移矩阵

#### 先限定允许走向的邻居

每个观测细胞是马尔可夫链的一个微状态。CellRank 先在 PCA 表达空间建立 KNN 图；只有图上的相邻细胞之间才允许转移。这个无向图保留表型流形的全局拓扑，防止速度把细胞推到表达上完全不相似的状态。

#### 再用速度给邻边定方向

对细胞 $i$ 和邻居 $j$，令表达位移为

$$
\delta_{ij}=x_j-x_i,
$$

计算速度 $v_i$ 与位移 $\delta_{ij}$ 的 Pearson 相关 $c_{ij}$，然后经 softmax 变成概率：

$$
p^{(v)}_{ij}=\frac{\exp(\sigma c_{ij})}
{\sum_{k\in N(i)}\exp(\sigma c_{ik})},
\qquad
\sigma=\frac{1}{\operatorname{median}(|c_{ij}|)}.
$$

相关越高，邻居越位于速度预测方向上。自动尺度 $\sigma$ 用全图相关绝对值的中位数校准 softmax。v1.5.1 源码在 `VelocityKernel.compute_transition_matrix()` 中先以确定性模式计算相关矩阵，再执行 `1 / median(abs(cmat.data))`。

举例：某细胞有三个邻居，相关为 $(0.8,0.2,-0.4)$；若 $\sigma=2$，softmax 权重大约是 $(0.72,0.22,0.06)$。它不是选择唯一后继，而是保留一个随机转移分布。

#### 混合方向与相似性

仅依赖 velocity 可能放大噪声，因此再与由 KNN 连通性行归一化得到的 $P_s$ 混合：

$$
P=(1-\lambda)P_v+\lambda P_s.
$$

论文分析常用小比例连接性权重；v1.5.1 高层 `transition_matrix()` 的默认值是 `weight_connectivities=0.2`，即 80% velocity、20% connectivity。源码还默认对 connectivity kernel 做 diffusion-pseudotime 式密度校正。由于每行和为 1，$P_{ij}$ 可解释为从细胞 $i$ 一步走到 $j$ 的概率。

图 1a–c 与扩展数据图 1 展示从 KNN、速度到转移矩阵的过程；扩展数据图 4 说明矩阵按细胞原顺序看似无结构，按宏状态重排后才显出块结构。

### 2. 速度不确定性怎样进入转移概率

论文把细胞速度视为随机向量

$$
v\sim\mathcal N(\mu,\Sigma_v),
$$

其中均值和对角方差由 KNN 内速度的一阶、二阶矩估计。若 $h(v)$ 表示“速度→邻居转移概率”的相关加 softmax 映射，则二阶 Taylor 近似为

$$
E[h_i(v)]\approx h_i(\mu)+\frac12\sum_g
H^{(i)}_{gg}\operatorname{Var}(v_g).
$$

一阶项因围绕均值展开而消失；JAX 自动微分计算 Hessian 对角。源码 `_run_stochastic()` 精确实现 `p_0 + 0.5 * H_diag.dot(variance)`，随后把近似造成的负值裁剪到 $[0,1]$ 并重新归一化。也可用 Monte Carlo 采样近似期望，代价更高。

这里存在重要版本/默认值边界：论文叙述把分析近似称为默认的不确定性传播方案，但 v1.5.1 的 `VelocityKernel.compute_transition_matrix()` 和旧高层 `transition_matrix()` 参数默认均为 `mode="deterministic"`；必须显式选择 `mode="stochastic"` 才走 Hessian 路径，选择 sampling/Monte Carlo 才采样。故“源码具备该机制”是 Exact，“该快照默认自动启用”则不成立。扩展数据图 3 比较确定性、分析近似和采样，显示高噪声区域差异最大；它证明近似与采样在示例中接近，不是对所有数据的误差保证。

### 3. GPCCA：从细胞微状态到可解释宏状态

单细胞转移矩阵巨大且非对称。普通用于可逆过程的谱聚类不合适，因为有向链可能产生复特征向量。CellRank 采用 GPCCA，以实 Schur 分解提取接近特征值 1 的慢动力学子空间：

$$
P=QRQ^\top.
$$

取 $n_s$ 个 Schur 向量 $\widetilde Q$，寻找旋转矩阵 $A$，得到软归属矩阵

$$
\chi=\widetilde Q A,
$$

其中 $\chi_{im}$ 是细胞 $i$ 属于宏状态 $m$ 的程度，每行和为 1。优化目标让归属尽量“清晰”而又保持非负和分割统一；论文/pyGPCCA 使用无导数 Nelder–Mead，并在迭代中把解映射回可行域。

宏状态之间的粗粒化转移矩阵为

$$
P_c=(\chi^\top D\chi)^{-1}\chi^\top DP\chi,
$$

它保留原链慢时间尺度。v1.5.1 的 `GPCCA.compute_macrostates()` 把实际优化委托给 pyGPCCA；CellRank 源码保存 memberships、`coarse_T`、粗粒化初始分布和稳态分布。Schur/GPCCA 的完整数值内核因此是外部 pyGPCCA 依赖，而不是全部复制在 CellRank 仓库中。

宏状态数量 $n_s$ 不是由生物学真值自动给定：可看近 1 特征值的 eigengap、minChi、crispness 或先验知识。代码 `n_states=None` 时可用 eigengap 启发式，但论文胰腺分析根据特征值间隙选了 12 个。不同 $n_s$ 会改变状态边界；若粗粒化矩阵出现明显负元素，论文建议把它视为宏状态数不合适的信号。

扩展数据图 2 用玩具链展示 Schur 子空间、软归属和粗粒化矩阵；图 2b–c 在胰腺数据上展示 12 个宏状态。

### 4. 怎样判定终末、初始和中间状态

终末宏状态应“进入后很少离开”。定义稳定性指数

$$
\mathrm{SI}_m=(P_c)_{mm}.
$$

论文和 v1.5.1 源码默认将 $\mathrm{SI}\ge0.96$ 的宏状态判为终末；每个终末状态默认选 membership 最高的 30 个代表细胞。该阈值是操作性规则，不是普适生物常数。胰腺数据的 alpha、beta、epsilon 分别为 0.97、1.00、0.98，自动通过；稀有 delta 状态只有 0.84，虽被识别成宏状态，却需要手动指定为终末状态。

初始状态依据粗粒化稳态分布：

$$
\pi_p=\chi^\top\pi,
\qquad \pi^\top P=\pi^\top.
$$

长期几乎不会重新访问的宏状态得到小 $\pi_p$，被视为初始；默认只选一个。若初始状态离开太快、无法在正向链中形成亚稳宏状态，也可反转动力学再把它当“反向终末状态”寻找。其余宏状态称为中间状态。

图 2d 用已知标记基因验证初末状态；扩展数据图 5–6 检查标记和增殖群体。这里“自动识别”应理解为给定转移矩阵、宏状态数和阈值后的算法输出，而不是无需参数或人工复核。

### 5. 命运概率就是吸收概率

对每个终末宏状态，选 membership 最高的 $f$ 个细胞作为近似吸收集合，并删除它们向外的边。按吸收与暂态细胞重排后：

$$
P=\begin{bmatrix}\widetilde P&0\\S&Q\end{bmatrix}.
$$

$Q$ 是暂态到暂态转移，$S$ 是暂态到吸收集合转移。命运概率矩阵为

$$
F=(I-Q)^{-1}S,
$$

即从每个细胞出发，随机游走最终先到达各终末集合的概率。若某个细胞对 alpha、beta、delta 的一行为 $(0.1,0.7,0.2)$，不是说它已经有 70% beta 表达，而是当前模型下最终先到 beta 吸收集合的概率为 0.7。

源码不显式求逆，而调用 `_solve_lin_system(q, s, use_eye=True)` 解

$$
(I-Q)F=S.
$$

线性求解器支持 direct、GMRES、LGMRES、BiCGSTAB、GCROT(m,k)；PETSc 是大规模问题的推荐可选后端，但 v1.5.1 的 `use_petsc` 默认是 False，不能笼统写成“所有运行都用 PETSc GMRES”。稀疏矩阵每行约有 K 个邻居，使迭代法可扩展到大数据。论文在 100,000 个细胞上报告宏状态约 33 秒、命运概率约 2 分钟、峰值内存低于 15 GiB；

图 1d、图 2e 展示命运概率；扩展数据图 2f 给出玩具例；循环投影则把各终末状态放在单位圆上，用命运概率加权坐标，使多谱系潜能高的细胞靠近中部。

### 6. 命运概率与伪时间不是同一个量

命运概率回答“会到哪个终点”，伪时间回答“沿过程走了多远”。论文默认用 CellRank 识别的初始细胞作为 Palantir 起点获得伪时间，再以命运概率作为谱系软权重拟合基因趋势。一个尚早但已强烈偏向 beta 的细胞可以有低伪时间、高 beta 命运概率；一个分叉点细胞可有中等伪时间、多个命运概率都非零。

CellRank 将表达与某谱系命运概率相关来筛候选驱动基因，再按伪时间峰值排列表达级联。趋势拟合使用 GAM/样条并以命运概率加权。相关性只是候选调控证据：基因可能是命运的结果、标记或共变量，并不因高相关就成为因果驱动。

### 7. 三个应用怎样检验方法

#### 胰腺内分泌发育（图 2–3）

E15.5 子集有 2,531 个细胞。CellRank 恢复 Ngn3-low EP 初始状态和 alpha/beta/epsilon 终末状态；delta 因稀少和 velocity 基因覆盖不足需要手工设为终末。Ngn3-high EP 的平均 beta 命运概率为 0.71。delta 命运概率定位 Fev+ delta 前体，并找回 *Hhex*、*Cd24a*，提出 *Hadh*、*Map2k4*、*Msi1* 等候选。这个案例同时说明“全局累积”能提取局部速度图上不明显的路线，也说明系统性缺失的 splicing 信号仍会影响自动终末判定。

#### MEF 到 iEP 重编程（图 4）

48,515 个细胞中，CellRank 找到成功与 dead-end 终末状态。以 CellTag 谱系追踪为外部标签，成功命运概率预测重编程结果的 AUC 随时间从第 12 天 0.84、15 天 0.91 到 21 天 0.96。越早的细胞尚未承诺，较低 AUC是合理现象；但验证只覆盖有 CellTag 真值的样本，不能推广为所有系统的固定准确率。

#### 肺损伤修复（图 6）

24,882 个上皮细胞、13 个时间点中，CellRank 预测 goblet 细胞向 Krt5+/Trp63+ basal 细胞去分化，并定位 Bpifb1+/Krt5+/Trp63− 中间状态；免疫荧光在损伤后第 10 天验证这一中间表型。该案例说明算法不要求过程一定沿“越来越分化”的传统方向。

图 5 比较 Palantir、STEMNET、FateID 和 velocyto。应注意比较条件不同：部分方法需要提供初始或终末状态，velocyto 不输出同类命运概率；因此图 5 支持特定任务上的综合能力，而非所有轨迹问题上的绝对排名。

### 8. 论文与 v1.5.1 源码的对应

| 论文机制 | 直接代码证据 | 判断 |
|---|---|---|
| 相关 + softmax、自动 $\sigma$ | `tl/kernels/_velocity_kernel.py:153-303`、`_velocity_schemes.py:80-139` | **Exact** |
| 80/20 velocity-connectivity 混合 | `tl/_transition_matrix.py:17-115` | **Exact**：旧高层 API 默认 connectivity 权重 0.2 |
| 二阶 Taylor/JAX 不确定性传播 | `_velocity_kernel.py:474-535`、`_velocity_schemes.py` | **Exact / opt-in**：实现存在，但 v1.5.1 默认 mode 是 deterministic |
| GPCCA 宏状态与粗粒化矩阵 | `estimators/terminal_states/_gpcca.py:131-206,951-976` | **Partial dependency**：CellRank 编排并存储结果，优化内核来自 pyGPCCA |
| SI 0.96 与手工终末状态 | `_gpcca.py:208-350` | **Exact** |
| CGSD 初始状态 | `_gpcca.py:1083-1176` | **Exact** |
| 吸收概率线性系统 | `estimators/mixins/_absorption_probabilities.py:383-415`、`tl/_linear_solver.py:341-430` | **Exact** |
| PETSc/SLEPc 加速 | 线性求解与 Schur 接口/外部依赖 | **Optional**：推荐用于大规模，不是默认必走路径 |
| 论文全部数据处理与作图 | `cellrank_reproducibility` 独立仓库 | **Not found here**：主源码仓库不是逐图复现仓库 |

本次补入的代码快照为论文时期标签 `v1.5.1`，提交 `ee533caa6b61f6dfbc2590e69423884475c0ba09`。这避免用当前 2.x/后续 API 反向解释 2022 论文。论文代码片段使用旧的 `cellrank.tools` 路径，而 v1.5.1 快照已同时体现 `cellrank.tl` 组织；现代 CellRank 的接口和默认行为可能继续变化，不能把此文档当作当前版本使用手册。

工作区 CodeGraph 在补入源码后仍未返回核心符号，因此导航回退到 `rg` 和逐行直接源文件读取；最终对应结论均来自论文原文与该固定提交，而非旧笔记中的符号名称。

### 9. 复现与解释边界

1. 结果首先受 RNA velocity 模型质量控制；稀少的 unspliced counts、错误动力学拟合、批次效应或非典型剪接会系统性改变方向。
2. KNN 图要求轨迹连续采样；缺少中间态会强迫随机游走跨越不真实邻边，CellRank 不会自动填补缺口。
3. 宏状态数、连接性权重、稳定阈值、终末代表细胞数都影响结果；delta 的手工处理说明人工复核不可省略。
4. 马尔可夫无记忆假设忽略未被转录组充分表达的历史和表观遗传状态。
5. 不确定性传播只近似局部速度的统计波动，不能校正整个速度场方向相反等模型偏差。
6. 命运概率是给定 $P$ 和吸收集合下的模型概率，不是同一细胞可被重复观测得到的经验频率。

### 推荐阅读顺序

先看图 1/扩展数据图 1理解“局部方向→全局概率”，再看扩展数据图 2和图 2b–e理解 GPCCA 与吸收；接着用扩展数据图 3检查不确定性边界；最后读图 3、4、6，分别看稀有命运、外部谱系追踪验证和非经典去分化应用。代码按 `_transition_matrix.py` → `_velocity_kernel.py` → `_gpcca.py` → `_absorption_probabilities.py` → `_linear_solver.py` 阅读最顺。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellRank: Directed Single-Cell Fate Mapping

### Paper Information

- **Title**: CellRank for directed single-cell fate mapping
- **Authors**: Marius Lange, Volker Bergen, Michal Klein, Manu Setty, Bernhard Reuter, Mostafa Bakhti, Heiko Lickert, Meshal Ansari, Janine Schniering, Herbert B. Schiller, Dana Pe'er, Fabian J. Theis
- **Journal**: Nature Methods, 19(2), 2022
- **DOI**: 10.1038/s41592-021-01346-6
- **Code**: https://github.com/theislab/cellrank

### Motivation and Novelty

Computational trajectory inference from single-cell RNA-seq can reconstruct developmental pathways, but it traditionally requires prior knowledge of the biological direction (e.g., specifying a root cell). RNA velocity estimates the direction of gene regulation from spliced/unspliced mRNA ratios, but velocity vectors are noisy, available only locally, and typically interpreted only through low-dimensional projections that distort global relationships. CellRank addresses these limitations by combining the global topology captured by kNN-based similarity graphs with the directional information from RNA velocity in a principled Markov chain framework. The key novelty is a three-stage pipeline -- (1) constructing a directed transition matrix from velocity + connectivity, (2) coarse-graining via GPCCA (adapted from protein conformational dynamics) to identify macrostates, and (3) computing absorption probabilities as fate predictions -- that automatically identifies initial, intermediate, and terminal cell states without user-provided root cells and produces quantitative, cell-level fate probability estimates.

Three specific innovations stand out:
1. **Uncertainty propagation**: A second-order Taylor approximation propagates the distribution over velocity vectors into the transition matrix, downweighting transitions in noisy regions. JAX-based automatic differentiation computes the required Hessians.
2. **GPCCA for single-cell data**: The real Schur decomposition handles the nonsymmetric, directed transition matrix (whose eigenvectors are complex), and the Perron cluster method decomposes it into metastable macrostates with a coarse-grained transition matrix.
3. **Absorption probabilities as fate probabilities**: Rather than simulating random walks, CellRank solves $(I - Q)A = S$ via iterative GMRES solvers (PETSc), making fate computation linear-time in cell number and scalable to 100,000+ cells.

### Method Overview

**Input**: scRNA-seq count matrix $X \in \mathbb{R}^{N \times G}$, RNA velocity matrix $V \in \mathbb{R}^{N \times G}$ (from scVelo or velocyto).

**Step 1 -- Transition matrix construction**:
- Compute a symmetric kNN graph (K=30 by default) in PCA space to define the phenotypic manifold.
- For each cell $i$, compute Pearson correlations between its velocity vector $v_i$ and state-change vectors $\delta_{ij} = x_j - x_i$ to all neighbors $j$.
- Apply a softmax transformation: $p_{ik} = \exp(\sigma c_{ik}) / \sum_l \exp(\sigma c_{il})$ where $\sigma = 1 / \text{median}(|c_{ik}|)$.
- Combine the velocity-based transition matrix $P_v$ with a connectivity-based transition matrix $P_s$ (row-normalized adjacency): $P = (1-\lambda)P_v + \lambda P_s$ with $\lambda = 0.2$.

**Step 2 -- Macrostate identification via GPCCA**:
- Compute the partial real Schur decomposition $P = QRQ^\top$ using SLEPc (krylov method for large sparse matrices).
- Select $n_s$ Schur vectors and optimize a rotation matrix $A$ to produce membership vectors $\chi = \tilde{Q}A$ that maximize crispness.
- Compute coarse-grained transition matrix $P_c = (\chi^\top D\chi)^{-1}(\chi^\top D P\chi)$.
- Classify macrostates: terminal (self-transition probability $\geq 0.96$), initial (smallest coarse-grained stationary distribution value), intermediate (remaining).

**Step 3 -- Fate probabilities via absorption**:
- Select the $f$ most confidently assigned cells per terminal state as absorbing states.
- Remove outgoing edges from absorbing sets to create recurrent classes.
- Solve $(I - Q)a_t = s_t$ for each absorbing state $t$ using GMRES, yielding the probability that each transient cell reaches each terminal state.

**Downstream analysis**: Gene expression trend fitting (GAMs weighted by fate probabilities), driver gene identification (correlation with fate probabilities), visualization (circular projections, directed PAGA graphs).

### Evaluation

#### Pancreas development (E15.5, 2,531 cells)
- Correctly identified initial Ngn3low EP state, terminal alpha/beta/epsilon states automatically, delta state as macrostate (manually assigned terminal due to small size and poor velocity coverage).
- Beta correctly predicted as dominant fate among Ngn3high EP cells (71% average fate probability).
- Identified known driver genes (Arx, Pdx1, Hhex) and novel delta cell candidates (Hadh, Map2k4, Msi1).

#### Reprogramming (MEF to iEP, 48,515 cells)
- Recovered successful and dead-end terminal states despite velocity failing to show the reprogramming path in 2D.
- Fate probabilities validated against CellTag lineage tracing: AUC = 0.84 (day 12), 0.91 (day 15), 0.96 (day 21).

#### Lung regeneration (24,882 cells, 13 timepoints)
- Predicted novel goblet-to-basal cell dedifferentiation trajectory, experimentally validated with immunofluorescence.
- Identified three stages (goblet -> intermediate Bpifb1+/Krt5+ -> basal Krt5+/Trp63+).

#### Benchmarking
- Compared against Palantir (Nature Biotechnology, 2019), STEMNET (Nature Cell Biology, 2017), FateID (Nature Methods, 2018), velocyto (Nature, 2018).
- CellRank was the only method to correctly identify both initial and terminal states automatically.
- Runtime: ~33s macrostates, ~2min fate probabilities on 100K cells; <15 GiB memory.
- CellRank 3-5x lower memory than Palantir/FateID for fate probabilities.

### Key Strengths

1. **Principled mathematical framework**: Markov chain theory provides formal guarantees (absorption probabilities, metastability, invariant subspace projection).
2. **Automatic state identification**: No root cell required; terminal states from stability index, initial states from coarse-grained stationary distribution.
3. **Scalability**: SLEPc partial Schur decomposition + GMRES linear solver achieve near-linear scaling in cell number.
4. **Uncertainty propagation**: Second-order Taylor approximation automatically downweights noisy velocity estimates.
5. **Modular design**: Kernel/estimator architecture allows easy extension to new data modalities.

### Limitations

1. **Dependency on RNA velocity quality**: If splicing kinetics do not capture the biology, CellRank cannot fully compensate.
2. **Number of macrostates**: Remains a user-specified parameter despite available heuristics.
3. **Stability index threshold**: Default 0.96 is somewhat arbitrary; delta cells (SI 0.84) required manual intervention.
4. **No batch correction for velocity**: An open problem at time of publication.
5. **Linear velocity extrapolation**: Assumes RNA velocity approximates the first derivative of gene expression.

### Reproducibility

**Rating: 4/5**

- Code is open source with comprehensive documentation and tutorials at https://cellrank.org.
- Jupyter notebooks for figure reproduction at https://github.com/theislab/cellrank_reproducibility.
- Processed data on figshare (10.6084/m9.figshare.c.5172299); raw data on GEO (GSE132188, GSE141259, GSE99915).
- Minor limitation: dependency on specific scVelo versions and pyGPCCA adds complexity.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
