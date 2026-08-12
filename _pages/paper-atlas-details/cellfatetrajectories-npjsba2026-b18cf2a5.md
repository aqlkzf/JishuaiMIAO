---
layout: default
permalink: /paper-atlas/cellfatetrajectories-npjsba2026-b18cf2a5/
title: "CellFateTrajectories_npjSBA2026"
nav: false
description: "这不是提出单一新算法的原创方法论文，而是一篇方法综述。它把不同时间点采到的、彼此不配对的单细胞分布视为随时间演化的概率分布，并用“spatiotemporal Dynamical Generative Model（stDGM）”统一最优传输、Schrödinger bridge、流匹配、增长/死亡、空间对齐和细胞相互作用方法。 核心问题是：Day 2 与 Day 4 的细胞不是同一批细胞，如何从若干 snapshot 推断中间连续动力学。"
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
      <span>npj Systems Biology and Applications · 2026</span>
    </div>
    <h1>CellFateTrajectories_npjSBA2026</h1>
    <p>Deciphering cell-fate trajectories using spatiotemporal single-cell transcriptomic data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41540-025-00624-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 时空单细胞命运轨迹：中文综述导读

### 这篇文章在统一什么

这不是提出单一新算法的原创方法论文，而是一篇方法综述。它把不同时间点采到的、彼此不配对的单细胞分布视为随时间演化的概率分布，并用“spatiotemporal Dynamical Generative Model（stDGM）”统一最优传输、Schrödinger bridge、流匹配、增长/死亡、空间对齐和细胞相互作用方法。

核心问题是：Day 2 与 Day 4 的细胞不是同一批细胞，如何从若干 snapshot 推断中间连续动力学。任何解都依赖模型假设；轨迹是满足假设的生成性解释，不是直接观测的单细胞历史。

### 数学谱系的主线

#### 从静态 OT 到动态 OT

静态 optimal transport 只求两个分布之间的最小代价耦合。动态 OT 把它写成连续时间密度 $\rho_t$ 与速度场 $v_t$，满足连续性方程：

$$\partial_t\rho+\nabla\cdot(\rho v)=0.$$

它适合细胞总“质量”近似守恒的确定性演化，但不能自然表达增殖、死亡或随机扩散。

#### Unbalanced OT

加入增长率 $g(x,t)$：

$$\partial_t\rho+\nabla\cdot(\rho v)=g\rho.$$

这允许不同时间点细胞数变化。选择 unbalanced 模型应有实验依据；测序捕获量变化不必然等于真实增殖/死亡。

#### Schrödinger bridge 与 score

SB 在参考随机过程附近寻找连接端点分布的最可能随机动力学，可表示细胞命运的不确定性。score 项与密度梯度有关，常用于随机反向动力学和 Waddington landscape。随机性更强不等于更真实；扩散强度仍需验证。

#### Mean-field interaction

当细胞之间通过接触或信号相互影响，漂移可依赖群体分布。UMFSB 同时容纳 velocity、growth、score 与 interaction，是综述中假设最宽的框架，也带来最高的数据与可辨识性要求。

#### 空间对齐

空间转录组跨时间点可能存在旋转、平移或组织形变。GWOT 比较样本内部距离结构；RBTI-OT 显式处理刚体变换。若坐标未可靠对齐，空间位移不能直接解释为细胞迁移。

### 如何按生物问题选模型

- 只关心相邻 snapshot 配对：静态/多阶段 OT。
- 需要连续插值和速度场：动态 OT、Neural ODE 或 flow matching。
- 真实细胞数显著变化：unbalanced OT，并核实采样偏差。
- 需要随机命运分叉：SB/SDE/score 模型。
- 不同时间或模态特征空间不可直接比较：GW/跨域 OT。
- 相互作用是问题核心：mean-field/interaction 模型，但需更多数据和验证。

“更一般”不是“更好”。每增加 growth、stochasticity 或 interaction，模型也增加不可辨识自由度。应选择最小但足以回答问题的假设集合。

### 图的左到右读法

