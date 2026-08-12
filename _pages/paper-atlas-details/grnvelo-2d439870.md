---
layout: default
permalink: /paper-atlas/grnvelo-2d439870/
title: "GRNvelo"
nav: false
description: "GRNvelo 把细胞状态变化建模成两层系统： 论文中的完整概念流程是： 代码中可验证的主流程更窄一些： 也就是说，本地代码直接验证了 density -> TC-PINN -> MP-PINN 这个核心训练流程；AE 训练、扰动、评价指标和高维 GRN 恢复没有在主脚本中串起来。"
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
      <span>Molecular Systems Biology · 2026</span>
    </div>
    <h1>GRNvelo</h1>
    <p>Multiscale learning of gene network-driven phenotypic dynamics of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s44320-026-00220-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GRNvelo 方法中文讲解

### 证据边界

这份文档基于三类证据：

1. 论文正文：`paper source/nature_html/paper.md`，重点是 Overview、Methods、Evaluation、Perturbation、GRN inference 部分。
2. 本地代码：`code/GRNvelo`，commit `4f53e91368644a6b5b8cf28cce6fb1c2fbbbb422`。
3. 本地图片：`paper source/nature_html/images/figure_01.png` 到 `figure_07.png`。

需要先明确一个边界：论文中的核心模型，即密度估计、TC-PINN、MP-PINN，在可见代码中有直接实现；但论文中的完整 perturbation 脚本、评价指标脚本、合成数据生成脚本，以及 `torch.linalg.pinv` 的高维 GRN 恢复实现，在当前可见仓库中没有找到。

### 这篇论文要解决什么问题

单细胞时间序列数据通常只有几个离散时间点，例如 D0、D1、D2 等。研究者希望从这些快照里回答几个问题：

- 细胞从一个状态转到另一个状态的速度是多少？
- 每个细胞处在连续发育过程的什么位置，也就是 latent time 是多少？
- 哪些基因调控关系驱动了这种状态变化？
- 细胞群体的增长、死亡、扩张和密度变化怎样影响轨迹？
- 如果敲除某个基因，或者改变药物组合，细胞命运会怎样改变？

传统 pseudotime 方法可以给细胞排序，但通常不能解释驱动轨迹的动态 GRN。很多轨迹或 optimal transport 方法可以预测群体迁移，但不一定能把速度场解释成基因调控网络产生的速度。GRNvelo 的核心目标就是把这两层连接起来：用 GRN 解释单细胞速度，再用群体 PDE 约束细胞密度和增长。

### 一句话理解 GRNvelo

GRNvelo 把细胞状态变化建模成两层系统：

```text
单细胞层面：
    基因调控 ODE 产生 GRN velocity V(x)

群体层面：
    细胞密度 rho(x,t) 被 V(x) 推动，同时受扩散 D 和增长 g 影响

算法层面：
    TC-PINN 先学 V(x) 和 latent time
    MP-PINN 再用 density / growth / PDE 约束修正 V(x,t)
```

论文中的完整概念流程是：

```text
高维 scRNA-seq
    |
    v
AutoEncoder 得到低维 embedding
    |
    v
TC-PINN：学习 GRN velocity + latent time
    |
    +--> DensityGeneration：估计每个时间点的细胞密度
    |
    v
MP-PINN：用 density / growth / PDE 约束修正速度
    |
    v
输出 velocity, trajectory, growth, GRN, latent time, perturbation trajectory
```

代码中可验证的主流程更窄一些：

```text
model/Train_GRNvelo.py
    -> DensityGeneration.main(args)
    -> VelocityGeneration.main(args)
    -> VelocityRefine.main(args)
```

也就是说，本地代码直接验证了 density -> TC-PINN -> MP-PINN 这个核心训练流程；AE 训练、扰动、评价指标和高维 GRN 恢复没有在主脚本中串起来。

### 变量和数据结构

论文把每个细胞状态写成：

$$
x(t)=(x_1(t),x_2(t),\ldots,x_d(t))\in \mathbb{R}^d
$$

这里的 $d$ 在论文表述中是基因维度；但高维数据会先经过 AE 降维，所以实际训练常在低维 embedding 空间中进行。代码里的 `data`、`data_cat_i`、`samples_x` 基本就是这个低维细胞状态。

主要变量：

