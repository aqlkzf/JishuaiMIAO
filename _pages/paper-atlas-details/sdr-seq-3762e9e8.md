---
layout: default
permalink: /paper-atlas/sdr-seq-3762e9e8/
title: "SDR-seq"
nav: false
description: "SDR-seq（single-cell DNA–RNA sequencing）把“这一个细胞在目标位点是什么基因型”和“这一个细胞的目标基因表达多少”放进同一次液滴多重 PCR 测量。它不依赖 gRNA 身份猜测编辑结果，而是直接测内源 gDNA；同时用原位逆转录和 UMI 测量目标 RNA，因此能把 REF/HET/ALT 基因型与表达表型在细胞级连接起来。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SDR-seq</h1>
    <p>Functional phenotyping of genomic variants using joint multiomic single-cell DNA–RNA sequencing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02805-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SDR-seq 方法解释：在同一个单细胞里直接读取基因型与靶向表达

### 一句话理解

SDR-seq（single-cell DNA–RNA sequencing）把“这一个细胞在目标位点是什么基因型”和“这一个细胞的目标基因表达多少”放进同一次液滴多重 PCR 测量。它不依赖 gRNA 身份猜测编辑结果，而是直接测内源 gDNA；同时用原位逆转录和 UMI 测量目标 RNA，因此能把 REF/HET/ALT 基因型与表达表型在细胞级连接起来。

### 1. 为什么需要直接联合测量

精确编辑常产生低效率和多种结果。若只按细胞携带的 gRNA 推断基因型，就会把未编辑、杂合和纯合编辑细胞混在一起；转录本测序又无法覆盖多数非编码变异。全基因组单细胞 DNA–RNA 方法虽范围广，但在高通量条件下 gDNA 很稀疏，容易发生 allelic dropout（ADO），难以可靠判断合子性。

SDR-seq 的选择是牺牲全基因组覆盖，换取目标区域的深覆盖：预先设计一组 gDNA amplicon 和 RNA amplicon，在同一细胞中同时扩增。论文验证到总计 480 个目标（240 gDNA + 240 RNA），适合已有候选位点和候选表达读出的实验，而不是无偏发现所有变异或全转录组探索。

### 2. 实验流程：先给 RNA 留身份，再把 DNA 和 cDNA 一起扩增

#### 2.1 固定、通透与原位逆转录

细胞先固定和通透。定制 poly(dT) RT primer 在细胞内把 RNA 逆转录成 cDNA，并加入 UMI、sample barcode（sample BC）和 capture sequence（CS）。sample BC 既标记样本/处理条件，也帮助识别 doublet 和过滤环境 RNA 污染；UMI 用于 RNA 分子去重。

论文比较 PFA 与 glyoxal 固定。两者的 gDNA 检测相近，而 glyoxal 的 RNA target/UMI 检出更好。这个结论来自所测 iPS 体系，不能泛化为所有组织和固定条件。

#### 2.2 Tapestri 的两次液滴操作

带有 gDNA 和已生成 cDNA 的细胞进入 Mission Bio Tapestri：

1. 第一轮液滴中，细胞裂解、proteinase K 处理，并加入各 gDNA/RNA target 的 reverse primer；
2. 第二轮液滴加入带 CS overhang 的 forward primer、PCR 试剂和 cell-barcoding bead；
3. PCR amplicon 的 CS 与 bead 上互补 CS 配对，使同一液滴中的 gDNA 与 RNA amplicon 获得同一 cell barcode；
4. emulsion 打破后，按 reverse primer overhang 分开构建两种 NGS library。

gDNA reverse primer 使用 Nextera R2N overhang，RNA 使用 TruSeq R2 overhang。分开建库允许 gDNA read 覆盖整个目标扩增子和变异位点，而 RNA read 同时保留 transcript、cell BC、sample BC 与 UMI 信息。

### 3. SDRranger 如何从 FASTQ 恢复单细胞计数

