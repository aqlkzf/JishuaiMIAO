---
layout: default
permalink: /paper-atlas/stvcr-556daa48/
title: "stVCR"
nav: false
description: "stVCR 把不同时间的空间转录组细胞群放入共同的空间–表达状态，用刚体对齐消除坐标框架差异，用带生长质量的神经 ODE 和多时点 OT 匹配学习连续迁移、表达与增殖场，再从这个模型生成插值、谱系和局部敏感度；它重建的是受快照与先验约束的最可能动力学之一，而不是对单细胞真实历史的直接观测。"
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
      <span>Nature Methods · 2026</span>
    </div>
    <h1>stVCR</h1>
    <p>stVCR: spatiotemporal dynamics of single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03010-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## stVCR：把多时点空间转录组“快照”重建成连续细胞动力学

### 它解决的不是普通轨迹排序问题

空间转录组在每个时间点都会破坏样本，因此同一个细胞不能被连续追踪。输入只是若干时刻的细胞群体：每个细胞有空间坐标 $\mathbf{x}$ 和基因表达 $\mathbf{q}$，但不同切片可能旋转、平移，细胞数还会因增殖和死亡改变。stVCR 的目标是从这些不配对快照中学习一个连续场，同时给出：

- 空间迁移速度 $\mathbf{v}_t(\mathbf{x},\mathbf{q})$；
- 表达空间速度 $\mathbf{p}_t(\mathbf{x},\mathbf{q})$；
- 增殖/死亡率 $g_t(\mathbf{x},\mathbf{q})$；
- 不同时间切片到共同坐标系的刚体变换。

论文把它比作“spatiotemporal video cassette recorder”，但这个“录像”是满足模型与最优传输约束的一种群体级重建，不是对真实单细胞的实验录像。其 RNA velocity 也不是由 unspliced/spliced 比例直接估计，而是联合表达–空间状态上的神经 ODE 导数。

### 输入如何变成联合状态

预处理先过滤细胞和基因，可选按批次归一化和 log1p，再选高变基因。自编码器把表达压缩到论文设定的 10 维潜在表达 $\mathbf{q}$；源码的编码器末端用 Sigmoid、解码器用 Softplus（`src/stvcr/preprocessing/ae_utils.py:29-57`）。这意味着后续动力学首先发生在 AE 潜空间，原始基因空间速度需要经过解码器映射或有限差分恢复。

不同时间点的坐标先分别中心化。初始对齐在表达差异与空间差异的融合代价上交替求 OT 耦合和 Procrustes 刚体变换，再缩放空间坐标（`src/stvcr/preprocessing/pp.py:59-142`；`src/stvcr/preprocessing/utils.py:7-89`）。它只允许旋转和平移，能消除切片坐标系差异，却不能代表任意组织形变；真实非刚性形变可能被动力学场吸收。

每个细胞最后表示为

$$
\mathbf{z}=(\mathbf{x},\mathbf{q})\in\mathbb{R}^{d_s+d_g},
$$

其中 $d_s$ 通常为 2 或 3，$d_g=10$。

### 三个场怎样构成连续动力学

stVCR 用带生长项的连续性方程描述细胞密度 $\rho_t$：

$$
\partial_t\rho_t+\nabla_{\mathbf{x},\mathbf{q}}\cdot
\left((\mathbf{v}_t,\mathbf{p}_t)\rho_t\right)=g_t\rho_t.
$$

沿单个粒子的特征线，它变成三条常微分方程：

$$
\frac{d\mathbf{x}}{dt}=\mathbf{v}_t(\mathbf{x},\mathbf{q}),\qquad
\frac{d\mathbf{q}}{dt}=\mathbf{p}_t(\mathbf{x},\mathbf{q}),\qquad
\frac{d\log w}{dt}=g_t(\mathbf{x},\mathbf{q}).
$$

$w$ 是粒子代表的质量，$w=\exp(\log w)$ 保证为正。空间速度、表达速度和生长率由三个以 $(t,\mathbf{x},\mathbf{q})$ 为输入的 MLP 给出（`src/stvcr/training/model.py:6-50`）。代码确实把空间和表达导数拼成 `dz_dt`，并单独返回增长率；所以这里的三种动力学是联合学习的，而不是训练三个互不相干的后处理器。

### 为什么要用 Wasserstein–Fisher–Rao

普通平衡 OT 要求起点和终点质量相等，难以表示细胞增殖与凋亡。stVCR 借用 Wasserstein–Fisher–Rao（WFR）思想，同时惩罚运动和质量变化：