- Figure 1A 从原始计数、时间标签和可选空间坐标，经标准化/HVG/低维表示进入模型。
- Figure 1B 把 velocity、growth、stochasticity 与 interaction 画成可组合动力学组件。
- Figure 1C 展示速度流线、时间插值、增长率、势景观、CellRank fate probability 与 GRN/扰动分析；这些是推断下游，不是独立实验真值。
- Figure 2A 是理论时间线；Figure 2B 以数据假设、建模策略、训练方法三种符号排列“algorithm zoo”。它是分类地图，不是性能排行榜。
- Figure 3/CytoBridge 选择图显示组件组合如何对应不同理论；Figure 4 用 Day 2–6 造血例子展示生成轨迹与随机增殖/死亡。

### CytoBridge 的证据边界

文章介绍正在开发的 CytoBridge 作为统一软件接口，并给出预处理、`fit`、下游分析和轨迹生成示例。但本 PaperCode 工作区没有克隆 CytoBridge 源码，因此不能验证 API、版本或结果复现。论文也明确称该包持续更新；这里的代码片段应视为发表时的概念性使用指南，而非当前稳定 API 合同。

### 关键局限

1. snapshot 数据本身不能唯一决定单细胞对应关系。
2. 模型通常擅长时间范围内插值，超出训练区间的外推更脆弱。
3. 低维嵌入有利于训练，却可能丢失基因层面的可解释信号；回投原基因空间需要误差检查。
4. velocity、growth、score 与 interaction 可相互补偿，需 lineage tracing、增殖测量或扰动实验做外部验证。
5. 综述涵盖大量 2025 年预印本；方法成熟度、软件维护和基准证据并不一致。

### 证据入口

