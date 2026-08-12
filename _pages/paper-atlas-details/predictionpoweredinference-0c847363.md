---
layout: default
permalink: /paper-atlas/predictionpoweredinference-0c847363/
title: "PredictionPoweredInference"
nav: false
description: "本文档基于本地 paper.md、两张本地图像和 ppipy 源码逐行核对写成。需要先说明一个重要限制：Science HTML 转换把论文方法区和 Table 1 中的大部分数学公式转换成了 No alternative text available，本地 acquisition manifest 也显示没有抽取到表格正文 。因此，下面解释的是论文可读文本、图示和代码中能验证的方法结构；"
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
      <span>Computational Tools</span>
      <span>Science · 2023</span>
    </div>
    <h1>PredictionPoweredInference</h1>
    <p>Prediction-powered inference</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.adi6000" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Prediction-Powered Inference 方法中文解读

### 证据边界

本文档基于本地 `paper.md`、两张本地图像和 `ppi_py` 源码逐行核对写成。需要先说明一个重要限制：Science HTML 转换把论文方法区和 Table 1 中的大部分数学公式转换成了 `No alternative text available`，本地 acquisition manifest 也显示没有抽取到表格正文 (`paper source/science_html/paper.md:39-65`; `paper source/science_html/acquisition_manifest.json:11-19`)。因此，下面解释的是论文可读文本、图示和代码中能验证的方法结构；不会凭记忆补写 Table 1 的精确公式、常数或补充材料算法。

补充材料在本地没有转换成 Markdown。论文正文提到 Theorem S1、Algorithms S1-S6、Theorem S3、Corollary S13 等细节 (`paper source/science_html/paper.md:39-65`, `paper source/science_html/paper.md:86-89`, `paper source/science_html/paper.md:211-218`)，但这些只能标为本地证据 `Not found`。

### 论文要解决什么问题

很多科学场景里，机器学习模型可以廉价地产生大量预测，但真正的 gold-standard 实验标签很少、很贵。直接把预测当真值使用，也就是 imputation approach，速度快但可能有偏差，导致置信区间和 P 值失效 (`paper source/science_html/paper.md:24-24`)。完全忽略预测、只用 gold-standard 标签的 classical approach 通常统计上有效，但样本太少，置信区间宽、检验功效低 (`paper source/science_html/paper.md:27-30`)。

Prediction-powered inference (PPI) 的目标是在这两者之间取得平衡：使用大量 ML 预测提高信息量，同时用少量 gold-standard 标签估计并校正预测误差，从而得到有效的置信区间和 P 值 (`paper source/science_html/paper.md:30-33`)。

论文明确说 PPI 可用于均值、分位数、线性回归系数、逻辑回归系数等目标，并且不要求对产生预测的 ML 算法做特定假设 (`paper source/science_html/paper.md:18-18`)。

### 核心思想：用少量真标签校正大量预测

论文把 PPI 描述为三步 (`paper source/science_html/paper.md:42-65`)：

1. **选择 estimand**：先定义要推断的总体量，例如均值、median/q-quantile、线性回归系数、逻辑回归系数。
2. **选择 measure of fit 和 rectifier**：用未标注数据上的预测来估计目标量，同时用有真标签的数据衡量预测误差。
3. **rectify confidence interval**：把预测贡献和误差校正项组合成 prediction-powered confidence interval。

Figure 1 很直观地画出了这条流水线：上支路使用 labeled data 和它们的预测来估计 rectifier；下支路使用 unlabeled data 的预测来估计 quantity of interest；两者在 Rectify 步骤合并，输出置信区间。

可以把它理解为：

```text
少量真标签:       X, Y, Yhat              -> 估计预测误差 / rectifier
大量未标注预测:   X_unlabeled, Yhat_unlabeled -> 用预测估计目标量

预测带来的大样本信息 + 真标签带来的误差校正
        |
        v
有效的点估计、标准误、置信区间或 P 值
```

### 均值估计：最清楚的代码对应

均值是最容易理解的 PPI 特例。论文多个实验都可以归到均值或由均值组成的目标，例如 Galaxy Zoo 中螺旋星系比例、Amazon deforestation 比例，以及 AlphaFold/PTM 例子中的 odds ratio 组成项 (`paper source/science_html/paper.md:104-139`)。

源码中，`ppi_mean_pointestimate` 接收：

- `Y`：gold-standard 标签；
- `Yhat`：这些有标签样本上的模型预测；
- `Yhat_unlabeled`：大量未标注样本上的模型预测；
- 可选权重 `w` 和 `w_unlabeled`。

