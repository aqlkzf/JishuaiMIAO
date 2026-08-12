---
layout: default
permalink: /paper-atlas/dechic-seq-b7a036a3/
title: "DeChIC-seq"
nav: false
description: "在单细胞层面定位组蛋白修饰和转录因子（TF）结合很困难。ChIP-seq、CUT&RUN 与 CUT&Tag 等技术依赖富集或片段化；TF 信号本身稀疏，低输入时尤为不利。DamID 类方法又受 GATC 位点分布限制，而直接读取甲基化的长读长方法通常需要较多 DNA。 DeChIC-seq 使用抗体识别目标组蛋白修饰或蛋白，再通过 protein A 把 pA-DddA 招募到该处。DddA 在邻近 DNA 上把 C 脱氨为 U；"
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
      <span>Technology Platforms</span>
      <span>Cell Research · 2026</span>
    </div>
    <h1>DeChIC-seq</h1>
    <p>Genome-wide profiling of histone modifications and transcription factor binding at single-cell resolution by DeChIC-seq</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DeChIC-seq 方法解读

### 它要解决什么问题？

在单细胞层面定位组蛋白修饰和转录因子（TF）结合很困难。ChIP-seq、CUT&RUN 与 CUT&Tag 等技术依赖富集或片段化；TF 信号本身稀疏，低输入时尤为不利。DamID 类方法又受 GATC 位点分布限制，而直接读取甲基化的长读长方法通常需要较多 DNA（`paper.md:21-33`）。

### 核心想法：把结合事件写进 DNA

DeChIC-seq 使用抗体识别目标组蛋白修饰或蛋白，再通过 protein A 把 pA-DddA 招募到该处。DddA 在邻近 DNA 上把 C 脱氨为 U；PCR 时 U 被读成 T。因此，测序中的 C-to-T 信号成为目标附近的“化学记录”。scDeChIC-seq 在此后接入单细胞全基因组扩增（WGA）（`paper.md:45`, `paper.md:53`）。

```text
目标抗体 + 染色质
  -> pA-DddA 局部定位
  -> C -> U
  -> DNA 提取、Tn5 建库、PCR（U 读为 T）
  -> 比对与 TC 位点计数
  -> 转换率轨道与峰
  -> 单细胞：peak x cell 矩阵、聚类/占据率
```

作者还利用 pH 控制 pA-DddA：pH 8.0 Tris-HCl 抑制活性，pH 6.4 MES 重新激活，目的在于先完成特异性结合、再进行转化（`paper.md:56`）。

### 计算量是什么？

每个被覆盖的 TC 位点定义为

$$
r_i = \frac{T_i}{C_i + T_i}.
$$

峰的信号是覆盖 TC 位点转换率的平均值（`paper.md:387-390`）。这不同于以片段富集数为主的 ChIP 信号：它反映的是可测位点上已发生转换的比例。

本地 SCENE 代码可核实这一层：`basalkit_functions_filterTC.py:306-386` 输出 C/CT 计数并计算 `ratio_mr = m_mr / d`；前面的读取逻辑按序列上下文计数，并可进行反向链 SNP 处理（`:219-291`）。

### 从转换率到生物学结论

1. **建轨道与找峰**：论文用 IgG 或 pseudo-IgG 对照进行峰调用（`paper.md:399-411`）。SCENE 生成平均 pseudo-IgG、用 Metilene 比较 target/control、按阈值过滤，再合并并去除 blacklist 区域（`SCENE/modules/callpeak.snakefile:111-180`）。
2. **单细胞矩阵**：以 pooled data 的 peaks 为行、细胞为列，在每个 peak 内对被覆盖位点的转换率求均值；覆盖不足则缺失（`paper.md:414-417`; `SCENE/modules/cellMatrix.snakefile:57-131`）。
3. **占据率**：SCENE 可过滤低检测率及 TC+GA 密度过高区域，再将高于 rate cutoff 的细胞记为阳性，输出阳性细胞比例（`SCENE/modules/peakPresence.snakefile:23-99`）。

### 论文展示了什么？

在 MEF 中，作者报告 H3K4me3 DeChIC-seq 与 ChIP-seq 共享 26,092 个峰；CTCF 实验报告 29,638 个 DeChIC-seq 峰，其中 76.33% 与 ChIP-seq 峰重叠（`paper.md:65`, `paper.md:77`）。主图还展示了胚胎中的 H3K4me3、CTCF、RAD21 以及 NR5A2、TFAP2C、KLF5 等 TF 的低输入应用（`paper.md:12`, `paper.md:126-218`）。

### 可复现性边界

代码快照支持“转换率、峰、矩阵、占据率”这些处理环节，但本地未找到论文所述 Signac/Seurat 聚类和注释流程，故这一部分为 **Not found**（搜索范围：`DeChIC/SCENE`）。文章链接了补充 PDF，但本工作区没有 `SUPP_MD`，因此具体实验参数和全部 target-specific 阈值仍是 **MISSING**（`paper.md:703-715`）。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## DeChIC-seq: conversion-based chromatin profiling

### Problem

Single-cell chromatin assays can struggle with sparse transcription-factor binding because conventional ChIP/CUT-style workflows depend on fragment enrichment or chromatin fragmentation; DamID-like approaches have sequence-context limits, and direct long-read modification detection needs substantial input DNA (`paper.md:21-33`).

### Contribution

DeChIC-seq tethers protein A-DddA to antibody-selected chromatin. Local C-to-U deamination is read as C-to-T after PCR, producing a TC-context conversion-rate signal without immunoprecipitating the marked fragments. scDeChIC-seq adds single-cell WGA and derives peak-by-cell conversion profiles (`paper.md:45`, `paper.md:372-417`).

### Evidence and evaluation

The paper reports 26,092 shared H3K4me3 peaks between DeChIC-seq and ChIP-seq in MEFs, representing 88.02% of DeChIC-seq calls, and reports 29,638 CTCF DeChIC-seq peaks from $5 \times 10^3$ MEFs with 76.33% overlap with CTCF ChIP-seq (`paper.md:65`, `paper.md:77`). Six inspected main figures show the assay workflow, bulk comparisons with ChIP-seq/CUT&Tag, single-cell workflow and embeddings, embryonic H3K4me3/CTCF analyses, and TF applications. In mouse preimplantation embryos, the authors apply scDeChIC-seq to H3K4me3, CTCF, RAD21, and limited-input TF profiling (`paper.md:12`, `paper.md:126-218`).

### Reproducibility

The author-linked GitHub snapshot contains a SCENE workflow that directly implements TC-aware conversion-rate output, control-aware peak calling, peak-by-cell averaging, and rate-thresholded peak prevalence. Paper-code fidelity is **medium**: these computational primitives match the described workflow, but target-specific settings and the Signac/Seurat clustering/annotation workflow are not established by the local source. Supplementary PDFs are linked but no local supplement markdown exists (`paper.md:510-513`, `paper.md:703-715`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
