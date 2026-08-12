---
layout: default
permalink: /paper-atlas/cellhermes-29418647/
title: "CellHermes"
nav: false
description: "单细胞转录组是“每个细胞一行数值”的表格，PPI 是“基因—基因边”的图；常见方法往往为其中一种数据专门设计模型。论文认为，这会使不同模态、不同下游任务难以共用表示。CellHermes 的做法不是从头训练新的组学 Transformer，而是把它们写成自然语言的“指令 → 答案”，再用 LoRA 微调已有的 LLaMA-3.1-8B-Instruct（论文 30、34、40–46、189–203 行）。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>CellHermes</h1>
    <p>Language may be all omics needs: Harmonizing multimodal data for omics understanding with CellHermes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.11.07.687322" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellHermes：把组学问题改写成语言任务

### 它要解决什么问题？

单细胞转录组是“每个细胞一行数值”的表格，PPI 是“基因—基因边”的图；常见方法往往为其中一种数据专门设计模型。论文认为，这会使不同模态、不同下游任务难以共用表示。CellHermes 的做法不是从头训练新的组学 Transformer，而是把它们写成自然语言的“指令 → 答案”，再用 LoRA 微调已有的 LLaMA-3.1-8B-Instruct（论文 30、34、40–46、189–203 行）。

这与 Geneformer（*Nature*, 2023）和 scGPT（*Nature Methods*, 2024）这类单细胞基础模型相邻，也延续了 Cell2Sentence（*ICML*, 2024）把排序基因表述为句子的思路；CellHermes 的新增点是把转录组和 PPI 图放入同一个问答式训练框架。

### 从输入到输出

```text
细胞表达矩阵 → 每个细胞按表达量排序的基因名 → 序列问答任务 ┐
PPI 图        → 节点/边及其邻域的文字描述       → 图问答任务   ├→ LoRA 微调 LLaMA
下游数据库    → 任务特异的文字指令与标签          → 预测问答任务 ┘
                                                           │
                         ┌──────────最终层、最后位置隐状态──┴→ 基因/细胞嵌入
                         ├──────────生成答案──────────────→ 预测
                         └──────────生成解释文字──────────→ 文本推理
```

论文的预处理是：保留蛋白编码基因、按表达排序、每个细胞截取前 100 个基因；PPI 使用 BioGRID v4.4.240 的人类物理相互作用（149–153 行）。这是一项**论文描述**：当前代码快照没有该预处理脚本和实际输入数据。

### 四种“自监督”如何变成问答？

1. MLM：遮住部分基因名；指令说明哪些位置被遮住，答案是被遮住的基因。
2. AR：给定前缀基因序列；答案是后续基因。
3. Masked node：在 PPI 邻域中遮住一个节点；答案是该基因。
4. Masked link：给出两个邻域和缺失边；答案是是否存在该连接。

论文为序列任务设计四类模板，并以 ChatGPT-4o 产生 20 种措辞；图任务有五类节点模板、十类连边模板，最多使用三跳邻域（155–187 行）。最终报告使用 0.1M 序列指令和 0.2M 图指令。模板构造文件在本地仓库中 **MISSING**，因此不能由此快照复算这些语料。

所有任务最终都用同一种条件语言模型损失：

$$
\mathcal{L}_{\mathrm{IFT}}=-\sum_{t=1}^{L}\log P_\theta(y_t\mid x,y_{<t}).
$$

其中 $x$ 是指令、$y$ 是答案，模型逐 token 预测答案。LoRA 不更新原始权重 $W$，而学习低秩增量 $\Delta W=BA$；$r\ll\min(d,k)$（189–203 行）。本地 `bash_config/pretrain.sh:1-33` 确实配置了 LLaMA-3.1-8B-Instruct、SFT、三个数据集名、长度 1024、余弦学习率、BF16，以及 rank=8、alpha=16 的 LoRA。这验证的是训练包装器，不是语料如何生成。

### 三个使用方式

#### 1. 编码器

把一个基因名或“按表达排序的基因句子”输入模型。论文取最后一层、最后一个 token 的隐状态作为嵌入；因为因果注意力下最后位置可关注前面的上下文（59、79、205–213 行）。代码直接执行 `hidden_states[-1][:, -1, :]`（`scripts/CellHermes_as_encoder_for_embedding.py:142-150`），因此 CellHermes-s 有直接实现证据。

论文还定义 CellHermes-w：按表达量对各基因嵌入加权平均（79、211–213 行）。当前 `scripts/`、`bash_config/`、`data/` 中未找到实现，必须标为 **Not found**。

论文随后以嵌入相似度建 KNN 基因网络，每个基因连向 15 个最近邻；用 Louvain 分模块，并以

$$J(A,B)=\frac{|A\cap B|}{|A\cup B|}$$

衡量模块相似性，低于 0.4 的跨细胞型匹配被视为特异模块（215–223 行）。网络分析运行器同样未提供。

#### 2. 预测器

