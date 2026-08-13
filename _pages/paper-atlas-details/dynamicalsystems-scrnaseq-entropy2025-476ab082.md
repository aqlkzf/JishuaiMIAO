---
layout: default
permalink: /paper-atlas/dynamicalsystems-scrnaseq-entropy2025-476ab082/
title: "DynamicalSystems_scRNAseq_Entropy2025"
nav: false
wide: true
description: "这篇 2025 年发表于 Entropy 的文章是一篇综述。它不提出一个名为“DynamicalSystemsscRNAseq”的可运行模型，也没有配套代码。它的贡献是建立一张方法地图：先按数据是否有真实时间、是否有空间坐标分类，再按动力学是离散还是连续、是否随机、是否允许细胞增殖和死亡分类。 因此，下文的公式是统一语言和方法族的代表形式。"
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
      <span>Entropy · 2025</span>
    </div>
    <h1>DynamicalSystems_scRNAseq_Entropy2025</h1>
    <p>Integrating Dynamical Systems Modeling with Spatiotemporal scRNA-Seq Data Analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.3390/e27050453" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DynamicalSystems_scRNAseq_Entropy2025">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 动力系统如何阅读单细胞时空数据：综述框架中文解读

### 1. 先明确：这不是一个新算法

这篇 2025 年发表于 *Entropy* 的文章是一篇综述。它不提出一个名为“DynamicalSystems_scRNAseq”的可运行模型，也没有配套代码。它的贡献是建立一张方法地图：先按数据是否有真实时间、是否有空间坐标分类，再按动力学是离散还是连续、是否随机、是否允许细胞增殖和死亡分类。

因此，下文的公式是统一语言和方法族的代表形式。它们分别归属于 Markov chain、RNA velocity、optimal transport、Schrödinger bridge 等已有方法，不能当成作者训练了一个统一模型后的实验结果。

### 2. 数据先决定你能问什么

综述区分四种观测场景：

| 数据 | 实际观测 | 能直接得到的内容 | 最大缺口 |
|---|---|---|---|
| 单时点 scRNA-seq | 一个细胞×基因矩阵 | 状态几何、细胞类型 | 没有真实时间，也不追踪同一细胞 |
| 多时点 scRNA-seq | 多个时间点的独立细胞群 | 分布随时间的变化 | 各时点细胞没有一一对应 |
| 单时点空间转录组 | 表达加二维/三维坐标 | 组织结构与局部邻域 | 缺少时间方向 |
| 多时点空间转录组 | 多个时间点的表达与空间坐标 | 时空分布演化 | 同时需要跨时点匹配和空间对齐 |

“多时点”仍不等于单细胞轨迹。测序通常是破坏性的：$t_0$ 的细胞不会在 $t_1$ 再被测一次。模型恢复的是跨群体的可能转移或概率路径。

### 3. 第一条主轴：离散状态还是连续动力学

#### 离散模型

离散模型把细胞或聚类看成节点，以转移矩阵 $P$ 描述一步变化：

$$
P_{ij}=\Pr(X_{t+1}=j\mid X_t=i),\qquad \sum_jP_{ij}=1.
$$

DPT、PAGA、Palantir、CellRank 等方法都能放进这一语言。优势是容易计算命运概率、吸收态和 metastable states；缺点是边、核函数和离散步长的选择会影响结果，而且转移概率不自动等于真实物理时间。

#### 连续模型

连续模型用 ODE 或 SDE 描述单细胞状态：

$$
\mathrm dX_t=b(X_t,t)\,\mathrm dt+\sigma(X_t,t)\,\mathrm dW_t.
$$

$b$ 是漂移场，给出平均运动方向；$\sigma$ 描述随机扩散。对应的群体密度 $p(x,t)$ 满足带源汇项的 Fokker–Planck 方程：

$$
\partial_t p=-\nabla\cdot(pb)+\frac12\nabla^2:(ap)+g(x,t)p,
\qquad a=\sigma\sigma^\top.
$$

$g>0$ 可表示局部增殖，$g<0$ 可表示死亡。这个“单细胞轨迹—群体密度”对应关系是综述最重要的统一桥梁。

### 4. 单时点 scRNA-seq：从排序到方向场

#### Pseudotime

