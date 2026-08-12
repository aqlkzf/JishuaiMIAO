---
layout: default
permalink: /paper-atlas/scnanoseq-cut-tag-3824b0fb/
title: "scNanoSeq-CUT-Tag"
nav: false
description: "单细胞染色质修饰测序已经能够回答“某个细胞中哪些区域带有 H3K4me3、H3K27ac、H3K27me3 等标记”，但绝大多数方法使用短读长测序。短读长带来两个结构性限制： 在 LINE、LTR、着丝粒附近或其他低可比对区域中，短片段难以确定来自哪一个重复拷贝。 一个短片段通常只能看到一个局部位点，无法直接证明同一条原始 DNA 分子同时跨过两个相邻的修饰峰。"
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
    <h1>scNanoSeq-CUT-Tag</h1>
    <p>scNanoSeq-CUT&amp;Tag: a single-cell long-read CUT&amp;Tag sequencing method for efficient chromatin modification profiling within individual cells</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scNanoSeq-CUT&Tag 方法详解

### 1. 这篇论文要解决什么问题？

单细胞染色质修饰测序已经能够回答“某个细胞中哪些区域带有 H3K4me3、H3K27ac、H3K27me3 等标记”，但绝大多数方法使用短读长测序。短读长带来两个结构性限制：

1. 在 LINE、LTR、着丝粒附近或其他低可比对区域中，短片段难以确定来自哪一个重复拷贝。
2. 一个短片段通常只能看到一个局部位点，无法直接证明同一条原始 DNA 分子同时跨过两个相邻的修饰峰。

早期单细胞 ChIP 方法 scDrop-ChIP（2015）每个细胞只有约 800 条唯一读段；CoBATCH（*Molecular Cell*, 2019）、Paired-Tag、scCUT&Tag 等方法改善了通量和信噪比，但仍建立在短读长平台上。Nanopore-DamID（bioRxiv, 2022）和 DiMeLo-seq（*Nature Methods*, 2022）能够读取单分子上的蛋白–DNA 信息，却主要用于群体样本，难以解析异质组织中的单细胞差异（`paper.md:24,361,375-376`）。

scNanoSeq-CUT&Tag 的目标是：在保留 CUT&Tag 抗体靶向特异性的同时，把长 DNA 分子和单细胞身份一起送入 Oxford Nanopore 测序，从同一份数据中同时获得常规单细胞染色质图谱与长分子特有的信息。

### 2. 核心创新

方法的关键不只是“把 Illumina 换成 Nanopore”，而是设计了一条能够保留长分子的实验与计算链路。

- pG-Tn5 只装载一种接头。论文认为这能减少短片段扩增，并使兼容末端的原始长片段都可被 PCR 回收；传统双接头设计理论上只有约一半片段两端组合可扩增（`paper.md:228-234`）。
- 每个细胞先获得内层条形码，细胞产物混合后再加外层条形码，形成组合索引。
- 对齐后，长分子的两个末端分别作为局部染色质信号；完整分子跨度则用于等位基因、相邻峰共占据和重复拷贝分析。

可以把同一条读段理解为同时提供两类信息：

```text
长分子左端 ───────────────────────── 长分子右端
   │                                       │
   └─ 局部 CUT&Tag 信号       局部 CUT&Tag 信号 ─┘

完整跨度额外携带：细胞条形码、杂合 SNP、重复拷贝差异、两个峰是否被同一分子连接
```

### 3. 从细胞到长读段

#### 3.1 抗体靶向与切割

细胞先与目标抗体孵育，再加入装载单接头的 pG-Tn5。pG-Tn5 通过抗体定位到目标染色质区域，Mg²⁺ 激活转座反应。论文使用约 10,000–300,000 个细胞完成这一步（`paper.md:240-243`）。

#### 3.2 单细胞分选和内层条形码

细胞经 FACS 单个分入 96 孔板。每孔裂解液含一个带 24 bp 内层细胞条形码的引物。裂解后进行 22 个循环的长片段预扩增（`paper.md:246-255`）。

#### 3.3 外层条形码和 Nanopore 测序

