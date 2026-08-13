---
layout: default
permalink: /paper-atlas/post-hoc-large-sample-statistical-inference-28bfbd73/
title: "Post_Hoc_Large_Sample_Statistical_Inference"
nav: false
description: "传统统计推断要求在看数据之前选定显著性水平 \\alpha。例如，研究者先算一个 95% 置信区间，发现结果“不显著”，再用同一批数据改算 90% 区间，通常已经失去原先的错误率保证。这就是论文所说的 “roving alphas” 问题。 现有 e-value 理论允许事后选择 \\alpha，但此前主要是有限样本方法。有限样本有效性很强，却往往依赖已知有界性、强矩条件或付出较大的保守性。"
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
    <h1>Post_Hoc_Large_Sample_Statistical_Inference</h1>
    <p>Post-Hoc Large-Sample Statistical Inference</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2603.08002" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Post_Hoc_Large_Sample_Statistical_Inference">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/bchugg/asymp-posthoc-confint" target="_blank" rel="noopener noreferrer" aria-label="Open code for Post_Hoc_Large_Sample_Statistical_Inference">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Post-Hoc Large-Sample Statistical Inference 方法详解

### 这篇论文解决什么问题？

传统统计推断要求在看数据之前选定显著性水平 $\alpha$。例如，研究者先算一个 95% 置信区间，发现结果“不显著”，再用同一批数据改算 90% 区间，通常已经失去原先的错误率保证。这就是论文所说的 “roving alphas” 问题。

现有 e-value 理论允许事后选择 $\alpha$，但此前主要是有限样本方法。有限样本有效性很强，却往往依赖已知有界性、强矩条件或付出较大的保守性。本文研究的是另一条路线：能否像 Wald 区间和中心极限定理那样，在弱假设下建立**大样本、事后有效**的置信区间、p 值和序贯置信序列？

答案是可以，但必须准确理解保证的含义：本文控制的是跨所有 $\alpha$ 的归一化风险，而不是声称“看完数据随便调整后仍有普通的 $1-\alpha$ 覆盖率”。

### 核心定义：把 $\alpha$ 放进风险之中

对参数 $\theta(P)$ 和一族置信集 $\mathcal H_n(\alpha)$，定义

$$
\mathbf R(\mathcal H_n;\theta,P)
=\mathbb E_P\left[\sup_{\alpha>0}
\frac{\mathbf 1\{\theta(P)\notin\mathcal H_n(\alpha)\}}{\alpha}\right].
$$

若

$$
\sup_{P\in\mathcal P}\limsup_{n\to\infty}
\mathbf R(\mathcal H_n;\theta,P)\le 1,
$$

则称其为渐近事后置信区间（APH-CI）。与普通定义相比，关键变化是 $\sup_\alpha$ 位于期望内部，因此 $\alpha$ 可以依赖数据。更强的 distribution-uniform 版本还要求对整类分布的最坏情况与 $n\to\infty$ 一起收敛。

### 为什么 e-variable 是唯一的核心工具？

渐近 e-variable 是非负统计量 $E_n$，满足其零假设下期望在渐近意义上不超过 1。论文的 Proposition 2.6 给出一个必要且充分的表示：在自然的单调性和连续性条件下，所有 APH-CI 都可以写成

$$
\mathcal H_n(\alpha)=\{\theta:E_n(\theta)<1/\alpha\},
$$

而所有渐近事后 p 值都等于 $1/E_n$。这不是“e-value 是一种可选技巧”，而是“合格的事后置信族本质上必须来自 e-variable”。

计算流程可以概括为：

```text
数据 X_1:n + 候选参数 theta
          |
          v
构造与最终 alpha 无关的渐近 e-variable E_n(theta)
          |
     以 1/alpha 为阈值
          |
          v
对 theta 反演 -> 整族置信区间 H_n(alpha)
          |
          v
观察结果后，才选择最终报告的 alpha
```

这里最容易犯的错误是：虽然最终 $\alpha$ 可以事后选，但 e-variable 的调参不能随着事后 $\alpha$ 一起重选。

### 方法一：IWR 自归一化构造

对均值参数 $\theta$，定义

$$
S_n(\theta)=\sum_{i\le n}(X_i-\theta),\qquad
V_n(\theta)=\left(\sum_{i\le n}(X_i-\theta)^2\right)^{1/2}.
$$

IWR e-variable 为

$$
E_n^{\textsc{iwr}}(\theta;\lambda)
=\exp\left(\lambda\frac{S_n(\theta)}{V_n(\theta)}-\frac{\lambda^2}{2}\right).
$$

它利用 $S_n/V_n$ 自归一化，不要求预先知道方差。本文证明：逐分布而言，它甚至适用于某些方差不存在但仍属于 Gaussian domain of attraction 的分布；若要求对一类分布统一有效，则需要一致有界的标准化三阶矩。

