---
layout: default
permalink: /paper-atlas/nonasymptotic-confidence-intervals-for-treatment-effects-in-rand-a753e847/
title: "Nonasymptotic Confidence Intervals for Treatment Effects in Randomized Experiments"
nav: false
description: "论文研究二元随机实验中的平均处理效应（ATE）置信区间。它要求的是严格的有限样本覆盖： 而不是只在 n\\to\\infty 时近似成立。 难点来自稀有处理。当处理概率 \\pi 很小时，真正提供处理组信息的有效样本量大约是 n\\pi。经典 CLT 区间的宽度通常是 1/\\sqrt{n\\pi}，但已有的单位级 Hoeffding 推导会得到 1/\\sqrt{n\\pi^2}，额外损失一个 1/\\sqrt\\pi。"
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
      <span>arXiv preprint · 2026</span>
    </div>
    <h1>Nonasymptotic Confidence Intervals for Treatment Effects in Randomized Experiments</h1>
    <p>On Nonasymptotic Confidence Intervals for Treatment Effects in Randomized Experiments</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2601.11744" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 随机实验处理效应的非渐近置信区间：方法详解

### 这篇论文解决什么问题？

论文研究二元随机实验中的平均处理效应（ATE）置信区间。它要求的是严格的有限样本覆盖：

$$
\forall n\in\mathbb N,\qquad \mathbb P(\psi\in C_n)\ge 1-\alpha,
$$

而不是只在 $n\to\infty$ 时近似成立。

难点来自稀有处理。当处理概率 $\pi$ 很小时，真正提供处理组信息的有效样本量大约是 $n\pi$。经典 CLT 区间的宽度通常是 $1/\sqrt{n\pi}$，但已有的单位级 Hoeffding 推导会得到 $1/\sqrt{n\pi^2}$，额外损失一个 $1/\sqrt\pi$。本文证明，这个损失并不是“有限样本保证必然更保守”，而是分析没有充分利用随机化设计的结构。

### 问题设定与适用边界

每个单位 $i$ 有处理指示 $Z_i\in\{0,1\}$、潜在结果 $Y_i(0),Y_i(1)\in[0,1]$，观测结果为

$$
Y_i=Z_iY_i(1)+(1-Z_i)Y_i(0).
$$

论文假定 SUTVA/一致性，并要求随机分配独立于潜在结果。它同时处理：

- 超总体 ATE：$\psi_{\mathrm{i.i.d.}}=\mathbb E[Y(1)-Y(0)]$；
- 设计型有限总体 ATE：$\psi_{\mathrm{DB}}=n^{-1}\sum_i[y_i(1)-y_i(0)]$。

基础估计量是 Horvitz--Thompson 估计量：

$$
\widehat\psi=\frac1n\sum_{i=1}^nY_i\left(\frac{Z_i}{\pi}-\frac{1-Z_i}{1-\pi}\right). \tag{4}
$$

因此，这不是针对观察性数据的“去混杂工具”，也不能在未知或估错 propensity score 时直接照搬。

### 为什么朴素 Hoeffding 界太宽？

单个逆概率加权项的取值范围约为 $[-1/(1-\pi),1/\pi]$。如果把 $n$ 个单位逐个套入 Hoeffding 引理，范围长度是 $O(1/\pi)$，最后自然得到

$$
O\!\left(\frac1{\pi\sqrt n}\right)
=O\!\left(\frac1{\sqrt{n\pi^2}}\right).
$$

但是，在完全随机化中，“恰好有 $n\pi$ 个单位接受处理”意味着各 $Z_i$ 不是独立的；一个单位被处理会降低其他单位被处理的机会。单位级分析浪费了这种负依赖。

### 方法一：用 MBCR 把负依赖显式化

#### 1. 重新表示完全随机化

Mini-batch complete randomization（MBCR）做两层随机排列：

```text
给定 n、n1 和 π=n1/n
        |
        v
组大小 G=ceil(1/π)
        |
        v
每个常规组固定放 1 个 treatment allocation
（末组可有 0/1/2 个）
        |
        v
组内随机排列 β
        |
        v
全体单位随机排列 η
        |
        v
组合排列得到最终 Z
```

命题 2.6 证明，MBCR 产生的 $Z$ 与标准完全随机化完全同分布。也就是说，MBCR 的主要作用不是提出一种边际上不同的实验，而是给证明增加“每组恰好一个处理”的记账结构。

#### 2. 按组做集中不等式

当 $\pi=1/K$ 时，组数 $T=n\pi$，组大小 $G=1/\pi$。对每个组，合并后的 Horvitz--Thompson 和被界在 $[-G,G]$ 内。于是对 $T$ 个组和应用 Hoeffding 引理，偏差项为

$$
G\sqrt{\frac{2T\log(1/\alpha)}{n^2}}
=\sqrt{\frac{2\log(1/\alpha)}{n\pi}}.
$$

论文的正式区间为

