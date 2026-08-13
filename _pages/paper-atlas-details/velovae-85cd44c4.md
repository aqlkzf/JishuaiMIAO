---
layout: default
permalink: /paper-atlas/velovae-85cd44c4/
title: "VeloVAE"
nav: false
wide: true
description: "VeloVAE 把每个细胞的 unspliced/spliced 计数看成 RNA 转录—剪接—降解 ODE 在某个未知发育时间的观测。编码器从全基因的 (u,s) 同时推断共享细胞时间 t 和连续细胞状态 c；解码器不自由生成表达，而是把 t,c 代入解析 ODE 解重建 (u,s)。因此潜变量具有明确动力学含义，也能用细胞状态调节转录率来表示分叉。"
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
      <span>PMLR · 2022</span>
    </div>
    <h1>VeloVAE</h1>
    <p>Variational Mixtures of ODEs for Inferring Cellular Gene Expression Dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1101/2022.07.08.499381" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for VeloVAE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/welch-lab/VeloVAE" target="_blank" rel="noopener noreferrer" aria-label="Open code for VeloVAE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## VeloVAE：用生化 ODE 约束时间与细胞状态的变分推断

### 1. 一句话理解

VeloVAE 把每个细胞的 unspliced/spliced 计数看成 RNA 转录—剪接—降解 ODE 在某个未知发育时间的观测。编码器从全基因的 $(u,s)$ 同时推断共享细胞时间 $t$ 和连续细胞状态 $c$；解码器不自由生成表达，而是把 $t,c$ 代入解析 ODE 解重建 $(u,s)$。因此潜变量具有明确动力学含义，也能用细胞状态调节转录率来表示分叉。

主论文是 Gu, Blaauw & Welch, “Variational Mixtures of ODEs for Inferring Cellular Gene Expression Dynamics,” ICML 2022, PMLR 162:7887–7901。本地 `paper.pdf` 包含附录；`paper_icml_published.pdf` 是会议版本。扩展预印本 “Bayesian Inference of RNA Velocity from Multi-Lineage Single-Cell Data” 加入了更多模型与比较。当前代码标称 setup.py 版本 0.1.4，但 `setup.cfg` 为 0.1.3-beta，且 README 明说这是为新版 Scanpy/AnnData 做过临时修补的 fork；没有记录 commit，不能当作精确原始发布快照。

### 2. 基础 RNA 动力学

对每个基因，经典模型为

$$
\frac{du}{dt}=\alpha-\beta u,
\qquad
\frac{ds}{dt}=\beta u-\gamma s,
$$

其中 $\alpha$ 是转录率，$\beta$ 是剪接率，$\gamma$ 是降解率。给定初值 $(u_0,s_0)$ 和经过时间 $\tau$，解析解为

$$
u(\tau)=u_0e^{-\beta\tau}+\frac{\alpha}{\beta}(1-e^{-\beta\tau}),
$$

$$
s(\tau)=s_0e^{-\gamma\tau}
+\frac{\alpha}{\gamma}(1-e^{-\gamma\tau})
+\frac{\alpha-\beta u_0}{\gamma-\beta}
(e^{-\gamma\tau}-e^{-\beta\tau}).
$$

`code/velovae/model/model_util.py` 的 `pred_su()` 直接实现解析解，并在 $\beta\approx\gamma$ 时使用极限形式避免除以接近零的数。这里没有逐细胞数值积分；训练主要是在不同潜在时间评估闭式解。

### 3. 为什么需要共享时间的变分推断

scVelo 可为不同基因分别拟合 latent time，但同一细胞可能因此得到互不一致的基因时间。VeloVAE 要求一个细胞的所有基因共享 $t_i$。论文附录说明：共享时间时，EM 的 E-step 归一化常数含 ODE 指数项嵌套在指数中的积分，通常无初等闭式解，因此不能简单复用逐基因 EM。

VeloVAE 使用 amortized variational inference：编码器一次读入全基因 $[u,s]$，输出

$$
q_\phi(t,c\mid u,s)
=q_\phi(t\mid u,s)q_\phi(c\mid u,s),
$$

