---
layout: default
permalink: /paper-atlas/welldr-seq-66af94c3/
title: "wellDR-seq"
nav: false
description: "wellDR-seq 是一种基于 5,184 孔纳米芯片的单细胞 DNA+RNA 共测技术：它先在每个孔中裂解一个细胞，用 Tn5 给基因组 DNA 加标签，同时用 poly-dT 和模板转换反应把 RNA 变成带生物素的 cDNA；随后把所有孔合并，以生物素捕获分开 cDNA 和 DNA。因为 DNA 与 RNA 来自同一孔、共享可对应的二维细胞条形码，研究者可以在同一个细胞中直接连接拷贝数基因型和转录表型。"
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
      <span>Cell · 2025</span>
    </div>
    <h1>wellDR-seq</h1>
    <p>Coalescing single-cell genomes and transcriptomes to decode breast cancer progression</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2025.08.012" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for wellDR-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/navinlabcode/wellDR-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for wellDR-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## wellDR-seq 中文方法解读

### 一句话理解

wellDR-seq 是一种基于 5,184 孔纳米芯片的单细胞 DNA+RNA 共测技术：它先在每个孔中裂解一个细胞，用 Tn5 给基因组 DNA 加标签，同时用 poly-dT 和模板转换反应把 RNA 变成带生物素的 cDNA；随后把所有孔合并，以生物素捕获分开 cDNA 和 DNA。因为 DNA 与 RNA 来自同一孔、共享可对应的二维细胞条形码，研究者可以在同一个细胞中直接连接拷贝数基因型和转录表型。

### 它要解决什么问题

乳腺肿瘤含有多个 DNA 亚克隆和多种细胞状态。批量 WGS 与 RNA-seq 会把这些群体平均在一起，因而难以回答“某个 CNA 属于哪个细胞状态”以及“同一亚克隆的拷贝数变化是否改变了基因表达”。早期 DNA+RNA 共测方法通常需要先物理分开两类分子，或不能在扩增过程中大规模加入细胞条形码，通量多为几十到几百个细胞。论文还指出，sci-L3-RNA/DNA 和 DEFND-seq 等可扩展方法不能充分去除 DNA 上的染色质，影响数据质量。

wellDR-seq 的目标不是得到单碱基精度的完整基因组，而是在数千个细胞中同时获得两类互补读出：

- DNA：以约 220 kb 可变区间为主的全基因组拷贝数轮廓，并可在足够深度下评估到 50 kb 分辨率。
- RNA：3' 端偏倚、无 UMI 的基因表达矩阵。
- 联合输出：同一细胞的 DNA 亚克隆、RNA 细胞类型/状态，以及亚克隆层面的 CNA—表达关系。

### 实验流程：为什么两种分子最后还能对应到同一细胞

```text
单细胞悬液
  ↓ 装入 72×72 = 5,184 孔芯片并成像选择活单细胞孔
蛋白酶裂解，去除细胞膜、核膜和 DNA 上的染色质
  ├─ DNA：Tn5 tagmentation → DNA-CB1
  └─ RNA：poly-dT + RNA-CB1 逆转录，生物素化 TSO 模板转换
  ↓ RNA 富集 PCR：加入 RNA-CB2
DNA/RNA 共富集 PCR：加入 DNA-CB2，并继续扩增 cDNA
  ↓ 全芯片合并
链霉亲和素磁珠捕获生物素化 cDNA
  ├─ 磁珠组分 → RNA 文库
  └─ 上清组分 → DNA 文库
  ↓ 独立测序与计算分析，再按二维孔条形码匹配
同一细胞的 DNA 拷贝数 + RNA 表达
```

关键设计有三点。第一，蛋白酶裂解发生在孔内，论文认为这能充分去除染色质，使 Tn5 更均匀地接触裸露 DNA。第二，两套 72×72 条形码提供 5,184 个孔身份；RNA-CB1/CB2 与 DNA-CB1/CB2 分别标记两种模态。第三，生物素只位于 cDNA 的 TSO 端，因此合池后仍可物理分离两种文库。图 1B 直接显示了这套不对称标签设计。

### DNA 计算流程

