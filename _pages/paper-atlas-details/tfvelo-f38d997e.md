---
layout: default
permalink: /paper-atlas/tfvelo-f38d997e/
title: "TFvelo"
nav: false
wide: true
description: "经典 RNA velocity 用未剪接 RNA u 与已剪接 RNA s 的相位差估计 ds/dt。但 intronic reads 稀疏，有些数据根本没有 spliced/unspliced 分层，而且逐基因剪接模型没有显式利用调控上下文。TFvelo 的核心替换是：对目标基因 g，把候选转录因子表达的加权和当作转录驱动，用总 RNA 表达也能建立速度模型。"
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
      <span>Nature Communications · 2024</span>
    </div>
    <h1>TFvelo</h1>
    <p>TFvelo: gene regulation inspired RNA velocity estimation</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-024-45661-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TFvelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xiaoyeye/TFvelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for TFvelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TFvelo 方法解读：用转录因子驱动替代剪接相位差

### 方法要解决什么

经典 RNA velocity 用未剪接 RNA $u$ 与已剪接 RNA $s$ 的相位差估计 $ds/dt$。但 intronic reads 稀疏，有些数据根本没有 spliced/unspliced 分层，而且逐基因剪接模型没有显式利用调控上下文。TFvelo 的核心替换是：对目标基因 $g$，把候选转录因子表达的加权和当作转录驱动，用总 RNA 表达也能建立速度模型。

它回答的是“在给定调控候选集和函数假设下，哪个方向最符合当前表达相图”，不是直接观测细胞祖先关系，也不是从 TF 表达证明因果调控。

### 输入、输出与数据流

输入是 cells × genes 的总表达矩阵。若已有 spliced/unspliced，演示代码把二者相加；否则直接使用 `adata.X`。预处理执行基因/细胞过滤、归一化、对数变换、HVG 选择、邻域图和矩估计，然后从 ENCODE 与 ChEA 文件为每个目标基因查找在数据中出现的候选 TF。

每个目标基因输出一组曲线参数 $(\alpha,\beta,\theta,\gamma)$、TF 权重 $\mathbf W$、每个细胞的基因级潜在时间、拟合损失和速度

$$
v(t)=\frac{dy}{dt}=\mathbf W\mathbf X(t)-\gamma y(t).
$$

所有合格基因的速度再用于构建细胞—细胞 velocity graph、检测根/终点并计算全局 velocity pseudotime。基因级时间和细胞级伪时间是两个层次，不能混为同一个直接拟合变量。

### 第一步：把 TF 表达压成一个调控驱动

对目标基因表达 $y$，候选 TF 表达向量为 $\mathbf X$，模型写作

$$
\frac{dy}{dt}=\mathbf W\mathbf X-\gamma y.
$$

$\mathbf W\mathbf X$ 是多个候选 TF 的线性组合。正权重可解释为模型中的正向贡献，负权重为负向贡献；但候选关系来自数据库，权重来自同一份横断面表达的曲线拟合，所以“正/负贡献”不自动等于已实验验证的激活/抑制因果关系。

源码 `get_TFs()` 逐条读取 ENCODE/ChEA，要求 TF 与 target 都存在于当前基因集，并把 TF 索引和 TF–target Spearman 相关写入 AnnData。演示默认最多保留 99 个 TF，权重由相关性初始化。

### 第二步：用正弦函数规定目标基因的时间形状

TFvelo 采用 top-down profile：

$$
y(t)=\alpha\sin(2\pi t+\theta)+\beta,\qquad t\in[0,1).
$$

$\alpha$ 控制振幅，$\beta$ 是基线，$\theta$ 决定峰谷位置；固定 $\omega=2\pi$ 意味着一个标准化周期内至多表达一个峰和一个谷。它适合单峰或单谷动态，却不能忠实表示多次脉冲、任意平台或多个独立过程。

代回动力学方程得到闭式调控驱动：

$$
\mathbf W\mathbf X(t)=\alpha\sqrt{4\pi^2+\gamma^2}
\sin(2\pi t+\theta+\phi)+\beta\gamma,
\qquad
\phi=\arctan\left(\frac{2\pi}{\gamma}\right).
$$

因此 $\mathbf W\mathbf X(t)$ 领先于 $y(t)$，二者在二维相图上形成椭圆。源码 `SplicingDynamics.get_solution()` 虽保留了 scVelo 的历史类名，却直接计算上述 `WX` 与 `y`，没有数值积分，也没有在这里计算 unspliced/spliced 动力学。

