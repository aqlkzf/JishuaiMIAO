---
layout: default
permalink: /paper-atlas/mioflow2-fcd4dedd/
title: "MIOFlow2"
nav: false
description: "时间序列单细胞实验在每个时间点破坏性取样，无法连续观察同一个细胞。MIOFlow 2.0 接收多个时间点的细胞群体，学习一个连续动力系统，使早期细胞经积分后在观测时点匹配真实群体。它试图同时处理低维流形、随机分叉、增殖/死亡和空间微环境。 输出轨迹是模型在群体分布约束下生成的可能路径，不是实验追踪到的一一谱系。分布匹配得好也不自动证明某条单细胞路径真实存在。 普通欧氏空间可能让轨迹穿过细胞不存在的空区。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>MIOFlow2</h1>
    <p>MIOFlow 2.0: A unified framework for inferring cellular stochastic dynamics from single cell and spatial transcriptomics data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2603.22564" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MIOFlow 2.0 中文方法解读

### 它要从群体快照恢复什么

时间序列单细胞实验在每个时间点破坏性取样，无法连续观察同一个细胞。MIOFlow 2.0 接收多个时间点的细胞群体，学习一个连续动力系统，使早期细胞经积分后在观测时点匹配真实群体。它试图同时处理低维流形、随机分叉、增殖/死亡和空间微环境。

输出轨迹是模型在群体分布约束下生成的可能路径，不是实验追踪到的一一谱系。分布匹配得好也不自动证明某条单细胞路径真实存在。

### 1. GAGA：先建立保持流形几何的潜空间

普通欧氏空间可能让轨迹穿过细胞不存在的空区。论文用 GAGA 编码器 $E_\phi$，令潜空间距离逼近预计算的 PHATE 距离：

$$
\mathcal L_{\mathrm{geom}}=\operatorname{MSE}\left(
\|E_\phi(x_i)-E_\phi(x_j)\|_2,
D_{\mathrm{PHATE}}(x_i,x_j)\right).
$$

本地 `gaga.py` 先训练编码器保持距离，再训练 decoder 重构。主 `MIOFlow` 类并不自动训练 GAGA：调用者必须传入已训练模型；否则类直接使用 `adata.obsm[gaga_input_key]`，默认是 PCA（`MIOFlow/MIOFlow/mioflow.py:223-271`）。因此“运行 MIOFlow”不必然意味着使用了 PHATE 几何。

论文关于潜空间欧氏距离近似流形测地距离的结论依赖近似等距条件。实际网络只最小化有限样本距离误差，这是经验近似而非运行后的数学保证。

### 2. Neural ODE/SDE：定义连续且可随机的运动

确定性版本学习

$$
\frac{dZ_t}{dt}=f_\theta(Z_t,t),
$$

随机版本加入扩散：

$$
dZ_t=b_\theta(Z_t,t)dt+\sigma_\phi(Z_t,t)dW_t.
$$

漂移描述共同发育趋势，扩散允许相同初态产生不同终态。代码中 `ODEFunc` 是时间条件的 SiLU 网络；`SDEFunc` 分别实现漂移和对角扩散，扩散末端用 Softplus 保证非负（`core/models/ode_model.py:5-47`；`core/models/sde_model.py:4-81`）。SDE 训练使用 Euler 积分。

论文式 (13) 把 momentum 写成对历史速度的加权积分，代码只保留上一次函数求值：

$$
v\leftarrow\beta v_{\mathrm{prev}}+(1-\beta)f_\theta(Z_t,t).
$$

而且每个区间和能量计算前都会重置它。这是单步 EMA，不是完整历史积分；ODE 求解器的内部调用顺序还会影响“上一次”的含义。

### 3. 三类损失

总目标写为

$$
\mathcal L=\lambda_m\mathcal L_m+lambda_e\mathcal L_e+lambda_d\mathcal L_d.
$$

边缘匹配损失用 POT 的离散 EMD 比较预测群体和下一时间点群体，代价矩阵为潜空间平方距离（`core/losses.py:6-34`）。它约束分布，不建立固定细胞配对。

能量损失沿加密时间网格重新积分，惩罚漂移平方范数，并可选惩罚扩散平方范数（`core/losses.py:36-88`）。默认 `lambda_energy_g=0`，所以默认并不直接惩罚扩散能量。