原始 DNA reads 先用 bowtie2 比对到 hg19，sambamba 标记 PCR duplicate。论文过滤低比对质量、读数过少以及空 bin 超过 10% 的细胞。随后采用等预期读深的可变区间计数、GC 校正、CBS 分段和 KNN 平滑，得到每个细胞的 segment ratio；CopyKit/研究脚本再完成低质量细胞过滤、正常二倍体识别、亚克隆聚类和整数拷贝数估计。

代码中的 `findNormalCell()` 先对每个细胞的分段值计算变异系数：

$$
CV_j=\frac{\mathrm{sd}(s_j)}{\mathrm{mean}(s_j)}.
$$

它把模拟的 $N(0,0.01)$ 值加入 CV 分布，用高斯混合模型拟合，并以第一成分的 $\mu+5\sigma$ 作为二倍体/非整倍体阈值（`scripts/0_wdr_functions.R:30-82`）。这是代码证据；论文方法对其作了相同描述。

DNA 质量比较使用 overdispersion：

$$
\Phi=\frac{D-1}{\mu},
$$

其中代码先对相邻 bin 的 $(y-x)/\sqrt{y+x}$ 用 L2E 稳健估计标准差，再平方得到 $D$，最后除以平均 bin count（`0_wdr_functions.R:398-422`）。图 2A 显示 wellDR1-3 的噪声与 Arc-well、10× CNV 相近，覆盖广度高于所比较的其他方法。

### RNA 计算流程

RNA Read 1 中的 RNA-CB1+CB2 用来拆分单细胞 FASTQ；Trimmomatic 去除 TSO、poly-A 和 Nextera 接头；STARsolo 以 `--soloType SmartSeq`、`--soloUMIdedup Exact NoDedup` 比对并生成 Gene/GeneFull 计数。肿瘤数据过滤少于 200 或多于 10,000 个基因、线粒体比例高于 30% 的细胞，之后用 SCTransform v2、PCA、`RunUMAP`/`FindNeighbors` 和 `FindClusters`（resolution 0.4-0.6）分析。旧文档把 RNA 聚类写成 HDBSCAN，这是错误的；论文明确写的是 Seurat 图聚类。

RNA 化学没有 UMI，因此不能按分子标识去除 PCR 扩增重复。论文把它列为限制，并只“推断”其不会显著影响基因剂量分析；代码和实验没有证明不同亚克隆的扩增偏差必然对称。

### 如何把 DNA 亚克隆连接到 RNA 表型

DNA 与 RNA 可分别聚类，但细胞条形码提供一一对应。MDA231 验证中，DNA 得到两个 superclone、八个 subclone，RNA 得到两个表达簇；图 2D/E 把同一批细胞的身份互相投影。与 bulk WGS 的 CNA 相关性在 pseudobulk 为 0.965、亚克隆层面均值为 0.966。1% SK-BR-3 spike-in 在 DNA 和 RNA 中均被单独恢复。相反，用 CopyKAT 或 inferCNV 只从 RNA 推断 CNA 时，整体相关性仅为 0.52/0.49，且不能恢复亚克隆结构，这说明“直接共测”不是可随意由 RNA 推断替代的步骤。

### 基因剂量分析

分析仅保留至少有 20 个 RNA 细胞的癌细胞亚克隆；P3 因无癌细胞亚克隆被排除。每个亚克隆的 DNA 使用 CopyKit consensus，RNA 用 `AggregateExpression()` 形成 pseudobulk，再经 DESeq2 `vst()` 标准化（`gene_dosage.R:868-905`）。

单基因层面，代码同时计算 expression 与 segment ratio、integer CN 的 Pearson 相关。最终主分类实际使用 segment-ratio 结果，并要求 $p<0.05$ 且相关系数为正。显著负相关的基因先被标成 `Dosage-reverse genes`，随后在二分类绘图数据中被排除（`gene_dosage.R:906-918`）。这比论文 Methods 中“显著相关即 dosage-sensitive”的文字多了一个正号条件，也不能说负相关基因被简单并入 insensitive。