| 符号 | 含义 | 代码对应 | 说明 |
|---|---|---|---|
| $x(t)$ | 细胞状态向量 | `data`, `data_cat_i`, `samples_x` | 通常是降维后的表达 embedding |
| $t$ | 时间或 latent time | `self.t`, `time_scale` | TC-PINN 用 0 到 1 的 2000 点网格 |
| $V(x)$ | GRN velocity | `net_f2()[1]`, `net_v` | TC-PINN 先给出参考速度，MP-PINN 再修正 |
| $\rho(x,t)$ | 细胞密度 | `dens_allcell.pkl`, `net_rho` | 密度估计后作为 MP-PINN 训练目标 |
| $g(x,t)$ | 增长率 | `net_g`, `pre_g` | MP-PINN 学到的增长项 |
| $a_{ij}$ | 激活强度 | `self.a` | TC-PINN 中的可训练参数 |
| $b_{ij}$ | 抑制强度 | `self.b` | TC-PINN 中的可训练参数 |
| $K_{ij}$ | Hill 函数半饱和参数 | `self.K1`, `self.K2` | 激活和抑制各有一套 |
| $h_{ij}$ | Hill 指数 | 固定为 2 | 代码没有找到可训练或可配置的 $h_{ij}$ |
| $d_i$ | 降解率 | `self.d` | TC-PINN 中的可训练参数 |
| $D$ | 扩散系数 | `self.D` | MP-PINN 中可训练 |
| $M$ | carrying capacity | `self.M` | MP-PINN 中可训练 |

### 第一层模型：GRN 产生单细胞速度

论文首先定义一个 Hill-kinetics ODE。对第 $i$ 个基因或 embedding 坐标：

$$
\frac{1}{\varepsilon^2}\frac{d x_i}{d\widetilde t}
=
\sum_j\left(
a_{ij}\frac{x_j^{h_{ij}}}{K_{ij}^{h_{ij}}+x_j^{h_{ij}}}
+
b_{ij}\frac{K_{ij}^{h_{ij}}}{K_{ij}^{h_{ij}}+x_j^{h_{ij}}}
\right)
-d_i x_i.
$$

这条式子可以这样理解：

- 第一项：如果 $x_j$ 激活 $x_i$，$a_{ij}$ 控制激活强度。
- 第二项：如果 $x_j$ 抑制 $x_i$，$b_{ij}$ 控制抑制强度。
- 第三项：$d_i x_i$ 是自身降解。
- 右边整体就是基因调控网络给细胞状态的变化速度。

论文把右边定义为 $V_i(x)$，也就是 GRN velocity 的第 $i$ 个分量。

代码对应：

- `VelocityGeneration.Latent_time` 初始化 `K1`, `K2`, `a`, `b`, `d`，并注册为神经网络参数。
- `net_x()` 用 root cell 和时间 $t$ 预测 $\hat{x}(t)$。
- `net_f2()` 用 autograd 计算 $d\hat{x}/dt$，再计算 Hill 激活、抑制、降解项，形成 ODE residual。
- 代码里的 Hill 指数固定为 2，这是论文一般形式 $h_{ij}$ 的一个具体实现，不是完全泛化形式。

### TC-PINN：同时学习 GRN velocity 和 latent time

TC-PINN 是第一阶段。它要做三件事：

1. 把细胞按 cluster-level lineage 分开。
2. 每条 lineage 选 root cell。
3. 对每条 lineage 训练一个 neural ODE/PINN，用它拟合连续轨迹、GRN velocity 和 latent time。

#### 1. cluster-level lineage

论文说，如果细胞有分叉，不同 lineage 应该有不同参数。它先按最终类别数 $m$ 把每个时间点的细胞分成 $m$ 类，再通过相邻时间点 cluster centroid 的欧氏距离把 cluster 串成 lineage。

代码中 `VelocityGeneration.cluster()` 使用 `GaussianMixture(n_components=num_cluster)` 对每个时间点聚类，然后根据 cluster center 距离对齐相邻时间点的 cluster。这个和论文思路一致。

#### 2. root cell

论文定义 root cell：在初始时间点 $t_1$ 中，找一个离 $t_2$ 细胞群最远的细胞。具体是每个 $t_1$ 细胞先算到所有 $t_2$ 细胞的最小距离，再选这个最小距离最大的细胞。

代码实现略有差异：`root_cell()` 计算初始细胞到后续 cluster center 的距离，对距离做归一化并跨时间求和，然后取最大值对应的细胞。这是相近但不完全相同的启发式。

#### 3. neural trajectory

TC-PINN 的神经网络输入是：

```text
[root cell expression, t]
```

输出是：

```text
x_hat(t)
```

也就是从 root cell 出发，在连续 latent time 上预测细胞状态。代码中 `self.t = torch.linspace(0, 1, 2000)`，所以 latent time 被离散成 2000 个候选点。

#### 4. TC-PINN loss

论文写的损失是：

