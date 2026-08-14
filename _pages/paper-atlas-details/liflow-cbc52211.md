---
layout: default
permalink: /paper-atlas/liflow-cbc52211/
title: "LiFlow"
nav: false
wide: true
description: "LiFlow 不再像传统分子动力学那样每隔约 1 fs 计算一次力并逐步积分，而是把“从当前晶体构型跳到较晚时刻的构型”改写成一个条件位移生成问题：Propagator 负责生成较长时间间隔后的原子位移，Corrector 再修正局部不合理结构。论文发表于 Nature Machine Intelligence（2025），DOI 为 10.1038/s42256-025-01125-4。"
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
      <span>Machine Learning Algorithm</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>LiFlow</h1>
    <p>Flow matching for accelerated simulation of atomic transport in crystalline materials</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/learningmatter-mit/liflow" target="_blank" rel="noopener noreferrer" aria-label="Open code for LiFlow">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## LiFlow 方法详解

### 一句话理解

LiFlow 不再像传统分子动力学那样每隔约 1 fs 计算一次力并逐步积分，而是把“从当前晶体构型跳到较晚时刻的构型”改写成一个**条件位移生成问题**：Propagator 负责生成较长时间间隔后的原子位移，Corrector 再修正局部不合理结构。论文发表于 *Nature Machine Intelligence*（2025），DOI 为 `10.1038/s42256-025-01125-4`。

### 证据边界

本地论文 Markdown 是 328 行的订阅预览，只包含摘要、图、扩展数据图说明、数据/代码可用性声明和参考文献，没有 Methods 正文、论文公式与补充材料。因此本文严格区分：

- **论文声明**：来自 `paper.md:9-12`、图 1-3 与扩展数据图。
- **代码确认**：来自 commit `e6fc475361d046865f12cae1aee11c4f56c48d87` 的直接源码行。
- **解释性推断**：用于帮助理解，但不冒充论文原文。
- **Not found / MISSING**：本地证据无法核实的内容。

下面的训练公式是从可执行代码还原的，不是论文公式的转录；论文中的原始符号和公式编号 **Not found**。

### 1. 它要解决什么问题？

锂离子在固态电解质中的扩散决定了材料的离子传导性能。AIMD 精度高，但要在每个很小的时间步上计算电子结构，难以同时扩展到：

- 数千种候选材料；
- 更大的超胞；
- 更长的轨迹；
- 足以估计低扩散率的时间尺度。

论文摘要明确把 AIMD 的尺度限制作为出发点，并报告 LiFlow 在 4,186 种固态电解质候选材料、四个温度、每条 25 ps 的轨迹上进行训练和评估 (`paper.md:9-12`)。

论文参考文献还列出机器学习势、Timewarp（NeurIPS 2023）、隐式转移算子（NeurIPS 2023）、Score Dynamics（*J. Chem. Theory Comput.* 2024）和 F3low（arXiv 2024）等相关路线 (`paper.md:98-108`)。但订阅预览没有 Introduction 正文，所以论文对每个具体方法的批评与差异 **Not found**，不能据此自行补写。

### 2. 核心思路

普通 MD 的思路是：

```text
当前构型 -> 算力 -> 积分 1 fs -> 再算力 -> 再积分 1 fs -> ...
```

LiFlow 的思路是：

```text
当前构型
  -> 根据温度、质量和迁移率类别采样一个物理先验位移
  -> Propagator 生成较长时间间隔后的构型
  -> Corrector 修正局部不合理几何
  -> 去除整体质心漂移
  -> 得到下一个粗时间步构型
  -> 重复，形成长轨迹
```

图 1 直接展示了这个“Propagator flow -> Corrector flow”的两阶段结构，并把目标迁移能力分为 composition、thermal condition 和 supercell size (`figure_01.png`; `paper.md:58-60`)。

### 3. 输入和输出

发布代码不直接读取原始 AIMD 输出，而是假设数据已经整理为：

