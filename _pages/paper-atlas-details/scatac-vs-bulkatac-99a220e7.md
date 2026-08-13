---
layout: default
permalink: /paper-atlas/scatac-vs-bulkatac-99a220e7/
title: "scATAC_vs_bulkATAC"
nav: false
wide: true
description: "本文不是提出新的 peak caller 或新的单细胞聚类算法，而是用原创的匹配样本比较回答三个实验设计问题： 把 scATAC-seq 细胞聚合成 pseudo-bulk 后，是否能像 bulk ATAC-seq 一样恢复总体开放染色质结构？ 两种实验对弱开放元件，尤其经典 CTCF 位点和远端调控元件的灵敏度差多少？ 一个 scATAC-seq 簇至少需要多少细胞，才能形成可靠调控图谱；又需要多少细胞才能被聚类算法发现？"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Scientific Reports · 2025</span>
    </div>
    <h1>scATAC_vs_bulkATAC</h1>
    <p>scATAC-seq generates more accurate and complete regulatory maps than bulk ATAC-seq</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41598-025-87351-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scATAC_vs_bulkATAC">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scATAC-seq 与 bulk ATAC-seq：单细胞方案为何能用更少细胞绘制更完整的调控图谱

### 1. 这是一项 primary benchmark，而不是综述

本文不是提出新的 peak caller 或新的单细胞聚类算法，而是用原创的匹配样本比较回答三个实验设计问题：

1. 把 scATAC-seq 细胞聚合成 pseudo-bulk 后，是否能像 bulk ATAC-seq 一样恢复总体开放染色质结构？
2. 两种实验对弱开放元件，尤其经典 CTCF 位点和远端调控元件的灵敏度差多少？
3. 一个 scATAC-seq 簇至少需要多少细胞，才能形成可靠调控图谱；又需要多少细胞才能被聚类算法发现？

核心比较使用同一供者、同一红系阶段的 erythroblast：bulk ATAC-seq 约 80,000 个细胞，scATAC-seq 4,485 个细胞。作者还用公开 NK/PBMC 数据做跨数据集验证，并用下采样和 spike-in 构造细胞数阈值实验。

### 2. 为什么这个比较不能只看“总 reads 更多”

若直接比较完整数据，scATAC-seq 的测序深度明显更高，因此灵敏度优势可能只是 reads 数差异。论文用了三层控制：

- 对两个数据集统一保留正确配对、MAPQ $\geq30$ 的 reads 并去重复；
- 将 scATAC-seq 下采样到与 bulk 相近的 read depth；
- 将 bulk 下采样到与 scATAC-seq 相近的输入细胞数。

两种实验的片段长度都呈现 sub-nucleosomal、mono-nucleosomal 和 di-nucleosomal 周期，说明它们保留相似的染色质结构。等深度后的非峰背景也相近。因此，论文把灵敏度差异主要定位到活跃元件上的 signal-to-background 和文库复杂度，而不是简单归因于总体背景更低。

不过这仍是观察性机制解释：论文没有通过实验拆分每一个可能原因，也明确说 scATAC-seq 在活跃区域产生更强信号的底层原因尚未完全阐明。

### 3. 公平分析管线：相同 peak caller，再用独立标记校验

#### 3.1 预处理与 peak calling

scATAC-seq 先经 Cell Ranger ATAC v1.1.0 对 hg19 比对并产生 cell-by-peak 矩阵和 BAM；bulk 和 scATAC BAM 随后做相近 QC。两种数据都以 deepTools 生成 RPKM coverage，再由同一个 LanceOtron 深度学习 peak caller 调峰，保留分数 $>0.5$ 且不落在 blacklist 的峰。

统一 peak caller 很重要：若两种技术分别使用不同调峰算法，就无法判断差异来自实验还是软件。即便如此，47 个 bulk-only 峰中多数经人工检查被认为是 peak caller 边界的细微变化，因此“unique peak”也不等同于确定的技术专属生物信号。

