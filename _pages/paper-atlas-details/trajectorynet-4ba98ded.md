---
layout: default
permalink: /paper-atlas/trajectorynet-4ba98ded/
title: "TrajectoryNet"
nav: false
wide: true
description: "TrajectoryNet 把不同时间点采到的细胞群看作一系列概率分布，用一个连续归一化流（continuous normalizing flow, CNF）学习随时间变化的速度场。最大似然负责让模型在观测时间点匹配数据分布，能量、密度、RNA velocity 和生长项则分别约束路径短、路径贴近数据流形、方向符合局部速度、群体质量允许增减。"
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
      <span>PMLR · 2020</span>
    </div>
    <h1>TrajectoryNet</h1>
    <p>TrajectoryNet: A Dynamic Optimal Transport Network for Modeling Cellular Dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2002.04461" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for TrajectoryNet">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/krishnaswamylab/TrajectoryNet" target="_blank" rel="noopener noreferrer" aria-label="Open code for TrajectoryNet">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TrajectoryNet 方法解读：从时间切片到连续细胞流

### 一句话结论

TrajectoryNet 把不同时间点采到的细胞群看作一系列概率分布，用一个连续归一化流（continuous normalizing flow, CNF）学习随时间变化的速度场。最大似然负责让模型在观测时间点匹配数据分布，能量、密度、RNA velocity 和生长项则分别约束路径短、路径贴近数据流形、方向符合局部速度、群体质量允许增减。

但“代码存在”不等于论文全部结果可一键复现。尤其 growth 路径缺少论文实验使用的 checkpoint，训练脚本含提前 `exit()`，固定三维输入也与论文的 5D PCA 实验不兼容。以下把方法原理、实际实现和复现边界分开说明。

### 1. 问题为什么不是普通伪时间

输入是在 $t_1,\ldots,t_k$ 不同时间点破坏性测量得到的细胞集合 $\mathcal X_{t_i}$。同一个细胞不会在下一时间点再次被测到，因此没有真实的一一对应。目标也不只是给细胞排序，而是学习连续速度场

$$
\frac{d x(t)}{dt}=f_\theta(x(t),t),
$$

使起始分布沿该场流动后，在每个观测时刻接近相应的细胞分布。给定一个起点，可以积分得到整条候选路径；给定终点，也可以反向积分，查看它在早期可能来自哪里。

这里的“trajectory”是模型在群体分布约束下推断的概率性路径，不是谱系追踪。横断面数据本身不能唯一确定单细胞历史；不同速度场可能产生相似的边缘分布。TrajectoryNet 用若干先验缩小解空间，但没有消除这种不可识别性。

### 2. 动态最优传输与 CNF 的连接

Benamou–Brenier 动态最优传输寻找密度 $P(x,t)$ 和速度场 $f(x,t)$，满足连续性方程

$$
\frac{\partial P}{\partial t}+\nabla\cdot(Pf)=0,
$$

同时最小化沿途动能

$$
(t_1-t_0)\int_{t_0}^{t_1}\int P(x,t)\lVert f(x,t)\rVert^2\,dx\,dt.
$$

CNF 同样通过 ODE 移动样本，并用瞬时变量替换公式跟踪密度：

$$
\frac{d\log P(x(t),t)}{dt}=-\operatorname{Tr}\left(\frac{\partial f_\theta}{\partial x}\right).
$$

因此 CNF 已经提供了“连续可逆流 + 密度计算”；TrajectoryNet 的关键改动是给普通最大似然 CNF 加上速度场能量。论文的 Theorem 4.1 说明，在其假设和足够大的 KL 罚参数下，终点分布松弛与能量目标趋向 $W_2$ 动态 OT。这个结论是理想化的变分结果，不表示有限网络、有限样本和有限优化迭代一定得到精确 OT 解。

代码中，`lib/layers/odefunc.py:278-311` 同时返回 $f_\theta$ 与负散度；`lib/layers/cnf.py:34-81` 用 `torchdiffeq.odeint_adjoint` 积分状态和 log-density。`train_misc.py:165-208` 构造时间条件 ODEnet，并包装成一个或多个 CNF block。这是论文核心机制的直接实现。

### 3. 为什么训练是“从晚到早”

