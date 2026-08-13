---
layout: default
permalink: /paper-atlas/tigon-b7ba56c0/
title: "TIGON"
nav: false
description: "TIGON 接收多个真实采样时刻的单细胞转录组快照，把每个时刻的细胞看成状态空间中的一团“有质量的密度”，再学习两个随状态和时间变化的函数：细胞状态的速度场 \\mathbf v(x,t)，以及允许群体质量增加或减少的净增长率 g(x,t)。它用 Wasserstein–Fisher–Rao（WFR）动态非平衡最优传输把离散快照连接起来，因此不必像平衡最优传输那样强迫总细胞质量守恒。 论文：Sha et al."
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
      <span>Nature Machine Intelligence · 2024</span>
    </div>
    <h1>TIGON</h1>
    <p>Reconstructing growth and dynamic trajectories from single-cell transcriptomics data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-023-00763-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TIGON">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/yutongo/TIGON" target="_blank" rel="noopener noreferrer" aria-label="Open code for TIGON">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TIGON：同时重建细胞状态运动与群体增长

### 1. 一句话理解

TIGON 接收多个真实采样时刻的单细胞转录组快照，把每个时刻的细胞看成状态空间中的一团“有质量的密度”，再学习两个随状态和时间变化的函数：细胞状态的速度场 $\mathbf v(x,t)$，以及允许群体质量增加或减少的净增长率 $g(x,t)$。它用 Wasserstein–Fisher–Rao（WFR）动态非平衡最优传输把离散快照连接起来，因此不必像平衡最优传输那样强迫总细胞质量守恒。

论文：Sha et al., *Nature Machine Intelligence* 6, 25–39 (2024)，DOI `10.1038/s42256-023-00763-w`。本地论文正文和 Methods 位于 `paper source/paper/paper.md`；代码快照的主入口是 `TIGON.py`，核心实现是 `utility.py`。

### 2. 输入与输出

输入不是配对后的单细胞轨迹，而是

$$
(t_1,C^1),(t_2,C^2),\ldots,(t_T,C^T),
$$

其中 $C^i$ 是第 $i$ 个时刻观测到的不同细胞。由于测序会破坏细胞，模型不知道一个早期细胞与哪个晚期细胞对应。

代码要求每个时刻的数据已经投影到共同的低维空间。`utility.py:216-221` 从 `Input/<dataset>.npy` 读取按时刻排列的数组；论文 Methods 说明数据轴被缩放到 $[-2,2]$。仓库提供 simulation、lineage、EMT 和 bifurcation 四组预处理输入。EMT 的 autoencoder 是独立预处理步骤，代码在 `AE/` 和 `Notebooks/AE.ipynb`，不是 TIGON 动力学目标的一部分。

模型直接输出：

- $\mathbf v(x,t)$：状态 $x$ 在时刻 $t$ 的瞬时变化方向；
- $g(x,t)$：该状态附近的净增殖/死亡倾向；
- 沿速度场积分得到的连续轨迹和未观测时刻状态；
- $\partial v_i/\partial x_j$：速度 Jacobian，被论文解释为局部、动态的调控矩阵；
- $\partial g/\partial x_j$：增长率对各状态维度的梯度，用于排序增长相关方向或基因。

### 3. 为什么需要“非平衡”最优传输

平衡最优传输只能移动质量。若一个分支在晚期细胞更多，它必须从别处搬入额外质量，于是状态运动和真实增殖会混在一起。TIGON 在连续性方程中加入源汇项：

$$
\partial_t\rho(x,t)+\nabla\cdot\bigl(\mathbf v(x,t)\rho(x,t)\bigr)
=g(x,t)\rho(x,t).
$$

左侧描述密度随时间变化及由速度造成的流入流出；右侧允许局部质量产生或消失。$g>0$ 表示净增长，$g<0$ 表示净衰减。这里的 $g$ 是由快照分布反推的净效应，不能单独区分细胞分裂与死亡，也不是直接实验测量值。