Monocle、Slingshot、DPT 等方法依据流形上的距离或图路径为细胞排序。它们回答“谁更早、谁更晚”，但 pseudotime 的单位通常不是小时，分支方向也常依赖 root cell。

StemID、SLICE、SCENT、CellMCE 用 entropy 描述分化潜能。直觉是未分化状态可访问的表达程序更多、entropy 较高，分化后状态更受限。这个直觉不是普适物理定律；entropy 的定义、基因网络和预处理不同，排序也会不同。

#### Markov random walk

随机游走把局部相似度、pseudotime 或 velocity 变成转移核。Palantir 计算终末命运概率，MuTrans 和 CellRank 进一步识别 metastability、macrostates 和 attractors。这里的吸收态是模型在所选核上的长期行为，并不自动证明细胞存在不可逆生物终点。

#### RNA velocity

经典基因级动力学为：

$$
\dot u=\alpha-\beta u,
\qquad
\dot s=\beta u-\gamma s,
$$

其中 $u$、$s$ 是 unspliced 与 spliced RNA。Velocyto 用稳态近似估计方向，scVelo 用诱导/抑制阶段和 latent time 放宽假设；VeloVI、VeloVAE、LatentVelo 等把动力学放入生成模型或低维潜空间。它们提供局部方向信息，但仍受剪接动力学、基因特异参数、批次效应和潜时间可辨识性限制。

#### Vector-field reconstruction

Dynamo、GraphDynamo、GraphVelo 等把离散 velocity 向量平滑成连续向量场，再分析 fixed points、divergence、curl 或 potential-like structures。几何结构是对拟合场的性质，不应跳过拟合误差而直接解释为调控机制。

### 5. 多时点 scRNA-seq：为什么 optimal transport 成为主线

在两个时间点观察到分布 $\nu_0$ 和 $\nu_1$，static OT 寻找运输计划：

$$
\min_{\pi\in\Pi(\nu_0,\nu_1)}\langle\pi,c\rangle.
$$

$\pi_{ij}$ 表示起点细胞 $i$ 向终点细胞 $j$ 分配的质量。它不是已观测谱系，而是在给定 cost 和边际约束下的最优耦合。

加入 entropy 正则可用 Sinkhorn 算法高效计算：

$$
\min_\pi\langle\pi,c\rangle-\varepsilon H(\pi).
$$

$\varepsilon$ 越大，匹配越平滑也越不确定。若细胞数因增殖/死亡变化，unbalanced OT 用 KL penalty 放松边际守恒。WaddingtonOT、Moscot 等处在这条离散 OT 路线上。

### 6. 连续时间的四象限：$g$ 与 $\sigma$

综述用是否允许源汇 $g$ 和随机性 $\sigma$ 组织连续方法：

| 情形 | 动力学 | 代表框架 | 主要假设 |
|---|---|---|---|
| $g=0,\sigma=0$ | 平衡、确定性 | dynamical OT、TrajectoryNet、MIOFlow | 质量守恒、轨迹无扩散 |
| $g=0,\sigma\neq0$ | 平衡、随机 | Schrödinger bridge、PRESCIENT | 质量守恒但有随机噪声 |
| $g\neq0,\sigma=0$ | 非平衡、确定性 | WFR、TIGON、unbalanced action matching | 允许生长/死亡，无扩散 |
| $g\neq0,\sigma\neq0$ | 非平衡、随机 | RUOT、UDSB、DeepRUOT | 同时估计漂移、扩散和源汇 |

论文正文列举四情形时，第 3 与第 4 项把条件重复写成 $(g\neq0,\sigma\neq0)$。图 3、WFR 小节和 RUOT 小节共同表明，第 3 项应为 $(g\neq0,\sigma=0)$。这是依据论文内部结构作出的勘误推断。

模型越靠近右下角越灵活，但并非自动越可信：同时从稀疏时间点识别 $b$、$\sigma$ 和 $g$ 容易出现多解，需要能量正则、增长先验或额外数据约束。

### 7. Schrödinger bridge 与 flow matching 在做什么

Schrödinger bridge 在给定起始和终止分布的条件下，寻找相对参考随机过程 KL divergence 最小的路径分布。它可理解为“在满足端点的随机演化中，找最不偏离参考过程的一种”。

Neural SDE、score matching 和 conditional flow matching 提供不同求解方式。Flow matching 常直接回归条件向量场，减少逐步模拟训练的成本；但 cost、reference process、插值路径和网络结构仍会决定学到的动力学。

