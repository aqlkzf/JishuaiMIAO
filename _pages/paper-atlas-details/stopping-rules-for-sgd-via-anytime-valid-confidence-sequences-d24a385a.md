---
layout: default
permalink: /paper-atlas/stopping-rules-for-sgd-via-anytime-valid-confidence-sequences-d24a385a/
title: "Stopping Rules for SGD via Anytime-Valid Confidence Sequences"
nav: false
wide: true
description: "传统 SGD 理论通常预先固定迭代次数 T，然后回答“运行到 T 时误差多大”。但实际使用者会持续查看训练轨迹，并在指标看起来足够好时停止。把只对固定时刻成立的置信界反复检查，会产生多重检验问题，原有置信水平不再成立。固定预算、肉眼判断平台期或随意设定梯度阈值，也不能控制“过早停止”的概率。"
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
    <h1>Stopping Rules for SGD via Anytime-Valid Confidence Sequences</h1>
    <p>Stopping Rules for Stochastic Gradient Descent via Anytime-Valid Confidence Sequences</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2512.13123" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Stopping Rules for SGD via Anytime-Valid Confidence Sequences">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用随时有效置信序列为 SGD 设计停止规则

### 1. 论文解决什么问题？

传统 SGD 理论通常预先固定迭代次数 $T$，然后回答“运行到 $T$ 时误差多大”。但实际使用者会持续查看训练轨迹，并在指标看起来足够好时停止。把只对固定时刻成立的置信界反复检查，会产生多重检验问题，原有置信水平不再成立。固定预算、肉眼判断平台期或随意设定梯度阈值，也不能控制“过早停止”的概率。

本文的目标是：只根据已经观察到的 SGD 轨迹，在任意时刻都能计算一个统计上有效的性能上界，并在该上界第一次低于容差 $\varepsilon$ 时停止。这个停止时刻可以由数据决定，不必预先指定。

### 2. 基本设置

论文研究投影 SGD：

$$
x_{t+1}=\Pi_{\mathcal X}(x_t-\eta_tg_t).
$$

步长 $\eta_t$ 必须是可预测的，即只能依赖 $t$ 时刻之前的信息；因此固定步长、递减步长以及基于历史轨迹的自适应步长都可以覆盖。随机梯度满足

$$
\mathbb E[g_t\mid\mathcal F_{t-1}]=\nabla f(x_t),
$$

且噪声 $\xi_t=g_t-\nabla f(x_t)$ 在给定历史后为方向条件次高斯。定义

$$
S_t=\sum_{s=1}^t\eta_s,
\qquad
V_t=\sum_{s=1}^t\eta_s^2.
$$

这些是两个分支共享的输入和累计量（`paper.md` 第 41–86 行）。

### 3. 凸与非凸分支不能混为一谈

#### 凸优化

目标量是加权平均次优性

$$
\bar F_t=\frac1{S_t}\sum_{s=1}^t\eta_s\bigl(f(x_s)-f(x^\star)\bigr).
$$

对应的加权平均迭代点 $\bar x_t=S_t^{-1}\sum_s\eta_sx_s$ 满足

$$
f(\bar x_t)-f(x^\star)\leq\bar F_t.
$$

自适应理论界依赖未知的 $\|x_t-x^\star\|$。若希望在线计算，必须事先知道统一距离上界 $R_x$。论文用紧凸可行域的直径提供该上界；紧性只为可观测版本服务，不是自适应定理本身的必要条件。

#### 非凸优化

这里令 $\mathcal X=\mathbb R^d$，并要求 $f$ 非负、可微且 $L$-光滑。目标量变为

$$
\bar G_t=\frac1{S_t}\sum_{s=1}^t\eta_s\|\nabla f(x_s)\|^2.
$$

因为

$$
\min_{1\leq s\leq t}\|\nabla f(x_s)\|^2\leq\bar G_t,
$$

它只证明轨迹中至少有一个点接近一阶驻点；不能证明接近某个指定驻点，更不能证明全局最优。若要把界在线算出来，还要知道真实梯度的统一上界 $\|\nabla f(x_t)\|\leq G$。这不是仅凭已观察到的随机梯度自动得到的条件（第 93–158、345–420 行）。

### 4. 方法流程

```text
给定 alpha、epsilon、步长规则和必要常数
                |
执行 SGD，观察 x_t、g_t、eta_t
                |
累计 S_t、V_t、sum eta_s^2 ||g_s||^2
                |
凸分支：计算 U_t^obs(alpha)，需要 sigma、R_x
非凸分支：计算 W_t^obs(alpha)，需要 sigma、L、G、f(x_1)
                |
当前上界 <= epsilon？ -- 否 --> 继续迭代
          |
         是
          |
停止并输出 tau_epsilon 及相应的最优性/驻点性证书
```

### 5. 可观测置信序列

