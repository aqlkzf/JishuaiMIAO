---
layout: default
permalink: /paper-atlas/celltrip-9f75c317/
title: "CellTRIP"
nav: false
wide: true
description: "单细胞测序通常给出的是“快照”：每个细胞只在某个时间或空间位置被观测一次。轨迹推断可以把细胞排成一条发展路径，但往往不显式描述细胞如何相互作用，也难以回答“敲低某个基因后，整群细胞会怎样移动或改变表达”。CellTRIP 的目标更像构造一个可运行的模拟器：把每个细胞视作一个智能体，让它们在低维环境空间里移动；只要这个空间仍能保留原始表达、空间坐标或时间阶段的信息，就给予正奖励。 因此，CellTRIP 的输出不是一条唯一的真实生物轨迹。"
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
      <span>2025</span>
    </div>
    <h1>CellTRIP</h1>
    <p>Inferring virtual cell environments using multi-agent reinforcement learning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/Oafish1/CellTRIP" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellTRIP">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellTRIP 中文方法解读：把单细胞快照训练成可交互的虚拟环境

### 1. 它到底想解决什么问题

单细胞测序通常给出的是“快照”：每个细胞只在某个时间或空间位置被观测一次。轨迹推断可以把细胞排成一条发展路径，但往往不显式描述细胞如何相互作用，也难以回答“敲低某个基因后，整群细胞会怎样移动或改变表达”。CellTRIP 的目标更像构造一个可运行的模拟器：把每个细胞视作一个智能体，让它们在低维环境空间里移动；只要这个空间仍能保留原始表达、空间坐标或时间阶段的信息，就给予正奖励。

因此，CellTRIP 的输出不是一条唯一的真实生物轨迹。它学习的是一个能够重构观测数据、支持插值和扰动模拟的潜在动力系统。

### 2. 输入、内部状态与输出

对细胞 $i$ 和模态 $k$，论文记观测为 $\vec m_i^{(k)}$。模态可以是基因表达、蛋白表达或空间坐标。代码先对表达矩阵做归一化、对数变换、标准化和 PCA，再把每个细胞放入 $n_d$ 维环境中。

每个时刻的核心状态是：

- 位置 $\vec x_i^t$：细胞在潜在环境中的坐标；
- 速度 $\vec v_i^t$：当前位置的变化趋势；
- 源模态 $\vec m_i^{(k)}$：策略可见的表达或其他特征。

策略输出动作 $\Delta\vec v_i^t$，环境再更新速度和位置。训练完成后，位置可经 pinning module 解码为目标模态；也可以修改某些基因或细胞状态后继续模拟，获得扰动轨迹。

### 3. 一次时间步怎样运行

论文的基本更新是：

$$
V^{t+1}=V^t+\Delta t\,\Delta V^t,\qquad
X^{t+1}=X^t+\Delta t\,V^t.
$$

直观地说，策略不直接指定细胞最终去哪里，而是不断给每个细胞一个“加速度”。代码中的 `EnvironmentBase.step()` 还加入摩擦、速度限制和边界处理；所以动作先改变速度，摩擦让速度逐渐衰减，位置随后按速度推进。当速度足够小时，细胞群进入论文所说的 steady state。

例如在一维情况下，若 $\Delta t=0.1$、当前速度为 $0.2$、动作是 $0.5$，忽略摩擦时新速度约为 $0.25$，位置再向前移动约 $0.025$。真实代码在多维空间中对所有细胞并行执行同一过程。

### 4. 策略为何使用残差自注意力

每个细胞的动作不能只由自身表达决定，因为方法要学习“细胞环境”。策略先把该细胞的位置、速度和源模态编码为 query，再把其他可见细胞编码为 key/value。多头注意力汇总邻居信息，残差连接保留自身状态，最后 actor 输出连续动作分布，critic 估计状态价值。

这一步的正确理解是“数据驱动的群体上下文聚合”，而不是已知配体—受体或物理接触网络。注意力权重说明哪些细胞状态对策略决策有用，但不能直接等同于实验验证的细胞间相互作用。

live code 中默认类是 `EntitySelfAttentionLite`：默认两头注意力、一个残差块，并允许每个细胞观察可变数量的邻居。默认 actor 与 critic 共享注意力骨干；独立 critic 是可选项。

### 5. 奖励函数如何把“有用的环境”定义出来

论文把总奖励写为：

$$
\vec r^t=(2\Delta t)^{-1}\vec r_{\mathrm{pinning}}^t
+(10\Delta t)^{-1}\vec r_{\mathrm{velocity}}^t
+10^{-3}\vec r_{\mathrm{action}}^t.
$$

