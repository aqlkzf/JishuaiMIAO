---
layout: default
permalink: /paper-atlas/blackwell-approachability-gradient-equilibrium-equivalent-64f6c1df/
title: "Blackwell_Approachability_Gradient_Equilibrium_Equivalent"
nav: false
description: "这篇论文证明：梯度均衡（gradient equilibrium, GEQ）与 Blackwell 可达性（Blackwell approachability, BA）虽然优化目标写法不同，但作为在线学习的“算法黑盒”具有同等能力。任意一个 BA 问题都能调用 GEQ oracle 来解；任意一个 GEQ 问题也能调用 BA oracle 来解；两边都只需每轮一次 oracle 查询，并保留原 oracle 的渐近误差阶。"
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
      <span>Proceedings of Machine Learning Research (COLT) · 2026</span>
    </div>
    <h1>Blackwell_Approachability_Gradient_Equilibrium_Equivalent</h1>
    <p>Blackwell Approachability and Gradient Equilibrium are Equivalent</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2606.27315" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Blackwell 可达性与梯度均衡为何等价

### 一句话结论

这篇论文证明：梯度均衡（gradient equilibrium, GEQ）与 Blackwell 可达性（Blackwell approachability, BA）虽然优化目标写法不同，但作为在线学习的“算法黑盒”具有同等能力。任意一个 BA 问题都能调用 GEQ oracle 来解；任意一个 GEQ 问题也能调用 BA oracle 来解；两边都只需每轮一次 oracle 查询，并保留原 oracle 的渐近误差阶。

### 1. 论文要解决什么问题？

GEQ 由 Angelopoulos 等人在 JMLR 2025 提出。它把离线优化的一阶驻点条件推广到在线环境：学习器依次选择 $\theta_t$，环境依次给出向量场 $g_t$，目标是让平均向量趋于零。无约束时，

$$
\left\|\frac{1}{T}\sum_{t=1}^{T}g_t(\theta_t)\right\|_2\to0.
$$

这与经典遗憾最小化很像，但已有工作证明 GEQ error 与 regret 互不推出：同一决策序列可以 GEQ 很小而 regret 不消失，也可以反过来。此外，GEQ 常依赖“恢复性”（restorativity），遗憾最小化常依赖凸性；两类条件也互不包含。因此，仅凭目标函数外形无法判断 GEQ 在在线学习理论中的位置。

作者转而问一个更强、更有用的问题：**不要求两种误差对同一序列相等，而是问一个框架的算法能否作为黑盒去解决另一个框架的问题。**

### 2. 两个框架分别在做什么？

#### 2.1 Blackwell 可达性

BA 问题写成 $(\mathbb{R}^{d},A,B,f,S)$。学习器选 $a_t\in A$，环境选 $b_t\in B$，产生向量收益 $f(a_t,b_t)\in\mathbb{R}^{d}$。学习器希望

$$
d\left(\frac{1}{T}\sum_{t=1}^{T}f(a_t,b_t),S\right)\to0,
$$

也就是平均收益靠近目标集合 $S$。Blackwell 条件从几何上要求：对每个可能把当前平均值与 $S$ 分开的方向，学习器都能选一个动作，使下一步收益不继续朝错误半空间移动。

#### 2.2 梯度均衡

一般的 GEQ 问题写成 $(\mathbb{R}^{d},\Theta,\mathcal{G})$。若 $\Theta$ 有约束，正确的一阶残差还要包括法锥向量 $n_t\in N_{\Theta}(\theta_t)$：

$$
\left\|\frac{1}{T}\sum_{t=1}^{T}\bigl(g_t(\theta_t)+n_t\bigr)\right\|_2\to0.
$$

无约束时 $N_{\mathbb{R}^{d}}(\theta)=\{0\}$，就退化为平均梯度趋零。论文假设向量场有界，并具有恢复性：当 $\|\theta\|_2\ge h$ 时，$-g(\theta)$ 不会继续把点推离原点，形式为

$$
\langle\theta,-g(\theta)\rangle\le0.
$$

### 3. 核心几何观察

整篇论文的两条归约都来自一个恒等式：

$$
\left\|\frac{1}{T}\sum_t g_t(\theta_t)\right\|_2
=\operatorname{dist}\left(-\frac{1}{T}\sum_t g_t(\theta_t),\{0\}\right)
=\max_{\theta\in B_2(1)}\left\langle-\frac{1}{T}\sum_t g_t(\theta_t),\theta\right\rangle.
$$