将 e-variable 对 $\theta$ 反演，得到闭式区间

$$
\mathcal H_n^{\textsc{iwr}}(\alpha;\lambda)
=\left(\bar X_n\pm
\frac{A_{n,\alpha}(\lambda)\hat s_n}
{\sqrt{1-A_{n,\alpha}^2(\lambda)}}\right),
$$

其中

$$
A_{n,\alpha}(\lambda)=
\frac{\log(2/\alpha)+\lambda^2/2}{\lambda\sqrt n}.
$$

若分母条件不满足，则区间必须退化为整个实数轴，而不能硬算一个看似精确的区间。

### 怎样合法选择 $\lambda$？

对某个固定 $\alpha$，最窄选择是 $\lambda_\alpha=\sqrt{2\log(2/\alpha)}$。但如果先看数据、再选 $\alpha$、随后用它重算 $\lambda$，就破坏了事后有效性。论文给出两种策略：

#### 1. Ex ante anchoring

分析前猜一个锚点 $\alpha_0$，固定

$$
\lambda=\sqrt{2\log(2/\alpha_0)}.
$$

以后无论选择哪个 $\alpha$，置信族都仍有效；只是 $\alpha$ 越接近锚点，区间越紧。Figure 1 显示在考察范围内，锚点错配带来的渐近宽度代价相对温和，最大比值为 1.184。

#### 2. Mixture IWR

不固定一个 $\lambda$，而是按照截断高斯分布对 e-variable 积分。这样可避免把性能押在一个锚点上，并自然形成双侧区间。代码通过 log-space 计算和二分法稳定求解一个标量根 $y$，再输出

$$
\bar X_n\pm\frac{\hat s_n y}{\sqrt{n-y^2}}.
$$

若 $y^2\ge n$，则返回 $(-\infty,\infty)$。

### 方法二：R-WS 及序贯扩展

R-WS 路线对经验方差加入 $1/\log n$ 正则项，并截断 e-value，换来在一致有界 $(2+\delta)$ 阶矩下的 distribution-uniform 保证。其混合区间一般比 IWR 更宽，但要求比一致三阶矩更弱。

更重要的是，它可以扩展到“事后 + 序贯”同时成立。论文引入 burn-in $m$ 和后续时刻 $k\ge m$ 的上三角数组，定义渐近 e-process，并证明在任意 stopping time 上仍保持渐近期望控制。对它反演得到 APH confidence sequence：研究者先收集至少 $m$ 个样本，之后既可以继续采样，也可以根据数据选择 $\alpha$，但需要满足 $\alpha>Cm^{-0.24}$ 的范围条件。

因此三种主方法的取舍是：

| 方法 | 主要优势 | 主要代价 |
|---|---|---|
| Anchored IWR | 锚点附近最紧，公式简单 | 需要事前选 $\alpha_0$；错配会变宽 |
| Mixture IWR | 无需押注单一锚点，最坏情况更稳健 | 通常比匹配良好的 anchored IWR 宽 |
| Mixture R-WS / APH-CS | 较弱统一矩条件；支持 optional continuation | 最保守、最宽；有 burn-in/range 条件 |

### 实验结果如何支持方法？

论文使用模拟数据，不是生物信息学数据分析。

- Figure 2：Wald 最窄，但没有事后有效性；所有区间随样本量增加而收窄，到 $n=10^4$ 时绝对宽度差已很小。
- Figure 3：在有界 Bernoulli 数据上，anchored IWR 与知道真实方差的 Bernstein 区间相近；betting CI 更紧，但利用了有界性。
- Table 1：模拟研究者在数据上搜索最小拒绝水平。Wald 的实际风险达到 7.089，而 anchored IWR、mixture IWR、mixture R-WS 分别为 0.532、0.367、0.001，直接显示普通 Wald 区间不能承受事后搜索 $\alpha$。
- Figures 5–7：mixture IWR 对测试范围内的 $\kappa$ 不敏感；REG 与 IWR 大样本宽度几乎一致，小 $\eta$ 时尤其接近。

### 代码实现与可复现性

官方仓库 `bchugg/asymp-posthoc-confint` 的固定提交 `1c73059e…` 实现了核心区间公式：

- `methods.py:6-13`：IWR e-variable；
- `methods.py:59-93`：anchored IWR 与 mixture IWR；
- `methods.py:95-111`：mixture R-WS 固定样本区间；
- `utils.py:48-74`：mixture IWR 的稳定数值反演；
- `methods.py:114-160`、`utils.py:8-31`：REG 与比较基线。

代码—论文一致性评为 **medium**：核心公式是直接对应的，但仓库 README 提到的 `experiments.ipynb` 和 `sanity_check.ipynb` 在该提交中不存在；也没有测试、环境锁文件、完整绘图脚本、APH-pvalue/test API，以及显式的 $(m,k)$ 序贯接口。因此，方法级公式可以核对和调用，但 Figures 1–7 与 Table 1 的端到端精确复现为 `Not found`。

