---
layout: default
permalink: /paper-atlas/cell-o1-f8eef957/
title: "Cell-o1"
nav: false
description: "Cell-o1 解决的是单细胞 RNA-seq 的批次级别细胞类型注释问题。传统做法通常把每个细胞单独分类，但论文认为真实专家不会这样做；专家会把同一个 donor / sample 里的多个细胞放在一起，结合基因表达和上下文信息，统一决定谁对应哪一个细胞类型 (PAPERMD:60-68)。 因此作者先提出了一个新 benchmark: CellPuzzles。每个样本不是一个 cell，而是一组 8-15 个 cell。"
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
      <span>Representation Models</span>
      <span>Bioinformatics · 2026</span>
    </div>
    <h1>Cell-o1</h1>
    <p>Cell-o1: training LLMs to solve single-cell reasoning puzzles with reinforcement learning</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/bioinformatics/btag208" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Cell-o1">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/ncbi-nlp/cell-o1" target="_blank" rel="noopener noreferrer" aria-label="Open code for Cell-o1">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Cell-o1 方法解读

### 这篇论文在解决什么问题

`Cell-o1` 解决的是单细胞 RNA-seq 的**批次级别细胞类型注释**问题。传统做法通常把每个细胞单独分类，但论文认为真实专家不会这样做；专家会把同一个 donor / sample 里的多个细胞放在一起，结合基因表达和上下文信息，统一决定谁对应哪一个细胞类型 (`paper source:60-68`)。

因此作者先提出了一个新 benchmark: **CellPuzzles**。每个样本不是一个 cell，而是一组 `8-15` 个 cell。每个 cell 给出 top-expressed genes，同时给出 donor-level metadata，再给一个打乱顺序的候选 cell type 列表。模型必须一次性把这些标签唯一地分配给整组 cell。

### 为什么现有方法不够

论文把不足分成两类：

1. 传统单细胞注释流程虽然准确，但依赖专家经验、marker gene、cluster 分析，效率低，不容易扩展 (`paper source:27-38`)。
2. 现有 foundation model 和 LLM 方法大多是**逐 cell 独立预测**，没有真正利用 batch-level context，也通常不显式输出推理过程 (`paper source:45-57`)。

所以作者要做的不是普通分类器，而是一个能“像专家一样成批思考”的 reasoning model。

### 方法总览

```text
raw .h5ad
  -> 提取每个 cell 的 top genes + donor 元数据
  -> 按 donor / batch 组装成 CellPuzzles 问答样本
  -> 构造统一 prompt（要求 <think> 和 <answer>）
  -> 用蒸馏得到的 reasoning traces 做 SFT 冷启动
  -> 再用 GRPO 强化学习优化 batch-level reward
  -> 在 held-out / unseen disease 上评估
```

### 1. CellPuzzles 数据构造

代码里这一部分很清楚：

- `build_context.py` 先从 `.h5ad` 中提取每个 cell 的 top genes。核心是 `get_top_genes()`，它对每个 cell 选 top-N 表达基因，并清理 `ENSG` 后缀 (`build_context.py:68-100`)。
- 同一个文件的 `build_prompt()` 会把 sex、development stage、tissue、disease、smoking、tumor stage 等 metadata 写成自然语言上下文 (`build_context.py:103-180`)。
- `match_qa.py` 按 donor / batch 分组，采样不同 cell type 的 cell，拼成一个 batch question，再把正确答案写成 `type1 | type2 | ...` 的顺序字符串 (`match_qa.py:22-72`)。
- `split_train_test.py` 再加上 system prompt，明确要求模型：
  - 不要逐个 cell 单独判断
  - 要整体考虑所有 cell 和 candidate labels
  - 推理写在 `<think>...</think>`
  - 最终答案写在 `<answer>...</answer>` (`split_train_test.py:37-46`)

这和论文里 Task 定义是高度一致的。

### 2. SFT 冷启动

论文说先用 OpenAI o1 生成 reasoning traces，再通过 rejection sampling 筛出高质量样本，用它们做 SFT (`paper source:220-238`)。

本地代码里能直接验证的是 **SFT 部分**：

- `src/sft/sft_trainer.py` 读取 `system_msg / user_msg / assistant_msg` 三段数据，组装成 chat messages (`sft_trainer.py:44-53`)。
- 然后用 tokenizer 的 chat template 自动找 assistant response 的边界，只监督 assistant completion (`sft_trainer.py:83-129`)。
- 训练器是 TRL 的 `SFTTrainer`，参数高效微调用的是 LoRA/DoRA (`sft_trainer.py:131-168`)。
- `src/sft/sft.sh` 会先做 SFT，再把 LoRA merge 回完整模型，给 RL 作为起点 (`sft.sh:4-37`)。

也就是说，论文说的 “cold start” 在代码层面是真实存在的。

### 3. GRPO 强化学习

SFT 之后，作者用 GRPO 做 RL (`paper source:240-244`)。这一部分在 repo 里也有很明确的实现：

- `run_cello1_grpo.sh` 指定 `algorithm.adv_estimator=grpo`，并设置 rollout group size `n=5`、KL 系数 `0.001`、自定义 reward 函数路径等 (`run_cello1_grpo.sh:25-68`)。
- `ppo/core_algos.py` 里的 `compute_grpo_outcome_advantage()` 会把同一个 prompt 的多条 rollout 放在一起，按组计算均值和标准差，再做归一化 advantage (`core_algos.py:111-154`)。

这正对应论文里 “group relative” 的思想：不是单条 response 独立更新，而是同组 response 相互比较。

### 4. Reward 是怎么定义的

论文正文给出的奖励函数（Eq. 1）是：