实现上，它把未标注预测的平均值和有标签样本上的残差校正相加 (`ppi_py/ppi_py/ppi.py:66-132`)。`ppi_mean_ci` 再分别计算预测项和校正项的标准误，把两个方差合并，然后用 z 区间产生上下界 (`ppi_py/ppi_py/ppi.py:135-228`)。`ppi_mean_pval` 和 `rectified_p_value` 用同样的分解构造 P 值 (`ppi_py/ppi_py/ppi.py:30-57`, `ppi_py/ppi_py/ppi.py:231-297`)。

一个关键实现细节是：当前包里很多函数默认 `lam=None`，这会自动估计 power-tuning 参数，源码注释引用的是后续 PPI++ 工作 (`ppi_py/ppi_py/ppi.py:82-91`, `ppi_py/ppi_py/ppi.py:155-164`)。如果目标是复现 2023 Science 论文正文中的基础 PPI 思路，`lam=1` 是更干净的对应；`lam=None` 应当视为后续包扩展。

### 分位数和中位数

论文把 median 和 q-quantile 作为常见 estimand，并在 gene expression 应用中估计表达水平的 median、25% quantile 和 75% quantile (`paper source/science_html/paper.md:127-133`)。

源码中的做法是把分位数问题转化为 rectified CDF 的反演：

- `_rectified_cdf` 用未标注预测估计 CDF，再加上有标签数据中真值 CDF 和预测 CDF 的差异 (`ppi_py/ppi_py/ppi.py:306-328`)。
- `ppi_quantile_pointestimate` 在由 `Y`、`Yhat`、`Yhat_unlabeled` 构成的 grid 上寻找 rectified CDF 最接近目标分位数的位置 (`ppi_py/ppi_py/ppi.py:331-371`)。
- `ppi_quantile_ci` 在 grid 上计算 rectified p-value，并返回未被拒绝的区间端点 (`ppi_py/ppi_py/ppi.py:374-427`)。

这个实现仍然是同一个思想：大量预测给出分布形状，少量真标签修正预测带来的分布偏差。

### OLS 和逻辑回归

论文把线性回归系数和逻辑回归系数列为 PPI 支持的典型目标 (`paper source/science_html/paper.md:18-18`)。

OLS 代码路径：

- `_ols` / `_wls` 计算普通或加权最小二乘估计 (`ppi_py/ppi_py/ppi.py:436-477`)。
- `ppi_ols_pointestimate` 在未标注预测上做 imputed WLS，并用有标签数据上的 `Y - lam * Yhat` 做校正 (`ppi_py/ppi_py/ppi.py:553-636`)。
- `_ols_get_stats` 和 `ppi_ols_ci` 计算梯度、Hessian、方差并输出置信区间 (`ppi_py/ppi_py/ppi.py:480-550`, `ppi_py/ppi_py/ppi.py:639-741`)。

逻辑回归代码路径：

- `ppi_logistic_pointestimate` 先用 classical logistic regression 初始化，然后最小化一个由未标注预测项、有标签预测项、真标签项组成的 rectified logistic loss (`ppi_py/ppi_py/ppi.py:750-890`)。
- `_logistic_get_stats` 计算 Hessian 和三类梯度 (`ppi_py/ppi_py/ppi.py:893-966`)。
- `ppi_logistic_pval` 和 `ppi_logistic_ci` 基于这些统计量构造 P 值和置信区间 (`ppi_py/ppi_py/ppi.py:969-1180`)。

这两个实现体现了论文中更一般的 convex-objective 思想：先定义目标函数或 measure of fit，再用真标签样本估计预测带来的偏差。不过论文声称的通用 convex minimizer master protocol 在本地补充材料中不可见，包里也没有找到一个单独的通用 convex-minimizer API；能直接验证的是 OLS、logistic 等具体实现。

### 分布偏移：covariate shift 和 label shift

论文讨论了两类分布偏移 (`paper source/science_html/paper.md:80-89`)：

- **Covariate shift**：特征分布变了，但条件关系可用加权方式处理。论文说要根据 Corollary S13 重加权数据 (`paper source/science_html/paper.md:86-86`)。
- **Label shift**：标签比例变了，例如 2013 和 2014 plankton 数据中 plankton/detritus 的比例不同 (`paper source/science_html/paper.md:154-160`)。

源码中，covariate shift 通过 `w` 和 `w_unlabeled` 参数进入主要估计器：mean、OLS、logistic 都有这些权重参数 (`ppi_py/ppi_py/ppi.py:72-85`, `ppi_py/ppi_py/ppi.py:561-575`, `ppi_py/ppi_py/ppi.py:648-665`, `ppi_py/ppi_py/ppi.py:773-790`)。