源端经验分布没有解析密度，所以论文额外引入标准高斯基分布 $P_{t_0}=\mathcal N(0,I)$。训练时，代码从最后一个观测时间点抽样，向前一个时间点反向积分；然后把反推点与前一时间点的真实样本拼接，再继续反向积分，直至回到可计算高斯密度的起点。

`main.py:85-218` 的实际顺序是：

1. 对倒序时间点抽取一个 batch，并加入训练噪声；
2. 用 CNF 从当前积分时刻反推一个时间间隔；
3. 把上一轮反推的点和该时刻真实样本拼接；
4. 在最早端计算高斯 log-density；
5. 逐段加回 CNF 产生的 `delta_logp`，得到每个时间点样本的负对数似然；
6. 加上选择的正则项，再反向传播。

这种一次串联反向积分让所有时间点共享同一个平滑速度场，避免每对时间点各自拟合而在观测时刻产生不连续；但论文也明确承认，当时间点很多或系统 stiff 时，误差会逐段累积。

### 4. 总损失不是一个固定套餐

论文把目标写为

$$
L_T=\sum_i-\log P_{t_i}(x_{t_i})+L_{energy}+L_{density}+L_{velocity}+L_{growth}.
$$

这是一组可选模块，不是所有实验同时打开所有项。表格中的 Base、+E、+D、+V、+G 表示不同组合。

#### 4.1 能量与 Jacobian 正则

$$
L_{energy}=\lambda_e\int\lVert f\rVert^2dt+
\lambda_j\int\lVert J_f\rVert_F^2dt.
$$

第一项鼓励短而低能的路径，接近欧氏动态 OT；第二项抑制速度场的剧烈局部变化，可理解为降低弯曲或加速度。图 2 显示，无正则的 CNF 可以沿 S 形密度绕行，加能量后路径更直，但论文也指出过强能量会“欠射”目标。因此能量与流形跟随不是天然一致：路径越短，越可能穿过没有细胞的区域。

代码通过 `cnf_regularization.py` 定义 squared-L2 和 Jacobian Frobenius 积分状态，`main.py:257-265` 把积累值乘权重加入训练损失。对应关系较直接。

#### 4.2 密度正则：贴近观测流形

论文定义 $k=5$、距离阈值 $h=0.1$ 的近邻 hinge loss。代码在 `main.py:184-216` 对随机中间时刻的生成点计算到所有非留出细胞的 `torch.cdist`，取五个最近邻，只有距离超过 0.1 的部分产生惩罚。

这个正则不是概率密度估计，也不保证生物可达性。它依赖所用 PCA/PHATE 坐标、StandardScaler 和欧氏距离，并把所有观测时间点的细胞合在一起作为流形参照。它能防止轨迹穿过明显空白区，却可能让路径靠近错误时间的细胞或受采样密度影响。

#### 4.3 velocity 正则：只对齐方向

代码在每个观测细胞附近计算网络方向，并最小化负余弦相似度：

$$
L_{velocity}=-\cos(f_\theta(x,t),\widehat{dx/dt}).
$$

`main.py:164-182` 默认忽略 RNA velocity 的长度，只匹配方向；`--use_magnitude` 才切换到 MSE。论文的 EB 结果中 +V 反而变差，并在补充 Figure S3 指出 unspliced counts 只有约 10%–20%，可能使 velocity 噪声较大。这说明先验质量会直接决定正则是否有帮助。

#### 4.4 growth：不平衡质量的外部修正

论文先在相邻时间点之间解带熵和边缘 KL 松弛的离散不平衡 OT，由 coupling $\gamma$ 的行质量得到每个细胞的 growth coefficient，再训练 $G(x,t)$ 拟合这些系数。TrajectoryNet 主训练时冻结 $G$，并在逐段 log-density 中加入

$$
\log M_{t_i}=\log M_{t_{i-1}}-\int\operatorname{Tr}(\partial f/\partial x)dt+log G(x,t).
$$

论文自己说明这种处理不保证质量守恒，训练后还需归一化。更重要的是，当前快照不能完整重跑此路径：

