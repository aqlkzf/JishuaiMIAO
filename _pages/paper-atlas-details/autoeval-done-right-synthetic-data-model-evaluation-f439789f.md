---
layout: default
permalink: /paper-atlas/autoeval-done-right-synthetic-data-model-evaluation-f439789f/
title: "AutoEval_Done_Right_Synthetic_Data_Model_Evaluation"
nav: false
description: "AutoEval 的关键不是让 AI 代替人类评测，而是让 AI 提供大量低成本、可相关但允许有偏的信号，再用少量人工标签估计偏差并校准不确定性；PPI++ 的 \\lambda 决定这份合成信息究竟值得相信多少。"
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
      <span>Proceedings of the 42nd International Conference on Machine Learning (PMLR 267) · 2025</span>
    </div>
    <h1>AutoEval_Done_Right_Synthetic_Data_Model_Evaluation</h1>
    <p>AutoEval Done Right: Using Synthetic Data for Model Evaluation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2403.07008" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## AutoEval Done Right 方法详解

### 1. 这篇论文解决什么问题？

模型评测通常需要人工或专家标签。标签少时，准确率、相关系数或模型排名的方差很大；让另一个 AI 大规模打标签虽然便宜，却可能有系统偏差。直接把 AI 判断当真，会得到很“稳定”但错误的结论。

AutoEval 的目标是：在只有少量人工标签、但可以获得大量 AI 合成标签时，得到

- 无系统偏差的模型性能估计；
- 能反映不确定性的置信区间；
- 更少并列、更接近真实顺序的模型排名。

论文属于通用的统计机器学习与模型评测方法。ProteinGym 只是其中一个生物学实验，不能因此把整篇论文归类为生信方法。

### 2. 为什么已有做法不够？

1. **只用人工标签**：统计上可靠，但样本量小、区间宽、模型之间经常无法区分。
2. **只用自动评分**：样本量大，但 AI judge、softmax 置信度或代理模型可能有偏差。
3. **普通 PPI，固定 $\lambda=1$**：能够纠偏，但如果合成信号质量差，方差甚至可能高于纯人工方法。
4. **传统排名区间**：可以表达排名不确定性，却无法利用大量合成标签提升精度。

AutoEval 使用 PPI++：既保留人工标签的纠偏作用，又自动决定合成信息应该占多大权重。

### 3. 输入、输出和关键假设

输入包括：

- 小规模人工标注集 $\{(X_i,Y_i)\}_{i=1}^{n}$；
- 大规模未标注输入 $\{X_i^u\}_{i=1}^{N}$，通常 $N\gg n$；
- 标注模型在两组数据上的合成标签或标签分布；
- 待评价模型 $f_1,\ldots,f_M$ 和评价函数 $\phi$。

目标量是

$$
\mu_m=\mathbb E[\phi(f_m(X),Y)].
$$

输出是每个模型的点估计、置信区间，以及由置信区间构造的排名。

最重要的假设是：基础版本中的人工标注样本和未标注样本代表同一个目标总体。若人工样本来自另一分布，基础置信区间会失效，需要使用附录中的重要性加权版本。

### 4. 核心直觉：大样本负责降噪，小样本负责纠偏

```text
大量未标注输入 + AI 合成标签
        │
        ├── 估计模型指标，方差小但可能有偏
        │
少量人工标签 + 同一批样本的 AI 标签
        │
        └── 测量 AI 指标与真实指标之间的偏差
                        │
                        ▼
          合成指标平均值 + 人工纠偏项
                        │
                        ▼
             点估计、置信区间、排名
```

AutoEval 不是假设 AI 标签正确，而是把 AI 标签当作一个与真实指标相关的“控制变量”。

### 5. PPI/PPI++ 估计器

标注模型可以输出一个标签，也可以输出完整的标签分布 $\tilde P_i$。先计算在该分布下的期望评价指标：

$$
\hat{\mathbb E}_{i,m}
=\int\phi(f_m(X_i),y)d\tilde P_i(y).
$$

然后构造

$$
\hat\mu_m=
\frac{\lambda}{N}\sum_{i=1}^{N}\hat{\mathbb E}_{i,m}^{u}
+\frac{1}{n}\sum_{i=1}^{n}
\left[\phi(f_m(X_i),Y_i)-\lambda\hat{\mathbb E}_{i,m}\right].
$$

第一项是在大规模合成数据上得到的低噪声估计；第二项是人工标注样本上的残差，用来纠正第一项的偏差。

对于固定 $\lambda$，两个合成项在期望上相消，因此保留的正是目标指标。三种重要情形是：

