---
layout: default
permalink: /paper-atlas/pseudodynamicsplus-808717ce/
title: "PseudodynamicsPlus"
nav: false
description: "时间序列 scRNA-seq 给出不同时间点的细胞状态快照，但每次捕获的细胞数通常由实验采样深度决定，并不等于组织中的真实细胞总数。如果某个状态在后期占比增加，至少有三种解释：该状态内细胞增殖、其他状态向它分化，或随机扩散使密度进入该区域。只看归一化后的单细胞比例无法区分这些机制。 Pseudodynamics+ 的输入因此有两部分： 每个时间点的单细胞状态坐标 \\mathbf s 与时间标签 t；"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>PseudodynamicsPlus</h1>
    <p>Pseudodynamics+: Reconstructing Population Dynamics from Time-Resolved Single Cell Landscapes with Physics Informed Neural Networks</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2025.11.30.691399" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Pseudodynamics+：把单细胞状态变化与真实组织规模放进同一个动力学模型

### 1. 核心问题：细胞“变多”与细胞“流过来”不能混为一谈

时间序列 scRNA-seq 给出不同时间点的细胞状态快照，但每次捕获的细胞数通常由实验采样深度决定，并不等于组织中的真实细胞总数。如果某个状态在后期占比增加，至少有三种解释：该状态内细胞增殖、其他状态向它分化，或随机扩散使密度进入该区域。只看归一化后的单细胞比例无法区分这些机制。

Pseudodynamics+ 的输入因此有两部分：

1. 每个时间点的单细胞状态坐标 $\mathbf s$ 与时间标签 $t$；论文主要在 diffusion map 等低维转录组坐标中建模。
2. 独立测量的组织/群体总细胞数 $N_t$。

输出不是一条单一伪时间，而是连续密度 $u(\mathbf s,t)$ 及三个随状态和时间变化的行为参数：净增长率 $g(\mathbf s,t)$、定向漂移/分化速度 $\mathbf v(\mathbf s,t)$、扩散系数 $D(\mathbf s,t)$。它们还能用于时间点插补、轨迹模拟、分化相关基因检测和连续密度转移图。

### 2. 概率密度必须恢复成“有质量”的细胞密度

普通 KDE 在每个时间点积分为 1。Pseudodynamics+ 定义的是非归一化密度：

$$
N_t=\int_{S}u(\mathbf s,t)\,d\mathbf s.
$$

也就是说，密度曲线的面积对应真实总体规模。代码 `reader.py` 先在细胞状态空间估计相对密度，再用 `popD['mean']` 等人口规模信息进行缩放。训练数据集还按密度幂次构造采样概率，并以默认约 0.5 的概率从高密度区域重采样边界点。这让网络更频繁看到对总体质量贡献大的区域，但也意味着低密度、稀有状态的拟合可能更弱。

论文先在单支巨核细胞数据上比较 KDE、hash KDE、TIGON GMM、Denmarf 和 Mellon，并比较 PC 与 diffusion map 坐标。以一维伪时间密度为参照，作者选择 diffusion map + 传统 Gaussian KDE。这个选择来自该基准，不代表所有数据集的最佳密度估计器；仓库另有 `dudt_train_mellon.py`，说明 Mellon 是可替换路线。

### 3. 控制方程：增长、漂移与扩散共同改变密度

方法采用 advection–reaction–diffusion 方程：

$$
\frac{\partial u}{\partial t}
=g(\mathbf s,t)u
-\nabla_{\mathbf s}\cdot\bigl(\mathbf v(\mathbf s,t)u\bigr)
+\nabla_{\mathbf s}\cdot\left(D(\mathbf s,t)\nabla_{\mathbf s}u\right).
$$

从左到右可读成：

- $g u$：原地净出生/死亡带来的密度增减；$g>0$ 是净扩张，$g<0$ 是净损失。
- $-\nabla\cdot(\mathbf v u)$：细胞沿确定性状态速度流入或流出。
- $\nabla\cdot(D\nabla u)$：未被定向速度解释的随机状态扩散。

这三项在有限快照下并不天然可辨识。模型通过神经网络结构、正则项、总体规模、额外的状态增量信息和跨时间数据共同约束它们。因而推断的 $g$、$\mathbf v$、$D$ 是在指定模型与损失下的有效参数，不是直接实验测得的单细胞分裂率、RNA velocity 或物理布朗扩散常数。

### 4. 为什么使用 Physics-Informed Neural Network

