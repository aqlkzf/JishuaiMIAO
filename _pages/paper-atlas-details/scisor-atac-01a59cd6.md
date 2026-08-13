---
layout: default
permalink: /paper-atlas/scisor-atac-01a59cd6/
title: "ScISOr-ATAC"
nav: false
wide: true
description: "ScISOr-ATAC 以 10x Multiome 同时获得单核 RNA 与 ATAC，再从同一批带 10x barcode 的全长 cDNA 中富集数千个脑相关基因的 exon–exon junction，进行 Oxford Nanopore 长读长测序。共同的细胞条形码把三个读出连接起来：短读 RNA 定义表达，ATAC 定义开放染色质，长读 RNA 定义 exon inclusion 和 isoform。"
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
      <span>Nature Biotechnology · 2025</span>
    </div>
    <h1>ScISOr-ATAC</h1>
    <p>Combined single-cell profiling of chromatin-transcriptome and splicing across brain cell types, regions and disease state</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-025-02734-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for ScISOr-ATAC">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/careenfoord/scisorATAC" target="_blank" rel="noopener noreferrer" aria-label="Open code for ScISOr-ATAC">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ScISOr-ATAC 方法解释：在同一个细胞核中连接染色质、表达与剪接

### 一句话理解

ScISOr-ATAC 以 10x Multiome 同时获得单核 RNA 与 ATAC，再从同一批带 10x barcode 的全长 cDNA 中富集数千个脑相关基因的 exon–exon junction，进行 Oxford Nanopore 长读长测序。共同的细胞条形码把三个读出连接起来：短读 RNA 定义表达，ATAC 定义开放染色质，长读 RNA 定义 exon inclusion 和 isoform。

### 1. 它为什么不是普通 Multiome

10x Multiome 可以在同一细胞核测 gene expression 与 chromatin accessibility，但标准 3′ RNA short read 难以还原一个分子跨越的多个 exon junction。反过来，单独的长读单细胞 RNA 测序能看剪接，却无法知道同一细胞的染色质状态。

ScISOr-ATAC 的关键不是发明第三种独立条形码，而是复用 10x cDNA 上的 cell barcode/UMI：一份 cDNA 进入短读表达文库，另一份经靶向富集后做 ONT；ATAC library 来自同一个 Multiome GEM。于是同一 cell barcode 上可以同时挂接表达、ATAC peak 和 long-read exon chain。

### 2. 从冻存脑组织到三种读出

#### 2.1 10x Multiome 主干

作者从冻存猕猴与人脑组织分离细胞核，使用 10x Genomics Multiome 生成 snRNA-seq 和 snATAC-seq。短读 RNA 用于聚类和细胞类型注释，ATAC fragments 用于 peak calling 与差异可及性分析。

论文涉及三类比较：

1. 两只成年雄性 rhesus macaque 的 PFC 与 visual cortex；
2. 人与 macaque 的 PFC；
3. 10 例 control 与 9 例 AD 人 PFC。

这些不是纵向追踪同一个细胞的动态实验，而是不同条件样本中的单核联合快照。

#### 2.2 为长读剪接做靶向富集

作者设计 Agilent enrichment array，覆盖 3,224 个 macaque 和 3,630 个人基因的已注释 splice junction，重点包含突触、AD、TDP43、ASD、精神分裂症、ALS 和既往细胞类型特异剪接基因。

10x 全长 cDNA 先经 linear/asymmetric PCR 富集带 barcode 的分子，再按 junction probe capture，最后做 ONT long-read sequencing。靶向后 on-target capture 为 79–83%；代价是它不是全转录组无偏 isoform survey，未设计 probe 或未注释 junction 的覆盖会受限。

长读经 minimap2 比对并由 `scisorseqR` 恢复 barcode、分配 gene、输出每条 read 的 exon chain。论文把同一 gene 中 UMI edit distance $\geq 4$ 的 spliced reads 视为不同 UMI。

### 3. 如何计算 exon inclusion

`scisorATAC` 的 bash/AWK 流程从两个条件的 `AllInfo.gz` 开始。对每个候选 exon 和 cell type，长读被分为 inclusion 与 exclusion。直观上：

$$
\Psi=\frac{N_{inc}}{N_{inc}+N_{exc}},
$$

