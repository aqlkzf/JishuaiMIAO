---
layout: default
permalink: /paper-atlas/velotrace-c2d5d711/
title: "VeloTrace"
nav: false
description: "轨迹推断通常从细胞在表达空间中的邻近关系出发，得到全局路径和伪时间；RNA velocity 则从每个基因的 unspliced/spliced 计数拟合瞬时转录动力学。前者擅长全局形状但缺少局部方向，后者有局部方向却容易受低表达、dropout 和动力学拟合误差影响。两条管线独立运行后再把 velocity 投影到轨迹上，可能掩盖原始速度与轨迹相互冲突的问题。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>VeloTrace</h1>
    <p>VeloTrace Reconciles Divergent Velocity and Trajectory in Single-cell Transcriptomics with Deep Neural ODE</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.04.09.717458" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for VeloTrace">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeloTrace：让速度成为轨迹的切向量

### 1. 方法要解决的矛盾

轨迹推断通常从细胞在表达空间中的邻近关系出发，得到全局路径和伪时间；RNA velocity 则从每个基因的 unspliced/spliced 计数拟合瞬时转录动力学。前者擅长全局形状但缺少局部方向，后者有局部方向却容易受低表达、dropout 和动力学拟合误差影响。两条管线独立运行后再把 velocity 投影到轨迹上，可能掩盖原始速度与轨迹相互冲突的问题。

VeloTrace 的核心几何约束是：速度不是轨迹上的附加箭头，而是轨迹的时间导数。它用一个 Neural ODE 学习共享速度场，轨迹直接由该场积分产生，因此切向一致性在模型定义中成立。

论文为 “VeloTrace Reconciles Divergent Velocity and Trajectory in Single-cell Transcriptomics with Deep Neural ODE”，bioRxiv 2026，DOI `10.64898/2026.04.09.717458`。截至 2026-07-19，工作区和公开检索均未发现源码仓库；以下实现细节只能来自论文，不能做 paper-code 对照验证。

### 2. 输入与输出

论文所需输入至少包括：

- 每个细胞的高维基因表达状态 $x$；
- 每个基因的 spliced $s_g$ 与 unspliced $u_g$ 计数；
- 外部伪时间提供的粗时间坐标；
- scVelo 动力学拟合和参考 RNA velocity；
- 通过拟合质量筛出的高可信基因集合。

输出是随细胞状态和时间变化的速度场 $f_\theta(x,t)$、由其正向或反向积分得到的连续路径，以及论文所称对低表达基因的表达/velocity refinement。后者的具体算法并未在 Methods 完整定义。

### 3. Neural ODE 如何统一速度与轨迹

流映射写成

$$
\Phi:(t,x_0)\mapsto\Phi_t(x_0),
$$

并满足

$$
\frac{d}{dt}\Phi_t(x_0)=v(\Phi_t(x_0)).
$$

VeloTrace 用神经网络参数化速度：

$$
\frac{dx}{dt}=f_\theta(x(t),t),\qquad
\hat v=f_\theta(x(t),t).
$$

从状态 $x_i$ 积分时间 $\Delta t$ 得

$$
\hat x=x_i+\int_{t_i}^{t_i+\Delta t}f_\theta(x(\tau),\tau)d\tau.
$$

因为 $\hat x$ 的路径就是同一个 $f_\theta$ 的积分曲线，所以预测速度天然沿轨迹切向。论文称内部积分使用 adaptive Runge–Kutta，但没有给出求解器名称、容差、步长策略、反向传播方式或网络架构。

### 4. 三类监督信号

#### 4.1 几何重建

如果伪时间把 $x_i$ 放在 $x_j$ 之前，模型把 $x_i$ 积分到目标时间，并最小化

$$
\mathcal L_{\rm geom}
=\lVert x_j-\Phi_{t_i+\Delta t}(x_i)\rVert^2.
$$

这使流经过观察到的细胞状态分布。但 scRNA-seq 并没有真实的逐细胞配对，因此 $x_i$ 与 $x_j$ 的配对本身是伪时间和抽样规则构造的监督，不是观察到的同一细胞未来。

#### 4.2 SQS 筛选的 splicing 方向监督

论文以 scVelo 动力学模型解释 spliced/unspliced 计数的 $R^2$ 作为 Splicing Quality Score：

$$
R_g^2=1-
\frac{\sum_t[(s_g-\hat s_g)^2+(u_g-\hat u_g)^2]}
{\sum_t[(s_g-\bar s_g)^2+(u_g-\bar u_g)^2]}.
$$

只保留

$$
\mathcal G=\{g:R_g^2\ge R^2_{\rm threshold}\}
$$

作为可靠基因。模型在 $\mathcal G$ 上用余弦损失对齐 Neural ODE 与 scVelo 参考方向：

