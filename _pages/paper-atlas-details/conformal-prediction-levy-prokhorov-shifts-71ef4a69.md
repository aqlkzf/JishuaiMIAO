---
layout: default
permalink: /paper-atlas/conformal-prediction-levy-prokhorov-shifts-71ef4a69/
title: "Conformal_Prediction_Levy_Prokhorov_Shifts"
nav: false
description: "标准 split conformal prediction 依赖校准样本与测试样本的可交换性。一旦测试分布变了，用训练/校准分布得到的分位数就可能太小，预测集合因而欠覆盖。本文研究的是一个更具体的问题：如果测试分布位于训练分布周围的 Lévy–Prokhorov（LP）模糊集中，怎样构造仍具有有限样本边际覆盖保证的预测集合？ 这是一篇统计机器学习方法论文，不是生信专用方法。"
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
      <span>Advances in Neural Information Processing Systems (NeurIPS) 38 · 2025</span>
    </div>
    <h1>Conformal_Prediction_Levy_Prokhorov_Shifts</h1>
    <p>Conformal Prediction under Lévy–Prokhorov Distribution Shifts: Robustness to Local and Global Perturbations</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2502.14105" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Lévy–Prokhorov 分布偏移下的稳健 Conformal Prediction

### 这篇文章解决什么问题？

标准 split conformal prediction 依赖校准样本与测试样本的可交换性。一旦测试分布变了，用训练/校准分布得到的分位数就可能太小，预测集合因而欠覆盖。本文研究的是一个更具体的问题：如果测试分布位于训练分布周围的 Lévy–Prokhorov（LP）模糊集中，怎样构造仍具有有限样本边际覆盖保证的预测集合？

这是一篇统计机器学习方法论文，不是生信专用方法。MNIST、ImageNet 和 iWildCam 只是用于验证一般方法的分类数据集。

### LP 模糊集为何适合描述分布偏移？

LP 模糊集写成

$$
\mathbb B_{\varepsilon,\rho}(\mathbb P)
=\{\mathbb Q:\operatorname{LP}_{\varepsilon}(\mathbb P,\mathbb Q)\leq\rho\},
$$

其中

$$
\operatorname{LP}_{\varepsilon}(\mathbb P,\mathbb Q)
=\inf_{\gamma\in\Gamma(\mathbb P,\mathbb Q)}
\int\mathbb 1\{\lVert z_1-z_2\rVert>\varepsilon\}\,d\gamma.
$$

直观上，它允许两种变化同时发生：

1. **局部扰动 $\varepsilon$**：所有概率质量都可以在半径 $\varepsilon$ 内移动。例如图像像素的小噪声。
2. **全局扰动 $\rho$**：最多 $\rho$ 比例的质量可以被搬到任意位置。例如少量标签被污染，或测试群体中出现训练集从未覆盖的新区域。

论文证明 LP 球等价于“先做 $W_\infty$ 半径 $\varepsilon$ 的局部移动，再做 TV 半径 $\rho$ 的全局污染”。因此它同时包含两个极端特例：$\varepsilon=0$ 时是 TV 稳健性，$\rho=0$ 时是 $W_\infty$ 稳健性。更重要的是，它不要求测试分布相对于训练分布绝对连续，所以比依赖密度比或 $f$-divergence 的方法能容纳更强的 support shift。

### 关键技巧：把高维偏移推到一维分数空间

Conformal prediction 最终只使用一个标量非一致性分数 $S=s(X,Y)$。如果 $s$ 是 $k$-Lipschitz，论文证明

