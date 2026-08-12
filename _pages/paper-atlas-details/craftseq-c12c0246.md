---
layout: default
permalink: /paper-atlas/craftseq-c12c0246/
title: "CRAFTseq"
nav: false
description: "CRISPR base editing 后，同一培养孔里通常只有一部分细胞获得目标编辑，其余细胞可能未编辑、杂合编辑、双等位编辑或带旁观者/indel。若以“加入了 guide”代替真实 genotype，会把这些细胞混在一起；同时 edited cells 分泌的 cytokine 和共同培养应激会影响未编辑邻居，使 condition-level comparison 把共享环境效应错当成 variant effect。"
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
      <span>Nature · 2025</span>
    </div>
    <h1>CRAFTseq</h1>
    <p>Precisely defining disease variant effects in CRISPR-edited single cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09313-3" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CRAFTseq：在同一个单细胞中直接连接基因型、RNA 和表面蛋白

### 为什么需要直接单细胞基因分型

CRISPR base editing 后，同一培养孔里通常只有一部分细胞获得目标编辑，其余细胞可能未编辑、杂合编辑、双等位编辑或带旁观者/indel。若以“加入了 guide”代替真实 genotype，会把这些细胞混在一起；同时 edited cells 分泌的 cytokine 和共同培养应激会影响未编辑邻居，使 condition-level comparison 把共享环境效应错当成 variant effect。

CRAFTseq 的核心原则是：在每个细胞内直接测 targeted genomic DNA allele，同时测 whole-transcriptome RNA、antibody-derived tags（ADT）和 index-flow metadata。统计模型以实际 allele dosage 解释表达，而不是以 guide 或处理条件作代理。这使 subtle non-coding eQTL、cell-state-specific effects 和 multiplexed editing interactions 有机会被识别。

### 1. 四种信息如何进入同一 384-well cell

细胞经 flow cytometry 单细胞分选到 384-well plate。荧光抗体/index sorting 记录 cell state、condition 和 donor；TotalSeq-A oligo antibodies 提供表面蛋白；barcoded oligo-dT 捕获 RNA 与 ADT oligo；locus-specific primers 扩增 genomic target。一个 combined RT+PCR 后产物分为 gDNA、cDNA 和 ADT 三条 library stream，各自加入 Illumina adapters，但共享 well barcode。

CRAFTseq 常被称为 quad-modal：targeted DNA、RNA、ADT、flow metadata。它不是全基因组 DNA+RNA multiome；DNA 只覆盖事先选择的 amplicon，因此需要为每个 locus 验证 nested PCR efficiency。plate-based 格式提高每细胞成本和操作量，却能直接连接 allele 与 phenotype，并避免 viral guide capture。

### 2. 三类 sequencing 数据分别处理

RNA 用 STARsolo 对 GRCh38 2020-A；ADT 用 kallisto|bustools/kite 对 antibody featuremap；DNA R2 按 well barcode 拆成 per-cell FASTQ，再用 CRISPResso2 对指定 amplicon calling。

本地 `DNAStep1_Demultiplex.sh:1-27` 明确取 R1 sequence 前 10 nt 作 cell barcode，将 paired reads 写入每 well FASTQ。`DNAStep2_CRISPRessoR2.sh:1-27` 为每 plate 构建 CRISPRessoBatch，并只处理 R2。脚本中 sample、amplicon 和路径均硬编码为 CD45 示例，不能直接视为通用 CLI。

CRISPResso 的 per-cell allele tables 再由 `DNAStep3_AlleleTable.R:11-40` 合并；每 cell 最多先读 top 10 alleles，保留 sequence、reads、percent 和 edit classification。代码依赖未显式加载的 data.table/tidyr/dplyr functions，运行环境需通过上游 source 或手工补全。

### 3. 如何从 reads 判定 genotype

