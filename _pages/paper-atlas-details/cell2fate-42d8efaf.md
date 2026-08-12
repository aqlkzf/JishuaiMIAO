---
layout: default
permalink: /paper-atlas/cell2fate-42d8efaf/
title: "cell2fate"
nav: false
description: "标准 RNA velocity 对每个基因使用转录、剪接、降解方程，但常把转录率简化成一次开启、一次关闭。真实发育过程中，同一基因可能被多个程序在不同阶段反复增强或抑制。cell2fate 的核心思想是：把复杂的时间依赖转录率拆成多个可解析的“模块”，每个模块有自己的开启/关闭时间窗、基因载荷和接近目标转录率的速度。各模块的表达和 velocity 相加，既得到完整动力学，也得到一个带生化意义的低维分解。"
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
    <h1>cell2fate</h1>
    <p>Cell2fate infers RNA velocity modules to improve cell fate prediction</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02608-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cell2fate：把 RNA 动力学拆成可解释的时间模块

### 1. 核心问题

标准 RNA velocity 对每个基因使用转录、剪接、降解方程，但常把转录率简化成一次开启、一次关闭。真实发育过程中，同一基因可能被多个程序在不同阶段反复增强或抑制。cell2fate 的核心思想是：把复杂的时间依赖转录率拆成多个可解析的“模块”，每个模块有自己的开启/关闭时间窗、基因载荷和接近目标转录率的速度。各模块的表达和 velocity 相加，既得到完整动力学，也得到一个带生化意义的低维分解。

论文为 Aivazidis et al., “Cell2fate infers RNA velocity modules to improve cell fate prediction,” *Nature Methods* 22, 698–707 (2025)，DOI `10.1038/s41592-025-02608-3`。本地补充 Markdown `output_supp1_md/paper_supp1/paper_supp1.md` 含完整公式、先验和比较；另有 supplementary/reporting PDF。代码来自 `BayraktarLab/cell2fate` 系谱，但没有记录 commit，`setup.cfg` 仍标为 `0.01a` 且 URL 指向早期作者仓库，不能视作精确期刊版本快照。

### 2. 基础 ODE 与模块线性化

对基因 $g$：

$$
\frac{du_g}{dt}=\alpha_g(t)-\beta_g u_g,
\qquad
\frac{ds_g}{dt}=\beta_g u_g-\gamma_g s_g.
$$

$u,s$ 分别是 unspliced 与 spliced RNA；$\beta_g,\gamma_g$ 是基因级、全细胞共享的剪接和降解率。RNA velocity 是

$$
v_g=\frac{ds_g}{dt}=\beta_g u_g-\gamma_gs_g.
$$

cell2fate 不是直接给 $\alpha_g(t)$ 一个任意神经网络，而是写成模块之和。对模块 $m$：

$$
\frac{d\alpha_{mg}}{dt}
=\lambda_{mi}(\hat\alpha_{mgi}-\alpha_{mg}),
$$

状态 $i$ 由细胞时间 $T_c$ 是否落在 $T_{mON}$ 与 $T_{mOFF}$ 之间决定。ON 时目标为 $A_{mgON}$，OFF 时目标为 0。$\lambda_{mi}$ 决定转录率以多快速度指数接近目标。

总量为

$$
\alpha_g=\sum_m\alpha_{mg},\quad
u_g=\sum_m u_{mg},\quad
s_g=\sum_m s_{mg},\quad
v_g=\sum_m v_{mg}.
$$

因为每个模块都是线性常系数 ODE 的分段组合，所以 $\alpha,u,s$ 都有闭式解。`cell2fate/utils.py` 的 `mu_alpha()` 和 `mu_mRNA_continousAlpha_globalTime_twoStates()` 实现 ON/OFF 两段解析传播；`_cell2fate_DynamicalModel_module.py` 汇总模块贡献。

### 3. 一个模块从 OFF 到 ON 再到 OFF

模块在 $T_{mON}$ 前为零。进入 ON 后，令 $\tau=T_c-T_{mON}$：

$$
\alpha_{mg}(\tau)
=\alpha^0_{mgi}+(\hat\alpha_{mgi}-\alpha^0_{mgi})(1-e^{-\lambda_{mi}\tau}).
$$