WFR 代价同时惩罚移动和增长：

$$
W_{0,T}=T\int_0^T\int
\left(\lVert\mathbf v\rVert^2+\alpha |g|^2\right)\rho\,dx\,dt.
$$

论文主要检验 $\alpha=1$。代价防止模型任意制造质量或让细胞走不必要的长路；二者的相对权重决定“分布变化应该由移动还是增长解释”。

### 4. 从 PDE 到可训练的神经 ODE

沿特征轨迹 $dx/dt=\mathbf v(x,t)$，连续性方程可写成

$$
\frac{d\log\rho}{dt}=g-\nabla\cdot\mathbf v.
$$

这一步是 TIGON 的计算桥梁：不用在高维空间铺规则网格，而是对采样点同时积分位置、累计增长和对数密度变化。`utility.py:43-67` 的 `UOT.forward()` 正好返回三项：

1. `dz_dt = hyper_net1(t,z)`，即速度；
2. `g = hyper_net2(t,z)`，即增长；
3. `dlogp_z_dt = g - trace_df_dz(dz_dt,z)`，即 $g-\nabla\cdot\mathbf v$。

`trace_df_dz()` 在 `utility.py:70-78` 对每个维度调用自动微分，求速度 Jacobian 的迹。因而维度升高会增加计算和显存成本；论文也明确指出直接扩展到数千维会遭遇 ODE 刚性和内存问题。

### 5. 密度重建与训练目标

#### 5.1 离散细胞变成连续密度

每个观测细胞作为一个高斯中心，混合后得到该时刻的连续密度。`MultimodalGaussian_density()`（`utility.py:183-195`）逐个构造多元高斯并平均；`Sampling()`（`utility.py:199-213`）从真实细胞中心抽样并加高斯噪声。代码还按 $N_i/N_0$ 缩放晚期密度（`utility.py:279,290`），把观测细胞数比例作为质量信息。

这意味着输入细胞数必须能代表相对群体规模。若不同时间点的捕获率、测序深度或抽样方案不同，模型可能把技术采样差异解释成生物增长；论文要求可靠的批次校正、足够的细胞数和时间点。

#### 5.2 长程与相邻重建误差

训练从晚期密度采样，把点向后积分：一条路径回到第一个时刻，另一条只回到相邻前一时刻。模型比较回推密度与真实早期密度。`train_model()` 中 `L2_value1` 是回到初始时刻的长程误差（`utility.py:265-283`），`L2_value2` 是相邻时刻误差（`utility.py:285-298`）。组合两者既约束整体漂移，也约束局部动态。

#### 5.3 总损失

代码实际损失为

$$
L=W+10^4(R_{\mathrm{long}}+R_{\mathrm{short}}).
$$

重建误差的 $10^4$ 权重直接写在 `utility.py:283,298`。WFR 积分在 `trans_loss()` 和 `train_model()` 的 `utility.py:231-243,301-307` 中计算，其中速度平方与增长平方乘累计增长权重。代码用 `torchdiffeq` 的 midpoint 积分代价，用 TorchDiffEqPack 的 Dopri5 回推密度。

密度带宽从 `sigma_now=1` 开始；当训练已进行且误差足够低时每 100 次迭代减半，最低约 0.02（`TIGON.py:66-70`，`utility.py:310-312`）。这是从平滑到精细的优化策略，并非生物噪声参数的估计。

### 6. 两个神经网络学什么

`UOT` 包含两个独立网络：

- `HyperNetwork1`（`utility.py:81-126`）接收 $[t,x]$，输出与 $x$ 同维的速度；隐藏层数由 CLI 的 `n_hiddens` 控制；
- `HyperNetwork2`（`utility.py:129-156`）接收同样输入，经过三层隐藏变换，输出一个标量增长率。

