---
layout: default
permalink: /paper-atlas/mioflow-24a0e542/
title: "MIOFlow"
nav: false
description: "MIOFlow 不把不同时间点的细胞强行一一配对。它先学习一个尽量保留数据流形距离的低维空间，再学习一个随时间变化的向量场，使起始细胞群沿该向量场移动后，在各观测时刻与对应的细胞群分布接近。 这里的“轨迹”是模型在群体分布约束下生成的可能路径，不是同一细胞被真实追踪得到的谱系。单细胞测序会破坏细胞，因此论文输入是若干独立的时间快照 X0,\\ldots,X{T-1}。"
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
      <span>NeurIPS 2022 · 2022</span>
    </div>
    <h1>MIOFlow</h1>
    <p>Manifold Interpolating Optimal-Transport Flows for Trajectory Inference</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2206.14928" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MIOFlow：从群体快照学习流形上的连续细胞轨迹

### 一句话理解

MIOFlow 不把不同时间点的细胞强行一一配对。它先学习一个尽量保留数据流形距离的低维空间，再学习一个随时间变化的向量场，使起始细胞群沿该向量场移动后，在各观测时刻与对应的细胞群分布接近。

这里的“轨迹”是模型在群体分布约束下生成的可能路径，不是同一细胞被真实追踪得到的谱系。单细胞测序会破坏细胞，因此论文输入是若干独立的时间快照 $X_0,\ldots,X_{T-1}$。

### 为什么普通欧氏最短路不够

如果细胞状态位于弯曲、分叉的低维流形上，环境空间中的直线可能穿过没有细胞支持的空白区域。论文为此定义多尺度 diffusion geodesic distance $G_\alpha$：从图扩散矩阵 $\mathbf P_\epsilon$ 出发，比较两个点在多个随机游走尺度上的转移分布。其理论目标是逼近流形测地距离的幂：

$$
G_\alpha(x_i,x_j) \simeq d_{\mathcal M}^{2\alpha}(x_i,x_j).
$$

随后训练 Geodesic Autoencoder（GAE）的编码器 $\phi$，让潜空间中的欧氏距离拟合这个目标：

$$
L_{\mathrm{GAE}}=
\frac{2}{N}\sum_i\sum_{j>i}
\left(\|\phi(x_i)-\phi(x_j)\|_2-G_\alpha(x_i,x_j)\right)^2.
$$

这样做的直觉是：先把弯曲道路“摊平”，再让神经 ODE 在这个空间中做最优传输。解码器 $\phi^{-1}$ 同时承担把潜空间轨迹还原到 PCA／基因空间的任务。

### 连续动力学与三个损失

向量场 $f_\theta(x,t)$ 给出细胞状态的瞬时变化方向：

$$
X_t=X_0+\int_0^t f_\theta(X_u,u)\,du.
$$

训练并不知道哪个终点属于哪个起点，所以比较的是预测群体 $\hat\mu_t$ 与观测群体 $\mu_t$，而不是细胞对。论文的核心目标包含：

1. 边缘分布损失 $L_m$：用 Wasserstein 距离要求预测群体匹配每个观测快照。
2. 能量损失 $L_e$：惩罚 $\|f_\theta(X_t,t)\|^2$，偏好较短、较平滑的输运路径。
3. 密度损失 $L_d$：若预测点离目标时刻的近邻过远，就施加 hinge 惩罚，减少穿越流形空白区的捷径。

因此，MIOFlow 的核心不是“先算出细胞配对再连线”，而是学习一个共享的连续向量场，使整群细胞在多个时间边缘上都对得上。

### 论文算法的局部与全局阶段

论文 Algorithm 1 明确区分两种训练：

- 局部阶段：以真实 $X_t$ 为初值，只预测相邻的 $\hat X_{t+1}$。
- 全局阶段：始终以 $X_0$ 为初值，一次积分得到所有后续 $\hat X_1,\ldots,\hat X_{T-1}$。

全局阶段很重要，因为仅在相邻区间上分别拟合，并不保证从同一个初始细胞出发的长程轨迹仍然一致。

### 论文图应如何阅读

Figure 1 从左到右给出完整逻辑：GAE 把流形几何编码到潜空间；神经网络接收状态和时间并输出导数；ODE 求解器把初始群体推进到下一时刻；Wasserstein 损失只在群体层面比较预测与观测。

