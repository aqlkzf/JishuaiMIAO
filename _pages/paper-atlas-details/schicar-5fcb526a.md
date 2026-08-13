---
layout: default
permalink: /paper-atlas/schicar-5fcb526a/
title: "scHiCAR"
nav: false
description: "基因表达不仅取决于启动子是否开放，还取决于远端增强子能否在三维空间接触启动子。过去的单细胞多组学通常只能同时测三者中的两个：RNA、开放染色质或染色质接触。把来自不同细胞的三张图计算对齐，会受到取样差异和整合模型影响。 scHiCAR 的目标是让同一个细胞核产生三种共享细胞身份的读出： RNA 文库：转录本； DNA R2：Tn5 标记的开放染色质； DNA 配对读段：开放位点与其空间邻近 DNA 的连接。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>scHiCAR</h1>
    <p>Trimodal single-cell profiling of transcriptome, epigenome and 3D genome in complex tissues with scHiCAR</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03013-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scHiCAR">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/DiaoLab/scHiCAR" target="_blank" rel="noopener noreferrer" aria-label="Open code for scHiCAR">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scHiCAR：同一个细胞里怎样同时读出 RNA、开放染色质和三维接触

### 1. 方法要解决的核心矛盾

基因表达不仅取决于启动子是否开放，还取决于远端增强子能否在三维空间接触启动子。过去的单细胞多组学通常只能同时测三者中的两个：RNA、开放染色质或染色质接触。把来自不同细胞的三张图计算对齐，会受到取样差异和整合模型影响。

scHiCAR 的目标是让同一个细胞核产生三种共享细胞身份的读出：

- RNA 文库：转录本；
- DNA R2：Tn5 标记的开放染色质；
- DNA 配对读段：开放位点与其空间邻近 DNA 的连接。

这里“同一细胞 ground truth”指三个文库可以由组合条码回到同一细胞核，并不表示每个 RNA 分子都能与某一条接触直接配对，也不自动证明增强子调控因果。

### 2. 四轮条码与 8490 万种组合

实验按顺序加入 BC1、BC2、BC3 和 BC4。理论组合数为：

$$
96^4=84{,}934{,}656.
$$

但 Methods 的实际第一轮使用 48 个 barcoded Tn5 和 48 个 RT primer；BC2、BC3 各使用 96 个连接条码，BC4 是 PCR index。论文把多批/索引组合的最大设计空间写成 8490 万，不能把它简化为“每一步实验都在 96 孔中用了 96 个等价细胞条码”。

本地预处理代码主要处理 RNA/DNA 读段中的 18 bp 条码，即三个 6 bp 片段，并按白名单允许单错配纠正；BC4 更接近文库索引。代码不能反向证明湿实验每一步都正确执行。

### 3. 湿实验从左到右怎样读

#### 第一步：同孔完成 Tn5 切割和逆转录

交联细胞核进入 48 个孔。带 BC1 的 Tn5 在开放染色质插入接头；带对应 BC1 的 oligo-dT 和随机六聚体引发 RNA 逆转录。因此 RNA 和开放染色质先获得同一轮身份。

#### 第二、三步：pool–split 加 BC2、BC3

细胞核先混池，再分到 96 孔连接第二轮条码；重复一次加入第三轮条码。三个条码共同降低不同细胞产生相同身份的概率。混合人/鼠细胞实验测得条码碰撞率 2.69%，这是具体实验条件下的观测值，不应直接由简单生日问题公式外推到 162 万脑细胞数据。

#### 第四步：SDS 物理分离 RNA 与 DNA

0.5% SDS、62°C 处理使带条码 cDNA 进入上清，而细胞核 DNA 留在沉淀。两部分之后分别建库并加入 BC4。这个分离步骤是 scHiCAR 把同一细胞身份传到两个文库、又让二者采用不同化学流程的关键。

#### 第五步：DNA 端只放大“开放位点锚定的接触”

沉淀中的 DNA 先用 CviQI 原位消化并连接空间邻近片段，再逆交联、用 NlaIII 二次消化并自连接成环。PCR 一端锚定 Tn5 接头，只有同时满足以下条件的分子容易被放大：

1. 该端原先是开放染色质，因而被 Tn5 标记；
2. 它与另一段空间邻近 DNA 完成原位连接；
3. 二次消化后形成可被引物扩增的环。