- `optimal_transport/train_growth.py:13-40` 依赖未导入的 `atd`，加载后立即 `exit()`；真正 coupling 与训练代码不会执行；
- 同一脚本的训练循环被三引号包住；
- `lib/growth_net.py:8-19` 和脚本内模型都把输入固定为 3，即二维状态加时间，而论文 EB 实验使用 5D PCA；
- `main.py:467-476` 加载 `../data/externel/growth_model_v2.ckpt` 或 `../data/growth/model_*`，这些 checkpoint 不在快照中。

因此 growth 数学设计和主损失接入可以核对，但论文 EB 的 +G 数字不能由当前仓库直接复现。不能假设缺失 checkpoint 自动解决了维度矛盾。

### 5. 网络和求解器：论文设置不等于代码默认值

论文报告三层、每层 64 节点、LeakyReLU，10,000 iterations，batch size 1,000，Adam 学习率 0.001、weight decay $5\times10^{-5}$，dopri5 的 atol/rtol 都为 $10^{-5}$。

代码默认的 `dims=64-64-64`、`niters=10000`、`batch_size=1000`、`lr=1e-3`、`solver=dopri5` 和容差与论文一致。但 `parse.py:39` 默认 `tanh`，不是 LeakyReLU；`parse.py:69` 默认 weight decay $10^{-5}$，不是论文的 $5\times10^{-5}$。若没有论文实验命令或保存的参数，不能确认表格实际使用了论文文字配置还是代码默认配置。

依赖也存在历史边界。论文附录列出 Python 时代的 torch 1.3.1、torchdiffeq 0.0.1、scvelo 0.1.24 等；当前 `requirements.txt` 则要求 torch>=1.5.0、scikit-learn>=0.23.1，同时仍固定 torchdiffeq==0.0.1。README 称代码测试于 Python 3.7/3.8。

### 6. 留一时间点评估到底验证什么

真实单细胞数据没有单细胞轨迹真值，所以论文把一个中间时间点从训练损失中排除，再比较模型预测分布与真实留出分布的 EMD。代码在 `main.py:159-162` 把该时间点的 NLL 权重设为零；`eval_utils.py` 负责生成样本并计算分布距离。

这个评估支持“模型能否插值群体分布”，不支持“每个细胞的祖先和后代是否正确”。EMD 低的两个模型仍可能给出不同的单细胞 coupling 或基因路径。论文比较对象主要是静态 OT 的 McCann interpolant、前一时间点、后一时间点和随机分布，不是对现代轨迹推断方法的广泛 benchmark。

实验结果也不是所有数据都由同一正则获胜：合成 Arch/Tree 上 velocity 明显有益；mouse cortex 中 +D+V 最好；EB 中 density 的平均 EMD 最低，而 velocity 变差，energy 和 growth 只改善部分留出时间点。这更支持“先验需按数据质量选择”，而不是某个固定 TrajectoryNet 配方普遍最优。

### 7. 图应该怎样读

本地 11 张图包含 8 张主图和 3 张补充图，已逐张检查。

- Figure 1 是“时间切片分布 → 时间条件速度场 → 连续积分”的概念图。
- Figure 2 的 Gaussian-to-S 对比说明普通 CNF 与能量正则的路径偏好；它是二维示例，不是生物真值。
- Figures 3–4 与 S2 展示 density/velocity 先验如何让路径沿 arch、tree、cycle 流形。
- Figure 5 是 EB growth field 的可视化，但不补足缺失 checkpoint 和训练脚本问题。
- Figure 6 与 Tables 2 展示 cortex 留一时间点的分布插值。
- Figure 7 展示 EB 的 PHATE 密度和路径；PHATE 是展示坐标，不能把二维线条直接当作基因空间谱系。
- Figure 8 从选定终末群反向积分并画若干基因趋势。由于终点是人工 curated，结果适合提出早期 marker 假设，不构成 lineage tracing。
- Figure S1 只表明每次函数评估的耗时随维度近似线性；论文明确说这不代表总收敛时间随维度线性。
- Figure S3 支持 EB velocity 输入可能较噪的解释。

### 8. 输入、输出与代码路径

对自定义数据，README 要求 NPZ 至少包含形状为 cells × dimensions 的 embedding 和 `sample_labels`；也可由 notebook 把 AnnData 转为输入。`dataset.py:313-397` 的 EBData 读取本地 `eb_velocity_v5.npz`，用 StandardScaler 标准化嵌入，并在可用时同步缩放 velocity。