| 文件/变量 | 含义 | 形状或内容 |
|---|---|---|
| `positions_{temp}K.npz` | 各材料在某温度下的轨迹 | `[n_frames, n_atoms, 3]` |
| `atomic_numbers.npy` | 原子序数 | 每个材料一个 `[n_atoms]` 数组 |
| `lattice.npy` | 晶胞矩阵 | 每个材料一个 `[3,3]` 数组 |
| `element_index.npy` | 原子序数到模型元素索引的映射 | 一维数组 |
| `train/test_{temp}K.csv` | 材料名、温度、时间区间、组成、MSD 和先验类别 | 表格 |
| Propagator/Corrector checkpoint | 训练后模型 | `.ckpt` |

直接证据见 `liflow/README.md:44-86` 与 `liflow/liflow/data/dataset.py:43-55,133-145`。

输出有两种：

- `FlowSimulator.run` 返回连续的坐标数组列表 (`liflow/liflow/utils/inference.py:168-210`)；
- 通用数据集评估写出包含锂/骨架 MSD、RDF MAE 和完成步数的 CSV (`liflow/liflow/experiment/test.py:81-123`)；LGPS 脚本写出 XYZ 轨迹 (`liflow/scripts/test_LGPS.py:87-108`)。

### 4. Propagator 如何构造训练样本？

`TimeDelayedPairDataset` 在一个允许的时间区间中随机选择起点 $s$，再用固定延迟 $\Delta$ 选择终点 (`liflow/liflow/data/dataset.py:150-165`)：

$$
x_{\mathrm{cond}}=R_s,\qquad x_1=R_{s+\Delta}.
$$

其中：

- $x_{\mathrm{cond}}$ 是当前构型，也是模型的条件；
- $x_1$ 是较晚时刻的真实构型；
- 默认在起点构型上建立 5 Å 截断的周期性邻居图 (`liflow/liflow/data/dataset.py:167-210`)。

通用模型联合使用 600、800、1,000、1,200 K 的数据，并按组成频率的倒数加权采样，避免高频组成主导训练 (`liflow/scripts/train_universal.sh:4-18`; `liflow/liflow/data/modules.py:190-246`)。

### 5. 自适应 Maxwell-Boltzmann 先验

#### 为什么需要先验？

不同元素、温度和材料中的原子位移尺度差别很大。若所有材料都从同一个高斯噪声尺度开始生成，模型必须同时覆盖几乎不动的框架原子和快速扩散的锂离子。LiFlow 先给出一个具有物理尺度的随机位移，再学习其余结构化信息。

#### 代码中的采样公式

对原子 $i$，代码使用

$$
\epsilon_i\sim\mathcal{N}(0,\sigma_i^2 I_3),
$$

$$
\sigma_i=a_{g(i),c_g}\sqrt{\frac{k_BT}{m_i}},
$$

其中：

- $m_i$ 是原子质量；
- $T$ 是温度；
- $g(i)$ 表示锂原子或框架原子；
- $c_g\in\{0,1\}$ 是 small/large prior 类别；
- $a_{g,c}$ 是对应的尺度乘子。

源码位于 `liflow/liflow/utils/prior.py:44-66`。通用模型默认尺度为

$$
a_{\mathrm{Li}}=[1,10],\qquad
a_{\mathrm{frame}}=[0.316,3.16]
$$

(`liflow/liflow/config/train.yaml:25-30`)。

#### small/large 类别从哪里来？

`prior_classifier.ipynb`：

1. 用 MACE 提取初始结构描述符；
2. 分别对锂原子和非锂框架原子取平均描述符；
3. 拼接 $T/1000$；
4. 用 $\log_{10}(\mathrm{MSD}/\tau)=-1$ 作为二分类阈值；
5. 分别训练隐藏层为 `(32,16)` 的 MLP 分类器；
6. 把预测类别写回所有训练/测试 CSV。

这是 **Notebook** 级证据：仓库没有打包好的分类器模块，也没有保存的分类器权重。扩展数据图 6 显示 large prior 总体富集于高迁移率样本，但两类在阈值附近明显重叠 (`figure_09.jpg`)。所以它是粗粒度的迁移率分档，不是连续、校准后的迁移率预测器。