$u_{mg}$ 和 $s_{mg}$ 的解由 $e^{-\lambda\tau}$、$e^{-\beta\tau}$、$e^{-\gamma\tau}$ 的线性组合构成。到 $T_{mOFF}$ 时，代码先评价 ON 解得到连续初值，再把目标改为零并解 OFF 段。因此表达、转录率和 velocity 在切换点连续，而不是硬跳变。

这种表达能力来自多个模块叠加：一个基因可以在早期模块和晚期模块都有载荷，从而出现多次 transcriptional boost。代价是模块数、时间顺序和先验会影响分解；模块不是实验直接测得的调控复合体。

### 4. 为什么模块也是一种降维

模块 ON 目标写成

$$
A_{mgON}=g_{mg}\gamma_g.
$$

$g_{mg}$ 类似 gene loading，描述模块 $m$ 对基因 $g$ 的稳态贡献；由时间和开关决定的标准化激活类似 cell loading。于是

$$
\alpha_g(T_c)=\sum_m A_{mgON}\alpha'_{mg}(T_c).
$$

它形式上像 NMF，但 cell loading 不是自由矩阵，而必须服从模块 ODE 的时间形状。Fig. 1 中的模块时间曲线和 gene loading 正是这个桥梁。模块 velocity 还能指出某一阶段哪些程序正在推高或降低成熟 RNA。

这种“模块”是统计—动力学成分；高载荷基因和 TF 富集可帮助命名模块，但不能据此声称模块本身就是一个已验证的因果 GRN。

### 5. 原始计数测量模型

cell2fate 直接建模 raw spliced/unspliced counts，而不是先归一化和 KNN 平滑。生物期望 $x^B_{cgj}$ 经技术层变为

$$
x^M_{cgj}=l_{cgj}(H_{ce}s_{egj}+x^B_{cgj}),
$$

其中 $H_{ce}$ 是 batch assignment，$s_{egj}$ 是 batch/gene/RNA 类型特异 ambient RNA，$l_{cgj}$ 分解细胞测序深度以及 spliced/unspliced、基因特异检测效率。观察计数使用负二项（代码中 Gamma–Poisson）似然，并分别为 spliced/unspliced 设置过度离散。

`_cell2fate_DynamicalModel.setup_anndata()` 明确注册 raw `unspliced`、`spliced` layer 和可选 batch；Pyro module 构造生物均值、技术修正和 `GammaPoisson` 观察。此层能减少批次/深度被误认为 velocity，但模型设定错误的 ambient 或 detection prior 仍会影响动力学参数。

### 6. 贝叶斯层级模型与训练

未知量包括：

- 每个细胞的过程时间 $T_c$；
- 模块 ON/OFF 时间与 activation/deactivation rates；
- 模块—基因载荷 $A_{mgON}$；
- 基因剪接/降解率 $\beta_g,\gamma_g$；
- batch、ambient、检测效率和过度离散参数。

补充材料为这些变量定义层级 Gamma 等先验，并用 Pyro stochastic variational inference 近似后验。`AutoHierarchicalNormalMessenger` 让变分位置保留部分层级依赖，而非完全独立 mean-field。外层 `Cell2fate_DynamicalModel.train()` 默认 500 epochs、batch size 1000、lr 0.01，并调用 scvi-tools 的 Pyro SVI 基础设施。

输出不是单一值：`export_posterior()` 写出均值、标准差、5%/95% 分位数、潜时间和 velocity uncertainty。后验窄只表示在给定模型/先验下参数集中，不包含数据集选择、模型错误或真实谱系不确定性。

### 7. 模块数与稳健拟合

模块数并非完全由边际似然自动决定。论文/工作流使用聚类结构和经验规则选取足够模块，再检查是否覆盖过程。源码工具还包含多次训练、正向/反向时间初始化或择优流程，以避免 SVI 局部最优；这一实际 workflow 对复现重要，但主论文叙述不如源码/教程详细。

模块开关时间通过累积间隔先验倾向顺序出现，但窗口可重叠。若模块数太少，会把多个转录阶段挤在一起；太多则可能把噪声拆成小模块。不同随机初始化得到相似方向，不等于模块编号一一可比，跨运行需要按载荷和时间对齐。

### 8. 从后验到 velocity 与 fate

