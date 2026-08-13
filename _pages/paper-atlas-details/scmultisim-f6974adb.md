---
layout: default
permalink: /paper-atlas/scmultisim-f6974adb/
title: "scMultiSim"
nav: false
wide: true
description: "scMultiSim 不是从参考数据中拟合一个黑箱生成器，而是让用户先给出细胞分化树，并可选提供基因调控网络（GRN）和细胞间相互作用（CCI），再把细胞身份、调控、染色质可及性和空间邻域逐层写入转录动力学参数，最终同时输出 RNA、ATAC、RNA velocity、空间位置及其真值。它的主要用途不是复刻某一个真实样本，而是构造“因素已知且强度可调”的数据来检验分析方法。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>scMultiSim</h1>
    <p>scMultiSim: simulation of single-cell multi-omics and spatial data guided by gene regulatory networks and cell-cell interactions</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02651-0" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scMultiSim">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ZhangLabGT/scMultiSim" target="_blank" rel="noopener noreferrer" aria-label="Open code for scMultiSim">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMultiSim 方法解读：从可控生物因素到多模态基准真值

### 一句话抓住方法

scMultiSim 不是从参考数据中拟合一个黑箱生成器，而是让用户先给出细胞分化树，并可选提供基因调控网络（GRN）和细胞间相互作用（CCI），再把细胞身份、调控、染色质可及性和空间邻域逐层写入转录动力学参数，最终同时输出 RNA、ATAC、RNA velocity、空间位置及其真值。它的主要用途不是复刻某一个真实样本，而是构造“因素已知且强度可调”的数据来检验分析方法。

论文来源为 Li 等发表于 *Nature Methods*（2025）的 “scMultiSim: simulation of single-cell multi-omics and spatial data guided by gene regulatory networks and cell-cell interactions”，DOI `10.1038/s41592-025-02651-0`。本地 `DESCRIPTION` 标为 scMultiSim 1.1.10、R >= 4.4.0，但没有 Git 提交哈希，因此可以验证机制与当前实现，不能声称它就是论文实验使用的精确提交。

### 1. 为什么要这样模拟

真实单细胞多组学数据通常没有可直接观测的细胞轨迹、GRN、CCI 或真实 RNA velocity。参考数据驱动的模拟器容易生成与参考数据相似的边际分布，却不一定能给出这些机制的无歧义真值。scMultiSim 选择相反路线：先指定机制，再生成观测。

最小输入是细胞分化树，它规定连续轨迹或离散细胞群。GRN 虽非语法上的必填项，却是模拟调控效应和开展 GRN 基准时的重要输入。空间模式还需要配体—受体关系、细胞类型间 CCI 参数及布局选项。论文 Fig. 1a 从左到右把这一契约画得很清楚：输入树与 GRN，中间生成多模态数据和元数据，外围对应轨迹、整合、velocity、GRN 与 CCI 等评测任务。

### 2. 主线：先构造因素，再构造观测

#### 2.1 CIF 与 GIV 是细胞因素和基因响应的接口

对每个细胞，Cell Identity Factor（CIF）是长度为 $n_{\mathrm{cif}}$ 的因素向量；对每个基因，Gene Identity Vector（GIV）给出该基因对这些因素的权重。矩阵乘法

$$
\mathrm{CIF}_{n_{\mathrm{cell}}\times n_{\mathrm{cif}}}
\mathrm{GIV}_{n_{\mathrm{cif}}\times n_{\mathrm{gene}}}
=M_{n_{\mathrm{cell}}\times n_{\mathrm{gene}}}
$$

把“某个因素在某个细胞中有多强”和“某个基因如何响应这个因素”组合成逐细胞、逐基因的动力学参数底稿。论文 Fig. 2a 将 CIF/GIV 都拆成四段：

- non-diff 段描述不随细胞群结构系统变化的异质性；
- diff 段沿输入树或离散群体改变，形成轨迹/聚类结构；
- TF 段把细胞内 TF 表达和 GRN 边效应连接起来；
- ligand 段把邻居细胞配体信号和 CCI 效应连接起来。

