---
layout: default
permalink: /paper-atlas/scalable-utility-aware-multiclass-calibration-03be5860/
title: "Scalable_Utility_Aware_Multiclass_Calibration"
nav: false
description: "多分类模型通常输出一个类别概率向量，但“校准得好不好”并没有脱离应用场景的唯一答案。医生可能更在意漏诊某种疾病的代价，推荐系统可能更在意真实类别的排序位置，另一个用户则可能只关心 top-1 或 top-K 是否正确。传统的 top-class calibration 和 class-wise calibration 先把多分类问题二值化，再用固定分箱估计误差；结果会明显受箱数和边界影响。"
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
      <span>Proceedings of the Twenty-Ninth International Conference on Artificial Intelligence and Statistics (AISTATS) · 2026</span>
    </div>
    <h1>Scalable_Utility_Aware_Multiclass_Calibration</h1>
    <p>Scalable Utility-Aware Multiclass Calibration</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2510.25458" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Scalable Utility-Aware Multiclass Calibration：方法详解

### 这篇论文解决什么问题

多分类模型通常输出一个类别概率向量，但“校准得好不好”并没有脱离应用场景的唯一答案。医生可能更在意漏诊某种疾病的代价，推荐系统可能更在意真实类别的排序位置，另一个用户则可能只关心 top-1 或 top-$K$ 是否正确。传统的 top-class calibration 和 class-wise calibration 先把多分类问题二值化，再用固定分箱估计误差；结果会明显受箱数和边界影响。直接估计完整的 Mean Calibration Error 又需要恢复高维条件期望，在无额外假设时不可一致估计，并且样本复杂度会随类别数迅速恶化。

本文提出 **utility calibration（效用校准）**：先明确下游用户真正获得什么效用，再检查模型预测的期望效用是否与最终实现的效用一致。它是通用机器学习/不确定性量化方法，不是生物信息学专用方法。

### 核心定义

设分类器输出 $f(X)\in\Delta^{C-1}$，真实标签是 one-hot 向量 $Y$。效用函数

$$
u:\Delta^{C-1}\times\mathcal Y\to[-1,1]
$$

描述用户基于预测 $f(X)$ 采取行动后，在真实结果 $Y$ 出现时得到的收益或损失。把每个可能类别的效用组成向量

$$
\vec u(X)=\big(u(f(X),e_1),\ldots,u(f(X),e_C)\big),
$$

则模型给出的“预测期望效用”为

$$
v_u(X)=\langle f(X),\vec u(X)\rangle. \tag{3.1}
$$

真实效用是 $u(f(X),Y)$。本文不是只比较二者的全局平均，因为不同区域的正负误差可能相互抵消；而是在 $v_u(X)$ 的所有区间上寻找最严重的偏差：

$$
\mathrm{UC}(f,u)=
\sup_{I\in\mathbb I[-1,1]}
\left|
\mathbb E[(u(f(X),Y)-v_u(X))\mathbf1\{v_u(X)\in I\}]
\right|. \tag{3.2}
$$

直观地说：把预测效用落在某个区间的样本挑出来，比较“用户以为会得到的效用”和“实际得到的效用”；在所有区间中取最坏者。由于乘上了区间发生概率，它衡量的是带总体影响权重的偏差，而不是只看极小群体中的条件误差。

### 为什么它可扩展

对每个样本计算

$$
s_i=v_u(X_i),\qquad r_i=u(f(X_i),Y_i)-s_i.
$$

然后按 $s_i$ 排序。排序后，任意效用区间都对应连续的一段样本，因此问题变成：寻找残差序列中绝对和最大的连续子数组。

```text
概率向量、标签、效用函数
          ↓
计算预测效用 s_i 与残差 r_i
          ↓
按 s_i 排序
          ↓
正残差和负残差各做一次 Kadane 扫描
          ↓
最大绝对连续区间和 / n
          ↓
UC 估计值 + 最坏区间端点
```

排序的复杂度是 $O(n\log n)$，扫描是 $O(n)$；加上预测器和效用函数求值，总复杂度为 $O(n\log n+nT_{eval})$。对一个固定效用，估计误差为 $\widetilde O(n^{-1/2})$，隐藏常数不显式依赖类别数 $C$。官方实现 `utility_cal/helper.py:54-129` 直接使用排序和正、负两次 Kadane 扫描。

### 如何统一并扩展已有校准指标

本文通过不同效用定义得到一组统一接口：

