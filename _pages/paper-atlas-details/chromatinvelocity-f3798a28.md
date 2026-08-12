---
layout: default
permalink: /paper-atlas/chromatinvelocity-f3798a28/
title: "ChromatinVelocity"
nav: false
description: "传统单细胞 ATAC-seq 主要读取开放染色质，但对紧缩的异染色质覆盖不足。论文指出，异染色质可占基因组很大比例，并且和细胞身份、基因组稳定性、癌症耐药等过程有关。因此，作者想解决两个问题： 如何在单细胞水平同时读取开放染色质和紧缩染色质？ 如何像 RNA velocity 那样，从染色质状态推断细胞沿发育或重编程路径的“未来方向”？ 论文提出两个连在一起的方法： scGET-seq：把普通 Tn5 与工程化的 TnH 联合使用。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Biotechnology · 2022</span>
    </div>
    <h1>ChromatinVelocity</h1>
    <p>Chromatin Velocity reveals epigenetic dynamics by single-cell profiling of heterochromatin and euchromatin</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-021-01031-1" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Chromatin Velocity / scGET-seq 方法中文解读

### 这篇文章要解决什么问题？

传统单细胞 ATAC-seq 主要读取开放染色质，但对紧缩的异染色质覆盖不足。论文指出，异染色质可占基因组很大比例，并且和细胞身份、基因组稳定性、癌症耐药等过程有关（`paper source/nature_html/paper.md:24-29`）。因此，作者想解决两个问题：

1. 如何在单细胞水平同时读取开放染色质和紧缩染色质？
2. 如何像 RNA velocity 那样，从染色质状态推断细胞沿发育或重编程路径的“未来方向”？

### 核心创新

论文提出两个连在一起的方法：

- **scGET-seq**：把普通 Tn5 与工程化的 TnH 联合使用。TnH 是 HP-1α chromodomain 与 Tn5 的融合蛋白，可以更好地接触 H3K9me3 相关的紧缩染色质；普通 Tn5 更偏向开放染色质（`paper.md:42-65`）。
- **Chromatin Velocity**：把 Tn5/TnH 信号比值类比为 RNA velocity 里的 unspliced/spliced 比值。Tn5/TnH 上升被解释为染色质更开放，反向则解释为染色质压缩（`paper.md:199-204`）。

### 输入与输出

**输入**：scGET-seq 原始测序 reads、Tn5/TnH 特异 barcode、细胞 barcode、DHS 区域或基因组 bin、可选的 TF motif/PWM 数据。

**输出**：

- 单细胞 Tn5/TnH 计数矩阵；
- 每个细胞的开放/紧缩染色质表示；
- CNV/SNV 和克隆结构分析；
- Chromatin Velocity 向量、velocity pseudotime 和高似然动态区域；
- 基于 TBA/PWM 的 TF dynamic score。

### 计算流程

```text
scGET-seq raw reads
  |
  |-- 按 Tn5/TnH barcode 拆分 reads
  v
每种 transposase 的 FASTQ/BAM
  |
  |-- 细胞 barcode 赋值 + 去重复
  v
细胞级 deduplicated BAM
  |
  |-- 在 DHS/基因组区域上计数
  v
Tn5 与 TnH count matrices
  |
  |-- filtering / normalization / log transform / scaling
  v
scanpy/AnnData 表示 + KNN/cluster/fusion
  |
  |-- 把 Tn5/TnH 放入 velocity 风格 layers，运行 scvelo dynamical model
  v
Chromatin Velocity 向量和动态区域
  |
  |-- motif/TBA + PLS 分析
  v
TF 动态程序和生物学解释
```

### 关键步骤解释

#### 1. 用 Tn5 + TnH 同时读取开放和紧缩染色质