大区段层面，两个亚克隆之间每个 DNA segment 的 MGED 定义为该区段所有可用基因表达差的中位数。使用的是绝对阈值：

$$
|\mathrm{MGED}|\ge 0.03.
$$

- CNA 与 MGED 都变：Matched。
- 只有 CNA 变：CNA diff。
- 只有 MGED 变：RNA diff。

代码以 `abs(median_diff) >= 0.03` 实现（`gene_dosage.R:570-573`），并用 `count > 10` 过滤区段，因此恰好 10 个 bin 的区段也会被去掉；论文写的是“少于 10 个 bin”，两者边界不完全一致。

### 图证据支持了什么

- 图 1：证明条形码、两步 PCR 和生物素分离的物理设计。
- 图 2：支持技术质量、DNA/RNA 同细胞匹配、1% 稀有群体检测，以及 RNA 推断 CNA 的不足。
- 图 3：在 P1/P7 展示低复杂度祖先亚克隆、MEDICC2 系谱和共享突变；四个祖先群体具有最高 LumHR module score。这里支持“与 LumHR 谱系一致的潜在起源”，不是对所有 ER+ 肿瘤细胞起源的普遍证明。
- 图 4：八名患者中 318 个非癌细胞（1.1%）落入 16 个散发 CNA 群，所有群体均低于 2%，说明检测到的是稀有、未明显扩增的事件。
- 图 5：大区段 CNA 与表达总体同向，但单基因差异很大。图 5E 图像标签为 PGR $r=0.59$、AURKA $r=0.45$、RB1 $r=0.43$；旧文档中的数值来自误读。图 5I 的论文正文/Methods 称 Pearson，而图注称 Spearman；本地代码则先拟合 GAM，再相关拟合值与观测值以得到 0.9343869（`gene_dosage.R:307-323`）。因此 $r=0.93$ 的统计描述存在论文内部与代码之间的不一致，不能把它无条件称为原始 CN—expression Pearson 相关。

### 代码覆盖与复现边界

本地仓库 commit `c7605b400d04cd58de74a4d00ca4c817b57c9b37` 包含核心函数、MDA231 和 P1-P12 的研究脚本、基因剂量、散发 CNA、突变调用和 QC 脚本。这足以核查许多图表级计算，但总体匹配度应评为 **Medium**，不是完整可运行的 assay 实现：

- 多个脚本直接读取未随仓库提供的 `objects/*.rds` 或样本目录中的 RDS。
- 原始 DNA preprocessing 依赖外部 CNA pipeline；MEDICC2 运行以注释中的终端命令表达。
- 没有容器、`renv` lockfile、统一入口或测试。
- 湿实验步骤当然不能由这些 R 脚本复现；ICELL8cx 设备、试剂和原始数据仍是必要输入。
- 患者脚本的 clonality 调用没有一致显式覆盖 helper 的默认阈值（±0.1、90%），而 MDA231 脚本明确使用 ±0.15、88%（`wdr_mda231_process.R:601-606`）。

因此，仓库更适合“审计论文下游分析与重建部分图表”，而不是从 FASTQ 一键复现整篇论文。

### 阅读结论

wellDR-seq 的真正贡献是把一个可扩展的孔内双模态化学设计和亚克隆级联合分析连在一起：直接测 DNA 避免把 RNA 推断 CNA 当作真值，直接测 RNA 又为同一 DNA 亚克隆赋予细胞谱系与表达状态。论文最可靠的结论位于群体和区段层面；单基因机制、LumHR 起源的普遍性，以及 $r=0.93$ 的精确定义都需要保留边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## wellDR-seq: Summary

**Paper**: "Coalescing single-cell genomes and transcriptomes to decode breast cancer progression"
**Authors**: Kaile Wang, Rui Ye, Shanshan Bai, et al. (Nicholas Navin lab, MD Anderson)
**Journal**: Cell 188, 6355-6369 (2025)
**DOI**: 10.1016/j.cell.2025.08.012
**Data**: SRA PRJNA1086561, GEO GSE261713
**Code**: https://github.com/navinlabcode/wellDR-seq

---

### Motivation & Novelty