低 DNA coverage 容易把 sequencing error 当 allele。CRAFTseq 对 rank-ordered reads/cell 曲线做 spline curvature/knee detection，获得实验特异 minimum read cutoff，常为 20–40 reads。再按 12–25% allele-frequency threshold 去除低频噪声，仅保留 top two alleles，依据二倍体假设编码 edited dosage 0/1/2。

top-two 规则适合二倍体、单 locus，但在 aneuploid cell line、copy-number altered locus 或复杂 mosaic indels 中可能错误。threshold 也随实验改变，不能从一个 CD45/PAX5 run 机械复制到其他位点。可靠做法是联合查看 knee plot、WT controls、known genotype mixtures 和 allele balance。

对于 HLA-DQB1 Cas9/HDR 实验，不同细胞可能有不同 deletion size；模型使用连续的 $\log_2(DeletionSize+1)$，而非简单 edited binary。对于 base editing，则每个目标 nucleotide 独立生成 dosage。

### 4. Genotype-specific NB model

对 gene/ADT count $X_i$，CRAFTseq 用 negative-binomial GLM 控制 overdispersion。cell-line null model 包含 library size 和 plate，full model加入 genotype dosage：

$$
\log E[X_i]=\beta_0+\beta_L\log(nCounts_i)+\beta_P Plate_i+\beta_G Genotype_i.
$$

比较 full/null likelihood ratio 产生 genotype $P$ value。primary cells 再加入 donor fixed effect，IL2RA 多 donor/plate 分析使用 random intercept。dosage 0/1/2 隐含 additive allele effect；dominant、recessive 或 allele-specific nonlinear effect 需要另外建模。

代码与论文有一处记号差异：论文写 $\log_{10}(nCounts)$，R 脚本使用自然 `log()`/或直接 nCount covariate（`PAX5_RNA_glmNB.R:158-159`）。由于 log bases 只改变 coefficient scale，在纯线性 covariate 下通常不改变拟合空间，但直接使用 raw nCount 则不是同一变换，应按具体脚本解释。

“genotype vs condition”比较是本文最关键控制。condition model 会抓到同孔所有细胞共享的 activation/cytokine effects；genotype model 只寻找随实际 allele dosage 改变的 cell-intrinsic association。因此 FBXO11 中 genotype model 得到 265 genes，而 condition model 的 168 genes 含更多 bystander signals。

### 5. 多重编辑的 joint model

PAX5 实验同时编辑 8 个 nucleotide。若逐位点独立分析，相互相关的 editing outcomes 会互相混淆。作者把 8 个 dosage 同时放进 NB model：

$$
\log E[X_i]=\text{covariates}+\sum_{v=1}^{8}\beta_vG_{iv}.
$$

这样每个 $\beta_v$ 是控制其他 7 个位点后的条件效应。为控制 8×genes tests，使用 Bonferroni。B.29（p.I135T）改变 113 genes，成为主要 functional variant。

为检验 A-region editing 是否增强 B.29，作者先按 B.29 effect sizes 加权显著 genes 的 raw counts，生成 gene score：

$$S_i=\sum_g\hat\beta_g E_{ig}.$$

再比较含/不含 $Aedited\times B.29$ 的线性模型。聚合 score 提高 power，但用同一数据选 genes、估 weights 和测试 interaction 可能产生选择偏倚；严格独立验证应在 held-out cells/experiment 重估。

### 6. 关键应用如何验证平台

- HLA-DQB1：deletion size 只预测 DQB1 expression，而不是广泛 genes/proteins，说明 direct genotype 可解析局部效应。
- FBXO11：展示 genotype model 与 culture condition/bystander effect 的差异。
- PTPRC/CD45：在 primary naive CD4 T cells 中，CD45 loss 与 CD4 upregulation 相关；donor covariate 防止个体混杂。
- RPL8：rs2954658 T allele 产生约 0.9-fold expression change，bulk RNA 未显著，说明低 editing fraction 会稀释 subtle eQTL。
- IL2RA：rs61839660 影响只在 proliferating Treg、非 TH1 中明显，说明同一 allele effect 依赖 cell state。
- PAX5：8-site multiplex model 分离单点和 region interaction。

