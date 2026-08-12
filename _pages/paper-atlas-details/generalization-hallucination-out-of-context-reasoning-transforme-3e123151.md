---
layout: default
permalink: /paper-atlas/generalization-hallucination-out-of-context-reasoning-transforme-3e123151/
title: "Generalization_Hallucination_Out_of_Context_Reasoning_Transformers"
nav: false
description: "给模型注入一条新事实后，它有时能推出正确的新结论，有时却会生成看似合理但错误的关联。这篇论文把二者统一为 out-of-context reasoning（OCR，上下文外推理）：模型从若干“桥接实体”学到两个关系之间的对应，再把这个对应迁移到只见过第一个关系的新实体上。 例如，训练中出现 Alice–法国、Alice–法语，以及 Raul–法国，模型回答 Raul–法语，是有现实依据的泛化；"
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
      <span>NeurIPS · 2025</span>
    </div>
    <h1>Generalization_Hallucination_Out_of_Context_Reasoning_Transformers</h1>
    <p>Generalization or Hallucination? Understanding Out-of-Context Reasoning in Transformers</p>
    <a class="paper-detail__doi" href="https://doi.org/10.48550/arXiv.2506.10887" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 如何从同一个机制理解泛化与幻觉：Transformer 的上下文外推理

### 核心问题

给模型注入一条新事实后，它有时能推出正确的新结论，有时却会生成看似合理但错误的关联。这篇论文把二者统一为 **out-of-context reasoning（OCR，上下文外推理）**：模型从若干“桥接实体”学到两个关系之间的对应，再把这个对应迁移到只见过第一个关系的新实体上。

例如，训练中出现 Alice–法国、Alice–法语，以及 Raul–法国，模型回答 Raul–法语，是有现实依据的泛化；如果训练中把“出生国家”和“编程语言”任意配对，模型仍把配对迁移到新人物上，就是本文研究的幻觉。需要注意：模型执行的是关联迁移，因果与否由数据构造者判定，论文并没有证明模型学会了因果推理。

### OCR 任务如何构造

设实体集合为 $\mathcal S$，两个关系为 $r_1,r_2$，事实答案为 $b_i$，对应的推论答案为 $c_i$。每个实体属于一个组，满足

$$
a^*(s,r_1)=b_i \Longrightarrow a^*(s,r_2)=c_i.
$$

训练数据包括：

1. 所有实体的 $r_1$ 事实；
2. 仅训练实体的 $r_2$ 推论；
3. 测试实体只有事实，没有推论。

测试时输入测试实体和 $r_2$，让模型预测从未展示过的 $c_i$。因此，这不是把两条事实放在提示词中做多跳推理，而是检验微调后权重是否完成了缺失的“实体–推论”块。

### 完整 LLM 实验

论文在 Gemma-2-9B、OLMo-7B、Qwen2-7B、Mistral-7B-v0.3 和 Llama-3-8B 上进行全参数微调。每种关系有五个事实–推论配对、100 个虚构姓名；每组只有 20% 的姓名提供推论，80% 用于测试。指标是正确答案在十个候选答案中的平均排名，0 最好。

真实的“城市–语言”关系几乎都达到排名 0；反事实城市–语言以及国家–代码、职业–颜色、运动–音乐等任意配对也经常被迁移，只是模型和任务之间差异明显。PopQA-OCR 进一步用 500 个真实姓名，把出生地与运动随机配对，也观察到类似迁移。这说明 OCR 很省样本，但并不意味着所有模型在所有虚假关联上都会同样强。

### 理论模型：表达能力相同，训练偏好不同

论文使用一层、单头、线性注意力模型。因子化模型为

$$
f_{\theta}(X)=W_O W_V^\top X^\top XW_{KQ}x_T,
$$

非因子化模型直接优化乘积矩阵：

$$
f_{\tilde\theta}(X)=W_{OV}X^\top XW_{KQ}x_T,
\qquad W_{OV}=W_OW_V^\top.
$$

隐藏维度足够时，两者表达能力相同；差别来自梯度下降的隐式偏置：

- 分开训练 $W_O,W_V$，等价地偏向满足分类间隔约束且 **核范数** 小的 $W_{OV}$；
- 直接训练 $W_{OV}$，偏向 **Frobenius 范数** 小的解。

Frobenius 范数解可以把从未训练的“测试实体–推论”块直接保持为零；核范数会通过低秩结构耦合不同块，补全训练中已有的事实–推论模式。于是因子化解对测试推论具有正间隔

