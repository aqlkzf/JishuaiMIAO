---
layout: default
permalink: /paper-atlas/osdr-078c7f0b/
title: "OSDR"
nav: false
wide: true
description: "OSDR（one-shot tissue dynamics reconstruction）利用同一张组织切片中的空间异质性，把许多细胞周围不同的邻域组成当作不同“局部初始条件”；再用 Ki67 判断哪些细胞处于分裂窗口，学习“邻域里各类细胞数量 → 某类细胞分裂概率”的统计模型。将分裂概率减去假设的移除率后，可得到细胞密度的常微分方程、相图与固定点，也可逐细胞随机模拟组织随时间的变化。"
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
      <span>Nature · 2026</span>
    </div>
    <h1>OSDR</h1>
    <p>Temporal tissue dynamics from a spatial snapshot</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09876-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for OSDR">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/JonathanSomer/osdr" target="_blank" rel="noopener noreferrer" aria-label="Open code for OSDR">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## OSDR 方法详解：怎样从一张空间组织快照推断细胞群体动力学

### 一句话理解

OSDR（one-shot tissue dynamics reconstruction）利用同一张组织切片中的空间异质性，把许多细胞周围不同的邻域组成当作不同“局部初始条件”；再用 Ki67 判断哪些细胞处于分裂窗口，学习“邻域里各类细胞数量 → 某类细胞分裂概率”的统计模型。将分裂概率减去假设的移除率后，可得到细胞密度的常微分方程、相图与固定点，也可逐细胞随机模拟组织随时间的变化。

论文 “Temporal tissue dynamics from a spatial snapshot” 发表于 *Nature* 2026，DOI `10.1038/s41586-025-09876-1`。方法面向天至周尺度的组织细胞群变化，不是 RNA velocity 那种小时尺度的细胞内转录动力学，也没有从单张切片直接观测真实纵向轨迹。

### 核心识别思路：用空间异质性替代时间采样

一张乳腺癌切片中，不同位置的成纤维细胞、巨噬细胞、T/B 细胞和肿瘤细胞密度不同。若某类细胞的分裂率确实主要由当前邻域决定，那么遍布切片的许多邻域提供了同一个局部动力学规则在不同状态上的观测。

对每个中心细胞 $x$，以半径 $r$ 画圆，计数邻域内每种细胞：

$$
N(x)=(N_1(x),N_2(x),\ldots,N_k(x)).
$$

论文主分析用 $r=80\,\mu\mathrm m$，来自体内细胞间作用距离；源码 `NeighborsDataset` 也以 80 µm 为默认半径，并用欧氏距离判断邻居。这个半径可以改变，论文在补充分析中做了灵敏度检查。

例如某成纤维细胞的邻域为“4 个成纤维细胞、3 个巨噬细胞”，特征向量就是 $(4,3)$；另一个细胞周围为 $(1,3)$。成千上万个细胞产生覆盖不同局部组成的训练点。重要前提是这些局部状态共享同一套动力学规则，而不是每个患者、区域或隐含环境都有完全不同的规则。

### 输入数据与五阶段软件流程

输入是一张单细胞表，每行至少含坐标 `x,y`、细胞类型、分裂标签、图像/患者标识；若有死亡标签也可使用。论文使用三个乳腺癌 IMC 队列，核心 Danenberg 队列含 715 位患者、859,710 个细胞，每张切片约 $500\times500\,\mu\mathrm m$。

源码 `Analysis.run()` 把拟合拆成五步：

1. 按图像构造 `Tissue`；
2. 对每个细胞计数邻居；
3. 限定纳入模型的细胞类型；
4. 对邻居计数做多项式/交互特征变换；
5. 为每个被建模细胞类型拟合分裂和移除模型。

切片边缘会漏记圆外邻居。默认路径剔除距边界不足一个半径的中心细胞；`ExtrapolateNeighborsDataset` 可按已观察到的圆面积比例外推计数。两种方式分别以样本量或偏差控制为代价，不能把边缘外推当作真的观察到切片外细胞。