- 全文：`paper source/paper/paper.md`
- 本地图：`paper source/paper/*.jpeg`
- 综述总结：`summary.md`
- 方法谱系：`doc_method.md`
- 阅读札记：`reading_notes.md`
- 逐图解读：`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Deciphering Cell-Fate Trajectories Using Spatiotemporal Single-Cell Transcriptomic Data

### Review Scope & Context

**Paper**: Zhang, Z., Wang, Z., Sun, Y., Shen, J., Peng, Q., Li, T. & Zhou, P. "Deciphering cell-fate trajectories using spatiotemporal single-cell transcriptomic data." *npj Systems Biology and Applications* 12:2 (2026). DOI: 10.1038/s41540-025-00624-9

**Field surveyed**: Computational methods for trajectory inference from time-series single-cell RNA-seq and spatiotemporal spatial transcriptomics data. The review specifically focuses on methods designed for *temporally resolved* (multi-time-point) data rather than single-snapshot pseudotime approaches.

**Time span**: The methods reviewed span from foundational optimal transport theory (Monge, 1781) through the modern explosion of deep-learning-based approaches up to mid-2025. The majority of reviewed algorithms were published between 2019 and 2025.

**Why timely**: The field has experienced explosive growth in 2023--2025, with dozens of new methods based on flow matching, Schrodinger bridges, and unbalanced optimal transport being published at top ML venues (NeurIPS, ICML, ICLR, AISTATS). The authors note this is an "algorithmic zoo" in rapid expansion. The paper unifies these under the "spatiotemporal Dynamical Generative Model" (stDGM) conceptual framework and introduces CytoBridge as an accompanying software package.

**Authors**: From Peking University (LMAM, Center for Quantitative Biology, Center for Machine Learning Research). The senior authors (Tiejun Li, Peijie Zhou) are developers of several key methods reviewed (TIGON, DeepRUOT, Var-RUOT, stVCR, CytoBridge).

---

### Field Landscape

The review covers **50+ trajectory inference algorithms** organized around a hierarchy of mathematical frameworks. The biological domains discussed include:

- **Embryogenesis and development**: Mouse embryogenesis, Drosophila embryo development, zebrafish development
- **Hematopoiesis**: Mouse blood hematopoiesis with lineage tracing
- **Epithelial-to-mesenchymal transition (EMT)**: Cancer-related cell-state transitions
- **Regeneration**: Axolotl brain regeneration
- **Perturbation prediction**: Drug response, gene knockouts

The methods are categorized along three independent axes:
1. **Data Assumption**: What biological features the data captures (balanced vs. unbalanced, count data, manifold structure, spatial data, cross-domain, conditional)
2. **Modeling Strategy**: The mathematical framework (discrete-time, stochastic dynamics, momentum dynamics, cell-cell interactions)
3. **Training Method**: How the model is computationally solved (Neural ODE/SDE, flow matching, simulation-free, optimality conditions, closed-form solutions)

---

### Method Taxonomy

#### Mathematical Foundations Hierarchy

```
Static Optimal Transport (1781/1942)
|
+-- Dynamical Optimal Transport (Benamou-Brenier, 2000)
|   |
|   +-- Unbalanced Dynamical OT (WFR distance, 2015)
|   |   |
|   |   +-- Regularized Unbalanced OT (RUOT) (2021)
|   |       |
|   |       +-- Unbalanced Mean-Field Schrodinger Bridge (UMFSB) (2025)
|   |
|   +-- Schrodinger Bridge (1932/stochastic control)
|       |
|       +-- Mean-Field Schrodinger Bridge (MFSB) (2019)
|           |
|           +-- UMFSB (2025)
|
+-- Gromov-Wasserstein OT (2009)
|
+-- Rigid Body Transformation Invariant OT (RBTI-OT)
```

#### Data Assumption Categories

| Category | Description | Representative Methods |
|----------|-------------|----------------------|
| Unbalanced Data | Cell proliferation/death changes total mass | TIGON, DeepRUOT, stVCR, VGFM |
| Count Data | Discrete gene expression counts (Poisson/NB) | Euclidean VAE |
| Low-Dim Manifold | Data on restricted manifold, not full Euclidean space | MIOFlow, Metric FM, WLR, Topological SB |
| Cross-Domain Mapping | Different feature spaces across conditions/modalities | MOSCOT, GENOT, SCOT+ |
| Spatial Data | Gene expression + physical coordinates | stVCR, DeST-OT, STORIES |
| Conditional Modeling | Categorical labels (treatment, dosage) | CFGen, CellFlow, MMFM |

#### Modeling Strategy Categories

| Category | Description | Representative Methods |
|----------|-------------|----------------------|
| Discrete-Time Dynamics | Static OT mapping between snapshots | WaddingtonOT, MOSCOT, Multistage OT, scEGOT |
| Continuous Deterministic | ODE-based continuous trajectories | TrajectoryNet, OT-CFM, MIOFlow |
| Stochastic Dynamics | SDE with Brownian noise (Schrodinger Bridge) | SF2M, PISDE, FBSDE Model, Lagrangian SB |
| Unbalanced Dynamics | Growth/death source terms | TIGON, DeepRUOT, Var-RUOT, VGFM |
| Momentum Dynamics | Second-order effects (inertia) | 3MSBM |
| Cell-Cell Interaction | Intercellular coupling forces | MetaFM, scIMF, GraphFP, CytoBridge |

#### Training Method Categories

| Category | Description | Representative Methods |
|----------|-------------|----------------------|
| Neural ODE/SDE | Backprop through ODE/SDE solver | TrajectoryNet, TIGON, DeepRUOT, CytoBridge |
| Flow Matching | Simulation-free, conditional FM | OT-CFM, SF2M, Metric FM, VGFM, CellFlow |
| Directly Solve Static OT | Sinkhorn or LP solvers | WaddingtonOT, MOSCOT, DeST-OT |
| Optimality Conditions | HJB/Pontryagin-based | PRESCIENT, Action Matching, Var-RUOT |
| Closed-Form Solution | Analytical for Gaussian cases | SB between Gaussian, scEGOT |
| Maximum Likelihood | Likelihood-based training | Pseudo Dynamics, Likelihood Training SB |

---

### Key Findings

1. **Unified framework**: All reviewed methods can be understood as instances of the stDGM framework, which learns mappings between time-resolved cell distributions by optimizing action functionals subject to continuity/Fokker-Planck equation constraints.

2. **Progressive relaxation of assumptions**: The field has progressively relaxed biological assumptions -- from mass conservation (standard OT) to unbalanced transport (proliferation/death), from deterministic to stochastic, and from independent cells to interacting populations. The UMFSB framework represents the most general formulation.

3. **Flow matching has become dominant**: Since 2023, conditional flow matching has emerged as the preferred training paradigm due to its simulation-free nature, scalability, and compatibility with various OT/SB formulations.

4. **HJB-based approaches are more efficient**: Learning a single scalar field (Lagrange multiplier $\lambda$) via the HJB equation simultaneously yields velocity, growth rate, and density, providing faster and more stable optimization than separately parameterizing each component.

5. **Spatial data requires special treatment**: Methods for spatiotemporal ST data must handle coordinate alignment (via GWOT or RBTI-OT) in addition to gene expression dynamics, and can jointly infer migration, differentiation, and proliferation.

6. **Generative capability is a key advantage**: Unlike static pseudotime methods, stDGM methods serve as generative models that can interpolate cell states at unobserved time points, simulate forward trajectories, and predict perturbation responses.

7. **Model selection is biology-driven**: The choice of framework depends on whether cell number changes matter (unbalanced), whether stochasticity is biologically relevant (SB), and whether cell-cell interactions shape fate decisions (mean-field).

---

### Open Problems & Future Directions

1. **Multi-modal integration**: Combining transcriptomic time series with epigenomic, proteomic, and imaging measurements for more comprehensive regulatory dynamics views.

2. **Lineage tracing validation**: Incorporating clonal recording and lineage tracing technologies to experimentally validate computationally inferred trajectories.

3. **Spatial-temporal resolution coupling**: Explicitly coupling intracellular dynamics with cell-cell interactions and tissue-level organization as spatial/temporal resolution improves.

4. **Cell mechanics integration**: Modeling cellular morphogenesis in physical space to provide multiscale perspectives on development and disease.

5. **Temporal generalization**: Current models excel at interpolation but degrade when extrapolating beyond training time ranges.

6. **Sensitivity to initial conditions**: Errors in early time-point data can be amplified throughout simulation, producing biologically implausible trajectories.

7. **Rare cell type generalization**: Models trained on specific differentiation pathways may fail to predict emergence of rare or unseen cell lineages.

8. **Validation standards**: Rigorous benchmarking of generated trajectories remains challenging; experimental lineage tracing is the gold standard but rarely available.

9. **User-friendly tools**: Continued refinement of computational packages for accessibility by the broader biology community.

---

### Method Comparison Table

| Method | Year | Venue | Mathematical Framework | Data Assumptions | Training Method | Key Idea | Application Example |
|--------|------|-------|----------------------|-----------------|----------------|----------|-------------------|
| WaddingtonOT | 2019 | *Cell* | Static OT | Temporal snapshot | Directly solve static OT | Baseline cell matching across time points | Reprogramming trajectories |
| TrajectoryNet | 2020 | ICML | Dynamical OT | Temporal snapshot | Neural ODE | Continuous nonlinear trajectories via CNF | Embryoid body differentiation |
| PRESCIENT | 2021 | *Nat Commun* | SDE/Optimality | Temporal snapshot + stochastic | Optimality conditions | Potential energy minimization at each time point | Cell trajectory prediction with interventions |
| Pseudo Dynamics | 2019 | *Nat Biotechnol* | Fokker-Planck Eq | Temporal snapshot | MLE | FPE with non-equilibrium terms | Population dynamics inference |
| GraphFP | 2022 | *PLoS Comput Biol* | Master Equation | Temporal snapshot | Optimality conditions | Minimum free energy dynamics on graph | Cell developmental landscape |
| MIOFlow | 2022 | NeurIPS | Dynamical OT | Low-dim manifold | Neural ODE | Manifold interpolation with geodesics | Trajectory on data manifold |
| Vanilla Flow Matching | 2023 | ICLR | Flow Matching | Temporal snapshot | Flow Matching | Simulation-free generative modeling | Distribution generation |
| OT-CFM | 2024 | TMLR | Dynamical OT | Temporal snapshot | Flow Matching | Flow matching to solve dynamical OT | Conditional trajectory generation |
| SB between Gaussian | 2023 | AISTATS | Schrodinger Bridge | Stochastic, Gaussian | Closed form | Analytical SB for Gaussian mixtures | Stochastic trajectory inference |
| TIGON | 2024 | *Nat Mach Intell* | Unbalanced Dynamical OT | Unbalanced | Neural ODE | Growth + velocity for unbalanced populations | EMT proliferation dynamics |
| SF2M | 2024 | AISTATS | Schrodinger Bridge | Stochastic | Flow Matching | Simulation-free SB via score+flow matching | mESC differentiation |
| MOSCOT | 2025 | *Nature* | Static OT + GWOT | Temporal/spatial | Directly solve static OT | Large-scale fused OT for spatial data | Mouse embryogenesis organogenesis |
| Lagrangian SB | 2023 | ICLR | Schrodinger Bridge | Stochastic | Neural SDE | SB in arbitrary potential fields | Diffusion in potential landscape |
| Likelihood Training SB | 2022 | ICLR | Schrodinger Bridge | Stochastic | MLE | FBSDE-based likelihood training | SB problem solution |
| Unbalanced Diffusion SB | 2023 | ICML Workshop | Unbalanced SB | Stochastic + unbalanced | IPF + Temporal Difference | SB with growth/death | Unbalanced stochastic dynamics |
| Action Matching | 2023 | ICML | Dyn OT/SB/Unbalanced | Stochastic/unbalanced | Simulation-free | Learn dynamics via single scalar field | Flexible dynamics learning |
| HJ-Sampler | 2024 | Preprint | Schrodinger Bridge | Stochastic | Neural SDE | HJB equation + Cole-Hopf transform | Bayesian posterior sampling |
| scNODE | 2024 | *Bioinform* | Neural ODE | Temporal snapshot | Neural ODE | Latent space dynamics via Neural ODE | Temporal scRNA-seq prediction |
| Metric FM | 2024 | NeurIPS | Dynamical OT | Low-dim manifold | Flow Matching | Geodesic interpolation on manifold | Manifold-respecting trajectories |
| MetaFM | 2025 | ICLR | Dynamical OT | Interaction | Flow Matching | Cell-cell interaction learning via FM | Intercellular dynamics |
| GENOT | 2024 | NeurIPS | GWOT | Multi-modality | Flow Matching | Entropic OT/GWOT velocity fitting | Cross-modal trajectory inference |
| DeepRUOT | 2025 | ICLR | RUOT | Stochastic + unbalanced | Neural ODE | Unbalanced FPE with diffusion | EMT continuous path tracing |
| CFGen | 2025 | ICLR | Flow Matching | Conditional (labels) | Flow Matching | Conditional generation of cell states | Multi-attribute cell generation |
| CellFlow | 2025 | bioRxiv | Flow Matching | Conditional (labels) | Flow Matching | Perturbation prediction via FM | Drug response prediction |
| FBSDE Model | 2024 | *PLoS Comput Biol* | Schrodinger Bridge | Stochastic | Neural SDE | FBSDE stabilized training | Single-cell trajectory modeling |
| PISDE | 2024 | *Bioinform* | Schrodinger Bridge | Stochastic | Neural SDE | HJB loss for accelerated SDE training | Physics-informed neural SDE |
| ARTEMIS | 2025 | *Bioinform* | Unbalanced SB | Stochastic + unbalanced | MLE | SB in VAE latent space | Perturbation dynamics |
| CT-OT Flow | 2025 | Preprint | Dynamical OT | Temporal snapshot | Flow Matching | High-resolution time label estimation | Continuous-time dynamics |
| MvOU-OTFM | 2025 | NeurIPS | Schrodinger Bridge | Stochastic | Flow Matching | Closed-form mvOU bridge solution | OU-process reference SB |
| Multistage OT | 2025 | Preprint | Static OT | Temporal snapshot | Directly solve static OT | Multi-stage process with terminal states | Cell development staging |
| scEGOT | 2024 | *BMC Bioinform* | Static OT (GMM) | Temporal snapshot | Closed form | Analytical OT between Gaussian mixtures | GMM-based trajectory |
| DeST-OT | 2025 | *Cell Systems* | Semi-relaxed unbal OT + GWOT | Spatial temporal | Directly solve static OT | Spatiotemporal slice alignment | ST slice alignment |
| 3MSBM | 2025 | NeurIPS | Momentum SB | Stochastic + momentum | Flow Matching | Second-order dynamics in SB | Momentum-aware trajectories |
| Euclidean VAE | 2025 | ICML | Dyn OT (Fisher metric) | Count data | VAE training | Geodesic interpolation in VAE latent space | Count data trajectory |
| CytoBridge | 2025 | NeurIPS | UMFSB | Stochastic + unbalanced + interaction | Neural ODE | Unified framework (velocity, growth, score, interaction) | Mouse hematopoiesis |
| CurlyFM | 2025 | ICLR Workshop | Dynamical OT | Temporal snapshot | Flow Matching | Non-gradient (curvilinear) velocity fields | Non-conservative dynamics |
| Branched SB | 2025 | Preprint | Schrodinger Bridge | Stochastic + branching | Neural ODE | Single source to multiple terminal distributions | Cell fate branching |
| Score-Based NF | 2025 | Preprint | Schrodinger Bridge | Stochastic | Neural ODE | FM as mean-field control for PF-ODE | Score-matching-based dynamics |
| SCOT+ | 2025 | bioRxiv | Unbalanced GWOT | Multi-modality spatial | Directly solve GWOT | Cross-dataset alignment via GWOT | Multi-modal spatial alignment |
| Smooth SB | 2025 | ICML | Schrodinger Bridge | Stochastic | Belief propagation | Smooth Gaussian process reference | Smoother trajectory inference |
| scIMF | 2025 | Preprint | SB + Interaction | Stochastic + interaction | Neural SDE | Attention-based cell-cell interaction | Collective multi-cellular dynamics |
| HMOT | 2025 | RECOMB | Hidden Markov OT | Temporal snapshot | Directly solve static OT | Latent state + OT jointly inferred | Partially observed data |
| STORIES | 2025 | *Nat Methods* | GWOT | Spatial temporal | Directly solve GWOT | FGWOT for spatial gene dynamics | Spatial cell fate landscapes |
| OTVelo | 2025 | *PLoS Comput Biol* | Static OT | Temporal snapshot | Directly solve static OT | RNA velocity estimation via OT | OT-informed velocity |
| MMFM | 2025 | ICLR | Dynamical OT | Conditional (labels) | Flow Matching | Conditional multi-time-point FM | Conditional trajectory generation |
| VGFM | 2025 | NeurIPS | Semi-relaxed unbal OT | Unbalanced | Flow Matching | Joint velocity + growth FM | Unbalanced dynamics via FM |
| Var-RUOT | 2025 | NeurIPS | RUOT | Stochastic + unbalanced | Neural ODE (HJB) | Single scalar field via HJB optimality | Mouse hematopoiesis |
| Topological SB | 2025 | ICLR | Schrodinger Bridge | Topological structure | MLE | Graph-based diffusion as reference | Graph-structured data |
| MMSFM | 2025 | ICML | Schrodinger Bridge | Stochastic | Flow Matching | Multi-marginal Brownian bridge connection | Multi-time-point SB |
| PASTE/PASTE2 | 2022/2023 | *Nat Methods*/*Genome Res* | GWOT | Spatial | Directly solve GWOT | Adjacent tissue slice alignment | ST slice registration |
| CODA | 2022 | *Nat Methods* | Image registration | Spatial + image | -- | 3D tissue reconstruction from sections | Histological reconstruction |
| STALocator | 2025 | *Cell Systems* | Static OT | Spatial | Directly solve static OT | Supervised AE for cell localization | scRNA-seq to ST mapping |
| iSORT | 2025 | *PLoS Comput Biol* | Transfer learning | Spatial | Weighted reconstruction | Gene expression to spatial position | Spatial position inference |
| Wasserstein FM | 2025 | ICML | Dynamical OT | Temporal snapshot | Flow Matching | FM in Wasserstein space | High-dim distribution generation |
| WLR | 2025 | AISTATS | B-spline on Wasserstein manifold | Temporal snapshot | Consecutive averaging | Smoother trajectories via B-splines | Wasserstein geodesic smoothing |
| PFI | 2025 | ICLR | Schrodinger Bridge | Temporal snapshot | Neural ODE | Probability flow ODE of SDE | Probability flow inference |
| Cell-MNN | 2025 | Preprint | OT | Temporal snapshot | Neural ODE | Linear ODE (single matrix) per trajectory | Simplified dynamics learning |
| Wasserstein Lagrangian Flow | 2024 | ICML | Dyn OT/SB/Unbalanced | Stochastic/unbalanced | Simulation-free | Covariant vectors on probability manifold | Simulation-free OT variants |
| Unbalanced Monge Map | 2024 | ICLR | Unbalanced static OT | Spatial + unbalanced | OT-MG + Flow Matching | Neural unbalanced OT | Unpaired domain translation |
| stVCR | 2024 | bioRxiv | RBTI-OT | Spatial + unbalanced | Neural ODE | Joint rigid alignment + unbalanced dynamics | Axolotl brain regeneration, Drosophila 3D development |

---

### Cross-References

- For detailed mathematical formulations, see doc_method.md
- For practical takeaways and method selection guide, see reading_notes.md
- For figure analysis, see figure_analysis.md

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
