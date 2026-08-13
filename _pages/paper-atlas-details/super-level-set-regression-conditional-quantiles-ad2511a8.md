---
layout: default
permalink: /paper-atlas/super-level-set-regression-conditional-quantiles-ad2511a8/
title: "Super_Level_Set_Regression_Conditional_Quantiles"
nav: false
wide: true
description: "给定特征 X 和多维响应 Y，SLS 不先拟合完整的条件密度 p(y\\mid X)，而是直接学习一条随 X 改变的几何边界，使边界内大约包含目标比例 \\tau 的样本，同时尽可能缩小区域体积。 这是一篇统计机器学习方法论文，核心属于多元条件分位数回归、最小体积预测集合和共形预测，并非生物信息学文章。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Super_Level_Set_Regression_Conditional_Quantiles</h1>
    <p>Super-Level-Set Regression: Conditional Quantiles via Volume Minimization</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2605.06210" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Super_Level_Set_Regression_Conditional_Quantiles">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ElSacho/super_level_sets_regression" target="_blank" rel="noopener noreferrer" aria-label="Open code for Super_Level_Set_Regression_Conditional_Quantiles">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Super-Level-Set Regression：用体积最小化直接学习条件分位数区域

### 一句话理解

给定特征 $X$ 和多维响应 $Y$，SLS 不先拟合完整的条件密度 $p(y\mid X)$，而是直接学习一条随 $X$ 改变的几何边界，使边界内大约包含目标比例 $\tau$ 的样本，同时尽可能缩小区域体积。

这是一篇**统计机器学习方法论文**，核心属于多元条件分位数回归、最小体积预测集合和共形预测，并非生物信息学文章。

### 1. 它要解决什么问题？

在一维中，“第 90% 分位数”有自然的顺序定义；但当 $Y\in\mathbb R^d$ 时，不存在唯一的多维排序。真正有用的对象往往是条件最高密度区域：在给定 $X$ 时，用最小体积装下至少 $\tau$ 的条件概率质量。

理论目标可写为

$$
\min_{\mathcal B(X)}\operatorname{Vol}(\mathcal B(X))
\quad\text{s.t.}\quad
\mathbb P(Y\in\mathcal B(X)\mid X)\ge \tau.
$$

传统做法通常先估计整个 $p(y\mid X)$，再寻找密度阈值。这有三个问题：

1. 为了得到一个特定覆盖率的区域，却要学习所有低密度和尾部细节；
2. 复杂密度的阈值常需大量 Monte Carlo 计算；
3. 直接学习区间、矩形或椭球的方法又会预设过强的几何形状，难以表达偏斜、多峰或不连通区域。

### 2. SLS 的基本表示

SLS 学习一个“边界评分函数” $G(X,y)$ 和一个随特征变化的阈值 $q_\tau(X)$：

$$
C_\tau(X)=\{y:G(X,y)\le q_\tau(X)\}.
$$

$G$ 越小，表示 $y$ 越靠近模型认为的高密度核心。为了让集合具有条件覆盖率，$q_\tau(X)$ 必须对应随机变量 $G(X,Y)\mid X$ 的条件 $\tau$ 分位数。

困难就在这里：一旦 $G$ 改变，$G(X,Y)$ 的条件分位数也会改变；体积目标和分位数约束彼此隐式耦合，直接反向传播容易产生体积塌缩。

### 3. 核心创新：逐渐收窄的分位数窗口

在第 $n$ 个训练阶段，SLS 不只盯住精确的第 $\tau$ 分位点，而是取一个小窗口

$$
[q_{\tau-\phi(n)}(X),\;q_{\tau+\psi(n)}(X)].
$$

只有当样本分数 $G(X,Y)$ 落入这个窗口时，它的几何体积才参与边界更新。对应的目标是

$$
J_n(G)=\mathbb E\left[
\frac{K_n(X,G(X,Y))}{\phi(n)+\psi(n)}
\operatorname{Vol}_G(G(X,Y),X)
\right].
$$

直观上：

- 训练早期窗口宽，模型先获得稳定、不会塌缩的全局几何；
- 训练后期窗口窄，优化逐渐聚焦于目标覆盖率 $\tau$ 附近；
- 更新 $G$ 时固定分位数模型，更新分位数模型时把 $G$ 视为不求导的目标。

命题 3.1 说明，在论文给出的紧致性、连续性、条件密度有界和体积一致 Lipschitz 等假设下，当窗口收缩时，该代理目标一致收敛到目标条件分位数处的期望体积，代理最优解的极限点也会落到原约束问题的最优解上。这是总体层面的渐近结论，不等同于有限样本的精确条件覆盖保证。

实际代码不会让窗口宽度严格变成 0，而是退火到小的正数。这样可以减少分位数估计误差导致的错位，并避免极薄窗口产生爆炸梯度。

### 4. 怎样表示复杂区域？

