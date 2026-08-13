---
layout: default
permalink: /paper-atlas/calpred-8e6d4aab/
title: "CalPred"
nav: false
wide: true
description: "多基因评分（PGS）通常给每个人一个风险或性状点预测，但同一个 PGS 在不同年龄、性别、遗传主成分、收入或生活方式群体中的准确度可能不同。CalPred 不重新训练 SNP 权重；它在一组有真实表型的校准样本中学习两件事： PGS 与情境变量怎样改变预测均值； 均值预测留下的残差方差怎样随情境变化。 对定量性状，输出是个体化均值与预测区间；对疾病性状，输出是异方差 probit 模型下的个体疾病概率。"
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
      <span>Nature Genetics · 2024</span>
    </div>
    <h1>CalPred</h1>
    <p>Calibrated prediction intervals for polygenic scores across diverse contexts</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-024-01792-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CalPred">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/KangchengHou/calpred" target="_blank" rel="noopener noreferrer" aria-label="Open code for CalPred">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CalPred：让多基因评分的不确定性随个体情境变化

### 先区分“点预测更准”和“知道自己有多不准”

多基因评分（PGS）通常给每个人一个风险或性状点预测，但同一个 PGS 在不同年龄、性别、遗传主成分、收入或生活方式群体中的准确度可能不同。CalPred 不重新训练 SNP 权重；它在一组有真实表型的**校准样本**中学习两件事：

1. PGS 与情境变量怎样改变预测均值；
2. 均值预测留下的残差方差怎样随情境变化。

对定量性状，输出是个体化均值与预测区间；对疾病性状，输出是异方差 probit 模型下的个体疾病概率。它的目标不是让所有人的区间一样窄，而是让名义 90% 区间在各情境亚组中都约有 90% 覆盖率：预测较差的情境应更宽，预测较好的情境可以更窄。

### 证据和版本边界

- 论文：`paper source/paper/auto/paper.md`，DOI `10.1038/s41588-024-01792-w`。
- 主图：`figure_pages/page-03.png` 至 `page-09.png`；图 1–8 分别覆盖概念、两个人群的 context-specific accuracy、模拟、LDL/跨性状区间和 T2D 风险。
- 补充：`supplementary/` 中三个 PDF，以及论文 OCR 中的 Supplementary/Extended Data 引用。
- 正式包：`calpred/`，GitHub `KangchengHou/calpred`，提交 `ab69fee65683f67513104a904bbb40c35931449c`。
- 手稿复现仓：`calpred-manuscript/`，GitHub `KangchengHou/calpred-manuscript`，提交 `a7c9c4de5cb6eeb7e4fc6e5f89f22f4231c2aa6a`。

正式包验证核心统计模型；手稿仓补充论文使用的交互斜率和 notebook 工作流。两者不是同一接口的重复副本，复现时必须说明使用哪一条代码路径。

### 为什么普通 PGS 区间会失准

若只用一个全体样本残差标准差 $\sigma$，90% 区间为

$$
[\hat\mu_i-1.645\sigma,\ \hat\mu_i+1.645\sigma].
$$

它可能总体覆盖 90%，却在高准确度群体中过宽、低准确度群体中过窄。图 1a–c 将这种差异拆成无校准、通用校准和情境特异校准。图 2、3 再用 UK Biobank 与 All of Us 表明：PGS 准确度差异不仅沿遗传 ancestry descriptors 出现，年龄、性别、收入、教育、贫困指数等也可有相似量级的影响。

论文先用边际指标描述这种现象：

$$
\mathrm{relative}\ \Delta R^2=
\frac{R^2_{\mathrm{top/group1}}-R^2_{\mathrm{bottom/group2}}}{R^2_{\mathrm{all}}}.
$$

连续情境比较顶/底五分位，二元情境比较两组。它直观但一次只看一个情境；CalPred 的方差系数 $\beta_\sigma$ 则在联合模型中估计某个情境对残差不确定性的独立贡献。

### 定量性状模型

令 $x_i$ 是均值设计矩阵的一行，通常包含 PGS、情境变量和选择性的 PGS×context 项；令 $z_i$ 是方差设计矩阵的一行。CalPred 假设

$$
y_i\sim N(\mu_i,\sigma_i^2),\qquad
\mu_i=x_i^\top\beta_\mu,qquad
\sigma_i^2=\exp(z_i^\top\beta_\sigma).
$$

指数链接保证方差为正。目标个体的预测为