- $\lambda=0$：完全不用合成标签，退化为经典人工评测；
- $\lambda=1$：普通 PPI，完全使用合成信号并纠偏；
- 自动估计 $\lambda$：PPI++，选择使渐近方差最小的权重。

所以 PPI++ 的“保险机制”很直观：judge 很差时令 $\lambda$ 接近 0；judge 与真实标签高度相关时令 $\lambda$ 接近 1。

### 6. 置信区间、ESS 与排名

估计量的方差可以拆成两部分：

$$
\frac1nV=
\frac{\lambda^2}{N}\operatorname{Cov}(L_i^u)
+\frac1n\operatorname{Cov}(\Delta_i^\lambda).
$$

前者来自大规模合成平均，后者来自小规模人工纠偏。用样本协方差代入即可构造渐近正态置信区间。

论文用有效样本量 ESS 描述节省了多少人工标签：

$$
\mathrm{ESS}=n\times
\frac{\widehat{\mathrm{Var}}(\hat\mu_{\mathrm{classical}})}
{\widehat{\mathrm{Var}}(\hat\mu_{\mathrm{PPI}})}.
$$

若 $n=500$ 而 ESS 约为 750，意思是 AutoEval 用 500 个人工标签获得了经典方法约 750 个标签的精度。

实验中先做 Bonferroni 校正的 90% 置信区间，再把区间重叠的模型视为并列。这样不会把很小、统计上不明确的差别硬解释成顺序。

### 7. 成对比较与 Bradley--Terry 扩展

LLM 评测常常没有单一“正确答案”，只有人类在两个模型回答之间的偏好。Bradley--Terry 模型写作

$$
P_\zeta(Y=1\mid A,B)=\frac{1}{1+e^{\zeta_A-\zeta_B}},
$$

其中 $\zeta_m$ 表示模型强度。经典方法只最小化人工偏好的交叉熵。AutoEval 的目标是

$$
\frac1n\sum_i
\left[\ell_\zeta(X_i,Y_i)-\lambda\ell_\zeta(X_i,\hat Y_i)\right]
+\frac\lambda N\sum_i\ell_\zeta(X_i^u,\hat Y_i^u).
$$

这仍是“人工真实损失减去同一样本的 AI 损失，再加大规模 AI 损失”。官方 JAX 代码直接实现了这个式子，并用自动微分得到梯度、Hessian 和 sandwich covariance。

### 8. 分布偏移时怎么办？

若人工样本来自 $Q_X$，而生产总体来自 $P_X$，基础纠偏项不能再正确抵消合成偏差。论文假设密度比

$$
w(X)=\frac{dP_X}{dQ_X}
$$

已知，并对人工真实标签部分做重要性加权。ImageNet 的偏移实验中，未加权 90% 区间的覆盖率可跌至约 0.16--0.50，而加权后恢复至约 0.91--0.94。这个修复依赖正确的权重，不能解决任意未知偏移。

### 9. 三组实验说明了什么？

- **ImageNet**：五种 ResNet 的准确率评测，PPI/PPI++ 的 ESS 约提高 50%，PPI++ 排名更接近完整验证集排名。
- **ProteinGym**：七种蛋白语言模型与实验 fitness 的 Pearson 相关性，PPI++ ESS 约提高 50%；$n=1000$ 时排名相关性约有五倍提升。普通 PPI 反而可能比经典方法差。
- **Chatbot Arena**：20 个 LLM 的 Bradley--Terry 排名，主 judge 下 PPI++ ESS 提高约 20--25%，不同 judge 下约提高 20--35%。

所有汇总结果基于 250 次随机人工/未标注划分。图 6 显示区间宽度下降时，覆盖率仍接近标称的 90%。

### 10. 代码覆盖与使用边界

官方代码能够证明核心统计实现：

- `ppi_py_v0_2_2/ppi_py/ppi.py:59-221`：均值类 PPI/PPI++ 点估计和置信区间；
- `autoeval/workflow/scripts/imagenet_experiment.py:216-387`：ImageNet 的 CI、ESS 与排名；
- `autoeval/workflow/scripts/llm_experiment.py:20-227`：Bradley--Terry PPI++ 目标、协方差与 $\lambda$。

但完整复现最终 ICML 论文仍有缺口：ProteinGym 脚本未找到；LLM 脚本仍是较早的 6 模型、固定 $n=25$ 配置；ImageNet Snakemake 中存在脚本文件名、命令参数和 `gt_labels.npy` 生成断链，并且代码使用 500 次而论文报告 250 次划分。因此应把代码理解为“核心方法实现 + 部分实验原型”，而不是完整的一键复现包。

### 11. 一句话理解

