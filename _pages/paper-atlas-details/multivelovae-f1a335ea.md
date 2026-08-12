---
layout: default
permalink: /paper-atlas/multivelovae-f1a335ea/
title: "MultiVeloVAE"
nav: false
description: "RNA velocity 用未剪接 RNA u 与已剪接 RNA s 的时间滞后估计表达变化方向。传统方法常逐基因设定开/关阶段，难以同时处理多分支、多样本、RNA+ATAC 以及组间动力学检验。MultiVeloVAE 将这些问题放入一个带机械 ODE decoder 的条件变分自编码器中。 输入可以是 RNA 的平滑未剪接/已剪接矩阵，也可以再加入每个基因附近的染色质可及性 c。多个样本通过 batch 标签共同训练；"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>MultiVeloVAE</h1>
    <p>Inferring differential dynamics from multi-lineage, multi-omic, and multi-sample single-cell data with MultiVeloVAE</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-66287-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MultiVeloVAE 中文方法解读

### 方法要解决的四个问题

RNA velocity 用未剪接 RNA $u$ 与已剪接 RNA $s$ 的时间滞后估计表达变化方向。传统方法常逐基因设定开/关阶段，难以同时处理多分支、多样本、RNA+ATAC 以及组间动力学检验。MultiVeloVAE 将这些问题放入一个带机械 ODE decoder 的条件变分自编码器中。

输入可以是 RNA 的平滑未剪接/已剪接矩阵，也可以再加入每个基因附近的染色质可及性 $c$。多个样本通过 batch 标签共同训练；部分样本可以只有 RNA。输出包括共享尺度的细胞潜时间 $t$、低维细胞状态 $z$、细胞—基因特异的转录状态 $\rho$ 与染色质目标状态 $k_c$、基因动力学参数以及三种 velocity。

velocity 是模型在当前状态下的瞬时导数，不是实验连续追踪到的细胞移动。潜时间也由模型与可选时间先验共同识别；没有真实时间先验时，其绝对单位不可直接解释为小时或天。

### 1. 三层动力学：染色质、未剪接和已剪接 RNA

对每个基因，论文使用

$$
\frac{dc}{dt}=\alpha_c(k_c-c),
$$

$$
\frac{du}{dt}=\rho\alpha c-\beta u,
\qquad
\frac{ds}{dt}=\beta u-\gamma s.
$$

$\alpha_c$ 是染色质变化尺度，$\alpha$ 是最大转录尺度，$\beta$ 是剪接率，$\gamma$ 是降解率。$k_c\in[0,1]$ 表示当前细胞状态下染色质趋向的稳态，$\rho\in[0,1]$ 表示相对转录活性。与二值开关不同，两个量由 decoder 的神经网络根据潜状态 $z$ 为每个细胞和基因连续预测，因此同一基因可以在不同分支采用不同调控状态。

线性 ODE 有闭式解。decoder 不做数值积分，而在 $\tau=t-t_0$ 上直接计算 $\hat c,\hat u,\hat s$。`pred_exp()` 和 `pred_exp_numpy()` 是核心解析解（`multivelovae/model/model_util_chrom.py:92-113`），`velocity()` 则直接计算

$$
v_c=\alpha_c(k_c-c),\quad
v_u=\rho\alpha c-\beta u,\quad
v_s=\beta u-\gamma s.
$$

代码为相近速率的分母加 $10^{-6}$，反向积分时还截断指数和预测计数。这些是必要的数值保护，也说明“解析解”并非在所有退化参数下无误差。

### 2. VAE 如何把细胞状态和动力学连起来

encoder 接收拼接的 $(c,u,s)$ 和可选 batch/连续协变量，估计

$$
q_\phi(z,t\mid c,u,s,b).
$$

