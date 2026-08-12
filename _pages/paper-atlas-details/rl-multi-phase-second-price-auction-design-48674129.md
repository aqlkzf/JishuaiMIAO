---
layout: default
permalink: /paper-atlas/rl-multi-phase-second-price-auction-design-48674129/
title: "RL_Multi_Phase_Second_Price_Auction_Design"
nav: false
description: "这是机制设计、在线学习和强化学习交叉领域的论文，不是生物信息学文章。卖方反复进行带个性化保留价的二价拍卖；每一阶段除了定保留价，还要决定先卖哪类商品。前面的商品选择会改变后续状态和买家的估值，因此问题是一个未知 MDP，而不是各轮相互独立的 contextual bandit。 困难还在于买家具有策略性。买家可能当前少赚一点，通过故意高报或低报来影响卖方以后学习到的保留价和商品顺序。卖方看到的是竞价和成交结果，而不是买家的真实价值。"
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
      <span>Journal of Machine Learning Research · 2026</span>
    </div>
    <h1>RL_Multi_Phase_Second_Price_Auction_Design</h1>
    <p>A Reinforcement Learning Approach in Multi-Phase Second-Price Auction Design</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CLUB：多阶段二价拍卖中的强化学习与策略性竞价

### 这篇文章解决什么问题？

这是机制设计、在线学习和强化学习交叉领域的论文，不是生物信息学文章。卖方反复进行带个性化保留价的二价拍卖；每一阶段除了定保留价，还要决定先卖哪类商品。前面的商品选择会改变后续状态和买家的估值，因此问题是一个未知 MDP，而不是各轮相互独立的 contextual bandit。

困难还在于买家具有策略性。买家可能当前少赚一点，通过故意高报或低报来影响卖方以后学习到的保留价和商品顺序。卖方看到的是竞价和成交结果，而不是买家的真实价值。

### 模型

买家 $i$ 在状态 $x$、商品选择 $\upsilon$ 下的价值为

$$
r_{ih}(x,\upsilon)=1+\mu_{ih}(x,\upsilon)+z_{ih},
\qquad z_{ih}\sim F.
$$

论文假设存在已知特征 $\phi(x,\upsilon)$，使得期望价值和状态转移都对特征线性：

$$
\mu_{ih}(x,\upsilon)=\langle\phi(x,\upsilon),\theta_{ih}\rangle,
\qquad
\mathbb P_h(x'\mid x,\upsilon)=\langle\phi(x,\upsilon),\mathcal M_h(x')\rangle.
$$

但是卖方收入并不线性，因为成交和付款同时取决于个人保留价、最高/次高竞价以及阈值事件。这正是普通 LSVI-UCB 不能直接套用的原因。

### CLUB 的整体流程

CLUB 是 **Contextual-LSVI-UCB-Buffer** 的缩写：

```text
当前状态、历史竞价与成交结果
        ↓
极少量随机保留价 + 当前学习策略
        ↓
收集成交指示 q（未知 F 时再构造虚拟 q~）
        ↓
协方差增长是否达到更新阈值？
        ↓ 是
插入固定长度 buffer，但暂不换策略
        ↓
估计买家参数 theta（以及未知的 F）
        ↓
计算个性化保留价和非线性收入估计
        ↓
乐观的反向 LSVI 更新 Q
        ↓
得到新的商品选择和保留价策略
```

真正的新意不只是“用强化学习做拍卖”，而是把策略性买家的激励约束嵌入 RL 的更新节奏。

### 随机定价、低切换与 buffer 各自做什么？

#### 1. 随机定价负责惩罚谎报

辅助策略 $\pi_{\mathrm{rand}}$ 随机选一位买家，只向他提供商品，并从 $[0,3]$ 均匀抽一个保留价。低报可能错失本来有利的交易，高报可能以超过真实价值的价格成交，因此大幅谎报会有即时成本。

CLUB 只以 $1/(HK)$ 的小概率执行这个策略，所以惩罚机制不会带来过多直接收入损失。

#### 2. low-switching 负责减少策略更新次数

对每个阶段维护信息矩阵

$$
\Lambda_h^k=I+\sum_{\tau\le k}\phi_h^\tau(\phi_h^\tau)^\top.
$$

只有某个方向的信息大约翻倍时，才考虑更新策略。这比固定长度 epoch 更适合 MDP，因为状态和动作特征由当前策略产生，最小特征值不一定按可预测速度增长。

#### 3. buffer 负责推迟谎报收益

达到更新阈值后，CLUB 不立即换策略，而是等待

$$
L_{\mathrm{buffer}}=\frac{3\log K}{\log(1/\gamma)}
$$

个 episode。买家未来效用按 $\gamma<1$ 折扣，谎报对新策略的潜在收益必须等到 buffer 结束才出现，届时价值大约已缩小到 $K^{-3}$ 量级。