传统数值 PDE 方法需要在状态空间建网格；维数升高或出现分支时，网格数量爆炸。Pseudodynamics+ 用四组神经网络替代网格：

- surrogate network $u_\theta(\mathbf s,t)$ 近似连续密度；
- behaviour networks 分别近似 $g_\phi$、$\mathbf v_\psi$ 和 $D_\omega$。

`_PINN_base.py` 通过自动微分计算 $\partial_tu$、状态梯度、散度和二阶导数。把四个网络代入控制方程得到残差

$$
R(\mathbf s,t)=
\partial_tu_	heta-gu_	heta
+\nabla\cdot(\mathbf v u_	heta)
-\nabla\cdot(D\nabla u_	heta).
$$

训练同时在两类点上约束模型：实验时间点/细胞状态附近的边界点要求预测密度接近人口规模校正后的 KDE；在状态—时间域内抽取的 collocation points 要求 PDE 残差接近零。另有增长、平滑、扩散和可选 `deltax` 等损失或惩罚，限制行为网络走向任意分解。

代码里存在重要的实现分支：常规 `pde_params.training_step` 会计算并记录 `R_loss`，但当前实现的 `total_loss` 没有把它加进去；`pde_params_fastmode` 则将残差项纳入总损失。因此不能笼统写成“所有入口都以同样方式强制 PDE”。使用者必须确认命令行选择的模型类和实际总损失。这个差异会直接影响“physics-informed”的强度。

### 5. 从训练到推断的完整数据流

1. 从 AnnData 读取时间标签、低维状态坐标和总体规模。
2. 在每个观测时间点做 KDE，并把积分质量缩放到 $N_t$。
3. 构造训练/验证/测试切分、密度加权边界点与随机 collocation points。
4. 初始化密度网络和 $g,\mathbf v,D$ 行为网络。
5. 以密度拟合、PDE 残差及行为正则联合训练；不同模型类的实际损失组合必须从代码核对。
6. 用学到的 $u,g,\mathbf v,D$ 在未观测时间预测密度和总体规模。
7. 对 $d\mathbf s/dt=\mathbf v(\mathbf s,t)$ 做 ODE 积分得到确定性轨迹；可选随机模式按 $\sqrt{2D}$ 添加噪声。
8. 联合增长和迁移构建 continuous density transport（CDT），回答某一初始状态的质量何时、向何处流动并保留多少。

`main_train.py` 是主要训练入口，支持从工作目录或 `data/` 下读取 `{dataset}.h5ad`。配置会记录状态键、时间点、维数、总体规模相关参数和损失权重。论文图使用的完整运行日志、外部基线脚本及所有图形 notebook 并未随仓库快照提供，因此包级接口可运行不等于论文全部结果可一键复现。

### 6. 轨迹与连续密度转移不是同一个对象

`Density_Transfer.cellstate_drift()` 用 `torchdiffeq.odeint` 积分

$$
\frac{d\mathbf s}{dt}=\mathbf v(\mathbf s,t).
$$

这给出状态坐标中的细胞轨迹；随机模式再加入由 $D$ 决定的噪声。轨迹只描述“位置怎样移动”，不自动携带该轨迹上的细胞质量。

CDT 则同时积分状态与密度，把初始密度拆为沿轨迹向后输送的部分和在时间步内保留/扩散的部分，最后得到每个初始细胞对应的三角形时间转移矩阵。归一化矩阵近似回答“这份初始质量在不同时间步的去向”，原始矩阵保留总体规模。它不同于 CellRank 的吸收概率，也不同于相邻快照的静态 OT coupling；论文利用它分析祖细胞输出偏向如何随时间变化。

### 7. 六张主图如何验证方法

#### 图 1：框架定义

图 1 把单细胞快照和总体规模输入、surrogate/behaviour networks、PDE/Neural ODE 约束，以及时间插补、轨迹、基因检测和 CDT 输出连成一条流程。它是方法结构图，不是性能证据。

#### 图 2：胚胎胸腺发育

在 E12.5–E19.5 的约 4.8 万个胸腺细胞中，旧 pseudodynamics-v1 把复杂分支压到一维伪时间；Pseudodynamics+ 在多维 diffusion map 上估计状态特异行为。两者都恢复总体扩增，但新方法识别出 progenitor、Phase 2 和 DP 的三轮增殖波。DP 区域较高的 G2M 比例为第三轮增殖提供独立一致性证据。速度/分化率与已知转录程序的对应支持状态分辨率提升，但不是直接逐细胞追踪。

