---
layout: default
permalink: /paper-atlas/towards-anytime-valid-statistical-watermarking-ddee85e3/
title: "Towards_Anytime_Valid_Statistical_Watermarking"
nav: false
wide: true
description: "这不是生物信息学论文，而是一篇结合统计推断、信息论与大语言模型安全的理论方法论文。它研究的是：服务商如何在生成文本时嵌入一个不改变原始 token 分布的统计水印，并让检测者可以边读边检验，一旦证据足够就立即停止，同时仍严格控制误报率。 传统水印检测通常预先固定文本长度，再计算一个 p-value。如果检测者每读几个 token 就看一次 p-value，并在第一次显著时停止，重复查看会放大误报概率。"
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
    <h1>Towards_Anytime_Valid_Statistical_Watermarking</h1>
    <p>Towards Anytime-Valid Statistical Watermarking</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.17608" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Towards_Anytime_Valid_Statistical_Watermarking">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Anchored E-Watermarking 方法详解

### 这篇论文解决什么问题？

这不是生物信息学论文，而是一篇结合统计推断、信息论与大语言模型安全的理论方法论文。它研究的是：服务商如何在生成文本时嵌入一个不改变原始 token 分布的统计水印，并让检测者可以边读边检验，一旦证据足够就立即停止，同时仍严格控制误报率。

传统水印检测通常预先固定文本长度，再计算一个 p-value。如果检测者每读几个 token 就看一次 p-value，并在第一次显著时停止，重复查看会放大误报概率。简单的 Bonferroni 修正虽然能恢复有效性，却会消耗更多 token。论文因此把检测量从 p-value 换成 **e-value / e-process**：只要累计证据在零假设下形成非负超鞅，Ville 不等式就保证任意停止时刻的 Type-I error 不超过 $\alpha$。

### 基本建模

设 token 取值空间为 $\mathcal V$，大小为 $n$。

- $q$：目标模型在当前时间步的真实 next-token 分布；生成器知道它。
- $p_0$：生成器和检测器都知道的 anchor 分布，例如一个较小的开源 LLM。
- $S\sim p_0$：由秘密密钥生成、检测端可重建的随机 seed。
- $V\sim q$：最终输出 token。
- $w(v,s)$：生成器设计的 $V$ 与 $S$ 的联合分布。
- $e(v,s)$：检测器看到 token-seed 对后计算的一步 e-value。

目标分布不要求等于 anchor，但必须落在其 $\ell_1$ 邻域：

$$
\mathcal Q(p_0,\delta)=\{q:\|q-p_0\|_1\leq\delta\}.
$$

$\delta$ 表示希望抵抗的模型失配程度。论文还假设 $\inf_v p_0(v)>\delta$，即 anchor 对所有 token 都给出足够的正概率。这个条件便于得到闭式最优解，但在大词表 LLM 中相当强；真实实验没有逐 token 验证它。

### 水印如何在不改变文本分布的情况下嵌入？

生成器不直接给某些 token 加概率，而是构造一个 coupling：

$$
\sum_s w(v,s)=q(v),\qquad \sum_v w(v,s)=p_0(s).
$$

第一个边缘约束保证输出 $V$ 仍严格服从目标分布 $q$，因此从 token 边缘分布看是 distortion-free；第二个边缘约束保证 seed 服从公开的 anchor 分布。水印信号只存在于 $V$ 与 $S$ 的相关性中：

- 无水印/人类文本：$V$ 与秘密 seed 独立；
- 有水印文本：$V,S$ 来自生成器设计的联合分布 $w$。

论文证明最优 $w^*$ 是一种 maximal coupling，与 SEAL 中通过 speculative decoding 使用的生成机制一致。因此它并不是简单提出另一种“偏置 logits”的经验技巧，而是给已有生成器一个鲁棒最优性解释。

### 为什么使用 e-value？

一步 e-value 必须对 anchor 邻域内所有可能的 $q$ 都满足

$$
\sup_{q\in\mathcal Q(p_0,\delta)}
\mathbb E_{V\sim q,S\sim p_0}[e(V,S)]\leq1. \tag{1}
$$

把每一步的 e-value 相乘：

$$
E_t=\prod_{i=1}^{t}e(V_i,S_i),
$$

在零假设下它是 test supermartingale。于是

$$
\Pr_{H_0}\left(\exists t:E_t\geq1/\alpha\right)\leq\alpha.
$$

“存在某个时间点越过阈值”的概率已经被整体控制，所以检测器可以一直看，也可以根据当前证据决定何时停止，不会因为 optional stopping 破坏误报保证。

### 最优 detector 怎样推导？

作者采用 Kelly 式的期望 log-growth 作为检验效率：在备择假设下，希望每个 token 带来的 $\log e$ 尽量大。由于检测器不知道真实 $q$，它要对邻域内最不利的 $q$ 也有效；生成器知道 $q$，可以选择最有利的 coupling。由此得到三层优化：