`TIGON.py:31-46` 创建模型，使用 Adam、weight decay 0.01 和分段学习率调度；`TIGON.py:67-89` 循环训练并定期保存检查点。命令行参数通过交互式 `input()` 收集，而不是固定配置文件，因此要复现特定图，必须同时知道数据集、真实时间刻度、采样数、网络宽度/深度、迭代数和随机种子。

### 7. 从动力学到 GRN 与增长基因

若使用可逆且可微的 PCA 或 autoencoder，低维速度可映回基因空间。论文把

$$
J_{ij}(x,t)=\frac{\partial v_i(x,t)}{\partial x_j}
$$

解释为基因 $j$ 对基因 $i$ 瞬时变化的局部影响。`plot_jac_v()`（`utility.py:458` 起）通过自动微分计算平均 Jacobian；`plot_grad_g()`（`utility.py:486` 起）计算 $\nabla g$。因此网络可以随时间、细胞状态或细胞类型给出不同矩阵。

但这些导数回答的是“在已拟合连续场中，输入坐标的小变化如何影响预测速度/增长”，不是干预实验意义上的因果效应。若降维不可逆、批次残留或模型在稀疏区域外推，基因层解释会随之失真。UMAP 适合画轨迹，但普通 UMAP 不足以支持严格的基因空间导数回映。

### 8. 图证据怎样支持方法

- Fig. 1 展示输入快照、连续密度、两个神经网络以及速度、增长、轨迹和 GRN 输出。
- Fig. 2 的三基因模拟有已知速度、增长和调控结构，用来检验能否恢复这些真值，并说明平衡 OT 在增长存在时会制造错误运动。
- Fig. 3 用有实验克隆信息的造血数据比较命运概率和增长；这是外部验证，但仍不是逐细胞真实连续轨迹。
- Fig. 4–5 在 EMT 数据上展示 10 维 AE 潜空间结果、基因轨迹、SNAI1 相关网络、增长与 CellChat 分析，并与 MIOFlow、scVelo 及依赖 KEGG/GO 基因集的增长估计比较。
- Fig. 6 在 iPSC 分化中恢复分叉、HAND1/SOX17 开关关系和分叉附近增长峰。

论文补充讨论显示：结果在多种降维和若干潜空间维度下具有一致性；短程加长程误差比单一尺度更稳定；不同 WFR 权重给出相近总体行为；但时间点、细胞数、初始密度带宽和降维质量都影响结果。`paper_supp2.pdf` 是 reporting summary，说明数据来自既有公开研究、未开展新的生物实验，并称计算任务用不同随机种子重复。

### 9. 论文—代码对应关系

| 论文机制 | 本地实现 | 对应程度 |
|---|---|---|
| 时间依赖速度与增长两个网络 | `utility.py:43-67,81-156` | Confirmed |
| $d\log\rho/dt=g-\nabla\cdot v$ | `utility.py:65`, `trace_df_dz()` | Confirmed |
| 高斯混合密度与质量比例 | `utility.py:183-221,279,290` | Confirmed |
| 长程与相邻重建误差 | `utility.py:265-299` | Confirmed |
| WFR 速度/增长代价 | `utility.py:231-243,301-307` | Confirmed；代码固定等权，未暴露 $\alpha$ |
| 神经 ODE 训练和检查点 | `TIGON.py:31-115` | Confirmed |
| Jacobian GRN 与增长梯度 | `utility.py:458` 起、`:486` 起 | Confirmed |
| AE 降维 | `AE/models.py`, `AE/trainer.py`, `Notebooks/AE.ipynb` | Partial；是独立预处理，非一键主流程 |
| 论文全部基准、CellChat 与统计图 | 本地快照 | Partial / Not found；核心训练代码存在，但完整基准和所有制图工作流未打包 |

### 10. 复现边界与正确解读

