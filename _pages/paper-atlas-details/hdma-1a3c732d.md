---
layout: default
permalink: /paper-atlas/hdma-1a3c732d/
title: "HDMA"
nav: false
description: "HDMA（Human Development Multiomic Atlas）先用 SHARE-seq 在同一个细胞核中同时测量 RNA 与开放染色质，再为每一种细胞类型训练一个“DNA 序列 → ATAC 可及性”的 ChromBPNet 模型。研究者随后把模型当作可计算的实验系统：寻找真正影响预测的序列基序，把两个基序按不同距离和方向插回背景序列，并比较联合效应与独立效应，从而区分需要精确间距的“硬语法”和允许较宽松间距的“软语法”。"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Nature · 2026</span>
    </div>
    <h1>HDMA</h1>
    <p>Multiomics and deep learning dissect regulatory syntax in human development</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10326-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## HDMA：用多组学与深度学习拆解人类发育中的调控语法

### 一句话理解

HDMA（Human Development Multiomic Atlas）先用 SHARE-seq 在同一个细胞核中同时测量 RNA 与开放染色质，再为每一种细胞类型训练一个“DNA 序列 → ATAC 可及性”的 ChromBPNet 模型。研究者随后把模型当作可计算的实验系统：寻找真正影响预测的序列基序，把两个基序按不同距离和方向插回背景序列，并比较联合效应与独立效应，从而区分需要精确间距的“硬语法”和允许较宽松间距的“软语法”。

### 论文要解决什么问题

同一套基因组如何在发育过程中产生大量不同细胞类型，关键取决于转录因子（TF）何时、何地结合顺式调控元件。传统 motif enrichment 能回答“哪些短序列富集”，却难以回答三个更强的问题：某段序列是否真的推动染色质开放；两个 TF 位点是否产生超出独立作用之和的协同；这种协同是否依赖特定方向和碱基级间距。

论文建立了跨 12 个胎儿器官的配对 RNA–ATAC 图谱，并把细胞类型特异的开放染色质交给深度模型学习。数据包含 817,740 个细胞、203 个细胞簇和 1,032,273 个候选顺式调控元件（caCRE）；这些量级和图谱构建见论文正文第 52–71 行。HDMA 的核心贡献不是只提供一个 atlas，而是把 atlas、可解释序列模型、motif 实例识别和计算扰动连成一条证据链。

### 输入、输出与三层结果

输入包括：

- SHARE-seq 的 RNA 计数与 ATAC fragments；
- 每个细胞类型的 ATAC peaks、GC 匹配的非 peak 背景区和参考基因组序列；
- GTEx eQTL、CAUSALdb 精细定位变异、ENCODE/VISTA 等外部验证资源。

输出分三层：

1. **图谱层**：203 个细胞类型、全局 caCRE 集合以及 caCRE–gene 链接；
2. **序列规则层**：189 个通过质控的细胞类型、每类 5 折模型，共 945 个 ChromBPNet 模型，以及 508 个去冗余 motif；
3. **机制与疾病层**：基序实例、67 个协同复合 motif、硬/软语法类别、负贡献 motif，以及发育期特异的疾病变异解释。

### 从原始数据到调控语法

```text
SHARE-seq（同一细胞核的 RNA + ATAC）
  ├─ RNA：去环境 RNA、归一化、降维、聚类、细胞注释
  └─ ATAC：fragment 质控、peak calling、chromVAR
          ↓
203 个细胞类型 + 1,032,273 个 caCRE
          ↓
每个细胞类型：peaks + GC 匹配背景 + 2,114 bp DNA
          ↓
ChromBPNet（5 折）→ 1,000 bp profile + log counts
          ↓
DeepLIFT 逐碱基贡献 → TF-MoDISco motif → Fi-NeMo 实例
          ↓
两个 motif × 距离 × 方向的 in silico marginalization
          ↓
联合效应 vs 独立效应 → synergy → hard / soft syntax
          ↓
eQTL、GWAS 和等位基因效应解释
```

#### 1. 配对多组学图谱

SHARE-seq 让 RNA 和 ATAC 来自同一细胞，因此无需跨细胞“猜配对”。RNA 侧使用 SCTransform v2、DecontX 和迭代聚类；ATAC 侧使用 ArchR、MACS2 与 chromVAR。论文没有进行全局 batch correction，因为供体、孕周和器官组成相互混杂；这里应理解为一个明确的设计取舍，而不是遗漏。方法细节位于论文第 434–463 行。

