---
layout: default
permalink: /paper-atlas/multivariate-conformal-prediction-gaussian-scoring-83467ee1/
title: "Multivariate_Conformal_Prediction_Gaussian_Scoring"
nav: false
wide: true
description: "普通 split conformal prediction 能保证总体平均意义上的边际覆盖率，但它使用一个全局校准阈值：对于噪声较小的输入，集合可能太大；对于噪声较大的输入，集合可能太小。多输出回归还要面对不同输出之间的相关性。本文不属于生物信息学，而是一篇统计机器学习与不确定性量化方法论文。"
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
    <h1>Multivariate_Conformal_Prediction_Gaussian_Scoring</h1>
    <p>Multivariate Standardized Residuals for Conformal Prediction</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2507.20941" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multivariate_Conformal_Prediction_Gaussian_Scoring">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ElSacho/Multivariate_Standardized_Residuals" target="_blank" rel="noopener noreferrer" aria-label="Open code for Multivariate_Conformal_Prediction_Gaussian_Scoring">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多变量标准化残差共形预测：方法详解

### 解决什么问题

普通 split conformal prediction 能保证总体平均意义上的边际覆盖率，但它使用一个全局校准阈值：对于噪声较小的输入，集合可能太大；对于噪声较大的输入，集合可能太小。多输出回归还要面对不同输出之间的相关性。本文不属于生物信息学，而是一篇统计机器学习与不确定性量化方法论文。

### 核心思想

模型对每个输入 $X$ 同时估计均值 $f_\theta(X)$ 和局部协方差 $\Sigma_\phi(X)$，然后把残差白化：

$$
S_{\mathrm{Mah}}(X,Y)=\left\|\Sigma_\phi(X)^{-1/2}(Y-f_\theta(X))\right\|_2.
$$

这个 Mahalanobis 分数同时消除各输出方向的尺度差异和相关性。对校准集上的分数取带有限样本修正的 $(1-\alpha)$ 分位数 $\hat q_\alpha$，新输入的预测集合就是

$$
C_\alpha(X)=\{y:S_{\mathrm{Mah}}(X,y)\leq\hat q_\alpha\}.
$$

几何上它是以 $f_\theta(X)$ 为中心、由 $\Sigma_\phi(X)$ 决定方向和长短轴的椭球。每个输入的椭球不同，但校准只需一个标量阈值。

### 从数据到预测集

```text
训练数据 (X,Y)
  -> 用 Gaussian NLL 学习 f_theta(X) 和 Sigma_phi(X)
  -> 在独立校准集计算局部 Mahalanobis 残差
  -> 得到共形分位数 q_alpha
测试输入 X
  -> 一次前向计算均值和协方差
  -> 直接输出闭式椭球预测集
```

完整协方差用 Cholesky 因子 $\Sigma=LL^\top$ 保证正定。高维输出可用 $\Sigma=D+VV^\top$ 的低秩形式，并借助 Woodbury 恒等式降低计算量。均值可以与协方差联合学习，也可以固定已有黑盒点预测器，只在其上学习残差协方差。

### Gaussian score 与覆盖保证的关系

“Gaussian”主要提供可学习的均值/协方差和闭式椭球几何，并不意味着边际覆盖保证依赖真实数据服从高斯分布。只要校准样本与测试样本可交换，split conformal 仍给出有限样本边际覆盖。

条件覆盖则更强。若真实数据可写成

$$
Y=f(X)+T(X)W,
$$

且标准化噪声 $W$ 与 $X$ 独立，那么正确白化后的残差范数分布不随 $X$ 改变，一个全局阈值也就是各输入的正确阈值。论文在协方差非退化、输出空间紧、分数 CDF 正则以及均值/协方差一致估计等条件下证明渐近条件覆盖；这不是无假设的有限样本条件覆盖。

### 三个扩展

1. **输出缺失**：只取已观测坐标的均值和协方差子块。不同样本的已观测维数不同，因此把平方 Mahalanobis 距离经过相应自由度的 $\chi^2$ CDF 转换到统一的 $[0,1]$ 尺度，再进行共形校准。保证针对“与校准时相同缺失机制下的观测输出”，不自动保证完整向量。
2. **部分输出已揭示**：把输出分成已知 $Y^r$ 和待预测 $Y^h$，用高斯条件分布更新均值，并用 Schur complement 更新协方差。相关性越强，揭示一个坐标后另一个坐标的区间通常越窄。
3. **输出线性变换**：若关心 $MY$ 而不是原始 $Y$，直接使用 $Mf_\theta(X)$ 和 $M\Sigma_\phi(X)M^\top$ 重新校准。对于非单射变换，这通常比先构造原空间集合再投影更紧。

### 实验结论

论文使用异方差 Gaussian/指数噪声合成数据和 8 个真实多输出数据集，对比 HPD、PCP、C-PCP、L-CP、ECM、OT 与 MVCS。各方法的总体边际覆盖大致达到 90%，但本文方法通常获得最小的估计条件覆盖偏差，同时不用 Monte Carlo 采样。聚合图中，Mahalanobis 方法每 1,000 个样本的覆盖评估约 0.06 秒；HPD、PCP 和 C-PCP 分别约为 1300、864 和 3747 秒。该时间不包含模型训练。

