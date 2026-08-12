---
layout: default
permalink: /paper-atlas/rna-ode-a25c2156/
title: "RNA_ODE"
nav: false
description: "RNA-ODE 的关键贡献是把“瞬时 RNA velocity”提升为“可模拟的动态系统”：先学习 dx/dt=f(x;θ)，再用模拟出来的未来轨迹推断细胞状态转移、发育方向和调控关系。概念上它把 velocity 信息用得更彻底；但就当前获取的代码而言，公开包只覆盖了核心 ODE/lineage/部分 GRN 功能，论文中若干下游分析仍缺少可核查实现。"
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
      <span>Journal of Molecular Biology · 2022</span>
    </div>
    <h1>RNA_ODE</h1>
    <p>Dynamical Systems Model of RNA Velocity Improves Inference of Single-cell Trajectory, Pseudo-time and Gene Regulation</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RNA-ODE 方法中文解读

### 1. 这篇论文想解决什么问题？

RNA velocity 可以从单细胞 RNA-seq 中估计每个细胞当前转录组变化的“瞬时速度”。但论文指出，瞬时速度本身只能告诉我们“现在朝哪个方向变”，不能直接回答“经过一段时间后细胞会到哪里”“不同细胞状态之间如何转移”“改变某个基因会不会改变细胞命运”等有限时间尺度的问题。

RNA-ODE 的核心想法是：把 RNA velocity 看成基因表达随时间变化的导数，学习一个常微分方程（ODE）系统。这样，给定一个细胞当前的表达状态，就可以数值求解 ODE，预测它未来的表达轨迹，并用这些轨迹改进轨迹推断、拟时序、基因调控网络和命运影响基因分析。

### 2. 为什么已有方法不够？

论文主要对比两类已有方法。

第一类是轨迹/拟时序方法，例如 Slingshot（*BMC Genomics*, 2018）、TSCAN（*Nucleic Acids Research*, 2016）和 Monocle-DDRTree（*Nature Methods*, 2017）。这些方法主要依赖静态表达矩阵，通常缺少方向信息，因此起始细胞或根状态常常需要人工先验，或者容易推断出与真实发育方向相反的轨迹。

第二类是基因调控网络（GRN）方法，例如 GENIE3（*PLOS One*, 2010）、SCODE（*Bioinformatics*, 2017）和 SCENIC（*Nature Methods*, 2017）。这些方法主要利用基因表达之间的共表达关系，而 RNA-ODE 试图利用“表达如何决定速度”这一动态信息。论文认为，velocity 与共表达是互补信息。

### 3. RNA-ODE 的核心模型

RNA-ODE 的输入是：

- 单细胞表达矩阵：$x_{1},…,x_{n_c}$，其中 $x_i=(x_{i1},…,x_{in_g})$ 表示第 $i$ 个细胞的 $n_g$ 个基因表达；
- RNA velocity 矩阵：$v_{1},…,v_{n_c}$，其中 $v_i=(v_{i1},…,v_{in_g})$ 表示第 $i$ 个细胞的速度向量；
- 用于轨迹分析的细胞状态/聚类标签，记作 $g(x)$。

核心方程是：

$$
\frac{dx}{dt}=v(x)=f(x\text{;}θ).
$$

这里 $f$ 是从数据中学习出来的函数：输入当前表达 $x$，输出预测的 RNA velocity $v$。论文默认使用回归随机森林来拟合 $f$，实验设置中使用 10 棵树、最大深度 10，并按 70%/30% 划分训练/测试集。

在获得 $f$ 后，对任意细胞的初始表达 $x(0)=x$，就可以数值求解 ODE 得到未来路径 $x(t)$。

### 4. 计算流程

```text
表达矩阵 X + RNA velocity V
        |
        v
学习速度函数 f: X -> V
        |
        v
从每个细胞出发求解 dx/dt=f(x;θ)
        |
        +--> 未来表达轨迹 x_i(t)
                 |
                 +--> 估计细胞状态转移概率 P_ij
                 |        |
                 |        +--> 根状态：最不容易被其他状态转入的状态
                 |        +--> 有向 MST/树：细胞状态发育拓扑
                 |        +--> 主曲线投影：拟时序（论文描述，代码中未找到）
                 |
                 +--> 过表达扰动模拟：命运改变评分（论文描述，代码中未找到）
        |
        +--> 每个目标基因单独建模：GRN 调控边排序
```

