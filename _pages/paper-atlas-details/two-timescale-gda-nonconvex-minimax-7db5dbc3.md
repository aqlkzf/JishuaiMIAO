---
layout: default
permalink: /paper-atlas/two-timescale-gda-nonconvex-minimax-7db5dbc3/
title: "Two_Timescale_GDA_Nonconvex_Minimax"
nav: false
description: "论文研究非凸极小极大优化： f 对外层变量 \\mathbf{x} 可以是非凸的，但对内层变量 \\mathbf{y} 要求凹或强凹，\\mathcal{Y} 是有界凸集。普通 GDA 往往给两个变量相同量级的学习率；在超出凸—凹情形后，它可能出现极限环甚至发散。 TTGDA 每轮只做一次下降和一次投影上升： 但选择 \\eta{\\mathbf{x}}^{t}\\ll\\eta{\\mathbf{y}}^{t}。"
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
      <span>Journal of Machine Learning Research · 2025</span>
    </div>
    <h1>Two_Timescale_GDA_Nonconvex_Minimax</h1>
    <p>Two-Timescale Gradient Descent Ascent Algorithms for Nonconvex Minimax Optimization</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2408.11974" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Two_Timescale_GDA_Nonconvex_Minimax">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TTGDA 方法详解

### 论文要解决什么问题？

论文研究非凸极小极大优化：

$$
\min_{\mathbf{x}}\max_{\mathbf{y}\in\mathcal{Y}}f(\mathbf{x},\mathbf{y}).
$$

$f$ 对外层变量 $\mathbf{x}$ 可以是非凸的，但对内层变量 $\mathbf{y}$ 要求凹或强凹，$\mathcal{Y}$ 是有界凸集。普通 GDA 往往给两个变量相同量级的学习率；在超出凸—凹情形后，它可能出现极限环甚至发散。

### 核心思想：让内层走得快、外层走得慢

TTGDA 每轮只做一次下降和一次投影上升：

$$
\mathbf{x}_{t}=\mathbf{x}_{t-1}-\eta_{\mathbf{x}}^{t-1}\mathbf{g}_{\mathbf{x}}^{t-1},
\qquad
\mathbf{y}_{t}=\mathcal{P}_{\mathcal{Y}}\left(\mathbf{y}_{t-1}+\eta_{\mathbf{y}}^{t-1}\mathbf{g}_{\mathbf{y}}^{t-1}\right),
$$

但选择 $\eta_{\mathbf{x}}^{t}\ll\eta_{\mathbf{y}}^{t}$。直观上，$\mathbf{x}$ 缓慢变化，使内层函数 $f(\mathbf{x}_t,\cdot)$ 也缓慢变化；因此 $\mathbf{y}$ 用较大步长做一次上升，就有机会持续跟踪当前内层最大化问题，而不必像嵌套算法那样在每一轮把内层问题解到很高精度。

TTSGDA 是随机版本：用 mini-batch 的无偏随机（次）梯度替换精确（次）梯度，其余流程相同。算法最后从所有访问过的 $\mathbf{x}_t$ 中均匀随机选一个返回，而不是保证最后一步最好。

```text
初值与步长/随机梯度 oracle
          |
          v
  x 小步下降（慢） + y 投影大步上升（快）
          |
        重复 T 轮
          |
          v
从访问过的 x 中随机返回 x_hat
```

### “找到平稳点”具体指什么？

定义 $\Phi(\mathbf{x})=\max_{\mathbf{y}\in\mathcal{Y}}f(\mathbf{x},\mathbf{y})$。

- 光滑且对 $\mathbf{y}$ 强凹时，$\Phi$ 可微，目标是 $\|\nabla\Phi(\mathbf{x})\|\leq\epsilon$。
- 只有凹或目标非光滑时，$\Phi$ 可能不可微，论文使用 Moreau envelope 的梯度作为平稳性指标：$\|\nabla\Phi_{1/(2\rho)}(\mathbf{x})\|\leq\epsilon$。这意味着该点靠近某个具有小 Clarke 次梯度的点。

这不是全局最优保证，也不是一般意义上 $(\mathbf{x},\mathbf{y})$ 的最后迭代收敛保证。

### 理论结果

忽略问题常数和对数项：

| 问题情形 | TTGDA | TTSGDA |
|---|---:|---:|
| 光滑、非凸—强凹 | $O(\kappa^2\epsilon^{-2})$ | $O(\kappa^3\epsilon^{-4})$ |
| 光滑、非凸—凹 | $O(\epsilon^{-6})$ | $O(\epsilon^{-8})$ |
| 非光滑、非凸—强凹 | $\widetilde O(\epsilon^{-6})$ | $\widetilde O(\epsilon^{-6})$ |
| 非光滑、非凸—凹 | $O(\epsilon^{-8})$ | $O(\epsilon^{-8})$ |