这里需要避免一个常见误读：CIF 不是最终表达量，GIV 也不是一个单独的 GRN。两者相乘得到的是生成动力学参数的中间量；TF-GIV 中的效应矩阵才直接承载给定 GRN 的调控权重。源码中 `R/1_main.R` 的 `.continuousCIF()` / `.discreteCIF()`、`.geneIdentifyVectors()` 分别构造这些部件，`R/2_sim.R` 的 `.getParams()` 执行 CIF 与 GIV 的乘法和后处理。

#### 2.2 ATAC 必须先生成，因为它会反过来影响 RNA

scMultiSim 用 Region Identity Vector（RIV）对染色质区域做与 GIV 类似的编码。先计算

$$
\mathrm{CIF}\,\mathrm{RIV}
$$

得到细胞×区域的相对可及性，再按真实数据学习到的非零分布做秩匹配并加入稀疏性和内在噪声。本地 `.atacSeq()` 的注释和实现明确执行 CIF×RIV、排序、按密度采样及零值填充。

区域不会仅作为一个独立输出结束。`.regionToGeneMatrix()` 建立区域—基因矩阵；`.getParams()` 将 ATAC 矩阵乘以该映射，得到逐细胞、逐基因的 `ATAC_kon`。参数 `atac.effect` 在 ATAC 排名和原始 $k_{\mathrm{on}}$ 排名之间插值，再将结果映射回参数分布。因此提高该参数改变的是可及性对基因激活率排序的控制程度，而不是简单地把 ATAC 计数乘到 RNA 计数上。论文 Fig. 2f 正是用不同 $E_a$ 展示 ATAC—RNA 相关随耦合强度增加。

#### 2.3 三个动力学参数决定表达

每个细胞—基因对有 $k_{\mathrm{on}}$、$k_{\mathrm{off}}$ 和合成率 $s$。前两者主要来自相应 CIF/GIV 乘积，并由 ATAC 修正 $k_{\mathrm{on}}$；$s$ 还承载 TF/GRN 和 ligand/CCI 效应。源码会用 `.matchParamsDen()` 将中间值按秩映射到真实数据学习的参数分布，这意味着模型同时保留因素诱导的相对顺序与较现实的边际分布。

随后有两种生成路径：

1. 快速 beta–Poisson 模式。`.betaPoisson()` 先采样

$$y\sim\mathrm{Beta}(k_{\mathrm{on}},k_{\mathrm{off}}),\qquad x\sim\mathrm{Poisson}(ys),$$

再用 `intr.noise` 在随机样本 $x$ 与均值 $k_{\mathrm{on}}s/(k_{\mathrm{on}}+k_{\mathrm{off}})$ 之间插值。它适合不需要 velocity、关注运行速度的场景。

2. 完整动力学模式。`gen_1branch()` 显式推进基因 on/off 状态、未剪接 RNA 和已剪接 RNA。若用 $u$ 表示未剪接、$x_s$ 表示已剪接，代码中的连续更新对应

$$\frac{du}{dt}=sI_{\mathrm{on}}-\beta u,\qquad
   \frac{dx_s}{dt}=\beta u-dx_s,$$

并输出真值速度

$$v=\beta u-dx_s.$$

因此 velocity 真值来自同一个动力学过程，而不是事后根据降维图画出的箭头。论文 Extended Data Fig. 2b 展示其方向沿输入 Phyla5 轨迹。

`intr.noise` 的含义也应谨慎解释：在 beta–Poisson 路径中它直接控制随机 burst 样本相对均值的权重；它不是后续测序 dropout 的同义词。后者属于第二阶段的技术噪声。

### 3. 空间与 CCI：邻居信号进入 ligand 段

开启 CCI 后，模拟不再一次性独立生成全部细胞。`R/3.1_spatial.R` 的 `CreateSpatialGrid()` 在二维网格中建立位置和邻域，论文 Fig. 2a(ix) 的默认示意中一个细胞最多有四个近邻。每一步加入一个新细胞，并依据 `same.type.prob`（论文记作 $p_n$）调节同类细胞聚集倾向；源码还支持 `default`、`islands` 与 `layers` 等布局。

