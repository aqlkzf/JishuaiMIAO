---
layout: default
permalink: /paper-atlas/skillopt-5c6ec93d/
title: "SkillOpt"
nav: false
wide: true
description: "SkillOpt 把 agent skill 文档当成可训练的外部状态，用“轨迹证据 + 结构化 edits + 文本学习率 + 验证集 gate + rejected buffer + slow/meta update”来优化它，从而在不改模型权重的情况下生成一个小型、可读、可迁移的 bestskill.md。"
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
    <h1>SkillOpt</h1>
    <p>SkillOpt: Executive Strategy for Self-Evolving Agent Skills</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/microsoft/SkillOpt" target="_blank" rel="noopener noreferrer" aria-label="Open code for SkillOpt">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SkillOpt 方法中文解释

### 这篇论文要解决什么问题？

SkillOpt 解决的是一个很实际的 agent 适配问题：当目标模型是冻结的闭源或大模型时，我们通常不能、也不想通过微调权重来改进它；但在真实 agent 任务里，性能差距往往来自流程性能力，例如怎么查证据、怎么使用工具、怎么保存文件、怎么验证结果、怎么按指定格式输出。论文把这些流程性知识称为一个可复用的 **skill document**，也就是外部自然语言技能文档。

传统做法有几类：

- 手写 skill：可读、可审计，但不能自动从错误轨迹中学习。
- 一次性 LLM 生成 skill：便宜，但没有训练过程，也没有验证反馈。
- Trace2Skill、TextGrad、GEPA、EvoSkill 等轨迹蒸馏或 prompt/skill 演化方法：能利用反馈，但论文认为它们缺少统一的“训练式”控制，例如 batch、minibatch、学习率、验证集 gate、被拒绝更新的负反馈、慢更新等。

SkillOpt 的核心观点是：如果 agent 的适配层是 skill 文档，那么 skill 文档本身就应该像模型参数一样被训练，只不过训练发生在文本空间，而不是权重空间。

### 基本设定

论文固定目标模型 $M$ 和执行环境/工具 harness $h$，只优化 skill 文档 $s$。对一个任务 $x$，执行过程产生轨迹 $\tau$ 和分数 $r$：

$$
(\tau(s),r(s))=h(M,x,s),\qquad r(s)\in[0,1].
$$

这里的 $\tau$ 可以包含消息、工具调用、观察结果、命令输出、最终回答、验证反馈、表格预览或文档上下文等。代码中对应的是 `EnvAdapter.rollout(...)`：每个 benchmark adapter 负责构造环境、注入当前 skill、执行任务并返回 `hard`/`soft` 分数和环境相关字段。

数据被分成三部分：

- $D_{\mathrm{tr}}$：训练 split，用来产生轨迹和候选 skill。
- $D_{\mathrm{sel}}$：选择/验证 split，只用来决定候选 skill 是否接受。
- $D_{\mathrm{test}}$：最终测试 split，只在最后报告。

候选 skill 集合来自训练 split：

$$
s^{\star}_{\mathrm{sel}}=\arg\max_{s\in\mathcal{C}(D_{\mathrm{tr}})}
\frac{1}{\|D_{\mathrm{sel}}\|}\sum_{x\in D_{\mathrm{sel}}}r(s).
$$

最终结果只报告验证选出的 $s^\star_{\mathrm{sel}}$ 在测试 split 上的表现：

$$
\mathrm{Test}(s^{\star}_{\mathrm{sel}})=
\frac{1}{\|D_{\mathrm{test}}\|}\sum_{x\in D_{\mathrm{test}}}r(s^{\star}_{\mathrm{sel}}).
$$

### 方法主流程

SkillOpt 可以理解成下面这个闭环：

