---
layout: default
permalink: /paper-atlas/calarena-0c387f79/
title: "CalArena"
nav: false
description: "分类器不仅给类别，还给概率；但“预测 0.9”并不保证类似样本中真的有约 90% 属于该类。后处理校准是在不重训分类器的情况下，用独立校准集学习一个映射，把原始概率变成更可靠的概率。 难点不在于缺少方法，而在于方法太多、比较不公平：既有研究的数据规模小，ECE 等指标对分箱方式敏感，公开实现也不统一。同一个方法可能在不同论文中得到相反结论。CalArena 因而是一篇机器学习基准论文，目标是建立统一的“赛场”，不是提出某个生信算法。"
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
    <h1>CalArena</h1>
    <p>CalArena: A Large-Scale Post-Hoc Calibration Benchmark</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2605.30188" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CalArena">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/probkit/CalArena" target="_blank" rel="noopener noreferrer" aria-label="Open code for CalArena">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CalArena 方法解读：如何公平比较后处理概率校准方法

### 1. 它要解决什么问题？

分类器不仅给类别，还给概率；但“预测 0.9”并不保证类似样本中真的有约 90% 属于该类。后处理校准是在不重训分类器的情况下，用独立校准集学习一个映射，把原始概率变成更可靠的概率。

难点不在于缺少方法，而在于方法太多、比较不公平：既有研究的数据规模小，ECE 等指标对分箱方式敏感，公开实现也不统一。同一个方法可能在不同论文中得到相反结论。CalArena 因而是一篇机器学习基准论文，目标是建立统一的“赛场”，不是提出某个生信算法。

### 2. 基准是什么？

CalArena 固定了 7 个基准、共 1,791 个“数据集–基础模型”实验：

| 场景 | 基准 | 实验数 |
|---|---|---:|
| 经典表格二分类 | TabRepo-binary | 832 |
| 先进表格二分类 | TabArena-binary | 314 |
| 视觉二分类 | CV-binary | 13 |
| 经典表格多分类 | TabRepo-multiclass | 520 |
| 先进表格多分类 | TabArena-multiclass | 84 |
| 视觉多分类 | CV-multiclass | 20 |
| ImageNet 大规模多分类 | ImageNet-multiclass | 8 |

每个实验都保存独立校准集与测试集的概率和标签。校准器只在校准集上拟合，在测试集上评估，因此不会把测试标签用于训练校准映射。

### 3. 为什么不只看 ECE？

只追求“看起来校准”会产生荒谬解：把所有样本都预测成校准集的类别频率，可能获得不错的校准误差，却完全丢掉区分样本的能力。

设原分类器为 $f(X)\in\Delta_K$，校准映射为 $g:\Delta_K\to\Delta_K$。CalArena 使用 proper loss $\ell$ 定义后处理改进（PHI）：

$$
\Phi_{\ell}(g)=\mathbb{E}[\ell(f(X),Y)]-\mathbb{E}[\ell(g\circ f(X),Y)].
$$

测试集上的经验形式是：

$$
\Phi_{\ell}(g)=\frac{1}{n_{\mathrm{test}}}\sum_i\ell(f(X_i),Y_i)-\frac{1}{n_{\mathrm{test}}}\sum_i\ell(g\circ f(X_i),Y_i).
$$

$\Phi>0$ 表示校准后总体概率预测变好，$\Phi<0$ 表示变差。主指标是 Brier score 的改进 $\Phi_{\mathrm{BS}}$；它同时惩罚校准误差和判别信息损失。PHI 不是“真实校准误差”的直接估计，而是固定基础模型前后、面向决策质量的比较。

### 4. 完整计算流程

```text
外部仓库中的基础模型预测 / 视觉 logits
                    ↓
整理为 7 个固定基准：实验索引 CSV + HDF5 概率/标签
                    ↓
选择一个 benchmark 与一个校准器
                    ↓
校准集：fit(p_cal, y_cal)
测试集：predict_proba(p_test)
                    ↓
计算 Brier、logloss、ECE-15、accuracy（以及二分类 Kuiper）
                    ↓
每个校准器输出一个结果 CSV
                    ↓
计算 PHI、逐实验胜率、Elo、绝对改进和显著性
                    ↓
按数据集或实验 bootstrap 得到 95% 置信区间
```

新方法只需实现 `fit` 和 `predict_proba` 并注册到 `custom_calibrators.py`。代码会自动遍历所选基准中的实验、计算指标并写出结果。

### 5. 比较哪些方法？

二分类覆盖分箱、等距/等频直方图、isotonic/CIR、Venn–Abers、Platt/temperature/Beta/Quadratic、Spline/Kernel 以及树模型等。多分类既有 TS、VS、SVS、MS、SMS、Dirichlet 等原生多分类方法，也把部分二分类方法按 one-vs-rest 分别拟合后再归一化。