| 效用类 | 含义 | 与已有指标的关系 |
|---|---|---|
| $\mathcal U_{\mathrm{TCE}}$ | top-1 预测是否正确 | 得到不依赖固定分箱的 top-class 最坏区间误差 |
| $\mathcal U_{\mathrm{CWE}}$ | 每个类别分别作为效用 | 同时找最坏类别和最坏概率区间 |
| $\mathcal U_{\mathrm{lin}}$ | 类别收益向量 $a$ | 支持任意类别成本/收益组合 |
| $\mathcal U_{\mathrm{rank}}$ | 真实类别所在名次的价值 | 面向排序任务或推荐任务 |
| $\mathcal U_{\mathrm{topK}}$ | 真实类别是否进入 top-$K$ | 统一评估所有 $K$ 的可靠性 |
| $\mathcal U_{\mathrm{dec},K}$ | 预测下最优行动的负损失 | 面向具有多个行动的决策问题 |
| DCG / 语义相似度 | 折扣排名收益或类别嵌入相似度 | 体现更具体的下游价值 |

top-class 和 class-wise 版本不是把旧的分箱数值原样重命名，而是把它们重新解释为效用校准，并在所有区间上取最大偏差。这样避免了分箱边界的任意性，也得到阈值决策的可解释保证。

### 单个效用、效用类与计算困难

对效用类 $\mathcal U$，形式上的目标是

$$
\mathrm{UC}(f,\mathcal U)=\sup_{u\in\mathcal U}\mathrm{UC}(f,u). \tag{3.5}
$$

论文区分两个概念：

- **主动可测（proactive measurability）**：算法能否高效找到接近最坏的效用？
- **交互可测（interactive measurability）**：用户给出任意具体效用后，我们能否准确估计它，并保证这种准确性对整个类同时成立？

有限的 class-wise/top-$K$ 类可以枚举，所以能主动审计。线性、排序等无限效用类的最坏效用搜索可能是非凸甚至计算困难，但交互估计仍然可以有多项式样本复杂度。论文证明线性和排序效用类的交互样本复杂度为 $\widetilde O(C)$。这一区分非常重要：方法承诺的是“用户拿来一个效用，我能可靠评估”，不虚构“所有丰富效用类的全局最坏情况都能快速求出”。

### 用 eCDF 评估丰富效用类

当求全局最坏效用不可行时，从代表用户群体的分布 $\mathcal D_{\mathcal U}$ 中抽取 $M$ 个效用，分别估计 UC，然后画经验累积分布：

$$
\widehat F_{E,M,n}(e)=\frac1M\sum_{m=1}^M
\mathbf1\{\widehat{\mathrm{UC}}(f,u_m;S)\leq e\}.
$$

曲线越靠左，说明更多被抽样效用具有较小误差；曲线尾部能展示少数难满足用户。它比一个平均分更丰富，但结论只针对选定的效用分布，并不是全效用空间的最坏情况证明。Figure 1 使用 1,500 个线性和排序效用，显示同一校准算法在不同效用族上的排名会变化。

### 可选的 post-hoc patching

UC 的最坏区间也给出了修正方向。算法每轮：

1. 找到当前最坏的效用和效用区间；
2. 只对落在该区间的预测沿效用向量更新；
3. 把更新后的向量投影回概率单纯形；
4. 重复到最大违反不超过 $\varepsilon$。

在能精确得到误差的理想条件下，使用 $\eta_t=\mathrm{err}_t/C$，每轮都会降低 Brier score，并在 $O(C/\varepsilon^2)$ 轮内终止。代码还加入 Armijo line search、动态步长、子采样以及多种效用的联合审计。这些是经验实现细节，不能和理想 oracle 定理完全等同。

### 实验结论

实验覆盖 CIFAR-10/100、ImageNet-1K 和 Yahoo Answers，使用 RepVGG、ResNet、ViT 等模型，并与 temperature scaling、vector scaling、Dirichlet calibration、isotonic regression 比较。14 个本地图像面板均已视觉核验。

最重要的结果不是“patching 在所有指标上获胜”，而是不存在统一赢家。以 ViT/ImageNet-1K 为例，patching 的 binned TCE 和组合效用误差最好，Dirichlet 的 Brier score 最好，isotonic regression 的 binned CWE 最好。eCDF 进一步显示：某些方法在线性效用上更好，却在排序效用上更差；部分传统后处理甚至会让某一效用族整体右移。

### 代码与复现边界

官方代码仓库由 AISTATS 2026 OpenReview camera-ready 页面给出，本地保存 commit `2f8d3f95665999ff40caa1571afceaf06e73d84a`。核心 UC 估计、各类效用、eCDF 和 patching 都能找到直接实现证据。但仓库没有论文使用的 logits/labels、绘图脚本和锁定依赖；`utility_cal/aligned_synthetic_exp.py:59` 还有未闭合字符串导致全仓 `compileall` 失败；论文附录写每轮采样 264 个效用，当前代码默认值则是 256。因此可理解和复用核心算法，但仅凭该快照不能精确复现全部表图。

### 使用时最需要注意的三点

