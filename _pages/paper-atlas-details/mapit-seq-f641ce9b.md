---
layout: default
permalink: /paper-atlas/mapit-seq-f641ce9b/
title: "MAPIT-seq"
nav: false
wide: true
description: "MAPIT-seq 是一种把内源 RBP-RNA 近邻关系转化为 RNA 编辑信号的实验与计算联合平台。它用抗体把携带 rAPOBEC1 和 hADAR2dd 的 pAG-deaminase 招募到目标 RBP 附近，在原位产生 C-to-U 和 A-to-G 编辑；随后同一份测序数据既能读出转录组表达，也能读出 RBP 附近的编辑信号。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MAPIT-seq</h1>
    <p>Co-profiling of in situ RNA-protein interactions and transcriptome in single cells and tissues</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02774-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MAPIT-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/WangLabPKU/MAPIT-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for MAPIT-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MAPIT-seq 方法中文解读

### 一句话概览

MAPIT-seq 是一种把内源 RBP-RNA 近邻关系转化为 RNA 编辑信号的实验与计算联合平台。它用抗体把携带 rAPOBEC1 和 hADAR2dd 的 pAG-deaminase 招募到目标 RBP 附近，在原位产生 C-to-U 和 A-to-G 编辑；随后同一份测序数据既能读出转录组表达，也能读出 RBP 附近的编辑信号。计算输出主要是 editing rate、editing index、MAPIT score、RBP target、binding cluster、单细胞状态相关的结合强度，以及长读长 isoform 级结合信号。

### 1. 生物学问题与建模目标

RBP 调控常常依赖细胞状态、组织环境和转录本 isoform。传统 RIP/CLIP 类方法容易受到裂解、pull-down、输入量和无法同步读出转录组的限制；STAMP/TRIBE 类编辑记录方法又通常需要遗传构建 RBP-deaminase 融合蛋白。MAPIT-seq 的目标是：在固定样本中用抗体识别内源 RBP，把附近 RNA 标记为可测序的编辑事件，再用 IgG 背景扣除后得到 RBP-RNA proximity score。

需要注意，MAPIT score 更适合解释为“相对 IgG 背景的 RBP 邻近编辑强度”，不是直接的结合亲和力，也不是单独证明因果调控的证据。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| anti-RBP / IgG 样本 | `--treatName`, `--controlName` | 目标抗体和背景对照 | `doc_code.md` |
| 编辑位点 | A-to-G / C-to-U | deaminase 在 RBP 附近留下的信号 | `doc_method.md` |
| 编辑率 | `EDITRate` | 某个位点被编辑 reads / 总 reads | `MAPIT-seq/src/rank_edits_based_on_reditools.py:41-51` |
| Editing Index | paper formula | 一个 transcript/window 内编辑率累加 | `claude_notes.md` |
| MAPIT score | RBP index - IgG index | 背景扣除后的结合强度 | 论文公式；代码只部分可见 |
| high-confidence cluster | `.highconfidence.bed` | 双编辑证据支持的候选结合区域 | `MAPIT-seq/src/MAPIT-seq.sh:525-547` |
| isoform edit matrix | `isomapit.py` | 长读长转录本级编辑结果 | `MAPIT-seq/isomapit.py:155-246` |

### 3. 方法主流程

1. 固定细胞或组织，保留原位 RBP-RNA 邻近关系。
2. 用 primary antibody 识别目标 RBP，再用 secondary antibody 和 pAG-deaminase 招募 rAPOBEC1/hADAR2dd。
3. 在原位反应中产生 C-to-U 和 A-to-G 编辑，然后提取 RNA 建库测序。
4. bulk 模式下，代码先去除 abundant RNA，再用 HISAT2 和 BWA 两轮 mapping，合并 BAM，并进行 SNV / editing call。
5. 用 dbSNP、1000 Genomes、EVS/EVA 等资源过滤已知 SNP，减少把基因组变异误判为 RNA 编辑。
6. 计算每个位点 editing rate，并聚合成 transcript/window 的 editing index。
7. anti-RBP 与 IgG 比较得到 MAPIT score，再按 fold enrichment、MAPIT score、P value 和 adjusted P value 叫 target。
8. 对高置信编辑位点使用 SAILOR/FLARE 和 HOMER，得到 binding cluster 和 motif。
9. scMAPIT-seq 分支使用 STARsolo、细胞 QC、UMI 去重和单细胞 BAM 拆分，分析细胞周期特异结合。
10. ISO-MAPIT 分支使用 IsoQuant assignment 和长读长 BAM，拆分到 transcript 后调用 isoform-level edits。

