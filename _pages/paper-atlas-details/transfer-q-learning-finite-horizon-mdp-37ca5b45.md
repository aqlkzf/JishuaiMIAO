---
layout: default
permalink: /paper-atlas/transfer-q-learning-finite-horizon-mdp-37ca5b45/
title: "Transfer_Q_Learning_Finite_Horizon_MDP"
nav: false
description: "目标任务只有少量轨迹，但我们拥有若干相关源 MDP 的离线轨迹。论文希望利用源数据更准确地估计目标任务各阶段的最优 Q^ 函数，并覆盖两种情形：目标任务也是离线数据，以及目标任务需要在线探索。 困难在于，强化学习的回归标签不是直接观测值。阶段 t 的 Bellman 标签依赖下一阶段的 Q^。如果直接把源任务自己的伪标签与目标数据混合，源任务使用的是 Q{t+1}^{(k)}，目标任务使用的是 Q{t+1}^{(0)}；"
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
      <span>Electronic Journal of Statistics · 2025</span>
    </div>
    <h1>Transfer_Q_Learning_Finite_Horizon_MDP</h1>
    <p>Transfer Q-learning for finite-horizon Markov decision processes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1214/25-EJS2459" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 有限时域 MDP 的迁移 $Q^*$ 学习

### 论文解决什么问题？

目标任务只有少量轨迹，但我们拥有若干相关源 MDP 的离线轨迹。论文希望利用源数据更准确地估计目标任务各阶段的最优 $Q^*$ 函数，并覆盖两种情形：目标任务也是离线数据，以及目标任务需要在线探索。

困难在于，强化学习的回归标签不是直接观测值。阶段 $t$ 的 Bellman 标签依赖下一阶段的 $Q^*$。如果直接把源任务自己的伪标签与目标数据混合，源任务使用的是 $Q_{t+1}^{*(k)}$，目标任务使用的是 $Q_{t+1}^{*(0)}$；两者的差异会产生额外偏差，并沿反向递推逐级累积。

### 核心创新：re-targeting

对源任务 $k$ 的一次转移，不使用源任务自己的未来价值，而统一使用目标任务的下一阶段估计：

$$
\widehat y_{t,i}^{(tl-k)}
=r_{t,i}^{(k)}+\gamma\max_a\widehat Q_{t+1}^{(0)}(s_{t+1,i}^{(k)},a).
$$

这样处理后，源伪标签与目标 $Q_t^{*(0)}$ 之间只剩当前阶段的奖励差异 $D_t^{(k)}$，不再包含源、目标未来 $Q^*$ 不一致造成的额外项。重要的是，论文并没有假设 $Q_t^{*(k)}$ 与 $Q_t^{*(0)}$ 本身接近。

### 算法流程

```text
目标轨迹 + 多个源任务轨迹
          |
从 t=T 向 t=1 反向递推
          |
目标数据：用目标 Qhat_(t+1) 构造伪标签
源数据：  用同一个目标 Qhat_(t+1) 重新定向标签
          |
源数据拟合公共部分（样本多）
          |
目标数据拟合小的任务差异并去偏（样本少）
          |
得到目标 Qhat_t，再进入前一阶段
          |
输出目标 greedy policy
```

在线版本采用 Explore-Transfer-Then-Commit：先在目标 MDP 中探索 $n_e$ 个 episode，再把这些目标数据与离线源数据交给上述迁移估计器，随后执行 greedy 策略。

### 理论解释

在线性 $Q^*$、稀疏参数和相容设计条件下，阶段误差包含三部分：下一阶段传来的误差、用全部源样本估计公共部分的 $s\log p/N_{\rm src}$，以及用目标样本估计任务差异的 $h\sqrt{\log p/n_0}$。单任务当前阶段需要承担 $s\log p/n_0$，因此当源样本远多于目标样本且奖励差异 $h$ 足够小时，迁移可以更快。

在线 regret 上界同样分成探索成本、源估计误差和任务差异误差。论文给出了迁移优于单任务的充分条件，但这不是无条件保证。

### 是否避免 negative transfer？

不能自动避免。论文没有提供自动筛除有害源任务的算法，也没有“任何来源下不差于 target-only”的 oracle 保证。当奖励差异很大、源目标协方差不相容或转移机制显著变化时，优势可能消失。未知相似度下的源选择与模型聚合被列为未来工作。

### 实验与边界

