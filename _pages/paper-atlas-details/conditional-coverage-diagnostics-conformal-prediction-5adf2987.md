---
layout: default
permalink: /paper-atlas/conditional-coverage-diagnostics-conformal-prediction-5adf2987/
title: "Conditional_Coverage_Diagnostics_Conformal_Prediction"
nav: false
wide: true
description: "共形预测（conformal prediction, CP）可以构造预测集合 C\\alpha(X)，并在交换性假设下保证总体覆盖率约为 1-\\alpha。但“总体平均正确”不意味着每类样本都可靠：某些区域可能系统性欠覆盖，另一些区域则过度保守。 理想目标是 但在没有额外分布假设时，精确的条件覆盖通常不可能保证。"
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
      <span>PMLR · 2026</span>
    </div>
    <h1>Conditional_Coverage_Diagnostics_Conformal_Prediction</h1>
    <p>Conditional Coverage Diagnostics for Conformal Prediction</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2512.11779" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Conditional_Coverage_Diagnostics_Conformal_Prediction">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ElSacho/Conditional_Coverage_Estimation" target="_blank" rel="noopener noreferrer" aria-label="Open code for Conditional_Coverage_Diagnostics_Conformal_Prediction">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用分类器诊断共形预测的条件覆盖：ERT 方法详解

### 论文到底在解决什么问题？

共形预测（conformal prediction, CP）可以构造预测集合 $C_\alpha(X)$，并在交换性假设下保证总体覆盖率约为 $1-\alpha$。但“总体平均正确”不意味着每类样本都可靠：某些区域可能系统性欠覆盖，另一些区域则过度保守。

理想目标是

$$
\mathbb{P}(Y\in C_\alpha(X)\mid X)=1-\alpha,
$$

但在没有额外分布假设时，精确的条件覆盖通常不可能保证。因此这篇论文不再设计一个新的 CP 构造算法，而是回答一个更基础的问题：**已有预测集合离条件覆盖还有多远，怎样用有限测试数据可靠地诊断？**

### 现有指标为什么不够？

- CovGap 等分组指标先对特征空间分箱或聚类，再比较各组覆盖率。维度升高后，每组样本少、分区选择敏感，还可能把真正有信息的方向淹没。
- WSC 在许多几何 slab 上搜索最差覆盖率。高维和小样本下，它容易挑中随机向下波动的区域，从而对本来条件有效的预测集合报出假警报。
- SSC、相关性或 HSIC 等指标关注集合大小或辅助表示。当集合宽度恒定但覆盖随 $X$ 改变时，它们可能完全看不出来。

ERT 的关键改变是：不要先规定“在哪些组里看覆盖率”，而是让一个监督学习器主动寻找 $X$ 中最能预测覆盖失败的结构。

### 核心转化：把覆盖诊断变成二分类

对每个测试样本定义

$$
Z_i=\mathbbm{1}\{Y_i\in C_\alpha(X_i)\}.
$$

$Z_i=1$ 表示预测集合覆盖了真实标签，$Z_i=0$ 表示没有覆盖。于是我们得到普通二分类数据 $(X_i,Z_i)$，其真实条件概率为

$$
p(x)=\mathbb{P}(Z=1\mid X=x).
$$

若条件覆盖成立，则 $p(x)$ 应处处等于 $1-\alpha$。对于任意 proper loss $\ell$，预测真实概率的 Bayes 分类器风险最低。因此在条件覆盖成立时，常数预测器 $h_0(x)=1-\alpha$ 已经是最优的；如果某个分类器能在独立数据上稳定胜过它，就说明 $X$ 中存在可预测的覆盖变化。

### ERT 的定义与直觉

分类器 $h$ 的风险为

$$
\mathcal{R}_\ell(h)=\mathbb{E}[\ell(h(X),Z)].
$$

论文定义目标覆盖的超额风险（excess risk of target coverage）：

$$
\ell\text{-ERT}=\mathcal{R}_\ell(1-\alpha)-\mathcal{R}_\ell(p).
$$

实际中不知道 $p$，便用学到的 $h$：

$$
\ell\text{-ERT}(h)=\mathcal{R}_\ell(1-\alpha)-\mathcal{R}_\ell(h).
$$

由于 Bayes 规则 $p$ 不会比 $h$ 更差，必有

$$
\ell\text{-ERT}(h)\leq \ell\text{-ERT}.
$$

所以 ERT 是保守的下界：检测到正值时有明确意义；但接近零不等于证明条件覆盖，可能只是分类器不够强或样本不够多。

### 实际计算流程