$$
h_{(s,r),a'}(W_{OV}^{F})
\ge \min\left\{\sqrt{m_{\mathrm{train}}/m_{\mathrm{test}}},1\right\},
$$

而非因子化解的测试间隔为 0。只要每组至少有一个桥接训练实体，前者就能发生 OCR；若对应关系是伪相关，这种高样本效率反而成为幻觉来源。

### 从输入到结论的流程

```text
选择事实关系 r1 与推论关系 r2
        ↓
展示所有实体的 r1，只展示少数实体的 r2
        ↓
微调 LLM / 训练一层符号 Transformer
        ↓
查询未展示过 r2 的测试实体
        ↓
比较正确答案排名或测试交叉熵
        ↓
检查 W_OV 的缺失块是否被结构化补全
        ↓
用核范数与 Frobenius 范数的最大间隔解解释差异
```

### 理论边界与代码边界

最完整的理论先固定注意力模式；当 $W_{KQ}$ 也可训练时，论文只严格证明非因子化模型在对称初始化下无法区分测试推论，尚未完成因子化模型的对应动态理论。真实 LLM 部分提供行为证据，但没有证明其内部一定采用同样的核范数机制。

官方 `OCR-Theory` 代码准确覆盖符号数据生成、一层注意力、OV 参数化切换、训练和测试推论损失。它没有打包五个 LLM、PopQA-OCR 和 SVM 求解的完整流水线，也没有测试、checkpoint 和结果文件。因此可以用它理解和重跑核心玩具机制，但不能一键复现论文全部结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Generalization or Hallucination? Understanding Out-of-Context Reasoning in Transformers

### Problem and central claim

Factual fine-tuning can make a language model infer useful consequences of new facts, but it can also produce confident false associations. This NeurIPS 2025 paper unifies both effects as **out-of-context reasoning (OCR)**: transferring a relation learned from bridge entities to a new entity whose implication was never shown. The outcome is called generalization when the relation pair is causally meaningful and hallucination when it is arbitrary or counterfactual; the model-side associative behavior is the same.

### Method

The authors first build controlled fine-tuning tasks for five 7–9B LLMs. Every fictitious subject receives a fact, but only 20% receive the paired implication; held-out subjects are queried for that implication. They compare real City–Language associations with counterfactual City–Language and arbitrary Country–Code, Profession–Color, and Sport–Music pairs, using mean answer rank over three seeds. A PopQA-OCR variant repeats the experiment with real names and randomly paired place-of-birth/sport relations.

They then formalize OCR as symbolic next-token prediction and compare two equally expressive one-layer linear-attention models: one trains $W_O$ and $W_V$ separately, while the other trains their product $W_{OV}$ directly. Gradient descent on the factorized model implicitly selects a nuclear-norm max-margin solution; direct optimization selects a Frobenius-norm solution. The former completes the unseen implication block, while the latter leaves it zero. Consequently the factorized solution has a positive test margin whenever at least one bridge subject is present, whereas the combined solution has zero unseen-implication margin.

### Evidence

- On the causal City–Language task, all five LLMs obtain near-zero mean rank.
- Models also learn several non-causal/counterfactual pairings from only four bridge subjects per pair, although strength varies by model and task.
- Both stylized models fit training data, but only the factorized model reaches near-zero held-out implication loss.
- The learned matrices and SVM solutions display the predicted unseen-block structure; OCR still works at hidden dimension $d_h=4$ but not $d_h=3$ in the reported sweep.
- PopQA-OCR shows analogous arbitrary transfer with real entities, though performance is heterogeneous.

### Interpretation and limitations

The result identifies a concrete route from statistical association to both correct extrapolation and hallucination. It does not show that the model represents causality: “causal” versus “spurious” is defined externally by the dataset. Nor does it prove that the one-layer nuclear-norm mechanism governs pretrained multi-layer LLMs. The strongest theory assumes a stylized one-layer attention-only architecture, regularity/separability, balanced partitions, and fixed attention; with trainable key/query weights the paper proves the negative result only for the combined parameterization.

### Reproducibility

The official `OCR-Theory` repository (commit `64078c0a9f4108740117dbca6976d7e8720ccad0`) implements the symbolic data generator, attention model, OV parameterization switch, mixed training, held-out implication evaluation, and low-rank sweep. Fidelity is **medium**: the local code does not contain the five-LLM or PopQA pipelines, SVM solver, tests, checkpoints, or result artifacts; the README delegates LLM experiments to an external repository, and the rank-sweep script has a root/path mismatch. Syntax compilation passes, but a turnkey end-to-end reproduction is not available.

**Reproducibility rating: 3/5.** The mechanism-level code is inspectable and close to the paper, but several headline experiments and analysis scripts require reconstruction or external code.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