Figures 2–3 的 Petal 与 Dyngen 实验检验“会不会抄直线捷径”和“能不能经过分叉”。论文图中 MIOFlow 的路径更贴近弯曲支路；Table 1 的留一时间点实验中，Petal 的 $W_1$ 为 0.090，Dyngen 为 0.783，均低于论文所列 TrajectoryNet 与 DSB。

Figure 4 展示 AML 处理中潜空间轨迹及 SLPI、B2M、MYB 的基因表达轨迹；Figure 5 比较 EB 神经元方向的 HAND2 和 ONECUT2 轨迹。它们说明解码器能把低维流还原成基因层面的假设轨迹，但这些曲线仍是模型推断，不是单细胞纵向实测。

### 当前代码实际做了什么

本工作区代码快照为提交 `206cc19ca89d985245ca204fbc86772e5c2446d0`，与论文算法存在实质差异：

#### 1. 几何目标是 PHATE 坐标距离，不是论文的 $G_\alpha$

`mioflow/gaga.py:335-413` 的 `fit_gaga()` 接收外部算好的 `X_phate`，标准化后直接计算两两欧氏距离。`train_gaga()` 再用 `torch.pdist(embedding)` 拟合这些距离（`gaga.py:197-215`）。代码没有构造论文定义的多尺度矩阵幂，也没有 $K$ 或 $\alpha$ 参数。因此只能说它保留 PHATE 坐标的几何，不能把论文关于 $G_\alpha$ 的收敛结论直接转移到当前实现。

GAE 采用两阶段训练（`gaga.py:70-132`）：先冻结 decoder，仅训练 encoder 的距离损失；再冻结 encoder，仅训练重构损失。这是当前实现的工程选择。

#### 2. 训练函数实际只有局部阶段

`mioflow/mioflow.py:458-528` 对每个相邻时间区间读取真实 `X_start` 和 `X_end`，分别调用 ODE/SDE 求解器，再立刻反向传播。虽然函数说明和进度条称其为 `global`，数据流符合论文的局部训练定义。代码没有从同一个 $X_0$ 一次积分并同时匹配全部后续快照的全局阶段。

#### 3. OT、密度与能量项的实现边界

- `core/losses.py:6-34` 构造平方欧氏代价矩阵并调用 `ot.emd2`；普通模式使用均匀质量。
- `core/losses.py:90-107` 对每个预测点取五个最近邻，把超过 `0.01` 的距离截断后求均值。这与论文公式的总体思想一致，但归约方式是当前代码的具体实现。
- `core/losses.py:36-88` 重新积分一条较密时间网格并求向量场平方范数，近似动力学能量。

当启用 growth-rate 模型时，代码过滤质量不超过 0.05 的源点，并把剩余质量归一化后仍调用 `ot.emd2`；它不是 Sinkhorn 求解。

#### 4. 当前 SDE 不是论文的每时间点标量扩散

论文描述学习 $T$ 个 $\sigma_t$，并报告它们训练后趋近于零。当前 `SDEFunc` 则用一个随 $(x,t)$ 变化的神经网络输出逐维对角扩散，再乘固定超参数 `diffusion_scale`（`core/models/sde_model.py:12-81`）。这比论文的标量形式更灵活，但并未实现或验证论文的“每时间点 $\sigma_t$ 学习并趋零”结论。

#### 5. 生成轨迹与解码

训练后，`_generate_trajectories()` 才从第一个时间点抽样，并在完整时间网格上连续积分（`mioflow.py:310-329`）。`decode_to_gene_space()` 依次执行 GAGA decoder、PCA 标准化逆变换和 PCA 逆投影（`mioflow.py:335-379`）。因此可得到连续基因空间曲线；但训练时的局部区间重置意味着，长程生成质量需要单独验证，不能由区间损失自动保证。

### 一个小例子

假设时刻 0、1、2 各有 100 个不同细胞。局部训练会用时刻 0 的真实细胞预测时刻 1，再重新用时刻 1 的真实细胞预测时刻 2；它可能把两个区间都拟合得很好。全局训练则必须把时刻 0 的同一批起点一直推进到时刻 2，所以会暴露误差累积和路径不连续。当前代码只优化前一种目标，却在训练完成后执行后一种长程生成；这是使用该快照时最需要注意的边界。

