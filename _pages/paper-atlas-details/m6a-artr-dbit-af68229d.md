---
layout: default
permalink: /paper-atlas/m6a-artr-dbit-af68229d/
title: "m6A-ARTR-DBiT"
nav: false
wide: true
description: "m6A-ARTR-DBiT 是一个把“原位 m6A 检测”和“DBiT 空间条形码”连接起来的空间表观转录组技术；论文完整描述了从组织切片到 Rm6A 空间分析的流程，但公开代码主要只复现 FASTQ 到 gene-by-pixel matrix 的预处理部分。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>m6A-ARTR-DBiT</h1>
    <p>Spatially resolved m6A profiling using m6A-ARTR-DBiT</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03123-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for m6A-ARTR-DBiT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/YXx-x23/m6A-ARTR-DBiT" target="_blank" rel="noopener noreferrer" aria-label="Open code for m6A-ARTR-DBiT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## m6A-ARTR-DBiT 方法中文解读

### 这篇文章要解决什么问题

m6A 是 RNA 上常见的化学修饰，和 RNA 代谢、基因表达调控有关。论文指出，已有 m6A 检测方法主要是 bulk 或单细胞层面的分析，不能保留组织中的原位空间结构，因此难以回答“某个组织区域里的 m6A 修饰如何分布”这类问题（`paper.md:21`）。

m6A-ARTR-DBiT 的目标是把 m6A 检测和空间条形码结合起来，在组织切片中做转录组范围的 m6A 空间测绘。它把 ARTR-seq 的原位反转录检测能力与 DBiT-seq 的确定性组织条形码技术组合在一起（`paper.md:21`, `paper.md:39-54`）。

### 核心思想

可以把整个方法理解为三层：

```text
分子识别层：m6A 抗体 + 二抗 + pAG-RTase 在组织中定位 m6A 位点
空间编码层：两轮垂直方向的 DBiT 微流控条形码给 cDNA 加空间坐标
计算分析层：测序 reads -> barcode/UMI -> 比对 -> 去重 -> 像素 x 基因矩阵 -> 峰、聚类、投影、Rm6A
```

第一层回答“哪些 RNA 附近有 m6A 信号”；第二层回答“这个信号来自组织的哪个空间像素”；第三层把测序 reads 转成可分析的空间 m6A 矩阵。

### 实验流程

#### 1. 在组织中识别 m6A

论文的方法从冷冻组织切片开始。组织经过固定、通透和封闭后，加入 m6A 一抗、荧光二抗和 pAG-RTase。pAG-RTase 会被抗体复合物招募到 m6A 附近，从而在组织内原位合成 cDNA（`paper.md:39`, `paper.md:177-183`）。

关键点是：RNA 不需要先从组织中抽提出来。反转录发生在组织原位，因此后续可以把 m6A 信号和空间位置联系起来。

#### 2. 原位反转录和生物素标记

反转录体系中包含 biotin-dUTP 和 biotin-dCTP，以及带随机碱基的 adapter-RT primer（`paper.md:183`）。这样生成的 cDNA 带有生物素，后面可以用链霉亲和素磁珠富集。反转录结束后，论文还会洗去未结合的 cDNA 和引物，以减少空间串扰（`paper.md:54`, `paper.md:183`）。

#### 3. DBiT 空间条形码

DBiT 部分使用两块微流控芯片。第一块芯片沿一个方向加入 barcode A，第二块芯片垂直加入 barcode B。每个空间像素由 A/B 两个条形码组合确定（`paper.md:54`, `paper.md:192-195`）。论文使用 50 微米或 20 微米通道宽度，分别用于常规空间图谱和更高分辨率的海马区域分析（`paper.md:168`, `paper.md:117`）。

因此，后续测序读段中需要解析出的关键信息是：

```text
空间 barcode A + 空间 barcode B + UMI + cDNA 序列
```

#### 4. 文库构建和测序