$$
\mathcal L_{\rm velo}=\frac1N\sum_k
\left[1-\cos\left(v_{\mathcal G}(\Phi_t(x_k)),
\hat v_{\mathcal G}(x_k)\right)\right].
$$

余弦只约束方向，不约束速度大小。SQS 降低低质量基因对训练的干扰，但高 $R^2$ 并不保证 scVelo 的生物方向无偏；模型仍继承其动力学假设。论文没有给出 $R^2$ 阈值。

#### 4.3 backward consistency

论文总损失写为

$$
\mathcal L_{\rm total}=\mathcal L_{\rm geom}
+\mathcal L_{\rm cons}+\alpha\mathcal L_{\rm velo}.
$$

正文把 $\mathcal L_{\rm cons}$ 称为 backward-consistency constraint，却没有公式、采样方式或权重定义。它可能意在约束正向后再反向积分回到起点，但这是推测，不能当作已证实机制。$alpha$ 的数值也未报告。

### 5. 多时间跨度 Monte Carlo 监督

单细胞只提供横截面快照。论文先用未指明的方法得到伪时间，然后随机采样起点 $x_i$、时间跨度 $\Delta t$ 和相应目标 $x_j$：

$$
\mathcal L_{\rm geom}=
\mathbb E_{(x_i,\Delta t)\sim p_{\rm data}}
\left[\lVert x_j-\Phi_{t_i+\Delta t}(x_i)\rVert^2\right].
$$

短跨度约束局部连续性，长跨度抑制只在局部看似合理、整体却打转或漂移的场。随机采样还让模型不只依赖一组相邻配对。

但论文未说明：目标细胞如何在分支轨迹上匹配、如何避免跨谱系配对、$\Delta t$ 的分布、每批采样量，以及分叉处如何处理一对多未来。这些细节会实质改变训练目标。

### 6. “扩展到低表达基因”应怎样理解

VeloTrace 只用高 SQS 基因提供可靠方向，同时在完整表达空间拟合一个共享流。论文据此称低质量基因的动力学可从全局结构中得到 refinement 或 imputation。它还在 Results 提到 “time-guided Laplacian smoothing”，用于改善 gene-wise splicing phase portrait。

然而 Methods 没有定义该 Laplacian 的图、边权、时间约束、正则强度或它与 Neural ODE 输出的关系。因此能够确认的是论文报告了 refinement 后的效果；不能确认具体算法，也不能判断提升有多少来自 ODE、平滑器或评估数据的相同伪时间结构。

### 7. 图证据

- Fig. 1 用概念图和不同表达/测序深度的二基因例子说明原始 splicing velocity 噪声与切向不一致。
- Fig. 2 在模拟数据中比较 scVelo、VeloVI、UniTVelo、scTour 和 VeloTrace 的角度误差、PC 空间流向及 gene-wise phase portrait MSE。模拟真值适合检验恢复能力，但论文未充分给出模拟生成细节。
- Fig. 3 在小鼠小脑发育中比较 GABAergic 与 gliogenic 分支，并展示 Pax2 等基因的 raw/refined 动态。这里的“正确方向”主要依赖已知生物层级和标记基因一致性。
- Fig. 4 使用带 lineage barcode 的造血数据，把预测 fate distribution 与克隆结果比较，是较强的外部方向验证；当前 OCR 仅有一个主 panel，评价与统计细节有限。

图号和正文存在 `Fig. ??` 等预印本编辑错误。工作区没有独立补充文件，不能声称已核验补充实验或超参数表。

### 8. 论文证据与实现边界

| 机制 | 论文证据 | 代码证据 |
|---|---|---|
| Neural ODE 流与切向一致性 | Methods 公式，`paper.md:177-218` | Not found |
| 几何重建损失 | `paper.md:221-227` | Not found |
| SQS 与高质量基因筛选 | `paper.md:229-241` | Not found；阈值也未报告 |
| velocity 余弦对齐 | `paper.md:243-249` | Not found |
| adaptive Runge–Kutta / SGD | `paper.md:251-257` | Not found；具体实现未报告 |
| Monte Carlo multi-time-lag | `paper.md:259-277` | Not found；配对规则未报告 |
| $\mathcal L_{\rm cons}$ | 仅出现在总损失 | Not found / undefined |
| time-guided Laplacian smoothing | Results 中提及 | Not found / Methods 缺失 |

2026-07-19 的公开检索仅找到 bioRxiv 论文页及转载，没有定位到作者代码仓库。没有源码时，`doc_code.md` 中的预期文件名只是导航性猜测，不是实际实现映射。

### 9. 识别性和生物解释限制