### 结论

论文方法的核心贡献是把流形几何、动态最优传输和神经 ODE 组合起来，用群体快照约束连续轨迹。当前代码保留了“自编码器 + OT/能量/密度损失 + ODE/SDE + 解码”这条主干，但把严格 diffusion geodesic 换成 PHATE 坐标距离，只保留局部区间训练，并改变了扩散参数化。理解或复现时应分别引用论文设计与代码行为，不能把两者混写成同一个已实现系统。

### 证据入口

- 论文：`paper source/paper/vlm/paper.md`，尤其 Section 3、Algorithm 1、Figures 1–5 与 Tables 1–2。
- 图像：`paper source/paper/vlm/images/`。
- GAE：`MIOFlow/mioflow/gaga.py`。
- ODE/SDE 训练：`MIOFlow/mioflow/mioflow.py`。
- 损失：`MIOFlow/mioflow/core/losses.py`。
- ODE/SDE 模型：`MIOFlow/mioflow/core/models/ode_model.py`、`sde_model.py`。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MIOFlow: Manifold Interpolating Optimal-Transport Flow

**Paper**: Manifold Interpolating Optimal-Transport Flows for Trajectory Inference
**Authors**: Guillaume Huguet, D.S. Magruder, Alexander Tong, Oluwadamilola Fasina, Manik Kuchroo, Guy Wolf, Smita Krishnaswamy
**Venue**: NeurIPS 2022 (arXiv:2206.14928)
**Code**: https://github.com/KrishnaswamyLab/MIOFlow

---

### Motivation & Novelty

**Biological problem**: Single-cell RNA sequencing is destructive — you cannot track the same cell over time. Researchers collect snapshot populations at multiple timepoints and want to reconstruct continuous individual cell trajectories, including bifurcations (one progenitor → two daughter types) and merges.

**Limitations of existing approaches**:
- **TrajectoryNet** (Tong et al., ICML 2020): Continuous normalizing flow (CNF) that requires starting from a Gaussian distribution. All intermediate distributions must be penalized relative to Gaussian rather than flowing directly between observed populations. CNF requires $O(k^2)$ Jacobian trace computation per step. Deterministic — cannot model intrinsic biological stochasticity.
- **Diffusion Schrödinger Bridge (DSB)** (De Bortoli et al., NeurIPS 2021): Optimal transport framework for generative modeling. Does not explicitly learn dynamics, making interpolations inaccurate for trajectory inference.
- **Waddington-OT** (Schiebinger et al., Cell 2019): Static OT method, does not learn continuous dynamics.
- **RNN-based methods** (Hashimoto et al., ICML 2016): Recurrent networks for population dynamics, less flexible than Neural ODEs.

**Unique contributions**:
1. **MIOFlow framework**: Neural ODE trained with OT loss on manifold-embedded data. Avoids Gaussian prior, avoids Jacobian trace, supports stochastic trajectories.
2. **Geodesic Autoencoder (GAE)**: Autoencoder whose latent space distances match a novel multiscale manifold distance (diffusion geodesic), enabling ODE training in a geometrically meaningful space.
3. **Diffusion geodesic distance** (Def 2): Multiscale distance based on diffusion matrix powers $\mathbf{P}_\epsilon^{2^k}$, proven to converge to geodesic distance on closed Riemannian manifolds (Theorem 2).
4. **Theoretical grounding**: Theorem 3 links the training objective (marginal matching + energy regularization) to dynamic optimal transport on the manifold.

---

### Method Overview

MIOFlow is a two-stage framework:

**Stage 1 — Geodesic Autoencoder (GAE)**:
- Trains an autoencoder to embed high-dimensional data into a latent space $\mathcal{Z}$ where Euclidean distances approximate manifold geodesics
- Two-phase training: Phase 1 trains encoder for distance preservation (using PHATE distances as proxy for diffusion geodesic); Phase 2 trains decoder for reconstruction
- Enables: (a) ODE training in geometrically meaningful low-dimensional space, (b) decoding trajectories back to gene space