- 第一种写法说明：GEQ 就像把负梯度当作向量收益、把原点当作目标集合的 BA。
- 第二种写法说明：GEQ 误差可以由一个“分离方向”见证；这恰好是 BA 算法使用的几何对象。

### 4. 方向 A：用 BA 算法解决 GEQ

给定无约束 GEQ，构造 BA：

$$
A=\mathbb{R}^{d},\quad B=\mathcal{G},\quad f(\theta,g)=-g(\theta),\quad S=\{0\}.
$$

对应关系很直接：BA 的学习器动作就是 GEQ 的决策 $\theta$，环境动作就是当前向量场 $g$，向量收益就是 $-g(\theta)$。

难点是如何满足 Blackwell 半空间条件。若知道恢复半径 $h$，面对方向 $u$ 可以选

$$
\theta=h\frac{u}{\|u\|_2},
$$

恢复性便保证 $\langle u,-g(\theta)\rangle\le0$。但算法不假设知道 $h$，所以论文使用随时间增长的尺度

$$
\theta_t=\alpha(t)\frac{u_t}{\|u_t\|_2}.
$$

只要 $\alpha$ 单调增大，违反半空间条件的轮数最多为 $m\le\lceil\alpha^{-1}(h)\rceil$。稳健 BA oracle 可以吸收这有限次错误，得到

$$
\left\|\frac{1}{T}\sum_t g_t(\theta_t)\right\|_2
\le C_m\frac{\overline{\mathbf{BA}}\operatorname{Err}(L,T)}{T}.
$$

这不仅给出归约，还说明 Blackwell 条件是 GEQ 可解的必要充分条件；恢复性则是容易用于构造算法的充分条件。

### 5. 方向 B：用 GEQ 算法解决 BA

先考虑目标 $S$ 是凸锥。算法在极锥 $S^{\circ}$ 中使用方向 $u_t$，再通过 BA 的 halfspace oracle 映射成实际动作 $a_t$。关键是 GEQ 定义允许出现法锥向量 $n_t$。对于锥，$n_t\in N_{S^{\circ}}(u_t)$ 会落在 $S$ 中，因此 $\frac1T\sum_t n_t$ 可以看成一个已经位于目标集合内的“合成收益轨迹”。

GEQ 保证真实收益平均值与这个合成轨迹越来越接近，于是

$$
d\left(\frac{1}{T}\sum_t f(a_t,b_t),S\right)
\le \left\|\frac{1}{T}\sum_t \bar g_t(x_t)\right\|_2.
$$

直觉上，GEQ 并非直接把真实收益压进 $S$，而是构造一个位于 $S$ 内、且与真实轨迹无法区分的参照轨迹。

### 6. 如何去掉“有约束 GEQ oracle”？

作者还需把 $S^{\circ}$ 上的有约束 GEQ 变成普通的无约束 GEQ。做法是把无约束点 $x$ 投影到 $\Theta$，并给原向量场加上放大的投影残差：

$$
\bar g_g(x)=g(\Pi_{\Theta}(x))+n_g(x),
$$

$$
n_g(x)=
\begin{cases}
2\|g(\Pi_{\Theta}(x))\|_2\dfrac{x-\Pi_{\Theta}(x)}{\|x-\Pi_{\Theta}(x)\|_2},&x\ne\Pi_{\Theta}(x),\\
0,&\text{否则}.
\end{cases}
$$

这个修正同时完成两件事：它让新向量场具有恢复性；它又恰好属于投影点的法锥，因此可充当有约束 GEQ 所需的 $n_t$。原来的 $(L,h)$ 常数只变成 $(3L,2h)$。若 BA 目标不是锥，再用标准的一维升维把它转成锥即可。

### 7. 完整流程图

```text
GEQ -> BA:
向量场 g_t
  -> 收益 -g_t(theta), 目标 {0}
  -> BA oracle 给分离方向 u_t
  -> 放大 u_t 得到 GEQ 决策 theta_t
  -> 平均梯度误差继承 BA 误差率

BA -> GEQ:
BA 目标 S
  -> 必要时升维为锥
  -> 在极锥上构造 halfspace 响应
  -> 投影 + 残差，得到无约束恢复性向量场
  -> GEQ oracle 产生真实/合成轨迹接近保证
  -> 平均收益接近 S
```

### 8. 与遗憾最小化的关系

把本文归约与已有 BA/RM 归约组合，可以双向转换 GEQ 与 regret minimization：