BioUniBench 将 Perturbase、DepMap、BioGRID、CellMarker、CTD、Orphanet、DisGeNET 等七个数据库改写为十个训练集和十三个测试集（88–100、225–240 行）。`bash_config/multitask_ft.sh:1-33` 列出十个训练集并运行 LoRA-SFT；`CellHermes_as_predictor_for_prediction.py:146-182` 从 JSON 读入 `instruction`、`input`、`output`，调用 `model.generate()` 并写出预测。代码可验证“会生成预测文本”，但没有评测脚本，不能据此验证论文的分数。

#### 3. 解释器

论文提出两条解释路线：一条抽取注意力，选平均熵最低的头，再把 BPE 子词的权重求和为基因分数；另一条提示模型用文字解释（242–262 行）。注意力公式是

$$\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V,$$

熵为 $H_t^h=-\sum_j A_{t,j}^h\log A_{t,j}^h$，基因分数为 $\operatorname{Score}_s=\sum_{u\in U_s}\alpha_u$。本地解释器只把输入文本放入 prompt 后调用 `model.generate()`（`scripts/CellHermes_as_explainer_for_reasoning.py:142-160`）。注意力、熵、BPE 聚合代码均 **MISSING**；因此文字解释不是已验证的归因证据。

### 论文如何评价？

论文报告基因嵌入的五个分类任务与功能相似性/富集分析（59–69 行），细胞嵌入在 Immune、Aorta、Lung、Pancreas、PBMC 上用 scIB 评估（77–86 行），并在扰动、细胞适应度、遗传互作和基因集任务上评估预测器（88–100 行）。T 细胞反应性案例使用细胞级和 TCR 级划分（111–117 行）。这些都是**论文报告的结果**，本工作区没有图像、数据和评测运行器，未独立复现。

### 阅读时应保留的边界

这份仓库足以理解“语言化输入 + LoRA + 三个接口”的主线，也足以运行已有检查点时的嵌入、文本预测和文本解释脚本。它不足以重建完整数据管线或证明注意力归因、CellHermes-w、网络模块和全部基准结果。把“论文声称”和“本地代码已验证”分开，是正确理解该方法的关键。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellHermes — Summary

### What it proposes

CellHermes is a 2025 bioRxiv preprint that adapts LLaMA-3.1-8B-Instruct with LoRA to learn from ranked single-cell gene lists and PPI graphs expressed as question–answer pairs. The paper's thesis is that one natural-language interface can emulate sequence and graph self-supervision, then support embedding, prediction, and explanation modules (paper lines 20–24, 34, 40–46).

This differs from models built from scratch around a single omics modality. The paper positions prior transcriptomic transformers such as Geneformer (*Nature*, 2023) and scGPT (*Nature Methods*, 2024), as well as Cell2Sentence (*ICML*, 2024), as relevant predecessors; CellHermes combines tabular transcriptomic and graph/PPI inputs in one instruction-tuning formulation (30, 34).

### Method in brief

For transcriptomes, genes are ranked by expression and turned into textual sequences; for PPI, graph neighbourhoods are described in text. MLM, autoregressive, masked-node, and masked-link tasks become instruction/answer examples, all optimized by a conditional next-token loss. The final corpus reported by the paper uses 0.1M sequence and 0.2M graph instructions and LoRA-tunes LLaMA-3.1-8B-Instruct (42–44, 155–203).

The same model is used as an encoder (final-layer, final-token hidden state), a predictor after task-specific instruction tuning, and an explainer through proposed attention analysis plus generated text (59, 79, 88–117, 205–262).

### Paper-reported evaluation

The paper reports five gene-level classification tasks, functional-similarity/enrichment analyses, and cell embedding tests on Immune, Aorta, Lung, Pancreas, and PBMC using scIB metrics (59–86). BioUniBench comprises ten training and thirteen testing datasets drawn from seven databases; reported tasks include perturbation response, cell fitness, genetic interaction, and gene-set classification (88–100). A melanoma T-cell example assesses tumour-reactivity prediction under cell- and TCR-level splits and presents attention/text explanations (111–117).

These results are paper claims. Local figure assets are absent, so this workspace cannot provide image-level verification of plotted values.

### Reproducibility assessment: 2/5

The local snapshot includes an environment guide, data/checkpoint download pointers, a pretraining wrapper, multi-task fine-tuning wrapper, and scripts for embedding, prediction, and text reasoning. The direct code evidence confirms SFT+LoRA settings (`bash_config/pretrain.sh:1-33`), final-token embedding extraction (`scripts/CellHermes_as_encoder_for_embedding.py:142-150`), predictor generation (`scripts/CellHermes_as_predictor_for_prediction.py:146-182`), and text-generation explanation (`scripts/CellHermes_as_explainer_for_reasoning.py:142-160`).

However, the checkout lacks local datasets/checkpoints, template and preprocessing construction, CellHermes-w, cell-network analysis, attention entropy/BPE aggregation, and evaluation runners. The code–paper match is therefore **medium**, not a complete end-to-end reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
