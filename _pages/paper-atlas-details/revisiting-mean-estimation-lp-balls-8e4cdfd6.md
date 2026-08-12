---
layout: default
permalink: /paper-atlas/revisiting-mean-estimation-lp-balls-8e4cdfd6/
title: "Revisiting_Mean_Estimation_Lp_Balls"
nav: false
description: "观测模型是 目标是在平方 \\ell2 损失下估计未知均值 \\theta^\\star。这里 p 控制参数空间的几何形状：小 p 对应稀疏或弱稀疏结构，较大的 p 限制坐标整体幅度。论文问的是：把观测点直接投影到 \\ellp 球上的最大似然估计（MLE），能否达到 minimax 最优速率？ 在高斯噪声下，MLE 等价于欧氏投影： 它看起来很自然：利用了参数空间本身的几何结构，是非线性估计器，而且不需要输入噪声强度 \\sigma。"
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
      <span>Machine Learning Algorithm</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>Revisiting_Mean_Estimation_Lp_Balls</h1>
    <p>Revisiting mean estimation over ℓp balls: Is the MLE optimal?</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2506.10354" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## $\ell_p$ 球均值估计中的 MLE：什么时候最优，什么时候失效？

### 论文解决什么问题

观测模型是

$$
Y=\theta^\star+\sigma\xi,\qquad \xi\sim\mathsf N(0,I_d),
\qquad \|\theta^\star\|_p\le r,
$$

目标是在平方 $\ell_2$ 损失下估计未知均值 $\theta^\star$。这里 $p$ 控制参数空间的几何形状：小 $p$ 对应稀疏或弱稀疏结构，较大的 $p$ 限制坐标整体幅度。论文问的是：把观测点直接投影到 $\ell_p$ 球上的最大似然估计（MLE），能否达到 minimax 最优速率？

### MLE 是什么

在高斯噪声下，MLE 等价于欧氏投影：

$$
\widehat\theta^{\mathrm{MLE}}
=\Pi_{rB_p^d}(Y)
=\arg\min_{\vartheta:\|\vartheta\|_p\le r}\|\vartheta-Y\|_2^2.
$$

它看起来很自然：利用了参数空间本身的几何结构，是非线性估计器，而且不需要输入噪声强度 $\sigma$。但论文证明，“非线性”并不自动意味着 minimax 最优。

### 核心机制

当 $1<p<2$ 时，投影可写成逐坐标收缩：

$$
|Y_i|=|\widehat\theta_i|+\lambda^\star|\widehat\theta_i|^{p-1}.
$$

关键是所有坐标共享同一个、由数据决定的 $\lambda^\star$。大量纯噪声坐标会迫使 $\lambda^\star$ 变大；为了在球内同时拟合这些噪声，投影结果会变得比真实稀疏信号更“稠密”，并过度收缩真正的信号坐标。论文用两类球面稀疏向量构造下界：

- 较高的中等噪声区间使用 $\theta^\star=e_1$，MLE 风险可以保持常数量级；
- 较低的中等噪声区间使用

  $$
  \theta^\star=k^{-1/p}(\mathbf1_k,0_{d-k}),
  \quad
  k\asymp\left(\frac1{\sigma^q d}\right)^{(p-1)/(2-p)}\vee1,
  \quad q=\frac p{p-1},
  $$

  得到风险下界 $1\wedge\sigma d^{1/q}$。

因此失效主要来自偏差，而不是方差：对凸对称参数集，投影估计器的方差本身仍然具有 minimax 量级，但远离原点的稀疏球面信号会产生过大的平方偏差。

### 最优性相图

定义

$$
\underline p(d)=1+\frac1{1+\log d}.
$$

对于单位球：

| 条件 | MLE 结论 |
|---|---|
| $p\ge2$，任意噪声 | minimax rate-optimal |
| $0\le p\le\underline p(d)$，任意噪声 | minimax rate-optimal |
| $\underline p(d)<p<2$ 且 $\sigma\le d^{-1/p}$ | 低噪声区间，rate-optimal |
| $\underline p(d)<p<2$ 且 $\sigma\ge(1+\log d)^{-1/2}$ | 高噪声区间，rate-optimal |
| $\underline p(d)<p<2$ 且 $d^{-1/p}<\sigma<(1+\log d)^{-1/2}$ | 通常 rate-suboptimal |

最后一行正是“结构信息有用、必须使用非线性估计器”的中等噪声区间。对于固定 $p\in(1,2)$，若 $\sigma^p d\gg1$ 且 $\sigma^2\log d\ll1$，MLE 风险相对 minimax 风险的比值随维数发散。

### 替代估计器

论文采用经典软阈值估计器作为具体对照：

$$
\widehat\theta^{\mathrm{ST}}
=\arg\min_\vartheta\bigl\{\|\vartheta-Y\|_2^2+2\lambda\|\vartheta\|_1\bigr\},
\qquad
\lambda=\sqrt{2\sigma^2\log(d\sigma^p)}.
$$

它需要知道 $\sigma$，但在相应 $p<2$ 区间能够达到 minimax 速率。Figure 2 的两个数值实验都显示软阈值曲线比 MLE 更快下降。