这些是编辑实验中的 genotype–phenotype association。base editor 可能产生 bystander edits；joint genotype table能部分控制，但目标位点 dosage 不一定代表唯一 sequence change。

### 7. 与 Mixscape 等代理方法的区别

Mixscape 从 transcriptomic perturbation signature 推断哪些 guide-positive cells 真正受扰动。对于 knockout 大效应很有用，但 subtle regulatory variants 可能没有足够强 signature，且以 phenotype 反推 genotype 会形成 circularity。论文在 FBXO11/PTPRC 中显示 Mixscape status 与直接 DNA genotype 不一致，DEG Z-scores 也较差。

CRAFTseq 不需要从 RNA 猜 genotype，这是它的主要优势；代价是 targeted PCR、plate throughput 和 locus-specific primer optimization。二者适用场景不同，不能由本文比较推出所有 Perturb-seq 都不可靠。

### 8. 主图证据链

- Fig. 1：四模态 plate workflow、DNA/RNA/ADT quality 和 cell-line mixture validation。
- Fig. 2：HLA-DQB1 与 FBXO11，展示 genotype-specific analysis 去除 bystander effects。
- Fig. 3：primary CD4 T-cell PTPRC knockout 与 direct protein/RNA consequences。
- Fig. 4：RPL8 fine-mapped eQTL，说明 bulk/condition analysis 对 subtle effects 的稀释。
- Fig. 5：IL2RA variant 的 Treg-state specificity。
- Fig. 6：PAX5 8-site multiplexed editing、B.29 主效应和 A×B interaction。

`figure_analysis.md` 对主图和 extended figures 已有逐面板证据；当前 PMC conversion 未设置单独 IMAGE_DIR，因此最终视觉定量需回到 paper PDF/figure captions。

### 9. 代码覆盖与复现边界

本地 repo 覆盖 STARsolo、kallisto-kite、DNA demultiplex、CRISPResso、allele consolidation、DNA filtering、各实验 NB models、PAX5 interaction 和 bulk comparisons，论文—代码匹配较高。没有 dependency manifest/renv，Phoenix R package 来源不清，notebooks 依赖相对/外部数据，raw sequencing 受 dbGaP 控制。

脚本常硬编码 plate/locus/path；`DNAStep1` 用 shell `ls`/awk 并为每 barcode 打开输出文件，扩展到更多 plates 时需注意文件描述符和 quoting。分析阈值按实验调整是方法合同的一部分，不应抽象成唯一 universal cutoff。

最强结论是：直接单细胞 genotype 能把真实 allele effect 与共同培养、编辑失败和 cell-state heterogeneity 分开，尤其适合 subtle regulatory variants。它不是高通量全基因组 screen，而是 targeted、深度 phenotype、每 locus 需工程化的验证平台。

### 源证据入口