每 48 个不同内码细胞的部分产物合并，经过两次 0.6× AMPure 纯化，再用外层条形码进行 8–10 个循环的 PCR，随后两次 0.9× AMPure 纯化并在 PromethION 48 上测序。条形码理论容量为 96×96=9,216 个组合；论文实验主要使用 48 个内码和 24 个外码，即每次 1,152 个组合（`paper.md:252-258`）。

### 4. 计算流程

```text
PromethION FASTQ
  → 外码拆分
  → 内码拆分
  → Q≥7、长度≥100 bp
  → 去接头
  → minimap2(map-ont) 比对
  → MAPQ≥30、去低质量/补充比对、排序、去 PCR 重复
  → 每条长分子两端各扩展 ±50 bp
       ├─ ArchR：细胞质控、LSI、聚类、UMAP、基因分数
       ├─ SEACR：峰识别和跨细胞支持过滤
       ├─ WhatsHap + 二项检验：等位特异峰
       ├─ 同分子峰对 + KS 检验：相邻区域共占据
       └─ 重复序列比较：L1/LINE 拷贝级染色质状态
```

#### 4.1 拆分、过滤和比对

公开代码先用 Nanoplexer 按外码拆分，再按内码拆分（`01_demultiplex.sh:6-44`）。NanoFilt 去除质量小于 7 或长度小于 100 bp 的读段，cutadapt 去接头，minimap2 使用 `map-ont` 预设；SAMtools 进一步使用 MAPQ 30 阈值并去 PCR 重复（`paper.md:261-270`; `02_trim_mapping.sh:25-92`）。

每条长分子的左右端各扩展 50 bp，作为一次目标染色质事件的局部信号。这样，常规聚类使用的是端点信号，而不是把整条长分子内部都视为带修饰。

#### 4.2 单细胞聚类

ArchR 的关键设置是：每细胞至少 2,000 个片段；5 kb TileMatrix；活性标记的最低 TSS 分数为 1，抑制性标记为 0.1；Iterative LSI 迭代两次并使用 1–30 维；Seurat 聚类后用 LSI 1–6 维做 UMAP（`paper.md:273-282`）。

这一步输出细胞嵌入、聚类、基因分数和按群体聚合的 bigWig。小鼠睾丸分析再根据标记基因给出细胞类型，并手工指定精子发生状态顺序后计算轨迹。因此轨迹表示“沿已知生物学顺序的变化”，不是自动发现的谱系方向。

#### 4.3 峰识别

SEACR 使用 `non-stringent 0.05`。若总细胞数为 \(N\)，峰至少需要

\[
s_{\min}=\max(5,0.015N)
\]

个细胞支持（`paper.md:285-288`）。重复元件峰还要求重复注释与峰的重叠长度至少占峰长的三分之二（`paper.md:312-315`）。

### 5. 长读段带来的三类关键分析

#### 5.1 等位特异染色质峰（ASP）

WhatsHap 利用已知的高可信杂合 SNP 给长读段加单倍型标签。补充方法要求：当一条分子有多个信息 SNP 时，只有某一亲本来源占比达到 90% 才保留；随后将带亲本标签的分子与染色质峰相交（`supplementary_information.md:317-352`）。

对一个峰，设两个单倍型的支持数为 \(n_1,n_2\)：

\[
n=n_1+n_2,\qquad r=\frac{n_1}{n},\qquad H_0:p_1=p_2=0.5.
\]

代码进行双侧二项检验，再做 FDR 校正（`ASP_identification.R:32-83`）。补充方法使用 FDR≤0.05 和某一亲本占比≥90% 作为 ASP 条件。需要注意一个边界差异：补充文字意味着支持数必须大于 20，而代码在 \(n\ge20\) 时就检验；代码还按唯一 `cell` 字段计数，不一定等同于原始读段条数。

长读段的优势在于：即使峰内部没有杂合 SNP，只要同一分子在邻近区域携带可定相 SNP，仍可把该峰归入父源或母源。

#### 5.2 相邻区域共占据