一个直观例子：若 $\gamma=2\pi$，则 $\phi=\arctan(1)=\pi/4$，调控驱动比目标表达提前八分之一个周期。观察点在椭圆哪一段，决定它被分配到上升期还是下降期。

### 第三步：广义 EM 交替寻找时间、权重和曲线

对每个基因，模型使观察状态

$$
\mathbf s_c^{obs}=[\mathbf W\mathbf X_c^{obs},y_c^{obs}]
$$

靠近模型曲线 $\hat{\mathbf s}(t)=[\mathbf W\mathbf X(t),y(t)]$。源码使用标准化平方距离的均值；`WX` 和 $y$ 两个轴分别按数据/模型尺度归一，其中 $y$ 轴的 `get_norm_std(..., par=1.5)` 是论文主公式未写明的实现细节。

一次交替更新包含：

1. **时间分配**：在 $[0,1]$ 上生成默认 1000 个模型点，把每个细胞分给相图上最近的点。
2. **权重更新**：固定时间后，用 `scipy.optimize.lsq_linear` 拟合 $\mathbf X\mathbf W+\delta$ 到模型所需的 $WX(t)$，默认每个权重和截距界于 $[-20,20]$。
3. **曲线参数更新**：用 Nelder–Mead 更新 $\alpha,\beta,\theta,\gamma$；只有损失下降才接受更新。

初始化用表达高低分位数估计 $\alpha,\beta$，用 TF–target 相关初始化 $\mathbf W$，再从多个 $\theta$ 起点搜索。源码第二轮还尝试 $\gamma\in\{2.5,5,7.5\}$，只有损失比首轮最好值再低至少 10% 才替换，从而减轻局部最优但不保证全局最优。

速度最后直接计算为

$$
\hat v_c=(\mathbf W\mathbf X_c+\delta)-\gamma y_c.
$$

正值表示模型预期目标表达上升，负值表示下降。它依赖正弦曲线方向、候选 TF、邻域平滑和优化解，不能当作物理时间导数的无偏测量。

### 从逐基因速度到细胞伪时间

演示脚本先把 `velo_hat` 按目标表达 scaling 还原为 `velocity`，用总表达的邻域矩 `M_total` 与速度建立 cosine-similarity velocity graph，再沿用 scVelo 风格的根/终点与 velocity pseudotime 计算。

用于流图的基因还经过强筛选：拟合损失低于第 50 百分位、至少 10% 细胞表达、并且重新排序后的基因级时间与全局 pseudotime 的 Spearman 相关大于 0.8。这个步骤提高流场一致性，但也形成选择闭环：展示的是最符合最终排序的那部分基因，而不是所有基因的独立验证。

由于正弦函数周期首尾相接，`get_sort_t()` 通过潜在时间直方图的空 bin 找切口，再把时间转成秩。若没有清晰空档，切口选择可能不稳定；这也是“周期参数”转换成“单向发育顺序”时的重要假设。

### 如何读论文图和验证

- **图 1** 给出 TF-target 相图动机与 TFvelo 流程；椭圆更清晰说明可拟合性，不等价于调控因果已证实。
- **图 2** 在模拟数据上检验已知 TF 权重与速度恢复，是参数可识别性的受控证据；模拟机制与模型同族，不能覆盖真实数据的模型错配。
- **图 3** 在 3696 个胰腺细胞上比较相图和流场，并分析 REST/HMGN3；富集与文献一致性是生物合理性证据，不是新的干预验证。
- **图 4** 在 9815 个 gastrulation erythroid 细胞上展示稀疏 unspliced 情况及 GATA1/GATA2 等调控因子。
- **图 5** 将仅用 RNA 的 TFvelo 与 RNA+ATAC 的 MultiVelo 比较；视觉/伪时间相似不代表 TF 表达等价于染色质可及性。
- **图 6** 在没有剪接分层的 1529 个 human embryo cells 上给出 E3→E7 排序，展示该方法最独特的适用场景。

论文使用 phase-portrait intra/inter-class distance、拟合误差、CBDir 与 in-cluster coherence 等指标。CBDir 需要预先指定正确的 cluster transition，主要检验已知边界方向；in-cluster coherence 衡量局部一致，不保证全局拓扑正确。