### 8. 空间数据多出的难题

单时点空间数据可以把表达相似、RNA velocity 和物理邻近组合成 transition kernel。stLearn 调整 pseudotime distance，STT 和 SpaTrack 构造空间感知的离散转移，TopoVelo 与 iSORT 尝试得到物理空间中的连续方向。

多时点空间数据还要对齐组织。Fused/Gromov–Wasserstein 类方法比较切片内的成对几何关系，而不只比较单细胞特征；Spateo、DeST-OT、Moscot 属于综述列出的离散时空方法。stVCR 在该综述的分类表中是连续时空代表，并把 rigid transformation 与 transport 同时优化。

“旋转和平移不变”只处理刚体差异。发育组织可能发生局部非线性形变、增殖和组织重塑，因而 non-rigid alignment 仍是开放问题。

### 9. 图 1–4 的最短阅读路径

- **图 1**：先看数据，再看离散 Markov chain 与连续 SDE/PDE 的对应关系。
- **图 2**：单时点 scRNA-seq 的方法树；原 PDF 中以排版表格呈现，转换结果没有独立图片文件。
- **图 3**：多时点 scRNA-seq。左侧是 static/entropic/unbalanced OT，右侧是 $g$–$\sigma$ 四象限。
- **图 4**：空间转录组。左侧单时点空间，右侧多时点时空；方法数量明显少于 scRNA-seq 部分，反映该方向在本文覆盖范围内仍较新。

这些图是 taxonomy，不是 benchmark。图中出现某方法不代表作者在共同数据上比较过精度，也不能据图断言某一类方法“最佳”。

### 10. 怎样按实际问题选方法

1. **只有单时点表达，想看相对顺序**：pseudotime；若有 unspliced/spliced，再考虑 RNA velocity。
2. **想要终末命运概率**：以合适的 pseudotime、velocity 或 OT kernel 构建 CellRank 类 Markov 模型。
3. **有多个真实时间点，只需跨时点耦合**：static/entropic OT；存在明显增殖死亡时用 unbalanced OT。
4. **需要连续插值或采样轨迹**：dynamical OT、flow matching 或 Schrödinger bridge，并检查质量守恒和随机性假设。
5. **同时有空间与时间**：先判断是否只需对齐/匹配，还是需要连续时空场；确认组织形变能否用 rigid transform 描述。

所有选择都应报告 root、cost、kernel、growth prior、regularization、时间间隔和对齐方式，并用已知 marker、谱系追踪或 held-out time points 验证。

### 11. 综述自身的边界

作者明确说明未深入覆盖 lineage tracing、gene regulatory networks、dynamic network biomarkers 和 critical transitions。文章也不是系统综述或正式 benchmark：没有预注册检索式、纳入排除流程、统一实验数据和定量排名。其价值在于数学组织框架，而不是穷尽 2025 年所有工具或证明被引方法的性能主张。

最稳妥的使用方式，是用这篇综述决定“我的数据和假设落在哪个动力学象限”，再回到目标方法的原始论文、实现和 benchmark 验证具体 API、参数和适用性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary: Integrating Dynamical Systems Modeling with Spatiotemporal scRNA-Seq Data Analysis

**Zhang, Sun, Peng, Li, Zhou** | *Entropy* 2025, 27, 453 (44 pages) | DOI: 10.3390/e27050453

---

### Review Scope & Context

This review surveys **computational methods that apply dynamical systems theory to single-cell and spatial transcriptomics data**, covering approaches from pseudotime inference through to generative models based on optimal transport and Schrodinger bridges. The review is authored by researchers at Peking University's School of Mathematical Sciences and Center for Machine Learning Research.

**Why timely**: The field sits at the convergence of three rapidly advancing areas: (1) temporally resolved scRNA-seq technologies that capture gene expression across multiple time points, (2) spatial transcriptomics (ST) methods that preserve tissue architecture, and (3) mathematical frameworks from dynamical systems, optimal transport, and generative modeling. Prior reviews have covered individual topics (pseudotime, RNA velocity, OT for single-cell), but this review uniquely provides a **unified dynamical systems perspective** across all four data modalities: snapshot scRNA-seq, temporal scRNA-seq, snapshot ST, and temporal ST.