所以 scHiCAR 不是无偏全基因组 Hi-C。它主动富集以候选 CRE 为锚点的接触，这解释了为什么长程顺式接触比例高于 Dip-C、LiMCA，也意味着两类方法捕获目标不同，不能只按每细胞总接触数判定优劣。

### 4. 三条计算支路

#### RNA

`1_RNA_preprocess/Snakefile` 修剪接头、拆分 oligo-dT/随机六聚体读段、提取并纠正条码，输出校正 FASTQ。STAR 比对和表达矩阵生成只在 README 说明中出现，没有集成进该 Snakemake 工作流。

#### ATAC

DNA R1 经过 BWA/Snaptools 比对，`scHiCAR_R2_parse.py` 使用 `MAPQ >= 20`、片段长度不超过 1,200 bp，并通过 barcode-rank knee 选择细胞，输出标准 fragment 文件。

#### 三维接触

双端 DNA 使用 BWA-MEM `-SP` 和 pairtools；本地 workflow 设置 `MAPQ >= 10`、最大插入 2,000 bp，保留 UU/UR/RU 类型并去重，输出 `.pairs`。之后可按 RNA 注释聚合成细胞类型 pseudobulk contact matrix，或拆成单细胞输入 Higashi/Fast-Higashi。

### 5. scDeepLUCIA 到底做了什么

单细胞接触极稀疏，5 kb loop 不能可靠地逐细胞调用。论文的 scDeepLUCIA 在细胞类型聚合矩阵上工作：以高深度 bulk HiCAR 的 Peakachu loops 作为训练标签，联合低分辨率接触矩阵、开放染色质和序列特征，学习在浅测序 scHiCAR pseudobulk 中预测 CRE 相关 loops。

因此必须保留三个边界：

- 论文的 5 kb loops 是细胞类型 pseudobulk 结果，不是每个细胞各自的 loop calls；
- bulk HiCAR 用于模型训练标签，训练标签不等于无误差的真值；
- 本地 `code/` 快照没有 `scDeepLUCIA` 实现；论文指向另一个 `kaistcbfg/scDeepLUCIA` 仓库，本次没有把它当作本地已验证代码。

图 4 的下采样结果说明模型在较少细胞的聚合矩阵上仍可恢复许多全量数据 loops；它不表示 5,000 个细胞里的每个细胞都拥有高分辨率接触图。

### 6. 增强子—基因配对的证据链

作者先要求远端 cCRE 与启动子被 scDeepLUCIA loop 连接，再计算 22 个脑细胞类型之间的可及性—表达 Pearson 相关：

$$
r_{eg}=\operatorname{corr}(A_e,E_g).
$$

经 FDR 筛选后得到 20,270 个候选增强子—基因对。VISTA enhancer、H3K27ac、跨细胞类型表达相关和功能富集为这些配对提供外部支持。

但 loop、相关性和活性标记仍主要是功能注释证据；真正证明某增强子调控某基因，需要删除/抑制增强子或扰动接触后观察目标表达。

### 7. 六张主图怎样连起来

1. **图 1**：湿实验设计、混合细胞验证，以及开放位点和长程接触富集。
2. **图 2**：5,313 个脑细胞中三种模态各自聚类，以及与其他方法的每细胞捕获量比较。
3. **图 3**：162 万脑细胞聚合后，22 个细胞类型的 RNA、ATAC 与 3D 结构和 bulk/snATAC 参照一致。
4. **图 4**：scDeepLUCIA 的训练/推断、下采样稳健性和细胞类型特异 loops。
5. **图 5**：利用 loops、开放性和表达筛选候选增强子—基因对，并用 VISTA/H3K27ac 支持。
6. **图 6**：肌肉损伤后 0、5、7 天的细胞，沿 RNA pseudotime 比较表达、开放性和 scA/B compartment。三维变化可先于、同步于或晚于转录变化。

图 6 的时间轴是跨样本阶段加推断 pseudotime，不是对同一细胞连续拍摄。单细胞 contact matrices 还经过 Higashi 类方法插补，图中平滑结构不能当成原始单细胞接触计数。

### 8. 论文与本地代码的真实覆盖关系