$z$ 表示低维细胞状态，$t$ 是所有基因共享的潜时间。decoder 由 $z$、$t$ 和 batch 标签产生 $k_c(z,b)$、$\rho(z,b)$ 及 ODE 重构。训练最大化 ELBO：三模态 Gaussian 重构似然减去 $z$ 与 $t$ 的 KL；多样本模式还对不同 batch 的基因动力学参数施加向参考 batch 靠拢的 L2 正则。

“所有基因共享时间”避免逐基因时间互相冲突，但并不代表每个基因都在所有细胞中同步启动。每个基因仍有激活时间和初始条件，decoder 通过 $\tau=t-t_0$ 表达其相对进程。

默认 `full_vb=False`（`vae_chrom.py:918-948`），所以常规运行对 $\alpha_c,\alpha,\beta,\gamma$ 使用点估计，而不是论文式 (16) 所描述的完整参数后验。VAE 仍对 $z,t$ 采样，差异检验也能传播细胞潜变量不确定性，但不能把这等同于默认对所有 ODE 参数完整贝叶斯化。

### 3. 多样本与部分模态如何统一

batch 标签以 one-hot 形式输入条件 VAE。目标是让 $z$ 尽量表达跨样本共享的生物状态，同时 decoder 允许 batch 特异的动力学参数、缩放和偏移。训练后可用统一参考 batch 解码所有细胞，生成反事实 batch-corrected $(c,u,s)$，再从校正值计算 velocity。

这不是简单把 velocity 箭头投影到整合 UMAP：动力学参数本身在联合模型中估计。但“去 batch”仍依赖参考样本和正则强度；若 batch 与真实生物条件完全混杂，模型无法从数据本身唯一分离技术与生物差异。

对于 RNA-only 样本，代码构造全 1 的伪染色质输入，并将模型约束为染色质恒开；混合数据时通过 `rna_only_idx` 标记没有 ATAC 的 batch（`vae_chrom.py:1017-1042`）。这允许 RNA-only 与 multiome 联合，但缺失 ATAC 并不是被观测数据真正补齐：其染色质预测由共享潜状态、multiome 样本和模型假设间接确定。

### 4. 两阶段训练与初始条件

第一阶段使用基因级全局初始条件和激活时间训练 VAE、ODE 参数、缩放和网络。第二阶段可选，默认开启：根据第一阶段的 $z,t$，在潜空间和较早时间窗口中寻找邻居，为每个细胞构造祖先平均 $(c_0,u_0,s_0)$，然后交替更新初始条件与模型。

这个阶段常被称为 EM refinement，但它不是从完整概率模型严格推导的闭式 E/M 更新；KNN 祖先窗口、最少邻居、重复次数和阈值都是算法选择。它的作用是让分支上的细胞从局部祖先出发，而不是所有细胞共享一条相轨迹。

参数初始化也很重要。代码先用相图、稳态估计、聚类、双峰和椭圆拟合等启发式推断速率与基因模式，再进入梯度训练。旧文档把 BasisVAE 的模式分配完全描述为 collapsed variational inference 会遗漏这一强初始化依赖。

### 5. BasisVAE 与多分支/MURK 基因

普通单轨迹模型可能无法表示同一基因在不同分支上诱导、抑制或出现 transcriptional boost。BasisVAE 为基因提供若干动力学 basis：RNA-only 情况对应诱导/抑制，多组学模式组合染色质目标和转录目标的开/关状态。collapsed Dirichlet 项对 basis 权重做边缘化，训练后获得基因的模式概率。

这提高了表达复杂相图的能力，但 `four_basis=False` 是默认值。只有显式启用 BasisVAE 才使用该机制；不能把论文展示的 BasisVAE 能力视为所有默认 MultiVeloVAE 运行都具备。模式结果也受初始化启发式和先验浓度影响，不是由数据唯一决定。

### 6. 从模型状态到 velocity 图

模型在每个细胞计算 $v_c,v_u,v_s$ 后，通常调用 scVelo 的 velocity graph，将基因空间导数与邻居细胞表达差的方向比较，再投影到 UMAP。箭头因此同时依赖：模型导数、velocity gene 筛选、邻居图和二维 embedding。