方法先寻找被同一长分子连接的两个候选峰，再按读段方向分别检验。峰中心 1 kb 内的分子端作为支持集合，周围 100 kb 区域作为背景；代码只比较长度大于 1 kb 的分子，并对支持/背景长度分布做 KS 检验和 FDR 校正（`paper.md:300-309`; `co_occupancy_ks_test.R:55-114`）。论文最终保留校正 P≤0.05 且至少 10 条读段支持的事件。

这个结果应解释为“同一长分子反复跨过两个相邻修饰峰的统计证据”，不能直接等同于两个蛋白发生物理相互作用。对于距离超过 10 kb 的峰，补充方法使用 ArchR 的跨细胞相关性推断，不是长读段直接跨越（`supplementary_information.md:378-407`）。

#### 5.3 重复元件拷贝分辨

人类 L1Hs 流程从 T2T 参考中提取全长拷贝，用 BLAST 比较拷贝间序列差异，并把约 6 kb 的 L1Hs 划分为 20 个连续 300 bp 窗口，判断每个窗口是否具有足够差异来区分具体拷贝（`L1HS_analysis_pip.sh:16-242`; `supplementary_information.md:281-314`）。

长读段只要跨过一个可区分区域，就可能把邻近的染色质端点锚定到具体重复拷贝。但这不是“所有重复序列都能唯一定位”：高度同质的着丝粒、rDNA 或缺少判别序列的拷贝仍然困难。

### 6. 实验验证和主要发现

- 六个人源细胞系、5 种组蛋白修饰以及 CTCF/RAD21 共得到 17,211 个高质量单细胞数据集，总测序量 3.5 Tb，中位读长 3.4–4.4 kb。
- 各靶标每细胞中位唯一读段约 9,193–13,373；FRiP 与短读长 scCUT&Tag 可比；人鼠混合实验估计碰撞率为 1.6%（`paper.md:44,50`）。
- 七种染色质标记都能区分六个人源细胞系；2,471 个小鼠 PBMC 的 H3K4me3 数据可分辨主要免疫细胞类型。
- 在特定细胞系混合数据中，下采样到每细胞 1,000 条读段仍能识别细胞类型。论文据 PromethION 吞吐量推算约 0.1 美元/细胞；这是测序成本投影，不是完整实验成本实测（`paper.md:73`）。
- 长读段分析展示了等位特异峰、相邻峰同分子支持、重复/黑名单区域信号、精子发生过程中的 H3K4me3 动态，以及 5-AZA 去甲基化后重复拷贝的 H3K27ac 变化。

### 7. 如何正确理解这项方法

scNanoSeq-CUT&Tag 最有价值的地方，是在同一实验中兼容两种尺度：

- **局部尺度：** 长分子端点可像传统单细胞 CUT&Tag 一样用于聚类、峰和基因调控分析。
- **分子尺度：** 完整读段可连接 SNP、重复拷贝和相邻峰，增加短读长缺失的上下文。

因此它更像一个“带单分子上下文的单细胞染色质平台”，而不是单一的峰识别算法。

### 8. 可复现性与限制

论文公开了 GEO 原始数据、Figshare 处理数据和 GitHub 代码，并提供一个小型 FASTQ 示例。核心计算步骤与论文有较高的一致性，但代码仓库是研究过程快照：大量脚本写死 `~/project` 或绝对路径，需要外部基因组索引、注释和中间文件；没有环境锁定、容器、自动测试、CI 或统一的端到端入口。

综合评价为 **3/5**：方法逻辑和核心实现可以追踪，数据也有公开入口，但复现全部图表需要重建运行环境、配置路径并补齐外部数据。生物学上还需注意抗体特异性、PCR 偏倚、杂合 SNP 密度、测序深度、极端重复区不可分辨，以及“共占据统计证据”不等于直接分子互作。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## scNanoSeq-CUT&Tag — Summary

### Problem and Motivation

Single-cell short-read chromatin assays can identify cell types and regulatory states, but their fragments map poorly in repetitive/low-mappability sequence and rarely preserve evidence that two marked regions occur on the same original molecule. The first single-cell ChIP-seq method, scDrop-ChIP (2015), produced only about 800 unique reads per cell, while later methods such as CoBATCH (*Molecular Cell*, 2019), Paired-Tag and scCUT&Tag improved throughput and signal but remained short-read based. Long-read Nanopore-DamID (bioRxiv preprint, 2022) and DiMeLo-seq (*Nature Methods*, 2022) recover molecule-scale protein–DNA information, but the paper identifies them as bulk assays (`paper.md:24,361,375-376`).

