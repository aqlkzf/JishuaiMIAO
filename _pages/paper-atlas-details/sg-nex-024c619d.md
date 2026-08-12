---
layout: default
permalink: /paper-atlas/sg-nex-024c619d/
title: "SG-NEx"
nav: false
description: "一个基因往往对应多个高度相似的转录本。短读长 RNA-seq 能稳定估计基因总表达量，却经常无法判断一条短片段究竟来自哪个异构体，尤其难以同时连接多个剪接位点。已有长读长数据集又常受样本少、重复不足、协议单一或测序深度有限的影响，因此很难公平比较技术差异。 SG-NEx 的目标不是提出一个新的预测模型，而是建立一个可复用、带匹配样本和对照的技术基准，回答：不同 RNA-seq 协议怎样影响读长、覆盖、基因表达、转录本定量和主要异构体判断？"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SG-NEx</h1>
    <p>A systematic benchmark of Nanopore long-read RNA sequencing for transcript-level analysis in human cell lines</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02623-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SG-NEx：长读长 RNA 测序的系统基准

### 这篇论文要解决什么问题？

一个基因往往对应多个高度相似的转录本。短读长 RNA-seq 能稳定估计基因总表达量，却经常无法判断一条短片段究竟来自哪个异构体，尤其难以同时连接多个剪接位点。已有长读长数据集又常受样本少、重复不足、协议单一或测序深度有限的影响，因此很难公平比较技术差异。

SG-NEx 的目标不是提出一个新的预测模型，而是建立一个可复用、带匹配样本和对照的技术基准，回答：不同 RNA-seq 协议怎样影响读长、覆盖、基因表达、转录本定量和主要异构体判断？

### 数据与实验设计

核心数据覆盖 7 种人类细胞系，每种主要协议至少有 3 个高质量重复：Nanopore 直接 RNA、无扩增直接 cDNA、PCR-cDNA，以及 Illumina 150 bp 双端短读长。部分样本还包含 PacBio IsoSeq、Sequin/ERCC/SIRV 等已知浓度 spike-in 和 m6ACE-seq。扩展后共有 14 种细胞系或组织、139 个文库。

```text
同源 RNA 样本 + 已知浓度 spike-in
        |
        +-- Nanopore direct RNA / direct cDNA / PCR-cDNA
        +-- PacBio IsoSeq
        +-- Illumina short-read
        |
        v
比对与转录本定量
        |
        +-- 产量、读长、5'/3'覆盖、剪接完整性
        +-- 基因表达和转录本表达
        +-- 每个基因的主要异构体
        |
        v
长读长计算截断实验 + RT-qPCR/dPCR 验证
```

### 计算流程

长读长使用 Minimap2 比对；Bambu、NanoCount 和 Salmon 估计长读长表达，Salmon 和 RSEM 估计短读长表达。不同工具的结果被整理为统一的转录本表，并用

$$
\mathrm{CPM}_{ts}=\frac{E_{ts}}{N_s}\times 10^6
$$

进行样本内标准化，其中 $E_{ts}$ 是转录本 $t$ 在样本 $s$ 的估计量，$N_s$ 是该样本的总估计计数。基因表达是同一基因全部转录本 CPM 的和。

论文把每个细胞系中平均表达最高的转录本定义为主要异构体，并分别用 Nanopore 长读长重复和短读长重复计算。因此每个异构体可归为：长短读长共同主要、长读长特异主要、短读长特异主要或次要异构体。

### 最关键的因果实验：把长读长“切短”

作者不是只比较两种技术，而是把完整长读长在计算机中随机切成 150 bp 片段：

1. 找到每条长读长在转录本上的主比对区间；
2. 在可用区间内均匀随机选择起点；
3. 按读长最多重复 $N\leq L/150$ 次；
4. 从参考转录本提取 150 bp 序列并生成 FASTQ；
5. 用 Salmon 重新定量；
6. 比较完整长读长、碎片化长读长和真实短读长。

结果显示，碎片化后转录本相关性下降、误差增加，而且估计值常向真实短读长结果移动。这说明短读长丢失跨多个剪接位点的连接信息，本身就是异构体定量差异的重要原因。

### 主要发现

