---
layout: default
permalink: /paper-atlas/e-values-expand-scope-conformal-prediction-f4311c84/
title: "E_Values_Expand_Scope_Conformal_Prediction"
nav: false
description: "传统共形预测通常把新样本的 nonconformity score 与校准分数做排序，从而得到 p-value 和固定错误率 \\alpha 下的预测集合。这套方法在标准的“一个交换样本、一个预先确定的覆盖率”场景中很好用，但本文关注三个超出这个模板的问题： 数据按批次持续到达，批次之间允许分布变化，而且不知道何时停止；需要所有时间点同时有效，而不只是每一批分别有效。 实际决策只能容纳最多 C 个候选标签；"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>E_Values_Expand_Scope_Conformal_Prediction</h1>
    <p>E-Values Expand the Scope of Conformal Prediction</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2503.13050" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用 E-value 扩展共形预测：方法详解

### 1. 论文解决什么问题？

传统共形预测通常把新样本的 nonconformity score 与校准分数做排序，从而得到 p-value 和固定错误率 $\alpha$ 下的预测集合。这套方法在标准的“一个交换样本、一个预先确定的覆盖率”场景中很好用，但本文关注三个超出这个模板的问题：

1. 数据按批次持续到达，批次之间允许分布变化，而且不知道何时停止；需要所有时间点同时有效，而不只是每一批分别有效。
2. 实际决策只能容纳最多 $C$ 个候选标签；希望先限制集合大小，再由数据决定可提供的覆盖水平。
3. 一个样本可能有多个合理标签，例如多位专家对同一图像给出不同诊断；把所有标签摊平成样本会破坏普通交换性。

这是一篇统计推断/共形预测方法论文。文中的医院和药物只是应用动机，论文并不是默认的生物信息学论文。

### 2. 核心：把排序 p-value 换成 e-value

令 $S(X,Y)>0$ 为“越大越不符合”的分数。给定 $n$ 个校准分数和一个候选测试分数，定义

$$
E=\frac{S_{n+1}}{\frac1{n+1}\sum_{i=1}^{n+1}S_i}.
$$

在交换性条件下，$E\geq0$ 且 $\mathbb E[E]=1$，因此它是 e-variable。由 Markov 不等式，

$$
\Pr(E\geq1/\alpha)\leq\alpha.
$$

所以对每个候选标签 $y$ 计算 $E(y)$，保留满足 $E(y)<1/\alpha$ 的标签即可形成共形集合。它不比较名次，而是比较测试分数与“包含测试分数在内的平均分数”。

e-value 的三种代数性质分别对应论文的三个方法：

```text
校准分数 + 候选标签分数
            |
            v
       归一化比值 E
       /      |       \
      /       |        \
跨批相乘    取倒数     多专家平均
   |          |           |
任意时刻有效  数据后选 alpha  歧义标签预测
```

### 3. 方法一：按批次、任意时刻都有效

第 $t$ 个批次有 $n_t$ 个校准分数和一个测试分数。定义

$$
E_t=\frac{S_{n_t+1}^t}{\frac1{n_t+1}\sum_{j=1}^{n_t+1}S_j^t},
\qquad
M_t=\prod_{s=1}^tE_s.
$$

只要第 $t$ 批数据在给定过去信息后内部可交换，就有 $\mathbb E[E_t\mid\mathcal F_{t-1}]=1$，因此 $M_t$ 是非负 martingale。Ville 不等式给出

$$
\Pr(\forall t\geq0, M_t<1/\alpha)\geq1-\alpha.
$$

构造第 $t$ 个集合时，把未知测试分数替换为候选标签的分数 $S(X_t,y)$：

$$
y\in\hat C_t
\Longleftrightarrow
M_{t-1}
\frac{S(X_t,y)}{\frac1{n_t+1}(\sum_{j=1}^{n_t}S_j^t+S(X_t,y))}
<1/\alpha.
$$

这样得到的是“所有批次同时覆盖”的概率保证，并且在依据历史自适应停止时仍然有效。批次之间不要求同分布，但批次内部的条件交换性不能丢。

FEMNIST 实验把 50 位 writer 当作 50 批数据，重复 100 次，$\alpha=0.15$。论文报告同时覆盖率 0.94，高于目标 0.85。图中大多数集合不大，但存在大小为 62 的完整标签集合，说明有效性并不自动保证信息量。