#### 图 3：LARRY 克隆条形码基准

LARRY 提供跨时间克隆关系，可用于检验预测的后代分布和命运概率。论文将 Pseudodynamics+ 与 flow-matching 等模型比较，报告未来状态生成和命运预测具有竞争力。这里的“ground truth”是克隆层面的祖先—后代约束，不是每个细胞的连续真实轨迹；同一克隆内仍存在多种状态。

#### 图 4：长期体内骨髓造血

在持续标记、长达九个月的小鼠骨髓数据中，模型用观测与预测总体规模、各细胞类型密度及状态图上的增长/分化率重建组织流。图中增长和分化率在不同谱系区域随时间改变，且基因关联测试找到与增殖、干性维持和髓系分化一致的表达程序。基因测试是“表达沿推断参数变化的统计关联”，不能改写为基因对参数的因果调控。

#### 图 5：中间时间与连续流验证

论文用留出时间点和轨迹模拟检查模型能否生成未观测的连续状态，并比较预测密度/总体规模。插补质量说明学到的场能连接观测快照，但不能单独证明 $g,\mathbf v,D$ 的分解唯一。

#### 图 6：祖细胞输出偏向

CDT 把 MEP 等祖细胞密度分配到红系和巨核系终点。结果显示早期偏巨核、随后趋于平衡，并用状态依赖基因与输出评分解释这种变化。图中还含 CellRank 比较，但当前仓库没有找到 Fig. 6e 的完整 CellRank 运行代码，因此只能从论文图文验证，不能从本地代码复跑。

### 8. 论文—代码对应

| 论文组件 | 本地代码 | 判断 |
|---|---|---|
| 非归一化人口密度 | `reader.py` | **Direct/Partial**：KDE 与总体规模缩放可见，结果依赖外部 `pop_dict` |
| PINN 自动微分 | `_PINN_base.py` | **Direct**：时间导数、梯度、散度和 Laplacian 辅助函数可见 |
| $g,\mathbf v,D$ 与 PDE | `_pde_informed_params.py` | **Partial**：核心公式存在，但不同模型类是否把 `R_loss` 纳入总损失不一致 |
| 密度加权重采样 | `reader.py:238-273` | **Direct**：高密度区域按幂次概率重采样 |
| 轨迹 ODE | `_density_transport.py:67-113` | **Direct**：确定性和可选随机状态积分可见 |
| CDT | `_density_transport.py:115-250` | **Direct/Partial**：分步质量输送实现可见，计算成本高且需训练 checkpoint/输入 |
| 分化相关基因 | `de_test/` | **Partial**：GAM/统计工具存在，论文所有图形配置不齐 |
| LARRY 外部基线、Fig. 6e CellRank | 当前快照未找到 | **Not found** |
| 论文完整 figure notebooks | `docs/notebooks/` 仅教程 | **Not found** |

总体上，核心方法实现与论文结构匹配，可评为中等偏高的 paper–code fidelity；端到端论文复现仍约为 3/5，因为大型数据、训练 checkpoint、精确实验配置、外部基线和若干作图/评估脚本缺失。

### 9. 最容易误读的边界

- **人口规模是额外输入，不是从 scRNA-seq 捕获数自动推断。** 若 $N_t$ 不可靠，绝对增长率也会受影响。
- **低维坐标不是原始基因空间。** 漂移向量首先表示 diffusion map/PC 空间中的状态变化，再通过邻域或基因关联解释。
- **漂移不是 RNA velocity。** 它来自跨时间密度和 PDE 的全局拟合，不依赖剪接动力学。
- **扩散不是测量噪声的完整分解。** 它吸收模型未由确定性漂移解释的随机状态传播。
- **PDE 残差的实际使用取决于代码路径。** 常规类与 fastmode 的总损失不同，必须报告所用类。
- **CDT 是模型推断的质量转移。** 它不是克隆示踪或静态 OT 的同义词。
- **图中的生物学一致性是验证而非唯一性证明。** 相似密度预测仍可能由不同参数组合产生。

Pseudodynamics+ 最有价值的思想，是把“单细胞状态的相对分布”恢复为“具有真实总质量的组织流”。只有在总体规模、状态漂移、局部增长和随机扩散同时进入守恒方程后，模型才有机会区分一个细胞群究竟是原地扩增，还是由上游状态持续补充。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PseudodynamicsPlus

