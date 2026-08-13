---
layout: default
permalink: /paper-atlas/signaling-data-markets-free-samples-7ee8ac2b/
title: "Signaling_Data_Markets_Free_Samples"
nav: false
description: "设想一个买家想估计未知参数 \\theta，市场上有 K 个数据卖家。每个卖家的数据都以 \\theta 为均值，但噪声方差可能是较小的 \\sigmaL^2 或较大的 \\sigmaH^2；方差越小，数据质量越高。卖家知道自己的质量和单位样本成本，买家事前却不知道。 免费试用似乎能解决信息不对称：卖家先给几个样本，买家观察其样本方差，再决定向谁购买。但卖家未必愿意这样做。好质量一旦被识别，买家只需购买更少样本就能达到同样精度；"
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
    <h1>Signaling_Data_Markets_Free_Samples</h1>
    <p>Signaling in Data Markets via Free Samples</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.16919" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Signaling_Data_Markets_Free_Samples">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用免费样本在数据市场中传递质量信号

### 这篇论文解决什么问题？

设想一个买家想估计未知参数 $\theta$，市场上有 $K$ 个数据卖家。每个卖家的数据都以 $\theta$ 为均值，但噪声方差可能是较小的 $\sigma_L^2$ 或较大的 $\sigma_H^2$；方差越小，数据质量越高。卖家知道自己的质量和单位样本成本，买家事前却不知道。

免费试用似乎能解决信息不对称：卖家先给几个样本，买家观察其样本方差，再决定向谁购买。但卖家未必愿意这样做。好质量一旦被识别，买家只需购买更少样本就能达到同样精度；坏质量一旦暴露，卖家又可能完全落选。论文研究的正是：**免费样本何时会在均衡中出现，竞争又会怎样改变披露激励？**

这是一篇算法博弈论与机制设计论文，不是生物信息学论文，也不是训练预测模型的方法。

### 与已有工作的区别

已有数据采购机制往往假设质量已知、可观察或可以由机制直接控制。Drakopoulos 和 Makhdoumi 在 *Management Science*（2023）也研究免费数据样本，但重点是买家拿到试用数据后“搭便车”的 hold-up 问题；本文则把免费样本看作改变买家质量信念的内生信号。一般的信息设计允许发送者选择抽象信号结构，而本文的卖家只能选择诚实提供多少个 i.i.d. 样本，因此需要把统计推断、采购拍卖与披露博弈合在一起分析。

### 两阶段机制

```text
卖家事前承诺免费样本数 m_i
            ↓
质量 σ_i² 与成本 c_i 实现
            ↓
提交免费样本 + 报告单位成本 c_i′
            ↓
买家由样本方差更新质量后验 π_i
            ↓
计算“后验方差 × 虚拟成本”评分
            ↓
只选择评分最小的一个卖家 i*
            ↓
购买 floor(σ̄_i*/sqrt(λψ(c_i*′))) 个样本
            ↓
Myerson 支付保证成本报告满足 BIC/IR
            ↓
反推卖家在免费样本阶段的最优响应与均衡
```

#### 1. 免费样本只用于判断质量

卖家选择 $m_i\in\{0,2,\ldots,M\}$；排除 1 是因为单个样本无法定义样本方差。免费样本不能进入最后的 $\theta$ 估计，只用于质量评估，这对应现实中的 evaluation-only 授权。买家由样本方差 $S_i^2$ 更新“高方差”的后验概率：

$$
\pi_H=\frac{1}{1+\frac{\mu}{1-\mu}\Lambda_m(S^2)},
$$

其中 $\Lambda_m$ 是样本方差在低方差与高方差模型下的似然比。随后计算后验平均方差

$$
\bar\sigma_i^2=pi_i(\sigma_L^2)\sigma_L^2+pi_i(\sigma_H^2)\sigma_H^2.
$$

样本方差不依赖未知均值，因此无需额外指定 $\theta$ 的先验。

