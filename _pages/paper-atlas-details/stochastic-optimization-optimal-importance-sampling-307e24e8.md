---
layout: default
permalink: /paper-atlas/stochastic-optimization-optimal-importance-sampling-307e24e8/
title: "Stochastic_Optimization_Optimal_Importance_Sampling"
nav: false
description: "普通随机梯度从原分布 \\mathbb P 采样。若目标主要由罕见事件决定，有信息的样本极少，梯度方差会非常大。重要性采样可以改从 \\mathbb P\\mu 采样并乘似然比 \\ell(x,\\mu)，但最合适的 \\mu 又依赖未知最优决策 \\theta^\\star 及其活跃约束。因此出现循环：不知道 \\theta^\\star 就无法校准采样器；采样器不好又难以学到 \\theta^\\star。"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>Stochastic_Optimization_Optimal_Importance_Sampling</h1>
    <p>Stochastic Optimization with Optimal Importance Sampling</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2504.03560" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Stochastic_Optimization_Optimal_Importance_Sampling">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 随机优化中的最优重要性采样：方法详解

### 论文解决什么问题

普通随机梯度从原分布 $\mathbb P$ 采样。若目标主要由罕见事件决定，有信息的样本极少，梯度方差会非常大。重要性采样可以改从 $\mathbb P_\mu$ 采样并乘似然比 $\ell(x,\mu)$，但最合适的 $\mu$ 又依赖未知最优决策 $\theta^\star$ 及其活跃约束。因此出现循环：不知道 $\theta^\star$ 就无法校准采样器；采样器不好又难以学到 $\theta^\star$。

### 核心思想

论文把采样器校准本身写成另一个随机优化问题：

$$
v(\theta,\mu)=\mathbb E_{X\sim\mathbb P}
[\|P_{A_a^\theta}G(\theta,X)\|^2\ell(X,\mu)].
$$

其中投影 $P_{A_a^\theta}$ 只保留沿当前活跃约束面的梯度分量。若似然比关于 $\mu$ 对数凸且可微，固定 $\theta$ 时 $v$ 对 $\mu$ 是凸的，并有无偏随机梯度

$$
H(\theta,\mu,X)=\|P_{A_a^\theta}G(\theta,X)\|^2\nabla_\mu\ell(X,\mu).
$$

这一结构适用于指数倾斜、对数凹分布的均值平移以及有限混合等采样族。

### 单循环算法

```text
当前 (θ_k, μ_k)
   ├─ 从 P_{μ_k} 采样 → 似然比校正梯度 G_{μ_k} → 更新决策 θ
   └─ 独立从 P 采样 → 方差目标梯度 H          → 更新采样器 μ
                    ↓
       在 Θ × M 上做一次联合 dual averaging
                    ↓
          输出原始迭代与平均迭代 θ̄_n, μ̄_n
```

两部分使用同一个 $\alpha_k=\alpha/k^\gamma$（$1/2<\gamma<1$）序列，在积空间上完成一次约束 Nesterov dual averaging。它不是“先把 $\theta$ 训好再调 $\mu$”，也不需要内层优化或人为设定快慢时间尺度。理论的关键是证明 $\theta$ 尚未收敛造成的校准梯度偏差是可求和扰动。

### 理论保证

1. 在凸性、矩条件和耦合正则条件下，$(\theta_n,\mu_n)$ 几乎必然全局收敛到 $(\theta^\star,\mu^\star)$。
2. 在线性约束和严格互补类条件下，决策与采样参数的活跃/非活跃约束会在有限时间后被正确识别。
3. 平均决策 $\bar\theta_n$ 满足中心极限定理；其渐近协方差等于从一开始就知道 $\mu^\star$ 的 oracle NDA。
4. “最优”是指在选定的重要性采样参数族和相应随机梯度方案中达到最小渐近方差，并非任意分布上的有限样本全局最优。

### 实验说明

当前 arXiv v3 用标准正态分布的 $0.9999$ 分位数做一维实验。约束 $\mu\in[-1.7,1.7]$ 把最优采样参数放在边界。1000 条轨迹显示：$\mu_n$ 最终贴住 $1.7$；随后 $\theta_n$ 的方差快速收缩；burn-in 后，自适应 IS 的缩放误差方差比 projected SGD 和普通 NDA 低多个数量级。八个主图面板均已直接检查。

### 使用边界与复现性

- 需要凸目标、线性约束、可有效采样的参数化 $\mathbb P_\mu$，并能计算 $\ell$ 和 $\nabla_\mu\ell$。
- 收敛、活跃集识别和 CLT 分别依赖有界矩、唯一性/曲率、约束资格、平滑性、受限强凸性和 martingale/Lindeberg 条件。
- 基本算法每次迭代要用两个独立样本；用于降低 $H$ 方差的“二级重要性采样”只被讨论，没有完整展开或实验。
- 原始 v1 只有理论；数值实验由 v3 添加。当前只验证了一维合成问题。
- 未找到官方代码。检索覆盖正文、作者主页、精确标题、arXiv ID、GitHub 和一般网页，因此无法核验随机种子、baseline 参数和绘图实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Stochastic Optimization with Optimal Importance Sampling

### Paper summary

Importance sampling can sharply reduce rare-event gradient noise, but stochastic optimization creates a circular dependency: the best proposal depends on the unknown optimal decision and its active constraints, while efficiently learning that decision depends on having a good proposal. This paper resolves the circle for convex stochastic programs with linear constraints by jointly learning the decision $\theta$ and proposal parameter $\mu$ in a single stochastic-approximation loop (paper lines 273–314 and 482–579).

The key reduction expresses the trace of projected gradient variance as a convex stochastic objective in $\mu$ whenever the likelihood ratio is log-convex. A product-space variant of Nesterov dual averaging then consumes an importance-weighted decision gradient and an independent nominal-sample proposal-calibration gradient, using the same step scale rather than nested optimization or time-scale separation. The paper proves almost-sure global convergence, finite-time identification of active decision/proposal constraints, and a CLT whose decision covariance matches an oracle that knew the best proposal at $\theta^\star$ in advance (lines 613–1155).

### Evidence and evaluation

The current arXiv v3 adds one synthetic rare-event illustration: estimating the $0.9999$ standard-normal quantile with a constrained exponential-tilting proposal. Across 1000 trajectories, adaptive NDA drives $\mu_n$ to its constrained optimum $1.7$, concentrates $\theta_n$ much more quickly than projected SGD or vanilla NDA, and after burn-in produces a plotted scaled-error variance orders of magnitude smaller than the baselines and near the theoretical target (lines 1158–1189). All eight principal figure panels were inspected directly.

### Scope and limitations

The oracle claim is asymptotic and relative to a chosen tractable proposal family; it does not promise finite-sample optimality or the unrestricted zero-variance sampler. The theory assumes convexity, linear constraints, bounded/regular feasible and sampling families, computable likelihood-ratio derivatives, moment bounds, uniqueness/curvature, active-set qualifications and CLT conditions. Empirical evidence is limited to a one-dimensional synthetic quantile problem.

The Jordan list originally pointed to the versionless 2025 preprint. The original v1 is theory-only; the current endpoint resolves to v3, which adds the numerical illustration. No official code repository was found after paper-text, author-page, exact-title, arXiv-ID, GitHub and general web searches, so reproducibility is **2/5 (paper-only)**: the algorithm is mathematically explicit, but the experiment and baselines cannot be rerun from an author-provided implementation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