$$
\hat\mu_i=x_i^\top\hat\beta_\mu,qquad
\hat\sigma_i=\sqrt{\exp(z_i^\top\hat\beta_\sigma)},
$$

任意置信水平 $1-\alpha$ 的区间是

$$
\hat\mu_i\pm \Phi^{-1}(1-\alpha/2)\hat\sigma_i.
$$

正式包 `calpred/method.py:146-229` 自动给均值和方差设计各加常数列，把三份临时文本交给 `calpred.R`，再加载均值/方差系数及标准误。R 端 `calpred.R:4-40` 调用 `statmod::remlscore` 拟合异方差正态模型。Python 的 `predict()` 完整对应上面的均值和标准差公式。

一个重要接口细节是：docstring 明确要求 `x`、`z` 不带截距，函数内部会自动添加；用户若预先加了重复常数列，可能造成列名/共线性问题。预测时还会严格检查 DataFrame 列顺序与拟合系数索引一致，因此训练/目标数据不能只保证“列集合相同”，还要保证顺序相同。

### 均值校准、斜率交互与方差校准解决不同问题

论文模拟（图 4）把失败分成两类：

- PGS 在另一个情境中回归斜率改变，属于均值偏差；需要 context 和 PGS×context 调整；
- 同一均值附近的残差散布改变，属于异方差；需要 variance-by-context（VbyC）。

手稿仓的扩展实现将点预测乘以情境斜率：

$$
\mu_i=(x_i^\top\beta_\mu),[1+s_i^\top\beta_s]
\quad (+\text{optional intercept component}),
$$

并在 `calpgs/ext.R` 中交替更新 REML 方差/均值参数和加权最小二乘斜率参数。正式包的简洁 `fit(y,x,z)` 没有单独 `slope_covar` 参数；调用者可自行把交互列放进 $x$，但这与手稿乘法式 slope extension 并非完全相同。

手稿 final-pipeline 也没有为每个情境盲目加入全部 PGS 交互，而是选择 `PGS×AGE`、`PGS×SEX`、`PGS×PC1`、`PGS×PC2` 等列。论文概念上说 PGS×context，实际数值复现必须追踪具体 trait、数据集和 notebook 的列清单。

### 表型与协变量预处理不在核心 API 内自动完成

定量分析通常先对表型做秩逆正态变换：

$$
q_i=\Phi^{-1}\left(\frac{\operatorname{rank}(y_i)-0.5}{n}\right).
$$

正式包 `calpred/utils.py:10-37` 提供 `quantile_normalize()` 和可双向插值的 `QMap`。但手稿 final notebook 使用另一个导入的 quantile-normalize 函数；中位数插补、标准化、变量重命名和交互列生成也在 notebook 中，而不是 `fit()` 内。因此原始表型直接传入包和论文分析的标准化输入不是自动等价的。

把标准化尺度上的区间映回原表型尺度时还要经过经验分位映射，尾部外推受校准样本支持范围限制。极端个体的反变换区间不能被理解为参数模型在原尺度上的精确正态区间。

### 二元疾病模型：为什么方差端没有截距

对疾病状态 $y_i\in\{0,1\}$，CalPred 使用异方差 probit 潜变量：

$$
y_i=\mathbf{1}(y_i^*>0),\qquad
y_i^*=x_i^\top\beta_\mu+\epsilon_i,qquad
\epsilon_i\sim N(0,\exp(z_i^\top\beta_\sigma)).
$$

所以疾病概率为

$$
P(y_i=1)=\Phi\left(\frac{x_i^\top\beta_\mu}
{\sqrt{\exp(z_i^\top\beta_\sigma)}}\right).
$$

`fit_binary()` 只给均值矩阵加截距，故意不给方差矩阵加截距（`calpred/method.py:232-298`）。原因不是遗漏，而是 probit 潜变量整体尺度不可识别：若方差端也有自由常数，可同时缩放均值和标准差而不改变概率。R 端 `calpred_binary.R:7-34` 使用 `Rchoice::hetprob(link="probit")`，并把包返回的尺度系数乘 2，从 log-standard-deviation 参数转换到 Python 后续使用的 log-variance 参数；`predict_binary()` 再按上式计算正态 CDF。

图 8 的 T2D 结果应这样理解：仅看总体校准的模型在低/高收入群体中可分别低估和高估风险；加入 context、交互与 VbyC 后，观察病例比例更接近预测概率。它不是说收入本身是遗传因果因素，而是收入作为测得情境携带了与风险基线和预测误差相关的信息。

### 从校准集到目标集的完整流程

