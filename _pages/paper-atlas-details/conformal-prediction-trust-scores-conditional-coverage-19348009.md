---
layout: default
permalink: /paper-atlas/conformal-prediction-trust-scores-conditional-coverage-19348009/
title: "Conformal_Prediction_Trust_Scores_Conditional_Coverage"
nav: false
wide: true
description: "标准 split conformal prediction 能保证 但这是对所有测试样本平均后的边际覆盖率。例如，90% 的简单样本全部覆盖、10% 的困难样本全部漏掉，整体仍然可以达到 90%。真正理想的是对每个 X=x 都覆盖，但有限样本下不可能同时获得非平凡、分布无关的精确 X-条件覆盖。"
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
    <h1>Conformal_Prediction_Trust_Scores_Conditional_Coverage</h1>
    <p>Conformal Prediction Sets with Improved Conditional Coverage using Trust Scores</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/jivatneet/conditional-conformal-trust" target="_blank" rel="noopener noreferrer" aria-label="Open code for Conformal_Prediction_Trust_Scores_Conditional_Coverage">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 基于 Trust Score 改善条件覆盖的共形预测

### 这篇论文解决什么问题？

标准 split conformal prediction 能保证

$$
\mathbb P\{Y_{n+1}\in\mathcal C(X_{n+1})\}\ge 1-\alpha,
$$

但这是对所有测试样本平均后的**边际覆盖率**。例如，90% 的简单样本全部覆盖、10% 的困难样本全部漏掉，整体仍然可以达到 90%。真正理想的是对每个 $X=x$ 都覆盖，但有限样本下不可能同时获得非平凡、分布无关的精确 $X$-条件覆盖。

论文因此不声称解决完整的 $X$-conditional coverage，而是问：能否找到一个低维统计量，专门识别标准共形预测最容易漏掉的样本，再针对这个统计量做条件校准？

这是一篇**统计机器学习 / 共形预测**论文。Fitzpatrick 17k 医学图像只是一个高风险应用实验，不应把论文归为生物信息学。

### 核心观察：高置信度 + 真实类别排名差

令 $\hat f_y(x)$ 为分类器对类别 $y$ 的 softmax 概率：

$$
\operatorname{Conf}(x)=\max_y\hat f_y(x),
$$

$\operatorname{Rank}(x,y)$ 是真实类别 $y$ 在所有类别概率降序中的名次。论文发现，APS 型共形集合的漏覆盖主要集中在分类器“自信但错得离谱”的区域：

- 在 Rank 相近时，Conf 越高，覆盖率越低；
- 在 Conf 相近时，真实类别 Rank 越差，覆盖率越低。

因此 $(\operatorname{Conf},\operatorname{Rank})$ 很适合描述漏覆盖风险。但测试时不知道 $Y_{n+1}$，也就无法计算真实类别 Rank。

### 用 Trust score 代理未知 Rank

论文使用 penultimate-layer 特征空间中的非参数 Trust score。设 $\hat y$ 为模型预测类别，$\tilde y$ 为离测试点最近、但类别不同于 $\hat y$ 的训练类，则实验中的简化版本为

$$
\operatorname{Trust}(x)
=\frac{d(x,\text{最近的非预测类样本})}
{d(x,\text{最近的预测类样本})}.
$$

Trust 较大表示测试点在局部几何上更支持模型预测，Trust 较小表示其他类别在特征空间中更近。原始 Jiang et al. 方法还有低密度过滤；本论文为效率明确跳过该步骤，代码也使用每类一个 FAISS `IndexFlatL2` 直接计算距离比（`utils/compute_trust_score.py:33-73`）。

要特别注意：Trust 只是 Rank 的代理，不是真实标签、真实 Rank 或 Bayes 分类器的直接观测。论文中 Trust 与 Rank 的 Spearman 相关为 $-0.29$ 到 $-0.53$，但散点仍很分散，这正是方法的主要局限。

### 条件共形校准的数学目标

论文把条件目标缩减为 $V=(\operatorname{Conf},\operatorname{Trust})$。Gibbs et al. 的思路是：不对所有可测函数要求条件覆盖，而只对选定函数类 $\mathcal F$ 要求覆盖误差矩平衡：

$$
\mathbb E\left[f(X_{n+1})
\left(\mathbbm 1\{Y_{n+1}\in\mathcal C(X_{n+1})\}-(1-\alpha)\right)\right]=0,
\quad f\in\mathcal F.
$$

若 $\mathcal F$ 包含常数函数，边际覆盖目标也包含在其中。保证只相对于所选 $\mathcal F$ 成立，不能解释为任意 $x$ 上的精确条件覆盖。