#### 3.2 两套注释体系

作者先用 ChIPseeker 按与 TSS 的距离把峰分为 promoter、intron、distal intergenic 等。然后使用 erythroblast 的 H3K4me1、H3K4me3、H3K27ac 与 CTCF ChIP-seq 信号，把峰进一步注释为 enhancer、promoter、CTCF 或组合类别。

其中最关键的灵敏度标尺是 22,072 个“经典 CTCF 位点”：有 CTCF ChIP 信号，但不与 enhancer/promoter 活性标记重叠。这类位点的 ATAC 峰通常较弱，适合测试低信号开放位点的检测能力。

### 4. 峰数结果应该怎样正确读

Fig. 2 的 Venn 图给出：

- scATAC-seq unique：57,586；
- bulk unique：47；
- shared：13,680。

因此 scATAC-seq 自身共有 $57,586+13,680=71,266$ 个峰，bulk 自身共有 $47+13,680=13,727$ 个峰；两种方法的并集才是 $71,313$。这三个口径不能混用。

bulk 峰更偏向 promoter，而 scATAC-seq 增加的大量峰位于 intronic 和 distal intergenic 区域，并富集弱 CTCF 及 enhancer-like 元件。几乎所有 bulk 峰都能在 scATAC 中找到，支持“scATAC 聚合图谱包含 bulk 主体结构，并额外恢复更多弱调控元件”的解释。

### 5. 78.77% 对 4.77%：headline 数字的含义与边界

在 22,072 个经典 CTCF 参考位点中：

- 完整 4,485-cell scATAC-seq 检出 17,387 个，即 78.77%；
- 约 80,000-cell bulk ATAC-seq 检出 1,054 个，即 4.77%；
- 将 scATAC-seq 下采样到与 bulk 相近的 read depth 后，仍检出 5,029 个，即 22.78%。

78.77/4.77 约为 16.5 倍，是论文最醒目的灵敏度比较；等 read-depth 时 22.78/4.77 仍约为 4.8 倍。这说明优势不能完全由更深测序解释。

但它不是“所有 scATAC 实验普遍比所有 bulk 实验强 16.5 倍”的定律。主比较来自单一供者和特定 erythroblast 制备，且经典 CTCF 位点只代表一类较弱元件。NK 验证支持方向一致，但 bulk 与 scATAC 来自不同供者，不能作为严格匹配重复。

### 6. scATAC 揭示所谓 homogeneous 样本中的亚群

cisTopic 对 4,485 个 erythroblast 进行 LDA topic 建模后得到一个 3,871-cell 大簇和一个 614-cell 小簇。小簇的 distal peaks 大幅减少，promoter 比例上升；与邻近峰对应的 GO/KEGG 富集包括 autophagy、catabolism 和 chromatin modification。结合红细胞成熟中的 pyknosis 与 enucleation，作者推断小簇代表更晚期的 erythroblast 状态。

这里应使用“支持/提示”而非“证明”：簇身份来自染色质模式与富集解释，没有额外的同细胞 RNA、蛋白或独立实验直接确认。它展示的是单细胞分辨率能够发现 bulk 平均会掩盖的候选异质性。

### 7. 两个不同的最小细胞数：200 与 40

#### 7.1 约 200 cells：用于可靠 pseudo-bulk 注释

作者从 4,485 个 erythroblast 随机抽取 2,000、1,000、500、400、300、200、100 和 50 个细胞，重新构建 BAM、coverage 和 peaks。以 CTCF overlap 为标尺，200 个细胞检出 1,469 个经典 CTCF 位点，已接近并略高于 bulk 的 1,054；enhancer/promoter 补图也给出相似结论。

所以“200”表示在本实验条件下，一个同质簇形成 bulk-equivalent 调控注释的大致规模，不是硬性通用阈值。测序深度、细胞类型、峰强度和 QC 都会改变它。

#### 7.2 约 40 cells：用于从异质背景中形成独立簇

