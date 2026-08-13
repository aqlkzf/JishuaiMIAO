---
layout: default
permalink: /paper-atlas/online-decision-focused-learning-a651f216/
title: "Online_Decision_Focused_Learning"
nav: false
wide: true
description: "经典的“先预测、再优化”流程先让模型尽量准确地预测成本，再把预测值交给一个优化器做决策。但预测误差小，不等于决策一定好：只要预测落在错误的决策边界一侧，即使数值非常接近真实成本，也可能选错物品；反过来，一个数值偏差较大、但仍位于正确边界一侧的预测，可以产生正确决策。 决策聚焦学习（decision-focused learning, DFL）因此不直接最小化预测误差，而是让模型最小化最终决策产生的真实成本。此前相关理论主要针对固定的 i."
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
      <span>ICLR · 2026</span>
    </div>
    <h1>Online_Decision_Focused_Learning</h1>
    <p>Online Decision-Focused Learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2505.13564" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Online_Decision_Focused_Learning">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Online Decision-Focused Learning 方法详解

### 1. 这篇论文要解决什么问题？

经典的“先预测、再优化”流程先让模型尽量准确地预测成本，再把预测值交给一个优化器做决策。但预测误差小，不等于决策一定好：只要预测落在错误的决策边界一侧，即使数值非常接近真实成本，也可能选错物品；反过来，一个数值偏差较大、但仍位于正确边界一侧的预测，可以产生正确决策。

决策聚焦学习（decision-focused learning, DFL）因此不直接最小化预测误差，而是让模型最小化最终决策产生的真实成本。此前相关理论主要针对固定的 i.i.d. 批数据。本文考虑在线、非平稳场景：每一轮的协变量分布和真实成本函数都可以变化。

第 $t$ 轮的流程是：

1. 观察协变量 $X_t$，但尚不知道真实成本 $\bar g_t(X_t)$；
2. 用模型 $g(\theta_t,X_t)$ 预测成本；
3. 在有界多面体 $\mathcal W$ 上求解线性优化问题
   $$
   w_t^\star(\theta_t)\in\operatorname*{arg\,min}_{w\in\mathcal W}
   \langle g(\theta_t,X_t),w\rangle;
   $$
4. 执行动作后才看到 $\bar g_t(X_t)$，再更新 $\theta_{t+1}$。

真正关心的损失是

$$
f_t(\theta)=\langle\bar g_t(X_t),w_t^\star(\theta)\rangle.
$$

困难在于：线性目标在多面体上通常选择某个顶点，所以 $w_t^\star(\theta)$ 随 $\theta$ 呈分段常数变化，梯度要么为零、要么不存在；由此产生的外层损失通常还是非凸的。普通 OGD 或基于凸性的在线算法不能直接使用。

### 2. 共同基础：先把内层决策变得可微

论文不是简单地给预测损失加正则，而是正则化**内层决策问题**：

$$
\widetilde w_t(\theta)\in\operatorname*{arg\,min}_{w\in\mathcal W}
\left\{\langle g(\theta,X_t),w\rangle+\alpha_t\mathcal R(w)\right\}.
$$

随后用已经揭示的真实成本定义代理损失

$$
\widetilde f_t(\theta)=\langle\bar g_t(X_t),\widetilde w_t(\theta)\rangle.
$$

这样就能通过 $\nabla\widetilde w_t$ 计算 $\nabla\widetilde f_t$。$\alpha_t$ 控制一个核心权衡：取值大时决策映射更平滑，但偏离原始离散决策更多；取值小时逼近更准，但梯度相关常数会变差。

对于一般的非退化有界多面体

$$
\mathcal W=\{w:A^\mathsf T w-b\preccurlyeq0\},
$$

论文使用对数障碍

$$
\mathcal R(w)=-\sum_{i=1}^n\ln(b_i-A_i^\mathsf T w),
$$

