---
layout: default
permalink: /paper-atlas/minimum-volume-conformal-sets-multivariate-regression-fdc97360/
title: "Minimum_Volume_Conformal_Sets_Multivariate_Regression"
nav: false
description: "多变量回归的输出 Y\\in\\mathbb{R}^k 不是一个数，而是一个向量。我们希望对每个输入 x 给出一个区域 C(x)：真实输出以至少 1-\\alpha 的概率落在区域里，同时区域尽可能小。只追求覆盖率很容易——给出一个巨大区域即可；真正困难的是在有限样本有效性和信息量之间取得平衡。 已有方法各有明显约束：逐维分位数区间的笛卡尔积忽略输出维度之间的相关性；经验协方差椭球假设近似椭圆结构；"
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
      <span>Journal of the American Statistical Association · 2026</span>
    </div>
    <h1>Minimum_Volume_Conformal_Sets_Multivariate_Regression</h1>
    <p>Minimum Volume Conformal Sets for Multivariate Regression</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1080/01621459.2026.2692078" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 最小体积多变量共形预测集（MVCS）

### 它解决什么问题

多变量回归的输出 $Y\in\mathbb{R}^k$ 不是一个数，而是一个向量。我们希望对每个输入 $x$ 给出一个区域 $C(x)$：真实输出以至少 $1-\alpha$ 的概率落在区域里，同时区域尽可能小。只追求覆盖率很容易——给出一个巨大区域即可；真正困难的是在有限样本有效性和信息量之间取得平衡。

已有方法各有明显约束：逐维分位数区间的笛卡尔积忽略输出维度之间的相关性；经验协方差椭球假设近似椭圆结构；copula、密度估计和最优传输方法更灵活，但在高维中可能昂贵或不稳定。MVCS 的核心选择是：把“区域体积”直接写进训练目标，而不是先训练点预测器、再事后套一个固定形状。

### 核心直觉

把预测区域写成变换后的 $p$-范数球：

$$
C(x)=\{y:\|M(x)(y-f_\theta(x))\|_p\le q\}.
$$

- $f_\theta(x)$ 决定中心；
- $M(x)$ 决定局部方向、伸缩和体积；
- $p$ 决定边界形状；
- $q$ 是最后用独立校准集得到的共形半径。

矩阵行列式越大，逆变换后的集合体积越小；但集合太小会漏掉训练点。作者用变换后残差的第 $r$ 大值 $\sigma_r$ 把覆盖约束变成一个可优化的次序统计量：目标一边压缩行列式体积，一边确保至少 $n-r+1$ 个点仍被覆盖。这就是“最小体积覆盖集”。

### 从静态集合到局部自适应回归

论文先研究固定点云的 MVCS。固定范数时，组合覆盖约束是非凸的；作者给出差分凸（DCA）重写和凸松弛。DCA 每次线性化目标中的凹部分，目标值单调下降，但只能保证收敛到局部解。学习 $p$ 后，集合可以从菱形状、椭圆状过渡到近似盒状；多个范数还能让不同方向具有不同曲率，从而得到非对称形状。

回归中，真正有用的是让不确定性随 $x$ 变化。模型令

$$
\Lambda(x)=A_\phi(x)A_\phi(x)^\top,
$$

因此无需约束优化也能保证矩阵半正定。局部目标同时最小化测试点平均意义下的逆行列式体积，并惩罚第 $r$ 大的变换残差。这样，噪声较小的区域得到紧凑集合，噪声较大或方向发生变化的区域得到更大、旋转后的集合。

### 训练与预测流程

```text
数据
 ├─ 训练集：学习模型
 ├─ 验证集：早停和模型选择
 ├─ 校准集：只计算共形分位数
 └─ 测试集：评估覆盖率和体积

训练集
  1. 用 MSE 预训练中心 f_theta
  2. 固定中心，学习矩阵网络 A_phi(x) 与范数 p
  3. 联合微调中心、矩阵网络和 p
  4. 每个小批量用 r=floor(alpha*B) 对应的第 r 大残差近似覆盖项

独立校准集
  5. 计算 s_i = ||Lambda(x_i)(y_i-f_theta(x_i))||_p
  6. 取有限样本修正后的 (1-alpha) 分位数 q_hat

新样本 x
  7. 输出 {y: ||Lambda(x)(y-f_theta(x))||_p <= q_hat}
```

### 为什么共形步骤仍然必要

训练损失只让训练数据上的集合紧且覆盖率高，不能自动保证新样本有效。独立校准集把学到的几何形状与严格的覆盖半径分开：形状由训练学习，半径由校准分数的秩确定。在交换性且分数无并列的条件下，Lemma 4.1 给出有限样本边际覆盖区间

$$
[1-\alpha,\;1-\alpha+1/(n_{cal}+1)).
$$

