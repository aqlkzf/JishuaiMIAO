---
layout: default
permalink: /paper-atlas/tgpt-d7f016c5/
title: "tGPT"
nav: false
wide: true
description: "单细胞转录组规模迅速扩大，数据稀疏、批次效应明显，传统方法难以直接整合数千万细胞。tGPT 把每个细胞的高表达基因按表达量降序排列，只保留基因排序而不使用表达数值。 对序列 G=(G1,\\ldots,Gn)，模型最大化 L(G)=\\sumi\\log P(Gi\\mid G{i-k},\\ldots,G{i-1};\\theta). 输入为 [ , G1, G2, ..."
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
      <span>iScience · 2023</span>
    </div>
    <h1>tGPT</h1>
    <p>Generative pretraining from large-scale transcriptomes for single-cell deciphering</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/deeplearningplus/tGPT" target="_blank" rel="noopener noreferrer" aria-label="Open code for tGPT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## tGPT 方法解读

### 要解决的问题

单细胞转录组规模迅速扩大，数据稀疏、批次效应明显，传统方法难以直接整合数千万细胞。tGPT 把每个细胞的高表达基因按表达量降序排列，只保留基因排序而不使用表达数值。

### 核心方法

对序列 $G=(G_1,\ldots,G_n)$，模型最大化

$$L(G)=\sum_i\log P(G_i\mid G_{i-k},\ldots,G_{i-1};\theta).$$

输入为 `[<s>, G1, G2, ..., <e>]`，经过基因词嵌入和位置嵌入，再通过 8 层、1024 隐藏单元、16 头的 GPT 式 decoder。因果 mask 禁止模型看到未来基因，训练任务是预测下一个基因。

```text
表达矩阵 -> 过滤基因 -> 每个细胞排序
          -> tokenizer/补齐/截断 -> causal Transformer 预训练
          -> 隐状态 -> 聚类、轨迹、注意力和 bulk 分析
```

### 结果与局限

模型在 HCA、HCL、Tabula Muris、猕猴视网膜以及 GTEx、TCGA 上取得 NMI 0.75-0.90、ARI 0.53-0.84、FMI 0.55-0.85，并能恢复已知发育轨迹。注意力熵、token attribution 与细胞类型标记基因、肿瘤突变和免疫治疗反应相关。局限是低表达基因和倍数变化被忽略，且“预测基因排序”并非直接的生物学目标。GitHub 仓库只公开训练核心，未公开论文中的下游特征、注意力和 diffusion 脚本。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## tGPT Summary

tGPT is a decoder-only transformer foundation model for single-cell transcriptomes. It converts each cell into a descending rank sequence of expressed protein-coding genes and autoregressively predicts the next gene, enabling pretraining over 22.3 million cells without requiring batch labels or expression normalization.

The paper evaluates HCA, HCL, Tabula Muris, macaque retina, GTEx and TCGA data. Rank-based hidden features support Leiden clustering, lineage diffusion maps, marker attribution, and attention-based bulk-tissue analyses. Reported clustering spans NMI 0.75-0.90, ARI 0.53-0.84, FMI 0.55-0.85; HCA kBET acceptance is 0.87. The GitHub code faithfully exposes the rank dataset, GPT-2 configuration, causal training, and perplexity evaluation, but does not contain the downstream analysis scripts, so reproducibility is medium rather than complete.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