其中 $N_{inc}$ 是支持 exon inclusion 的 informative reads，$N_{exc}$ 是跨越该 exon 的 skipping reads。条件差为：

$$
\Delta\Psi=\Psi_{case}-\Psi_{control}.
$$

主分析以 $|\Delta\Psi|\geq0.1$ 且多重校正后显著作为差异 inclusion 的判据。实现并非一个纯 R 函数：导出的 `casesVcontrols()` 只是用 `system()` 调 shell，shell 再并行调用 AWK 和 R 检验脚本。

代码中还有三项重要实现细节：

- inclusion 由多种 flank-support 类型相加，不只是单一列；
- AWK 有硬编码 70 bp intronic-overlap 过滤，Methods 未明确写出；
- full analysis 使用 Benjamini–Yekutieli FDR，而 exon downsampling 的迭代内部采用 Bonferroni threshold，二者不要混写。

### 4. 四种 chromatin–transcriptome cell state

论文沿用 MultiVelo 框架，为每个 gene–cell 组合赋予四种状态：

- state 0，priming：chromatin 先打开而 transcription 尚未启动；
- state 1，coupled-on：开放染色质与活跃转录同步；
- state 2，decoupled：转录与染色质关闭不同步；
- state 3，coupled-off：低转录与关闭染色质同步。

作者先按 cell barcode 和 gene 把 long reads 分到状态，再比较不同状态的 exon inclusion。状态关联以 2×2 count table 的检验和 log odds ratio（LOR）描述；本地 LOR 脚本对零计数加入 0.5 pseudocount，这一点论文正文未展开。

为了问“条件总体的剪接差异能否在同一 cell state 内看到”，作者定义：

$$
\text{normalized-state }\Delta\Psi_x=
\frac{\Delta\Psi_x}{\Delta\Psi_{overall}}.
$$

值 $\geq1$ 表示某一状态中的差异达到或超过总体差异；0.9–1 表示接近；$<0.9$ 表示没有在所检状态内充分重现。

这个指标不能“排除所有 cell-state abundance confounding”，也不能证明 cell state 导致剪接改变。它是一种分层一致性检查；分母接近零、状态覆盖不足和 long-read depth 都会影响稳定性。

### 5. 为什么需要双重 downsampling

不同 cell type 的细胞数、ATAC peak 数和 informative long-read 数差异很大，直接比较显著事件比例会把统计功效当作生物差异。作者因此对两种模态分别等量抽样：

- splicing：固定每个 exon/condition 的 reads，再固定抽取 exon 数并重复，比较每轮显著 exon 比例；
- ATAC：每条件固定抽取细胞，用 MACS2 重调 peaks，再固定抽取 peak 数，以 Signac logistic regression 检验差异可及性并重复。

downsampling 使“谁的变化比例更高”更可比，但也改变了被分析的目标集合；结果代表在指定抽样规模下的相对检出率，不是整个细胞类型中真实改变位点的绝对百分比。

### 6. 五张主图的证据链

#### 图 1：数据组织

图 1a 从冻存组织、Multiome、junction capture 到 ONT 和 cell-state 分层，说明三个模态如何以 barcode 串联。图 1b–e 展示 macaque PFC/VIS、人 AD/control PFC 以及 human–macaque integration 的细胞类型。人中两个 CUX2/RORB 共表达亚群较少，论文保留 species difference 或 sampling bias 两种解释。

#### 图 2：脑区比较中两种模态的排名不同

在 macaque excitatory neurons 中，4,818 个 exons 里有 143 个达到 FDR 与 $|\Delta\Psi|$ 阈值；`POLN` 两个 exon 在 PFC 跳过、VIS 包含，并由 bulk tissue 呈相似趋势。

按等功效 downsampling，L3–L5/L6 IT_RORB 的 region-specific splicing 最强；ATAC 则是 L2–L4 IT_CUX2.RORB 的 region-specific accessibility 最强。结论是两模态突出不同亚型，而不是 chromatin 与 splicing 完全无关。

51%（82/160）的测试 exon 在至少一个 state 中 normalized-state $\Delta\Psi\geq1$。这表示总体脑区差异可在一个状态层中重现，不等于这些事件已被因果“验证”为状态驱动。