密度损失取预测点到目标群体五个最近邻的 hinge 距离，减少落入空区（`core/losses.py:90-107`）。但类默认不启用它；现有 notebook 甚至在 `use_density_loss=True` 时设置 `lambda_density=0.0`，此时仍无贡献。

### 关键差异：名为 global 的代码实际按相邻区间训练

论文区分 local 与 global：local 从每个真实 $Z_t$ 预测 $Z_{t+1}$；global 应从 $Z_0$ 连续积分并同时匹配所有后续时点。

当前 `train_mioflow()` 虽在日志和 docstring 中称 global，却在每个 epoch 遍历相邻区间，每次重新读取该区间真实 `X_start`、`X_end`，重置 momentum，只积分 `[t_start,t_end]`（`mioflow.py:471-499`）。这正是 local 风格。未找到从最初群体递推到全部时间点的真正 global 训练目标。

训练后 `_generate_trajectories()` 确实从初始群体跨全时间范围积分，但那是生成阶段，不能把逐区间训练变成全局训练。因此旧文档中“global Exact、local Not found”的结论应当反转。

### 4. 生长率模型与非守恒质量

论文用正值网络 $h_\psi(z,t)$ 估计细胞的相对后代质量：小于 1 表示丢失，大于 1 表示扩增。代码先对相邻时间点求 unbalanced OT，取运输计划的源边缘作为目标质量，再以 MSE 预训练生长网络（`growth_rate.py:130-180,182-245`）。

实现有三条重要边界：

- 论文式 (16) 使用 KL 边缘散度，代码默认 `div='l2'`，优化问题不同。
- `ot_loss()` 把预测质量 `detach()` 后交给 EMD；虽然 optimizer 包含生长网络参数，主 marginal loss 不会沿质量权重更新它。
- 质量低于 0.05 的细胞被屏蔽；若全部低于阈值，OT 损失直接为零。

所以当前生长网络最明确的学习信号来自 UOT 预训练，不能简单说漂移、扩散和生长率由主目标完全联合学习。

### 5. 论文中的空间条件

论文从空间坐标构图，为每个细胞汇总：邻域细胞类型频率；目标受体表达乘邻居配体表达的 interaction potential；邻居表达 PCA 的均值。归一化、拼接、PCA 后得到空间向量 $x_s$，再分别编码基因和空间：

$$
z=[E_\phi(x_s),\;sE_\theta(x_g)].
$$

动力学学习发生在这个联合状态上。坐标只用于定义邻居，因此模型试图利用微环境摘要而非绝对位置。

本地 `3.01.02-Axalotl-spatial-feature-extraction.ipynb` 确实实现空间 kNN、配体—受体聚合和细胞类型邻域计数，写出 `LR_feats` 与 `celltype_nbrhood`。但当前 commit 没有完整论文空间链：

- 空间特征只有 notebook，没有库 API。
- 未找到 local expression niche 被完整接入最终空间向量的路径。
- `3.01.04-single-trajectory.ipynb` 当前加载的是 `data/sergio/SERGIO_sim_DS9.h5ad`，只训练基因 PCA/PHATE 的二维 GAGA。
- 它没有读取处理后的 axolotl 空间对象，也没有构造双 GAGA 的四维联合嵌入，更没有复现图 5 的空间特征解码。

因此旧文档所说“空间联合嵌入已在 notebook 确认”不成立。当前快照只有部分空间特征原型，缺少从特征到论文图 5 轨迹的完整实现链。

### 6. 五张主图提供什么证据

- 图 1 是概念架构：基因/空间输入、潜空间、生长/漂移/扩散网络和损失。它说明设计，不证明所有箭头均已完整实现。
- 图 2 说明空间邻域、细胞类型、配体—受体与邻域表达特征的构造。
- 图 3 比较 SERGIO 三分叉和 S 形轨迹。MIOFlow 更贴近采样流形是特定模拟与潜空间中的结果，不是普遍保证。
- 图 4 用 branching、dying、growing 模拟展示 SDE 和生长先验各自针对的失败模式。随机轨迹能分散并不等于分叉概率已经校准。
- 图 5 展示 axolotl 再生中的基因/空间嵌入和 NCAN:SDC3 趋势。它提出空间微环境候选，但没有通过邻域干预证明 MSN 邻域对命运的因果作用。