### 论文—代码对应与复现边界

| 论文机制 | 直接源码 | 判断 |
|---|---|---|
| ENCODE/ChEA 候选 TF | `TFvelo/preprocessing/utils.py:get_TFs()` | Exact |
| 正弦 $y(t)$ 与闭式 $WX(t)$ | `TFvelo/core/_models.py:get_solution()` | Exact |
| 最近曲线点分配基因时间 | `DynamicsRecovery.assign_time()` | Exact |
| 有界最小二乘 TF 权重 | `BaseDynamics.update_WX()` | Exact；源码还拟合截距 |
| 广义 EM 与多起点 | `dynamical_model.py` 的 `search_and_fit()`、`update()` | Exact，含论文未展开的接受阈值 |
| $v=WX-\gamma y$ | `get_raw_velocity()` | Exact |
| 全局伪时间和流场 | `TFvelo_analysis_demo.py`、velocity graph 工具 | Partial：继承并修改 scVelo 框架 |
| 全论文结果一键重现 | demo、baseline、simulation 脚本 | Partial：有入口，但本次未安装锁定环境或重跑全基准 |

README 锁定 Python 3.8.12、scVelo 0.2.4 等旧版本，且 ENCODE 必须先解压；论文补充材料在正文中有链接，但本地没有独立转换的 supplementary markdown。

本次已用 CodeGraph 定位 `recover_dynamics → DynamicsRecovery → assign_time/get_solution` 与 downstream velocity graph，再以直接源码核对公式和默认值；没有执行完整环境安装、训练、基准或论文数值复算。

### 使用时应做的敏感性检查

至少应改变候选 TF 数据库、TF 数量上限、邻居数、权重边界、时间网格和多起点设置，检查速度方向是否稳定；分别报告全基因与筛选基因结果；用已知采样时间、谱系标记或 perturbation 数据做外部验证。若目标基因呈多峰动态、存在汇合/循环谱系，或 TF 蛋白活性与其 RNA 表达严重脱耦，线性 $WX$ 加单周期正弦假设尤其需要谨慎。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TFvelo: Gene Regulation Inspired RNA Velocity Estimation