```text
已固定的预测集合 C_alpha + 独立评估数据 (X_i, Y_i)
                         |
                         v
             生成覆盖标签 Z_i = 1{Y_i in C_i}
                         |
                         v
                    做 k 折划分
                         |
                         v
       每一折只用其余数据训练概率分类器 h_{-j}
                         |
                         v
             在留出折上预测 h_{-j}(X_i)
                         |
                         v
   计算 loss(1-alpha,Z_i)-loss(h_{-j}(X_i),Z_i)
                         |
                         v
       对所有样本平均，得到 L1/L2/KL 等 ERT
```

交叉拟合非常重要。如果在同一批样本上训练并评估，一个高容量分类器即使面对纯噪声也可能显得优于常数基线，制造虚假的条件覆盖违背。论文主实验使用五折交叉验证；官方 `covmetrics` 实现也按折重建模型并只在留出折计算风险差。

### 不同 loss 给出不同含义

| 指标 | 它估计的总体量 | 解释 |
|---|---|---|
| $L_1$-ERT | $\mathbb{E}|p(X)-(1-\alpha)|$ | 平均绝对条件覆盖偏差，最直观，也最容易估计。 |
| $L_2$-ERT | $\mathbb{E}(p(X)-(1-\alpha))^2$ | 平方偏差，对概率估计精度要求更高。 |
| KL-ERT | $\mathbb{E}D_{\mathrm{KL}}(p(X)\|1-\alpha)$ | 对过度自信的概率错误更敏感。 |

论文进一步证明，任何以目标覆盖率为最小点的凸距离 $f$，都可以通过构造

$$
\ell(p,y)=-f(p)-(y-p)f'(p)
$$

表示成

$$
\ell\text{-ERT}=\mathbb{E}[f(p(X))].
$$

因此 ERT 不是单一指标，而是一个可以根据问题目标选择距离的统一框架。

### 区分过覆盖与欠覆盖

总偏差可以拆成两个方向：

$$
f_+(p)=f(\max\{p,1-\alpha\}),\qquad
f_-(p)=f(\min\{p,1-\alpha\}).
$$

过覆盖意味着集合可能不必要地大；欠覆盖意味着某些区域实际风险高于承诺。官方代码对预测概率相对于 $1-\alpha$ 做单侧截断，然后分别计算 L1、Brier 或 log-loss。这使诊断从“哪里不对”进一步细化为“是过于保守还是不够安全”。

### 论文实验说明了什么？

分类器比较使用 8 个大型 TabArena 回归数据集。TabICLv1.1 找回的 ERT 最大，但速度慢且更依赖 GPU；LightGBM 接近它、CPU 更快，因此被推荐为默认分类器。$L_1$-ERT 比 $L_2$/KL 更容易估计，因为它主要要求判断 $p(X)$ 位于目标的哪一侧，而后两者要求更准确的概率值。

在 8 维异方差模拟中，标准 CP 只有边际覆盖，oracle 集合则按构造满足条件覆盖。1,500 个测试点时，$L_1$-ERT 在无效场景得到 $0.091$，接近真实绝对偏差 $0.098$；在 oracle 场景接近零。CovGap 无法区分两种情况，WSC 和 EOC 又会在有效场景误报。图 1–3 直接显示了 ERT 更快收敛，并能恢复随 $X$ 变化的覆盖曲线。

12 个单变量/多变量回归数据集的 CP benchmark 则显示：降低条件覆盖偏差往往需要更大的预测集合。ERT 提供的是诊断坐标，不替用户决定覆盖质量和集合效率之间应如何取舍。

### 官方代码与关键实现细节

论文发布两个仓库：`covmetrics` 是可安装的指标包，实验仓库保存模拟、分类器比较和 CP benchmark。核心对应关系很完整：

- `ERT.py` 生成交叉拟合概率并计算“常数 loss 减分类器 loss”；
- `losses.py` 实现 L1、Brier/L2、log/KL 及单侧版本；
- `classifiers.py` 中 LightGBM 默认模型还包含内部 8 折集成与概率校准。

外层五折 ERT 与默认分类器内部的校准集成是两层不同操作。代码不会把负的有限样本风险差截成零，这与论文表格中条件有效场景出现轻微负值一致。

### 使用时最容易误解的地方

1. ERT 高说明检测到了可预测的局部覆盖变化；ERT 低不自动证明条件覆盖。
2. $h(x)$ 是覆盖概率的统计代理，不是新的分布无关保证，也不是因果解释。
3. 诊断样本不能被预测集合构造或分类器的对应训练折使用。
4. 分类器应匹配数据模态；论文系统验证主要针对表格数据。
5. 该方法属于统计机器学习与不确定性量化，不应套用生信分析框架。

### 复现边界

