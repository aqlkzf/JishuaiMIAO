---
layout: default
permalink: /paper-atlas/variational-estimator-lp-calibration-errors-daf69640/
title: "Variational_Estimator_Lp_Calibration_Errors"
nav: false
description: "该方法把难以直接估计的 Lp 概率校准距离，改写成“原始预测与交叉拟合重校准预测之间的、随样本预测而变化的 proper-loss 风险差”，从而避免分箱，并在期望意义下控制过度估计。"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Variational_Estimator_Lp_Calibration_Errors</h1>
    <p>A Variational Estimator for L^p Calibration Errors</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.24230" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用变分方法估计 $L_p$ 校准误差

### 这篇论文要解决什么问题？

分类器输出的概率不只用于选类别，还应当有概率意义。例如，在所有预测为 0.8 的样本中，真实标签出现的频率应接近 0.8。设分类器输出为 $f(X)\in\Delta_k$，在给定输出后真实的类别概率为

$$
C=\mathbb E[Y\mid f(X)].
$$

论文关注的目标是

$$
\mathrm{CE}_{\|\cdot\|_p}(f)
=\mathbb E[\|f(X)-C\|_p],\qquad p\ge1.
$$

难点是 $C$ 不可直接观察。传统 ECE 把概率划分成若干箱，再比较箱内平均置信度与准确率；它依赖箱数，在小样本下有偏，而且多分类概率位于高维单纯形上，直接分箱很快遭遇维数灾难。

### 核心想法：不直接估计距离，而是估计“改校准后能降低多少风险”

如果能够学到一个重校准函数

$$
g^\star(f(X))=\mathbb E[Y\mid f(X)]=C,
$$

那么原始预测与最佳重校准预测之间的风险差，可以作为校准误差。早期的变分方法适用于由固定 proper loss 诱导的散度，例如 Brier score 对应的平方误差、log loss 对应的 KL 散度；普通 $L_1$ 或 $L_2$ 距离却不属于这类固定散度。

这篇论文的关键突破，是允许损失函数随每个原始预测 $f(X)$ 改变。对每个 $f(X)$ 定义

$$
H_{f(X)}(z)=-\|z-f(X)\|_p.
$$

由它构造的、以 $f(X)$ 为中心的 proper loss 为

$$
\ell_{f(X)}(z,Y)
=\left\langle\nabla_z\|z-f(X)\|_p,\,f(X)-Y\right\rangle,
\quad z\ne f(X),
$$

并约定在 $z=f(X)$ 处的次梯度为零，因此 $\ell_{f(X)}(f(X),Y)=0$。把 $z$ 取为真实条件概率 $C$ 并对 $Y\mid f(X)$ 求期望后，风险差恰好等于

$$
\mathbb E[\|C-f(X)\|_p].
$$

直观地说：不需要先在概率空间里分箱并显式重建 $C$，而是训练任意概率分类器去近似 $C$，再测量“它相对原始预测减少了多少特制损失”。

### 实际算法

输入是原始概率预测 $f(X_i)$、标签 $Y_i$、范数参数 $p$、重校准模型类别和折数 $K$。

```text
概率预测 f(X_i) + 标签 Y_i
          |
          v
      划分 K 折
          |
          v
对第 j 折：
  用其余 K-1 折训练 g_hat_j: f(X) -> Y 的概率
  只在第 j 折产生 g_hat_j(f(X_i))
  用以原始 f(X_i) 为中心的 Lp proper loss 评价
          |
          v
对 K 个 held-out 风险差取平均
          |
          v
得到 CE_hat_{||.||_p}(f)
```

第 $j$ 折的估计为

$$
\widehat{\mathrm{CE}}_{\|\cdot\|_p}^{(j)}(f)
=-\frac{1}{|\mathcal I_j|}
\sum_{i\in\mathcal I_j}
\ell_{f(X_i)}(\hat g_j(f(X_i)),Y_i).
$$