**Paper**: Li, J., Pan, X., Yuan, Y. & Shen, H.-B. *Nature Communications* 15, 1268 (2024)
**DOI**: [10.1038/s41467-024-45661-w](https://doi.org/10.1038/s41467-024-45661-w)
**Code**: [https://github.com/xiaoyeye/TFvelo](https://github.com/xiaoyeye/TFvelo)
**Institution**: Shanghai Jiao Tong University

---

### Formal Problem Statement

**Given**: A single-cell RNA-seq dataset with $n$ cells and $p$ genes, with or without splicing annotations (unspliced/spliced counts).

**Find**: The RNA velocity $v_g = \frac{dy_g}{dt}$ for each gene $g$ in each cell, and the resulting cell trajectory and pseudotime ordering.

**Challenge**: Conventional RNA velocity methods require unspliced/spliced mRNA abundance, which is often too sparse, too noisy, or entirely unavailable. Each gene is modeled independently, ignoring regulatory context. These limitations degrade phase portrait fitting and trajectory inference.

---

### 1. Motivation & Novelty

#### Biological Problem

RNA velocity -- the time derivative of gene expression -- captures the rate and direction of cellular state transitions in single-cell data. Existing methods (velocyto, *Nature* 2018; scVelo, *Nature Biotechnology* 2020) model RNA velocity through the phase delay between unspliced ($u$) and spliced ($s$) mRNA. This approach suffers from three fundamental limitations:

1. **Insufficient splicing signal**: Pre-mRNA splicing completes within approximately 30 seconds, far shorter than the hours-to-days timescale of cellular differentiation captured by scRNA-seq. The resulting $u$-$s$ phase delay is too brief for robust modeling, producing near-degenerate phase portraits.
2. **Extreme sparsity of unspliced counts**: Only approximately 20% of sequencing reads map to intronic regions, producing unspliced count matrices that are sparse and noisy. This noise directly undermines the kinetic ODE models.
3. **Restricted data applicability**: Many single-cell datasets lack unspliced/spliced annotation entirely -- FISH-based spatial transcriptomics, certain human datasets with privacy restrictions, and datasets archived without raw sequencing files. Splicing-dependent velocity methods cannot be applied to these data.

#### Limitations of Existing Approaches

| Method | Journal, Year | Limitation Addressed by TFvelo |
|--------|--------------|-------------------------------|
| velocyto | *Nature*, 2018 | Steady-state assumption; sparse unspliced data; each gene modeled independently |
| scVelo | *Nat. Biotechnol.*, 2020 | Dynamical model still depends on u/s counts; no regulatory context across genes |
| UniTVelo | *Nat. Commun.*, 2022 | Top-down gene profile approach, but still requires spliced/unspliced data |
| CellDancer | *Nat. Biotechnol.*, 2023 | Neural network operates on u/s counts; no regulatory information incorporated |
| VeloVI | *Nat. Methods*, 2023 | Bayesian uncertainty quantification but remains splicing-dependent |
| MultiVelo | *Nat. Biotechnol.*, 2023 | Requires additional ATAC-seq data for chromatin dynamics |
| Dynamo | *Cell*, 2022 | Requires metabolically labeled RNA-seq data for accurate rate estimation |
| VeloAE | *PNAS*, 2021 | Autoencoder embeds steady-state velocity only; no joint time inference |

#### Motivating Finding: RNA Velocity Predicted from TF Expression

Before proposing TFvelo, the authors provide two key empirical validations that TF expression can replace unspliced mRNA:

1. **LASSO regression (Eq. 1)**: scVelo-estimated RNA velocity of each gene can be approximated as a linear combination of TF expression levels:

$$v_g = \sum_{TF_i \in S_g} w_{g,TF_i} \cdot e_{TF_i} + w_{g,g} \cdot e_g$$

On the pancreas dataset, TFs with non-zero LASSO weights are significantly enriched in ENCODE-annotated TF-target pairs (one-sided $t$-test, $p = 6.66 \times 10^{-6}$), confirming that the learned associations reflect genuine regulatory relationships rather than spurious correlations.

2. **Phase delay observation**: TF-target co-expression plots exhibit clockwise elliptical curves analogous to the unspliced-spliced phase portraits, but with a larger and more observable phase delay. This larger delay arises because TF regulation operates on a minutes-to-hours timescale (TF translation, nuclear import, DNA binding, polymerase recruitment), compared to the ~30-second splicing timescale.

These two findings -- predictability and observable phase delay -- provide the theoretical basis for replacing the $u$-$s$ framework with TF-target regulation.

#### Unique Contributions

1. **Regulatory-driven velocity**: Replaces the unspliced/spliced ODE with a TF-target gene regulation model, making RNA velocity estimation independent of splicing information.
2. **Broader applicability**: Works on total RNA expression alone -- no spliced/unspliced counts or multi-omics data required. Enables velocity analysis on previously inaccessible datasets.
3. **Interpretable TF weights**: Learns a per-gene weight vector $\mathbf{W}_g$ via constrained least squares, enabling identification of key activating and repressing TFs. Provides biological insights beyond trajectory inference.
4. **Generalized EM optimization**: Three-group alternating optimization (latent time, TF weights, curve parameters) with multi-initialization grid search to escape local minima.
5. **Phase portrait in TF-target space**: The phase delay between the learned TF representation $\mathbf{W}\mathbf{X}$ and target gene expression $y$ produces cleaner, more informative phase portraits than the conventional $u$-$s$ space.

---

### 2. Method Overview

#### Core Dynamic Equation

For each target gene $g$ with expression $y_g(t)$, TFvelo replaces the standard splicing-based ODE ($\frac{ds}{dt} = \beta u - \gamma s$) with a TF-regulation-based model:

$$\frac{dy_g(t)}{dt} = \mathbf{W}_g \mathbf{X}_g(t) - \gamma_g y_g(t) \quad \text{(Eq. 4)}$$

where:
- $\mathbf{X}_g(t) \in \mathbb{R}^{n_{\text{TF}}}$: expression levels of $n_{\text{TF}}$ transcription factors regulating gene $g$
- $\mathbf{W}_g \in \mathbb{R}^{1 \times n_{\text{TF}}}$: learned weight vector mapping TF expressions to a scalar regulatory signal
- $\gamma_g > 0$: degradation rate of gene $g$

The term $\mathbf{W}_g \mathbf{X}_g(t)$ represents the net transcriptional drive: positive weights indicate activating TFs, negative weights indicate repressors.

#### Gene Expression Profile Function

TFvelo adopts a "top-down" strategy (following UniTVelo's philosophy) by directly parameterizing the target gene's temporal profile:

$$y_g(t) = \alpha_g \sin(\omega_g t + \theta_g) + \beta_g \quad \text{(Eq. 5)}$$

with:
- $\alpha_g > 0$: amplitude (half the expression range)
- $\beta_g$: baseline expression level (mean)
- $\omega_g = 2\pi$ (fixed): angular frequency ensuring exactly one peak and one trough within $t \in [0, 1)$
- $\theta_g \in (-\pi, \pi)$: phase offset controlling when expression peaks or troughs

The sine function avoids a discrete switching time between induction and repression phases, producing smooth velocity fields. By varying $\theta_g$, the model handles genes that start from either upregulation ($\theta \approx -\pi/2$) or downregulation ($\theta \approx \pi/2$).

#### Analytical Solution for WX

Substituting the profile function into the dynamic equation and solving for $\mathbf{W}\mathbf{X}(t)$:

$$\mathbf{W}\mathbf{X}(t) = \frac{dy}{dt} + \gamma y = \alpha \omega \cos(\omega t + \theta) + \gamma[\alpha \sin(\omega t + \theta) + \beta]$$

Applying the trigonometric identity $a\cos\theta + b\sin\theta = \sqrt{a^2 + b^2}\sin(\theta + \arctan(a/b))$:

$$\mathbf{W}\mathbf{X}(t) = \alpha\sqrt{\omega^2 + \gamma^2}\sin(\omega t + \theta + \phi) + \beta\gamma \quad \text{(Eq. 8)}$$

where $\phi = \arctan\left(\frac{\omega}{\gamma}\right)$ is the phase lead. Since both $y(t)$ and $\mathbf{W}\mathbf{X}(t)$ are sinusoidal with the same period but different phases, plotting them against each other traces an ellipse (a Lissajous figure). The phase lead $\phi$ governs the ellipse shape:
- $\gamma \to 0$: $\phi \to \pi/2$, the ellipse approaches a circle (maximum delay)
- $\gamma \to \infty$: $\phi \to 0$, the ellipse collapses to a line (near-synchronous)

This closed-form solution avoids numerical ODE integration entirely.

#### Loss Function

The loss is the sum of squared distances between observed and model-predicted states on the $\mathbf{W}\mathbf{X}$-$y$ phase portrait:

$$L = \sum_c \left(\mathbf{W}\mathbf{X}_c^{\text{obs}} - \mathbf{W}\mathbf{X}(t_c)\right)^2 + \left(y_c^{\text{obs}} - y(t_c)\right)^2 \quad \text{(Eq. 9)}$$

Distances in the WX and $y$ dimensions are normalized by the geometric mean of the observed and model standard deviations. In the code, the $y$-dimension receives a factor of $1/1.5$, giving it slightly more weight (this detail is not documented in the paper).

#### Optimization: Generalized EM

TFvelo uses a generalized EM algorithm with three alternating steps per iteration:

**E-step -- Latent time assignment**: Generate 1000 equally spaced points on $[0, 1]$, compute the parametric curve $(\mathbf{W}\mathbf{X}(t), y(t))$, and for each cell, assign $t_c$ as the time of the nearest point on the curve by Euclidean distance.

**M-step 1 -- TF weight update**: Given current time assignments, compute target $\mathbf{W}\mathbf{X}(t_c)$ values from the model. Solve the bounded least-squares problem:

$$\min_{\mathbf{W}} ||\mathbf{X}_f \cdot \mathbf{W} - \mathbf{W}\mathbf{X}_t||^2 \quad \text{subject to } |w_i| \leq 20$$

using `scipy.optimize.lsq_linear`. The input is augmented with a column of ones to learn a bias term $\delta$.

**M-step 2 -- Parameter update**: Optimize $[\alpha, \beta, \theta, \gamma]$ via Nelder-Mead (`scipy.optimize.minimize`) with constraints: $\alpha > 0$, $\theta \in (-\pi, \pi)$, $\gamma > \gamma_{\text{thres}}$.

#### Multi-Initialization Strategy

To escape local minima, TFvelo performs grid search in two rounds:
1. **Round 1**: $\theta \in$ linspace from $-\pi$ to $\pi$ (9 values), $\gamma$ from initial estimate
2. **Round 2**: Same $\theta$ grid with $\gamma \in \{2.5, 5.0, 7.5\}$; accepted only if loss < 90% of Round 1 best

Initial TF weights are set via Spearman correlation between each TF and the target gene expression.

#### Preprocessing Pipeline

| Step | Operation | Detail |
|------|-----------|--------|
| 1 | Compute total counts | Spliced + unspliced (or raw X if no splicing) |
| 2 | Filter genes | Detected in $\geq$ 2% of cells |
| 3 | Select HVGs | Top 2000 highly variable genes |
| 4 | Normalize + log transform | Total count normalization per cell, then log1p |
| 5 | KNN graph | 30 neighbors in 30-PC space |
| 6 | Compute moments | 1st and 2nd order via KNN smoothing |
| 7 | TF lookup | Match gene names to ENCODE and ChEA databases |

#### Downstream Analysis

After per-gene recovery (parallelized across CPUs):
1. Compute velocity: $v = \mathbf{W}\mathbf{X} - \gamma y$, rescaled by $1/\text{scaling\_y}$
2. Filter genes: loss < 50th percentile, expressing cells > 10%, Spearman correlation between gene time and pseudotime > 0.8
3. Build velocity graph via cosine similarity transition matrix
4. Infer pseudotime from velocity graph
5. Generate velocity stream plots on UMAP embedding

---

### 3. Evaluation

#### Datasets

| Dataset | Cells | Genes | Type | Has Splicing? | Source |
|---------|-------|-------|------|--------------|--------|
| Pancreas (E15.5 mouse) | 3,696 | 27,998 | scRNA-seq (10X) | Yes | Bastidas-Ponce et al., 2019 |
| Gastrulation erythroid | 9,815 | 53,801 | scRNA-seq | Yes | Pijuan-Sala et al., 2019 |
| 10x mouse brain (E18) | 3,365 | 936 | Multi-omics (RNA+ATAC) | Yes | 10x Genomics |
| Human embryo (hESC) | 1,529 | -- | scRNA-seq | No | Chu et al., 2016 (E-MTAB-3929) |
| Synthetic | 1,000 | 200 | Simulated (10 TFs each) | N/A | Generated by authors |

#### Evaluation Metrics

- **Phase portrait quality**: Intra-class distance (lower = better cell-type clustering on phase portrait), inter-class distance (higher = better cell-type separation)
- **Velocity stream quality**: Cross Boundary Direction Correctness (CBDir), In-Cluster Coherence (ICCoh)
- **Synthetic recovery**: Spearman correlation of inferred vs true weights and velocities, F1 score and AUROC for weight sign detection

#### Synthetic Data Validation

The authors generate ground truth data with 200 genes, 10 TFs per gene, and 1000 cells, using known weight matrices and sinusoidal profiles.

| Metric | Value |
|--------|-------|
| Weight recovery (Spearman $\rho$) | 0.823 |
| Velocity estimation (Spearman $\rho$) | 0.894 |
| Weight sign detection (F1) | 0.944 |
| Weight sign detection (AUROC) | 0.962 |

These results confirm that the EM algorithm can faithfully recover both TF regulatory weights and the true velocity from noisy observations.

#### Pancreas Dataset (3,696 Cells)

**Phase portrait quality**: TFvelo achieves significantly lower intra-class distance ($p = 4.23 \times 10^{-51}$, paired $t$-test on 405 genes) and significantly higher inter-class distance ($p = 5.65 \times 10^{-117}$) compared to unspliced/spliced-based phase portraits. This demonstrates that TF-target space provides dramatically cleaner gene dynamics than $u$-$s$ space.

**Velocity coherence**: CBDir and ICCoh are comparable to UniTVelo, the best-performing existing method, and significantly better than scVelo, Dynamo, and CellDancer. TFvelo and UniTVelo both achieve ICCoh of approximately 0.97, reflecting the advantage of top-down gene profile approaches.

**Biological validation**:
- **REST** identified as the most influential TF (approximately 90 target genes with $|\tilde{w}| > 0.5$), with consistently negative weights on insulin secretion pathway genes -- confirming its known role as a negative regulator of endocrine differentiation.
- **HMGN3** identified as the second most influential TF, with consistently positive weights on insulin secretion genes -- consistent with its established role as a regulator of insulin secretion.
- KEGG enrichment of best-fitted genes yields insulin secretion pathway and glucagon signaling pathway as top hits.

#### Gastrulation Erythroid Dataset (9,815 Cells)

**Trajectory inference**: TFvelo correctly captures the blood progenitor to erythroid differentiation lineage (Blood progenitors 1/2 $\to$ Erythroid 1 $\to$ Erythroid 2 $\to$ Erythroid 3). Baseline methods show reversed flow (scVelo), fragmented streams (CellDancer), or noisy arrows (Dynamo).

**Robustness to sparse unspliced data**: The unspliced layer contains approximately 1000 genes with >90% zero entries. Conventional methods fail on these sparse genes; TFvelo produces clean elliptical phase portraits because it uses total expression rather than unspliced counts.

**Biological validation**:
- GO enrichment: heme biosynthetic process (GO:0006783), porphyrin-containing compound biosynthetic process (GO:0006779) -- directly relevant to erythroid development.
- Top TFs: GATA1 (approximately 186 targets), GATA2 (approximately 130 targets), LMO2 -- all well-established master regulators of erythropoiesis.

#### 10x Mouse Brain Dataset (3,365 Cells, Multi-Omics)

TFvelo is compared against MultiVelo, which integrates both RNA and ATAC-seq data. Despite using only RNA, TFvelo achieves remarkably similar pseudotime patterns and velocity streams. On individual genes:
- **AHI1**: MultiVelo mistakenly fits cyclic dynamics; TFvelo correctly captures monotonic increase from V-SVZ cells.
- **NTRK2**: TFvelo captures the complete dynamic including an initial decrease that MultiVelo misses.
- **GRIN2B**: Both methods agree on increasing dynamics.

This demonstrates that TF regulation can serve as a proxy for chromatin accessibility in modeling gene dynamics.

#### Human Embryo Dataset (1,529 Cells, No Splicing Information)

This is TFvelo's most distinctive benchmark. The dataset (Chu et al., 2016; E-MTAB-3929) contains expression from human preimplantation embryos (E3-E7) without any splicing annotation. All conventional velocity methods are inapplicable.

TFvelo successfully infers:
- Correct developmental trajectory: E3 $\to$ E5 $\to$ E6 $\to$ E7
- Temporally structured gene expression waves in a heatmap of the top 300 genes ordered by pseudotime
- Biologically validated individual gene dynamics:
  - **PPP1R14A**: expression rises then falls, peaking around day 5 -- consistent with zebrafish developmental expression patterns
  - **RGS2**: decreasing expression from early to late -- consistent with known early embryo role
  - **GSTP1**: monotonically increasing expression through development

#### Compared Methods (Full Table)

| Method | Journal | Year |
|--------|---------|------|
| velocyto | *Nature* | 2018 |
| scVelo | *Nature Biotechnology* | 2020 |
| UniTVelo | *Nature Communications* | 2022 |
| Dynamo | *Cell* | 2022 |
| CellDancer | *Nature Biotechnology* | 2023 |
| VeloAE | *PNAS* | 2021 |
| VeloVI | *Nature Methods* | 2023 |
| MultiVelo | *Nature Biotechnology* | 2023 |
| veloVAE | bioRxiv | 2022 |
| Pyrovelocity | bioRxiv | 2022 |
| LatentVelo | bioRxiv | 2022 |
| Palantir (TI) | *Nature Biotechnology* | 2019 |

---

### 4. Reproducibility Assessment

#### Rating: 4/5

#### Strengths

- **Code availability**: Complete source code on GitHub with demo scripts for all four biological datasets and the synthetic validation.
- **Framework compatibility**: Built as a modified fork of scVelo, inheriting a well-established preprocessing and visualization ecosystem.
- **Default parameters**: All key hyperparameters documented in argparse with sensible defaults (`max_iter=20`, `max_n_TF=99`, `n_time_points=1000`, `WX_thres=20`, `init_weight_method=correlation`).
- **TF database included**: ENCODE and ChEA database files are provided in the repository (ENCODE as a zip archive, ChEA as a text file).
- **Preprocessed data**: The 10x mouse brain dataset is provided as preprocessed `.h5ad` files.

#### Blockers and Limitations

- **Hardcoded relative paths**: TF database loading expects `ENCODE/processed/` and `ChEA/ChEA_2016.txt` relative to the working directory. Users must decompress `ENCODE.zip` before running.
- **No environment specification**: No `environment.yml` or `requirements.txt` provided. Dependencies must be inferred from the README: Python 3.8.12, scvelo 0.2.4, pandas, anndata, scanpy, numpy, scipy, numba, matplotlib.
- **External data downloads required**: The human embryo dataset (E-MTAB-3929) must be manually downloaded from EMBL-EBI and converted to AnnData format. The pancreas and gastrulation erythroid datasets are loaded via scVelo's built-in dataset loaders.
- **Computational cost**: Per-gene TF weight optimization is slower than scVelo. The parallelization across CPU cores helps but runtimes are not systematically benchmarked in the paper.
- **Python version constraint**: README specifies Python 3.8.12 specifically, which may conflict with newer system environments.

#### Key Command-Line Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset_name` | `pancreas` | Dataset to analyze (`pancreas`, `gastrulation_erythroid`, `10x_mouse_brain`, `hesc1`) |
| `--max_iter` | `20` | Number of EM iterations per gene |
| `--max_n_TF` | `99` | Maximum TFs considered per target gene |
| `--n_time_points` | `1000` | Grid density for latent time assignment |
| `--WX_thres` | `20` | Bound on TF weights ($|w_i| \leq 20$) |
| `--init_weight_method` | `correlation` | Weight initialization method (options: `correlation`, `knockTF_Log2FC`) |
| `--WX_method` | `lsq_linear` | Weight optimization solver |

#### Quick Start

```bash
# Create environment
conda create -n TFvelo_env python=3.8.12
conda activate TFvelo_env
pip install pandas anndata scanpy numpy scipy numba matplotlib scvelo

# Prepare ENCODE database
cd TFvelo/
unzip ENCODE.zip

# Run recovery (preprocessing + dynamics fitting)
python TFvelo_run_demo.py --dataset_name pancreas
# Output: TFvelo_pancreas_demo/rc.h5ad

# Run analysis (velocity, pseudotime, stream plots)
python TFvelo_analysis_demo.py --dataset_name pancreas
# Output: TFvelo_pancreas_demo/TFvelo.h5ad, figures/
```

---

### Discussion & Limitations

#### Strengths Highlighted by Authors

- TFvelo constructs dynamics based on TF-target regulation rather than unspliced/spliced counts, addressing the fundamental signal insufficiency problem in RNA velocity.
- The sine function profile avoids a discrete switching time point, allowing modeling of non-monotonic dynamics starting from either up- or down-regulation.
- The learned TF weights provide interpretable biological insights, enabling identification of key regulators (e.g., REST as a repressor in pancreas, GATA1 as an activator in erythropoiesis).

#### Acknowledged Limitations

1. **Computational cost**: Learning TF weights per gene is slower than scVelo; larger datasets require more CPU cores for parallelization.
2. **Imperfect gene fitting**: Some genes cannot be well-fitted by the current sinusoidal model (see Supplementary Fig. S14 in the paper).
3. **Linear model constraint**: The linear weight model ($\mathbf{W}\mathbf{X}$) may be insufficient for complex nonlinear regulatory relationships.
4. **Unimodal restriction**: The fixed $\omega = 2\pi$ limits dynamics to a single peak and trough within $t \in [0, 1)$, preventing modeling of genes with bimodal or more complex temporal profiles.

#### Future Directions Proposed by Authors

- Replace the linear TF weight model with neural networks for nonlinear regulatory modeling.
- Explore alternative profile functions beyond sine to handle more diverse expression dynamics.
- Integrate Bayesian inference for uncertainty quantification.
- Extend to spatial transcriptomics and multi-omics data integration.
- Apply universal time inference across all genes simultaneously (as in UniTVelo).

---

### Key AnnData Slots After Recovery

| Slot | Content |
|------|---------|
| `adata.var["fit_alpha"]` | Amplitude parameter $\alpha$ per gene |
| `adata.var["fit_beta"]` | Baseline parameter $\beta$ per gene |
| `adata.var["fit_theta"]` | Phase offset $\theta$ per gene |
| `adata.var["fit_gamma"]` | Degradation rate $\gamma$ per gene |
| `adata.varm["fit_weights"]` | Learned TF weight vectors $\mathbf{W}_g$ per gene |
| `adata.varm["TFs_id"]` | TF indices per gene (from ENCODE/ChEA) |
| `adata.layers["velo_hat"]` | Raw velocity ($\mathbf{W}\mathbf{X} - \gamma y$) |
| `adata.layers["fit_t"]` | Gene-specific latent time per cell |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
