---
layout: default
permalink: /paper-atlas/scvelo-f8858c2f/
title: "scVelo"
nav: false
description: "scVelo 的关键贡献不是把速度箭头画得更平滑，而是放弃“数据必须已经看到稳态”的强假设，直接为每个基因拟合转录、剪接和降解动力学，同时估计每个细胞处于诱导还是抑制阶段以及它在该基因轨迹上的潜在时间。得到基因空间的速度后，方法再用速度与邻近细胞表达差的方向一致性构造转移图，并据此投影到 UMAP、识别起点/终点和整合 gene-shared latent time。"
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
      <span>Nature Biotechnology · 2020</span>
    </div>
    <h1>scVelo</h1>
    <p>Generalizing RNA velocity to transient cell states through dynamical modeling</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-020-0591-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/theislab/scvelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for scVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scVelo 方法解读：用完整转录动力学推断瞬态细胞的 RNA velocity

### 一句话理解

scVelo 的关键贡献不是把速度箭头画得更平滑，而是放弃“数据必须已经看到稳态”的强假设，直接为每个基因拟合转录、剪接和降解动力学，同时估计每个细胞处于诱导还是抑制阶段以及它在该基因轨迹上的潜在时间。得到基因空间的速度后，方法再用速度与邻近细胞表达差的方向一致性构造转移图，并据此投影到 UMAP、识别起点/终点和整合 gene-shared latent time。

论文为 Bergen 等发表于 *Nature Biotechnology*（2020）的 “Generalizing RNA velocity to transient cell states through dynamical modeling”，DOI `10.1038/s41587-020-0591-3`。

### 1. 原始稳态方法为什么会失败

RNA velocity 使用未剪接 RNA $u$ 与已剪接 RNA $s$ 的相对丰度估计表达变化。经典简化模型在稳态处令 $ds/dt=0$，由极端分位细胞拟合未剪接与已剪接计数的比例，再把偏离拟合线的残差当作速度。若诱导和抑制阶段都足够长、确实观察到高低稳态，这种近似有效且快速。

问题在于短暂祖细胞、快速响应或只覆盖部分过程的数据可能根本没到稳态。此时 phase portrait 中的点只形成弯曲轨迹的一段，线性稳态拟合会把同一段中的细胞人为分到正负速度两边。它还把速率缩放到共同剪接率 $\beta=1$，难以描述不同基因的时间尺度。论文 Fig. 1b 用“达到稳态”和“提前切换”的两条轨迹直观展示这一差别。

### 2. scVelo 拟合的动力学

对单个基因，模型为

$$
\frac{du}{dt}=\alpha_k-\beta u,\qquad
\frac{ds}{dt}=\beta u-\gamma s.
$$

$\alpha_k$ 是依赖转录状态 $k$ 的转录率：诱导阶段为开启值，抑制阶段为关闭/基线值；$\beta$ 是剪接率，$\gamma$ 是已剪接 RNA 降解率。给定阶段初值 $(u_0,s_0)$ 后有解析解：

$$
u(t)=u_0e^{-\beta t}+\frac{\alpha}{\beta}(1-e^{-\beta t}),
$$

$$
s(t)=s_0e^{-\gamma t}+\frac{\alpha}{\gamma}(1-e^{-\gamma t})
+\frac{\alpha-\beta u_0}{\gamma-\beta}(e^{-\gamma t}-e^{-\beta t}).
$$

本地 `code/scvelo/core/_models.py::SplicingDynamics.get_solution()` 逐项实现这两个解。速度是状态方程右侧，而不是降维坐标差：

$$
v_u=\alpha_k-\beta u,\qquad v_s=\beta u-\gamma s.
$$

通常 RNA velocity 指 $v_s$。正值表示在当前参数下已剪接 RNA 倾向增加，负值表示倾向减少。

### 3. 隐变量：时间和转录状态必须与速率一起估计

每个观测细胞只有 $(u_i,s_i)$，没有真实时间，也不知道它位于 induction、active steady state、repression 还是 inactive steady state。scVelo 因而把细胞时间 $t_i$ 和状态 $k_i$ 与动力学参数

$$\theta=(\alpha,\beta,\gamma,t_*)$$

一起估计，其中 $t_*$ 是从开启切换到关闭的时间。