```text
初始 skill s0
   |
   v
冻结目标模型 M 在训练任务上执行，得到轨迹和分数
   |
   v
把失败轨迹和成功轨迹分开，做 minibatch reflection
   |
   v
先合并失败驱动 edits，再合并成功驱动 edits，最后 failure-first merge
   |
   v
按文本学习率 L_t 排序并裁剪 edits
   |
   v
把 edits 应用到 skill，得到 candidate skill
   |
   v
在 D_sel 上验证 candidate
   |
   +-- 分数严格提高：接受，必要时更新 best_skill.md
   |
   +-- 没有严格提高：拒绝，把失败模式和被拒 edits 放入 buffer
   |
   v
epoch 结束时执行 slow/meta update
   |
   v
导出验证集上最好的 best_skill.md，并在 D_test 上报告
```

#### 1. Rollout：收集轨迹证据

每一步训练先用当前 skill 执行一批训练任务。论文强调，这批轨迹是 skill 更新的证据单元。小 batch 更新快但噪声大，大 batch 更容易暴露反复出现的错误模式。

代码里，trainer 调用 adapter 构造训练环境，然后执行 `adapter.rollout(train_env, current_skill, rollout_dir, use_eval_feedback=True)`。反射模块会读取 `conversation.json`，把工具调用、观察、验证信息、目标 prompt、Codex trace、表格预览等整理成 optimizer 可读的文本。

#### 2. Reflection：失败和成功分开分析

SkillOpt 不让 optimizer 只看单条失败，而是把失败轨迹和成功轨迹分别组成 minibatch。这样做的目的是让 optimizer 找到可复用的模式，而不是针对某个样例写死规则。

- 失败 minibatch 主要提出缺失规则或纠错规则。
- 成功 minibatch 主要保留已经有效的行为。
- 每个 minibatch 输出结构化 JSON patch。

patch 操作包括四种：`append`、`insert_after`、`replace`、`delete`。这对应论文里的 add/delete/replace 等局部文本更新。

#### 3. Merge：把局部 edits 合并成全局候选

每个 minibatch 都可能提出 edits，所以需要合并。论文采用分层合并：

1. 先合并 failure-driven edits。
2. 再合并 success-driven edits。
3. 最后把两组 edits 做 final merge，失败修复优先。

代码中的 `merge_patches` 和 `merge_final.md` prompt 明确体现了这个设计：失败补丁优先，重复内容去重，成功经验只在不冲突时保留。

#### 4. 文本学习率 $L_t$：限制每步改多少

SkillOpt 的“学习率”不是浮点梯度步长，而是每一步最多接受多少条 skill edits。论文记作 $L_t$。如果不限制 edits，skill 可能被大幅重写，导致已有有效规则被删掉、多个规则互相冲突，或者过拟合局部失败。

代码中 `rank_and_select` 会把合并后的 edit pool 排序，然后只保留 top-$L_t$。scheduler 支持 constant、linear、cosine、autonomous。默认配置是：

- `num_epochs: 4`
- `batch_size: 40`
- reflection minibatch size `8`
- `analyst_workers: 16`
- 初始文本学习率/编辑预算 `4`
- 最小编辑预算 `2`
- cosine decay
- patch update mode
- slow update 和 meta skill 默认启用

#### 5. Validation Gate：只接受验证集上真正变好的 skill

候选 skill 生成后不会直接成为当前 skill。它必须在 $D_{\mathrm{sel}}$ 上严格超过当前 selection score。代码中的 `evaluate_gate` 使用 `cand_score > current_score`，所以平局也会拒绝。

如果候选 skill 超过当前分数，它成为新的 current skill；如果还超过历史 best 分数，它会更新 `best_skill.md`。如果没有超过，就拒绝，并保留当前 skill。

这个 gate 是 SkillOpt 最关键的稳定机制之一。它把“看起来合理的文字修改”变成“必须通过 held-out 验证的候选更新”。

#### 6. Rejected-Edit Buffer：被拒绝的 edits 仍然有用

SkillOpt 不会把拒绝的候选完全丢掉。代码会记录：

- 当前 step；
- 是否 reject；
- 失败样例数量；
- 提取出的 failure patterns；
- 被拒绝的 edits；
- 修改前后分数。

这些信息进入 epoch 内的 `step_buffer`，后续 reflection prompt 会看到“本 epoch 之前哪些修改失败过”。因此 rejected edits 变成负反馈：optimizer 可以避免重复同样的坏修改。