模型对每个后验样本计算 $u,s$ 和 $v_s=\beta u-\gamma s$，再汇总平均与不确定性。velocity graph/stream embedding 使用类似 Bergen et al. 的邻域投影，把高维 velocity 显示在 UMAP 上。二维箭头仍依赖邻居图与嵌入，主证据应回到模块时间、基因拟合和已知转变边界。

cell fate prediction 不是模型直接输出一个监督分类标签，而是由 velocity graph、转移概率和下游 fate 工具得到。论文用 CBDir、cluster time differences 和已知发育顺序评价方向。因而“改善 fate prediction”意味着推断方向更符合这些外部/先验边界，不是逐细胞未来命运全部被真实追踪。

### 9. 图与补充证据

- Fig. 1 展示解析模块、基因载荷和与混合成员模型的联系。
- Fig. 2 在 dentate gyrus 中用连续模块解析晚期 granule neuron maturation，并与常规聚类/velocity 方法比较。
- Fig. 3–5 比较多个数据集的 CBDir、时间方向和多速率基因；说明 cell2fate 在测试集合上的平均方向表现。
- Fig. 6/空间应用把 snRNA-seq 模块稳态表达作为 cell2location reference 映射到脑组织；这是下游组合，不是 cell2fate 本身使用空间邻接拟合 velocity。
- Supplementary Note 1 给出约 75 个核心公式、测量层、先验和 SVI；后续补充图检验 prior sensitivity、半模拟数据、运行时间和各方法差异。

### 10. 论文—代码映射

| 机制 | 当前源码 | 状态 |
|---|---|---|
| 连续转录率 ON/OFF 解析解 | `cell2fate/utils.py` | Confirmed |
| 模块求和的 $u,s,v$ | `_cell2fate_DynamicalModel_module.py` | Confirmed |
| raw count + batch/ambient/detection/NB | 同一 Pyro module | Confirmed |
| 层级先验与 SVI guide | `_pyro_base_cell2fate_module.py`, `AutoAmortisedNormalMessenger.py` | Confirmed |
| AnnData 入口、训练、后验导出 | `_cell2fate_DynamicalModel.py:61-164,331` 起 | Confirmed |
| amortized 版本 | `_cell2fate_DynamicalModel_amortized*` | Confirmed，但需与主文默认模型区分 |
| 期刊论文全部 benchmark notebook | 外部 notebooks 仓库；本地核心包不完整包含 | Partial |
| 精确期刊发布 commit/version | 无 commit；setup.cfg `0.01a` 且仓库 URL 历史不一致 | Not found |

### 11. 生物与复现边界

1. $\beta_g,\gamma_g$ 对所有细胞固定，无法表达细胞状态特异剪接/降解。
2. 单一 $T_c$ 和顺序模块适合连续过程，但不显式建模分叉点的随机命运选择；不同分支可能通过时间/模块组合间接表示。
3. 模块载荷不编码模块之间的因果调控，窗口之间可重叠。
4. velocity 方向依赖计数质量、spliced/unspliced 定量、先验、模块数与优化解。
5. 空间映射使用模块表达 signature，不是从 Visium 的 RNA velocity 直接拟合动态。
6. 当前代码依赖较老的 scvi-tools/Pyro/PyTorch 环境；无 commit 使精确复现期刊运行存在版本边界。

cell2fate 最恰当的定位是：一个将复杂转录率表示为多个可解析时间模块，并在原始计数的层级贝叶斯测量模型中联合推断时间、动力学和技术效应的方法。它提高了多阶段基因动力学与弱 velocity 信号的可解释性，但模块与 fate 仍是模型条件下的统计推断，而不是直接观察到的调控机制或单细胞命运。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cell2fate: RNA Velocity Modules for Cell Fate Prediction

**Paper**: Aivazidis A, Memi F, Kleshchevnikov V, Er S, Clarke B, Stegle O, Bayraktar OA. Cell2fate infers RNA velocity modules to improve cell fate prediction. *Nature Methods* 22, 698–707 (2025).

