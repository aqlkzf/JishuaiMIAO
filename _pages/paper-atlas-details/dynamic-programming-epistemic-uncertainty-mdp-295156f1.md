---
layout: default
permalink: /paper-atlas/dynamic-programming-epistemic-uncertainty-mdp-295156f1/
title: "Dynamic_Programming_Epistemic_Uncertainty_MDP"
nav: false
description: "标准马尔可夫决策过程假定转移概率 P 已知，但实际决策中，转移模型往往来自有限数据或专家判断，本身并不确定。问题不仅是“下一步会随机走到哪里”，还包括“我们甚至不确定描述这种随机性的转移核是否正确”。前者是轨迹层面的偶然不确定性，后者是模型层面的认知不确定性。 论文要回答两个相互关联的问题： 能否用统一数学框架表示 robust MDP、multi-model MDP、分位数优化、CVaR 等各种“不确定转移核”模型？"
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
      <span>PMLR · 2026</span>
    </div>
    <h1>Dynamic_Programming_Epistemic_Uncertainty_MDP</h1>
    <p>Dynamic Programming for Epistemic Uncertainty in Markov Decision Processes</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2602.03381" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Dynamic_Programming_Epistemic_Uncertainty_MDP">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 面向 MDP 认知不确定性的动态规划：方法详解

### 论文到底在解决什么问题

标准马尔可夫决策过程假定转移概率 $P$ 已知，但实际决策中，转移模型往往来自有限数据或专家判断，本身并不确定。问题不仅是“下一步会随机走到哪里”，还包括“我们甚至不确定描述这种随机性的转移核是否正确”。前者是轨迹层面的偶然不确定性，后者是模型层面的认知不确定性。

论文要回答两个相互关联的问题：

1. 能否用统一数学框架表示 robust MDP、multi-model MDP、分位数优化、CVaR 等各种“不确定转移核”模型？
2. 什么时候还能沿用普通 MDP 最重要的工具——Bellman 方程、平稳最优策略、值迭代和策略迭代？

它的核心结论带有明显的“边界定理”性质：动态规划虽然带来计算便利，但也会把可选的风险度量压缩到一个极小集合。

### 统一建模：把转移核本身看成随机变量

论文定义 ambiguity-averse MDP：

$$
\mathsf M_\nu=(\mathcal S,\mathcal A,r,\nu,\gamma,\mu).
$$

其中状态、动作、奖励、折扣因子和初始分布与普通 MDP 相同；新增的 $\nu$ 是转移核 $\tilde P$ 的分布。给定策略 $\pi$，每一个可能的转移核都会产生一个期望回报，于是 $\mu^\top V^{\pi,\tilde P}$ 本身成为随机变量。决策者通过风险度量 $\rho$ 评价它：

$$
\sup_{\pi\in\Pi_{\mathsf H}}
\rho\!\left(\mu^\top V^{\pi,\tilde P}\right). \tag{6}
$$

这里有两层随机性，但论文有意把它们分开：

- $V^{\pi,\tilde P}$ 中的期望已经平均了轨迹随机性；
- 外层 $\rho$ 只处理对转移核 $\tilde P$ 的不确定性。

因此，这不是通常“已知 MDP 中对随机回报厌恶”的 risk-averse MDP，而是对模型参数不确定性进行风险调整。

### 静态核与重采样核为什么差别巨大

- **静态核：** 开始时抽取一次 $\tilde P_0\sim\nu$，之后所有时刻都使用同一个核。
- **重采样核：** 每个时刻独立抽取 $\tilde P_t\sim\nu$。

静态核会让长期历史携带关于同一个隐藏模型的信息，时间之间高度耦合；重采样则在时间上重新独立化。论文中的两状态反例表明：即使选最朴素的期望风险度量，静态核也可能让风险调整后的值函数不再满足 Bellman 方程，而重采样情形却可以满足。

### 不同风险度量如何复原已有模型

| $\rho$ 的选择 | 对应模型 | 含义 |
|---|---|---|
| Dirac 核下的期望 | nominal MDP | 转移核已知 |
| $\operatorname{ess\,inf}$ | robust MDP | 按支持集中的最坏核评价 |
| $\operatorname{ess\,sup}$ | optimistic MDP | 按最好核评价 |
| $\mathbb E^\nu$ | multi-model MDP | 对多个候选模型取平均 |
| $\operatorname{VaR}_\alpha$ | percentile optimization | 优化回报分位数 |
| CVaR、ERM 等 | Bayes/soft risk 模型 | 表达更细腻的风险偏好 |