1. **先定义正确的效用。** UC 很精确，但如果效用类没有代表真实用户，它只会精确回答错误问题。
2. **eCDF 不是 worst-case certificate。** 它描述被抽样用户的误差分布，不能替代全局最坏效用搜索。
3. **稀有但高风险事件要显式编码。** UC 的区间误差带发生概率权重，不能自动保证极小群体获得足够重视。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Scalable Utility-Aware Multiclass Calibration

### Problem

Multiclass classifiers can support users with very different costs, rewards, and ranking preferences. Full mean calibration error is generally unestimable without assumptions and suffers exponential dependence on the number of classes; common top-class or class-wise proxies collapse the task to binary events and depend strongly on bin choices. Variational calibration metrics avoid fixed bins but can be expensive in high dimension. The paper therefore asks for a calibration assessment that is scalable, binning free, and tied to what a downstream user values.

### Main idea

For a bounded utility $u(f(X),Y)$, the model predicts the expected utility

$$
v_u(X)=\langle f(X),\vec u(X)\rangle.
$$

Utility calibration measures the largest probability-weighted bias between realized and predicted utility over every interval of $v_u$:

$$
\mathrm{UC}(f,u)=\sup_I\left|
\mathbb E[(u(f(X),Y)-v_u(X))\mathbf1\{v_u(X)\in I\}]
\right|.
$$

On a sample, sorting examples by $v_u$ turns each interval into a contiguous block; two Kadane scans find the largest positive or negative residual sum. The resulting estimator costs $O(n\log n+nT_{eval})$ and has $\widetilde O(n^{-1/2})$ error for a fixed utility, with no explicit dimension factor beyond evaluating the predictor and utility.

### Unification and extension

Specific utility choices recover binning-free analogues of top-class and class-wise calibration by taking the worst interval (and worst class). Other choices directly encode linear payoff vectors, rank or top-$K$ value, multi-action decision losses, discounted cumulative gain, semantic similarity, or custom gain matrices. For a class $\mathcal U$, $\mathrm{UC}(f,\mathcal U)=\sup_{u\in\mathcal U}\mathrm{UC}(f,u)$ is the formal worst-case target.

The paper distinguishes **proactive measurability**—efficiently finding a near-worst utility—from **interactive measurability**—uniformly estimating any utility supplied by a user. Rich infinite classes may make the first computationally hard while retaining polynomial sample complexity for the second. Linear and rank utilities are shown to be interactively measurable with $\widetilde O(C)$ sample complexity. When worst-case optimization is impractical, the proposed evaluation samples plausible utilities and plots the eCDF of their errors, making typical behavior and tails visible without pretending to certify the global supremum.

### Post-hoc patching

Utility calibration is a weighted-calibration objective, so its worst interval supplies a correction direction. The optional algorithm repeatedly finds the most violated utility/interval, updates only affected predictions along the utility vector, and projects them back to the simplex. With oracle errors and step $\eta_t=\mathrm{err}_t/C$, Brier score decreases and the method reaches error $\varepsilon$ in $O(C/\varepsilon^2)$ iterations. The public implementation uses JAX, masked updates, simplex projection, subsampling, and Armijo/dynamic step selection.

### Evaluation

Experiments cover CIFAR-10/100, ImageNet-1K, and Yahoo Answers with RepVGG, ResNet, and ViT outputs. Baselines include temperature scaling, vector scaling, Dirichlet calibration, and isotonic regression. Across all 14 inspected image panels and Tables 1–8, method rankings change with dataset and utility family. On the headline ViT/ImageNet-1K experiment, patching has the lowest binned TCE and combined utility error, while Dirichlet has the best Brier score and isotonic regression the best binned CWE. Sampled-utility eCDFs reveal concentration and heavy-tail differences that these scalar summaries obscure; some conventional post-hoc methods even worsen particular utility families.

### Reproducibility assessment

**3/5 — method implementation available, full experiment reproduction incomplete.** OpenReview identifies the official repository `mahegz/Scalable-Calibration`; the stored snapshot is commit `2f8d3f95665999ff40caa1571afceaf06e73d84a`. Direct source inspection finds faithful implementations of the interval estimator, utility families, eCDF computation, and patching loop. The repository README documents commands, but the exact logits/labels, plotting scripts, and a pinned environment are absent. Repository-wide `compileall` also fails on an unterminated string in the auxiliary `aligned_synthetic_exp.py:59`, and the current code defaults to 256 sampled utilities where Appendix C.1 states 264. Core method code is usable; exact tables and figures are **Not found** as reproducible from the snapshot alone.

### Scope and limitations

Utility calibration is only as relevant as the supplied utility or sampling distribution. Sampled eCDFs summarize that distribution rather than proving global worst-case calibration; rare but important cases may require explicit weighting; and interactive measurability does not remove computational hardness of searching expressive utility classes. The paper's central contribution is therefore a rigorous, scalable interface between calibration assessment and downstream value—not a single universal replacement score that ranks every classifier for every user.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