$$
Loss=\lambda_1 Loss_{data}+\lambda_2 Loss_f+\lambda_3 Loss_{lt}.
$$

含义：

- $Loss_{data}$：预测轨迹 $\hat{x}(s_l)$ 要接近观测细胞。
- $Loss_f$：预测轨迹要满足 GRN ODE。
- $Loss_{lt}$：不同实验时间点对应的 latent time 应该大致单调，不应反向。

代码中分两阶段：

1. 早期训练：使用初始化的 latent time，`loss3=0`。
2. 后期训练：每个细胞重新分配到距离最近的 $\hat{x}(s_l)$，再统计不同实验时间点的 latent-time mode 是否出现反向。如果反向，加入惩罚。

重要实现细节：

- 论文写 $\lambda_1,\lambda_2,\lambda_3$ 默认 1 并网格搜索。
- 代码实际使用 `1 * loss1 + 0.1 * loss2 + 1 * loss3`。
- 所以 `Loss_f` 的权重在当前代码中是 0.1。

TC-PINN 的输出包括：

- 每个细胞的 discrete velocity：`velocity_allcell.pkl`。
- 每条 lineage 的 latent time：`latent_time*.pkl`。
- 相关可视化图。

### 密度估计：为 MP-PINN 提供 rho

论文在 reduced space 中估计每个时间点的密度 $\rho_{t_i}$。它使用一个 Gaussian mixture：每个观测细胞作为一个 Gaussian center，然后平均这些 Gaussian。论文还说最终密度乘以相对细胞数 $N_i/N_1$。

代码中：

- `DensityGeneration.MultimodalGaussian_density()` 对每个细胞中心建立多元正态分布并求和平均。
- `DensityGeneration.main()` 对每个时间点计算密度，保存为 `dens_allcell.pkl`。

差异：

- 代码中没有看到论文所说的 $N_i/N_1$ 相对丰度缩放。
- 因此密度估计核心形式匹配，但相对 population-size scaling 是 `Not found`。

### 第二层模型：MP-PINN 用群体动力学修正速度

MP-PINN 是第二阶段。它把 TC-PINN 得到的速度当成参考，同时加入群体密度和增长约束。

论文中的 population PDE 是：

$$
\partial_t\rho + \nabla_x\cdot(V\rho)
=
D\Delta_x\rho
+
\left(1-\frac{\int \rho(x,t)dx}{M}\right)g\rho.
$$

这条式子可以拆开理解：

- $\partial_t\rho$：密度随时间变化。
- $\nabla_x\cdot(V\rho)$：速度场推动细胞群在状态空间里移动。
- $D\Delta_x\rho$：随机扰动、epimutation 或噪声造成扩散。
- $\left(1-\frac{\int \rho dx}{M}\right)g\rho$：增长项，群体越接近 carrying capacity $M$，增长越受限制。

MP-PINN 的神经网络输出三个量：

```text
NN2(x,t) -> V_hat(x,t)
NNrho(x,t) -> rho_hat(x,t)
NNg(x,t) -> g_hat(x,t)
```

代码中对应 `net_v`, `net_rho`, `net_g`。

### MP-PINN loss

论文写：

$$
Loss=\gamma_1 Loss_\rho+\gamma_2 Loss_{V_{size}}+\gamma_3 Loss_{V_{direction}}+\gamma_4 Loss_F.
$$

四个部分：

1. $Loss_\rho$：预测密度 $\hat\rho$ 接近 GMM 估计密度。
2. $Loss_{V_{size}}$：预测速度大小接近 TC-PINN 速度大小。
3. $Loss_{V_{direction}}$：预测速度方向和 TC-PINN 速度方向一致。
4. $Loss_F$：预测的 $\hat\rho,\hat V,\hat g$ 满足 PDE residual。

代码中：

- `loss_rho = mean((samples_rho - pred_rho)^2)`。
- `loss_v_size = mean((samples_v - 10 * pred_v)^2)`。
- `loss_v_diret = mean(1 - cosine_similarity(samples_v, pred_v))`。
- `loss_f = mean(pred_f ** 2)`。
- 总损失是四项直接相加。

重要差异：

- 论文把 velocity scale 写成 $\kappa$，代码里是硬编码的 `10 * pred_v`。
- 论文写 $\gamma_1,\ldots,\gamma_4$ 默认 1 并可网格搜索，代码当前是固定四项权重都为 1。

### MP-PINN 如何生成 trajectory 和 growth

训练完成后，代码用 `net_v` 作为 ODE 右端项做积分：

```text
初始细胞状态 x(0)
    |
    v
dx/dt = V_hat(x,t)
    |
    v
连续轨迹 pre_x
```

同时保存：

