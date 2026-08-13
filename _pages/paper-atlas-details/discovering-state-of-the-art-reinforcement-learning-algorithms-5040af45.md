---
layout: default
permalink: /paper-atlas/discovering-state-of-the-art-reinforcement-learning-algorithms-5040af45/
title: "Discovering_State_of_the_Art_Reinforcement_Learning_Algorithms"
nav: false
wide: true
description: "传统强化学习（RL）通常由人手工决定：智能体应该预测什么、预测目标是什么、策略如何更新，以及不同损失如何组合。已有的自动发现方法往往只搜索少量超参数或局部损失，在简单环境中元学习，容易过拟合，难以替代复杂的手工 RL 系统。本文的目标是让机器直接从大量智能体在复杂环境中的交互经验中，发现一条可以迁移到新环境的 RL 更新规则。 DiscoRL 不让元网络输出一个标量损失，而是让它根据轨迹生成“智能体应该靠近的目标”。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>Discovering_State_of_the_Art_Reinforcement_Learning_Algorithms</h1>
    <p>Discovering state-of-the-art reinforcement learning algorithms</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/google-deepmind/disco_rl" target="_blank" rel="noopener noreferrer" aria-label="Open code for Discovering_State_of_the_Art_Reinforcement_Learning_Algorithms">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DiscoRL：自动发现强化学习算法的方法解释

### 这篇论文要解决什么问题？

传统强化学习（RL）通常由人手工决定：智能体应该预测什么、预测目标是什么、策略如何更新，以及不同损失如何组合。已有的自动发现方法往往只搜索少量超参数或局部损失，在简单环境中元学习，容易过拟合，难以替代复杂的手工 RL 系统。本文的目标是让机器直接从大量智能体在复杂环境中的交互经验中，发现一条可以迁移到新环境的 RL 更新规则。

### DiscoRL 的核心想法

DiscoRL 不让元网络输出一个标量损失，而是让它根据轨迹生成“智能体应该靠近的目标”。智能体除了策略 $\pi$ 外，还输出两类不预先规定语义的预测：观测条件预测 $y(s)$ 和动作条件预测 $z(s,a)$。同时保留有明确语义的动作价值 $q(s,a)$ 与辅助策略预测 $p(s,a)$，避免元学习重新发现这些基础组件。$y$、$z$ 的语义由训练结果决定，因此可以表示价值、奖励、未来事件或新的任务相关量，而不局限于某个手工定义。

### 计算流程

```text
多个环境 + 多个智能体
        |
        v
收集轨迹：动作、奖励、终止标记，以及 π、y、z、q、p
        |
        v
对动作条件输入做共享编码，并构造选中动作/动作平均等特征
        |
        v
按环境时间反向运行轨迹 LSTM
按智能体更新次数正向运行 lifetime meta-RNN
        |
        v
输出目标：π_hat、y_hat、z_hat
        |
        v
智能体最小化 KL(目标, 当前输出)
并加入辅助策略损失和 q 的分类价值损失
        |
        v
经过多次智能体更新后，沿更新过程反向传播元梯度
        |
        v
聚合不同环境/智能体的元梯度，更新元网络参数 η
```

论文给出的智能体目标为

$$L(\theta )=&#123;&#123;\mathbb{E}}}_{s,a\sim &#123;&#123;\boldsymbol{\pi }}}_{\theta }}[D(\hat&#123;&#123;\boldsymbol{\pi }}},&#123;&#123;\boldsymbol{\pi }}}_{\theta }(s))+D(\hat&#123;&#123;\bf{y}}},&#123;&#123;\bf{y}}}_{\theta }(s))+D(\hat&#123;&#123;\bf{z}}},&#123;&#123;\bf{z}}}_{\theta }(s,a))+{L}_&#123;&#123;\rm{a}}{\rm{u}}{\rm{x}}}].$$

其中 $D$ 使用 KL 散度。辅助项将 Retrace 产生的动作价值目标投影到 two-hot/分类表示，并令辅助策略预测逼近下一时刻策略。代码中的 `DiscoUpdateRule.agent_loss` 对策略、$y$、执行动作对应的 $z$ 计算分类 KL，再加入终止状态屏蔽的 one-step 辅助策略 KL（`disco_rl/update_rules/disco.py:225-294`）。$q$ 的 TD/分类损失在独立的 `agent_loss_no_meta` 中计算（同文件 `296-323`）。

元优化目标是不同环境和智能体回报的期望：

$$J(\eta )=&#123;&#123;\mathbb{E}}}_&#123;&#123;\mathcal{E}}}&#123;&#123;\mathbb{E}}}_{\theta }[J(\theta )],\qquad
{\nabla }_{\eta }J(\eta )\approx &#123;&#123;\mathbb{E}}}_&#123;&#123;\mathcal{E}}}&#123;&#123;\mathbb{E}}}_{\theta }[{\nabla }_{\eta }\theta {\nabla }_{\theta }J(\theta )].$$

论文通过多次内层智能体更新、20 步滑动反向传播窗口和 discovery-only meta-value function 估计这个梯度。大规模训练还使用优势归一化、按智能体分别 Adam 后再平均、预测熵正则和目标策略 KL 正则来稳定元优化。

### 为什么要用两个 LSTM？

