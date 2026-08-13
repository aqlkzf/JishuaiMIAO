---
layout: default
permalink: /paper-atlas/topovelo-e5a92b56/
title: "TopoVelo"
nav: false
description: "传统 RNA velocity 把细胞当作相互独立的观测：每个细胞的 unspliced/spliced counts 只由自身潜在时间和动力学参数解释。但发育组织中，接触信号、形态素、ECM 和局部组织结构都与命运变化相关。TopoVelo 把空间转录组构成一张图，用图神经网络让一个细胞的潜在状态和转录率同时受到空间邻居影响。 它输出两种容易混淆的“速度”： RNA velocity：每个细胞、每个基因的 ds/dt，位于表达空间；"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>TopoVelo</h1>
    <p>Topological velocity inference from spatial transcriptomic data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02688-8" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TopoVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/welch-lab/TopoVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for TopoVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TopoVelo 方法解读：让空间邻域参与 RNA velocity 推断

### 核心问题

传统 RNA velocity 把细胞当作相互独立的观测：每个细胞的 unspliced/spliced counts 只由自身潜在时间和动力学参数解释。但发育组织中，接触信号、形态素、ECM 和局部组织结构都与命运变化相关。TopoVelo 把空间转录组构成一张图，用图神经网络让一个细胞的潜在状态和转录率同时受到空间邻居影响。

它输出两种容易混淆的“速度”：

- **RNA velocity**：每个细胞、每个基因的 $ds/dt$，位于表达空间；
- **cell velocity**：用单独 spatial decoder 推断的二维/三维坐标变化方向，位于物理空间。

后者表示模型认为“发育状态变化对应的空间方向”，在迁移型组织中可能接近真实运动，但不是细胞追踪实验直接测得的位移。

### 输入、图与输出

输入 AnnData 需要 unspliced/spliced counts 和空间坐标。预处理进行基因过滤、归一化、矩估计，并以 KNN、epsilon-ball 或 Delaunay 方法建空间图 $\mathcal G=(V,E)$。节点是细胞或 spots，节点特征是拼接的 $[u_i,s_i]$，边表示空间邻接而非谱系关系。

输出包括 latent time $t_i$、latent state $z_i$、转录率 $\rho_{ig}$、gene-level kinetic rates、RNA velocity、空间 cell velocity、重构结果，以及使用 GAT 时的邻域 attention/influence summaries。

### 生成模型：细胞不再条件独立

普通模型常写成

$$
p(\mathcal O\mid\mathcal Z,\mathcal T)=
\prod_i p(o_i\mid z_i,t_i).
$$

TopoVelo 改为让第 $i$ 个观测依赖其空间邻域：

$$
p(\mathcal O\mid\mathcal Z,\mathcal T)=
\prod_i p\!\left(o_i\mid\{z_j,t_j:j\in\operatorname{nbr}(i)\}\right).
$$

实现上，Encoder 先用 GAT/GCN 聚合邻居表达，再输出时间和状态的 variational posterior；Decoder 再从邻域 latent states 预测 cell-by-gene transcription modulation $\rho_{ig}$。这使邻居通过共享图消息影响重构，但不等于模型识别了具体 ligand–receptor 通路。

### 空间耦合的剪接动力学

对细胞 $i$、基因 $g$：

$$
\frac{du_{ig}}{dt}=\rho_{ig}\alpha_g-\beta_g u_{ig},
\qquad
\frac{ds_{ig}}{dt}=\beta_g u_{ig}-\gamma_gs_{ig}.
$$

$\rho_{ig}$ 由 graph decoder 产生，随细胞和邻域变化；$\alpha_g,\beta_g,\gamma_g$ 是基因参数。源码 `rna_velocity_vae()` 也按上述式子计算 $v_u,v_s$。因此 TopoVelo 的 cell-specific flexibility 主要进入 transcription drive，splicing/degradation 默认仍不是任意 cell-specific functions。

在短区间内把 $\rho\alpha$ 视为常量，ODE 有解析解。以 $\Delta t=t-t_0$ 为例：