$$
\sup_{e\in\mathcal E}\inf_{q\in\mathcal Q(p_0,\delta)}
\sup_{w\in\mathcal P(p_0,q)}\mathbb E_w[\log e(V,S)]. \tag{2}
$$

论文给出闭式最优一步证据：

$$
e^*(v,s)=
\begin{cases}
\dfrac{1-\delta/2}{p_0(s)}, & v=s,\\[4pt]
\dfrac{\delta}{2(n-1)p_0(s)}, & v\neq s.
\end{cases} \tag{3}
$$

直观上：token 与 seed 相等时给较大的证据；不等时给较小但非零的证据；再除以 $p_0(s)$，避免 anchor 中常见 seed 被过度计分。它不是简单的 match count，而是对 anchor 概率作校准的似然式赌注。

最坏情况下的最优平均 log-growth 为

$$
J^*=H(p_0)-H(\nu_\delta),
$$

其中 $\nu_\delta=(1-\delta/2,\delta/[2(n-1)],\ldots)$。因此：

- anchor 熵 $H(p_0)$ 越高，可用随机性越多，证据增长越快；
- 容忍半径 $\delta$ 越大，鲁棒性要求越强，保证的增长率越低。

### 实际检测流程

```text
离线设定：p0、delta、alpha
          |
          +--> 用 Eq. (3) 构造 e*(v,s)

每个生成时间步 t：
目标模型给 q_t
    -> 用 maximal coupling w*_t(q_t,p0) 联合抽样 (V_t,S_t)
    -> 输出 V_t；由密钥保留/重建 S_t

每个检测时间步 t：
读取 V_t，重建 S_t
    -> 计算 log e*(V_t,S_t)
    -> W_t = W_(t-1) + log e*(V_t,S_t)
    -> 若 W_t >= log(1/alpha)，立即判定“有水印”并停止
    -> 否则继续读取下一个 token
```

停止时间为

$$
\tau_\alpha=\inf\{t:W_t\geq\log(1/\alpha)\}.
$$

Theorem 4.3 的关键结论是

$$
\mathbb E[\tau_\alpha]\sim\frac{\log(1/\alpha)}{J^*}.
$$

更强的是，对任何有效 e-value，都不可能在最坏情况下获得比 $1/J^*$ 更小的渐近常数；Eq. (3) 的 $e^*$ 恰好达到这个下界。该结论允许 adversary 根据历史改变每一步的 $q_t$，因此可覆盖自回归依赖，而不限于 i.i.d. token。

### 实验怎样验证？

#### 两个理论模拟

Figure 1 在二元 token 空间里，用 CLARABEL 求解 max-min 问题。三个 anchor 的数值目标都在约 5 次迭代后贴近理论 $J^*$，验证闭式增长率。

Figure 2 对每个 $\alpha$ 模拟 10,000 个停止时间。随着 $\alpha$ 从 $10^{-2}$ 下降到 $10^{-120}$，$\mathbb E[\tau_\alpha]/\log(1/\alpha)$ 逐步趋近红色虚线 $1/J^*$，验证渐近 sample-complexity 常数。

#### 真实 LLM 水印

- target：Llama2-7B-chat；anchor：Phi-3-mini-128k-instruct；
- benchmark：MARKMYWORDS；
- 300 个生成样本，覆盖书籍摘要、创意写作和新闻生成；
- 扰动包括字符、单词、同义词、释义与往返翻译；
- $\alpha=0.02$；baseline 使用 Bonferroni schedule 保持 anytime validity；
- quality 由 Llama-3 judge 计算；size 是跨攻击和密钥的中位检测 token 数。

温度 0.7 时，本方法 quality 为 0.919、size 为 72.0；SEAL 分别为 0.901 和 84.5。温度 0.3、0.7、1.0 下，本方法的 size 分别为 97.0、72.0、97.5，都是表中最小值，同时质量没有明显下降。

### 怎样正确理解贡献与边界？

论文最重要的贡献不是“又一个水印打分函数”，而是把三件事连成同一个可证明框架：

1. **生成无失真**：coupling 保持 $q$ 的 token 边缘分布；
2. **检测可随时停止**：e-process 保证 optional-stopping-safe Type-I error；
3. **效率达到极限**：同一个 $e^*$ 同时实现最优一步 log-growth 和最优渐近停止时间。

但当前证据也有明确限制：

- 未找到官方代码或独立补充材料，不能核验真实实现是否完全等于数学描述；
- 论文没有给出大词表 maximal coupling、密钥到 seed、数值截断等完整工程细节；
- 真实实验只有一个 target/anchor 模型组合和 300 个输出；
- 邻域假设和最小 anchor 概率条件没有在真实 logits 上系统验证；
- baseline 的 anytime 化采用特定 Bonferroni 修正，其他更强的序贯化方式可能改变差距。