### 多样本推广

若有 $n$ 个独立样本 $Y_i\sim\mathsf N(\theta^\star,\tau^2I_d)$，样本均值把问题化为有效噪声 $\sigma=\tau/\sqrt n$ 的单样本问题。论文给出一个极高维例子：$p=1+\delta$、$d=e^{\sqrt n}$、$r=\tau=1$ 时，MLE 的竞争比达到

$$
\mathfrak C_n^{\mathrm{MLE}}\asymp n^{(1-\delta)/4},
$$

即相对 minimax 风险出现多项式级差距。

### 如何计算投影

- $p=0$：保留绝对值最大的 $s$ 个坐标；
- $p=\infty$：逐坐标截断到 $[-r,r]$；
- $p\ge1$：凸优化，可用拉格朗日对偶与二分法；
- 论文实验在 $p=1.5$ 时用嵌套 Brent 求根器求解 KKT 方程。

### 阅读边界

这是一篇高维统计理论论文，不是生物信息学论文。结论限定于高斯序列模型、已知 $\ell_p$ 约束和平方误差，不能外推为“所有模型中的 MLE 都不可靠”。论文没有公开官方代码；Appendix B 给出了重建实验所需的主要算法细节，但未提供可执行实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Revisiting mean estimation over $\ell_p$ balls: Is the MLE optimal?

### Paper summary

This theoretical statistics paper asks whether the constrained Gaussian maximum-likelihood estimator is minimax rate-optimal when the unknown mean lies in an $\ell_p$ ball. The observation is $Y=\theta^\star+\sigma\xi$ with $\xi\sim\mathsf N(0,I_d)$ and $\|\theta^\star\|_p\le r$; performance is worst-case squared $\ell_2$ risk. In this Gaussian model the MLE is the Euclidean projection of $Y$ onto the parameter ball. The central message is that “nonlinear” does not imply “minimax optimal”: the projection adapts to the ball geometry and needs no noise-level input, yet it can shrink sparse boundary signals incorrectly (paper lines 13–19, 83–97).

For the unit ball, the MLE is order-optimal for all noise levels when $p\ge2$, when $0\le p\le 1+1/(1+\log d)$, and also in the very-low- or very-high-noise regimes for the remaining $p$. For the intermediate interval

$$
1+\frac{1}{1+\log d}<p<2,
\qquad
d^{-1/p}<\sigma<(1+\log d)^{-1/2},
$$

the paper proves rate-suboptimality for essentially the full regime in which nonlinear estimation is needed. For fixed $p\in(1,2)$, if $\sigma^p d\gg1$ and $\sigma^2\log d\ll1$, the ratio between the MLE risk and the minimax risk diverges with dimension (paper lines 173–257). The conclusions rescale to radius $r$ and to $n$ i.i.d. observations by replacing the effective noise with $\tau/\sqrt n$; one constructed high-dimensional scaling yields a polynomial gap $n^{(1-\delta)/4}$ (paper lines 380–607).

### Why the MLE fails

For $1<p<2$, KKT conditions express the projection coordinatewise as a data-dependent shrinkage rule. Noise-only coordinates force a common Lagrange multiplier $\lambda^\star$ upward. Because the same multiplier acts on signal coordinates, a sparse vector on the boundary is over-shrunk while the estimator spends part of the $\ell_p$ budget fitting many noise coordinates. The authors turn this mechanism into constructive lower bounds at $\theta^\star=e_1$ and at $k$-sparse equal-amplitude boundary vectors. The variance component of the projection remains minimax-order; the failure is attributable to squared bias away from the origin (paper lines 263–378, 631–643).

### Alternative estimator and evidence

Soft thresholding with the theoretically calibrated $\ell_1$ penalty attains the minimax rate in the relevant $p<2$ regime, so it is the concrete alternative to the MLE. Simulations at $p=1.5$ use 50 dimensions between $10^2$ and $10^4$ and 100 Gaussian draws per dimension. Both Figure 2 panels show soft thresholding decaying faster than the projected MLE in the two constructed suboptimality regimes (paper lines 73–79, 140–169, 1707–1729).

### Reproducibility and limitations

- **Source:** arXiv:2506.10354v2, 43 pages, updated 2025-07-01; no archival publication was found. An author page reports a major revision at *The Annals of Statistics*, which is not a publication claim.
- **Code:** no author-official repository or code-availability statement was found after paper, arXiv, author-page, and focused GitHub searches. Appendix B gives enough numerical detail to reconstruct the experiments, including nested Brent solvers, but no implementation is supplied.
- **Evidence:** all three numbered figures were visually inspected; Figure 2 has two separately stored panels. The official PDF was converted with MinerU because arXiv HTML returned 404. The Markdown passes structure, formula, and image-link gates, with a few isolated OCR glyph errors; exact mathematical claims were checked against their surrounding theorem statements.
- **Scope:** results concern Gaussian mean estimation under squared $\ell_2$ loss and $\ell_p$ constraints. They do not establish that MLE is broadly suboptimal outside this model.

**Reproducibility rating: 3/5.** The proofs and experiment recipe are detailed, but executable code and an archival version are absent.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
