---
layout: default
permalink: /paper-atlas/many-needles-in-a-haystack-01932766/
title: "Many_needles_in_a_haystack"
nav: false
wide: true
description: "在 CRISPR 或单细胞扰动筛选中，候选基因可能有上万甚至更多，但实验预算只能覆盖其中很小一部分。目标不是找到唯一的全局最优基因，而是在有限轮次内尽可能多地找出表型超过阈值的“命中”（hit），并覆盖可能来自不同通路的多个高响应区域。随机采样会把预算花在低价值区域；只按预测均值挑选的 Bayesian optimization 方法又容易反复利用一个主峰，漏掉其他生物学机制。"
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
      <span>Perturbation Resources</span>
      <span>arXiv · 2026</span>
    </div>
    <h1>Many_needles_in_a_haystack</h1>
    <p>Many Needles in a Haystack: Active Hit Discovery for Perturbation Experiments</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Probability-of-Hit 方法解读

### 这篇论文解决什么问题？

在 CRISPR 或单细胞扰动筛选中，候选基因可能有上万甚至更多，但实验预算只能覆盖其中很小一部分。目标不是找到唯一的全局最优基因，而是在有限轮次内尽可能多地找出表型超过阈值的“命中”（hit），并覆盖可能来自不同通路的多个高响应区域。随机采样会把预算花在低价值区域；只按预测均值挑选的 Bayesian optimization 方法又容易反复利用一个主峰，漏掉其他生物学机制（论文第 1-2 节，`paper.md` 第 17-81 行）。

论文讨论的相关路线包括 UCB、Expected Improvement、Probability of Improvement、Thompson Sampling、纯探索，以及 *DiscoBAX*（ICML 2023）。这些方法主要面向单个最优点、信息增益或边界估计，而不是“在批量实验中恢复尽可能多的阈值命中”。

### 核心想法：Probability-of-Hit

令候选扰动集合为 \(\mathcal{G}\)，未知表型函数为 \(f(g)\)，用户给定阈值 \(\tau\)。真实命中集合是

$$\mathcal{G}^{\star}=\{g\in\mathcal{G}\mid f(g)>\tau\}.$$

第 \(t\) 轮选择大小为 \(b\) 的批次 \(B_t\)，实验返回带噪观测

$$y_g=f(g)+\varepsilon_g,$$

并用此前批次形成的数据集

$$\mathcal{D}_t=\{(g,y_g):g\in B_s,\ s<t\}$$

更新概率模型。模型为每个尚未测试的基因给出后验均值 \(\mu_t(g)\) 和不确定度 \(\sigma_t(g)\)。PoH 不直接最大化 \(\mu_t(g)\)，而是计算超过阈值的后验概率：

$$p_t(g)=\Pr(f(g)>\tau\mid\mathcal{D}_t).$$

如果后验近似为高斯分布，则

$$p_t(g)=1-\Phi\!\left(\frac{\tau-\mu_t(g)}{\sigma_t(g)}\right),$$

其中 \(\Phi\) 是标准正态分布 CDF。每轮按 \(p_t(g)\) 排序，从未采样候选中取前 \(b\) 个；批次内不能使用同批次其他基因尚未返回的结果。实验结束后把真实标签加入训练集，循环直到 \(T\) 轮。输出是已发现的命中集合 \(\mathcal{G}_T\) 及其数量/命中率。

```text
候选基因 G、阈值 tau、初始标注集 D_1
          |
          v
在 D_t 上训练或更新概率预测模型
          |
          v
对每个未测试 g 计算 mu_t(g)、sigma_t(g)、p_t(g)
          |
          v
按 p_t(g) 选 top-b，组成 B_t（不重复）
          |
          v
并行做生物实验，获得 y_g=f(g)+噪声
          |
          v
将新样本并入 D_{t+1}，进入下一轮
          |
          v
返回命中集合 G_T、HitRatio_T
```

因此，预测均值高的基因会得到高分；均值接近阈值且不确定度大的基因也可能得到高分。这使算法能够在利用已知高响应区域的同时，探索潜在的其他命中簇。图 1 的左侧展示多模态命中区域，右侧展示“选候选—做实验—更新模型”的闭环；图 2 的三幅快照展示随着轮次增加后验均值靠近真实曲线、不确定带收缩。

