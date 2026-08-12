---
layout: default
permalink: /paper-atlas/velocycle-96ecb319/
title: "VeloCycle"
nav: false
description: "这篇 Nature Methods 论文提出 VeloCycle，用单细胞 RNA-seq 中未剪接和已剪接 RNA 的计数，在细胞周期这一 1D 周期流形上估计细胞周期速度。传统 Seurat/scanpy 细胞周期打分通常给出 G1、S、G2/M 这类离散标签，不能直接回答“这个条件下细胞周期是不是更快、在哪个阶段变慢、差异是否可信”。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>VeloCycle</h1>
    <p>Statistical inference with a manifold-constrained RNA velocity model uncovers cell cycle speed modulations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02471-8" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeloCycle 方法中文解读

### 论文解决的问题

这篇 Nature Methods 论文提出 VeloCycle，用单细胞 RNA-seq 中未剪接和已剪接 RNA 的计数，在细胞周期这一 1D 周期流形上估计细胞周期速度。传统 Seurat/scanpy 细胞周期打分通常给出 G1、S、G2/M 这类离散标签，不能直接回答“这个条件下细胞周期是不是更快、在哪个阶段变慢、差异是否可信”。普通 RNA velocity 方法虽然利用 unspliced/spliced 延迟，但常把每个基因独立建模，并依赖邻域平滑，得到的速度场不一定沿着真实表达流形运动，也缺少可用于条件比较的可信区间。

### 核心思想

VeloCycle 把细胞周期表示为圆环 $S^1$ 上的相位 $\varphi \in [0,2\pi)$。每个基因的已剪接表达沿圆环用 Fourier 基函数拟合，所有基因共享同一个角速度函数 $\omega(\varphi)$。这样，RNA velocity 不再是每个基因各自独立的速度，而是由同一个流形速度通过链式法则约束出来的切向速度。

计算流程分两步：

```text
raw spliced/unspliced UMI counts
        |
        v
1. Manifold learning
   infer cell phase phi and gene Fourier coefficients nu from spliced counts
        |
        v
2. Velocity learning
   condition on phi and nu, infer beta, gamma, and angular speed omega from unspliced counts
        |
        v
posterior samples of cell-cycle speed, period, and condition differences
```

第一步使用已剪接计数学习相位和基因表达的周期曲线。论文方法部分说明，模型把每个细胞的相位和每个基因的 Fourier 系数作为潜变量，并用负二项分布直接拟合原始计数。第二步在第一步相位和曲线的基础上，用一阶 RNA 动力学方程约束未剪接计数的期望。关键公式是：已剪接表达曲线对相位的导数乘以角速度，再加上降解项 $\gamma_g$，共同决定未剪接表达的期望。代码中对应实现位于 `velocycle/velocity_inference_model.py:344-368`。

### 概率模型与推断

VeloCycle 使用 Pyro 的 SVI 和 ELBO 目标进行变分推断。论文说明通常对 manifold learning 训练 5,000 步，对 velocity learning 训练 10,000 步，并用 ClippedAdam 优化器；代码中的训练循环和早停逻辑位于 `velocycle/velocity_inference_model.py:111-151`。后验不只输出点估计，而是通过 500 次 posterior predictive sample 得到 5th-95th percentile 的可信区间，论文方法中也明确用 500 posterior samples 计算速度和周期的不确定性。

论文的一个重要改进是 LRMN 变分分布。普通 mean-field SVI 会低估速度不确定性，因为降解率 $\log\gamma_g$ 和角速度 $\nu\omega$ 的后验不确定性相关。论文用 MCMC 观察到这种相关结构后，引入 Low-Rank Multivariate Normal 近似，让 $\log\gamma_g$ 和 $\nu\omega$ 联合建模，并让 $\log\beta_g$ 条件依赖 $\log\gamma_g$。代码实现位于 `velocycle/velocity_inference_guide.py:65-140`。

### 结果与验证

模拟数据中，VeloCycle 能恢复细胞周期相位和速度，并在混入一定比例非周期细胞时仍保持可用。真实数据中，FUCCI/FACS mES 细胞验证了相位估计；RPE1 两个重复样本验证了未剪接-已剪接延迟携带速度信息；dHF 和 RPE1 活细胞成像验证了速度换算出的周期时间。论文报告 dHF 中 VeloCycle 估计周期为 15.3 ± 1.2 h，活细胞成像中位数为 15.8 h；RPE1 中 VeloCycle、活细胞成像和 EdU 标记得到的周期也一致。