1. 在独立训练数据中得到 PGS 权重；CalPred 本身不重新估计 SNP 效应。
2. 在代表目标人群的校准集中计算 PGS、真实表型与情境变量。
3. 按论文流程做缺失处理、标准化和必要的表型秩变换。
4. 明确构造均值矩阵 $X$、方差矩阵 $Z$，以及需要时的 PGS×context/slope 设计。
5. 拟合 $\beta_\mu,\beta_\sigma$；疾病模型走异方差 probit。
6. 在目标个体上用同样的列、顺序和预处理计算均值、标准差/风险概率。
7. 不只检查总体指标，还按关键情境检查覆盖率或 observed-vs-predicted risk。

CalPred 的外推假设非常关键：校准样本必须覆盖目标人的情境范围。图 5 与 Extended Data Fig. 7 支持在模拟设定下 $N_{cal}>500$ 且相关情境被测量时估计较可靠；这不是所有真实高维设计都只需 500 人的通用样本量定理。

### 图 1–8 串成的证据链

- **图 1** 定义任务：总体 90% 不足够，必须按情境达到覆盖目标。
- **图 2–3** 先证明问题存在：UK Biobank 和 All of Us 的 PGS $R^2$ 与方差系数沿多类情境变化；这些是关联与预测性能差异，不是情境对遗传效应的因果证明。
- **图 4** 用两情境模拟分离均值交互与异方差的作用；二者联合才同时修正中心和区间。
- **图 5** 在多个相关情境的模拟中显示通用区间可总体正确、亚组错误，而 CalPred 接近亚组 90%。
- **图 6** 在 LDL 上把年龄等变量对应到区间宽度；论文报告年轻/年长组预测 s.d. 约 27.4/34.3 mg dl⁻¹。
- **图 7** 汇总多个性状和人群的个体预测 s.d. 变化，说明并非 LDL 特例。
- **图 8** 将框架扩到 T2D 风险，强调总体风险校准会掩盖收入分组失准。

补充和 Extended Data 覆盖参数估计、漏掉相关 context、样本量、更多性状/人群与敏感性分析。它们扩展了证据范围，但仍依赖 UK Biobank/All of Us 的选择、测量与表型匹配。

### 代码级评估边界

`compute_group_stats()` 在 `calpred/utils.py:40-176` 计算分组 $R^2$、覆盖率和一个名为 `length` 的量。覆盖率使用 $\hat\mu\pm z\hat\sigma$，与方法一致；但 `length` 实际实现为平均 $z\hat\sigma$，这是**半宽度**，完整区间长度应是 $2z\hat\sigma$。比较组间相对变化时比例不变，但绝对“interval length”数值会少一倍，文档/绘图若使用该列必须注明。

bootstrap 使用全表有放回抽样，再在样本内分组；这保留总体组比例的随机波动，而不是每组固定样本量的分层 bootstrap。`return_r2_diff` 又按结果行首尾相减，依赖 group 排序语义，调用者需要确认首尾正是预期比较组。

Python 拟合通过临时文件调用外部 `Rscript`，依赖 R 包 `statmod` 或 `Rchoice`。`subprocess.run()` 没有 `check=True`，R 失败通常会在随后读取输出文件时才暴露，而不是立即给出清晰的 R 返回码错误。二元拟合的 `verbose` 输出重定向条件也与参数名直觉相反：当前代码在 `verbose=True` 时将 stdout 丢弃。

### Paper–code 对应关系

#### 直接匹配

- 定量异方差正态模型、指数方差链接、个体预测 s.d.；
- 正态分位数预测区间和分组覆盖率；
- 二元异方差 probit 与 $\Phi(\mu/\sigma)$ 风险；
- 定量 `statmod::remlscore`、疾病 `Rchoice::hetprob`；
- 模拟、分组 $R^2$/coverage 和 bootstrap 工具。

#### 部分匹配或多版本边界

- 正式包提供简化 $X/Z$ API；论文手稿还使用独立 slope-coordinate-descent 扩展；
- 论文广义描述 PGS×context，final notebook 只选择部分交互；
- 包有 quantile 工具，但论文 final pipeline 使用 notebook/外部实现完成预处理；
- 正式包不是端到端 PGS 训练或论文作图工具。

### 最简心智模型

CalPred 可以记成一句公式和一句限制：

$$
\text{点预测由 }X\beta_\mu\text{ 校准，区间宽度由 }
\sqrt{\exp(Z\beta_\sigma)}\text{ 校准。}
$$