**Time span**: Methods reviewed range from ~2016 (Monocle, DPT) to 2025 (stVCR, DeepRUOT, Moscot, CellRank2), with ~208 references.

---

### Field Landscape

The review organizes the field around **two orthogonal axes**:

1. **Data type** (4 categories): snapshot scRNA-seq, temporally resolved scRNA-seq, snapshot spatial transcriptomics, temporally resolved spatial transcriptomics
2. **Modeling paradigm** (2 categories): discrete (Markov chains, random walks) vs. continuous (ODEs, SDEs, PDEs, OT)

**Key biological domains**: developmental biology, cell fate decisions, cellular differentiation, cell migration, disease progression, Waddington's landscape reconstruction.

**Total methods discussed**: ~40+ distinct computational methods, with detailed mathematical treatment of ~25.

---

### Method Taxonomy

The review's classification follows a hierarchical scheme organized by data type and modeling paradigm:

#### I. Snapshot scRNA-seq (Section 3.1)

| Subcategory | Methods |
|---|---|
| **Pseudotime -- Geodesic** | Monocle, Monocle 2/3, Slingshot |
| **Pseudotime -- Entropy** | StemID, SLICE, SCENT, CellMCE |
| **Discrete Dynamics -- Markov Chain** | DPT, PAGA, Palantir, PBA, MuTrans, CellRank |
| **Continuous Dynamics -- RNA Velocity (Linear Regression)** | Velocyto |
| **Continuous Dynamics -- RNA Velocity (EM)** | scVelo |
| **Continuous Dynamics -- RNA Velocity (Function Class)** | UniTVelo, TFVelo |
| **Continuous Dynamics -- Deep Learning (VAE)** | VeloAE, LatentVelo, VeloVI, VeloVAE |
| **Continuous Dynamics -- Deep Learning (Continuity)** | DeepVelo, CellDancer |
| **Continuous Dynamics -- Vector Field Reconstruction** | Dynamo, GraphDynamo, GraphVelo |

#### II. Temporally Resolved scRNA-seq (Section 3.2)

| Subcategory | Methods |
|---|---|
| **Discrete: Static OT** | WaddingtonOT, Moscot |
| **Discrete: Entropic OT** | WaddingtonOT, Moscot |
| **Discrete: Unbalanced OT** | WaddingtonOT, Moscot |
| **Continuous: Dynamical OT** ($g=0,\sigma=0$) | TrajectoryNet, MIOFlow, Action Matching |
| **Continuous: Schrodinger Bridge** ($g=0,\sigma\neq 0$) | SB Flow Matching, Neural LSB/PI-SDE, gWOT, PRESCIENT |
| **Continuous: WFR Metric** ($g\neq 0,\sigma=0$) | TIGON, Unbalanced AM, stVCR |
| **Continuous: RUOT / UDSB** ($g\neq 0,\sigma\neq 0$) | DeepRUOT, UDSB, gWOT |

#### III. Snapshot Spatial Transcriptomics (Section 4.1)

| Subcategory | Methods |
|---|---|
| **Pseudotime** | stLearn (PSTS algorithm) |
| **Discrete Dynamics** | STT, SpaTrack |
| **Continuous Dynamics** | iSORT, TopoVelo |

#### IV. Temporally Resolved Spatial Transcriptomics (Section 4.2)

| Subcategory | Methods |
|---|---|
| **Discrete Spatiotemporal** | Moscot, DeST-OT, Spateo |
| **Continuous Spatiotemporal** | stVCR |

#### V. Extensions (Section 5)

| Topic | Methods/Concepts |
|---|---|
| **Bridging Discrete-Continuous** | CellRank kernels, continuum limits, GraphDynamo, GraphVelo |
| **Cell-Cell Interaction** | GraphFP |
| **Waddington Landscape** | Boltzmann-based landscape, time-evolving landscapes |

---

### Key Findings

1. **No single method dominates**: Snapshot data requires fundamentally different approaches (pseudotime, RNA velocity) than temporal data (OT-based methods). Spatial data adds another layer of complexity requiring spatial-aware kernels and rigid-body transformations.

2. **RNA velocity is powerful but limited**: The standard splicing kinetics model ($\dot{u} = \alpha - \beta u$, $\dot{s} = \beta u - \gamma s$) requires strong assumptions (steady-state or two-phase dynamics). Deep learning methods (DeepVelo, CellDancer) relax these but sacrifice interpretability.