#### 4.1 单个流：表达连通但高度非线性的形状

基本边界为

$$
G_\theta(X,Y)=\left\|L_\theta(X)left(T_\phi(Y;X)-\mu_\theta(X)\right)\right\|_2^2.
$$

这里：

- $\mu_\theta(X)$ 决定中心；
- $L_\theta(X)$ 决定局部椭球形状；
- $T_\phi(Y;X)$ 是条件体积保持流，Jacobian 行列式恒为 1。

因此集合体积有解析形式

$$
\operatorname{Vol}(q(X),X)\propto\frac{q(X)^{d/2}}{\det L_\theta(X)}.
$$

若 $T$ 是恒等映射，区域就是椭球；加入体积保持流后，椭球可被弯曲为星形、弯带等非凸但仍连通的区域，而且体积计算仍然可控。

#### 4.2 多个流：表达不连通、多峰区域

单个可逆流保持拓扑连通性，因此对多个彼此分离的高密度岛屿不够自然。SLS 建立 $K$ 个局部流和 Mahalanobis 边界，再用 softmin 近似最小值：

$$
G_\beta(X,Y)=\sum_k w_kG_k(X,Y),\qquad
w_k=\frac{e^{-\beta G_k}}{\sum_j e^{-\beta G_j}}.
$$

随着 $\beta$ 增大，它逼近 $\min_kG_k$，集合就能成为多个不连通分量的并。此时重叠区域的精确体积通常无闭式解，论文和代码都采用各分量体积之和作为代理；这是一项明确的近似。

### 5. 训练流程

```text
训练样本 (X, Y) + 目标覆盖率 tau
          |
          v
共享网络预测中心、精度矩阵、分量权重
以及 q_low(X)、q_tau(X)、q_high(X)
          |
          v
体积保持流变换 Y，计算一个或多个 G_k(X,Y)
          |
          v
softmin 合并成总体边界分数 G(X,Y)
          |
          +--------------------------------+
          | 每个 minibatch 的交替更新       |
          | 1. detach G，pinball loss 更新 q |
          | 2. detach q，窗口内体积更新 G    |
          | 3. 收窄窗口并增大 softmin beta   |
          +--------------------------------+
          |
          v
用校准后的验证体积选择 checkpoint
          |
          v
可选阈值细化 + split conformal 标量校正
          |
          v
C_tau(X)={y:G(X,y)<=r q_tau(X)}
```

代码与这一流程高度吻合：`SLS_regressor` 同时构造中心、精度矩阵、流和三个分位数头；每个 minibatch 先更新 pinball loss，再更新体积 loss，并进行梯度裁剪和退火。高维响应可采用 $D+VV^\top$ 的低秩精度矩阵，并使用更稳定的 log-volume 目标。

### 6. 共形校准保证了什么？

SLS 用独立校准集计算

$$
S_i=\frac{G(X_i,Y_i)}{q_\tau(X_i)}
$$

的经验分位数 $r$，最终阈值变为 $rq_\tau(X)$。这给出有限样本的**边际覆盖**保证。它不保证每个具体 $X$ 都精确达到 $\tau$，因为无强分布假设时，非平凡的分布无关精确条件覆盖本来就不可能。SLS 的条件分位数网络负责提高条件适应性，共形步骤则作为整体有效性的保险。

### 7. 实验告诉了我们什么？

#### 合成数据

合成图像直接展示了：

- 单流可沿着不对称、弯曲的高密度带形成非凸区域；
- 区域随 $X$ 改变位置、宽度和方向；
- 在远端异常点存在时，SLS 的椭球仍围住主密度团，而 Gaussian NLL 会被异常点拉偏；
- 同一代理思想还能学习条件中位绝对偏差，不只适用于体积。

#### 真实数据

论文使用 Bias、CASP、House、rf1、rf2 和 Taxi 六个多输出表格数据集，样本量从 7,752 到 61,286，输出维度为 2 或 8，比较 C-HDR、PCP、CP2-PCP、L-CP 和 C-PCP。指标必须联合解读：预测集合体积越小越有效，ERT 条件覆盖偏差越小越有效。

- $\tau=0.9$ 时，SLS 在 Bias、rf1、CASP 上取得最小体积，但并非所有数据集都最好；
- $\tau=0.5$ 时，SLS 在 Bias、rf1 上体积最小，并在 rf1、rf2、CASP 上取得最低 ERT；
- 某些竞争方法体积更小，却伴随明显更差的条件覆盖偏差。

因此最稳妥的结论是：SLS 在“区域大小—条件适应性”的 Pareto 权衡上有竞争力，而不是对所有基线、所有指标全面领先。

### 8. 复现性与限制

