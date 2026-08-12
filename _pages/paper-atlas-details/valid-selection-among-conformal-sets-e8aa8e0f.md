---
layout: default
permalink: /paper-atlas/valid-selection-among-conformal-sets-e8aa8e0f/
title: "Valid_Selection_Among_Conformal_Sets"
nav: false
description: "假设我们针对同一个样本 X 有 K 个 conformal predictor。每个方法单独使用时，都能保证 直觉上，我们会想查看这 K 个预测集合，然后选最小的那个。但这样做把集合大小重新用于“模型选择”，被选中的集合不再是事先固定的方法，原有 coverage 通常会失效。"
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
      <span>Advances in Neural Information Processing Systems 38 (NeurIPS 2025) · 2025</span>
    </div>
    <h1>Valid_Selection_Among_Conformal_Sets</h1>
    <p>Valid Selection among Conformal Sets</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2506.20173" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Valid Selection among Conformal Sets：方法详解

### 这篇论文解决什么问题？

假设我们针对同一个样本 $X$ 有 $K$ 个 conformal predictor。每个方法单独使用时，都能保证

$$
\mathbb P\{Y\in C_i^\alpha(X)\}\geq 1-\alpha.
$$

直觉上，我们会想查看这 $K$ 个预测集合，然后选最小的那个。但这样做把集合大小重新用于“模型选择”，被选中的集合不再是事先固定的方法，原有 coverage 通常会失效。

论文关心的不是“在整个数据集上选平均最好的一个模型”，而是更细的 **pointwise selection**：对每一个 $X$，根据当前各个集合的大小，选择此时最合适的预测器，同时仍然控制误覆盖率。这是一篇统计机器学习与 conformal prediction 论文，不是生信论文。

### 核心想法：用稳定性限制选择偏差

把当前集合大小写成

$$
\xi=[\lambda(C_1^α(X)),\ldots,\lambda(C_K^α(X))].
$$

选择器 $\hat S(\xi,\varepsilon)$ 不直接、确定性地取最小值，而是输出一个受控的随机索引。若选择分布相对某个不依赖当前 $\xi$ 的参考分布变化有限，即满足 $(\eta,\tau)$-stability，那么

$$
\mathbb P\{Y\in C_{\hat S}^α(X)\}
\geq 1-\alpha e^\eta-\tau.
$$

因此，如果最终希望误覆盖率不超过 $\alpha$，可先把每个基础集合做得更保守，让其误覆盖率变为

$$
\alpha'=(\alpha-\tau)e^{-\eta}.
$$

$\eta$ 或 $\tau$ 越大，选择器越能偏向当前最小集合，但基础预测集合就必须越宽。论文给出的最坏情形和独立 coin-flip 例子说明，这个代价在无额外假设时确实可能不可避免。

### MinSE：在所有稳定选择分布里尽量选小集合

MinSE 先给一个在观察当前大小之前确定的 prior $b\in\Delta^{K-1}$，再求解

$$
\begin{aligned}
\min_{p,s}\quad &\sum_i p_i\lambda(C_i^α(X))\\
\text{s.t.}\quad
&p\in\Delta^{K-1},\quad s_i\geq0,\\
&p_i\leq e^\eta b_i+s_i,\\
&\sum_i s_i\leq\tau.
\end{aligned}
$$

最后按照最优概率 $p_i^\star$ 抽取一个预测集合。约束控制选择概率不能离 prior 太远，目标函数则把尽可能多的概率质量放在较小的集合上。

当 $\tau=0$ 时，算法非常直观：

```text
按集合大小从小到大排序
        |
        v
依次给小集合分配概率
        |
        v
每个集合最多获得 e^eta * b_i
        |
        v
总概率填满 1 后停止
```

官方补充代码的 `batch_setting/utils.py:5-31` 正是这个 capped-simplex 贪心解。MinSE 的最优性是“相对于给定稳定性类别”的：对任意 $(\eta,\tau)$-stable 选择器，存在一个与之对应的 prior，使 MinSE 的期望集合大小不更大；它不是说同一个固定 prior 能统一支配所有方法。

### AdaMinSE：自动分配 coverage correction

MinSE 需要手动选择 $\eta$ 和 $\tau$。AdaMinSE 同时优化选择概率、乘性稳定因子和松弛量：

$$
e^\eta\alpha'+\tau\leq\alpha.
$$

它直接输入基础误覆盖率 $\alpha'$ 和目标误覆盖率 $\alpha$，由线性规划决定如何在“更激进地选小集合”和“保留 coverage”之间分配预算。

实现时通常把 $r=e^\eta$ 当作 LP 变量。online solver 明确要求 $r\geq1$；batch solver 中这个变量仍叫 `eta`，但没有强制下界为 1，这是代码和论文的一个重要偏差。因此可以信任其核心实验逻辑，但不能把 batch LP 当作论文约束的完全逐字实现。