- 论文：`paper source/PMC12488502/paper.md`
- 代码：`craft-seq/`
- DNA 预处理：`craft-seq/preprocessing/`
- 统计模型：`craft-seq/figures/`
- 论文—代码映射：`doc_code.md`
- 分图解读：`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CRAFTseq: Summary

### Motivation & Novelty

#### The Biological Problem

Large-scale GWAS has catalogued thousands of non-coding disease variants, but most have no proven causal function. Pinning function to a specific SNP requires introducing it into the right cell type and measuring the downstream effect. CRISPR base editing now enables base-pair-resolution edits in primary cells, but two compounding obstacles prevent clean functional readout:

1. **Heterogeneous editing**: Even with the best base editors, 3–58% of cells acquire the intended edit (Arbab et al., *Cell* 2020). Methods that treat all "CRISPR-exposed" cells as edited conflate edited and non-edited cells.
2. **Non-specific culture effects**: Secreted cytokines and activation signals from edited cells affect neighboring non-edited cells in the same well. Condition-level comparisons (CRISPR pool vs control pool) therefore pick up dozens of non-specific changes that obscure the true variant effect.

#### Limitations of Existing Methods

- **Pooled CRISPR screens (e.g., Perturb-seq)** (*Science* 2023, Morris et al.): Use sgRNA as proxy for editing; 50% of guides may be inactive; require viral transduction which confounds primary cell work.
- **BEAN** (*Nature Genetics* 2024, Ryu et al.): Designed for large effects from coding variants; assumes a bimodal distribution of edited/non-edited cells that may not hold for subtle non-coding effects.
- **Mixscape** (*Nature Genetics* 2021, Papalexi et al.): Uses transcriptomic signatures to infer editing status; fails when edit effects are small (as shown by CRAFTseq's direct comparison, Extended Data Fig. 8).
- **G&T-seq** (*Nature Methods* 2015, Macaulay et al.) and **GoT** (*Nature* 2019, Nam et al.): Capture DNA + RNA but require low-throughput physical separation or are limited to coding regions via transcriptome capture.

#### What's New

CRAFTseq is the **first method to simultaneously capture targeted genomic DNA amplicons, whole-transcriptome RNA, and cell-surface protein (ADT) in a single plate-based workflow**. Key advances:
- Direct genotyping in every cell — no proxy, no inference
- Genotype-specific analysis eliminates bystander culture effects as a confound
- Plate-based, ~$3/cell, ~thousands of cells/week, no specialized equipment
- Detects cell-state-specific effects (IL2RA only in proliferating Treg cells)
- Scales to multiplexed editing of 8 nucleotides simultaneously (PAX5)

---

### Method Overview

#### Experimental Platform

CRAFTseq is a **quad-modal single-cell assay**:

| Modality | What's captured | How |
|----------|----------------|-----|
| Genomic DNA | CRISPR editing outcome at specific locus | Nested PCR amplicon, R2 sequencing |
| RNA | Whole transcriptome (3' mRNA) | Modified FLASH-seq protocol |
| ADT | 154 cell-surface proteins | TotalSeq-A antibody panel, barcoded oligo-dT |
| Flow cytometry | Cell hashing (condition, individual) | Indexing flow cytometry |

Cells are sorted into 384-well plates pre-loaded with barcoded lysis buffer. A combined RT+PCR reaction co-amplifies all four modalities before splitting into separate library preparation streams. All libraries carry well-specific barcodes enabling single-cell resolution.

#### Statistical Framework

The core innovation is **genotype-specific analysis**: rather than comparing CRISPR vs control conditions (which mixes edited and non-edited cells), CRAFTseq models expression as a function of actual allele dosage (0/1/2) at the edited nucleotide. This uses negative binomial GLMs with:
- Library size (log-normalized) as offset covariate
- Plate as batch covariate (or Harmony batch-corrected PCs for visualization)
- Individual as covariate (fixed) or random effect (mixed model) for primary cell experiments
- LRT for significance testing (null vs full model)
- BH-FDR or Bonferroni multiple testing correction

For multiplexed editing (PAX5), all 8 variant dosages enter a single joint model, and interaction effects between edited regions are tested via a gene-score aggregation strategy.

#### Biological Applications Demonstrated

| Experiment | Cell type | Editing type | Key finding |
|-----------|-----------|-------------|-------------|
| PTEN validation | Jurkat/Daudi/HEK293T mix | None (endogenous) | Correct cell-type identification |
| HLA-DQB1 | HH + Daudi | CRISPR–Cas9 HDR | Deletion size specifically affects only HLA-DQB1 |
| FBXO11 | Jurkat + Daudi | ABE8e base editing | 265 genotype-specific genes; condition analysis picks up bystander effects |
| PTPRC | Primary naive CD4+ T cells | BE4 base editing | CD4 upregulation on CD45 loss (new finding) |
| RPL8 eQTL | Daudi | ABE8e | rs2954658 T allele → 0.9-fold RPL8 change (P<10^-9) |
| IL2RA variant | Primary CD4+ T cells (TH1/Treg) | BE4-NG | rs61839660 effect is Treg-specific, not TH1 |
| PAX5 | Daudi | ABE8e multiplexed | B.29 (p.I135T) affects 113 genes; A+B region synergy |

---

### Evaluation

#### Datasets

| Experiment | Cells (passing QC) | Plates | Individuals |
|-----------|-------------------|--------|-------------|
| Cell-line mix (PTEN) | 606 | 2 | — |
| HLA-DQB1 | 646 | — | — |
| FBXO11 | 1,220 (Daudi) + 1,531 (Jurkat) | — | — |
| PTPRC | 618 | 3 | 3 |
| RPL8 | 969 | — | — |
| IL2RA | 1,994 | — | 5 |
| PAX5 RNA | 1,926 | 12 | — |
| PAX5 ADT | 1,004 | 6 | — |

#### Key Results

**Technical validation**:
- Mean 5,089 genes / 57,540 UMIs per cell (similar to 10x Genomics)
- 869 median DNA reads/cell; 605/768 cells genotyped
- DNA miscall rate: 1.44% in Daudi cells (no miscalls in HEK293T)

**Genotype-phenotype results**:
- HLA-DQB1: Deletion size uniquely predicts DQB1 expression (P<10^-8); 0 other genes or proteins (FDR>0.05)
- FBXO11: Genotype analysis recovers 265 genes vs condition analysis 168 (genotype better powered despite smaller N)
- PTPRC: First demonstration of CD4 upregulation upon CD45 loss in naive CD4+ T cells (P<10^-16, β=0.28)
- RPL8: Fine-mapped eQTL variant confirmed (P<10^-9); bulk RNA-seq of same experiment shows no significant effect — single-cell genotyping is essential
- IL2RA: rs61839660 effect exclusively in proliferating Treg cells, resolves contradictory literature
- PAX5 B.29 (p.I135T): 113 genes significant; A region editing amplifies B.29 gene score (interaction P=1.72×10^-4)

**Mixscape comparison**: Mixscape misclassified edited cells in both FBXO11 and PTPRC experiments; concordance of DEG Z-scores between CRAFTseq genotype model and Mixscape-predicted status was poor.

**Bulk vs single-cell**: Same cells analyzed by bulk RNA-seq showed no significant RPL8 change and non-specific PTPRC KO effects — demonstrating single-cell genotyping is necessary.

---

### Reproducibility

**Rating: 3/5**

**Justification**: The protocol itself is detailed and deposited on protocols.io (https://www.protocols.io/view/craftseq-d7bk9ikw), and all analysis scripts are on GitHub. However:

**Strengths**:
- Protocol fully described with exact reagent concentrations, instrument settings, and PCR programs
- Analysis code covers all experiments; preprocessing scripts handle full pipeline
- Count matrices deposited on Zenodo (10.5281/zenodo.15935857)
- PMCID PMC12488502 — open access

**Limitations**:
- Raw sequencing data requires dbGAP access (phs004042.v1.p1) — not immediately available
- No dependency manifest (requirements.txt, conda environment, or renv lockfile)
- Experiment-specific thresholds (DNA read cutoffs, allele frequency thresholds) vary per run; not all documented in main text
- `Phoenix` R package used in PAX5 analysis is not a CRAN package — unclear origin/installation

**Common pitfalls**:
- DNA read cutoff is automated but sensitive to experiment; validate with knee-plot visualization
- Competition between flow-cytometry and oligo-conjugated antibodies (CD45 example documented in Supplementary Fig. 1)
- Nested PCR efficiency varies by locus; test primers before scaling
- The ADT data for PAX5 covers only 6 of 12 plates — not stated in main text

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
