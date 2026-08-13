---
layout: default
permalink: /paper-atlas/universal-log-optimality-7064fcab/
title: "Universal Log-Optimality"
nav: false
wide: true
description: "论文研究的是序贯假设检验，不是生物信息学问题。数据不断到来时，我们希望随时都能检查是否拒绝复合原假设 \\mathcal P，同时保证即使反复查看结果，第一类错误率仍不超过 \\alpha。 标准做法是构造非负的 e-process Wn，当 时拒绝原假设。相应的首次拒绝时间是 Ville 不等式保证 \\sup{P\\in\\mathcal P}\\PrP(\\tau\\alpha<\\infty)\\leq\\alpha。"
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
      <span>arXiv · 2025</span>
    </div>
    <h1>Universal Log-Optimality</h1>
    <p>Universal Log-Optimality for General Classes of e-processes and Sequential Hypothesis Tests</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2504.02818" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Universal Log-Optimality">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 通用对数最优 e-process：从后悔界到序贯检验最优性

### 1. 这篇论文解决什么问题？

论文研究的是**序贯假设检验**，不是生物信息学问题。数据不断到来时，我们希望随时都能检查是否拒绝复合原假设 $\mathcal P$，同时保证即使反复查看结果，第一类错误率仍不超过 $\alpha$。

标准做法是构造非负的 e-process $W_n$，当

$$
W_n\geq \frac{1}{\alpha}
$$

时拒绝原假设。相应的首次拒绝时间是

$$
\tau_\alpha=\inf\{n\in\mathbb N:W_n\geq1/\alpha\}.
$$

Ville 不等式保证 $\sup_{P\in\mathcal P}\Pr_P(\tau_\alpha<\infty)\leq\alpha$。但“检验始终有效”并不等于“检验有力”。论文进一步问两个问题：

1. 在备择分布 $Q$ 下，$W_n$ 的长期对数增长率能否达到最优？
2. 达到阈值 $1/\alpha$ 平均需要多少个样本，能否达到最小可能的渐近常数？

来源：`paper.md:17-128`。

### 2. 基本构造：把 e-value 当成两种资产

每个时间点 $i$ 有两个非负 e-value，记为 $E_i^{(1)}$ 和 $E_i^{(2)}$。在原假设下，它们的期望都不超过 1。检验者在看到第 $i$ 个观测之前选择 $\lambda_i\in[0,1]$，然后更新财富：

$$
W_n=\prod_{i=1}^n
\left((1-\lambda_i)E_i^{(1)}+\lambda_iE_i^{(2)}\right). \tag{1}
$$

可以把两个 e-value 看成两种资产，$\lambda_i$ 是第二种资产的仓位。因为 $\lambda_i$ 是可预测的、每一步只是 e-value 的凸组合，所以式 (1) 是检验超鞅，进而可以安全地用于 anytime-valid 检验（`paper.md:45-60,929-951`）。

论文的主要功效理论采用 i.i.d. 结构。仅为了保证原假设下的有效性，可以放宽成条件 e-value；但不能据此自动认为后面的最优功效结论也已经覆盖任意依赖数据。

### 3. 如果知道真实备择分布，最优策略是什么？

假设真实备择分布是 $Q$。若一直使用固定仓位 $\lambda$，一步的期望对数收益为

$$
\ell_Q(\lambda)
=\mathbb E_Q\left[
\log\left((1-\lambda)E_1^{(1)}+\lambda E_1^{(2)}\right)
\right].
$$

最优固定仓位与最优增长率定义为

$$
\lambda_Q^\star\in\arg\max_{\lambda\in[0,1]}\ell_Q(\lambda),
\qquad
\ell_Q^\star=\ell_Q(\lambda_Q^\star).
$$

若 $Q$ 已知，一直使用 $\lambda_Q^\star$ 即可；强大数律给出

$$
\frac{1}{n}\log W_n(\lambda_Q^\star)\to\ell_Q^\star
\quad Q\text{-几乎必然}.
$$

但复合备择意味着 $Q$ 未知，所以 $\lambda_Q^\star$ 只是分析用的 oracle，不能直接作为实际算法（`paper.md:73-79,258-266`）。

### 4. 核心思想：不估计 $Q$，只控制确定性的 portfolio regret

论文把实际过程与“事后看完整条序列后才选出的最佳固定仓位”比较：

$$
\mathcal R_n
=\max_{\lambda\in[0,1]}
\sum_{i=1}^n\log\left((1-\lambda)e_i^{(1)}+\lambda e_i^{(2)}\right)
-\log W_n. \tag{2}
$$