- 官方代码仓库已固定到 commit `0b29d4f3f8a3e9ea0c8bfe446127993bf82a33be`，核心模型与论文高度一致。
- 仓库包含使用/实验 notebook、基线实现和数据集参数，但没有自动化测试或随仓库提供的结果文件。
- 论文最后使用 TabICL 细化 $q_\tau$；核心类提供外部分位数模型接口，但没有把 TabICL 步骤封装成独立的一键脚本。
- 本次分析没有安装 GPU 依赖或重新运行 V100 实验，因此数值结果没有独立复现。
- arXiv HTML 转换保留了六张本地图，但每张多面板图只抓取到一个面板；未保留面板的结论仅根据论文图注和表格核对。
- 实际训练窗口停在正宽度，多个流的并集使用体积代理，且训练集上的最终阈值细化可能过拟合。这些都是论文自己承认或代码直接显示的边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Super-Level-Set Regression: summary

### Problem

For multivariate regression, a useful prediction region should adapt to $X$, contain a target conditional probability $\tau$, and avoid wasting volume on low-density areas. Density plug-in approaches estimate the entire conditional law $p(y\mid X)$ before thresholding it, which is statistically and computationally demanding. Simpler direct approaches often impose intervals, rectangles, ellipsoids or marginal rather than conditional constraints, making them inefficient for skewed, nonconvex or multimodal responses (`paper.md:14-29,49-67`).

### Proposed method

Super-level-set regression (SLS) directly learns

$$
C_\tau(X)=\{y:G(X,y)\le q_\tau(X)\},
$$

where $G$ is a geometric frontier and $q_\tau(X)$ is the conditional $\tau$-quantile of $G(X,Y)$. Its central contribution is a shrinking-window surrogate: rather than differentiating through a model-dependent conditional quantile, it minimizes frontier volume only for samples whose scores lie in a narrowing probability band around $\tau$. Proposition 3.1 gives uniform convergence of this surrogate to target-quantile volume under stated population regularity assumptions (`paper.md:100-180`).

The principal frontier is a conditional volume-preserving flow followed by a Mahalanobis distance. It has analytic volume proportional to $q(X)^{d/2}/\det L(X)$ and can represent highly nonlinear connected regions. A soft minimum over multiple such flows models disconnected/multimodal regions, using the sum of component volumes as an overlap-sensitive proxy (`paper.md:186-258`). Training alternates pinball-loss updates for three conditional quantiles with frontier-volume updates, after a global warm start. A final split-conformal scalar correction gives finite-sample marginal coverage; exact distribution-free conditional coverage remains impossible in general (`paper.md:171-183,646-652,697-735`).

### Evaluation

Synthetic studies cover asymmetric, multimodal, heteroscedastic and outlier-contaminated distributions. The acquired images visually show nonlinear high-density boundaries, covariate-dependent cross-sections, and a rigid SLS ellipse that ignores remote contamination better than Gaussian NLL. The paper's additional experiment applies the same surrogate principle to conditional median absolute deviation, illustrating that it is not specific to volume (`paper.md:267-291,622-627,760-778`).

Real-data evaluation uses six multivariate tabular datasets—Bias, CASP, House, rf1, rf2 and Taxi—with 7,752–61,286 samples and response dimension 2 or 8. SLS is compared with conformalized conditional-density HDR, PCP, CP2-PCP, L-CP and C-PCP over ten seeds. The relevant outcome is the joint trade-off between scaled prediction-set volume and ERT-estimated conditional-coverage deviation. At $\tau=0.9$, SLS reports the smallest volume on Bias, rf1 and CASP; at $\tau=0.5$, it is smallest on Bias and rf1 and has the best ERT on rf1, rf2 and CASP. Other methods win elsewhere, supporting the authors' Pareto-competitiveness claim rather than uniform dominance (`paper.md:292-306,784-844`).

### Reproducibility and evidence assessment

**Rating: 4/5 for inspectability; numerical reproduction not run.** The paper links an official GitHub repository, acquired here at commit `0b29d4f3f8a3e9ea0c8bfe446127993bf82a33be`. Direct source inspection found a high-fidelity implementation of the flow/Mahalanobis frontier, multiple components, annealed window, quantile heads, alternating loss updates, validation-volume checkpointing and conformalization. It also includes usage and experiment notebooks, baseline code and per-dataset parameter files.

Important boundaries remain. The repository has no automated test suite or checked-in experiment results in this snapshot; its README contains two stale filename examples; the paper's TabICL refinement is represented only through a generic external-quantile hook in the core class; and no GPU/V100 experiments were rerun. The arXiv HTML conversion produced six local images but retained only one panel of each multi-panel figure, so absent panels were assessed from captions/tables rather than direct pixels. These are documented limitations, not reasons to lower the code-paper fidelity assessment.

### Domain and paper type

This is a **statistical machine learning method paper**, specifically multivariate conditional quantile regression, minimum-volume prediction regions and conformal prediction. It is not a bioinformatics paper and has been analyzed according to its actual theory, optimization, geometry and tabular experiments.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