#### 图 3：同一脑区内的细胞亚型

比较 macaque excitatory neuron subtypes 时，RORB 与 CUX2 亚群在 splicing 和 ATAC 两种模态上都是最不同的一对。`ARAP3` 展示亚型特异 exon inclusion，`DOCK4` 和 `CTNNA2` 展示 subtype accessibility。这里两种模态的亚型排名较一致，但没有逐 locus 证明 ATAC peak 改变导致相邻 exon 改变。

#### 图 4：human–macaque divergence

跨物种比较出现明显模态分离：astrocytes 的 chromatin divergence 强而 splicing divergence 较弱，L2–L3 IT_NRGN.CBLN2 neurons 的趋势相反。55%（64/117）的 excitatory-neuron species-specific exons 在至少一个 state 中达到 normalized-state $\Delta\Psi\geq1$；另有 26% 小于 0.9，可能受状态组成影响。

由于 probe 按各物种已注释 junction 设计，作者用跨多个 junction 的 reads 做稳健性分析；这降低但不能完全消除 annotation/capture bias。

#### 图 5：AD 中 glia 最突出，但不同模态指向不同 glial type

原始计数与等功效结果需分开读。ATAC downsampling 中 astrocytes 最强，其次 oligodendrocytes/microglia；splicing downsampling 中 oligodendrocytes 最强。`FMNL2` 附近 peak 在 AD astrocytes 丢失，`ZNF711` exon 在 AD oligodendrocytes inclusion 下降 42%，而 excitatory neurons 增加 10%。

因此论文总结为两种模态在 AD 中都更突出于 glia，尤其 oligodendrocytes；但不能简化成“同一 glial type 在两种模态上始终排名第一”。这些是病例–对照关联，未证明相应 chromatin 或 splicing 事件驱动 AD。

### 7. 本地代码覆盖与实际缺口

| 环节 | 本地证据 | 判断 |
|---|---|---|
| exon inclusion、Fisher/BY、splicing downsampling | `scisorATAC/inst/bash`、`inst/R_scripts` | Exact/Partial：核心实现可读，存在正文未写的阈值与校正差异 |
| ATAC 等量抽样、MACS2、Signac LR | `DAPeaks_ByCondition.R`、`DAPeaks_ByCelltype.R` | Partial：算法存在，但条件脚本含可执行语法缺陷 |
| cell-state LOR 与 normalized-state ΔΨ | `ScisorATAC_pipelines/` | Partial：主脚本存在，部分使用硬编码本地路径，README 提到的 notebooks 并未全部在本地快照中出现 |
| barcode 恢复、ONT mapping、AllInfo 生成 | 外部 `scisorseqR` | Not found locally |
| MultiVelo state inference | 外部 MultiVelo/notebooks | Partial/Not found：依赖外部版本和未完整随快照提供的 notebook |

#### 可执行性警告

1. 包实际导出 `casesVcontrols()`、`DAPeaks_ByCondition()` 等；旧交接中的 `call_casesVcontrols()` 与 `call_DAPeaksByCondition()` 不是导出函数。
2. `scisorATAC/inst/R_scripts/DAPeaks_ByCondition.R:114` 使用 Unicode 弯引号 `“peaks”`，原样运行会造成 R parse error，需先改成普通双引号。
3. 并行脚本使用 Python 2 `print` 语法，shell 明确调用 `python2`；没有 Python 2 会直接失败，而不是静默兼容 Python 3。
4. R wrapper 用 `paste()` 拼 shell command，带空格或 shell 特殊字符的路径可能解析错误。
5. README 明确提示 splicing 流程中断后应删除 output directory 重跑，说明其 checkpoint/resume 能力有限。

### 8. 解释边界

- ScISOr-ATAC 是靶向 junction 长读方案，不是全转录组 isoform atlas。
- cell state 与 exon inclusion 的共现不能替代调控因果实验。
- downsampling 控制功效差异，但结论依赖指定 cell/read/peak/exon 抽样规模。
- 核 RNA 受 internal oligo(dT) priming 和未完成转录影响，不能等同成熟 cytosolic isoform。
- 代码覆盖主要统计分析；从 Cell Ranger ARC、scisorseqR 到 MultiVelo 的完整端到端环境未封装。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ScISOr-ATAC — Summary