- 乐观 regret 算法可导出依赖预测误差的 GEQ 界；梯度越可预测，GEQ error 越小。
- 强自适应 regret 算法可导出对所有时间子区间同时成立的 GEQ 界。
- 反方向可用 GEQ 的常数步长 OGD 构造最优 $O(BLT^{-1/2})$ regret 算法，而且步长可固定为 $\eta=1$，无需事先知道 $L$ 或 $T$。

需要注意：这证明的是**算法能力等价**，并没有否定“同一决策序列上的 GEQ error 与 regret 互不推出”。

### 9. 如何理解这篇论文的贡献边界？

这是一篇理论论文，没有数据集、训练实验或经验基线。其证据是定义、构造、定理和证明。唯一的图展示新得到的 GEQ $\leftrightarrow$ BA 蓝色双向归约，以及通过已有 BA $\leftrightarrow$ RM/校准归约形成的更大等价网络。

可复现方面，论文给出了足够完整的数学算法，但 arXiv 正文、GitHub 链接侧车和全文搜索均未找到公开实现。因此，实际落地仍需为具体问题实现投影与 halfspace oracle；这些 oracle 的通用计算复杂度在论文中 **Not found**（已检查第 3-5 节及附录）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Blackwell Approachability and Gradient Equilibrium are Equivalent

### Outcome

Lee, Haghtalab, Jordan, and Tibshirani prove that gradient equilibrium (GEQ) and Blackwell approachability (BA) are algorithmically equivalent: a black-box oracle for either framework can solve the other using one oracle query per round, while preserving a sublinear cumulative error rate up to constants. The paper appeared at COLT 2026 (PMLR 336) and is available as arXiv:2606.27315.

### Problem

GEQ generalizes offline first-order stationarity to online learning by asking the time-average of observed vector fields (plus normal-cone corrections for constrained decisions) to converge to zero. BA asks a learner in a repeated vector-payoff game to drive its average payoff toward a target set. Before this work, GEQ was known to resemble regret minimization but differed in essential ways: GEQ error and regret are incomparable objectives; restorative vector fields and convex losses are incomparable condition classes; and canonical OGD uses different step-size logic in the two frameworks (paper lines 28-50). The precise place of GEQ among classical online-learning frameworks was therefore unresolved.

### Main construction

The GEQ-to-BA direction encodes $-g(\theta)$ as the vector payoff and uses the singleton target $\{0\}$. Restorativity supplies Blackwell halfspace responses, while an increasing scaling rule handles an unknown restorativity radius. This yields GEQ error controlled by the BA oracle's rate (Theorem 3, lines 394-414).

The BA-to-GEQ direction first handles conic targets. It uses polar-cone directions, a halfspace oracle, and normal-cone vectors produced through GEQ to build a synthetic payoff transcript lying in the target. A projection-residual transformation converts constrained GEQ to unconstrained GEQ. General convex BA targets are then handled by a one-dimensional conic lift. Theorem 9 bounds approachability distance by the GEQ residual without asymptotic rate loss (lines 724-789).

### Consequences

Together with established BA equivalences, the reductions imply that GEQ, regret minimization, and calibration are equally powerful algorithmic primitives, despite their different native objectives. Concrete compositions transfer optimistic and strongly adaptive regret guarantees to GEQ (Corollaries 11-12), and convert fixed-step-size GEQ OGD into an optimal-rate regret algorithm that does not need the loss-norm bound $L$ or horizon $T$ for step-size tuning (Corollary 13 and Remark 9).

### Evidence and evaluation

This is a theoretical paper. Evaluation consists of formal reductions, rate bounds, and recovery of known results rather than datasets or experiments. The only figure is an equivalence diagram; direct inspection confirms that it distinguishes the paper's two new GEQ/BA arrows from previously known BA/RM and BA/calibration connections.

### Reproducibility

**Rating: 3/5.** The mathematical setup, constructions, pseudocode, and proofs are detailed enough to reimplement the reductions for an application with explicit projection and halfspace oracles. However, no public implementation or supplementary code was found in the arXiv source or full-paper search, and concrete runtime depends on problem-specific oracle costs that are not universally specified. The workspace is therefore `paper-only`; `doc_code.md` and CodeGraph are intentionally skipped.

### Limitations

- The cleanest BA-to-GEQ construction works first for cones; general targets require an extra-dimensional conic lift.
- The reductions assume access to elementary projections and valid halfspace responses whose implementation cost may be nontrivial in a concrete application.
- The results establish oracle equivalence, not equality of GEQ error and regret on a fixed action sequence; those objectives remain semantically incomparable.
- Calibration follows through prior reductions and is not developed in detail in this paper (paper lines 970-976).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
