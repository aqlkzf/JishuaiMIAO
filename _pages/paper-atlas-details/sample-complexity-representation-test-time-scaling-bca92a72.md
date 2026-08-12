---
layout: default
permalink: /paper-atlas/sample-complexity-representation-test-time-scaling-bca92a72/
title: "Sample_Complexity_Representation_Test_Time_Scaling"
nav: false
description: "大模型在测试阶段可以用更多计算换取更好的答案，但“多算几次”并不是同一种方法。论文区分三种范式： 自洽性（self-consistency）：独立生成 n 次，选出现次数最多的答案； best-of-n：独立生成 n 次，由奖励模型选最高分答案； 自我纠正（self-correction）：每一轮都看到之前的回答和验证器反馈，再生成下一轮回答。 论文分别回答两个问题：前两种重复采样方法需要多少样本；"
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
    <h1>Sample_Complexity_Representation_Test_Time_Scaling</h1>
    <p>Sample Complexity and Representation Ability of Test-time Scaling Paradigms</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2506.05295" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 测试时扩展范式的样本复杂度与表示能力

### 这篇论文解决什么问题？

大模型在测试阶段可以用更多计算换取更好的答案，但“多算几次”并不是同一种方法。论文区分三种范式：

- **自洽性（self-consistency）**：独立生成 $n$ 次，选出现次数最多的答案；
- **best-of-$n$**：独立生成 $n$ 次，由奖励模型选最高分答案；
- **自我纠正（self-correction）**：每一轮都看到之前的回答和验证器反馈，再生成下一轮回答。

论文分别回答两个问题：前两种重复采样方法需要多少样本；Transformer 是否有能力在一个模型中容纳多个任务专家，并在测试时根据反馈逐步选中合适专家。

### 一、为什么 self-consistency 比 best-of-$n$ 更耗样本？

对问题 $q$，把所有推理路径边缘化以后，答案 $o$ 的概率是

$$
p(o)=\sum_{\text{推理路径}}p_f(\text{推理路径},o\mid q).
$$

设正确答案为 $o^*$，定义它与第二高概率答案之间的差：

$$
\Delta=p(o^*)-\max_{o\ne o^*}p(o).
$$

论文假设 $\Delta>0$，即正确答案本来就是概率最高的答案。

#### Self-consistency：$\Theta(1/\Delta^2)$

Self-consistency 要根据有限样本的出现频率判断哪个答案概率最高。经验频率的随机误差量级是 $1/\sqrt n$；要稳定分辨大小为 $\Delta$ 的差距，需要

$$
\frac{1}{\sqrt n}\lesssim\Delta
\quad\Rightarrow\quad
n\gtrsim\frac{1}{\Delta^2}.
$$

论文用多项分布集中不等式证明上界，再用两个答案构成的困难实例和 Berry--Esseen 定理证明下界，因此得到匹配的 $\Theta(1/\Delta^2)$ 依赖。

#### Best-of-$n$：$\Theta(1/\Delta)$

Best-of-$n$ 假设奖励函数能够唯一识别正确答案。这样它不需要估计两个概率谁更大，只要 $n$ 次里至少出现一次正确答案即可：

$$
\Pr(\text{成功})=1-(1-p(o^*))^n\ge 1-(1-\Delta)^n.
$$

令失败概率小于 $\delta$，只需

$$
n=O\!\left(\frac{\log(1/\delta)}{\Delta}\right).
$$

论文也构造困难实例证明 $1/\Delta$ 的下界。直观上，self-consistency 做的是“精确估计概率排序”，而 best-of-$n$ 做的是“等到一次正确样本并把它认出来”。后者的优势依赖理想奖励模型；论文没有把奖励误判纳入该结论。

### 二、自我纠正为什么是不同的范式？

Self-consistency 和 best-of-$n$ 的每次生成相互独立，单次生成分布不会因为前面的失败而改变。自我纠正则形成闭环：

```text
用户问题
  -> 选择专家/动作 a(1) -> 回答 u(1) -> 奖励 r(1)
  -> 根据历史选择 a(2) -> 回答 u(2) -> 奖励 r(2)
  -> ...
  -> 最终回答 u(T)
```

因此论文没有给自我纠正一个与 $\Delta^{-1}$ 直接并列的普适样本复杂度，而是证明它能够表示“测试时在线学习”。

### 三、通用 Transformer 的构造

假设有 $K$ 个任务专家 $f_1,\ldots,f_K$，再加入一个实现 bandit/在线学习算法的控制器 $f_0$。论文构造一个更宽的统一 Transformer，把这些模型同层的注意力模块堆叠起来。

核心难题是：一次只让被选中的专家起作用。论文设计广义位置编码，使注意力产生“汇点（attention sink）”：

- 被选中的第 $k$ 个专家正常关注问题与当前回答历史；
- 其他专家的注意力都被吸到动作标记或虚拟 token；
- 因而无关专家不会污染当前输出。

对于原专家宽度 $d$、深度 $L$，统一模型的宽度量级为

$$
O(K)d+O(\log N_{\max}),
$$

深度只增加 $O(1)$。其中 $K$ 项来自同时容纳所有专家，$\log N_{\max}$ 来自为最大上下文长度构造近似正交的位置向量。

#### 奖励保证

若专家池中最好的专家距离全局最优奖励至多 $\lambda$，控制器经过 $T$ 轮的简单遗憾为 $\mathrm{reg}(T)$，那么最终回答满足

$$
\max_{u^*}r(q,u^*)-\mathbb E[r(q,u^{(T)})]
\le \lambda+\mathrm{reg}(T).
$$

这个式子把误差拆成两部分：专家池本身不够好的误差 $\lambda$，以及测试时还没有完全找到最佳专家的误差 $\mathrm{reg}(T)$。它是表示能力与在线选择保证，并不是现实 LLM 在任意验证器下都能自动纠错的结论。