这里保证的是对随机测试点总体的**边际覆盖**，不是对每一个固定 $x$ 的条件覆盖。论文明确指出，过度压缩体积可能损害样本稀疏区域的条件可靠性。

### 实验结论

基线包括逐维朴素分位数回归、全局经验协方差椭球和局部经验协方差椭球。在四个四维合成设置、目标覆盖率 90% 时，MVCS 的归一化体积全部最小，覆盖率约为 89.7%–90.0%。九个真实多输出回归数据集、90% 和 99% 两种覆盖水平共 18 个比较中，MVCS 在 16 个比较里体积最小，同时覆盖率接近目标值。例外是 90% 的 Bias correction 和 99% 的 scm1d。

图 1 直观展示了学习 $p$ 和多范数如何适配相关高斯、指数和非对称混合分布；图 7 显示同一模型会对不同 $x$ 产生不同大小和方向的集合；图 8 展示了在非对称噪声下 MVCS 与 pinball loss 的边界差异。

### 代码对应与边界

公开仓库 `ElSacho/MVCS` 的 `code/MVCS.py` 实现中心、局部 PSD 矩阵、联合训练和共形校准；`code/torch_functions.py` 实现 $p$-范数、单位球体积、次序统计量和 MVCS 损失；实验目录包含 DCA、真实数据和合成数据流程。核心单范数局部自适应方法与论文吻合度较高，但 MSE 预训练在公共类之外完成，未找到可复用的多范数 API，也没有自动化测试。

还应保留三点限制：非凸优化没有全局最优保证；矩阵网络学习率等超参数依数据集而变；边际有效并不等于条件有效。因完整实验涉及多个大数据集和大量配置，本次分析验证了源码路径和静态可编译性，没有重跑整套基准。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Minimum Volume Conformal Sets for Multivariate Regression

### Overview

Multivariate conformal regression needs prediction regions that are valid but also geometrically efficient. Products of marginal intervals ignore dependence; empirical-covariance ellipsoids impose elliptical symmetry; copula, density, and optimal-transport approaches can be costly or high variance. Braun, Aolaritei, Jordan, and Bach formulate prediction-region learning directly as minimum-volume covering-set (MVCS) optimization and then apply split conformal calibration for finite-sample marginal validity.

The method learns three coupled components: a center predictor $f_\theta(x)$, a covariate-dependent positive-semidefinite transform $M(x)$, and a norm order $p$. Its training loss combines inverse determinants (set volume) with an order statistic of transformed residual norms (empirical coverage). Single learned norms adapt between diamond-, ellipse-, and box-like shapes; a multi-norm formulation can produce asymmetric regions. For regression, the implementation parameterizes the transform as $A(x)A(x)^\top$ and performs center pretraining, matrix-only fitting, then joint optimization.

After training, the score $s(x,y)=\|M(x)(y-f_\theta(x))\|_p$ is evaluated on an independent calibration set. The finite-sample corrected empirical quantile rescales the learned region. Under exchangeability and no ties, the resulting set has conditional-on-training marginal coverage between $1-\alpha$ and $1-\alpha+1/(n_{cal}+1)$; this is not a guarantee of coverage conditional on every covariate value.

### Evaluation

The paper compares MVCS with naïve quantile regression, global empirical covariance, and local empirical covariance. In four synthetic 4-D response settings at 90% target coverage, MVCS has the smallest normalized volume in every setting while achieving roughly 89.7–90.0% coverage. Across nine real multivariate-regression datasets and target coverages of 90% and 99%, it reports the best normalized volume in 16 of 18 comparisons with observed coverage close to nominal. Visual experiments show that learned norms follow non-elliptical support and that $M(x)$ changes size and orientation with heteroskedasticity.

### Reproducibility and limitations

The paper's public repository, `https://github.com/ElSacho/MVCS`, was analyzed at commit `9e9ec51968bafa3ce5e40664c4641b32941aee9a`. Core single-norm adaptive loss, PSD transform, conformal quantile, volume, coverage, DCA experiments, datasets, configurations, notebooks, and saved results are present. Code-paper fidelity is **medium-high**: the central adaptive single-norm method is direct, while MSE pretraining lives outside the reusable class and no reusable multi-norm API or automated tests were found. Full experiments were not rerun; core Python files pass static compilation.

The main scientific limits are nonconvex optimization without global guarantees, dataset-sensitive hyperparameters, and a potential tension between aggressive volume minimization and conditional coverage. The method requires an independent calibration split and is trained for a fixed confidence level, though it can be recalibrated post hoc. No separate supplementary document was found.

### Publication identity

The source analyzed is arXiv `2503.19068` (first submitted 24 March 2025; version 2 updated 18 March 2026). Michael I. Jordan's publication list and Crossref identify the archival publication as *Journal of the American Statistical Association* (2026), DOI `10.1080/01621459.2026.2692078`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
