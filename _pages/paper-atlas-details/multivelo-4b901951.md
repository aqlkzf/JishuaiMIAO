---
layout: default
permalink: /paper-atlas/multivelo-4b901951/
title: "MultiVelo"
nav: false
description: "MultiVelo 对每个基因分别拟合一条三维轨迹 (c,u,s)：c 是聚合到基因的染色质可及性，u 是未剪接 RNA，s 是已剪接 RNA。它先估计染色质与转录何时开关、各反应速率多快，再把每个细胞投影到该轨迹上的最近位置；ODE 在该位置的导数就是该细胞—基因的多组学 velocity。 这种时间与速度来自横截面细胞群的模型推断，不是同一细胞的纵向实测，也不是对所有基因共同拟合一个统一生物钟。"
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
      <span>Nature Biotechnology · 2023</span>
    </div>
    <h1>MultiVelo</h1>
    <p>Multi-omic single-cell velocity models epigenome-transcriptome interactions and improves cell fate prediction</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-022-01476-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MultiVelo：把染色质开放、未剪接 RNA 和已剪接 RNA 放进同一条动力学轨迹

### 一句话理解

MultiVelo 对每个基因分别拟合一条三维轨迹 $(c,u,s)$：$c$ 是聚合到基因的染色质可及性，$u$ 是未剪接 RNA，$s$ 是已剪接 RNA。它先估计染色质与转录何时开关、各反应速率多快，再把每个细胞投影到该轨迹上的最近位置；ODE 在该位置的导数就是该细胞—基因的多组学 velocity。

这种时间与速度来自横截面细胞群的模型推断，不是同一细胞的纵向实测，也不是对所有基因共同拟合一个统一生物钟。

### 1. 为什么 RNA velocity 还需要染色质

经典动态 RNA velocity 使用

$$
\frac{du}{dt}=\alpha^{(k)}-\beta u,
\qquad
\frac{ds}{dt}=\beta u-\gamma s.
$$

它能用 $u$ 与 $s$ 的相对位置判断表达正在上升还是下降，但 induction 阶段通常把转录输入看成常数。MultiVelo 增加可及性 $c(t)$，并让实际转录输入随它变化：

$$
\frac{dc}{dt}=k_c\alpha_c-\alpha_c c,
$$

$$
\frac{du}{dt}=\alpha^{(k)}c-\beta u,
$$

$$
\frac{ds}{dt}=\beta u-\gamma s.
$$

其中 $k_c=1$ 时 $c$ 指数趋向 1，$k_c=0$ 时指数趋向 0；转录开启时 $\alpha^{(k)}=\alpha$，关闭时为 0。于是“染色质开了多少”成为转录速率的一部分，而不仅是用于画图的附加特征。

当前代码进一步用 `scale_cc` 允许关闭速率为 opening rate 的倍数，即 $\alpha_{cc}=\mathrm{scale}_{cc}\alpha_{co}$；输出仍以 `fit_alpha_c` 和 `fit_scale_cc` 保存。

### 2. 三个开关时间如何形成四个状态

完整轨迹包含三个事件：染色质开放后，转录开始；随后染色质开始关闭与转录开始抑制，后二者的先后次序决定模型类型。

- Model 1：染色质先关闭，转录后停止。
- Model 2：转录先停止，染色质后关闭。

把三个 switch time 排序后，轨迹被切成四段：

1. primed：染色质正在打开，但转录尚未启动；
2. coupled-on：染色质开放且转录开启；
3. decoupled：染色质关闭与转录停止不同步；
4. coupled-off：两者均进入关闭/抑制状态。

“decoupled”在 M1 中表示染色质已开始关闭但转录仍开，在 M2 中则表示转录已停而染色质仍较开放。因此同一个状态名对应两种相反的事件次序，解释单个基因时必须同时查看 `fit_model`。

### 3. 观测数据如何进入模型

