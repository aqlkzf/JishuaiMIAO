---
layout: default
permalink: /paper-atlas/structured-matrix-scaling-0f4656e9/
title: "Structured Matrix Scaling"
nav: false
description: "分类器给出的 softmax 概率往往不等于真实事件发生概率。后校准用一小份带标签的校准集，在不重新训练原分类器的情况下修正这些概率。困难在于：校准样本通常很少，但类别数 k 可能很大。 温度缩放（TS，Guo 等，ICML 2017）只有一个参数，稳定但只能统一调节置信度； 向量缩放（VS）能为每类设置不同尺度和截距，但不能表达类别之间的相互影响；"
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
      <span>AISTATS · 2026</span>
    </div>
    <h1>Structured Matrix Scaling</h1>
    <p>Structured Matrix Scaling for Multi-Class Calibration</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2511.03685" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Structured Matrix Scaling（SMS）方法详解

### 这篇论文解决什么问题？

分类器给出的 softmax 概率往往不等于真实事件发生概率。后校准用一小份带标签的校准集，在不重新训练原分类器的情况下修正这些概率。困难在于：校准样本通常很少，但类别数 $k$ 可能很大。

- 温度缩放（TS，Guo 等，ICML 2017）只有一个参数，稳定但只能统一调节置信度；
- 向量缩放（VS）能为每类设置不同尺度和截距，但不能表达类别之间的相互影响；
- 矩阵缩放（MS）可表达跨类别关系，却有 $k(k+1)$ 个参数，容易在小校准集上严重过拟合；
- Dirichlet calibration（Kull 等，NeurIPS 2019）对矩阵缩放加正则，但本文实验中仍不够稳定且计算较慢。

SMS 的核心不是发明一种完全不同的分类模型，而是把矩阵缩放拆成有明确含义的参数组，并按参数组大小、类别数和校准样本数分别控制复杂度。

### 理论动机：为什么不能只用一个温度？

论文考虑一个理想化情形：各类别条件下的分类器 logit 服从不同均值、不同协方差的高斯分布。经 Bayes 公式推导，正确的后验概率一般是 centered logits 的二次 softmax 函数：

$$
g(x)=S\!\left(S^{-1}(x)^\top\mathbf A S^{-1}(x)+B S^{-1}(x)+C\right).
$$

只有当各类别协方差相同时，二次项才可忽略，此时矩阵缩放足够。这个推导不是说真实网络的 logits 一定高斯，而是说明：即便在简单模型中，一个全局温度也可能表达能力不足。

完整的多类二次模型需要 $O(k^3)$ 个参数，实际更易过拟合。因此论文选择 $O(k^2)$ 的矩阵模型，并重点解决其统计稳定性。

### SMS 与 TS、VS、MS 的关系

先令 $z=S^{-1}(x)$ 表示输入概率对应的 logits。SMS 使用

$$
g_{\mathrm{SMS}}(x)=S\!\left(
[I_k+\operatorname{diag}(v)+(\mathbf 1_k\mathbf 1_k^\top-I_k)\odot M]z+b
\right).
$$

三个可学习参数组分别是：

- $b$：每个类别的截距，修正类别基准概率；
- $v$：对角线增量，相当于每类独立的温度修正；
- $M$ 的非对角元素：表达一个类别的 logit 对另一个类别校准结果的影响。

它以单位矩阵 $I_k$ 为中心。正则极强时，$b,v,M$ 被压到零，模型退回预处理后的原 logits；不会把输出压成均匀分布。

从模型族看：

```text
TS：一个全局尺度
 └─ VS/SVS：每类尺度 + 每类截距
     └─ MS/SMS：再加入跨类别的非对角关系
```

SMS 与普通 MS 的表达形式相近，关键差别是 SMS 对不同结构分别正则化。SVS 是去掉非对角矩阵 $M$ 的版本，参数量为 $O(k)$，适合类别数很大的任务。

### 结构化正则目标

SMS 在校准集上最小化交叉熵与三组惩罚：

$$
\begin{aligned}
\min_{b,v,M}\quad &\frac{1}{n_{\mathrm{cal}}}\sum_i
\ell(g_{\mathrm{SMS}}(x_i),y_i)\\
&+\lambda_b\frac{k^\rho}{n_{\mathrm{cal}}^\tau}\lVert b\rVert_\delta
+\lambda_v\frac{k^\rho}{n_{\mathrm{cal}}^\tau}\lVert v\rVert_\delta
+\lambda_M\frac{[k(k-1)]^\rho}{n_{\mathrm{cal}}^\tau}\lVert M\rVert_\delta.
\end{aligned}
$$