### 如何去掉随机选择？

若不希望每次随机抽一个模型，可以输出 1/2 weighted-vote set：

$$
C_{\mathrm{dr}}(X,\xi)=
\left\{y:\sum_i p_i(\xi)\mathbf1\{y\in C_i^α(X)\}\geq\frac12\right\}.
$$

这样消除了选择器自身的随机抽样，但误覆盖上界变为 $2(\alpha e^\eta+\tau)$。这里“derandomized”只表示不再抽选模型；基础 conformal predictor 本身若有随机性，最终集合仍可能是随机的。

### Online 版本：AdaCOMA

COMA 用过去的区间长度通过 Hedge/AdaHedge 形成权重 $w^{(t)}$，但在时刻 $t$ 还没看到当前集合大小，所以无法针对当前 $X_t$ 做局部选择。

AdaCOMA 的流程是：

```text
过去的区间损失 -> Hedge/AdaHedge -> 历史 prior w^(t)
                                         |
当前 K 个区间 -> 当前大小 xi_t ----------+
                                         v
                                  MinSE / AdaMinSE
                                         |
                        随机选一个，或输出 1/2 加权投票集合
```

这样既保留历史表现，也能对当前样本做 pointwise adaptation。需要注意，论文的 online 结论是长期平均的概率 coverage 结论，不是任意有限时刻、每条实现路径都保证固定 coverage。

### Recal：利用 split conformal 的 rank 结构减少保守性

一般稳定性 correction 在实际 split conformal 场景里可能过于保守。Recal 进一步利用 score rank 的交换性。

对校准样本 $i$，让选择器挑出模型 $\hat S(X_i,\varepsilon_i)$，再记录该模型对样本 $i$ 的分数排名：

$$
\hat R_i=R_{\hat S(X_i,\varepsilon_i),i}.
$$

这些“被选择后的 rank”被视为新的 meta-score，再取 conformal order statistic $\hat R_{(\tau_\alpha)}$。只要选择器在给定 $X$ 后与 calibration block 条件独立，就能直接得到目标 $1-\alpha$ coverage，不必再承受 $e^\eta$ 和 $\tau$ 的最坏情形膨胀。

关键是不能用同一 calibration block 既计算当前集合大小又做 rank calibration。论文因此再分出独立 auxiliary block：

1. auxiliary block 估计各模型的 proxy quantile 和 proxy set size；
2. 只基于这些 proxy size 做 MinSE/AdaMinSE 选择；
3. 在独立 calibration block 中计算被选模型的 effective rank；
4. 对 effective rank 再做 conformal calibration；
5. 测试时仍用 auxiliary proxy 做选择，并使用重新校准的 rank 生成区间。

Recal 的代价是分走部分校准数据，并依赖 proxy size 足够反映真实集合大小。补充代码默认每个辅助样本抽一次选择，与定理一致；可选的多次 resampling 是论文没有单独证明的工程扩展。

### 实验告诉我们什么？

Batch 实验覆盖 synthetic regression、Bike Sharing、Abalone 和 California Housing，目标 coverage 为 0.9。主要结论是：

- Recal 基本保持目标 coverage，并在主实验中得到最短或接近最短的区间；
- YK-Adjust 通常明显 overcoverage，同时区间很宽；
- MinSE/AdaMinSE 在不同模型具有局部互补优势时有效；
- 在 homogeneous 场景中，如果一个模型整体占优，原始稳定选择反而可能比基线更宽。

Online 实验中，ELEC 上 AdaCOMA 在相近误覆盖率下把平均长度从 COMA 的约 0.69 降到约 0.31–0.32；ARMA(1,1) 上只得到很小优势。50 个 ARMA seeds 中有 4 个因双方都出现数值不稳定而被排除。因此实验支持的是“当预测器优势随输入或时间变化时，pointwise stable selection 有价值”，而不是普遍缩短区间。

### 使用时最重要的边界

- 基础 conformal predictors 必须先有效；稳定选择不会修复无效的基础模型。
- marginally valid 的基础集合不会因为本方法自动获得 conditional coverage。
- MinSE 的效果依赖 prior 和预测器之间是否真正互补。
- Recal 需要交换性、独立辅助/校准划分和有信息量的 proxy size。
- 当前实验以回归为主，未覆盖分类、结构化输出或复杂集合几何。
- 官方补充代码不是公开 Git 仓库：依赖未固定版本、无测试套件、全部实验约需 200 CPU-hours。

一句话概括：**MinSE 用受稳定性约束的概率分布代替不安全的“直接取最小”，AdaMinSE/AdaCOMA 提高自适应性，而 Recal 在 split conformal 条件下利用 effective rank 把理论有效性与更好的实际区间效率结合起来。**

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Valid Selection among Conformal Sets