### 4. 数学目标与直觉

编辑事件按测序深度归一化：

$$
\mathrm{editing\ events\ per\ million\ bases}
= \frac{\mathrm{Total\ Editing\ Events}}{\mathrm{Total\ Mapped\ Bases}} \times 10^6
$$

单个位点的编辑率是：

$$
\mathrm{Editing\ Rate}_i =
\frac{\mathrm{edited\ depth}_i}{\mathrm{total\ depth}_i}
$$

代码中可验证的是 `EDITRate = EDIT / Coverage`。随后论文把一个 transcript 或窗口中的 editing rate 相加：

$$
\mathrm{Editing\ Index}=\sum_i \mathrm{Editing\ Rate}_i
$$

最后定义：

$$
\mathrm{MAPIT\ score}=
\mathrm{Editing\ Index}(\mathrm{RBP})-
\mathrm{Editing\ Index}(\mathrm{IgG})
$$

直觉上，MAPIT score 越高，说明目标抗体样本相对 IgG 背景有更多局部编辑，因而该 RNA 更可能处在目标 RBP 附近。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| bulk mapping | `MAPIT-seq/src/MAPIT-seq.sh:125-243` | abundant RNA 去除，HISAT2/BWA 两轮 mapping，合并 BAM | 精确匹配 |
| SNP 过滤 | `MAPIT-seq/src/MAPIT-seq.sh:245-336` | 按染色体过滤 dbSNP/1000G/EVS-EVA | 精确匹配 |
| editing rate | `MAPIT-seq/src/rank_edits_based_on_reditools.py:41-51` | 从 REDItools base count 计算 edit fraction | 精确匹配 |
| target calling | `MAPIT-seq/pipeline/MAPIT_pipeline_example.sh:37-42` | 暴露 `Mapit calltargets` 命令 | 部分匹配，内部公式不可读 |
| FLARE cluster | `MAPIT-seq/src/MAPIT-seq.sh:493-547` | CT/AG 阈值、overlap、slop、cluster 输出 | 精确/部分匹配 |
| scMAPIT | `MAPIT-seq/pipeline/10x-scMAPIT-seq_pipeline.sh:1-108` | STARsolo、UMI 去重、按 cell/phase 拆 BAM、REDItools | notebook-heavy，部分匹配 |
| ISO-MAPIT | `MAPIT-seq/isomapit.py:155-246` | IsoQuant assignment 过滤、转录本 BAM 拆分、REDItools | 精确匹配，但有硬编码路径 |

### 6. 结果如何解读

Fig. 1 证明抗体依赖的双编辑信号可行，并且转录组相关性较高。Fig. 2 证明 MAPIT-seq 能恢复多个 RBP 的已知 target、motif 和 CLIP/STAMP/INSCRIBE 对照关系。Fig. 3 用 PRC2 例子说明该方法能检验有争议的 in situ RNA proximity。Fig. 4 展示组织切片应用。Fig. 5 是 scMAPIT-seq 的核心证据，支持细胞周期特异 G3BP1 target 和 binding-expression correlation。Fig. 6 展示 long-read MAPIT-seq 能做 isoform-specific binding，并用部分 RIP-qPCR 验证。

### 7. 局限性与未验证部分

- 代码可验证的是 processing pipeline，不是完整论文复现包。
- `Mapit calltargets` 内部 MAPIT score / target aggregation 源码没有直接找到。
- PRC2、组织 GO、cell-cycle correlation、RIP-qPCR 等最终图的专用脚本没有在公开代码中完整找到。
- scMAPIT 依赖 notebook；ISO-MAPIT 有 `/home/gangx/...` 硬编码路径。
- MAPIT score 是 proximity/editing strength，很多输出更适合作为假设生成，需要额外实验验证。