$$
s_\#\mathbb B_{\varepsilon,\rho}(\mathbb P)
\subseteq\mathbb B_{k\varepsilon,\rho}(s_\#\mathbb P).
$$

这里 $s_\#\mathbb P$ 是通过 $s$ 得到的 score pushforward 分布。也就是说，高维 $(X,Y)$ 空间里难处理的 LP 偏移，被压缩成一维 score 分布上的 LP 偏移；局部半径变成 $k\varepsilon$，全局质量比例 $\rho$ 不变。

需要注意：Lipschitz 假设只服务于“数据空间到分数空间”的这一步。如果直接假设 score 分布发生 LP 偏移，后面的分位数和覆盖结论不要求深度网络本身是 Lipschitz 的。

### 最坏分位数与最坏覆盖为什么有闭式解？

LP 模型把两类偏移分开，因此最坏情况也能分开计算：

$$
\operatorname{Quant}^{\mathrm{WC}}_{\varepsilon,\rho}(\beta;\mathbb P)
=\operatorname{Quant}(\beta+\rho;\mathbb P)+\varepsilon,
$$

$$
\operatorname{Cov}^{\mathrm{WC}}_{\varepsilon,\rho}(q;\mathbb P)
=F_{\mathbb P}(q-\varepsilon)-\rho.
$$

这两个式子揭示了参数的不同作用：

- $\varepsilon$ 把阈值向右平移，主要扩大预测集合；
- $\rho$ 不仅提高所需分位数水平，还直接从最坏覆盖率中扣除，因此对欠覆盖更敏感。

若 $\rho\geq1-\beta$，允许任意搬走的质量已经足以把目标分位数推到无穷远或支持集最大值，因此非平凡公式要求 $\rho<1-\beta$。

### 稳健 conformal 构造

给定 $n$ 个校准分数 $S_i=s(X_i,Y_i)$、目标误覆盖率 $\alpha$ 和 score-space 半径 $(\varepsilon,\rho)$：

1. 构造经验分布 $\widehat{\mathbb P}_n=n^{-1}\sum_i\delta_{S_i}$；
2. 做有限样本修正

$$
\beta=\alpha+\frac{\alpha-\rho-2}{n};
$$

3. 计算稳健阈值

$$
\widehat q_{\mathrm{LP}}
=\operatorname{Quant}(1-\beta+\rho;\widehat{\mathbb P}_n)+\varepsilon;
$$

4. 输出

$$
C(x)=\{y:s(x,y)\leq\widehat q_{\mathrm{LP}}\}.
$$

在测试 score 分布确实落入该 LP 球的前提下，论文证明 $\Pr\{Y_{n+1}\in C(X_{n+1})\}\geq1-\alpha$。

```text
训练好的预测器 + 校准样本
          |
          v
  计算非一致性分数 S_i
          |
  指定/估计 (epsilon, rho)
          |
  提高经验分位数水平 + 加 epsilon
          |
          v
    得到稳健阈值 q_LP
          |
          v
  保留所有 score <= q_LP 的候选标签
```

算法核心非常轻量：理论已经把分布稳健优化化成了一个经验顺序统计量加一个常数。官方代码 `src/lp_robust_cp.py:66-71` 正好实现这个公式，并使用 `method='higher'` 避免在两个分数之间插值。

### 怎样从数据估计 $(\varepsilon,\rho)$？

附录给出一个需要目标分布 score 样本的实用方案：

1. 把校准 score 随机分成两个互不重叠的批次；
2. 扫描候选 $\varepsilon_i$；
3. 用第一批校准 score 与目标分布 score 做一维最优传输，代价为 $\mathbb 1\{|x-y|\geq\varepsilon_i\}$，得到对应 $\rho_i$；
4. 用第二批校准 score 计算每个 $(\varepsilon_i,\rho_i)$ 的稳健分位数；
5. 选择分位数最小、预测集合最紧的候选。

两批校准 score 必须分开，避免用同一批数据既选参数又校准阈值。这个过程并不是“无需目标数据就能自动知道未来偏移”；论文明确承认它需要 500–1000 个左右的目标 score。在可以直接取得可交换的带标签目标样本时，直接用标准 conformal 校准可能更合适。

### 实验告诉了我们什么？

论文设 $\alpha=0.1$，使用 NLL score：

- MNIST/ImageNet：局部偏移是均匀像素噪声，全局偏移是一定比例的标签污染；
- iWildCam：相机位置、时间、背景、物种频率等造成真实 train–test shift；
- 比较 SC、$\chi^2$-robust CP、weighted CP、RSCP 和 FG-CP。

三档合成偏移图中，固定参数和数据估计的两个 LP 版本都保持约 90% 或更高覆盖；标准 CP 随偏移增强明显欠覆盖。RSCP 通常也有效，但 ImageNet 预测集合接近 900 个标签，远大于 LP 方法。iWildCam 的二维曲面清楚显示：增大 $\varepsilon$ 或 $\rho$ 会提高覆盖，也会扩大集合；估计点接近 90% 覆盖前沿，图中估计点与网格最优点的集合大小约为 6.583 和 6.521。

### 使用时最容易误解的边界

- 保证依赖“真实测试 score 分布属于所选 LP 球”；错误低估 $\rho$ 尤其可能造成欠覆盖。
- 保证是边际覆盖，不是每个 $x$、每个亚组都达到覆盖率。
- 实验把数据空间噪声半径乘固定 $k=2$；这是经验选择，不是对 ResNet 的全局 Lipschitz 常数证明。
- 估参方法看到了目标 score，因此不能宣传为对未知未来 shift 的无数据自适应。
- 官方代码与核心公式高度一致，但缺少依赖锁定、自动测试、iWildCam 权重和统一运行入口；完整复现实验仍需人工配置。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Conformal Prediction under Lévy–Prokhorov Distribution Shifts

### Paper summary

This paper develops finite-sample conformal prediction for train–test shifts modeled by a Lévy–Prokhorov (LP) ambiguity set. The LP model unifies two qualitatively different changes: every observation may move locally by at most $\varepsilon$, while an arbitrary fraction up to $\rho$ of probability mass may move globally. Unlike likelihood-ratio or $f$-divergence methods, the model can include test distributions that put mass outside the training support.

The central move is to push the ambiguity set through the nonconformity score. For a $k$-Lipschitz score, a high-dimensional LP shift on $(X,Y)$ maps into a one-dimensional LP shift on scores with radii $(k\varepsilon,\rho)$. In score space, the authors derive exact expressions:

$$
\operatorname{Quant}^{\mathrm{WC}}_{\varepsilon,\rho}(\beta;\mathbb P)
=\operatorname{Quant}(\beta+\rho;\mathbb P)+\varepsilon,
$$

$$
\operatorname{Cov}^{\mathrm{WC}}_{\varepsilon,\rho}(q;\mathbb P)
=F_{\mathbb P}(q-\varepsilon)-\rho.
$$

These formulas turn a distributionally robust optimization problem into a shifted empirical quantile. With the finite-sample correction $\beta=\alpha+(\alpha-\rho-2)/n$, the prediction set using threshold $\operatorname{Quant}(1-\beta+\rho;\widehat{\mathbb P}_n)+\varepsilon$ has at least $1-\alpha$ marginal coverage whenever the test score distribution lies in the specified LP ball.

### Why prior approaches are insufficient here

- Standard split conformal prediction loses its exchangeability guarantee under general distribution shift.
- Weighted conformal prediction (NeurIPS 2019) targets covariate shift and needs density-ratio information.
- $f$-divergence robust validation (JASA 2024) requires absolute continuity and cannot represent new support as naturally.
- Randomly smoothed conformal prediction (ICLR 2021) handles norm-bounded adversarial changes but can be highly conservative.
- Fine-grained conformal prediction (ICML 2024) separates covariate and conditional shifts but retains reweighting/$f$-divergence structure.

LP ambiguity sets cover local transport and global contamination together, with TV and $W_\infty$ robustness as limiting cases.

### Method in one paragraph

Compute calibration nonconformity scores, choose LP radii $(\varepsilon,\rho)$ in score space, raise the empirical quantile level by $\rho$ with the paper's finite-sample correction, add $\varepsilon$ to the resulting threshold, and include every candidate label whose score is below that threshold. An optional estimator searches over $\varepsilon$, estimates the corresponding $\rho$ by one-dimensional indicator-cost optimal transport using shifted test scores, and selects the pair giving the smallest robust quantile on an independent calibration split.

### Evaluation

The experiments use negative log-likelihood scores at target coverage 90% on MNIST, ImageNet, and iWildCam. Synthetic MNIST/ImageNet shifts combine uniform input noise (local) with label corruption (global); baselines are standard conformal prediction, $\chi^2$-robust CP, weighted CP, RSCP, and FG-CP. Across the three plotted perturbation levels, both fixed-parameter and estimated LP variants maintain the target, whereas standard CP degrades and several structured baselines under-cover. RSCP remains valid but is extremely inefficient on ImageNet, with prediction sets near 900 labels in the displayed settings. On iWildCam, the estimated $(\varepsilon,\rho)$ pair lies near the empirical 90%-coverage frontier and has nearly the same set size as the grid-search point (approximately 6.583 versus 6.521 in the figure).

### Reproducibility assessment: 3.5/5

The official repository is available at `https://github.com/olivrw/LP-robust-conformal.git`; this workspace pins `main@8a81440d0c591589c050afff4dec5fb6461862d5`. The code matches the core adjusted quantile exactly and provides MNIST, ImageNet, and iWildCam drivers plus parameter-estimation scripts. The mathematical core is unusually transparent: `src/lp_robust_cp.py:66-71` implements the robust threshold in four lines.

Reproduction is not turnkey. The repository lacks pinned dependencies, tests, and a single run guide; datasets must be provisioned separately; the iWildCam checkpoint is referenced externally but absent; and two direct code inconsistencies are documented in `doc_code.md`. Baseline code is partly borrowed from other repositories. These limitations affect experimental reruns, not the source-level match of the proposed quantile rule.

### Limitations and interpretation

- The guarantee assumes the chosen LP ambiguity set contains the test score distribution; misspecified radii can invalidate protection.
- Coverage is marginal, not conditional for each covariate value or subgroup.
- Translating data-space perturbations into score-space $\varepsilon$ requires Lipschitz control. The experiments use empirical fixed $k=2$, not a proved global constant for the neural networks.
- The optional estimator needs shifted test scores and a disjoint calibration split; it is not an unsupervised guarantee for unseen future shift.
- The empirical comparisons cover three classification datasets and a particular family of perturbations.

### Metadata

- Authors: Liviu Aolaritei, Zheyu Oliver Wang, Julie Zhu, Michael I. Jordan, Youssef Marzouk.
- Canonical source: arXiv `2502.14105v2` (submitted 19 February 2025; revised 19 May 2025).
- Venue: the Michael I. Jordan publication page identifies NeurIPS 2025. No separate proceedings page was located in the acquisition search, so arXiv v2 is the verified primary text used here.
- Domain/type: statistical machine learning; method paper; not specifically bioinformatics.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