空间条形码完成后，组织被裂解，交联被逆转，核酸经过酚氯仿抽提和乙醇沉淀回收（`paper.md:198-201`）。随后 RNA 被消化，生物素化 cDNA 由链霉亲和素磁珠富集，再进行 3' adapter ligation、PCR 扩增、片段筛选和 Illumina paired-end 150 bp 测序（`paper.md:204-219`）。

### 计算流程

论文的 primary data processing 描述了从 FASTQ 到 gene-by-pixel matrix 的主流程：过滤 barcode linker 不正确的 reads，提取 UMI 和空间 barcode，修剪 R1，用 Bowtie2 去除 rRNA reads，用 STAR 比对到基因组，用 UMI-tools 去 PCR duplicate，并按空间 barcode 生成 gene-by-pixel 表达矩阵（`paper.md:267-270`）。

公开代码确实覆盖了这段预处理流程：

| 步骤 | 代码行为 | 证据 |
|---|---|---|
| 过滤 linker 正确的 FASTQ | 两轮 `bbduk.sh` 用固定 linker 序列过滤 paired reads | `1_fastq_filter.sh:7-27` |
| 提取空间 barcode 和 UMI | Python 生成 `seq1[22:30] + seq1[60:68] + seq2[0:8]` | `2_fastq_processing.py:18-24` |
| 用 UMI-tools 解析 barcode/UMI | 正则解析 16 nt cell barcode 和 8 nt UMI | `3_fastq_processing_2.sh:6-13` |
| 修剪 R1 | Cutadapt 去 adapter、做质量和长度过滤 | `3_fastq_processing_2.sh:15-17` |
| 去除 rRNA | Bowtie2 比对到 rRNA reference，把 unmapped reads 留给后续 | `4_alignment.sh:11-20` |
| 基因组比对 | STAR 输出排序 BAM | `4_alignment.sh:22-42` |
| 基因计数和去重 | featureCounts 标注基因，UMI-tools group/dedup/count | `5_count_matrix_prepare.sh:6-31` |

这说明公开仓库主要支持“测序预处理到矩阵生成”，不是完整复现论文所有图的分析代码。

### 下游分析：论文有描述，但公开代码没有找到

#### 峰识别

论文说会把每个 library 的 reads 按正负链分成两个 BAM，用 MACS3 识别 peaks，再用 signal value 和 q-value 过滤；Guitar 用于 meta distribution，HOMER 用于 motif，ChIPseeker 用于 peak annotation（`paper.md:273-276`）。

**代码状态：Not found。** 克隆仓库中没有 MACS3、Guitar、HOMER 或 ChIPseeker 脚本。

#### 空间归一化和聚类

论文使用 Seurat V4：`SCTransform` 按像素归一化，`RunPCA` 降维，`FindNeighbors` 建图，`FindClusters` 聚类，`RunUMAP` 可视化，`FindMarkers` 找 cluster marker（`paper.md:279-282`）。

**代码状态：Not found。** 仓库中没有 R 脚本、notebook 或 Seurat 调用。

#### scRNA-seq 整合和标签迁移

论文用 Seurat anchor-based integration，把 m6A-ARTR-DBiT 像素和参考 scRNA-seq 数据整合。`FindTransferAnchors` 找 anchors，`TransferData` 把参考细胞类型标签以概率形式转移到空间像素上（`paper.md:285-288`）。这支撑了 E11 胚胎和脑组织中的细胞类型解释（`paper.md:72`, `paper.md:81`）。

**代码状态：Not found。**

#### Visium 投影和 RNA 归一化

在脑组织分析中，论文把 10x Genomics Visium 空间转录组作为 reference，把 m6A-ARTR-DBiT 作为 query，用 `FindTransferAnchors` 的 `pcaproject` 设置和 `TransferData` 把 Visium cluster 投影到 m6A 像素上，用于 RNA abundance normalization（`paper.md:291-294`）。结果中报告了 median prediction accuracy score = 0.77（`paper.md:96`）。