本地快照包含四组 `.npy` 输入、训练与绘图脚本、AE notebook、若干检查点和示例 PDF 输出，因此能够追踪核心实现，也具备运行示例的主要材料。但它没有环境锁定文件；依赖版本主要来自论文 reporting summary。交互式 CLI 没有保存每个论文实验的完整配置，仓库快照也没有记录 Git commit，不能把这里的代码断言为精确 commit-pinned 版本。

使用 TIGON 结果时应保留以下边界：

1. 速度和增长由群体快照在平滑、最小代价等假设下识别，并非唯一真实历史。
2. $g$ 是净群体质量变化，不区分分裂、死亡和采样偏差。
3. 连续轨迹是模型在观测时刻之间的插值/推断，不是同一细胞的实测追踪。
4. Jacobian 和增长梯度是模型敏感度；因果 GRN 仍需扰动或独立实验验证。
5. 高维基因解释依赖可逆降维；二维图上的可视化一致不保证原基因空间动力学正确。
6. 论文展示了模拟真值、克隆信息和已知标记的一致性，但并未消除不同速度—增长分解可能同样解释快照的识别性问题。

因此，TIGON 最合适的定位是：一个把时间序列单细胞快照、群体增长和连续状态动力学统一起来的生成式动力学框架。它提供可检验的轨迹、增长和局部调控假设，而不是直接观测到的细胞谱系或已被实验证明的因果网络。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TIGON: Reconstructing Growth and Dynamic Trajectories from Single-Cell Transcriptomics Data