全局 peak 合并得到 caCRE 后，修改版 ABC 模型以 ATAC 信号近似 enhancer activity，并用距离幂律近似 contact，将 caCRE 连接到候选靶基因。因为没有使用该胎儿图谱自身的 Hi-C，这部分是可解释的近似链接，而不是实测三维接触；论文第 464–472 行给出阈值和实现范围。

#### 2. ChromBPNet 学习“序列如何产生可及性”

每个训练样本取 2,114 bp DNA 上下文，模型输出中央 1,000 bp 的碱基分辨率 ATAC profile 和一个总 read count。论文为每种细胞类型训练五折模型，并以染色体划分训练、验证和测试集合；189 个细胞类型通过质控，测试 peak 上预测与观察 log counts 的中位 Pearson 相关为 0.78（论文第 103–109、474–489 行）。

ChromBPNet 把 Tn5 序列偏好与生物学可及性分离。仓库训练脚本复用一个在 `Heart_c0/fold_0` 上训练的 bias model；真正用于下游解释的是 bias-corrected 的 `chrombpnet_nobias.h5`。本地 wrapper 对 profile logits 做 softmax，再乘以 $\exp(\text{log counts})$，得到可解释的逐碱基预测 reads（`HDMA_code/code/03-chrombpnet/tangermeme_utils/wrappers.py:7-46`）。

#### 3. 从贡献分数得到 motif lexicon

DeepLIFT 为每个碱基计算其对 counts 输出的贡献；TF-MoDISco 把局部高贡献片段聚成 motif。作者先在细胞类型和器官内聚类，再跨器官去冗余并人工质控，最终得到 508 个 motif，其中 493 个为正贡献、15 个为负贡献。这里的“正/负”描述的是模型预测方向，不等同于直接证明某 TF 在体内激活或抑制转录（论文第 103–113、490–503 行）。

Fi-NeMo 用 motif 的 contribution weight matrix 在每个 peak 的贡献轨迹中寻找预测性实例。代码运行两遍：一次包含 composite motifs，一次排除 composite motifs，再协调结果；这样避免稀疏回归让复合模式遮蔽 constituent motif。论文报告每个细胞类型平均约 839,544 个实例，通常每个 peak 有 2–8 个（论文第 113 行及第 504–507 行）。

#### 4. 把模型变成“虚拟扰动实验”

对 motif A、B 和二者联合插入后的预测，以背景预测 $y_0$ 为参照：

$$
\Delta_A=y_A-y_0,\qquad \Delta_B=y_B-y_0,\qquad \Delta_J=y_{AB}-y_0.
$$

独立模型在 log-count 空间相加：

$$
\Delta_S=\Delta_A+\Delta_B.
$$

若 $\Delta_J$ 系统性大于 $\Delta_S$，说明两个 motif 的联合效应超过独立预期。代码确实在 log-count 输出上计算 `y_after - y_before`，并用单侧 Wilcoxon signed-rank test 比较联合效应和独立效应（`04b-in_silico_test_cooperativity.py:131-162,563-584,714-736`）。这比只看 motif 共现更强，因为它直接改变输入序列后观察同一个模型的反事实预测；但它仍然是模型内的计算扰动，不是湿实验中的因果验证。

#### 5. 硬语法与软语法

作者对 138 个 composite motifs 扫描不同方向和 0–200 bp 间距，并用 100 条背景序列和五折模型减少背景与单模型偶然性。最终 67 个 motif 对显示协同，其中 48 个具有硬语法、27 个具有软语法，二者有 8 个重叠（论文第 142–159、522–536 行）。

- **硬语法**：联合效应只在少数特定方向/间距出现尖峰；代码以不同 arrangement 的效应 z-score 表征集中程度，核心计算为 $z=(x-\bar{x})/\sigma$（`syntax_helpers.py:52-64`）。约 7 bp 和 11 bp 的偏好与相邻/螺旋转角位置相符。
- **软语法**：在较宽距离范围内仍超过独立预期，效应随距离逐渐衰减；这更符合 motif 通过核小体竞争产生的间接协同。

间距在代码中最终转换为 motif 中心到中心距离，而不是边缘到边缘距离（`04b-in_silico_test_cooperativity.py:734-736`），这是解释 7 bp、11 bp 峰值时容易忽略的实现细节。