| 环节 | 本地证据 | 覆盖状态 |
|---|---|---|
| RNA/DNA 条码修剪和纠错 | 1、2 号 Snakemake | Exact/Partial |
| ATAC fragments | 3 号 Snakemake + Python/R | Exact |
| contact pairs | 4 号 Snakemake + pairtools | Exact |
| Seurat/ArchR/MACS2/cooler/Higashi 示例 | `5_downsteam_analysis/README.md` | Partial；手工示例、有占位路径和语法问题 |
| STAR 表达矩阵 | README 说明 | Partial；未自动化 |
| scDeepLUCIA | 本地未找到 | Not found；外部仓库 |
| 20,270 enhancer pairs、肌肉 pseudotime、论文统计图 | 本地未找到完整脚本 | Not found |

旧文档所说“Seurat/ArchR/Higashi 下游完全不在仓库”已经不准确：当前 README 确实给出代码片段。但它仍不是端到端可复现分析，示例含 `The/PATH/...`、缺失 Higashi 配置文件，并有 `config = ./higashi.JSON"` 这样的语法错误。

### 9. 复现时最重要的边界

- 正确代码入口是论文列出的 `https://github.com/DiaoLab/scHiCAR`；旧元数据中的 `yueyuanxu/scHiCAR` 不是论文 Code availability URL。
- 本地快照没有 `.git`，因此无法从本地确认精确 commit。
- GEO 数据为 `GSE305889`；loops 另存于 Zenodo `10.5281/zenodo.18196030`。
- 本地有示例 FASTQ 和条码白名单，但没有完整原始数据、参考基因组、全部配置、环境锁定或论文全部下游脚本。
- 论文报告的成本、规模和性能是在其特定实验、测序深度与比较设置下得到的，不应外推成所有实验的固定保证。

一句话总结：scHiCAR 的真正创新不是“同时跑三个软件”，而是用同一套组合条码把 RNA、开放染色质和开放位点锚定的三维接触归回同一细胞；它最强的高分辨率 loop 和增强子结论则依赖细胞类型聚合、外部训练的 scDeepLUCIA 与后续统计，不能等同于逐细胞直接观测。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scHiCAR: Trimodal Single-Cell Profiling of Transcriptome, Epigenome and 3D Genome

**Paper:** Wei et al., *Nature Biotechnology*, 2026
**DOI:** 10.1038/s41587-026-03013-7
**Code stated by paper:** https://github.com/DiaoLab/scHiCAR (processing) + https://github.com/kaistcbfg/scDeepLUCIA (loop caller). Only the processing snapshot is present locally, without `.git` commit metadata.

---

### Motivation & Novelty

#### The Problem

Gene regulation requires coordinated action among three genomic modalities: the **transcriptome** (what genes are active), the **epigenome** (where regulatory elements are accessible), and the **3D genome** (which regulatory elements physically contact gene promoters). Capturing all three from the same individual cells has been technically impossible — prior methods captured at most two.

**Why computational integration of separately profiled cells falls short:**
- Different cells are sampled in each experiment (sampling bias)
- Rare cell types detected in one assay may be missed in another
- The 3D genome and epigenome do not always track together — some genes change compartment before or after chromatin opening; joint analysis from different cells cannot resolve this
- Integration methods (Seurat WNN, etc.) introduce artifacts and cannot establish ground truth for per-cell regulatory dynamics

#### Limitations of Existing sc3C Methods

| Method | Throughput | mRNA | ATAC | Contacts | Key Limitation |
|--------|-----------|------|------|----------|----------------|
| Dip-C (*Science* 2018) | Low (~hundreds) | No | No | High | Individual cell processing, no ATAC/RNA |
| snm3C (*Nat Methods* 2019) | Low–medium | No | No | Medium | No RNA/ATAC |
| HiRES (*Science* 2023) | Low–medium | Yes | No | Very high | No ATAC; low throughput |
| GAGE-seq (*Nat Genet* 2024) | Medium | Yes | No | High | No ATAC; no long-range enrichment |
| LiMCA (*Nat Methods* 2024) | Low | No | No | Medium | No RNA/ATAC; low long-range fraction |
| ChAIR (*Nat Methods* 2025) | Very low (~1000× below scHiCAR) | Yes | Yes | Very low | Low molecular efficiency; cannot resolve cell types from 3D genome alone |

The absence of biotin-dNTP enrichment in Dip-C, LiMCA, HiRES, and GAGE-seq means only ~6–13% of captured contacts are long-range cis-interactions (>20kb), the biologically most informative class.

#### scHiCAR's Contributions