**Biological problem**: Breast cancer progression from normal epithelium to DCIS to invasive cancer remains poorly understood at the cellular level. Two key open questions are: (1) Which normal breast epithelial cell type serves as the cell of origin for ER+ cancers? (2) How do copy-number alterations (CNAs) affect gene expression at the single-cell, subclone level?

**Why existing methods fall short**:
- **Bulk sequencing** (WGS, RNA-seq): cannot resolve subclonal heterogeneity or cell-type mixtures; CNA-expression correlations are confounded by tumor purity
- **Low-throughput DNA+RNA co-assays** — DR-seq (*Nat. Biotechnol.* 2015), G&T-seq (*Nat. Methods* 2015), SIDR-seq (*Genome Res.* 2018), DNTR-seq (*Mol. Cell* 2020), scONE-seq (*Sci. Adv.* 2023), scTrio-seq (*Cell Res.* 2016): require physical separation of DNA and RNA before amplification; limited to tens to hundreds of cells; cannot add cell barcodes at scale
- **Scalable alternatives** — sci-L3-RNA/DNA (*Mol. Cell* 2019), DEFND-seq (*Nat. Methods* 2025): chromatin not fully removed from DNA, leading to poor coverage uniformity; DEFND-seq shows only 9.1% exon mapping rate vs. ≥92% for wellDR-seq
- **RNA-based CN inference** — CopyKAT (*Nat. Biotechnol.* 2021), inferCNV (CTAT Project 2019): correlate only r=0.52-0.49 with ground-truth DNA copy number; cannot resolve subclonal structure

**Unique contributions**:
1. **High-quality, high-throughput simultaneous DNA+RNA** at scale (up to 2,600 cells per chip; 33,646 cells from 12 patients)
2. Protease-based complete chromatin removal → clean DNA with high breadth of coverage and low overdispersion
3. **Direct discovery of ancestral cancer subclones** with linked lineage identity (LumHR cell of origin)
4. **Sporadic CNA detection** in normal non-cancer cells across breast tissue compartments
5. **Subclone-level gene dosage quantification** that separates cis-associated DE genes from trans-associated changes and tests dosage-sensitive versus dosage-insensitive behavior.

---

### Method Overview

wellDR-seq uses the ICELL8cx nanowell platform (5,184 wells) for simultaneous single-cell DNA+RNA co-profiling:

1. **Cell loading**: diluted to ~1 cell/nanowell; imaging-based singlet selection
2. **Protease lysis**: removes all chromatin from DNA (critical innovation); 55°C→70°C
3. **Dual labeling**: Tn5 tagmentation adds DNA barcodes; poly-dT + biotinylated TSO captures RNA
4. **Two-step PCR**: RNA enrichment (6 cycles) then DNA+cDNA co-enrichment (10 cycles)
5. **Biotin separation**: streptavidin beads pull down cDNA; supernatant = DNA library
6. **Sequencing**: STARsolo SmartSeq mode for RNA; variable-bin CN pipeline for DNA

Key computational tools: CopyKit (custom), Seurat 4.1.0, DESeq2, MEDICC2, GATK/MuTect2, HDBSCAN.

---

### Evaluation

#### Technical Benchmarking (MDA231 cell line)

| Metric | wellDR-seq | Best competitor |
|--------|-----------|-----------------|
| Overdispersion (DNA) | Comparable to Arc-well, 10× CNV | Lower = better |
| Breadth of coverage | Significantly higher than DLP+, 10× CNV, DOP-PCR, DEFND-seq (p<2.2e-16) | Higher = better |
| Mean genes/cell (RNA) | 2,654-2,675 | Takara Bio: 2,559 (p>0.05) |
| Exon mapping rate | ≥92% | 10× Genomics: 76.4% |
| Rare cell detection | Down to 1% (spike-in validated) | — |
| CNA-bulk WGS correlation | r=0.965 (pseudobulk), r=0.966 (subclone level) | — |

#### Biological Findings

**Study**: 33,646 cells from 12 ER+ breast cancers (3 DCIS, 9 synchronous DCIS-IDC or IDC); immune cells depleted (CD45−); 5 patients with 1-3 chips, up to 5 chips for one patient.