3. **Optimal transport is the dominant framework for temporal data**: Both static (WaddingtonOT) and dynamic (TrajectoryNet, TIGON, DeepRUOT) OT approaches have become central, with entropic regularization (Sinkhorn algorithm) enabling scalable computation.

4. **Stochasticity and unbalancedness matter**: Cell proliferation/death violate mass conservation, requiring unbalanced OT formulations. Intrinsic noise in gene expression motivates SDE-based models and Schrodinger bridges over deterministic ODE approaches.

5. **The four-case taxonomy is clarifying**: The review's $(g, \sigma)$ classification of continuous methods -- (1) deterministic balanced ($g=0,\sigma=0$), (2) stochastic balanced ($g=0,\sigma\neq 0$), (3) deterministic unbalanced ($g\neq 0,\sigma=0$), (4) stochastic unbalanced ($g\neq 0,\sigma\neq 0$) -- provides a principled way to select methods.

6. **Spatial transcriptomics dynamics is nascent**: Very few methods (stVCR, Spateo) address continuous spatiotemporal dynamics. Fused Gromov-Wasserstein OT handles spatial alignment, but lacks a dynamic formulation. stVCR's rigid-body-transformation-invariant OT is a notable advance.

7. **Discrete and continuous models can be bridged**: CellRank shows how RNA velocity or OT can inform transition kernels in Markov chains. Theoretical convergence results (continuum limits of diffusion maps, MuTrans) validate this connection.

---

### Open Problems & Future Directions

1. **Bridging discrete and continuous models**: Building theoretical connections between random walk models and differential equation models remains an active area. The continuum limit of RNA-velocity-induced kernels needs further investigation.

2. **Cell-cell interaction dynamics**: Current methods (GraphFP) model interactions at the cell-type level; extending to single-cell resolution is needed.

3. **Waddington landscape construction**: Despite conceptual elegance, constructing quantitative potential landscapes from data remains challenging. Time-evolving landscapes from temporal data are a promising direction.

4. **Multi-omics integration**: Incorporating epigenomic, proteomic, and metabolomic data into dynamical models would improve resolution.

5. **Non-rigid spatial transformations**: Current methods (PASTE, Moscot) use rigid-body transformations for aligning ST slices; non-linear and non-rigid transformations are needed for more complex tissue deformations.

6. **SDE models for spatial transcriptomics**: Applying stochastic dynamics to spatial data and constructing spatiotemporal landscapes is largely unexplored.

7. **Lineage tracing integration**: Incorporating lineage tracing data (barcoding, CRISPR-based) into trajectory inference.

8. **Gene regulatory networks (GRNs)**: Integrating GRN structure into spatiotemporal trajectory inference.

9. **Dynamic network biomarkers (DNBs)**: Using critical transition theory to identify tipping points in cell fate decisions.

---

### Method Comparison Table