再通过重参数化采样 $t,c$。训练最大化 ELBO，即重建似然减去 $t$、$c$ 与其先验之间的 KL 项。多捕获时间数据可用 capture time 构造更有信息的时间先验，但 capture time 只是粗实验时间，不等于真实发育时间。

代码 `vae.py:546-729` 构建完整 VAE；编码器接收 $2G$ 维拼接输入并输出时间/状态分布，`forward()`（`:797-875`）采样 $t,z$ 后调用受 ODE 约束的 decoder 重建 $u,s$ 和 velocity。

### 4. 从单一 ODE 到 ODE 混合

单个固定 $\alpha$ 的 ODE 难以表示同一时间附近不同细胞向不同谱系分化。VeloVAE 令转录率变为

$$
\widetilde\alpha_{ig}=\rho_{ig}\alpha_g,
\qquad
\rho_i=g_\theta(c_i)\in[0,1]^G.
$$

对每个细胞，$c_i$ 经 decoder 网络产生每个基因的转录调制 $\rho_{ig}$。不同细胞即使时间相近，也可有不同的有效转录率；解析 ODE 形式仍保持不变。这就是“variational mixture of ODEs”：不是离散挑选几个 ODE，而是由连续细胞状态生成一族细胞特异 ODE。

$\rho$ 是模型对转录强度的调制参数，不应直接等同于转录因子活性或调控因果边。$c$ 也不是实验细胞类型标签；论文展示其随时间平滑分支，说明它捕获到相关结构，但潜空间旋转和尺度并无唯一生物定义。

### 5. 两阶段训练与初始条件

若始终假设 $(u_0,s_0)=(0,0)$，潜时间和全局动力学较容易稳定，但对每个细胞未来状态的局部预测不准确。论文流程是：

1. 先以简单初始条件训练至收敛，估计全局时间、细胞状态和动力学；
2. 在潜时间上寻找每个细胞稍早窗口内的邻居，用 KNN/局部平均估计 $(u_0,s_0,t_0)$；
3. 固定或弱化潜变量更新，使用局部初值微调 ODE 参数。

当前 `vae.py` 的配置默认 `n_epochs=1000`、post training 500、`n_refine=20`、batch size 128，并有邻居窗口 `dt=(0.03,0.06)`；这些是当前代码默认值，不等同于论文每个实验的唯一配置。`use_knn`、`u0/s0/t0` 和 `_update_x0()` 负责第二阶段。

这种细化引入一个重要边界：局部 velocity 不再只由全局生成模型决定，也受潜时间邻域和 KNN 图影响。错误的时间排序或跨分支邻居会污染初值。

### 6. 三个需要区分的模型族

#### VanillaVAE

只推断共享时间，使用基因级固定动力学参数，适合近似单线性过程。它是判断 cell-state-dependent $\rho$ 是否必要的基线。

#### VAE / VeloVAE

推断时间和连续状态，由 $c$ 产生 $\rho$，支持平滑多谱系分叉。ICML 主论文的核心贡献主要对应 `code/velovae/model/vae.py`。

#### BrODE

`code/velovae/model/brode.py` 根据已知/推断细胞类型转换图，为不同类型使用不同 ODE 参数并沿树传播初值。它属于扩展预印本和后续代码功能，不能当作 ICML 论文中原始连续状态 VAE 的同义实现。

当前仓库还包含 discrete Poisson/NB、full variational Bayes、conditional VAE、velocity continuity loss 等开关；这些扩展有源码证据，但并非都在 ICML 2022 主论文中完整评估。

### 7. velocity 怎样得到

训练后，对于重建的 $u,s$，模型按 ODE 右端计算

$$
v_u=\rho\alpha-\beta u,
\qquad
v_s=\beta u-\gamma s.
$$

`code/velovae/model/velocity.py` 将训练结果写回 AnnData 并计算 velocity 图。velocity 的方向依赖拟合率、潜时间、局部初值和邻域投影；二维 stream plot 是图上的汇总可视化，不等于直接观测到逐细胞未来。

代码还提供可选 velocity continuity loss：`VAE.forward()` 可从当前预测状态继续解到未来 `t1`，比较未来状态/速度。但默认配置为 0，属于实现扩展边界。

### 8. 图与附录证据