- `pre_v_initialdata.pkl`：所有细胞的修正速度。
- `pre_g_initialdata.pkl`：预测增长。
- `pre_x.pt`、`pre_x_timepoints.pt`：预测轨迹。
- `pre_rho.pt`、`pre_g.pt`、`pre_v.pt`：采样细胞的密度、增长、速度。
- `gradg_alltime.png`：增长对输入维度的梯度。

这部分和论文 Figure 1、Figure 3、Figure 4 中的 velocity、trajectory、growth 输出最直接对应。

### 扰动预测和高维 GRN：论文有，代码证据不足

论文后半部分非常重要的一点是 perturbation prediction：

- 单基因 KO：把目标基因表达置零，再通过 normalized GRN 传播间接影响。
- 多基因 KO：同时把多个目标基因置零，再用对应的 NGRN 子矩阵传播影响。
- Erl+Criz/MET：在高维表达空间中模拟 Criz 对 MET 的作用，再投回 latent space 继续演化。
- dynamic combination：在 D1 到 D10 不同时间加入 Criz，看 D11 结果。

论文还说，高维 GRN 由低维 velocity 和 encoder Jacobian 的 pseudo-inverse 恢复，并且实现中使用 `torch.linalg.pinv`。

但是在当前可见代码中：

- 没找到 `torch.linalg.pinv`。
- 只在 bundled `TFvelo` 工具里找到一个 `np.linalg.pinv`，它不是论文这个高维 GRN 恢复公式的直接实现。
- 没找到 `NGRN`、`MET`、`Criz`、`Erl`、KO update 公式的主仓库脚本。

所以对这部分要保守理解：论文结果展示了这些扰动分析，但当前仓库没有提供可以直接核验的完整实现。

### 图像证据怎么理解

- Figure 1 是整体流程图，清楚展示 AE、TC-PINN、density、MP-PINN 和输出。
- Figure 2 显示 3-gene 和 10-gene 合成系统，包含 velocity、trajectory、latent time、growth、GRN heatmap 和 benchmark。
- Figure 3 是 pancreatic beta-cell 数据，展示 velocity、trajectory、latent time、growth 和 CBDir/ICCoh/Wasserstein 等指标。
- Figure 4 是 lineage tracing 数据，展示 Neu/Mo 分支、growth prediction 和 fate prediction。
- Figure 5 是 CD8 T cell 的 KLF2 KO 扰动预测。
- Figure 6 是 TCF7、LEF1、TCF7+LEF1 多基因 KO。
- Figure 7 是 NSCLC PC9 的 Erl/Criz/MET 药物扰动和动态组合治疗。

最强的代码支持来自 Figure 1 的核心流程和 Figure 3/4 中 velocity、trajectory、growth 这类主模型输出。扰动图和评价指标图主要是论文结果证据，当前可见代码无法完整复现。

### 如何从研究者角度学习 GRNvelo

可以按三层来学：

#### 第一层：先理解 ODE

记住一个核心：

```text
基因调控参数 a,b,K,d  ->  Hill kinetics  ->  GRN velocity V(x)
```

这解释了为什么 GRNvelo 的 velocity 不只是几何方向，而是被解释成 GRN 驱动的速度。

#### 第二层：再理解 latent time

TC-PINN 不只拟合曲线，还要给每个细胞找一个最合适的 latent time。它做法很直接：

```text
在 0 到 1 上生成很多候选时间点
    |
预测每个时间点的 x_hat(t)
    |
每个观测细胞找最近的 x_hat(t)
    |
这个 t 就是该细胞的 latent time
```

然后再用时间单调性惩罚避免实验时间点顺序被打乱。

#### 第三层：最后理解 PDE

MP-PINN 的意义是：单个细胞的速度不能随便学，必须和群体密度变化、增长、扩散一致。

也就是：

```text
如果速度场 V_hat 真的合理，
它推动 rho 的变化应该能解释观测到的密度变化；
同时 growth g 和 carrying capacity M 也要参与约束。
```

这就是 GRNvelo 比单纯轨迹方法更强调 multiscale 的原因。

### 结论

GRNvelo 的核心贡献是把单细胞 GRN ODE 和群体 PDE 接到一起，并用两个 PINN 阶段来学习：TC-PINN 负责 GRN velocity 和 latent time，MP-PINN 负责 density/growth/trajectory 约束下的速度修正。当前可见代码较好覆盖了这条核心主线，但对论文中最吸引人的 perturbation、高维 GRN 恢复和完整 benchmark 复现，证据不足，需要额外脚本或补充材料才能完全核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GRNvelo Summary

### Paper

