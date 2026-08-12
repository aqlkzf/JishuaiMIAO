---
layout: default
permalink: /paper-atlas/sample-complexity-online-reinforcement-learning-multi-model-4a077daa/
title: "Sample_Complexity_Online_Reinforcement_Learning_Multi_Model"
nav: false
description: "论文研究连续状态、连续动作、不能重置环境的在线强化学习。真实动力学未知： 学习者一边施加控制，一边从连续轨迹中识别系统。动作既影响当前代价，也决定未来状态以及能够获得多少辨识信息，因此普通的独立同分布统计分析或回合式 RL 分析不能直接使用。论文要控制的是相对于真实动力学对应策略的 policy regret，同时还要保证闭环状态不会因为早期选错模型而失控。"
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
      <span>International Conference on Learning Representations (ICLR) · 2026</span>
    </div>
    <h1>Sample_Complexity_Online_Reinforcement_Learning_Multi_Model</h1>
    <p>The Sample Complexity of Online Reinforcement Learning: A Multi-model Perspective</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2501.15910" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多模型视角下在线强化学习的样本复杂度

### 这篇论文解决什么问题？

论文研究连续状态、连续动作、不能重置环境的在线强化学习。真实动力学未知：

$$
x_{k+1}=f(x_k,u_k)+n_k.
$$

学习者一边施加控制，一边从连续轨迹中识别系统。动作既影响当前代价，也决定未来状态以及能够获得多少辨识信息，因此普通的独立同分布统计分析或回合式 RL 分析不能直接使用。论文要控制的是相对于真实动力学对应策略的 **policy regret**，同时还要保证闭环状态不会因为早期选错模型而失控。

### 核心想法

作者把问题拆成两个相对独立的模块：

1. **在线模型辨识**：根据一步预测误差维护候选动力学的 softmax/后验分布；
2. **确定性等价控制**：抽到哪个候选模型，就调用为该模型预先求得的控制策略。

为了让不同模型真正可区分，控制动作中还加入随时间衰减的高斯扰动。完整循环是：

```text
候选动力学 + 每个候选的控制策略
              ↓
累计每个模型的一步预测误差
              ↓
按 exp(-η × 误差) 抽取一个模型
              ↓
连续 M 步使用该模型的确定性等价策略
              ↓
叠加衰减高斯激励，执行动作并观察下一状态
              ↺
```

### 第一步：用预测误差形成候选模型权重

有限候选集 $F=\{f^1,\ldots,f^m\}$ 中，第 $i$ 个模型的累计分数为

$$
s_k^i=\sum_{j=1}^{k-1}
\frac{\lvert x_{j+1}-f^i(x_j,u_j)\rvert^2}
{1+\lvert(x_j,u_j)\rvert^2/b^2}.
$$

分子是在真实轨迹上的一步预测误差；高斯过程噪声下，它可以看作负对数似然。分母用于限制大状态、大动作对分数的影响，使稳定性与遗憾分析更容易。每隔 $M$ 步按

$$
\Pr(i_k=i\mid\mathcal F_{k-1})
=\frac{\exp(-\eta s_k^i)}{\sum_q\exp(-\eta s_k^q)}
$$

抽取一个候选。$\eta\approx1$ 时接近后验采样；$\eta$ 很大时接近最大后验模型；从在线学习角度又相当于 Hedge/乘法权重更新。

这里不能简单照搬普通 Hedge 的证明，因为模型选择会改变动作，动作会改变之后访问的状态，随后又会改变模型辨识数据。

### 第二步：调用候选模型的策略

抽到模型 $i_k$ 后执行

$$
u_k=\mu^{i_k}(x_k)+n_{uk},
\qquad n_{uk}\sim\mathcal N(0,\sigma_{uk}^2I).
$$

$\mu^{i_k}$ 是为候选动力学 $f^{i_k}$ 设计的确定性等价策略，可以来自动态规划、MPC，或离线仿真中的 PPO。它不必严格全局最优，但必须具有有限稳态性能并满足论文的平滑性/稳定性假设。这个分离原则避免了每一步都构造置信集、再求一个“最乐观”策略；代价是需要为所有可能被抽到的模型准备策略。

### 第三步：持续激励为什么关键？

如果闭环轨迹从不访问能够区分两个模型的区域，预测误差再精确也无法辨识。论文因此假设存在 $M$ 与分离常数 $\Delta>0$，使任意错误模型在一个 $M$ 步窗口中的期望归一化偏差至少为 $\Delta\sigma_u^2$。高斯扰动负责提供辨识信号，但“加入噪声”本身不自动证明这个条件；persistent excitation 仍是需要检查的结构假设。