邻居细胞的配体表达被写入当前细胞的 ligand-CIF，而 ligand-GIV 给出它对受体/下游基因的效应。于是空间距离不会直接替代 CCI 真值：位置决定候选邻居，给定的配体—受体及细胞类型规则决定哪些信号有效，最终效应再经 CIF/GIV 和动力学参数进入表达。长距离模式还可按距离核抽样相互作用。

这条逐步模拟在大细胞数时可能昂贵。本地 `sim_true_counts()` 显示，当空间细胞数超过 800 且保持自动设置时，`sp_start_layer` 可跳到最后一层以加速。该实现边界会影响运行时间和中间动态的可观察性，复现实验时应记录选项，而不能只记录最终随机种子。

### 4. “真值计数”与“观测计数”必须分开

前述过程产生 phase 1 的 true counts。phase 2 才模拟捕获、扩增、测序、批次等技术过程。入口是 `R/6_technoise.R` 的 `add_expr_noise()`；底层 `True2ObservedCounts()` 将真值转换为观测计数，并可按批次划分和施加批次效应。

这种两阶段设计对评测很重要：若目标是验证生物机制恢复能力，可以使用真值计数隔离技术噪声；若目标是接近真实分析场景，应使用观测计数，并明确噪声和批次参数。把两者混用会将“生成机制是否正确”和“方法能否抗实验噪声”混成一个问题。

### 5. 从接口看一次实际运行

本地源码的主入口是 `R/1_main.R::sim_true_counts(options, return_summarized_exp = FALSE)`。其执行顺序可概括为：

1. `.check_opt()` 校验选项，解析树、velocity、GRN 和空间设置；
2. 标准化 GRN、重命名基因并建立 TF—靶基因效应；
3. 构造连续或离散 CIF，以及 GIV、RIV 和区域—基因映射；
4. `.atacSeq()` 先生成 ATAC；
5. `.getParams()` 生成并校准 $k_{\mathrm{on}}$、$k_{\mathrm{off}}$，随后组织 $s$；
6. 选择 beta–Poisson 或完整动力学路径生成 RNA；空间模式则逐层传播 CCI；
7. 返回 counts、ATAC、细胞元数据、动力学量和 GRN/CCI 等真值；需要观测数据时再调用技术噪声层。

最小示例可以只给树；若要评测 GRN，应显式给 GRN 并保存全部参数：

```r
data(GRN_params_100, envir = environment())
res <- sim_true_counts(list(
  rand.seed = 0,
  GRN = GRN_params_100,
  num.cells = 500,
  num.cifs = 50,
  tree = Phyla5()
))
```

具体返回字段应以本地版本的函数文档与 `results` 对象为准。源码快照提供实现证据，但工作区没有保存论文 144 个主数据集的完整生成脚本、原始环境锁文件或论文代码提交哈希，所以不能仅靠上述示例逐位复现论文所有 benchmark 数字。

### 6. 怎样读论文中的验证

论文不是只比较边际统计，而是逐项验证可控机制：

- Fig. 2c–e 检查输入树、CIF 方差、diff-CIF 比例和 intrinsic noise 是否按预期改变轨迹/聚类清晰度；
- Fig. 2f 检查 `atac.effect` 是否改变 ATAC—RNA 关联；
- Fig. 3 检查给定 GRN 与 CCI 是否在表达相关中留下预期信号；
- Extended Data Fig. 2 检查批次效应和 RNA velocity 真值；
- Extended Data Fig. 4 检查空间布局、空间域、SVG 与长距离 CCI。

这些结果证明“调节输入会得到方向正确的输出效应”，不等于模拟数据覆盖了真实组织的全部机制。论文随后用 144 个主要配置和若干辅助数据集开展整合、velocity、GRN、CCI 等 benchmark；这些比较依赖选定参数、方法版本和评测指标，不应解读成对所有数据集的通用方法排名。

### 7. 论文—代码对应和证据边界