AutoEval 的关键不是让 AI 代替人类评测，而是让 AI 提供大量低成本、可相关但允许有偏的信号，再用少量人工标签估计偏差并校准不确定性；PPI++ 的 $\lambda$ 决定这份合成信息究竟值得相信多少。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## AutoEval Done Right: Using Synthetic Data for Model Evaluation

### Problem

Model evaluation often depends on scarce and expensive human or expert labels. Using an LLM or another model to generate many cheap labels reduces sampling noise, but a naive automatic score inherits the annotator's bias and cannot provide trustworthy confidence intervals. The paper asks whether abundant synthetic labels and a small human-labeled sample can be combined to estimate model metrics and rankings more precisely without sacrificing statistical validity.

### Contribution

AutoEval instantiates prediction-powered inference (PPI) and its variance-optimized form PPI++ for model evaluation. It evaluates the target metric over a large synthetic-labeled sample and then uses paired human/synthetic labels in the small labeled sample to estimate and subtract the synthetic bias. The construction handles arbitrary expected metrics, extends to probabilistic annotators that return a distribution over labels, produces asymptotic confidence intervals, and adapts to Bradley--Terry ranking from pairwise preferences. A supplementary importance-weighted version handles a specified covariate shift between labeled and target populations.

The key estimator is

$$
\hat\mu_m=
\frac{\lambda}{N}\sum_{i=1}^N\hat{\mathbb E}^{u}_{i,m}
+\frac1n\sum_{i=1}^n
\left[\phi(f_m(X_i),Y_i)-\lambda\hat{\mathbb E}_{i,m}\right].
$$

For fixed $\lambda$, the synthetic terms cancel in expectation. PPI uses $\lambda=1$; PPI++ estimates $\lambda$ to minimize variance and can fall back toward the human-only estimator at $\lambda=0$ when the annotator is unhelpful.

### Evaluation and findings

- **ImageNet:** five ResNet accuracies are evaluated from softmax distributions. PPI/PPI++ lower MSE, maintain calibrated intervals, and yield about 50% higher effective sample size (ESS); PPI++ improves rank recovery, especially at intermediate label counts.
- **ProteinGym:** seven protein-language-model correlations with measured protein fitness are ranked using a held-out model as annotator. PPI++ delivers about 50% higher ESS and a fivefold rank-correlation improvement at $n=1000$. Plain PPI can underperform the classical estimator, showing why optimized weighting matters.
- **Chatbot Arena:** 20 LLMs are ranked from 16K pairwise comparisons using gpt-4o-mini preferences as synthetic labels. PPI++ improves ESS by 20--25%, with 20--35% gains across alternative judges, while producing tighter, calibrated intervals and more accurate Bradley--Terry estimates.

The experimental rankings use 90% Bonferroni-corrected confidence intervals and treat overlapping intervals as ties. All reported aggregate results average 250 random labeled/unlabeled splits. ESS measures the number of classical human labels needed to match AutoEval's variance.

### Assumptions and limitations

The labeled and unlabeled samples must represent the same production population in the base method. Nonrandom human labeling or distribution shift breaks the stated guarantees; the weighted extension requires the density ratio $dP_X/dQ_X$ to be known or estimated reliably. The main confidence intervals are asymptotic. Better annotators yield larger efficiency gains, but the method does not certify the annotator itself, and PPI with a fixed $\lambda=1$ may be less efficient than human-only inference. AutoEval evaluates already-trained models; it is not a synthetic-data training method.

### Reproducibility

**Assessment: 3/5 (core estimators available; final experiment reproduction incomplete).**

The official `PierreBoyeau/autoeval` snapshot contains the ImageNet and JAX Bradley--Terry implementations and pins `ppi_py` v0.2.2. The exact pinned package implements the PPI/PPI++ point estimator and confidence intervals. However, the released workflow is not end-to-end: its Snakefile calls a missing filename, passes an unsupported argument, and lacks a rule for ground-truth labels; the ImageNet script uses 500 rather than the paper's 250 splits. The ProteinGym experiment is **Not found**, and the checked-in LLM script represents an older six-model/fixed-$n$ setup rather than the final 20-model gpt-4o-mini study. Code-paper fidelity is therefore medium: strong for the statistical core, partial for the final empirical record.

### Bottom line

AutoEval turns synthetic labels into a variance-reduction device rather than treating them as truth. Its practical value comes from the labeled rectifier and PPI++ tuning: annotator bias is estimated from scarce human labels, while abundant automated judgments reduce uncertainty. The gains are real in the three studied domains, but depend on representative sampling and should not be interpreted as unconditional validation of AI judges.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