### Ki67 如何变成分裂事件

Ki67 在细胞周期中升高，尤其接近 G2/M。论文先以噪声阈值 $T_n$ 去除基线，再用阈值以上值的标准差归一化：

$$
K_i^{\mathrm{norm}}=\frac{K_i-T_n}{\operatorname{sd}(K\mid K>T_n)}.
$$

主数据中 $T_n=0.5$ mean isotopic counts。若归一化后的 Ki67 超过分裂阈值 $T_d$，标签记为 1，否则为 0。论文报告 $T_d$ 在 0–1 范围内改变时主要结论稳定。源码 `preprocess/ki67.py` 实现噪声扣除、尺度归一化和布尔分裂标签；不同数据加载器可覆盖 typical noise，因此 0.5 不是所有平台的通用常数。

Ki67 阳性不是瞬时“正在一分为二”的观测，而是在一个可见时间窗内经历分裂的代理。论文把这个窗口定义为一个时间单位，约几小时，并同样令移除时间单位为 1。因此模拟的“一步”首先是模型单位；只有额外校准后才能解释成精确小时或天数。

### 用逻辑回归学习邻域依赖的分裂概率

对细胞类型 $i$，OSDR 拟合

$$
p_i^+(N)=\Pr(Y_i=1\mid N)
=\sigma\!\left(\beta_{i0}+\sum_j\beta_{ij}N_j+\sum_{j\ell}\beta_{ij\ell}N_jN_\ell+\cdots\right),
$$

其中 $Y_i$ 是 Ki67 二值分裂标签，$\sigma(z)=1/(1+e^{-z})$。多项式/交互项允许“巨噬细胞只有在成纤维细胞很多时才改变分裂”等非加性效应。

当前源码用 statsmodels `Logit`，可不正则化、使用 L1，或在一组 $\alpha$ 上以 BIC/AIC 或 k 折交叉验证选择惩罚强度。`_fit_score_optimized_model()` 默认在 $10^{-8}$ 到 $10^4$ 间取 20 个候选；`_fit_cv_optimized_model()` 默认 3 折、log loss。论文的模型选择与具体图应以论文复现脚本为准，不应把类的默认值自动视为每项分析参数。

一个系数例子：若巨噬细胞计数系数为 0.2，其他变量固定时，多 1 个巨噬细胞会使分裂的 log-odds 增加 0.2，即 odds 乘 $e^{0.2}\approx1.22$；它不是分裂概率直接增加 0.2。若存在二次项或交互项，单个系数必须结合当前邻域共同解释。

论文先验证“当前邻域是否足够预测分裂”。Danenberg 数据中各类型拟合的似然比检验均 $P<10^{-13}$，校准图中预测概率与真实分裂频率接近。如果某系统的分裂强烈依赖未观测历史，当前邻域预测表现会差，论文明确建议此时不要使用 OSDR。

### 最强假设：移除率等于平均分裂率

可靠的泛细胞死亡标记缺失，因此论文没有像分裂率那样学习邻域依赖的死亡/移除模型，而是假定每种细胞的移除率为常数：

$$
p_i^-(N)=\overline{Y_i}.
$$

这在准稳态组织中平均分裂等于平均移除时成立。源码 `Model._estimate_death` 用分裂标签均值建立常数模型。这里的“移除”还可能包含细胞离开切片区域，而不只生物学死亡。

这个假设决定了绝对净增长的基线。论文对多种常数移除率做灵敏度分析，主要相图结构仍稳定，但这不能证明真实死亡无邻域依赖。若未来有可靠死亡或迁移标记，应该直接拟合 $p_i^-(N)$。

### 从概率模型到群体 ODE

对一个局部邻域状态

$$
X=(X_1,X_2,\ldots,X_k)^\top,
$$

细胞类型 $i$ 的期望变化为

$$
\frac{dX_i}{dt}=X_i\,[p_i^+(X)-p_i^-(X)].
$$