这里的后悔值对每条确定性序列都定义，不是概率意义上的平均损失。只要存在 $r_n=o(n)$ 使 $\mathcal R_n\leq r_n$，那么后悔除以 $n$ 后会消失，实际过程的平均对数财富就不会长期落后于 oracle。

#### 三个显式构造不能混为一谈

1. **Universal Portfolio（UP）**

UP 直接给出每一步的可预测仓位：

$$
   \lambda_n^{\mathrm{UP}}
   =\frac{\int_0^1\lambda W_{n-1}(\lambda)\,dF(\lambda)}
          {\int_0^1 W_{n-1}(\lambda)\,dF(\lambda)},
   $$

其中 $F=\mathrm{Beta}(1/2,1/2)$。它是真正逐步下注的 self-financing 策略，并有 $O(\log n)$ 后悔界。

2. **Regret-CO96**

它先计算当前序列上的最佳固定仓位财富，再从对数财富中减去 CO96 后悔上界：

$$
   W_n^{\mathrm{CO96}}
   =\exp\left\{
   \log W_n(\lambda_n^{\max})-\frac12\log(n+1)-\log2
   \right\}.
   $$

3. **Regret-OJ23**

它采用同样的“经验最大对数财富减罚项”思路，但使用 Orabona–Jun 2023 给出的更紧后悔罚项。

因此，UP 是逐步投资规则；CO96/OJ23 是由经验最大财富和可证明罚项构造出来的保守 e-process。论文证明

$$
W_n^{\mathrm{CO96}}leq W_n^{\mathrm{OJ23}}leq W_n^{\mathrm{UP}},
$$

且三者都有对数级 portfolio regret（`paper.md:174-198,330-352`）。论文没有提出一个需要读者自行猜测容差的通用数值优化器。

### 5. 从输入到检验结果的完整流程

```text
连续到来的观测
      |
      v
针对原假设构造 E_i^(1), E_i^(2)
      |
      v
选用全区间 [0,1] 的低后悔构造
  UP 逐步仓位 / CO96 / OJ23
      |
      v
更新凸组合财富 W_i
      |
      +---- W_i >= 1/alpha ----> 拒绝原假设
      |
      v
用 regret + numeraire 理论证明
增长率与拒绝时间常数最优
```

不同具体问题的主要工作，是找到对原假设有效的 e-value 表示；一旦它能写成式 (1)，通用定理就可以接上。

### 6. “Universal”究竟是什么意思？

论文先定义**逐分布的通用性**：同一个不依赖 $Q$ 的过程，对每个固定的 $Q\in\mathcal Q$ 都满足

