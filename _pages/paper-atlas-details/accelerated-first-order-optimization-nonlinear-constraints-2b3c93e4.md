---
layout: default
permalink: /paper-atlas/accelerated-first-order-optimization-nonlinear-constraints-2b3c93e4/
title: "Accelerated_First_Order_Optimization_Nonlinear_Constraints"
nav: false
wide: true
description: "论文考虑 投影梯度法每一步都要把新位置投影回完整可行域；Frank–Wolfe 则要在完整可行域上解线性优化。当约束数量很多、结构复杂，甚至可行域非凸时，这两个操作可能很贵或没有闭式解。本文希望只用梯度和一个局部凸子问题，同时保留动量带来的加速效果。 在当前位置 x，作者构造 它是由线性半空间组成的局部速度集合。即使原始可行域是非凸的，固定 x 后的 V\\alpha(x) 仍是凸集。"
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
      <span>Mathematical Programming · 2025</span>
    </div>
    <h1>Accelerated_First_Order_Optimization_Nonlinear_Constraints</h1>
    <p>Accelerated First-Order Optimization under Nonlinear Constraints</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1007/s10107-025-02224-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Accelerated_First_Order_Optimization_Nonlinear_Constraints">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 非线性约束下的加速一阶优化：方法详解

### 论文解决什么问题？

论文考虑

$$
\min_x f(x),\qquad \text{s.t. }g(x)\geq0.
$$

投影梯度法每一步都要把新位置投影回完整可行域；Frank–Wolfe 则要在完整可行域上解线性优化。当约束数量很多、结构复杂，甚至可行域非凸时，这两个操作可能很贵或没有闭式解。本文希望只用梯度和一个局部凸子问题，同时保留动量带来的加速效果。

### 核心思想：约束速度，而不是直接约束位置

在当前位置 $x$，作者构造

$$
V_\alpha(x)=\{v:\nabla g_i(x)^\top v+\alpha g_i(x)\geq0\}.
$$

它是由线性半空间组成的局部速度集合。即使原始可行域是非凸的，固定 $x$ 后的 $V_\alpha(x)$ 仍是凸集。$\alpha g_i(x)$ 是“恢复项”：若当前违反约束，允许的速度必须把轨迹推回可行域；连续时间下违反量至少按 $e^{-\alpha t}$ 衰减。

论文给出两种版本：

- **仅激活/违反约束**：只加入 $g_i(x)\leq0$ 的约束，局部子问题通常更稀疏；可证明非凸情形收敛到驻点，但离散时间的完整加速速率没有证明。
- **全部约束**：每步加入所有约束，计算量更大，但可得到清晰的离散时间非渐近加速界。

### 为什么需要“碰撞”模型？

无约束动量系统可写成

$$
\dot u+2\delta u+\nabla f(x+\beta u)=0,
$$

其中 $u$ 是速度/动量。当轨迹突然撞到约束边界时，为避免继续向不可行方向运动，$u$ 可能必须瞬间跳变。因此作者借用非光滑力学中的测度微分包含：平时按加速梯度流运动，撞到边界时由约束冲量修正动量。恢复系数 $\epsilon$ 控制碰撞前后约束方向速度的关系；$\epsilon=0$ 对应非弹性碰撞。

### 离散算法

每一步的计算流程是：

```text
(x_k, u_k)
   │
   ├─ 计算带阻尼、look-ahead 梯度的无约束动量目标 r_k
   ├─ 选择 active-only 或 full constraint 集合
   ├─ 解局部凸二次问题：寻找最接近 r_k 的可允许速度 u_{k+1}
   └─ 用新速度更新位置 x_{k+1}=x_k+T_k u_{k+1}
```

active-only 的核心更新为

$$
u_{k+1}=\arg\min_v\frac12\|v-r_k\|^2
$$

并满足每个当前违反约束的线性速度不等式。这里投影的是“动量目标”到局部半空间，而不是把“位置”投影到完整可行域。没有激活约束时，算法退化为标准 heavy-ball 或 Nesterov 型更新。

full-constraint 版本在 $y_k=x_k+\beta u_k$ 处同时计算目标梯度和约束梯度，并加入一个约束曲率修正。这个设计主要是为了让离散 Lyapunov 分析闭合；作者也明确说，修正项可能只是证明造成的技术产物。

### 理论保证

- 连续时间：在光滑性、约束资格条件以及凸性或足够阻尼条件下，轨迹收敛到驻点；凸情形可达 $\mathcal O(1/t^2)$，强凸情形可达指数加速率。
- 离散 active-only：采用 $T_k=T_0/k^s$、$s\in(1/2,1)$，再加 Mangasarian–Fromovitz 约束资格、动量有界、驻点孤立等条件，可证明 $x_k$ 收敛到驻点且 $u_k\to0$。
- 离散 full-constraint：若 $f$ 强凸、$g$ 光滑且凹，Lagrangian 条件数为 $\kappa_l$，迭代复杂度为 $\mathcal O(\sqrt{\kappa_l}\log(1/\varepsilon))$。未知光滑常数或仅凸情形有相应的近似加速结果。