$$
\mathcal{L}_{Dyn}=\int\rho_t
\left(\|\mathbf{v}_t\|^2+
\alpha_{Exp}\|\mathbf{p}_t\|^2+
\alpha_{Gro}|g_t|^2\right)dt.
$$

第一项限制空间迁移不要无谓剧烈，第二项限制表达变化，第三项限制生长/死亡。权重不是生物常数，而是决定哪类变化更“昂贵”的正则化超参数。源码在 ODE 积分中把该能量作为额外状态累积，并以 $\exp(\log w)$ 加权（`src/stvcr/training/train.py:130-143,204-223`）。

### 快照如何约束学到的“视频”

只有平滑能量会产生许多可能轨迹，因此每个观测时点还要做边缘分布匹配。模型从第一个时点向前积分、从最后一个时点向后积分，在每个真实时点把预测粒子与观测细胞比较。代价矩阵融合表达和空间距离：

$$
C_{ij}^{(k)}=\kappa_{Exp}C_{ij,Exp}^{(k)}+
(1-\kappa_{Exp})C_{ij,Spa}^{(k)}.
$$

归一化质量用 2-Wasserstein/精确 OT 代价匹配，另用相对质量误差匹配不同时间点的细胞数。源码在 `src/stvcr/training/train.py:188-311` 用 `pot.emd2` 实现这一流程。这里有两个解释边界：批量 OT 的复杂度高，训练依赖采样；观测细胞数也受到采样和实验捕获效率影响，不等于纯粹的真实增殖率。

切片刚体参数与神经动力学共同优化。2D 用旋转角和平移，3D 用三个欧拉角（`src/stvcr/training/model.py:129-188`）。源码的变换写成 $R(x-r)$，论文写作 $Rx+r$；可通过重新参数化平移联系，但复现时必须按源码约定。

### 可选生物先验做了什么

当仅靠长时间间隔的边缘匹配会产生不合理路径时，stVCR 可加入两类先验：

1. 细胞类型转移先验：只在允许的类型组之间做分组匹配，限制不合理的类型跳转。
2. 空间结构保持（SSP）先验：先在指定结构内找空间且表达相近的邻居，再惩罚这些邻居的轨迹间距改变，减少器官被撕裂或错误聚合。

它们是软约束，不是新观测。错误或过强先验会把预期结构写入结果，因此有无先验的实验和消融需要分开解释。训练路由位于 `src/stvcr/training/train.py:30-100`，无先验、仅类型先验和类型+SSP 使用不同分支。

### 训练完成后能得到什么

- **对齐坐标**：学习到的刚体变换写入 `X_spatial_aligned`。
- **任意时刻插值和外推**：从已知时刻沿神经 ODE 演化状态；区间内插值通常比超出观测范围的外推更受数据约束。
- **群体生长/死亡**：由 $g$ 和粒子权重表示；下游模拟还用随机 birth–death 生成离散细胞。
- **谱系树**：依据演化时保留的模拟 cell ID 和时空分类器标签构树（`src/stvcr/downstream/lineage.py:19-49,118-171`）。这是模型谱系，不是条形码谱系追踪。
- **调控和迁移驱动线索**：通过 autograd 求表达速度、空间速度或生长率对基因表达的偏导（`src/stvcr/downstream/partial_derivative.py:94-163`）。偏导是局部模型敏感度，不自动等于因果调控。

源码用有限差分把 AE 潜空间的表达速度映回原始基因空间，并固定步长 0.1；迁移驱动实现实际对 $\|v\|^2$ 求导，而图注/文字常简写为对速度模长求导。这些比例相关但数值并不相同，报告具体分数时应按实现定义。

### 图证据怎样串起来

- **图 1** 给出全流程：快照预处理与刚体对齐、联合神经 ODE/WFR 优化、可选类型和空间结构先验，以及插值、谱系、速度和敏感度下游。
- **图 2** 用模拟数据检验连续表达–空间动力学、增长率和组件消融；它能与已知真值比较，是方法可辨识性的主要证据。
- **图 3** 在美西螈脑损伤再生时序空间转录组上展示对齐、插值、迁移/表达变化和增长动力学。
- **图 4** 进一步用模型谱系和局部偏导分析再生过程中细胞类型转变及候选调控关系。
- **图 5** 扩展到 3D 果蝇胚胎并与其他空间映射方法比较，强调空间连贯性。

补充材料 44 页包含推导、训练伪代码、更多模拟/消融/鲁棒性结果、补充图 1–13 和补充表。它们扩大了参数和数据情景覆盖，但仍是在相同模型假设和基准设计下的证据，不能替代独立实验追踪。

### 版本与复现边界

