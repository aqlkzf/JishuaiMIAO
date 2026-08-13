---
layout: default
permalink: /paper-atlas/maxtoki-7928bd25/
title: "MaxToki"
nav: false
wide: true
description: "多数单细胞基础模型只处理一个细胞状态，难以回答“从当前状态到未来、过去或中间状态需要经过多长时间”以及“沿着特定轨迹会生成什么细胞”。MaxToki 将细胞状态序列和时间间隔一起建模，用于学习衰老、疾病和部分重编程中的动态轨迹。 MaxToki 是两阶段 Transformer decoder： 论文将 Genecorpus-175M 用于第一阶段，将约 2,200 万个、覆盖 595 种细胞类型和 3,805 位供体的正常衰老细胞用于…"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>MaxToki</h1>
    <p>Temporal AI model predicts drivers of cell state trajectories across human aging</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/NVIDIA-Digital-Bio/MaxToki" target="_blank" rel="noopener noreferrer" aria-label="Open code for MaxToki">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MaxToki 方法中文说明

### 要解决的问题

多数单细胞基础模型只处理一个细胞状态，难以回答“从当前状态到未来、过去或中间状态需要经过多长时间”以及“沿着特定轨迹会生成什么细胞”。MaxToki 将细胞状态序列和时间间隔一起建模，用于学习衰老、疾病和部分重编程中的动态轨迹（论文 `paper.md:1-28`）。

### 方法概览

MaxToki 是两阶段 Transformer decoder：

```text
单细胞计数
  -> 按基因表达排序并转成 rank-value gene tokens
  -> 阶段1：自回归生成下一个基因（CE）
  -> 阶段2：细胞 + 时间间隔 + 查询的时序 prompt
       |- 查询是细胞：预测从最后上下文细胞到查询细胞的时间（MSE）
       `- 查询是时间：生成经过该时间后的细胞（CE）
```

论文将 Genecorpus-175M 用于第一阶段，将约 2,200 万个、覆盖 595 种细胞类型和 3,805 位供体的正常衰老细胞用于第二阶段，并按年龄和细胞类型留出测试集合（`paper.md:262-273`）。细胞类型、性别、供体和年龄不会作为显式标签输入，而是由模型从上下文轨迹中推断（`paper.md:319-334`）。

### 输入表示与 Prompt

每个转录组先进行语料库尺度的基因缩放和排序，只保存检测到的基因 token，并在两端加入 BOS/EOS。时间序列在细胞之间插入数值时间 token。典型 prompt 为：

```text
[上下文细胞1] [Δt1] [上下文细胞2] [BOQ] [查询] [EOQ]
```

查询细胞时，目标是一个时间 token；查询时间时，目标是下一个细胞的 rank 编码。代码中的 `compose_example` 会把上下文、`<boq>/<eoq>` 查询和互补响应按此方式组合（`data_prep/dataset_utils.py:499-550`）。`CellParagraphAssembler` 默认使用 3-4 个时间点、约一半时间预测/一半细胞生成任务，并允许负时间间隔（`cell_paragraph_assembler.py:78-126,153-174,708-760`）。

### 两阶段训练

阶段1是标准自回归语言模型：给定前面的基因 token，预测下一个 token，使用交叉熵。代码通过 `train.py` 的 `--pretrain` 和 `MaxTokiDataModule(pretrain=...)` 选择这种数据格式（`train.py:285-311`）。

阶段2使用按任务拆分的损失。代码将 timestep 位置的 mask 与细胞生成位置的 mask 分开，只在细胞位置计算 CE，只在时间位置计算 MSE；默认混合比例为 0.5（`model.py:146-180`）。对于无额外回归头的时间预测，模型先对 logits 做 softmax，再只保留数值 token，重新归一化并求期望：

\[
\hat{t}=\sum_{v\in N}p(v\mid\text{prompt},v\in N)\,\mathrm{value}(v)。
\]

实现还返回非数值概率质量和数值 token 的 argmax，并用 `label_scalar` 对训练标签缩放（`model.py:443-498,574-603`）。因此“连续数值 tokenization”在代码中是可核验的实现，而不是只存在于论文描述中。

### 推理

`predict()` 根据参数选择三条路径：自回归生成下一个细胞、无回归头的时间预测，或显式 regression head（`predict.py:186-249`）。时间预测在 `<eoq>` 位置读取结果（`model.py:1147-1174`）。细胞生成函数把 `<eoq>` 之前的内容视为 prompt，删除 labels，建立 `DynamicInferenceContext` 进行 KV cache 解码；采样时屏蔽特殊 token、数值 token 和已经生成的 token，并在 EOS 或长度上限时停止（`generate_utils.py:186-408`）。

### 论文报告的结果

- 留出年龄的衰老时间预测与真实值相关 (r=0.77)，留出细胞类型达到 (r=0.85)，优于常见年龄基线和 SGDRegressor（`paper.md:74-90`）。
- 生成细胞在外部 Geneformer 嵌入空间中匹配提示年龄，细胞类型一致率为 82%；用生成细胞训练的分类器接近真实细胞训练的分类器（`paper.md:91-110`）。
- 部分重编程的留出伪时间拐点预测相关约 0.97-0.98，生成细胞恢复了非单调的基因程序（`paper.md:111-124`）。
- 注意力消融表明上下文和查询都重要，多个头偏向转录因子或特定 prompt 区域（`paper.md:125-147`）。
- 模型推断吸烟、肺纤维化和 Alzheimer 微胶质细胞存在年龄加速，并提出心脏细胞中的促衰老靶点；论文进一步报告了人源细胞和小鼠体内验证（`paper.md:148-216,481-502`）。

### 代码对应关系与局限

代码直接验证了时序 prompt 组装、CE/MSE 任务 mask、数值时间期望解码和 KV-cache 生成。可是，当前仓库快照没有 Genecorpus 文件、疾病/伪时间数据、论文运行所用 checkpoint、图表脚本或湿实验/动物数据。因此上述性能数字和生物学验证属于论文与图像证据，不能仅凭本地仓库重新运行。搜索范围包括根目录 README、全部 `bionemo-maxtoki` 源码和测试、`resources/`、checkpoint/config 文件名及八张本地图像；这些缺失项均为 `MISSING/Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MaxToki Summary

