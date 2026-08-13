---
layout: default
permalink: /paper-atlas/cellstream-25371181/
title: "CellStream"
nav: false
wide: true
description: "CellStream 面向多个离散时间点的单细胞快照。它不先做一个固定的 PCA/UMAP 再拟合轨迹，而是同时训练低维 autoencoder、速度场和生长/死亡率，使低维空间既能重构原始数据，又能让从最早时间点出发的粒子流匹配后续快照。 方法输出的是一个 dynamics-informed latent space，以及其中的连续速度场 v(t,z)、质量增长率 g(t,z) 和积分轨迹。"
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
      <span>AAAI · 2026</span>
    </div>
    <h1>CellStream</h1>
    <p>CellStream: Dynamical Optimal Transport Informed Embeddings for Reconstructing Cellular Trajectories from Snapshots Data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1609/aaai.v40i1.37041" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellStream">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/PQ-Zhang/CellStream" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellStream">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellStream：让低维嵌入与细胞动力学共同学习

### 一句话理解

CellStream 面向多个离散时间点的单细胞快照。它不先做一个固定的 PCA/UMAP 再拟合轨迹，而是同时训练低维 autoencoder、速度场和生长/死亡率，使低维空间既能重构原始数据，又能让从最早时间点出发的粒子流匹配后续快照。

方法输出的是一个 dynamics-informed latent space，以及其中的连续速度场 $v(t,z)$、质量增长率 $g(t,z)$ 和积分轨迹。它并没有追踪到真实的同一细胞，也不能把低维箭头自动解释成原始基因的因果调控。

### 1. 输入、状态和输出

输入是时间序列快照

$$
\{(t_i,X_i)\}_{i=0}^{T-1},
$$

其中 $X_i$ 是时间 $t_i$ 的细胞×特征矩阵。特征可以是 scRNA-seq、qPCR，或外部 GNN 已经整合空间邻接后的向量。每个时点的细胞数 $N_i$ 还被当作总体质量变化的观测。

代码把时间列直接拼到每个细胞的特征前：`info=[time, values]`。基因/特征逐列缩放到 $[0.05,0.95]$，而不是 $[0,1]$；这样避免 decoder Sigmoid 在边界饱和（`TranscriptomicsData.py:6-29`）。

输出包括二维 latent coordinates、$v_\phi(t,z)$、$g_\psi(t,z)$，以及从初始细胞积分得到的预测粒子和权重。可视化轨迹只是根据学习到的 ODE 前向积分；它不是细胞条形码或 lineage tracing 证据。

### 2. 四个神经网络部件

#### 2.1 Encoder 与 decoder

encoder 接收时间和表达：

$$
z=f^{enc}_\theta(t,x),
$$

decoder 尝试重构

$$
(\hat t,\hat x)=f^{dec}_\theta(z).
$$

代码的 encoder 有三层 ReLU hidden layer，末层 Tanh，再用 `(Tanh+1)/2` 映射到 $[0,1]$；decoder 三层 ReLU，末层 Sigmoid，并对重构的第一列做 `logit` 以恢复未压缩的时间值（`Autoencoder.py:4-44`）。这两个末端变换在论文架构描述中没有展开。

#### 2.2 速度与生长网络

速度网络输出 latent-space velocity：

$$
\frac{dz}{dt}=v_\phi(t,z).
$$

生长网络输出局部增长/死亡率：

$$
\frac{d\log w}{dt}=g_\psi(t,z),
$$

所以粒子权重始终为正：$w(t)=w(0)\exp(\int g\,dt)$。代码中 velocity hidden 层数可配置，growth 固定三层；二者都把时间 $t$ 与 latent state 拼接后输入（`Net.py:14-76`）。

### 3. 为什么使用 unbalanced dynamical OT

平衡 OT 假设总质量守恒，但真实发育过程中细胞会增殖或死亡。CellStream 使用 Wasserstein–Fisher–Rao（WFR）形式，同时惩罚移动速度和质量变化：

