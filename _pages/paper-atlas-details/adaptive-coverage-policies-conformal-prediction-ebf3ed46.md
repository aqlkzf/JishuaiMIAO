---
layout: default
permalink: /paper-atlas/adaptive-coverage-policies-conformal-prediction-ebf3ed46/
title: "Adaptive_Coverage_Policies_Conformal_Prediction"
nav: false
description: "用 soft-rank e-value 构造 conformal set；把校准集逐个 leave-one-out，合成 n 个伪 conformal 任务；训练一个小神经网络最小化“预测集合大小 + \\lambda × 失覆盖率”；再通过 bracket + bisection 选择 \\lambda，使平均集合大小接近用户目标 M。"
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
    <h1>Adaptive_Coverage_Policies_Conformal_Prediction</h1>
    <p>Adaptive Coverage Policies in Conformal Prediction</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2510.04318" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Adaptive Coverage Policies：让 conformal prediction 的覆盖水平随样本调整

### 论文要解决什么问题

传统 conformal prediction 先指定失覆盖率 $\alpha$，再对所有测试样本使用同一个覆盖水平 $1-\alpha$。这保证简单清楚，但不够灵活：容易样本可能得到过大的集合，困难样本则可能得到空集或无法操作的集合。更麻烦的是，如果看过数据后再选择 $\alpha$，普通 conformal 的标准覆盖保证通常不再成立。

本文提出一个 **coverage policy**：它根据校准分数和当前测试样本，输出样本特异的失覆盖率 $\tilde\alpha$。核心并不是普通的条件覆盖，而是借助 e-value 获得允许数据依赖选择 $\tilde\alpha$ 的 post-hoc validity。

### 一句话方法

用 soft-rank e-value 构造 conformal set；把校准集逐个 leave-one-out，合成 $n$ 个伪 conformal 任务；训练一个小神经网络最小化“预测集合大小 + $\lambda$ × 失覆盖率”；再通过 bracket + bisection 选择 $\lambda$，使平均集合大小接近用户目标 $M$。

### 1. 为什么要用 e-value

对非负、可交换的 nonconformity score $S$，soft-rank e-value 是

$$
E(x,y)=\frac{S(x,y)}{\frac{1}{n+1}\left(\sum_{i=1}^{n}S(X_i,Y_i)+S(x,y)\right)}.
$$

用阈值 $1/\tilde\alpha$ 定义预测集合：

$$
\hat C_n^{\tilde\alpha}(x)=\{y:E(x,y)<1/\tilde\alpha\}.
$$

关键保证为

$$
\mathbb E\!\left[
\frac{\mathbb P(Y_{\rm test}\notin\hat C_n^{\tilde\alpha}(X_{\rm test})\mid\tilde\alpha)}{\tilde\alpha}
\right]\leq1.
$$

因此 $\tilde\alpha$ 可以依赖校准数据和测试数据。注意，这不是“对每个 $X=x$ 都精确覆盖”的 conditional coverage；它是一个 post-hoc 比率保证。

### 2. coverage policy 看什么、输出什么

策略写为

$$
\pi:\mathbb R_+\times\mathcal T\to(0,1).
$$

它的输入是：

1. 校准样本真实标签分数之和 $\sum_i S(X_i,Y_i)$；
2. 测试样本摘要 $t(X_{\rm test})$。

分类中，$t(X)$ 是所有候选类别的分数向量；MAE 回归示例中集合宽度只依赖校准分数之和，所以 $t(X)$ 为空。输出是失覆盖率 $\tilde\alpha$，不是覆盖率本身。

### 3. 用 leave-one-out 制造训练任务

```text
一个大小为 n 的 calibration set
        |
依次留出第 j 个样本
        |
n-1 个样本 = pseudo calibration set
第 j 个样本 = pseudo test point
        |
输入 [其余分数之和, 第 j 个样本的候选标签分数]
        |
coverage network 输出 alpha_tilde_j
```

这样只用一个校准集就得到 $n$ 个训练例子，不必额外保留一批数据训练 coverage policy。代码中的分类策略输入是十个 CIFAR-10 候选标签的交叉熵分数，再加一个校准分数总和，共 11 维；网络只有一个 32-unit ReLU 隐层和 sigmoid 输出层。

### 4. 为什么损失里要加 $\lambda\tilde\alpha$

如果只最小化集合大小，最简单的退化解就是允许极高失覆盖率。论文使用

$$
\mathcal L_\lambda(\theta)=\frac1n\sum_{j=1}^n
\left[
\operatorname{Size}(\hat C_{n-1}^{\tilde\alpha_\theta^j}(X_j))
+\lambda\tilde\alpha_\theta^j
\right].
$$

- 第一项让集合更小、更有信息量；
- 第二项惩罚过大的失覆盖率；
- $\lambda$ 越大，通常越保守，集合越大。

分类集合大小本来是离散基数，论文用 sigmoid 平滑指示函数以便反向传播；回归的 MAE 例子则有解析宽度

$$
2\frac{\sum_iS(X_i,Y_i)}{(n+1)\tilde\alpha-1},\qquad \tilde\alpha>1/(n+1).
$$

### 5. 怎样把平均集合大小调到目标 $M$

算法先不断加倍或减半 $\lambda$，找到平均 LOO set size 位于目标 $M$ 两侧的区间，然后二分。每试一个 $\lambda$ 都重新训练策略并测量 LOO 平均集合大小，直到误差不超过 $\varepsilon$。