$$
u(t)=u_0e^{-\beta\Delta t}
+\frac{\rho\alpha}{\beta}(1-e^{-\beta\Delta t}),
$$

$$
s(t)=s_0e^{-\gamma\Delta t}
+\frac{\rho\alpha}{\gamma}(1-e^{-\gamma\Delta t})
+\frac{\rho\alpha-\beta u_0}{\gamma-\beta}
(e^{-\gamma\Delta t}-e^{-\beta\Delta t}).
$$

源码 `pred_su()` 直接实现解析式，并在 $|\beta-\gamma|<10^{-6}$ 时改用极限形式，最后以 ReLU 截断负重构。没有数值积分误差，但仍依赖“区间内速率恒定”和一阶剪接模型。

例如 $u=4,s=6,\rho\alpha=5,\beta=1,\gamma=0.5$ 时：

$$
v_u=5-4=1,\qquad v_s=4-3=1,
$$

两层都预测上升。若空间邻域使 $\rho$ 降至 0.4，则 $\rho\alpha=2$，$v_u=-2$，而 $v_s$ 暂仍为 1；这正是驱动先变、成熟 RNA 滞后的相位信息。

### Encoder、Decoder 与 gene phase

Encoder 用一层图卷积加全连接层，把 $[u,s]$ 映射到 $q(t,z\mid o,\mathcal G)$ 的均值和尺度。时间与 cell state 默认具有对角 Gaussian priors；若有 capture time，可把它作为 informative time prior 的均值，并按相邻实验间隔设置方差。

Decoder 先由 graph network 预测 $\rho$，再结合解析 ODE 重构 $u,s$。模型还用 categorical gene-phase variable 区分 induction 与 repression，并以 Dirichlet prior 约束其混合概率。这个 phase 是对建模区间的简化状态；反复振荡或多次开关的基因不会被一个二元全局 phase 完整表达。

训练最大化 ELBO：重构 likelihood 减去 time/state posterior 对 prior 的 KL，并包含 phase categorical/Dirichlet 项。源码以 minibatch Adam、early stopping 和 gradient clipping 训练，ODE rates 以 steady-state/scVelo-like estimates 初始化。图只用于 node-feature reconstruction，不重构边，因此 minibatch 能降低内存，但 GAT scatter/reduction 在 GPU 上可能仍非完全确定性。

### Attention 与 cell influence 不能直接当因果

GAT 对邻接边计算 attention coefficient，表示在当前重构目标和训练解中，邻居特征被加权的强度。论文把多头、多层 attention 汇总为 cell influence score，并与 contact-dependent ligand–receptor signals 比较。

高 attention 说明该邻居对模型消息传递重要，但它还会受节点度数、表达相似性、图半径、归一化和参数化影响。没有 ligand/receptor identity、干预或方向性实验时，attention 不是“细胞 A 生物学上导致细胞 B 分化”的证明。

### Spatial decoder 与物理空间 cell velocity

主 VAE 收敛后，TopoVelo 再训练 spatial decoder：输入 latent time/state、估计的前态时间 $t_0$ 与前态坐标 $(x_0,y_0)$，输出当前坐标。$t_0,x_0,y_0$ 来自 cell-state 邻域中的较早细胞均值，而不是同一细胞的真实历史位置。

沿 latent time 改变 decoder 输入即可估计坐标导数/差分，形成物理空间 cell velocity。若组织变化主要由迁移驱动，它可与速度尺度比较；若组织由增殖、形变、切片几何或细胞类型更替塑造，箭头更合适解释为“空间化的发育流”，而非实际运动轨迹。

主包的 downstream RNA velocity graph 仍按表达变化 $x_j-x_i$ 与 $v_i$ 的 cosine similarity 构造。源码中曾设计 timed-KNN 的代码块被三引号注释掉，实际 `VelocityGraph` 使用普通邻居索引；不能声称默认 velocity graph 已按 latent time 过滤未来邻居。

### 如何读论文图与证据