#### 4.1 学习表达到速度的函数 $f$

论文把 $f$ 作为机器学习回归问题：用表达矩阵预测 velocity。源码中的 `BUILD_MODEL` 支持随机森林、lasso 和线性回归；默认随机森林参数与论文实验设置一致，即 `n_estimators=10`、`max_depth=10`、`train_size=0.7`。这部分与论文核心 ODE 学习步骤吻合。

#### 4.2 求解 ODE

论文说 RNA-ODE 默认使用 Euler 方法，同时提供 Heun 和四阶 Runge-Kutta 选项。直接读取到的源码中，`ODE_SIMULATION` 只实现了显式 Euler：

$$
x_{t+1}=x_t+dt\,f(x_t),
$$

并把负表达值截断为 0。检索整个已获取包源码后，没有找到 Heun 或 RK4 的实现。因此，论文里的“其他求解器选项”在当前获取的 Python 包中属于 **Not found**。

#### 4.3 细胞状态转移和轨迹拓扑

论文定义从状态 $i$ 到状态 $j$ 的时间 $t$ 后转移概率：

$$
p_{\mathrm{ij}}(t)=p(g(x(t))=j|g(x(t=0))=i).
$$

再定义时间范围内的平均转移概率：

$$
P_{\mathrm{ij}}=\frac{1}{T}∫t=0Tp_{\mathrm{ij}}(t)dt.
$$

源码中的 `GET_LINEAGE` 做法是：先用原始表达训练一个细胞状态分类器（随机森林或 kNN），再把 ODE 模拟出的轨迹点输入分类器，得到各状态概率，并对细胞和时间点求平均。这可以看作对 $P_{ij}$ 的离散近似。

根状态定义为：

$$
\mathrm{Starting}\;\mathrm{state}=\mathrm{arg}\;\mathrm{min}_{j}\sum_{i≠j}P_{\mathrm{ij}}.
$$

也就是说，最不容易被其他状态转入的状态就是起始状态。源码中确实按“最小 incoming probability”选择 root。随后，论文用权重 $1-P_{ij}$ 构造有向图，并用最小生成树/有向树得到状态拓扑；源码中也通过 `min_spanning_arborescence` 实现了这一点。

#### 4.4 拟时序

论文描述的拟时序步骤是：把学到的 MST 拆成多条 lineage，对每条 lineage 拟合 principal curve；有分支时按 Slingshot/Street 等人的方法合并曲线；最后把细胞正交投影到曲线上得到 pseudotime。

但是，在已获取源码中没有找到 principal curve 或 pseudotime 函数。`RNA_ODE` 类的 docstring 提到了 pseudo-time inference，但没有公开方法实现它。因此这部分应视为论文方法描述存在，当前包源码实现 **Not found**。

#### 4.5 命运影响基因分析

论文提出一个很有吸引力的应用：对某个分支点附近的细胞，在初始时刻把基因 $k$ 过表达 $α$ 倍，然后用 ODE 预测未来轨迹，看细胞是否从原来的分支转到另一个分支。二分叉时的重要性评分为：

$$
I(k,α)=p(g^{-k}(x_{a}′(k,α)(t=T))=c|g^{-k}(x_{a}(t=T))=b).
$$

多分叉时变为：

$$
I(k,α)=p(g^{-k}(x_{a}′(k,α)(t=T))\in S_{a}⧹{b}|g^{-k}(x_{a}(t=T))=b).
$$

其中 $g^{-k}$ 表示分类时去掉被扰动的基因 $k$，避免“因为直接改变了该基因表达，所以分类器直接变了”的假象。