这些结果不能混用：非凸部分保证的是驻点，不是全局最优；便宜的 active-only 版本也没有获得 full-constraint 版本的完整离散加速定理。

### 稀疏回归与压缩感知

实验考虑 $\|x\|_p^p\leq\nu$，包括 $p<1$ 的非凸稀疏约束。作者引入 $\bar x$ 表示 $|x|$，并用可微的 $(\bar x)^p_\Delta$ 平滑零点附近的 $x^p$。局部速度子问题随后化成加权单纯形投影，通过排序和一个对偶阈值求解，最坏复杂度为 $\mathcal O(n\log n)$，而且不依赖 $p$ 是否小于 1。

在 1,000 维合成压缩感知和 131,072 变量的图像重建中，$p=1$ 时本文算法与加速投影梯度的目标下降相近；$p=0.8$ 时仍能直接处理非凸约束，并在图中表现出约 $1/k^2$ 的经验趋势和更少的重建伪影。但这个非凸 $1/k^2$ 只是实验观察，不是定理。

### 复现边界

正式 Springer 论文给出了完整公式、证明和伪代码，Appendix A–D 已包含在正文中；没有发现单独补充文件。对论文正文、Springer 页面、arXiv、两位作者主页、GitHub 和精确题名网页检索后，官方实现仍为 **Not found**。因此可以据伪代码重新实现，但不能声称已有官方代码可直接复现实验；随机种子和若干实验细节也需要自行补齐。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Accelerated First-Order Optimization under Nonlinear Constraints

### Paper summary

This paper develops accelerated first-order algorithms for smooth nonlinear constrained optimization without projecting positions onto the full feasible set. Its key move is to impose linearized constraints on velocity or momentum: at each step, the unconstrained heavy-ball/Nesterov momentum update is projected onto a local polyhedron $V_\alpha(x)$. Because that local subproblem is convex even when the original feasible set is nonconvex, the approach can treat constraints such as $\ell^p$ sparsity balls with $p<1$ that are awkward for ordinary projected-gradient methods.

The continuous-time formulation is a measure differential inclusion. Smooth motion follows a damped accelerated flow, while newly activated constraints cause impact-like momentum jumps governed by a complementarity law. Discretization yields two variants: Eq. (8) includes only violated constraints and is computationally sparse; Eq. (22) includes all constraints and adds a curvature correction that enables a clean accelerated discrete-time proof.

The theory separates what is guaranteed in each regime. The active-only dynamics converge to stationary points under smoothness, constraint qualification, damping/convexity, boundedness, and diminishing-step assumptions, including nonconvex problems. In convex settings, the continuous flow attains $\mathcal O(1/t^2)$ or strongly convex exponential rates. For the all-constraint discrete algorithm, the paper proves $\mathcal O(\sqrt{\kappa_l}\log(1/\varepsilon))$ iterations for smooth strongly convex problems, plus near-$1/\sqrt\varepsilon$ and $\mathcal O(\log^2N/N^2)$ variants when smoothness is unknown or strong convexity is introduced by regularization.

### Evaluation

The numerical studies cover a one-dimensional impact example, synthetic compressed sensing with 1,000 variables, and wavelet-domain image reconstruction with 131,072 variables and 131,073 constraints. For $p=1$, the proposed algorithms match accelerated projected gradient in objective decrease and outperform ordinary gradient descent. For $p=0.8$, they directly solve the nonconvex sparsity-constrained problem; the figures show approximately $1/k^2$ empirical decrease and fewer image artifacts. The specialized local subproblem reduces to a weighted-simplex projection with $\mathcal O(n\log n)$ worst-case complexity.

### Reproducibility and limitations

The Springer version of record contains detailed equations, proofs, pseudocode, and integrated Appendices A–D, but no separate supplement was found. An official code repository is **Not found** after checking the VOR/article page, arXiv, both author pages, GitHub, and exact-title web searches; therefore this workspace is `paper-only`. Reproducing the experiments requires an independent implementation. The nonconvex claims concern convergence to stationary points, not global optima, and the plotted nonconvex $1/k^2$ behavior is empirical. The stronger discrete accelerated theorem applies to the all-constraint variant, not the cheaper active-only algorithm.

Bibliographically, the article was published online on 21 April 2025, which explains its placement in Jordan's 2025 list; Springer assigns it to *Mathematical Programming* volume 215, pages 407–452 (2026).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
