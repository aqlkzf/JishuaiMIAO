---
layout: default
permalink: /paper-atlas/multi-armed-sequential-hypothesis-testing-by-betting-49c93519/
title: "Multi_Armed_Sequential_Hypothesis_Testing_By_Betting"
nav: false
wide: true
description: "设有 K 个数据源或“臂”。每一轮只能选择一个臂 An 并观察它的结果 Yn(An)，其余臂在这一轮的结果不可见。我们要检验的是全局原假设 即所有臂都满足各自的原假设；备择假设 则表示至少一个臂不是 null。典型例子是多个药物剂量：问题不是分别判断每个剂量，而是尽快发现“是否存在至少一个有效剂量”。"
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
    <h1>Multi_Armed_Sequential_Hypothesis_Testing_By_Betting</h1>
    <p>Multi-Armed Sequential Hypothesis Testing by Betting</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2603.17925" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Multi_Armed_Sequential_Hypothesis_Testing_By_Betting">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多臂序贯假设检验：用 betting/e-process 在探索与取证之间取得最优平衡

### 1. 论文究竟解决什么问题？

设有 $K$ 个数据源或“臂”。每一轮只能选择一个臂 $A_n$ 并观察它的结果 $Y_n(A_n)$，其余臂在这一轮的结果不可见。我们要检验的是全局原假设

$$
\mathcal P=\bigcap_{a\in\mathcal A}\mathcal P_a,
$$

即所有臂都满足各自的原假设；备择假设

$$
\mathcal Q=\bigcup_{a\in\mathcal A}\mathcal P_a^c
$$

则表示至少一个臂不是 null（`paper.md:167-177`）。典型例子是多个药物剂量：问题不是分别判断每个剂量，而是尽快发现“是否存在至少一个有效剂量”。

这是一篇统计学方法与理论论文，核心属于序贯检验、betting/e-process、多臂 bandit 和自适应实验设计，不是生物信息学论文。

### 2. 为什么已有方法不够？

对固定数据流，betting 方法已经能构造 anytime-valid 检验：只要财富过程 $W_n$ 是合适的 e-process，就在 $W_n\ge 1/\alpha$ 时拒绝，且允许随时查看、随时停止而保持第一类错误不超过 $\alpha$。

多臂场景的新困难不是有效性，而是效率。论文证明，只要每次选择可由过去信息预测，并且被选中臂的乘法因子在 null 下条件期望不超过 1，那么自适应选臂仍给出检验超鞅（`paper.md:180-203`）。真正困难的是：只观察一个臂时，怎样尽快找到最能产生反对 null 证据的臂？

普通 UCB 也不能直接套用，因为这里的“奖励”是

$$
\log\!\left(\boldsymbol\lambda_{\mathsf Q}(a)^\top\mathbf E(a)\right),
$$

其中最优 betting 组合 $\boldsymbol\lambda_{\mathsf Q}(a)$ 本身未知，因此奖励不可直接观测；而且 log 增量可能向负方向无界，不能预先假定为已知方差的次高斯变量（`paper.md:627-640`）。

### 3. 把问题拆成两种 regret

每次拉取臂 $a$ 后，方法得到一组 e-values

$$
\mathbf E_n(a)=\left(E_n^{(0)}(Y_n(a)),\ldots,E_n^{(d)}(Y_n(a))\right),
$$

再从单纯形 $\Delta_d$ 选择组合权重 $\boldsymbol\lambda_n$。财富按

$$
\overline W_n=\prod_{i=1}^n\boldsymbol\lambda_i^\top\mathbf E_i(A_i)
$$

累积（Eq. 13；`paper.md:224-248`）。取对数后，乘法财富变成累计收益。

论文把“追上全知 oracle”拆成两部分：

1. **臂内 portfolio regret**：在每个臂内部，在线选择 $\boldsymbol\lambda_n$，追赶事后看来最好的固定组合。Cover universal portfolio 的路径级 regret 至多为 $d\log(n+1)/2+\log 2$。
2. **臂间 allocation regret**：在线选择 $A_n$，追赶永远选择最优臂 $a_{\mathsf Q}$ 的 oracle。

只要每个臂的 portfolio regret 和臂间 allocation regret 都是 $o(n)$，实际财富的单位时间 log 增长率就会达到 oracle 最优值（Proposition 3.5；`paper.md:437-468`）。

### 4. SPRUCE 如何运行？

SPRUCE 是 **Sublinear Portfolio Regret Upper Confidence Estimation** 的缩写。它不直接估计不可见的 oracle 奖励，而是用“事后最优 portfolio 的经验 log 财富”作为中心，再加入既包含抽样不确定性、又包含 portfolio regret 的置信宽度：

$$
\begin{aligned}
\mathrm{UCB}_a(n)
={}&\max_{\boldsymbol\lambda\in\Delta_d}
\frac{1}{N_a(n-1)}\sum_{i=1}^{n}\mathbf 1\{A_i=a\}
\log(\boldsymbol\lambda^\top\mathbf E_i(A_i))\\
&+\sqrt{\frac{8b\gamma\log(\zeta n+1)}{N_a(n-1)}}
+\frac{4\gamma\log(\zeta n+1)}{N_a(n-1)}
+\frac{R_{N_a(n-1)}^{\mathrm{CO96}}}{N_a(n-1)}.
\end{aligned}
$$