因此三者不是重复设计：随机定价增加“说谎成本”，low-switching 限制“可被操纵的更新次数”，buffer 延迟“说谎收益兑现时间”。

### 已知噪声分布 $F$ 时

如果 $F$ 已知，买家在阈值 $m_{ih}$ 下成交的概率可以写成 $F$ 与 $\theta_{ih}$ 的函数。论文用成交指示 $q_{ih}\in\{0,1\}$ 做约束最小二乘：

$$
\widehat\theta_{ih}=
\arg\min_{\|\theta\|\le2\sqrt d}
\sum_\tau
\left[q_{ih}^\tau-1+F\left(m_{ih}^\tau-1-
\langle\phi_h^\tau,\theta\rangle\right)\right]^2.
$$

使用成交与否而不是直接回归竞价有一个重要好处：小幅谎报不一定改变阈值事件，因此对参数估计的破坏有限。

随后对每位买家计算最优个性化保留价

$$
\widehat\rho_{ih}(x,\upsilon)=
\arg\max_y y\left[1-F\left(y-1-\widehat\mu_{ih}(x,\upsilon)\right)\right],
$$

再把各买家的保留价和竞价次序组合成收入估计 $\widehat R_h$。CLUB 的反向价值更新为

$$
\widehat Q_h=
\min\left\{\omega_h^\top\phi+\widehat R_h+
\operatorname{poly}(\log K)\|\phi\|_{\Lambda_h^{-1}},,3H\right\}.
$$

与普通 LSVI-UCB 不同，$\omega_h$ 只拟合下一状态价值，非线性收入由单独的 plug-in 估计加入。已知 $F$ 的 regret 为

$$
\widetilde O(H^{5/2}\sqrt K).
$$

### 未知噪声分布：为什么需要 simulation？

如果直接把 $F$ 换成经验估计 $\widehat F$ 再求 $\theta$，两种估计误差会耦合，难以保持 $\sqrt K$ regret。传统办法是经常真的执行随机价格做纯探索，但会牺牲收入，典型界是 $\widetilde O(K^{2/3})$。

CLUB 的关键做法是构造一个**没有实际执行的虚拟保留价**：

$$
\widetilde\rho_{ih}^\tau\sim\mathrm{Unif}[0,3],
\qquad
\widetilde q_{ih}^\tau=\mathbb 1\{b_{ih}^\tau\ge\widetilde\rho_{ih}^\tau\}.
$$

真实拍卖仍然使用当前较优策略；算法只利用已经观察到的竞价，回答“如果当时使用这个随机保留价，会不会成交”。这相当于从同一条竞价记录中得到随机探索的反事实标签，而不支付实际探索的收入代价。

基于 $\widetilde q$，参数估计变为

$$
\widehat\theta_{ih}=
\arg\min_{\|\theta\|\le2\sqrt d}
\sum_\tau\left(3N\widetilde q_{ih}^\tau-
[1+\langle\phi_h^\tau,\theta\rangle]\right)^2.
$$

再从竞价残差构造经验 CDF：

$$
\widehat F(z)=\frac1{NTH}\sum_{i,\tau,h}
\mathbb 1\{b_{i\tau h}-1-\langle\phi_h^\tau,
\widehat\theta_{ih}\rangle\le z\}.
$$

这样 $\theta$ 和 $F$ 的误差被分开控制，DKW 不等式给出经验 CDF 的 $1/\sqrt K$ 收敛。未知 $F$ 版本还在 $k$ 为 2 的幂时强制更新，避免 CDF 长期过旧；这些额外更新只有 $O(\log K)$ 次，每次仍经过 buffer。

当分布类的 covering number 随 $K$ 多项式增长时，最终达到

$$
\widetilde O(H^3\sqrt K)
$$

量级的收入 regret。

### 实验说明

论文只做了小型合成实验：$N=1$、$K=10{,}000$、$\gamma=0.9$、30 次重复。contextual bandit 中 CLUB 与 NPAC-S 平均 regret 接近，并优于 SCORP；在 $H=2$ 的 MDP 中，CLUB 30/30 次优于 NPAC-S，平均 regret 为 203.07 对 756.31。截断高斯噪声下仍保持同样的 MDP 排序。

这些结果支持所构造低维环境中的算法行为，但不能说明其已适用于真实广告市场、多买家大规模系统或长时域 MDP。

### 代码应该怎样理解？

JMLR 给出的 `SPA_CLUB` 是官方**实验代码**，不是完整通用实现。它确实实现了 buffer、稀疏随机定价、协方差/2 的幂更新、虚拟成交标签、$\theta$ 最小二乘、经验 CDF、网格保留价和 $H=2$ 的乐观 Q 更新；但只覆盖 $N=1$ 的小型情形。

需要特别注意：MDP 脚本中存在 `if h==0`，而循环的 $h$ 从 1 开始，因此该分支不可达。仓库也没有依赖锁定、随机种子、测试或原始结果文件。所以代码适合帮助理解实验，不宜直接当作理论算法的生产实现。