图 2(c,d) 展示了 Mllt11 过表达可能把一个细胞从 granule 方向改到 CA 方向，并把 Mllt11 排在最前。但直接搜索源码后，没有找到 perturbation、overexpression、branch-switch score 或 Mllt11 相关实现。因此该分析在论文中清楚描述，但当前包源码实现 **Not found**。

#### 4.6 GRN 推断

RNA-ODE 的 GRN 思路是：对每个目标基因 $j$，用其他基因的表达预测该目标基因的 velocity：

$$
v_{ij}=f_j(x_i^{-j}\text{;}θ_j).
$$

其中 $x_i^{-j}$ 表示去掉目标基因 $j$ 自身的表达，避免自调控偏差。每个目标基因拟合一个随机森林，特征重要性就作为候选调控因子的分数。论文还要求先把 velocity 标准化到单位方差，以避免高变异基因带来的偏差。

源码中的低层 `GENIE3_single` 确实包含：去掉目标基因、标准化输出、训练树模型、计算 feature importance 这些步骤。但公共包装函数 `compute_grn_scores(method='RNA_ODE')` 与 `GET_GRN` 之间似乎存在参数语义反转：按源码逻辑，传入 velocity 时反而调用普通 `GENIE3(counts)`。因此，底层函数支持论文思路，但公共包装层存在可复现性风险。

### 5. 结果如何？

论文在合成数据和真实脑发育数据上评估 RNA-ODE。

合成数据部分使用 Saelens 等人的轨迹推断 benchmark 工作流，覆盖 5 种拓扑、187 个模拟实验，每个实验 1000 个细胞。论文报告 RNA-ODE 在根状态识别、轨迹拓扑和拟时序上优于 Slingshot、TSCAN、Monocle-DDRTree；在 GRN 上与 GENIE3 可比，并能发现一些 GENIE3 没发现的真实调控边。

真实数据部分包括小鼠海马和人类第一孕期新皮层单细胞数据。图 2 显示了 velocity 场、Slingshot 与 RNA-ODE 的轨迹方向对比、Mllt11 过表达示例，以及 TF/RBP 子集预测 velocity 的 R² 柱状图。论文认为，RNA-ODE 的轨迹方向更符合 velocity 场，并且少量 TF/RBP 就能保留大量速度预测信息。

### 6. 代码可复现性总结

当前获取的 GitHub 包可以复现/支持的核心部分：

- 表达 $\to$ velocity 的模型拟合；
- Euler ODE 轨迹模拟；
- 基于分类器的状态转移概率；
- root 识别；
- 有向 MST/lineage 推断；
- lineage correctness 和 GRN AUROC 评估；
- 低层 tree feature importance 型 GRN 计算。

当前源码中没有找到的部分：

- Heun / 四阶 Runge-Kutta ODE solver；
- principal-curve pseudotime；
- in silico overexpression 的命运改变评分；
- 论文尺度的实验 notebooks/scripts；
- 补充材料 markdown，因此补充表格和补充图说明无法核查。

### 7. 一句话理解 RNA-ODE

RNA-ODE 的关键贡献是把“瞬时 RNA velocity”提升为“可模拟的动态系统”：先学习 $dx/dt=f(x;θ)$，再用模拟出来的未来轨迹推断细胞状态转移、发育方向和调控关系。概念上它把 velocity 信息用得更彻底；但就当前获取的代码而言，公开包只覆盖了核心 ODE/lineage/部分 GRN 功能，论文中若干下游分析仍缺少可核查实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RNA-ODE Summary

### Problem

RNA velocity estimates the instantaneous direction of transcriptome change in each single cell, but it does not directly answer finite-time questions such as where a cell will go later, which state transitions are likely, or how perturbing one gene could change fate. RNA-ODE addresses this gap by learning an ordinary differential equation from expression and RNA velocity, then using simulated trajectories for common single-cell analyses.

### Existing-method limitations

