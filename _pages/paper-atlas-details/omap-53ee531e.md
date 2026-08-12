---
layout: default
permalink: /paper-atlas/omap-53ee531e/
title: "OMAP"
nav: false
description: "RNA 的功能不仅由“直接结合它的分子”决定，也由它所在的局部细胞环境决定，例如同一核内区室中的蛋白、RNA 和染色质。传统反义寡核苷酸捕获通常在裂解后富集目标 RNA，容易引入裂解液中的非特异结合，并且常需要较多细胞；基因编码的邻近标记方法则可能存在游离或错误定位的酶，而且不容易用于原代样本和组织。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>OMAP</h1>
    <p>Multiomic characterization of RNA microenvironments by oligonucleotide-mediated proximity-interactome mapping</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02457-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## O-MAP 方法详解

### 它要解决什么问题？

RNA 的功能不仅由“直接结合它的分子”决定，也由它所在的局部细胞环境决定，例如同一核内区室中的蛋白、RNA 和染色质。传统反义寡核苷酸捕获通常在裂解后富集目标 RNA，容易引入裂解液中的非特异结合，并且常需要较多细胞；基因编码的邻近标记方法则可能存在游离或错误定位的酶，而且不容易用于原代样本和组织。

O-MAP（Oligonucleotide-mediated proximity-interactome MAPping）的核心创新，是用可编程的 RNA-FISH 类寡核苷酸识别内源 RNA，再把通用的邻近标记催化单元定位到该 RNA 附近。这样可以在固定样本中保留区室结构，并标记目标 RNA 周边的多类分子。本文只解释原理和数据分析，不复述可直接执行的湿实验步骤。

### 方法的核心逻辑

```text
选择目标 RNA
   ↓
设计并验证特异性寡核苷酸探针池
   ↓
通过通用 landing pad 招募邻近标记催化单元
   ↓
在目标 RNA 周围形成局部共价标记
   ↓
亲和富集被标记的材料
   ├─ O-MAP-MS   → 蛋白质组
   ├─ O-MAP-seq  → 邻近转录组
   └─ O-MAP-ChIP → 邻近基因组区域
```

landing pad 将“识别哪个 RNA”和“招募哪个催化单元”解耦。作者还把交替排列的探针分成两个子池，分别显示 O-MAP 信号和 RNA-FISH 信号，用共定位来检查探针池是否偏离目标。这个质控非常关键，因为后续统计分析无法补救系统性的错误定位。

### 三条数据分析分支

#### 1. O-MAP-MS：RNA 周边蛋白质组

47S 和 7SK 实验把相邻但不同的核内区室作为对照：47S 代表核仁，7SK 代表核质/核斑相关环境，scrambled 探针用于估计背景。对蛋白 $p$，可用类似下式的分数比较区室：

$$
s_p=\log_2\left(\frac{I_{p,47S}}{I_{p,7SK}}\right).
$$

作者用已知区室标志蛋白进行 ROC 分析并选择阈值，再用 GO/GSEA 判断候选蛋白是否恢复了预期功能。初始实验检测到 1,954 个蛋白；论文报告 47S 方向覆盖了 95% 的已观测核仁标志物，而 7SK 方向覆盖了 98% 的核质标志物。

时间序列实验把每个蛋白表示成随标记时长变化的轨迹。公开 R 脚本计算重复均值和 log2 比值，然后用 PAM/k-medoids 分成 12 类。论文合并其中四个富集核仁蛋白的簇，得到 313 个高置信候选，其中 241 个已有核仁或核糖体生物发生注释。

Xist 没有合适的“相邻 RNA 区室”对照，因此采用省略靶向探针的 mock 条件。ROC 阈值以上恢复了 147 个已知 Xist 互作蛋白中的 128 个，并显示染色质组织、基因抑制和 RNA 加工因子共同构成 Xi 微环境。

#### 2. O-MAP-seq：RNA 周边转录组

这条分支将富集 RNA 与匹配 input 比较：

```text
双端 RNA-seq
 → 参考基因组比对
 → 基因/转录本定量
 → enriched 与 input 的差异分析
 → 基因、异构体和转座元件层面的候选集合
```

论文使用 HISAT2、StringTie 和 DESeq2 分析基因/转录本，使用 STAR、TEtranscripts 和 DESeq2 分析转座元件。47S 数据恢复了与核仁相关的 snoRNA、lncRNA、假基因及非典型异构体；Xist 数据显示 X 染色体基因和部分常染色体 RNA 的邻近富集。这里的结论是“处于同一微环境”，不能自动等同于直接 RNA–RNA 结合。

#### 3. O-MAP-ChIP：RNA 周边染色质

DNA 分支将富集片段与 input 归一化，再进行宽区域或峰检测。47S 分析合并 EDD 与 epic2 得到核仁相关结构域；Xist 使用 MACS2 broad peaks 描述 Xi 周边染色质。

Patski 细胞中的等位基因比例写为：

$$
r=\frac{X_i}{X_a+X_i}.
$$

$r>0.7$ 被定义为 Xi 特异，$r<0.3$ 为 Xa 特异，中间区域为两者共有。公开 shell 文件能验证 ref/alt 计数和比例计算的核心逻辑，但完整运行仍依赖缺失的 BAM、SNP、peak 和环境配置。

### 与已有方法相比的新意