**Stage 2 — Neural ODE Training**:
- Trains a time-conditioned MLP $f_\theta(x, t)$ as the derivative of trajectories
- Loss = OT marginal loss $L_m$ (Wasserstein between predicted and observed distributions) + energy regularization $L_e$ (kinetic energy of trajectories) + density loss $L_d$ (k-NN hinge to keep points near manifold)
- Optional SDE mode: adds a learned state/time-dependent diagonal diffusion network, scaled by a fixed hyperparameter; this differs from the paper's learned per-timepoint scalar $\sigma_t$
- Integrated via `torchdiffeq.odeint` (ODE) or `torchsde.sdeint_adjoint` (SDE)

**Key biological assumptions**:
- Cell populations lie on a low-dimensional Riemannian manifold
- Temporal snapshots are independent samples from the same underlying process
- Cells at different timepoints are not matched (no lineage tracing)

**Computational pipeline**: PCA → GAGA embedding → Z-normalize → Neural ODE training → trajectory integration → GAGA decode → inverse PCA → gene-space trajectories

---

### Evaluation

**Datasets**:
- **Petal** (toy): Synthetic bifurcating/merging trajectories on curved paths. Tests manifold-following behavior.
- **Dyngen** (simulated scRNA): Simulated single-cell data with one bifurcation, embedded in 5D PHATE. Asymmetric branching.
- **Embryoid Body (EB)**: Human embryoid body differentiation over 27 days, 5 timepoints, 17,846 genes, reduced to 200 PCA dims.
- **AML**: Acute myeloid leukemia treatment response, 3 timepoints (day 2, 5, 7), chemotherapy resistance analysis.

**Metrics**: Leave-one-out interpolation accuracy:
- $W_1$ (1-Wasserstein distance): lower is better
- MMD with Gaussian kernel MMD(G): lower is better
- MMD with mean kernel MMD(M): lower is better

**Quantitative results** (Table 1, Petal dataset, held-out timepoint 2):
| Method | W₁ | MMD(G) | Runtime |
|---|---|---|---|
| MIOFlow | **0.090** | **0.029** | 284s |
| TrajectoryNet | 0.181 | 0.136 | 64 min |
| DSB | 0.199 | 0.157 | 86 min |

MIOFlow achieves ~2× better W₁ and ~5× better MMD(G) vs TrajectoryNet, while being ~13× faster.

**Dyngen dataset** (Table 1): MIOFlow W₁=0.783 vs TrajectoryNet 1.499 vs DSB 2.051.

**EB dataset** (Table 2): GAE with α-decay kernel achieves W₁=25.744 at t=2 vs 29.243 without GAE, confirming the manifold embedding improves trajectory accuracy.

**Biological validation**: On EB data, MIOFlow correctly captures non-monotonic HAND2 expression (peaks in neural early progenitors then decreases) and higher ONECUT2 in neuronal lineage — both biologically validated. TrajectoryNet shows chaotic early divergence in these genes.

---

### Reproducibility Rating: 3/5

**Justification**: The core method is implemented and functional, but there are significant gaps between the paper and the released code.

**Strengths**:
- Clean Python package with clear API (`MIOFlow`, `fit_gaga`, `train_mioflow`)
- Jupyter notebooks for EB and SERGIO datasets
- Standard dependencies (PyTorch, torchdiffeq, POT, PHATE)
- Well-documented `pyproject.toml` with pinned versions

**Weaknesses**:
- **Diffusion geodesic not implemented**: The paper's central theoretical contribution (Def 2, Theorem 2) is replaced by PHATE distances in code. The exact multiscale formula $G_\alpha$ is not computed.
- **Global training phase missing**: Algorithm 1 specifies local pre-training followed by global full-trajectory training. The code's loop is labelled “global” but resets from each interval's observed `X_start`, so its actual data flow is local only.
- **Per-timepoint σ_t not learned**: Paper claims T learned diffusion parameters; code uses a single fixed scalar.
- **Evaluation metrics not in package**: W₁ and MMD must be computed externally.
- **No automated tests**: CI only checks installation, not functionality.

**Practical notes**:
- Install: `pip install -e .` or `conda env create -f environment.yml`
- Requires PHATE (`pip install phate`) and POT (`pip install POT`)
- GPU recommended for SDE mode (gradient clipping important: `grad_clip=1.0`)
- For EB data: run PCA to 200 dims first, then PHATE for GAGA distances
- Common pitfall: `adata.varm['PCs']` must be present for gene-space decoding
- The `obs_time_key` column must be sortable (factorized to integer indices internally)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
