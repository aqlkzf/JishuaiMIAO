---
layout: default
permalink: /paper-atlas/strategic-feature-selection-06a566da/
title: "Strategic_Feature_Selection"
nav: false
wide: true
description: "很多预测模型不仅“观察世界”，还会改变被预测者的行为。以 Medicare Advantage 为例，政府根据诊断编码预测患者风险并向保险公司付费；模型给某个诊断的系数越大，保险公司就越有动力通过补充或强化诊断编码来提高支付额。 战略分类（strategic classification）的经典思路是重新设计一个能够预见这种行为的预测器。但现实制度通常不允许彻底替换已有流程，决策者往往只能调整两个粗粒度杠杆： 删除一部分容易被操纵的特征；"
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
    <h1>Strategic_Feature_Selection</h1>
    <p>Strategic Feature Selection</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2606.18867" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Strategic_Feature_Selection">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/jivatneet/strategic-feature-selection" target="_blank" rel="noopener noreferrer" aria-label="Open code for Strategic_Feature_Selection">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Strategic Feature Selection：策略行为下如何联合选择特征与正则化

### 1. 论文要解决什么问题？

很多预测模型不仅“观察世界”，还会改变被预测者的行为。以 Medicare Advantage 为例，政府根据诊断编码预测患者风险并向保险公司付费；模型给某个诊断的系数越大，保险公司就越有动力通过补充或强化诊断编码来提高支付额。

战略分类（strategic classification）的经典思路是重新设计一个能够预见这种行为的预测器。但现实制度通常不允许彻底替换已有流程，决策者往往只能调整两个粗粒度杠杆：

1. 删除一部分容易被操纵的特征；
2. 用 ridge 正则化缩小保留特征的系数。

本文的问题不是“怎样构造任意形式的最优战略预测器”，而是：**在只能使用特征选择和普通 ridge 的条件下，应该怎样联合选择特征集合与正则强度？**

### 2. 为什么“删除最容易操纵的特征”不够？

单个特征是否应该保留，至少取决于三件事：

- **可预测性**：删除它会损失多少无法由其他特征恢复的预测信号？
- **可操纵性**：保留它会带来多大的战略响应？
- **相对结构**：保留特征之间的操纵成本是否相近，以及是否存在低操纵性的相关代理特征？

因此，高度可操纵的特征不一定要删除。如果它非常有预测力，而且同组特征的操纵成本较为同质，一个共同的 ridge 系数可能就能有效控制风险。反过来，如果存在一个较难操纵且高度相关的代理变量，删除原来的可操纵特征可能几乎不损失预测信息。

这与既有的战略分类方法不同。Hardt 等（2016）以来的工作主要优化完整的战略预测规则；Björkegren 等（2025）研究线性规则和二次操纵成本下的稳健预测。本文则把制度约束本身作为核心：只能在既有回归管线里做变量筛选和标量 ridge，而不是自由设计预测器。

### 3. 数学模型

决策者发布线性预测器

$$
f_{\theta,b}(x)=\theta^{\top}x+b.
$$

组织可以把特征从 $x$ 改为 $x+a$，并支付二次成本

$$
C(a)=\frac12a^{\top}Ha,
$$

其中 $H\succ0$。组织的最优响应为

$$
a^{*}(\theta)=H^{-1}\theta.
$$

所以决策者真正关心的不是部署前 MSE，而是组织响应之后的战略 MSE：

$$
\mathrm{MSE}_{\mathrm{strat}}(\theta,0)
=(\theta-\theta^{*})^{\top}\Sigma(\theta-\theta^{*})
+(\theta^{\top}H^{-1}\theta)^2+\sigma^2.
$$

第一项是预测系数偏离真实线性投影带来的误差，第二项是模型系数诱发操纵后产生的系统性偏移，第三项是不可约噪声。

给定特征集合 $\mathsf S$ 和 ridge 强度 $\lambda$，部署模型是普通的支持集限制 ridge：

$$
\theta^{\mathrm{OR}}(\mathsf S,\lambda)
\in\arg\min_{\operatorname{supp}(\theta)\subseteq\mathsf S}
\mathbb E[(Y-\theta^{\top}X)^2]+\lambda\|\theta\|_2^2.
$$

目标是在预算 $|\mathsf S|\le s$ 下最小化其战略 MSE。

