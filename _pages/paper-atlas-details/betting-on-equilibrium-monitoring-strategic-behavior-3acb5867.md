---
layout: default
permalink: /paper-atlas/betting-on-equilibrium-monitoring-strategic-behavior-3acb5867/
title: "Betting_On_Equilibrium_Monitoring_Strategic_Behavior"
nav: false
wide: true
description: "假设一个多智能体系统一直在运行：交易机器人持续博弈，自动驾驶车辆持续协调，或者多个学习智能体持续更新策略。我们希望在行为刚刚偏离约定规则时就报警，而不是先规定“收集 10,000 轮数据”，结束后再做一次离线检验。 难点在于：如果不断查看普通固定样本检验的结果，并在“看起来显著”时停止，就会积累假阳性。本文用 e-value / e-process（证据值/证据过程）解决这个问题。"
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
    <h1>Betting_On_Equilibrium_Monitoring_Strategic_Behavior</h1>
    <p>Anytime Detection of Strategic Deviations in Multi-Agent Systems</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/GauthierE/anytime-detection-deviation" target="_blank" rel="noopener noreferrer" aria-label="Open code for Betting_On_Equilibrium_Monitoring_Strategic_Behavior">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法详解：如何随时检测多智能体的策略偏离

### 1. 这篇论文解决什么问题？

假设一个多智能体系统一直在运行：交易机器人持续博弈，自动驾驶车辆持续协调，或者多个学习智能体持续更新策略。我们希望在行为刚刚偏离约定规则时就报警，而不是先规定“收集 10,000 轮数据”，结束后再做一次离线检验。

难点在于：如果不断查看普通固定样本检验的结果，并在“看起来显著”时停止，就会积累假阳性。本文用 **e-value / e-process（证据值/证据过程）**解决这个问题。它把检验理解成下注：原假设成立时，下注财富的期望不能系统增长；一旦财富异常变大，就产生反对原假设的证据。因为控制针对整个时间轴成立，所以研究者可以随时查看并自适应停止。

论文当前版本为 arXiv `2601.05427v3`，标题是 *Anytime Detection of Strategic Deviations in Multi-Agent Systems*。用户提供的 *Betting on Equilibrium: Monitoring Strategic Behavior in Multi-Agent Systems* 是同一 arXiv 身份的早期/列表标题。当前获取的 arXiv 元数据没有确认 ICML 2026，因此本文档不把它写成已核实发表信息。

### 2. 为什么已有方法不够？

Babichenko 等人在 2017 年研究了固定数据集上的均衡检验。这类方法适合“先收集、后检验”，却不适合无限运行的系统。每来一批数据就重复普通检验，相当于不断寻找有利的停止点，会破坏显著性水平。

本文的改进有三点：

1. 从固定样本检验改为安全的序贯监控；
2. 在重复标准型博弈中，不必事先知道被检验的均衡混合策略，只需能够计算各纯动作偏离的反事实收益；
3. 同时监控许多偏离时，除保守的族错误率（FWER）外，还可用 e-BH 控制错误发现率（FDR），用较宽松的错误目标换取更早检测。

### 3. 第一部分：重复标准型博弈中的“对均衡下注”

#### 3.1 输入、输出与假设

输入是每轮联合动作 $\mathbf a_t$，以及每个玩家 $i$ 的收益函数 $u_i$。收益先缩放到 $[0,1]$。论文假设各轮联合动作独立同分布地来自一个固定但未知的联合分布。

- 原假设 $\mathcal H_0$：该联合分布满足 Nash 均衡条件；
- 备择假设 $\mathcal H_1$：至少存在玩家 $i$ 和纯动作 $a_i'$，改成该动作能把期望收益提高至少 $\eta>0$。

$\eta$ 不能省略。若只说“不是精确均衡”，偏离可以无限小，任何方法都可能需要无限长时间才能可靠识别。

输出是一个报警时间，以及哪些“玩家—候选偏离动作”获得了足够证据。

#### 3.2 把可获利偏离变成逐轮证据

对每个玩家 $i$ 和纯偏离 $a_i'$，计算

