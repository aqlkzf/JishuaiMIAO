---
layout: default
permalink: /paper-atlas/graph-odes-and-beyond-5295276d/
title: "Graph ODEs and Beyond"
nav: false
description: "这是一篇 Graph Neural Differential Equations（Graph NDEs）综述，不提出单一新模型。它把“图神经网络怎样与 ODE、PDE、SDE 结合”整理成一张选择地图：任务是什么、图如何随空间/时间构造、微分方程描述哪种动力学、GNN 在系统中扮演什么角色，以及不同组合解决哪些困难。 Graph NDE 的共同形式是让图上状态 H(t) 沿连续变量演化： t 可以是真实时间，也可以是连续化的网络深度。"
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
      <span>Representation Models</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>Graph ODEs and Beyond</h1>
    <p>Graph ODEs and Beyond: A Comprehensive Survey on Integrating Differential Equations with Graph Neural Networks</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2503.23167" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Graph ODEs and Beyond">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Emory-Melody/Awesome-Graph-NDEs" target="_blank" rel="noopener noreferrer" aria-label="Open code for Graph ODEs and Beyond">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Graph ODEs and Beyond 中文综述解读

### 这篇综述的核心价值

这是一篇 Graph Neural Differential Equations（Graph NDEs）综述，不提出单一新模型。它把“图神经网络怎样与 ODE、PDE、SDE 结合”整理成一张选择地图：任务是什么、图如何随空间/时间构造、微分方程描述哪种动力学、GNN 在系统中扮演什么角色，以及不同组合解决哪些困难。

Graph NDE 的共同形式是让图上状态 $H(t)$ 沿连续变量演化：

$$
\frac{dH(t)}{dt}=f_\theta(H(t),G,t),\qquad H(t_0)=H_0.
$$

$t$ 可以是真实时间，也可以是连续化的网络深度。GNN 可用于构造初始状态、参数化右端向量场，或将求解后的潜在轨迹解码为预测。

### 1. 从离散消息传递到连续深度

普通 GNN 用层索引 $l$ 更新节点：

$$
H^{(l+1)}=H^{(l)}+\operatorname{GNN}_\theta(H^{(l)},G).
$$

当层步长趋于零，可写成 Graph ODE：

$$
\frac{dH(t)}{dt}=\operatorname{GNN}_\theta(H(t),G).
$$

这并非只是换记号。连续形式允许在任意时间求状态、用自适应 solver 控制步长，并可把稳定性、扩散、守恒、能量和随机过程工具引入图学习。但 solver 会反复调用向量场，计算成本不一定低于固定层 GNN；连续化也不自动保证可解释或稳定。

### 2. GNN 的三种角色

图 1明确展示三种组合方式。

1. Encoder：把原始节点/边观测编码为 $H(t_0)$。适合原始特征维度复杂或初始状态不完全可观测的任务。
2. Differential equation：GNN 直接参数化 $dH/dt$，邻接关系决定节点导数如何耦合。这是最典型的 Graph ODE。
3. Decoder：DE 在潜在空间演化，GNN 或图读出把一个或多个时间点映射到节点、边或图级输出。

实际方法可同时使用多个角色。图 1中的彩色轨迹是潜在状态，虚线向上箭头表示解码中间时间点或最终 $H_T$；图结构还可能在事件时刻发生跳变。因此该图是系统框架，不是一套固定网络。

### 3. ODE、PDE 与 SDE 各解决什么

#### ODE

ODE 常用于节点特征随时间变化、连续深度表示学习、事件间演化和不规则采样。它给定当前状态与图后产生确定性导数。Neural ODE、Graph NODE、连续图卷积、latent graph ODE 等属于这一主线。

#### PDE

PDE 视角强调图上的空间传播，例如扩散、对流、波动或反应—扩散。图 Laplacian 离散化空间微分算子；不同频率分量决定平滑、锐化与方向传播。它对解释 over-smoothing、heterophily 与物理系统尤其有用。

#### SDE

SDE 加入随机扩散项：

$$
dH(t)=\mu_\theta(H(t),G,t)dt+\sigma_\theta(H(t),G,t)dW_t.
$$

它可表达观测噪声、过程不确定性和生成扩散，但训练和采样需要随机 solver、score 或相应概率目标。随机性不是“抗噪插件”，应与任务的不确定性假设和校准评价对应。

### 4. 最实用的第一刀：时间动力学还是空间动力学

#### Temporal dynamics

这里 $t$ 是真实时间。综述进一步拆分：

- Dynamic updates：事件可能瞬时改变节点或图，需要 jump/reallocation，而非只靠平滑 ODE。
- Irregular intervals：观测时间不等距，连续模型可在任意时间查询，但插值质量仍依赖可辨识性。
- Delay：邻居影响有传播延迟，导数依赖 $H(t-\tau)$，需 delay differential equation。
- Hybrid systems：用 SIR、Hamiltonian、Lagrangian 或物理约束限定方程形式，或让 GNN 只预测机制参数。
- Efficient simulation：学习 PDE/ODE surrogate 可替代昂贵数值模拟，但必须验证守恒、稳定与外推。