一个重要的论文—代码差异是：论文写 $S=1/p_f(Y\mid X)^{1/4}$，notebook 实际写成 $1/\log(1+p_f(Y\mid X))^{1/4}$。二者都保持正值和“概率越低，分数越大”的方向，因此不破坏 e-value 论证，但不能把二者视为完全相同的实验实现。

### 4. 方法二：先定集合大小，再让数据选择覆盖水平

如果 $E$ 是 e-variable，那么 $P=1/E$ 是 post-hoc p-variable。由此得到的精确保证是

$$
\mathbb E\left[
\frac{\Pr(Y_{n+1}\notin\hat C_n^{\tilde\alpha}(X_{n+1})\mid\tilde\alpha)}
{\tilde\alpha}
\right]\leq1,
$$

其中 $\tilde\alpha$ 可以依赖校准数据和测试特征 $X_{n+1}$，但不能偷看真实标签 $Y_{n+1}$。

若最多只允许 $C$ 个候选标签，就计算不同 $\alpha$ 下的集合并选择

$$
\tilde\alpha=\inf\{\alpha:|\hat C_n^\alpha(X_{n+1})|\leq C\}.
$$

实验把候选值离散为 $0.01,0.02,\ldots,0.30$。代码遍历所有标签和所有候选 $\alpha$，选择第一个集合大小不超过 $C$ 的水平。注意，这里最可靠的结论是 post-hoc 的期望相对误差控制；“边际覆盖约为 $1-\mathbb E[\tilde\alpha]$”还使用了一阶 Taylor 近似和集中性条件，并不是对每个已观察 $\tilde\alpha$ 都给出条件覆盖。

代码还有一个工程边界：如果候选网格里没有任何 $\alpha$ 满足大小限制，`next(..., -1)` 会直接使用最后一个网格值，而不是报告不可行。实际系统应显式检查这个情况。

### 5. 方法三：有多个合理真值时平均 e-value

假设每个校准特征 $X_i$ 有 $m$ 个标签 $Y_i^1,\ldots,Y_i^m$。对固定的专家/抽样索引 $j$，构造

$$
E_j=\frac{S_{n+1}}{\frac1{n+1}(\sum_{i=1}^nS_i^j+S_{n+1})}.
$$

每个 $E_j$ 都是 e-variable，而 e-variable 的算术平均仍是 e-variable：

$$
\bar E=\frac1m\sum_{j=1}^mE_j.
$$

因此候选标签集合为

$$
\hat C_n(x)=\left\{y:\frac1m\sum_{j=1}^m
\frac{S(x,y)}{\frac1{n+1}(\sum_{i=1}^nS(X_i,Y_i^j)+S(x,y))}
<1/\alpha\right\},
$$

并具有至少 $1-\alpha$ 的覆盖保证。对应的 p-value 算术平均通常需要乘 2 才有效，因此论文比较的方法只能证明 $1-2\alpha$。

CIFAR-10H 实验保留 857 张歧义图像，比较 $m=1$ 与 $m=20$，重复 200 次。增加 $m$ 会明显降低覆盖率和集合大小在不同划分间的波动。e 方法理论保证更强，但实验中更保守：覆盖约 0.90，集合也更大；p 方法虽只有 $1-2\alpha$ 的理论下界，却经验上接近 $1-\alpha$ 且集合更小。论文明确把这个差距列为未解决问题。

### 6. 如何理解贡献与局限

- 贡献不是发明一个更强的分类器，而是用 e-value 的闭包性质扩展共形推断的可组合性。
- 三个精确保证依赖各自的交换性/条件交换性；若医院内部、writer 内部或固定专家索引下的数据不交换，论文定理不能直接套用。
- e-value 保证覆盖，不保证集合小。批次 product martingale 过小会导致后续集合膨胀。
- data-dependent coverage 不是逐实例条件覆盖；不要把 post-hoc 期望不等式改写成更强但未证明的结论。
- 在普通固定 $\alpha$、完全交换的场景，论文并未声称 e-prediction 总是优于传统 p-prediction。

### 7. 代码可复现性

官方仓库固定在 commit `a8b7c35d2e252d2f6501f461978c34f7cf200da3`。三条实验流水线都能在对应 notebook 中找到，核心公式与数据划分匹配度高；但它是实验 notebook 集合，不是可安装的方法库。FEMNIST 与 CIFAR-10H 需要 notebook/人工准备，依赖版本未锁定，没有测试和一键运行入口。本次分析检查了代码、预训练权重、保存结果和图像，但没有重新执行训练及 100/200 次完整实验。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## E-Values Expand the Scope of Conformal Prediction

### Paper summary