| 论文机制 | 本地直接实现 | 对应程度 |
|---|---|---|
| CIF/GIV 编码细胞身份和调控 | `R/1_main.R`, `R/1.1_cif.R` | Exact：结构和主流程可直接核对 |
| CIF/RIV 生成 ATAC | `R/2_sim.R::.atacSeq()` | Exact |
| ATAC 经区域—基因映射影响 $k_{\mathrm{on}}$ | `R/1_main.R::.regionToGeneMatrix()`, `R/2_sim.R::.getParams()` | Exact |
| beta–Poisson 与内在噪声 | `R/2_sim.R::.betaPoisson()` | Exact |
| 完整动力学及真值 velocity | `R/2_sim.R::gen_1branch()` | Exact |
| 网格布局和 CCI | `R/3.1_spatial.R`, `sim_true_counts()` | Exact，具体数据集参数仍需实验脚本 |
| 技术噪声与批次 | `R/6_technoise.R` | Exact |
| 论文全部 benchmark 数据与结果 | 论文正文提供设计，本地包源码为核心实现 | Partial：缺少完整实验环境与精确提交 |

### 8. 使用时最容易踩的坑

- 不要把树看成可选装饰：它决定连续轨迹或离散群体，是最小输入中的结构真值。
- 不要把 `atac.effect` 解释为表达量线性倍数；当前实现通过秩融合影响 $k_{\mathrm{on}}$。
- 不要用 observed counts 反向校验“无噪声机制”而不报告技术噪声配置。
- 不要只保存输出矩阵。树、GRN、CCI、区域—基因映射、随机种子、包版本和全部 options 都是可复现真值的一部分。
- 不要把源码快照的 1.1.10 版本等同于论文提交；缺失 commit 和实验环境是明确的复现边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scMultiSim: Paper and Implementation Summary

**Paper**: "scMultiSim: simulation of single-cell multi-omics and spatial data guided by gene regulatory networks and cell-cell interactions"
**Journal**: Nature Methods (April 2025)
**DOI**: 10.1038/s41592-025-02651-0
**Code Repository**: https://github.com/ZhangLabGT/scMultiSim/

### Paper-Code Mapping Table

| Paper Concept | Code Location | Key Functions |
|---------------|---------------|---------------|
| **Kinetic Model (k_on, k_off, s)** | `R/2_sim.R` | `.getParams()`, `.betaPoisson()`, `.betaPoisson.vec()` |
| **Beta-Poisson Model (Eq. 1-2)** | `R/2_sim.R:945-963` | `.betaPoisson()` - samples y~Beta(k_on, k_off), x~Poisson(y*s) |
| **Intrinsic Noise σ_i (Eq. 3)** | `R/2_sim.R:952` | `intr.noise * x + (1 - intr.noise) * xMean` |
| **CIF/GIV Matrices (Fig. 2a)** | `R/1_main.R`, `R/1.1_cif.R` | `.continuousCIF()`, `.discreteCIF()`, `.geneIdentifyVectors()` |
| **Full Kinetic Model (RNA velocity)** | `R/2_sim.R:828-941` | `gen_1branch()` - state transitions, spliced/unspliced counts |
| **Velocity Ground Truth (Eq. 13)** | `R/2_sim.R:933` | `velo_mat <- beta_vec * counts_u - d_vec * counts_s` |
| **scATAC-seq Simulation** | `R/2_sim.R:212-241` | `.atacSeq()` - CIF × RIV multiplication |
| **ATAC Effect on k_on** | `R/2_sim.R:114-146` | ATAC_kon integration with parameter E_a |
| **Parameter Density Matching** | `R/2_sim.R:1-24` | `.matchParamsDen()` - matches to real data distributions |
| **GRN Effects (TF-target)** | `R/1_main.R:746-764` | `.geneEffectsByRegulator()` - gene-by-TF effect matrix |
| **Spatial Grid System (Fig. 2a-ix)** | `R/3.1_spatial.R:329-656` | `spatialGrid` class, `CreateSpatialGrid()` |
| **Cell-Cell Interactions** | `R/3.1_spatial.R:1-120` | `.parseSpatialParams()`, ligand-receptor pair handling |
| **Technical Noise Addition** | `R/6_technoise.R` | `add_expr_noise()`, `True2ObservedCounts()` |
| **Batch Effects** | `R/6_technoise.R:72-125` | `divide_batches()`, `.divideBatchesImpl()` |
| **Region-to-Gene Mapping (Eq. 9)** | `R/1_main.R:873-889` | `.regionToGeneMatrix()` |
| **Dynamic GRN** | `R/3.2_dyngrn.R` | Time-varying network structure |
| **Main Simulation Interface** | `R/1_main.R:53-298` | `sim_true_counts()` - orchestrates entire pipeline |