- Fig. 1–2 说明问题、生成模型和变分推断思想。
- Fig. 3 对比 Basic 与 Full：完整模型同时推断 $t,c$，再由 $c$ 产生细胞/基因特异 $\rho$。
- Table 1 与附录 C 比较重建误差、似然和 capture-time 相关；held-out reconstruction 支持生成模型拟合，但更低 MSE 不自动等于 velocity 方向更真实。
- Fig. 4–6 展示 capture time、early repression、late induction、transcriptional boost 和多分支 velocity。
- Fig. 7–8 展示潜状态分支和不确定性；这是模型后验的结构，不是已知谱系真值。
- Fig. 9 给出运行时间；论文报告约 30K 细胞在 V100 上数小时，具体性能依赖版本和参数。

本地 `paper.pdf` 已包含附录 A–C，因此附录的 EM 论证、数据与完整指标可由 `paper.md` 核验；没有另一个独立 supplement Markdown。

### 9. 论文—代码映射

| 论文机制 | 当前源码 | 状态 |
|---|---|---|
| RNA ODE 解析解 | `model/model_util.py:180-217` | Confirmed |
| 共享时间 Basic VAE | `model/vanilla_vae.py` | Confirmed |
| 时间与细胞状态 encoder | `model/vae.py:38` 起、`:797-875` | Confirmed |
| $c\to\rho$ 的 ODE 混合 | `model/vae.py` decoder | Confirmed |
| ELBO、时间/状态 KL | `model/vae.py` risk/loss 路径 | Confirmed |
| KNN 初值与第二阶段微调 | `model/vae.py` train / `_update_x0` | Confirmed |
| BrODE 类型树动力学 | `model/brode.py`, `transition_graph.py` | Confirmed，但属扩展版本 |
| 离散 Poisson/NB、full-VB | `model/vae.py:759-795` 等 | Confirmed，但超出 ICML 核心 |
| 精确原始发布版本 | 当前无 Git 元数据；setup 版本冲突且为修补 fork | Not found |

### 10. 复现和解释边界

1. 模型仍假设给定 $t,c$ 后基因条件独立；它没有直接学习共调控网络。
2. $\beta_g,\gamma_g$ 等主要是全局基因参数，$\rho$ 吸收许多细胞特异变化；参数之间可能有尺度/识别性耦合。
3. 潜时间没有绝对单位，除非依赖 capture-time prior 和明确缩放；跨数据集率值不能直接比较。
4. 分叉来自连续潜状态和 decoder 灵活性，并不自动给出离散命运决定点或谱系概率真值。
5. KNN refinement 依赖已估时间与邻域，可能形成自我强化。
6. 当前 fork 有严格旧依赖约束：NumPy ≤1.23.5、pandas ≤1.5.3、scVelo ≤0.2.5；新版 AnnData/Scanpy 邻居存储改变会破坏旧路径。
7. `setup.py` 与 `setup.cfg` 版本不一致，又无 commit，因此只能把本地代码描述为“VeloVAE 派生快照”，不能断言为官方 v0.1.4 原样。

总体上，VeloVAE 的强项是把全基因共享时间、连续细胞状态和已知 RNA 生化动力学放进同一个生成模型。它比逐基因拟合更一致，也能表示分叉；但输出仍是条件于 ODE、先验、邻域和版本实现的统计推断，不是直接测得的真实细胞年龄或基因调控因果关系。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## VeloVAE: Variational Mixtures of ODEs for Inferring Cellular Gene Expression Dynamics