- **图 1** 展示空间图、graph VAE、ODE decoder、spatial decoder 与 attention influence 的完整关系。
- **图 2** 在模拟和四个空间数据集上比较 time correlation、CBDir/k-CBDir、spatial time/velocity consistency 等。许多指标奖励空间平滑或依赖预设 transitions，不能彼此视为完全独立证据。
- **图 3** 在 cortex 中给出 radial cell velocity、约 10 μm h⁻¹ 的尺度与 influence pattern；速度吻合 live imaging 的量级很有启发性，但不是同一细胞的配对追踪验证。
- **图 4** 对 E9 neural tube 做三维 unrolling 和一维 divergence，定位 closure regions。unrolling、principal curve 与 sliding-window divergence 是专门分析流程，主要在 notebooks，不是核心 `VAE` 一次调用的通用输出。
- **图 5** 分析 human embryoid bodies 的 inside-to-outside dynamics 与 WNT-related influence enrichment；相关与富集支持机制假说，不是 perturbation proof。
- **Extended Data Fig. 1–3** 补充模拟、cell velocity 与 latent time 比较；**Fig. 4–7** 检查低分辨率和 graph radius；极端半径退化说明空间图选择是模型假设而非无关 preprocessing。

论文还报告 Visium、Slide-seq、Stereo-seq、Slide-tags、Curio Seeker 等不同分辨率数据。跨技术表现支持适用范围，但 spots 混合多个细胞时，“node influence”和“cell velocity”实际上是 spot-level quantity。

### 论文—代码对应与版本边界

论文报告 TopoVelo 0.0.2，而本地 `setup.py` 标记 `0.0.1a1`；不能把本地快照当成论文精确发布版本。

| 论文机制 | 直接源码 | 对应程度 |
|---|---|---|
| GAT/GCN encoder | `topovelo/model/vae.py:Encoder` | Exact |
| graph transcription decoder | `Decoder` / `GraphDecoder` / `_compute_rho()` | Exact |
| analytical splicing ODE | `model_util.py:pred_su()` | Exact |
| variational objective / staged training | `vae_risk()`、`train_epoch()` | Exact，配置细节决定实际权重 |
| RNA velocity | `model/velocity.py:rna_velocity_vae()` | Exact |
| spatial decoder | `SpatialDecoder`、`train_spatial_epoch()` | Exact |
| attention influence | GAT attention extraction/analysis | Partial：权重可提取，生物影响是解释层 |
| neural-tube unrolling/divergence | training/plot notebooks | Partial：不是核心包 API |
| timed velocity graph | `scvelo_util.py` | Not active：相关代码被注释 |
| 全论文复现 | notebooks + external Figshare/GEO data/models | Partial |

CodeGraph 已定位 VAE training、ODE solution、velocity 与 graph utilities，本次再直接核对源码、notebooks 路由、package metadata 和论文 OCR。未下载所有外部结果文件、未重新训练 GAT、未复算论文 benchmarks 或 attention/LR enrichment。

### 实际分析应检查什么

至少比较 KNN、epsilon-ball 与 Delaunay 图，扫描 radius/neighbor count；报告不同随机种子与 GAT/GCN 的稳定性；区分 cell-resolved 与 spot-resolved 数据；用 capture time、已知 transitions 或 live imaging 外部验证；分别呈现 RNA velocity 和 physical-space cell velocity；对 attention 做 degree/graph-null controls。若空间相邻主要来自切片几何而非真实交互，或组织含跨层远程信号，邻域图消息不应被直接命名为细胞间因果影响。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TopoVelo: Topological Velocity Inference from Spatial Transcriptomic Data