本地 Figure 1–5 图片均可直接查看，已与正文和图注交叉核对；旧 `figure_analysis.md` 关于“图片不可读”的说明已过时。

### 7. 输出与解码边界

训练后从最早时间点抽样初态，在 `n_bins` 个时间上积分，得到“时间 × 轨迹 × 潜维度”。若传入 GAGA 和 `adata.varm['PCs']`，`decode_to_gene_space()` 经 decoder、逆缩放和 PCA loading 映回近似基因空间（`mioflow.py:322-392`）。这些值依赖 PCA 和解码误差，不是精确计数；该 API 也不提供通用空间特征解码。

### 当前代码—论文结论

可确认实现包括 GAGA 两阶段训练、ODE/SDE、相邻区间 OT/能量/密度损失、生长率 UOT 预训练、轨迹生成和基因解码。主要缺口是：

- 所称 global 训练实际是 local 风格。
- 生长质量在 OT 中 detach。
- UOT 默认 L2 而论文为 KL。
- momentum 是单步 EMA 而非历史积分。
- 空间功能只有部分特征抽取，缺少完整联合建模链。
- axolotl 最终 notebook 的内容与文件名和论文案例不一致。
- 外部数据、已训练模型和关键行为未在本工作区端到端复算，也未见覆盖这些差异的自动化测试。

最可靠的定位是：当前仓库提供了可追踪的非空间 ODE/SDE 轨迹核心、生长率预训练和部分空间特征原型；论文提出的统一空间—随机—非守恒系统尚未在此 commit 中形成一条完整、一致、可复现的训练链。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MIOFlow 2.0: Summary

### Motivation & Novelty

**Biological problem**: Single-cell RNA sequencing captures population-level snapshots at discrete timepoints, but cells cannot be tracked continuously (destructive measurement). Reconstructing individual cell trajectories from these snapshots requires inferring continuous dynamics from static distributions.

**Why existing methods fall short**:
- **Waddington-OT** (Cell, 2019): Static OT between snapshots; no continuous time model; assumes mass conservation
- **TrajectoryNet** (ICML, 2020): Continuous normalizing flow with OT regularization; assumes mass conservation; no spatial context; deterministic
- **Flow Matching / OT-CFM** (arXiv, 2023): Fast but assumes straight-line paths in ambient space; ignores manifold geometry; no stochasticity
- **Riemannian Flow Matching** (arXiv, 2023): Addresses geometry but requires analytically-defined manifolds (not feasible for empirical single-cell data)
- **SpaTrack** (Cell Systems, 2025): Incorporates spatial coordinates but requires shared coordinate system across timepoints; discrete transport maps
- **NicheFlow** (NeurIPS, 2025): Models niche-level (not cell-level) trajectories; no manifold-constrained transport

**Unique contributions**:
1. First trajectory inference framework integrating spatial transcriptomics via derived spatial features (coordinate-system independent)
2. Unified framework combining manifold-constrained OT + Neural SDEs + growth rates + spatial conditioning
3. Theoretical guarantee (Theorem 1) connecting latent Euclidean OT to geodesic OT on ambient manifold
4. Momentum-based trajectory refinement for sparse temporal data

### Method Overview

MIOFlow 2.0 operates in four stages:

1. **GAGA autoencoder**: Encodes high-dimensional gene expression into a low-dimensional latent space (typically 2-4 dimensions) that preserves PHATE manifold geometry. Two-phase training: encoder learns PHATE-distance isometry, decoder learns reconstruction.

2. **Growth rate model**: Optional neural network $h_\psi(z,t)$ predicting cell proliferation/death rates. Warm-started via unbalanced optimal transport (UOT) between adjacent timepoints, then jointly trained with the dynamics model.

3. **Neural SDE/ODE training**: Time-conditioned neural network learns the vector field $f_\theta(z,t)$ (drift) and optionally $\sigma_\phi(z,t)$ (diffusion). Trained with three losses: Wasserstein-2 marginal matching, kinetic energy regularization, and kNN density hinge. Momentum smoothing ($\beta$) stabilizes trajectories in sparse regions.

