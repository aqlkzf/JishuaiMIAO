---
layout: default
permalink: /paper-atlas/neural-sampling-from-cognitive-maps-enables-goal-directed-imagin-7ac3239c/
title: "Neural_sampling_from_cognitive_maps_enables_goal_directed_imagination_and_planning"
nav: false
wide: true
description: "这篇论文关注一种很具体的智能能力：给定一个起点和一个新目标，系统能否立刻在内部“想象”出若干条可行路径，而不必为每个目标重新训练策略，也不必在每次查询时做大规模穷举搜索。 强化学习是常用方案，但许多方法把策略和值函数绑定到奖励或目标，目标改变后需要重新学习；精确图搜索和模型预测控制（MPC）虽然通用，却会在在线规划阶段反复展开候选路径。"
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
      <span>Nature Machine Intelligence · 2026</span>
    </div>
    <h1>Neural_sampling_from_cognitive_maps_enables_goal_directed_imagination_and_planning</h1>
    <p>Neural sampling from cognitive maps enables goal-directed imagination and planning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/LH-cbicr/GCML" target="_blank" rel="noopener noreferrer" aria-label="Open code for Neural_sampling_from_cognitive_maps_enables_goal_directed_imagination_and_planning">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GCML 方法详解：从认知地图中采样，实现目标导向的想象与规划

### 1. 论文要解决什么问题？

这篇论文关注一种很具体的智能能力：给定一个起点和一个新目标，系统能否立刻在内部“想象”出若干条可行路径，而不必为每个目标重新训练策略，也不必在每次查询时做大规模穷举搜索。

强化学习是常用方案，但许多方法把策略和值函数绑定到奖励或目标，目标改变后需要重新学习；精确图搜索和模型预测控制（MPC）虽然通用，却会在在线规划阶段反复展开候选路径。原始 CML（*Nature Communications*, 2024）已经能通过预测学习构造带有方向感的认知地图，但它是确定性的，只给出一条轨迹。论文提出的 **GCML（generative cognitive map learner）** 在 CML 上增加内部状态递推、可供性门控和噪声采样，从而生成一组目标导向的候选方案。

### 2. 核心直觉

GCML 不直接学习“在目标 $g$ 下动作 $a$ 的价值”，而是先学习一个与具体目标无关的几何空间：

- 观测经过 **Q** 映射成内部状态；
- 动作经过 **V** 映射成该空间中的局部位移；
- **W** 学习“某个状态差通常由哪个动作造成”；
- **G** 或任务特定的可供性函数判断哪些动作可执行。

因此，规划时只需计算“当前想象状态到目标状态的方向”，再用 **W** 找出最对齐的动作。加入噪声后，不同动作可能在不同采样中胜出，于是得到多条仍然总体朝向目标的轨迹。

### 3. 输入、输出与主要变量

输入包括探索数据 $({\bf o}_t,{\bf a}_t,{\bf o}_{t+1})$、规划起点 ${\bf o}_0$、目标观测 ${\bf o}^*$ 和离散动作集合。输出是一条或多条虚拟动作/状态轨迹；下游模块还可以按路径长度、累计奖励或其他代价选择其中一条。

| 符号 | 含义 | 作用 |
|---|---|---|
| ${\bf o}_t,{\bf o}^*$ | 当前观测、目标观测 | 任务域中的输入表示 |
| ${\bf s}_t,{\bf s}^*$ | 当前内部状态、目标内部状态 | 认知地图中的坐标 |
| **Q** | 观测嵌入 | ${\bf s}_t={\bf Q}{\bf o}_t$ |
| **V** | 动作嵌入/前向模型 | 预测动作造成的状态位移 |
| **W** | 逆模型 | 把目标方向映射为各动作效用 |
| **G** | 通用可供性映射 | 预测哪些动作在想象状态中可执行 |
| ${\bf u}_t$ | 动作效用 | 与目标方向的匹配程度 |
| ${\bf e}_t$ | 动作资格值 | 效用、门控和噪声的组合 |
| $\boldsymbol\epsilon$ | 高斯噪声 | 控制候选轨迹的多样性 |

### 4. 从训练到想象的完整计算流程

