---
layout: default
permalink: /paper-atlas/share-seq-1905ff68/
title: "SHARE-seq"
nav: false
description: "SHARE-seq 是一种 split–pool combinatorial barcoding 技术：在同一固定细胞/细胞核内分别标记开放染色质和 mRNA，再给两类分子连接相同的三轮细胞条形码，最终分开建 ATAC 与 RNA 文库。论文利用真实的一对一配对测量寻找 peak–gene 关联、定义 DORC，并把当前 DORC 可及性与其他细胞的 RNA 状态匹配，得到“chromatin potential”向量。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Cell · 2020</span>
    </div>
    <h1>SHARE-seq</h1>
    <p>Chromatin Potential Identified by Shared Single-Cell Profiling of RNA and Chromatin</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2020.09.056" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SHARE-seq：同一细胞中连接染色质可及性、RNA 与潜在命运

主论文：Ma et al., *Chromatin Potential Identified by Shared Single-Cell Profiling of RNA and Chromatin*（Cell, 2020；DOI: 10.1016/j.cell.2020.09.056）

伴随短评：Clyde, *SHARE-seq reveals chromatin potential*（Nature Reviews Genetics, 2021）

### 一句话理解

SHARE-seq 是一种 split–pool combinatorial barcoding 技术：在同一固定细胞/细胞核内分别标记开放染色质和 mRNA，再给两类分子连接相同的三轮细胞条形码，最终分开建 ATAC 与 RNA 文库。论文利用真实的一对一配对测量寻找 peak–gene 关联、定义 DORC，并把当前 DORC 可及性与其他细胞的 RNA 状态匹配，得到“chromatin potential”向量。

chromatin potential 是跨模态近邻推断，不是 lineage tracing、物理时间模型或已校准的单细胞未来概率；“future”表示数据流形上与当前染色质最兼容的后续 RNA 状态假设。

### 1. 为什么必须在同一细胞测两种模态

若 ATAC 和 RNA 来自不同细胞，整合算法通常假定两种模态共享相同细胞身份。但染色质开放可能先于转录，正是这种时间错位承载 lineage priming 信号；强制对齐反而可能抹掉它。SHARE-seq 用共同 barcode 给同一细胞的 ATAC 与 RNA 建立实验配对，使“染色质已开放、RNA 尚未表达”成为可直接观察的联合状态。

论文共分析 84,426 个来自四种细胞系和鼠肺、脑、皮肤的 profiles；核心毛囊分析使用 34,774 个小鼠皮肤联合 profiles。这些数字是作者数据结果，不代表每次 SHARE-seq 都能达到相同产量或质量。

### 2. SHARE-seq 实验流程

#### 2.1 先在完整细胞/细胞核内标记两类分子

1. 低浓度甲醛固定并透化细胞或细胞核，保存分子共定位。
2. Tn5 对开放染色质做 transposition。
3. 带 UMI 和 biotin 的 poly(T) primer 对 mRNA 逆转录。

此时 ATAC 片段和 cDNA 仍属于同一个细胞，但还没有唯一细胞编号。

#### 2.2 三轮 split–pool 赋予共同细胞 barcode

细胞被分到 96 孔板，与 well-specific oligo 杂交，再混合并重复分孔，共三轮。落在同一细胞内的 ATAC 与 cDNA 分子得到同一个 barcode 组合。理论组合数为

$$
D=96^3=884{,}736.
$$

随后同时连接 barcode，去交联释放分子。用 streptavidin beads 捕获 biotin-cDNA，把 RNA 与 chromatin library 分开；两套测序 reads 再按共同 barcode 配回同一细胞。

三轮 barcode 不是绝对唯一：两个细胞可能碰巧走过同一孔序列。论文用 birthday-collision 公式估计每个 sub-library 20,000 细胞时约 224 次碰撞，即约 1%；人鼠混合实验实测 2,244 个通过 QC 的细胞中仅一个跨物种 doublet（0.04%）。理论负载碰撞和特定小规模实验实测率不能混为同一个指标。

### 3. 两个测序模态如何预处理

