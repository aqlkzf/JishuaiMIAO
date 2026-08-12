---
layout: default
permalink: /paper-atlas/dnd-seq-bff3bb81/
title: "DnD-seq"
nav: false
description: "D&D-seq（Docking and Deamination followed by sequencing）把一个胞嘧啶脱氨酶 DddA 通过抗体/纳米抗体定位到目标 TF 或 chromatin regulator 附近，让结合位点附近的 C 被编辑成 U，测序后表现为 C>T 或互补链上的 G>A 变异。这样，D&D edit 的局部富集就可以作为 DNA-protein interaction 的分子足迹。"
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
      <span>Cell · 2026</span>
    </div>
    <h1>DnD-seq</h1>
    <p>Single-cell mapping of regulatory DNA-protein interactions</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2026.05.014" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DnD-seq 方法解释

### 一句话概括

D&D-seq（Docking and Deamination followed by sequencing）把一个胞嘧啶脱氨酶 DddA 通过抗体/纳米抗体定位到目标 TF 或 chromatin regulator 附近，让结合位点附近的 C 被编辑成 U，测序后表现为 C>T 或互补链上的 G>A 变异。这样，D&D edit 的局部富集就可以作为 DNA-protein interaction 的分子足迹。

论文声称的是一种单细胞兼容的实验技术加分析框架；代码可验证的是其中核心的 D&D edit calling、peak/motif、target/background footprint、SNR 和 D&D edit matrix 生成流程。代码中未找到直接实现的是论文后半部分的一些下游分析，例如 target prediction 的 `glmnet` 模型、GoT-ChA genotyping、LMM、Cicero/Monocle、C.Origami，以及完整的 CellRanger/Seurat/Signac/Multiome 预处理。

### 这篇论文想解决什么问题

单细胞 RNA、ATAC 和 Multiome 已经能看到表达和开放染色质，但直接测量 TF 或 chromatin regulator 在每个细胞里的 DNA 结合仍然困难。ChIP-seq 和 CUT&Tag 类方法对稳定、丰富的 chromatin factor 更友好，但对弱结合、瞬时结合、低亲和力抗体、以及高通量单细胞整合都不够理想（`paper.md:23-31`, `paper.md:37-39`）。

D&D-seq 的核心想法是：不要依赖切割或 tagmentation 来记录结合，而是在目标蛋白附近留下碱基编辑痕迹。只要这个痕迹能随 ATAC、scATAC、WGS 或 Multiome 测到，就能把 protein binding 和 chromatin accessibility 放在同一个数据框架里分析（`paper.md:39-47`, `paper.md:207-213`）。

### 实验层：Docking + Deamination

论文的实验逻辑可以拆成五步：

1. 固定并通透化细胞。
2. 用 primary antibody 标记目标 TF 或 chromatin regulator。
3. 加入能识别 primary antibody 的 `nb-DddA_NT` 或 IgG-binder-DddA_NT。
4. 加入 `DddA_CT` 和 Zn^2+，让 split DddA 重新形成有活性的 deaminase。
5. 进入 bulk ATAC、single-cell ATAC、WGS/PTA、GoT-ChA 或 10x Multiome library construction。

这些步骤在论文 Methods 里有直接描述（`paper.md:189-213`, `paper.md:219-229`）。图 1A-B 也可视化了这个过程：target staining、D&D enzyme binding、enzyme activation、open chromatin tagmentation、library construction（`figure_analysis.md`）。

这里的关键是位置编码：DddA 不需要知道 TF 的 motif，它只要被抗体带到目标蛋白附近，就会在附近 DNA 上留下 C-to-U editing。测序时这些编辑主要表现为 C>T 和 G>A，所以后续分析把这两个变异类型作为 D&D edit。

### 计算层：从 BAM 到 D&D footprint

论文 STAR Methods 把 D&D signal extraction 总结成五个分析步骤（`paper.md:261-269`）。

#### 1. BAM 预处理

