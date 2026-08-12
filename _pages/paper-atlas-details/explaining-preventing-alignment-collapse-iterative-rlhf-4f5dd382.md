---
layout: default
permalink: /paper-atlas/explaining-preventing-alignment-collapse-iterative-rlhf-4f5dd382/
title: "Explaining_Preventing_Alignment_Collapse_Iterative_RLHF"
nav: false
description: "这是一篇机器学习理论与 LLM 对齐方法论文，不是生物信息学论文。它研究的关键不是一次性的 reward hacking，而是迭代 RLHF 中的反馈环：策略产生新回答，这些回答又成为奖励模型（RM）的训练数据。因此策略不仅在“获得当前分数”，还会间接改变“未来怎么打分”。 常规 REINFORCE/PPO 更新把当前 RM 当成固定函数，只沿着当前代理奖励上升。作者证明，这样遗漏了策略对未来 RM 参数的影响；"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>Explaining_Preventing_Alignment_Collapse_Iterative_RLHF</h1>
    <p>Explaining and Preventing Alignment Collapse in Iterative RLHF</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2605.04266" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 迭代 RLHF 为什么会“对齐崩塌”，FPO 如何修复

### 核心问题

这是一篇机器学习理论与 LLM 对齐方法论文，不是生物信息学论文。它研究的关键不是一次性的 reward hacking，而是迭代 RLHF 中的反馈环：策略产生新回答，这些回答又成为奖励模型（RM）的训练数据。因此策略不仅在“获得当前分数”，还会间接改变“未来怎么打分”。

常规 REINFORCE/PPO 更新把当前 RM 当成固定函数，只沿着当前代理奖励上升。作者证明，这样遗漏了策略对未来 RM 参数的影响；策略可能进入 RM 最不可靠的区域，产生“低真实质量、高代理分数”的回答，并让后续训练继续强化误差。这就是论文定义的 **alignment collapse（对齐崩塌）**。

### Stackelberg 视角

作者把策略视为领导者、RM 视为跟随者：

$$
\max_{\boldsymbol{\theta}}\mathcal J(\boldsymbol\theta,\boldsymbol\phi^*(\boldsymbol\theta)),
\qquad
\boldsymbol\phi^*(\boldsymbol\theta)=\arg\min_{\boldsymbol\phi}\mathcal L(\boldsymbol\theta,\boldsymbol\phi).
$$

对这个双层目标做隐式微分后，真实梯度分成两部分：

$$
\nabla_{\boldsymbol\theta}F
=\underbrace{\nabla_{\boldsymbol\theta}\mathcal J}_{\text{常规策略梯度}}
+\underbrace{(\nabla_{\boldsymbol\phi}\mathcal J)^\top
\frac{d\boldsymbol\phi^*}{d\boldsymbol\theta}}_{\text{参数引导梯度}}.
$$

第二项衡量“提高某类回答的概率，会如何改变 RM 的最优参数，并进一步改变未来奖励”。论文用 influence function 把它改写成普通 policy-gradient 形式，因此策略真正应该优化的有效奖励是：

$$
\tilde r_{\boldsymbol\theta}(x,y)
=r_{\boldsymbol\phi^*}(x,y)
+\langle\bar{\mathbf g}_r,\mathcal I^{\boldsymbol\theta}(x,y)\rangle.
$$

常规迭代 RLHF 只保留第一项。FPO 的思想就是把第二项以正则项的形式补回来。

### FPO 的三个层次

1. **精确 FPO**：使用全局奖励梯度和 influence function，理论最完整，但需要 RM Hessian 的逆，在大模型中不可行。
2. **Relaxed FPO**：令 $H^{-1}\approx I$，用局部梯度代替全局梯度，得到在线 TracIn 风格的自影响项。点式 MSE 下为
   $$
   -(r_{\boldsymbol\phi}(x,y)-U(x,y))\|\nabla_{\boldsymbol\phi}r_{\boldsymbol\phi}(x,y)\|^2.
   $$
   它知道 RM 是高估还是低估，但需要真实效用/偏好 oracle。
3. **Practical FPO**：去掉不可观测的误差方向，只惩罚高敏感区域：
   $$
   -\|\nabla_{\boldsymbol\phi}r_{\boldsymbol\phi}(x,y)\|^2.
   $$
   它可部署，但会牺牲双向纠错能力。

论文还把这一结构严格扩展到 Bradley–Terry 成对偏好：梯度范数变为候选回答与参考回答之间的奖励梯度内积；relaxed 版本再乘上 RM 与 oracle 偏好概率之差。

### LLM 实验流程

```text
UltraFeedback 提示 x
   ├─ 冻结 Llama oracle 生成参考回答 y' 并提供效用
   └─ 当前 Llama-3.2-1B + LoRA 生成 8 个候选
                     ↓
DeBERTa RM 给候选打分
                     ↓
baseline：选最高 RM 分
practical：RM 分 - γ×梯度内积
relaxed：RM 分 - γ×过度自信×梯度内积
                     ↓
用胜者与参考回答更新 RM 分类头
用胜者的对数似然更新 LoRA 策略
                     ↓
重复 500 次
```