### 4. 理论结论：三个量共同决定支持集

定理 2 把某个支持集在最优 ridge 下相对零截距战略最优解的误差上界写成：

$$
\underbrace{-\bigl(\Gamma([d])-\Gamma(\mathsf S)\bigr)}_{\text{删除特征带来的操纵收益}}
+\underbrace{L_{\mathrm{pred}}(\mathsf S)}_{\text{预测损失}}
+\underbrace{C_H(\mathsf S)\delta_H(\mathsf S)^2}_{\text{成本异质性缺口}}.
$$

直观上：

- 删除特征能够减轻战略负担，这是收益；
- 被删特征中无法由保留特征线性恢复的信号形成预测损失；
- 如果保留特征的操纵成本差异很大，一个标量 $\lambda$ 无法同时给不同方向施加合适强度的收缩，因此会产生异质性缺口。

这解释了为什么特征选择与 ridge 不能分开调参。支持集改变以后，最佳 $\lambda$ 会变；$\lambda$ 改变以后，最佳支持集也可能变化。

### 5. 算法流程

精确枚举所有支持集是组合爆炸。论文采用“连续松弛筛选 + 离散局部优化 + 标准 ridge 重拟合”：

```text
输入：未操纵数据、Sigma、theta*、H^{-1}、支持预算 s
  │
  ├─ 遍历候选 ridge 强度 lambda
  │
  ├─ 求解连续权重 w ∈ [0,1]^d，且 1^T w ≤ s
  │     权重为 0 时强制对应系数为 0
  │
  ├─ 取权重最大的 s 个特征，得到初始支持集
  │
  ├─ 按真实战略目标执行 add / drop / swap 局部搜索
  │     每一步只接受严格降低战略 MSE 的移动
  │
  ├─ 在改进后的支持集上重新拟合普通 ridge
  │
  └─ 选择战略 MSE 最小的 (支持集, lambda)

输出：离散特征集合、ridge 强度、标准稀疏 ridge 系数
```

连续松弛使用透视惩罚 $\varphi(\theta_i,w_i)=\theta_i^2/w_i$。当权重是 0/1 时，它与真实的支持集限制 ridge 完全一致；连续权重只是为了找到较好的初始支持集。最终部署的不是加权松弛模型，而是离散支持集上的普通 ridge。

局部搜索在每个固定 $\lambda$ 下尝试加入一个特征、删除一个特征或交换一对特征。因为每个接受的移动都会严格降低精确目标，而候选支持集数量有限，所以算法一定终止，并且不会比简单的 top-$s$ 舍入更差。

### 6. 实验结果

#### 合成基准

论文在 $d=18$、支持预算 $s=5$ 的 30 个低维实例上枚举全部可行支持集，得到精确网格 oracle。连续权重直接舍入只在 18/30 个实例达到 oracle；加入局部改进以后，完整方法在 30/30 个实例达到 oracle。只做子集选择、不做 ridge 的方法，中位归一化战略 MSE 为 1.34，最大为 1.82。

#### Medicare Advantage 案例

数据包含 5,000 名半合成受益人和 115 个 CMS-HCC V28 指标，其中 30 个在基线数据中非零。论文用已发表的 CMS 系数作为 $\theta^{*}$，并依据差异编码证据构造操纵易度矩阵。这个矩阵是政策校准的代理量，不是从真实保险公司行为中估计出的结构成本。

在操纵强度 $\alpha=1$ 时，保留 $k=25$ 个特征的联合方法相对 full ridge 将部署后 MSE 降低约 40%，优于“删除 top-ten 诊断组”、prediction-only、cost-only 和 subset-only。绝对最优支持大小是 $k=20$，但 $k=25$ 几乎不损失性能，并保留了数据中属于 top-ten 诊断组的全部 6 个 HCC。这说明“编码敏感”并不自动意味着“必须删除”。

### 7. 应如何理解结论？

本文最重要的不是给出一个新的单变量排序分数，而是否定这种排序思路本身。特征选择必须在协方差结构、预测信号、操纵成本以及 ridge 的表达能力之间做联合权衡。

但结论也有明确边界：模型是一轮博弈、线性预测、二次成本，并假设所有组织共享已知的成本矩阵；真实案例使用半合成响应和人工校准的成本代理。论文没有解决长期动态、组织间成本异质性或显式最坏情形鲁棒优化。