论文 Fig. 1c–d 展示迭代逻辑：

1. 给定当前参数曲线，把每个点投影到诱导/抑制等轨迹段，分配时间并计算状态似然；
2. 给定这些时间和状态，更新速率与切换时间，使观测点在 phase portrait 中更接近解析轨迹；
3. 重复直到拟合稳定。

论文称这一过程为 EM 框架，但实现不是一个只有两行的标准 EM。`DynamicsRecovery` 采用分阶段优化：以稳态回归初始化 $\beta=1$ 和相对降解率，随后依次更新缩放、速率、时间及稳态参数。`recover_dynamics()` 默认逐基因执行，保存 `fit_alpha`、`fit_beta`、`fit_gamma`、`fit_t_`、`fit_likelihood` 和细胞×基因的 `fit_t`。因此“dynamical mode”首先产生的是逐基因参数和时间；仍需再调用 `velocity(mode="dynamical")` 才把它们转成 velocity layer。

时间分配使用解析反演或轨迹投影以避免在密集时间网格上穷举。默认源码参数 `assignment_mode="projection"` 与论文早期描述的主要解析近似并不完全相同，这是论文算法与当前快照接口的版本边界之一。

### 4. 三种 velocity 模式不要混淆

#### 4.1 deterministic / steady-state

`code/scvelo/tools/velocity.py::Velocity.compute_deterministic()` 对极端分位的 $u$、$s$ 做线性回归，估计比例 $\gamma'$，再计算

$$v=u-\gamma's-o.$$

它速度快，但依赖稳态和完整诱导/抑制取样。代码中的 `mode="steady_state"` 或 deterministic 语义对应这条路径。

#### 4.2 stochastic

stochastic 模式仍是稳态框架，但加入邻域平滑后的二阶矩，例如 $\langle us\rangle$ 和 $\langle s^2\rangle$，以广义最小二乘联合约束比例。`compute_stochastic()` 调用 `second_order_moments()` 并通过 `leastsq_generalized()` 或 likelihood 路径求解。它利用噪声协变信息，计算量接近稳态模式，但并没有恢复完整的瞬态 $\alpha,\beta,\gamma,t$。

#### 4.3 dynamical

dynamical 模式读取 `recover_dynamics()` 的拟合参数与逐细胞时间，按完整 ODE 计算速度。它能拟合未观测稳态和基因特异速率，代价是更慢、也更依赖 phase portrait 是否包含足够曲率。论文报告其在约 35,000 个细胞、1,000 个基因上可在约 20 分钟完成，这是论文硬件和当时实现下的结果，不应当作当前任意环境的性能保证。

### 5. 从基因速度到细胞转移图

速度向量 $v_i$ 位于基因表达空间，不能直接当作 UMAP 平面上的位移。对当前细胞 $i$ 和候选邻居 $j$，scVelo 计算表达差

$$\delta_{ij}=s_j-s_i$$

与 $v_i$ 的 cosine similarity：

$$
\pi_{ij}=\frac{\delta_{ij}^{\mathsf T}v_i}
{\|\delta_{ij}\|\,\|v_i\|}.
$$

`VelocityGraph` 只在 kNN 的直接邻居及递归邻居中评估候选边，并把正、负相关图分别写入 `adata.uns`。`transition_matrix()` 再以指数核和自转移概率将方向分数变成转移概率。最后 `velocity_embedding()` 计算邻居嵌入位移的概率加权期望；图上的箭头因此是基因空间速度诱导的局部期望方向，而不是 ODE 在 UMAP 坐标上的直接求导。

这个边界非常重要：UMAP 流线可能受邻居图、选择的 velocity genes、嵌入扭曲和投影参数影响。论文也明确建议不要只看箭头，应检查关键基因的 phase portrait。

### 6. latent time 与 pseudotime 的区别

每个基因独立拟合会给同一细胞多个 `fit_t`。`latent_time()` 先筛选 likelihood 足够高且局部一致的基因，再将逐基因时间对齐到根细胞，使用多个分位候选汇总为 gene-shared latent time，并用邻域卷积修正不一致点。若未提供根，函数可借助 velocity graph 推断 terminal states；用户也能用 `root_key`、`end_key` 加先验。