#### Spatial dynamics

这里连续变量常代表模型深度或图上扩散尺度。主要问题包括：

- Over-smoothing：纯扩散最终趋向平稳；source/restart、二阶振荡或 fractional Laplacian 可避免所有节点塌缩。
- Uncertainty：Graph SDE 表达结构与传播噪声。
- Robustness：分析扰动如何沿连续流放大或衰减。
- Heterophily：对流—扩散、低/高通双通道避免只做邻居平滑。
- High-order relations：hypergraph ODE 联合演化顶点和超边状态。

### 5. 图构造同样是模型假设

空间图可以由真实关系、距离、网格、kNN 或学习邻接构造。时间上又分：拓扑固定而节点特征变化；边权随时间变化；节点/边集合本身动态变化。固定图 ODE 无法天然表示新节点/新边出现，通常要加入事件更新、动态邻接模块或连续结构演化。

所以选 Graph NDE 前应先问：图是物理已知还是推断出来？邻接是静态、平滑变化还是突变？边方向和延迟是否重要？若这些假设错了，再先进的 solver 也只是在错误图上精确积分。

### 6. 图 2 如何作为方法检索器

图 2按四行组织文献：顶部是 ranking、link prediction、classification、forecasting、generation；第二行是 ODE/PDE/SDE；第三行列代表方法并用颜色区分静态/动态图；底部标 GNN 作为 decoder、DE 或 encoder。

这张图最适合从任务向下查：例如 forecasting 主要连接 ODE/PDE 方法，graph generation 更多连接 PDE/SDE；然后再看 GNN 角色。它不是排行榜，方法框宽度和位置不代表性能。具体方法的任务、图类型和方程类别应回到 Appendix A核对。

### 7. 五类应用与评价边界

1. Physics simulation：粒子、流体和多体系统需要几何关系、守恒与长程稳定。短期轨迹误差小不等于长期物理可信。
2. Traffic forecasting：路网图与不规则时间共同出现；要检验跨时段、缺失观测、突发事件和动态图泛化。
3. Recommendation：用户—物品是二部动态图，偏好连续变化又伴随离散交互；评价需防时间泄漏和曝光偏差。
4. Epidemic modelling：节点为区域/人群、边为接触；hybrid GNN-SIR 可预测参数或潜在修正，但政策结论需要机制可辨识与不确定性。
5. Graph generation：SDE/score 方法同时演化节点特征和邻接；必须保持 permutation invariance，并评价有效性、唯一性和任务属性。

综述汇总的是不同论文的结果，没有统一数据、划分和指标，不能跨应用用单一数值排方法。

### 8. 常见方法选择

- 仅有不规则时间戳、拓扑基本固定：从 latent/controlled Graph ODE 开始。
- 图在事件时跳变：选择带 jump/update 的混合连续—离散系统。
- 已知传播延迟：使用 delay Graph NDE，而非让普通 ODE 隐式猜延迟。
- 深层静态图 over-smoothing：使用 source/restart、非纯扩散或二阶动力学。
- heterophily：选择 convection/high-pass/dual-channel 方程。
- 噪声与多种未来：选择 Graph SDE 并评价 calibration。
- 物理系统：优先把 Hamiltonian、Lagrangian、守恒或 PDE 结构写入模型。
- 超图/群组关系：使用高阶或 hypergraph differential equation。

### 9. Solver 与训练不是无关细节

自适应 ODE solver 通过容差决定 function evaluations。更严格容差通常更准但更慢；刚性系统可能迫使显式 solver 取极小步。反向传播可用保存轨迹或 adjoint，两者在内存、数值误差和实现复杂度间取舍。事件、非光滑激活、动态邻接和 stochastic dynamics 会进一步影响梯度。

因此报告 Graph NDE 时至少应说明 solver、容差、最大步数、NFE、反向方式、随机种子及推理时间。只报告参数量会漏掉主要计算成本。

### 10. 综述提出的开放问题

作者归纳五个方向：自动发现图微分方程；稀疏和偶发观测；大规模动态图扩展；连续结构演化；层级/多尺度动力学。它们共享一个核心矛盾：模型既要灵活吸收数据，又要保持方程可识别、数值稳定和科学可信。

尤其需要谨慎的是“学到的导数”等同机制的说法。多个向量场可能在有限观测点产生相似轨迹；隐藏混杂、错误邻接和稀疏采样会削弱可辨识性。方程发现需要符号/稀疏先验、干预数据、跨轨迹验证和不确定性，而不只是拟合误差。

### 11. 证据与代码边界