作者把 300、150、80、40 或 20 个 erythroblast spike 到约 3,000 个 PBMC 中，再以完全相同的 ArchR iterative LSI/UMAP/聚类流程处理。300 到 40 个细胞都形成独立簇，20 个则被分散到多个免疫簇。B cell 和 CD8 naive 的补充实验也在 40 个细胞时保持可识别。

这说明 cluster detection 与 pseudo-bulk annotation 是两个不同的功效问题：约 40 个细胞可能足以知道“这里有一个群”，但约 200 个细胞才足以对它的弱调控元件做接近 bulk 的系统注释。不能把 40-cell 结果表述为“40 个细胞即可获得完整调控图谱”。

### 8. 五张主图的证据链

- **Fig. 1**：控制细胞数/read depth，比较片段结构、背景与活跃元件信号；建立技术可比性。
- **Fig. 2**：展示基因组位置、峰集合、ChIP 标记和经典 CTCF 检出率；支撑灵敏度与调控图谱完整性结论。
- **Fig. 3**：cisTopic 发现 erythroblast 小亚群，并用峰位置和 GO 解释可能的晚期成熟状态。
- **Fig. 4**：逐级下采样，分离“数据仍可看”与“弱元件可系统注释”，得到约 200-cell benchmark。
- **Fig. 5**：PBMC spike-in 的 UMAP，比较 300 到 20 个细胞，得到约 40-cell cluster-detection benchmark。

本地五张主图均已直接检查。正文引用 Supplementary Figs.因此补充结果可按正文引用总结，不能声称已直接视觉核验每张补图。

### 9. 可复现性边界

数据是公开的：erythroblast、ChIP-seq、NK 等有 GEO accession，PBMC 来自 10x。主要软件与版本也在 Methods 中给出，包括 Cell Ranger ATAC、SAMtools、deepTools、LanceOtron、cisTopic、ArchR、ChIPseeker 和 clusterProfiler。

但论文没有提供分析代码仓库。本地也没有研究代码。尤其缺失：随机细胞下采样、barcode BAM 拆分、spike-in 合并和完整作图脚本。cisTopic topic 数选择还依赖 likelihood 曲线的人工判断，LanceOtron 需要相应模型/服务环境。因此该工作是数据可获得、流程可重建，但不是一键精确复现。

### 10. 最应带走的结论

这项 benchmark 的主要结论不是“单细胞技术只适合找亚群”，而是：高质量 scATAC-seq 在聚合后可以复现 bulk 的主开放染色质结构，同时以远少于 bulk 的细胞检出更多弱调控位点；单细胞层面又额外提供异质性。实践上要同时规划两个样本量目标：发现一个簇所需的细胞数，和为该簇绘制可靠 pseudo-bulk 调控图谱所需的细胞数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary — scATAC-seq Generates More Accurate and Complete Regulatory Maps than Bulk ATAC-seq

**Paper**: Gur & Hughes, *Scientific Reports* 15, 2025
**DOI**: 10.1038/s41598-025-87351-7
**Type**: Benchmark / comparison study

---

### Motivation & Novelty

**Biological problem**: Understanding gene regulation requires accurate maps of chromatin regulatory elements — enhancers, promoters, and CTCF-bound insulators. Bulk ATAC-seq has been the standard approach, but it generates a *population-average* accessibility profile that obscures cell-type heterogeneity and misses rare or weakly accessible elements. Single-cell ATAC-seq (scATAC-seq) was developed to address heterogeneity, but its relationship to bulk ATAC-seq in terms of signal quality, sensitivity, and practical requirements was not comprehensively characterized.

**Limitations of existing approaches**:
- **Bulk ATAC-seq** requires many cells (~80,000), provides average signal, cannot detect heterogeneity. The original bulk ATAC-seq protocol (Buenrostro et al., *Nat. Methods* 2013) and its improved OMNI-ATAC variant are limited to population-average measurements.
- **scATAC-seq** data is sparse per cell, and practical questions about minimum cell numbers for pseudo-bulking and clustering had not been rigorously benchmarked.
- Prior comparisons (Chen et al., *Genome Biol.* 2019; Baek & Lee, *Comput. Struct. Biotechnol. J.* 2020) focused on computational tool evaluation rather than technology comparison on *matched* samples.