这不是普通的表达相似度 pseudotime：其主要信息来自拟合的转录动力学和方向。但当前实现仍调用 velocity pseudotime、邻居连接和根/终点先验来筛选或稳定结果，所以也不应宣称 latent time 完全独立于图结构。论文 Fig. 3d 显示胰腺数据中 latent time 能区分实验时点并给出与 diffusion pseudotime 不同的时序。

### 7. 标准运行链及对象流

典型分析顺序是：

```python
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
scv.tl.recover_dynamics(adata)
scv.tl.velocity(adata, mode="dynamical")
scv.tl.velocity_graph(adata)
scv.tl.latent_time(adata)
```

数据流应按以下字段理解：

- 输入 `adata.layers["spliced"]` 与 `["unspliced"]`；
- `moments()` 通过邻居图产生平滑的一阶矩 `Ms`、`Mu`；stochastic 路径还使用二阶矩；
- `recover_dynamics()` 在 `adata.var` 写入逐基因参数，在 `adata.layers["fit_t"]` 写入逐细胞逐基因时间；
- `velocity()` 写 `adata.layers["velocity"]`；
- `velocity_graph()` 写稀疏正/负图；
- `latent_time()` 写 `adata.obs["latent_time"]`。

邻域平滑不是纯粹的可视化步骤，它改变用于参数拟合的 $u,s$ 估计。因而 `n_neighbors`、PCA 表示、过滤和归一化都属于模型输入的一部分，复现时必须记录。

### 8. 论文图展示了什么

- Fig. 1 是算法图：a 为 ODE，b 为稳态与提前切换，c–d 为时间/状态分配与参数更新循环。
- Fig. 2 在 dentate gyrus 数据中比较稳态与动态速度，展示动态模型纠正部分方向并用 likelihood 区分动态驱动基因与不具信息的基因。likelihood 是拟合支持度，不等同于因果调控证据。
- Fig. 3 在胰腺内分泌发育中比较两种 velocity、展示 Cpe 等基因的局部差异，并引入 latent time、turning genes 和基因切换次序。
- 补充图进一步检查模拟恢复、参数可识别性、differential kinetics、partial kinetics/root prior、运行时间和更多数据集。

这些结果支持动态模型在瞬态系统中比稳态近似更合适，但不是“任何数据上 dynamical 必定正确”。论文专门列出 differential kinetics、观测不足和时间尺度不匹配三类失败模式，并建议用 phase portraits 和先验核查。

### 9. 关键限制与诊断

#### 多谱系的 differential kinetics

同一基因可能在不同谱系有不同速率，一个全局参数集不能解释多条 phase trajectory。论文用 likelihood-ratio test 检测差异动力学，再按群体分别拟合。本地源码包含相应测试。不要把多条轨迹硬压成一个环形曲线。

#### 只观察到局部动力学

若 phase portrait 近似直线，诱导末端与抑制开端可能同样解释数据，形成不可识别的局部最优。root prior 能用实验时间或已知祖细胞打破方向歧义，但先验并不会凭空补回未观测动力学；结论必须标明其依赖。

#### 模型假设

动力学模型假定每个基因在一个 regime 内有恒定 $\beta,\gamma$，并以有限转录状态描述开关；基因分别拟合，没有显式 GRN 耦合。剪接异构体、状态依赖降解、转录后调控和数据生成偏差可能违反假设。

#### 速度不是命运概率的直接测量

velocity 表示局部短期表达变化。沿图累计得到的终点、潜在时间或 fate 相关量还依赖邻域图和传播模型，不能自动解释为谱系追踪的实验真值。

### 10. 论文—代码匹配与复现边界

| 机制 | 当前源码证据 | 判断 |
|---|---|---|
| 解析剪接 ODE | `core/_models.py::SplicingDynamics`、`tools/_em_model_utils.py` | Exact |
| 稳态/随机 velocity | `tools/velocity.py::Velocity` | Exact |
| 动态参数与时间恢复 | `tools/_em_model_core.py::DynamicsRecovery`, `recover_dynamics()` | Exact 主机制；当前分阶段优化细节比论文概述更具体 |
| velocity graph 与转移矩阵 | `tools/velocity_graph.py`, `transition_matrix.py` | Exact |
| gene-shared latent time | `_em_model_core.py::latent_time()`, `_em_model_utils.py::compute_shared_time()` | Partial：当前分位选择准则与论文文字描述不完全一致 |
| 论文全套结果复现 | 正文/补充与源码均在 | Partial：缺少可验证上游 commit、确定包版本和锁定实验环境 |