代码的 velocity gene 并非只按 likelihood：还要求预处理得到的 `quantile_genes`，并使用随 RNA-only、多组学和 batch 模式变化的阈值（`velocity_chrom.py:216-228`）。所以图上箭头是筛选后基因集合的结果，阈值变化可能改变局部方向。

论文提出 GCBDir 等指标评估跨边界方向。它们基于已知 cell type、邻居与随机游走基线，适合比较方向一致性，但不是细胞真实谱系的直接准确率。

### 7. 连续 priming、coupling 与 decoupling

由于 $k_c$ 和 $\rho$ 都在 $[0,1]$，论文定义

$$
\delta=k_c-\rho,
\qquad
\kappa=k_c+\rho-1.
$$

$\delta>0$ 表示染色质目标状态领先转录活性，可解释为 priming/decoupling；$\delta<0$ 表示转录相对领先。$\kappa>0$ 接近共同诱导，$\kappa<0$ 接近共同抑制。这是对模型潜在调控状态的摘要，不是直接测得的染色质因果先于转录；其可信度取决于 ODE 可识别性、平滑 counts 和 ATAC—gene 配对。

### 8. 差异动力学检验

`differential_dynamics()` 从两组细胞的 $q(z,t)$ 反复采样，经 decoder 生成 $k_c,\rho$、表达和 velocity，比较两组差值或变化幅度，并用 posterior probability、Bayes factor 和预期 FDP 排序。时间趋势模式把生成细胞分成 50 个潜时间分位箱，计算箱均值，再用 Gaussian process 与常数零/一基线做似然比检验。

这一流程能比较 velocity、转录率、染色质状态和 coupling，但有几条边界：

- 默认 full VB 关闭，ODE 参数的不确定性没有全部传播。
- GP 默认 RBF+WhiteKernel 是代码选择，论文未完整指定 kernel 超参数。
- 潜时间箱中的点来自模型 posterior predictive，不是新的独立实验细胞。
- batch 与待比较条件重叠时，采样会尽量同 batch 配对；完全混杂时仍不能消除不可识别性。

### 9. 论文图证据怎么读

- 图 1 给出 ODE、VAE、共享时间、多样本与部分模态的总框架。
- 图 2 是 RNA-only benchmark，并展示 BasisVAE 对复杂/MURK 相图的用途；它不能证明所有默认配置都使用四 basis。
- 图 3 比较 multiome velocity 和 MultiVelo，重点是连续 $k_c,\rho$、多分支以及 GPU 训练。
- 图 4 检查两个 HSPC 样本的整合与联合 velocity；batch removal 和 biological conservation 是不同指标，不能只看 UMAP 混合。
- 图 5 用 macrophage 数据将连续 coupling/decoupling 与 SCENIC+ 网络联系。网络关联与模型状态共同提出机制候选，不等于直接调控验证。
- 图 6 展示 macrophage 与 DC 的时间分辨差异动力学，串联 $k_c\rightarrow\rho\rightarrow velocity\rightarrow expression$ 的相对变化。
- 图 7 将两个 multiome HSPC 与一个 RNA-only BMMC 联合，并展示外部 CellOracle perturbation 分析。核心包不包含完整 perturbation/SCENIC+ 管线，因此这部分不是仅安装包即可复现。

### 10. 代码对应和复现范围

当前本地代码直接覆盖 ODE 闭式解、VAE/cVAE、BasisVAE、两阶段训练、velocity、差异动力学和评价指标；还包含六个论文 notebook、固定包版本和一个小型测试输入。测试验证初始化、完整训练输出和差异检验，但 `test_VAEChrom` 硬编码 `cuda:0`，当前环境未据此重跑完整测试。

需要保留的实现边界是：