RNA AnnData 需要经 scVelo 邻域平滑得到 `Mu`、`Ms`；ATAC 侧先把 promoter 与相关 enhancer peaks 聚合到基因，做 TF–IDF 归一化，再用跨模态邻居平滑得到 `Mc`。动态入口 `recover_dynamics_chrom()` 要求 RNA 与 ATAC 的细胞、基因严格对齐。

这些预处理不是可忽略的装饰。单细胞 ATAC 很稀疏，若不做 peak-to-gene 聚合、归一化与邻域平滑，$c$ 的轨迹形状可能主要反映 dropout。论文主分析用 Seurat WNN；包内也提供 `pyWNN.py`，但两条邻居构建路径不能默认视为数值完全相同。

### 4. 单基因拟合的真实步骤

#### 4.1 先缩小搜索空间

`ChromatinDynamical` 会过滤全零/极端值细胞，缩放三种模态，并用 GMM、稳态斜率和 peak chromatin 位于 RNA 相图哪一支等启发式判断该基因是 induction-only、repression-only 还是完整轨迹，以及优先尝试 M1 或 M2。这是预判搜索空间，不是最终的生物学分类证据。

#### 4.2 用解析解生成候选轨迹

每一阶段的线性 ODE 有闭式解；`predict_exp()` 计算一段，`generate_exp()` 按开关时间拼成完整 $(c,u,s)$ 曲线。代码把标准总时间固定在 0–20 的内部尺度，真实实验小时不能直接从这个数字读取。

#### 4.3 把细胞投影到 anchor

`anchor_points()` 按开关时间把 0–20 切成四段。动态 API 默认 `n_anchors=500`，类内部限制到 201–2000。`calculate_dist_and_time()` 在经过 `scale_factor` 加权的三维空间为理论轨迹建 KD-tree，再为每个观测细胞寻找最近 anchor；最近点所在阶段成为 state，anchor 时间成为 gene-specific latent time。

因此时间赋值不是解析反解，也不是在 UMAP 上按距离排序。它依赖候选参数、模态缩放、邻域平滑和离散 anchor 密度。

#### 4.4 交替更新时间与参数

论文把过程描述为 expectation–maximization：给定参数更新细胞时间，给定时间更新参数。代码的默认实现是分块 Nelder–Mead 优化（`dynamical_chrom_func.py:2844-2992`），依次调整 switch times、$\alpha_c$、模态缩放、$\alpha$、$\beta$、$\gamma$，并反复重新投影细胞。它更准确地说是带有硬最近点赋值的交替优化，而不是计算完整 posterior responsibility 的软 EM。

可选 `adam` 或 neural-network time assignment 是后续工程扩展；默认论文式路径仍是解析轨迹、KD-tree 与 Nelder–Mead。

#### 4.5 模型比较与拟合质量

外层 `multimodel_helper()` 可分别拟合候选模型并选 loss 更低者。最终 `compute_likelihood()` 计算拟合后 likelihood，用于筛 velocity genes；likelihood 不是默认参数优化时直接最大化的唯一目标。当前 API 默认以 `fit_likelihood >= 0.05` 初筛速度基因，还可通过 `set_velocity_genes()` 叠加速率、switch interval 与 R² 等条件。

### 5. velocity 到底怎么算

给定某个细胞在某个基因的拟合时间、状态与参数，直接代回三条 ODE：

$$
v_c=k_c\alpha_c-\alpha_c c,
\quad
v_u=\alpha^{(k)}c-\beta u,
\quad
v_s=\beta u-\gamma s.
$$

代码把它们写入 `velo_chrom`、`velo_u`、`velo_s` layers（`dynamical_chrom_func.py:4936-5090`）。这些值先在基因维度描述瞬时变化；随后 `velocity_graph()` 调用 scVelo，以细胞间表达差向量和 velocity 的 cosine similarity 构建转移图，`velocity_embedding_stream()` 才把转移方向投影成 UMAP streamlines。