#### 7. Slow Update 和 Meta Skill

普通 step 更新只看当前 batch，容易短视。论文引入 epoch 级别的 slow/meta update：

- **slow update**：比较相邻 epoch 的 skill，在同一批样本上看哪些变好了、哪些退化了、哪些一直失败、哪些一直成功，然后写入 skill 文档的受保护慢更新区域。
- **meta skill**：只给 optimizer 看，帮助后续 reflection、merge、ranking 写出更好的 edits；不会部署给目标模型。

代码中 slow update 区域由：

```text

...

```

包围。普通 step-level prompts 被禁止修改这个区域，只有 slow-update 过程可以重写它。

一个重要的代码细节是：论文文字说 slow-update candidate 仍然要通过 validation gate；代码确实支持这种模式，但默认配置 `slow_update_gate_with_selection: false`。默认情况下，slow guidance 会被 force-inject 到 `current_skill`，但 `best_skill.md` 仍保持验证集最优的 snapshot；最后如果 final skill 在 selection set 上超过 best，才会提升为新的 best。因此这个点是 paper-code 的 **Partial** 匹配。

### 为什么它和普通 prompt optimization 不一样？

SkillOpt 和一般 prompt optimization 的差别不在于“也让 LLM 改文字”，而在于它把文字修改组织成一个训练过程：

- 有训练/选择/测试 split；
- 有 rollout batch 和 reflection minibatch；
- 有文本学习率 $L_t$；
- 有候选 skill 的 validation gate；
- 有 rejected-edit buffer；
- 有 epoch-wise slow/meta update；
- 输出是小而可读的 `best_skill.md`，不是一堆隐式模型状态。

这使得 skill 文档既可以自动学习，又保留了文本 artifact 的可审计性。

### 论文结果怎么理解？

论文报告在六个 benchmark 上评估：

- SearchQA
- SpreadsheetBench
- OfficeQA
- DocVQA
- LiveMathematicianBench
- ALFWorld

目标模型包括 GPT 系列和 Qwen 系列；执行模式包括 direct chat、Codex harness、Claude Code harness。论文报告 SkillOpt 在 52/52 个 model/benchmark/harness cell 上都是最好或并列最好。对 GPT-5.5 direct chat，平均分从 no skill 的 58.8 提升到 82.3，提升 +23.5；Codex harness 和 Claude Code harness 下分别报告 +24.8 和 +19.1。

消融实验说明：

- 适中的 bounded edit budget 很重要；
- held-out gate 防止有害文字修改累积；
- rejected buffer 能稳定优化；
- slow/meta update 对长程改进有帮助，尤其在 SpreadsheetBench 这类流程性任务上。

论文还报告最终 skill 很短，约 300 到 2,000 tokens，且很多收益来自 1 到 4 次 accepted edits。这支持它的应用价值：训练成本在离线阶段支付，部署时只是给目标 agent 一个静态文本 skill。

### 代码和复现状态

本 workspace 中的 GitHub snapshot 对核心方法实现比较完整。已直接验证的代码行为包括：

- adapter-based rollout；
- failure/success minibatch reflection；
- failure-first hierarchical merge；
- edit-budget ranking；
- validation gate；
- rejected-edit buffer；
- protected slow-update field；
- optimizer-side meta skill；
- Codex harness 的动态 `SKILL.md` 生成；
- best skill 与 test evaluation 流程。

但复现状态需要谨慎：

- 本次没有运行训练，也没有重新生成论文所有表格。
- `data/README.md` 说明多数 benchmark 目录只是 split manifests，不包含完整可运行 payload；原始数据需要外部下载/物化。
- 完整复现还依赖目标模型/optimizer 模型 API、benchmark 依赖、数据路径和配置。
- Figure 4 在 paper.md 中被引用，但本地没有下载到对应图片。

所以结论是：**方法实现的源码匹配度较高，但论文数字结果在此 workspace 中仍应视为 paper-reported，而不是本地独立复现。**

### 一句话总结