**Novel contributions**:
1. First comprehensive matched comparison of bulk ATAC-seq and scATAC-seq using *aliquots from the same cell population*, eliminating donor and cell-type variability
2. Quantitative sensitivity benchmark using classical CTCF sites as an orthogonal reference (ChIP-seq validated)
3. Practical guidance: minimum cell counts for (a) chromatin annotation via pseudo-bulking and (b) robust cluster detection
4. Demonstration that scATAC-seq detects cellular heterogeneity in presumed homogenous populations with biological interpretation

---

### Method Overview

The study uses four linked analytical pipelines (detailed in `doc_method.md`):

1. **Matched bulk vs. scATAC-seq comparison** (erythroblasts): Same donor, same timepoint, bulk ~80,000 cells vs scATAC-seq ~4,485 cells. After QC filtering (Bowtie2/CellRanger, SAMtools MAPQ≥30, dedup), LanceOtron peak calling is applied. Peaks are annotated by genomic location (ChIPseeker) and ChIP-seq histone marks (H3K4me1, H3K4me3, H3K27ac, CTCF). Classical CTCF sites (22,072 ChIP-confirmed sites without active marks) serve as the sensitivity benchmark.

2. **Heterogeneity detection**: cisTopic (LDA-based topic modeling, 48 topics) clusters the erythroblast scATAC-seq data; cluster-specific peaks are annotated and GO/KEGG enrichment is used to biologically interpret the clusters.

3. **Cell number for chromatin annotation**: In silico downsampling (4,485 → 2000 → 1000 → 500 → 400 → 300 → 200 → 100 → 50 cells), with CTCF site detection as the benchmark.

4. **Cell number for clustering**: In silico spike-in experiment — erythroblasts (highly distinct) or B cells / CD8 naive cells (less distinct) spiked into PBMC background at 300/150/80/40/20 cells. ArchR v1.0.2 used for iterative LSI clustering and UMAP.

**Key tools**: LanceOtron (Hentges et al., *Bioinformatics* 2022, DL peak calling), CellRanger-ATAC (10X Genomics), ArchR v1.0.2 (Granja et al., *Nat. Genet.* 2021), cisTopic (Bravo González-Blas et al., *Nat. Methods* 2019), Azimuth/Seurat (Hao et al., *Cell* 2021), ChIPseeker, clusterProfiler (Yu et al., *OMICS* 2012), deepTools, bedtools.

---

### Evaluation

#### Datasets
| Dataset | GEO Accession | Cells | Purpose |
|---|---|---|---|
| Erythroblast bulk ATAC-seq | GSE193035 | ~80,000 | Primary comparison |
| Erythroblast scATAC-seq | GSE193038 | 4,485 | Primary comparison |
| NK cells bulk ATAC-seq | GSE125164 | ~80,000 | Validation (different donor) |
| PBMC scATAC-seq (merged 5 datasets) | 10X Genomics | ~4,119 NK cells | Validation |
| PBMC multiome (3k cells) | 10X Genomics | ~3,000 | Clustering experiment |
| Erythroblast ChIP-seq | GSE244929 | — | Peak annotation reference |
| NK ChIP-seq | ENCODE (ENCAN910QXX, etc.) | — | NK validation |

#### Key Results

**Sensitivity comparison** (matched erythroblasts):
- The union contains 71,313 peaks: scATAC-seq calls 71,266 peaks (57,586 unique + 13,680 shared), whereas bulk calls 13,727 (47 unique + 13,680 shared)
- 78.77% of classical CTCF sites detected by scATAC-seq (4,485 cells) vs. only **4.77%** by bulk ATAC-seq (~80,000 cells) — a **16.5× improvement**
- Even at matched read depth (scATAC-seq downsampled to ~11% of reads), 22.78% of CTCF sites detected — still **4.8× better** than bulk
- scATAC-seq strongly enriched for distal intergenic and intronic peaks (enhancer/CTCF sites) while bulk is biased toward promoters