### 6. Flow Matching 训练目标

对一个训练样本，记：

- $x_{\mathrm{cond}}$：条件构型；
- $x_1$：目标构型；
- $\epsilon$：先验位移；
- $t\sim U[0,1]$：每个图随机采样的流时间。

默认 velocity 模式先定义

$$
x_0=x_{\mathrm{cond}}+\epsilon,
$$

然后沿直线路径插值：

$$
x_t=(1-t)x_0+t x_1.
$$

这条路径的目标速度是常数：

$$
u_t=\frac{dx_t}{dt}=x_1-x_0.
$$

模型输出每个原子的三维速度，训练损失为

$$
\mathcal{L}=\frac{1}{N}\sum_{i=1}^{N}
\left\|v_\theta(x_{\mathrm{cond}},x_t,t,T,Z)_i-(x_{1,i}-x_{0,i})\right\|_2^2.
$$

这些运算逐行对应 `liflow/liflow/model/modules.py:31-57`。代码还支持 `data` 模式直接预测位移 $x_1-x_{\mathrm{cond}}$，但仓库提供的训练脚本没有覆盖默认 velocity 模式，因此论文实验是否使用 `data` 模式 **Not found**。

### 7. DualPaiNN 看到了什么？

模型不是只看当前流位置 $x_t$，而是同时看：

- 条件构型 $x_{\mathrm{cond}}$；
- 当前流构型 $x_t$；
- 原子元素 $Z$；
- 流时间 $t$；
- 温度 $T/1000$；
- 周期性邻居边和晶胞镜像位移。

对每条边 $(i,j)$，它分别在两个坐标场上计算距离和方向：

$$
r^{(1)}_{ij}=\left\|x^{\mathrm{cond}}_j-x^{\mathrm{cond}}_i+s_{ij}\right\|,
$$

$$
r^{(2)}_{ij}=\left\|x^t_j-x^t_i+s_{ij}\right\|.
$$

双几何消息层把两套径向基、截断函数和单位方向同时用于标量/向量消息 (`liflow/liflow/model/layers.py:51-91`)。初始标量特征由元素嵌入、流时间 Fourier 特征和温度 Fourier 特征组成；初始向量特征来自 $x_t-x_{\mathrm{cond}}$ (`liflow/liflow/model/models.py:35-78`)。门控等变输出层为每个原子生成一个三维向量 (`liflow/liflow/model/layers.py:114-137`)。

默认配置是 64 维特征、20 个径向基、3 层消息传递、5 Å 截断 (`liflow/liflow/config/train.yaml:6-16`)。这些是**代码确认**的架构细节；订阅预览没有 Methods，无法确认论文原文如何描述它们。

### 8. Corrector 学什么？

论文摘要说 Corrector 用于局部修正不物理结构 (`paper.md:12`)。代码中的训练数据这样构造：

1. 取真实干净构型 $x_1$；
2. 加入逐原子随机尺度的高斯噪声 $\eta$：

$$
x_{\mathrm{cond}}=x_1+\eta;
$$

3. 再采样一个较小的 Maxwell-Boltzmann 先验 $\epsilon$；
4. 用同一个 flow-matching 目标，从 $x_0=x_{\mathrm{cond}}+\epsilon$ 学回 $x_1$。

直接证据见 `liflow/liflow/data/dataset.py:60-106` 和 `liflow/liflow/config/train.yaml:31-39`。

#### 一个值得注意的训练/推理不对称

Propagator 推理时会明确把 prior 加到起始坐标 (`liflow/liflow/utils/inference.py:144-155`)。Corrector 推理时虽然采样并保存了 `data["prior"]`，却没有把它加到 `positions_2`，而 `FlowModule`/`DualPaiNN` 也不读取这个字段 (`liflow/liflow/utils/inference.py:158-164`; `liflow/liflow/model/modules.py:27-29`)。

因此，代码中的 Corrector 训练从 $x_{\mathrm{cond}}+\epsilon$ 起步，而推理从 $x_{\mathrm{cond}}$ 起步。这个行为已由源码确认，但其理论动机或是否为有意设计 **Not found**。