This 2025 arXiv method paper develops conformal **e-prediction** as a flexible alternative to conventional rank/p-value conformal prediction. Its key observation is that a normalized positive nonconformity score

$$
E=\frac{S_{n+1}}{(n+1)^{-1}\sum_{i=1}^{n+1}S_i}
$$

is an e-variable under exchangeability. The paper then uses properties that p-values do not share as cleanly—sequential multiplication, inversion into post-hoc p-variables, and averaging without inflation—to solve three different uncertainty-quantification problems.

1. **Batch anytime-valid sets.** Per-batch e-values are multiplied into a test martingale. Ville's inequality guarantees that every set in an unbounded, adaptively stopped sequence covers simultaneously with probability at least $1-\alpha$, even when distributions shift between batches, provided each batch is conditionally exchangeable.
2. **Fixed-size sets with data-dependent coverage.** Inverting an e-variable gives post-hoc validity, so the procedure may choose $\tilde\alpha$ after seeing calibration data and the test feature. The paper chooses the smallest level whose label set has at most a requested size $C$ and reports the realized coverage level rather than fixing it in advance.
3. **Ambiguous ground truth.** When each feature has $m$ plausible labels, the method averages $m$ expert/label-specific e-values. The average remains an e-variable and gives a $1-\alpha$ theorem, whereas the compared arithmetic p-value construction has only a $1-2\alpha$ guarantee.

The contribution is statistical inference rather than bioinformatics; pharmaceutical and medical examples are motivations alongside supply-chain and image-classification experiments.

### Evidence and results

- **FEMNIST batch experiment:** 50 writers act as heterogeneous sequential batches; a 62-class LeNet is reported at 87.6% test accuracy. Across 100 repetitions with $\alpha=0.15$, simultaneous empirical coverage is 0.94 versus the 0.85 target. Figure 2 shows that most sets are small, but a clear mass at size 62 exposes trivial predictions.
- **FEMNIST fixed-size experiment:** 2,000 calibration images, one held-out test image, 100 repetitions, and an alpha grid from 0.01 to 0.30. Experiments for $C=3$ and $C=5$ show adaptive levels and conservatism consistent with the paper's post-hoc interpretation. The exact theorem controls expected relative error; the familiar marginal $1-\mathbb E[\tilde\alpha]$ statement is based on a first-order approximation plus concentration assumptions.
- **CIFAR-10H ambiguity experiment:** 857 ambiguous images (at least two classes with probability $\geq0.1$), 30% calibration, $m\in\{1,20\}$, and 200 splits at $\alpha=0.3$. More labels reduce variability for both e- and p-prediction. E-prediction is conservative, with about 0.90 coverage and larger sets; p-prediction empirically reaches roughly $1-\alpha$ and yields smaller sets despite its weaker $1-2\alpha$ theorem. The paper leaves this discrepancy open.

### Why standard conformal prediction is insufficient here

Applying a standard marginal conformal set independently to every unknown future batch cannot give one simultaneous guarantee over all times without preallocating error across a known horizon. Choosing a set size after viewing the data invalidates the usual fixed-$\alpha$ interpretation. Pooling multiple labels per feature breaks ordinary exchangeability, while arithmetic averaging of dependent p-values costs a factor of two. E-values directly address these three algebraic obstacles, but they are not claimed to dominate p-values in standard fixed-level exchangeable settings.

### Reproducibility and limitations

Official code is available at `GauthierE/evalues-expand-cp`, pinned here to commit `a8b7c35d2e252d2f6501f461978c34f7cf200da3`. The three experiment folders closely match Sections 2–4: notebooks explicitly implement the batch product threshold, fixed-size alpha search, ambiguous-label e-average, p-value comparator, and repeated-split metrics. Overall experimental fidelity is **high**, with important caveats:

- the batch notebook uses $1/\log(1+p_f)^{1/4}$ while the paper displays $1/p_f^{1/4}$;
- the fixed-size notebook silently falls back to the last alpha when no candidate meets the size cap;
- formal proofs and alternative predictable-$\lambda_t$ martingales are not code artifacts;
- external data preparation is manual/notebook-based, dependencies are unpinned, and there are no tests or single-command runner;
- pretrained checkpoints and saved plots are supplied, but this analysis did not rerun large training or the 100/200-repeat experiments.

Methodologically, e-values guarantee validity, not informativeness: batch martingales can shrink and produce large or trivial sets; the data-dependent result is post-hoc expectation control rather than per-instance conditional coverage; and the ambiguous-label e-method is empirically less efficient than its p-based comparator in the reported experiment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