作者先证明如果把 Tn5 正确引导到 H3K9me3 区域，它可以切割紧缩染色质；随后用 HP-1α 的 chromodomain 与 Tn5 融合，构建 TnH，并筛选出效果最好的 TnH 3（`paper.md:33-57`）。最终方案是先用 native Tn5，再用 TnH，并通过特异 barcode 区分两个酶产生的片段（`paper.md:59-65`）。

#### 2. 预处理和矩阵构建

论文 Methods 写明：用 `bc2rg.py` 将 accepted cellular barcodes 赋给 reads，用 `cbdedup.py` 在细胞水平去重复，用 scatACC 的 `peak_count.py` 生成 count matrices（`paper.md:397-403`）。本地代码与这一点吻合：

- `scGET/modules/scget_wf.smk:1-35` 配置 Tn5/TnH barcode；
- `scGET/modules/scget_wf.smk:48-65` 用 tagdust 按 barcode 拆分 reads；
- `scGET/modules/scget_wf.smk:139-153` 将 `bc2rg.py` 管道连接到 `cbdedup.py`；
- `scGET/modules/scget_wf.smk:176-211` 调用 scatACC 的计数流程；
- `scGET/scripts/tn_layers.py:6-38` 生成 `tn5` 和 `tnH` layers。

论文每个实验生成四类矩阵：`Tn5-dhs`、`Tn5-complement`、`TnH-dhs`、`TnH-complement`（`paper.md:397-403`）。这些矩阵支撑后续聚类、CNV 和 velocity 分析。

#### 3. Chromatin Velocity 的核心思想

在 Chromatin Velocity 中，作者先过滤到 Tn5/TnH 共有 DHS 区域，然后创建一个类似 RNA velocity 的对象：把 Tn5 与 TnH 数据放入 velocity 模型使用的 layers，计算 KNN graph 上的 moments，再用 scvelo dynamical modeling，最后用 latent time regularization 得到 velocity（`paper.md:460-464`）。

这一步的直觉是：

- Tn5 信号变强：染色质趋向开放；
- TnH 信号相对变强：染色质趋向压缩；
- Tn5/TnH 的动态变化可以给出细胞状态转变方向。

#### 4. TF dynamic score

为了解释 velocity 背后的调控因子，作者对高似然动态 DHS 区域提取 500 bp 序列，使用 HOCOMOCO v11 PWM 计算 total binding affinity (TBA)，再将 region-by-TBA 矩阵与 cell-by-region velocity 矩阵相乘，得到 cell-by-TF 的动态分数（`paper.md:472-478`）。本地 `scatACC/tba_nu.py:8-122` 实现了 PWM 解析、正反向序列 affinity 计算以及 TBA 聚合。

### 主要实验结果

- scGET-seq 可以区分 HeLa/Caki-1 混合细胞，并恢复预期比例的 cell identity（`paper.md:77-91`）。
- 由于 TnH 读取更多基因组区域，scGET-seq 在 CNV 推断上比 scATAC/Tn5-only 信号更稳定，分辨率可到 500 kb（`paper.md:94-109`）。
- 在 organoid 和 PDX 模型中，scGET-seq 能同时反映遗传克隆、表观遗传亚克隆、治疗相关异质性和 SNV（`paper.md:112-144`）。
- 在 FIB/iPSC/NPC 发育数据中，Chromatin Velocity 给出类似 RNA velocity 的方向场，并找到神经发育相关动态区域和 TF 程序（`paper.md:199-222`）。

### 代码可复现性评价

论文 Code availability 指向 `https://github.com/leomorelli/scGET` 和 `https://github.com/dawe/scatACC`，并说明 postprocessing snippets 在 Supplementary Data 2 中（`paper.md:493-496`）。本工作区已克隆两个 repo。代码对 **scGET 预处理** 支持较好，但在克隆 repo 中没有找到完整的 Chromatin Velocity/scvelo 后处理脚本。因此，本论文的复现性可概括为：预处理可复现性中等偏高；最终 Figure 6 的 velocity 动态模型和图形复现需要额外 supplementary snippets 与数据。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Chromatin Velocity reveals epigenetic dynamics by single-cell profiling of heterochromatin and euchromatin