ATAC reads 经自定义 trimming/demultiplexing 后用 Bowtie2 比对，过滤低 MAPQ、异常配对、chrY/线粒体等 reads，Picard 去重复，MACS2 call summits，并把 summit 向两侧各延伸 150 bp。RNA 用 STAR/featureCounts 等流程统计 exon 与 intron；SHARE-seq RNA 对 intronic reads 富集，因此既能看成熟 RNA，也能近似看 nascent RNA。

论文明确说 raw reads 由 custom Python script trimming，但资源表只给 GEO GSE140203 和第三方软件，没有本地或公开的专用分析代码仓库。因而从 FASTQ 到作者矩阵的条形码纠错、trim 和部分定制分析不能仅靠本工作区逐行复核。

### 4. peak–gene 关联如何建立

对每个 gene，先考虑 TSS 周围 $\pm50$ kb 的 ATAC peaks，计算跨细胞 peak accessibility 与 gene expression 的 Spearman 相关 $\rho_{obs}$。高可及 peak 与 GC 含量会系统性抬高相关，因此 chromVAR 为每个 peak 找 100 个 accessibility/GC 匹配的 background peaks，构造 null correlation 分布：

$$
z=\frac{\rho_{obs}-\mu_{null}}{\sigma_{null}}.
$$

作者用 one-sided z-test；负相关 peaks 约占 1.2%，为简化而未作为显著正调控关联。若一个 peak 显著关联多个 genes，只保留最小 p 值的一条。皮肤数据在 $p<0.05$、报告 FDR 0.1 下得到 63,110 条关联。

重要边界：这是同细胞共变加背景校正，不是 enhancer perturbation 或 3D contact 的直接证据。细胞类型、伪时间或共同上游因子都可能制造相关；one-sided test 也系统性忽略潜在抑制关联。

### 5. DORC 是如何定义和计分的

把 genes 按 $\pm50$ kb 内显著关联 peak 数排序，作者依据 rank curve 的 elbow，把超过 10 个 peaks 的 857 个皮肤 genes 定义为 Domains of Regulatory Chromatin（DORCs）；GM12878 cutoff 为 5。随后对这些 genes 把搜索窗扩到 $\pm500$ kb，重新计算关联。

cell $c$ 上 gene $g$ 的 DORC score 是其所有显著 peaks 的 normalized accessibility 之和：

$$
D_g(c)=\sum_{p\in P_g}
\frac{x_{cp}}{\sum_{q\in P_{all}}x_{cq}}.
$$

DORC 不是一段由连续坐标严格分割出的 domain，而是“围绕某 gene 的显著相关 peak 集合”；大于 10 的阈值来自本数据 elbow，不是普适生物常数。DORCs 与 super-enhancers 显著富集重叠，但只有部分 DORCs 属于已有 super-enhancers，两者不是同义词。

### 6. residual 如何描述“染色质领先 RNA”

作者用 chromatin/cisTopic 空间建立分化 pseudotime（Palantir）。对每个 DORC gene，分别沿 pseudotime 用 loess 平滑 DORC score 与 RNA expression，再各自 min–max normalize，定义

$$
R_g(t)=\widetilde D_g(t)-\widetilde E_g(t).
$$

$R>0$ 表示在各自动态范围归一化后，染色质曲线走在 RNA 曲线前面。论文报告毛囊谱系中 92% DORC-regulated genes 的平均 residual 为正，并在 Wnt3 等位点观察到 enhancer accessibility、promoter accessibility、intronic RNA、exonic RNA 的顺序变化。

Residual 不是原始 counts 差值，也没有统一物理单位；它受 pseudotime、loess bandwidth 和各曲线 min–max 极值影响。正 residual 支持时间先后关联，但不能单独证明开放染色质因果驱动转录。

### 7. chromatin potential 算法逐步拆解

#### 第一步：把输入限制到 DORC 对应特征

对每个细胞保留 DORC scores（chromatin profile）及相应 genes 的 RNA expression。先在 normalized cisTopic ATAC topics 建 $k=50$ 邻域，对两类 profiles 分别平滑，减少单细胞稀疏性。

#### 第二步：跨模态寻找 RNA 邻居

对细胞 $i$ 的平滑 chromatin vector $C^{ATAC}_i$，在所有细胞的平滑 RNA vectors $C^{RNA}_j$ 中找最相似的 10 个：