**Paper**: Gu, Y., Liu, J., Lee, K. H., Li, C., Lu, L., Moline, J., Guan, R. & Welch, J. D. *Nature Biotechnology* (2025)
**DOI**: [10.1038/s41587-025-02688-8](https://doi.org/10.1038/s41587-025-02688-8)
**Code**: [https://github.com/welch-lab/TopoVelo](https://github.com/welch-lab/TopoVelo) (v0.0.2)
**Lab**: Welch Lab, University of Michigan

---

### Motivation & Novelty

#### Biological Problem

Cell fate transitions are fundamentally **spatiotemporal** processes: transcription is regulated by signaling molecules from neighboring cells, extracellular matrix interactions, and gap junctions. Understanding how a cell's spatial microenvironment influences its molecular state during differentiation is a central question in developmental biology.

#### Limitations of Existing Approaches

| Category | Methods | Journal / Year | Key Limitation |
|----------|---------|---------------|----------------|
| Pseudotime | Monocle | *Nat. Methods*, 2017 | No spatial positions modeled; no direction or rate inference |
| Pseudotime | Slingshot | *BMC Genomics*, 2018 | No spatial positions modeled; no direction or rate inference |
| Optimal transport | moscot | *Nature*, 2025 | Require multiple timepoints; cannot be applied to single-slice data |
| Optimal transport | WOT | *Cell*, 2019 | Require multiple timepoints; cannot be applied to single-slice data |
| RNA velocity | scVelo | *Nat. Biotechnol.*, 2020 | **Do not consider spatial information** during parameter estimation |
| RNA velocity | VeloVAE | *ICML* (PMLR), 2022 | **Do not consider spatial information** during parameter estimation |
| RNA velocity | cellDancer | *Nat. Biotechnol.*, 2024 | **Do not consider spatial information** during parameter estimation |
| RNA velocity | DeepVelo | *Genome Biol.*, 2024 | **Do not consider spatial information** during parameter estimation |
| RNA velocity | VeloVI | *Nat. Methods*, 2024 | **Do not consider spatial information** during parameter estimation |
| Spatial velocity (existing) | Spateo | *Cell*, 2024 | Project velocity onto spatial coordinates but **do not use spatial positions during inference** |
| Spatial velocity (existing) | cell2fate | *bioRxiv* preprint, 2023 | Infers velocity modules from scRNA data and projects onto spatial coordinates |
| Spatial velocity (existing) | STT | *Nat. Methods*, 2024 | Estimates rates from scRNA data, projects velocity onto spatial coordinates |
| Spatial gene expression | GASTON | *Nat. Methods*, 2025 | Learns 1D isosurface but cannot model spliced/unspliced counts or assign directionality |

#### Key Innovation

TopoVelo is the **first method** to directly model how a cell's spatial microenvironment affects its gene expression dynamics through **spatially coupled differential equations**. The transcription rate of each cell is a function of both its own transcriptional state and the states of its spatial neighbors, implemented via a graph attention mechanism that learns cell-cell influence from data.

**Core probabilistic distinction**: Previous RNA velocity methods model cells as independent: $P(\mathcal{O}|\mathcal{Z},\mathcal{T}) = \prod_i P(\mathbf{o}_i | \mathbf{z}_i, t_i)$. TopoVelo models cells as **jointly distributed**: $P(\mathcal{O}|\mathcal{Z},\mathcal{T}) = \prod_i P(\mathbf{o}_i | \{\mathbf{z}_j, t_j : j \in \text{nbr}(i)\})$ (Eq. 3). Each cell's observation depends on the latent states and times of all its spatial neighbors.

#### Three Qualitative Advances Over Non-Spatial Methods

1. **Cell velocity prediction**: Estimates the rate and direction of cell movement in physical space (not just gene expression space)
2. **Cell influence scores**: Identifies which neighboring cells most strongly influence fate transitions, capturing contact-dependent signaling
3. **Morphological changes**: When paired with histology images, can identify changes in cell morphology during differentiation

---

### Method Overview

#### Algorithmic Framework

TopoVelo models tissue as a **graph** where nodes are cells/spots and edges connect spatial neighbors. Gene expression dynamics follow a system of ODEs:

$$\frac{du_{i,g}}{dt} = \rho_{i,g}(\{\mathbf{z}_j : j \in \text{nbr}(i)\}) - \beta_g u_{i,g}$$
$$\frac{ds_{i,g}}{dt} = \beta_g u_{i,g} - \gamma_g s_{i,g}$$

where $\rho_{i,g}$ (transcription rate) depends on the cell states of spatial neighbors via a **graph neural network decoder**.

#### Architecture

- **Encoder**: Graph attention network (GAT) + FC layers → latent cell time $t_i$ and cell state $\mathbf{z}_i$
- **Decoder**: GAT + FC layers → spatially coupled transcription rates $\rho_{i,g}$ → analytical ODE solution → predicted $u, s$
- **Spatial Decoder** (optional): Additional GNN that predicts 2D spatial coordinates from latent time/state
- **Training**: Variational inference maximizing an ELBO with KL divergence on cell time and state priors

#### Key Technical Components

1. **Gene phase modeling**: Dirichlet-Categorical indicator variables distinguish induction vs. repression genes
2. **Graph attention**: Multi-head attention (Eq. 8) learns directional influence between neighboring cells
3. **Cell influence score**: Aggregated attention weights (Eq. 10) quantify each cell's influence on its neighborhood
4. **Spatial graph options**: KNN, epsilon-ball, or Delaunay triangulation

#### Computational Pipeline

```
Input: AnnData with unspliced/spliced counts + spatial coordinates
  → Preprocessing (gene filtering, normalization, PCA, KNN smoothing)
  → Spatial graph construction (KNN/epsilon-ball/Delaunay)
  → VAE training with graph attention encoder-decoder (~1000 epochs)
  → Post-training spatial decoder (~500 epochs)
  → RNA velocity + cell velocity computation
  → Cell influence score extraction from attention weights
Output: Latent time, cell velocity, RNA velocity, influence scores stored in AnnData
```

---

### Evaluation

#### Datasets

| Dataset | Technology | Tissue | Stage | Resolution |
|---------|-----------|--------|-------|------------|
| Mouse cerebral cortex | Slide-seq v2 | Brain | E15 | 10 μm |
| Mouse gut/lung | Stereo-seq | GI/Lung | E13.5 | 20 μm bins |
| Human thymus | 10x Visium | Thymus | 3-month postnatal | 55 μm |
| Mouse brain | Slide-tags | Brain | E14.5 | Single-cell |
| Mouse embryo | Slide-seq | Neural tube | E9.0 | 20 μm |
| Mouse embryo | 10x Visium | Whole embryo | E13.5 | 55 μm |
| Human embryoid bodies | Curio Seeker | iPSC-derived EBs | Day 21 | **New data** |
| Simulated (layered/radial) | — | Simulation | — | Single-cell |

#### Methods Compared

| Method | Version | Key Characteristic |
|--------|---------|-------------------|
| scVelo | 0.2.5 | Gene-by-gene fitting, steady-state assumption, single lineage |
| VeloVAE | 0.1.2 | VAE with shared latent time, branching trajectories (authors' prior work) |
| cellDancer | 1.1.7 | Deep learning, cell-specific RNA velocity |
| DeepVelo | 0.2.8 | GNN-based but **not** using spatial information |
| VeloVI | — | VAE fitting each gene separately |
| STT | — | Estimates rates from scRNA data, projects velocity onto spatial coordinates (only other method using spatial info) |

#### Metrics

| Metric | What It Measures |
|--------|-----------------|
| CBDir | Cross-boundary direction correctness (velocity crosses cell type boundaries correctly) |
| k-CBDir | **Novel metric** — extends CBDir to k-step neighbors with time ordering penalty; addresses limitations of original CBDir (projection-only, no time order, too-similar neighbors) |
| Time correlation | Spearman correlation with ground truth/capture time |
| Spatial velocity consistency | Average Pearson correlation of RNA velocity among spatial neighbors |
| Spatial time consistency | Moran's I of inferred time across spatial neighborhoods |
| Velocity accuracy (sim) | Cosine similarity between true and predicted spatial velocity |

#### Key Results

1. **Benchmarking (Fig. 2)**: TopoVelo achieves **highest** performance on spatial time consistency, CBDir, spatial velocity consistency, and time correlation across all four real datasets and simulations
2. **Cell velocity magnitude (Fig. 3b)**: Predicted cortical neuron migration speed of **~10 μm/hr** matches live-cell imaging measurements (9.8–11.3 μm/hr)
3. **Cell influence scores (Fig. 3c-e)**: Spatial pattern of influence scores correlates with CytoSignal contact-dependent ligand-receptor signaling — despite TopoVelo using no L-R information
4. **Neural tube closure (Fig. 4)**: Correctly identifies all three closure points (C1, C2, C3) via divergence analysis of cell velocity
5. **Embryoid bodies (Fig. 5)**: Reveals inside-to-outside differentiation pattern, with WNT signaling enrichment near influential cells (Spearman correlation = 0.14, $P < 2.2 \times 10^{-16}$)
6. **Robustness**: Stable performance across epsilon-ball radii 10–200 μm; degrades only at extreme radii (>500 μm). Also robust to Visium-level spatial resolution reduction (Extended Data Fig. 4)
7. **Rate estimation trade-off**: TopoVelo and VeloVAE best at cell-specific transcription rates; scVelo and VeloVI best at gene-level splicing/degradation rates — suggesting a fundamental trade-off between cell-level and gene-level parameter accuracy

---

### Limitations (Acknowledged by Authors)

1. **No explicit spatial modeling of gene expression**: Spatial position builds the graph but gene expression is not directly modeled as a function of coordinates
2. **No cell-specific splicing/degradation**: $\beta_g$ and $\gamma_g$ are gene-specific but shared across all cells
3. **No transcriptional variance modeling**: Does not capture stochastic gene expression variation
4. **Two gene phases only**: Each gene is globally in induction or repression; oscillating expression patterns not supported
5. **Cell velocity interpretation**: Cell velocity vectors indicate direction of cell maturation and *sometimes* migration — not guaranteed to reflect physical movement in all contexts

---

### Reproducibility Assessment

#### Rating: 4/5

#### Strengths

- **Code available**: Full Python package on GitHub with pip installation
- **Preprocessed data**: Available on figshare (doi:10.6084/m9.figshare.28516139.v2)
- **Tutorial notebooks**: Training, evaluation, and plotting notebooks for multiple datasets
- **Simulation framework**: Built-in simulation with ground truth for validation
- **Comprehensive API**: Well-documented classes with docstrings

#### Potential Blockers

1. **GPU dependency**: Requires PyTorch with CUDA; graph attention is memory-intensive
2. **Version pinning**: Strict dependency constraints (numpy ≤1.23.5, pandas ≤1.5.3, scvelo ≤0.2.5) may cause environment conflicts
3. **PyTorch Geometric**: Installation can be non-trivial due to CUDA version matching
4. **Non-deterministic**: Graph attention in PyTorch is not fully reproducible even with fixed random seeds (acknowledged in code)
5. **Large files**: Example data and trained models require separate download
6. **New EB data**: Raw Curio Seeker data on GEO (GSE291200), but processing pipeline requires proprietary Curio software

#### Environment Setup

```bash
pip install topovelo
# Or from source:
git clone https://github.com/welch-lab/TopoVelo.git && cd TopoVelo && pip install .
```

Requires: Python 3.9–3.10, PyTorch ≥1.8, PyTorch Geometric ≥2.0.4, CUDA-compatible GPU recommended.

#### Data Availability

| Resource | URL |
|----------|-----|
| Preprocessed AnnData (all datasets) | [figshare 28516139.v2](https://doi.org/10.6084/m9.figshare.28516139.v2) |
| AnnData with TopoVelo results | [figshare 28516184.v1](https://doi.org/10.6084/m9.figshare.28516184.v1) |
| Human EB raw data (Curio Seeker) | [GEO GSE291200](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE291200) |
| Slide-tags mouse brain raw | [GEO GSE244355](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE244355) |
| E9 3D mouse embryo raw | [GEO GSE197353](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE197353) |
| Stereo-seq data | [CNGB MOSTA](https://db.cngb.org/stomics/mosta/) |
| Human thymus Visium | [ENA PRJEB77091](https://www.ebi.ac.uk/ena/browser/view/PRJEB77091) |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