### Problem

Single-cell ATAC-seq profiles accessible chromatin, but it largely misses compacted heterochromatin, which the paper notes can encompass up to half of the genome and carries important regulatory and genomic information (`paper source/nature_html/paper.md:24-29`). The authors also want a way to convert single-cell chromatin-state measurements into directional dynamics, analogous to RNA velocity.

### Proposed Method

The paper introduces **scGET-seq** and **Chromatin Velocity**. scGET-seq combines native Tn5 with an engineered HP-1α chromodomain--Tn5 hybrid (**TnH**) so the same single-cell assay can capture accessible/open and compacted/H3K9me3-associated chromatin (`paper.md:42-74`). Chromatin Velocity then treats the Tn5/TnH relationship like the unspliced/spliced relationship in RNA velocity: an increasing Tn5/TnH ratio indicates relaxation/opening, whereas the opposite indicates compaction (`paper.md:199-204`).

### Method Overview

1. Use transposase-specific barcoded oligos to distinguish Tn5 and TnH products.
2. Run droplet-based single-cell processing, assigning reads to cell barcodes and deduplicating them.
3. Generate count matrices over DHS regions and complementary genomic regions: `Tn5-dhs`, `Tn5-complement`, `TnH-dhs`, and `TnH-complement` (`paper.md:397-403`).
4. Normalize/filter/scale matrices, build batch-balanced KNN graphs, cluster cells, and fuse multiple views with scikit-fusion (`paper.md:397-403`).
5. For Chromatin Velocity, keep common DHS regions, inject Tn5/TnH matrices into velocity-style layers, calculate scvelo moments and dynamical model, and regularize final velocity by latent time (`paper.md:460-464`).
6. Interpret high-likelihood dynamic regions with gene-set enrichment and TF dynamic scores computed from HOCOMOCO PWM/TBA matrices (`paper.md:472-478`).

### Evaluation and Main Claims

- scGET-seq separates mixed HeLa/Caki-1 cells and captures cell identity (`paper.md:77-91`).
- TnH-derived scGET-seq signal improves copy-number profiling over scATAC/Tn5-only signal at multiple resolutions (`paper.md:94-109`).
- In organoids and PDX models, scGET-seq jointly captures genetic clones, epigenetic subclones, treatment-associated heterogeneity, and SNVs (`paper.md:112-144`).
- In FIB/iPSC/NPC developmental data, Chromatin Velocity produces directional flows on a UMAP, identifies 1,703 high-likelihood dynamic DHS regions enriched for neural morphogenesis, and derives TF dynamic programs (`paper.md:199-222`).

### Code and Reproducibility

The paper states that preprocessing code is available in `https://github.com/leomorelli/scGET` and `https://github.com/dawe/scatACC`, while illustrative postprocessing snippets are in Supplementary Data 2 (`paper.md:493-496`). This workspace clones both repositories. The local code matches preprocessing well: `scGET/modules/scget_wf.smk:139-153` runs `bc2rg.py | cbdedup.py`; `scGET/modules/scget_wf.smk:176-211` performs interval counting; `scGET/scripts/tn_layers.py:6-38` builds `tn5` and `tnH` AnnData layers; `scatACC/tba_nu.py:8-122` implements TBA/PWM scoring.

The full Chromatin Velocity scvelo postprocessing script is **Not found** in the cloned repositories after searching `scGET/` and `scatACC/` for scvelo/velocity/layer terms. Thus, reproducibility is **medium**: raw scGET preprocessing is supported by code, but complete Figure 6 reproduction requires supplementary postprocessing snippets and datasets not represented as local source code.

### Reproducibility Rating

**3/5** — strong source/code support for scGET preprocessing and TBA utility; partial support for Tn5/TnH layer construction; missing direct source for the final Chromatin Velocity scvelo analysis and figure-generation workflow.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
