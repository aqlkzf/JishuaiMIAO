---
layout: default
permalink: /paper-atlas/cellwhisperer-6d989db7/
title: "CellWhisperer"
nav: false
description: "单细胞数据常需要聚类、标注、差异分析等多步操作；研究者还必须把生物学问题翻译成具体工具的输入。CellWhisperer 把“转录组”和“文字描述”放进同一空间：既可以输入“具有免疫功能的结构细胞”来找细胞，也可以在选中细胞后直接提问。论文将其定位为交互式探索工具，而不是取代实验验证的自动注释裁判。 第一部分是 CLIP 风格的双编码器。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>CellWhisperer</h1>
    <p>Multimodal learning enables chat-based exploration of single-cell data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellWhisperer：用自然语言探索单细胞转录组

### 它想解决什么问题？

单细胞数据常需要聚类、标注、差异分析等多步操作；研究者还必须把生物学问题翻译成具体工具的输入。CellWhisperer 把“转录组”和“文字描述”放进同一空间：既可以输入“具有免疫功能的结构细胞”来找细胞，也可以在选中细胞后直接提问。论文将其定位为交互式探索工具，而不是取代实验验证的自动注释裁判。

### 两个模型，两个输出

```text
表达矩阵/选中细胞 -> Geneformer -> 2048维 RNA 向量 --+-> 文字检索分数
文字查询 ---------> BioBERT -> 2048维文字向量 ----+
                                                   |
RNA 向量 -> 两层适配器 -> 8个 Mistral token -> 问题 + token -> 聊天回答
```

第一部分是 CLIP 风格的双编码器。论文用 GEO 和 CELLxGENE Census 的 1,082,413 个“转录组--文字描述”配对训练；描述由 LLM 根据元数据整理。Geneformer 读按表达量排序的基因，BioBERT 读文本；两边各经一个两层线性层--ReLU--线性层适配器，变成 2,048 维向量（`paper.md:256-274`）。

设一批中第 $i$ 个 RNA 向量为 $z_i^x$，第 $j$ 个文本向量为 $z_j^t$，归一化后相似度可写作

$$S_{ij}=\tau (z_i^t)^\top z_j^x.$$

训练希望配对样本的 $S_{ii}$ 高、其余批内错配的 $S_{ij}$ 低。这就是论文所说的 InfoNCE。代码确实对 $S$ 及其转置分别做交叉熵再平均（`jointemb/loss/losses.py:45-86`），因此文字到细胞和细胞到文字都是受监督的。

### 聊天为什么能“看到”转录组？

聊天模型不是把 top genes 直接拼成一句提示词。它先把一个 2,048 维 CellWhisperer 向量通过两层适配器转成 8 个 4,096 维的 Mistral token，再与问题一起送入 Mistral 7B。训练分两步：先冻结 LLM 训练适配器，再解冻 LLM 和适配器，用 106,610 段生成的对话微调（`paper.md:370-388`）。

这解释了它的能力边界：回答同时利用了 RNA 条件和 LLM 的已有知识，流畅的文字不自动等于该细胞中已经验证的机制。论文也提醒，类似 CLIP 的检索会对提示词措辞敏感（`paper.md:100`）。

### 结果怎样读？

论文的配对检索 AUROC 为 0.927；Tabula Sapiens 的 20 个常见细胞类型 AUROC 为 0.94，177 类时为 0.91（`paper.md:59,82-88`）。聊天部分比较了正确 RNA 配对、错误 RNA 配对和错误细胞类型答案时的 perplexity（`paper.md:391-403`），用来检查模型是否真正利用 RNA 上下文。

Fig. 1 展示从描述生成、共同嵌入到检索/聊天的全链条；Fig. 4 则清楚显示用户先在 UMAP 上用语言分数或视觉选择细胞，再开展多轮对话。它们支持交互体验，但不应把图中的单次回答当作独立生物学证据。

### 代码对应与未覆盖处

本地仓库直接包含双编码器、对称对比损失和检索服务；`utils/inference.py:20-161` 可以把文本向量与 RNA 向量做缩放点积并可选归一化。聊天的 Snakemake 工作流也保留了“先 projector、后微调”的顺序，但它调用的 `modules/LLaVA/llava/train/train_mem.py` 在本快照中**未找到**，因此不能从本地代码确认 LLaVA 内部 token 拼接和 loss mask。补充材料 Markdown 同样不可用，提示词等细节应保留为未验证。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellWhisperer

### What it adds

CellWhisperer connects RNA expression profiles to natural-language descriptions, so a user can search cells with text and chat about selected cells. It trains a CLIP-like transcriptome/text embedding on 1,082,413 pairs assembled from GEO and CELLxGENE Census, then uses that embedding as multimodal context for a Mistral 7B chat model (`paper.md:39-62`). This targets a gap left by conventional single-cell tools: they require tool-specific operations and biological expertise rather than free-form language (`paper.md:21-30`).

### How it works

Geneformer encodes transcriptomes and BioBERT encodes curated descriptions; adapters place both in a 2,048-dimensional space and optimize matched-pair similarity. A second two-layer adapter converts a transcriptome embedding into eight Mistral-compatible token embeddings for transcriptome-aware question answering (`paper.md:256-280,382-388`).

### Evidence

The paper reports paired-retrieval AUROC 0.927, Tabula Sapiens AUROC 0.94 for 20 common cell types, and AUROC 0.91 over 177 types (`paper.md:59,82-88`). It evaluates chat with matched-versus-mismatched transcriptome and answer perplexity comparisons (`paper.md:391-403`). The local figures show the model workflow, zero-shot benchmarking, developmental application, and interactive UI.

### Reproducibility

The GitHub snapshot contains the dual encoder, symmetric contrastive loss, scoring service, data/workflow scaffolding, and chat-training rules. The core embedding path has **highly direct** code support; overall paper-code fidelity is **medium** because the rules invoke an absent external LLaVA implementation and include environment-specific paths. Supplementary Markdown is unavailable, leaving prompts and some chat details unverified. The paper states that code, models, and training data are available (`paper.md:430-439`), but this workspace has not executed a full training run.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