这个设计把偏差—方差权衡显式写进正则强度：

1. $n_{\mathrm{cal}}$ 越大，正则可越弱，让模型利用更多结构；
2. 参数组越大，正则越强，尤其保护有 $k(k-1)$ 个参数的非对角组；
3. 三个 $\lambda$ 可独立设置，不必假设截距、对角和跨类别关系具有相同可信度。

论文报告的默认配置为 ridge、$\rho=\tau=1$、三个组系数均为 1。因此截距和对角组的有效强度为 $k/n_{\mathrm{cal}}$，非对角组为 $k(k-1)/n_{\mathrm{cal}}$。这些默认值不是在每个测试数据集上调出来的，而是通过独立的合成任务元优化选择。

### 为什么先做温度缩放？

相同大小的参数变化，在不同 logit 尺度上产生的概率变化不同。若直接正则化，过度自信和不够自信的分类器需要完全不同的 $\lambda$。论文先拟合 TS，把不同分类器拉到较统一的尺度，再让 SMS 学习相对于单位映射的结构增量。

代码中这一步使用 `ts-mix`，含 Laplace smoothing，用于避免校准准确率为 100% 等边界情况下出现无限温度。概率转 logits 时还会把极小概率的对数裁剪到 float32 最小正规数的对数附近（约 $-90$），避免 $-\infty$。

### 优化如何实现？

- ridge 目标可微：当前代码对较小参数向量使用 BFGS，超过 1,000 个参数时使用 L-BFGS；
- LASSO、group LASSO、MCP、ridge 或无惩罚：使用 Numba 编译的 SAGA；
- SAGA 每次更新残差矩阵 $W_\Delta$，随后分别对截距、对角、非对角坐标执行对应的 proximal 操作；
- ridge/LASSO/MCP 可逐坐标收缩，group LASSO 则按整组范数收缩；
- 可计算对偶目标时用 primal–dual gap 停止，否则比较相邻 primal objective。

### 完整计算流程

```text
冻结分类器输出的校准概率 + 标签
              │
              ▼
检查概率；稳定地转换为 logits
              │
              ▼
拟合并保存 temperature scaling（ts-mix）
              │
              ▼
按 k、n_cal 计算三组正则强度
              │
              ▼
拟合 SVS 或 SMS
  ridge → BFGS/L-BFGS
  非光滑惩罚 → proximal SAGA
              │
              ▼
测试时重复温度变换，应用仿射 logit 映射
              │
              ▼
稳定 softmax → 校准后的多类概率
```

### 实验结论

主实验使用 TabRepo：65 个多类数据集、7 类模型、3 个测试折选择，共 1,365 次实验。比较 no calibration、isotonic、多个 TS 实现、普通 VS/MS、Dirichlet、SVS 和 SMS，并在独立测试预测上比较 log loss 与 Brier score 的变化。

- Table 1 中 SMS 的平均 Brier 变化为 $-0.0046$、log-loss 变化为 $-0.0210$，均为最优；
- Figure 1 直观看到普通 MS 有很长的有害正尾，而 SMS 的分布主要落在改善区间；
- Figure 2 中 SMS 的平均 rank 为 1.9，是唯一显著优于所有对照的方法；
- Figure 3 显示其实现比 Dirichlet calibration 约快 70 倍；
- CIFAR-10/100 上 SMS 也稳定；ImageNet 有 1,000 类，完整矩阵需要超过一百万参数，因此只评估到向量级方法。

### 代码对应与局限

代码—论文一致性为 **high**。`probmetrics/probmetrics/calibrators/logistic.py` 直接实现 SMS/SVS、温度预处理、三组正则和优化器选择；`probmetrics/probmetrics/saga/matrix_scaling.py` 实现 SAGA 与各类 proximal operator；实验仓库保存 benchmark 脚本和结果 notebook。

需要注意：

- SMS 仍是 $O(k^2)$，超大类别数应优先用 SVS 或进一步加结构；
- 高斯推导只是模型复杂度的动机，不保证真实 logits 满足高斯假设；
- 默认超参数具有经验性，不保证所有应用最优；
- TabRepo 实验复用了早停/模型选择所用的 validation predictions 来拟合校准器，论文明确承认这不是最严格的独立校准协议；
- 完整数值复现仍需外部 TabRepo 预测、视觉 logits 和冻结的历史依赖环境。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Structured Matrix Scaling for Multi-Class Calibration

### Paper in one paragraph

