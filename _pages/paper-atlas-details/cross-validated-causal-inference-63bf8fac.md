---
layout: default
permalink: /paper-atlas/cross-validated-causal-inference-63bf8fac/
title: "Cross-Validated Causal Inference"
nav: false
wide: true
description: "目标是估计实验人群中的平均处理效应（ATE）： 实验数据有随机化或条件无混杂与 overlap，因此可以识别这个目标；但实验昂贵，样本量通常较小。观察数据便宜、量大，却可能有未测混杂、模型设错、协变量分布漂移，甚至与实验人群有不同的处理效应。论文要回答的是：能否在不把观察数据误当成可信因果证据的前提下，用它降低估计方差？"
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
    <h1>Cross-Validated Causal Inference</h1>
    <p>Cross-Validated Causal Inference: a Modern Method to Combine Experimental and Observational Data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2511.00727" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Cross-Validated Causal Inference">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xyang23/cross_validated_causal" target="_blank" rel="noopener noreferrer" aria-label="Open code for Cross-Validated Causal Inference">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Cross-Validated Causal Inference：用实验数据守住因果有效性，用观察数据争取精度

### 1. 论文在解决什么问题？

目标是估计**实验人群中的平均处理效应**（ATE）：

$$
\tau^\star=\mathbb E[Y^{\mathrm{exp}}(1)-Y^{\mathrm{exp}}(0)].
$$

实验数据有随机化或条件无混杂与 overlap，因此可以识别这个目标；但实验昂贵，样本量通常较小。观察数据便宜、量大，却可能有未测混杂、模型设错、协变量分布漂移，甚至与实验人群有不同的处理效应。论文要回答的是：能否在不把观察数据误当成可信因果证据的前提下，用它降低估计方差？

答案是 CVCI（Cross-Validated Causal Inference）：**让实验数据决定因果参数是否可信，让观察数据只负责提供可能有用的完整模型信息。**

### 2. 最重要的识别边界

这篇论文并不是说“无假设就能做因果推断”。它的边界非常清楚：

- 实验样本 $X^{\mathrm{exp}}$ 是 i.i.d.，处理分配满足无混杂和 overlap；因此实验估计量 $\widehat\tau^{\mathrm{exp}}$ 是因果锚点。
- 对观察样本 $X^{\mathrm{obs}}$ 不要求无混杂、i.i.d.、相同协变量、相同 outcome model 或相同 ATE。
- 所以，**ATE 的识别来自实验数据，不来自观察数据**。观察数据只能在其诱导的因果参数与留出的实验数据一致时，作为提高精度的辅助来源。

这一区分也解释了为什么交叉验证必须在实验数据上完成，而不能用观察预测误差选择模型。

### 3. 核心方法：两个 loss 承担两种职责

设 $\theta$ 是完整模型参数，$\beta(\theta)$ 是从中提取的因果参数，例如线性模型中的 treatment coefficient。给定权重 $\lambda\in[0,1]$，拟合

$$
\widehat\theta(\lambda)=
\arg\min_\theta\Big[
(1-\lambda)L^{\mathrm{exp}}(\beta(\theta);X^{\mathrm{exp}})
+\lambda L^{\mathrm{obs}}(\theta;X^{\mathrm{obs}})
\Big].
$$

两个 loss 不对称：

- $L^{\mathrm{exp}}$ 只检查因果参数，常用形式是
  $$
  L^{\mathrm{exp}}(\beta;X^{\mathrm{exp}}_{\mathcal J})
  =(\beta-\widehat\tau^{\mathrm{exp}}(X^{\mathrm{exp}}_{\mathcal J}))^2.
  $$
- $L^{\mathrm{obs}}$ 检查完整模型在观察数据上的拟合，例如线性回归的均方误差。

$\lambda=0$ 就退回实验估计；$\lambda$ 越大，观察数据对完整模型和因果参数的牵引越强。但 $\lambda$ 不是“观察研究正确的概率”，而是由实验验证决定的偏差—方差权衡参数。

### 4. 为什么这里的 cross-validation 不同于普通预测交叉验证？

CVCI 只切分实验样本，把观察样本在每一折中完整复用：

```text
实验数据 ──切成 K 折──┬── K-1 折进入实验因果 loss ──┐
                      └── 1 折只做因果参数验证       │
观察数据 ─────────────── 每折全部进入完整模型 loss ───┤
                                                       ↓
                          对每个 λ 计算 held-out 实验 loss
                                                       ↓
                              选择 λ̂，再用全部数据重拟合
                                                       ↓
                                           输出 β(θ̂(λ̂))
```

数学上，验证准则是

$$
\mathsf{CV}(\lambda)=\frac1K\sum_{k=1}^{K}
L^{\mathrm{exp}}\left(
\beta(\widehat\theta(\lambda;D_{-k}));X^{\mathrm{exp}}_{B_k}
\right).
$$

