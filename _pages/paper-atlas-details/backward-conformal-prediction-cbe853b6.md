---
layout: default
permalink: /paper-atlas/backward-conformal-prediction-cbe853b6/
title: "Backward_Conformal_Prediction"
nav: false
description: "普通 conformal prediction 是“先定覆盖率，再看集合有多大”；Backward Conformal Prediction（BCP）把顺序反过来：先规定预测集合最多能有几个标签，再让算法自适应选择误覆盖水平，并估计这样做实际对应的边际可靠性。"
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
      <span>Advances in Neural Information Processing Systems (NeurIPS) · 2025</span>
    </div>
    <h1>Backward_Conformal_Prediction</h1>
    <p>Backward Conformal Prediction</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Backward Conformal Prediction 方法详解

### 一句话理解

普通 conformal prediction 是“先定覆盖率，再看集合有多大”；Backward Conformal Prediction（BCP）把顺序反过来：**先规定预测集合最多能有几个标签，再让算法自适应选择误覆盖水平，并估计这样做实际对应的边际可靠性。**

### 问题设定

输入包括：已经训练好的分类模型或非符合度分数 $S(x,y)$、$n$ 个有标签校准样本、新样本特征 $X_{\rm test}$，以及用户给出的集合大小规则 $\mathcal T$。分数越小，候选标签 $y$ 与样本 $x$ 越匹配。$\mathcal T$ 可以是常数，例如集合最多含 1 个标签；也可以依赖校准集和当前测试特征，让困难样本获得更大的集合。

输出有两个：满足大小约束的标签集合 $\hat C_n^{\tilde\alpha}(X_{\rm test})$，以及用 $1-\hat\alpha^{\rm LOO}$ 表示的**边际覆盖率估计**。

### 核心步骤

#### 1. 用 e-value 比较候选标签

对每个候选标签 $y$，计算

$$
\mathbf E_y^{\rm test}=\frac{S(X_{\rm test},y)}
{\frac1{n+1}\left(\sum_{i=1}^nS(X_i,Y_i)+S(X_{\rm test},y)\right)}.
$$

它衡量测试候选分数相对于校准分数平均水平有多异常。在交换性条件下，真实标签对应的量是 e-variable。固定 $\alpha$ 时，保留 $\mathbf E_y^{\rm test}<1/\alpha$ 的标签即可得到 e-value conformal set。

#### 2. 不固定 $\alpha$，而固定集合大小

BCP 选择