**Paper**: Sha, Y., Qiu, Y., Zhou, P. & Nie, Q. *Nature Machine Intelligence* **6**, 25–39 (2024).
**DOI**: [10.1038/s42256-023-00763-w](https://doi.org/10.1038/s42256-023-00763-w)
**Code**: [github.com/yutongo/TIGON](https://github.com/yutongo/TIGON)

---

### Motivation & Novelty

Time-series single-cell RNA sequencing (scRNA-seq) provides snapshots of cellular systems at discrete time points, but the destructive nature of sequencing prevents tracking individual cell trajectories. For example, during epithelial-to-mesenchymal transition (EMT) in cancer, the A549 cell population changes dramatically — cells divide, die, and shift gene expression over 7 days — but each sequencing snapshot destroys all measured cells. The fundamental challenge is to reconstruct continuous trajectories, growth dynamics, and regulatory networks from these disconnected snapshots.

Existing trajectory inference methods face key limitations:

- **Pseudotime methods** (Monocle, *Nat. Biotechnol.* 2014; PAGA, *Genome Biol.* 2019) order cells by transcriptomic similarity but cannot capture real temporal dynamics or population changes
- **RNA velocity** (scVelo, *Nat. Biotechnol.* 2020) infers directions from spliced/unspliced ratios but assumes steady-state kinetics, cannot model population changes, and often produces noisy/inconsistent velocity fields (Fig. 5d)
- **Balanced optimal transport** (Waddington-OT, *Cell* 2019; TrajectoryNet, *PMLR* 2020; MIOFlow, *Adv. Neur. Inf. Process. Syst.* 2022) transports mass between distributions but assumes constant total mass, generating spurious velocity in quiescent cell populations to compensate for growth (Fig. 2g)
- **PRESCIENT** (*Nat. Commun.* 2021) models differentiation as diffusion but requires preselected growth/death gene lists from external databases (KEGG/GO), making growth inference biased — KEGG and GO gene sets give contradictory growth estimates on the same EMT dataset (Fig. 5e–f)

**TIGON's unique contributions**:
1. **Dynamic unbalanced optimal transport** — simultaneously captures cell velocity (gene expression change per cell) and population growth/death via the Wasserstein–Fisher–Rao (WFR) distance, which generalizes OT to measures of different total mass
2. **Dimensionless deep learning formulation** — converts the high-dimensional PDE-constrained OT problem into a mesh-free system of ODEs solvable by neural ODEs, enabling direct computation in up to 10 dimensions without spatial grids
3. **Unbiased growth inference** — learns growth without preselected gene lists, avoiding database-selection bias
4. **Temporal causal GRN inference** — extracts time-varying, cell-type-specific gene regulatory networks from the Jacobian of the velocity field, with complete architecture including self-regulation

---

### Method Overview

#### Mathematical Framework

TIGON models cell population dynamics via a continuity equation with a growth term:

$$\partial_t \rho(x,t) + \nabla \cdot (\mathbf{v}(x,t) \rho(x,t)) = g(x,t) \rho(x,t)$$

where $\rho(x,t)$ is the cell density over gene expression state $x \in \mathbb{R}^d$ at time $t$, $\mathbf{v}(x,t)$ is the velocity field describing instantaneous gene expression change, and $g(x,t)$ is the growth rate (positive = proliferation, negative = death).

#### Optimization Objective

The WFR cost function balances transport efficiency against growth energy:

$$W_{0,T} = T \int_0^T \int_{\mathbb{R}^d} \left( |\mathbf{v}(x,t)|^2 + \alpha |g(x,t)|^2 \right) \rho(x,t) \, dx \, dt$$

where $\alpha$ controls the trade-off between Wasserstein (transport) and Fisher–Rao (growth) metrics ($\alpha=1$ used throughout the paper). The total loss $L = W + \lambda_d R$ combines this WFR cost with short- and long-term reconstruction errors $R$ measuring density match at observed time points, with $\lambda_d = 10^4$.

#### Computational Pipeline

1. **Preprocessing**: Dimension reduction (PCA, autoencoder, or reversible UMAP) to project high-dimensional gene expression to a low-dimensional space (2–10 dims), scaled to $[-2,2]$
2. **Density estimation**: Gaussian mixture model with annealing variance $\sigma$ constructs continuous densities $\rho_i$ from discrete cell samples at each time point
3. **Neural ODE training**: Two neural networks approximate $\mathbf{v}(x,t)$ and $g(x,t)$; the ODE system is solved by Dopri5 (adaptive Runge–Kutta) and gradients are computed via the adjoint method
4. **Downstream analysis**:
   - **Trajectory**: Integrate velocity field from initial conditions
   - **GRN**: Jacobian $J = \{\partial v_i / \partial x_j\}$ gives directed, signed, weighted regulatory matrix
   - **Growth genes**: Gradient $\nabla g = \{\partial g / \partial x_j\}$ identifies genes driving proliferation/death
   - **Cell–cell communication**: Inferred gene expression at unmeasured time points enables temporal CellChat analysis

#### Key Theoretical Result

The paper proves a **Lemma** and **Theorem** showing that the continuity equation with growth can be decomposed into characteristic ODEs: $dx/dt = \mathbf{v}(x,t)$ and $d(\ln\rho)/dt = g - \nabla \cdot \mathbf{v}$. This converts the PDE into a system of ODEs amenable to neural ODE solvers, yielding a dimensionless formulation where high-dimensional integrals become expectations over sample points.

---

### Evaluation

#### Datasets

| Dataset | Type | Timepoints | Cells | Genes/Dims | Source |
|---------|------|-----------|-------|------------|--------|
| Simulated 3-gene | Synthetic | 5 (t=0,10,20,30,40) | ~400–914/tp | 3 genes | Stochastic GRN model |
| Lineage tracing | Mouse hematopoiesis | 3 (d2,4,6) | ~5,210 | 2D SPRING | Weinreb et al., *Science* 2020 |
| EMT | A549 cancer, TGFB1-induced | 5 (0h,8h,1d,3d,7d) | 577–885/tp | 10D AE latent | Cook & Vanderhyden, *Nat. Commun.* 2020 |
| iPSC differentiation | Single-cell qPCR | 8 (d0–d5) | Variable | 4 PCs (96 genes) | Bargaje et al., *PNAS* 2017 |

#### Benchmarked Methods

**Trajectory inference** (11 methods): TIGON, Balanced OT, TrajectoryNet (*PMLR* 2020), MIOFlow (*Adv. NIPS* 2022), MST, Slingshot, Component1, SLICER, reCAT, ElPiGraph, EmbedCurve, Angle, EPG/GraphFlow, Monocle

**GRN inference** (13 methods): TIGON, PPCOR, GRNVBEM, GRNBOOST2, CellOracle (*Nature* 2023), LEAP, SCODE, PIDC, GENIE3, SINCERITIES, SCRIBE, SCNS, GRSL

#### Key Results

1. **Simulated data**: TIGON achieves lowest MSE in velocity prediction and population ratio accuracy vs. balanced OT, TrajectoryNet, MIOFlow. For GRN inference, TIGON has highest AUPRC and AUROC among 13 methods
2. **Lineage tracing**: Inferred growth correlates with ground truth (Pearson=0.62, Spearman=0.44). Fate probability prediction achieves 5% higher Pearson correlation and 7% higher AUROC than PBA, WOT, FateID
3. **EMT**: Successfully reconstructs gene expression trajectories showing epithelial-to-mesenchymal marker transitions (CDH1↓, VIM↑). Identifies SNAI1 as key TF. Growth inference is unbiased (no gene list needed), unlike KEGG/GO-based approaches that give contradictory results
4. **iPSC**: Captures bifurcation into mesodermal and endodermal fates. Recovers toggle-switch interaction between HAND1 and SOX17. Top 5 growth-related genes at branching are all validated in UniProtKB

#### Consistency Analysis

TIGON shows robust performance across different dimension reduction methods (PCA, AE, reversible UMAP) and latent space dimensions (2–10). Velocity cosine similarity >0.5, growth Pearson correlation >0.5, GRN correlation >0.5 across configurations (Supplementary Figs. 6–12).

#### Limitations

- **Computational scalability**: The GMM density estimation computes $N$ Gaussian evaluations per sample, scaling as $O(N \cdot K \cdot d)$ per time point. The Jacobian trace computation requires $d$ autograd passes per forward evaluation
- **Low-dimensional requirement**: Operates in reduced dimensions (2–10); high-dimensional gene space requires a separate AE/PCA preprocessing step that may lose biologically relevant variation
- **Assumes smooth dynamics**: The continuity equation and neural ODE framework assume smooth velocity and growth fields; discontinuous transitions (e.g., stochastic cell-fate switching) may not be well captured
- **No uncertainty quantification**: Single deterministic model; no confidence intervals on inferred trajectories, GRNs, or growth rates
- **Hyperparameter sensitivity**: The undocumented $\lambda_d = 10^4$ and sigma annealing schedule require tuning for new datasets

---

### Reproducibility Assessment

**Rating: 4/5**

| Aspect | Status | Notes |
|--------|--------|-------|
| Code availability | ✓ | MIT license, GitHub repo with training/visualization scripts |
| Data availability | ✓ | All datasets publicly available; preprocessed .npy files included |
| Environment | ⚠ | No setup.py/requirements.txt; dependencies listed in Reporting Summary only |
| Training procedure | ⚠ | Interactive CLI-based configuration; no automated scripts for reproducing paper results |
| Pretrained models | ✓ | Checkpoint files included for simulation and EMT |
| Documentation | ⚠ | README with basic usage; Jupyter notebooks for AE training and visualization |

**Key dependencies** (from Reporting Summary): Python 3.8, PyTorch 1.13.1, scipy 1.10.1, TorchDiffEqPack 1.0.1, torchdiffeq 0.2.3, numpy 1.23.5, seaborn 0.12.2, matplotlib 3.5.3

**Potential blockers**:
- No `requirements.txt` or `setup.py` — users must manually install dependencies
- Hyperparameters are set interactively via command-line prompts, not config files
- The AE training notebook requires separate preprocessing of raw scRNA-seq data not fully documented in the repo
- Exact reproduction requires knowing the specific hyperparameters used for each dataset (partially in Supplementary Table 2)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