对测试点的一个候选得分 $s$，算法把它加入校准集，通过 pinball loss 拟合条件分位数：

$$
\hat g_s=\arg\min_{g\in\mathcal F}\frac{1}{n+1}
\left[\sum_{i=1}^n\ell_\alpha(g(X_i),s_i)
+\ell_\alpha(g(X_{n+1}),s)\right].
$$

然后对每个候选类别 $y$ 判断：

$$
y\in\mathcal C(X_{n+1})
\iff
s(X_{n+1},y)\le
\hat g_{s(X_{n+1},y)}(X_{n+1}).
$$

因此每个测试点、每个候选标签都有自适应阈值，而不是所有点共用一个全局分位数。

### 理论函数类与实验函数类并不相同

论文的 indicator function class 使用 Conf 区间和 Trust 区间的指示函数，可直接对应分组条件覆盖推论；代码在 `core/run_condconf.py:82-118` 实现了这条路径。

但大规模实验使用的是更便宜的五阶多项式基：

$$
\Phi(X)=\{\operatorname{Conf}(X)^i\operatorname{Trust}(X)^j:i+j\le d\},
\qquad d=5.
$$

`PolynomialFeatures(5)` 生成截距及所有总次数不超过 5 的交互项（`core/run_condconf.py:120-146`）。它能平滑建模 Conf 与 Trust 的高阶交互，但不等同于对每个经验分箱给出严格的 indicator 保证。

此外，`conditional (NAIVE)` 是另一条 baseline：对每个 Conf×Trust **联合分箱**分别计算经验分位数。它不是 indicator-basis conditional solver，不能混为一谈。

### 完整计算流程

```text
训练/校准/测试图像或缓存特征与 logits
        |
        +--> 模型 penultimate features --> 每类 FAISS 索引 --> Trust
        |
        +--> softmax/APS/RAPS score ------> Conf
                                             |
                           [Conf, Trust] --> 五阶多项式 Phi
                                             |
校准 scores ------------------------------> 条件共形 LP
                                             |
每个测试点 × 每个候选类别 ----------------> 自适应 cutoff
                                             |
                 prediction set + coverage + set size
                                             |
                CovGap / class / local-ball / group metrics
```

主实验设 $\alpha=0.1$、使用 temperature scaling 和非随机 APS。随机化版本可对相应函数类得到等式型的 $1-\alpha$ 覆盖；实验采用确定性版本，目标是至少达到 $1-\alpha$，避免同一样本每次产生不同集合。

### 实验与结果

四个通用数据集为 ImageNet、ImageNet-LT、Places365、Places365-LT；临床应用为包含 114 种皮肤病标签和 1–6/Unknown skin type 的 Fitzpatrick 17k。指标包括：

- 边际覆盖率和平均集合大小；
- Conf×Trust、Conf×Rank、class-conditional CovGap；
- penultimate 特征空间随机 $\ell_2$ 邻域的 local CovGap；
- Fitzpatrick skin-type CovGap 与 worst-group coverage。

在约 90% 边际覆盖下，Conf×Rank CovGap 分别从 $33.12\to23.66$、$19.92\to17.09$、$25.58\to22.09$、$13.23\to11.75$。但代价并不统一：ImageNet 上 APS 平均集合大小从 4.32 增到 22.36，而 Places365-LT 从 43.46 降到 37.07。

Fitzpatrick 17k 中，提出的方法在校准时不使用 skin-type 标签，skin-type CovGap 从 1.88 降到 1.73，worst-group coverage 从 0.86 升到 0.87，class CovGap 从 7.69 降到 7.47；平均集合大小从 27.30 增至 30.17。这说明条件覆盖指标有小幅改善，但不能据此声称临床有效性或普适公平性。

### 如何正确理解贡献与边界

1. **贡献不是精确 $X$-条件覆盖**，而是围绕已识别漏覆盖机制构造实用的低维条件目标。
2. **Trust 不是 oracle**。如果特征空间不好、每类样本不足，或 Trust 与真实 Rank 相关性弱，方法可能没有改善。
3. **函数类决定保证内容**。实验中的五阶多项式只对其张成空间施加矩条件，不保证每个经验小格都精确为 90%。
4. **集合大小是重要代价**，不能只比较 CovGap。
5. **计算成本较高**：每个测试点和候选标签都要计算条件 cutoff；多项式次数越高，基维数和求解成本越大。
6. **复现状态为中等**：官方代码覆盖核心算法与评估，但本地缺少原始数据、缓存特征、Trust 数组、结果文件和自动化测试，因此尚未数值复现论文表格。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Conformal Prediction Sets with Improved Conditional Coverage using Trust Scores