**代码状态：Not found。**

### Rm6A 是什么

论文定义 Rm6A 为相对 m6A 丰度。m6A-ARTR-DBiT 的信号用 RPKM 归一化，因为它捕获的是整条 transcript 上的 m6A 信号，需要同时校正测序深度和 transcript 长度；Visium RNA 用 RPM 归一化，因为 Visium 主要捕获 3' 端，主要校正测序深度（`paper.md:111`, `paper.md:297-300`）。

```text
Rm6A = m6A-ARTR-DBiT RPKM / Visium RNA RPM
```

论文用 Rm6A 比较不同脑区内外的像素，并用 Wilcoxon rank-sum test 评估差异（`paper.md:300`）。结果中，六个脑区的 m6A RPKM 与 RNA RPM Spearman 相关系数为 0.63 到 0.81，并用 `Nrg1`、`Pcdh9`、`Gabrb2` 等基因展示区域相关的相对 m6A 差异（`paper.md:111`）。

**代码状态：Not found。** 仓库中没有 Rm6A、RPKM/RPM 比值或 Wilcoxon 分析代码。

### Effective library size 公式

论文用 Lander-Waterman 模型估计 effective library size `X`，输入是 observed unique reads `C` 和 sequencing depth `N`（`paper.md:303-306`）：

$$C=X\times \left(1-{e}^{-\frac{N}{X}}\right)$$

论文给了一个 R `uniroot` 片段来求解 `X`（`paper.md:312-315`）。直观上，这个公式是在问：如果真实可采样分子池大小是 `X`，测序深度是 `N`，在泊松采样假设下应该观察到多少 unique reads `C`。

**代码状态：Not found。** 公开仓库没有 R 文件或对应实现。

### 结果如何支持方法

论文先在细胞中验证 ARTR-seq 模块：pAG-RTase 与二抗共定位、replicate 相关性高、peak overlap 高、motif 为 RRACU、`Mettl3` CKO 后 m6A/A 比例和 m6A read density 下降（`paper.md:45-51`）。本地 Fig. 1 图片直接可见这些验证面板，包括 workflow schematic、免疫荧光、`R = 0.998` 的 replicate 图、motif logo 和 `Mettl3` control/CKO read-density tracks。

在 E11 小鼠胚胎中，论文报告平均每个像素检测到 2,359 个 UMI 和 1,594 个基因，并识别出 16 个空间 cluster（`paper.md:72`）。在成年小鼠脑中，平均每 50 微米像素检测到 2,489 个 UMI 和 1,664 个基因，识别 20 个空间 cluster，并用 iStar 生成更高分辨率的空间 m6A 图谱（`paper.md:81`）。在海马区域，20 微米芯片解析出 7 个 cluster，其中 cluster 6 和 7 对应 CA1sp 与 DG-sg 结构（`paper.md:117`）。

### 局限性

- 论文层面：抗体检测可能受到 m6A 结合蛋白竞争影响；作者也提出未来可以同时 profiling m6A regulatory protein binding sites（`paper.md:132`）。
- 检测层面：tRNA 和 snoRNA 等短非编码 RNA 捕获有限，论文认为原因包括长度短和二级结构复杂（`paper.md:48`）。
- 代码层面：公开仓库只覆盖预处理到矩阵，缺少 peak calling、Seurat、projection、Rm6A、effective library size 和大部分 figure-level 分析代码。
- 运行层面：脚本包含 `your_path`、`your_sample`、`genome_build` 等占位符，并且 `4_alignment.sh` 中 `bw2.mrRNA` 与 `bw2mrRNA` 路径不一致，实际运行前需要人工检查（`4_alignment.sh:8-20`, `4_alignment.sh:42`）。

### 一句话总结