### 理论保证（如何理解）

理论需要两个条件。第一，后验集中：存在随时间增长的置信系数 \(\beta_t\)，使得以高概率

$$|f(g)-\mu_t(g)|\leq\beta_t\sigma_t(g)\quad(\forall g,t).$$

第二，存在一个距离阈值至少为 \(\varepsilon\) 的强命中，即 \(f(g)\geq\tau+\varepsilon\)。这排除了所有候选都贴着阈值的退化情况。令 \(\lambda\) 为观测噪声方差、\(K_A\) 为核矩阵，最大信息增益为

$$\gamma_n=\max_{|A|=n}\tfrac12\log\det(I+\lambda^{-1}K_A).$$

定理 4.3 给出高概率下的命中数下界：主项约为 \(Tb/2\)，减去一个 \(\sqrt{Tb\log(1/\delta)}\) 的随机波动项，以及由 \(\beta_{Tb}^3/\varepsilon^2\)、\(\gamma_{Tb}\)、\(\gamma_T\)、批大小和噪声共同决定的不确定度代价。若所用核满足 \(\gamma_n=o(n)\)，则渐近得到 \(Tb/2-o(Tb)\) 的命中数。证明先用鞅集中把真实命中数与 \(\sum p_t(g)\) 联系起来，再证明：当仍有强命中未被测试却选到了非命中时，该非命中的后验不确定度必须足够大，最后用批量信息增益控制所有轮次的不确定度总和（附录 B，`paper.md` 第 538-693 行）。

这是依赖校准和间隔条件的渐近/高概率结论，不是对任意有限数据都保证精确恢复全部命中的定理。

### 实验如何进行？

- **合成数据：** Sine (1D)、Sine-2D、Branin-Hoo (2D)、Perturbation-Pathways (4D) 和 Perturbation-SEM (6D)。后两者分别模拟通路簇、基因-细胞状态-环境的交互与因果结构。
- **真实数据：** GeneDisco 的 Schmidt IFN-\(\gamma\)、Schmidt IL-2、Sanchez Tau、Zhu SARS-CoV-2、Zhuang NK 五个 CRISPR 筛选，每个约 1.7-1.8 万基因，使用 808 维 Achilles 特征。
- **预测模型：** 合成数据使用 RBF-GP；真实数据使用两层（128、64）ReLU MLP + dropout \(p=0.2\)，50 次 Monte Carlo dropout 采样，最多训练 100 epochs、early stopping patience=10。
- **协议与指标：** 合成批大小为 2/5/10，真实批大小为 200；阈值为 top 5%、10%、20%，每次 10 轮。CHR@\(\tau\) 衡量真实命中恢复，SMAPE 衡量未见样本上的预测误差。
- **对比方法：** Random、Top-K Greedy、Thompson Sampling、Thompson-Hit、DiscoBAX。

Table 2 显示在合成任务上 PoH 的 CHR@10 通常最高或并列最高。Table 3 中，PoH 在 Schmidt IFN-\(\gamma\)、Schmidt IL-2、Sanchez Tau 的平均 CHR@10 分别为 337.2、575.4、389.4；Zhu SARS-CoV-2 和 Zhuang NK 则由 Thompson-Hit 取得最高值。附录图像显示 PoH 的命中率优势、DiscoBAX 的运行时间代价，以及批大小增大通常比阈值微调带来更明显的 CHR 提升。论文摘要的“最高 6.4% 提升”与不同表格比较得到的相对差值口径不完全一致，本地分析保留原文数字而不自行统一分母。

### 复现边界与局限

论文未完整给出初始采样、预处理、优化器、Thompson-Hit 实现和逐种子原始结果；Figures 3、4、7、9-11 只有图注而无本地图片。因此可以复述数学定义、算法流程、数据集和主要超参数，但不能声称已经验证具体实现。论文还指出 PoH 依赖不确定度校准、没有显式的批内多样性约束，且主要评估单扰动；组合扰动、条件上下文和多目标读出留待后续工作。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