这相当于让每个 $\lambda$ 定义一个候选模型，再用随机化证据选择因果输出最可靠的模型。如果观察模型诱导的 treatment effect 与实验 holdout 一致，交叉验证可以选择较大权重；如果不一致，就趋向 $\lambda=0$。

### 5. 两个可直接计算的特例

#### 5.1 无协变量：自适应 shrinkage

$$
\widehat\theta(\lambda)
=(1-\lambda)\overline Y^{\mathrm{exp}}+lambda\overline Y^{\mathrm{obs}}.
$$

它把实验均值向观察均值收缩。观察偏差小时，大样本观察均值可以降低方差；偏差大时，实验 holdout 会把 $\widehat\lambda$ 推向 0。

#### 5.2 线性模型：只把 treatment coefficient 锚定到实验结果

观察数据拟合完整线性 outcome model，而实验 loss 约束其第一个系数 $\theta_W$ 接近实验 ATE $\widehat\tau^{\mathrm{exp}}$。闭式方程为

$$
\left((1-\lambda)e_1e_1^\top+
\frac{\lambda}{N^{\mathrm{obs}}}XX^\top\right)\theta
=(1-\lambda)\widehat\tau^{\mathrm{exp}}e_1+
\frac{\lambda}{N^{\mathrm{obs}}}XY.
$$

其直觉是：实验数据负责正则化 treatment coefficient，观察数据负责估计完整响应结构。两个来源不需要共享相同协变量，因为它们真正共享的是一个标量因果参数，而不是原始特征。

实验 ATE 可以来自均值差、plug-in 回归或 AIPW。官方代码中的 AIPW 分支使用已知的 $0.5$ propensity，适用于随机化模拟；它不是通用 propensity estimation 流程。

### 6. 理论到底证明了什么？

理论要求：

1. 实验 ATE 估计量是 $\sqrt{N^{\mathrm{exp}}}$-consistent，并有有界线性展开（LinATE）。
2. 观察 loss 在有界参数空间内强凸、二阶和三阶导数受控（OBS）。
3. 折数 $K$ 与实验样本量满足论文给定的增长条件。

在这些条件下，论文证明