论文声称代码位于 `https://github.com/jivatneet/strategic-feature-selection`，但截至 2026-07-21，对该精确地址的匿名 clone、`git ls-remote`、网页和 GitHub API 检查均返回仓库不存在或 404。因此当前只能依据论文分析，代码实现与论文对应关系为 **Not found**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Strategic Feature Selection

### What problem does it solve?

Strategic prediction systems change the behavior of the organizations they evaluate. In Medicare Advantage, for example, payment coefficients create incentives to report additional or more severe diagnoses. Most strategic-classification work responds by redesigning the predictor, but institutions often have only two coarse controls inside a legacy pipeline: exclude some features and shrink the remaining coefficients. This paper asks how those two controls should be chosen together.

### Main contribution

The paper formalizes support-restricted ridge regression under predictor-induced feature manipulation. Its central conclusion is that manipulability alone is not a valid feature-selection rule. Under optimal ridge tuning, support quality depends on three interacting quantities: strategic burden removed by exclusion, predictive signal lost after accounting for correlated retained proxies, and the heterogeneity of manipulation costs among retained features. Consequently, a highly manipulable but predictive feature may be retained and regularized, while a manipulable feature with a less manipulable correlated proxy may be dropped.

The algorithm replaces combinatorial support search with a weighted continuous relaxation. For each ridge level, it optimizes fractional feature weights under a support budget, rounds to the top-$s$ coordinates, improves that support by exact add/drop/swap moves under strategic MSE, and refits ordinary ridge. The delivered predictor therefore remains a standard sparse ridge model rather than a fractional or custom strategic model.

### Evidence

In 30 low-dimensional synthetic instances ($d=18$, budget $s=5$), exhaustive search supplies the exact support-and-ridge grid oracle. Weighted rounding alone reaches the oracle in 18/30 cases; exact local refinement repairs 12 rounded supports; the complete screen-and-refit method reaches the oracle in all 30. Subset selection without ridge has median normalized strategic MSE 1.34 and maximum 1.82.

The healthcare case study uses 5,000 semi-synthetic beneficiaries, 115 CMS-HCC V28 features (30 with nonzero prevalence), published CMS coefficients, and a policy-calibrated manipulation-ease proxy. At manipulation intensity $\alpha=1$, the $k=25$ support-restricted ridge design reduces post-manipulation MSE by about 40% relative to full ridge, beats top-ten exclusion, prediction-only, cost-only, and subset-only baselines, and remains close to the zero-intercept oracle across manipulation intensities. Although the absolute support optimum is $k=20$, $k=25$ performs nearly identically and retains all six observed HCCs belonging to the policy-defined top-ten diagnosis groups.

### What is genuinely new?

- A theory of feature selection *under optimally tuned scalar ridge* in strategic environments, including an irreducible-gap lower bound and a three-term upper bound.
- A policy interpretation distinguishing predictive loss, removed strategic burden, and retained-cost heterogeneity.
- A weighted screen–round–refine–refit algorithm that returns an ordinary support-restricted ridge estimator.
- An analysis of inherent robustness under uncertain manipulation costs, showing how shrinking or removing uncertain directions can outperform a plug-in intercept correction.

### Limitations and reproducibility

The model assumes one-shot linear interaction, quadratic positive-definite manipulation costs known to the decision maker, and homogeneous costs across organizations. The healthcare evaluation is semi-synthetic: its inverse-cost matrix is explicitly a constructed proxy, not a structural estimate of real insurer costs, and ridge tuning minimizes a deterministic plug-in strategic objective. The paper does not design a worst-case robust method for cost uncertainty.

The arXiv HTML and all 14 figure images were acquired successfully. The paper states that code is available at `https://github.com/jivatneet/strategic-feature-selection`, but anonymous clone, `git ls-remote`, the webpage, and the GitHub API all returned repository-not-found/404 on 2026-07-21. Therefore this workspace is `paper-only`; implementation fidelity and end-to-end reproduction are **Not found** within the searched public scope.

**Reproducibility rating: 2/5.** The mathematical method, optimization targets, tuning grid, semi-synthetic construction, and evaluation protocol are described in substantial detail, but the advertised implementation was unavailable and the empirical cost model contains deliberate policy calibration choices.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