$$
N_i=\operatorname{kNN}_{j}^{k=10}
\left(C^{ATAC}_i,C^{RNA}_j\right).
$$

这里两种向量因使用一一对应的 DORC genes 才能直接比较。匹配到的是数据集中真实存在的其他 cells，而不是由动力学方程外推的新表达向量。

#### 第三步：在 chromatin embedding 上画向量

将这 10 个 RNA-matched cells 在 chromatin low-dimensional space 中的位置取平均，从 cell $i$ 指向该平均位置。箭头长度反映当前位置与匹配状态的距离。为展示，作者再用低维空间 $k=15$ 近邻平滑 arrows，或在 UMAP 上分成 $40\times40$ grids 后平均。

这至少包含三层平滑/平均（profile $k=50$、cross-modal $k=10$、arrow $k=15$），所以单根可视化箭头并不是单细胞原始测量。Methods 只说 arrow length 经过 normalization，没有给出完整归一化公式；本地也没有代码可确认。因此不能声称可从文字无歧义地逐位复现向量长度。

#### 一个简化例子

若细胞 A 的 DORC profile 最接近 RNA cells B、C、D，而它们在 ATAC UMAP 的坐标平均为 $(4,3)$，A 位于 $(1,1)$，raw vector 是 $(3,2)$。这表示 A 的染色质更像 B/C/D 已呈现的 RNA 状态；它不表示 A 在 1 个单位时间后必然移动到 $(4,3)$。

### 8. chromatin potential 与 RNA velocity 的差别

RNA velocity 利用同一细胞 unspliced/spliced imbalance，通常对应较短期转录动力学；chromatin potential 用当前 chromatin profile 匹配数据中的 RNA states，试图捕捉更早的 priming。论文观察到早期 TAC 中 chromatin-potential arrows 较长、RNA velocity 分辨率较低，而晚期 RNA velocity reach 更远。

但 arrow length 不是统一时间单位，两种方法也使用不同特征、平滑和 embedding，不能仅凭向量更长断言预测时间严格更久。论文自己强调 primed chromatin 可逆，因此 chromatin potential 表示“likely/possible”，而非已经 committed 的命运。

### 9. TF–DORC 网络如何构建

候选 TF 同时满足两类证据：

1. TF expression 与 DORC score 的 Spearman correlation；
2. DORC peaks 中 TF motif 相对 GC/accessibility-matched backgrounds 的富集。

作者先在 DORC-score PC space 找 $k=50$ DORC neighbors，再用 chromVAR `matchMotifs`/KS test 计算 motif enrichment；最终阈值根据分布手动设定。因此网络是“表达关联 + motif 支持”的候选调控图，不等于 TF binding 或 perturbation 验证网络，且同 motif family 的 TF 往往难以区分。

### 10. 图证据应怎样阅读

- **图 1**：技术工作流、人鼠混合碰撞与 ATAC/RNA sensitivity，证明两模态能在同一 barcode 下可靠共测。
- **图 2**：皮肤 RNA 与 ATAC independently resolve 相似但不完全相同的 cell types；计算配对在皮肤只有 74.9% cluster-level agreement，说明真实共测有必要。
- **图 3**：peak–gene 背景校正、Dlx3 locus 和 DORC/super-enhancer enrichment，支撑 DORC 定义但不证明每条 edge 因果。
- **图 4**：Wnt3 等基因沿 pseudotime 的 DORC–RNA lag，以及 enhancer→promoter→intron→exon 顺序，是 priming 主证据。
- **图 5**：TF–DORC network、poised histone marks 与 chromatin-potential arrows；不同毛囊 stages 和 RNA velocity 提供一致性支持，但不是逐细胞未来跟踪。

### 11. 代码与复现状态