### Motivation and Novelty

#### Biological Problem Addressed
scMultiSim addresses the critical need for comprehensive single-cell multi-omics data simulation in computational biology. Current experimental single-cell datasets lack ground truth information, making it challenging to evaluate computational methods for:
- Gene regulatory network (GRN) inference
- RNA velocity estimation
- Multi-modal data integration
- Cell-cell interaction (CCI) analysis
- Spatial transcriptomics analysis

#### Limitations of Existing Approaches
Existing single-cell simulators suffer from several key limitations:
- **Limited modalities**: Most simulators generate only scRNA-seq data, while real experiments increasingly involve multiple modalities
- **Simplified biological modeling**: Current tools model only one or few biological factors (e.g., only GRNs or only cell identity), missing the complex interplay between multiple biological processes
- **Lack of comprehensive ground truth**: Reference-based simulators cannot provide ground truth for biological factors, limiting benchmarking capabilities
- **No spatial considerations**: Most simulators ignore spatial arrangements and cell-cell interactions that are crucial in real biological systems

#### Unique Contributions and Innovations
scMultiSim introduces several groundbreaking features:

1. **Comprehensive Multi-modal Output**: Simultaneously generates scRNA-seq, scATAC-seq, RNA velocity, and spatial location data with biologically meaningful relationships between modalities

2. **Unified Biological Factor Modeling**: First simulator to simultaneously model:
   - Cell identity (trajectories/clusters)
   - Gene regulatory networks
   - Chromatin accessibility effects
   - Cell-cell interactions
   - Technical noise and batch effects

3. **Novel Mathematical Framework**:
   - Cell Identity Factors (CIFs) and Gene Identity Vectors (GIVs) encode biological heterogeneity
   - Kinetic model with parameters k_on, k_off, s drives realistic gene expression
   - Multi-step spatial simulation considers both time and space

4. **Flexible Parameter Control**: Users can adjust the effect of each biological factor independently, enabling systematic investigation of method performance under different biological scenarios

5. **Comprehensive Benchmarking Platform**: Single framework can evaluate methods for tasks that previously required different simulators, including mosaic integration, multi-omics GRN inference, and spatial CCI analysis

#### Significance for Bioinformatics Community
- **Method Development**: Provides realistic data for developing and testing new computational methods
- **Fair Comparison**: Enables standardized benchmarking across diverse computational tasks
- **Biological Insight**: Allows investigation of how biological factors affect method performance
- **Educational Value**: Helps researchers understand relationships between different biological processes

### Method Overview

#### Algorithmic Framework and Core Ideas
scMultiSim employs a two-phase simulation approach:

**Phase 1: True Count Generation**
- Uses kinetic model with parameters k_on (activation rate), k_off (deactivation rate), and s (synthesis rate)
- Incorporates biological factors through Cell Identity Factors (CIFs) and Gene Identity Vectors (GIVs)
- CIF × GIV multiplication generates cell-gene parameter matrices encoding biological effects

**Phase 2: Technical Noise Addition**
- Models experimental procedures (mRNA capture, PCR amplification, sequencing)
- Adds batch effects and technical variations
- Converts "true" counts to "observed" counts matching real data statistics

#### Key Technical Components

##### Kinetic Modeling
- **Full Kinetic Model**: Simulates gene on/off state changes over time, provides RNA velocity ground truth
- **Beta-Poisson Model**: Faster equivalent model for when velocity is not needed
- **Intrinsic Noise Parameter σ_i**: Controls transcriptional burst variability