本工作区有两个代码面：`SDRranger/` 是 Python FASTQ 处理器，`SDR-seq/` 是论文各实验的参考构建、GATK 和 R 分析脚本。

#### 3.1 条形码结构不是固定切片问题

cell barcode 由多个 barcode block 与 linker 组成，linker 可变长。`SDRranger/bc_aligner.py` 不是按固定坐标硬切，而是对候选模板做带 gap 的 pairwise alignment；程序还比较前 500 条 reads，自动判断哪一个 FASTQ mate 是 barcode read。

cell BC 的单段纠错由 `BCDecoder` 完成：若 raw barcode 精确命中 whitelist 直接接受；否则寻找允许编辑距离内的唯一候选，若没有候选或最佳候选并列则拒绝。sample BC 走 `SBCDecoder`，使用 free-divergence decoder。拒绝模糊条形码减少错配，但会损失一部分 reads。

#### 3.2 RNA 与 gDNA 走不同处理路径

RNA path 用 STAR 对目标转录参考比对，将 `CB/CR/UR/FL` 等标签写入 BAM，然后在每个 cell–gene 内纠正 UMI。gDNA path 先从 reads 提取条形码并裁剪，再做 paired-end STAR 比对，最后按 read name 把条形码标签重新附回 BAM。

主要标签为：

- `CB`：纠正后的完整 cell barcode（含 sample barcode pieces）；
- `CR`：原始 cell barcode；
- `UB`：纠正后 UMI，仅 RNA；
- `UR`：原始 UMI；
- `FL`：linker 的组合长度。

#### 3.3 UMI directional network

RNA 中同一 cell、同一 gene 的 UMI 可能因测序错误形成低计数“子 UMI”。`umi.py` 在编辑距离允许的 UMI 间连边；高计数 UMI $A$ 可吸收低计数 UMI $B$ 的条件为：

$$
n_A \ge 2n_B-1.
$$

连通分量最后归并到代表 UMI，生成 `UB` 和 UMI count matrix。这是分子计数纠错规则，不是基因表达归一化模型。

### 4. 从计数矩阵到单细胞基因型–表达关联

SDRranger 输出标注 BAM、read count matrix 和 RNA UMI matrix。论文分析随后：

1. 用 sample BC purity、测序深度等过滤细胞并去除 doublet；
2. 用 sinto 将 BAM 按细胞拆分；
3. 对每个细胞运行 GATK HaplotypeCaller，获得 REF/HET/ALT genotype；
4. 合并 VCF，并按 depth、genotype quality 和低频噪声阈值过滤；
5. 将 RNA、gDNA/VAF 和 genotype assay 加入 Seurat 对象；
6. 用 MAST 比较不同 genotype 或 perturbation group 的目标基因表达；
7. 在淋巴瘤中用卡方检验比较 DZ/LZ 变异丰度，用 topGO 分析差异表达通路。

因此“联合”发生在 cell barcode 上：同一 `CB` 的 gDNA genotype 与 RNA UMI 被并到同一个细胞记录，而不是把两个独立实验的群体平均相关起来。

### 5. 四张主图建立的证据链

#### 图 1：可行性与固定条件

POP 实验测 28 个 gDNA 和 30 个 RNA targets，一次运行获得约 9,000 个高质量 iPS 细胞。23/28 个 gDNA targets 在多数细胞中高覆盖；pseudo-bulk SDR-seq 表达与 bulk RNA-seq 高度相关。物种混合实验显示 gDNA 串扰平均低于 0.16%，RNA 串扰约 0.8–1.6%，并且 sample BC 可过滤大部分环境 RNA。

图中没有证明五个未检出 target 一定是“预期 primer failure”；它们只能作为该 panel 中未成功/低效目标记录。

#### 图 2：扩展到 480 个目标