#### 2. 把准确度和采购支出放入同一目标

买家的效用是“负的估计方差”减去总支付的 $\lambda$ 倍。若从多个卖家购买，最优估计权重与 $n_i/\bar\sigma_i^2$ 成正比。利用 Myerson 引理，可把满足贝叶斯激励相容的期望支付改写为采购量乘虚拟成本

$$
\psi(c)=c+\frac{F(c)}{f(c)}.
$$

这样，买家的连续松弛问题变成在估计方差与虚拟采购成本之间权衡。

#### 3. 最优连续解为什么只向一个卖家购买？

给定总虚拟支出，把全部采购量放在 $\bar\sigma_i^2\psi(c_i')$ 最小的卖家上，可以获得最高精度。因此获胜者与连续采购量为

$$
i^*\in\arg\min_i\bar\sigma_i^2\psi(c_i'),
\qquad
n^*=\frac{\bar\sigma_{i^*}}{\sqrt{\lambda\psi(c_{i^*}')}}.
$$

这不是“选成本最低者”：质量后验与虚拟成本共同决定结果。真实采购量取 $\lfloor n^*\rfloor$。向下取整仍保持采购量随报价单调不增，所以配合 Myerson 支付后，诚实报告成本仍是贝叶斯激励相容的；近似损失只来自整数化造成的方差增加。

### 两个看似相反、实则互补的均衡结果

#### 不披露均衡

定理 1 表明：对任意卖家数 $K$，都存在一组质量和先验参数，使所有卖家选择 $m_i=0$ 成为近似子博弈完美均衡。尤其当 $\sigma_H/\sigma_L$ 很大时，少量样本会强烈改变后验：好质量虽更容易被选中，却会因所需样本更少而降低销售量；坏质量则可能直接失去订单。因此“保持模糊”可能优于披露。

注意，这是一条**参数存在性**结论，不是说任何市场都不会出现免费试用。

#### 最大披露且唯一的均衡

定理 2 固定其他参数并增大 $K$。当卖家足够多时，所有人都提供最大允许样本数 $M$，并且在买家使用上述采购机制的条件下，这是唯一均衡。

证明的核心是竞争造成的不同衰减速度。提供 $M$ 个样本的竞争者有固定正概率获得特别好的“质量—成本”评分；若已有 $J$ 个竞争者最大披露，一个少披露者的获胜概率至多按 $(1-q)^J$ 指数下降。最大披露者仍有多项式量级的效用下界。卖家数足够大时，指数劣势压倒节省披露的任何好处，所以少披露不再是最优响应。

### 数值实验怎么看？

论文用 $N=100{,}000$ 次 Monte Carlo 抽样检查每个候选对称策略及其所有单边偏离，并要求候选收益比每种偏离高至少两个合并标准误。Figure 1 显示：

- $K$ 大或质量差距较小时，最大披露区域占主导；
- $K$ 小且质量差距大时，可出现零披露；
- 两者之间还存在中间披露和多重均衡；
- 灰格只是当前保守统计判据“未检测到”，不能解释为均衡不存在。

### 适用边界与复现性

模型依赖二元高斯方差、诚实且同分布的试用样本、免费样本不可用于最终估计、对称卖家以及规则且有界的成本密度。最大披露的唯一性还以买家采用论文 Proposition 1 的继续机制为条件。论文给出了完整理论推导、仿真参数和相图，但**未找到**官方代码、仿真脚本、补充材料或数据文件；因此理论可逐式核查，Figure 1 需要自行重写程序才能复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Signaling in Data Markets via Free Samples

### Paper summary

This theoretical paper asks when competing data sellers voluntarily provide free samples that let a buyer assess otherwise private data quality before procurement. It couples Bayesian quality inference with mechanism design: sellers commit to a trial size, the buyer updates a binary Gaussian-variance prior from each trial's sample variance, and an approximately optimal Bayesian incentive-compatible auction purchases data from a single seller chosen by posterior quality and virtual cost.

The main conclusion is deliberately non-monotone. Free trials are not automatically incentive compatible: for any number of sellers, parameter regimes exist in which everyone revealing zero samples is an equilibrium because favorable disclosure reduces the quantity purchased while unfavorable disclosure reduces the chance of winning. With fixed primitives and sufficiently many sellers, however, maximal disclosure becomes the unique equilibrium under the proposed procurement continuation mechanism, because a seller revealing fewer samples is increasingly likely to be screened out by a better-looking rival.

### Why prior approaches are insufficient

Prior data-acquisition mechanisms often assume that quality is known, observed, controlled, or separately tested. Work on free data samples such as Drakopoulos and Makhdoumi (*Management Science*, 2023) focuses on preventing buyer free-riding, whereas this paper studies free samples as endogenous signals that change posterior beliefs about quality. General information-design results allow abstract signal structures; here, sellers can control only how many honest i.i.d. samples to reveal. The paper therefore needs to solve the downstream procurement mechanism and upstream disclosure game together (`paper.md:59-89`).

### Method at a glance

After observing free-sample variance, the buyer calculates seller $i$'s posterior mean variance $\bar\sigma_i^2$ and Myerson virtual cost $\psi(c_i')=c_i'+F(c_i')/f(c_i')$. Proposition 1 chooses

$$
i^*\in\arg\min_i \bar\sigma_i^2\psi(c_i'),
\qquad
n^*=\frac{\bar\sigma_{i^*}}{\sqrt{\lambda\psi(c_{i^*}')}}.
$$

It buys $\lfloor n^*\rfloor$ samples from this one seller and uses a Myerson payment. The real-valued relaxation supplies the closed form; flooring retains monotonicity and BIC while causing a controlled loss. Equilibrium proofs then compare the polynomial utility available to sufficiently revealing sellers with the exponentially shrinking selection probability of a seller revealing fewer samples (`paper.md:220-353`, `598-807`).

### Evidence and results

- **Theorem 1:** for any $K$ and $\zeta>0$, suitable $(\sigma_L,\sigma_H,\mu)$ admit a $\zeta$-approximate subgame-perfect equilibrium with $m_i=0$ for all sellers (`paper.md:383-398`).
- **Theorem 2:** for fixed primitives and sufficiently large $K$, $m_i=M$ for all sellers is a $1/(\alpha-1)$-approximate subgame-perfect equilibrium and is unique when the buyer uses Proposition 1 (`paper.md:598-611`).
- **Simulation:** a $K\times(\sigma_H/\sigma_L)$ sweep with 100,000 Monte Carlo samples per candidate/deviation comparison shows maximal, zero, intermediate, and coexisting symmetric equilibria. At $K=10$, maximal disclosure is the only detected equilibrium across every tested quality ratio (`paper.md:810-831`; Figure 1).

### Limitations

The model assumes binary Gaussian variances, honest i.i.d. free trials, evaluation-only access, symmetric ex-ante sellers, and regular bounded cost distributions. The uniqueness result is conditional on the buyer's proposed continuation mechanism. Numerical evidence covers one parameter family and uses a conservative finite-simulation test; gray cells mean “not detected,” not “no equilibrium.” The paper itself identifies heterogeneous means, non-i.i.d. trials, and non-Gaussian observations as future work (`paper.md:834-843`).

### Reproducibility

**Rating: 2/5 (theory auditable, computation not packaged).** The arXiv HTML provides a complete 2026 v1 manuscript, detailed formulas and proofs, the simulation parameters, and one recoverable phase-diagram image. No official code repository, simulation script, supplementary archive, or data artifact was found in the arXiv metadata, HTML links, full paper text, or acquisition sidecars. The proofs can be followed from the paper, but Figure 1 requires an independent reimplementation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