| 环节 | 论文/本地证据 | 状态 |
|---|---|---|
| SHARE-seq wet-lab protocol | STAR Methods、试剂与步骤 | 描述较完整 |
| custom trimming/demultiplexing | 论文称 custom Python script | **Not found**：本地无源码仓库 |
| Bowtie2/STAR/MACS2/chromVAR/cisTopic/Palantir | 版本/参数见 Methods | 外部工具可获得，但不是 SHARE-seq 专用代码 |
| peak–gene background model | 公式和参数在 Methods | 可重实现；作者代码 **Not found** |
| DORC scoring/residual | 步骤清楚 | 可重实现；平滑细节仍影响结果 |
| chromatin potential | k 值和概念步骤给出 | **Partial**：arrow normalization 未说明，源码 **Not found** |
| TF–DORC thresholds | Methods 明称 manual cutoffs | 不能从文字自动复现精确网络 |
| 原始数据 | GEO GSE140203 | 可获取；本次未重新下载/计算 |

因此 `doc_code.md` 应被理解为 paper-described implementation audit，而不是本地 repository source map。`.codegraph` 没有找到相关实现符号也与 paper-only 状态一致。

### 12. 最重要的解释边界

- peak–gene correlation 不是 enhancer–gene causal link。
- DORC cutoff 是数据驱动 elbow，不应直接复制到新组织。
- residual 是两条独立归一化平滑曲线的差，不是绝对分子时间差。
- chromatin potential 匹配其他已观察细胞，不是真实 longitudinal tracking。
- UMAP arrow 受 embedding 和多层 smoothing 影响，长箭头也可能来自噪声或稀有细胞；论文明确承认这一点。
- priming 可以逆转；chromatin state 表示 bias/potential，不等于命运承诺。
- 没有作者定制代码时，不能声称该工作区可一键复现 FASTQ 到所有论文图。

### 建议阅读顺序

先读主论文图 1 理解共同条形码，再读图 3 的 peak–gene/DORC、图 4 的 residual 与时间先后、图 5 的 chromatin potential。随后核对 STAR Methods 的 `Peak-gene association`、`DORC`、`Residual analysis` 和 `Chromatin potential` 四节；伴随短评只用于快速概览，最终方法边界以 Cell 主论文为准。

### 证据范围

本文基于本地主论文 PDF/OCR Markdown、提取的主图/补充图、伴随研究短评及现有分析文档整理。论文 DOI 为 `10.1016/j.cell.2020.09.056`，数据入口为 GEO `GSE140203`。本工作区没有 SHARE-seq 作者分析代码仓库；本次未下载原始数据、重跑 wet-lab demultiplexing 或复算 chromatin-potential arrows。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SHARE-seq: Chromatin Potential Identified by Shared Single-Cell Profiling of RNA and Chromatin

### Paper Information

- **Main Paper**: Ma, S. et al. "Chromatin Potential Identified by Shared Single-Cell Profiling of RNA and Chromatin." *Cell* **183**, 1103–1116 (2020)
- **Companion**: Clyde, D. "SHARE-seq reveals chromatin potential." *Nature Reviews Genetics* **22**, 2 (2021) — Research Highlight summarizing the main paper
- **Authors**: Sai Ma, Bing Zhang, Lindsay M. LaFave, Andrew S. Earl, Zachary Chiang, Yan Hu, Jiarui Ding, Alison Brack, Vinay K. Kartha, Tristan Tay, Travis Law, Caleb Lareau, Ya-Chieh Hsu, Aviv Regev, Jason D. Buenrostro
- **Affiliations**: Broad Institute, Harvard University, MIT
- **Data**: GEO: GSE140203
- **Visualization**: https://buenrostrolab.shinyapps.io/skinnetwork/

---

### Motivation & Problem Statement

Cell differentiation is regulated across multiple layers of gene regulation, including chromatin accessibility and gene expression. A longstanding hypothesis in developmental biology posits that changes in chromatin state (e.g., histone modifications, chromatin accessibility) may **precede and foreshadow** changes in gene expression, creating "primed" chromatin states that bias cells toward particular lineage outcomes. However, prior evidence for this came only from bulk measurements of purified cell populations, which require well-defined markers, FACS isolation, and synchronous models — making it impossible to study priming in asynchronous, complex tissues at single-cell resolution.

Existing single-cell multi-omics methods (sci-CAR, SNARE-seq, Paired-seq) could co-profile chromatin accessibility (ATAC) and gene expression (RNA) in the same cell, but suffered from **limited throughput, low sensitivity, or high cost**, restricting the ability to detect fine regulatory differences.