**Key results**:

1. **Ancestral subclones (4/12 patients)**: In P1 (2,901 cells) and P7 (2,069 cells), rare subclones with only 1-2 CNAs (chr22 loss in P1, chr16q loss in P7) were identified as ancestral populations. Validated by somatic mutations (12 shared mutations in P1's c2 subclone). Module scoring showed all 4 ancestral subclones had highest LumHR lineage score, lowest LumSec and MyoEpi scores. Major cancer subclones showed reduced LumHR identity (P1: p=0.03; P7: p=0.09).

2. **Sporadic CNAs in non-cancer cells**: Merged 8 patients → 318 cells (1.1%) with sporadic CNAs from 16 clusters. CNA cells: 85% from epithelial lineages (LumSec 70.7%, LumHR 29.3%), 0% from MyoEpi. Stromal CNA cells showed mainly chrX gain/loss. All sporadic CNA clusters had <2% frequency and were not expanded. Consistent with Lin et al. (*Nature* 2024) showing aneuploid cells in normal breast tissue.

3. **Gene dosage relationships** (11 patients integrated, P3 excluded):
   - Cis DE gene fraction: mean=0.31 (high variation; 11 subclone pairs across samples)
   - MGED concordance: 55.71% ± 23.17% DNA segments have matching MGED (18% CNA-only, 26.5% RNA-only)
   - Segment-level r=0.93 (p<2.2e-16); near-linear up to CN=13
   - Dosage-sensitive examples: PGR, AURKA and RB1 (Figure 5E reports significant Pearson associations); FHIT and CDH1 are additionally named in the Discussion
   - Dosage-insensitive genes: PIK3CA (p=0.55), BRCA1 (p=0.30), TP53 (p=0.94)

---

### Reproducibility

**Rating: 3/5**

**Justification**:
- Code is publicly available on GitHub with per-patient R scripts and core function library
- Pre-load data (bin coordinates, HBCA markers, barcode lists) included
- Data deposited in SRA and GEO
- **Barriers**: (1) No container/environment specification (R 4.1.2 + many packages required); (2) Raw processed RDS objects (per-patient DNA+RNA) are not in the repo — gene dosage analysis loads from `./objects/*.rds` which must be generated by running per-patient scripts first; (3) Per-patient scripts require running the CNV pipeline separately; (4) Some scripts have hardcoded paths (e.g., `source("/wellDR-seq-main/R_scripts/0_wdr_functions.R")` in DNA_QC.R)
- **Partial discrepancy**: Clonality cutoffs in per-patient scripts P1-P12 may use function defaults (±0.1) rather than paper's stated ±0.15
- Reagents: ICELL8cx chip requires Takara Bio equipment (not universally available)

**Practical notes**:
- Environment: R 4.1.2 with packages listed in Key Resources table; no `renv` lockfile provided
- Data availability: SRA PRJNA1086561 (raw), GEO GSE261713 (processed)
- Comparison data: multiple public datasets (Arc-well PRJNA799605, 10× CNV PRJNA629885, DLP+ EGAS00001003190)
- Entry point: start with per-patient scripts (P1-P12) → gene_dosage.R → sporadic_CNA.R

**Strengths**: Comprehensive supplementary data; reproducible benchmarking; code is per-patient with clear structure.

**Weaknesses**: Missing environment specification; intermediate RDS files not published; hardware dependency (ICELL8cx platform); no unit tests.

---

### Limitations

1. **DNA data focused on CNAs, not mutations**: wellDR-seq DNA is optimized for whole-genome copy-number profiling; targeted mutation panels would require additional capture step
2. **No UMIs in RNA**: PCR amplification bias not corrected; gene counting less accurate than Smart-seq3 or 10× Genomics 3' v3
3. **Throughput limited to 5,184 wells**: non-Poisson loading and larger chips would further scale
4. **ER+ cancers only**: 12 patients, all ER+; findings about LumHR cell of origin may not generalize to TNBC or HER2+ subtypes
5. **Protease lysis chemistry**: specifically designed for ICELL8cx; not adaptable to droplet-based platforms without re-engineering

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
