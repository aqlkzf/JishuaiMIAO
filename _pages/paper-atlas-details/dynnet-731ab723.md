---
layout: default
permalink: /paper-atlas/dynnet-731ab723/
title: "DynNet"
nav: false
description: "时间序列 scRNA-seq 在每个时点测到的是不同细胞，不能直接观察同一细胞的连续轨迹。DynNet 选择一小组驱动基因，把每个细胞表示为基因表达状态，并拟合一个随机微分方程（SDE），使模拟群体在终点稳定状态、比例和基因边缘分布上接近观测数据。 因此，DynNet 输出的是在所选基因、GRN 先验和损失假设下学到的随机动力系统。模拟轨迹、吸引子、势景和首次通过时间是模型推断，不是谱系追踪的直接观测；"
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
      <span>Nature Communications · 2026</span>
    </div>
    <h1>DynNet</h1>
    <p>Inferring stochastic dynamics by biophysical Neural ODE using single-cell transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-73257-z" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for DynNet">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/cetusdou/DynNet" target="_blank" rel="noopener noreferrer" aria-label="Open code for DynNet">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DynNet 方法解读：用带 GRN 先验的随机动力系统连接单细胞时间快照

### 任务与证据边界

时间序列 scRNA-seq 在每个时点测到的是不同细胞，不能直接观察同一细胞的连续轨迹。DynNet 选择一小组驱动基因，把每个细胞表示为基因表达状态，并拟合一个随机微分方程（SDE），使模拟群体在终点稳定状态、比例和基因边缘分布上接近观测数据。

因此，DynNet 输出的是**在所选基因、GRN 先验和损失假设下学到的随机动力系统**。模拟轨迹、吸引子、势景和首次通过时间是模型推断，不是谱系追踪的直接观测；不确定性也不只是测量误差，而被压缩进状态依赖的对角噪声。

### 核心模型

模型写作

$$
d\mathbf x=\mathbf f(\mathbf x)dt+\sigma(\mathbf x)d\mathbf W.
$$

漂移 $\mathbf f$ 用带符号 GRN 约束的 Hill 调控函数表示。对目标基因 $i$，激活边贡献饱和上升项，抑制边贡献饱和下降项，再减去线性降解：

$$
f_i(\mathbf x)=
\sum_{N_{ij}=1}a_{ij}\frac{x_j^n}{s_j^n+x_j^n}
+\sum_{N_{ij}=-1}b_{ij}\frac{s_j^n}{s_j^n+x_j^n}
-k_ix_i.
$$

这里 $a,b$ 是调控强度，$s$ 是 Hill 阈值，默认 $n=4$。`DynNet/models/dynnet.py:36-60` 实现主模型的 Hill 特征和漂移；`DynNet_Hard` 与 `EMT_Sim` 在 `100-119`、`146-170` 显式把正/负边 mask 乘到产生项。

### 一步模拟如何发生

源码的 Euler–Maruyama 更新是

$$
\mathbf x_{t+h}=\mathbf x_t+h\mathbf f(\mathbf x_t)+\sqrt h\,\mathbf D\odot\hat\sigma(\mathbf x_t)\odot\boldsymbol\epsilon,
\qquad \boldsymbol\epsilon\sim\mathcal N(0,I).
$$

主模型在 `DynNet/models/dynnet.py:68-76` 实现一步更新；`DynNet/utils/solver.py` 重复更新并把负表达截到零。代码学习的是逐基因对角噪声，没有完整的跨基因扩散协方差。

### 三阶段训练

#### 1. 调控权重

`train_omega()` 冻结噪声、阈值和 $D$，最小化终态漂移范数，使终末细胞靠近稳定点，并可加入 GRN 约束（`train/train.py:6-31`）。代码的 `drift_loss()` 是平均向量范数，而论文公式写成平方范数，属于实现差异。

更关键的是，主 `DynNet` 类虽然构造了正负 mask，却没有在 forward 中使用；`soft_constraint_loss()` 又对**先验中存在的边**选择权重后平方惩罚（`train/loss.py:56-61`）。这与论文“惩罚不支持或符号矛盾边”的文字并不自然一致。硬约束变体的 mask 路径更直接，软约束结果需谨慎解释。

#### 2. Hill 阈值与终态比例

`train_s()` 用 100 步模拟的最终状态与观测终态 GMM 比较。`weight_loss()` 根据各模拟点对 GMM 分量的责任度估计分量总权重，再与观测 mixture weight 做 MSE（`train/loss.py:11-53`; `train/train.py:33-62`）。它约束的是终点群体比例，不保证中间时刻分布已匹配。

#### 3. 状态依赖噪声

`train_variance_net()` 固定漂移参数，调整噪声网络和 $D$，比较模拟终态 KDE 与 GMM 的逐基因边缘分布 KL（`train/loss.py:63-95`; `train/train.py:65-92`）。默认积分网格固定为 0–20、步长 0.1；联合多基因分布只通过各维边缘间接约束。

### 六张主图的证据链

1. **图 1**：总流程，从时间快照、先验 GRN、漂移/噪声网络到分阶段训练、势景、转移路径、FPT 和扰动分析。
2. **图 2**：两基因 MISA 多稳态系统。展示稳定态、边缘分布、势景、决策区和速度场，并与 Neural ODE 比较快照数量变化下的误差。
3. **图 3**：七基因 BoolODE 分支系统。比较 PCA 轨迹、稳定态表达、速度场以及软/硬约束下的参数和收敛。
4. **图 4**：肝细胞发育。论文从势景和速度场得到状态转移网络、FPT 与 knockout 效应；本地 notebook 只覆盖其中一部分，且依赖作者绝对路径和预计算 streamplot。
5. **图 5**：EMT/MET 数据。用五基因系统重建 E、pEMT、IM、M 等状态和加权 GRN；本地有数据、checkpoint 与模型类，但没有完整图 5/6 分析 notebook。
6. **图 6**：EMT 的直接/间接最小作用路径、转移网络、参数敏感性与基因 knockout。对应的 MAP、action、FPT 和多数扰动源码在公开树中未找到，因此这些结果是 paper-reported 证据。