### 使用时必须保留的边界

1. 这是渐近保证，不是所有有限样本都精确有效。
2. 风险控制不同于任意适应后的普通覆盖率。
3. 可以事后选 $\alpha$，不能同时事后重选 $\lambda$、混合参数和分析策略而不付出额外校正。
4. pointwise 与 distribution-uniform 结论假设不同，不能混用。
5. 如果还要边看数据边决定是否继续采样，应使用 APH-CS，而不是重复使用固定样本 APH-CI。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Post-Hoc Large-Sample Statistical Inference

### Problem

Classical asymptotic confidence intervals and p-values require the significance level $\alpha$ to be fixed before seeing the data. Recomputing an inconclusive result at a more permissive level on the same data—the “roving alpha” problem—invalidates their usual guarantee. Existing post-hoc-valid methods based on e-values are nonasymptotic and consequently can require strong boundedness/moment information or be conservative.

### Contribution

Chugg, Gauthier, Jordan, Ramdas, and Waudby-Smith develop a mathematical-statistics framework for **asymptotic post-hoc inference**. Its confidence sets and p-values permit data-dependent $\alpha$, while controlling a normalized risk rather than claiming ordinary coverage after arbitrary selection. The framework has four main results:

1. Under monotonicity and continuity, asymptotic e-variables are necessary and sufficient for asymptotic post-hoc confidence intervals; asymptotic post-hoc p-values are exactly inverse e-values.
2. The IWR self-normalized e-variable remains valid pointwise over the Gaussian domain of attraction and distribution-uniformly under a bounded standardized third moment. Its inversion gives a closed-form APH-CI.
3. IWR tuning can be handled legally either by fixing an ex ante anchor $\alpha_0$ or by mixing over $\lambda$; the latter avoids committing to one anchor and improves worst-case width behavior.
4. A regularized/truncated R-WS construction works under a uniform $(2+\delta)$-moment condition and extends to a new notion of asymptotic e-process, yielding a post-hoc asymptotic confidence sequence that supports optional continuation after burn-in.

### How the method works

Given iid observations and a candidate mean $\theta$, compute an asymptotic e-variable $E_n(\theta)$ whose expectation is asymptotically bounded by one under the null. Form the entire nested confidence family by inversion,

$$
\mathcal H_n(\alpha)=\{\theta:E_n(\theta)<1/\alpha\}.
$$

Because $E_n$ itself is fixed independently of the eventual level, $\alpha$ may be selected after viewing the data. Anchored IWR is usually tightest near its prespecified anchor; mixture IWR is more robust to anchor mismatch; mixture R-WS is wider but supplies weaker uniform moment requirements and the stronger sequential guarantee.

### Evaluation

The paper uses controlled simulations rather than real-world datasets. Width comparisons cover Gaussian, Bernoulli, and sub-Gaussian settings and contrast IWR, mixture IWR, R-WS, Wald, Bernstein, betting, and regularized variants. Figure 2 shows the Wald interval remains narrower but the absolute gap is reported below 0.05 by $n=10^4$. Figure 3 shows anchored IWR is comparable to the oracle Bernstein interval on bounded data, though the betting interval is tighter because it exploits boundedness.

The most direct test mimics p-hacking by searching the observed data for the smallest rejecting $\alpha$. Practical empirical risk is 7.089 for Wald, versus 0.532 for anchored IWR, 0.367 for mixture IWR, and 0.001 for mixture R-WS. This supports the intended risk-control distinction: ordinary Wald inference breaks badly under data-dependent level selection, while the APH-CIs remain below one in the experiment.

### Interpretation and limitations

This is not a license to change every analysis decision after seeing the data. The e-variable construction and tuning policy must be fixed independently of the eventual $\alpha$, and the resulting guarantee is asymptotic **risk control**, not finite-sample conditional coverage or conventional long-run coverage under arbitrary adaptation. Pointwise and distribution-uniform claims also rely on different moment assumptions.

The authors recommend the R-WS confidence sequence as the safest practical option when optional continuation matters; anchored IWR is typically the tightest for plausible levels, while mixture IWR has better worst-case anchoring behavior.

### Reproducibility

The paper links an official Python repository, archived here at commit `1c73059e0b12764549f9ba74cd4999f55e78d858`. The snapshot faithfully implements the core IWR, mixture-IWR, R-WS, REG, Wald, Bernstein, and sub-Gaussian formulas, including stable numerical inversion. Overall code-paper fidelity is **medium**: the principal interval formulas are present, but the notebooks named by the repository README and the paper's complete simulation/plot pipeline are absent. There are no packaged tests, environment lockfile, or explicit APH-pvalue/test and burn-in-indexed sequential APIs. Exact regeneration of Figures 1–7 and Table 1 is therefore `Not found`, despite detailed prose parameters in Appendix D.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