This machine-learning methods paper makes full multiclass matrix scaling usable when calibration data are scarce. It first temperature-normalizes a classifier's probability outputs, then learns an identity-centered affine transformation of the logits whose intercept, diagonal, and off-diagonal groups receive separate penalties scaled by the number of classes and calibration samples. This **Structured Matrix Scaling (SMS)** hierarchy contains temperature-, vector-, and matrix-like corrections while shrinking unsupported complexity. Across 1,365 multiclass tabular experiments, SMS has the best average Brier and log-loss changes and is the only method significantly better than every comparator in the dataset-level log-loss rank analysis.

### Problem and existing limitations

Post-hoc calibration reserves labeled predictions to align reported class probabilities with observed outcomes. The calibration set is usually much smaller than the classifier's training set, producing a sharp bias–variance tradeoff:

- temperature scaling (Guo et al., ICML 2017) is stable but can only change global confidence;
- vector scaling adds classwise scales/intercepts but cannot model cross-class interactions;
- full matrix scaling is expressive but has $k(k+1)$ parameters and often overfits;
- Dirichlet calibration (Kull et al., NeurIPS 2019) regularizes matrix scaling, but the paper finds its conventional configuration slow and insufficiently robust in these benchmarks.

A Gaussian class-conditional logit calculation further shows that the optimal logistic recalibrator may even be quadratic; thus the issue is not that richer maps are unnecessary, but that they need better statistical control.

### Method

SMS applies three steps:

1. **Robust preprocessing.** Convert probabilities to finite logits and fit temperature scaling (`ts-mix` in code) so classifiers with different confidence scales enter the structured stage comparably.
2. **Identity-centered structured regression.** Fit
   $$
   g(x)=S\!\left([I_k+\operatorname{diag}(v)+\operatorname{offdiag}(M)]S^{-1}(x)+b\right).
   $$
3. **Group-adaptive regularization.** Penalize $b$ and $v$ proportional to $k^\rho/n_{\mathrm{cal}}^\tau$, and off-diagonal $M$ proportional to $[k(k-1)]^\rho/n_{\mathrm{cal}}^\tau$. The reported defaults use ridge with $\rho=\tau=1$ and unit coefficients; BFGS/L-BFGS handles ridge, while a Numba SAGA solver supports ridge, LASSO, group LASSO, and MCP.

SVS removes the off-diagonal group and provides an $O(k)$ alternative for very large class counts.

### Evaluation and findings

The primary benchmark uses TabRepo predictions from seven model families, 65 multiclass datasets, and three held-out-fold choices (1,365 experiments). Baselines include no calibration, isotonic regression, multiple TS implementations, unregularized VS/MS, and Dirichlet calibration. Proper-score differences on held-out test predictions are the main metrics.

- **Table 1:** SMS achieves mean Brier difference $-0.0046$ and log-loss difference $-0.0210$, best among compared methods.
- **Figure 1:** unregularized MS has a large harmful tail, while SMS remains mostly beneficial.
- **Figure 2:** SMS has average log-loss rank 1.9 and is the sole statistically significant winner under the dataset-level Friedman/Nemenyi comparison.
- **Figure 3:** the optimized SMS implementation is roughly 70 times faster than Dirichlet calibration in the reported CPU benchmark.
- **Vision results:** SMS is best or nearly best on CIFAR-10/100. Full matrix methods are not attempted on 1,000-class ImageNet because of their quadratic parameter count; SVS remains applicable.

### Code and reproducibility

**Code-paper fidelity: high.** The official `probmetrics` snapshot directly implements temperature preprocessing, group-scaled regularization, SMS/SVS estimators, BFGS/L-BFGS, proximal SAGA, and stable probability/logit handling. The separate official `LogisticCalibrationBenchmark` snapshot contains binary, multiclass, and vision benchmark scripts plus result notebooks.

Full numerical reproduction requires external TabRepo predictions and vision logits, as well as pinning the current package/dependency state to a paper-era environment. The method itself is usable through a scikit-learn-style API. The arXiv v2 PDF includes the supplement and was converted successfully; 17 linked figures were visually inspected.

### Limitations

- SMS remains $O(k^2)$ in parameters and is unsuitable for extremely large $k$ without additional structure; SVS is the practical fallback.
- Gaussian theory motivates expressiveness but is not an empirical assumption validated for each dataset.
- Default regularization is meta-selected rather than universally optimal.
- The tabular protocol reuses validation predictions for early stopping/model selection and calibration, which the paper acknowledges may increase overfitting risk.
- Current independent metadata confirms arXiv v2 (2025 preprint, revised 2026); AISTATS 2026 is listed by the author's publication page and code documentation, while an archival PMLR record was not located during this run.

### Reproducibility rating

**4/5.** Core implementation and experiment code are public and closely matched to the paper; one point is withheld because key benchmark prediction inputs are external and the exact historical environment is not frozen locally.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