**Paper**: Combined single-cell profiling of chromatin-transcriptome and splicing across brain cell types, regions and disease state
**DOI**: 10.1038/s41587-025-02734-5
**Journal**: Nature Biotechnology (2025)
**Authors**: Wen Hu*, Careen Foord*, Justine Hsu* et al. (Tilgner lab, Weill Cornell Medicine)
**Category**: Technology platform / experimental method with biological applications

---

### Motivation and Novelty

#### The Biological Problem

The mammalian brain contains dozens of cell types distinguishable by gene expression, chromatin state, and alternative splicing — but these three regulatory layers have never been measured simultaneously in single cells. A fundamental open question is whether chromatin and splicing changes in different biological contexts (brain regions, species, disease) are coupled or independent. Prior work has measured each modality separately:

- **Chromatin accessibility in AD**: Single-nucleus ATAC studies (Morabito et al., *Nat. Genet.* 2021) showed cell-type-specific accessibility changes but lacked splicing information
- **Bulk tissue splicing in AD**: Raj et al. (*Nat. Genet.* 2018) showed splicing changes correlated with AD risk genes, but no single-cell resolution
- **Single-cell isoform sequencing**: SnISOr-Seq (Hardwick et al., *Nat. Biotechnol.* 2022) provided cell-type-resolved isoforms but no chromatin data

A second gap is the **cell state framework** from MultiVelo (Li et al., *Nat. Biotechnol.* 2023): transcriptome and chromatin accessibility can be coupled or decoupled for each gene in each cell (priming, coupled-on, decoupled, coupled-off). Whether this cell state influences alternative splicing was entirely unexplored.

#### Unique Contributions

1. **ScISOr-ATAC method**: First protocol to simultaneously measure chromatin accessibility (ATAC) + full-length RNA isoforms (ONT long-read) + gene expression (Illumina) from frozen single nuclei using a single multi-omic workflow
2. **Cell state × splicing link**: Demonstrates associations between chromatin-transcriptome cell states (MultiVelo states 0-3) and distinct splicing patterns within the same cell type
3. **Normalization framework**: Uses normalized-state ΔΨ to ask whether an overall splicing difference is reproduced within at least one cell state; this stratifies, but does not fully rule out, cell-state-abundance and coverage confounding
4. **Comparative multimodal atlas**: Systematic comparison of chromatin and splicing across brain regions, species (human vs macaque), and AD — revealing that these modalities often diverge rather than converge

---

### Method Overview

ScISOr-ATAC builds on the 10x Genomics Chromium Multiome platform and adds two key extensions:

**Experimental**:
- Custom Agilent SureSelect exon-junction probe set covering 3,224–3,630 disease/synaptic genes
- Linear/asymmetric PCR to remove non-barcoded cDNA before enrichment
- ONT PromethION long-read sequencing (72h) on enriched barcoded cDNA

**Computational**:
- Short-read processing: cellranger-arc-2.0.1 + Seurat/Signac + Harmony
- Long-read processing: scisorseqR (GetBarcodes, MapAndFilter, InfoPerLongRead) + minimap2
- Differential splicing: scisorATAC R package — casesVcontrols bash/AWK pipeline
- Cell state integration: Velocyto + MultiVelo 0.1.3 → state-split AllInfo → normalized-state ΔΨ
- Species integration: LIGER for human+macaque co-embedding (16 joint cell types identified); TransMap for ortholog exon mapping
- Downsampling: paired exon/cell subsampling to equalize statistical power across cell types

**Key statistics**: Fisher's exact test + Benjamini-Yekutieli FDR; χ² prefilter; Wilcoxon rank-sum for downsampling distributions

---

### Evaluation

#### Datasets

| Dataset | Samples | Cells | Long reads |
|---------|---------|-------|------------|
| Macaque PFC + VIS cortex | 4 (2 animals × 2 regions) | 6,858–13,710 per sample | 20-33M barcoded reads per sample |
| Human control PFC | 6 samples (C1-C6) | Multiple cell types | 42.3M barcoded reads total |
| Human AD PFC | 9 samples | Multiple cell types | >200M barcoded reads total |
| Human control (extended) | 10 samples (for AD comparison) | Multiple | — |