```text
真实探索数据 (o_t, a_t, o_{t+1})
              │
              ▼
学习 Q、V：让动作在内部空间中表现为可加位移
学习 W：把局部状态差映射回造成它的动作
学习 G：从状态预测动作可供性
              │
              ▼
输入起点 o_0 和目标 o*
ŝ_0 = Q o_0，s* = Q o*
              │
              ▼
u_t = W(s* - ŝ_t)              计算目标导向效用
e_t = ĝ_t ⊙ (u_t + ε)          加噪并屏蔽不可执行动作
a_t = WTA(e_t)                 选出本次虚拟动作
ŝ_{t+1} = ŝ_t + V a_t          在内部前向推进
              │
              └──── 重复，直到目标、死路或长度上限

多次采样 → 多条候选轨迹 → 可选的奖励/代价筛选
```

#### 4.1 学习前向认知地图

观测和动作被放入同一个高维空间：

$$
{\bf s}_t={\bf Q}{\bf o}_t,\qquad {\bf s}^*={\bf Q}{\bf o}^*.
$$

模型希望动作效应可以做向量加法：

$$
\widehat&#123;&#123;\bf s}}_{t+1}={\bf Q}{\bf o}_t+{\bf V}{\bf a}_t,
$$

$$
{\bf Q}{\bf o}_{t+1}\approx {\bf Q}{\bf o}_t+{\bf V}{\bf a}_t.
$$

论文用局部 delta rule 更新 **Q** 和 **V**，目标是减小下一状态预测误差，而不是预测奖励。这样学到的内部空间保留了动作造成的关系结构。

#### 4.2 学习逆模型 **W**

探索时已知动作和真实状态差，因此用 Hebbian 形式学习：

$$
\Delta {\bf W}_{t+1}=\eta_w {\bf a}_t({\bf s}_{t+1}-{\bf s}_t)^{\rm T}.
$$

规划时，把更远的目标差输入同一个线性逆模型：