整个系统写成 $dX/dt=f(X)$。乘 $X_i$ 很关键：分裂概率是单细胞率，群体期望新增量还取决于当前有多少该类细胞。若 $X_i=0$ 且模型不含外部流入或类型转换，该类细胞不会凭空出现，因此坐标轴天然是零流线。

假设一个邻域有 10 个 T 细胞，预测分裂概率 0.08、移除概率 0.03，那么一个单位时间的期望净变化为 $10(0.08-0.03)=0.5$ 个细胞。随机模拟不会真的增加半个细胞；0.5 是许多随机重复的均值。

#### 最大密度校正

逻辑回归若向未采样的高密度区域外推，可能持续预测正增长。论文假定在观测到的最大密度附近不能有正净流，并加入

$$
p_i^{\mathrm{correction}}=c_i d_i^n,
$$

选择 $c_i$ 使 95% 分位密度附近净增长不为正。源码的 `CellTypeSpecificDensityEnforcer` 执行这一校正，默认分析幂次为 8；实现还把校正下限裁到 -0.5，这是论文公式没有突出说明的数值保护。校正约束高密度外推，不是从数据发现的生物作用。

### 两种互补输出：相图与空间随机模拟

#### 相图：局部规则的全局几何

对于两种细胞，网格化 $(X_1,X_2)$，在每个点计算 $f(X)$ 并画流线。满足 $dX_1/dt=0$ 或 $dX_2/dt=0$ 的曲线是两条 nullclines；交点是固定点。源码用 contourpy 提取零等高线，用 shapely 求交点，再通过数值 Jacobian 的特征值分类：

- 所有实部为负：稳定固定点；
- 内部点存在非负方向：不稳定；
- 坐标轴上只沿可行方向收缩：标为半稳定。

图轴常用 $\log_2(1+X)$，仅为压缩高密度范围；模型预测前会反变换回原始计数。相图不保留某张切片具体的空间排列，它回答“若局部邻域处于某种组成，平均往哪变”。

#### 随机组织模拟：保留初始空间排列

`TissueStep` 为每个细胞预测分裂/移除概率并抽样事件：分裂为 +1、移除为 -1、其余为 0。新生细胞随机放在亲本邻域内，死亡细胞删除，可再加随机游走；重复得到一条空间组织轨迹。

相同的总体细胞数若空间排列不同，可能得到不同结果。例如 T 与 B 分居两侧时，局部相互作用弱；若聚在一起则可能越过激发阈值。相图展示规则和吸引域，空间模拟展示一个具体初始组织的命运，两者不能互相替代。

### 仿真验证：能否从已知系统找回相图

论文先生成四类两细胞已知动力学拓扑，模拟不同初始密度形成空间数据，再只用末端快照拟合 OSDR。图 2 比较 known 与 inferred：随着每类细胞达到几千个，固定点与吸引域可较可靠重建；主图示例使用每类 10,000 个模拟细胞和 10 次重复。

这验证了模型在“数据确由相同类型规则生成、状态空间覆盖充分”的理想条件下可以反演简单 2D 系统。它不证明任意高维真实组织都可由单快照唯一识别；维数增加时需要更多细胞覆盖组合空间。

### 生物学应用一：热/冷纤维化

在 Danenberg 乳腺癌 IMC 数据中，成纤维细胞与巨噬细胞的 OSDR 相图得到：

- 两者共存、互相支持的稳定“hot fibrosis”点；
- 成纤维细胞单独维持的“cold fibrosis”点；
- 高巨噬细胞、无成纤维细胞的半稳定点。

这些结构与独立的鼠源共培养时间实验相图相似。加入肿瘤细胞的 3D 模型后，肿瘤密度升高把稳定点推向巨噬细胞更多的热纤维化。患者按热/冷状态分组时，热纤维化与较差生存相关（log-rank $P=0.0046$，临床数据 $n=607$）。