训练入口是 `python -m TrajectoryNet.main`：`main.py:433` 解析数据、时间点、模型和可选 growth checkpoint，再调用 `train()`。模型输出不是一个离散谱系图，而是可积分的速度场和密度变换。推断可从高斯基分布向前生成各时刻群体，也可从终末细胞反向积分保存轨迹。`eval.py` 当前主路径在保存 backward trajectories 后有 `exit()`，后面的 EMD 分支不会由该入口自然执行；评估函数仍存在于 `eval_utils.py`，但需要调用者选择正确路径。

### 9. 论文—代码匹配结论

#### Exact / 直接对应

- CNF 的 ODE 与 log-density 散度积分；
- 64-64-64 时间条件网络结构；
- 倒序跨时间点累积 NLL；
- squared-L2/Jacobian、density kNN hinge、velocity cosine 正则；
- leave-one-timepoint 训练权重与 EMD/MSE 评估函数；
- EB、合成 arch/tree/cycle 数据读取或生成路径。

#### Partial / 只部分对应

- 论文 LeakyReLU 与代码默认 tanh；
- 论文 weight decay $5\times10^{-5}$ 与默认 $10^{-5}$；
- growth 主损失接入存在，但训练脚本、维度和 checkpoint 不闭合；
- 评估工具存在，但 `eval.py` 的默认控制流含提前退出和硬编码调整；

#### Not found / 当前证据中缺失

- 生成论文全部表格和图的完整命令、seed 清单与 checkpoint；
- cortex 原始数据（论文已注明当时不公开）；
- EB growth checkpoints 与可执行的端到端 growth 训练流程；
- 现代环境上的端到端复现记录。

### 10. 最安全的使用结论

TrajectoryNet 最值得保留的思想是：用一个跨所有时间点共享的连续速度场拟合横断面分布，并把“最短运输”“贴近流形”“局部方向”“质量增减”拆成可选先验。它比逐对静态 OT 更自然地表达连续、非线性路径。

使用结果时应说“模型推断的候选连续流”而不是“恢复了真实单细胞命运”。留一时间点 EMD 验证的是分布插值；反向基因轨迹、分支归属和 growth 权重仍依赖模型先验。若要复现，先从 Base 或 +D 的无 growth 路径开始，显式传入论文参数并记录环境；growth 结果应在修复训练脚本、输入维度和 checkpoint 来源之前视为不可复现边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## TrajectoryNet: A Dynamic Optimal Transport Network for Modeling Cellular Dynamics

**Paper**: Tong, Huang, Wolf, van Dijk, Krishnaswamy. *ICML 2020* (Proceedings of the 37th International Conference on Machine Learning, PMLR 119).