**Signal architecture**:
- Common peaks (13,680 overlapping) have the same relative signal strength in both technologies — same peaks are "big" in both
- Fragment size distribution (mono/di/sub-nucleosomal periodicity) is identical in both technologies
- Background noise levels are comparable when read depth is equalized; the sensitivity advantage of scATAC-seq is from increased signal *over* active elements, not lower background

**Heterogeneity detection**:
- cisTopic (48 topics, t-SNE) reveals 2 distinct clusters in "homogenous" erythroblasts
- Small cluster (~minority): almost exclusively promoter peaks, loss of distal regulatory elements
- GO enrichment: autophagy, macroautophagy, catabolism, chromatin modification → consistent with pyknosis (nuclear condensation before enucleation) — a previously undocumented late erythroblast subpopulation in this culture system

**Minimum cells for chromatin annotation**:
- 500 cells: visually robust signal, most peaks preserved
- ~200 cells: comparable sensitivity to bulk ATAC-seq (1,469 vs 1,054 CTCF peaks)
- 100 cells: interpretable but increased computational challenge, major sensitivity loss for weak elements (CTCF)
- 50 cells: very poor quality

**Minimum cells for cluster detection**:
- Erythroblasts (highly distinct from PBMCs): robust at 40 cells; fails at 20 cells
- B cells and CD8 naive cells (less distinct, closer to PBMC background): also robust at 40 cells
- 40 cells is well *below* the 200-cell threshold needed for informative chromatin profiles → cluster detection is not the bottleneck; pseudo-bulking quality is

**NK cell validation**: scATAC-seq cluster (~4,119 NK cells extracted from PBMC) identifies 58,753 peaks vs. 39,778 for bulk (from different donor). Lower overlap than erythroblast comparison as expected (different donors), but confirms higher peak count in scATAC-seq.

---

### Reproducibility

**Rating: 3/5**

**Justification**: Data is publicly available (GEO + 10X Genomics), all tools used are standard and well-maintained (ArchR, cisTopic, LanceOtron, deepTools, SAMtools). However:
- No analysis scripts provided (custom Python downsampling pipeline not shared)
- Custom peak annotation/classification heuristic (ChIP-seq mark thresholds) not fully specified
- LanceOtron DL model may produce slightly different results with future updates
- cisTopic model selection (topic number = 48) requires manual judgment (second derivative of likelihood curve)
- Supplementary materials are in .docx format, not easily machine-readable

**Practical notes**:
- **Data download**: Erythroblast data from GEO GSE193035 (bulk) and GSE193038 (scATAC), ChIP-seq from GSE244929
- **Environment**: Standard bioinformatics stack; no GPU required (ArchR and cisTopic are CPU-based R packages)
- **Computational requirements**: ArchR iterative LSI on 3k cells is fast (~minutes); cisTopic with 100 models × 500 iterations is heavy (~hours on CPU, or use GPU-accelerated WarpLDA)
- **Pitfall 1**: LanceOtron requires a running server or Docker container — not a simple pip install
- **Pitfall 2**: cisTopic model selection requires visual inspection of likelihood/perplexity curves; fully automated selection may give different topic counts
- **Pitfall 3**: The in silico downsampling and spike-in scripts are custom Python code (pysam, pandas) but not provided — would need to be reimplemented

**Strengths**: Matched samples from same donor, orthogonal ChIP-seq validation, multiple datasets (erythroblast + NK), multiple cell lines (PBMC B/CD8), clear quantitative benchmarks.

**Weaknesses**: Single donor for matched comparison; custom scripts not shared; comparison in NK cells is cross-donor (bulk vs sc from different individuals); classical CTCF site definition not fully specified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