证据边界是：共培养体系与人肿瘤切片跨物种、跨环境；相似固定点支持动力学结构，却不证明每条细胞间作用边都是同一分子机制。生存关联也可能受肿瘤负荷等混杂影响。

### 生物学应用二：T–B 可激发回路

T–B 相图在零点稳定，但 T 细胞超过阈值后产生大脉冲：T 先升高，B 后升高，之后两者下降。第一次脉冲后，B 细胞仍高时再次加入 T 不能触发新脉冲；待 B 降低后才能再次激发，形成 refractory period。三维 CD4–CD8–B 模型保留这种 flare。

相图中的脉冲是拟合规则的预测，不是同一患者中实际连续拍摄到的免疫 flare。论文用不同队列和灵敏度分析检查其稳健性，但真实时间序列的直接验证仍是后续任务。

### 生物学应用三：治疗响应的纵向检验

NeoTRIP 三阴性乳腺癌试验包含化疗 141 人、化疗+免疫治疗 138 人，在基线、治疗 3 周和约 24 周采样。作者分别用早期治疗切片拟合 responder 与 non-responder 模型，再从共同的基线组织组成启动轨迹。

图 5 中两种治疗臂的 responder 模型均预测肿瘤群体崩塌，non-responder 模型则维持或上升；T 细胞邻域中 responder 肿瘤细胞分裂更少。共同初始条件有助于把差异归因于学到的动力学而非初始组成，但 responder 标签已经用于分组拟合，所以这是组层面的机制/回顾性验证，不是对新患者的盲法个体预测器。

论文图注说 Fig. 5c 使用卡方独立性检验、$P<10^{-7}$；本地 `f5.py` 当前实现使用 `scipy.stats.ttest_ind`。这是明确的论文—代码统计检验差异，不能抹平。

### Fokker–Planck 对未建模过程的估计

论文补充用 Fokker–Planck 思路把状态空间速度拆成已建模的分裂−移除场 $v(x)$、未建模迁移/分化场 $u(x)$ 和随机扩散 $D(x)$：

$$
\partial_t\rho(x)=-\nabla\cdot[\rho(x)(v(x)+u(x))]
+\sum_{ij}\partial_{x_i}\partial_{x_j}[D_{ij}(x)\rho(x)].
$$

主结论认为局部分裂/移除足以解释所分析系统的大部分场。现有 `src/tdm/` 中没有找到完整的 KDE/散度误差场实现，因此这部分属于论文方法/补充证据，而不是当前主包可直接调用的功能。

### 论文—代码对应

| 环节 | 直接代码 | 状态 |
|---|---|---|
| 五阶段分析编排、80 µm 默认值 | `src/tdm/analysis/analysis.py:30-153` | Exact |
| 邻居计数与边缘剔除 | `src/tdm/dataset/neighbors.py:17-158` | Exact |
| Ki67 预处理 | `src/tdm/preprocess/ki67.py` | Exact；阈值依数据集 |
| 逻辑回归与 L1/BIC/CV | `src/tdm/model/logistic_regression.py:23-229` | Exact |
| ODE、常数死亡与事件采样 | `src/tdm/model/model.py` | Exact，高层假设来自论文 |
| 最大密度校正 | `src/tdm/model/maximal_density_enforcer.py` | Exact，含代码裁剪细节 |
| 空间随机模拟 | `src/tdm/simulate/tissue_step.py:11-194` | Exact |
| nullcline、固定点与稳定性 | `src/tdm/numerical/phase_portrait_analysis.py:16-234` | Exact |
| 论文图 2–5 | `src/tdm/publications/first/` | 大部分可追踪，存在统计/CI差异 |
| Fokker–Planck 未建模场 | `src/tdm/` searched | Not found |

本地目录是 `https://github.com/JonathanSomer/osdr` 的软件/论文脚本快照，包名为 `tdm`、版本 `0.0.1`、Python ≥3.10。

### 主图怎么读