### 最重要的理解

CLUB 的逻辑可以概括为：

> 用随机价格让说谎有代价，用低切换减少可操纵的策略更新，用 buffer 让说谎收益很晚才兑现，再用反事实随机保留价解决未知噪声下的探索成本。

这四部分共同作用，才把策略性拍卖中的学习问题转化成可以进行乐观 RL 分析、并达到 $\sqrt K$ 级 regret 的机制。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A Reinforcement Learning Approach in Multi-Phase Second-Price Auction Design

### Problem

This JMLR paper studies repeated personalized-reserve second-price auctions in which the seller's item choices influence later bidder valuations through an unknown MDP. The seller must learn both item order and reserve prices while bidders can strategically misreport values to manipulate future policies. The setting is mechanism design and reinforcement learning—not bioinformatics.

Prior contextual-bandit auction methods do not capture endogenous temporal dynamics, and pure exploration for an unknown nonparametric market-noise distribution commonly yields $\widetilde O(K^{2/3})$ regret. Standard LSVI-UCB also cannot be used directly because seller revenue is an unknown nonlinear function of bidder thresholds and is not observed as a clean linear reward.

### Proposed method

The paper introduces **CLUB (Contextual-LSVI-UCB-Buffer)**. It combines:

1. a rare random-price policy that makes large over- or underbids costly;
2. covariance-triggered low-switching updates;
3. buffer periods of length about $3\log K/\log(1/\gamma)$, which delay any benefit from manipulation for impatient bidders;
4. win-indicator estimation of bidder value parameters;
5. plug-in personalized reserve/revenue estimation plus optimistic linear-MDP value iteration.

When market noise $F$ is unknown, CLUB samples virtual random reserves and computes counterfactual win indicators from real bids. This “simulation” supplies identification data without executing pure-exploration prices. It estimates bidder parameters from these indicators, estimates $F$ from residual bids with an empirical CDF, and adds power-of-two policy updates so the CDF estimate remains fresh.

### Guarantees

Under a known feature map, linear-MDP structure, impatient bidders, regular noise density, and log-concavity assumptions, known-$F$ CLUB achieves

$$
\widetilde O(H^{5/2}\sqrt K)
$$

revenue regret. For unknown $F$ in a class $\mathcal F$, the bound is

$$
\widetilde O\!\left(H^3\sqrt K+H^{5/2}\sqrt{K\log\mathcal N_{1/K}(\mathcal F)}\right).
$$

With polynomial covering number this becomes $\widetilde O(H^3\sqrt K)$, matching the embedded linear-MDP lower bound in its dependence on $K$.

### Evaluation

Experiments use small synthetic environments with $N=1$, $K=10{,}000$, $\gamma=0.9$, and 30 trials. In the contextual uniform-noise case, mean regrets are 106.62 for CLUB, 178.96 for SCORP, and 99.69 for NPAC-S; CLUB and NPAC-S are comparable. In the $H=2$ MDP, CLUB beats NPAC-S in all 30 trials, averaging 203.07 versus 756.31. Truncated-Gaussian robustness experiments retain the same ordering in the MDP case (265.59 versus 923.95). The plots support the finite synthetic comparisons but provide no real-market validation or ablation of buffers/simulation.

### Code and reproducibility

JMLR links the official [SPA_CLUB repository](https://github.com/Air-8/SPA_CLUB); this workspace preserves commit `1a6774e070228c5459bb806f529059675178349c`. The source matches the experimental motifs: buffer length, random reserves, covariance/power-of-two update triggers, simulated outcomes, constrained least squares, empirical CDF, reserve grid search, optimistic two-step value recursion, and 30-trial baselines.

Code-paper fidelity is **medium**. The repository explicitly covers experiments, not the full theorem-level method: it is specialized to one bidder and either contextual or two-state/two-action $H=2$ settings. It lacks dependency versions, seeds, tests, raw outputs, and a general mechanism implementation. An `if h==0` stage branch in the MDP script is unreachable because loops start at $h=1$, so an exact rerun should audit that behavior first.

### Limitations

- Strategic deterrence relies on bidders discounting future utility more than the seller.
- Theory requires a known, useful feature representation and linear MDP structure.
- Noise smoothness and bounded-complexity assumptions rule out hard nonparametric cases behind the classical $K^{2/3}$ lower bound.
- Virtual-outcome simulation depends on observing submitted bids; it does not solve strategic behavior under arbitrary information restrictions.
- Empirical evidence is synthetic, single-bidder, low-dimensional, and small-horizon.

### Bottom line

The central contribution is a careful coupling of incentive design and online RL: low switching alone controls policy churn, but buffers control *when manipulation can pay*, while random reserves control *how costly manipulation is*. For unknown noise, counterfactual reserve simulation separates value and noise estimation and restores a $\sqrt K$ regret rate without frequent pure-exploration auctions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