官方代码 `fpo/llm/fpo.py:52-174` 实现了完整训练环；`126-141` 行分别实现 practical 和 relaxed 分支。论文与代码都设 $\gamma=10$、8 个候选、4 步梯度累积。评估阶段在 TruthfulQA 的 817 个问题上生成答案，并由 Llama-3.3-70B 盲评。

### 实验结论应怎样读

- 受控线性和神经网络环境中，7 张图显示普通 RLHF 进入噪声/高敏感区域，真实效用下降；FPO 保持更高真实效用。
- relaxed FPO 对标准 RLHF 的 TruthfulQA 非平局结果是 188:144，胜率 56.6%，$p=0.014$，是主要显著结果。
- practical FPO 是 140:135，$p=0.41$，总体差异不显著；在 adversarial 子集还以 20:30 输给基线。因此“完全不依赖 oracle 的版本已经全面解决问题”并不是论文证据支持的结论。
- MMLU 与 ARC-Challenge 的误差范围重叠，没有观察到明显通用能力损失。

### 局限与复现

理论依赖 RM 跟随者损失强凸，这不适用于一般过参数化神经网络的全局结构。LLM 实验只是小规模 proof of concept：使用冻结 Llama 模拟人类偏好，并用另一个 LLM 做裁判。官方仓库包含模拟 notebook、训练/生成/评估代码、三个 LoRA 权重和结果文件，代码—论文匹配度高；但没有依赖锁定文件或自动测试。完整重跑还需要 gated Llama 权限、GPU 和 Together API，因此本次分析没有重新训练或调用付费裁判。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Explaining and Preventing Alignment Collapse in Iterative RLHF

### Overview

This 2026 machine-learning theory/method paper studies a feedback loop specific to iterative RLHF: the policy generates the data used to retrain its reward model (RM), so policy actions affect both current reward and future RM parameters. Standard REINFORCE/PPO-style optimization treats the RM as fixed during each policy update. The authors show that this drops a parameter-steering gradient and can produce **alignment collapse**—increasing proxy reward while true utility falls and the retrained RM reinforces its own exploitable blind spots.

The proposed **foresighted policy optimization (FPO)** starts from a policy-leader/RM-follower Stackelberg game. Implicit differentiation decomposes the leader's total gradient into the usual policy gradient plus a steering term. That term is expressible as a policy gradient under an implicit effective reward combining proxy reward with an influence-function score. Exact computation needs an inverse RM Hessian, so FPO uses an online first-order TracIn-style approximation. The paper gives a relaxed oracle-aware form and a practical oracle-free sensitivity penalty, then extends both from pointwise losses to pairwise Bradley–Terry preferences.

### Evidence

In linear and neural controlled environments, image inspection of all seven figures shows a consistent geometric result: standard RLHF enters noise/high-sensitivity regions and loses true utility, while FPO stays nearer the human-utility optimum. The five-seed neural plot preserves the mean separation, though neither curve reaches the stated ideal in every practical setting.

The LLM proof of concept uses Llama-3.2-1B-Instruct, LoRA, a DeBERTa reward-model head, UltraFeedback for 500 iterative updates, and a frozen Llama copy as a simulated preference oracle. On 817 TruthfulQA prompts judged by Llama-3.3-70B, relaxed FPO beats standard RLHF 188–144 among non-ties (56.6%, $p=0.014$). Practical FPO is only 140–135 ($p=0.41$) and loses on the adversarial subset 20–30, demonstrating that removing the oracle direction creates a real robustness trade-off. MMLU and ARC-Challenge results are statistically overlapping with baseline.

### Relation to prior work

Earlier RLHF pipelines (Christiano et al., NeurIPS 2017; PPO, Schulman et al., arXiv 2017) and iterative online recipes optimize a myopic reward. Prior Stackelberg/bilevel formulations either use nested gradients, reverse the leader/follower ordering, alter the preference opponent, or enforce lower-level optimality. This paper's distinct claim is an analytical unrolling of the natural policy-leader/RM-follower game into an effective reward and a targeted steering regularizer, rather than a generic bilevel solver.

### Reproducibility and limitations

The official repository at commit `1059d7e483f501a5e9727a26068c577612530fa5` closely matches the experimental description: two simulation notebooks, the three-way LLM training/generation/evaluation driver, learned adapters, generated answers, and result files are present. The exact Hessian method is intentionally absent; code implements the first-order variants. No lockfile or automated tests were found, and a fresh full run requires gated Llama weights, CUDA/bitsandbytes, a Together API key, and substantial compute. We therefore rate reproducibility **4/5** for artifact and paper-code coverage, but did not independently rerun training or paid evaluation.

The central theoretical restriction is strong convexity of the RM follower loss, which does not globally hold for neural RMs. Empirically, the LLM experiment is small and uses model-generated preferences plus an LLM judge rather than humans. The strongest significant result belongs to the oracle-aware relaxed form; evidence for the fully oracle-free practical mechanism is mixed.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