### 势景和转移分析应怎样理解

论文定义 $U(\mathbf x)=-\log P_{ss}(\mathbf x)$，局部低谷解释为稳定命运。公开 notebook 能以 GMM/PCA 密度构建 `-log` 势景，但论文描述的 Fokker–Planck、矩方程、投影高斯、最小作用路径和 FPT 没有完整可复用实现。不能因为论文有公式，就把公开代码的 notebook 势景说成已实现了整套解析近似。

### 论文—代码匹配

本地固定 commit 为 `0637cd0cd0f2c295f7e497cc6369734053a4dfbd`。核心 Hill/SDE 模型、Euler 求解器、三阶段损失和部分预训练资产真实存在，属于中等强度匹配。缺口包括：原始 scRNA-seq 到驱动基因/先验 GRN 的完整构建、论文收敛准则、MMD/F1 评估、moment-equation 势景、MAP/FPT、Neural ODE baseline 训练，以及完整 EMT 分析。

两个 notebook 也不是 turnkey：MISA 引用缺失的 `utils.load_data`；肝细胞 notebook 切换到作者机器的绝对路径，并读取预计算的 vector-stream `.npz`。所以当前仓库适合研究核心模型和部分演示，不能宣称一键复现论文全部主图。

### 使用时最重要的限制

- 结果高度依赖少量驱动基因和 prior GRN；遗漏调控因子会改变学到的动力系统。
- 快照分布匹配并不唯一确定细胞级路径，多个 SDE 可能解释相同边缘观测。
- 主模型的非负权重只在初始化时保证，优化后未再次投影；硬约束变体才在 force 中使用 `abs()` 与 mask。
- 代码只在终态施加若干损失，中间时点的时间一致性不能从公共训练函数自动推出。
- 势景、FPT 和 knockout 是模型生成的可检验假设，应由 lineage tracing、扰动或额外时间点验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DynNet Summary

### Motivation and Novelty

DynNet targets the problem of inferring stochastic cell-fate dynamics from time-course scRNA-seq snapshots. Because scRNA-seq destroys cells, the data do not contain direct single-cell trajectories. Existing fate-mapping and trajectory tools can order cells or infer terminal probabilities, but they often do not provide a gene-level dynamical model. The paper contrasts DynNet with Markov/fate methods such as CellRank (Nature Methods, 2022), Neural ODE methods such as scTour (Genome Biology, 2023) and DeepVelo (Science Advances, 2022), RNA-velocity approaches such as scVelo (Nature Biotechnology, 2020), and stochastic velocity modeling such as SDEvelo (Nature Communications, 2024).

The novelty is a biophysical Neural SDE whose drift is constrained by a signed gene regulatory network and parameterized with Hill functions. DynNet combines trainable activation/inhibition strengths, trainable Hill thresholds, a learned diagonal noise estimator, Gaussian-mixture state-weight matching, and energy-landscape interpretation. This makes the output more mechanistic than a black-box latent trajectory: stable states, transition paths, weighted GRNs, and in silico perturbation responses can be interpreted in the selected gene space.

### Method Overview

DynNet starts from scRNA-seq matrices measured at known experimental time points. A small set of driver genes defines the state vector $\mathbf{x}$, and a signed prior GRN defines activation, inhibition, or absent edges. The model learns an SDE:

$$d\mathbf{x}=\mathbf{f}(\mathbf{x})dt+\sigma(\mathbf{x})d\mathbf{W}.$$

The drift $\mathbf{f}(\mathbf{x})$ is a Hill-function regulatory model with activation weights $A$, repression weights $B$, thresholds $S$, and degradation $k$. The noise network estimates state-dependent per-gene diffusion. Training is staged: fit regulatory weights with drift and prior-constraint losses, fit thresholds with GMM state-weight matching, then fit noise with KL divergence between observed and simulated gene marginals. After training, simulations are converted into landscapes, velocity fields, transition networks, first-passage-time estimates, and perturbation predictions.

### Evaluation

The paper evaluates DynNet in four settings. On a two-gene MISA system, DynNet recovers three stable states, marginal distributions, decision boundaries, and velocity fields, and shows lower velocity-field MSE than a Neural ODE baseline across 2, 3, and 5 snapshots. On a 7-gene BoolODE branching system, it reconstructs bifurcation dynamics and shows how hard and soft GRN constraints affect convergence and learned regulatory weights.

For hepatocyte differentiation, DynNet reconstructs a landscape with mature hepatocyte-like and liver-bud attractors, estimates transition networks and first-passage times, and predicts marker-gene knockout effects. For EMT/MET data, it reconstructs E, M, pEMT, and IM states, infers a five-gene weighted GRN, and uses transition-action and perturbation analyses to highlight CDH1/CD44-related effects.

### Reproducibility

Rating: **3/5**.

The public repository includes the core model, losses, solver, bundled data, and checkpoints, and the main SDE/Hill/loss implementation matches the paper at medium fidelity. However, it is not a turnkey reproduction package. The MISA notebook imports a missing `utils.load_data` helper, the hepatocyte notebook uses an author-specific absolute path and a precomputed vector-stream file, and reusable source for moment-equation landscapes, minimum-action paths, FPT, EMT Figure 6 analyses, and several knockout workflows was not found. The core method can be studied and partly reproduced from code, but the full paper workflow requires notebook repair or unavailable analysis scripts.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
