---
layout: default
permalink: /paper-atlas/gptcelltype-44d43be1/
title: "GPTCelltype"
nav: false
wide: true
description: "单细胞 RNA 测序的细胞类型注释通常依赖专家比较 marker gene，并维护组织特异性的参考数据。本文考察：如果只把标准 Seurat/Scanpy 流程已经产生的 marker gene 或差异基因交给 GPT-4，它能否直接给出可靠的细胞类型标签。 GPTCelltype 是一个 R 软件包。它不训练新的神经网络，也不在本地建立参考图谱，而是把每个细胞群的基因列表组织成自然语言 prompt，调用 GPT-4 或 GPT-3."
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Methods · 2024</span>
    </div>
    <h1>GPTCelltype</h1>
    <p>Assessing GPT-4 for cell type annotation in single-cell RNA-seq analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02235-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GPTCelltype">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Winnie09/GPTCelltype" target="_blank" rel="noopener noreferrer" aria-label="Open code for GPTCelltype">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GPT-4 单细胞类型注释方法说明

### 研究问题

单细胞 RNA 测序的细胞类型注释通常依赖专家比较 marker gene，并维护组织特异性的参考数据。本文考察：如果只把标准 Seurat/Scanpy 流程已经产生的 marker gene 或差异基因交给 GPT-4，它能否直接给出可靠的细胞类型标签（`paper.md:25-45`）。

### 核心想法

GPTCelltype 是一个 R 软件包。它不训练新的神经网络，也不在本地建立参考图谱，而是把每个细胞群的基因列表组织成自然语言 prompt，调用 GPT-4 或 GPT-3.5。可选的 `tissuename` 为模型提供组织背景；没有 API key 时，函数只返回 prompt，便于人工检查（`code/R/gptcelltype.R:31-50`）。

### 输入、处理与输出

```text
表达矩阵
  -> 标准 Seurat/Scanpy 预处理
  -> cluster 与差异基因
  -> GPTCelltype 组织 marker 行和组织名称
  -> GPT chat completion
  -> 按换行拆分并检查行数
  -> 每个 cluster 一个细胞类型标签
```

函数支持两种输入：

1. 命名的 gene list：每个元素代表一个细胞群，基因被逗号连接。
2. `FindAllMarkers()` 风格的数据表：保留 `avg_log2FC > 0` 的基因，按 `cluster` 分组，并取前 `topgenenumber` 个基因（`code/R/gptcelltype.R:40-45`）。

基本 prompt 要求“每一行只返回一个细胞类型名称”，并允许混合细胞类型。代码把多个群体用换行分隔；有 API key 时按最多约 30 个群体分批调用 `openai::create_chat_completion()`，再把回答按换行拆开。若回答行数与输入群体数不一致，代码会重试（`code/R/gptcelltype.R:47-77`）。

### 论文评价

作者使用十个数据集，覆盖五个物种、正常与癌症组织及数百种细胞/组织类型。手工标签和模型标签先映射到 Cell Ontology 及 broad cell type，再按 fully match = 1、partially match = 0.5、mismatch = 0 计算平均 agreement score（`paper.md:47-55,146-150`）。十个差异基因和双侧 Wilcoxon 检验通常最优；GPT-4 在多数研究/组织中对超过 75% 的细胞类型达到完全或部分匹配，并优于 GPT-3.5、SingleR、ScType 与 CellMarker2.0（`paper.md:58-82`）。模拟实验中，混合/单一细胞类型识别准确率为 93%，已知/未知类型识别准确率为 99%；相同 marker 重复查询的可重复性为 85%（`paper.md:83-90`）。

### 如何理解结果与风险

模型对 granulocyte 等免疫细胞和主要细胞类型较强，对很小的群体、细分亚型、噪声 marker 及部分 B lymphoma 较弱。GPT-4 的训练语料不透明，输出可能有 hallucination，作者因此要求下游分析前由专家复核（`paper.md:64-94`）。API 成本由输入/输出 token 数决定：`$(0.00003*i* + 0.00006*o*)`（`paper.md:175-179`）。

### 代码与论文的边界

GitHub 快照直接验证了用户-facing 的 R 注释函数、prompt、API 调用、分批和解析逻辑；但没有十个数据集的下载、模拟、ontology 评分或图复现脚本。论文还指向一个单独的 Zenodo reproduction repository，因此当前代码复现度应标为中等，而不是端到端完全可复现（`paper.md:224-225`）。代码的重试循环没有最大次数或退避策略，模型持续返回错误行数时可能无限等待（`code/R/gptcelltype.R:61-72`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Assessing GPT-4 for Cell Type Annotation

### Problem

Cell-type annotation in scRNA-seq remains expert-intensive: analysts inspect cluster markers, consult canonical marker knowledge, and often build or maintain tissue-specific reference workflows. Hou and Ji test whether GPT-4 can turn marker genes already produced by standard Seurat/Scanpy pipelines into useful labels without a reference atlas (`paper.md:25-45`).

### Proposed Method

GPTCelltype is an R interface that accepts marker lists or positive differential genes, embeds each population as a row in a constrained natural-language prompt, and sends the prompt to GPT-4 or GPT-3.5. It returns one label per row, supports tissue context and prompt-only inspection, and integrates with Seurat (`paper.md:112-123`; `code/R/gptcelltype.R:31-77`).

### Evaluation

The paper evaluates ten datasets spanning five species, normal and cancer tissues, and hundreds of tissue/cell types. Labels are compared with manual annotations using Cell Ontology and broad-type matching: full = 1, partial = 0.5, mismatch = 0. GPT-4 performs best with ten two-sided-Wilcoxon differential genes; it fully or partially matches manual labels for more than 75% of cell types in most studies, outperforms GPT-3.5, SingleR, ScType, and CellMarker2.0, and is faster in the reported comparisons (`paper.md:47-82`). Simulations report 93% mixed/single discrimination, 99% known/unknown discrimination, and 85% repeated-response reproducibility (`paper.md:83-90`).

### Limitations

Performance falls for small populations, fine subtypes, noisy or incomplete marker sets, and some malignant/lymphoma cases. GPT-4's undisclosed training data, optional human refinement, stochastic responses, and hallucination risk make expert review mandatory (`paper.md:91-94`). API cost is token-based and grows with the number of queried cell types (`paper.md:175-179`).

### Reproducibility

The acquired Nature HTML is complete and includes two local main figures. The linked GitHub package at commit `3d2785aa96ab5f260dd075b688a9fa51654cdf0d` verifies the core R function, prompt text, API call, batching, response parsing, and no-key mode. It does **not** include the ten-dataset benchmark, simulation, ontology-scoring, or figure-reproduction scripts; the paper points to a separate Zenodo reproduction repository (`paper.md:224-225`). The package's unbounded retry loop is an implementation caveat (`code/R/gptcelltype.R:61-72`). Overall code-paper fidelity is **medium**: the user-facing method is directly matched, while the published analysis is not end-to-end runnable from the cloned snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