- 正式论文来源只有本地 PDF，没有转换后的 `paper.md` 或补充材料。
- full VB 与 four-basis 默认关闭，论文的扩展能力需要显式配置。
- 基因模式、速度基因和初始条件均包含重要启发式筛选。
- chromatin scaling 使用 99.5% 分位而非严格 min-max。
- in silico perturbation、CellOracle 和 SCENIC+ 不在核心包中。
- 论文数据依赖 GEO/dbGaP/Figshare；本工作区没有端到端重跑全部主图。

因此，MultiVeloVAE 的核心论文—代码对应度较高，但应把“模型支持某能力”“默认配置启用该能力”和“论文全部分析可由核心包独立复现”三件事分开陈述。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Inferring differential dynamics with MultiVeloVAE

### Paper Information

- **Title**: Inferring differential dynamics from multi-lineage, multi-omic, and multi-sample single-cell data with MultiVeloVAE
- **Authors**: Chen Li, Yichen Gu, Maria C. Virgilio, Kun H. Lee, Kathleen L. Collins & Joshua D. Welch
- **Affiliation**: University of Michigan (Departments of Computational Medicine & Bioinformatics, ECE, CS, Microbiology & Immunology, Internal Medicine)
- **Journal**: Nature Communications (2025)
- **DOI**: 10.1038/s41467-025-66287-6
- **Code**: https://github.com/welch-lab/MultiVeloVAE (BSD-3-Clause license, also on PyPI)
- **Data**: GEO GSE284047 (raw), Figshare 10.6084/m9.figshare.30280333 (processed AnnData)

### Motivation & Novelty

#### Biological Problem

RNA velocity uses the ratio of unspliced (nascent) to spliced (mature) RNA to infer the direction and magnitude of transcriptional changes, providing a snapshot-to-dynamics approach for single-cell data. Existing methods face four critical limitations:

1. **Linear trajectory assumption**: scVelo (Nature Biotechnology, 2020) and UniTVelo (Nature Communications, 2022) assume cells follow a single induction-repression trajectory per gene with a discrete binary switch, failing to capture multi-lineage bifurcations (e.g., hematopoietic differentiation into erythrocytes vs. granulocytes vs. megakaryocytes).

2. **No multi-sample integration**: Existing velocity methods (scVelo, UniTVelo, DeepVelo, VeloVI, PyroVelocity, cellDancer) cannot jointly analyze multiple samples/conditions. Users must chain integration methods (e.g., Scanorama, Nature Biotechnology, 2019; scVI, Nature Methods, 2018) with velocity inference, accumulating errors and preventing proper batch correction of velocity parameters.

3. **Limited multi-omic modeling**: MultiVelo (Nature Biotechnology, 2023), the predecessor, introduced chromatin-RNA coupling but used discrete "priming" states with a single parameter set for all cells, preventing identification of cell-type-specific regulatory patterns.

4. **No statistical testing**: Deterministic ODE-based methods cannot propagate uncertainty or perform differential testing of velocity parameters between conditions, limiting biological discovery.

#### Unique Contributions

MultiVeloVAE introduces five key innovations that address all four limitations:

1. **VAE framework with mechanistic ODE decoder**: Learns continuous latent cell states $z$ and latent times $t$ with uncertainty quantification through variational inference, while enforcing biochemically interpretable dynamics via analytical ODE solutions.

2. **Continuous cell-specific regulatory parameters**: Replaces discrete induction/repression phases with continuous $k_c(z) \in [0,1]$ (chromatin opening rate) and $\rho(z) \in [0,1]$ (transcription rate) predicted by neural networks from cell state $z$, enabling cell-type-specific and gene-specific regulation on a shared time scale.

3. **BasisVAE for gene mode clustering**: Models genes as mixtures of ODE basis functions using collapsed variational inference with a Dirichlet prior, automatically assigning genes to induction/repression modes and handling transcriptional boosts (MURK genes).

4. **Conditional VAE for multi-sample integration**: Conditions encoder/decoder on one-hot sample labels, separating biological variation from technical artifacts. Supports sample-specific rate parameters ($\alpha_c, \alpha, \beta, \gamma$), scaling factors, and offsets while sharing latent cell state across samples.