High-throughput perturbation screens have tens of thousands of candidate genes but can assay only a small budget. The target is therefore to recover many perturbations whose response exceeds a threshold, including hits in disconnected biological pathways, rather than to optimize a single global maximum. Random/pure-exploration policies spend budget in low-value regions, while UCB/EI/Top-K-style Bayesian optimization can over-focus on one dominant mode (paper Sections 1-2, lines 17-81).

### Proposed Method

The paper introduces **Probability-of-Hit (PoH)**, a model-agnostic acquisition rule. Given a probabilistic surrogate with posterior mean \(\mu_t(g)\) and standard deviation \(\sigma_t(g)\), it computes

$$p_t(g)=\Pr[f(g)>\tau\mid\mathcal{D}_t]=1-\Phi((\tau-\mu_t(g))/\sigma_t(g))$$

under a Gaussian posterior, and selects the top \(b\) unsampled candidates each round. Labels from the parallel experiments update the surrogate for the next cycle. The method directly optimizes expected threshold exceedance and naturally balances predicted response with uncertainty (lines 173-200; Figure 1).

### Theory

Under a uniform posterior-concentration assumption, an \(\varepsilon\)-margin hit, and a kernel information-gain bound, Theorem 4.3 gives a high-probability lower bound on the number of recovered hits. Its leading term is \(Tb/2\), minus a martingale term and a batched uncertainty cost involving \(\beta_{Tb}^3/\varepsilon^2\), \(\gamma_{Tb}\), \(\gamma_T\), and noise variance \(\lambda\). For kernels with sublinear information gain, the paper derives \(Tb/2-o(Tb)\) asymptotically. The proof uses hit-count concentration, a one-sided normal-CDF bound, the fact that a PoH mistake implies large posterior uncertainty, and a batched information-gain inequality (lines 208-312 and Appendix B, lines 538-693).

### Evaluation

Synthetic benchmarks are Sine (1D), Sine-2D, Branin-Hoo, Perturbation-Pathways (4D), and Perturbation-SEM (6D); real evaluation uses five GeneDisco CRISPR screens represented by 808-dimensional Achilles features: Schmidt IFN-\(\gamma\), Schmidt IL-2, Sanchez Tau, Zhu SARS-CoV-2, and Zhuang NK. Synthetic experiments use GP/RBF surrogates, batch sizes 2/5/10, and ten cycles; real experiments use a Bayesian MLP with two hidden layers (128 and 64), dropout \(p=0.2\), 50 Monte Carlo samples, 100 epochs with patience 10, batch size 200, and ten cycles (lines 332-411).

At \(b=5\), Table 2 reports PoH as best or tied-best CHR@10 across the synthetic tasks and cycles. In the real-data Table 3, PoH has the largest mean CHR@10 on Schmidt IFN-\(\gamma\) (337.2), Schmidt IL-2 (575.4), and Sanchez Tau (389.4), while Thompson-Hit is best on Zhu SARS-CoV-2 (261.2) and Zhuang NK (252.4). The paper reports significant aggregate gains over Random and paired tests/effect sizes (lines 418-453). Appendix Table 5 gives a 5-cycle Schmidt IL-2 PoH value of 336.6 versus 120.4 for Random; Appendix Table 6 shows that PoH is not the best SMAPE method on every dataset. The abstract advertises “up to 6.4% improvement,” whereas the tabulated CHR differences imply different relative comparisons; this analysis preserves both claims without resolving the denominator ambiguity.

### Reproducibility and Limitations

The local source is an arXiv HTML conversion with five raster figures and no supplementary Markdown or code repository (`github_links.json` reports no repository). The paper specifies the acquisition formula, assumptions, synthetic functions, model families, major hyperparameters, datasets, and metrics, but does not provide runnable scripts, exact initialization/preprocessing, optimizer details, complete Algorithm 1/Thompson-Hit pseudocode in the converted source, per-seed data, or several captioned figure images (Figures 3, 4, 7, 9-11). The method assumes calibrated uncertainty, does not explicitly enforce within-batch diversity, and is evaluated mainly on single perturbations; the paper lists combinatorial, contextual, and multi-objective extensions as future work (Section 7). Reproducibility is therefore **2/5 (paper specification with material implementation gaps)**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