因此，这篇工作最可靠的结论是：在论文定义的 anchor-neighborhood 模型下，Anchored E-Watermarking 给出了闭式、任意时刻有效且渐近样本最优的检测器；真实 LLM 实验提供了有希望的支持，但还不是跨模型、跨实现的充分工程验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Towards Anytime-Valid Statistical Watermarking

### Bottom line

This 2026 arXiv preprint introduces **Anchored E-Watermarking**, a statistical watermark for autoregressive generators whose detector may continuously monitor text and stop early without losing Type-I error control. It jointly derives a distortion-free generator coupling and a robustly log-optimal e-value detector, then proves that the detector attains the best possible asymptotic expected stopping-time constant even when the target distribution changes adaptively over time.

### Problem

Modern generative watermarks create dependence between output tokens and secret pseudorandom seeds, then test for that dependence. Existing designs face two gaps highlighted by the paper:

1. seed/sampling distributions and detection scores are often selected heuristically rather than from one optimality principle;
2. fixed-horizon p-value tests do not permit unrestricted repeated inspection and data-dependent early stopping without correction.

The second issue is especially awkward for variable-length autoregressive text: a detector should be able to stop when the evidence is convincing instead of choosing a token budget in advance.

### Method

Both generator and detector share an anchor distribution $p_0$, such as a smaller open-source language model. The unknown target next-token distribution $q$ is assumed to lie in an $\ell_1$ neighborhood of $p_0$. The generator couples $q$ with an anchor-distributed seed while preserving both marginals, so the token distribution is unchanged. The detector uses a nonnegative score $e(v,s)$ constrained to have expectation at most one under every independent null distribution in that neighborhood.

The authors solve a robust max-min Kelly-growth problem and obtain a closed-form score: matching token and seed receives $(1-\delta/2)/p_0(s)$ and a mismatch receives $\delta/[2(n-1)p_0(s)]$. Multiplying these one-step e-values yields a test supermartingale. The detector stops when the product reaches $1/\alpha$, retaining false-positive probability at most $\alpha$ under optional stopping. The optimal worst-case log-growth rate is $J^*=H(p_0)-H(\nu_\delta)$, and the optimal expected sample size scales as $\log(1/\alpha)/J^*$.

The optimal generator is the maximal coupling used by speculative decoding. This theoretically supports SEAL's generator choice, while replacing SEAL's detector with the derived e-value rule.

### Evaluation

- **Synthetic theory checks:** binary-anchor convex programs converge to the derived $J^*$, and simulations with 10,000 stopping times per $\alpha$ show $\mathbb E[\tau_\alpha]/\log(1/\alpha)$ converging to $1/J^*$.
- **Real LLM task:** Llama2-7B-chat is watermarked using Phi-3-mini-128k-instruct as the anchor and evaluated on 300 MARKMYWORDS outputs across summarization, creative writing, and news generation under character-, word-, and text-level perturbations.
- **Main reported comparison:** at temperature 0.7 and $\alpha=0.02$, the proposed scheme reaches quality 0.919 and median detection size 72.0 tokens, compared with SEAL's 0.901 and 84.5 tokens. Its median size is also lowest at temperatures 0.3 and 1.0 (97.0 and 97.5 tokens).

These results support improved token efficiency for the tested target/anchor pair, not universal superiority across models or attack distributions.

### Strengths

- generation and detection are optimized under one explicit robust criterion;
- e-process construction gives formal anytime-valid false-positive control;
- the stopping-time rate is both achievable and information-theoretically optimal against adaptive target sequences;
- the method remains distortion-free at the token marginal;
- simulations and an attacked-text benchmark connect the theory to operational token savings.

### Limitations and reproducibility

- The anchor-neighborhood and positive-support assumptions are strong and are not directly validated for the selected LLM distributions.
- The stopping-time optimality is asymptotic as $\alpha\downarrow0$; finite-threshold comparisons are empirical.
- Real-data evidence covers one target/anchor model pair and 300 outputs, even though three temperatures and multiple attacks are used.
- Baselines are sequentialized with a particular Bonferroni correction, which may not represent their strongest possible e-process adaptations.
- **Public code: Not found.** The full paper, appendices, arXiv record, exact-title/arXiv-ID web searches, and repository-link surfaces were checked; no attributable implementation repository or separate supplement was found. Consequently, the mathematical specification is detailed, but exact benchmark replication, coupling implementation, random-key handling, and numerical safeguards cannot be code-verified.

**Reproducibility rating: 2.5/5.** The theorem statements, closed forms, hyperparameters, benchmark setup, and result tables are present, but lack of released code and a limited account of implementation details prevent turnkey reproduction.

### Source identity

- Authors: Baihe Huang, Eric Xu, Kannan Ramchandran, Jiantao Jiao, Michael I. Jordan
- arXiv: `2602.17608v1`, submitted 2026-02-19
- DOI: `10.48550/arXiv.2602.17608`
- Primary categories: cs.LG; also cs.AI and stat.ML
- Article type: primary method/theory paper, not bioinformatics

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