m6A-ARTR-DBiT 是一个把“原位 m6A 检测”和“DBiT 空间条形码”连接起来的空间表观转录组技术；论文完整描述了从组织切片到 Rm6A 空间分析的流程，但公开代码主要只复现 FASTQ 到 gene-by-pixel matrix 的预处理部分。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Problem

m6A RNA modification is spatially patterned across tissues, but the paper argues that existing bulk and single-cell m6A assays lose native tissue architecture (`paper.md:21`). m6A-ARTR-DBiT is introduced to map transcriptome-wide m6A distributions while preserving spatial context, by combining ARTR-seq in situ reverse-transcription detection with DBiT deterministic tissue barcoding (`paper.md:21`, `paper.md:39-54`).

### Method

The assay fixes and permeabilizes a tissue section, targets m6A sites with an m6A antibody plus secondary antibody and pAG-RTase, synthesizes biotinylated cDNA in situ, ligates orthogonal DBiT barcodes through 50-micrometer or 20-micrometer microfluidic channels, recovers and enriches cDNA, constructs sequencing libraries, and processes reads into spatial m6A profiles (`paper.md:177-219`). Computationally, the paper describes FASTQ filtering, barcode/UMI extraction, trimming, rRNA removal, STAR alignment, UMI deduplication, count matrix generation, peak calling, Seurat clustering/integration/projection, Rm6A analysis, and effective-library-size estimation (`paper.md:267-315`).

### Evaluation And Results

The validation data show that ARTR-seq recovers known m6A features: antibody/pAG-RTase co-localization, high replicate agreement, RRACU motif enrichment, reduced m6A/A after `Mettl3` knockout, and reduced read density at eTAM-seq sites after `Mettl3` CKO (`paper.md:45-51`; local `figure_01.png`). Applied to E11 mouse embryo, the method reports 2,359 UMIs and 1,594 genes per pixel on average, 16 spatial clusters, and scRNA-seq reference-based annotation (`paper.md:72`). Applied to mouse brain, it reports 2,489 UMIs and 1,664 genes per 50-micrometer pixel, 20 spatial clusters, super-resolution with iStar, Allen Brain Atlas agreement, and cell-type validation by scRNA-seq integration (`paper.md:81-90`). The paper further compares m6A with spatial RNA expression via Visium projection, reports median projection accuracy of 0.77, defines Rm6A as m6A RPKM divided by RNA RPM, and identifies region-associated relative m6A signals (`paper.md:96-111`).

### Reproducibility

Raw and processed sequencing data are deposited under GEO accessions GSE285303 and GSE285304, with additional reference m6A and spatial datasets listed in the paper (`paper.md:330-333`). The public GitHub repository at commit `1464ca5e0882ae8d550fb416c94e75d15ea36aed` contains five scripts and a README for the primary preprocessing path: linker filtering, barcode/UMI extraction, Cutadapt trimming, Bowtie2 rRNA removal, STAR alignment, featureCounts assignment, UMI-tools deduplication, and gene-by-pixel matrix generation (`doc_code.md`). The code-paper fidelity is **low-to-medium / partial** because downstream peak calling, Seurat clustering/integration/projection, Rm6A analysis, BigWig/profile generation, and effective-library-size code were not found in the cloned repo.

Reproducibility rating: **2/5 for full paper reproduction; 3/5 for raw-read-to-count-matrix preprocessing**. The main blocker is missing downstream analysis code, not absence of data or paper method detail.

### Main Limitations

- Paper-level: antibody-based detection may be affected by m6A regulatory proteins, and short noncoding RNAs such as tRNAs/snoRNAs are difficult to capture (`paper.md:48`, `paper.md:132`).
- Code-level: released scripts are small, placeholder-driven, and not directly turnkey; one alignment script has a likely `bw2.mrRNA` versus `bw2mrRNA` path inconsistency (`doc_code.md`).
- Evidence-level: local main figure images for Figs. 2-5 were not retained in this workspace, so `figure_analysis.md` marks them as paper/caption-supported rather than image-inspected.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