Label shift 则有独立函数 `ppi_distribution_label_shift_ci`。它用有标签数据构造预测标签和真实标签之间的 confusion matrix，然后对未标注数据上的预测标签分布做校正，最后返回 count 或 proportion 的区间 (`ppi_py/ppi_py/ppi.py:1837-1905`)。

### 实验和图像证据

Figure 2 展示了七个应用场景：AlphaFold/proteomics、galaxy classification、gene expression、deforestation、health insurance、covariate-shift income、plankton label shift (`paper source/science_html/images/figure_02.jpg`)。论文说明每个任务都比较了 PPI、classical 和 imputation，并比较不同 labeled sample size 下的区间宽度 (`paper source/science_html/paper.md:92-115`)。

图中绿色代表 prediction-powered，灰色代表 classical，橙色代表 imputed，虚线是真值参考。可读的视觉结论是：多数行中绿色宽度曲线低于灰色；橙色 imputed 区间在多个行里偏离真值参考。精确数值端点和 Table 2 的样本量阈值无法从本地图像和转换后的文本可靠抽取，因此没有报告。

包的 README 把这些实验对应到本地 notebooks：`alphafold.ipynb`、`galaxies.ipynb`、`gene_expression.ipynb`、`forest.ipynb`、`census_healthcare.ipynb`、`census_income_covshift.ipynb`、`plankton.ipynb` (`ppi_py/README.md:73-83`)。examples README 说明这些 notebooks 生成 PPI/classical/imputation 的置信区间数据框，并比较达到发现所需的 labeled examples (`ppi_py/examples/README.md:3-18`)。

### 代码匹配和复现建议

代码仓库为 `https://github.com/aangelopoulos/ppi_py.git`，本地快照 commit 是 `3d1f0c668444907b39bd045cb9dd38e479ce7dd6`。

代码和 2023 Science 论文的匹配度是 **medium**：

- 强匹配：mean、quantile、OLS、logistic、covariate-shift weights、label-shift helper 都能在源码中找到直接实现。
- 限制：本地论文转换缺失 Table 1 精确公式和补充材料算法，所以不能验证常数、定理条件和算法 S1-S6。
- 额外扩展：当前包还实现了 PPI++、Cross-PPI、Prediction-Powered Bootstrap、PTD 和 power-analysis utilities，这些属于后续工作或包扩展，不应直接当作 2023 Science 论文正文的方法 (`ppi_py/README.md:134-148`)。

如果研究者想用代码复现基础 PPI，可以按这个流程：

1. 明确 estimand：mean、quantile、OLS coefficient、logistic coefficient 或 label-shift count/proportion。
2. 准备 `Y`、`Yhat`、`Yhat_unlabeled`；回归问题还需要 `X` 和 `X_unlabeled`。
3. 调用对应的 `ppi_*_ci`，若要最接近 2023 基础 PPI，显式设置 `lam=1`。
4. 用 `classical_*_ci` 作为 classical baseline。
5. 若有 covariate shift，提供 `w` 和 `w_unlabeled`；若是 label shift，用 `ppi_distribution_label_shift_ci`。

### 本地证据缺口

| 项目 | 状态 | 说明 |
|---|---|---|
| Table 1 精确 measure-of-fit / rectifier 公式 | MISSING | `paper.md` 只有占位符和 caption，没有表格正文。 |
| Theorem S1 常数和完整置信集形式 | Not found | 本地只有补充 PDF 链接，没有转换文本。 |
| Algorithms S1-S6 | Not found | 未进行补充材料 OCR 或重新获取。 |
| Theorem S3 / Corollary S13 的证明条件 | Not found | 代码有对应实现入口，但本地无定理文本。 |
| Table 2 样本量数值 | MISSING | 表格正文和正文中的数值字段都未被可靠抽取。 |
| 通用 convex-minimizer API | Not found | 论文有 general applicability claim；包里验证到的是具体 estimand API。 |

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Prediction-Powered Inference

### Overview

Prediction-powered inference (PPI) is a statistical framework for using abundant machine-learning predictions together with scarce gold-standard labels to compute valid confidence intervals and p-values for population quantities such as means, quantiles, and linear/logistic regression coefficients (`paper source/science_html/paper.md:18-18`). The paper appeared in *Science* in 2023 and presents PPI as a way to gain the power of high-throughput ML systems without treating their predictions as error-free measurements.