在指定的衰减方差下，错误模型被选中的概率满足

$$
\Pr(i_k\neq i^*)\leq\frac{M^2}{(k-M)^2}.
$$

因为 $1/k^2$ 可求和，早期选错模型带来的累计影响有限；而激励方差的累计和只按对数增长，这正是有限候选情况下得到对数遗憾的原因。

### 第四步：怎样从辨识误差得到控制遗憾？

作者使用一个满足 Bellman 型不等式的 cost-to-go/storage function $V$。在每一步中把期望分成两种情况：选中真实模型和选中错误模型。选对时，$V$ 按 Bellman/耗散关系受控；选错时，$V$ 可能放大，但该事件的概率快速下降。对时间求和以后，policy regret 主要由两项控制：

$$
\sum_k\sigma_{uk}^2
\quad\text{和}\quad
\sum_k\Pr(i_k\neq i^*).
$$

第一项刻画探索成本，第二项刻画误识别成本。若阶段代价从下方控制 $\lvert x\rvert^2$，相同的 Lyapunov 分析还能给出状态二阶矩的一致上界。

### 三种模型类与结论

#### S1：有限个候选模型

在平滑性、Bellman 型耗散和持续激励等条件下，主要阶数为

$$
R_N=O\!\left(
\frac{d_u\ln N}{\Delta}
+\frac{d_u\ln m}{\Delta}
+\sigma^2d_x
\right).
$$

它对时间跨度 $N$ 和候选数 $m$ 都是对数依赖，但会随模型难以区分（$\Delta$ 小）而恶化。

#### S2：有界的无限函数类

算法在线构造 $\epsilon$-packing，把无限类用至多 $m(\epsilon)$ 个代表模型覆盖，再使用有限候选分析。遗憾中出现

$$
N\epsilon^2+
\frac{d_u\ln N}{\epsilon^2}+
\frac{d_u\ln m(\epsilon)}{\epsilon^2}.
$$

$\epsilon$ 控制近似误差与模型类复杂度之间的权衡。这更像一般性的“可学习性”结果：任意函数类的在线 packing、后验抽样以及逐模型求策略未必具有实际可计算性。

#### S3：紧致的 $p$ 维参数模型

连续参数按

$$
p_k(\theta)\propto\exp(-\eta s_k(\theta))
\mathbf 1\{\theta\in\Omega\}
$$

抽样。若动力学对参数线性，$f_\theta(x,u)=\phi(x,u)^\top\theta$，这个分布是截断高斯；均值是加权最小二乘解，协方差来自加权特征 Gram 矩阵的逆，因此可以递归最小二乘更新。主要结论为

$$
R_N=\widetilde O(\sqrt{d_uNp}).
$$

论文提到神经网络和 Transformer，是因为它们属于参数化函数族；这不表示论文实际训练或实验验证了这些架构。一般非线性参数化还需要 MCMC 等方法抽后验，并且为每个抽样模型求控制策略可能才是计算瓶颈。

### 实验说明了什么？

作者展示了两个仿真族：20 维线性系统，以及带小车的非线性倒立摆。有限模型算法在线性系统中大约 25 步达到接近最优的稳态行为；连续参数版本有明显更大的瞬态峰值，大约 60 步后才接近参考状态尺度。候选数从 10 增加到 10,000 时，稳态状态轨迹仍较接近。

倒立摆实验用 500 个候选模型和约束 MPC；真实参数并不在候选集中。学习控制器约在第 80 步完成摆起，真实模型控制器约在第 60 步完成。后验集中到一组近似模型，而不是唯一真实模型。六幅编号图及其所有面板均已直接查看；它们支持“在所选仿真中可行且瞬态可接受”，但不能单独验证理论阶数。

### 理解时最重要的边界

- 这是在线 RL、控制理论与系统辨识论文，不是生信论文。
- 持续激励、平滑策略、Bellman/耗散结构以及可用的候选策略都是核心条件。
- S2 的广泛函数类结论主要回答统计可学习性，不保证普遍可部署。
- 任意模型错设不被保证；附录要求存在一个全局一致的最近模型。
- 未找到官方实现代码、实验数据、随机种子或完整 MATLAB 配置，因此数值结果无法从公开制品独立复现。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## The Sample Complexity of Online Reinforcement Learning: A Multi-model Perspective