**Paper**: Yichen Gu, David Blaauw, Joshua Welch. *ICML 2022* (PMLR 162:7887–7901).
**Extended preprint**: "Bayesian Inference of RNA Velocity from Multi-Lineage Single-Cell Data" (bioRxiv 2022.07.08.499381).
**Code**: [github.com/welch-lab/VeloVAE](https://github.com/welch-lab/VeloVAE) (v0.1.4, PyPI package `velovae`)

---

### 1. Motivation & Novelty

#### Formal Problem Statement

Each cell $i$ is represented by a vector $X_i(t) \in \mathbb{R}^d$ parametrized by time $t$, governed by some differential equation plus noise. Only the vector $x_i := X_i(t_i)$ is observed at an **unknown** time $t_i$. The goal is two-fold: (1) recover the latent time $t_i$ for each cell, and (2) predict future states $X_i(t)$ for $t > t_i$. This is a problem of learning a dynamical system from observations with unknown times — a setting that has not been well-studied prior to this work.

#### Biological Problem

Single-cell RNA sequencing (scRNA-seq) captures a static snapshot of each cell, destroying it during measurement. Since cells develop asynchronously, inferring the temporal ordering and gene expression dynamics from these snapshots is a fundamental challenge. RNA velocity leverages the relative abundance of unspliced ($u$) and spliced ($s$) mRNA to predict the future transcriptional state of each cell.

#### Why EM is Intractable (Appendix A)

The authors prove that the EM algorithm cannot be easily applied when cell time is shared across genes. The posterior $p(t|\mathbf{x}; \theta)$ involves integrating $\exp(\exp(-ct))$ terms from the ODE solution, which has no elementary closed form. This intractability motivates the use of variational inference with an amortized encoder network.

#### Limitations of Existing Approaches

| Method | Journal / Year | Key Limitation |
|--------|---------------|----------------|
| RNA velocity (La Manno et al.) | *Nature*, 2018 | Steady-state assumption; fails for transient genes |
| scVelo (Bergen et al.) | *Nature Biotechnology*, 2020 | Gene-specific time (inconsistent across genes); constant $\alpha$; no bifurcation modeling |
| Diffusion Pseudotime (Haghverdi et al.) | *Nature Methods*, 2016 | Similarity-based only; no rates or directions |
| Monocle (Qiu et al.) | *Nature Methods*, 2017 | No mechanistic gene expression modeling |
| Neural ODEs (Chen et al.) | *NeurIPS*, 2018 | Require observed time labels |
| scVAE (Grønbech et al.) | *Bioinformatics*, 2020 | No ODE-constrained dynamics |
| VeloAE (Qiao & Huang) | *PNAS*, 2021 | Embeds steady-state velocity only; no joint time inference |

#### Unique Contributions

1. **Joint inference of global cell time and gene expression dynamics** using variational inference, bypassing the intractable EM problem that arises when time is shared across genes (proven analytically in Appendix A)
2. **Variational mixture of ODEs**: a latent cell state $\mathbf{c}$ modulates the transcription rate $\widetilde{\alpha} = \rho \alpha$ via a decoder network $g(\mathbf{c}; \theta_\rho)$, allowing continuous and bifurcating dynamics
3. **Biological interpretability**: latent variables have clear biological meanings — time ($t$) and cell state ($\mathbf{c}$) — constrained by known biochemistry of mRNA splicing

---

### 2. Method Overview

#### Algorithmic Framework

VeloVAE is a variational autoencoder whose decoder is constrained by the analytical solution of the RNA splicing ODE. Three model variants with increasing complexity:

| Variant | Class | Key Feature | Use Case |
|---------|-------|-------------|----------|
| **Basic (VanillaVAE)** | `VanillaVAE` | Constant $\alpha, \beta, \gamma$ per gene; infers time $t$ only | Simple linear dynamics |
| **Full (VAE)** | `VAE` | Latent cell state $\mathbf{c}$ modulates $\rho$; two-stage training with KNN refinement | Bifurcating dynamics |
| **Branching ODE (BrODE)** | `BrODE` | Explicit tree-structured dynamics with per-cell-type parameters; transition graph | Multi-lineage with known types |

#### Key Technical Components

- **Encoder**: MLP (500 → 250 neurons, BatchNorm, LeakyReLU, Dropout 0.2) outputs posterior $q(t|\mathbf{x})$ and $q(\mathbf{c}|\mathbf{x})$
- **Decoder**: ODE-constrained reconstruction using analytical kinetic function $F(t; \theta)$ with cell-state-dependent transcription modulation via network $g(\mathbf{c}; \theta_\rho)$
- **ODE**: Linear splicing kinetics $\frac{du}{dt} = \rho\alpha - \beta u$, $\frac{ds}{dt} = \beta u - \gamma s$ with analytical closed-form solution
- **Training**: Two-stage — (1) global dynamics with mixture of gene modes, (2) local velocity refinement using KNN-derived initial conditions
- **Full Variational Bayes (optional)**: Treats $\alpha, \beta, \gamma$ as random variables with learned posterior distributions for uncertainty quantification

#### Biological Assumptions

1. Gene expression follows two-step kinetics: transcription → splicing → degradation
2. Rates $\beta, \gamma$ are constant per gene across all cells; $\alpha$ varies via cell-state modulation $\rho \in [0,1]$
3. Genes are conditionally independent given time and cell state
4. Observation noise is Gaussian with gene-specific variance

---

### 3. Evaluation

#### Datasets

| Dataset | Cells | Genes | Cell Types | Time Points | Source |
|---------|-------|-------|------------|-------------|-------|
| Pancreatic Endocrinogenesis (PE) | 3,696 | 2,000 | 8 | 1 | Bastidas-Ponce et al., 2019 |
| Dentate Gyrus (DG1) | 2,930 | 800 | 14 | 1 | Hochgerner et al., 2018 |
| 10x Mouse Brain (MB1) | 3,365 | 1,000 | 7 | 1 | 10x Genomics |
| Erythroid (ET) | 9,815 | 1,000 | 5 | 7 | Pijuan-Sala et al., 2019 |
| Dentate Gyrus (DG2) | 18,213 | 2,000 | 14 | 2 | La Manno et al., 2018 |
| Mouse Brain Dev. (MB2) | 29,994 | 1,000 | 10 | 20 | La Manno et al., 2021 |

#### Metrics

- **MSE/MAE**: Reconstruction error (train and test)
- **Log-likelihood**: Generative model fit
- **$k_t$**: Spearman correlation of inferred time with capture time
- **Qualitative**: Velocity stream plots, phase portraits, cell state evolution

#### Key Results (Table 1 from paper)

| Dataset | Method | MSE | $k_t$ | $k_t$ (Informative Prior) |
|---------|--------|-----|--------|--------------------------|
| PE | scVelo | 2.107 | N/A | N/A |
| | Basic Model | 6.815 | N/A | N/A |
| | **VeloVAE** | **0.823** | N/A | N/A |
| DG1 | scVelo | 0.670 | N/A | N/A |
| | Basic Model | 0.574 | N/A | N/A |
| | **VeloVAE** | **0.243** | N/A | N/A |
| MB1 | scVelo | 10.160 | N/A | N/A |
| | Basic Model | 10.431 | N/A | N/A |
| | **VeloVAE** | **1.886** | N/A | N/A |
| ET | scVelo | 0.873 | -0.707 | N/A |
| | Basic Model | 0.246 | 0.802 | 0.802 |
| | **VeloVAE** | **0.151** | 0.622 | **0.855** |
| DG2 | scVelo | 1.385 | -0.158 | N/A |
| | Basic Model | 0.968 | 0.304 | 0.306 |
| | **VeloVAE** | **0.159** | 0.529 | **0.707** |
| MB2 | scVelo | 18.19 | -0.777 | N/A |
| | Basic Model | 2.295 | 0.621 | 0.629 |
| | **VeloVAE** | **0.152** | 0.870 | **0.897** |

VeloVAE achieves 2–120× lower MSE than scVelo across all datasets. On single-time-point datasets (PE, DG1, MB1), the Basic Model sometimes outperforms scVelo on MSE (DG1: 0.574 vs 0.670) but not always (PE: 6.815 vs 2.107), because scVelo fits each gene separately with $N \times G$ time parameters, essentially overfitting. On multi-time-point datasets (ET, DG2, MB2), scVelo produces anti-correlated time estimates ($k_t < 0$) while VeloVAE achieves strong positive correlations (0.5–0.9), further improved with informative priors.

#### Full Performance Table (Appendix C)

| Dataset | Method | MSE (Train, Test) | MAE (Train, Test) | LL (Train, Test) |
|---------|--------|--------------------|--------------------|------------------|
| PE | scVelo | 2.107, N/A | 0.423, N/A | -1702, N/A |
| PE | Basic | 6.815, 5.163 | 0.356, 0.351 | 271.71, 274.68 |
| PE | **VeloVAE** | **0.823, 0.616** | **0.191, 0.192** | **727.42, 717.20** |
| DG1 | scVelo | 0.670, N/A | 0.316, N/A | -2287, N/A |
| DG1 | **VeloVAE** | **0.243, 0.253** | **0.190, 0.194** | **237.63, 234.57** |
| MB1 | scVelo | 10.160, N/A | 0.947, N/A | -1779, N/A |
| MB1 | **VeloVAE** | **1.886, 1.942** | **0.392, 0.398** | **440.61, 440.65** |
| ET | **VeloVAE** | **0.151, 0.161** | **0.194, 0.196** | **67.36, 66.88** |
| DG2 | **VeloVAE** | **0.159, 0.163** | **0.120, 0.121** | **1797.30, 1791.32** |
| MB2 | **VeloVAE** | **0.152, 0.147** | **0.089, 0.091** | **926.98, 924.48** |

Note: scVelo cannot compute test metrics because it does not support out-of-sample prediction. VeloVAE's train/test performance is nearly identical, indicating strong generalization.

#### Gene-Specific vs Global Time Consistency (Table 2)

A key scVelo failure mode is inconsistency between gene-specific and global time:

| Dataset | Avg. Correlation (gene vs global time) |
|---------|---------------------------------------|
| PE | 0.262 |
| DG1 | 0.097 |
| MB1 | 0.226 |
| ET | 0.103 |
| DG2 | -0.008 |
| MB2 | -0.272 |

This low/negative correlation shows that scVelo's per-gene time estimates are mutually inconsistent, explaining its poor global time inference.

#### Qualitative Advantages

1. **Early repression / late induction genes**: VeloVAE correctly fits genes that scVelo systematically misorders (e.g., *Smoc1*, *Gng12*)
2. **Transcriptional boosts**: Cell-state-dependent $\rho$ captures time-varying transcription rates (e.g., *Hba-x*)
3. **Cell type bifurcations**: Models multi-lineage branching dynamics (e.g., PE four-way branching, MB2 neuron-oligodendrocyte split)
4. **Meaningful cell states**: 3D visualization shows continuous cell state evolution over time with branching at differentiation points
5. **Scalability**: Minibatch optimization; 30K cells in ~5 hours on V100 GPU

#### Compared Methods (from bioRxiv extended paper)

| Method | Journal / Year |
|--------|---------------|
| scVelo | *Nature Biotechnology*, 2020 |
| UniTVelo (Gao et al.) | *Nature Communications*, 2022 |
| DeepVelo (Chen et al.) | *Science Advances*, 2022 |
| cellDancer (Li et al.) | *Nature Biotechnology*, 2024 |
| PyroVelocity (Qin et al.) | bioRxiv, 2022 |
| VeloVI (Gayoso et al.) | *Nature Methods*, 2024 |

#### Interpretations & Limitations (from Discussion)

The authors offer three complementary interpretations of VeloVAE:
1. **Constrained distribution**: The ODE solution constrains the joint distribution of $u(t)$ and $s(t)$ to reflect prior biochemical knowledge
2. **Biologically meaningful VAE**: A VAE whose latent variables (time and cell state) have clear biological meanings by construction, rather than being arbitrary
3. **Two-of-three inference**: Given any two of {time, observations, dynamics}, the third can be inferred — VeloVAE uses observations + dynamics knowledge to recover time

**Acknowledged limitations**: The model assumes genes are conditionally independent given time and cell state. Relaxing this to infer co-regulated gene groups and modeling raw integer counts (rather than normalized continuous values) are identified as future directions.

---

### 4. Reproducibility Assessment

**Rating: 4/5** (Good)

#### Strengths
- Complete source code on GitHub with PyPI package
- Multiple reproducibility scripts for all compared methods
- Jupyter notebook example included
- All six datasets are publicly available (scVelo built-in or 10x Genomics)

#### Blockers / Concerns
- **Dependency pinning**: Strict version constraints (numpy ≤ 1.23.5, pandas ≤ 1.5.3, scvelo ≤ 0.2.5) may cause environment setup difficulties
- **Known compatibility issues**: GitHub issue #6 documents `adata.uns['neighbors']['indices']` breakage with newer Scanpy/AnnData versions
- **No automated tests**: No unit test suite; only comparison scripts
- **GPU required**: Training on large datasets (MB2) requires GPU and takes ~5 hours
- **Hardcoded paths**: Some reproducibility scripts reference specific file paths

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