论文声称：去除 duplicate、低质量、非 primary alignment、非 proper-pair、非标准染色体的 reads。

代码可验证的是：`dnd-pt1` 调用 `flt_bam`，其中 `picard MarkDuplicates REMOVE_DUPLICATES=true` 负责去重复，`samtools view` 使用 MAPQ、proper-pair、primary alignment 和 chromosome BED 过滤（`DnD/main/src/dnd_pt1.py:76-80`; `DnD/main/src/main/step1.py:12-81`）。这一部分和论文描述高度一致。

#### 2. SNV pileup

论文声称：从过滤后的 BAM 里收集 SNV，VCF 需要至少 3 个 aligned reads，总变异支持中至少 2 个 reads 支持 ALT；论文正文提到 `bcftools mpileup`，同时也允许用 pysam 多线程方式（`paper.md:263`）。

代码可验证的是：当前包使用 pysam 实现 pileup，不是默认走 `bcftools mpileup`。`dnd-pt1` 的默认 `--count=3` 与论文一致，但默认 `--alt=1`，和论文“at least two reads supporting variants”不完全一致（`DnD/main/src/dnd_pt1.py:41-44`; `DnD/main/src/main/step2.py:13-122`）。因此这里应写成 `Partial`，不是 `Exact`。如果用户运行时设定 `--alt 2`，才更贴近论文文字。

#### 3. gnomAD/custom/VAF 过滤

论文声称：用 gnomAD 和可选 custom VCF 去除 germline/uninformative variants，再去除 VAF 高于 10% 的变异（`paper.md:263`）。

代码可验证的是：`dnd-pt1` 默认会调用 `flt_vcf` 做 gnomAD 过滤；如果传入 `--custom`，会额外过滤 custom VCF；之后调用 `flt_vaf`（`DnD/main/src/dnd_pt1.py:82-96`）。`flt_vcf` 用 bedtools subtract/intersect 和 allele check 做数据库过滤（`DnD/main/src/main/step3.py:12-92`），`flt_vaf` 按 depth 和 variant/depth 百分比重写 VCF（`DnD/main/src/main/step3.py:95-124`）。这部分是方向一致的实现，但 VAF 逻辑比论文一句话更复杂，所以也更适合标记为 `Partial`。

#### 4. 提取 D&D edits 和 edited reads

论文声称：过滤后生成两个 VCF，一个包含所有 single variants，一个专门包含 C-to-T 或 G-to-A variants，用后者识别 edited peaks；同时从 BAM 中提取含 D&D edits 的 QNAME/read（`paper.md:263`）。

代码可验证的是：`dnd-pt1` 先用 `flt_snvs(vcf, ..., False)` 生成 all-SNV VCF，再用默认 `--snv "C>T,G>A"` 生成 D&D-specific VCF；`flt_alignment` 读取 D&D VCF 的 QNAME，写入 `qnames.txt`，再用 `samtools view -N` 输出 `.snvs.bam`（`DnD/main/src/dnd_pt1.py:99-117`; `DnD/main/src/main/step4.py:12-108`）。这是核心的 `Exact` 实现。

#### 5. Peak calling、motif search、target/background 定义

论文声称：对预处理 BAM 用 MACS2 `-f BAM --nomodel` call peaks，过滤 blacklist，用 MEME SEA + HOCOMOCO v11 找 motif，也可以用 HOMER2 或 ChIP-seq reference。含目标 motif 或 ChIP-seq overlap 的 peak 是 target peak，其他 peak 是 background peak；target peak 以 motif center 或 ChIP-seq summit 为中心缩放到 200 bp（`paper.md:263`）。

代码可验证的是：