三部分分别回答：

1. **pinning reward**：从潜在位置能否更准确地重构目标模态；
2. **velocity reward**：细胞是否逐渐减速并收敛；
3. **action penalty**：动作是否平滑，避免策略用剧烈跳动取巧。

核心的 pinning 项比较相邻时间步的重构质量：

$$
\vec r_{\mathrm{pinning}}^{t+1}=\vec\delta^t-\vec\delta^{t+1},
$$

其中 $\delta_i^t$ 是经过方差归一化和饱和变换的负重构误差。奖励关注的是“误差改善量”，而不是单个时刻的绝对误差；因此累积奖励可解释为整段模拟中保留信息能力的净提升。

论文第 3.4.1 节明确说明，pinning module 是 $n_d\times 2n_d\times n_{mk}$ 的 MLP，与策略并行训练，损失为 MSE。代码中的 `PinningNN` 正是主路径。`EnvironmentBase.get_pinning()` 还保留了没有传入 pinning 网络时的最小二乘备用分支，但 `train_celltrip()` 的正常训练会传入 `policy.pinning`；因此这不是论文与代码的主要不一致。

### 6. PPO、截断回报自举和自适应缩放

CellTRIP 用 PPO 更新 actor-critic，并以 GAE 计算优势。大规模环境训练常因固定最大步数而被截断；如果把截断状态误当成真正终点，价值估计会系统性偏低。`AdvancedMemoryBuffer.compute_advantages()` 对截断 episode 使用末状态的 critic 值继续自举，而对自然终止使用零终值，这对应论文强调的 truncated reward bootstrapping。

输入分布和回报尺度也会随训练变化。代码用 `ArtStandardization`/`PopArtStandardization` 维护运行统计，并在尺度变化时调整相邻层参数，以尽量保持网络原有输出。论文把对输入层的同类扩展作为稳定训练的重要贡献。

### 7. 训练后怎样做三类任务

#### 空间插补

用已有空间坐标作为目标模态训练 pinning MLP；对只有表达的细胞，先由策略得到环境位置，再由 pinning module 回归空间坐标。空间比较还需要旋转和平移对齐，因为潜在空间本身没有固定朝向。

#### 时间插补

对相邻阶段生成数量匹配的 pseudocells，并用最优传输建立起点与终点的对应关系。环境从前一阶段运行到稳态后，逐步吸收后一阶段目标，模拟中间状态。这里得到的是模型生成的过渡状态，不是对同一真实细胞的连续观测。

#### 扰动预测

先让细胞达到稳态，再通过 hook 修改某个基因或模态，继续运行环境。扰动前后在潜在空间或解码表达空间中的差异可形成 cell-level 或 gene-level effect size。该结果是模型内反事实预测，需用外部扰动实验验证。

### 8. 图和结果应怎样读

- **图 1** 给出闭环：环境状态进入自注意力策略，策略动作推进环境，pinning/速度/动作奖励反过来训练策略。
- **图 2** 的 Dyngen 基准提供已知 GRN 与分支真值。CellTRIP 的 label-transfer accuracy 为 0.248，重构 MSE 约 221；说明其主要优势是同时保留类别与轨迹结构，而不是所有单项误差都最低。
- **图 3** 展示小鼠皮层空间坐标插补和基因敲低后的层间迁移预测。结果依赖跨数据集批次校正，论文也把这列为限制。
- **图 4** 用 trametinib 数据检验连续扰动轨迹；PCA-adjusted CellTRIP 在 48 小时预测中报告 MSE 3.87、Pearson delta 0.650，并在未参与训练的 24 小时点达到 0.72。
- **图 5** 在果蝇五个阶段、155,684 个细胞上同时检验空间与时间插补；留出阶段的空间 MSE 为 90.41，低于 MLP 333.86 和 KNN 360.33。

这些数字支持“在给定数据集和评估协议下有效”，但不证明学到的力、注意力或潜在距离就是唯一真实机制。

### 9. 代码入口与证据边界

从实现追踪方法时，建议按以下顺序阅读：

1. `celltrip/train.py::train_celltrip`：分布式训练和策略/环境初始化；
2. `celltrip/environment.py::EnvironmentBase.step` 与 `get_pinning`：动力学和奖励；
3. `celltrip/policy.py::EntitySelfAttentionLite`、`PinningNN`、`PPO`：注意力策略、解码器和优化；
4. `celltrip/memory.py::AdvancedMemoryBuffer.compute_advantages`：GAE 与截断自举；
5. `celltrip/manager.py` 及 `utility/state_manager.py`：稳态、时间插补和扰动推理。