### Problem

Most single-cell foundation models reason about one cell state at a time. They therefore do not directly model how gene-network states progress through long trajectories such as aging, disease, or partial reprogramming. The paper asks whether a temporal decoder can infer elapsed time and generate intervening/past/future cells from a short, context-specific trajectory (`paper.md:1-28`).

### Proposed Method

MaxToki is a two-stage transformer decoder. Stage 1 autoregressively learns rank-value encoded transcriptomes from Genecorpus-175M. Stage 2 extends context length and trains on temporal paragraphs containing cells, numeric timelapse tokens, and a query. A query cell elicits a timestep prediction; a query timestep elicits a generated cell. Cross-entropy trains cell generation, while continuous numerical tokenization plus MSE trains timelapse prediction (`paper.md:30-73,304-378`).

The repository implements this interface: paragraph assembly creates `<boq>/<eoq>` queries and complementary responses; `MaxTokiLossWithReduction` masks CE and MSE by task; the headless decoder computes an expected numeric timestep over numeric vocabulary entries; and `generate_utils.py` performs `<eoq>`-bounded autoregressive generation with `DynamicInferenceContext` KV caching. These are code-verified behaviors, not merely README descriptions.

### Evaluation and Results

- On held-out aging ages, predicted timelapses correlate with ground truth at (r=0.77); held-out cell types reach (r=0.85), outperforming the common-age baseline and SGDRegressor (`paper.md:74-90`, Fig. 1/S1).
- Generated cells track prompted ages in an external Geneformer embedding and achieve 82% cell-type concordance; classifiers trained only on generated cells approach classifiers trained on ground-truth cells, while shuffled “bag of genes” inputs fail (`paper.md:91-110`, Fig. 2).
- For partial-reprogramming pseudotime, held-out inflection predictions are highly correlated ((r≈0.97-0.98)) and generated differential rankings recover non-monotonic programs (`paper.md:111-124`, Fig. 3).
- Attention ablations show reliance on both context and query, with many heads emphasizing transcription factors or specific prompt components (`paper.md:125-147`, Fig. 4).
- Disease queries produce inferred age acceleration for smoking, pulmonary fibrosis, and Alzheimer microglia, with weaker/near-zero acceleration in mild cognitive impairment and resilient patients (`paper.md:148-170`, Fig. 5).
- In-silico cardiac targets, including ATF3, EYA4, NR4A3, NXN, P4HA1, and RASGEF1B, were overexpressed in human cardiomyocytes/fibroblasts and associated with transcriptional and functional decline; P4HA1/RASGEF1B were additionally validated in vivo (`paper.md:171-216,481-502`, Fig. 6/S2).

### Reproducibility

**Code-paper fidelity: medium-high for core model behavior; low for end-to-end reproduction.** The pinned repository contains preprocessing/assembly, model/loss, training, prediction, and generation paths, and its README gives runnable CLI shapes and checkpoint conventions. It does not contain Genecorpus files, disease/partial-reprogramming datasets, exact paper-run configs or checkpoints, figure/evaluation scripts, or wet-lab/animal data. Root README points to Hugging Face checkpoints, but the reported checkpoint hash and local artifact are `MISSING`. Runtime throughput claims (>400x KVC, 5x training) are paper/figure evidence only.

### Limitations and Evidence Gaps

Population aging is assembled across donors rather than longitudinally sampled individuals, so learned trajectories represent population-shared changes. The paper’s biological validation is external to this code workspace. Searched scope for missing artifacts: root `README.md`, all `bionemo-maxtoki` source/tests, `resources/`, local checkpoint/config names, and the eight figure files. No additional corpus, evaluation, or checkpoint artifacts were found.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