### Paper identity

Michael Muehlebach, Zhiyu He, and Michael I. Jordan. Published as a poster at the Fourteenth International Conference on Learning Representations (ICLR 2026). The source analyzed here is arXiv `2501.15910v4`; `10.48550/arXiv.2501.15910` is the arXiv DOI, and no separate publisher DOI was found.

### Problem

The paper asks how quickly an agent can learn to control an unknown nonlinear dynamical system in a continuous-state, continuous-action, non-episodic setting. The system cannot be reset, so actions simultaneously incur cost, change future states, and determine how informative later observations will be. The target is a frequentist, nonasymptotic policy-regret guarantee together with closed-loop state control, not merely accurate one-step prediction.

### Why existing approaches are insufficient

Posterior-sampling RL had mostly yielded Bayesian guarantees or results tailored to tabular, episodic, mixing, or linear settings. Optimism-based algorithms maintain confidence sets and repeatedly solve for an optimistic policy, which can be computationally burdensome and difficult to characterize for broad nonlinear classes. Adaptive-control results often emphasize asymptotic stability rather than finite-time performance. This work combines posterior/Hedge-style model selection, system-identification excitation, and control-theoretic dissipativity to address those gaps under explicit assumptions.

### Proposed method

For every candidate dynamics model, the learner accumulates a normalized squared one-step prediction error. Every $M$ steps it samples a model with probability proportional to $\exp(-\eta s_k)$, keeps that model during the block, applies its certainty-equivalent feedback policy, and adds decaying Gaussian action noise. The softmax distribution can be read as a tempered posterior or a multiplicative-weights update. Persistent excitation ensures that wrong models become distinguishable; a Bellman-type/Lyapunov argument then converts rapidly vanishing wrong-model probability into policy regret.

The framework covers three model classes:

- **S1, finite candidates:** regret is logarithmic in horizon $N$ and candidate count $m$, scaled by inverse model separation $1/\Delta$.
- **S2, bounded infinite classes:** an online $\epsilon$-packing reduces the problem to finite candidates, giving a tradeoff between approximation $N\epsilon^2$ and packing complexity $\ln m(\epsilon)/\epsilon^2$.
- **S3, compact $p$-parameter classes:** continuous posterior sampling gives $\widetilde O(\sqrt{d_uNp})$ policy regret. For linear-in-parameter dynamics, the posterior is truncated Gaussian and can be updated by recursive least squares.

The guarantees require realizability or a uniformly closest model, smooth/Lipschitz policies and value structure, a Bellman/dissipativity condition, and persistent excitation. Mentioning neural networks and transformers in S3 does not mean the paper empirically trains them; they are examples of parametric dynamics families covered conditionally by the theorem.

### Evidence and evaluation

Two simulation families illustrate the algorithms. A 20-state, 5-input linear system compares finite-model Algorithm 1 and continuous-parametric Algorithm 3; finite-model identification reaches near-optimal behavior in about 25 steps, while the parametric variant has a much larger transient and approaches the optimal state scale around 60 steps. Scaling finite candidates from 10 to 10,000 changes the regret level but produces nearly overlapping state trajectories after the initial transient.

A nonlinear pendulum-on-cart experiment uses 500 misspecified candidate models and a 50-step constrained MPC policy for each sampled model. The learned controller swings the pendulum upright around iteration 80 versus around 60 with the true model, and posterior/model estimates settle within roughly 100 steps. All six numbered figures and their constituent panels were inspected directly; they support feasibility and transient behavior, not a comprehensive benchmark or direct empirical verification of the asymptotic rates.

### Reproducibility and limitations

**Reproducibility: 2/5 (paper description only).** The paper provides equations, algorithms, assumptions, numerical dimensions, controller construction, and several hyperparameters, but no official implementation repository or downloadable experiment data was found after checking the paper, arXiv, ICLR/OpenReview, author pages, and focused title/GitHub searches. The authors state that experiments were implemented in MATLAB, using `dlqr`, IPOPT, and CasADi; exact scripts, seeds, sampled candidate sets, and full configurations are unavailable.

The main conceptual limitation is that persistent excitation and stable certainty-equivalent policies are assumed rather than automatically produced for arbitrary nonlinear models. S2 is primarily a learnability result because online packing and per-model policy construction can be intractable. The numerical evidence is limited to two simulated control families and has no competing-method comparison. The formal misspecification extension requires one candidate to be uniformly closest in a strong geometric sense.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