它把解限制在多面体内部，从而可用隐函数定理得到 Jacobian。对于单纯形，使用负熵 $\sum_iw_i\ln w_i$，此时 $\widetilde w_t$ 就是温度由 $\alpha_t$ 控制的 softmax。实验采用的是后一个单纯形版本；一般多面体理论中的 $n$ 表示面数，不能把两种情形混为一谈。

### 3. 两个必要假设

**H1（有界性与模型光滑性）**要求参数集合 $\Theta$ 紧且凸、直径有限；$g(\theta,X_t)$ 对 $\theta$ 连续可微且 Jacobian 一致有界；真实成本向量也有界。论文不要求真实成本一定能由模型类精确表达，也就是不要求 realizability。

**H2（margin 条件）**控制最优顶点与次优顶点之间出现近似平局的概率。它保证正则化软决策与原始顶点决策之间的期望距离可控。如果经常有多个顶点几乎同样好，轻微平滑就可能大幅改变动作，理论也无法得到相同的逼近控制。

正则化后损失仍然非凸，因此论文进一步假设存在一个 $\xi$-近似离线 oracle：

$$
h(\mathbf O_\xi(h))\le\inf_{\theta\in\Theta}h(\theta)+\xi.
$$

论文用 SGD 找局部极小值来解释其实践合理性，但这不是“SGD 必然找到全局最优”的保证；最终遗憾界中保留了 $\xi$，oracle 不够准确时误差不会消失。

### 4. DF-FTPL：扰动累计目标，控制静态遗憾

DF-FTPL 每轮真正执行的仍是未正则化的精确决策 $w_t^\star(\theta_t)$；$\widetilde w_t$ 只用于构造可微训练损失。观察真实成本后，它更新

$$
\theta_{t+1}=\mathbf O_\xi\!\left(
\sum_{i=1}^t\widetilde f_i-\langle\sigma_t,\cdot\rangle
\right),
$$

其中 $\sigma_t$ 各坐标服从参数为 $\eta$ 的指数分布。

这里的关键是：DF-FTPL 对**截至当前的全部正则化损失之和**加随机线性扰动，再调用 oracle 近似最小化累计目标。它不是一步梯度下降，也不是只跟踪最新一轮的最优点。

它控制静态遗憾，即与一个全程固定的最佳参数比较。调参后平均静态遗憾为

$$
T^{-1}\mathbb E[\mathfrak R_T^s]
=\widetilde{\mathcal O}\!\left(m^{3/4}n^{3/2}T^{-1/4}+\xi\right).
$$

要让平均遗憾趋于零，$\xi$ 也必须随 $T$ 下降，例如达到 $\mathcal O(T^{-1/4})$。

### 5. DF-OGD：在线段上随机取梯度，控制动态遗憾

DF-OGD 不扰动累计目标。每一轮先对**当前**代理损失调用 oracle：

$$
\vartheta_t=\mathbf O_\xi(\widetilde f_t).
$$

然后采样 $s_t\sim\operatorname{Unif}[0,1]$，令

$$
u_t=\vartheta_t+s_t(\theta_t-\vartheta_t),
$$

也就是让 $u_t$ 在 $[\theta_t,\vartheta_t]$ 线段上均匀分布，再更新

$$
\theta_{t+1}=\Pi_\Theta\left[
\theta_t-\eta_t\nabla\widetilde f_t(u_t)
\right].
$$

为什么一定要在线段上均匀采样？因为对可微但非凸的 $\widetilde f_t$，有

$$
\widetilde f_t(\theta_t)-\widetilde f_t(\vartheta_t)
=\int_0^1
\left\langle
\nabla\widetilde f_t(\vartheta_t+s(\theta_t-\vartheta_t)),
\theta_t-\vartheta_t
\right\rangle ds.
$$