- **Title:** Multiscale learning of gene network-driven phenotypic dynamics of single cells
- **Journal / year:** Molecular Systems Biology, 2026
- **DOI:** 10.1038/s44320-026-00220-x
- **Code:** https://github.com/SunXQlab/GRNvelo

### Problem

GRNvelo addresses the problem of reconstructing cell fate dynamics from temporal single-cell RNA-seq snapshots while identifying the gene regulatory networks that drive those dynamics. The paper argues that conventional pseudotime methods such as Monocle (Nature Biotechnology, 2014) and TSCAN (Nucleic Acids Research, 2016) can order cells but struggle with reversible, branching, and nonlinear transitions. It also argues that dynamical methods such as TrajectoryNet (PMLR, 2020), PRESCIENT (Nature Communications, 2021), MIOFlow (NeurIPS, 2022), TIGON (Nature Machine Intelligence, 2024), and PI-SDE (Bioinformatics, 2024) do not simultaneously connect intracellular GRN mechanisms, cell growth, latent time, and perturbation prediction. GRN-inference tools such as SCENIC (Nature Methods, 2017), SCODE (2017), and Dictys (Nature Methods, 2023) are discussed as useful but not sufficient for linking micro-scale regulatory interactions to macro-scale fate decisions.

### Method Overview

GRNvelo builds a multiscale ODE-PDE model. At the single-cell level, a Hill-kinetics ODE defines a GRN velocity field $V(x)$ from activation, inhibition, and degradation terms. At the population level, cell density $\rho(x,t)$ follows an advection-diffusion-growth PDE in which the same $V(x)$ transports density while diffusion and density-constrained growth shape phenotypic population dynamics.

The inference algorithm has two main phases. TC-PINN learns lineage-specific GRN velocity and latent time by fitting a neural trajectory $\hat{x}(t)$ to observed time-series cells while penalizing the GRN ODE residual and non-monotone latent-time assignments. MP-PINN then refines velocity with population constraints by learning $\hat V(x,t)$, $\hat\rho(x,t)$, and $\hat g(x,t)$ under density, velocity magnitude, velocity direction, and PDE residual losses. The paper also describes AE-based dimensionality reduction, high-dimensional GRN recovery, and in silico perturbations for single-gene KO, multi-gene KO, and dynamic drug combinations.

### Evaluation

The paper evaluates GRNvelo on two synthetic regulatory systems, additional stochastic/Gillespie-style simulations, and four real datasets: pancreatic beta-cell differentiation, murine hematopoiesis lineage tracing, acute LCMV CD8+ T cell differentiation, and NSCLC PC9 drug treatment. Reported comparisons include TrajectoryNet, MIOFlow, TIGON, PI-SDE, PRESCIENT, PBA, WOT, FateID, and multiple GRN inference baselines. Metrics include velocity magnitude MSE, velocity direction correlation, latent-time/real-time correlation, GRN AUROC, CBDir, ICCoh, Wasserstein distance, JS divergence, growth correlation, and fate prediction correlation. The main reported outcomes are strong synthetic latent-time correlations, favorable pancreatic trajectory metrics, competitive lineage-tracing fate/growth prediction, and plausible perturbation predictions for KLF2, TCF7/LEF1, and Erl+Criz/MET scenarios.

### Code and Reproducibility

The visible repository provides a runnable example for the central model. `model/Train_GRNvelo.py` runs `DensityGeneration`, `VelocityGeneration` (TC-PINN), and `VelocityRefine` (MP-PINN) in sequence. The source verifies the core density, ODE-residual, latent-time, PDE-residual, velocity, growth, and trajectory machinery.

Reproducibility is **medium** rather than high. The code includes AE helper modules, but the top-level script does not train or call them. The visible code differs from the paper in several implementation details: the TC-PINN Hill exponent is hard-coded to 2, TC-PINN loss weights are fixed as `1, 0.1, 1`, MP-PINN velocity-size loss uses a hard-coded factor of 10, root-cell selection uses cluster-center distances rather than the paper's exact all-cell t2 rule, and density estimation does not visibly apply the paper's relative abundance scaling. No visible implementation was found for the paper's metric scripts, perturbation update equations, synthetic-data generation, or claimed `torch.linalg.pinv` high-dimensional GRN recovery.

### Bottom Line

GRNvelo is a biologically interpretable framework for linking GRN-driven single-cell velocity to population-level fate dynamics with PINNs. The paper's core modeling idea is well represented in the visible TC-PINN and MP-PINN code, but the broader paper claims about perturbation analysis, high-dimensional GRN recovery, and full benchmark reproduction require additional scripts or supplementary materials not present in the checked repository.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