论文提供的仓库地址是 `github.com/daifengwanglab/CellTRIP`，而本地 README 使用 `github.com/Oafish1/CellTRIP`。

### 10. 最重要的结论

CellTRIP 的核心不是把快照直接拟合成一条伪时间曲线，而是训练一个“可保留观测信息的细胞群动力环境”。残差自注意力负责让每个细胞根据群体上下文行动，pinning MLP 把潜在位置锚定回可测模态，PPO 学习如何让群体稳定到有信息的布局。空间插补、时间补点和扰动预测都建立在同一个可运行环境之上；也正因为如此，其模拟轨迹应被视为可检验的模型假设，而非已被直接观测的生物事实。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellTRIP: Inferring Virtual Cell Environments Using Multi-Agent Reinforcement Learning

**Paper**: Kalafut et al., 2025
**Repository**: [https://github.com/Oafish1/CellTRIP](https://github.com/Oafish1/CellTRIP)
**Core Technology**: Multi-agent reinforcement learning (MARL) + self-attention + PPO
**Applications**: Spatiotemporal trajectory interpolation, imputation, and perturbation in single-cell data

---

### 1. Motivation & Novelty

#### Biological Problem
Single cells continuously interact to form dynamic cell environments that drive biological processes like development, differentiation, and spatial organization. Understanding these cell-cell interactions and dynamics at the molecular level is essential but challenging because:
- Sequencing captures only static snapshots (either temporal OR spatial)
- Existing "virtual cell" models learn static representations that ignore cell environment dynamics
- No single framework handles both spatial and temporal modalities simultaneously

#### Limitations of Existing Methods
- **Static representation models** (e.g., scGPT, Geneformer): Learn per-cell embeddings but cannot model dynamic interactions
- **Trajectory inference methods**: Typically operate on population-level pseudotime, not individual cell dynamics
- **Spatial imputation methods**: Specialized for cross-modal prediction but lack temporal dynamics
- **ODE/SDE-based methods** (e.g., CellDrift, PRESCIENT): Model cell dynamics as differential equations but don't capture individual agent-level interactions

#### Unique Contributions
1. **First MARL framework for virtual cell environments**: Each cell is modeled as an independent RL agent that interacts with other cells through self-attention
2. **Unified framework for spatial AND temporal data**: Handles any combination of modalities as input
3. **Novel truncated reward bootstrapping**: Stabilizes training by bootstrapping rewards from terminal states
4. **Adaptive input rescaling (ART/PopArt)**: Normalizes observations and returns during training for stable learning
5. **Interactive virtual environment**: After training, users can perform in-silico perturbations, simulate developmental trajectories, and impute unobserved modalities
6. **Variable cell input**: Unlike fixed-input architectures, CellTRIP handles arbitrary numbers of cells

---

### 2. Method Overview

#### Algorithmic Framework
CellTRIP models cells as agents in a continuous $d$-dimensional latent environment:

1. **Environment**: Cells have positions $\mathbf{p}_i \in \mathbb{R}^d$ and velocities $\mathbf{v}_i \in \mathbb{R}^d$ in a bounded space
2. **Policy Network**: An `EntitySelfAttentionLite` model processes each cell's state (position, velocity, gene expression) through self-attention to produce force actions
3. **Reward System**: Combines:
   - **Pinning reward**: How much a concurrently trained pinning MLP improves reconstruction of target modalities from latent positions; the code also retains a least-squares fallback that is not used in the main training path
   - **Velocity penalty**: Penalizes excessive movement
   - **Action penalty**: Penalizes large force actions
   - **Distance reward**: Optional match to pairwise distances
4. **Pinning Network**: An MLP (`PinningNN`) that maps latent positions back to gene expression, trained alongside the policy
5. **Training**: Distributed PPO with Ray across multiple GPUs, with GAE (Generalized Advantage Estimation) for stable policy updates

#### Key Technical Components
- **Self-attention mechanism**: `EntitySelfAttentionLite` uses cross-attention where each cell attends to all visible cells, capturing cell-cell interactions
- **PopArt standardization**: Adaptive normalization that preserves layer outputs when rescaling (for both inputs and returns)
- **Advanced memory buffer**: Efficient replay memory with suffix caching, GAE computation, and staleness-based culling
- **Preprocessing pipeline**: Sample normalization, log1p transformation, feature filtering, PCA dimensionality reduction

#### Computational Pipeline
```
Raw AnnData → Preprocessing (normalize, log, PCA) → Environment setup
    → MARL Training (PPO + self-attention policy + pinning network)
    → Trained model checkpoints
    → Post-hoc: simulation, imputation, perturbation, trajectory recovery
```

---

### 3. Evaluation

#### Datasets
| Dataset | Type | Cells | Features | Key Task |
|---------|------|-------|----------|----------|
| **Dyngen** | Simulated GRN | 1,500 | 2,400 (gene + protein) | Trajectory recovery, TF knockdown validation |
| **Mouse Cortex** | Spatial (Visium + scRNA-seq) | 1,075 train / 4,785 validation | Genome-wide | Spatial coordinate imputation across 6 cortical layers |
| **DrugSeries** | Temporal (cancer drug) | 13,713 (5,992 trametinib-treated) | Genome-wide | Perturbation prediction, held-out 24hr recovery |
| **Flysta** | Spatiotemporal (*Drosophila*) | 155,684 | Genome-wide | Spatial imputation + developmental stage recovery (E16-18h_a held out) |
| **ExpVal** | Temporal (human brain) | Variable | Variable | Experimental validation of developmental genes |

#### Evaluation Metrics
- **Reconstruction quality**: Pairwise MSE, label transfer accuracy (Dyngen)
- **Spatial imputation**: Layer-score distributions, AUROC per cortical layer, matrix MSE of cell-type enrichment
- **Perturbation prediction**: MSE and Pearson delta ($\delta$) against ground-truth perturbed expression
- **Trajectory recovery**: Wasserstein distance (EMD) between predicted and observed cell distributions
- **Gene prioritization**: GO enrichment of top-ranked perturbation genes

#### Key Results (Quantitative)

| Experiment | Metric | CellTRIP | Best Competitor | Improvement |
|------------|--------|----------|-----------------|-------------|
| **Dyngen** | Label Transfer Accuracy | **0.248** | scScope (0.10) | 2.5× |
| **Cortex** | Excitatory cell matrix MSE | **0.042** | CellTREK (0.066) | 36% lower |
| **DrugSeries** | 48hr Pearson $\delta$ | **0.650** | GEARS (0.414) | +57% |
| **DrugSeries** | 48hr MSE | **3.87** | CPA (5.52) | 30% lower |
| **DrugSeries** | 24hr Pearson $\delta$ (held-out) | **0.72** | N/A | Interpolation |
| **Flysta** | Heldout E16-18h_a EMD | **24.5** | LERP-0.25 (82.7) | 3.4× lower |
| **Flysta** | Spatial MSE (overall) | **90.41** | MLP (333.86) | 3.7× lower |

**Biological Highlights**:
1. **Cortex**: Top perturbation genes enriched for *neuron projection morphogenesis* ($p < 10^{-3}$); Camk2n1 knockdown causes catastrophic L6b migration, consistent with known role in long-term memory
2. **Drosophila CNS**: Developmental genes enriched for *innate immune response* ($p < 2.36 \times 10^{-4}$), a known CNS protective pathway
3. **Drosophila muscle**: Enriched for *proteolysis* ($p < 2.12 \times 10^{-5}$), critical for starvation-response muscle atrophy

---

### 4. Reproducibility Assessment

#### Rating: **3.5/5** (Partially Reproducible)

#### Strengths
- **Complete codebase**: All source code available with Cython-compiled versions
- **Detailed README**: Installation instructions, training commands, and high/low-level API tutorials
- **Application notebooks**: Jupyter notebooks for all five experimental applications
- **AWS/Ray configuration**: Infrastructure config files for distributed training
- **Preprocessing pipeline**: Full data processing code included

#### Blockers
- **Data availability**: Training data (AnnData files) must be obtained separately from public repositories; not bundled
- **Compute requirements**: Training requires multi-GPU Ray cluster (AWS recommended), significant compute budget
- **Pretrained weights**: Checkpoints referenced in notebooks are stored on S3; long-term availability was not verified from this local workspace
- **Training duration**: No explicit training time estimates; hundreds of millions of timesteps required
- **Environment complexity**: Many dependencies (30+ packages), CUDA required, HDF5 with ROS3 optional

#### Hidden Complexity
- `aws_config.yaml` and `ray-ec2-launcher.json` indicate heavy AWS infrastructure dependence
- Cython compilation (`.c` and `.so` files) adds build complexity
- S3 paths hardcoded in notebooks for model weights and data

---

### 5. Cross-Document References

- **Detailed method explanation**: See doc_method.md for mathematical formulation and bio-math-code bridge
- **Code audit**: See doc_code.md for architecture details, code-paper mapping, and discrepancies
- **Figure analysis**: See figure_analysis.md for systematic figure-by-figure analysis

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