### 8. 快速阅读路线

1. `summary.md`：快速理解问题、贡献和复现评分。
2. `doc_method.md`：按生物学背景、公式和计算流程理解方法。
3. `doc_code.md`：看论文步骤与公开代码的对应关系和缺口。
4. `figure_analysis.md`：逐图理解证据支持什么、不支持什么。
5. `claude_notes.md`：查看完整证据表、公式、假设和代码行号。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MAPIT-seq Summary

### Motivation And Novelty

MAPIT-seq addresses the difficulty of profiling endogenous RBP-RNA interactions in native cellular context while also measuring transcript abundance from the same sample. Existing RIP/CLIP-family approaches can require large input, involve lysis or pull-down artifacts, lack paired transcriptome readout, or do not scale naturally to high-throughput single-cell and isoform-resolved settings. Edit-recording methods such as STAMP/TRIBE require genetically encoded RBP-deaminase fusions, which limits primary tissues and temporal control.

The novelty is an antibody-directed, dual-deaminase recording strategy. A pAG fusion carrying rAPOBEC1 and hADAR2dd is recruited to endogenous RBPs by antibodies, marking nearby RNAs through C-to-U and A-to-G edits. The same sequencing data support transcriptome quantification and RBP-proximity scoring.

### Method Overview

MAPIT-seq begins with fixed cells or tissue, antibody recruitment of pAG-deaminases, in situ deamination, RNA extraction, and sequencing. Computationally, reads are aligned, deaminase-compatible edits are called, known SNPs are filtered, edit rates are aggregated into editing indices, IgG background is subtracted to form MAPIT scores, and targets are called using enrichment/statistical thresholds. Dual-editor evidence can also be passed through SAILOR/FLARE to define high-confidence binding clusters and motifs.

The platform has three analysis modes: bulk/tissue MAPIT-seq for target and cluster calls, scMAPIT-seq for cell-state-specific binding-expression analysis, and long-read ISO-MAPIT-seq for isoform-specific binding.

### Evaluation

The paper validates MAPIT-seq across several RBPs and contexts. YTHDF2-FLAG and G3BP1 experiments show antibody-dependent edit enrichment near known binding sites. G3BP1 targets overlap PAR-CLIP and other published data; RBFOX2, PTBP1, YTHDF2, SERBP1, and PUM1 analyses recover expected target overlaps and canonical motifs. Compared methods include RIP (Methods in Molecular Biology, 2016), eCLIP (Nature Methods, 2016), RT&Tag (Nature Methods, 2022), ARTR-seq (Nature Methods, 2024), STAMP (Nature Methods, 2021), and INSCRIBE (Nature Methods, 2023).

Application figures show MAPIT-seq can re-examine PRC2-RNA proximity, profile G3BP1 targets in embryonic brain tissue, perform high-throughput scMAPIT-seq with cell-cycle analysis, and resolve isoform-specific G3BP1 binding with long reads.

### Reproducibility

Rating: **3 / 5**.

Positive evidence: the paper provides public sequencing data, a public GitHub repository, extracted paper text, main figures, and a code snapshot. The repository contains real processing code for bulk MAPIT-seq, edit filtering, SAILOR/FLARE clustering, scMAPIT pipeline skeletons, and ISO-MAPIT transcript-level edit calling.

Limitations: the public code is mainly a processing pipeline, not a full manuscript reproduction package. The exact readable implementation of MAPIT score/target aggregation is hidden behind the `Mapit` command. Figure-specific scripts for PRC2, tissue GO, cell-cycle correlations, and RIP-qPCR validation were not found. Some single-cell steps are notebook-heavy, and ISO-MAPIT contains hardcoded author-local paths. The README also requires manual patches to REDItools2 and FLARE.

### Key Open Gaps

- Supplementary Methods are available as PDFs but were not converted to Markdown in this workspace.
- MAPIT score and target-call implementation are only partially source-visible.
- Biological result figures depend on private or absent downstream scripts.
- scMAPIT and ISO-MAPIT are analyzable but not cleanly turnkey from the public snapshot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