$$
\liminf_{n\to\infty}\frac{1}{n}
\left(\log W_n-\log W_n'\right)\geq0
\quad Q\text{-几乎必然},
$$

其中 $W'$ 是同一比较类中的任意过程。这里每次先固定 $Q$，再取极限。“对所有 $Q$ 都成立”并不自动等于“对 $Q$ 一致收敛”。

第 6 节才证明更强的**分布一致**版本：先对 $Q\in\mathcal Q^\circ$ 取上确界，再控制最终偏差概率。需要区分三层含义：

- 原假设下对所有 $P$ 的 anytime validity；
- 同一算法对每个固定 $Q$ 的 pointwise 最优性；
- 在一整类 $Q$ 上的 distribution-uniform 收敛或拒绝时间界。

一致的相对支配可以由分布无关的后悔界得到；但 $n^{-1}\log W_n$ 一致收敛到 $\ell_Q^\star$ 还需要 $p\in[1,2)$ 阶一致可积性与 $r_n=o(n^{1/p})$。一致拒绝时间界还需要 $s>2$ 阶矩的一致控制以及 $\ell_Q^\star$ 的统一正下界（`paper.md:723-789`）。

### 7. 为什么 regret 足够？numeraire 是另一半

第 5 节把 $\lambda\in[0,1]$ 推广为 $\theta\in\Theta$，把每步混合收益推广为 $E_i(\theta)$。定义广义后悔：

$$
\sup_{\theta\in\Theta}\sum_{i=1}^n\log E_i(\theta)-\log W_n\leq r_n(Q).
$$

同时定义 $(\Theta,Q)$-numeraire $\theta_Q^\star$，使任意可预测策略相对于它的财富比

$$
\prod_{i=1}^n\frac{E_i(\theta_i)}{E_i(\theta_Q^\star)}
$$

成为非负 $Q$-超鞅。证明形成一个夹逼：

- numeraire 性质限制实际财富不能持续显著高于 oracle；
- regret 界限制实际财富不能显著低于事后最优，而事后最优至少不低于 oracle。

因此实际财富、oracle 财富和事后最优财富在次线性尺度内夹在一起。对两种 e-value 的凸组合，$\lambda_Q^\star$ 满足的 KKT 条件正好推出 numeraire 性质（`paper.md:615-721,953-1047,1209-1243`）。

注意：论文讨论 reverse information projection 是为了说明相关的单步 numeraire e-value 文献，并没有把“先求 reverse projection”作为本文算法步骤。

### 8. 最优增长率与最优拒绝时间

Theorem 2.1 说明：若 $\mathcal R_n=o(n)$，则

$$
\frac{1}{n}\log W_n\to\ell_Q^\star
\quad Q\text{-几乎必然},
$$

而比较类中的其他过程不能拥有更大的渐近增长率。

对拒绝时间，任意可预测策略都满足类内下界

$$
\frac{\mathbb E_Q[\tau_\alpha]}{\log(1/\alpha)}
\geq\frac{1}{\ell_Q^\star}.
$$

若 $\ell_Q^\star>0$，且 oracle 下的中心化对数收益具有某个 $s>2$ 阶有限矩，那么次线性后悔过程达到同一个常数：

$$
\lim_{\alpha\to0^+}
\frac{\mathbb E_Q[\tau_\alpha]}{\log(1/\alpha)}
=\frac{1}{\ell_Q^\star}.
$$

下界的关键工具是 numeraire 财富比、可选停止、Jensen 不等式与 Wald 恒等式；上界还使用有限矩浓缩。这个最优性是在 $\mathcal W$ 或 $\mathcal W(\Theta)$ 内成立，不是对所有可能序贯检验的信息论下界（`paper.md:368-459,677-705,1049-1191`）。

### 9. 三个具体例子

#### 单侧有界均值

若 $X_i\in[0,1]$，检验 $\mathbb E[X_i]\leq\mu_0$，可使用

$$
W_n^{\leq}=\prod_{i=1}^n\left(1+\gamma_i(X_i-\mu_0)\right),
\qquad \gamma_i\in[0,1/\mu_0].
$$

它是通用混合式的特例，低后悔策略可以在完整区间内适应最优仓位（`paper.md:467-505`）。

#### 双侧有界均值

检验 $\mathbb E[X_i]=\mu_0$ 时取

$$
E_i^{(1)}=\frac{1-X_i}{1-\mu_0},
\qquad
E_i^{(2)}=\frac{X_i}{\mu_0}.
$$

仓位等价于 $\gamma_i\in[-1/(1-\mu_0),1/\mu_0]$。在论文引用的结果下，这一形式穷尽了该问题的检验鞅，因此类内最优结论更有力度（`paper.md:507-573`）。

#### 有界二元组的均值差

令 $D_i=X_i-Y_i$、$Z_i=(D_i+1)/2$，即可把均值差检验化成 $\mu_0=1/2$ 的有界均值检验。允许完整仓位区间的低后悔策略得到比文中引用的 ONS 界更紧的渐近拒绝时间界（`paper.md:575-613`）。

### 10. 图像证据如何理解？

- Figure 1 是三个嵌套集合，说明“具体检验 ⊂ 式 (1) 混合类 ⊂ Section 5 一般类”。
- Figure 2 同时示意增长率和首次拒绝时间。
- Figure 3 对比两种 Bernoulli 情形：当 oracle 仓位在 ONS 范围内时，ONS 可接近最优；当 oracle 在范围外时，UP/CO96/OJ23 接近最优而 ONS 明显落后。
- Figure 4 用首次拒绝时间分布展示同一机制。

这些是模拟说明，不是定理的证明。完整逐图分析见 `figure_analysis.md`。

### 11. 局限与复现边界

- 主功效理论以 i.i.d. 为核心条件；不能把原假设有效性的条件 e-value 放宽直接套到所有功效结论。
- 拒绝时间等式需要正的 $\ell_Q^\star$ 和 $s>2$ 阶矩；分布一致版本条件更强。
- 最优性相对于论文定义的过程类，而不是全体序贯检验。
- 两样本与独立性检验只给出 oracle witness 的化简；witness 需要从数据学习时仍能否保持最优性，被明确留作未来问题（`paper.md:897-925`）。
- 未发现官方代码或独立补充材料；arXiv 源包含正文和图片资产，但没有可运行的模拟脚本。
- 论文给出解析构造，没有规定通用数值积分器、优化器或容差。因此实现时必须自行记录这些工程选择，不能假称它们来自论文。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Universal Log-Optimality for General Classes of e-processes and Sequential Hypothesis Tests

### Problem

Anytime-valid sequential tests can reject a composite null by thresholding an e-process at $1/\alpha$, but validity alone does not say how quickly the process grows under an alternative or how many observations rejection will take. This paper asks whether one adaptive procedure can attain the best possible almost-sure log-growth and expected-rejection-time constants for every unknown distribution in a composite alternative (`paper.md:17-128`).

### Gap in prior approaches

Online Newton Step (Hazan, Agarwal, and Kale, *Machine Learning*, 2007) has been used for betting-based bounded-mean and related tests, including the framework of Waudby-Smith and Ramdas (*JRSS B*, 2024), but its restricted betting interval can exclude the log-optimal allocation. Existing analyses therefore did not provide matching optimal lower and upper constants in the paper's general process class. Other adjacent results target $L_1(Q)$ log optimality without rejection-time analysis, or obtain exact sample-complexity constants in different parametric/bandit classes (`paper.md:791-823`).

### Proposed framework

The basic test supermartingale multiplies predictable convex mixtures of two e-values,

$$
W_n=\prod_{i=1}^n\left((1-\lambda_i)E_i^{(1)}+\lambda_iE_i^{(2)}\right).
$$

For a fixed alternative $Q$, the oracle constant allocation maximizes the expected log increment $\ell_Q(\lambda)$, giving optimum $\ell_Q^\star$. The central result is that any valid e-process whose deterministic portfolio regret is $o(n)$ adapts to the unknown $Q$: its log wealth converges almost surely to $\ell_Q^\star$, it is asymptotically no worse than any comparator in the class, and—under a finite centered log-increment moment of order $s>2$ and $\ell_Q^\star>0$—its expected rejection time satisfies

$$
\lim_{\alpha\to0^+}\frac{\mathbb E_Q[\tau_\alpha]}{\log(1/\alpha)}
=\frac{1}{\ell_Q^\star}.
$$

The matching lower bound holds for every predictable allocation in the class (`paper.md:258-459`).

The paper gives three explicit logarithmic-regret e-processes. Universal Portfolio uses a predictable beta-mixture allocation; Regret-CO96 and Regret-OJ23 instead subtract certified regret penalties from empirical maximum log wealth, with OJ23 using the sharper penalty. They are related but are not the same computational construction (`paper.md:174-198,330-352`).

### Proof mechanism and scope

The general theory replaces the allocation $\lambda$ with $\theta\in\Theta$. A $(\Theta,Q)$-numeraire makes wealth relative to the $Q$-optimal process a nonnegative $Q$-supermartingale. This controls adaptive wealth from above, while regret controls it from below; the resulting concentration sandwich proves log optimality. Wald's identity, optional stopping, Jensen's inequality, and a finite-moment concentration bound yield the rejection-time constants (`paper.md:615-721,953-1243`).

“Universal” first means one process is pointwise optimal for every fixed $Q$. Section 6 strengthens this to distribution-uniform eventual-deviation statements. Uniform convergence and stopping-time conclusions require additional uniform integrability, regret-rate, moment, and positive-growth assumptions (`paper.md:723-789`).

### Applications and empirical illustrations

The framework specializes to one-sided bounded-mean tests, the exhaustive martingale representation for two-sided bounded-mean tests, and bounded difference-in-means tests. Appendix A gives an oracle-witness reduction for two-sample and independence testing, but learning that witness while retaining optimality is left unresolved (`paper.md:467-613,897-925`).

Figures 2-4 simulate growth rates and first-rejection-time distributions. When the oracle allocation lies inside ONS's restricted range, ONS can track the optimum; when it lies outside, Universal Portfolio and the two regret-corrected processes approach the optimum while ONS does not. These plots illustrate the mechanism and are not the evidence for the theorems (`figure_analysis.md`).

### Reproducibility and limitations

- **Reproducibility: 2/5.** The paper and exact TeX/figure source are public, and the analytic constructions are explicit, but no official implementation or runnable simulation scripts were found.
- The main power theory uses i.i.d. observations/e-value tuples; conditional e-values suffice only for the broader null-validity statement made in the introduction.
- Expected-rejection-time equality needs positive optimal growth and a finite $s>2$ centered log-increment moment. Distribution-uniform results impose stronger uniform conditions.
- Optimality and lower bounds are relative to $\mathcal W$ or $\mathcal W(\Theta)$, not globally information-theoretic over all tests.
- The paper does not specify generic numerical integration/optimization tolerances for implementing UP or hindsight maximization.
- No separate supplement exists; appendices are included in the main manuscript. No code repository was found in the paper, arXiv source, GitHub title/arXiv searches, or identified author-owned repository scope.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