强凹时，内层最优解 $\mathbf{y}^{\star}(\mathbf{x})$ 唯一且随 $\mathbf{x}$ Lipschitz 变化，证明可以控制跟踪误差 $\|\mathbf{y}^{\star}(\mathbf{x}_t)-\mathbf{y}_t\|^2$。仅凹时最优解可能不唯一，论文改为控制内层值差 $\Phi(\mathbf{x}_t)-f(\mathbf{x}_t,\mathbf{y}_t)$，再与 Moreau envelope 的下降联系起来。

### 实验告诉了我们什么？

在 6 个 LIBSVM 鲁棒逻辑回归数据集上，TTGDA/TTSGDA 比 GDmax 更快降低梯度范数。在线性生成器 WGAN 上，TTSGDA 优于 Adam 和 RMSprop；但在带 ReLU 的非线性生成器上，vanilla TTSGDA 明显落后于 Adam/RMSprop。这说明“两时间尺度”是重要结构，但不能自动替代自适应优化和正则化。

### 局限与复现状态

理论依赖 $\mathbf{y}$ 方向的凹性以及有界凸集 $\mathcal{Y}$，不覆盖一般非凸—非凹博弈，也没有证明复杂度最优。步长依赖多个未知问题常数和目标精度。论文未提供可确认的作者官方代码；已检查论文、JMLR/arXiv 页面、作者论文页及 GitHub 精确标题/arXiv ID 搜索，因此实验脚本、随机种子、预处理和最终调参配置均记为 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Paper Summary

### Problem and contribution

This JMLR 2025 optimization/ML-theory paper analyzes simple single-loop minimax algorithms for $\min_{\mathbf{x}}\max_{\mathbf{y}\in\mathcal{Y}}f(\mathbf{x},\mathbf{y})$ when $f$ is nonconvex in $\mathbf{x}$ but concave in $\mathbf{y}$. Ordinary equal-rate GDA can cycle or diverge outside convex-concave settings. TTGDA instead makes the outer descent much slower than the inner projected ascent, $\eta_{\mathbf{x}}\ll\eta_{\mathbf{y}}$, so the fast maximization variable can track an inner problem whose objective changes slowly.

The deterministic TTGDA and stochastic TTSGDA algorithms each use one descent/ascent pair per iteration and return a uniformly sampled outer iterate. The paper gives one analysis spanning smooth and nonsmooth, strongly-concave and merely-concave inner problems. Its main conceptual contribution is to control either inner-solution tracking error or the inner value gap without solving a nested inner loop.

### Main theoretical results

For smooth nonconvex-strongly-concave problems, TTGDA and TTSGDA reach an $\epsilon$-stationary point of $\Phi(\mathbf{x})=\max_{\mathbf{y}}f(\mathbf{x},\mathbf{y})$ in $O(\kappa^2\epsilon^{-2})$ and $O(\kappa^3\epsilon^{-4})$ gradient evaluations. For smooth nonconvex-concave problems the corresponding rates are $O(\epsilon^{-6})$ and $O(\epsilon^{-8})$. In nonsmooth weakly-convex settings, Moreau-envelope stationarity replaces ordinary gradient stationarity; the simplified deterministic/stochastic rates are $\widetilde O(\epsilon^{-6})$ under strong concavity and $O(\epsilon^{-8})$ under mere concavity.

These are visited/random-iterate guarantees for $\mathbf{x}$, not last-iterate convergence, global optimality, or a general guarantee for the pair $(\mathbf{x},\mathbf{y})$.

### Evaluation

Figure 1 shows TTGDA/TTSGDA reducing $\|\nabla\Phi\|$ faster than GDmax on six LIBSVM robust-logistic-regression datasets. Figure 2 shows TTSGDA outperforming Adam and RMSprop for a simple WGAN with a linear generator. Figure 3 is an important negative result: with a nonlinear ReLU generator, vanilla TTSGDA is worse than Adam/RMSprop, indicating that timescale separation alone does not replace adaptive optimization and regularization in richer neural models.

### Reproducibility and limitations

The paper states objectives, algorithms, step-size regimes, datasets, comparison methods, and several experimental hyperparameters, but no author-linked official code was found in the paper, JMLR/arXiv pages, authors' publication pages, or exact-title/arXiv-ID GitHub searches. Reproducibility is therefore **2.5/5**: theory is unusually explicit, while empirical scripts, seeds, preprocessing, and exact tuned configurations are unavailable. The analysis also assumes concavity in $\mathbf{y}$ and bounded convex $\mathcal{Y}$, does not establish optimal rates, and does not cover general nonconvex-nonconcave games.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