在应用层面，VeloCycle 检测到 erlotinib 处理后 PC9 细胞在 G2/M 附近速度降低；小鼠胚胎脑径向胶质细胞在 E10 呈现 hindbrain > midbrain > forebrain 的细胞周期速度梯度；Perturb-seq 中 MCM6、EIF3B 等 knockdown 显著降低细胞周期速度，DBR1 等 RNA 处理相关扰动也会强烈影响估计。

### 代码对应关系与注意点

公开代码与论文主模型匹配度较高：`phase_inference_model.py` 实现相位学习，`velocity_inference_model.py` 实现速度学习，`velocity_inference_guide.py` 实现 mean-field 与 LRMN guide，`preprocessing.py` 构建计数、gene set、design matrix 和 metaparameter。核心公式、负二项似然、posterior sampling、Fourier basis 和 transfer learning 都能在代码中定位。

也有几个复现时需要注意的差异。代码在 `preprocessing.py:152-153` 加入了 library-size `count_factor`，这是实际运行的重要偏移项，但主公式中没有显式写出。负二项 dispersion 在模型里有 Gamma prior，但 guide 中用 Delta 点估计，见 `velocity_inference_guide.py:55-56` 和 `velocity_inference_guide.py:115-116`。Fourier basis 的顺序在代码里是 `[1, sin, cos, ...]`，而论文符号写法偏向 `[1, cos, sin, ...]`；二者张成空间等价，但变量逐项对照时需要交换符号解释。

总体上，VeloCycle 的贡献是把细胞周期 RNA velocity 从启发式向量场推进到“流形约束 + 计数噪声模型 + 后验不确定性”的统计推断框架，使 snapshot scRNA-seq 可以用于比较条件、组织区域或扰动下的细胞周期速度差异。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeloCycle: Manifold-Constrained Bayesian RNA Velocity for Cell Cycle Analysis

### Reference

**Paper**: Lederer, A.R., Leonardi, M., Talamanca, L., Bobrovskiy, D.M., Herrera, A., Droin, C., Khven, I., Carvalho, H.J.F., Valente, A., Dominguez Mantes, A., Mulet Arabi, P., Pinello, L., Naef, F., & La Manno, G. (2024). Statistical inference with a manifold-constrained RNA velocity model uncovers cell cycle speed modulations. *Nature Methods*, 31 October 2024.