**Key question**: Can we build a scalable, sensitive technology to simultaneously measure chromatin accessibility and gene expression in the same single cell, and use it to determine whether chromatin accessibility truly foreshadows gene expression during lineage commitment?

---

### Novelty & Unique Contributions

1. **SHARE-seq technology**: A highly scalable split-pool combinatorial barcoding method for joint scATAC-seq and scRNA-seq from the same cell, with ~$96^3 \approx 885{,}000$ barcode combinations per sub-library, achieving remarkably low collision rates (~0.04–1%) and substantially outperforming all prior joint profiling methods in both library complexity and cost efficiency (~\$433 per 100,000 cells vs. >\$30,000 for sci-CAR).

2. **Domains of Regulatory Chromatin (DORCs)**: A new computational concept — genes with an exceptionally large number (>10) of significantly associated chromatin peaks in *cis*. DORCs identify key lineage-determining genes *de novo* without prior knowledge of cell type identity, overlap with super-enhancers, and are highly cell-type-specific.

3. **Chromatin Potential**: A new analytical framework analogous to RNA velocity but operating on chromatin-to-RNA dynamics. Chromatin potential predicts a cell's future RNA state from its current chromatin state, providing **longer-range temporal predictions** than RNA velocity, especially at early stages of differentiation.

4. **Evidence for chromatin priming**: Direct single-cell evidence that chromatin accessibility at DORCs precedes gene expression during hair follicle differentiation, with sequential activation of distal enhancers → promoter → nascent RNA → mature RNA.

---

### Method Overview

#### Experimental Platform (SHARE-seq)

1. **Fixation & Permeabilization**: Cells/nuclei fixed with 0.1–0.2% formaldehyde
2. **Tn5 Transposition**: Tags open chromatin regions
3. **Reverse Transcription**: Poly(T) primer with UMI and biotin tag converts mRNA to cDNA
4. **Split-Pool Barcoding**: Three rounds of 96-well plate hybridization → $96^3$ unique barcode combinations
5. **Ligation**: Barcodes simultaneously attached to cDNA and chromatin fragments
6. **Reverse Crosslinking**: Releases barcoded molecules
7. **Streptavidin Separation**: Biotin-tagged cDNA separated from chromatin using streptavidin beads
8. **Independent Library Prep**: Separate scATAC and scRNA libraries sequenced and paired by shared barcodes

#### Computational Pipeline

1. **Pre-processing**: Bowtie2 alignment (ATAC), STAR alignment (RNA), MACS2 peak calling, chromVAR for TF motif analysis
2. **Dimensionality Reduction**: cisTopic (ATAC), PCA + UMAP (RNA), Seurat v3 for clustering
3. **Peak-Gene Association**: Spearman correlation between peak accessibility and gene expression across cells, with GC-content and accessibility-matched background correction
4. **DORC Identification**: Genes ranked by number of associated peaks; >10 peaks → DORC
5. **Pseudotime**: Palantir on cisTopic-derived topics
6. **Residual Analysis**: DORC score − gene expression (both loess-smoothed and min-max normalized over pseudotime)
7. **Chromatin Potential**: k-NN (k=10) between smoothed chromatin profile of cell $C_{\text{atac}}$ and smoothed RNA profiles of all cells → arrow from chromatin state to predicted future RNA state
8. **TF Regulatory Network**: Combining TF motif enrichment in DORCs with TF expression–DORC score correlation

---

### Key Results

#### Technology Validation
- 34,774 high-quality joint profiles from adult mouse skin; 84,426 total cells across 4 cell lines and 3 tissues
- Median: ~2,545 RNA UMIs and ~8,252 unique ATAC fragments per cell
- Outperformed sci-CAR, SNARE-seq, and Paired-seq in both ATAC and RNA library complexity
- RNA enriched for intronic regions (similar to snRNA-seq), useful for studying nascent transcription

#### Cell Type Discovery
- Chromatin and RNA-defined cell types broadly congruent (74.9% correct computational pairing in skin)
- Notable exception: Cell cycle genes form coherent RNA clusters but not chromatin clusters, suggesting cell cycle is more reflected in gene expression than chromatin accessibility
- TAC populations (which couple cell cycle with lineage identity changes) form coherent clusters in both modalities