release notes 说明快照至少包含到 0.2.5 的历史，但动态版本配置无法单独证明源码就是某一正式发行版。因此本文档不把它标作 0.2.5，也不声称已重跑论文数字。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scVelo: Generalizing RNA Velocity to Transient Cell States through Dynamical Modeling

**Authors**: Volker Bergen, Marius Lange, Stefan Peidli, F. Alexander Wolf, Fabian J. Theis
**Journal**: Nature Biotechnology (2020)
**DOI**: [10.1038/s41587-020-0591-3](https://doi.org/10.1038/s41587-020-0591-3)
**Code**: [https://github.com/theislab/scvelo](https://github.com/theislab/scvelo) | [https://scvelo.org](https://scvelo.org)

---

### Motivation & Novelty

#### Problem
RNA velocity, introduced by La Manno et al. (*Nature*, 2018), estimates the rate of gene expression change from the ratio of unspliced to spliced mRNA in scRNA-seq data. However, the original "steady-state model" makes two restrictive assumptions: (1) all genes share a common splicing rate, and (2) both transcriptional induction and repression phases last long enough to reach steady-state equilibrium. These assumptions frequently fail in transient cell populations (e.g., short-lived progenitor states, perturbed systems) and heterogeneous subpopulations with different kinetic regimes, leading to erroneous velocity estimates.

#### Existing Limitations
- **velocyto** (La Manno et al., *Nature*, 2018): Assumes steady-state ratio exists for all genes; assigns single common splicing rate ($\beta=1$); quadratic runtime scaling; cannot handle >40,000 cells.
- **Diffusion pseudo-time** (Haghverdi et al., *Nature Methods*, 2016): Similarity-based; does not account for transcriptional dynamics, speed, or direction.
- **Trajectory inference methods** (Trapnell et al., *Nature Biotechnology*, 2014; Wolf et al., *Genome Biology*, 2019; Saelens et al., *Nature Biotechnology*, 2019): Model static snapshots without directional information from splicing kinetics.

#### Unique Contributions
1. **Dynamical model**: Solves the full gene-wise transcriptional dynamics (ODE system for unspliced/spliced mRNA) via expectation-maximization, recovering gene-specific rates of transcription ($\alpha$), splicing ($\beta$), and degradation ($\gamma$).
2. **Latent time**: Infers a gene-shared latent time that represents each cell's internal clock, grounded on transcriptional dynamics rather than similarity-based pseudo-time.
3. **Driver gene identification**: Ranks genes by model likelihood to identify putative drivers of differentiation.
4. **Stochastic model**: Extends the steady-state model with second-order moments (variances and covariances) for improved velocity estimation without the computational cost of the full dynamical model.
5. **Scalability**: >10x speedup over velocyto; handles >300,000 cells; near-linear scaling with cell number.

---

### Method Overview

#### Algorithmic Framework

scVelo implements three velocity estimation modes:

| Mode | Model | Key Idea | Runtime |
|------|-------|----------|---------|
| `deterministic` | Steady-state | Linear regression on extreme quantiles to estimate $\gamma/\beta$ ratio; velocity = deviation from steady state | <1 min |
| `stochastic` | Stochastic steady-state | Extends deterministic with second-order moments (covariation); generalized least squares | <1 min |
| `dynamical` | Full EM | Solves ODE system explicitly; infers $\alpha$, $\beta$, $\gamma$, latent time per cell via EM | ~20 min for 35k cells, 1k genes |

#### Core Pipeline

1. **Preprocessing**: Size normalization, gene filtering (top 2,000 HVGs with min 20 shared counts), kNN graph (30 neighbors in 30-PC space), first/second-order moment computation.
2. **Velocity estimation**: Per-gene ODE solving and parameter inference.
3. **Velocity graph**: Cosine similarity between velocity vectors and cell-to-cell expression differences.
4. **Latent time** (dynamical mode): Gene-shared time from per-gene time assignments.
5. **Downstream**: Transition probabilities, velocity embedding projection, terminal state identification, driver gene ranking.

#### Biological Assumptions
- Transcription follows a two-state model (on/off) with constant splicing ($\beta$) and degradation ($\gamma$) rates per gene.
- Each gene's dynamics are independent of other genes.
- Cells are sampled from a continuous developmental process; snapshot data captures diverse stages.

#### Pipeline Pseudocode (Dynamical Mode)

```
# Preprocessing
adata = filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
adata = moments(adata, n_neighbors=30, n_pcs=30)
  # → adata.layers['Ms'], ['Mu'], ['Mss'], ['Mus']

# Core dynamical model
for gene in velocity_genes:
    dr = DynamicsRecovery(gene_data)
    dr.initialize()                     # β=1, γ from quantile regression
    for iter in range(max_iter):
        E-step: assign τ_i via analytical inversion (Eq. 10-11)
                assign k_i via state likelihood
        M-step: update (α, β, γ, t_*) via Nelder-Mead
    store fit_alpha, fit_beta, fit_gamma, fit_t_, fit_scaling, fit_likelihood

# Velocity from inferred kinetics
velocity[i,g] = β_g * u[i,g] - γ_g * s[i,g]

# Latent time
shared_time = couple gene-wise times via root-anchored quantiles (Eq. 16-17)

# Downstream
velocity_graph = cosine_similarity(velocity, expression_differences)
transition_matrix = exponential_kernel(velocity_graph)
```

---

### Evaluation

#### Datasets
1. **Dentate gyrus neurogenesis** (Hochgerner et al., *Nature Neuroscience*, 2018): Mouse hippocampal dentate gyrus, two time points (P12, P35), droplet-based 10x Chromium scRNA-seq.
2. **Pancreatic endocrinogenesis** (Bastidas-Ponce et al., *Development*, 2019): Mouse pancreas E15.5, endocrine differentiation from ductal progenitors to $\alpha$/$\beta$/$\delta$/$\epsilon$-cells.
3. **Simulated splicing kinetics**: 2,000 log-normally distributed parameter sets; Poisson-distributed time events; varying induction durations (2-10 hours).

#### Key Results

| Metric | Dynamical Model | Stochastic Model | Steady-State Model |
|--------|----------------|-------------------|-------------------|
| Pearson correlation (true vs. inferred $\gamma/\beta$) | 0.97 | N/A | 0.71 |
| Sensitivity to induction duration | Insensitive | N/A | Systematic error increases with shorter induction |
| Recovery of kinetic rates ($\alpha$, $\beta$, $\gamma$) | Correlations ≥0.85 (with 20h prior) | N/A (only estimates ratio) | N/A (only estimates ratio) |
| CR cells correctly identified as terminal | Yes | — | No (erroneously assigns high velocity) |
| OPC→OL differentiation direction | Correct | — | Incorrect (points away) |
| Cell cycle in endocrine progenitors | Resolved | Partially resolved | Not captured |
| Chronology of $\alpha$ vs. $\beta$-cell fates | Correct ($\alpha$ earlier) | Not distinguished | Not distinguished |
| Velocity coherence (consistency score) | Highest | Intermediate | Lowest |
| $\alpha$-cell backflows | None | Present (as in steady-state) | Present |
| Dentate gyrus sublineages (granule, astrocyte, GABA) | All resolved | All resolved | Partially resolved |
| Runtime (25k cells) | ~20 min (1k genes) | <1 min | <1 min |

#### Benchmarked Methods
- **velocyto** (La Manno et al., *Nature*, 2018): Original steady-state RNA velocity implementation.
- **Diffusion pseudo-time (DPT)** (Haghverdi et al., *Nature Methods*, 2016): Similarity-based pseudo-time; used for comparison against latent time (not a velocity method).

#### Scalability Benchmarks
- Steady-state + stochastic: <1 min for 25,919 cells (full pipeline).
- Dynamical model: ~20 min for 35,000 cells × 1,000 genes.
- scVelo handles >300,000 cells on 64 GB RAM; velocyto fails at >40,000 cells.
- >10x speedup over velocyto; near-linear time scaling.

---

### Reproducibility

#### Rating: 4/5

#### Strengths
- Complete Python package available on GitHub and PyPI (`pip install scvelo`).
- Both example datasets are publicly available (GEO: GSE95753, GSE132188) and directly accessible via `scv.datasets`.
- Default parameters clearly specified; all analyses use defaults.
- Integrated with scanpy/AnnData ecosystem.
- Comprehensive documentation at [scvelo.org](https://scvelo.org).

#### Potential Blockers
- **Environment complexity**: Requires specific versions of scanpy, AnnData, and dependencies. Package has been mostly in maintenance mode since ~2022.
- **No explicit test suite for paper results**: Unit tests exist but do not reproduce paper figures.
- **Simulated data generation**: Simulation parameters are described in the paper but the exact simulation script for reproducing Figure S3 is not provided in the main repository.
- **Velocyto preprocessing required**: Spliced/unspliced count annotations need velocyto CLI or kallisto pseudo-alignment, adding an upstream dependency.

#### Data Availability
| Dataset | Accession | Direct Access |
|---------|-----------|---------------|
| Dentate gyrus | GSE95753 | `scv.datasets.dentategyrus()` |
| Pancreas | GSE132188 | `scv.datasets.pancreatic_endocrinogenesis()` |
| Analysis notebooks | — | [theislab/scvelo_notebooks](https://github.com/theislab/scvelo_notebooks) |

---

### Discussion & Limitations (from the paper)

#### Maintained Assumptions
The dynamical model relaxes the steady-state and common-splicing-rate assumptions but retains:
- **Constant gene-specific rates**: $\beta$ and $\gamma$ are time-independent within a kinetic regime. Real systems may exhibit state-dependent degradation or alternative splicing.
- **Two-state transcription**: Only on/off switching is modeled. More complex transcriptional regulation (e.g., graded activation, multiple enhancer states) is not captured.
- **Gene independence**: Each gene is modeled in isolation; coordinated regulation (e.g., transcription factor cascades) is not explicitly modeled.

#### Extensions Proposed by Authors
1. **Full-length protocols** (Smart-seq2): Enable accounting for gene structure, alternative splicing, and state-dependent degradation.
2. **Spatial transcriptomics**: Could provide spatial constraints to resolve position-dependent gene regulation.
3. **Stochastic dynamical model**: Combine second-order moments with the full EM framework (left for future work).
4. **Metabolic labeling** (scSLAM-seq): Quantify new vs. total RNA directly, incorporating varying labeling lengths as priors.
5. **Protein velocity**: Extend the kinetic chain to translation ($s \to p$ with rate $\delta$).
6. **Regulatory motifs**: Couple single-gene models to infer gene regulatory networks.

#### Practical Caveats (from the paper)
- **Always inspect phase portraits**: Users should examine individual gene phase portraits (e.g., `scv.pl.scatter(adata, basis=gene_name)`) rather than relying solely on projected velocity streamlines. Projected velocities average over hundreds of genes and can mask gene-level issues.
- **Test for differential kinetics**: The differential kinetic test (`scv.tl.differential_kinetic_test()`) should be applied to detect populations with distinct kinetic regimes (e.g., CR cells in dentate gyrus, which follow a different trajectory).
- **Root prior for straight-line phase portraits**: For genes with insufficiently observed kinetics ($R^2 > 0.95$ in phase space), the root prior is needed but requires either an informative gene set or prior knowledge (e.g., known progenitor population via `root_key` parameter).
- **Time-scale mismatches**: When the developmental process is faster than the kinetic timescale, observable dynamics are limited. This manifests as straight-line phase portraits for most genes and low consistency scores.
- **Stochastic model limitations**: The stochastic model improves over steady-state in many scenarios but still fails in the same situations as steady-state (e.g., $\alpha$-cell backflows in pancreas), because it extends the steady-state assumption rather than solving the full dynamics.

#### Impact
scVelo became the de facto standard for RNA velocity analysis (>3,000 citations by 2024), used in studies of lung regeneration, immune response, cancer progression, and numerous developmental systems. It is integrated into the scverse ecosystem alongside scanpy and was a precursor to more recent velocity methods (e.g., veloVI, UniTVelo, CellRank) that build upon its dynamical framework.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