$$
\mathbb E[(\beta(\widehat\theta(\widehat\lambda))-\tau^\star)^2]
\le \frac{C'}{N^{\mathrm{exp}}},
$$

而且这个风险阶对观察偏差保持稳健。无协变量高斯模型中的 minimax 下界说明：若要求估计量对任意观察偏差都稳健，就不能普遍快于 $1/N^{\mathrm{exp}}$。

需要特别注意：这是**估计误差/风险界**，不是渐近正态性、标准误公式或置信区间覆盖率理论。LaLonde 实验中的 bootstrap 只报告重采样和交叉验证共同产生的标准差；官方代码也没有提供通用 CI API。

### 7. 实验告诉了我们什么？

- 无协变量和线性模拟中，观察偏差较小时，CVCI 能利用大样本观察数据降低 MSE；偏差增加后，$\widehat\lambda$ 通常降到 0 附近。
- 更多观察样本可能提高精度，但收益取决于其因果参数与实验是否一致。
- 当实验样本很小、观察偏差极端时，少数非零权重选择会造成很大的平方误差。Figure 4 和 Figure 9 直接展示了这一尾部风险。
- LaLonde 的 48 种配置中，CVCI 都比 observational-only 更接近实验参考值，30/48 比 pooling 更接近。加入更有信息的协变量、选择更相似的观察控制组时，$\widehat\lambda$ 通常更大。
- 这里的实验估计只是有限样本 reference，不应表述为绝对 ground truth。

### 8. 代码实现与论文的对应关系

- `causal_sim.py:75-86`：无协变量闭式估计。
- `causal_sim.py:88-136`：线性闭式方程及奇异矩阵分支。
- `causal_sim.py:154-261`：实验估计量、实验 loss、观察 loss。
- `causal_sim.py:297-348`：遍历 $\lambda$、只切实验数据、复用观察数据、最终全数据 refit。
- `mean_*.py`、`linear_*.py`：模拟图。
- `lalonde_cv.py`、`lalonde_cv_bootstrap.py`：LaLonde 点估计与 bootstrap dispersion。

代码完整覆盖两个主要特例，但没有实现论文提出的任意 parametric loss 通用优化器，也没有 theorem test。`combined_loss` 的 linear 分支还引用了未定义变量 `d`；实际脚本通过闭式 `fit_model` 绕过该函数。论文参数是 50 个 $\lambda$ 候选值和 5000 次重复，而部分脚本当前默认值为 5 和 100，注释中明确标出了差异。

### 9. 如何理解这个方法

CVCI 最准确的定位不是“把 RCT 和观察数据简单融合”，而是：

> 用观察数据提出更精确的候选完整模型，用实验 holdout 决定其因果参数是否值得信任。

它的优势是识别边界清晰、兼容不同协变量和不同 outcome model，并能连续地选择借用程度；它的限制则是实验样本仍决定最坏情况下的统计速率，而且有限样本交叉验证不能完全消除错误借用的风险。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cross-Validated Causal Inference

### Paper summary

This paper develops Cross-Validated Causal Inference (CVCI), a loss-based method for estimating the average treatment effect in an experimental population while using potentially biased observational data for precision. The key separation is that randomized/experimental data identify and validate the causal parameter, whereas observational data fit a richer full model but are granted no causal validity: they may contain unmeasured confounding, model misspecification, non-i.i.d. sampling, covariate shift, different covariates, and a different treatment effect. CVCI minimizes a weighted experimental causal loss plus observational full-model loss, chooses the weight $\lambda$ by held-out **experimental** causal loss, and refits on all data. It therefore borrows observational information when it agrees with randomized evidence and retreats toward experimental-only estimation when it does not.

The paper gives closed forms for no-covariate shrinkage and linear outcome models, plus a general parametric ERM abstraction. Under a $\sqrt{N^{\mathrm{exp}}}$-consistent asymptotically linear experimental estimator and strong-convexity/smoothness conditions on the observational loss, the estimator has expected squared error $O(1/N^{\mathrm{exp}})$ uniformly over observational bias. A Gaussian no-covariate lower bound shows this rate is minimax optimal over a class of estimators required to remain robust to that bias. These are finite-sample estimation-risk guarantees—not asymptotic normality, confidence-interval coverage, or a general inference theory.

### Why existing approaches are insufficient

Pooling can destroy randomized validity and requires observational unconfoundedness. Existing shrinkage methods often require predefined strata or shared effects across sources, while error-prone-estimator approaches require carefully structured bias cancellation. The paper positions CVCI as a softer, data-adaptive alternative that validates only the causal component and does not require aligned covariates, outcome models, or observational treatment effects (`paper.md:102-130`).

### Method in brief

For full-model parameter $\theta$ and causal component $\beta(\theta)$,

$$
\widehat\theta(\lambda)=\arg\min_\theta
\left[(1-\lambda)L^{\mathrm{exp}}(\beta(\theta);X^{\mathrm{exp}})
+\lambda L^{\mathrm{obs}}(\theta;X^{\mathrm{obs}})\right].
$$

Only the experiment is folded. For each $\lambda$, the model is trained on $K-1$ experimental folds plus all observational observations, and its causal output is scored on the held-out experimental fold. The minimizing $\widehat\lambda$ is used for a full-data refit. In the no-covariate case this is a cross-validated weighted mean; in the linear case the experimental loss regularizes the treatment coefficient toward an experimental ATE estimate while observational least squares fits the remaining response model.

### Evaluation and findings

The simulations vary observational bias, experimental/observational sample sizes, noise, and whether source outcome models/covariates align. CVCI generally outperforms at least one single-source estimator, benefits from observational data in low-bias regimes, and moves its selected weight toward zero as bias increases. The figures also reveal a genuine limitation: with small experimental samples and extreme observational bias, rare nonzero weights can cause very large squared errors.

The real-data study uses NSW randomized treatment/control observations and PSID/CPS observational controls from the LaLonde benchmark. Experimental-only estimates serve as a finite-sample reference, not literal ground truth. Across 48 configurations, CVCI is closer to that reference than observational-only estimation in all 48 and closer than pooling in 30. Richer covariates and more comparable observational subgroups receive larger weights. Bootstrap standard deviations are comparable to other estimators, but they are empirical dispersion summaries rather than a demonstrated CI procedure (`paper.md:413-425`).

### Reproducibility

**Rating: 3.5/5.** The official repository at `https://github.com/xyang23/cross_validated_causal` (snapshot `d74cb7c928938fd1a2978481f9aab6ac654c7d08`) implements the mean and linear closed forms, causal cross-validation, simulation sweeps, and LaLonde analyses. The core paper-code match is good for these special cases. Reproduction is weakened by separately downloaded LaLonde files, no dependency lockfile or test suite, checked-in fast defaults (5 lambda bins/100 runs versus 50/5000 stated for the paper), and absence of the generic parametric solver. The linear `combined_loss` branch references undefined `d`, while concrete scripts bypass it through the closed-form path. The AIPW example uses a known 0.5 propensity in randomized simulations. Bootstrap code reports dispersion and should not be represented as a general confidence-interval API.

### Main limitations

- Causal identification still depends on a valid experimental design and estimator.
- Observational data offer possible efficiency, not guaranteed finite-sample improvement.
- The proved class requires a smooth, strongly convex observational loss and does not cover LASSO, elastic net, or Huber as stated.
- Cross-validation can make rare harmful selections under extreme bias and limited experimental data.
- The implementation covers mean/linear cases but not the full general-parametric proposal.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