$$
\mathcal L_{WFR}
=\int\sum_j w_j(t)
\left(\lambda_v\|v(t,z_j)\|^2+
\lambda_g|g(t,z_j)|^2\right)dt.
$$

代码不在网格上解连续性 PDE，而把最早时点的细胞当作 Lagrangian particles。Neural ODE 同时积分三种状态：

$$
\dot z=v(t,z),\qquad
\dot{\log w}=g(t,z),\qquad
\dot a=w(\lambda_v\|v\|^2+\lambda_g|g|^2),
$$

最后的 $a$ 就是累计 WFR energy。实现位于 `Train.py:14-50`，ODE solver 使用 Euler，固定 `step_size=0.1`。因此数值精度依赖时间尺度；代码没有自适应步长或误差控制。

实现还提供 `WFR_mode='global'|'local'|'all'`：分别取最后时点、第二个时点或所有时点的累计量。论文只给统一公式，实验 notebook 的具体 mode 属于复现配置，不是理论中唯一确定的选择。

### 4. 三类损失

#### 4.1 Autoencoder 重构

$$
\mathcal L_{AE}=\mathrm{MSE}([t,x],f^{dec}(f^{enc}([t,x]))).
$$

它约束 latent space 保留输入信息，但论文也明确指出 decoder 仍不足以把动力学高保真映回基因空间。

#### 4.2 质量匹配

预测粒子总权重应匹配每个时间点的相对细胞数：

$$
\mathcal L_{Mass}=\sum_i
\left|\sum_j\hat w^j_i-\frac{N_i}{N_0}\right|.
$$

代码位于 `Train.py:53-55`。这里把采样细胞数变化当作生物质量变化；若不同时间点捕获效率或下采样策略不同，$g$ 会混合真实增殖/死亡与实验采样差异。

#### 4.3 分布 OT 匹配

每个时点把预测粒子位置与观测 latent points 做离散 OT。代码先将两侧权重各自归一化，再构建

$$
M_{ab}=\|z^{obs}_a-z^{pred}_b\|_2,
$$

并调用 `ot.emd2()`（`Train.py:57-77`）。函数名 `emd2` 表示返回最优运输 objective，不会自动把 cost 平方；因为代码传入的是未平方欧氏距离，实际项是该 ground cost 下的 EMD/一阶运输代价，而不是论文文字所称的标准平方欧氏 $W_2^2$。因此这里是 **Partial** 匹配。

总实现损失为

$$
\lambda_{WFR}\mathcal L_{WFR}
+\lambda_{Mass}\mathcal L_{Mass}
+\lambda_{OT}\mathcal L_{OT}
+\lambda_{AE}\mathcal L_{AE}.
$$

代码 tuple 顺序是 `(lambda_WFR, lambda_Mass, lambda_OT, lambda_AE)`，与论文叙述顺序不同。论文实验的权重对应 $\lambda_{AE}=10$、$\lambda_{WFR}=1$、$\lambda_{Match}=5$，而 match 内部两项权重各为 1；实际 notebook 参数必须逐项核对。

### 5. 交替训练如何形成 dynamics-informed embedding

训练采用 block coordinate descent：

1. 固定 velocity/growth 网络，只更新 autoencoder；损失仍包含 WFR、Mass 和 OT，因此 embedding 会被动力学反馈改变。
2. 固定 autoencoder，只更新 velocity/growth 网络，使粒子流匹配当前 latent snapshots。
3. 重复两阶段，直到外层流程认为损失不再下降。

库函数 `train()` 每次只执行一个 mode 并冻结另一组参数（`Train.py:104-150`）；完整交替顺序、迭代次数和 PCA initialization 由 tutorial notebook 驱动，没有独立 CLI 或统一训练脚本。因此论文 Algorithm 1 是整体流程，单次 `train()` 调用并不自动完成整个 BCD。