$$
C_n^{\mathrm{Hoeff-MBCR}}
=\left[\widehat\psi'\pm c_n^{\mathrm{MBCR}}(\pi)
\sqrt{\frac{2\log(2/\alpha)}n}\right], \tag{6}
$$

其中 $\widehat\psi'$ 使用组条件 propensity，$c_n^{\mathrm{MBCR}}(\pi)$ 也纳入可能存在的残余组。定理 3.1 给出对所有 $n$ 成立的 $(1-\alpha)$ 覆盖；推论 3.2 证明其宽度仍为 $1/\sqrt{n\pi}$。

### 方法二：Bernoulli 随机化下使用 sub-Bernoulli 界

Bernoulli 随机化中，各处理指示独立，因此不能使用上面的固定处理数负依赖。作者改用更贴合不对称二点分布的累积母函数上界：

$$
\gamma_B(\lambda)=\log\left(\frac b{b-a}e^{\lambda a}-\frac a{b-a}e^{\lambda b}\right). \tag{11}
$$

定理 3.5 给出 Bernoulli 与 MBCR 两种设计下的 sub-Bernoulli 区间。在大 $n$、小 $\pi$ 下，其宽度分别为

$$
\sqrt{\frac{4\log(2/\alpha)}{n\pi}},\qquad
\sqrt{\frac{8\log(2/\alpha)}{n\pi}}.
$$

它们同样恢复 $n\pi$ 有效样本量。关键并不是“换一个估计量就自动更好”，而是针对分配机制选择正确的集中工具。

### 方法三：镜像 + cross-fitting 的方差自适应区间

前两类区间主要依赖取值范围。即使样本中的加权结果方差很小，它们也未必明显变窄。Studentized 方法增加了方差自适应。

#### 1. 一对镜像伪结果

下界使用标准伪结果

$$
\widehat\psi_i^{(\ell)}
=Y_i\left(\frac{Z_i}{\pi}-\frac{1-Z_i}{1-\pi}\right), \tag{13}
$$

上界使用仍然无偏的镜像伪结果

$$
\widehat\psi_i^{(u)}
=(Y_i-1)\left(\frac{Z_i}{\pi}-\frac{1-Z_i}{1-\pi}\right). \tag{14}
$$

二者取值范围相互镜像，使上、下尾分别利用更有利的一侧。

#### 2. 按单位或组拆成两份

Bernoulli 设计按单位拆分，MBCR 按组拆分。每一份的中心估计借助另一份以及本份此前的观测构造，再计算组级平方残差和 $V_{m_s}^{*}(s)$ 与经验方差 $\widehat\sigma_s^{*2}$。调节量

$$
\lambda_s^*=\sqrt{\frac{2\log(2/\alpha)}{m_s\widehat\sigma_s^{*2}}}
\wedge\frac1{2c} \tag{16}
$$

直接依赖估计方差。

#### 3. 构造单侧端点

定理 3.6 分别得到 $L_n^{\mathrm{Stud}}$ 与 $U_n^{\mathrm{Stud}}$。每个端点都是 $(1-\alpha)$ 的单侧置信集，但组合区间

$$
[L_n^{\mathrm{Stud}},U_n^{\mathrm{Stud}}]
$$

按论文写法保证的是 $1-2\alpha$ 覆盖。若目标是总覆盖 $1-\alpha$，应在两个单侧构造中各使用 $\alpha/2$。当两份经验方差稳定到 $\sigma^2$ 时，误差项约按 $2\sigma\sqrt{\log(2/\alpha)/n}$ 缩放。

### 理论最优性

作者先证明 Horvitz--Thompson 估计的 RMSE 上界是 $O(1/\sqrt{n\pi})$，再用适配了 $(Z,Y)$ 依赖关系的 Le Cam 两点法证明超总体下界

$$
\inf_{\widehat\psi}\sup_P
\|\widehat\psi-\psi_{\mathrm{i.i.d.}}\|_{L_2(P)}
\gtrsim\frac1{\sqrt{n\pi}}.
$$

设计型有限总体的对应下界为

$$
\gtrsim\frac1{\sqrt{n\pi}}-\frac1{\sqrt n}. \tag{23}
$$

所以 $n\pi$ 不只是作者方法达到的速率，也是所研究模型下不可普遍超越的有效样本量阶。

### 如何选择区间？

| 实验设计/情形 | 论文建议 | 原因 |
|---|---|---|
| Bernoulli 随机化 | SB-Bern | sub-Bernoulli 界利用分配分布的不对称结构 |
| MBCR | Hoeffding--MBCR | 直接利用组内固定处理数与负依赖 |
| 完全随机化且 $\pi=1/K$ | Hoeffding--MBCR | 此时其中心就是标准 Horvitz--Thompson 估计量 |
| 一般 $\pi$ 的完全随机化 | sub-Bernoulli | 论文指出 Bernoulli 推导的界在完全随机化下仍有效 |
| 组级伪结果方差很小 | 可考虑 Studentized | 宽度可随经验方差缩小，但并非处处占优 |