5. **Bayesian differential dynamics testing**: Uses posterior sampling and Bayes factors to identify genes with significantly different velocity, transcription rate, chromatin opening rate, or coupling/decoupling patterns between cell populations, with FDR control and Gaussian process regression for time-varying trends.

### Method Overview

#### Core Architecture

MultiVeloVAE is an encoder-decoder VAE where the decoder uses a system of coupled ODEs:

**Encoder** $q_\phi(z, t | c, u, s, b)$: MLP (FC → BN → LeakyReLU → Dropout(0.2)) mapping concatenated chromatin ($c$), unspliced RNA ($u$), spliced RNA ($s$), and optional batch labels ($b$) to posterior distributions $\mathcal{N}(\mu_z, \sigma_z^2)$ and $\mathcal{N}(\mu_t, \sigma_t^2)$.

**Decoder** $p_\theta(c, u, s | z, t, b)$: Two parallel neural networks predict $k_c(z)$ and $\rho(z)$, then the ODE system is solved analytically:

$$\frac{dc}{dt} = \alpha_c(k_c - c), \quad \frac{du}{dt} = \alpha \rho c - \beta u, \quad \frac{ds}{dt} = \beta u - \gamma s$$

The analytical solutions (Eq. 4–5) are used to generate predictions $(\hat{c}, \hat{u}, \hat{s})$ from $(c_0, u_0, s_0)$ at time $\tau = t - t_0$.

**Training objective**: Maximize the ELBO:
$$\text{ELBO} = \mathbb{E}_{q(z,t|x,b)}[\log p(c|z,t,b) + \log p(u|z,t,b) + \log p(s|z,t,b)] - D_{KL}(q(z,t|x,b) \| p(z,t|b))$$

#### Two-Stage Training

- **Stage 1**: Train full VAE with global initial conditions $(c_0, u_0, s_0)$ per gene, optimizing both encoder and decoder.
- **Stage 2**: Freeze encoder; use EM algorithm to refine cell-specific initial conditions by averaging ancestor cells in a time window $[t - \delta_1, t - \delta_2]$, then optimize ODE parameters.

#### Coupling and Decoupling Factors (Eq. 21)

$$\delta := k_c - \rho \quad \text{(decoupling factor, range [-1,1])}$$
$$\kappa := k_c + \rho - 1 \quad \text{(coupling factor, range [-1,1])}$$

These generalize MultiVelo's discrete states to continuous, cell-specific quantities.

#### GCBDir Metric (Eq. 17–20)

Extends Cross-Boundary Direction correctness (CBDir) to: (1) k-step neighbors instead of direct neighbors, (2) time-ordering with sign penalty, and (3) subtraction of a random-walk baseline.

### Evaluation

#### Datasets

| Dataset | Cells | Genes | Modalities | Source |
|---------|-------|-------|------------|--------|
| 10 scRNA-seq benchmarks | 500–34k | Variable | RNA only | Published (Pancreas, BMMC, Brain, etc.) |
| Mouse brain 10X Multiome | ~5,000 | Variable | RNA + ATAC | La Manno et al. (Nature, 2021) |
| Human brain Multiome | ~10,000 | Variable | RNA + ATAC | Trevino et al. (Cell, 2021) |
| SHARE-seq mouse skin | ~34,000 | Variable | RNA + ATAC | Ma et al. (Cell, 2020) |
| **Embryoid body (new)** | 4,240 | 3,138 | RNA + ATAC | This study |
| **HSPC integration (new)** | 17,667 | 892 | RNA + ATAC | This study (2 donors) |
| **HSPC + Macrophage (new)** | 9,908 | 929 | RNA + ATAC | This study |
| **3-sample partial (new)** | 27,841 | 1,044 | RNA + ATAC + RNA-only | This study |

#### Benchmark Methods (with journal and year)