### 9. 推理时怎样生成整条轨迹？

每个粗时间步包含：

1. 从当前坐标重建周期性邻居图；
2. 采样 Propagator prior 并加入起点；
3. 在 $t\in[0,1]$ 上用 Euler 或 Heun 积分；
4. 可选地运行 Corrector；
5. 移除质量加权的整体平移；
6. 若出现 NaN 或最大位移超过 $10^3$ Å，则重试；
7. 重试仍失败则提前终止轨迹。

Euler 更新是

$$
x_{k+1}=x_k+\Delta t\,v_\theta(x_k,t_k),
$$

Heun 更新是

$$
\widetilde{x}_{k+1}=x_k+\Delta t\,v_\theta(x_k,t_k),
$$

$$
x_{k+1}=x_k+\frac{\Delta t}{2}
\left[v_\theta(x_k,t_k)+v_\theta(\widetilde{x}_{k+1},t_{k+1})\right].
$$

实现见 `liflow/liflow/utils/inference.py:89-134`。发布的通用评估默认每个粗步使用 10 个 Euler 子步，并生成 25 个粗步 (`liflow/liflow/config/test.yaml:12-17`)。

质心修正为

$$
\Delta r_{\mathrm{COM}}=
\frac{\sum_i m_i(x_i^{\mathrm{new}}-x_i^{\mathrm{old}})}{\sum_i m_i},
$$

$$
x_i^{\mathrm{new}}\leftarrow x_i^{\mathrm{new}}-\Delta r_{\mathrm{COM}}.
$$

它去除模型产生的整体平移漂移 (`liflow/liflow/utils/inference.py:168-210`)。

### 10. 论文怎样评估？

#### 论文声明

- 在未见组成上，锂 MSD 的 Spearman 相关系数稳定在 0.7-0.8 (`paper.md:12`)；
- 可以从短训练轨迹泛化到更长轨迹和更大超胞；
- 相对第一性原理方法最高加速 $600{,}000\times$ (`paper.md:12`)。

#### 图像直接显示的结果

- 图 2/扩展数据图 2：整体存在相关趋势，但同时有明显过扩散和欠扩散离群点 (`figure_02.png`; `figure_05.jpg`)。
- 扩展数据图 3：LiFlow 与 AIMD 在 LGPS 中恢复出相似的主要扩散通道，但访问的具体位点并不完全一致 (`figure_06.jpg`)。
- 扩展数据图 4：两者的二维 PMF 空间拓扑相似，局部势垒强度仍有差异 (`figure_07.jpg`)。
- 图 3：在显示的高温范围内，LiFlow 的扩散率趋势接近 AIMD/MLIP，并可运行 `4x4x4` 大超胞 (`figure_03.png`)。
- 扩展数据图 5：低温外推明显变差。离开训练温区后，MLIP 扩散率继续下降多个数量级，而 LiFlow 曲线趋于平台，说明它会高估极慢扩散 (`figure_08.jpg`)。

#### 代码能直接计算什么？

通用评估代码计算锂和框架原子的末帧 MSD：

$$
\mathrm{MSD}(A)=\frac{1}{|A|}\sum_{i\in A}
\|x_i^{\mathrm{final}}-x_i^0\|_2^2,
$$

并计算周期性 RDF 及其平均绝对误差 (`liflow/liflow/utils/analysis.py:5-45`; `liflow/liflow/experiment/test.py:91-120`)。

但 Spearman 汇总、扩散率拟合、PMF 构建、计时、误差统计与论文绘图代码均 **Not found**。

### 11. 如何理解它为什么可能有效？

这是基于论文摘要、图和实现的解释性推断：

- $\sqrt{k_BT/m_i}$ 先把温度与质量决定的位移尺度显式交给先验，网络不必从零学习最基本的热运动尺度。
- 锂/框架与 small/large 两级尺度进一步处理不同材料的迁移率异质性。
- 等变网络保证旋转坐标系下的向量输出按物理方式变化。
- 局部周期图使模型结构上可以接受不同原子数的超胞。
- Propagator 学长时间位移分布，Corrector 专注局部几何质量，降低单个模型同时处理大尺度输运和小尺度结构约束的难度。