| Method | Year | Journal/Venue | Category | Input Data | Key Idea | Strengths | Limitations |
|---|---|---|---|---|---|---|---|
| **Monocle** | 2017 | Nat Methods | Pseudotime (geodesic) | Snapshot scRNA-seq | MST + ICA for cell ordering | Simple, handles branching (Monocle 2/3) | Requires root cell selection; no dynamics model |
| **Slingshot** | 2018 | BMC Genomics | Pseudotime (geodesic) | Snapshot scRNA-seq | Principal curves + MST for multiple lineages | Handles branching; consistent pseudotime across lineages | Requires pre-clustering; sensitive to cluster quality |
| **StemID/SLICE/SCENT** | 2016-2017 | Cell Stem Cell / NAR / Nat Commun | Pseudotime (entropy) | Snapshot scRNA-seq | Entropy of gene expression as stemness measure | No root cell needed; biologically motivated | May not capture all branching structures |
| **CellMCE** | 2020 | Brief Bioinform | Pseudotime (entropy) | Snapshot scRNA-seq + PPI network | Markov chain entropy on gene interaction graph | Incorporates gene-gene interactions; principled | Depends on quality of PPI network |
| **DPT** | 2016 | Nat Methods | Discrete dynamics | Snapshot scRNA-seq | Diffusion map random walk + distance metric | Captures both short and long-range transitions | Assumes connected graph; requires root cell |
| **PAGA** | 2019 | Genome Biol | Discrete dynamics | Snapshot scRNA-seq | Graph abstraction for disconnected lineages | Handles disconnected/sparse data | Coarse-grained; may miss subtle transitions |
| **Palantir** | 2019 | Nat Biotechnol | Discrete dynamics | Snapshot scRNA-seq | Directional random walk + cell fate probabilities | Computes fate probabilities and differentiation potential | Depends on pseudotime quality |
| **PBA** | 2018 | PNAS | Discrete dynamics | Snapshot scRNA-seq | Potential function from graph Laplacian + proliferation | Accounts for cell proliferation; principled | Requires predefined proliferation gene lists |
| **MuTrans** | 2021 | Nat Commun | Discrete dynamics | Snapshot scRNA-seq | Multi-scale coarse-graining of random walk | Identifies metastable attractors and transition cells; energy landscape | EM-like optimization can be sensitive to initialization |
| **CellRank / CellRank2** | 2022/2024 | Nat Methods | Discrete dynamics | Snapshot or temporal scRNA-seq | GPCCA + flexible kernels (velocity, pseudotime, OT) | Flexible kernel combination; terminal state detection; supports multi-modal | Requires velocity or OT input; many hyperparameters |
| **Velocyto** | 2018 | Nature | RNA velocity (linear regression) | Snapshot scRNA-seq (spliced/unspliced) | Steady-state assumption for $\tilde{\gamma}$ estimation | Simple; foundational concept | Steady-state assumption violated for most transient cells |
| **scVelo** | 2020 | Nat Biotechnol | RNA velocity (EM) | Snapshot scRNA-seq (spliced/unspliced) | Two-phase kinetics + EM for latent time | Models full dynamics; uses all cells | Complex model fitting; gene-independent time assumption |
| **UniTVelo** | 2022 | Nat Commun | RNA velocity (function class) | Snapshot scRNA-seq (spliced/unspliced) | Radial basis function for spliced RNA dynamics | Flexible functional form; unified time | Many parameters; may overfit |
| **TFVelo** | 2024 | Nat Commun | RNA velocity (function class) | Snapshot scRNA-seq + TF info | TF-coupled sinusoidal dynamics | Incorporates TF regulatory logic | Requires TF annotation; sinusoidal assumption |
| **VeloAE** | 2021 | PNAS | RNA velocity (VAE) | Snapshot scRNA-seq (spliced/unspliced) | Latent space velocity with steady-state constraint | Reduced dimensionality; denoising | Steady-state assumption in latent space |
| **LatentVelo** | 2023 | Cell Rep Methods | RNA velocity (VAE) | Snapshot scRNA-seq (spliced/unspliced) | Neural ODE dynamics in latent space + chromatin | Models chromatin accessibility dynamics | Complex architecture; requires careful tuning |
| **VeloVI** | 2024 | Nat Methods | RNA velocity (VAE) | Snapshot scRNA-seq (spliced/unspliced) | Dirichlet prior for gene states + VAE | Uncertainty quantification; handles multiple kinetic states | Computationally expensive |
| **VeloVAE** | 2022 | ICML | RNA velocity (VAE) | Snapshot scRNA-seq (spliced/unspliced) | Latent z maps to cell-specific kinetic parameters | Cell-specific parameters; flexible | Overfitting risk |
| **DeepVelo** | 2024 | Genome Biol | RNA velocity (continuity) | Snapshot scRNA-seq (spliced/unspliced) | Neural network kinetics + forward/backward consistency | Multi-lineage; cell-specific kinetics | Requires neighbor graph quality |
| **CellDancer** | 2024 | Nat Biotechnol | RNA velocity (continuity) | Snapshot scRNA-seq (spliced/unspliced) | Neural network kinetics + neighbor alignment | Cell-dependent rates; relay model | Depends on neighbor structure |
| **Dynamo** | 2022 | Cell | Vector field reconstruction | Snapshot scRNA-seq + velocity | RKHS-based vector field + geometric analysis | Jacobian, divergence, curvature analysis; transition paths | Requires velocity estimates; scalability to high dimensions |
| **GraphDynamo** | 2023 | bioRxiv | Vector field reconstruction | Snapshot scRNA-seq + velocity | Graph-based manifold-projected velocity correction | Geometry-aware velocity correction | Preprint; depends on graph quality |
| **GraphVelo** | 2024 | bioRxiv | Vector field reconstruction | Snapshot scRNA-seq + velocity | Multi-modal velocity with manifold projection | Multi-modal integration possible | Preprint; similar limitations |
| **WaddingtonOT** | 2019 | Cell | Static OT | Temporal scRNA-seq | Unbalanced OT between time-point distributions | Accounts for growth/death; ancestor/descendant analysis | Pairwise coupling; no continuous dynamics |
| **Moscot** | 2025 | Nature | Static/entropic/unbalanced OT + FGW | Temporal scRNA-seq or temporal ST | Fused GW-OT with entropic regularization | Unified framework; spatial + temporal; scalable | Many hyperparameters; discrete couplings |
| **TrajectoryNet** | 2020 | ICML | Dynamical OT | Temporal scRNA-seq | Neural ODE for Benamou-Brenier formulation | Continuous trajectories; CNF solver | Deterministic; no growth/death |
| **MIOFlow** | 2022 | NeurIPS | Dynamical OT | Temporal scRNA-seq | Manifold-interpolating OT flows | Respects data manifold | Requires manifold estimation |
| **TIGON** | 2024 | Nat Mach Intell | Unbalanced dynamical OT (WFR) | Temporal scRNA-seq | Neural ODE with growth term; WFR metric | Models proliferation/death + continuous dynamics | Deterministic; no stochastic effects |
| **PRESCIENT** | 2021 | Nat Commun | Schrodinger bridge | Temporal scRNA-seq | SDE-based trajectory prediction | Predicts intervention effects; stochastic | No unbalancedness |
| **SB Flow Matching** | 2024 | AISTATS | Schrodinger bridge + CFM | Temporal scRNA-seq | Simulation-free SB via CFM + score matching | Scalable; simulation-free; stochastic | Balanced dynamics only |
| **DeepRUOT** | 2025 | ICLR | RUOT | Temporal scRNA-seq | Fisher regularization + probability flow ODE | Stochastic + unbalanced; no prior knowledge needed | Two-stage training; complex loss |
| **stLearn** | 2023 | Nat Commun | Pseudotime (spatial) | Snapshot ST | PSTS: weighted pseudotime + spatial distance | Integrates spatial information | MST-based; limited to simple trajectories |
| **STT** | 2024 | Nat Methods | Discrete spatial dynamics | Snapshot ST | Space-aware random walk + attractor decomposition | Integrates velocity, expression, and space | Iterative; requires RNA velocity |
| **SpaTrack** | 2025 | Cell Systems | Discrete spatial dynamics (OT) | Snapshot ST | Entropy-regularized OT with spatial + expression cost | Simple; interpretable trajectories | No time resolution |
| **iSORT** | 2024 | bioRxiv | Continuous spatial dynamics | Snapshot ST | Transfer learning for gene-to-space mapping + spatial velocity | Novel spatial velocity concept | Requires reference spatial data |
| **TopoVelo** | 2024 | RECOMB | Continuous spatial dynamics | Snapshot ST | GNN for spatial RNA velocity | Topology-aware velocity | Conference paper; limited validation |
| **DeST-OT** | 2024 | bioRxiv | Discrete spatiotemporal | Temporal ST | Semi-relaxed FGW-OT with growth inference | Simultaneous growth and mapping inference | Preprint; scaling concerns |
| **Spateo** | 2022 | bioRxiv | Discrete spatiotemporal | Temporal ST | OT + Procrustes alignment + spatial velocity field | Comprehensive geometric analysis (divergence, curvature, torsion) | Depends on OT quality; preprint |
| **stVCR** | 2024 | bioRxiv | Continuous spatiotemporal | Temporal ST | Rigid-body-invariant OT + WFR PDE + neural ODE | Simultaneous migration, differentiation, proliferation; continuous dynamics | Complex optimization; preprint |
| **GraphFP** | 2022 | PLoS Comput Biol | Cell-cell interaction dynamics | Temporal scRNA-seq | Fokker-Planck on cell-type graph + Wasserstein distance | Models cell-cell interactions; energy landscape | Cell-type level (not single-cell); balanced dynamics |

---

### Cross-References

- For detailed mathematical formulations, see doc_method.md
- For practical method selection guidance, see reading_notes.md
- For figure analysis, see figure_analysis.md

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