1. 本地代码来源标为 `https://github.com/QiangweiPeng/stVCR`，但没有嵌套 Git 元数据或 `.repo_source` 提交记录，因此**没有可核验的 commit hash**。
2. `src/stvcr.egg-info/PKG-INFO` 记录版本 `0.1`，这是本地构建元数据；工作区没有 `setup.py`、`pyproject.toml`、requirements 或锁文件，不能据此恢复精确依赖环境。
3. 本地包含四个教程 notebook、模拟数据、主文和补充 PDF，但没有自动化测试。论文还给出 Code Ocean 复现入口；本轮未联网刷新 capsule，也未重建环境、训练模型或重画结果。
4. 神经 ODE 从离散边缘学习的连续路径通常不唯一。刚体形变假设、AE 表示、表达/空间代价权重、生长质量、先验和采样共同决定最终路径。
5. 论文报告的优越性来自指定模拟、留一时点插值和真实数据比较；不能外推成对任意平台、时间间隔、组织形变或稀疏度都最优。

### 一句话总结

stVCR 把不同时间的空间转录组细胞群放入共同的空间–表达状态，用刚体对齐消除坐标框架差异，用带生长质量的神经 ODE 和多时点 OT 匹配学习连续迁移、表达与增殖场，再从这个模型生成插值、谱系和局部敏感度；它重建的是受快照与先验约束的最可能动力学之一，而不是对单细胞真实历史的直接观测。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## stVCR: Spatiotemporal Video Cassette Recorder — Summary

**Paper**: Peng, Q., Zhou, P. & Li, T. stVCR: spatiotemporal dynamics of single cells. *Nature Methods* (2026). DOI: 10.1038/s41592-026-03010-3

**Code**: https://github.com/QiangweiPeng/stVCR

---

### Motivation & Novelty

Time-series spatial transcriptomics captures snapshots of cellular development at single-cell resolution, but recovering continuous spatiotemporal trajectories from these destructive measurements remains unsolved. Existing methods address only parts of the problem: static OT methods like Moscot (*Nature*, 2025), Spateo (*Cell*, 2024), and DeST-OT (*Cell Systems*, 2025) find optimal mappings between adjacent time points but cannot generate continuous intermediate trajectories. Dynamic OT methods for scRNA-seq — TrajectoryNet (*ICML*, 2020), TIGON (*Nature Machine Intelligence*, 2024), OT-CFM (*Transactions on Machine Learning Research*, 2024) — reconstruct continuous dynamics but lack spatial coordinate modeling. RNA velocity methods (scVelo, *Nature Biotechnology*, 2020; UniTVelo, *Nature Communications*, 2022; DeepVelo, *Genome Biology*, 2024) infer directionality from splicing ratios but suffer from scale invariance and cannot model physical-space migration.

**stVCR addresses three key gaps simultaneously:**

1. **Continuous spatiotemporal dynamics**: Uses dynamical (not static) optimal transport to reconstruct continuous cell differentiation, migration, and proliferation trajectories via neural ODEs
2. **Coordinate system alignment**: Introduces rigid-body transformation invariant OT that jointly optimizes spatial alignment and dynamics — unlike Gromov-Wasserstein approaches (used by Moscot, Spateo) that are computationally expensive and don't align to a common coordinate system
3. **Unbalanced transport**: Models cell division and apoptosis through the Wasserstein-Fisher-Rao metric, with growth rate parameterized by a neural network rather than approximated from hallmark gene databases (as in Waddington-OT, *Cell*, 2019)

Additional novelty includes optional biological priors (cell-type transitions, spatial structure preservation) and interpretable downstream analyses (gene-space Jacobians for regulatory networks, migration/growth driver genes).

---

### Method Overview

stVCR models cell population dynamics with a transport-with-growth PDE: $\partial_t \rho_t + \nabla \cdot ((\mathbf{v}_t, \mathbf{p}_t)\rho_t) = g_t \rho_t$, where $\mathbf{v}_t$ (spatial velocity), $\mathbf{p}_t$ (RNA velocity), and $g_t$ (growth rate) are parameterized by three neural networks taking $(t, \mathbf{x}, \mathbf{q})$ as input.

**Computational pipeline:**

1. **Preprocessing**: Size-factor normalization → 2000 HVGs → autoencoder embedding to 10D → spatial centering and initial rigid alignment
2. **Training**: Bidirectional neural ODE integration (forward t₀→tK and backward tK→t₀) with three loss components: WFR kinetic+growth energy (dynamics regularization), 2-Wasserstein matching loss (data fidelity with fused gene+spatial cost), and optional spatial structure preservation
3. **Alignment**: Rotation matrices (2D angle or 3D Euler angles) and translation vectors are learned jointly with dynamics, using a 10× lower learning rate
4. **Downstream**: Interpolation via Euler stepping with stochastic birth-death; gene regulatory networks via autograd Jacobians; migration/growth driver genes via gradient analysis; lineage trees via cell tracking + time-dependent classifier