$$
\tilde\alpha=\inf\left\{\alpha:\#\{y:\mathbf E_y^{\rm test}<1/\alpha\}\leq\mathcal T\right\}.
$$

当 $\alpha$ 增大时，阈值 $1/\alpha$ 变小，集合随之收缩。论文实验通过二分搜索找到最小可行 $\tilde\alpha$，容差为 0.005。

#### 3. 用校准集做 leave-one-out

测试标签未知，因此无法直接知道这种自适应选择平均会带来多少误覆盖。算法依次把第 $j$ 个校准样本当作“伪测试样本”，用其余样本重新构造比例并得到 $\tilde\alpha_j$，最后计算

$$
\hat\alpha^{\rm LOO}=\frac1n\sum_{j=1}^n\tilde\alpha_j.
$$

直觉上，它回答的是：如果校准点轮流成为新样本，同一个大小规则平均需要多大的误覆盖水平？它估计的是总体量 $\mathbb E[\tilde\alpha]$，不是当前单个测试样本的真实出错概率。

```text
校准分数 + 测试特征 + 大小规则 T
              |
              v
      每个标签的 e-value 比例
              |
              v
  二分搜索 alpha_tilde，使集合大小 <= T
              |
       +------+------+
       |             |
       v             v
    预测集合      校准点逐一作为伪测试点
                     |
                     v
              平均得到 alpha_hat_LOO
                     |
                     v
            返回集合和边际覆盖率估计
```

### 保证应当怎样解读

论文的精确 post-hoc 结论是

$$
\mathbb E\left[\frac{\mathbb P(\text{miscoverage}\mid\tilde\alpha)}{\tilde\alpha}\right]\leq1.
$$

常见而直观的

$$
\mathbb P(\text{coverage})\geq1-\mathbb E[\tilde\alpha]
$$

在正文中依赖一阶 Taylor 近似，不能写成无条件的精确有限样本保证。论文还证明，在分数有界、样本 i.i.d.、比例非退化等条件下，常数大小规则有

$$
|\hat\alpha^{\rm LOO}-\mathbb E[\tilde\alpha]|=O_P(n^{-1/2}),
\qquad
\operatorname{Var}(\hat\alpha^{\rm LOO})=O(1/n).
$$

一般的数据依赖规则还需要稳定性假设 P3。附录 D 给出不使用 Taylor 近似的另一种界，但它依赖 $\tilde\alpha^2$、分数矩和余项，并不是把上述简单公式原样“精确化”。

### 实验与代码

主要实验在 CIFAR-10 上使用 EfficientNet-B0，组合三种校准规模和三种大小上限，各重复 200 次。随着 $n$ 增大，LOO 估计越来越接近平均自适应误覆盖。附录还用 Breast Cancer Wisconsin 展示二分类中普通 conformal set 可能包含两个标签，以及用局部邻域标签熵把 CIFAR 样本映射到 1–3 的自适应大小。

官方仓库提供这些实验的 notebook 和模型权重，但代码忠实度只能评为 **medium**。论文的 LOO 伪比例分母是 $n$ 项平均，因此等价乘子是 $n$；两个 CIFAR notebook 却使用 `calibration_size + 1`，即 $n+1$。这会改变有限样本下的 $\tilde\alpha_j$，虽然相对差异随 $n$ 增大而减小。仓库也没有独立软件包、测试、环境锁或附录 D 的实现。

### 适用边界

- 给的是边际覆盖，不是条件覆盖或单样本覆盖保证。
- $\mathcal T$ 越激进，覆盖率可能越低；算法只是让这种权衡可计算。
- 自适应 $\mathcal T$ 的理论需要稳定性，示例中的熵分箱也不是最优学习规则。
- 论文只实验了分类，回归仍是未来方向。
- 高风险应用中的医学例子只是动机和小型数据实验，不能视为临床验证。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Backward Conformal Prediction

### Paper summary

Backward Conformal Prediction (BCP) reverses the usual design of split conformal prediction. Rather than fixing a target miscoverage $\alpha$ and accepting whatever prediction-set size results, it lets the practitioner specify a fixed or data-dependent maximum set size $\mathcal T$ and chooses an adaptive level $\tilde\alpha$ that makes an e-value conformal set obey that cap. Since the resulting coverage is no longer fixed in advance, the paper introduces a leave-one-out estimator $\hat\alpha^{\rm LOO}$ for the marginal adaptive miscoverage $\mathbb E[\tilde\alpha]$.

This is a statistical machine-learning method paper, not a bioinformatics paper. It is authored by Etienne Gauthier, Francis Bach, and Michael I. Jordan. The Berkeley page lists NeurIPS 2025; the canonical acquired source is arXiv `2505.13732v5`, and the arXiv source contains the NeurIPS 2025 template. No archival DOI was found.

### Why it is needed

Standard conformal prediction provides distribution-free marginal coverage under exchangeability, but it does not promise that the resulting set is actionable. In binary diagnosis, for example, the set may contain both labels. Prior methods can optimize or adapt efficiency, but BCP directly makes a cardinality rule the primary design input. The cost is that coverage becomes an estimated consequence of the chosen cap instead of a fixed user guarantee.

### Method in brief

For each candidate label, BCP divides its test nonconformity score by the average of the $n$ calibration true-label scores plus that candidate score. These ratios are e-values under exchangeability. It then finds the smallest $\tilde\alpha$ for which the number of candidate ratios below $1/\tilde\alpha$ is no greater than $\mathcal T$. To estimate reliability without the test label, every calibration point is treated in turn as a pseudo-test point; the corresponding pseudo-levels are averaged into $\hat\alpha^{\rm LOO}$.

The exact result is a post-hoc e-value ratio guarantee. The simple statement

$$
\mathbb P(Y_{\rm test}\in\hat C_n^{\tilde\alpha}(X_{\rm test}))
\geq1-\mathbb E[\tilde\alpha]
$$

is justified only up to a first-order Taylor approximation. Under bounded-score and stability assumptions, the LOO estimate converges to $\mathbb E[\tilde\alpha]$ at $O_P(n^{-1/2})$ and its variance is $O(1/n)$. Appendix D gives a different, approximation-free second-moment bound; it is not the simple coverage formula made exact.

### Evaluation

The main experiment uses EfficientNet-B0 on CIFAR-10, calibration sizes 100, 1,000, and 5,000, size caps 1–3, and 200 repeated runs. The plots show the LOO estimate increasingly matching the mean adaptive level as calibration size grows, while empirical coverage stays above the plotted approximate marginal target. The appendices include a Breast Cancer Wisconsin binary task and an adaptive CIFAR rule that converts local neighbor-label entropy into allowed sizes 1–3. These are demonstrations of estimation behavior rather than a broad benchmark against many conformal algorithms.

### Reproducibility and limitations

The official repository `GauthierE/backward-cp` contains all three experiment families as notebooks plus pretrained CIFAR checkpoints. Code-paper fidelity is **medium**: cardinality control, binary search, entropy rule, and plots are present, but both CIFAR notebooks use an $n+1$ multiplier in the LOO pseudo-ratio where the displayed paper equation implies $n$. There is no packaged API, dependency lock, test suite, theorem-bound calculator, or implementation of Appendix D.

BCP provides marginal—not conditional or per-test-case—reliability. Tight caps can force lower coverage; adaptive-rule theory needs a stability assumption; the score must satisfy regularity conditions; and only classification is evaluated. The exact alternative is more complex and depends on score moments. Thus BCP is best viewed as a principled interface for explicitly trading set size against estimated marginal reliability, not a way to obtain arbitrary small sets while preserving a chosen fixed coverage.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