均匀采样后，随机梯度内积的期望恰好等于这段代理损失差。这一等式替代了凸 OGD 证明常用的凸性不等式。因此，这里的随机化不能只笼统地称为“乐观机制”：它具体是以当前 oracle 点为线段端点，对梯度评价位置做随机化，从而在期望上恢复非凸损失差。

DF-OGD 控制动态遗憾，即与每轮不同的条件期望损失最优点比较。环境变化由 oracle 路径长度

$$
P_T=\sum_{t=1}^{T-1}\|\vartheta_{t+1}-\vartheta_t\|
$$

衡量。调参后的平均动态遗憾为

$$
T^{-1}\mathbb E[\mathfrak R_T^d]
=\widetilde{\mathcal O}\!\left(
\mathbb E[\sqrt n(1+P_T)^{1/4}T^{-1/4}]+\xi
\right).
$$

因此环境变化越快、$P_T$ 越大，保证越弱；要得到消失的平均动态遗憾，还需要 $P_T$ 增长足够慢以及 $\xi$ 足够小。这个调优界不显含预测参数维数 $m$，但仍依赖多面体面数 $n$ 以及被 $\widetilde{\mathcal O}$ 隐去的几何和对数因子。

### 6. 两种方法的差别一览

| 维度 | DF-FTPL | DF-OGD |
|---|---|---|
| oracle 输入 | 累计代理损失减去随机线性扰动 | 当前代理损失 $\widetilde f_t$ |
| 随机化位置 | 扰动整个累计目标 | 在 $[\theta_t,\vartheta_t]$ 上随机选择梯度评价点 |
| 参数更新 | 直接取扰动累计目标的近似最优解 | 投影梯度步 |
| 比较对象 | 一个固定最佳参数 | 每轮变化的条件风险最优参数 |
| 理论指标 | 静态遗憾 | 动态遗憾，依赖 $P_T$ |
| 步长/正则 | 固定 $(\eta,\alpha)$ | 随时间变化的 $(\eta_t,\alpha_t)$ |

两者共同使用内层正则化与近似 oracle，但不能把 DF-OGD 描述成 DF-FTPL 的梯度版本：oracle 的目标、随机化对象、比较基准和理论结论都不同。

### 7. 实验如何验证方法？

实验是“每轮从 $K$ 个物品中选成本最低的一个”，等价于在 $K$ 维单纯形上优化。数据具有相关特征、非线性成本和随时间变化的真实参数，但学习器只使用线性预测模型，因此存在明显 misspecification。

主实验设置为 $K=5$、$p=10$、$T=5000$，重复 10 次；比较 DF-OGD、DF-FTPL、预测聚焦 PF-OGD 和 online SPO。Figure 1 显示，两种 DFL 方法的平均累计决策成本更低，但预测 MSE 更高，正好说明“预测更准”与“决策更好”并不等价。Figure 3 的非线性扫描显示：接近线性可实现情形时 PFL 更有利，misspecification 增强后 DFL 逐渐占优。Figure 4 在 $K=80$ 时仍呈现类似趋势。

Figure 2 只是复现 Mandi et al. (2024) 的二维概念图，用于解释决策边界，不是本文的新实验结果。

### 8. 应该如何理解论文的边界？

- 理论依赖 H1、H2 和 $\xi$-近似 oracle；这些不是免费得到的条件。
- 若内层线性决策本身只能做到加性误差 $\kappa$，遗憾界整体会增加 $\kappa$。
- 实验只覆盖合成数据和选择单个物品的单纯形结构，没有验证一般多面体上的广泛应用。
- 图中没有直接测量理论遗憾率、H2、$\xi$ 或 $P_T$。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Online Decision-Focused Learning

### Paper summary

Online Decision-Focused Learning extends decision-focused learning (DFL) from fixed i.i.d. batches to sequential environments where covariates, true cost functions, and their distributions may change over time. At each round, a predictor estimates an unknown cost vector, a downstream linear program over a bounded polytope converts that prediction into an action, and the true cost is revealed only afterward. Training directly on the downstream decision cost creates a bilevel, generally non-convex objective whose gradients are zero or undefined because the inner linear program switches between polytope vertices.