#### Peak-Gene Associations & DORCs
- 63,110 significant peak-gene associations in mouse skin (±50 kb, p < 0.05, FDR = 0.1)
- Half-life of peak-gene association distance: 24.4 ± 3.6 kb — remarkably consistent with CRISPR perturbation data (24.1 kb)
- 857 DORCs identified (>10 peaks per gene), enriched for:
  - Known super-enhancers (2.1-fold enrichment, $p = 10^{-238}$)
  - Key lineage-determining TFs (*Dlx3*, *Lef1*, *Hoxc13*, *Wnt3*)
- 82% of chromatin peaks not correlated with any gene expression

#### Lineage Priming
- 92% of DORC-regulated genes show positive residuals (chromatin accessibility > gene expression)
- Sequential activation at *Wnt3* locus: distal enhancers → promoter → intron RNA → exon RNA
- Stepwise TF regulatory model: *Lef1* expression → *Lef1* motif accessibility → *Hoxc13* expression → *Hoxc13* motif + *Wnt3* DORC → *Wnt3* RNA
- Lineage-primed loci correspond to "poised" histone states (H3K4me1$^{\text{high}}$ / H3K27ac$^{\text{low}}$)

#### Chromatin Potential
- Chromatin potential arrows flow from progenitors (TACs) to differentiated cells (IRS/hair shaft)
- Identified a second root of differentiation (TAC-2) not detected by pseudotime alone, validated by RNA velocity and hair follicle staging experiments
- Chromatin potential has **longer reach** than RNA velocity at early pseudotimes; RNA velocity has farther reach at late pseudotimes
- Discrepancy between RNA velocity and chromatin potential greatest in TACs (undifferentiated progenitors)

---

### Evaluation & Validation

| Validation Aspect | Method | Result |
|---|---|---|
| Species mixing | Human/mouse cell line mix | 0.04% collision rate, clean separation |
| Concordance with published data | Bulk ATAC-seq, ChIP-seq, HiChIP | Peak-gene associations enriched in H3K27ac HiChIP loops ($p < 10^{-608}$), depleted in H3K27me3 |
| Biological validation | Known super-enhancers | 2.1× enrichment in DORCs |
| Priming validation | ChIP-seq poised enhancer marks | High-residual DORCs coincide with poised chromatin (H3K4me1$^{\text{hi}}$/H3K27ac$^{\text{lo}}$) |
| Temporal validation | SHARE-seq on multiple hair cycle stages | TAC-1 and TAC-2 present at anagen III and VI, consistent with lineage-biased progenitors |
| Method comparison | RNA velocity | Chromatin potential resolves TAC fate dynamics where RNA velocity cannot |
| Computational pairing benchmark | Seurat CCA | 74.9% (skin), 36.7% (brain) correct assignment |

---

### Reproducibility Assessment

**Rating: 4/5**

| Factor | Status |
|---|---|
| Data availability | GEO: GSE140203, all raw and processed data deposited |
| Code availability | Custom scripts referenced but not deposited as a formal package; key tools (chromVAR, Seurat, Palantir, cisTopic) are publicly available |
| Protocol detail | Highly detailed STAR Methods with exact reagent concentrations, incubation times, buffer recipes |
| Computational reproducibility | All key parameters documented; background correction for peak-gene associations well-described |
| Potential blockers | Custom Python scripts for read trimming/demultiplexing not publicly released; chromatin potential code not packaged |

---

### Significance for the Field

SHARE-seq established several foundational concepts now widely adopted in single-cell multi-omics:

1. **DORCs** provide a principled, unsupervised way to identify key lineage genes and their regulatory regions without requiring cell sorting or ChIP-seq
2. **Chromatin potential** complements RNA velocity by predicting cell fate at longer timescales, from chromatin state rather than splicing kinetics
3. The split-pool barcoding strategy influenced subsequent technologies (e.g., SHARE-seq derivatives, multi-ome platforms)
4. Demonstrated that chromatin accessibility and gene expression, while broadly concordant, carry distinct and complementary information about cell identity and fate

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