1. 横截面细胞没有真实配对；伪时间和采样策略先验会影响学到的流。
2. 一个平滑场能连接观察分布，不代表它是唯一真实动力学；分叉处尤其存在一对多未来。
3. splicing 监督来自 scVelo，不能完全独立验证 VeloTrace。
4. 余弦方向对齐忽略尺度，预测 velocity magnitude 的可比性不清楚。
5. 高维 Neural ODE 的网络容量、正则化和数值求解器未报告，难以判断过拟合和计算成本。
6. refinement 可能改善平滑性，但平滑曲线更接近模拟真值不自动证明真实低表达基因动力学被恢复。
7. 论文 Discussion 也承认网络架构缺少可解释性，尚未直接整合调控网络和信号通路。

### 10. 复现结论

VeloTrace 的概念贡献很清楚：把速度与轨迹放入同一个 Neural ODE，使轨迹成为速度场积分曲线；再用 SQS 筛选的 splicing velocity 提供弱方向监督，并用多时间跨度配对约束局部—全局一致性。

但当前只能做 paper-only 理解，不能复现或核验实现。缺失项包括代码、环境、数据 accession、网络结构、伪时间方法、SQS 阈值、$\alpha$、$\mathcal L_{\rm cons}$、Monte Carlo 配对规则、Laplacian refinement 和完整模拟生成过程。最稳妥的定位是：这是一个有吸引力但尚未具备可审计实现合同的预印本方法框架；其效果主张应与未公开实现细节共同阅读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeloTrace: Summary

### Motivation & Novelty

#### Biological Problem

Single-cell RNA sequencing captures static snapshots of cell populations. Two complementary approaches reconstruct cellular dynamics from these snapshots:

- **Trajectory inference** (Monocle, *Nature Biotechnology* 2014; Slingshot, *BMC Genomics* 2018; PAGA) connects cell states by proximity in expression space and assigns pseudotime. It captures global developmental structure but ignores local transcriptional dynamics.
- **RNA velocity** (scVelo, *Nature Biotechnology* 2020; VeloVI; UniTVelo) models splicing kinetics (unspliced/spliced mRNA ratios) to infer instantaneous transcriptional rates. It captures local dynamics but is noisy for low-expression genes and is computed independently of trajectory.

The fundamental geometric inconsistency: velocity is the time derivative of position, so it must be *tangent* to the trajectory everywhere. Current methods enforce this post-hoc by projecting gene-level velocities onto a pre-computed trajectory — masking underlying disagreements. A systematic analysis (Zheng et al., *Genome Biology* 2023) showed that raw RNA velocities are highly sensitive to sequencing noise and often chaotic without projection and smoothing.

#### Limitations of Existing Methods

| Method | Limitation |
|---|---|
| scVelo (*Nat Biotechnol* 2020) | Noisy for low-expression genes; trajectory and velocity computed independently |
| VeloVI | Improved uncertainty but same independence problem |
| UniTVelo | Better consistency but still post-hoc projection |
| scTour (*Genome Biology* 2023) | NeuralODE in latent space; velocities don't translate to gene space |
| Slingshot (*BMC Genomics* 2018) | Pseudotime-based velocity is unstable; requires manual smoothing |

#### Unique Contributions

1. **Geometric unification**: VeloTrace learns a NeuralODE velocity field whose integral curves *are* the trajectories — no post-hoc projection. Tangency is enforced by construction.
2. **Splicing Quality Score (SQS)**: Uses scVelo's $R^2$ to filter high-confidence genes for directional supervision, avoiding noisy signals.
3. **Monte Carlo multi-time-lag sampling**: Samples cell pairs at varying temporal displacements to enforce local-global coherence simultaneously.
4. **Gene-space operation**: Unlike scTour, VeloTrace operates directly in high-dimensional gene expression space, enabling direct biological interpretation.
5. **Velocity imputation**: Extends reliable velocity estimation to low-expression genes by learning the global field structure from high-quality genes.

---

### Method Overview

VeloTrace models transcriptomic dynamics as a continuous-time dynamical system:
$$\frac{d}{dt}\Phi_t(x_0) = v(\Phi_t(x_0))$$

where $x \in \mathbb{R}^n$ is the cell state (gene expression vector) and $v$ is the velocity field. The velocity field is parameterized by a neural network $f_\theta$ (NeuralODE), trained to minimize:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{geom}} + \mathcal{L}_{\text{cons}} + \alpha \mathcal{L}_{\text{velo}}$$

- $\mathcal{L}_{\text{geom}}$: geometric reconstruction — ODE-predicted cell states match observed states
- $\mathcal{L}_{\text{velo}}$: cosine alignment with scVelo reference velocities on high-quality genes (SQS-filtered)
- $\mathcal{L}_{\text{cons}}$: backward-consistency constraint (not formally defined in paper)