统一表达并不意味着统一可解。论文的目标正是找到“哪些选择仍能让 Bellman 机器运转”。

### 风险调整后的 Bellman 算子

对平稳策略 $\pi$，先对随机核下的普通一步 Bellman 更新应用 $\rho$：

$$
T^{\pi,\nu,\rho}v(s)
=\rho\!\left(T^{\pi,\tilde P}v(s)\right). \tag{7}
$$

再在平稳策略中做逐状态优化：

$$
T^{\nu,\rho}v(s)
=\sup_{\pi\in\Pi_{\mathsf S}}
T^{\pi,\nu,\rho}v(s). \tag{8}
$$

如果 $\rho$ 单调且平移不变，这两个算子仍然单调、在 $\ell_\infty$ 范数下以 $\gamma$ 为收缩因子，而且局部最优策略可达到。但这还不够：论文明确要求值函数必须真正成为这些算子的固定点。

```text
MDP 数据 + 核分布 ν + 风险度量 ρ
                |
                v
       构造风险调整 Bellman 算子
                |
      值函数是否满足固定点条件？
          /                 \
        是                   否
        |                    |
平稳最优策略存在       普通状态空间上的
值迭代/策略迭代有效     Bellman 递推失效
        |                    |
 输出 V*、π*        增广状态/嵌套风险/
                    直接优化目标函数
```

### 动态规划成立时能得到什么

若策略评价和策略优化两个固定点条件都成立：

1. 存在一个平稳策略 $\pi^\star$，它从每个起始状态都最优；
2. 值迭代和策略迭代都以 $\gamma^n$ 控制的线性速度收敛；
3. 若 $\rho$ 还是凸风险度量，可用 Bellman 不等式构造凸优化问题求 $V^{\nu,\rho}$。

但实际计算 $T^{\pi,\nu,\rho}$ 仍依赖具体的 $\rho$ 和 $\nu$。论文给出统一理论框架和算法形式，并没有提供适用于任意风险度量的通用数值 oracle。

### 最关键的结论：Bellman 兼容性几乎只留下三个选择

论文用 Figure 3 的七状态构造，把图上的独立随机转移转化为对 $\rho$ 的代数约束。只要一个非平凡、law-invariant 的风险度量满足任一 Bellman 条件，它就必须：

- 对常数等于恒等映射；
- 正齐次；
- 对独立随机变量可加。

这些条件已经会排除 ERM 和 CVaR。进一步加入单调性后，Theorem 4.4 给出完整分类：

| 转移核机制 | 与状态级动态规划兼容的单调、law-invariant 风险度量 |
|---|---|
| 静态 | 只有 $\operatorname{ess\,inf}$、$\operatorname{ess\,sup}$ |
| 重采样 | 再加 $\mathbb E$ |

若把正则性加强为 $W^1$ 连续，则静态核下一个都没有，重采样核下只剩期望。

直观上，Bellman 递推要求把长期问题拆成逐状态、逐时间的一步问题；而 CVaR、VaR 等对整个回报分布的偏好通常无法被一个只依赖当前状态的标量值函数完整保存。所谓“不兼容”是说不能直接使用论文定义的状态级 Bellman 固定点，不是说这些目标没有任何求解办法。

### 如何理解这篇论文的贡献

它既不是新的深度 RL 算法，也没有生物信息学任务或实验数据。其领域是强化学习、运筹优化与风险决策理论，文章类型是理论方法论文。真正的新意是：

- 把多类认知不确定性 MDP 放进同一风险度量框架；
- 精确说明动态规划一旦成立，会自动带来哪些结构和算法结果；
- 反过来证明，要求这些便利会严重限制可表达的风险偏好。

对实践者的直接提示是：如果希望使用 CVaR、VaR 或 entropic risk 处理模型不确定性，就应预期需要增广状态、嵌套风险、分布式值表示或直接优化，而不能简单把风险度量塞进普通 Bellman 更新。

### 证据与复现边界

- 本文没有数值 benchmark，证据主要由定理、反例和证明构造组成。
- Figures 1-2 是两状态 Bellman 失败例，Figure 3 是风险度量分类证明的结构装置；三图均已视觉核验。
- arXiv HTML 不可用，39 页官方 PDF 经 MinerU hybrid 转换；正文、公式、表格、引用和图链通过质量检查，但仍保留轻微 OCR 排版噪声。
- 官方实现或公开代码仓库：**Not found**。检索范围包括 canonical arXiv 元数据、全文 URL、`code`、`software`、`implementation`、`repository` 和 `github` 等关键词。
- Jordan 页面中的 ICML 条目和后续 arXiv 条目是同一篇论文；ICML 条目的旧 href 错连到了 arXiv `2512.11779`，该编号属于另一篇 conformal prediction 论文。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Dynamic Programming for Epistemic Uncertainty in Markov Decision Processes