**Code**: [https://github.com/KrishnaswamyLab/TrajectoryNet](https://github.com/KrishnaswamyLab/TrajectoryNet)

---

### Motivation & Novelty

#### Biological Problem
Single-cell RNA sequencing (scRNA-seq) captures static snapshots of gene expression across cells, but cells are destroyed during measurement, making it impossible to track individual cell trajectories over time. With only a handful of discrete timepoints collected, researchers must infer the continuous dynamics of cellular differentiation, including:
- How cells transition between states (e.g., stem cells to differentiated lineages)
- Which genes drive fate decisions at specific developmental stages
- The branching structure of cell fate hierarchies

#### Limitations of Existing Approaches
- **Pseudotime methods** (Diffusion Pseudotime, *Nature Methods* 2016; Monocle, *Nature Biotechnology* 2014; as reviewed in Saelens et al., *Nature Biotechnology* 2019): Operate on a single timepoint, can be biased, and do not incorporate experimental time
- **Static optimal transport** (Waddington-OT/Schiebinger et al., *Cell* 2019; SCOT/Yang & Uhler, *ICLR* 2019): Match populations between pairs of timepoints linearly, assuming shortest Euclidean paths; cannot model non-linear or manifold-following trajectories; produce discontinuities at measured timepoints
- **RNA velocity** (La Manno et al., *Nature* 2018; Bergen et al., *bioRxiv* 2019): Estimates local direction of change but cannot give accurate global distributional dynamics
- **Population-level dynamics** (Hashimoto et al., *ICML* 2016): Model population dynamics but use coarse-grained matching between timepoints

#### Unique Contributions
1. **First method** to establish a computational link between continuous normalizing flows (CNFs) and dynamic optimal transport (DOT), enabling efficient neural ODE-based solving of DOT in high dimensions
2. **Continuous-time trajectories**: Unlike pairwise static OT, produces smooth, continuous paths between all timepoints simultaneously using a single parametric model
3. **Modular biological priors**: Integrates growth rate correction (unbalanced transport), manifold density regularization, and RNA velocity direction supervision into a unified loss framework
4. **Theorem 4.1**: Proves that CNF with energy regularization converges to the $W_2$ optimal transport solution for sufficiently large penalty weight

---

### Method Overview

#### Core Idea
TrajectoryNet parameterizes a time-dependent velocity field $f_\theta(x, t)$ using a neural ODE, where $x$ is a cell's state (gene expression in PCA space) and $t$ is time. The velocity field transforms a simple base distribution (standard Gaussian) to match observed cell distributions at each measured timepoint. By adding an energy penalty $\|f\|^2$ on the velocity field, the learned paths approximate dynamic optimal transport — the minimum-cost smooth flow between distributions.

#### Algorithmic Framework
1. **Architecture**: 3-layer MLP with 64 hidden units and LeakyReLU/tanh activations, taking $(x, t) \mapsto dx/dt$ via ConcatSquash time-conditioning
2. **Training**: Backward integration from the last timepoint to the base Gaussian, accumulating log-likelihood at each intermediate timepoint; ODE solved with dopri5 (adaptive Runge-Kutta)
3. **Energy regularization**: Penalizes $\int_t \|f(x,t)\|^2 dt$ (path energy) and $\int_t \|J_f(x)\|_F^2 dt$ (Jacobian Frobenius norm for curvature)
4. **Biological priors**: Growth rate model (2-layer MLP trained from unbalanced OT), density-based manifold regularization (k-NN hinge loss), velocity direction supervision (cosine similarity with RNA velocity)

#### Computational Pipeline
```
Raw scRNA-seq → PCA (5D) → StandardScaler normalization
→ TrajectoryNet training (Neural ODE with regularization)
→ Forward integration for trajectory generation
→ Backward projection to gene space for biological interpretation
```

---

### Evaluation

#### Datasets
| Dataset | Type | Timepoints | Cells | Dimensions |
|---------|------|------------|-------|------------|
| Arch | Synthetic (1D manifold in 2D) | 3 | 15,000 | 2 |
| Tree | Synthetic (branching) | 3 | 15,000 | 2 |
| Cycle | Synthetic (circular) | 3 | 10,000 | 2 |
| Mouse Cortex | Real scRNA-seq (E12.5-E17.5) | 4 | ~20,000 | 5 (PCA) |
| Embryoid Body | Real scRNA-seq (Day 0-24) | 5 | ~16,000 | 5 (PCA) |

#### Metrics
- **EMD (Earth Mover's Distance)**: Wasserstein distance between predicted and held-out distributions at intermediate timepoints (leave-one-out validation). Lower = better.
- **MSE**: Mean squared error between predicted and true individual cell positions for synthetic data with known ground truth paths.

#### Comparative Results

**Artificial Data (Table 1)**:

| Method | EMD Arch | EMD Tree | EMD Cycle | MSE Arch | MSE Tree | MSE Cycle |
|--------|----------|----------|-----------|----------|----------|-----------|
| **Base+V** | **0.243** | **0.143** | 0.033 | **0.107** | **0.098** | **0.068** |
| Base+D | 0.607 | 0.373 | 0.049 | 0.236 | 0.145 | 0.191 |
| Base | 0.691 | 0.490 | 0.037 | 0.300 | 0.218 | 0.190 |
| OT | 0.644 | 0.492 | 0.032 | 0.252 | 0.196 | 0.192 |

Velocity regularization (+V) is the most effective: 2.6× EMD improvement on Arch vs. OT, 3.4× on Tree. The Cycle dataset is notable because the distribution is unchanging (uniform circle) — without velocity supervision, no method can detect the counterclockwise rotational dynamics, making +V essential.

**Mouse Cortex (Table 2)**:

| Method | rep1 | rep2 | mean |
|--------|------|------|------|
| **Base+D+V** | $0.851 \pm 0.08$ | $0.866 \pm 0.07$ | **$0.859 \pm 0.07$** |
| Base+D | $0.882 \pm 0.03$ | $0.895 \pm 0.03$ | $0.888 \pm 0.03$ |
| OT | 1.098 | 1.095 | 1.096 |

TrajectoryNet+D+V achieves ~22% improvement over static OT. The curved manifold structure of neurogenesis data makes density and velocity regularization jointly effective.

**Embryoid Body (Table 3)**:

| Method | t=1 | t=2 | t=3 | mean |
|--------|-----|-----|-----|------|
| **Base+D** | 0.759 | **0.783** | **0.811** | **0.784** |
| Base+G | **0.700** | 0.913 | 0.829 | 0.814 |
| Base | 0.764 | 0.811 | 0.863 | 0.813 |
| OT | 0.791 | 0.831 | 0.841 | 0.821 |
| Base+V | 0.816 | 0.839 | 0.865 | 0.840 |

Density regularization helps the most overall (mean EMD 0.784 vs. OT 0.821). Velocity regularization *hurts* performance here (0.840 > 0.813 base), attributed to low unspliced RNA counts (~10-20% vs. typical 30%), leading to noisy velocity estimates. Growth regularization (+G) dramatically improves the earliest timepoint (0.700 vs. 0.764) but worsens later ones.

#### Benchmarked Methods
| Method | Description | Source |
|--------|-------------|--------|
| OT (McCann interpolant) | Static optimal transport via Sinkhorn, linear interpolation | Schiebinger et al., *Cell* 2019 |
| prev/next | Use previous or next timepoint as prediction | Baseline |
| rand | Random timepoint as prediction | Baseline |

#### Biological Validation
- Backward integration of TrajectoryNet trajectories from terminal cell types to gene space recapitulates known biology: HAND1 (cardiac marker) distinguishes populations early (Day 6); ONECUT2 (neuronal) distinguishes only at later timepoints (consistent with Moon et al., *Nature Biotechnology* 2019, Figure 6)

---

### Reproducibility

#### Rating: 4/5

#### Strengths
- Code is publicly available and well-organized as a pip-installable Python package
- Paper provides detailed hyperparameter specifications (Section 5, Appendix E)
- Artificial datasets are fully reproducible with seeded random generation
- Software versions are specified (Appendix E.3)

#### Blockers
- **Mouse cortex data**: "not currently publicly available" (paper Section E.2) — one of two real datasets cannot be reproduced
- **Embryoid body data**: Available at [https://doi.org/10.17632/v6n743h5ng.1](https://doi.org/10.17632/v6n743h5ng.1) (Mendeley Data), but requires preprocessing with CellRanger and velocyto
- **Growth model checkpoints**: Training code references hardcoded paths (`../data/externel/growth_model_v2.ckpt` — note typo "externel"); pre-trained growth model files are not included in the repository. Additionally, `GrowthNet` hardcodes input dimension to 3, incompatible with 5D PCA data
- **Dependency versions**: Requires older versions (torch==1.3.1, torchdiffeq==0.0.1) which may not be readily installable on modern systems
- **Code-paper mismatch**: Paper states LeakyReLU activations (§4.3, §5) but code defaults to tanh; paper states weight decay $5 \times 10^{-5}$ but code defaults to $10^{-5}$
- **Runtime**: Each training run is 10,000 iterations on GPU; hyperparameter search over regularization weights adds significant compute

#### Limitations
- **Scalability**: While computation scales linearly with dimension per iteration, convergence speed for complex distributions is not characterized
- **Static growth model**: Growth rates are learned from discrete OT and then frozen — they cannot adapt during TrajectoryNet training, creating a chicken-and-egg problem
- **Backward accumulation error**: Training integrates backward from the last timepoint; numerical error compounds for early timepoints when $k$ is large or the system is stiff (acknowledged in §4.3)
- **No stochastic dynamics**: The deterministic ODE formulation cannot model stochastic fluctuations in gene expression; extending to SDEs is identified as future work (§6)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
