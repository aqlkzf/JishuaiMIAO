---
layout: default
permalink: /paper-atlas/longcallr-5da5aa74/
title: "longcallR"
nav: false
description: "长读长 RNA 测序能把遗传变异与完整转录本结构连在同一条 read 上，但 RNA 数据的覆盖度受表达量影响、剪接位点附近易错配、等位基因表达会使 allele fraction 偏离 0.5，A-to-I RNA editing 还可能伪装成 SNP。longcallR 把 SNP calling、单倍型定相和等位基因特异分析放进同一流程。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>longcallR</h1>
    <p>SNP calling, haplotype phasing and allele-specific analysis with long RNA-seq reads</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## longcallR 方法解读

### 它解决什么问题？

长读长 RNA 测序能把遗传变异与完整转录本结构连在同一条 read 上，但 RNA 数据的覆盖度受表达量影响、剪接位点附近易错配、等位基因表达会使 allele fraction 偏离 0.5，A-to-I RNA editing 还可能伪装成 SNP。longcallR 把 SNP calling、单倍型定相和等位基因特异分析放进同一流程。

### 整体流程

```text
比对后的 lrRNA-seq BAM
  -> 候选 SNP（深度≥6、alt fraction≥0.1、alt count≥2）
  -> longcallR-nn：7 通道 pileup + ResNet-50，预测基因型/合子性
  -> longcallR-phase：联合优化 SNP 相位 δ 与 read 标签 σ
  -> phased VCF + 带 HP/PS 标签的 BAM
  -> ASE：beta-binomial；ASJ：单倍型×junction 的 2×2 检验
```

神经网络输入为 (41\times d\times7)，七个通道分别编码碱基、参考序列、插入、碱基质量、比对质量、read 链方向和转录链方向。它输出五类合子性（包括 RNA editing）和十六类基因型。该部分位于独立的 `longcallR-nn` 仓库，不在本次获取的主仓库中。

### 定相的核心思想

令 (delta_i\in\{1,-1\}) 表示 SNP (i) 的相位，(sigma_k\in\{1,-1\}) 表示 read (k) 的 haplotag，(q_{ki}(x)) 是由碱基质量决定的观测概率。目标是最大化所有 read–SNP 观测的联合概率：

$$P(\delta,\sigma)=\prod_k\prod_{i\in I_k}q_{ki}(\sigma_k\delta_i).$$

算法交替固定 SNP 相位更新 read 标签、再固定 read 标签更新 SNP 相位；如果翻转能提高条件概率就保留。它先利用低冲突 SNP 对构建连通分量作为初始化，再逐步吸收兼容的困难候选位点，因此可以同时改善定相并排除测序错误/RNA editing。代码路径是 `main -> thread::run -> SNPFrag::phase -> cross_optimize`。

### ASE 与 ASJ

ASE 先按最大外显子重叠把 read 分配给基因，选择 read 数最多的 phase set，再对 H1/H2 计数做期望比例 0.5 的 beta-binomial 检验并进行 BH 校正。ASJ 则把 read 分为 junction present/absent 与 H1/H2 四格，论文描述 Fisher 精确检验，并计算对称优势比 SOR。

代码核查发现一个重要差异：当前 Rust ASJ 实现除了 Fisher 还计算 G-test，并取两者中较大的 P 值，因此比论文文字描述更保守。

### 主要结果与局限

在 12 个 PacBio/ONT 数据集上，PacBio SNP precision 为 98.5–99.0%，recall 为 91.0–95.3%；相对 Clair3-RNA，longcallR precision 平均高 1.4 个百分点，但 sensitivity 较低。它也比 WhatsHap 得到更长、错误率更低的 phase blocks。对 202 个 HPRC 样本分析时，每个样本平均发现 88 个显著 ASJ，46.5% 涉及未注释 junction。

局限包括：定相目标近似求解，可能落入局部最优；低表达区域缺少跨 SNP reads；目前专注 SNP 而非 indel；完整复现还需要独立 `longcallR-nn` 仓库、训练模型与外部数据。补充材料未转成可检索 Markdown，因此相关参数表仍标记为 `Not found`。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## longcallR Summary

longcallR is a three-part workflow for long-read RNA sequencing: a ResNet-50 pileup caller predicts SNP genotype/zygosity, a probabilistic Rust algorithm jointly phases SNPs and haplotags reads while filtering errors/RNA editing, and downstream modules test allele-specific expression (ASE) and allele-specific junctions (ASJs). It addresses uneven transcript coverage, splice-alignment errors, skewed allele fractions, and RNA-editing confounding that make genomic-read callers unsuitable for lrRNA-seq.

Across 12 PacBio and Oxford Nanopore datasets, PacBio precision was 98.5–99.0% with 91.0–95.3% recall; longcallR averaged 1.4 percentage points higher precision than Clair3-RNA, with comparable F1 (95.7%) but lower sensitivity. Its phasing produced longer blocks with lower switch and Hamming error than WhatsHap on the reported benchmarks. In 202 HPRC MAS-seq samples, the study found 1,852 genes with highly significant ASJs; samples averaged 88 significant events, and 46.5% involved unannotated junctions.

The acquired primary repository contains the Rust phasing, ASE, and ASJ implementations and demo assets. Code-paper fidelity is medium: most core algorithms map directly to source, but the neural caller is in a separate repository. A notable implementation difference is that current Rust ASJ code takes the larger of Fisher and G-test P values, while the paper describes Fisher alone. Reproduction therefore requires the separate `longcallR-nn` models plus external reference/data resources; supplementary text was not locally converted.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