**DOI**: [10.1038/s41592-024-02471-8](https://doi.org/10.1038/s41592-024-02471-8)

**GitHub**: [lamanno-epfl/velocycle](https://github.com/lamanno-epfl/velocycle)

**Category**: dynamics_fate_trajectory

---

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing (scRNA-seq) captures static snapshots — yet biological processes like the cell cycle are fundamentally dynamic. The cell cycle is the most pervasive periodic process in biology and is central to cancer, development, and tissue homeostasis. Despite its ubiquity in scRNA-seq data, standard analysis pipelines (Seurat, scanpy) reduce the continuous process to three categorical phases (G1/S/G2M) using a small curated set of ~100 marker genes — discarding quantitative, temporal information entirely.

#### Limitations of Existing RNA Velocity Methods

RNA velocity (La Manno et al. 2018, *Nature*) exploits the unspliced/spliced RNA delay to infer a direction of gene expression change, but existing tools suffer from three fundamental problems:

1. **Gene-wise independence**: scVelo (Bergen et al. 2020, *Nature Biotechnology*) estimates a separate velocity for each gene on different time scales. The resulting vector field is not tangent to the gene expression manifold — it is geometrically inconsistent.

2. **Heuristic smoothing**: Nearest-neighbor smoothing of RNA counts causes information to "bleed" across cells and genes, introducing artifacts. Standard methods cannot model raw count noise directly.

3. **No statistical inference**: Existing methods (including VeloVAE, Gu et al. 2022 bioRxiv; VeloVI, Gayoso et al. 2024 *Nat. Methods*; Pyro-Velocity) provide either no uncertainty estimates or mean-field posteriors that underestimate uncertainty due to ignored inter-variable correlations. No method previously supported statistical comparison of velocity between conditions.

#### VeloCycle's Contributions

VeloCycle reformulates RNA velocity as a **manifold-constrained probabilistic model** with three key innovations:

1. **Geometric consistency**: All genes share a single angular speed function ω(φ) defined on the manifold. This forces velocity vectors to be tangent to the gene expression manifold by construction (the chain-rule constraint couples all genes).

2. **No smoothing**: Raw UMI counts are modeled directly with a negative binomial (NB) noise model. No heuristic preprocessing.

3. **Full Bayesian inference**: Stochastic Variational Inference (SVI) returns posterior distributions with credibility intervals, enabling statistical tests — both against a null (zero velocity) and between conditions. A Low-Rank Multivariate Normal (LRMN) variational distribution captures correlation structure between degradation rate γ and angular speed νω, producing more calibrated uncertainties than mean-field SVI (and approaching MCMC accuracy while being 100× faster).

---

### Method Overview

#### Algorithmic Framework

VeloCycle operates on a **1D periodic manifold** (topologically S¹ circle) — the cell cycle phase φ ∈ [0, 2π). The method runs in two sequential phases:

**Step 1 — Manifold Learning (PhaseFitModel)**: Infers cell-specific phase coordinates φ_c and gene-specific Fourier coefficients ν_g from spliced RNA counts. Gene expression is modeled as a smooth Fourier series on the circle:

$$E[\log S_{gc}] = \sum_f \nu_{gf} \zeta_f(\varphi_c) + \text{count\_factor}_c$$

**Step 2 — Velocity Learning (VelocityFitModel)**: Conditioned on φ_c and ν_g from Step 1, infers the angular speed function ω(φ), splicing rates β_g, and degradation rates γ_g from unspliced RNA counts via the manifold-constrained kinetic equation:

$$E[\log U_{gc}] = -\log\beta_g + \log\!\left(\omega(\varphi_c) \sum_f \nu_{gf} \frac{\partial\zeta_f}{\partial\varphi} + \gamma_g\right) + E[\log S_{gc}]$$

All parameters are inferred jointly with a negative binomial noise model via SVI (ELBO objective, ClippedAdam optimizer).

#### Key Technical Components

- **Fourier parameterization**: Both gene expression and angular speed are Fourier series on S¹. Default: 1 harmonic (3 parameters per gene: constant, sin, cos). Phase represented as 2D projected normal to avoid circular boundary artifacts.
- **LRMN variational distribution**: γ_g and νω jointly modeled as Low-Rank Multivariate Normal (k=5 factors); β_g|γ_g conditional Normal. Captures γ-νω correlation structure observed by MCMC.
- **Transfer learning**: Gene Fourier coefficients inferred on large reference datasets can be fixed as priors for small datasets (~75 cells), enabling velocity inference in Perturb-seq conditions.
- **Statistical testing**: Non-overlapping 90% credibility intervals (5th–95th percentile) indicate statistically significant velocity differences.

#### Biological Assumptions

- Cell cycle progresses on a 1D periodic manifold (S¹)
- Gene expression is smooth and approximately sinusoidal along the cycle
- All genes share the same angular speed function (key manifold-constraint)
- mRNA kinetics follow a first-order ODE: ds/dt = β·u − γ·s
- Average mRNA half-life ~1h (for real-time period estimation)

---

### Evaluation

#### Datasets Used

| Dataset | Cell Type | Technology | Purpose |
|---------|-----------|------------|---------|
| 3000 cells × 300 genes (20 simulations) | Simulated | — | Ground-truth benchmarking |
| FUCCI mES cells | Mouse embryonic stem | Smart-seq2 | Phase validation vs FACS |
| Human fibroblasts | Primary fibroblasts | 10x Chromium | Phase comparison vs DeepCycle |
| RPE1 (2 replicates) | Retinal pigment epithelium | 10x | Velocity replication |
| dHF + time-lapse microscopy | Dermal human fibroblasts | 10x + live imaging | Direct velocity validation |
| PC9 lung adenocarcinoma | Cancer cells (D0/D3 erlotinib) | 10x | Drug treatment testing |
| Mouse brain RG (E10, E14-15) | Radial glia, FB/MB/HB | 10x | Spatiotemporal speed variation |
| RPE1 Perturb-seq | 167,119 cells, 986 knockdowns | 10x | Transfer learning at scale |

#### Key Quantitative Results

**Manifold learning accuracy** (simulations, 20 datasets):
- Circular correlation with ground truth: r = 0.95 (VeloCycle) vs r = 0.73 (DeepCycle, Riba et al. 2022, *Nat. Commun.*)
- 60% lower mean squared error vs DeepCycle
- 99.2% of cells have true phase within 5–95% credible interval

**Kinetic parameter recovery** (simulations, 20 datasets):
- r(γ/β) = 0.997; r(β) = 0.918; r(γ) = 0.617
- Mean angular velocity error: 5.4–22.6% (depending on speed and dataset size)

**Cell cycle period validation** (real-time, live imaging comparison):
- dHF cells: VeloCycle 15.3 ± 1.2h; live imaging 15.8h median (SD 3.1h, n=282 cells)
- RPE1 cells: VeloCycle 17.7 ± 2.1h; live imaging 17.7h mean (SD 3.4h, n=338 cells)
- EdU labeling (RPE1): 16.8h mean — all methods agree within credibility intervals

**LRMN vs mean-field SVI vs MCMC** (human fibroblasts):
- MCMC posterior width: 0.10 rpmh
- LRMN (SVI+LRMN) posterior width: 0.08 rpmh
- Mean-field SVI: 0.02 rpmh (5× underestimate)
- SVI+LRMN reduces KL divergence from MCMC substantially vs mean-field SVI

**Cross-boundary direction correctness** (CBDir benchmark, 4 datasets):
- VeloCycle achieves highest CBDir across all evaluated methods (scVelo Bergen et al. 2020 *Nat. Biotechnol.*; cellDancer Li et al. 2024 *Nat. Methods*; Dynamo Qiu et al. 2022 *Cell*; VeloVAE Gu et al. 2022 bioRxiv)

**Biological applications**:
- Erlotinib treatment: detected decreased G2/M phase speed at D3 vs D0 (non-overlapping credibility intervals)
- Mouse brain RG: HB > MB > FB cell cycle speed at E10; all regions converge at E14-15
- Perturb-seq: MCM6Δ, EIF3BΔ knockdowns among largest cell cycle speed decreases; DBR1Δ splicing factor showed 11.7-fold decrease

#### Limitations and Caveats

- Currently specialized to 1D periodic manifolds; 1D non-periodic (B-spline) and 2D extensions exist but are in tutorial form only, not library-grade
- Minimum data requirements: 500 cells (with ≥50 genes) or 350 genes (with ≥50 cells) for reliable velocity
- Constant gene-specific kinetic rates (β_g, γ_g) assumed; phase-varying rates are not modeled
- Splicing factor knockdowns may violate biophysical parameterization assumptions (DBR1Δ finding)
- Cross-method benchmarking limited by absence of ground-truth velocity in real data

---

### Reproducibility

**Rating: 4/5**

**Justification**: The code is well-structured, publicly available, and the main pipeline (preprocess → manifold → velocity) is clearly implemented. All main paper analyses can be reproduced with the provided VeloCycle package plus published datasets. However, some details reduce full reproducibility:

**Strengths**:
- PyPI-installable package (velocycle) with documented entry points
- All primary datasets are publicly available (FUCCI mES, fibroblasts, RPE1, mouse brain)
- Default hyperparameters match paper (MEDIUM gene set 218, SVI steps 5000/10000, LRMN with k=5)
- Jupyter tutorials in repo cover main use cases

**Weaknesses / Pitfalls**:
- Step count (5000/10000) and learning rate decay schedule are documented in tutorials but not hardcoded as library defaults — must be set manually
- NB dispersion α_g is a point estimate in the guide (Delta distribution) despite paper describing it as a proper random variable with Gamma prior — uncertainty is underestimated for dispersion
- Fourier coefficient ordering in code [1, sin, cos, sin(2φ), cos(2φ)] differs from paper equation notation [1, cos, sin] — functionally equivalent but creates paper-to-code symbol mismatch
- The β prior (N(2, 3²) in log space) is extremely wide and not "biochemically informed" as claimed; only γ is genuinely constrained
- Large datasets (>30k cells) may require GPU; memory management for 500 posterior samples requires batching (50/call)
- The 1D non-periodic (B-spline) and 2D models exist only in `tutorials/` and are not production-ready

**Environment**: Python 3.9+, pyro-ppl 1.8.6, torch 2.1.1, anndata 0.9.2, scanpy 1.9.6. GPU not required but strongly recommended for datasets >10k cells.

**Data availability**: All primary datasets cited in the paper are available from original sources. The Perturb-seq dataset (Replogle et al. 2022) is available from public repositories.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