### 阅读时最需要注意的边界

- 论文的硬保证是边际覆盖；条件覆盖依赖白化是否充分和估计是否一致。
- 缺失输出校准对完整向量没有一般保证，部分数据集上的完整向量覆盖约降至 81%。
- 椭球在非椭圆分布下可能不是最小体积集合。
- 官方代码的默认 full-Cholesky 路径与论文最一致；low-rank 路径中 $D$ 与 $D^2$ 的语义在不同函数之间不完全一致。
- 校准代码对排序后数组使用 `scores[p]`，相对论文的第 $p$ 个次序统计量似乎多移一位，使用前应修正或核验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multivariate Standardized Residuals for Conformal Prediction

### Problem and contribution

Split conformal prediction gives finite-sample **marginal** coverage, but a single global residual scale can under-cover uncertain inputs and over-cover easy ones. The difficulty is sharper for a multivariate response $Y\in\mathbb{R}^k$: output coordinates may be correlated, their variances may change with $X$, and flexible conditional-density methods usually need expensive Monte Carlo scoring. This paper introduces **multivariate standardized residuals** (listed on the Berkeley page under the earlier title *Multivariate Conformal Prediction via Conformalized Gaussian Scoring*). It learns a feature-dependent mean $f_\theta(X)$ and covariance $\Sigma_\phi(X)$ and uses the local Mahalanobis norm

$$
S_{\mathrm{Mah}}(X,Y)=\left\|\Sigma_\phi(X)^{-1/2}(Y-f_\theta(X))\right\|_2
$$

as the split-conformal score. Calibrating one scalar threshold produces an input-adaptive ellipsoid centered at $f_\theta(X)$ whose axes follow the local covariance. The method retains distribution-free marginal coverage from split conformalization; conditional coverage is asymptotic only under additional assumptions on standardized residuals and consistent estimation.

### Why this is useful

The Gaussian model is primarily a computational device for learning the first two conditional moments, rather than a claim that all responses are Gaussian. It yields a closed-form score and prediction ellipsoid, avoiding inference-time sampling. The same covariance structure also supports:

- calibration when response coordinates are missing, using a chi-square CDF to make scores comparable across observed dimensions;
- post-hoc prediction for hidden coordinates after other coordinates are revealed, via Gaussian conditioning and a Schur complement;
- prediction sets for a linear transformation $MY$, using mean $Mf_\theta(X)$ and covariance $M\Sigma_\phi(X)M^\top$.

The main theorem characterizes a broad sufficient class $Y=f(X)+T(X)W$, where $W$ is standardized and independent of $X$, for which whitening removes the score's dependence on $X$. With compact output space, a uniformly nondegenerate covariance, a regular score CDF, and uniformly consistent mean/covariance estimators, the conditional coverage error converges to zero.

### Evaluation

The paper evaluates heteroskedastic Gaussian and exponential synthetic data and eight real multivariate regression datasets with output dimensions from 2 to 16. Baselines include HPD, PCP, C-PCP, L-CP, empirical covariance (ECM), optimal transport (OT), and MVCS. All methods preserve approximately 90% marginal coverage, but the proposed score generally has the lowest estimated conditional-coverage deviation while remaining much cheaper than sampling-based density methods. For example, the paper's aggregated full-output plot reports 0.06 s per 1,000 coverage evaluations for Mahalanobis scoring, versus 1300.48 s for HPD, 863.75 s for PCP, and 3746.96 s for C-PCP. These timings measure score/coverage evaluation, not model training.

For calibration with missing outputs, coverage of outcomes under the same missingness mechanism remains near the 90% target. Coverage of the *fully observed* vector is explicitly not guaranteed by that calibration and can be much lower (about 81% on scm1d/scm20d in the reported experiment).

### Reproducibility and limitations

The official repository is included at commit `e34bb9aa7cd466d056f43d4b17848ffc1cf404f8`. It contains a reusable `StandardizedResiduals` class, two usage notebooks, experiment scripts/configuration, saved results, and figure notebooks. Core full-Cholesky scoring, Gaussian NLL training, missing-output scoring, conditioning, projection, conformal thresholds, volumes, and coverage are directly represented in code. The repository is research code: it has no automated test suite or packaged release, stored experiment results include a notebook larger than 10 MB, and dependencies/hardware must be reconstructed from the README and requirements file.

Two implementation details deserve care. First, the calibration functions use zero-based `scores[p]` after setting $p=\lceil(n+1)(1-\alpha)\rceil$, whereas the standard order-statistic formula ordinarily indexes the $p$-th element as `scores[p-1]`; this is a conservative one-rank shift and fails when $p=n$. Second, the low-rank branch uses `D` inconsistently as a standard-deviation vector in likelihood/Mahalanobis calculations but as a variance vector in covariance reconstruction, while projection scoring squares it again. The full-Cholesky default does not have this ambiguity. These are source-code observations, not claims made by the paper.

### Bottom line

The method occupies a useful middle ground: richer and more locally adaptive than a global covariance ellipsoid, but simpler and faster than estimating a full multivariate conditional density. Its firm guarantee is finite-sample marginal coverage; improved conditional coverage depends on whether local whitening makes the residual norm approximately invariant across inputs.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