### At a glance

This ICML 2026 theory paper develops a unified framework for MDPs whose transition probabilities are uncertain. It models the transition kernel as a random variable $\tilde P\sim\nu$ and evaluates each policy by applying a risk measure $\rho$ to its kernel-dependent expected return. The framework covers nominal, robust, optimistic, multi-model, percentile, and other Bayes-risk MDP objectives without conflating epistemic model uncertainty with aleatoric trajectory randomness.

### Why existing approaches are insufficient

Earlier uncertain-MDP formulations were analyzed separately and exhibit sharply different computational behavior. Rectangular robust MDPs admit Bellman recursion, stationary policies, and efficient algorithms; static multi-model MDPs and percentile optimization can be NP-hard; and the dynamic-programming status of common CVaR or entropic epistemic-risk objectives was unclear. A catalogue of separate results did not reveal which property of the risk criterion creates or destroys tractability.

### Proposed framework

The ambiguity-averse MDP is $\mathsf M_\nu=(\mathcal S,\mathcal A,r,\nu,\gamma,\mu)$. A kernel is either drawn once and held fixed (**static**) or redrawn i.i.d. at each time (**resampled**). The decision problem is

$$
\sup_{\pi\in\Pi_{\mathsf H}}\rho\!\left(\mu^\top V^{\pi,\tilde P}\right).
$$

The authors define policy-specific and optimal risk-adjusted Bellman operators by applying $\rho$ to nominal one-step Bellman updates. They then separate two substantive requirements: Bellman fixed points for policy evaluation and for policy optimization.

### Main results

If $\rho$ is monotone and translation-invariant and both Bellman requirements hold, the risk-adjusted operators remain contractions, an optimal stationary policy exists for every starting state, and value and policy iteration converge linearly. A convex program is also available when $\rho$ is convex.

The key result is a complete boundary for law-invariant risk measures:

- For **static kernels**, monotone law-invariant dynamic programming permits only $\operatorname{ess\,inf}$ and $\operatorname{ess\,sup}$—the robust and optimistic extremes.
- For **resampled kernels**, it additionally permits expectation.
- Under $W^1$ continuity, no qualifying criterion works for static kernels, while expectation is the only survivor under resampling.

The paper reaches this classification by proving that Bellman compatibility forces identity on constants, positive homogeneity, and additivity for independent random variables. This excludes attractive criteria such as CVaR, VaR, and entropic risk from ordinary state-only Bellman recursion. It does not say these objectives are impossible to optimize: augmented states, nested/non-law-invariant risks, and direct objective optimization remain possible.

### Evidence and evaluation

The work is evaluated by theorem, counterexample, and characterization rather than datasets. A two-state MDP shows that expectation with a static random kernel violates the Bellman fixed-point property. A seven-state proof gadget converts transition geometry into algebraic constraints on $\rho$. Three substantive diagrams and Tables 1-2 were checked against the accompanying arguments; there are no numerical benchmark claims to reproduce.

### Limitations

The principal results assume finite state/action spaces, discounted return, known rewards, a single distribution $\nu$ over kernels, convex support, product structure, and law invariance plus monotonicity or continuity conditions. The framework does not fully include distributionally robust MDPs with an ambiguity set of distributions, average/total-return criteria, value approximation, or policy-gradient implementations.

### Reproducibility

**Evidence reproducibility: 4/5.** The complete 39-page arXiv paper, equations, proofs, tables, and diagrams are locally available. The canonical PDF passed MinerU hybrid OCR quality checks, although minor typography/OCR artifacts remain and arXiv HTML was unavailable. No official public code repository or numerical experiment package was found after checking canonical metadata, the full paper, URLs, and code/software/repository terms. The analysis is appropriately `paper-only`; its theoretical claims can be audited from the local primary source, but no implementation can be executed.

### Identity note

Jordan's publication page lists this work twice in 2026: once as an ICML paper and once as arXiv `2602.03381`. These are the same paper and share this workspace. The earlier ICML-list href points incorrectly to arXiv `2512.11779`, which is *Conditional Coverage Diagnostics for Conformal Prediction*; it was rejected during identity resolution.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