环境时间上的 LSTM 读取从 $t$ 到未来的轨迹，并反向展开，所以当前目标可以依赖未来预测，形成 bootstrapping。跨智能体生命周期的 meta-RNN 则在每次 agent update 后更新一次，能够记住奖励尺度、奖励稀疏性和 episode 长度等学习动态。代码中，轨迹 LSTM 位于 `disco_rl/networks/meta_nets.py:109-117`，meta-RNN 的状态更新与批次平均嵌入位于 `160-226`。

动作条件输入/输出使用跨动作共享权重，并对动作维度做平均嵌入，因此元网络参数量不随动作数增加；这解释了它为何可以迁移到不同离散动作空间。元网络只看智能体输出，不直接看观测，从而减少环境依赖，但也意味着它不能直接发现像像素控制、观测模型或逆动力学这样的规则。

### 论文报告的结果

- Disco57 在 57 个 Atari 游戏上发现，论文报告 Atari IQM 为 13.86，并超过所列 MuZero、Dreamer、STACX、IMPALA、DQN、PPO 等手工规则。
- 在从未用于 Disco57 发现的 ProcGen、Crafter、NetHack、Sokoban 上，规则仍有竞争力；NetHack 达到 NeurIPS 2021 挑战赛第三名，且没有使用领域特定子任务或奖励塑形。
- Disco103 使用 Atari、ProcGen、DMLab-30 共 103 个环境发现，Atari 表现相近，但其他已见和未见基准更强。
- 图 4 的探针分析显示，$y/z$ 包含未来策略熵和大回报事件的信息；扰动未来 $z_{t+k}$ 会改变当前 $\hat z_t$，说明存在 bootstrapping。去掉 bootstrapping 或完全去掉预测都会显著降低表现。

### 如何理解代码证据？

当前仓库（commit `9059a29f7121d60948f25ef165e08e050e9399c8`）确认了 DiscoRL 的输出规格、输入变换、反向轨迹 LSTM、lifetime meta-RNN、KL/价值损失、目标参数 EMA 和通用 learner step。`Agent.learner_step` 的静态路径是：先调用 `unroll_meta_net` 产生目标，再计算损失和梯度，最后应用优化器更新参数（`disco_rl/agent.py:248-316`）。

但这不是运行时复现实验：本地没有验证 TPU 大规模 population 调度、MixFlow-MG、完整 replay/reset 方案或 Nature 图中曲线。因此“代码实现了接口和核心计算”与“代码重现了论文性能”必须分开表述。补充 PDF 已被直接阅读，但尚未生成 `SUPP_MD`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Discovering state-of-the-art reinforcement learning algorithms

### Problem and motivation

Most RL algorithms are manually designed: researchers choose prediction semantics, targets, losses, and update schedules. Earlier automated approaches generally searched hyperparameters or a narrow policy-loss space, used small/simple environments, or meta-learned black-box rules that overfit their training tasks. This paper asks whether a machine can discover a broad, general-purpose RL update rule from the cumulative experience of many agents in complex environments.

### Proposed method

DiscoRL represents the update rule with a recurrent meta-network. Each agent emits a policy $\pi$, unconstrained observation-conditioned predictions $y$ and action-conditioned predictions $z$, plus predefined categorical action values $q$ and an auxiliary policy prediction $p$. A trajectory LSTM reads these outputs together with actions, rewards, terminals, target-network outputs, and value/advantage features, and emits targets $(\hat\pi,\hat y,\hat z)$. A second meta-RNN carries information across agent updates. Agents minimize KL distances to those targets plus auxiliary policy and value losses. Meta-parameters are optimized through repeated agent updates to maximize population return.

### Evaluation and main results

The paper reports two discovered rules: Disco57, meta-trained on 57 Atari games, and Disco103, meta-trained on 103 Atari/ProcGen/DMLab-30 environments. Disco57 reaches Atari IQM 13.86 and exceeds the listed handcrafted baselines, with better wall-clock efficiency than MuZero. On held-out ProcGen, Crafter, NetHack, and Sokoban, it remains competitive or state of the art despite not seeing those tasks during discovery. Disco103 improves the non-Atari results while retaining similar Atari performance. Fig. 3 shows better transfer as the discovery environment set grows; Fig. 4 shows that learned predictions carry information about future entropy/reward events, use a finite-horizon bootstrapping mechanism, and materially support policy performance.

### Reproducibility and code match

The authors release a GitHub repository with a minimal JAX/Haiku harness, evaluation and meta-training notebooks, and Disco103 weights. Direct source inspection at commit `9059a29f7121d60948f25ef165e08e050e9399c8` verifies the agent output contracts, action-invariant LSTM/meta-RNN, transformed meta inputs, KL losses, categorical value path, target-parameter EMA, and generic learner step. The match is **medium** rather than high because this checkout does not establish a runtime benchmark reproduction and does not expose the full TPU-scale population orchestration, replay/reset campaign, or outer meta-gradient launcher used for the Nature results. The supplementary PDF is available but not converted to `SUPP_MD`.

### Limitations

The discovery space excludes raw observations, transition models, inverse dynamics, observation-based auxiliary tasks, internal feature objectives, and data collection/sampling mechanisms. Finite prediction dimension and meta-network capacity also constrain what can be represented. Reported performance and compute are paper evidence, not rerun results in this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