### 负贡献 motif 与疾病变异

15 个负贡献 motifs 的实例更靠近推断的核小体 dyad，并远离 peak summit。作者删除这些实例进行 in silico ablation 时，模型预测可及性略升；相反，删除正 motif 会使预测下降。该结果支持“某些常见 motif 与降低可及性相关”，但作者也明确讨论了多种可能机制，不能仅凭模型把它们统一解释为直接抑制因子（论文第 160–203、532–545 行；Fig. 5 的轨迹、热图和位置分布提供视觉证据）。

疾病分析先用 g-chromVAR 找到 GWAS 精细定位变异富集的胎儿细胞类型，再筛选高 PIP 变异是否落在 motif 实例中，并用 ChromBPNet 比较参考/替代等位基因的预测可及性。Fig. 6 的矩阵显示不同疾病–细胞类型组合，下面的 locus tracks 展示胎儿开放、成人关闭的实例。论文得到 28 个 fetal-only 和 80 个 fetal-and-adult 候选变异；这些是优先级排序和机制假说，不是全部经过实验验证的致病机制（论文第 204–248、556–565 行）。

### 如何读六张主图

- **Fig. 1**：样本、器官和细胞图谱；重点是 RNA/ATAC 同细胞配对与 203 个注释簇。
- **Fig. 2**：caCRE–gene 链接与 VISTA 切片；把计算链接连接到组织特异 enhancer 活性。
- **Fig. 3**：整条序列学习流程和 508-motif lexicon；模型性能散点说明哪些细胞类型进入后续分析。
- **Fig. 4**：最关键的方法图；从不同方向/间距插入，到 joint-versus-independent 效应，再到 hard/soft 分类。
- **Fig. 5**：负 motif 的预测、核小体位置和 eQTL 方向性证据。
- **Fig. 6**：疾病富集矩阵和 fetal-only locus 案例，把 atlas 的发育窗口用于变异解释。

这些判断来自对 `paper.pdf` 主图页的直接检查；`figure_analysis.md` 给出逐 panel 的详细说明。

### 论文与本地代码能对应到什么程度

总体匹配度为 **高，但不是完全自包含**。本地仓库覆盖细胞处理、ChromBPNet 输入准备与训练、motif compendium、synergy、ABC/VISTA、eQTL、g-chromVAR 和变异评分的分析脚本。核心 synergy 方程可以逐行映射到 Python 实现。

仍需保留的边界：原始 SHARE-seq demultiplexing、ChromBPNet、ABC、NucleoATAC 等部分核心能力来自外部仓库或包；若没有 Zenodo 上的大型数据、945 个模型和 Stanford Sherlock 的调度环境，不能从这个代码快照一键重现全文。若要复现，建议先从仓库的 adrenal demo 或一个细胞类型开始，而不是直接重训全部模型。

### 最值得带走的三个认识

1. HDMA 的关键桥梁是“同细胞多组学图谱 → 细胞类型特异序列模型”，不是孤立的 atlas 或单个 CNN。
2. synergy 的判断依赖联合效应与 log-additive 独立模型的比较；motif 共现本身不等于协同。
3. hard/soft syntax 是对模型扰动响应形状的操作性分类。它提供机制线索，但最终的 TF 复合物结构和体内因果性仍需要独立实验验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multiomics and Deep Learning Dissect Regulatory Syntax in Human Development