它能在已测情境和有代表性的校准数据范围内诚实地改变不确定性，却不能补回一个本身缺乏可迁移遗传信号的 PGS，也不能自动处理未测量情境、因果混杂或校准范围之外的个体。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CalPred

### Motivation and Novelty

Polygenic scores (PGS) are commonly reported as point predictions or risks, but their accuracy is not constant across target individuals. Accuracy can vary by genetic ancestry, age, sex, socioeconomic context, BMI and other measured variables. A single generic prediction interval can therefore be calibrated on average while under-covering one context group and over-covering another.

CalPred reframes PGS portability as a calibration problem. Given pretrained PGS weights and a representative calibration biobank with genotype, phenotype and context measurements, it learns individual-specific prediction intervals or disease probabilities that vary by context. The novelty is not improved PGS weight estimation; it is calibrated uncertainty for applying existing PGS across heterogeneous target populations.

Compared with earlier PGS portability work such as Martin et al. (Nature Genetics, 2019), Mostafavi et al. (eLife, 2020), Privé et al. (AJHG, 2022) and Ding et al. (Nature, 2023), CalPred moves from documenting variable accuracy to producing context-specific prediction intervals. Compared with generic calibration approaches such as Chatterjee et al. (Nature Reviews Genetics, 2016), Wei et al. (Journal of Medical Genetics, 2022), Sun et al. (Nature Communications, 2021) and broader calibration literature, it explicitly models measured contexts through a heteroskedastic regression.

### Method Overview

For quantitative traits, CalPred models phenotype as

$$
y_i \sim \mathcal{N}(\mu(\mathbf{c}_i), \sigma^2(\mathbf{c}_i)),
$$

where the mean model uses PGS, contexts and selected PGS x context terms, and the variance model uses

$$
\sigma^2(\mathbf{c}_i)=\exp(\mathbf{c}_i^\top\beta_\sigma).
$$

The fitted $\hat{\mu}$ and $\hat{\sigma}$ define individual prediction intervals, such as $\hat{\mu}\pm1.645\hat{\sigma}$ for a 90% interval. For nonnormal quantitative phenotypes, the workflow uses rank-based inverse normal transformation and maps intervals back to the original scale. For disease traits, CalPred supports a heteroskedastic probit/liability formulation and compares it with logistic models that add contexts and PGS x context terms.

The official `calpred` package implements the core model with a Python/R bridge: Python builds mean and variance design matrices, R `statmod::remlscore` fits the quantitative heteroskedastic model, and R `Rchoice::hetprob` fits the binary heteroskedastic probit. The `calpred-manuscript` repository contains notebook-based workflows for the paper analyses.

### Evaluation

The paper first shows that context-specific PGS accuracy is pervasive. In UK Biobank, all 72 evaluated traits have at least one context affecting PGS accuracy, and 264 of 792 PGS-context pairs are significant. In All of Us, all 12 matched PGS have at least one significant context effect, with socioeconomic variables showing especially strong roles.

Simulation studies show the two CalPred components address different failures. PGS x context terms correct biased slopes/means, while variance-by-context corrects interval width. With multiple simulated contexts, generic intervals are calibrated only overall but miscalibrated within PC1, age or sex strata; CalPred restores approximately 90% subgroup coverage when relevant contexts are measured.

In real data, the LDL case study shows context-specific intervals correct age/PC/sex subgroup coverage and reveal large individual uncertainty differences. Across traits, prediction s.d. differences between top and bottom uncertainty deciles average 30% in UK Biobank and 47% in All of Us. For disease traits, the T2D example shows baseline predicted risks are miscalibrated across household income groups, while adding contexts and interactions improves calibration.

### Reproducibility

**Rating: 3/5.**

The core algorithm is reproducible from public code. The package cleanly implements the heteroskedastic mean/variance model, prediction s.d. calculation, binary probit extension, quantile-normalization utility and grouped calibration metrics. The code-paper match is strongest for the mathematical model.

Full numerical reproduction of the paper is harder. The manuscript workflows are mostly notebooks and depend on controlled UK Biobank and All of Us data stored under institutional paths. Public code verifies the analysis structure, but not all reported biobank-scale results can be regenerated without restricted data access and substantial environment setup. The exact Fig. 8 four-model T2D income workflow was not found as a clean standalone script in this pass.

### Practical Takeaway

CalPred is best understood as a calibration layer for existing PGS. It asks whether a given prediction should be trusted equally across individuals and provides a way to report uncertainty that reflects measured context. Its strongest use case is a health-system or biobank setting where local calibration data are representative of future target individuals and include the contexts that matter for prediction accuracy.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