The central problem is that the naive imputation strategy, which treats predictions as true outcomes, can produce invalid scientific conclusions, while the classical strategy, which ignores predictions and uses only gold-standard labels, is valid but often underpowered (`paper source/science_html/paper.md:21-30`). PPI combines both sources: it estimates the target from predictions on a large unlabeled sample, then rectifies that estimate using prediction errors measured on a small labeled sample (`paper source/science_html/paper.md:42-65`).

### Method in Brief

The paper’s protocol has three steps:

1. Choose an estimand, such as a mean, median/quantile, or regression coefficient.
2. Identify a measure of fit and a rectifier that captures the prediction error relevant to that estimand.
3. Combine the imputed-data contribution and the rectifier into a prediction-powered confidence interval.

Figure 1 shows this split explicitly: a labeled-data branch estimates the rectifier, an unlabeled-data branch estimates the quantity using predictions, and the two are combined into the final confidence interval (`paper source/science_html/paper.md:42-47`; `paper source/science_html/images/figure_01.jpg`). The paper states that validity holds for any ML algorithm and data distribution in the iid setting, with distribution-shift extensions for covariate shift and label shift (`paper source/science_html/paper.md:68-89`).

Exact Table 1 formulas and constants are not available in the local Science HTML conversion: most math appears as `No alternative text available`, and no table bodies were extracted (`paper source/science_html/paper.md:39-65`; `paper source/science_html/acquisition_manifest.json:11-19`). Supplementary algorithms and theorem details are referenced but not locally converted.

### Evaluation

The paper demonstrates PPI on seven real-data tasks spanning proteomics, astronomy, genomics, remote sensing, census analysis, and ecology (`paper source/science_html/paper.md:92-160`). Figure 2 compares prediction-powered, classical, and imputed intervals, and plots interval widths as the labeled sample size varies (`paper source/science_html/paper.md:110-112`; `paper source/science_html/images/figure_02.jpg`). The visible figure and text support the qualitative conclusion that prediction-powered intervals are generally narrower than classical intervals while the imputation approach often misses the ground-truth reference.

The application rows map to package examples: AlphaFold/proteomics, galaxies, gene expression, forest/deforestation, census health insurance, covariate-shift income, and plankton label shift (`ppi_py/README.md:73-83`; `ppi_py/examples/README.md:3-18`).

### Code Match and Reproducibility

Code repository: `https://github.com/aangelopoulos/ppi_py.git` at commit `3d1f0c668444907b39bd045cb9dd38e479ce7dd6`.

The code-paper match is **medium**. The package directly implements the main estimator families named in the Science paper:

- mean point estimates, confidence intervals, and p-values (`ppi_py/ppi_py/ppi.py:66-297`);
- quantile point estimates and confidence intervals (`ppi_py/ppi_py/ppi.py:306-427`);
- OLS point estimates and confidence intervals (`ppi_py/ppi_py/ppi.py:436-741`);
- logistic point estimates, p-values, and confidence intervals (`ppi_py/ppi_py/ppi.py:750-1180`);
- covariate-shift weighting arguments across estimators (`ppi_py/ppi_py/ppi.py:72-85`, `ppi_py/ppi_py/ppi.py:561-575`, `ppi_py/ppi_py/ppi.py:648-665`, `ppi_py/ppi_py/ppi.py:773-790`);
- label-shift class-distribution intervals (`ppi_py/ppi_py/ppi.py:1837-1905`).

The score is not "high" because the local paper evidence cannot verify exact Table 1 formulas/constants, Algorithms S1-S6, or supplementary theorem conditions, and the package has expanded beyond the 2023 Science paper. The README lists later implementations including PPI++, Cross-PPI, Prediction-Powered Bootstrap, PPI with imputed covariates/nonuniform sampling, and Mixed Subjects Design (`ppi_py/README.md:134-148`). In particular, package docstrings cite later PPI++ work for automatic `lam` power tuning, so `lam=1` is the closer setting when trying to mirror the original rectified estimator (`ppi_py/ppi_py/ppi.py:82-91`, `ppi_py/ppi_py/ppi.py:155-164`).

### Main Gaps

- Exact Table 1 measure-of-fit/rectifier formulas and constants: **MISSING** from local `paper.md`.
- Supplementary Algorithms S1-S6, Theorem S1, Theorem S3, and Corollary S13: **Not found** as local markdown.
- Table 2 labeled-example counts: **MISSING** because table body and placeholder math/sample-size fields were not extracted.
- Generic convex-minimizer master protocol: described in the paper, but no single generic public API was found in the package; specific estimand APIs are present.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