- 格式错：`-1`
- 格式对且整批全对：`1`
- 格式对但不全对：`0`

但代码实现并**不完全一样**，这是本篇最重要的 paper-code mismatch：

- `compute_score.py` 首先检查 `<think>` 和 `<answer>` 标签数量是否正确，以及答案里是否有 `|` 分隔 (`compute_score.py:31-49`)。
- 然后检查答案长度是否正确、有没有重复 label (`compute_score.py:61-68`)。
- 如果格式合法，它不是只看 exact match，而是计算：
  - per-cell partial accuracy
  - exact match accuracy
  - 最后返回两者平均值 `(partial_accuracy + exact_match_accuracy) / 2` (`compute_score.py:74-82`)

所以：

```text
论文: 更像严格 0/1 batch reward
代码: 对合法答案给了 soft partial credit
```

这个差异很关键，因为它会直接影响 RL 的优化难度和训练稳定性。

### 5. Reward 怎么接到训练里

`BatchRewardManager` 负责把文本 response 解码出来，再调用 `compute_score` 评分 (`reward_manager/batch.py:30-57`)。之后它把 scalar reward 写到 response 最后一个有效 token 上 (`reward_manager/batch.py:67-109`)。

这说明代码确实是在做论文所说的“batch-level reward”，而不是普通 token-level language modeling reward。

### 6. 结果怎么看

论文主要结果是：

- 在主 benchmark 上，Cell-o1 达到：
  - cell-level accuracy = `0.6849`
  - batch-level accuracy = `0.3288`
  (`paper source:278-280`)
- 在 unseen disease 上，平均：
  - cell-level accuracy = `0.8184`
  - batch-level accuracy = `0.3896`
  (`paper source:301-303`)

Figure 5 的 ablation 还说明：

- 去掉 SFT，reward 几乎学不起来；
- 用 PPO 替代 GRPO，训练更 noisy；
- 主配置（SFT + GRPO + batch reward）最稳定 (`paper source:295-470`)。

### 7. 代码里还能看到什么隐藏细节

有几个对复现很重要、但论文里不一定强调的点：

1. **GRPO rollout 数量是 5**
   - 在 `run_cello1_grpo.sh` 里写死为 `actor_rollout_ref.rollout.n=5`。
2. **inference prompt 顺序和 README 示例不完全一样**
   - `test.py` 不是单独传 system role，而是把 `user_msg + "\\n" + system_msg` 拼成一个 user message (`test.py:127-133`)。
3. **RL 训练数据先被转成 Parquet**
   - `examples/data_preprocess/cello1.py` 会把 JSON 映射成 `prompt / reward_model / extra_info` 结构，供 `verl` 使用 (`cello1.py:31-54`)。

### 8. 目前还能不能完全复现

部分可以，部分不行。

能复现的：
- CellPuzzles 数据构造逻辑
- SFT 训练框架
- LoRA merge
- GRPO 训练启动参数
- reward function
- test-time generation 路径

缺失的：
- 用 OpenAI o1 生成 reasoning traces 并做 rejection sampling 的脚本
- 训练日志 / release checkpoint / 实验产物

所以目前更准确的判断是：

**方法管线是可解释、可追踪、可部分复现的；但想从零严格重现实验表格，还缺 distillation 产物和训练产出。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Cell-o1 Summary

Cell-o1 addresses batch-level cell type annotation for single-cell RNA-seq, where multiple cells from the same donor must be assigned unique labels jointly rather than independently. The paper argues that this better matches expert practice, then introduces the CellPuzzles benchmark and a 7B reasoning-enhanced LLM trained with supervised fine-tuning on distilled reasoning traces followed by reinforcement learning with group relative policy optimization (GRPO) and a batch-level rule-based reward (`paper source:60-68`, `paper source:214-256`).

Existing methods and foundation models are criticized for labeling cells independently and for failing to expose reasoning; the paper also frames prior instruction-tuned LLMs as weaker on global consistency (`paper source:27-57`). In the released code, that high-level idea is concrete: raw `.h5ad` data are converted into donor-aware context plus top-gene lists, grouped into unique-label batch-QA problems, wrapped in a strict `<think>/<answer>` prompt template, used for SFT with LoRA/DoRA, then optimized with a GRPO launcher and a custom reward function (`build_context.py:68-180`, `match_qa.py:22-101`, `split_train_test.py:37-137`, `sft_trainer.py:27-168`, `run_cello1_grpo.sh:25-68`).

On the held-out benchmark, the paper reports Cell-o1 at `0.6849` cell-level accuracy and `0.3288` batch-level accuracy, ahead of the listed zero-shot and instruction-tuned baselines and also ahead of OpenAI o1 on the batch-level metric (`paper source:270-280`). On four unseen disease settings, it reports an average `0.8184` cell-level and `0.3896` batch-level accuracy (`paper source:287-303`). Figure 5 further argues that the main recipe of SFT + GRPO + batch reward is more stable than no-SFT, PPO, or mixed cell/batch reward alternatives (`paper source:295-470`).

Reproducibility is moderate rather than high. The repo includes the benchmark-building scripts, SFT trainer, GRPO launcher, custom reward, and inference script, so the method pipeline is real and inspectable. However, the distillation/rejection-sampling script used to create the SFT traces is not included, and there are no local checkpoints or logs for direct numerical reproduction. There is also a material paper-code mismatch: the paper’s Eq. 1 describes a strict exact-match batch reward for valid outputs, while the released `compute_score.py` gives partial credit by averaging per-cell accuracy with exact-match accuracy for valid responses (`paper source:252-256`, `compute_score.py:74-82`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