1. **True trimodal single-cell profiling** — mRNA, open chromatin, and chromatin contacts from the same cell (ground truth)
2. **Plate-based combinatorial barcoding** — up to 84.9M unique barcodes, $0.04/cell cost, accessible in 3-4 days by one researcher
3. **CRE-anchored Hi-C enrichment** — 48% long-range cis-contacts (vs 6-10% for Dip-C/LiMCA)
4. **Scalability** — 1.62M cells profiled in a single study (largest sc3C dataset published)
5. **scDeepLUCIA** — new deep-learning loop caller robust to rare cell types (>75% loop recovery at 5,000 cells)
6. **Functional enhancer prediction** — superior to coaccessibility models (OR=1.78 vs 1.33 for VISTA enhancers)
7. **Single-cell 3D genome dynamics** — gene-locus-specific 3D remodeling during muscle stem cell regeneration

---

### Method Overview

#### Experimental Design

scHiCAR uses a **plate-based, split-pool combinatorial barcoding** strategy with four rounds of molecular barcoding:

**Round 1 (BC1):** Crosslinked nuclei distributed into 48-well plates. Tn5 transposase (barcoded) fragments open chromatin while RT primers (also barcoded with same BC1) initiate mRNA reverse transcription simultaneously. Critical: both Tn5 adaptors and RT primers carry the same well-specific BC1.

**Rounds 2-3 (BC2, BC3):** All nuclei pooled → redistribution into 96-well plates → sequential ligation of barcoded adaptors.

**Physical separation:** FACS-sorted nuclei treated with 0.5% SDS at 62°C → RNA (cDNA) released to supernatant, DNA remains in pellet.

**RNA library (from supernatant):** Reverse crosslink → second RT + template switching → PCR amplification → tagmentation → final indexed PCR.

**DNA library (from pellet):** CviQI restriction digest → in situ ligation (links Tn5-tagged open chromatin to spatially proximal DNA) → NlaIII digest → self-ligation (circularization) → PCR with primers anchored on Tn5 adaptor. This 4C-seq-like design specifically amplifies fragments that are both open-chromatin-tagged AND correctly in situ ligated, achieving the CRE-anchored enrichment.

**Round 4 (BC4):** PCR amplification adds the final index.

See `doc_method.md` for detailed step-by-step algorithm and `diagrams/method_pipeline.svg` for visual overview.

#### Computational Pipeline

1. **Barcode processing** — 4-round demultiplexing with 1-mismatch tolerance per 6bp barcode slice
2. **RNA alignment** — STAR alignment to generate gene expression matrices
3. **ATAC fragment processing** — BWA alignment + quality filtering (MAPQ≥20, length≤1200bp) + knee-point cell selection
4. **Hi-C contact processing** — BWA-MEM `-SP` mode + pairtools (MAPQ≥10, valid pair types UU/UR/RU) + deduplication
5. **Pseudo-bulk analysis** — Aggregate by cell type → MACS2 peaks + cooler matrices + compartment/TAD analysis
6. **Single-cell analysis** — Seurat (RNA), ArchR (ATAC), Higashi/Fast-Higashi (3D genome)
7. **scDeepLUCIA loop calling** — DNN-based loop prediction robust to low cell numbers

---

### Evaluation

#### Datasets

| Experiment | Cells | Cell Types | Tissue |
|-----------|-------|-----------|--------|
| Cell line validation | 2,456 (H1+GM12878+mES) | 3 | Cell lines |
| Mouse brain pilot | 5,313 | 22 | Frontal cortex |
| Mouse brain large-scale | 1,620,000 | 22 | Frontal cortex |
| Mouse muscle regeneration | 41,578 | 8 | Skeletal muscle |

**Data availability:** GEO accession GSE305889. scDeepLUCIA loops: Zenodo (DOI: 10.5281/zenodo.18196030) and http://junglab.kaist.ac.kr/Dataset/scDeepLUCIA.

#### Benchmarking Results

**Accuracy (cell line validation):**
- Transcriptome-based cell type accuracy: **100%** (vs BC1 ground truth)
- ATAC-based accuracy: **97-99%**
- 3D genome-based accuracy: **97-99%**
- Barcode collision rate: **2.69%** (3 cell types mixed)

**Molecular efficiency (mouse brain, vs comparators):**
- mRNA: **18,957 UMIs/cell** (ChAIR: 2,634; 10x Multiome: 3,284; GAGE-seq: 19,803; HiRES: 28,867)
- ATAC fragments: **24,455/cell** (ChAIR: 1,952; 10x Multiome: 23,713)
- Open-chromatin contacts: **19,622/cell** (ChAIR: 385 — 51-fold higher than ChAIR)
- Long-range cis fraction: **48%** (Dip-C: 6%; LiMCA: 10%; HiRES: 13%; GAGE-seq: 28%)