- `step5.macs2_callpeak` 生成 MACS2 命令、做 blacklist subtract、写 `peaks_bkflt.narrowPeak` 和 `summits_bkflt.bed`（`DnD/main/src/main/step5.py:8-78`）。
- `dnd-pt2` 支持 SEA 和 HOMER2，并默认使用 HOCOMOCO MEME 文件（`DnD/main/src/dnd_pt2.py:54-90`; `DnD/main/src/main/step5.py:211-233`）。
- `dnd-pt3` 提供 `--mode chip|homer2|sea`、`--size` 默认 200、`--rand` 默认 200、`--var` 默认 `C>T,G>A`（`DnD/main/src/dnd_pt3.py:16-32`）。
- `step6.tf_peaks` 在 SEA 模式下按 motif 名称选 peaks，并且多个 motif position 时选择最高 score 的 position（`DnD/main/src/main/step6.py:24-62`）。
- `step6.py` 写出 `motif_TF.narrowPeak` 和 `motif_bkgd.narrowPeak`，并构造 motif-centered windows（`DnD/main/src/main/step6.py:203-247`）。

这一段是代码最清楚、最接近论文的部分。

### SNR 和 footprint 怎么计算

论文里的 SNR 思路是：目标区域和背景区域都有一些非 D&D variants。假设非 D&D variants 的背景频率在 target/background 中相对稳定，就可以用它们来归一化 D&D edits（`paper.md:267`）。

可以写成：