The paper distinguishes RNA-ODE from two families of prior tools. For trajectory inference, methods such as Slingshot (*BMC Genomics*, 2018), TSCAN (*Nucleic Acids Research*, 2016), and Monocle-DDRTree (*Nature Methods*, 2017) primarily use static expression and often require or benefit from user-specified root information. For GRN inference, GENIE3 (*PLOS One*, 2010), SCODE (*Bioinformatics*, 2017), and SCENIC (*Nature Methods*, 2017) mainly use co-expression/static transcriptome patterns. The paper's claim is that these approaches do not directly exploit velocity as the derivative of expression, limiting finite-time trajectory prediction and velocity-informed regulatory analysis.

### Proposed method

RNA-ODE models gene expression dynamics as

$$
\frac{dx}{dt}=v(x)=f(x\text{;}θ),
$$

where $x$ is a gene-expression vector, $v$ is RNA velocity, and $f$ is learned from observed expression/velocity pairs. The paper uses regression random forests as the default $f$, with 10 trees, max depth 10, and a 70/30 train/test split in evaluation. Once $f$ is fitted, RNA-ODE solves the ODE from each cell's expression snapshot to obtain future paths $x(t)$.

### High-level pipeline

1. Input expression matrix and RNA velocity matrix.
2. Fit $f: x\mapsto v$ with a regression model, usually random forest.
3. Simulate future expression paths with an ODE solver; the acquired code implements explicit Euler stepping.
4. Classify simulated path points into cell states to estimate transition probabilities $P_{ij}$.
5. Infer the starting state as the state with least incoming transition probability.
6. Build a directed MST/arborescence over cell states using edge weights $1-P_{ij}$.
7. Paper-described downstream analyses include principal-curve pseudotime, in silico gene perturbation/fate-switch scoring, and GRN ranking from expression-to-velocity feature importances.

### Evaluation and findings

The paper evaluates RNA-ODE on synthetic trajectory datasets derived from the Saelens et al. benchmark workflow, covering five topology types and 187 simulated experiments. It compares lineage/pseudotime against Slingshot, TSCAN, and Monocle-DDRTree, and compares GRN inference against GENIE3. The paper reports improved root identification, trajectory topology, and pseudotime; GRN performance that is comparable to GENIE3 but discovers complementary links; and robustness to added velocity noise and solver variants.

For real data, the paper analyzes a mouse hippocampus dataset and a human trimester neocortical dataset. Figure 2 shows velocity fields, Slingshot versus RNA-ODE trajectory comparisons, an Mllt11 overexpression example, and TF/RBP subset velocity-prediction bars. The text reports that TF/RBP subsets retain much of the velocity-prediction signal and that RNA-ODE trajectory directions better match the observed velocity fields in the shown examples.

### Code-paper match and reproducibility

The acquired GitHub package (`VelocytoAnalysis`) contains a compact implementation of the core ODE workflow:

- `RNA_ODE` wrapper with model, simulation, lineage, and GRN/evaluation methods.
- `BUILD_MODEL` for random forest/lasso/linear expression-to-velocity regression.
- `ODE_SIMULATION` for Euler rollout with nonnegative clipping.
- `GET_LINEAGE` for classifier-based transition probabilities, root inference, and directed arborescence lineage.
- `COMPUTE_LINEAGE_CORRECTNESS` and `COMPUTE_GRN_AUROC` evaluation helpers.
- GENIE3-derived tree feature-importance code that can support per-target expression-to-velocity GRN scoring at the lower level.

Reproducibility caveats are important. The acquired package source did **not** contain Heun or RK4 solvers, principal-curve pseudotime, or influential-gene branch-switch scoring, even though these are described in the paper. The public GRN wrapper also appears inconsistent with the paper's RNA_ODE-versus-GENIE3 semantics: direct source suggests the velocity-output path is not used when `method='RNA_ODE'`. The repository README mentions example notebooks in `experiments`, but the acquired listing contained only `experiments/data/`. Supplementary markdown is unavailable, so supplementary tables and captions could not be checked.

### Practical takeaway

RNA-ODE is conceptually valuable because it turns RNA velocity into an explicit dynamical simulator and uses that simulator to orient lineage graphs and propose regulatory/fate hypotheses. The available package supports the central model fitting, Euler rollout, lineage graph, and some GRN/evaluation utilities, but it is not a complete reproduction of every paper-described downstream analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