### 图像证据与限制

Figure 1 的三个面板显示：当 $\pi$ 从 0.1 降到 0.001 时，旧 Hoeffding 区间迅速膨胀，而新区间保持显著更紧。Figure 2 显示 Studentized 方法在潜在结果靠近边界、经验方差低时可以明显收紧一侧，但在高方差情形并不保证优于 Hoeffding--MBCR。六个面板均已直接查看。

需要保留的限制是：结果依赖有界结果、已知随机化机制、SUTVA 与 ignorability；它们不是对干扰、观察性混杂、可选停止或任意无界结果的通用保证。论文页面、v2 TeX 源和全文均未找到官方代码或补充材料，因此方法可以由公式复现，但本工作区没有代码级验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## On Nonasymptotic Confidence Intervals for Treatment Effects in Randomized Experiments

### Paper at a glance

- **Authors:** Ricardo J. Sandoval, Sivaraman Balakrishnan, Avi Feller, Michael I. Jordan, and Ian Waudby-Smith
- **Version:** arXiv:2601.11744v2, revised 23 January 2026
- **Field:** statistical methodology and causal inference for randomized experiments
- **Type:** primary theory/method paper
- **Analysis mode:** paper-only

### Problem

The paper asks whether confidence intervals for average treatment effects can be both genuinely finite-sample valid and as statistically efficient—in their dependence on treatment probability—as familiar asymptotic intervals. Earlier Hoeffding-style nonasymptotic bounds have width of order $1/\sqrt{n\pi^2}$, whereas CLT-based intervals behave like $1/\sqrt{n\pi}$. This gap is especially damaging when treatment is rare ($\pi\ll1$).

### Main contribution

The authors close this gap. For outcomes bounded in $[0,1]$, randomized treatment with known propensity $\pi\le1/2$, SUTVA, and treatment/potential-outcome independence, they construct confidence intervals satisfying coverage for every sample size and achieving the $n\pi$ effective sample size. The guarantees cover both i.i.d. superpopulation and design-based finite-population ATEs under the stated conditions.

There are three complementary constructions:

1. **Hoeffding--MBCR:** rewrite complete randomization as a distributionally equivalent mini-batch procedure. Each batch has a fixed treated count, making negative dependence explicit. Applying concentration to group sums rather than unitwise inverse-probability-weighted terms improves the rate to $1/\sqrt{n\pi}$.
2. **Sub-Bernoulli intervals:** under Bernoulli assignment, use a sharper cumulant-generating-function bound adapted to the asymmetric assignment distribution. This also yields $1/\sqrt{n\pi}$ scaling.
3. **Cross-fit Studentized intervals:** use ordinary and mirrored Horvitz--Thompson pseudo-outcomes, split/groupwise variance estimates, and one-sided sub-exponential bounds. These intervals adapt to low realized variance, although the two-sided construction has $1-2\alpha$ coverage when each endpoint uses level $\alpha$.

The paper then proves matching RMSE upper and minimax lower rates: $1/\sqrt{n\pi}$ in the i.i.d. model and $1/\sqrt{n\pi}-1/\sqrt n$ in the design-based model, up to constants. Thus the improved dependence on $\pi$ is information-theoretically optimal in the studied models.

### Evidence and evaluation

This is primarily a theorem paper, not a data benchmark. Figure 1 compares interval contraction at $\pi=0.1$, $0.01$, and $0.001$; visual inspection confirms that the older Hoeffding interval degrades severely as $\pi$ shrinks while the proposed intervals remain much tighter. Figure 2 uses three simulated potential-outcome distributions and shows that Studentization can substantially tighten a favorable endpoint when empirical variance is low, but does not uniformly dominate fixed-range intervals.

### Practical interpretation

- Use the sub-Bernoulli interval for Bernoulli randomization.
- Use Hoeffding--MBCR for MBCR, and directly for complete randomization when $\pi=1/K$ so its center equals the standard Horvitz--Thompson estimator.
- For general complete-randomization propensities, the paper recommends the sub-Bernoulli route.
- Consider the Studentized construction when the groupwise pseudo-outcomes are expected to have low variance.

These are design-specific finite-sample results. They do not cover observational confounding, estimated propensities, unbounded outcomes without additional work, interference, or optional stopping.

### Reproducibility

**Source reproducibility: 3/5.** The paper provides explicit estimators, interval formulas, a complete MBCR algorithm, and detailed proofs. The 46-page arXiv v2 PDF was converted to structured Markdown with all six linked figure panels available locally and visually checked. However, no official repository, executable package, data archive, or supplementary material was found in the arXiv page, v2 TeX source, or full paper text, so numerical reproduction was not code-verified. MinerU OCR is structurally good but contains recurring spelling artifacts; equations and claims should be checked against the PDF when exact typography matters.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
