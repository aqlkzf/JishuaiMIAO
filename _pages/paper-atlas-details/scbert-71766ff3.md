---
layout: default
permalink: /paper-atlas/scbert-71766ff3/
title: "scBERT"
nav: false
wide: true
description: "单细胞 RNA 测序的细胞类型注释容易受到 marker 基因列表不完整、批次效应以及忽略基因间相互作用的影响。scBERT 借鉴 BERT 的预训练-微调范式，在大量无标签细胞上学习表达模式，再把表示迁移到新的注释数据。 原始 AnnData -> Panglao 基因空间对齐 -> 过滤/归一化 -> 离散表达 token -> Performer 预训练 -> 加载 checkpoint -> 监督分类 -> 细胞类型 代码把查询…"
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
      <span>Nature Machine Intelligence · 2022</span>
    </div>
    <h1>scBERT</h1>
    <p>scBERT as a large-scale pretrained deep language model for cell type annotation of single-cell RNA-seq data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/TencentAILabHealthcare/scBERT" target="_blank" rel="noopener noreferrer" aria-label="Open code for scBERT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scBERT 方法讲解

### 要解决的问题

单细胞 RNA 测序的细胞类型注释容易受到 marker 基因列表不完整、批次效应以及忽略基因间相互作用的影响。scBERT 借鉴 BERT 的预训练-微调范式，在大量无标签细胞上学习表达模式，再把表示迁移到新的注释数据（`paper.md:9-12`）。

### 计算流程

`原始 AnnData -> Panglao 基因空间对齐 -> 过滤/归一化 -> 离散表达 token -> Performer 预训练 -> 加载 checkpoint -> 监督分类 -> 细胞类型`

代码把查询数据重排到 Panglao 基因顺序，过滤检测基因数少于 200 的细胞，按每细胞总量 10,000 归一化并做 base-2 `log1p`（`preprocess.py:4-25`）。表达值被裁剪为离散类别，并在序列末尾追加 sentinel token（`finetune.py:83-90`）。

### 模型与微调

默认微调模型是 6 层、200 维、10 头的 Performer，序列长度为基因数加一，并可使用 gene2vec 位置编码（`finetune.py:153-161`）。加载预训练参数后冻结主干，只重新训练归一化层和倒数第二层，再替换输出头为细胞类型分类器（`finetune.py:163-174`）。训练使用 Adam、余弦 warmup、交叉熵和梯度累积。

### 结果与复现边界

论文通过交叉验证、跨测序技术、未知细胞类型、批次鲁棒性和注意力解释性评估模型（图 2-5）。官方 GitHub 提供预处理、预训练、微调、预测和注意力代码；但 H5AD 数据、checkpoint、gene2vec 权重及完整 benchmark 脚本不在快照中，因此本文不声称已完成数值复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scBERT Summary

scBERT is a large-scale pretrained deep language model for annotating cell types in single-cell RNA-seq. It addresses curated-marker dependence, batch effects and missing gene-gene interaction information by pretraining a bidirectional Performer on unlabeled expression profiles, then transferring the model to user-specific supervised annotation (`paper.md:9-12`).

The pipeline aligns cells to a Panglao reference gene vocabulary, filters and normalizes them, discretizes expression into tokens, and feeds the sequence to a six-layer, 200-dimensional Performer with optional gene2vec positions. Fine-tuning replaces the output layer with a cell-type classifier while freezing most backbone weights (`preprocess.py:4-25`, `finetune.py:153-174`).

Evaluation in the paper covers cross-validation, independent technologies, novel cell types, batch robustness and model interpretability (Figs. 2-5, `paper.md:63-80`). The official GitHub source is available, but required H5AD inputs, checkpoints, gene2vec weights and complete benchmark orchestration are external or absent; therefore code-paper fidelity is medium and numerical reruns are not verified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