PCA initialization 也只在 EMT tutorial notebook 中完成：先拟合 PCA，再让 autoencoder 接近 PCA coordinates。它不是 `Autoencoder` 构造函数或 `train()` 的内建行为。

### 6. 轨迹与可视化如何生成

可视化从最早时间点随机抽细胞，用显式 Euler 更新

$$
z\leftarrow z+v(t,z)\Delta t,
$$

其中绘图函数使用 `dt=0.01`。它还用 KMeans cluster bounding boxes 检查每个预测时点是否落在观测簇附近，只有通过所有时点检查的序列才画出（`Visualization.py:120-223`）。因此图上的 trajectory 是经过可视化筛选的有效序列子集，不是对全部初始细胞无条件展示。

### 7. 评价指标的实际含义

- **VA**：模拟数据中，预测 velocity 与经 encoder Jacobian 投影后的真实 velocity 之间的 distance correlation。
- **VC**：邻近细胞速度的平均 cosine similarity。代码只保留**不同时间标签**的邻居（`Evaluation.py:20-32`），比论文公式的表述更窄。
- **TC**：半径邻域中同时间标签细胞所占比例（`Evaluation.py:9-18`）。高 TC 表示时间点分离清楚，但过度按时间分层的 embedding 也可能得到高分；它不单独证明生物轨迹正确。

### 8. 论文实验怎样理解

Figure 2 的模拟分叉实验有真实 velocity，显示 CellStream 在增加噪声时保持较高 VA 与 TC。EMT、iPSC 和 MOSTA 没有单细胞真轨迹，主要用 VC、TC 和二维图比较：EMT 呈顺序推进，iPSC 展示 M/En 分叉，MOSTA 使用预训练 GNN 的 50 维空间输入后呈现时空推进与质量增长。

这些结果支持“学到更时间一致、速度更平滑的二维表示”。它们不等价于 lineage-ground-truth accuracy；真实数据上的 VC/TC 还部分评价方法自己塑造的 latent geometry。MOSTA 的空间能力也来自外部 GNN 预处理，CellStream 本体没有直接构图或空间消息传递层。

### 9. 论文—代码匹配结论

| 环节 | 匹配 | 边界 |
|---|---|---|
| 时间+表达 autoencoder | Exact / Partial | 主体存在；末端 Tanh/Sigmoid 与时间 logit 是额外实现细节 |
| velocity/growth ODE | Exact | `Net.py:14-76`, `Train.py:14-45` |
| Lagrangian WFR accumulator | Exact | 固定步长 Euler |
| Mass loss | Exact with assumption | 细胞数比例同时受采样影响 |
| 论文称 $W_2$ 的 OT loss | Partial | 代码传未平方欧氏 cost 给 `ot.emd2()` |
| BCD 交替训练 | Partial | 冻结逻辑在库中，完整调度在 notebooks |
| PCA initialization | Notebook | 非库内默认 |
| VC | Partial | 代码仅跨时间邻居 |
| MOSTA 空间整合 | External preprocessing | GNN 输出作为输入，非 CellStream 内部模块 |
| 一键复现四个数据集 | Not found | 仅 EMT 与 SimData tutorial；无独立训练 CLI |

### 10. 最重要的使用边界

CellStream 的强项是让 latent space 与可运输动力学相互约束，而不是在一个任意几何 embedding 上事后画箭头。其输出仍是由快照分布识别出的一个可能连续流，存在非唯一性；growth 会吸收采样数量差异，二维表示会压缩基因维度，真实数据评价没有 lineage ground truth。

复现时最需要固定的是：输入预处理、时间尺度、`time_indices_list`、WFR mode、四个代码权重、PCA 预训练、外层 BCD 次数和 ODE step size。缺少这些配置时，即使网络结构相同，也不能声称重现了论文结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellStream — Summary