其中 $N_a(n-1)$ 是臂 $a$ 过去被拉取的次数，$b$ 是 e-value 组合的上界，$\gamma>2$ 和 $\zeta>0$ 调节探索，$R_m^{\mathrm{CO96}}=d\log(m+1)/2+\log2$（`paper.md:474-485`）。

```text
已有历史
  |
  v
逐臂计算 regret-aware UCB
  |
  v
选择 UCB 最大的臂 A_n
  |
  v
只观察 Y_n(A_n)，构造 E_n(A_n)
  |
  v
更新各臂的 betting 财富并相乘得到 W_n
  |
  v
若 W_n >= 1/alpha，则拒绝全局原假设
```

论文给出两种财富更新：

- **UP**：每个臂运行 universal portfolio；得到检验超鞅。
- **CO96**：每个臂取事后最优累计 log 收益，减去 Cover regret bound，再指数化并跨臂相乘；它是 UP 财富的路径级下界，因此构成 e-process。该形式避免高维积分，可用求根/优化计算（`paper.md:485-519`）。

算法展示没有明确写出 $N_a(n-1)=0$ 时如何初始化 UCB。实际实现需要先各拉一次，或把未拉臂的 UCB 设为无穷大；这是根据算法结构给出的实现推论，论文中的明确规则 **Not found**。

### 5. 为什么能达到 oracle？

证明链条分三步：

1. 最优 portfolio 下的 log 增量是次指数的（Lemma 5.1）。
2. 把这个尾界与路径级 portfolio regret 合并，得到“事后最佳经验增长率”围绕真实最佳增长率的非渐近置信区间（Proposition 5.2）。
3. 用该区间做 UCB 分析，得到次优臂的期望拉取次数为对数阶，从而

$$
\mathcal R_{n,\mathsf Q}^{\mathrm{Alloc}}
=\mathcal O\!\left(\sum_{a\in\mathcal A}\frac{\log n}{\Delta_{a,\mathsf Q}}\right)
$$

（Theorem 5.3；`paper.md:643-706`）。

最终，SPRUCE 的单位时间 log 财富满足

$$
\lim_{n\to\infty}\frac{1}{n}\log W_n
=\max_{(a,\boldsymbol\lambda)\in\mathcal A\times\Delta_d}
\mathbb E_{\mathsf Q}\!\left[\log(\boldsymbol\lambda^\top\mathbf E_1(a))\right]
$$

几乎处处成立，即使与知道最佳臂、最佳 portfolio、甚至可访问完整反事实历史的比较器相比，也不会有更低的渐近增长率（Theorem 3.7；`paper.md:522-532`）。

对首次越过 $1/\alpha$ 的拒绝时间 $\tau_\alpha$，SPRUCE 还在 $\alpha\to0^+$ 的高置信极限中达到所有允许策略共同的下界：期望拒绝时间的主导常数与 oracle 完全相同（`paper.md:575-624`）。注意这是渐近结论，不是任意固定 $\alpha$ 下逐点相等。

### 6. 随机试验中的 treatment-effect 实例

论文令臂对应不同治疗方案，以共享对照为基线，检验

$$
H_0:\ \forall a,\ \psi_{\mathsf P}(a)\le\delta
\quad\text{vs}\quad
H_1:\ \exists a,\ \psi_{\mathsf P}(a)>\delta.
$$

每个受试者先由 SPRUCE 自适应选一个候选治疗臂，再以固定概率 $\pi$ 在该治疗与对照之间随机化。利用 Horvitz-Thompson 得分

$$
\widehat\psi_n(a)=Y_n^{\mathrm{obs}}(a)
\left(\frac{Z_n}{\pi}-\frac{1-Z_n}{1-\pi}\right),
$$

在 SUTVA、随机化无混杂和 positivity 下得到平均治疗效应的无偏估计。经过 $[0,1]$ 变换后，构造二元 e-value 向量

$$
\mathbf E_n=\left(1,\frac{\underline{\widehat\psi}_n(A_n)}{\underline\delta}\right),
$$

即可直接送入 SPRUCE（`paper.md:712-814`）。

### 7. 图像证据说明什么？

本地共检查了 Figures 1–3 的六个面板：

- 在 bounded-mean 的 easy/hard 模拟中，SPRUCE 的经验增长率逐渐接近 Oracle Arm，而 Round Robin 和 Random Selection 停留在明显更低水平。
- 在 $\alpha=0.001$ 的拒绝时间分布中，SPRUCE 明显早于两种非自适应分配，hard 场景差距更大。
- 在 treatment-effect 模拟中，论文报告 SPRUCE 的平均拒绝时间约为 Round Robin 或 Random Selection 的 44%（`paper.md:817-842`）。