- 图 1：从切片、邻域计数、Ki67 到随机事件、轨迹和相图，是完整方法定义。
- 图 2：known/inferred 配对验证固定点拓扑；散点分布提示重复间不确定性。
- 图 3：先看模型校准，再比较独立共培养相图与 OSDR 热/冷纤维化，最后看肿瘤密度和生存关联。
- 图 4：相图闭合轨迹、T 后 B 的脉冲和 refractory period 构成“可激发”证据链。
- 图 5：两治疗臂分别比较 responder/non-responder 模型；注意这是分组拟合而非前瞻性分类。

### 关键限制

1. 单快照反演依赖当前邻域足以预测分裂的马尔可夫式假设；无历史、分子梯度和治疗暴露可能造成遗漏变量偏差。
2. 细胞类型标注、Ki67 阈值、邻域半径和多项式阶数都会改变状态变量和模型。
3. 死亡率是常数并等于平均分裂率；迁入、迁出、状态转换通常不在主 ODE 中。
4. 一个小切片可能没有覆盖整个吸引域，尤其难识别稀有或高维固定点。
5. 相图忽略具体空间排列，随机模拟则强依赖初始切片和边缘处理。
6. 逻辑回归描述统计关联；系数不能自动解释为分泌因子或直接接触机制。
7. 稳健性分析支持所研究乳腺癌队列，但不能保证迁移到炎症、发育或其他平台。
8. 本次只做源码与论文证据核对，没有下载全部受限数据或端到端重跑图 2–5。

### 最短使用路径

使用 OSDR 前先做一个决定性检查：在留出数据或患者层面验证邻域计数能否校准预测各细胞类型的分裂率。若不能，后面的漂亮相图没有可信基础。若能，再依次检查 Ki67/死亡假设、邻域半径和边缘、模型复杂度与固定点 bootstrap；最后才把相图或模拟结果解释为可检验的组织动力学假说。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## OSDR - One-Shot Dynamics Reconstruction

### Executive Summary

**OSDR (One-Shot Dynamics Reconstruction)** is a computational framework for inferring cell population dynamics from a single spatial tissue snapshot. Published in *Nature* (2026) by Somer, Mannor, and Alon, OSDR addresses a fundamental limitation in tissue biology: the inability to observe temporal dynamics in human tissues where only single biopsies are available.

**DOI**: https://doi.org/10.1038/s41586-025-09876-1

**Primary sources used for this summary (verifiable)**:
- Paper: `paper source/PMC12893916/paper.md` (PMC JATS, primary source)
- Code: OSDR reference implementation (`src/tdm/`), centered around `src/tdm/analysis/analysis.py::Analysis`

### Motivation & Novelty

#### Biological Problem
- Physiological and pathological processes (inflammation, cancer) emerge from cell population changes over time
- Human biopsies provide only a single snapshot - longitudinal sampling is infeasible
- Existing methods (intravital microscopy, lineage tracing) are limited to animal models or in vitro settings
- No prior approach reconstructs tissue-level population dynamics from static spatial data

#### Key Innovation
OSDR uses a cell division marker (Ki67) to learn how neighborhood composition influences cell division rates, converting static spatial information into dynamical models. The critical insight is:

> "If we obtain a marker for cell division, and in each cell division the marker remains above a defined threshold for a time period $dt$, then all observed divisions occurred within the last $dt$ hours."

Paper support: Methods ("OSDR aims to transition from static observations...")

#### Limitations of Existing Approaches

| Method | Approach | Limitation vs OSDR | Journal (Year) |
|--------|----------|-------------------|----------------|
| RNA velocity | Spliced/unspliced ratio → intracellular dynamics | Hours timescale; single cell, not population-level | *Nature* (2018) |
| Ergodic rate analysis | Cell-cycle marker time series → rates | Requires cell line experiments, not biopsies | *Nature* (2013) |
| CellPhoneDB | Ligand-receptor co-expression → communication | Single time point; no population dynamics | *Nat. Protoc.* (2020) |
| NicheNet | Expression → ligand-target gene links | Static communication; no temporal trajectories | *Nat. Methods* (2020) |
| DIALOGUE | Multi-cellular programs from spatial/scRNA | Identifies co-varying programs; no population ODEs | *Nat. Biotechnol.* (2022) |
| Intravital microscopy | In vivo live imaging | Requires animal models; not applicable to human biopsies | *Nat. Rev. Cancer* (2023) |
| In vitro co-culture | Seeded cells measured at multiple time points | Lacks native in vivo context; not human patient data | *Nat. Commun.* (2023) |