$$
X_{i,t}^{(a_i')}=u_i(a_{i,t},a_{-i,t})-u_i(a_i',a_{-i,t}).
$$

它比较“实际动作的收益”和“保持对手动作不变、自己改成 $a_i'$ 的反事实收益”。

- 若处于均衡，长期看 $\mathbb E[X]\ge 0$；
- 若 $a_i'$ 是有利偏离，则 $\mathbb E[X]\le-\eta$。

选择下注比例 $\lambda\in(0,1]$，构造

$$
E_{i,t}^{(a_i')}(\lambda)=1-\lambda X_{i,t}^{(a_i')},
$$

再把逐轮证据相乘：

$$
M_{i,t}^{(a_i')}(\lambda)=\prod_{s=1}^{t}E_{i,s}^{(a_i')}(\lambda).
$$

均衡成立时，$M$ 是从 1 开始的非负超鞅；存在持续获利的偏离时，$X$ 经常为负，因而乘子 $1-\lambda X$ 经常大于 1，财富会增长。

#### 3.3 不知道偏离强度时怎么办？

最坏情形下的 Kelly 最优下注比例恰好为 $\lambda^*=\eta$。但实际监控时，$\eta$ 正是未知量。论文因此建议对多个下注比例做混合：

$$
M_{i,t}^{(a_i')}(\nu)=\int_0^1M_{i,t}^{(a_i')}(\lambda)\,d\nu(\lambda).
$$

超鞅的加权平均仍是超鞅，所以既保持有效性，又避免只押一个可能不合适的 $\lambda$。代码中的主要实验使用固定 $\lambda$ 或离散参数网格，并没有实现论文的连续均匀混合，这是理论与实验实现之间的一个边界。

#### 3.4 两种报警规则

一共有

$$
m=\sum_i|A_i|
$$

个“玩家—纯偏离”假设。

**FWER 规则。** 任意一个财富达到

$$
b_{\mathrm{FWER}}=\frac{m}{\alpha}
$$

就报警。Ville 不等式加 union bound 保证：均衡成立时，在任意时间至少出现一次假报警的概率不超过 $\alpha$。

**FDR 规则。** 当 $m$ 很大，FWER 会很保守。给每个假设权重 $\gamma_h$，满足权重和为 1。在每个时刻，用所有 **当前** e-value 找最大的 $k$，使至少 $k$ 个假设满足

$$
M_{h,t}\ge\frac{1}{k\alpha\gamma_h}.
$$

一旦 e-BH 首次产生非空拒绝集，所有过程在同一个全局时间停止。可选停止保证这些停止后的量仍是有效 e-value，随后 e-BH 控制错误发现比例的期望不超过 $\alpha$。均匀权重时，FDR 报警不会晚于相应的 FWER 报警。

这里有一个重要代码差异：当前 arXiv v3 使用“当前值 + 单一全局停止时刻”；`normal-form.ipynb` 却保存各过程的历史最大值和曾经越界的集合。历史最大值不会在证据回落时撤回，因此不是同一个统计量，论文对当前算法的 FDR 证明不能直接覆盖该 notebook 版本。

#### 3.5 标准型博弈流程

```text
每轮联合动作 + 完整收益表
          |
          v
对每个玩家、每个纯偏离计算反事实收益差 X
          |
          v
更新财富 M <- M * (1 - lambda * X)
（可对多个 lambda 混合）
          |
          +--------------------+
          |                    |
          v                    v
是否有 M >= m/alpha？      对所有当前 M 做 e-BH
          |                    |
          v                    v
       FWER 报警          全局 FDR 报警 + 偏离集合
```

### 4. 第二部分：随机博弈中的策略合规监控

#### 4.1 为什么不能直接检验均衡？

在随机博弈中，动作会改变下一状态。若要判断一次单边偏离是否提高长期折扣收益，就必须知道“如果当时采取别的动作，之后整条状态轨迹会怎样”。这需要反事实轨迹，通常不可直接观测。

因此论文把问题改成更可处理的 **策略合规检验**：不直接证明当前行为是不是均衡，而是检验智能体是否服从一个给定目标策略 $\pi$。该策略可以来自预先计算的均衡，也可以是其他安全/合规策略。

#### 4.2 用策略似然比积累证据

对玩家 $i$，目标策略为 $\pi_i$，候选偏离为 $\pi_i^{(1)}$。看到状态 $s_t$ 和动作 $a_{i,t}$ 后，计算

$$
E_{i,t}=\frac{\pi_i^{(1)}(a_{i,t}\mid s_t)}{\pi_i(a_{i,t}\mid s_t)},
\qquad
M_{i,t}=\prod_{r=1}^{t}E_{i,r}.
$$

若智能体确实服从 $\pi_i$，条件期望为 1，所以 $M$ 是鞅。若行为更像 $\pi_i^{(1)}$，对数财富会以状态平均 KL 散度决定的速率增长。直观上，目标策略极少产生、但偏离策略经常产生的动作，会带来较大的正证据。

若不知道偏离的具体参数，可维护多个候选似然比鞅再取加权平均。Predator-Prey 实验就对 5 个候选 $\varepsilon$ 取算术平均。

#### 4.3 随机博弈流程

```text
状态 s_t + 智能体动作 a_i,t
            |
            v
计算目标策略概率 pi_i(a_i,t | s_t)
和候选偏离概率 pi_i^(1)(a_i,t | s_t)
            |
            v
似然比 E = 偏离概率 / 目标概率
            |
            v
累计 M <- M * E
（未知偏离时平均多个候选 M）
            |
            v
超过阈值 -> 策略偏离报警
```

### 5. 实验怎样验证方法？

#### 5.1 $2\times2$ 标准型博弈

300 次模拟中，论文报告 FWER 平均停止时间为 1765 轮，FDR 为 1546 轮，FDR 约快 $1.15\times$。图中 FDR 的直方图和累计检测曲线明显左移。空假设下的参数扫描中，12 个 $\lambda$/$\alpha$ 组合的经验 FWER 都低于名义水平。

#### 5.2 20 人群体剪刀石头布

20 个玩家、每人 3 个动作，共监控 60 个假设。平均停止时间从 FWER 的 2025 轮降至 FDR 的 1248 轮。若先用独立的 50 轮筛选窗口选出 10 个候选，再开始正式检验，split-FWER 和 split-FDR 分别降至 1438 和 802 轮。

一个容易误读的结果是：报警主要落在仍使用均匀策略的玩家上，而不是偏向石头的 5 个玩家上。这是合理的——石头偏多改变了群体环境，使其他玩家“改出布”成为有利偏离。检验定位的是被破坏的激励约束，不是导致分布偏移的责任人。

#### 5.3 Grid Soccer

代码用逐状态线性规划求近似极小极大策略，并加入 5% 均匀噪声以保证所有动作概率为正；否则某些似然比会变成无穷大。偏离策略人为压低向球门前进的 East 概率，形成“胆怯”进攻者。检测时间随混合强度 $\varepsilon$ 呈约 $1/\varepsilon^2$ 下降。

#### 5.4 Predator-Prey

目标不是 Nash 均衡，而是均匀随机游走；候选偏离更倾向朝猎物移动。监控器不知道真实 $\varepsilon$，用 5 个候选强度的混合仍得到接近 $1/\varepsilon^2$ 的曲线。影片图中，嫌疑捕食者持续追逐猎物，财富在第 8 步从 15.38 跳到 30.20，超过阈值 20。

两个随机博弈图中的理论虚线都用最大 $\varepsilon$ 的经验点来定比例常数。因此它们支持“斜率/阶数相符”，不能解释为无拟合参数的绝对时间预测。

### 6. 如何正确解释报警？

- 报警说明某个反事实纯动作看起来可获利，或实际动作序列更像候选偏离策略。
- 它不证明智能体有主观意图，也不直接证明串谋或因果责任。
- 在随机博弈中，它证明的是相对给定策略的合规偏离，不是重新求解并否定 Nash 均衡。
- 财富可以在越过阈值后回落；有效结论依赖停止规则，而不是把分数当作单调风险指标。

### 7. 适用边界与复现状态

主要理论边界包括：标准型博弈要求固定、i.i.d. 联合策略；需要所有纯偏离的反事实收益；随机博弈需要完整目标策略概率和支撑条件；对错误目标策略、依赖数据和非平稳漂移的稳健保证未给出。

官方代码快照只有三个 notebook。核心更新、阈值、策略平滑和离散混合都能从源码对应到论文，但没有依赖版本、环境文件、测试、CLI、自动化运行脚本或完整输出契约。综合忠实度为 **中等**：FWER 与似然比主干较吻合，FDR notebook 与当前 v3 算法存在实质差异。复现实验前应先修正该 FDR 实现，并补充可固定版本的运行环境。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Anytime Detection of Strategic Deviations in Multi-Agent Systems

### Problem

Multi-agent behavior is often evaluated after collecting a fixed dataset, but a deployed system needs to be monitored continuously. Repeatedly applying ordinary fixed-sample tests as more rounds arrive invalidates their error guarantees. This paper develops an anytime-valid framework that can raise an alarm at a data-dependent time while controlling false positives.

The current archival identity is arXiv `2601.05427v3`, by Etienne Gauthier, Francis Bach, and Michael I. Jordan. “Betting on Equilibrium: Monitoring Strategic Behavior in Multi-Agent Systems” is an earlier/listing-title alias. A conference venue is not established by the acquired arXiv metadata; the supplied ICML 2026 label remains unverified.

### Proposed method

For repeated normal-form games, the benchmark is equilibrium. For every player and pure unilateral deviation, the method computes the payoff difference between the observed action and its counterfactual deviation. It converts that bounded regret-like increment into a multiplicative e-process. Under equilibrium, the process is a nonnegative supermartingale; under a profitable deviation, it tends to grow. Crossing $m/\alpha$, where $m$ is the number of monitored player/action hypotheses, gives an anytime-valid FWER alarm. Mixing betting fractions avoids needing to know the deviation margin $\eta$ and yields an expected detection-time bound of order $\eta^{-2}$ up to logarithmic factors.

To improve power when many deviations are monitored, the paper applies e-BH to all **current** e-values and stops them at the first shared time when at least one rejection appears. This controls FDR and, with uniform hypothesis weights, alarms no later than the conservative FWER rule.

For stochastic games, direct equilibrium verification would require counterfactual state trajectories. The paper therefore monitors compliance with a specified state-dependent target policy. Each observed action contributes a likelihood ratio between an alternative policy and the target; their product is a martingale under compliance. Its log-growth under deviation is governed by a state-averaged KL divergence. Mixtures over alternative policies preserve validity when the deviation magnitude is unknown.

### Evaluation

- In a $2\times2$ normal-form simulation with 300 runs, the paper reports mean stopping times of 1765 rounds for FWER and 1546 for FDR, about a $1.15\times$ FDR speedup. Null simulations remain below the tested nominal error levels.
- In a 20-player population Rock-Paper-Scissors experiment with 60 hypotheses, mean stopping time falls from 2025 (FWER) to 1248 (FDR); a held-out screening window further reduces it to 1438 (split-FWER) and 802 (split-FDR).
- Grid Soccer uses a smoothed computed minimax policy as the target and a timid “afraid” policy as the alternative. Predator-Prey uses a uniform random walk as the target and a finite mixture of chasing alternatives. Both show detection-time curves compatible with $O(1/\varepsilon^2)$ scaling.

These are synthetic simulations. The dashed stochastic scaling curves are normalized to the final empirical point, so they validate rate shape rather than a parameter-free prediction of absolute detection time.

### What is new relative to prior testing

The framework replaces fixed-sample equilibrium tests such as Babichenko et al. (2017) with safe sequential monitoring, does not require knowing the equilibrium joint strategy in the payoff-based normal-form construction, and extends the template to coarse correlated, correlated, and approximate equilibria. It also introduces FDR control for a fixed collection of continuously updated strategic-deviation hypotheses and provides a tractable policy-compliance monitor for stateful games.

### Assumptions and limitations

- Normal-form play is modeled as i.i.d. draws from a fixed joint distribution, which excludes adaptive learning, dependence, and drift unless the method is extended.
- The payoff-based test needs every counterfactual pure-deviation payoff. The stochastic test instead needs exact target-policy probabilities and adequate support.
- A rejection identifies an incentive violation or policy mismatch, not intent, collusion, causal responsibility, or direct equilibrium failure in a stochastic game.
- Practical mixture-weight selection, robustness to an incorrect target policy, and guarantees under dependent/nonstationary play are not specified.
- Experiments cover designed games rather than real deployed multi-agent systems.

### Reproducibility and code-paper fidelity

The official commit `42b8f0edfe76fb9dd006e9cab84f6cb8b75849c6` contains three notebooks for normal form, Soccer, and Predator-Prey. Direct source reads confirm the core regret update, FWER threshold, stochastic likelihood ratio, policy smoothing, and discrete alternative mixture. However, the repository has no dependency lockfile, installation instructions, automated tests, command-line runner, or pre-created result/output contract, so reproducibility is notebook-level and partial.

Overall code-paper fidelity is **medium**. The most important discrepancy is in `normal-form.ipynb`: its FDR experiment tracks running maxima and hypotheses that have ever crossed thresholds, whereas current arXiv v3 applies e-BH to current values at one global stopping time. The notebook result is therefore not an exact implementation of the theorem's procedure. The notebooks also use fixed betting fractions rather than the paper's continuous $\lambda$ mixture, and the two theoretical scaling guides are empirically anchored. See `doc_code.md` for the line-level map.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