这些机制解释了高温插值和大超胞迁移为何可行，但不能证明任意温度或任意材料上的可靠性。扩展数据图 5 已给出明确反例：极低扩散率区域的外推较弱。

### 12. 复现性判断：3/5

#### 已提供

- 模型、数据加载、训练与推理源码；
- Hydra 配置与通用/LGPS/LPS 脚本；
- 7 个 Propagator/Corrector checkpoint；
- 通用数据和 LGPS 数据的公开链接；
- prior 分类 notebook；
- 默认随机种子和主要超参数。

#### 缺失或受限

- 论文声明提供的原始轨迹预处理脚本，在该 commit 中 **Not found** (`paper.md:80-89`)；
- 通用与 LGPS 数据未打包在仓库中，LPS 数据需要向原作者申请 (`liflow/README.md:44-55`)；
- 论文最终统计与作图脚本 **Not found**；
- prior 分类器没有保存成可复用权重；
- 自动化测试 **Not found**；
- 本地论文缺少 Methods 和补充材料；
- 因外部数据不存在，本次没有执行完整训练或数值复现实验。

因此，这个仓库足以理解核心算法，也适合在下载符合格式的数据后运行预训练推理；但它不是从原始轨迹到论文全部数字和图表的一键复现包。

### 13. 最重要的结论

LiFlow 的真正创新点不是简单“用神经网络替代势能面”，而是直接学习**时间粗粒化后的条件位移分布**，并用温度/质量先验、等变双几何图网络以及 Propagator/Corrector 分工来保持物理尺度和局部结构。

它最有说服力的证据来自训练温区内的排序、扩散通道和空间分布一致性，以及对更大超胞和更长轨迹的支持。使用时必须同时记住两个边界：科学上，低温极慢扩散会被明显高估；工程上，预处理、最终统计/作图和测试链条并未完整发布。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## LiFlow

**Paper:** Juno Nam et al., “Flow matching for accelerated simulation of atomic transport in crystalline materials,” *Nature Machine Intelligence* 7, 1625-1635 (2025). DOI: `10.1038/s42256-025-01125-4`.

### Problem

Atomic transport controls solid-electrolyte performance, but ab initio molecular dynamics (AIMD) is too expensive for broad composition screening or long, large-cell trajectories. LiFlow replaces many femtosecond-scale force evaluations with conditional generation of a coarse atomic displacement. The paper focuses on lithium diffusion in crystalline solid-state electrolytes (`paper.md:9-12`).

### Relation to Existing Approaches

The accessible paper preview explicitly identifies the scale limitation of AIMD but does not preserve the Introduction's detailed comparison. Its reference list places LiFlow alongside machine-learning interatomic potentials (for example, *Nature Materials* 2021 and *Nature Computational Science* 2023 reviews), time-coarsened dynamics such as Timewarp (NeurIPS 2023) and implicit transfer operators (NeurIPS 2023), Score Dynamics (*Journal of Chemical Theory and Computation*, 2024), and flow-based frame generation such as F3low (arXiv, 2024) (`paper.md:98-108`). Exact paper-stated limitations of each named method are **Not found** in the acquired subscription preview.

### Method in Brief

LiFlow has two separately trained equivariant flow models:

1. The **Propagator** learns a distribution over displacements between time-delayed MD frames.
2. The **Corrector** learns to map a locally noised configuration back toward a clean geometry.

The Propagator starts from the current coordinates plus an adaptive Maxwell-Boltzmann prior. The prior standard deviation scales with $\sqrt{k_BT/m_i}$ and selects separate small/large multipliers for lithium and framework atoms. A binary classifier based on MACE descriptors and temperature supplies those prior classes in the universal dataset. `DualPaiNN` then predicts an equivariant velocity field conditioned on the original geometry, the current flow point, element identity, flow time, and temperature. Euler or Heun integration generates the next coarse configuration; repeated steps form a trajectory, with optional correction, center-of-mass drift removal, and divergence retries.