See `doc_method.md` for full mathematical details and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets

| Dataset | Source | Time Points | Cells | Spatial Dim |
|---|---|---|---|---|
| Simulated 1 (toggle switch) | Synthetic gene circuit | 6 (t=0–2.5) | ~3000 initial | 2D |
| Simulated 2 (heart→duck) | Shape transformation | 5 (t=0–1.0) | ~3800 initial | 2D |
| Simulated 3 (bio prior) | Cell migration + steady state | 2 or 5 | Variable | 2D |
| Axolotl brain regeneration | Stereo-seq (Wei et al., *Science*, 2022) | 5 (2–20 DPI) | Large-scale | 2D |
| 3D Drosophila embryo | Stereo-seq (Qiu et al., *Cell*, 2024) | 2 (E7–9h, E9–10h) | Large-scale | 3D |

#### Metrics

- **2-Wasserstein distance**: Gene expression space and joint gene+spatial space (leave-one-time-point-out interpolation)
- **MAE of growth rate**: Mean absolute error vs ground truth (simulated data only)
- **MRMSE of spatial velocity**: Mean root-mean-square error vs ground truth (simulated data only)
- **Qualitative**: Spatial alignment visualization, migration streamlines, lineage trees, GRN consistency

#### Key Results

- stVCR achieves the best or near-best 2-Wasserstein interpolation accuracy across all datasets (Supp Tables 4-5, 8-11), outperforming SF2M (*AISTATS*, 2024) and TIGON (*Nature Machine Intelligence*, 2024)
- Ablation studies confirm all modules (spatial, gene, growth, alignment) are essential — removing any one degrades performance
- On simulated data, stVCR accurately recovers ground-truth spatial velocity (MRMSE), growth rates (MAE), and gene regulatory relationships
- Robustness analysis shows stable performance across wide ranges of $\lambda_{Mch}$, $\kappa_{Exp}$, and $\alpha_{Gro}$, and under gene/spatial coordinate noise perturbation
- Scalability: linear in dataset size, time points, and model size; time increases with batch size due to $O(B^3)$ OT complexity
- On axolotl data, stVCR reveals biologically meaningful dynamics: reaEGC migration toward wound, wntEGC→reaEGC transition in early injury, reaEGC→neuron differentiation in late regeneration
- On 3D Drosophila, stVCR produces spatially coherent CNS migration (cells move along internal structure) vs Spateo (disconnected parts) and Moscot (cell aggregation artifacts)
- Compared methods: Spateo (*Cell*, 2024), Moscot (*Nature*, 2025), DeST-OT (*Cell Systems*, 2025), TopoVelo (*Nature Biotechnology*, 2025), STT (*Nature Methods*, 2024)

---

### Reproducibility

**Rating: 4/5** (Good)

#### Strengths
- Full source code on GitHub with 4 tutorial notebooks covering simulated and real data
- Code Ocean capsule (DOI: 10.24433/CO.9796381.v1) for figure reproduction
- Clean Python package structure (`src/stvcr/`) with modular preprocessing, training, and downstream analysis
- All datasets publicly available (CNGB for axolotl, Spateo package for Drosophila, GitHub for simulated)
- Default hyperparameters documented and shown to be robust

#### Weaknesses
- No `requirements.txt` or `setup.py` with pinned versions — users must manually install PyTorch, torchdiffeq, TorchDiffEqPack, POT, scanpy, etc.
- Training takes substantial GPU time (neural ODE + exact OT per epoch); no training time benchmarks for real datasets
- No automated test suite
- `TorchDiffEqPack` imported but unused in training code (potential dependency confusion)
- Model selection is rudimentary: saves every 100 epochs, overwrites, no validation-based early stopping for the main training loop

#### Practical Notes
- Requires CUDA GPU for reasonable training times
- Key Python packages: `torch`, `torchdiffeq`, `TorchDiffEqPack`, `ot` (POT), `scanpy`, `gseapy`, `plotly`, `pyvista` (for 3D visualization)
- Start with tutorial `00_simulated_data_rectangle.ipynb` for basic workflow
- The `pp_stvcr()` function handles the full preprocessing pipeline in one call
- Default hyperparameters work well for most cases; $\kappa_{Exp}$ (gene vs spatial balance) is the most dataset-dependent parameter

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