- PCR-cDNA 产量高，但扩增会带来覆盖和转录本多样性偏差；direct RNA 存在明显的 3' 端覆盖偏向；PacBio 平均读长最长，但短转录本代表性不足。
- 基因层面相对稳健：蛋白编码基因跨协议相关性高，样本聚类主要由细胞系决定。
- 转录本层面差异明显：长读长跨越更多剪接位点，更容易唯一分配到一个转录本。
- 长读长特异主要异构体在技术间的一致性高于短读长特异主要异构体；后者常对应较短、使用内部首末外显子的版本。
- RT-qPCR 和 dPCR 对部分 MCF7 候选基因提供了独立验证。

### 代码与可复现性

论文链接的 `GoekeLab/sg-nex-data` 仓库包含论文分析脚本。`GenerateExpressionTable.R` 整理 Bambu/Salmon/NanoCount/RSEM 输出，`CombineExpressionAcrossMethods.R` 合并协议和方法，`run_trim_reads_sim.R` 实现长读长碎片化，`GetNumberOfJunctions.R` 统计每条读长覆盖的剪接位点，Figure R Markdown 文件生成主要图。

但该仓库是分析快照，不是一键运行的软件包：它依赖外部 S3/ENA 大数据、预先生成的 RDS/XLSX 文件和原始环境路径。nf-core/nanoseq 也在外部项目维护。因此可以较好追踪论文计算逻辑，但完整复现仍需重建环境和中间数据。

### 使用时应注意

这个基准同时比较了测序平台、建库和计算流程，不能把所有差异归因于单一因素；主要异构体标签依赖注释和定量工具；核心表达比较主要使用已注释转录本；补充材料中的新转录本、融合和 m6A 细节未在本工作区完整转换。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SG-NEx benchmark summary

### What problem does it solve?

Gene-level RNA abundance is often robust, but transcript-level abundance is hard to estimate because isoforms share exons and short reads rarely preserve long-range splice-junction linkage. Existing long-read datasets were commonly limited in throughput, replication, conditions or protocol coverage. SG-NEx provides a matched benchmark that can separate protocol behavior from biological variation and support development of isoform-aware computational methods.

### What was built?

The study profiles seven core human cell lines with replicated Nanopore direct RNA, direct cDNA and PCR-cDNA sequencing plus Illumina short-read RNA-seq; subsets also have PacBio IsoSeq, multiple known-concentration spike-ins and m6ACE-seq. The expanded resource contains 139 libraries across 14 cell lines or tissues. It is paired with public ENA/S3 data, a GitHub resource and the external community-curated nf-core/nanoseq processing pipeline.

### Main analysis

Reads are compared by yield, length, transcript-position coverage, splice completeness and assignment ambiguity. Gene and transcript abundances are estimated with Bambu, NanoCount, Salmon and RSEM, normalized across methods and benchmarked against spike-in concentrations. Major isoforms are defined independently for long- and short-read replicates as the highest-average-abundance transcript per gene. An in silico experiment fragments long reads into 150-bp pieces, re-quantifies them and tests whether lost linkage explains short-read-like estimates. Discordant MCF7 isoforms are further assessed by RT-qPCR and dPCR.

### Main findings

- Library preparation remains consequential: PCR-cDNA has high throughput but amplification-related coverage/diversity biases; direct RNA has a 3′ coverage bias; PacBio reads are longest but the study observes depletion of short transcripts.
- Gene expression is comparatively stable across technologies. Protein-coding genes show stronger agreement than long-noncoding genes, and samples cluster mainly by cell line.
- Transcript estimates are less stable. Long reads cover more junctions and are more often assigned uniquely, and long-read-specific major isoforms agree better across protocols than short-read-specific major isoforms.
- Fragmenting long reads reduces transcript-level correlation and shifts estimates toward short-read results, supporting a causal role for lost long-range information.
- The resource enables alternative-isoform, novel-transcript, fusion and direct-RNA m6A analyses beyond the benchmark itself.

### Reproducibility

Code-paper fidelity is **medium**. The paper-linked `GoekeLab/sg-nex-data` snapshot contains manuscript utilities and figure scripts that directly implement expression-table construction, cross-method normalization, junction counting and fragmentation simulation. However, it is not a turnkey pipeline: scripts contain environment placeholders and require large external BAM/FASTQ data plus precomputed RDS/XLSX inputs. The nf-core/nanoseq source is maintained externally and is not vendored in the snapshot. The full data are public through ENA accession `PRJEB44348` and AWS Open Data.

### Limitations

Protocol effects include both sequencing and library-preparation differences; PacBio has fewer runs; major-isoform calls depend on alignment, annotation and quantification; primary expression comparisons use annotated isoforms; and detailed alternative-transcript/fusion/m6A procedures are deferred to supplementary notes that were not locally converted.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