The released velocity-mode training path is reconstructed from code as

$$
x_0=x_{\mathrm{cond}}+\epsilon,\qquad
x_t=(1-t)x_0+t x_1,
$$

$$
\mathcal{L}=\frac{1}{N}\sum_i
\left\|v_\theta(x_{\mathrm{cond}},x_t,t,T,Z)_i-(x_{1,i}-x_{0,i})\right\|_2^2.
$$

These equations are direct code behavior (`liflow/liflow/model/modules.py:31-57`); the acquired paper contains no Methods equations or numbering.

### Evaluation and Main Findings

The paper reports a dataset of 25-ps trajectories for 4,186 solid-state-electrolyte candidates at 600, 800, 1,000, and 1,200 K. On unseen compositions, lithium MSD rankings reach Spearman correlations of 0.7-0.8. The abstract further reports transfer from short training trajectories to longer trajectories and larger supercells, with speed-ups up to $600{,}000\times$ over first-principles simulation (`paper.md:12`).

The figures add useful qualifications:

- Universal-set parity plots show a clear correlation but meaningful outliers, including both severe over-diffusion and under-diffusion (`figure_02.png`; `figure_05.jpg`).
- LGPS diffusion traces and projected potentials of mean force recover much of the AIMD channel topology, although visited sites and local barrier intensities are not identical (`figure_06.jpg`; `figure_07.jpg`).
- LiFlow agrees with AIMD/MLIP in the displayed high-temperature training regime and supports a larger `4x4x4` LGPS cell (`figure_03.png`).
- Low-temperature extrapolation is weak: outside the shaded training range, LiFlow diffusivity flattens while the MLIP reference continues to fall by orders of magnitude (`figure_08.jpg`).
- The small/large prior selector separates mobility regimes only coarsely; its predicted distributions overlap around the threshold (`figure_09.jpg`).

### What the Code Actually Provides

The GitHub snapshot at commit `e6fc475361d046865f12cae1aee11c4f56c48d87` includes the full model, trajectory datasets/loaders, priors, Propagator/Corrector training entry, universal evaluation entry, LGPS trajectory script, seven checkpoints, configs, and a prior-classifier notebook. The universal evaluator emits lithium/frame MSD, RDF MAE, completion length, and the source CSV fields. The LGPS script supports arbitrary supercell replication, long trajectories, multiple temperatures, and XYZ output.

Code-paper fidelity is **medium**. The central model and inference workflow match the abstract and Fig. 1, but equation-level comparison is impossible from the available preview. A notable implementation asymmetry is that Corrector training uses a prior-shifted flow start, while Corrector inference samples but does not add that prior before integration (`liflow/liflow/data/dataset.py:60-106`; `liflow/liflow/utils/inference.py:158-164`).

### Reproducibility: 3/5

**Strengths:** install instructions, released checkpoints, task scripts, explicit configs, public universal/LGPS data links, deterministic default seeds, and direct evaluation code. Data availability is documented at `paper.md:80-89` and `liflow/README.md:44-116`.

**Gaps:**

- The acquired article is a subscription preview without Methods or supplementary text.
- The preprocessing script promised by both paper availability statements is **Not found** in this commit.
- Universal/LGPS data are external; LPS data are available only on request.
- Spearman aggregation, diffusivity fitting, PMF construction, timing, and paper figure scripts are **Not found**.
- The prior classifiers exist only in a notebook and are not saved as packaged artifacts.
- No automated tests were found, and no clean-environment numerical run was possible without external data.

The release is suitable for inspecting the algorithm and running pretrained inference after obtaining the expected datasets. It is not a complete push-button reproduction of the published analysis.

### Bottom Line

LiFlow is a physically conditioned, equivariant flow-matching surrogate for time-coarsened crystalline transport. Its strongest evidence is high-temperature interpolation: it preserves useful transport rankings and spatial diffusion structure while enabling much longer and larger simulations than AIMD. Its key scientific limitation is extrapolation into very low-mobility regimes, and its key reproducibility limitation is the missing bridge from raw trajectories to the final paper statistics and figures.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