所以 Figure 2 等图上的箭头不是三维 ODE 轨迹本身，而是许多 gene-wise spliced velocities 经邻域图汇总后的低维可视化。

### 6. gene-specific time 与全局 latent time

每个基因独立拟合，`fit_t` 中同一细胞对不同基因可有不同时间。下游 `latent_time()` 使用 velocity graph、root/end information 与基因时间的共享结构生成一个全局进程轴。全局 latent time 适合排序细胞群，但不是绝对实验时间，也不能解释为所有基因严格同步。

### 7. 主图如何读

Figure 1 是机制图：M1/M2 只由“chromatin closing”和“transcription repression”谁先发生决定；红色 primed 与绿色 decoupled 是两种不同来源的跨模态不同步。

Figure 2 的 mouse brain 结果首先展示 MultiVelo 与 RNA-only scVelo 的群体流场差异，然后用基因相图说明 chromatin 能区分在 $u$–$s$ 原点附近难以排序的细胞。论文报告的动力学类型比例是在所分析的变量基因中计算：induction 29.5%、M1 41.4%、M2 26.7%、repression 2.4%。这些比例是数据集结果，不是算法固定先验。

Figure 3 把每个基因的四状态映射回细胞 UMAP，并统计 switch intervals；它表达的是 cell–gene state，不能把一张“primed gene count”图读成单一细胞命运标签。

Figures 4–6 在 skin、HSPC 和 fetal cortex 上展示分支方向、基因动态和 TF/motif 或 SNP/gene 的时间滞后。DTW 分析属于 ODE 拟合之后的论文下游分析，其中 R 脚本位于 `Examples/dtw_example.R`，不是 `recover_dynamics_chrom()` 的核心拟合步骤。

### 8. 随机/稳态分支不是动态模型的同义词

`steady_chrom_func.py` 的 `velocity_chrom()` 提供 deterministic/stochastic steady-state 分支。它用一阶或二阶矩估计 $u$–$s$ 稳态斜率，spliced velocity 本质上是对拟合稳态线的 residual。该分支不执行完整 switch-time/latent-time 动态恢复；调用 `mode='dynamical'` 反而会提示用户无需在这里运行动态模型。

因此论文的 stochastic moment model 与主三 ODE 动态模型应分开理解：前者用于稳态参数/速度估计，后者才产生四阶段、switch times 和 gene-specific time。

### 9. 当前源码与论文叙述的实现边界

- 论文用 $\alpha_{co}$、$\alpha_{cc}$；代码用 `alpha_c × scale_cc` 表示关闭速率。
- 论文称 EM；默认代码是最近-anchor 硬赋值加分块 Nelder–Mead 的交替优化。
- 模型预判使用启发式规则，最终模型选择由外层候选拟合比较完成。
- `compute_likelihood()` 是拟合后评分；主优化目标包含到解析轨迹的加权距离及 penalty。
- WNN、peak linkage、RNA/ATAC smoothing 的选择直接影响输入，包内实现不等于论文所有 R/Seurat 处理的逐位复现。
- 当前工作区是 MultiVelo 0.1.5 源码快照，位于 workspace 根目录的 `src/multivelo/`，并非 `Examples/`。

### 10. 一个小例子

假设两个细胞的 $u$ 和 $s$ 都很低，RNA-only 相图会把它们挤在原点附近。若细胞 A 的 $c$ 也低，而细胞 B 的 $c$ 已升高，MultiVelo 可把 A 放在轨迹起点，把 B 放在 primed 阶段。两者当前 RNA 相似，却对下一步转录启动有不同预测。这个例子说明增加 $c$ 的价值是拆开 RNA 相图中重叠的时间状态，而不是简单地把 ATAC 当作第三个聚类特征。

### 证据入口