论文在“网络恒定输出 $\alpha$”的理想情形证明：

- LOO 平均大小以 $O_P(n^{-1/2})$ 逼近期望测试集合大小；
- 优化后的集合大小随 $\lambda$ 单调不减。

但对实际输入依赖的神经网络策略，这两个性质只是实验上近似成立，论文没有给出一般定理。这是理解方法时最重要的证据边界。

### 实验说明了什么

主实验使用 CIFAR-10、冻结的 EfficientNet-B0 和 $n=100$ 校准样本。与使用相同平均 $\tilde\alpha$ 的 fixed-e baseline 相比，adaptive-e 在 $\lambda=5,10,50$ 时的集合大小分别为 $1.21,1.23,1.63$，小于 $1.26,1.33,1.92$。普通 fixed-p 集合更小，但不支持观察数据后再原则性地选择 $\alpha$。

目标大小实验希望 $M=2$，最终 LOO 均值为 2.00，测试均值为 2.07。回归检查为 8.82 对 9.31。这些结果支持 proxy 的实用性，但样本规模和任务范围都有限。

### 代码和复现边界

官方代码仓库完整覆盖 LOO 构造、平滑集合大小、Eq. (9)、$\lambda$ bracket/bisection 和回归公式，paper-code fidelity 较高。但代码主要由 notebook、保存好的数组和权重组成，没有测试、依赖锁文件或一键运行入口。本次做了直接代码映射和全部六张图的视觉核验，没有重新训练 CIFAR-10 模型。

### 应该怎样理解这项工作

它解决的不是“如何让 conformal set 在所有意义下都更小”，而是“当用户确实需要看数据后再调整覆盖水平时，如何用 e-value 保住合适的统计保证，并把调整规则学习出来”。方法的代价是 e-set 可能比固定 $\alpha$ 的 p-value set 更大；收益是获得合法的 post-hoc adaptivity 和可针对目标平均 set size 优化的策略。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Adaptive Coverage Policies in Conformal Prediction

### Paper summary

Classical conformal prediction requires a miscoverage level $\alpha$ to be fixed before observing calibration and test data, even though different examples may need different coverage/size trade-offs. This paper learns an adaptive coverage policy that selects a data-dependent $\tilde\alpha$ for each test example while retaining a post-hoc-valid conformal e-prediction guarantee. It is a statistical machine-learning and uncertainty-quantification method paper, accepted at AISTATS 2026; the analyzed source is arXiv `2510.04318v2`.

### Method in brief

The method forms prediction sets by thresholding soft-rank e-values. A small neural network maps the calibration-score sum and a test-score summary to $\tilde\alpha$. Because only one calibration set may be available, each calibration observation is held out in turn to create a pseudo calibration/test episode. The network minimizes average differentiable prediction-set size plus $\lambda\tilde\alpha$, preventing the degenerate zero-coverage solution. To target a user-chosen expected set size $M$, the algorithm brackets and bisects $\lambda$, retraining the policy and measuring mean leave-one-out size at each step.

The paper proves that mean LOO size estimates expected test size at $O_P(n^{-1/2})$ and is monotone in $\lambda$ only for a constant-output $\alpha$. The analogous behavior for an input-dependent neural policy is supported empirically, not theoretically guaranteed.

### Evaluation

The main experiment uses CIFAR-10, a frozen EfficientNet-B0 (91.1% test accuracy), cross-entropy scores, and calibration size $n=100$. Across five calibration splits, adaptive e-sets are smaller than fixed e-sets at the compared mean adaptive alpha: mean sizes are $1.21/1.23/1.63$ versus $1.26/1.33/1.92$ for $\lambda=5/10/50$. Fixed p-value conformal yields still smaller sets but cannot validly choose $\alpha$ post hoc. The target-size procedure reaches LOO mean 2.00 and test mean 2.07. A synthetic regression check obtains 8.82 versus 9.31.

### What is novel

- It uses conformal e-values so the coverage level may depend on observed data without invalidating the stated post-hoc ratio guarantee.
- It turns one calibration set into policy-training data through leave-one-out pseudo episodes rather than reserving a separate policy-training set.
- It optimizes the expected-size/miscoverage trade-off and provides a practical $\lambda$ search for a desired mean set size.

### Reproducibility and limitations

The official repository is available at `https://github.com/GauthierE/adaptive-coverage-policies`, analyzed at `main@55a415ba16be96b68bf61e919e014fdd4cd0dfcc`. Code-paper fidelity is high for the reported experiments: the notebooks directly implement the LOO construction, smooth classification size, penalized objective, target-size search, and regression interval. Saved model/output artifacts and plots are included.

Reproducibility is **3.5/5**. The release is notebook-centered, lacks tests, dependency pinning, and a one-command pipeline, and contains a large pretrained weight. Numerical experiments were not rerun. The evidence is limited to CIFAR-10 and a simple synthetic regression task; the post-hoc guarantee is not conditional coverage; and the regression construction has constant width unless paired with a more locally adaptive score/e-variable.

### Publication metadata

- Authors: Etienne Gauthier, Francis Bach, Michael I. Jordan.
- Venue: AISTATS 2026 acceptance verified on the official conference virtual poster page.
- arXiv: `2510.04318v2`, first submitted 2025-10-05 and revised 2026-04-02.
- DOI: `10.48550/arXiv.2510.04318`.
- PMLR volume/publisher DOI: **Not found as of 2026-07-22**; no archival identifier is invented here.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