**DOI**: [10.1038/s41592-025-02608-3](https://doi.org/10.1038/s41592-025-02608-3)

**Code**: [https://github.com/BayraktarLab/cell2fate](https://github.com/BayraktarLab/cell2fate)

---

### Motivation & Novelty

#### Biological Problem

RNA velocity — the inference of transcriptional dynamics from spliced and unspliced RNA counts — enables reconstruction of cell fate trajectories from single-cell RNA-seq data. However, existing RNA velocity models face fundamental tradeoffs:

- **Simplified kinetic models** (scVelo, *Nature Biotechnology* 2020; velocyto, *Nature* 2018; PyroVelocity, *bioRxiv* 2022): assume stepwise transcription rates $\alpha_g(t)$ with at most one non-zero value, missing multi-rate kinetic genes
- **Numerical solvers** (DeepVelo, *Genome Biology* 2024; VeloVAE, *Cell Reports Methods* 2023; LatentVelo, *bioRxiv* 2022): allow complex $\alpha_g(t)$ but resort to numerical ODE approximations, impairing scalability, accuracy, and interpretability

#### Limitations of Existing Approaches

1. **Weak dynamical signals** in mature/rare cell types are unresolved (e.g., late granule neuron maturation in dentate gyrus)
2. **Multi-rate kinetic genes** — genes with multiple transcription rate boosts across trajectories — cannot be captured by single-step models
3. **No measurement model** for raw counts: most methods require normalization and kNN smoothing
4. **No uncertainty quantification**: point estimates without posterior distributions
5. **No connection to dimensionality reduction**: velocity and decomposition are separate analyses

#### Unique Contributions

1. **Linearization of the velocity ODE**: decomposes $\frac{d\alpha_g}{dt}$ into a sum of $M$ integrable basis functions (modules), enabling analytical solutions for arbitrarily complex transcription rate dynamics
2. **Biophysical module decomposition**: each module corresponds to a time-windowed transcriptional program, providing a mechanistic link between RNA velocity and dimensionality reduction
3. **Comprehensive measurement model**: negative binomial likelihood on raw counts, with batch correction, ambient RNA modeling, and differential detection efficiency for spliced/unspliced RNA
4. **Fully Bayesian inference**: hierarchical priors with posterior uncertainty quantification via stochastic variational inference in Pyro
5. **Spatial integration**: module steady-state expression serves as reference signatures for cell2location spatial deconvolution

---

### Method Overview

#### Core Innovation: Linearized Transcription Rate

Cell2fate approximates the complex transcription rate function $\frac{d\alpha_g}{dt} = F_\alpha(t)$ as a linear sum of $M$ modules:

$$\frac{d\alpha_g}{dt} = \sum_{m=1}^{M} \lambda_{mi}(\hat{\alpha}_{mgi} - \alpha_{mg})$$

Each module $m$ has:
- **ON/OFF states** controlled by switch times $T_{m,\text{ON}}$, $T_{m,\text{OFF}}$ on a cell-specific timescale $T_c$
- **Target transcription rate** $\hat{\alpha}_{mgi}$ (nonzero when ON, zero when OFF)
- **Activation rate** $\lambda_{mi}$ governing the exponential approach to the target

This linearization allows the coupled ODEs for unspliced and spliced counts to be solved **analytically** for each module, with the total solution being the sum of module-level solutions.

#### Computational Pipeline

1. **Input**: raw spliced and unspliced count matrices (no normalization needed)
2. **Model fitting**: stochastic variational inference (Pyro/scvi-tools), ~8–19 min on GPU
3. **Outputs**: cell-specific times $T_c$, module switch times, gene-specific rates ($\beta_g$, $\gamma_g$), module gene loadings, velocity vectors, posterior uncertainties
4. **Downstream**: velocity graph embedding, module activation trajectories, module state classification, module marker genes, TF identification, spatial mapping via cell2location

#### Key Biological Assumptions

- Constant per-gene splicing rate $\beta_g$ and degradation rate $\gamma_g$ (no cell-specific rates)
- No stochastic bifurcations at lineage branching
- Transcription rate changes approximated as exponential approaches to targets within time windows
- Sequential module activation (enforced by cumulative sum constraint on $T_{m,\text{ON}}$)

---

### Evaluation

#### Datasets (5 benchmarks + 1 spatial application)

| Dataset | Species | Cells | Challenge |
|---------|---------|-------|-----------|
| Mouse dentate gyrus | Mouse | 2,930 | Late granule neuron maturation (weak signal) |
| Mouse pancreas | Mouse | 3,669 | Standard benchmark |
| Mouse bone marrow | Mouse | 2,600 | Low UMI counts |
| Mouse erythroid maturation | Mouse | 9,815 | Multi-rate kinetic genes |
| Human bone marrow | Human | 5,780 | Complex trajectories |
| Human developing brain | Human | 9,443 | Spatial integration (snRNA-seq + Visium) |

#### Benchmarked Methods (11 total, including cell2fate)

| Method | Version | Publication |
|--------|---------|------------|
| scVelo (dynamical + stochastic) | 0.2.5 | *Nature Biotechnology*, 2020 |
| UniTVelo (independent + unified) | 0.2.5 | *Nature Communications*, 2022 |
| DeepVelo | 0.2.5-rc.1 | *Genome Biology*, 2024 |
| VeloVAE | N/A | *Cell Reports Methods*, 2023 |
| VeloVI | 0.1.1 | *Nature Methods*, 2024 |
| cellDancer | — | *Nature Biotechnology*, 2024 |
| PyroVelocity (model1 + model2) | 0.1.0 | *bioRxiv*, 2022 |
| cell2fate | — | This paper (*Nature Methods*, 2025) |

#### Metrics

- **CBDir** (Cross-Boundary Directional Correctness): consistency of transition probabilities at cluster boundaries with known transitions
- **Time difference concordance**: agreement of estimated time differences between clusters with prior knowledge
- **Developmental age correlation**: comparison of inferred time to known developmental ages of mouse samples

#### Key Results

1. **Best average CBDir** across all 5 datasets; only method (with pyroVelocity_model2) to never infer reverse-order dynamics (negative CBDir = reversed trajectory direction)
2. **Late granule neuron maturation** resolved: 6 sequentially activated modules (4–9) dissect the trajectory into distinct transcriptional windows, unresolved by all other methods and by MOFA/Leiden clustering
3. **Multi-rate kinetic genes** (e.g., *Hba-x*, *Nudt4*) correctly recapitulated as stepwise transcription rate boosts in erythroid maturation; pyroVelocity_model2 can only capture a single boost
4. **Posterior CV** near 0 for dynamic datasets, near 1 for steady-state PBMC data — serves as built-in quality control. Heuristic confidence score for transitions correlates with CBDir ($\rho = 0.56$)
5. **Spatial mapping**: RNA velocity modules spatially resolved across cortical layers in human brain — immature ULn modules map to upper layers + intermediate zone, mature DLn module 5 exclusively to deep layers
6. **Robust** to prior distribution changes (Supplementary Fig. 11) and validated on semisynthetic data (Supplementary Fig. 12)
7. **Competitive runtime**: ~3–19 min on Tesla V100, comparable to other GPU-based methods

#### Limitations (Acknowledged by Authors)

- Assumes **constant per-gene degradation rate** — no cell-specific rates
- **No stochastic bifurcations** at lineage branching points (cannot model fate choice)
- Does not model **cell-cell interactions** or spatial signaling effects on transcription
- Performance depends on the assumption that transcription rate changes can be decomposed into independent modules — may not capture causal regulatory dependencies between time points

---

### Reproducibility

#### Rating: 4/5

#### Strengths
- Full code available on GitHub ([BayraktarLab/cell2fate](https://github.com/BayraktarLab/cell2fate)) and archived on Zenodo
- Benchmarking notebooks available ([cell2fate_notebooks](https://github.com/AlexanderAivazidis/cell2fate_notebooks), [fate_benchmarking](https://github.com/AlexanderAivazidis/fate_benchmarking))
- All datasets downloadable from [data portal](https://cell2fate.cog.sanger.ac.uk/browser.html)
- FASTQ data deposited on ENA (PRJEB79988)
- Detailed Supplementary Notes with complete mathematical derivations (75 equations)
- Default hyperparameters work across all benchmark datasets

#### Potential Blockers
- Pinned dependency versions: `scvi-tools==0.16.1`, `torch==1.11.0`, `jax==0.4.10` — may cause compatibility issues on newer systems
- GPU required for practical runtimes (CPU feasible but slow)
- Robust optimization procedure (forward + reversed time, 3 training runs) in `utils.py` not described in the main paper — may affect reproducibility if not used
- Number of modules determined heuristically from Leiden clustering resolution

#### Data Availability
- Raw UMI counts + metadata in AnnData format: [cell2fate.cog.sanger.ac.uk/browser.html](https://cell2fate.cog.sanger.ac.uk/browser.html)
- Human brain FASTQ: ENA accession PRJEB79988

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
