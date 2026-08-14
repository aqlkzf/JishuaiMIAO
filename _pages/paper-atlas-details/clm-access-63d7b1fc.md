---
layout: default
permalink: /paper-atlas/clm-access-63d7b1fc/
title: "CLM-Access"
nav: false
wide: true
description: "scATAC-seq 每个细胞可对应约 115 万个统一 cCRE，数据极度稀疏、近似二值，而且不同实验的 peak 坐标缺少统一词表。传统方法常先筛掉大部分 peak，损失调控信息并限制规模。 CLM-Access 将按染色体位置排序后的 cCRE 划分为约 2,000 个固定 patch，每个 patch 约含 575 个 peak。"
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
      <span>AAAI · 2026</span>
    </div>
    <h1>CLM-Access</h1>
    <p>CLM-Access: A Specialized Foundation Model for High-Dimensional Single-Cell ATAC-Seq Analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/HIM-AIM/CLM-Access" target="_blank" rel="noopener noreferrer" aria-label="Open code for CLM-Access">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CLM-Access 方法说明

### 要解决的问题

scATAC-seq 每个细胞可对应约 115 万个统一 cCRE，数据极度稀疏、近似二值，而且不同实验的 peak 坐标缺少统一词表。传统方法常先筛掉大部分 peak，损失调控信息并限制规模。

### 核心方法

CLM-Access 将按染色体位置排序后的 cCRE 划分为约 2,000 个固定 patch，每个 patch 约含 575 个 peak。每个 patch 同时有一个离散 token 和一个由二值 peak 向量线性投影得到的 value embedding；两者相加后，连同 `[CLS]` 输入双向 Transformer。预训练随机遮盖约 15% 的 peak-value 位置，解码器重建被遮盖的 peak，并用 peak-level BCE 学习。

```text
稀疏 cell x cCRE
 -> 统一 peak、排序、分 patch、padding、二值化
 -> token embedding + peak-value embedding
 -> Transformer/FlashAttention
 -> [CLS] 表示与 masked peak decoder
 -> BCE 重建
```

论文在 2.8M 人类细胞上预训练，报告批次校正、细胞类型注释、RNA 表达预测和 RNA/ATAC 多模态整合。RNA 预测 Pearson 为 0.9175；注释在 GSE219281 上 accuracy 为 0.7635。公开代码验证了 15% masking、FlashAttention、`-2` padding 忽略和 BCE 分支，但没有提供全部权重、补充材料和可直接复现论文表格的运行配置。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CLM-Access Summary

CLM-Access is a BERT-inspired foundation model for high-dimensional single-cell ATAC-seq. It addresses the million-scale cCRE vocabulary, extreme sparsity, binary counts, and lack of a universal peak annotation by mapping 2.8 million human cells to a unified cCRE reference, grouping peaks into fixed patches, and retaining every peak signal.

The key design is token/value dual embedding: each patch is a token while its padded, binarized peak vector is linearly embedded and added to the token embedding. A bidirectional Transformer models patch interactions, and masked peak reconstruction trains the representation with peak-level BCE. The public code confirms the 15% masking, FlashAttention encoder, `-2` padding exclusion, and downstream task heads, but does not include all paper assets or a turnkey reproduction script.

Ablations favor binarization, fine patches, peak-level BCE, and value-only masking. On reported benchmarks CLM-Access improves batch correction, cell annotation, RNA prediction (Pearson 0.9175 versus BABEL 0.9101 and MultiVI 0.8845), and multimodal integration. Limitations are human-only pretraining, unavailable supplementary details/checkpoints, and incomplete decoding of PDF equations.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