##### Cell Identity Factors (CIFs) and Gene Identity Vectors (GIVs)
- **CIF Design**: One-dimensional vectors representing cellular states and biological factors
- **GIV Design**: Weight vectors determining how CIF factors affect individual genes
- **Four Segments**: Each CIF/GIV contains segments encoding:
  1. Cell population identity
  2. Gene regulatory network effects
  3. Cell-cell interaction effects
  4. Additional biological variations

##### Multi-modal Data Generation
- **scATAC-seq**: Generated first using Region Identity Vectors (RIVs), affects scRNA-seq through k_on
- **RNA Velocity**: Full kinetic model outputs unspliced/spliced counts with ground truth velocity
- **Spatial Data**: Grid-based placement with neighborhood-aware CCI simulation

#### Biological Assumptions and Model Design

##### Chromatin Accessibility Effects
- scATAC-seq data influences scRNA-seq through k_on parameter (activation rate)
- User-controllable ATAC-effect parameter E_a determines coupling strength
- TF-motif matrices and GRNs determine region-gene relationships

##### Gene Regulatory Networks
- Supports both static and dynamic GRNs (time-varying network structures)
- TF effects encoded in GIV segments affecting target gene expression
- Correlation patterns validate successful GRN encoding

##### Cell-Cell Interactions
- **Spatial Grid System**: Cells placed on 2D grid with neighborhood relationships
- **Dual CCI Effects**: Models both correlation effects and high-expression effects
- **Ligand-Receptor Pairs**: Cross-cell regulatory interactions supplement within-cell GRNs

#### Computational Pipeline

##### Input to Output Flow
1. **Input**: Cell differentiation tree, GRN, optional CCI network, parameter settings
2. **CIF/GIV Generation**: Create factor matrices encoding biological effects
3. **scATAC-seq Simulation**: Generate chromatin accessibility using RIVs
4. **Parameter Calculation**: Compute kinetic parameters from CIF×GIV + scATAC effects
5. **scRNA-seq Simulation**: Apply kinetic model (full or beta-Poisson)
6. **Spatial/CCI Simulation**: Multi-step process considering time and space
7. **Technical Noise**: Add experimental artifacts and batch effects
8. **Output**: Multi-modal data with ground truth for benchmarking

##### Scalability and Performance
- Beta-Poisson mode provides faster simulation when velocity not needed
- Memory-efficient parameter matching for large gene sets
- Parallelization support for large-scale simulations
- Benchmark datasets: 144 main datasets with various parameter combinations

### Evaluation Strategy

#### Datasets Used
scMultiSim evaluation employs both simulated benchmarks and real data comparisons:

##### Simulated Benchmark Datasets
- **144 Main Datasets**: Comprehensive parameter combinations including:
  - Different cell population structures (linear, tree, discrete)
  - Various cell numbers (100-800) and gene numbers (100-500)
  - Multiple σ_cif values controlling within-population heterogeneity
  - Four random seeds per configuration
- **Auxiliary Datasets**: Focused datasets for specific parameter studies
- **Spatial Datasets**: Include cell-cell interactions and spatial arrangements

##### Real Dataset Comparisons
- **10x Genomics Multiome PBMC**: Paired scRNA-seq and scATAC-seq validation
- **ISAAC-seq**: Additional multi-modal validation dataset
- **MERFISH and seqFISH+**: Spatial transcriptomics validation datasets

#### Evaluation Metrics and Biological Relevance

##### Statistical Similarity Metrics
- **Library size distribution**: Total UMI/read counts per cell
- **Zero count patterns**: Dropout rates per cell and gene
- **Mean-variance relationships**: Gene expression variability patterns
- **Gene-gene and cell-cell correlations**: Co-expression and similarity structures

##### Biological Validation Metrics
- **GRN Correlation Analysis**: Heat maps showing TF-target co-expression
- **ATAC-RNA Coupling**: Spearman correlations between accessibility and expression
- **CCI Validation**: Expression correlations between neighboring vs. non-neighboring cells
- **RNA Velocity Accuracy**: Ground truth velocity direction validation
- **Spatial Pattern Validation**: SVG expression patterns and domain structures

#### Comparative Results Against Baseline Methods