**Paper**: CellStream: Dynamical Optimal Transport Informed Embeddings for Reconstructing Cellular Trajectories from Snapshots Data
**Authors**: Yue Ling, Peiqi Zhang, Zhenyi Zhang, Peijie Zhou (Peking University)
**Venue**: AAAI 2026
**Code**: https://github.com/PQ-Zhang/CellStream

---

### Motivation & Novelty

#### Biological Problem

Time-resolved scRNA-seq captures gene expression snapshots at discrete time points, but sequencing destroys cells — so each snapshot is a static cross-section of a dynamic process. Reconstructing the continuous trajectory of cell state changes (e.g., stem cell differentiation, cancer EMT) from these disconnected snapshots is a fundamental challenge.

#### Limitations of Existing Approaches

- **Geometric embeddings** (PCA, t-SNE, UMAP, diffusion maps): reduce dimensionality but treat each time point independently, ignoring temporal ordering. They optimize for geometric structure, not temporal coherence.
- **RNA velocity methods** (VeloViz, CellPath, Ocelli): require unspliced/spliced count data (not always available), assume steady-state splicing kinetics, and struggle with long time-scale transitions.
  - VeloViz: *Bioinformatics* 2022; CellPath: *Cell Reports Methods* 2021; Ocelli: *NAR Genomics and Bioinformatics* 2025
- **Dynamical OT methods** (TIGON, MIOFlow): model dynamics but operate on pre-computed embeddings (PCA/UMAP), decoupling embedding from dynamics. The embedding is not shaped by the dynamics it represents.
  - TIGON: *Nature Machine Intelligence* 2024; MIOFlow: *NeurIPS* 2022; TrajectoryNet: *ICML* 2020

#### CellStream's Contribution

CellStream **jointly learns the embedding and the dynamics** — the autoencoder is trained simultaneously with the velocity and growth networks, so the latent space is explicitly shaped to support temporal trajectory reconstruction. Key novelties:
1. First method to integrate an autoencoder with unbalanced dynamical OT for joint embedding-dynamics learning
2. Handles cell proliferation/apoptosis via the Wasserstein-Fisher-Rao (WFR) distance
3. Applicable to spatial transcriptomics (ST) data by accepting GNN-processed spatial features as input

---

### Method Overview

CellStream is a deep learning framework with four neural network components:
- **Encoder** $f_\theta^{\mathrm{enc}}$: maps [time, gene expression] → 2D latent space
- **Decoder** $f_\theta^{\mathrm{dec}}$: reconstructs input from latent space
- **Velocity network** $\mathbf{v}_\phi(t,\mathbf{z})$: predicts cell movement direction in latent space
- **Growth network** $g_\psi(t,\mathbf{z})$: predicts cell proliferation/death rate

**Training objective** (Eq. 4):
$$\mathcal{L} = \lambda_{\mathrm{AE}}\mathcal{L}_{\mathrm{AE}} + \lambda_{\mathrm{WFR}}\mathcal{L}_{\mathrm{WFR}} + \lambda_{\mathrm{Match}}\mathcal{L}_{\mathrm{Match}}$$

- $\mathcal{L}_{\mathrm{AE}}$: MSE reconstruction (ensures embedding faithfulness)
- $\mathcal{L}_{\mathrm{WFR}}$: Wasserstein-Fisher-Rao kinetic+growth energy (regularizes dynamics)
- $\mathcal{L}_{\mathrm{Match}}$: OT distribution matching + mass conservation (ensures predicted trajectories match observed snapshots)

**Training strategy**: Block Coordinate Descent (BCD) alternates between optimizing the autoencoder (with dynamics feedback) and the dynamics networks (with frozen embedding).

**Key technical detail**: The WFR integral is computed in Lagrangian (particle) form via Neural ODE, tracking N_0 particles from t=0 forward. This avoids solving a PDE for the density field.

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets

| Dataset | Type | Time Points | Cells | Biological Process |
|---------|------|-------------|-------|-------------------|
| Simulated (SDE) | Synthetic | 3 | ~300 | Bifurcating populations, 6 genes |
| EMT (Cook & Vanderhyden 2020) | scRNA-seq | 4 | ~1000 | A549 cancer EMT (TGFB1 treatment) |
| iPSC (Bargaje et al. 2017) | qPCR | 6 | ~500 | iPSC → Mesoderm/Endoderm bifurcation |
| MOSTA (Chen et al. 2022) | Spatial transcriptomics | Multiple | ~10000 | Mouse organogenesis (C57BL/6) |

#### Metrics

- **VA** (velocity accuracy): distance correlation between predicted and ground-truth velocity (simulated only)
- **VC** (velocity consistency): average cosine similarity between velocity vectors of cross-time neighbors (r=0.05)
- **TC** (temporal consistency): fraction of neighbors within r=0.05 that share the same time label

#### Results (Table 1)

| Method | EMT VC | EMT TC | iPSC VC | iPSC TC | MOSTA VC | MOSTA TC |
|--------|--------|--------|---------|---------|----------|----------|
| **CellStream** | **0.97** | **0.99** | **0.97** | 0.91 | **0.98** | **0.99** |
| VeloViz | 0.88 | 0.70 | 0.41 | 0.92 | 0.83 | 0.89 |
| MIOFlow | 0.96 | 0.77 | 0.98 | **0.92** | 0.42 | 0.92 |
| TIGON+PCA | 0.66 | 0.59 | 0.32 | 0.94 | 0.85 | 0.99 |
| TIGON+t-SNE | 0.70 | 0.94 | 0.74 | 0.95 | 0.43 | 0.99 |
| TIGON+UMAP | 0.67 | 0.91 | 0.82 | 0.93 | 0.47 | 0.99 |
| TIGON+DiffMap | 0.68 | 0.57 | 0.78 | 0.84 | 0.98 | 0.99 |

CellStream achieves highest or near-highest VC and TC across all three real datasets. On simulated data, CellStream maintains high VA and TC across 5 noise levels while other methods degrade.

#### Biological Validation

- **EMT**: CellStream embedding shows clear temporal progression of cancer cell state transition, consistent with known EMT biology
- **iPSC**: Successfully resolves the Day 3 bifurcation into Mesodermal vs Endodermal lineages; VeloViz shows tangled velocity at the branch point
- **MOSTA**: Captures dramatic cell population growth at early time points and consistent forward drift, consistent with the published spatiotemporal atlas

---

### Reproducibility

**Rating: 3/5**

**Strengths**:
- Clean, modular PyTorch codebase with tutorial notebooks for EMT and simulated data
- Pre-trained model weights provided in `params/`
- All datasets are publicly available (EMT, iPSC, MOSTA)
- Dependencies clearly specified (PyTorch 2.6.0, torchdiffeq 0.2.3, pot 0.9.4)

**Weaknesses**:
- No standalone training script — workflow is notebook-only
- Hyperparameters (λ weights, WFR_mode) are set in notebooks, not in a config file
- PCA initialization claimed in paper but not implemented in code
- Preprocessing details for real datasets (HVG selection, normalization steps) are in Appendix A.2 (not in main paper) and not fully reflected in the library code
- No iPSC or MOSTA tutorial notebooks provided (only EMT and SimData)
- The `WFR_mode` parameter ('global'/'local'/'all') used in experiments is not specified in the paper

**Setup**:
```bash
git clone https://github.com/PQ-Zhang/CellStream
cd CellStream
pip install torch torchdiffeq pot dcor scikit-learn umap-learn
jupyter notebook notebooks/
```

**Common pitfalls**:
- `ot.emd2` is O(N²) — for large datasets (>1000 cells per time point), this becomes a bottleneck
- Euler ODE with step_size=0.1 may be insufficient for datasets with large time gaps
- The `time_indices_list` parameter must be set carefully to cover all consecutive time pairs

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