#### 凸情形

令

$$
\widetilde\Sigma_t^2=\sigma^2R_x^2V_t,
\qquad
\widetilde\Sigma_{t,\mathrm{eff}}^2=max\!\left\{\widetilde\Sigma_t^2,2\left(\log\frac2\alpha+1\right)\right\}.
$$

在线可计算的上界是

$$
U_t^{\mathrm{obs}}(\alpha)=\frac{1}{2S_t}\left[
7\sqrt{\widetilde\Sigma_{t,\mathrm{eff}}^2\left(\log\frac2\alpha+\log\log(\mathrm e+\widetilde\Sigma_{t,\mathrm{eff}}^2)\right)}
+R_x^2+\sum_{s=1}^t\eta_s^2\|g_s\|^2
\right].
$$

它以至少 $1-\alpha$ 的概率同时对所有 $t$ 满足 $\bar F_t\leq U_t^{\mathrm{obs}}(\alpha)$。

#### 非凸情形

令

$$
\widetilde\Gamma_t^2=\sigma^2G^2V_t,
\qquad
\widetilde\Gamma_{t,\mathrm{eff}}^2=max\!\left\{\widetilde\Gamma_t^2,2\left(\log\frac2\alpha+1\right)\right\}.
$$

则

$$
W_t^{\mathrm{obs}}(\alpha)=\frac1{S_t}\left[
4\sqrt{\widetilde\Gamma_{t,\mathrm{eff}}^2\left(\log\frac2\alpha+\log\log(\mathrm e+\widetilde\Gamma_{t,\mathrm{eff}}^2)\right)}
+f(x_1)+\frac L2\sum_{s=1}^t\eta_s^2\|g_s\|^2
\right]
$$

以至少 $1-\alpha$ 的概率同时控制所有 $t$ 的 $\bar G_t$（第 236–299、345–420 行）。

### 6. 为什么可以“边看边停”？

证明先把优化误差拆成可望远镜求和的确定性部分与鞅噪声部分。条件次高斯假设为每个固定 $\lambda$ 产生一个非负指数超鞅。问题在于：若观察数据后再选择当时最优的 $\lambda$，这个数据依赖选择会破坏超鞅结构，不能直接使用 Ville 不等式。

论文预先固定几何网格和权重

$$
\lambda_k=\mathrm e^{-k/2},
\qquad
w_k=\frac{6}{\pi^2(k+1)^2},
$$

再对整族超鞅做混合。混合后仍是初值为 1 的非负超鞅，Ville 不等式一次性控制它在所有时间的越界概率。几何网格保证对任意实际方差尺度，总有一个 $\lambda_k$ 接近事后最优尺度；代价是边界中的 $\log\log$ 修正项。凸证明从投影距离递推出发，非凸证明从 $L$-光滑下降不等式出发，但二者使用相同的“超鞅混合 + Ville”核心（第 719–1429 行）。

### 7. 精确停止规则与含义

凸情形采用

$$
\tau_\varepsilon=\inf\{t\geq1:U_t^{\mathrm{obs}}(\alpha)\leq\varepsilon\}.
$$

论文证明

$$
\mathbb P\!\left(\{\tau_\varepsilon<\infty\}\cap
\{f(\bar x_{\tau_\varepsilon})-f(x^\star)>\varepsilon\}\right)\leq\alpha.
$$

因此，只要规则触发，错误宣称达到 $\varepsilon$ 精度的概率不超过 $\alpha$。非凸情形把 $U_t^{\mathrm{obs}}$ 换成 $W_t^{\mathrm{obs}}$，并把结论解释为轨迹中最小平方梯度范数不超过 $\varepsilon$。保证来自对所有时间同时成立的事件，所以任意数据依赖停止不会再额外消耗置信水平（第 541–597 行）。

### 8. 终止与复杂度

速率分析额外使用条件二阶矩上界 $\mathbb E[\|g_t\|^2\mid\mathcal F_{t-1}]\leq M^2$。

- 对 $\sum_t\eta_t=\infty$、$\sum_t\eta_t^2<\infty$ 的随机逼近步长，证书在期望和几乎处处意义下按 $O(1/S_t)$ 衰减，停止时间几乎必然有限。
- 对 $\eta_t=\eta_0t^{-1/2}$，证书按 $O(\log t/\sqrt t)$ 衰减；在论文规定的有界梯度条件下，
  $$
  \mathbb E[\tau_\varepsilon]=O\!\left(\varepsilon^{-2}\log^2\frac1\varepsilon\right).
  $$
- 对 $t^{-\gamma}$、$\gamma\in(1/2,1)$，自然的期望复杂度尺度需要 $1/(1-\gamma)$ 阶矩；当 $\gamma\to1$ 时，证明常数会迅速恶化。若随机梯度几乎处处有界，则可获得更直接的路径式上界。