- 相比裂解后反义捕获，O-MAP 在固定样本中先定义空间邻域，减少裂解后伪互作，并保留高阶区室信息。
- 相比基因编码 APEX 类方法，它不要求转基因表达，因而更容易迁移到组织、类器官和难以改造的样本。
- 相比 RNA-TRAP、HyPro 等非转基因策略，作者强调 O-MAP 使用通用、现成的组件，并能复用探针验证框架。
- 三种 readout 共用同一个靶向层，使蛋白、RNA 和染色质可以围绕同一目标 RNA 进行多组学描述。

### 证据与局限

直接查看主图可见：47S、7SK 和 Xist 的标记形态与预期区室一致；Fig. 3–6 分别展示蛋白质组、Xi 蛋白环境、邻近转录组和邻近染色质的区分能力。方法的主要局限是：FISH 难靶向的低丰度或短 RNA 仍可能困难；固定可能扰动局部结构；邻近标记会同时捕获直接互作物和附近分子；结果依赖合适的对照和阈值。

公开代码只覆盖三个图级分析：Fig. 3i 聚类、Fig. 6c 等位比例、Fig. 6f 的统计结果。完整 MS、RNA-seq 和 ChIP 流程主要存在于论文 Methods 中，而不是可直接运行的软件包。因此，本工作在实验与数据公开方面较强，但端到端计算复现仍需要研究者重建环境和管线。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## O-MAP paper summary

### Problem and contribution

RNA function is shaped not only by direct binders but by proteins, transcripts and chromatin in the surrounding subcellular compartment. Antisense pulldown methods can accumulate lysate-induced background and often require large inputs, while genetically encoded proximity-labeling systems can create mislocalized enzyme and are difficult to deploy in unmodified tissues. This 2024 *Nature Methods* paper introduces Oligonucleotide-mediated proximity-interactome MAPping (O-MAP), which uses programmable RNA-FISH-like targeting to position a common proximity-labeling catalyst at an endogenous RNA in fixed specimens (`paper.md:21-30`).

O-MAP is a technology platform with three readouts: O-MAP-MS for proteins, O-MAP-seq for RNAs and O-MAP-ChIP for genomic loci. The same target-recognition layer is reused, while affinity-enriched material is routed to quantitative mass spectrometry, RNA sequencing or DNA sequencing. The method is explicitly a microenvironment mapper: recovered molecules can be direct binders or nearby members of the same compartment.

### Main evidence

- Targeting was demonstrated for 47S, 7SK and Xist and extended across cultured cells, organoids and fixed tissue. Local figure inspection shows compartment-shaped signal, omission/scramble controls and close agreement with RNA-FISH markers.
- In the initial 47S/7SK proteomics experiment, 1,954 proteins were detected with inter-replicate Pearson correlations of 0.77–0.99. The paper reports recovery of 95% of observed nucleolar markers in the 47S direction and 98% of observed nucleoplasmic markers in the 7SK direction (`paper.md:108`).
- Temporal 47S profiling and 12-cluster k-medoid analysis produced a merged 313-protein nucleolar group; 241 were previously annotated and 31 more were supported by manual curation (`paper.md:114`).
- Xist O-MAP-MS recovered 128 of 147 known Xist interactors above an ROC-selected threshold, with about fourfold average enrichment, using less input than the compared oligonucleotide-capture studies (`paper.md:134`).
- O-MAP-seq recovered RNA classes and locus-level patterns consistent with nucleolar and Xi neighborhoods, including candidate compartment-level relationships beyond direct-contact distance scales.
- O-MAP-ChIP produced chromosome-X-wide Xist enrichment and 47S-associated broad genomic domains that overlap nucleolar-fractionation NADs while revealing cell-line-specific domains.

### Analysis design

The study relies on target-versus-control enrichment rather than a single universal score. For 47S/7SK proteomics, a neighboring RNA-defined compartment provides a ratiometric contrast. Xist proteomics uses omission of primary probes as the control. RNA and DNA branches use matched input normalization followed by differential-expression or domain/peak analysis. Known marker sets, ROC analysis, GO/GSEA and orthogonal imaging are used to interpret the enriched candidates.

### Limitations

O-MAP depends on a target that can be reached by a specific FISH-like probe pool. Fixation may perturb native organization, and the labeling radius means direct binders cannot be distinguished from nearby molecules without follow-up validation. Results also depend on control selection and enrichment thresholds. The displayed specimen types and RNAs establish breadth but do not guarantee equally strong performance for small or low-abundance targets (`paper.md:210`).

### Reproducibility assessment: 3/5

The paper provides detailed Methods, public proteomics data at MSV000094186, sequencing data at GSE217566, source data and local figure assets. The public GitHub snapshot matches the explicitly promised code for Fig. 3i clustering and the core Fig. 6c allele-proportion calculation; it also preserves the Fig. 6f Fisher-test output.

However, the repository is not an end-to-end reproducibility package. It lacks the Fig. 3i input table, uses hard-coded personal paths, depends on absent project/reference data for the Xi workflow, and provides no executable pipelines for routine MS processing, RNA-seq, or ChIP alignment and peak/domain calling. Overall paper-code fidelity is therefore low for the full platform and medium for the narrowly released figure analyses. The experimental method is described here only at a conceptual level; stepwise wet-lab reproduction should rely on the original paper and institutional safety/experimental oversight.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