核心包、单元测试、两个官方 commit 和 5 张论文图均已保留并核验。完整 benchmark 未运行：它需要外部数据、TabICL/TabPFN 类模型、GPU 资源以及第三方 CP 实现。两个仓库 README 中也没有找到一个能从原始输入一次性重建所有表格和图的统一命令；这一项记为 **Not found**，而不是推测其存在。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Conditional Coverage Diagnostics for Conformal Prediction

### One-paragraph overview

This statistical machine-learning paper introduces **excess risk of target coverage (ERT)**, a family of diagnostics for asking whether conformal prediction sets cover equally well across feature values rather than only on average. It turns evaluation into binary probability estimation: label each held-out example by whether its outcome lies in the set, train a classifier to predict that label from $X$, and measure how much its out-of-sample proper-loss risk improves over the constant target $1-\alpha$. The resulting $L_1$, $L_2$/Brier, and KL variants conservatively estimate interpretable conditional-coverage deviations, can separate over- from under-coverage, and support non-constant target policies.

### Why existing diagnostics are insufficient

Marginal conformal coverage does not rule out severe local failures, but exact distribution-free conditional coverage is unattainable without assumptions. Existing evaluation tools have complementary weaknesses. CovGap and related group metrics depend on arbitrary partitions and need many points per group; worst-case slab coverage (WSC) scans restricted geometric regions and can false-alarm in high dimensions; size-stratified or dependence diagnostics may miss violations when prediction-set size is constant. ERT unifies the evaluation problem around predictive risk and permits modern classifiers rather than fixed bins or slabs.

### Method

Given evaluation pairs $(X_i,Y_i)$ and a fixed predictive-set rule $C_\alpha$, form $Z_i=1\{Y_i\in C_\alpha(X_i)\}$. Under conditional validity, $\mathbb{P}(Z=1\mid X)=1-\alpha$, so no classifier should beat the constant $1-\alpha$ under a proper score. ERT is the constant predictor's risk minus the Bayes conditional-probability risk; the operational estimator substitutes cross-fitted probabilities $h(X_i)$. Because any learned $h$ is no better than the Bayes rule in population, learned ERT lower-bounds the corresponding true divergence. This one-sided guarantee is useful for detecting violations, but a near-zero estimate is not proof of validity when the classifier is weak or data are scarce.

### Evidence

On eight large TabArena regression datasets, the paper compares seven classifier choices over multiple test sizes with five-fold evaluation and ten repetitions. TabICLv1.1 recovers the most ERT but is GPU-oriented and slower; LightGBM is close, much faster, and selected as the practical default. In an eight-dimensional heteroskedastic simulation with 1,500 test points, $L_1$-ERT is $0.091$ for conditionally invalid sets against a true absolute deviation of $0.098$, then falls near zero for oracle conditional sets. CovGap fails to separate these cases, while WSC and EOC false-alarm in the valid case. A 12-dataset univariate/multivariate regression benchmark further shows that smaller conditional deviation often trades off against larger prediction-set volume.

### Code and reproducibility

Two official repositories are preserved. `covmetrics` implements ERT, the proper losses, one-sided variants, default LightGBM classifier, baselines, and unit tests; the experiment repository contains classifier comparisons, simulations, CP benchmarks, parameters, and plotting code. Direct source inspection found a high match between the central equations and package behavior, including five-fold held-out scoring and raw (not clipped) risk differences. Full figures/tables were not rerun because the experiment suite depends on external benchmark data, TabICL/TabPFN-class models, GPU resources, and incorporated third-party CP code. A single top-level reproduction command was **Not found**.

### Limitations

- Statistical power is inseparable from classifier quality and representation choice.
- Cross-fitting prevents obvious in-sample optimism but does not make finite-sample ERT an exact hypothesis test.
- Slight negative values are possible and indicate estimation noise or an inferior learned predictor.
- The main systematic classifier comparison is for tabular data; other modalities are proposed extensions.
- ERT diagnoses coverage but does not itself modify conformal sets or decide the acceptable efficiency trade-off.

### Identity and classification

Canonical identity is arXiv `2512.11779`, **Conditional Coverage Diagnostics for Conformal Prediction**, by Sacha Braun, David Holzmuller, Michael I. Jordan, and Francis Bach, listed for ICML 2026. Jordan's publication HTML attached this ID to the preceding MDP entry; the workspace follows the current arXiv title/authors and records the mislink in `logs/preflight_and_identity.md`. This is a machine-learning/statistics method paper, not a bioinformatics paper.

**Reproducibility rating: 4/5.** Core method code, tests, experiments, commits, and local figures are available; the missing point reflects the substantial external dependencies and absence of a unified end-to-end reproduction entry point.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