为什么一定要交叉验证？如果在训练 $\hat g$ 的同一批数据上评价，它会因过拟合而表现得“改善特别大”，从而把校准误差估得过高。把训练与评价样本分开后，$g^\star$ 仍然是总体风险最优解，所以估计在期望意义下是保守的下界。重校准模型越接近 $g^\star$，下界越紧。

### 过度自信、信心不足与多分类

二分类中，论文通过相对 $f(X)$ 和阈值 $1/2$ 截断重校准预测，只保留一个方向的修正，从而分别估计 over-confidence 和 under-confidence。多分类没有唯一的全向量“过度自信”定义，因此作者采用 top-class 方案：先用原始 $f(X)$ 选出概率最大的类别，把“该类别是否为真”转成二分类，再应用方向损失。

代码中的对应关系很直接：

- `ProperLpLoss` 实现预测依赖的 $L_p$ 损失；
- `MetricsWithCalibration` 对每折拟合重校准器并计算 held-out 风险差；
- `OverConfidenceLoss`、`UnderConfidenceLoss` 实现方向截断；
- `TopClassLoss` 完成多分类 top-class 二值化。

### 实验说明了什么？

在校准函数已知的合成数据上，不做交叉验证的 isotonic regression 和分箱 ECE 都会高估，尤其在样本少或真实误差接近零时更明显；交叉验证版本从下方接近真实值。在 3 类与 10 类合成问题上，$L_2$ 误差也表现出同样趋势。方向实验中，不存在的方向被估为接近零，混合情形的两种误差也能分开。

真实数据实验使用 TabRepo 保存的 out-of-fold 预测：58 个二分类数据集 × 6 种基础模型，以及 25 个多分类数据集 × 5 种基础模型。作者用五折交叉验证、十次重复比较多种重校准器。TabICLv2 与 RealTabPFN-2.5 的估计较紧，但需要 GPU；warm-started CatBoost 在二分类列中最好，并兼顾多分类表现与运行成本，因此被推荐为默认方案。

### 如何正确理解“下界”

- 它是总体期望层面的性质，不是每次有限样本运行都严格不超过真值。
- 下界小不一定说明模型校准好，也可能只是 $\hat g$ 太弱，没学到真实 $C$。
- 比较重校准器时，目标固定且大家都是下界，因此较大的估计通常表示更紧；这不等于“校准误差越大越好”。
- 真实数据上不知道真值，论文只能用候选方法中最大的估计作为相对参照，而不能测量绝对估计误差。

### 代码与复现边界

论文不是生信研究，而是机器学习中的概率校准与不确定性评估方法。官方 `probmetrics` 仓库完整覆盖核心损失和交叉验证估计器；另一官方仓库提供合成/TabRepo 实验、结果 CSV 和绘图 notebook。核心论文—代码匹配度高。完整重跑 Table 1 仍需要外部 TabRepo 预测、CatBoost/LightGBM/TabICL/TabPFN 等依赖和 GPU；仓库没有覆盖整套实验的锁定环境。包内测试验证了指标接口，但没有找到对每个新 $L_p$ 与方向变体数值公式的独立单元测试。

### 一句话总结

该方法把难以直接估计的 $L_p$ 概率校准距离，改写成“原始预测与交叉拟合重校准预测之间的、随样本预测而变化的 proper-loss 风险差”，从而避免分箱，并在期望意义下控制过度估计。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## A Variational Estimator for $L_p$ Calibration Errors

### Problem

Probability calibration asks whether a classifier's stated probabilities match observed class frequencies. The natural $L_p$ target,

$$
\mathbb E\!\left[\|f(X)-\mathbb E[Y\mid f(X)]\|_p\right],
$$

is hard to estimate because the conditional probability is unknown and $f(X)$ is continuous. Standard expected calibration error bins the prediction space, introducing bias and a bin-count choice; multiclass binning additionally suffers from the curse of dimensionality. Existing variational excess-risk estimators directly cover divergences induced by fixed proper losses, but not ordinary $L_p$ distances.