**Liu, B.B., Jessa, S., Kim, S.H., Ng, Y.T. et al.**
Nature (2026) | DOI: [10.1038/s41586-026-10326-9](https://doi.org/10.1038/s41586-026-10326-9)
Greenleaf Lab, Kundaje Lab, Stanford University + Illumina AI Lab

---

### Motivation & Novelty

#### Biological Problem

During human development, transcription factors (TFs) bind regulatory DNA to establish cell identity, but the rules governing how combinations of TF binding sites cooperate — their "regulatory syntax" — remained poorly defined. Prior single-cell chromatin atlases covered individual organs (Trevino et al., *Cell* 2021; Ameen et al., *Cell* 2022) or single modalities (Cao et al., *Science* 2020; Domcke et al., *Science* 2020), and bulk approaches (Vierstra et al., *Nature* 2020; Meuleman et al., *Nature* 2020) obscured cellular heterogeneity. Classical motif enrichment methods (MEME, HOMER) identify overrepresented sequences but cannot test causal contributions or syntactic constraints. Deep learning models like BPNet (Avsec et al., *Nature Genetics* 2021) and ChromBPNet (Pampari et al., *bioRxiv* 2024) provided a framework for learning causal sequence features, but had not been applied systematically across human fetal development.

#### Unique Contributions

1. **Human Development Multiomic Atlas (HDMA)**: First multi-organ (12 organs), multimodal (ATAC + RNA from same cells), single-cell atlas of human fetal development — 817,740 cells, 203 cell types, >1 million cis-regulatory elements
2. **Cell-type-resolved ChromBPNet models**: 945 trained deep learning models (189 cell types × 5 folds) predicting base-resolution chromatin accessibility from DNA sequence
3. **508-motif regulatory lexicon**: Comprehensive catalog of de novo motifs driving accessibility, including 15 negative motifs that reduce accessibility — an underexplored regulatory mechanism
4. **Systematic TF cooperativity screen**: 67 synergistic motif pairs classified into 48 with "hard" (precise spacing/orientation) and 27 with "soft" (flexible) syntactic constraints, revealing distinct physical mechanisms
5. **Disease variant interpretation**: Fetal-specific regulatory contexts for adult-onset disease variants, identifying 28 variants in fetal-only accessible regions

---

### Method Overview

#### Experimental Design

SHARE-seq (split-and-pool combinatorial barcoding) simultaneously captures chromatin accessibility and gene expression from the same nuclei. 76 tissue samples from 23 individuals across 12 fetal organs (adrenal gland, brain, eye, heart, liver, lung, muscle, skin, spleen, stomach/oesophagus, thyroid, thymus) at post-conception weeks 10–23.

#### Computational Pipeline

1. **Preprocessing**: Snakemake pipeline converts raw sequencing to ATAC fragment files and RNA count matrices. RNA processed with Seurat (SCTransform v2 + DecontX); ATAC processed with ArchR + Macs2. 203 cell types annotated through iterative clustering.

2. **Regulatory element cataloguing**: 1,032,273 candidate cis-regulatory elements (caCREs) defined from iterative peak overlap. ABC model links caCREs to genes. VISTA enhancer validation resolves organ-specific activity including 6 liver enhancers misannotated in the original VISTA database.

3. **Deep learning**: ChromBPNet models trained per cell type to predict ATAC-seq profiles + counts from 2,114 bp DNA sequence input. Bias-factorized architecture separates Tn5 enzymatic preferences from TF-driven accessibility. DeepLIFT extracts per-nucleotide importance scores.

4. **Motif discovery**: TF-MoDISco clusters high-importance seqlets into motifs per cell type (6,362 total). Two-round clustering + manual curation yields 508 non-redundant motifs. Fi-NeMo identifies genomic instances via sparse regression.

5. **Synergy analysis**: In silico marginalization (tangermeme) tests composite motif pairs at 0–200 bp spacing × all orientations. Synergy quantified as deviation from log-additive model. Hard syntax (z-score > 4 at specific arrangements) vs soft syntax (synergy at 20–150 bp distances).

6. **Disease variants**: g-chromVAR identifies cell types enriched for GWAS variants. ChromBPNet predicts allele-specific accessibility changes. eQTL enrichment validates that positive motif disruption correlates with decreased expression.

See `doc_method.md` for mathematical details and `doc_code.md` for implementation mapping.

---

### Evaluation

#### Datasets

- **Primary**: 817,740 fetal cells across 12 organs (SHARE-seq, deposited BioProject PRJNA1402391)
- **Validation**: VISTA enhancer database (766 enhancers overlapping caCREs), ENCODE v4 cCREs, GTEx v8 eQTLs, CAUSALdb GWAS variants (1,483 GWASs, 349 traits)

#### Key Metrics & Results

| Analysis | Result |
|---|---|
| ChromBPNet model performance | Median Pearson r = 0.78 (predicted vs observed log counts, test chromosomes) |
| caCRE recovery of ENCODE v4 | 85.1% overlap; 48.7% of all ENCODE v4 sites recovered |
| Novel caCREs | 14.9% not in ENCODE (brain/eye enriched) |
| De novo motif lexicon | 508 motifs (493 positive, 15 negative) from 189 cell types |
| Synergistic motif pairs | 67 of 138 tested (48 hard syntax, 27 soft syntax; 8 overlap) |
| Hard syntax spacing | Peaks at 7 bp and 11 bp center-to-center |
| eQTL enrichment (positive motifs) | Downregulating variants: P = 9.91 × 10$^{-11}$, OR = 0.047 |
| eQTL enrichment (negative motifs) | Upregulating variants: P = 8.01 × 10$^{-4}$, OR = ∞ |
| Disease enrichment | 131 cell types significant (FDR < 0.05) across 13,194 GWAS studies |
| Fetal-only variant hits | 28 variants in fetal-accessible, adult-inaccessible regions |

#### Biological Validation

- **VISTA enhancers**: 6 heart-annotated enhancers re-classified as active in liver erythroblasts, confirmed by sectioning and histology
- **Coordinator element**: Predicted 5 bp head-to-tail geometry matches X-ray crystallography of TWIST1-TCF4-ALX4 complex (Kim et al., *Cell* 2024)
- **p53 homocomposite**: Predicted 4 bp separation matches canonical p53 response element
- **rs12740374 (CAD)**: Predicted gain of C/EBP site and increased accessibility consistent with established SORT1 enhancer mechanism (Musunuru et al., *Nature* 2010)

---

### Reproducibility

**Rating: 4/5**

#### Strengths
- **Complete code**: All analysis code deposited on GitHub (github.com/GreenleafLab/HDMA) and archived on Zenodo
- **Trained models**: 189 × 5 = 945 ChromBPNet models publicly available on Zenodo
- **Comprehensive data deposition**: Fragment files, count matrices, cell annotations, motif lexicon, motif instances, genomic tracks on Zenodo
- **Version-pinned environments**: Conda specs for all Python packages in `code/envs/`
- **Demo data**: Adrenal gland subset for testing pipelines
- **Interactive browser**: WashU Genome Browser trackhub for data exploration
- **Well-organized pipeline**: Clear directory structure with README documentation and figure-to-code mapping

#### Weaknesses
- **HPC dependency**: Pipeline designed for Stanford's Sherlock SLURM cluster; requires adaptation for other systems
- **No Docker/Singularity containers**: Environment setup relies on conda, which can be fragile across platforms
- **Large computational footprint**: Training 945 models requires substantial GPU time (estimated weeks)
- **External data dependencies**: Requires GTEx, ENCODE, CAUSALdb, VISTA downloads
- **Manual curation steps**: Motif QC and cell type annotation involve manual inspection not fully captured in code

#### Practical Notes
- **R version**: 4.1.2 (pinned); key packages: Seurat v4.3.0, ArchR v1.0.2, BPCells v0.2.0
- **Python**: ChromBPNet (commit a5c231), tangermeme v0.4.3, bpnetlite
- **GPU**: Required for ChromBPNet training, Fi-NeMo, and in silico marginalization
- **Memory**: ChromBPNet training uses ~60GB RAM per model; SLURM jobs specify `-G 1 --mem=60G`

---

### Compared Methods

| Method | Reference | Comparison |
|---|---|---|
| ENCODE v4 cCREs | Moore et al., *Nature* 2026 | 85.1% caCRE overlap; HDMA adds 14.9% novel elements |
| Cao et al. fetal gene expression | *Science* 2020 | HDMA has improved UMIs/genes per cell (multimodal advantage) |
| Domcke et al. fetal chromatin | *Science* 2020 | HDMA has higher TSS enrichment and fragment counts |
| BPNet / ChromBPNet | Avsec et al., *Nature Genetics* 2021; Pampari et al., *bioRxiv* 2024 | HDMA extends to 189 fetal cell types with systematic syntax analysis |
| CAP-SELEX TF cooperativity | Jolma et al., *Nature* 2015 | In vitro system; HDMA provides in vivo resolution across cell types |
| DNA-guided cooperativity | Xie et al., *Nature* 2025 | HDMA complements with developmental context |
| Coordinator element | Kim et al., *Cell* 2024 | HDMA independently recovers 5bp geometry from deep learning |
| IFN-β enhanceosome | Panne et al., *Cell* 2007 | Classic hard syntax example; HDMA identifies 48 additional cases |
| AICE/EICE composites | Glasmacher et al., *Science* 2012 | Known rigid composites; HDMA recovers and extends |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