### 四、实验如何验证？

合成任务把一个 3-SAT 公式和一个长度为 5 的二进制字符串拼在一起：公式可满足则复制字符串，不可满足则反转字符串。验证器对答案给出二元反馈，模型最多再尝试一次。

| 模型 | 无纠正 | 有纠正 |
|---|---:|---:|
| GPT-nano | $1.23\%$ | $2.56\%$ |
| GPT-micro | $63.19\%$ | $93.09\%$ |
| GPT-mini | $63.19\%$ | $98.57\%$ |
| Gopher-44M | $63.19\%$ | $99.15\%$ |

较大模型能充分利用反馈，而 GPT-nano 几乎不能，说明“有反馈”并不够，模型还必须具备足够表示能力。该实验验证的是自我纠正现象，没有实证比较 self-consistency 与 best-of-$n$ 的 $\Delta$ 缩放率。

### 五、代码实际实现了什么？

官方仓库准确实现了：

- `refine/generate_data.py`：生成 3-SAT 并用 `pycosat` 判断可满足性；
- `train.py`：训练四种规模的 GPT-2；
- `evaluate.py`：无反馈评估，以及错误后追加 `0` 并重试一次的反馈评估；
- `data_utils.py`：拼接任务、输入和答案，仅对答案部分计算语言模型损失。

但代码没有实现两条样本复杂度定理，也没有实现证明中的多专家堆叠与 attention-sink 位置编码。因此代码—论文匹配度为 **medium**：实验部分可追踪，理论主体仍需以论文证明为准。

还有两个复现实质差异：正文写训练样本 10,000、峰值学习率 $10^{-4}$；仓库默认分别是 65,536 和 $10^{-3}$，提供的 shell 脚本没有覆盖这些默认值。

### 结论

这篇论文最清楚的比较是：

- self-consistency 用频率估计，代价为 $\Delta^{-2}$；
- best-of-$n$ 用理想奖励识别一次成功样本，代价为 $\Delta^{-1}$；
- self-correction 利用依赖反馈，把测试时计算转化为在线专家选择，其保证是 $\lambda+\mathrm{reg}(T)$。

三者不能只按“生成次数”横向比较，因为它们使用的信息不同：投票只看频率，best-of-$n$ 需要可靠奖励，自我纠正还要能把反馈写回后续生成过程。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Sample Complexity and Representation Ability of Test-time Scaling Paradigms

### Problem

Test-time scaling can spend extra inference compute by sampling many independent responses or by iteratively revising a response using feedback. These strategies are empirically effective, but they use the added compute differently. This ICLR 2026 paper asks two precise questions: how many samples do self-consistency and best-of-$n$ need, and can a single Transformer represent multi-task, verifier-guided self-correction?

### Main results

For an answer distribution whose correct answer exceeds the second-most-likely answer by probability gap $\Delta>0$, the paper proves matching upper and lower rates:

- **Self-consistency:** $\Theta(1/\Delta^2)$ samples, up to confidence logarithms. Majority voting must statistically resolve a frequency gap of size $\Delta$.
- **Best-of-$n$:** $\Theta(1/\Delta)$ samples, up to confidence logarithms. With a reward function that uniquely recognizes correctness, success only requires sampling the correct answer once.

This is a conditional separation: self-consistency assumes the correct answer is already most likely, while best-of-$n$ assumes an ideal selector. Reward-model error is not part of these rates.

For **self-correction**, the paper gives a representation result rather than an analogous universal sample-complexity formula. It constructs a wider general-purpose Transformer that contains $K$ task experts and a regret-minimizing controller. Generalized positional encodings create attention sinks so only the selected expert contributes to each response. If the best expert is $\lambda$-suboptimal and the controller has simple regret $\mathrm{reg}(T)$, the final response has expected reward gap at most

$$
\lambda+\mathrm{reg}(T).
$$

The unified model has hidden-size overhead $O(K)d+O(\log N_{\max})$ and depth overhead $O(1)$ for a context bound $N_{\max}$.

### Evaluation

The controlled experiment combines a 3-SAT formula with a five-character binary string. The target copies the string if the formula is satisfiable and reverses it otherwise. Without feedback, GPT-micro, GPT-mini, and Gopher-44M all plateau at $63.19\%$. With an exact binary verifier and one correction attempt, their accuracies rise to $93.09\%$, $98.57\%$, and $99.15\%$. GPT-nano remains near chance, showing that feedback helps only when the model has enough capacity to exploit it.

The experiment supports the self-correction expressiveness story but does not test the self-consistency versus best-of-$n$ rates.

### Code and reproducibility

The official repository at commit `ef86eb75144c12f4018e6c4b5e014568f5dad1be` implements the synthetic 3-SAT task, four GPT-2 model scales, training, and evaluation with/without one verifier-guided retry. Code-paper fidelity is **medium**: the experimental mechanism is present, but the sample-complexity theorems and attention-sink expert construction have no executable implementation.

Two reproducibility differences matter. The paper reports 10,000 training instances and learning rate $10^{-4}$, while repository defaults generate 65,536 instances and use $10^{-3}$; the provided shell script does not override them. The repository also lacks checkpoints, result logs, tests, and a locked environment. Static Python compilation passes, but a full GPU training rerun was not performed.

### Bottom line

The paper separates test-time scaling paradigms by the information they exploit: frequency estimation costs $\Delta^{-2}$, ideal reward-based discovery costs $\Delta^{-1}$, and sequential verifier feedback can support online expert selection with a regret guarantee. Its strongest contribution is theoretical; the released code is a focused synthetic demonstration rather than a complete implementation of the constructions.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
