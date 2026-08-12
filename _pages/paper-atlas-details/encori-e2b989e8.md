---
layout: default
permalink: /paper-atlas/encori-e2b989e8/
title: "ENCORI"
nav: false
description: "这篇 Nature Methods 论文关注的是 RNA interactome，也就是 RNA 与 RNA-binding proteins (RBPs)、miRNA、其他 RNA 分子之间的大规模相互作用网络。作者指出，CLIP-seq 和 RNA-RNA interactome sequencing 已经能在全转录组层面产生大量相互作用证据，但这些实验数据背景噪声很高，因此很难准确定位 RBP 结合峰、交联诱导位点和 RNA-RN…"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>ENCORI</h1>
    <p>An encyclopedic regulatory and functional atlas of RNA interactomes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03105-x" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ENCORI 方法中文解释

### 这篇论文要解决什么问题？

这篇 *Nature Methods* 论文关注的是 RNA interactome，也就是 RNA 与 RNA-binding proteins (RBPs)、miRNA、其他 RNA 分子之间的大规模相互作用网络。作者指出，CLIP-seq 和 RNA-RNA interactome sequencing 已经能在全转录组层面产生大量相互作用证据，但这些实验数据背景噪声很高，因此很难准确定位 RBP 结合峰、交联诱导位点和 RNA-RNA 相互作用位点（`paper.md:21-24`）。

论文的解决方案分成两层：

1. 先开发两个上游算法：`rbsSeeker` 用于 CLIP-seq 中 RBP 结合峰和交联位点识别；`rriScan` 用于 RNA-RNA 相互作用识别（`paper.md:24-32`）。
2. 再把这些高置信相互作用整合进 ENCORI atlas，提供 RBP-RNA、miRNA-target、RNA-RNA、RBP-motif、degradome、pathway、disease 和 pan-cancer 等网页模块（`supp.md:366-447`）。

### 为什么已有方法不够？

论文比较的背景包括两个方面。第一，CLIP-seq peak/site caller 很多，例如 CTK、CLIPper、DEWSeq、Piranha、PureCLIP、omniCLIP 和 Skipper，但作者认为不同 CLIP 类型中的背景噪声、突变、截断和 deletion 事件需要统一处理；rbsSeeker 因此同时建模 peak 和单核苷酸交联事件（`paper.md:35-43`, `paper.md:70-91`）。第二，已有数据库如 starBase v2.0、POSTAR3、ENCORE 覆盖面较窄或缺少 RNA-RNA interactome、RBP motif、pan-cancer 等模块；补充材料说 ENCORI 扩展到 23 个物种、2,725 个 CLIP-seq 数据集和超过 26 million RBP-binding regions（`supp.md:451-543`, `supp.md:545-587`）。

### ENCORI 的整体计算流程

可以把 ENCORI 理解为一个从原始公共数据到网页 atlas 的流水线：

```text
公共测序数据和注释
  |
  |-- RBP CLIP-seq / AGO CLIP-seq
  |      -> adapter/barcode 处理、去重复、STAR 比对
  |      -> rbsSeeker 识别 peaks/sites
  |      -> 合并、注释 RBP binding regions
  |      -> RBP-target 和 RBP-motif 模块
  |
  |-- miRNA target prediction + AGO CLIP + degradome
  |      -> 合并 miRNA target sites
  |      -> 计算 TDMDScore
  |      -> miRNA-target / TDMD 候选模块
  |
  |-- RNA-RNA interactome 数据
  |      -> STAR normal/chimeric 比对
  |      -> rriScan 识别 RNA-RNA interactions
  |      -> 聚合 reads、MFE、alignment score 等证据
  |
  |-- expression / mutation / cancer / pathway 数据
         -> survival、co-expression、disease、pathway 等下游分析模块
```

需要注意：本次检查的 GitHub snapshot 是 ENCORI 数据处理代码，不是所有上游算法和网页代码的完整合集。论文在 Code availability 中把 ENCORI processing code、`rbsSeeker` source、`rriScan` source 和 Zenodo figure-generation code 分开列出（`paper.md:277-280`）。

### rbsSeeker：RBP 结合峰和交联位点

论文中，rbsSeeker 对 RBP-binding peak 使用滑动窗口和 Poisson 模型：