### Paper at a glance

- **Authors:** Mahmoud Hegazy, Liviu Aolaritei, Michael I. Jordan, Aymeric Dieuleveut
- **Venue:** *Advances in Neural Information Processing Systems 38 (NeurIPS 2025)*, Main Conference Track
- **Canonical preprint:** arXiv:2506.20173v1, 25 June 2025
- **DOI:** `10.48550/arXiv.2506.20173`
- **Domain/type:** statistical machine learning method; conformal prediction and post-selection inference. This is not a bioinformatics paper.

### Problem and contribution

Each of several conformal predictors can have valid marginal coverage on its own, yet selecting the smallest prediction set after seeing all current set sizes can destroy that guarantee. Existing approaches often choose one predictor by average calibration-set size or use additional splitting/inflation; they do not directly provide valid, input-dependent selection of whichever predictor is most attractive for the current $X$.

The paper frames selection as an algorithmic-stability problem. If the selected index's distribution cannot move too far from an input-independent reference distribution, then individual conformal validity transfers to the selected set after a quantified coverage correction. Its central algorithm, **MinSE** (Minimum Stable Expectation), chooses a probability distribution over predictors that minimizes expected selected-set size subject to stability constraints. **AdaMinSE** jointly allocates the post-selection error budget between multiplicative stability and additive slack. The paper further gives a $1/2$ weighted-vote derandomization, a conditional-coverage inheritance result, an online extension, and **AdaCOMA**, which uses historical COMA weights as the prior but adapts selection to current interval sizes.

For split conformal prediction, the generic stability bound can be conservative. The paper's most practically effective variant, **Recal**, uses a separate auxiliary split to build selection proxies and then treats the chosen model's calibration-score rank as a meta-score. A conformal order statistic of these effective ranks restores finite-sample post-selection coverage without the worst-case stability inflation, provided selection is independent of the calibration block.

### Core guarantee

For an $(\eta,\tau)$-stable selector applied to base sets with miscoverage $\alpha$, the selected set satisfies

$$
\mathbb P\{Y\in C_{\hat S}^\alpha(X)\}\geq 1-\alpha e^\eta-\tau.
$$

Thus base sets constructed at miscoverage $(\alpha-\tau)e^{-\eta}$ achieve target post-selection miscoverage $\alpha$. This correction is sometimes conservative but can be tight in worst-case and independent-oracle examples.

### Evaluation

Batch experiments use one synthetic regression setting plus Bike Sharing, Abalone, and California Housing. They compare MinSE, AdaMinSE, Recal, ModSel, YK-Adjust, and the uncorrected YK-Base diagnostic at target coverage 0.9. The main and appendix figures show:

- Recal stays near target coverage and is shortest or near-shortest in the reported main synthetic and real-data comparisons.
- YK-Adjust commonly overcovers and produces much longer intervals.
- MinSE/AdaMinSE benefit when predictors have complementary local strengths, but can be inefficient in homogeneous settings where one predictor is globally best.

The online study uses ten switching forecasters built from six Adaptive Conformal Inference configurations on ELEC and synthetic ARMA(1,1). At similar miscoverage on ELEC, AdaCOMA reduces average length from about 0.69 for COMA to 0.31–0.32. On ARMA(1,1), the difference is small (roughly 4.23–4.31 versus 4.40). Four numerically unstable ARMA runs out of 50 were excluded for both methods, an important experimental boundary.

### Reproducibility and limitations

The official NeurIPS supplemental ZIP contains batch and online experiment code, one online dataset, tuned hyperparameters, and plotting utilities; no public GitHub repository was identified. All Python files compile, but dependencies are unpinned, there are no automated tests or frozen full result bundles, and the appendix reports approximately 200 CPU-hours for all experiments. The code-paper match is **medium**: core algorithms and experiments are present, while the batch AdaMinSE solver uses a stability multiplier variable without enforcing the paper's explicit $e^\eta\geq1$ parameterization, and optional multiple-resampling in Recal extends beyond the theorem's one-draw construction.

The guarantees assume valid base predictors and do not manufacture conditional coverage from marginally valid sets. Recal relies on exchangeability, a separate auxiliary/calibration split, and informative proxy sizes. The empirical evidence is regression-focused and intentionally creates heterogeneous predictor strengths, so it does not establish universal interval-size improvement.

### Bottom line

The paper's main conceptual step is to replace unsafe “choose the smallest” with a constrained distribution over choices whose stability directly controls post-selection error. MinSE supplies the general distribution-free mechanism; AdaMinSE and AdaCOMA make it adaptive; derandomization replaces a sampled predictor with a vote at a factor-two coverage cost; and effective-rank Recal exploits split-conformal structure to recover much better practical efficiency.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