**3D genome quality:**
- Eigenvector PCC vs bulk HiCAR: 0.91–0.93
- Insulation score PCC vs bulk HiCAR: 0.90–0.96
- Loop overlap with bulk HiCAR: 52–63%
- Eigenvector PCC vs in situ Hi-C: 0.98

**scDeepLUCIA:**
- AUROC on downsampled bulk HiCAR: **0.9494** (vs CovNorm 0.74, Peakachu 0.65)
- Loop recovery at 5,000 cells (from 120,000): **>75%**
- Anchors overlapping open chromatin: **>98%**
- CTCF at both anchors with convergent motifs: **~60%**
- Cross-species AUROC (human→mouse or vice versa): **≥0.93**

**Enhancer validation (VISTA database, n=182 forebrain enhancers):**
- scHiCAR loops alone: OR = **1.78** (P = 0.00040)
- + H3K27ac: OR = **2.02** (P = 0.00059)
- coaccessibility alone: OR = 1.33; H3K27ac alone: OR = 1.35

**Mouse brain (1.62M cells):**
- 554,946 total open chromatin peaks; 260,781 unique accessible cCREs
- 70% overlap with BICCN snATAC-seq peaks (matched cell types)
- 294,395 unique CRE-associated interactions at 5kb (22 cell types)
- 20,270 high-confidence enhancer-gene pairs (FDR<0.05)

**Muscle regeneration:**
- 8 cell types identified in 41,578 nuclei
- 19,255 MuSC and progeny cells traced along regeneration pseudotime
- scA/B score–mRNA correlation: R=0.19 (comparable to GAGE-seq R=0.22)
- Demonstrated gene-locus-specific 3D remodeling patterns (Myh3, Ncam1, Agbl1)

---

### Reproducibility

**Rating: 3/5**

**Strengths:**
- Processing code publicly available (Snakemake pipelines, well-documented)
- The paper points to a separate scDeepLUCIA repository; it is not included or verified in this local snapshot
- Complete data deposited to GEO (GSE305889)
- Chromatin loops deposited to Zenodo
- Detailed Methods section with exact reagent catalog numbers, concentrations, and step-by-step protocol
- Barcode whitelist files included in code repository

**Weaknesses:**
- Protocol requires specialized equipment: Sony SH800 FACS sorter, thermomixer (ika MS 3)
- scDeepLUCIA training requires bulk HiCAR data as ground truth (expensive to generate)
- Downstream analysis is only partially scripted: the current README gives manual Seurat, ArchR, MACS2/cooler and Higashi/Fast-Higashi examples, but has placeholders and omits paper-complete analyses
- RNA alignment (STAR) not integrated into Snakemake pipeline
- The 1.62M-cell analysis needs substantial compute and storage, but no verified end-to-end resource budget is present locally
- No containerized environment (Docker/Singularity) provided — dependency management can be challenging
- Large-scale cost depends on cell number and sequencing depth; the local evidence does not support a fixed total-cost estimate

**Practical notes for reproduction:**
1. Start with the cell line validation (3 cell types, 2,456 cells) — uses publicly available cell lines, no tissue collection needed
2. Barcode whitelist files are provided in the code repository (`scHiCAR_RNA_18bp_barcode.txt.gz`, `scHiCAR_DNA_18bp_barcode.txt.gz`); oligo sequences in Supplementary Table 1
3. Genome references: mm10 (mouse), hg38 (human) with BWA index and chromosome sizes required for config.yaml
4. For scDeepLUCIA: pre-trained models available; re-training requires bulk HiCAR from matched species (expensive); de novo inference on scHiCAR data requires only the ATAC + contact outputs
5. GEO accession discrepancy: main text cites **GSE305889** (use this); reporting summary cites GSE267126/267117/267118 with reviewer tokens — these appear to be pre-publication reviewer access codes
6. RNA library uses SMART-seq-like chemistry — sequencing on paired-end mode; RNA reads are NOT compatible with standard 10x UMI-based pipelines (use STAR with custom barcode extraction from Stage 1)
7. scHiCAR is explicitly designed for complex tissues — simpler single-cell culture systems may not challenge its advantages over existing methods

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