**Key technical components**:
- **SQS filtering**: Selects genes with $R^2_g \geq \tau$ from scVelo kinetic model fit
- **Monte Carlo sampling**: At each iteration, samples $(x_i, x_j, \Delta t)$ pairs at varying time lags
- **Adaptive Runge-Kutta**: ODE integration with adaptive step size
- **Time-guided Laplacian smoothing**: Post-hoc gene-wise refinement (not in Methods)

**Biological assumptions**:
- Transcriptomic dynamics are governed by a smooth, time-invariant velocity field
- scVelo kinetics are reliable for high-$R^2$ genes and can serve as directional supervision
- Pseudotime provides a coarse but usable initial ordering of cells

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation analysis.

---

### Evaluation

#### Datasets

| Dataset | Type | Purpose |
|---|---|---|
| Simulation | Synthetic with ground-truth kinetics | Benchmarking velocity accuracy |
| Mouse cerebellum | Real scRNA-seq, bifurcating (GABAergic + gliogenic lineages) | Biological validation |
| Mouse hematopoiesis | Real scRNA-seq + lineage barcodes (days 2, 4, 6) | Fate prediction validation |

#### Metrics

- **Cell-wise velocity accuracy**: Cosine distance between inferred and ground-truth velocity directions (0-180°, lower is better)
- **Gene-wise accuracy**: MSE between observed $(u_i, s_i)$ and predicted $(\hat{u}_i, \hat{s}_i)$ on phase portrait
- **Fate prediction**: Cosine similarity between predicted fate distributions and barcode-derived lineage outcomes

#### Comparative Results

**Simulation benchmarks**:
- VeloTrace: minimal angular error, smooth directionally consistent vectors along entire trajectory
- scVelo: broad angular dispersion, locally inconsistent chaotic vectors
- VeloVI: improved but systematic angular shifts and region-specific misalignment
- UniTVelo: smaller deviations, consistent across expression levels
- scTour: coherent in latent space but wide angular deviations in gene space (approaching 180°)

**Gene-wise MSE** (simulation):
- scVelo, VeloVI: substantially higher and more variable errors
- UniTVelo + VeloTrace (raw): comparable to ground-truth kinetics MSE
- VeloTrace (refined): further reduces MSE, especially for low-expression genes

**Mouse cerebellum**:
- VeloTrace: correctly resolves GABAergic and gliogenic lineages
- scVelo: local inconsistencies in VZ progenitors
- VeloVI: contradicts expected gliogenic differentiation flow
- scTour: fails to distinguish gliogenic from GABA interneuron lineages
- UniTVelo: complete reversal of velocity directionality

**Mouse hematopoiesis** (vs scDiffEq):
- VeloTrace: higher cosine similarity with barcode-derived fate outcomes
- scDiffEq: weak drift near progenitor hub, false-positive basophil predictions

#### Biological Findings (Mouse Cerebellum)

- Identifies driver genes for GABAergic lineage: Pax2 (refined dynamics)
- Identifies driver genes for gliogenic lineage: Ptprz1 (oligodendrocyte differentiation), Slc1a3 (astrocyte marker)
- Proliferation genes: Rpl4, Rrm2, Set (decrease during differentiation)
- Progenitor maintenance: Sox6, Ddah1 (upregulated in gliogenic progenitors)
- Recovers dynamics of low-expression driver genes that scVelo cannot characterize

---

### Reproducibility

**Rating: 2/5**

**Justification**: This is a preprint with no code repository, no data availability statement, and multiple underdefined methods components. Reproduction is not currently possible.

**Specific gaps**:
- No code available (no GitHub link, no supplementary code)
- Neural network architecture of $f_\theta$ not described
- $\mathcal{L}_{\text{cons}}$ (backward-consistency loss) mentioned but never defined
- "Time-guided Laplacian smoothing" described in Results but absent from Methods
- $R^2$ threshold for SQS not specified
- Pseudotime method for initial ordering not specified
- $\alpha$ (velo loss weight) not specified
- Simulation dataset generation procedure not described
- Mouse cerebellum and hematopoiesis datasets not cited with accession numbers

**Strengths**:
- Mathematical framework is clearly stated (Eqs. 1-11)
- SQS concept is well-defined and principled
- Monte Carlo sampling strategy is clearly motivated
- Comparison methods are well-chosen and fairly evaluated (scTour decoded to gene space)

**Weaknesses**:
- Preprint quality: figure numbering errors ("Fig. ??"), missing Methods sections
- No ablation study (e.g., what happens without SQS? without Monte Carlo?)
- No sensitivity analysis for $R^2$ threshold or $\alpha$
- Computational cost not reported (gene-space NeuralODE is expensive)
- $\mathcal{L}_{\text{cons}}$ is a critical component that is never defined

**Environment** (inferred):
- Python with PyTorch
- scVelo ≥0.2 as preprocessing dependency
- torchdiffeq for NeuralODE integration
- scanpy for data handling

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