### Proposed Technology

scNanoSeq-CUT&Tag combines antibody-directed CUT&Tag, a single-adaptor pG-Tn5 design, plate-based combinatorial cell barcoding, long-range PCR and Oxford Nanopore sequencing. The single-adaptor design is intended to retain full long tagmented molecules. After outer/inner demultiplexing, reads are filtered, mapped and deduplicated; ±50-bp windows around each molecule end become conventional chromatin signals for ArchR clustering and SEACR peak calling, while the full molecule span enables haplotype, neighboring-peak and repeat-copy analyses (`paper.md:36,228-288`).

The specialized analysis modules are:

- allele-specific peaks from phased long reads, a balanced binomial null, FDR control and parental-dominance filtering;
- neighboring-region co-occupancy from repeated same-molecule peak pairs and orientation-specific KS tests against local read-length backgrounds;
- sequence-discriminability analysis for full-length repeat copies, including 300-bp windows across human L1Hs;
- ArchR-based cell-state clustering/trajectory and integration with WGBS or long-read transcript data for biological applications.

### Evaluation and Main Results

The assay was evaluated on six human cell lines, mouse PBMCs, mouse testicular cells and 5-AZA-treated K562 cells. Across five histone modifications plus CTCF and RAD21, the authors retained 17,211 human single-cell datasets, generated 3.5 Tb, and reported median read lengths of 3.4–4.4 kb. Median unique reads per cell ranged from 9,193 to 13,373 across targets; FRiP was comparable to short-read scCUT&Tag, and a human–mouse mixing experiment gave a 1.6% estimated collision rate (`paper.md:44,50`).

All seven profiled marks separated the six cultured cell lines. H3K4me3 profiles also resolved major populations among 2,471 mouse PBMCs. In the tested cell-line mixture, downsampling to 1,000 reads per cell retained cell-type identification; the paper’s roughly US$0.10-per-cell figure is a projected sequencing-cost estimate under assumed PromethION throughput, not a measured full workflow cost (`paper.md:59-76`).

Long-read-specific results include validated allele-specific chromatin peaks, hundreds to thousands of predominantly sub-10-kb neighboring co-occupancy events per mark/data point, improved signal in repeats and blacklist regions, developmental H3K4me3 changes across mouse spermatogenesis, and repeat-copy H3K27ac responses to DNA demethylation. Associations beyond 10 kb are inferred from cross-cell signal correlation rather than directly spanned by reads (`paper.md:99,174-192`; `supplementary_information.md:378-407`).

### Interpretation

The method’s important contribution is not merely replacing a sequencer. It separates each long molecule into two complementary representations: local tagmentation endpoints support standard single-cell epigenomic analysis, while the intervening sequence carries haplotype, repeat-discriminating and peak-linking context. The figures consistently show that ordinary cell-type structure is retained while molecule-scale analyses become possible.

The approach does not make every repeat uniquely mappable, prove protein–protein interactions, or directly observe long-range (>10 kb) co-occupancy when reads do not span both loci. PCR, antibody specificity, phased-variant density and sequencing depth remain important constraints.

### Reproducibility — 3/5

Raw sequencing data are available under GEO `GSE249799`, processed data are linked through Figshare, and the public GitHub repository contains substantial task-specific code plus a small preprocessing FASTQ example (`paper.md:330-339`). Direct inspection found close matches for demultiplexing, mapping/QC, ArchR analysis, SEACR filtering, ASP testing, KS-based co-occupancy and L1Hs sequence analysis.

Reproduction is nevertheless not turnkey. Scripts contain hard-coded home/absolute paths, scheduler assumptions and external reference/intermediate dependencies; no environment lockfile, container, tests, CI or end-to-end runner was found. Several later scripts also require manual object setup or contain path/object inconsistencies. The code is therefore a useful and fairly faithful analysis record, but rebuilding every result requires substantial reconstruction and independent data acquisition.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