4. **Spatial conditioning** (optional): Spatial features (cell type composition, ligand-receptor signaling, local expression niche) are extracted from neighborhood graphs, encoded by a separate GAGA autoencoder, and concatenated with gene embeddings. The joint embedding drives trajectory dynamics.

**Key biological assumptions**:
- Cell states lie on a low-dimensional manifold in gene expression space
- Developmental transitions follow geodesics on this manifold (minimum kinetic energy)
- Stochasticity is modeled as Brownian diffusion in latent space
- Spatial context is captured by neighborhood-aggregated features (not absolute coordinates)

### Evaluation

**Synthetic benchmarks (SERGIO simulator)**:
- Trifurcation dataset (100 genes, 500 cells, 3 terminal fates): MIOFlow 2.0 error 0.243 ± 0.202 vs SF2M-ODE 0.278, OT-CFM 0.298
- S-shaped dataset (1000 genes, 315 cells, cyclic + bifurcation): MIOFlow 2.0 error 0.082 ± 0.070 vs SF2M-SDE 0.115, OT-CFM 0.118
- Metric: mean distance from held-out test cells to nearest point on predicted mean branch trajectory

**Embryoid body (EB) dataset** (leave-one-out, 5 timepoints):
- Evaluated in GAGA 2D latent space; metrics: W1 (Wasserstein-1), MMD-G (Gaussian kernel), MMD-M (mean discrepancy)
- MIOFlow 2.0 best on held-out t=2 (W1: 0.4689 vs OT-CFM 0.4741, SF2M 0.4864) and t=3 (W1: 0.4101 vs OT-CFM 0.4612, SF2M 0.4667)
- Comparable on t=1 (all methods similar: ~0.80-0.87)

**Ablation study** (synthetic branching/dying/growing datasets):
- Base MIOFlow 2.0 (OT only): spurious trajectories between branches; fails on growing populations
- + Growth rate model: eliminates spurious cross-branch trajectories
- + Neural SDE: captures probabilistic branching; follows diverging manifold structure

**Axolotl brain regeneration** (spatial transcriptomics, 7 timepoints):
- 4 cell types: reaEGCs → rIPCs → IMNs → nptxEXs
- Spatial features: 3-hop 5-NN graph, 640 LR pairs (CellChat), 828-dim → 100-d PCA
- Key finding: NCAN:SDC3 ligand-receptor signaling increases along regenerative trajectory; only a subpopulation of terminal cells experiences high signaling
- Demonstrates spatial conditioning reveals microenvironmental drivers inaccessible to gene-expression-only methods

### Reproducibility

**Rating: 2.5/5**

**Justification**: The core Neural ODE/SDE, GAGA and growth pretraining paths are traceable. However, the function called global performs adjacent-interval local-style training, growth masses are detached from the main OT loss, and the spatial innovation is not connected into a complete local chain: the final axolotl notebook currently loads SERGIO rather than the processed axolotl object.

**Strengths**:
- Clean Python package with `pip install -e .`
- Tutorial notebooks for basic usage
- All core mathematical components implemented and verifiable
- SERGIO synthetic benchmarks reproducible with the library

**Weaknesses**:
- Spatial feature extraction (Algorithm 1) not in library — notebook-only
- Axolotl data not included; requires downloading from original paper (Wei et al., Science 2022)
- Local training mode (Algorithm 4) not exposed in `MIOFlow.fit()` API
- UOT uses L2 divergence in code vs KL in paper — minor discrepancy
- No automated tests beyond CI installation check

**Environment setup**:
```bash
conda env create -f environment.yml
pip install -e .
```
Key dependencies: `torch`, `torchdiffeq`, `torchsde`, `phate`, `pot` (Python Optimal Transport), `scanpy`

**Common pitfalls**:
- GAGA training requires precomputed PHATE distances — use `PointCloudDataset` or `RowStochasticDataset`
- Spatial features must be pre-computed and concatenated before GAGA encoding
- Growth rate model must be pretrained before passing to `MIOFlow`
- SDE training requires gradient clipping (`grad_clip=1.0`) for stability
- `adata.varm['PCs']` required for gene-space decoding

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