**RNA velocity**: scVelo (Nature Biotechnology, 2020), UniTVelo (Nature Communications, 2022), DeepVelo (Genome Biology, 2024), VeloVI (Nature Methods, 2023), PyroVelocity (bioRxiv, 2022), cellDancer (Nature Biotechnology, 2023)

**Multi-omic velocity**: MultiVelo (Nature Biotechnology, 2023)

**Integration**: Scanorama (Nature Biotechnology, 2019), scVI (Nature Methods, 2018); benchmarked with scIB metrics (Nature Methods, 2022)

**Cross-modality prediction**: scButterfly (Nature Communications, 2024), scCross (Genome Biology, 2024), MultiVI (Nature Methods, 2023)

#### Key Results

1. **RNA-only benchmarks** (Fig. 2f): MultiVeloVAE achieves the highest mean GCBDir and time correlation across 10 datasets. Particularly strong on multi-lineage systems (BMMC, brain).

2. **Multi-omic velocity** (Fig. 3g): Higher k-step CBDir than MultiVelo across 5 datasets in both gene and embedding space. Significantly faster runtime via GPU acceleration.

3. **Multi-sample integration** (Fig. 4d–e): Comparable to Scanorama in batch removal; outperforms scVI in biological conservation (ASW, cLISI).

4. **Differential dynamics** (Fig. 6b–d): Identifies genes with differential velocity between macrophages and DCs, revealing coordinated temporal patterns in $k_c$, $\rho$, velocity, and expression.

5. **Cross-modality prediction** (Supplementary Fig. 19): On par with scButterfly in ATAC prediction from RNA; highest GCBDir when using predicted ATAC for velocity.

6. **In silico perturbation** (Fig. 7e–h): SPI1 KO reverses GMP/DC lineages; GATA1 KO disrupts MEP/erythrocyte lineages — consistent with known biology and CellOracle predictions.

#### Biological Validation

- **GATA2→GATA1 switch**: Coupling factors of GATA1-linked genes increase during erythropoiesis while GATA2-linked genes show chromatin-level repression (Supplementary Fig. 11c).
- **Chromatin priming**: Continuous $\delta$ captures cell-type-specific priming in Wnt3 (mouse skin), correctly separating IRS lineage from true priming cells (Fig. 3f).
- **ChromHMM integration**: Peaks associated with decoupled states enriched in TSS, Promoter, and Bivalent Promoter annotations (Supplementary Fig. 13b).
- **Housekeeping genes**: Maintain positive decoupling status throughout differentiation, as expected (Fig. 5e).

### Reproducibility

#### Rating: 4/5

**Strengths**:
- Complete Python package on PyPI (`pip install multivelovae`) and GitHub
- Comprehensive documentation with tutorials
- New experimental data deposited in GEO (GSE284047)
- Preprocessed AnnData objects shared on Figshare (doi:10.6084/m9.figshare.30280333)
- Zenodo archive of code at publication version (doi:10.5281/zenodo.17268254)

**Potential Blockers**:
- GPU required for practical runtime (developed on RTX 3060 12GB)
- Large memory footprint for >20k cells (may need batch size reduction)
- Preprocessing pipeline requires STARsolo and manual QC parameter tuning
- SCENIC+ integration requires additional dependencies (pycisTopic)

#### Key Dependencies

- Python 3.8+, PyTorch ≥ 1.10, NumPy, SciPy, scikit-learn
- scVelo ≥ 0.2.4, Scanpy, AnnData
- Optional: pycisTopic (SCENIC+), CellRank (fate probabilities)

### Limitations

1. **Computational cost**: Two-stage training with EM is time-intensive for large datasets (>50k cells)
2. **Unspliced RNA quality**: Performance depends on quality of u/s quantification, challenging in mature cell types with low differentiation potential
3. **Sparse ATAC handling**: Binary accessibility may not capture full chromatin dynamics
4. **No pre-trained models**: Every dataset requires de novo training
5. **Hyperparameter sensitivity**: BasisVAE prior weights and number of gene clusters (default 7) require tuning

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