#### Unique Contributions
1. **Spatial-to-temporal transformation**: Converts single-snapshot spatial proteomics into dynamical systems
2. **Phase portrait analysis**: Reveals fixed points and basins of attraction in cell population dynamics
3. **Treatment response prediction**: Predicts therapy outcomes from early-treatment biopsies
4. **Excitable circuit discovery**: Identifies pulse-generating T-B cell dynamics in tumor microenvironment

### Method Overview

#### Core Principle
The rate of change in cell population $X_i$ is modeled as:

$$\frac{dX_i}{dt} = \frac{\text{\#Divisions}}{\text{Time a division remains observable}} - \frac{\text{\#Deaths}}{\text{Time a death remains observable}}$$

Paper support: Methods, equations just after "Thus:", `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`

Division probability for each cell is learned as a function of its neighborhood composition using logistic regression:

$$p_i^{+1}(N(x))$$

where $N(x)$ represents the neighborhood cell counts within radius $r = 80 \mu m$.

Paper support: "Tissue dynamics from a spatial snapshot" (radius choice) and Methods ("Model inference algorithm"), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/dataset/neighbors.py::_default_neighborhood_size`, `src/tdm/model/logistic_regression.py::LogisticRegressionModel`.

#### Technical Pipeline
1. **Data Input**: Spatial proteomics (IMC) with cell coordinates, types, and Ki67 expression
2. **Neighborhood Definition**: Count cells of each type within radius $r$ for each cell
3. **Division Probability**: Logistic regression models $P(\text{division} | \text{neighborhood})$
4. **Death Approximation**: Constant rate equal to mean division rate (steady-state assumption)
5. **ODE System**: Construct dynamics $\frac{d}{dt}X = f(X)$ from learned probabilities

Paper support: "Tissue dynamics from a spatial snapshot" (constant death approximation) + Methods ("Model inference algorithm", step (5)), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/model/model.py::Model._estimate_death`.

#### Key Equations (from paper)

The full dynamical system:

$$\frac{d}{dt}X = \begin{pmatrix} X_1 (p_1^{+1}(X) - p_1^{-1}(X)) \\ X_2 (p_2^{+1}(X) - p_2^{-1}(X)) \\ \vdots \\ X_k (p_k^{+1}(X) - p_k^{-1}(X)) \end{pmatrix}$$

Paper support: Methods (ODE definition), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`

Ki67 threshold computation:
$$\text{cutoff} = K \cdot \sigma + N$$

where $K$ is the threshold fraction, $\sigma$ is standard deviation of Ki67 values above noise, and $N$ is typical noise level.

Paper support: Methods ("Ki67 thresholds"), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/preprocess/ki67.py::is_dividing`.

Time unit note (implementation detail): the paper sets $dt^+ = dt^- = 1$ time unit (roughly a few hours), and the triple-negative trajectory plotting code maps 1 time unit to 0.25 days. Paper support: Methods (stating $dt^+ = dt^- = 1$), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/publications/first/triple_negative_plots.py::melt_sols`.

### Biological Applications

#### 1. Fibroblast-Macrophage Dynamics
- Reconstructs **hot fibrosis** (fibroblast + macrophage coexistence) and **cold fibrosis** (fibroblast-only) fixed points
- Validated against in vitro co-culture experiments (Mayer et al.)
- Hot fibrosis associated with poor prognosis (log-rank P = 0.0046)

Paper support: fibroblast-macrophage results + survival analysis (Fig. 3 and surrounding text), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support for OSDR-side reconstruction/plots: `src/tdm/publications/first/analyses.py::fm_analysis`, `src/tdm/publications/first/figures/f3.py::fig_3def`, `src/tdm/publications/first/figures/f3.py::fig_3g`, `src/tdm/publications/first/figures/f3.py::fig_3h`. In vitro co-culture data ingestion is NOT VERIFIED in this repo (no Mayer et al. dataset code found).

#### 2. T-B Cell Excitable Circuit
- Discovers pulse-generating dynamics with stable fixed point at zero cells
- T cell threshold triggers immune flare followed by B cell inhibition
- Refractory period prevents immediate re-triggering
- CD4 T cells initiate pulse; B cells provide negative feedback

Paper support: "Excitable dynamics of T and B cells" (Fig. 4), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/publications/first/analyses.py::tb_analysis`, `src/tdm/publications/first/figures/f4.py::fig_4abc`, `src/tdm/publications/first/figures/f4.py::fig_4d`, `src/tdm/publications/first/figures/f4.py::fig_4e`, `src/tdm/publications/first/figures/f4.py::fig_4f`.

#### 3. Treatment Response Prediction
- NeoTRIP trial: 279 triple-negative breast cancer patients
- OSDR predicts tumor collapse in responders but not non-responders
- Predictions based on week 3 biopsies (before clinical response)
- Works for both chemotherapy and chemotherapy + immunotherapy arms

Paper support: "OSDR predicts response to treatment" (including Mann-Whitney U-test $P < 10^{-5}$) + Fig. 5 description, `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/publications/first/triple_negative_plots.py::get_analysis`, `src/tdm/publications/first/figures/f5.py::fig_5b`.

### Evaluation

#### Datasets
| Dataset | Patients | Cells | Technology |
|---------|----------|-------|------------|
| Danenberg et al. (2022) | 715 | 859,710 | IMC |
| Wang et al. (2023) | 279 | 577,285 | IMC (longitudinal) |
| Fischer et al. (2023) | 1,012 | 2.1M | IMC |

Paper support: Danenberg counts in "OSDR infers fibroblast-macrophage dynamics" and NeoTRIP cohort/cell counts around Fig. 5, `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Fischer dataset size is stated as "additional 1,012 patients and 2.1 million cells" near the end of the fibroblast-macrophage section (same paper markdown).

#### Validation Results
- Log-likelihood ratio test for model fits: $P < 10^{-13}$
- Hot fibrosis survival difference: median 132 vs 192 months
- Treatment response prediction: Mann-Whitney U $P < 10^{-5}$
- Robustness across patient subgroups (stage, genotype, tumor size)

Paper support: logistic regression significance in fibroblast-macrophage section; survival and medians in Fig. 3 description; response prediction + Mann-Whitney U-test in "OSDR predicts response to treatment"; subgroup robustness is described via Supplementary figure references in the results sections, all in `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`.

#### Simulation Validation
- All four 2D phase portrait topologies correctly reconstructed
- ~10,000 cells sufficient for reliable fixed point recovery
- Results are robust to neighborhood radius and Ki67 threshold variations (specific ranges are NOT VERIFIED in the main-text markdown; see Supplementary figure references in the paper).

Paper support: simulation validation in "Tissue dynamics from a spatial snapshot" + Methods ("Simulations of known dynamical models"), `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support: `src/tdm/simulate/generate_distribution.py::get_random_positions_on_phase_portrait`, `src/tdm/publications/first/figures/f2.py::fig_2d`.

### Reproducibility Assessment

#### Reproducibility Rating: **4/5**

OSDR is among the most reproducible computational biology papers reviewed: full Python package on GitHub, comprehensive documentation, paper-figure notebooks, and Zenodo-hosted datasets. One dataset (Wang NeoTRIP) requires license agreement. The Fokker-Planck error-field analysis (used in Supplementary Figs 3m/n, 4m/n) is not in the main package.

**Justification**: Code is installable via pip; tutorial notebooks run end-to-end; paper figure notebooks exist for Figs 2-5; all primary data is publicly available; the only barrier is the NeoTRIP dataset license. Minor statistical test discrepancy in Fig. 5c (code: t-test, paper: chi-squared). Fokker-Planck supplementary analysis missing from package.

#### Strengths
- Complete Python package (`tdm`) available at https://github.com/JonathanSomer/osdr
- Comprehensive documentation site (https://jonathansomer.github.io/osdr/) with API reference and tutorials
- Four paper figure reproduction notebooks (`docs/notebooks/paper_figures/Figure-0[2-5].ipynb`)
- Danenberg and Fischer datasets on Zenodo with automated download (`tdm.raw`)
- Bootstrap utilities for reproducing confidence intervals

#### Practical Notes
1. **Wang (NeoTRIP) dataset**: requires license agreement at https://zenodo.org/records/7990870 — cannot reproduce Fig. 5 without it
2. **Ki67 noise threshold**: dataset-specific (`typical_noise` varies by IMC platform); use paper's T_n=0.5 for Danenberg data
3. **Common pitfall**: coordinates must be in standard units (1 µm = 1e-6); code uses `microns(80)` = 80e-6 for neighborhood
4. **Environment**: Python 3.10+; install with `pip install git+https://github.com/JonathanSomer/osdr.git`
5. **Fokker-Planck analysis**: not reproducible from package; supplementary figures require unpublished scripts

#### Blockers/Limitations
1. **Death rate approximation**: No death marker — uses mean division rate assumption (testable via sensitivity analysis)
2. **Spatial confounders**: Requires testing across patient subgroups (code supports subgroup filtering)
3. **Migration not modeled**: Assumes local proliferation dominates (Fokker-Planck check needed)
4. **Computational requirements**: Neighbor counting is O(N²) per patient; ~100K cells takes 1-2 min; >1M cells requires significant RAM

#### Data Availability
- Danenberg dataset (Nat. Genet. 2022): https://zenodo.org/records/7324285 (clinical data on cBioPortal)
- Fischer dataset (Cell Rep. Med. 2023): https://zenodo.org/records/7494509
- Wang NeoTRIP dataset (Nature 2023): https://zenodo.org/records/7990870 (license required)

Paper support: "Data availability" section, `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`. Code support (license requirement for Wang): `src/tdm/raw/triple_negative_imc.py::_read_single_cell_df`.

#### Code Availability
- Repository: https://github.com/JonathanSomer/osdr
- Documentation: https://jonathansomer.github.io/osdr/
- License: Apache 2.0
- Python 3.10+ required

### Limitations & Caveats (from authors)

1. **Dynamics change over time**: OSDR estimates dynamics at one time point; cannot model changes in dynamics
2. **History dependence**: Assumes division rate depends only on current neighborhood, not history
3. **Sample requirements**: Recommend ~0.2 cm² tissue for patient-specific models
4. **Extrapolation caution**: State-space regions with minimal data have higher uncertainty
5. **Confounders**: Must verify results across patient subgroups and test spatial confounders

Paper support: "Limitations and caveats" section, `paper source/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot/Somer et al. - 2026 - Temporal tissue dynamics from a spatial snapshot.md`

### Key Figures

| Figure | Content |
|--------|---------|
| Fig. 1 | OSDR overview: spatial snapshot to dynamics |
| Fig. 2 | Simulation validation: 4 phase portrait topologies |
| Fig. 3 | Fibroblast-macrophage dynamics vs in vitro validation |
| Fig. 4 | Excitable T-B cell circuit discovery |
| Fig. 5 | Treatment response prediction in NeoTRIP trial |

### Citation

```bibtex
@article{somer2026temporal,
  title={Temporal tissue dynamics from a spatial snapshot},
  author={Somer, Jonathan and Mannor, Shie and Alon, Uri},
  journal={Nature},
  year={2026},
  doi={10.1038/s41586-025-09876-1}
}
```

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