$$P\,(X\ge h)=\mathop{\sum }\limits_{k=h}^{\infty }\frac&#123;&#123;\lambda }^{k}}{k!}{e}^{-\lambda }$$

其中 \(h\) 是 IP 样本中候选 peak 的最大 read coverage，\(\lambda\) 来自多个背景覆盖度候选的最大值，包括 transcriptome-wide IP 背景、候选区域上下游扩展区域、input 样本同位点和 input 样本扩展区域，之后做 FDR 校正（`paper.md:73-82`）。

对 cross-linking-induced sites，例如 PAR-CLIP 的 C-to-T mutation、iCLIP/eCLIP 的 truncation、HITS-CLIP 的 deletion，rbsSeeker 使用 binomial 模型：

$$P\,\left(X\ge \,k\right)=\sum\limits_{i=k}^{n}\left(\begin{array}{c}n\\ &#123;&#123;\rm{i}}}\end{array}\right){p}^{i}{\left(1-p\right)}^{n-i}$$

其中 \(n\) 是该位点总 reads，\(k\) 是带特定事件的 reads，\(p\) 是 input 或 IP 全局事件背景概率（`paper.md:85-91`）。论文实际运行 rbsSeeker 的参数包括 `-p 0.05 -q 0.05 --rm -S 0.99 -d 5 -N -L 2 --skip --rnafold`（`paper.md:109-118`）。

代码验证结果：本 GitHub snapshot 没有找到 rbsSeeker 的 Poisson/binomial engine。仓库里能验证的是下游处理，例如 `RBPcluster.sh` 从 `rbsSeekerBed/formattedBed/hg38` 读取结果并调用合并/注释脚本（`ENCORI/RBP-RNA/bash/hg38/RBPcluster.sh:6-39`），`RBPclusterBed.py` 用 BEDTools 合并同链相邻区域（`ENCORI/RBP-RNA/python/RBPclusterBed.py:56-80`），`RBPclusterBedAnno.py` 把 cluster 映射到 exon、CDS、UTR、intron 等区域（`ENCORI/RBP-RNA/python/RBPclusterBedAnno.py:30-119`）。因此，rbsSeeker source 在这个 snapshot 中保持 **Not found**。

### RBP motif 模块

论文说明，作者在 rbsSeeker 识别出的 RBP binding sites 上用 HOMER v4.11 做 de novo motif finding，并用 GC% 做 sequence-content normalization、binomial test 计算 p-value、保留 \(P < 0.05\) 的 motifs，再转换坐标、注释基因并生成 PPM/motif logos（`paper.md:121-124`）。补充材料进一步说，这些高置信 motifs 被聚成 13 个 motif subgroups，并与生物通路关联（`supp.md:174-190`）。

代码中，`RBPmotifBatch.py` 直接调用 `findMotifsGenome.pl`，随后用 `findMotifsGenome.pl -find` 把 motif 映射回 BED 区域，再用 `bedtools getfasta` 校验序列，并与注释 BED 相交输出 motif BED 文件（`ENCORI/RBP-RNA/python/RBPmotifBatch.py:45-76`, `ENCORI/RBP-RNA/python/RBPmotifBatch.py:113-173`）。`RBPmotifInfo.py` 则把 HOMER 输出的 `motif_information.txt` 和 `motif_focus_information.txt` 汇总成含 motif 序列、长度、p-value、target/background 百分比、average position 和 best match 的表（`ENCORI/RBP-RNA/python/RBPmotifInfo.py:44-105`）。

解释：motif discovery 和 motif table 生成是有代码证据的；但 Extended Data Fig. 4/5 的最终画图代码没有在 GitHub snapshot 中找到。论文说 figure-generation code 在 Zenodo（`paper.md:274`, `paper.md:280`），所以这里应标为 Partial，而不是 Exact。

### miRNA-target 与 TDMDScore

论文对 miRNA-target 的构建方式是：使用七个 miRNA target prediction programs 预测 target sites，去掉与 miRNA precursor 重叠的位点，保留 canonical 和 noncanonical sites，然后与 rbsSeeker 识别的 AGO binding sites 相交，得到 miRNA-mRNA、miRNA-lncRNA、miRNA-circRNA、miRNA-pseudogene 和 miRNA-sncRNA interactions（`supp.md:974-989`）。论文报告约 8.9 million high-confidence miRNA-target interactions（`paper.md:55`）。

TDMDScore 是本仓库中最强的 paper-code 对应点。论文定义它用于判断 miRNA-target pairing 是否可能触发 target-directed miRNA degradation (TDMD)。它把配对分为 Watson-Crick、G-U wobble、mismatch 和 gap，分数分别为 2、1、-1、-2；再根据 seed region、central bulge 和 miRNA 3' region 不同区域加权，最后除以 miRNA 长度归一化（`supp.md:1018-1070`）。论文用 TDMDScore >= 1.6 作为 potential TDMD event 阈值（`supp.md:285-289`）。

代码中，`TDMDScore.py` 完整实现了这个思路：先重建 Watson-Crick/wobble alignment（`ENCORI/TDMDScore.py:8-29`），再判断 6mer、7mer-A1、7mer-m8、8mer、noncanonical、offset-6mer 和 non-seed 类型（`ENCORI/TDMDScore.py:61-117`），然后找 bulge region 并按 match/wobble/mismatch/gap 分类（`ENCORI/TDMDScore.py:119-198`），最后用 `match=2`、`wobble=1`、`gap=-2`、`mismatch=-1`、3' 区域平方根权重和长度归一化得到分数（`ENCORI/TDMDScore.py:200-259`）。

`miRmRNAwithSeq.py` 和 `miRotherWithSeq.py` 把 TDMDScore 写入 mRNA 和 non-mRNA target 的整合表，并附加 AGO-CLIP/degradome/RBP 支持证据（`ENCORI/miRNA-target/python/miRmRNAwithSeq.py:314-330`, `ENCORI/miRNA-target/python/miRotherWithSeq.py:309-353`）。`miRmRNAcluster.py` 进一步把重叠 target sites 合并成 clusters，保留最大 TDMDScore 并聚合 software、CLIP 和 degradome 支持（`ENCORI/miRNA-target/python/miRmRNAcluster.py:28-141`, `ENCORI/miRNA-target/python/miRmRNAcluster.py:173-299`）。

### rriScan 与 RNA-RNA interaction

论文中的 rriScan 从 STAR 产生的 normal aligned reads 和 chimeric aligned reads 出发，扫描 N-containing CIGAR、过滤 splicing reads、保留最佳 chimeric alignment、限制 segment length 和 gap，然后把 RNA-RNA interactions 分为 sameSeq、antiRRI、intraRRI 和 interRRI。它还用自定义配对打分、DuplexFold MFE 和 readsNum/alignScore/MFE/lScore/rScore 等特征输出 interaction matrix（`paper.md:94-106`）。补充方法中给出运行参数 `-l 15 -M 0 -p 0 -s 5 -g 1`，并保留 alignScore > 10 的结果（`supp.md:1091-1097`）。

代码验证结果：本 GitHub snapshot 没有 rriScan engine。`RNA-RNA/bash/rnaRNArun.sh` 指向 `$base/rriScan/rriScan_new/filter`，说明它消费外部 rriScan 结果（`ENCORI/RNA-RNA/bash/rnaRNArun.sh:1-24`）。`rnaRNA.py` 明确把输入定义为 original rriScan result file（`ENCORI/RNA-RNA/python/rnaRNA.py:11-21`），然后重建配对序列和 locus（`ENCORI/RNA-RNA/python/rnaRNA.py:28-76`），过滤部分 RNA 类型，解析 `rriScanGroup...` ID，计算最大连续 Watson-Crick matches，并保留 freeEnergy、Smith-Waterman、read support 等信息（`ENCORI/RNA-RNA/python/rnaRNA.py:173-245`）。最后它输出 pair-level 和 gene-level RNA-RNA 表（`ENCORI/RNA-RNA/python/rnaRNA.py:265-340`）。

因此，rriScan source 在这个 ENCORI snapshot 中保持 **Not found**；但 rriScan 输出的下游汇总和 ENCORI RNA-RNA 表构建有代码证据。

### 论文的生物学应用和验证

论文把 ENCORI 用在多个应用上：

- RBP target gene type 和 RNA region preference：利用 RBP-RNA 数据分析 RBPs 对 protein-coding genes、lncRNA、tRNA、rRNA、LINE1/2、Alu、CDS、UTR、splice sites 等区域的偏好（`paper.md:49-52`, `supp.md:73-170`）。
- RBP motif 和 m6A-associated proteins：通过 motif atlas 找到包含 DRACH/m6A 相关 motifs 的 RBPs，并进一步用 RNA pulldown、dot blot、LC-MS/MS、RIP-qPCR 和 mRNA half-life assays 验证 CPSF6 等候选因子（`paper.md:52`, `supp.md:193-254`）。
- TDMD：用 TDMDScore 发现 potential TDMD interactions，论文报告它能恢复已知 TDMD cases，并用 GFP reporter system 在 HEK293T 和 HeLa 细胞中验证若干预测（`paper.md:55`, `supp.md:277-316`）。
- SNORA49：用 rriScan/RNA-RNA 模块发现 orphan snoRNA SNORA49 与 28S rRNA 直接互作，并通过 knockout/rescue 和 primer extension 证明它指导 28S rRNA 上 U2828/U2832 的 Ψ 修饰（`paper.md:55`, `supp.md:331-362`）。

### 复现与代码可信度总结

本次代码-论文对应关系的结论是：ENCORI GitHub snapshot 对 TDMDScore 和下游 interaction table construction 支持较强；对 RBP motif discovery、RBP cluster annotation、RNA-RNA post-processing 支持为 Partial 到强 Partial；但 rbsSeeker、rriScan 两个核心上游 engine 不在这个 snapshot 里，网页接口代码也没有包含。若要完全审查 rbsSeeker 和 rriScan 的实现，需要单独检查论文 Code availability 中给出的两个独立仓库（`paper.md:277-280`）。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ENCORI Summary

### What Problem Does It Solve?

ENCORI targets the problem of reconstructing RNA interactomes from noisy high-throughput assays. The paper argues that CLIP-seq and RNA-RNA interactome sequencing can reveal transcriptome-scale protein-RNA and RNA-RNA contacts, but background noise makes accurate interaction-site detection difficult (`paper.md:21-24`). ENCORI is presented as both a new computational workflow and a large web atlas for exploring RBP-RNA, miRNA-RNA, RNA-RNA and disease/cancer-linked regulatory relationships (`paper.md:24-32`).

### Main Contribution

The paper contributes three layers:

- `rbsSeeker`, a CLIP-seq peak/site caller that models RBP-binding peaks with a cumulative Poisson test and cross-link-induced sites with a cumulative binomial test (`paper.md:70-91`).
- `rriScan`, an RNA-RNA interaction caller that uses STAR normal/chimeric alignments, filters likely splice artifacts, classifies interaction types, scores RNA-RNA pairs and reports features such as readsNum, alignScore and MFE (`paper.md:94-106`).
- ENCORI, an atlas integrating public CLIP-seq, AGO CLIP-seq, RNA-RNA interactome, degradome, expression, mutation, cancer and pathway data into more than 30 web modules (`paper.md:27-32`, `supp.md:366-447`).

Compared with starBase v2.0, the supplement says ENCORI expands to 23 species, 2,725 CLIP-seq datasets, more than 26 million RBP-binding regions, new TDMD/miRNA-function tools, RNA-RNA interactome modules, RBP-motif modules, pan-cancer data and APIs (`supp.md:451-543`). Compared with POSTAR3 and ENCORE, the paper emphasizes broader CLIP coverage, rbsSeeker-based peaks plus cross-link sites, rriScan-based RNA-RNA interactions and additional pan-cancer/pathway modules (`supp.md:545-587`).

### Method Overview

At a high level, the workflow is:

```text
Public assays and annotations
  -> preprocess reads and map with STAR/Bowtie as appropriate
  -> call RBP peaks/sites with rbsSeeker
  -> call RNA-RNA interactions with rriScan
  -> intersect AGO binding, miRNA target predictions and degradome support
  -> compute TDMDScore for miRNA-target base-pairing architecture
  -> merge, annotate and expose interactions in ENCORI modules
```

The most code-verifiable algorithm in this GitHub snapshot is TDMDScore. The paper defines TDMDScore as a pairing-architecture score that rewards Watson-Crick and wobble pairing, penalizes mismatches/gaps, emphasizes 3' miRNA complementarity and normalizes by miRNA length (`supp.md:1018-1070`). The cloned code implements the same scoring logic in `TDMDScore.py`, then reuses it in miRNA-target integration scripts (`ENCORI/TDMDScore.py:200-259`; `ENCORI/miRNA-target/python/miRmRNAwithSeq.py:215-266`; `ENCORI/miRNA-target/python/miRotherWithSeq.py:220-271`).

### Evaluation And Main Results

For rbsSeeker, the paper benchmarks against CTK, CLIPper, DEWSeq, Piranha, PureCLIP, omniCLIP and Skipper across eCLIP, HITS-CLIP, iCLIP and PAR-CLIP. The reported evidence includes stronger motif occurrence/distance signals, better capture of YTHDF1/YTHDF2 m6A-site patterns, agreement with known RBP regional preferences, biological-replicate reproducibility and computational efficiency (`paper.md:35-43`).

For rriScan, the paper uses snoRNA-rRNA interactions from snoDB and snoRNA Atlas as reference standards and reports better enrichment than RNAInter/random background, more than half of predictions validated by the reference resources across cell lines, and ROC AUC 0.943 (`paper.md:46`).

For ENCORI resource use, the paper applies the atlas to RBP target-gene types and RNA-region preferences, de novo RBP motif clustering, m6A-associated RBP discovery, TDMD candidate discovery and SNORA49-guided 28S rRNA pseudouridylation (`paper.md:49-58`). Experimental validations include CPSF6 as an m6A-associated protein affecting mRNA stability (`supp.md:193-254`), TDMDScore-predicted interactions validated by reporter assays (`supp.md:307-316`) and SNORA49 knockout/rescue validation of two 28S rRNA pseudouridine sites (`supp.md:331-362`).

### Code And Reproducibility

The acquired GitHub repo is best understood as ENCORI data-processing code, not the full source bundle for every method and figure. Verified contents include:

- RBP downstream processing from `rbsSeekerBed` outputs, including clustering and transcript/gene annotation (`ENCORI/RBP-RNA/bash/hg38/RBPcluster.sh:6-39`; `ENCORI/RBP-RNA/python/RBPclusterBed.py:56-80`; `ENCORI/RBP-RNA/python/RBPclusterBedAnno.py:30-119`).
- HOMER-based motif discovery and motif summary-table export (`ENCORI/RBP-RNA/python/RBPmotifBatch.py:45-76`; `ENCORI/RBP-RNA/python/RBPmotifBatch.py:113-173`; `ENCORI/RBP-RNA/python/RBPmotifInfo.py:44-105`).
- TDMDScore implementation and miRNA-target evidence integration (`ENCORI/TDMDScore.py:8-259`; `ENCORI/miRNA-target/python/miRmRNAwithSeq.py:314-330`; `ENCORI/miRNA-target/python/miRotherWithSeq.py:309-353`; `ENCORI/miRNA-target/python/miRmRNAcluster.py:28-299`).
- RNA-RNA post-processing of original rriScan outputs (`ENCORI/RNA-RNA/python/rnaRNA.py:11-21`; `ENCORI/RNA-RNA/python/rnaRNA.py:173-245`; `ENCORI/RNA-RNA/python/rnaRNA.py:265-340`).

Major gaps are explicit. The standalone `rbsSeeker` and `rriScan` engines are **Not found** in this repo snapshot; the paper points to separate GitHub repositories for them (`paper.md:277-280`). Figure-generation code is also **Not found** in this snapshot; the paper says figure-related analysis data and figure-generation code are in Zenodo (`paper.md:274`, `paper.md:280`). The web-interface implementation described as PHP/JavaScript/MySQL/Bootstrap is **MISSING** from this repo snapshot (`supp.md:1206-1215`).

### Practical Takeaway

ENCORI is a broad RNA-interactome atlas paper whose strongest reproducible code bridge in the acquired GitHub snapshot is TDMDScore and downstream table construction. The paper's central upstream algorithms, rbsSeeker and rriScan, are well described and benchmarked in the article, but their source code must be checked in their separate repositories for full implementation-level verification.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