$$
{\bf u}_t={\bf W}({\bf s}^*-\widehat&#123;&#123;\bf s}}_t).
$$

这是 GCML 的关键泛化假设：虽然 **W** 只见过局部一步位移，但若认知地图几何和逆模型足够线性，它仍能判断哪个局部动作大致朝向远处目标。

#### 4.3 可供性、噪声与 WTA

单纯沿目标方向走可能选到物理上不可执行的动作。因此通用 GCML 用 **G** 从想象状态预测可供性，再形成资格值：

$$
{\bf e}_t=\widehat&#123;&#123;\bf g}}_t\odot({\bf u}_t+\boldsymbol\epsilon).
$$

动作由 winner-take-all 选出：

$$
{\bf a}_t={\rm WTA}({\bf e}_t).
$$

低噪声时，轨迹更集中于认知地图给出的最强方向；高噪声时，轨迹更丰富，可能发现奖励更高或绕开障碍的路线，但也更容易变长或不稳定。

#### 4.4 内部自举：想象与真实执行的分界

CML 执行动作后读取环境的新观测；GCML 不执行虚拟动作，而是用前向模型更新内部状态：

$$
\widehat&#123;&#123;\bf s}}_{t+1}=\widehat&#123;&#123;\bf s}}_t+{\bf V}{\bf a}_t.
$$

新状态再次进入“目标差 → 效用 → 门控 → WTA → 前向推进”的闭环。这就是论文所谓的目标导向想象。

### 5. 三个任务域如何落地

#### 5.1 二维空间导航

空间版本使用 1,000 个解析构造的网格细胞活动作为状态，并学习从网格编码差到上、下、左、右四个基础动作的逆映射。动作中加入高斯噪声后形成多样路径；障碍物产生排斥力，修正二维位移。图 1 直观看到：噪声越大，路径越分散；轨迹能够穿过探索阶段未访问的区域，也能绕开新障碍。

#### 5.2 随机抽象图

节点和有向边动作都采用 one-hot 表示。论文的主要示例含 32 个节点，节点度为 2–5；用 200 条长度 32 的随机轨迹学习地图。低噪声时样本集中在最短路径附近，高噪声产生更多稍长路径。若节点奖励是在学图之后才指定，多样性更高的候选集合有更大机会包含高累计奖励路径。

#### 5.3 轮廓分解与重建

轮廓是 10×10 二值图像；动作是在特定位置移除八种 building block 之一，共 664 个位置相关动作。训练集为 18,000 条五块轮廓分解轨迹，测试集 2,000 条，核心泛化实验从未见过的八块轮廓出发。

这一任务对通用模型做了专门化：**Q** 保持恒等映射，固定四邻域卷积计算突出像素的上下文信息；**W** 学成二值重叠映射；$\mathsf g_1$ 提供真实可行性，$\mathsf g_2$ 用卷积衡量局部约束。多次带噪采样能避开某些早期错误移除，从而显著提高成功率。同一认知地图还可把目标改成非空轮廓，或通过“先拆后装”完成重建。

### 6. 结果应该怎样解读？

论文证据支持的是一种清晰的折中：

- 与 K*、mA*、BELA* 等精确搜索相比，GCML 不保证最优，图变大后路径长度误差上升；
- 但它生成第一条候选轨迹时访问的节点更少，目标改变后的额外重规划代价在实验中近乎可忽略；
- 在轮廓任务的小样本预算下，GCML 的成功率优于 Random、CML、duelling double DQN 和基于 CEM 的 MPC；20 次采样时与 MPC 大致持平；
- 它的价值在于低延迟、目标可切换的候选方案生成，而不是取代所有精确搜索。

图 1 和图 3 的“噪声—多样性”关系、图 4 从五块训练到八块测试的泛化、图 6 的精度—在线计算量折中，是最直接的视觉证据。关于海马回放、局部突触可塑性、WTA 神经回路和神经形态硬件的论述主要是机制解释与实验假设，不能当作已验证的生物实现。

### 7. 代码与论文的对应程度

当前固定快照为 GitHub `LH-cbicr/GCML` 的 `main@ff76859b71a2bc2056b50f5e052475351c007f76`。直接阅读代码可确认：

- `gcml_abstract_graph.ipynb:409-459` 含 **Q/V/W/G** 初始化和局部更新；`:687-788` 含目标效用、噪声、门控、`argmax` WTA 和内部轨迹采样；
- `gcml_grid_cell.ipynb:649-690` 与 `:1001-1058` 含网格编码方向、噪声导航和障碍排斥；
- `gcml_tiling.ipynb:403-562` 含固定卷积编码、动作效应学习、真实可供性枚举和带噪移除；
- `utils/dataset_tiling.py:74-116`、`:183-303` 精确实现位置相关动作、相邻且不重叠的五块轮廓生成和 20,000 条 HDF5 轨迹。

但代码保真度只能评为中等：仓库以演示 notebook 为主，没有统一入口、测试或 Fig. 6 的 K*/mA*/BELA*、RL、MPC 基线脚本；tiling notebook 默认加载的 `tmp_data/fig4_tiling.pth` 不存在；数据脚本含硬编码绝对路径；tiling notebook 直接计算真实可供性，并未完整实现独立的学习式 **G**。补充材料 PDF 存在，但本次没有补充 Markdown，也没有执行 OCR，因此 Supplementary Algorithms 1–2 未与代码逐项核对。Notebook 源码已审阅，但本次未运行实验，数值结果仍属于论文报告。

### 8. 适用边界

GCML 更适合“目标经常变化、需要快速提出若干可行候选、允许近似解”的离散规划问题。它不提供最优性或完备性保证；U 形障碍等局部结构可能需要更高噪声才能逃离，从而降低稳定性；通用连续状态和连续动作仍是 MPC 更自然的应用场景。实际复现时，还必须补齐基线代码、模型资产、运行入口和参数化配置。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Neural Sampling from Cognitive Maps Enables Goal-Directed Imagination and Planning

### Problem

Planning systems should adapt quickly when the goal or environment changes and should propose solutions that traverse states never encountered during training. Standard reinforcement learning often binds learning to rewards or goals and can require retraining; exact graph search and model predictive control perform substantial query-time computation. Existing cognitive-map models, including the CML (*Nature Communications*, 2024), learn useful transition geometry but are deterministic and therefore generate one action sequence rather than a diverse menu of imagined solutions.

### Proposed Method

The paper introduces the **generative cognitive map learner (GCML)**. During exploration, observation and action embeddings **Q** and **V** learn an additive forward model, an inverse map **W** learns which actions cause state differences, and an affordance map **G** learns which actions are feasible. At planning time, **W** maps the difference between the goal and an internally predicted current state to action utility. Affordance gating removes infeasible choices, Gaussian noise creates diversity, a winner-take-all step chooses a virtual action, and **V** advances the imagined state without environmental feedback. Repeating this loop samples goal-directed trajectories; changing the goal does not require relearning the map.

Three instantiations are studied: grid-cell-based 2D navigation, short paths through random abstract graphs, and NP-hard decomposition/rebuilding of binary silhouettes from building blocks. The compositional task uses a 10×10 binary state, eight block types, 664 placement-specific actions, and a fixed local convolution to emphasize context-sensitive pixels.

### Evaluation and Main Findings

- **Spatial navigation:** sampled paths become more diverse as noise increases, can enter a region excluded during exploration, and reroute around novel barriers. The match to hippocampal replay is qualitative rather than a fitted quantitative comparison.
- **Abstract graphs:** on a 32-node graph, low noise concentrates samples near the shortest path; higher noise produces longer but more diverse paths and improves the best accumulated reward across 40 samples. For the benchmark, $k=5$ paths are evaluated on graphs of 32–160 nodes, ten graphs per size and 100 start/goal pairs per graph.
- **Compositional generalization:** the model trains on 18,000 five-block silhouettes and evaluates on 2,000 disjoint cases, including eight-block starts. Success rises sharply as more trajectories are sampled and exceeds Random and deterministic CML; the same map also supports non-empty goals and remove-then-add rebuilding.
- **Baselines:** K*, mA* and BELA* remain exact for the graph task, whereas GCML's relative path-length error increases modestly with graph size. GCML visits far fewer nodes and has negligible additional replanning cost when the query changes. For tiling, the reported GCML success is highest at small sample budgets against Random, duelling double DQN, cross-entropy MPC and CML, and is approximately tied with MPC at twenty samples.

The central trade-off is therefore **approximate quality for low-latency, goal-flexible online proposal generation**, not superiority to exact search on optimality.

### Relationship to Prior Methods

The CML (*Nature Communications*, 2024) supplies the predictive cognitive-map learning rules but is deterministic. Successor-representation RL, including the predictive-map account (*Nature Neuroscience*, 2017), can decouple some goal changes from relearning, but the paper identifies sampling compositional trajectories through unseen states as unresolved. The Tolman–Eichenbaum machine (*Cell*, 2020) emphasizes structural generalization but not the GCML's explicit direction-to-arbitrary-goal sampler. MPC (*Automatica*, 1989) handles continuous control more naturally but repeatedly optimizes action sequences online; the paper's cross-entropy implementation incurs rollout/refinement work at every step.

### Limitations

GCML is heuristic and is not guaranteed to find a valid or optimal path. Higher noise can escape local structures but reduce stability; U-shaped obstacles are identified as a difficult case. The generic experiments use discrete actions and mostly synthetic settings. Fig. 6's online effort and replanning metrics do not include fixed parameter storage or training cost. Neural and biological interpretations—local plasticity, WTA circuitry, hippocampal replay and neuromorphic suitability—are mechanistic proposals rather than empirical validation of the brain implementation.

### Reproducibility

**Rating: 3/5 (partial).** The paper, six primary figures, three demonstration notebooks, environment file and synthetic HDF5 data are public at the pinned repository snapshot (`ff76859b71a2bc2056b50f5e052475351c007f76`). Direct source inspection verifies representative spatial, graph Q/V/W/G, noisy planning, and tiling code. The tiling data generator closely matches the reported 20,000 five-block trajectories but has a hard-coded output path and module-level side effects.

The snapshot is not an end-to-end reproducibility package: it has no unified entry point, tests, or scripts for the Fig. 6 K*/mA*/BELA*, RL and MPC comparisons; a default tiling checkpoint path points to an absent `tmp_data/fig4_tiling.pth`; and notebook variants simplify parts of the paper's full affordance and learning rules. The supplementary PDF exists locally, but no supplementary Markdown was available, so Algorithms 1–2 were not checked. Notebook source was inspected but experiments were not rerun; numerical results remain paper-reported.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