这是 review/no-code 工作区。论文提供的 `Awesome-Graph-NDEs` 是文献清单，不是实现本文所有方法的代码仓库；本次不创建 `doc_code.md`，也不声称代码复现。两张主图 `x1.png`、`x2.png` 已直接检查。arXiv HTML 正文含 Appendix A方法总表，没有单独补充文件。

### 推荐阅读路线

先看图 1建立 encoder—DE—decoder 心智模型，再读 ODE/PDE/SDE背景；接着用“真实时间 vs 连续深度”分流到 temporal 或 spatial methodology；用图 2和 Appendix A找代表论文；最后读 Future Work，检查自己的数据是否真正支持所选动力学假设。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Graph ODEs and Beyond

### Review Scope

This is a review/survey article, not a primary method paper. The paper surveys Graph Neural Differential Equations (Graph NDEs), a family of models that combine graph neural networks with ODE/PDE/SDE-style continuous dynamics. The stated scope is to categorize existing Graph NDE methods, explain their principles, summarize applications, and identify future research directions across molecular modeling, traffic prediction, epidemic spreading, physics simulation, recommendation, and graph generation (`paper source/arxiv_html/paper.md:14`, `paper source/arxiv_html/paper.md:32-38`).

The authors position the review around a gap in prior surveys: existing reviews were either too narrow around neural differential equations or too narrow around graph-DE integration, while this paper aims to cover a broader methodology taxonomy for continuous spatial and temporal graph dynamics (`paper source/arxiv_html/paper.md:41`).

### Core Thesis

Graph NDEs treat graph learning as continuous state evolution rather than only discrete message-passing layers. The paper frames the class around two components: a differential equation governing temporal or spatial state evolution, and an initial condition that starts the trajectory. GNNs can appear as encoders, decoders, or the differential-equation parameterization itself (`paper source/arxiv_html/paper.md:88-106`).

### Taxonomy

The review organizes Graph NDEs along four main axes:

| Axis | Categories | Evidence |
| --- | --- | --- |
| Task | Node/graph classification, link prediction, ranking, forecasting, graph generation | `paper source/arxiv_html/paper.md:130-148` |
| Graph construction | Point-based vs grid-based spatial graphs; static vs dynamic temporal graphs | `paper source/arxiv_html/paper.md:151-178` |
| Dynamics target | Temporal dynamics over real time vs spatial dynamics over model depth | `paper source/arxiv_html/paper.md:181-200` |
| DE family and GNN role | ODE/PDE/SDE and GNN as encoder, decoder, or DE module | `paper source/arxiv_html/paper.md:88-106`, `paper source/arxiv_html/paper.md:605-651` |

### Method Landscape

The methodology section separates temporal and spatial challenges. Temporal modeling covers dynamic graph updates, irregular time intervals, temporal delays, hybrid systems, and efficient simulation (`paper source/arxiv_html/paper.md:212-248`). Spatial modeling covers over-smoothing, uncertainty, adversarial robustness, heterophily, and high-order relations (`paper source/arxiv_html/paper.md:251-291`).

The major trade-off is that differential-equation views offer continuous-time interpolation, principled dynamics, and physical analogies, but they also inherit solver cost, scalability pressure, and implicit vector-field interpretability issues (`paper source/arxiv_html/paper.md:248`, `paper source/arxiv_html/paper.md:348-351`).

### Applications

The paper highlights five application groups:

| Application | Review claim |
| --- | --- |
| Physics systems simulation | Graph ODEs parameterize continuous-time physical dynamics and can incorporate Hamiltonian or hybrid-system structure. |
| Traffic flow forecasting | Continuous-time graph dynamics help model long-range and irregular traffic evolution. |
| Recommendation systems | Bipartite user-item graphs can be modeled as continuously evolving preferences. |
| Epidemic modeling | Hybrid GNN-mechanistic models integrate graph structure with SIR-like dynamics. |
| Graph generation | SDE-based graph diffusion can model node and edge distributions while respecting permutation invariance. |

Evidence: `paper source/arxiv_html/paper.md:294-327`.

### Open Problems

The review identifies five directions: discovering explicit graph differential equations, handling sparsity and sporadic observations, scaling to large dynamic graphs, modeling continuously changing graph topology, and integrating multi-scale or hierarchical graph dynamics (`paper source/arxiv_html/paper.md:330-363`).

### Reproducibility And Code

No implementation code is associated with this review. The only discovered GitHub link is a companion literature list, `https://github.com/Emory-Melody/Awesome-Graph-NDEs`, which the acquisition step identified as not being a primary implementation repository. This workspace is therefore review/no-code.

### Evidence Status

The arXiv HTML conversion produced a complete structured paper markdown with 651 lines. The two main figures were reacquired manually from the arXiv HTML image paths and are stored under `paper source/arxiv_html/images/`. Both figures were visually inspected for this analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