##### Single-cell Simulators Comparison
**Compared Methods**:
- **dyngen**: Multi-modal GRN-based simulator
- **SERGIO**: GRN-guided scRNA-seq simulator
- **scDesign3**: Reference-based multi-modal simulator

**Statistical Performance**:
- scMultiSim matches scDesign3 in similarity to real data
- Outperforms dyngen in zero-count and mean-count distributions
- Similar performance to SERGIO but with additional modalities

##### Computational Method Benchmarking Results

**Mosaic Data Integration** (3 methods tested):
- **UINMF**: Best performance across all metrics (ARI, NMI, GC, ASW)
- **Seurat-bridge**: Moderate performance, integration-specific advantages
- **Cobolt**: Lower cell identity preservation but good batch mixing

**GRN Inference** (13 methods tested):
- **Expression-only methods**: PIDC > GENIE3 > GRNBOOST2
- **Multi-omics methods**: scMTNI and CellOracle show superior AUPRC ratios
- **Technical noise impact**: Significant performance degradation with observed counts
- **Consistency validation**: Rankings match previous biological benchmarks

**RNA Velocity Estimation**:
- Ground truth velocity enables systematic evaluation
- Methods tested on both continuous and discrete populations

**Spatial Analysis**:
- **Domain Detection**: STAGATE (ARI=0.662) > scHybridNMF (ARI=0.597)
- **SVG Detection**: Multiple pattern types validated
- **CCI Inference**: Both correlation and high-expression effects benchmarked

#### Biological Validation Experiments

##### Multi-factor Effects Validation
- **Parameter Sensitivity**: σ_cif, σ_i, r_d effects on population clarity
- **GRN Effects**: Module correlation patterns confirm regulatory relationships
- **Chromatin Accessibility**: E_a parameter controls ATAC-RNA coupling strength
- **Spatial Effects**: Layout patterns and CCI correlation validations

##### Cross-modality Relationships
- **Expected Correlations**: 0.2-0.3 ATAC-RNA correlations at default settings
- **Biological Realism**: Negative correlation between zero counts and mean expression
- **Technical Noise Effects**: Realistic degradation patterns with experimental artifacts

The comprehensive evaluation demonstrates that scMultiSim generates biologically realistic data while providing the ground truth necessary for meaningful method benchmarking across diverse computational tasks.

### Key Mathematical Formulas (from Paper)

#### Beta-Poisson Model (Methods)
The master equation of the kinetic model is approximated by the Beta-Poisson distribution:

$$y = \text{Beta}(k_{\text{on}}, k_{\text{off}})$$

$$x = \text{Poisson}(y \times s)$$

#### Intrinsic Noise Control (Eq. 3)
Parameter $\sigma_i$ controls intrinsic noise by adjusting weight between random samples and theoretical mean:

$$x_{\sigma_i} = \sigma_i \times x + (1 - \sigma_i) \times \left(\frac{k_{\text{on}}}{k_{\text{on}} + k_{\text{off}}} \times s\right)$$

#### RNA Velocity Ground Truth (Eq. 13)
Velocity is calculated from splicing dynamics:

$$v = \beta \times x_u - d \times x_s$$

Where $\beta$ is splicing rate and $d$ is degradation rate.

#### TF-CIF Encoding (Eq. 5)
TF effects on subsequent cells:

$$\text{tf-CIF}_i^{(t+1)} = \frac{x_i^{(t)}}{x_i^{(t)} + \frac{1}{n}\sum_l x_l^{(t)}}$$

#### ATAC-GRN Relationship (Eq. 9)
Region-to-gene mapping through TF motifs:

$$M_{\text{tg}} = M_{\text{tr}} \times M_{\text{rg}}$$

#### Batch Effects Model
For each gene $i$ in batch $j$, shift factor sampled from:

$$\text{Unif}(\mu_i - e_b, \mu_i + e_b), \quad \mu_i \sim \mathcal{N}(0,1)$$

#### Long-Distance CCI (Eq. 6)
Probability of cell interaction with Gaussian kernel:

$$P(\text{Interact}(i,j)) \propto \exp\left(\frac{-d(i,j)^2}{2 \cdot \sigma_{\text{rad}}^2}\right)$$

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