平方根步长中的对数因子来自 $V_t\asymp\log t$ 及其反函数，而不是“随时有效”本身（第 423–509、600–706 行）。

### 9. 实际使用边界

论文完整给出了数学公式和阈值判断，但没有官方实现、伪代码或数值示例，也没有说明如何从数据可靠估计 $\sigma$、$R_x$、$G$ 和 $L$。全文没有实验、数据集、基线、评价指标、数值结果或图。因此本文证明的是理论有效性和渐近停止复杂度，而不是证书在真实训练任务上足够紧或比现有启发式规则更省计算。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Stopping Rules for Stochastic Gradient Descent via Anytime-Valid Confidence Sequences

### Problem

Classical SGD theory usually answers a fixed-horizon question: after a prespecified number of iterations, how accurate is the result? Repeatedly inspecting such fixed-time bounds and stopping when they look favorable invalidates their nominal error control. Common alternatives—fixed budgets, apparent plateaus, and ad hoc gradient thresholds—do not quantify the probability of premature certification (`paper.md` lines 14–40).

### Proposed framework

Aolaritei and Jordan formulate stopping as sequential inference. For projected SGD with predictable, possibly data-dependent stepsizes and conditionally unbiased sub-Gaussian stochastic gradients, they construct confidence sequences that upper-bound a performance process simultaneously for every $t\geq1$ with probability at least $1-\alpha$.

- In the convex setting, the target is weighted average suboptimality $\bar F_t$. The adaptive certificate depends on distances to an unknown optimizer; a fully observable version replaces them with a known trajectory-distance bound $R_x$, supplied by a compact convex feasible set of diameter $R_x$.
- In the unconstrained nonconvex setting, the target is weighted average squared-gradient stationarity $\bar G_t$. The objective must be nonnegative and $L$-smooth. The adaptive certificate involves true gradient norms; a fully observable version additionally assumes a known almost-sure bound $\|\nabla f(x_t)\|\leq G$.

Both observable bounds use only fixed problem/noise constants, predictable stepsizes, and accumulated observed stochastic-gradient norms once those constants are supplied (`paper.md` lines 41–158 and 228–420).

### Key idea and stopping guarantee

The proofs reduce SGD progress to a martingale term plus telescoping optimization terms. Conditional sub-Gaussianity yields exponential nonnegative supermartingales. A countable mixture over the fixed geometric grid $\lambda_k=\mathrm e^{-k/2}$ remains a supermartingale, and Ville's inequality controls its boundary crossing over all times. This avoids the invalid step of selecting the best $\lambda$ after observing the trajectory and produces the iterated-log variance correction (`paper.md` lines 719–1270).

The operational rule is exact and simple:

$$
\tau_\varepsilon=\inf\{t\geq1:U_t^{\mathrm{obs}}(\alpha)\leq\varepsilon\}
$$

in the convex case, with $W_t^{\mathrm{obs}}$ substituted in the nonconvex case. If it triggers, the probability that the returned convex weighted iterate is worse than $\varepsilon$-optimal is at most $\alpha$. The nonconvex analogue certifies that the smallest squared true-gradient norm visited by the stopping time is at most $\varepsilon$; it does not certify global optimality (`paper.md` lines 541–597).

### Theoretical evaluation and rates

The paper contains no empirical evaluation. Its evidence consists of theorem statements and proofs. Under a conditional second-moment bound, square-summable stochastic-approximation stepsizes yield observable certificate decay $O(1/S_t)$ in expectation and almost surely. For $\eta_t=\eta_0t^{-1/2}$, the decay is $O(\log t/\sqrt t)$. With the stated bounded-gradient assumption, the corresponding expected stopping time is

$$
\mathbb E[\tau_\varepsilon]=O\!\left(\varepsilon^{-2}\log^2\frac1\varepsilon\right).
$$

The logarithm here is attributed to the horizon-free square-root stepsize schedule through $V_t\asymp\log t$, not to optional-stopping validity. For polynomial SA schedules $t^{-\gamma}$ with $\gamma\in(1/2,1)$, natural expected rates require increasingly high moments and have fragile constants as $\gamma$ approaches one (`paper.md` lines 423–509 and 600–706).

### Reproducibility and limitations

Reproducibility rating: **2/5 (theory specified, implementation absent)**.

The mathematical construction, assumptions, boundaries, and stopping threshold are explicit enough to reimplement symbolically. However, no verified official code, supplement, pseudocode, runnable example, experiment, dataset, baseline, metric, numerical result, or figure is available. Practical use requires known or defensible values for $\sigma$ and, depending on the branch, $R_x$ or $(L,G,f(x_1))$; the paper does not provide a data-driven calibration procedure for these constants. The certificates concern weighted suboptimality or weighted stationarity rather than the last iterate, validation performance, or nonconvex global optimality.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