聚合时，胜率表示某方法在一个实验中击败其他方法的比例，再跨实验平均。论文还报告 Elo 和绝对 PHI，因为胜率只看输赢、不看差距大小；Friedman/Nemenyi 图用于判断平均排名差异是否足够明确。

### 6. 主要发现

1. **二分类：** Quadratic、Platt-logits、Beta 的平均表现最好，Spline 是很强的非参数备选。
2. **多分类：** SMS 总体领先，其后是 SVS 与 VS。类别少时 OvR Spline 可以竞争，但类别数增加后原生多分类结构更重要。
3. **平滑性重要：** 分箱方法可能改善 ECE-15，却损害 Brier PHI；平滑映射更能保留预测信息。
4. **通用模型不等于好校准器：** XGBoost、LightGBM、CatBoost 默认设置整体不占优；对 CatBoost 加浅树和单调约束后表现改善，说明校准需要专门的结构偏置。
5. **别把榜首理解成绝对胜者：** 关键差异图中很多相邻方法由黑线连接，说明它们未必具有统计显著差异。

### 7. 如何正确使用结论？

CalArena 给的是跨数据集的平均证据，而不是“任何任务都选同一个方法”。新任务仍应在匹配的模态、类别数和校准集规模下运行完整比较，同时看 PHI、置信区间、运行时间和绝对改进。尤其不能因为某方法降低 ECE 就忽略它是否损害整体预测质量。

### 8. 复现边界

官方代码快照与论文的基准执行和统计分析高度匹配。校准器和指标的内部实现位于官方外部依赖 `probmetrics`，本次未获取，不能声称已逐行验证；代码中也未找到独立自动化测试套件。论文自身还承认固定超参数、视觉数据覆盖较窄以及部分方法缺失等限制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CalArena: A Large-Scale Post-Hoc Calibration Benchmark

### Problem

Modern classifiers often output unreliable probabilities, but practitioners face dozens of post-hoc calibration methods evaluated on small, inconsistent benchmarks. Expected Calibration Error is sensitive to estimator choices, implementations are fragmented, and a method can appear calibrated while destroying predictive refinement.

### Contribution

CalArena is a standardized machine-learning benchmark, not a bioinformatics method. It consolidates 1,791 dataset–model experiments into seven tabular and computer-vision benchmarks spanning binary, multiclass, and ImageNet-scale classification. It compares 20 binary and 19 multiclass entries (including the uncalibrated baseline), supplies a common fit/predict interface, and releases fixed predictions, runners, aggregation utilities, results, and figure-generation artifacts.

Its central evaluation quantity is Post-Hoc Improvement (PHI), the difference between a proper-score risk before and after calibration. Brier-score PHI is primary; log-loss, ECE-15, accuracy, and binary Kuiper variants are supplementary. This scores calibration gain while penalizing post-processing that sacrifices useful discrimination. Results are summarized using per-experiment winrates with bootstrap confidence intervals, Bradley–Terry Elo, absolute improvements, and Friedman/Nemenyi analyses.

### Main results

- Binary logistic-style methods—Quadratic, Platt-logits, and Beta—lead on average; Spline is the strongest broadly competitive non-parametric method.
- SMS leads multiclass evaluation, followed by SVS and VS. OvR Spline competes on few-class tasks but loses ground as class dimension rises.
- Smooth mappings consistently outperform binning under Brier PHI, even when binning looks good under ECE-15.
- Generic boosted trees are weak out of the box; adding shallow-depth and monotonicity constraints improves CatBoost, suggesting that calibration-specific inductive bias matters.

These are aggregate benchmark findings, not guarantees for every dataset. Critical-difference plots show substantial overlap among neighboring methods, and ImageNet contains one dataset across eight models.

### Reproducibility and code-paper match

**Rating: 4/5.** The official CalArena snapshot closely matches the paper's benchmark orchestration: experiment indexes, source-construction scripts, method registries, held-out evaluation loop, committed result CSVs, aggregation functions, plots, and a two-method custom calibrator interface are present. Code-paper fidelity is high for this layer.

Important boundaries remain. The seven HDF5 benchmark files (~1.71 GB) are intentionally absent and must be downloaded; an end-to-end rerun was therefore not performed. All calibrator and metric implementations come from the official external `probmetrics` package, which was not acquired, so their internals are unverified here. No standalone automated test suite was found. The paper also uses fixed hyperparameters, has narrower CV than tabular coverage, and omits some slow or unavailable calibration methods.

### Practical interpretation

CalArena is most valuable as evaluation infrastructure: it turns a new calibrator into a controlled, held-out comparison against many established alternatives. Its strongest methodological lesson is to optimize and report overall probabilistic improvement rather than a calibration-error estimate in isolation, while keeping dimension, compute, tuning, and statistical uncertainty visible.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