### Citation

Zheng W., Barile M., Wilson N. K., Huang Y., Theis F. J., and Gottgens B. **Pseudodynamics+: Reconstructing Population Dynamics from Time-Resolved Single Cell Landscapes with Physics Informed Neural Networks.** bioRxiv, 2025. DOI: `10.64898/2025.11.30.691399`.

### Motivation and Novelty

Pseudodynamics+ addresses a gap in time-resolved single-cell analysis: scRNA-seq snapshots describe relative cell-state composition, but not the true tissue-scale number of cells flowing through the landscape. Methods such as Waddington-OT, TrajectoryNet, MIOFlow, TIGON, OT-CFM, and SF2M model transport or generative trajectories, while pseudodynamics-v1 modeled population dynamics along one-dimensional pseudotime. The key novelty of Pseudodynamics+ is to model an unnormalized cell density over multidimensional cell-state space, scaled by measured population size, and to infer continuous growth, drift, and diffusion fields with a physics-informed neural network.

The method is especially aimed at developmental or homeostatic systems where differentiation, proliferation, death, and stochastic dispersion are simultaneous. Its most distinctive output is not only a predicted future cell state, but interpretable dynamic parameters: local net growth, directed differentiation velocity, diffusion, and density transport from selected source populations.

### Method Overview

Input data are time-resolved single-cell profiles, low-dimensional cell-state coordinates, time labels, and population-size measurements. The observed density `u(s,t)` is estimated on the cell-state landscape, usually in diffusion-map coordinates, and scaled so its integral matches total population size `N_t`.

Pseudodynamics+ then fits four neural components: a surrogate density network `u_theta(s,t)` and behavior networks for growth `g(s,t)`, drift `v(s,t)`, and diffusion `D(s,t)`. These functions enter an advection-reaction-diffusion PDE:

```text
density change = growth-driven mass change - drift divergence + diffusion dispersion
```

Training combines density matching at observed timepoints, NeuralODE simulation between timepoints, PDE residual terms, and regularization on diffusion, velocity direction, and growth/population behavior. After training, the model can impute intermediate densities, simulate cell-state trajectories, rank genes associated with drift changes, and compute continuous density transport maps.

### Main Results

In embryonic thymus development, Pseudodynamics+ recovers tissue-scale population expansion and identifies three proliferative waves. The third wave aligns with a high G2M fraction in DP-like cells, supporting the multidimensional model over pseudodynamics-v1's pseudotime-only formulation.

On LARRY lineage-barcoded hematopoiesis, Pseudodynamics+ shows competitive fate prediction and trajectory simulation. It is close to OT-CFM and SF2M in endpoint fate prediction, but the Wasserstein-distance panel shows that it is not uniformly best across all trajectory metrics.

In long-term in vivo mouse hematopoiesis, the method models the expansion of tdTomato-labeled HSC progeny over 269 days, imputes held-out cell-type densities, and reveals time-dependent lineage dynamics. The paper argues for an early megakaryocyte-biased phase followed by later balanced homeostatic hematopoiesis. Continuous density transport further localizes this transition to MEP output, where early mass is more megakaryocyte-biased and later output becomes more balanced.

### Code Reproducibility

The public repository contains the core implementation for the main model, density preprocessing, NeuralODE simulation, parameter evaluation, continuous density transport, and drift-associated gene utilities. The code match is **medium fidelity**: the central algorithm is implemented, but exact paper figure notebooks, large data assets, external benchmark scripts, and substantive CellRank fate-probability scripts were not found.

Important paper-code caveat: the paper presents the PDE residual loss as part of the total objective. In the inspected code, `pde_params_fastmode` includes this residual in the total loss, but the base `pde_params.training_step` computes and logs `R_loss` while omitting it from the final summed loss. Saved configs in the public repo use `pde_params`, so this is a real implementation ambiguity.

**Reproducibility score: 3/5.** The main method can be understood and partly reused from the public code, but a reader cannot fully reproduce the paper's benchmark panels, figure generation, or all downstream analyses from the repository alone.

### Practical Takeaways

Pseudodynamics+ is a strong fit when the system has real time-series sampling, a biologically meaningful low-dimensional manifold, and measured or defensible population-size estimates. It is less appropriate for single snapshots, distorted embeddings, or systems where density changes are dominated by sampling bias. The inferred parameters should be interpreted as model-based tissue flux descriptors, not direct causal gene regulation or direct lineage tracing.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