#### Key Results

**Brain region (macaque PFC vs visual cortex)**:
- 143 significant exons in excitatory neurons (FDR<0.05, |ΔΨ|≥0.1, median |ΔΨ|=0.21)
- L3-L5/L6 IT_RORB neurons: strongest splicing region specificity (downsampling p<2.2×10⁻¹⁶ vs CUX2)
- L2-L4 IT_CUX2.RORB neurons: strongest chromatin region specificity (2.75× higher than RORB)
- 51% of exons show brain-region-specific splicing confirmed in ≥1 cell state

**Cell subtype specificity**:
- L3-L5/L6 IT_RORB vs L2-L3 IT_CUX2: 88 significant exons; also highest chromatin specificity
- Splicing and chromatin agree on which cell type pair is most distinct

**Species divergence (human vs macaque PFC)**:
- Astrocytes: most chromatin divergence, relatively conserved splicing
- L2-L3 IT_NRGN.CBLN2 neurons: highest splicing divergence (p<2×10⁻²⁸), low chromatin divergence
- Inhibitory neurons overall: more splicing divergence than excitatory or glia (p<8×10⁻³)
- 55% of exons with species-specific splicing confirmed in ≥1 cell state

**Alzheimer's disease**:
- Oligodendrocytes: 1,480 peaks (22.1%) near splicing-targeted genes changed; strongest splicing dysregulation in downsampling
- Astrocytes: highest chromatin dysregulation; NOT strongest splicing dysregulation
- Neurons: weak signal in both (potential survival bias)
- ZNF711: 42% exon inclusion decrease in AD oligodendrocytes; 10% increase in excitatory neurons
- AD samples show higher fraction of novel/inconsistent isoforms (not explained by intron count)

**Validation**:
- POLN brain-region splicing validated by bulk RT-PCR in 3 macaque samples
- Exon-junction probes vs whole-exome probes: ΔΨ correlation 0.80 (p<2.2×10⁻¹⁶)
- Downsampling positive/negative controls (neurons vs glia; within neurons): method performs correctly
- SynGO analysis consistent between full and downsampled datasets

---

### Reproducibility

**Rating: 3/5**

**Justification**: The code is available and covers all major analyses, but requires expertise in multiple tools and has undocumented dependencies.

**Strengths**:
- Both code repositories publicly available (scisorATAC + ScisorATAC_pipelines)
- Data deposited at NCBI SRA (PRJNA1021558)
- The R package has a vignette and documentation
- Core statistics (Fisher + BY FDR + downsampling) are well-documented

**Weaknesses/Practical notes**:
- **Python 2 dependency**: The shell pipeline explicitly invokes `python2` for the Python-2-syntax parallel AWK executor; environments without Python 2 fail at this stage
- **Upstream pipeline not packaged**: GetBarcodes, MapAndFilter, InfoPerLongRead are in scisorseqR (separate package); compatibility with current scisorseqR versions not guaranteed
- **Hardcoded paths**: `LOR_ADvsControl_withinHuman_altWorkflow.R` and `From_StatePSIperConditione...R` use absolute local paths (`/Users/apple/Wen/...`) — must be manually updated
- **MultiVelo integration is notebook-only**: No standalone script for running Velocyto + MultiVelo state assignment; requires manual Jupyter execution
- **Frozen tissue optimization**: Protocol optimized for frozen tissue; fresh tissue may require protocol modifications
- **Compute requirements**: AWK parallelization needs high-core compute nodes; MACS2 peak calling in downsampling loops needs 50-100GB RAM; ONT sequencing generates substantial data (>200M reads)
- **Data availability**: Reference genomes, GENCODE annotations, and UCSC chain files for TransMap must be downloaded separately

**Common pitfalls**:
1. AllInfo.gz file format must match exactly (columns 1-5 plus column 9 for exon chain)
2. MultiVelo cell state CSV must use `SampleName_CellBC-Suffix` barcode format
3. MACS2 must be in PATH; test with `macs2 --version` before running DAPeaks functions
4. The 5-read-minimum for isoform retention in scisorseqR must match what was used for analysis (strict = per sample; relaxed = across all samples combined)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