两阶段合成实验中，迁移方法降低了参数和 $Q^*$ 预测误差，并提高正确动作比例；在线模拟中 regret 更低。MIMIC-III 示例把女性轨迹视为源、样本较少的男性轨迹视为目标，迁移方法的估计聚合价值平均较高。但这是回顾性方法展示，论文明确没有开展严谨医学分析，因此不能解释为治疗效果或临床部署证据。

论文所称代码在线可用，但 TeX 中唯一可识别的官方仓库地址在 2026-07-22 返回 404；没有找到可核验的替代实现，所以本工作区为 paper-only。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Transfer Q-learning for finite-horizon Markov decision processes

### Problem and contribution

Chen, Li, and Jordan study how to estimate the target task's optimal action-value functions in a time-inhomogeneous finite-horizon MDP when target trajectories are scarce but offline trajectories from related source MDPs are available. Directly pooling ordinary source Bellman pseudo-responses is unsafe: each source response bootstraps with its own future $Q^{*(k)}$, so differences in future values create a stage-by-stage bias that need not be small even when immediate rewards are similar.

The paper's key device is **re-targeting**. At stage $t$, every source transition is labeled using the current estimate of the *target* next-stage value,

$$
\widehat y^{(tl-k)}_{t,i}=r^{(k)}_{t,i}+\gamma\max_a\widehat Q^{(0)}_{t+1}(s^{(k)}_{t+1,i},a).
$$

This removes the source-versus-target future-value mismatch from the population moment; the remaining contrast is the stage-wise reward discrepancy $D_t^{(k)}$. A supervised transfer-regression block then pools the abundant source labels to learn a common component and uses target data to estimate and subtract the small bias. Backward induction repeats this from $T$ to 1, creating both cross-task transfer and a positive cross-stage cascade.

### Assumptions and guarantees

The general framework permits multiple source tasks and either an offline or online target. Formal rates are for sparse linear $Q^*$ approximation with common state-action features, approximately sparse reward-contrast coefficients, compatible design covariances, and sufficient source/target sample sizes. Theorem 4.2 gives the stagewise error recursion

$$
\|\widehat\theta_t^{(0)}-\theta_t^{(0)}\|_2^2
\lesssim
\|\widehat\theta_{t+1}^{(0)}-\theta_{t+1}^{(0)}\|_2^2
+\frac{s\log p}{N_{\rm src}}+h\sqrt{\frac{\log p}{n_0}},
$$

up to the paper's design conditions. This replaces the single-task current-stage term $s\log p/n_0$ by a source-learned common term and a target-learned contrast term. For offline-to-online transfer, Explore-Transfer-Then-Commit uses $n_e$ target exploration episodes, calls the offline transfer estimator, then acts greedily. Theorem 4.3 bounds regret by exploration cost plus $N-n_e$ times source-estimation and task-contrast errors; the comparison is favorable under explicitly stated high-similarity and source-sample regimes.

These are **conditional positive-transfer guarantees, not a general negative-transfer safeguard**. Large reward discrepancy $h$ or strong transition/design shift can erase the advantage, and the method does not automatically select or reject harmful source tasks. The paper names aggregation/source selection for unknown similarity as future work.

### Evidence and evaluation

- In a two-stage synthetic MDP ($p=100$, target sparsity 7), transfer lowers coefficient and relative $Q^*$ prediction errors at both stages, with the largest gain at the earlier stage; correct-action frequency rises from 0.555–0.905 for target-only learning to 0.965–1.000 across the reported source-sample configurations.
- In online simulations, transferred policies have visibly lower cumulative regret across exploration lengths and learning phases.
- In the MIMIC-III illustration, female trajectories are used as the source and the smaller male subgroup as the target. The learned aggregate-value ratio is mostly above one, but the authors explicitly state that rigorous medical analysis is outside scope; this is not clinical validation or causal treatment evidence.

### Reproducibility and limitations

The analyzed source is arXiv `2202.04709v2`, matching the 2025 EJS article (volume 19, issue 2, pages 5289–5312; DOI `10.1214/25-EJS2459`). Project Euclid was protected by Incapsula. The arXiv manuscript integrates the supplement and its source archive provides the six main figures. The manuscript says code is online, but its only identifiable official URL, `https://github.com/ElynnCC/TransferQLearning`, is commented in the TeX and returned 404 on 2026-07-22; no matching official replacement was found. Consequently this is a **paper-only** analysis, and empirical reproduction is blocked by missing public code and processed data.

Other boundaries are important: all formal theory is for the linear instantiation, not the full plug-in function-class framework; transition transfer is discussed but not theoretically solved; common horizon/action/feature assumptions exclude several forms of task heterogeneity; and unknown source similarity can cause negative transfer.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