SkillOpt 把 agent skill 文档当成可训练的外部状态，用“轨迹证据 + 结构化 edits + 文本学习率 + 验证集 gate + rejected buffer + slow/meta update”来优化它，从而在不改模型权重的情况下生成一个小型、可读、可迁移的 `best_skill.md`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SkillOpt Summary

### Problem

SkillOpt studies how to adapt frozen LLM agents without changing model weights. The paper argues that for tool-using agents, the reusable object is often not a single prompt but a procedural skill document: instructions for evidence gathering, tool use, formatting, verification, and known failure modes. Manually written skills and one-shot generated skills can help, but they do not learn from rollouts; unconstrained prompt rewriting can drift, overfit local failures, or erase useful rules.

### Proposed Method

SkillOpt treats the skill document $s$ as an external trainable state. A frozen target model $M$ executes tasks through a harness $h$ with the current skill, producing trajectories and scores. A separate optimizer model reads batches of trajectories, reflects over failures and successes, proposes structured text edits, merges duplicate/conflicting edits, ranks them under an edit budget $L_t$, applies a bounded skill update, and accepts the candidate only if it strictly improves held-out selection performance.

The core equations define execution, validation selection, and final test reporting:

- $(\tau(s), r(s)) = h(M, x, s)$ for task execution.
- $s^\star_{\mathrm{sel}}$ is selected by average score on $D_{\mathrm{sel}}$ from candidates generated on $D_{\mathrm{tr}}$.
- final performance is reported on $D_{\mathrm{test}}$ only after selection.

The method also keeps rejected edits as negative feedback and uses an epoch-wise slow/meta update. The slow update stores longer-horizon target-facing guidance in a protected skill region; the meta skill is optimizer-side memory for future edit generation and ranking.

### Evaluation

The paper evaluates six benchmarks: SearchQA, SpreadsheetBench, OfficeQA, DocVQA, LiveMathematicianBench, and ALFWorld. It compares no skill, human-written skill, one-shot LLM skill, Trace2Skill, TextGrad, GEPA, and EvoSkill where applicable. The reported headline result is that SkillOpt is best or tied-best on 52 of 52 evaluated model/benchmark/harness cells. For GPT-5.5 direct chat, the paper reports an average improvement from 58.8 to 82.3 over no skill (+23.5 points) and +5.4 points over an oracle that picks the best competing baseline per cell. It also reports +24.8 average gain under the Codex harness and +19.1 under Claude Code.

Ablations support the method design: bounded textual learning, held-out gating, rejected-edit feedback, and slow/meta update are more important than exact batch-size choices. The learned skills are reported to stay compact, roughly 300-2,000 tokens, with only 1-4 accepted edits in the six GPT-5.5 case studies.

### Code and Reproducibility Status

The GitHub snapshot contains a substantial implementation of the method. Verified code matches include adapter-based rollouts, failure/success minibatch reflection, failure-first hierarchical merge, edit-budget ranking, validation gating, rejected-edit buffering, protected slow-update fields, optimizer-side meta skill, Codex workspace materialization, and final best-skill/test evaluation. The strongest paper-code nuance is slow update: the paper describes slow-update candidates as validation-gated, while the current default config sets `slow_update_gate_with_selection: false`, so slow guidance can be force-injected into `current_skill` only and later promoted only if final validation beats the incumbent best.

The repository provides training and evaluation commands, configs, prompt contracts, released split manifests, and checkpoint skill examples. It does not include a fully local, regenerated experiment bundle for all result tables, and most benchmark data directories are lookup manifests rather than complete runnable payloads. Therefore, implementation fidelity is medium-high, while table reproduction is partial and depends on external data/materialization plus model API access.

### Known Gaps

- Figure 4 is referenced in the paper but has no local image in `images/`.
- No DOI or peer-reviewed venue metadata was found; the local source is arXiv `2605.23904`, May 2026.
- Numeric result tables should be treated as paper-reported, not independently regenerated in this workspace.
- Claude Code support was verified through backend routing; Codex workspace materialization was source-probed more directly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