### Paper summary

Standard split conformal prediction can guarantee that a prediction set contains the true class with probability at least $1-\alpha$ **on average**, while still failing systematically on the cases where uncertainty matters most. This paper shows that APS-style conformal sets under-cover when a classifier is highly confident but ranks the true label poorly. Because true-label rank is unavailable at test time, it proposes a practical two-dimensional surrogate: maximum softmax confidence plus a nonparametric Trust score derived from nearest-class distances in the classifier's penultimate feature space. This is a statistical machine-learning paper about conformal prediction; Fitzpatrick 17k medical images are one application, not a bioinformatics contribution.

The method inserts this Conf/Trust statistic into the conditional-conformal framework of Gibbs et al. Instead of attempting impossible distribution-free coverage conditional on the full high-dimensional $X$, it asks coverage errors to balance over a selected finite-dimensional function class. For every test point and candidate label, the algorithm augments calibration quantile regression with that candidate score, solves the pinball-loss conditional conformal problem, and includes the label when its score falls below the resulting point-specific cutoff. The exact indicator class connects to a Conf/Trust group guarantee; the practical experiments use all bivariate monomials through degree five, trading a literal binwise guarantee for a smoother and computationally tractable approximation. The deterministic experimental version retains an at-least-coverage guarantee relative to the function class; only the randomized construction yields exact equality.

### Evaluation and findings

Experiments use ImageNet, ImageNet-LT, Places365, Places365-LT, and Fitzpatrick 17k with a 90% coverage target. They compare standard split conformal, a Mondrian-like naive joint-bin baseline, and the proposed method. Evaluation includes marginal coverage, average set size, Conf×Trust and Conf×Rank CovGap, class-conditional CovGap, coverage over random local feature-space balls, and Fitzpatrick skin-type/worst-group metrics.

At approximately 90% marginal coverage, the proposed method reduces Conf×Rank CovGap on all four general datasets: $33.12\to23.66$ (ImageNet), $19.92\to17.09$ (ImageNet-LT), $25.58\to22.09$ (Places365), and $13.23\to11.75$ (Places365-LT). Conf×Trust CovGap also improves over standard in all four, though the naive baseline is better on Places365. The tradeoff is real: APS set size on ImageNet rises from 4.32 to 22.36, while Places365-LT sets become smaller. On Fitzpatrick 17k, without skin-type labels during proposed calibration, skin-type CovGap improves from 1.88 to 1.73, worst-group coverage from 0.86 to 0.87, and class CovGap from 7.69 to 7.47, with average set size increasing from 27.30 to 30.17. These results support improved approximate conditional behavior, not exact $X$-conditional validity or demonstrated clinical benefit.

### What is novel

- A miscoverage analysis that isolates the high-confidence/poor-true-rank failure region of marginally valid APS-style sets.
- A label-free test-time proxy, $(\operatorname{Conf},\operatorname{Trust})$, designed specifically around that failure mode rather than around predeclared demographic groups.
- A practical function class for Gibbs-style conditional conformal calibration that can improve unobserved class, local-neighborhood, and demographic coverage without using those group labels in calibration.
- A broad evaluation suite that separates marginal validity from conditional utility and makes set-size costs visible.

### Assumptions and limitations

The underlying validity statements require exchangeability/IID structure, and the quoted finite-dimensional theorem additionally assumes continuity of $s\mid X$. Guarantees are indexed by the chosen function class: degree-five Conf/Trust polynomials do not ensure exact coverage at every feature point or every empirical bin. Trust quality depends on meaningful feature geometry, sufficient per-class data, and its correlation with true-label rank; the paper's scatterplots show substantial noise. Polynomial degree is dataset-specific and becomes expensive above five. Finally, conditional improvements can require much larger sets.

### Reproducibility

**Rating: 3/5.** The pinned first-author repository is an authentic and fairly complete implementation of the core algorithm. Direct source reads match Trust computation, APS/RAPS/softmax scores, polynomial features, conditional cutoff construction, and all primary evaluation metrics. Fidelity is assessed as **medium** because raw datasets, cached features, precomputed Trust arrays, result files, and model assets are external and absent locally, while no automated tests were found. The repository offers download/run scripts and notebooks, but this snapshot cannot reproduce the reported tables immediately. No formal archival venue or non-arXiv DOI was found in the recorded arXiv/Crossref/OpenAlex search scope; the source should be cited as arXiv:2501.10139v2 (2025).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