作者比较 120、240、480 总目标 panel，并共享一组 gDNA/RNA targets。为公平比较，不同 panel 按大小 subsample 到相同平均覆盖。共享目标的检测和覆盖高度相关；80% 的 gDNA targets 在超过 80% 的细胞中高置信检出。异合 SNP 在高检测 amplicon 中有 87–94% 的细胞被正确判为 heterozygous，相应 ADO 约 6–13%。

测试的 expressed/non-expressed gene 区域、不同染色质标记和 DNase signal 未显示系统性检测偏差。这个结论只覆盖论文设计的位点集合，不能外推成“任意基因组位点完全不受染色质影响”。

#### 图 3：编辑实验必须按实际基因型分组

CRISPRi 中，95% 的 TSS-targeting control 显著降低目标表达；部分 eQTL-targeting gRNA 也有表达效应，但靠近 TSS 的 gRNA 可能产生类似 CRISPRi 的直接抑制，不能当作精确变异效应。

Prime editing 的总体编辑效率有限，eQTL 难以解释；显著表达变化只见于 STOP controls，且 SOX11、ATF4、MYH10 因 STOP 位置不同表现不一。Base editing 中若干候选 eQTL genotype 与目标表达显著关联。POU5F1 amplicon 还显示多个共现变异组合可对应不同表达，说明只盯一个命名变异可能混淆真实背景。

#### 图 4：原发 B 细胞淋巴瘤中的联合分析

作者分析两例 follicular lymphoma 和一例 GCB-DLBCL，每例约 3,600–8,400 个细胞。RNA 与 gDNA 聚类都能区分 B/non-B cell，并在两个样本中看到 variant-defined clone。DZ/LZ 状态间存在差异丰度变异，BCL2 和免疫球蛋白可变区是其中一部分。

高 variant-burden 细胞具有更高的 B-cell receptor signaling 与 tumorigenic expression。该结果是同一批单细胞中的关联，作者提出其可能与更多轮 somatic hypermutation 和逃避凋亡有关；主图没有通过干预证明“变异负担导致 BCR signaling”。

### 6. 论文机制与本地代码匹配

| 环节 | 本地证据 | 判断 |
|---|---|---|
| FASTQ barcode 解析、纠错、RNA UMI 和矩阵 | `SDRranger/SDRranger/*.py` | Exact：CLI 与核心算法可直接核查 |
| 参考构建、各实验 SDRranger/GATK/Seurat/MAST 分析 | `SDR-seq/*` | Partial-to-Exact：大部分实验脚本存在，但路径和参数分散在多份 Rmd/shell 中 |
| Tapestri 液滴与湿实验步骤 | 论文与 protocols.io | Not executable locally：需要专有设备、试剂和 primer panel |
| 一键端到端复现 | 本地无统一 workflow/environment lock | Not found：需手动连接两个仓库及外部 STAR、GATK、sinto 等工具 |

代码审计还发现论文/配置对一个 constant linker 长度的描述不一致（论文 15 bp，示例 JSON 中相应序列为 23 bp）。在没有原始 run-specific config 进一步核对前，应将它保留为版本/配置差异，而不是自行选择一个值改写实验设计。

### 7. 适用范围与边界

1. SDR-seq 是候选驱动的 targeted assay；480 是 gDNA + RNA targets 总数，不是 480 个全长基因组和 480 个基因各自同时测量。
2. 低 ADO 依赖 target 被有效扩增；低覆盖 amplicon 仍是主要 dropout 来源。
3. 编辑效率低时，即使测到实际 genotype，各 genotype group 的细胞数仍可能不足以解释细微效应。
4. 差异表达与变异共现支持关联，因果解释仍取决于编辑设计、共现变异和独立验证。
5. Tapestri 是专有平台；计算代码公开不等于完整实验可无障碍复现。

### 证据入口