这些图用于说明理论结论，并非真实临床试验，也不是大规模 benchmark。

### 8. 适用边界与复现状态

- 理论要求有限臂、逐臂跨轮 i.i.d. 的 e-value 向量、e-value 组合有界，以及臂间财富可分解。
- treatment-effect 版本还要求结果有界、SUTVA、随机化无混杂和 positivity。
- 论文没有展示非平稳环境、连续臂、带协变量选臂或真实数据结果；这些属于后续方向。
- arXiv v2 正文、附录证明和六个图面板已获取并核验。
- 官方代码仓库、模拟脚本、随机种子、重复次数和完整参数表均 **Not found**；因此可从公式重建算法，但不能凭当前材料精确复刻论文图片。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multi-Armed Sequential Hypothesis Testing by Betting

### Problem

The paper asks how to run an anytime-valid global-null test when several data sources or experimental arms are available but only one can be observed per round. The null says every arm is null; the alternative says at least one is non-null. Adaptive arm choice preserves type-I error when each selected observation contributes a valid conditional e-value, but a poor allocation rule can waste most samples on arms that generate little evidence (`paper.md:167-203`).

### Limitation of existing approaches

Standard testing-by-betting methods explain how to build an e-process for a fixed data stream, not how to learn which of several partially observed streams is most informative. Standard UCB bandit algorithms also do not apply directly: the relevant reward is the log payoff under an unknown arm-specific optimal betting portfolio, so it is not observed, and it need not satisfy a known sub-Gaussian bound (`paper.md:627-640`). The paper distinguishes itself from concurrent global-null work by targeting nonasymptotic anytime validity together with sharp oracle-style optimality, rather than only eventual rejection, loose stopping bounds, or finite-sample tests derived through asymptotic approximations (`paper.md:206-221`).

### Proposed method

The contribution is SPRUCE (Sublinear Portfolio Regret Upper Confidence Estimation). For every arm it computes the best empirical log wealth achievable by a fixed portfolio in hindsight, then adds a confidence width containing sampling uncertainty and a deterministic portfolio-regret penalty. It pulls the arm with the largest resulting UCB, constructs new e-values from that observation, and updates either a universal-portfolio test supermartingale or a computationally simpler regret-corrected e-process (`paper.md:474-519`).

The conceptual decomposition is the key: control portfolio regret within every arm and allocation regret across arms. The authors derive new concentration inequalities for the unobservable optimal log-growth reward and prove logarithmic allocation regret,

$$
\mathcal R_{n,\mathsf Q}^{\mathrm{Alloc}}
=\mathcal O\!\left(\sum_a\frac{\log n}{\Delta_{a,\mathsf Q}}\right),
$$

under their bounded e-value-vector assumptions (`paper.md:643-706`).

### Guarantees

SPRUCE is multi-armed log-optimal: its normalized log wealth converges almost surely to the largest expected log payoff attainable over every arm and betting portfolio. This matches an oracle that knows the best arm and portfolio in advance, and no comparator in the paper's oracle-history class can asymptotically do better (Theorem 3.7; `paper.md:522-532`). Its expected rejection time also matches the universal lower bound with the exact leading constant in the high-confidence limit $\alpha\to0^+$ (Proposition 4.1 and Theorem 4.2; `paper.md:575-624`). These are strong asymptotic efficiency claims, not finite-sample equality statements.

### Evaluation

The empirical evidence consists of six simulation panels:

- one-sided bounded-mean testing under easy and hard alternatives, comparing SPRUCE with Oracle Arm, Round Robin, and Random Selection;
- rejection-time distributions at $\alpha=0.001$ for the same settings;
- a randomized-treatment example that constructs e-values from bounded Horvitz-Thompson treatment-effect scores.

Visual inspection shows SPRUCE's growth approaching the oracle level and its stopping times remaining much earlier than nonadaptive allocations, especially in the hard setting. In the treatment-effect simulation, the paper reports an average SPRUCE rejection time about 44% of the round-robin or random-selection average (`paper.md:817-842`). The experiments illustrate the theorems but are not a broad empirical benchmark.

### Scope and limitations

The framework assumes finitely many arms, i.i.d. e-value vectors across rounds for each arm, bounded convex-combination payoffs, and an arm-wise wealth factorization. The RCT specialization further relies on bounded outcomes, SUTVA, no confounding from randomized treatment/control assignment, and positivity (`paper.md:251-275`, `paper.md:712-814`). Extensions to covariate-informed allocation, LLM evaluation, and quantum certification are proposed but not demonstrated (`paper.md:845-851`).

### Reproducibility

**Rating: 2/5 (paper-only theoretical reproducibility).** The arXiv v2 HTML provides complete theorem statements, proofs, three numbered figures, and six source image panels. No official implementation or data repository was found in the arXiv HTML/Markdown, and simulation scripts, seeds, replicate counts, and a complete parameter manifest are **Not found**. The algorithm can be reconstructed from the mathematics, but the published figures cannot be exactly regenerated from the acquired artifacts. No `doc_code.md` is produced because the normalized mode is `paper-only`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