- 论文：`paper source/Li et al. - 2023 - Multi-omic single-cell velocity models epigenome–transcriptome interactions and improves cell fate p/Li et al. - 2023 - Multi-omic single-cell velocity models epigenome–transcriptome interactions and improves cell fate p.md`。
- 主图：同目录下 `_page_*_Figure_2.jpeg`。
- 动态模型：`src/multivelo/dynamical_chrom_func.py`。
- 稳态/随机矩模型：`src/multivelo/steady_chrom_func.py`。
- ATAC/WNN 辅助：`src/multivelo/auxiliary.py`、`src/multivelo/pyWNN.py`。
- 包版本：`setup.cfg`，0.1.5。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MultiVelo: Multi-omic Single-Cell Velocity Models Epigenome–Transcriptome Interactions

**Paper**: Li C, Virgilio MC, Collins KL, Welch JD. *Nature Biotechnology* 41, 387–398 (2023).
**DOI**: [10.1038/s41587-022-01476-y](https://doi.org/10.1038/s41587-022-01476-y)
**Code**: [https://github.com/welch-lab/MultiVelo](https://github.com/welch-lab/MultiVelo) (Python, PyPI, Bioconda)

---

### Motivation & Novelty

#### Biological Problem

During cellular differentiation, chromatin accessibility (epigenome) and gene expression (transcriptome) change in a temporally coordinated but imperfectly synchronized manner. Chromatin remodeling at promoters and enhancers can precede or follow transcriptional changes, creating biologically meaningful time lags. Existing methods could not jointly model these two molecular layers from the same cell:

- **RNA velocity** (La Manno et al., *Nature*, 2018; Bergen et al., *Nature Biotechnology*, 2020) models only unspliced→spliced RNA dynamics, assuming constant transcription rate during induction — ignoring chromatin's influence on transcription rate.
- **Chromatin potential** (Ma et al., *Cell*, 2020) quantified epigenomic priming but did not incorporate gene expression into a mechanistic ODE model.
- **Chromatin velocity** (Tedesco et al., *Nature Biotechnology*, 2021) inferred future cell states from epigenomic data alone without integrating expression.
- **Protein velocity** (Gorin et al., *Genome Biology*, 2020) extended RNA velocity to protein but used steady-state assumptions without latent time estimation.

#### Unique Contributions

1. **Three-ODE dynamical model**: Extends RNA velocity by adding a chromatin accessibility ODE ($c \to u \to s$), making transcription rate time-varying and proportional to chromatin accessibility $c(t)$.
2. **Two biologically distinct gene regulation models**: Model 1 — chromatin closes before transcription represses ("delayed transcriptional repression"); Model 2 — transcription represses before chromatin closes ("delayed chromatin repression").
3. **Four cell state classification**: Each cell–gene pair is assigned to one of four states — primed, coupled-on, decoupled, coupled-off — quantifying epigenome–transcriptome concordance/discordance.
4. **Analytical ODE solutions**: Closed-form solutions for all three variables across all states enable efficient EM-based parameter estimation with Nelder-Mead optimization.
5. **Stochastic model variant**: Models chromatin "breathing" (binary open/closed switching) as a Markov process, deriving moment equations for steady-state parameter estimation.

---

### Method Overview

#### Algorithmic Framework

MultiVelo models the temporal dynamics of chromatin accessibility ($c$), unspliced pre-mRNA ($u$), and spliced mRNA ($s$) as a system of three ODEs:

$$\frac{dc}{dt} = k_c \alpha_c - \alpha_c c(t), \quad \frac{du}{dt} = \alpha^{(k)} c(t) - \beta u(t), \quad \frac{ds}{dt} = \beta u(t) - \gamma s(t)$$

where $k_c \in \{0, 1\}$ indicates chromatin opening/closing state, $k \in \{0, 1\}$ indicates transcription on/off, and the five rate parameters ($\alpha_{co}$, $\alpha_{cc}$, $\alpha$, $\beta$, $\gamma$) plus three switch times ($t_i$, $t_c$, $t_r$) are estimated per gene. The analytical solution allows the model to describe four sequential phases per gene, and the code fits separate chromatin opening ($\alpha_{co}$) and closing ($\alpha_{cc}$) rates despite the paper's simplified notation using a single $\alpha_c$.

#### Key Technical Components

| Component | Description |
|-----------|-------------|
| **Model predetermination** | Classifies genes as induction-only, repression-only, Model 1, or Model 2 using GMM bimodality test + steady-state slope ratio + peak chromatin position relative to the RNA phase portrait |
| **Parameter initialization** | Grid search over switch time combinations; RNA rates from steady-state regression ($\gamma$ from top-percentile u/s slope, $\alpha$ from mean top-percentile u, $\beta = 1$); chromatin rate from $\alpha_c = -\log(1-c_{high})/t_{cc}$ |
| **EM optimization** | Block coordinate descent via Nelder-Mead simplex (6 stages): (1) chromatin switch + $\alpha_c$, (2) scale factors, (3) RNA switch + $\alpha$, (4) $\beta$ + rescale_u, (5) $\alpha$ + $\gamma$, (6) all three switch times |
| **Time assignment** | KD-tree nearest-neighbor search from 500 uniformly spaced anchor points along the ODE-predicted trajectory in $(c, u, s)$ space |
| **Velocity computation** | Plugs fitted parameters + neighborhood-smoothed cell times back into ODEs to get $dc/dt$, $du/dt$, $ds/dt$ per cell |
| **Downstream integration** | Velocity normalization → cosine-similarity transition graph → stream embedding via scVelo |

#### Biological Assumptions

- Chromatin accessibility at a locus is a single value $c \in [0, 1]$, aggregated from promoter + linked enhancer peaks.
- Transcription rate is proportional to $c(t)$, abstracting complex TF/cofactor interactions into rate constants.
- Each gene independently follows one of two orderings (M1 or M2), determined by relative timing of chromatin closing and transcriptional repression.
- Chromatin opening/closing are modeled as exponential approach to full accessibility (1) or inaccessibility (0).
- Cells are measured at a single time point (snapshot), and the observed population spans the full dynamical trajectory.

---

### Evaluation

#### Datasets

| Dataset | Species | Technology | Cells | Genes | Source |
|---------|---------|-----------|-------|-------|--------|
| Embryonic mouse brain (E18) | Mouse | 10x Multiome | 3,365 | 936 | 10x Genomics |
| Mouse hair follicle (skin) | Mouse | SHARE-seq | 6,436 | 962 | GEO:GSE140203 |
| Human HSPCs (day 0) | Human | 10x Multiome | 11,605 | 1,000 | GEO:GSE209878 |
| Fetal human cortex | Human | 10x Multiome | 4,693 | 919 | GEO:GSE162170 |
| Simulated data | — | — | 2,000 | 500–1,000 | Generated |

#### Metrics & Comparative Results

| Comparison | MultiVelo | scVelo (Bergen et al., *Nat. Biotechnol.*, 2020) |
|------------|-----------|------|
| Mouse brain velocity direction | Correct differentiation trajectory (RG → neurons) | Biologically implausible backflows in upper-layer neurons |
| Mouse skin differentiation | Correct TAC → IRS/hair shaft direction | Failed to capture hair-shaft differentiation direction |
| HSPC velocity consistency | Improved local consistency for hematopoietic hierarchy | Inaccurate direction in early progenitors |
| Latent time vs Palantir pseudotime (Setty et al., *Nat. Biotechnol.*, 2019) | Spearman ρ = 0.51 (skin) | Spearman ρ = 0.44 |
| Simulation model recovery | 985/1,000 correct model assignments | N/A |
| Simulation parameter estimation | Accurate recovery of rate parameters and switch times under noise | N/A |

#### Key Biological Findings

1. **Model 1 vs Model 2 distribution**: Model 1 (delayed transcriptional repression) is more common across all datasets (41.4% vs 26.7% in mouse brain). Model 2 genes are enriched for cell cycle terms (mitotic cell cycle, cell cycle phase transition).
2. **Priming and decoupling intervals**: Median priming = 21% of gene expression cycle; median decoupling = 19%. Coupled states dominate, consistent with expected chromatin–expression correlation.
3. **TF expression → binding site accessibility**: Dynamic time warping shows TF expression precedes motif accessibility, with median positive time lag across all expressed TFs in human brain.
4. **Disease SNP grouping**: Three distinct groups of psychiatric disease-associated SNPs distinguished by timing of maximum accessibility relative to linked gene expression.
5. **Chromatin opening ≈ closing rates**: Median ratio $\alpha_{cc}/\alpha_{co} \approx 1$ across genes.
6. **GO enrichment differences**: M1 genes enriched for neuronal/developmental terms; M2 genes enriched for cell cycle (mitotic cell cycle, cell cycle phase transition) and histone-related terms.
7. **Histone mark distinction**: M1 genes have significantly higher H3K4me3 peaks than M2 genes in HSPCs (Wilcoxon p = 0.016), suggesting epigenetic differences between the two regulatory models.

#### Biological Validation

- Cell cycle scores confirm MultiVelo's latent time places cycling populations at the root (mouse brain).
- Known marker genes (*Eomes* for IPCs, *Tle4* for deep-layer neurons) show expected priming patterns.
- DTW-based TF–target time lags are validated against known TF targets from ChIP-seq literature (*EGR1*, *EOMES*, *FOXP2*, *PBX3*).

---

### Reproducibility

#### Rating: 4/5

#### Strengths
- Complete Python package on PyPI and Bioconda with documented API
- Tutorials and example notebooks on ReadTheDocs
- All four biological datasets publicly available with accession numbers
- Core algorithm is deterministic (seeds specified for auxiliary functions)
- Numba JIT compilation for performance-critical functions
- Optional neural network-based time assignment with pre-trained models included in package
- Parallel gene fitting via joblib

#### Runtime & Memory (from Paper)

| Dataset | Cells | Runtime (parallel) | Peak Memory | Memory Increment |
|---------|-------|-------------------|-------------|------------------|
| Mouse brain | 3,365 | 40 min | 857 MiB | 481.5 MiB |
| Mouse skin | 6,436 | 69 min | 1,602 MiB | 1,136.5 MiB |
| Human HSPCs | 11,605 | 124 min | 2,921 MiB | 2,293.2 MiB |
| Human brain | 4,693 | 40 min | 1,100 MiB | 660.6 MiB |

Hardware: Intel Core i7-9750H (12 threads), 32 GB RAM.

#### Limitations
- **Multi-tool preprocessing pipeline**: Requires coordinated processing of RNA (Velocyto + scVelo) and ATAC (peak aggregation + TF-IDF normalization + WNN smoothing via Seurat in R), spanning Python and R ecosystems.
- **WNN dependency**: Weighted nearest neighbor computation requires Seurat v4 in R. The package includes a Python reimplementation (`pyWNN.py`) but the paper's analyses use Seurat.
- **Runtime**: 40–124 minutes per dataset on a 12-thread CPU; scales with cell count and gene count. Downsampling cells or reducing anchors can reduce runtime.
- **Feature linkage files**: Required for peak-to-gene aggregation (from CellRanger ARC or manual annotation); not standardized across technologies (10x Multiome vs SHARE-seq require different pipelines).
- **Unpaired data support**: For separately sequenced RNA and ATAC, the paper uses Seurat's anchor transfer (FindTransferAnchors + TransferData) to impute matching ATAC for RNA cells. This workflow is not automated in the package.
- **SHARE-seq data access**: BAM files and UMAP coordinates required direct author contact — not fully available from public repositories.
- **Stochastic model**: Less thoroughly validated than the dynamical model; limited to steady-state analysis without latent time estimation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