- 论文：`paper source/PMC12510883/paper.md`
- 主图：`paper source/PMC12510883/images/41592_2025_2805_Fig1_HTML.jpg` 至 `Fig4_HTML.jpg`
- SDRranger：`SDRranger/SDRranger/`
- 实验分析：`SDR-seq/01_POP/` 至 `SDR-seq/07_Species_Mix/`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SDR-seq: Functional Phenotyping of Genomic Variants Using Joint Multiomic Single-Cell DNA–RNA Sequencing

**Lindenhofer, Bauman, Hawkins, Fitzgerald et al.** | *Nature Methods* 22(10) (2025)
DOI: [10.1038/s41592-025-02805-0](https://doi.org/10.1038/s41592-025-02805-0)
Code: [SDRranger](https://github.com/hawkjo/SDRranger) (pipeline) | [SDR-seq](https://github.com/DLindenhofer/SDR-seq) (analysis)
Data: [GSE268646](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE268646) | [EGAS50000000374](https://ega-archive.org/studies/EGAS50000000374)

### Motivation & Novelty

Understanding how genetic variants — particularly the >90% located in noncoding regions — impact gene expression requires simultaneously profiling genotype and transcriptome in single cells. Existing methods face a fundamental trade-off between throughput and sensitivity:

**Limitations of prior approaches:**
- **High-throughput droplet/split-pool methods** (HIPSD&R-seq, *Genome Biology* 2024; scalable co-sequencing, *Nature Methods* 2025; linear amplification, *Molecular Cell* 2019) rely on tagmentation of nucleosome-depleted chromatin, achieving thousands of cells but with allelic dropout (ADO) >96% — making zygosity determination unreliable
- **Plate-based methods** (G&T-seq, *Nature Methods* 2015; PTA-seq, *Nature* 2024; scONE-seq, *Science Advances* 2023; SIDR, *Genome Research* 2018) achieve high per-cell sensitivity but process only hundreds of cells
- **Reporter assays** (STARR-seq, *Science* 2013; MPRA, *Cell* 2016; Perturb-seq, *Nature Biotechnology* 2022) screen thousands of variants but lack endogenous genomic context

**SDR-seq's unique contributions:**
1. **Targeted + droplet-based**: Combines thousands-of-cells droplet throughput with targeted amplification (ADO ~6-13% in well-detected amplicons). The paper's ~100× comparison refers to cell throughput versus PTA-based joint methods, not a 100× ADO improvement.
2. **Joint gDNA + RNA**: Reads both modalities from the same cell with separate, optimized library preparation via distinct primer overhangs (R2N for gDNA, R2 for RNA)
3. **Noncoding variant coverage**: Directly amplifies any genomic locus (independent of transcription), enabling study of the vast majority of disease-associated variants
4. **Scalable panels**: Demonstrated up to 480 simultaneous targets (240 gDNA + 240 RNA) with consistent performance

### Method Overview

SDR-seq is a droplet-based single-cell DNA–RNA sequencing method built on Mission Bio's Tapestri platform. Fixed and permeabilized cells undergo in situ reverse transcription, tagging RNA with cell-specific barcodes (cell BC + sample BC + UMI). Cells are then encapsulated in droplets where multiplexed PCR amplifies both gDNA and cDNA targets. After emulsion breaking, distinct overhangs on primers enable separate library generation for each modality.

The computational pipeline has two components:
- **SDRranger** (Python): Processes raw FASTQ files — barcode identification via gapped pairwise alignment (handles variable-length linkers), error correction (Levenshtein for cell BCs, free divergence for sample BCs), UMI deduplication via directional network method, and count matrix generation
- **SDR-seq analysis** (R/Seurat): Per-cell variant calling (GATK HaplotypeCaller), genotype-expression association (MAST for differential expression, χ² for variant enrichment), and downstream biological analysis

See `doc_method.md` for detailed algorithm descriptions and `doc_code.md` for code-paper mapping.

### Evaluation

#### Datasets & Experiments

| Experiment | Targets | Cells | Key Question |
|---|---|---|---|
| POP (proof-of-principle) | 28 gDNA + 30 RNA | ~9,000 | Method validation, PFA vs glyoxal |
| Species mixing | Human + mouse | ~16,000 | Cross-contamination assessment |
| Panel scaling | 120/240/480 targets | ~17,000 | Scalability testing |
| CRISPRi screen | gDNA + RNA + CROP-seq | ~5,000 | Detect strong expression changes |
| Prime editing | pegRNA library | ~5,000 | Install eQTL variants, detect subtle effects |
| Base editing | 56 eQTLs (ABE8e/CBE) | ~5,000 | Noncoding variant functional testing |
| B cell lymphoma | Targeted panels | ~20,000 (3 patients) | Variant–expression linking in primary tumor |

#### Key Results

- **Sensitivity**: 80% of gDNA targets detected in >80% of cells across all panel sizes; heterozygous variants correctly called in 87-94% of cells
- **Specificity**: Cross-contamination <0.16% (gDNA) and 0.8-1.6% (RNA) in species-mixing experiment
- **Scalability**: Performance consistent from 120 to 480 targets; shared target correlation >0.95 between panels
- **CRISPRi validation**: 95% of TSS-targeting gRNAs caused significant reduction in target gene expression
- **Base editing**: Multiple eQTL variants with significant effects on target gene expression identified; POU5F1 3'UTR variant combinations showed differential expression effects
- **Lymphoma biology**: Higher mutational burden associated with elevated B cell receptor signaling and tumorigenic gene expression in primary samples; BCL2 variants enriched in light zone vs dark zone maturation states

#### Compared Methods (with citations)

| Method | Type | Throughput | ADO Rate |
|---|---|---|---|
| **SDR-seq** | Targeted droplet | ~10K cells | ~6-13% |
| G&T-seq (*Nature Methods*, 2015) | Plate-based WGS | ~100s cells | Varies |
| PTA-seq (*Nature*, 2024) | Plate-based WGS | ~100s cells | <10% |
| HIPSD&R-seq (*Genome Biology*, 2024) | Split-pool tagmentation | ~1000s cells | >96% |
| Scalable co-seq (*Nature Methods*, 2025) | Split-pool tagmentation | ~1000s cells | >96% |
| Tapestri (Mission Bio) | Targeted droplet (DNA only) | ~10K cells | <10% |

### Reproducibility

**Rating: 4/5** — High-quality code with comprehensive analysis notebooks, but some external dependencies and manual steps limit full automation.

#### Strengths
- **Two well-organized code repositories** with experiment-specific notebooks covering the full analysis
- **SDRranger**: Clean Python package with CLI, checkpoint-based processing, and example data + configs
- **Complete statistical analysis**: R notebooks implement all claimed statistical tests (MAST, χ², topGO)
- **Raw data deposited**: GEO (GSE268646) for non-human samples; EGA (EGAS50000000374) for primary patient data (controlled access)
- **Detailed protocol**: Published on protocols.io (10.17504/protocols.io.6qpvr9q43vmk/v1)

#### Weaknesses
- **Hardware dependency**: Requires Mission Bio Tapestri platform (proprietary microfluidic device)
- **Manual steps**: GATK variant calling setup requires manual VCF header adjustment; VEP annotation appears to use web interface
- **No unified pipeline**: The analysis requires sequential execution of multiple R notebooks with manual intermediate file management
- **Custom pysam/pywfa forks**: SDRranger depends on custom forks of pysam and pywfa, which may complicate installation
- **Primary patient data**: B cell lymphoma data under controlled access (EGA), limiting independent validation

#### Practical Notes
- SDRranger installation: `pip install .` from the repository; requires STAR aligner installed separately
- R environment: Seurat v5.0.3, MAST, topGO v2.54.0, TAPseq; R ≥ 4.0 recommended
- GATK batch processing limited to ≤1,000 cells per batch to avoid samtools memory issues
- For new experiments: primer design uses TAPseq + Primer3 + BLAST pipeline (R notebooks in 01_TAP_primer_pred/)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