The paper resolves two different obstacles in two stages. First, it regularizes the inner decision problem, using a log barrier for a general bounded non-degenerate polytope or negative entropy for a simplex. This produces a differentiable soft decision $\widetilde w_t$ and surrogate loss $\widetilde f_t$, at the cost of a smoothing-versus-bias trade-off controlled by $\alpha_t$. Second, it assumes access to an $\xi$-approximate offline oracle and introduces two non-convex online algorithms with distinct mechanisms:

- **DF-FTPL** perturbs the cumulative regularized objective with coordinate-wise exponential noise and oracle-minimizes all past surrogate losses. It is analyzed against the best fixed parameter and attains tuned average static regret
  $$
  \widetilde{\mathcal O}(m^{3/4}n^{3/2}T^{-1/4}+\xi).
  $$
- **DF-OGD** oracle-minimizes only the current surrogate to obtain $\vartheta_t$, samples the gradient point uniformly along $[\theta_t,\vartheta_t]$, and takes a projected gradient step. Uniform segment sampling makes the expected gradient inner product equal the exact surrogate-loss difference by the fundamental theorem of calculus; it is not merely unspecified “optimism.” Its tuned average dynamic regret is
  $$
  \widetilde{\mathcal O}\!\left(\mathbb E[\sqrt n(1+P_T)^{1/4}T^{-1/4}]+\xi\right),
  \qquad
  P_T=\sum_{t=1}^{T-1}\|\vartheta_{t+1}-\vartheta_t\|.
  $$

These are different guarantees: static regret compares DF-FTPL with one best fixed predictor, while dynamic regret compares DF-OGD with time-varying conditional-risk minimizers and worsens with their path variation $P_T$. Both results require boundedness/smooth-predictor assumption H1, margin assumption H2, and sufficiently accurate oracle access; they do not remove non-convex optimization difficulty. An additive $\kappa$ error in solving the inner decision problem shifts the regret bounds by $\kappa$.

### Evaluation

The experiments use a synthetic choose-one-item knapsack problem, equivalently a simplex decision set. Costs are nonlinear and non-stationary, covariates are correlated, and the learner uses a misspecified linear predictor. In the main $K=5$, $p=10$, $T=5000$ experiment (10 runs), DF-FTPL and DF-OGD achieve lower average cumulative decision cost than prediction-focused OGD and online SPO, even though their prediction MSE is worse. A 50-run misspecification sweep shows PFL leading closer to the linear/realizable regime and DFL becoming favorable as nonlinearity increases. A $K=80$ experiment preserves the decision-cost advantage.

The evidence is encouraging but limited: all results are synthetic, the feasible set used empirically is the simple choose-one-item simplex rather than a diverse collection of general polytopes, and the figures do not empirically validate the theorem assumptions or regret rates. Figure 2 is a conceptual diagram reproduced from Mandi et al. (2024), not a new result.

### Reproducibility

The appendix states that the experiments were implemented in PyTorch and gives important settings, including $A=45$, $\rho=0.8$, and a DF-OGD oracle approximated by 10 SGD steps at learning rate 0.01 with warm starts. However, an official implementation was **Not found** in the paper, arXiv metadata, or exact-title/arXiv-ID/author-title GitHub searches. There is therefore no code-paper fidelity assessment, runnable example, environment specification, or script-level confirmation of the plotted experiments. This workspace is intentionally `paper-only` and contains no `doc_code.md`.

### Publication metadata

Published as a poster/conference paper at the **International Conference on Learning Representations (ICLR), 2026** (OpenReview `FJhtHBphCt`). The preprint history begins with arXiv submission in 2025: arXiv `2505.13564v3`, DOI `10.48550/arXiv.2505.13564`. The arXiv DOI is not presented as a proceedings DOI.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