$$
\text{D&D edits per peak} = \frac{\#(C>T) + \#(G>A)}{\# \text{peaks}}
$$

$$
\text{SNR} = \frac{\text{D&D edit counts per peak}}{\operatorname{mean}(\text{non-D&D edit counts per peak})}
$$

代码可验证的是：`stats_peaks` 把 D&D VCF 和 all-SNV VCF 分别 intersect 到 target/background windows，然后生成 non-D&D VCF，调用 `motifCenteredCounts` 和 `countOnlySnvs`，最后用 `tools.R` 画 footprint 和 SNR/context 图（`DnD/main/src/main/step6.py:250-428`; `DnD/main/src/main/dnd_acc.py:70-115`; `DnD/main/src/main/dnd_acc.py:231-318`; `DnD/main/src/main/tools.R:47-127`）。

footprint 分析里，论文说在 motif center 的 +/-100 bp 内计数，并随机采样 10 次，用 mean 和 standard deviation 可视化（`paper.md:269`）。代码中 `motifCenteredCounts` 明确 `for r in range(10)`，每次随机采样 `sampArg` 个 peaks 并按距离统计 target/background edits（`DnD/main/src/main/dnd_acc.py:365-432`）。`plot_footprint` 再对 10 个文件取均值和标准差（`DnD/main/src/main/tools.R:47-95`）。这是很强的 paper-code 对齐证据。

### `dnd-pt4` 做什么

论文后续把 D&D 信号放进 single-cell analysis。代码里的 `dnd-pt4` 不是完整的 Seurat/Signac/CellRanger pipeline，而是一个转换器：

1. 从 VCF 和 BAM 中找到含 D&D edit 的 reads。
2. 写出 `dndedits.txt`、`fragments.tsv.gz` 和 qnames。
3. 把 edits 聚合到 peaks 上。
4. 写出 MatrixMarket 格式的 `mtx/matrix.mtx`、`barcodes.tsv` 和 `peaks.bed`。

直接证据是 `DnD/main/src/dnd_pt4.py:160-215`, `DnD/main/src/dnd_pt4.py:218-392`, `DnD/main/src/dnd_pt4.py:395-430`。README 只展示了如何把这些矩阵加载为 `Signac::CreateChromatinAssay` 和 `Seurat::CreateSeuratObject`（`DnD/README.md:349-379`）。因此这里应该说：代码可验证的是 D&D edit matrix/fragments 生成和一个加载示例，不是完整的 Multiome preprocessing。

### 图像证据怎么支持方法

`figure_analysis.md` 直接读了本地六张图：`ga1_lrg.jpg`、`gr1_lrg.jpg` 到 `gr5_lrg.jpg`。

- 图形摘要展示了 D&D-seq 从 single cells、D&D reaction、base editing call 到 patient sample/data integration 的整体逻辑。
- Figure 1 支持 assay chemistry 和 bulk footprinting：DddA split enzyme、C>T/G>A edit enrichment、target/background footprint、motif enrichment 和 ChIP-seq track comparison。
- Figure 2 支持 single-cell specificity：CA46/K562 两个 UMAP cluster 分离，CTCF edits 富集在 CA46，GATA1 edits 富集在 K562。
- Figure 3 展示 primary PBMC 的 CTCF signal 和 D&D-C.Origami 应用，但 C.Origami 代码中未找到直接实现。
- Figure 4 展示 D&D-GoT-ChA、IDH2 WT/MUT、CTCF differential binding、Cicero co-accessibility 和 C.Origami contact map，但这些主要是论文应用证据，不是当前 DnD package 可验证的代码。
- Figure 5 展示 GATA1 在 erythropoiesis 里的 binding dynamics 和 target gene module score，但完整 Multiome preprocessing/trajectory/linkage workflow 代码中未找到直接实现。

另一个小的 acquired artifact：`paper.md:9` 写的是 `images/fx1_lrg.jpg`，但本地实际文件是 `images/ga1_lrg.jpg`。图像已经从本地 `ga1_lrg.jpg` 读取。

### 论文声称但当前代码未验证的部分

这些 gap 不应该被改写成确定实现，除非后续拿到新的源码或 notebook。

| 论文部分 | 当前代码状态 |
|---|---|
| target prediction 的 `glmnet` / logistic 或 linear regression model，包含 10-fold CV、alpha search、AUC/PR AUC、Youden threshold | `MISSING`。在 acquired non-archive package 中搜索 `glmnet`, regression, AUC, sklearn/statsmodels, `cv.glmnet` 未找到直接实现。 |
| GoT-ChA genotyping / Gotcha mutation calling | `Not found`。论文指向外部 GoT-ChA/Gotcha workflow。 |
| IDH2 WT/MUT CD8 T cell 的 LMM differential CTCF binding | `Not found`。 |
| Cicero/Monocle co-accessibility analysis | `Not found`。 |
| C.Origami Hi-C prediction workflow | `Not found`。 |
| CellRanger-ATAC/ARC、Seurat/Signac QC、Monocle trajectory、LinkPeaks/AddMotifs、AddModuleScore 的完整 workflow | `Not found`，除了 README 里的 Signac/Seurat loading example。 |

### 读代码时最重要的路径

| 想理解什么 | 读哪个文件 |
|---|---|
| CLI 入口 | `DnD/main/pyproject.toml:10-24` |
| 示例运行顺序 | `DnD/main/cmd_dnd.sh:17-32` |
| Part 1 总调度 | `DnD/main/src/dnd_pt1.py:24-127` |
| BAM 预处理 | `DnD/main/src/main/step1.py:12-81` |
| pysam pileup / VCF | `DnD/main/src/main/step2.py:13-122` |
| gnomAD/custom/VAF 过滤 | `DnD/main/src/main/step3.py:12-124` |
| D&D edit VCF 和 edited-read BAM | `DnD/main/src/main/step4.py:12-108` |
| MACS2 / SEA / HOMER2 | `DnD/main/src/main/step5.py:8-233` |
| target/background 和 footprint/SNR | `DnD/main/src/main/step6.py:12-247`, `DnD/main/src/main/step6.py:250-498` |
| D&D/non-D&D VCF、count、sampling utilities | `DnD/main/src/main/dnd_acc.py:70-115`, `DnD/main/src/main/dnd_acc.py:231-318`, `DnD/main/src/main/dnd_acc.py:365-487` |
| R plotting / resize | `DnD/main/src/main/tools.R:27-175` |
| D&D edit matrix conversion | `DnD/main/src/dnd_pt4.py:160-430` |

### 最终理解

D&D-seq 的本质是把“目标蛋白是否在某个 DNA 区域附近出现”转化为“这个区域附近是否有 DddA 造成的 C>T/G>A editing footprint”。论文用多个系统证明这个 footprint 具有 factor specificity：bulk K562、CA46/K562 single-cell mixing、primary PBMC、IDH2 clonal hematopoiesis 和 erythropoiesis Multiome。

代码可验证的是这个 footprint 的核心计算管线：从 BAM 到 SNV，到 D&D-specific VCF，到 target/background motif-centered peaks，再到 footprint/SNR 和 D&D edit matrix。这里更适合作为假设生成和下游分析输入的是 Figure 3-5 中的 C.Origami、Cicero、GoT-ChA、LMM 和 Multiome trajectory 等应用，因为它们在论文里有描述和图像支持，但在当前 acquired `DnD/` package 中没有找到直接实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DnD-seq: Single-Cell Mapping Of Regulatory DNA-Protein Interactions

### Paper Metadata

- **Title:** Single-cell mapping of regulatory DNA-protein interactions
- **Method / platform:** D&D-seq, docking and deamination followed by sequencing
- **Journal / date:** *Cell*, 2026-06-04
- **DOI:** `10.1016/j.cell.2026.05.014`
- **Workspace:** `[local path omitted]`
- **Mode:** paper+code
- **Code:** GitHub snapshot `https://github.com/landau-lab/DnD`, commit `337439aaf32c83f4f98bdf2bf2fc35f201d5f255`

### Motivation

Single-cell methods can measure chromatin accessibility and gene expression, but direct mapping of transcription factor (TF) or chromatin-regulator binding remains difficult, especially for weak or transient protein-DNA interactions. Existing ChIP-seq and CUT&Tag-like approaches can work well for stable or abundant factors, but are harder to integrate into high-throughput single-cell workflows and can be biased by open chromatin (`paper.md:23-31`, `paper.md:37-39`).

D&D-seq addresses this by tethering a cytosine deaminase to antibody-labeled DNA-binding proteins. Instead of cutting or tagmenting DNA near the protein, the tethered enzyme leaves local C-to-U edits that become C>T and G>A signatures after sequencing. Those edits can be read together with ATAC, scATAC, WGS, GoT-ChA, or 10x Multiome measurements (`paper.md:39-47`, `paper.md:207-213`).

### Method Overview

The assay has two layers.

First, the wet-lab layer fixes/permeabilizes cells, labels the target factor with a primary antibody, recruits nb-DddA_NT or an IgG-binder-DddA_NT fusion, activates the split DddA enzyme with DddA_CT plus Zn^2+, and then proceeds into ATAC or single-cell library construction (`paper.md:189-213`).

Second, the computational layer identifies D&D edits and evaluates their enrichment around target motifs or reference peaks. The STAR Methods define five analytic steps: BAM preprocessing, SNV collection, germline/VAF/custom filtering, MACS2 peak calling plus motif analysis, and target/background D&D edit evaluation (`paper.md:261-269`).

The acquired code implements that core computational layer as a command-line package:

- `dnd-pt1`: preprocessing, pileup, filtering, D&D edit extraction, and initial peak calling.
- `dnd-pt2`: joint peak calling and SEA/HOMER2 motif search.
- `dnd-pt3`: target/background peak selection, motif-centered footprinting, SNR/context plots.
- `dnd-pt4`: D&D edit table, fragment, and MatrixMarket conversion for downstream single-cell loading.

These entrypoints are registered in `DnD/main/pyproject.toml:10-24`; the example script runs `dnd-pt1 -> dnd-pt2 -> dnd-pt3` in `DnD/main/cmd_dnd.sh:17-32`.

### Main Results

Figure 1 and the associated text show that D&D-seq creates factor-specific edit footprints for CTCF, GATA1, and GATA2 in K562 cells, with target motifs recovered and D&D tracks aligning with ENCODE ChIP-seq references (`paper.md:39-49`, `paper.md:397-398`).

Figure 2 extends the assay to single-cell CA46/K562 mixing. The ATAC UMAP separates the cell lines, while CTCF edits localize to CA46 and GATA1 edits localize to K562. Pseudobulk footprints and motif enrichment retain factor specificity, and FRiP benchmarking is visually much stronger for scD&D-seq than uliCUT&RUN in the figure (`paper.md:57-75`, `paper.md:400-401`).

Figures 3-5 show applications in primary PBMCs, `IDH2` clonal hematopoiesis, and erythroid differentiation. The paper uses D&D-derived CTCF or GATA1 profiles for C.Origami contact-map prediction, GoT-ChA genotype-linked regulatory analysis, Cicero co-accessibility, and 10x Multiome trajectory/target-gene analysis (`paper.md:79-109`, `paper.md:403-410`).

### Evaluation And Evidence

The paper evaluates specificity by motif recovery, target/background molecular footprints, comparison with ENCODE ChIP-seq tracks, FRiP benchmarking against uliCUT&RUN/scCUT&Tag, and a paper-described target prediction model. The target prediction model uses D&D edit features, 10-fold cross-validation with R `glmnet`, alpha search, 70:30 train/test split, and Youden-thresholded performance reporting (`paper.md:67-75`, `paper.md:277-279`).

The code-verified evaluation pieces are narrower but strong for the core pipeline. `step6.py` intersects D&D and non-D&D VCFs with target/background regions, samples peaks for footprinting, calls `motifCenteredCounts`, and dispatches R plotting (`DnD/main/src/main/step6.py:250-428`). `dnd_acc.py` repeats random sampling 10 times and writes per-distance target/background counts (`DnD/main/src/main/dnd_acc.py:365-432`), while `tools.R` plots mean/std footprints and SNR-style context summaries (`DnD/main/src/main/tools.R:47-127`).

### Code Availability And Reproducibility

The paper states that Python and R scripts for D&D-seq analysis are available on GitHub and that raw/processed cell-line data are available under GEO accession `GSE296495`; patient sequencing data are under EGA accessions `EGAD50000002273` and `EGAD50000002299` (`paper.md:137-139`). The local acquisition captured the GitHub snapshot and six figure images; no supplementary markdown was acquired.

**Reproducibility rating: 3 / 5.**

The rating is medium because the acquired package has a clear environment file, CLI entrypoints, README usage, and direct implementations for the core D&D edit-calling and footprinting workflow (`DnD/main/environment.yml:1-18`; `doc_code.md`). However, full paper reproduction requires external or missing downstream workflows for target prediction, GoT-ChA genotyping, LMM differential binding, Cicero/Monocle co-accessibility, C.Origami Hi-C prediction, and full CellRanger/Seurat/Signac/Multiome preprocessing.

### Important Implementation Gaps

The following gaps are publishable and should stay explicit unless new source evidence is acquired:

| Claim / Workflow | Status In Acquired Code |
|---|---|
| Target prediction glmnet/logistic/linear-regression model and AUC/PR-AUC evaluation | `MISSING` in non-archive package scan for `glmnet`, regression, AUC, sklearn/statsmodels, and `cv.glmnet`. |
| GoT-ChA genotype assignment and mutation-calling workflow | `Not found`; paper points to external GoT-ChA/Gotcha workflow. |
| LMM differential CTCF binding between WT/MUT CD8 T cells | `Not found`. |
| Cicero/Monocle co-accessibility workflow | `Not found`. |
| C.Origami Hi-C prediction workflow | `Not found`. |
| Full CellRanger-ATAC/ARC, Seurat/Signac QC, Monocle trajectory, LinkPeaks/AddMotifs, and module-score preprocessing | `Not found` except for a README example loading D&D edit matrices into Signac/Seurat (`DnD/README.md:349-379`). |

### Takeaway

D&D-seq is best understood as an antibody-tethered base-editing footprinting assay that turns local C>T/G>A edits into a protein-DNA interaction readout. The public package faithfully supports the core edit extraction, motif/peak, target/background footprint, SNR, and edit-matrix workflow. The paper's later biological demonstrations are convincing as paper evidence, but they are not fully reproduced by the acquired package alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