### Contribution

Berta, Braun, Holzmüller, Bach, and Jordan construct a prediction-dependent family of proper losses that turns any binary or multiclass $L_p$ calibration error ($p\ge1$) into a variational excess-risk difference. A probabilistic recalibrator $\hat g$ learns $Y$ from the original prediction $f(X)$. With cross-fitting, each observation is evaluated only by a recalibrator trained on other folds, so the population estimate is conservative in expectation rather than systematically inflated by recalibrator overfitting. The framework also supports general convex distances and separate binary/top-class over- and under-confidence diagnostics.

### Method in brief

For each baseline prediction, the paper centers an entropy at $f(X)$:

$$
H_{f(X)}(z)=-\|z-f(X)\|_p.
$$

Its associated prediction-dependent loss satisfies

$$
\mathbb E[\ell_{f(X)}(f(X),Y)-\ell_{f(X)}(g^\star(f(X)),Y)]
=\mathrm{CE}_{\|\cdot\|_p}(f),
$$

where $g^\star(f(X))=\mathbb E[Y\mid f(X)]$. In practice, fit $\hat g_j$ on the training part of each fold, evaluate the centered loss on the held-out part, and average. Better recalibrators yield tighter lower bounds; the paper recommends warm-started CatBoost plus structured matrix scaling as a practical default.

### Evaluation and results

Synthetic binary experiments show that same-data isotonic regression and 15-bin ECE overestimate calibration error, while cross-validated isotonic estimates track the known truth from below and converge faster. Synthetic 3- and 10-class experiments show the same behavior for $L_2$ error. Directional simulations recover nearly zero error in the absent direction and separate mixed over-/under-confidence.

On real out-of-fold predictions from TabRepo—58 binary datasets with 6 model sources and 25 multiclass datasets with 5—the study compares nine recalibration approaches using five-fold cross-validation and ten repetitions. TabICLv2 and RealTabPFN-2.5 recover strong estimates but require GPUs. Warm-started CatBoost leads both binary columns in Table 1 (72.9% and 59.4% of the maximum recovered estimate) and offers the recommended accuracy/runtime compromise.

### Code and reproducibility

This is a machine-learning calibration paper, not a bioinformatics paper. It provides two official repositories:

- [`probmetrics`](https://github.com/dholzmueller/probmetrics), snapshot `9d991bf3aa1f90ed792018704898cfa96b7df8f5`, implements `ProperLpLoss`, fold-wise `MetricsWithCalibration`, directional wrappers, and top-class reduction.
- [`Evaluating_Lp_Calibration_Errors`](https://github.com/ElSacho/Evaluating_Lp_Calibration_Errors), snapshot `a2c19fe0a1207090c400a10adf0ba5ec3afd3d58`, contains experiment drivers, simulations, saved CSV outputs, and plotting notebooks.

Core paper–code fidelity is high. Full benchmark reproduction is only partial from the snapshot alone because it requires external TabRepo prediction artifacts, several optional heavyweight model packages, and GPU resources; no frozen container or lockfile covers the complete run. The package tests exercise metric interfaces and names, but direct numerical unit tests for every new directional/$L_p$ case were not found.

### Limitations

- The expectation-level lower-bound property depends on held-out evaluation; finite-sample estimates can cross zero or fluctuate around the truth.
- Bound tightness is controlled by how well $\hat g$ estimates $\mathbb E[Y\mid f(X)]$.
- Multiclass over-/under-confidence is defined only through a top-class binary reduction.
- Real-data comparisons use the largest recovered lower bound as a proxy because ground-truth calibration error is unavailable.
- Stronger recalibrators improve sample efficiency but add runtime, dependencies, and sometimes GPU requirements.

### Reproducibility rating

**4/5.** The mathematical estimator, package implementation, experiment code, saved results, and figure notebooks are public and align closely. One point is withheld because the broad benchmark lacks a single pinned, self-contained reproduction environment and relies on external artifacts and heavyweight models.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
