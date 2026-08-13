---
layout: default
permalink: /paper-atlas/sptedu-seq-debd1ac4/
title: "SPTEdU-seq"
nav: false
description: "SPTEdU-seq 把两个原本分开的实验合并起来：用 random-primer/加尾化学捕获空间 total transcriptome；用 EdU 标记 DNA 复制，再把 clicked tag probe 作为可测序的 UTI 信号捕获到同一块 10 μm spatial array。"
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
      <span>Cell Stem Cell · 2026</span>
    </div>
    <h1>SPTEdU-seq</h1>
    <p>SPTEdU-seq enables parallel optics-free newborn cell tracking and spatial total transcriptional dynamics in intact microenvironments</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.stem.2026.03.001" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SPTEdU-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/AritaZ-hang/SPTEdU-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for SPTEdU-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPTEdU-seq 方法解读：同一张空间芯片上读“总转录组”和“出生时间”

### 一句话抓住方法

SPTEdU-seq 把两个原本分开的实验合并起来：用 random-primer/加尾化学捕获空间 total transcriptome；用 EdU 标记 DNA 复制，再把 clicked tag probe 作为可测序的 UTI 信号捕获到同一块 10 μm spatial array。每个位置因此同时有基因表达 UMI 和 EdU-derived UTI，研究者无需荧光成像或 FACS，就能在完整组织中定位近期经历 DNA synthesis 的细胞并分析其转录状态。

“newborn cell”是论文对 UTI-enriched spatial bead 的功能性称呼。更精确地说，它表示在 EdU pulse window 内有足够 DNA replication signal 的空间位置；它可以是增殖、DNA repair 或混合 pixel，不能只凭 UTI 自动等同于完成分裂的新细胞。

### 1. 为什么普通空间转录组回答不了这个问题

大多数平台用 oligo-dT 抓取天然 poly(A) mRNA，强烈偏向 3' 端，难以同时观察 lncRNA、intronic/pre-mRNA、splicing intermediates。它们还是静态快照，无法知道某个表达状态是在处理前已存在，还是处理后新产生。

EdU 是 thymidine analog，在 S phase 被掺入 DNA。传统 EdU detection 依赖 fluorescence imaging；Div-seq/TrackerSci 可把 EdU 与单细胞 RNA 结合，却要 dissociation/FACS，丢失空间并可能损伤 reactive astrocytes 等脆弱细胞。SPTEdU-seq 的创新是把 EdU 变成一个 sequencing-readable molecular count。

### 2. 湿实验的两条分子支路

#### 2.1 总转录组支路

组织固定和 permeabilization 后，MATQ-like chemistry 用 random primer 在 RNA 不同位置 reverse-transcribe，而不是只从天然 poly(A) 尾开始。terminal transferase 再给 cDNA 加 dA tail，使其能与 chip 上 poly(T) probes hybridize。

这提高 gene-body coverage、non-polyadenylated RNA 和 unspliced reads，但“total”不是绝对无偏：primer preference、RNA structure、fragment length、mapping annotation 与 amplification 仍会影响各 RNA biotype。

#### 2.2 EdU/UTI 支路

EdU-bearing DNA 经 click chemistry 连接 5'-azide tag probe。每条 probe 带 10-nt unique tag identifier（UTI）、linker、sequencing primer 和可切 cleavage site。USER enzyme 释放 tag，tag probe 与 cDNA 一同被 spatial array 捕获。

custom array 约 80% beads 为 poly(T) capture、20% 为 linker capture。论文还提出对 conventional 100% poly(T) array 做 extension/strip，使部分 probes 获得 linker，从而降低专用芯片门槛。不过 10 μm pre-decoded chip 本身仍是重要实验依赖。

### 3. 一条 read 怎样被分到表达或 EdU

R1 包含三段 4-nt sub-barcode 与 linker，加上 10-nt UMI；合并后是 12-nt spatial barcode + 10-nt molecular tag。R2 是 cDNA insert 或 UTI tag。

`Upstream/Align/SPTT_upstream_Barcode_Preprocessing.sh` 与 `SPTT_mergeFastq.py` 提取/合并 barcode。`SPTT_upstream_clearStruct.sh` 在 R2 中搜索 27-nt linker3（允许 Hamming distance 2），将 reads 分成：

- `WithoutLinker`：transcript cDNA，进入 STAR/Drop-seq DGE；
- `WithLinker`：clicked tag probe，进入 UTI counting。

图 1 标示约 95% reads 为 transcript、约 5% 带 linker。这个比例受 EdU dose、组织增殖、capture design 和 sequencing allocation 影响，不是固定常数。

### 4. UTI/UMI ratio 为什么是核心指标

对 spatial barcode $b$：

$$
\mathrm{UMI}(b)=\text{表达分支的去重分子数},
$$

$$
\mathrm{UTI}(b)=\text{EdU 分支中不同 10-nt tag 序列数}.
$$

代码 `SPTT_barcode_UTI_summarise.py` 逐对读取 FASTQ：R1 前 12 nt 是 barcode，R2 前 10 nt 是 UTI；同一 barcode 下不同 UTI keys 的数量就是 UTI count。distinct tags 比 raw read count 更接近 clicked probe molecules，降低 PCR amplification 影响。

为校正 permeability、capture area 和 sequencing depth，使用：

$$
r_b=\log\left(1+\frac{\mathrm{UTI}(b)}{\mathrm{UMI}(b)}\right).
$$

`Trace-SPTT_IS/Analysis_Pipeline/01_GMM_Filter.R` 明确计算 `ratio=UTIs/UMIs` 和 `ratio_adjusted=log1p(ratio)`。高 $r_b$ 表示 EdU signal 相对 transcript capture 富集，但 UMI 很小时 ratio 会不稳定，因此必须先做 tissue/quality filtering。

### 5. 三步 UTI enrichment 如何选 newborn beads

`Trace-SPTT_IS/Enrich_Nascent_Barcodes/UTI_Threshold.R` 不是用一个全局固定 cutoff，而是逐样本拟合三层筛选。

#### 第一步：kernel density valley

对 $r_b$ 做 Gaussian KDE，在主背景峰下降区域寻找第一个局部最低点，去掉低 ratio background。

#### 第二步：一维 k-means

剩余 ratios 分成 $k=3$，以中间 cluster 的最大 ratio 作为进一步阈值。代码设置 `set.seed(1)`，因此这一步可重复。

#### 第三步：空间 GMM

在 $(x,y,UTI,UMI,r)$ 五维特征上拟合两个 Gaussian components。选择平均 ratio 更高的 component，再用 selected/non-selected ratio boundary 得到 final threshold。

加入 $(x,y)$ 的原因是 proliferative niches 通常空间聚集；但这也意味着算法偏好成团信号，散在的新生/增殖细胞可能被漏掉，而局部 technical hotspot 可能被强化。论文不同 stroke windows 的阈值不同（约 0.70、0.83、1.58），证明不应把一个 cutoff 跨样本复制。

### 6. 空间 barcode 如何连接到物理坐标

MOB/cerebrum 的 SEDAL-decoded chips 采用 degenerate barcode correction。`SPTT_degen_barcode.py` 同时构建：

- 空间上 10 μm 半径内的 bead adjacency；
- barcode sequence Hamming distance ≤1 adjacency。

两矩阵 element-wise 相乘后形成 graph，connected component 内的相近 beads 合并成含 N 的 degenerate consensus，并用成员坐标平均得到 centroid。随后 bipartite matching 只保留能唯一映射到一个 bead group 的 sequenced barcode。

这不是普通“容许一个错配”：它同时利用物理邻近与序列邻近，避免把全芯片远处相似 barcode 混在一起。embryo/tumor/human samples 则走 tagGD correction；两条路径对应不同 chip decoding，不应任意互换。

### 7. 表达矩阵为何富含 unspliced reads

WithoutLinker reads 经 STAR alignment 和 Drop-seq DigitalExpression。release scripts 设置 `LOCUS_FUNCTION_LIST=INTRONIC`、`STRAND_STRATEGY=BOTH`，并保留大量 intronic signal。这使 SPTEdU-seq 在 benchmark 中 unspliced fraction 高，可用于 RNA velocity 和 alternative splicing。

旧方法文档把 `--alignIntronMax 1` 解释为“最大化局部 intronic mapping”，需要谨慎：它禁止常规长 intron splice alignment，也可能损失跨 exon junction reads；具体 mapping tradeoff 必须结合另行 realignment/rMATS pipeline，而不能把一个 STAR 参数同时解释成所有剪接分析的优势。

### 8. 图 2 的 benchmark 应怎样读

论文以 mouse olfactory bulb 比较 Visium、Stereo-seq、Decoder-seq、Slide-seqV2、DBiT-seq、STRS、Patho-DBiT。SPTEdU-seq 在统一 subsampling 和 100 μm bins 下报告较高 UMI/gene capture，10 μm bins 平均约 1,109 genes、2,326 UMIs；100 μm bins 中位约 12,403 genes、210,583 UMIs。它也检测更高 ncRNA/unspliced fraction和更多 splicing events。

但平台数据来自不同实验、组织处理和公开数据，figure caption 也明确 fresh-frozen/FFPE、tissue types 不完全一致。它是 harmonized reanalysis，不是所有平台在同一块组织上的 head-to-head wet-lab trial。`Benchmark/Realign_Techs/` 和 subsampling scripts 实现部分统一处理，不能消除样本质量与 protocol differences。

### 9. 图 3–5：stroke 中“何时出生、在哪里、变成什么”

3–7 days post-stroke EdU labeling 在 lesion 周边形成 UTI-enriched beads。Fig. 3J 将其分成 oligodendrocytes、transit-amplifying astrocytes、reactive astrocytes、immature neurons 和 fibroblast-like cells，并与 adjacent EdU fluorescence 对照。

三组 pulse windows（0–3、3–7、10–14 dpi）提供 birth timing。CellRank/DPT 从 reactive astrocytes 经 transit-amplifying astrocytes 到 immature neurons构建 trajectory；CytoTRACE2 比较 newborns、neighbors、residents 的 potency；CellChat 在 spatial distance parameters 下推断 newborn–resident signaling；IF 验证 14 dpi 的 IGFBP5+ astrocytes。

这些证据组合支持 pro-repair niche 模型，但有三层边界：

1. EdU label 表示 pulse window 内 DNA synthesis，不是直接 lineage barcode；
2. DPT/CellRank 是状态连续性推断，不证明单个 astrocyte 真正变成 neuron；
3. CellChat arcs 是 ligand/receptor expression-based probabilities，长图线连接 cluster centroids，不代表长距离 physical signaling。

代码还存在一处 paper–code discrepancy：Methods 说 DPT root 手动指定为 C3；释放的 `06_Kb_python_CellRank.py` 使用 diffusion-map component 极值选择 root。结果可能相近，但复现时必须说明使用哪一种。

### 10. 图 6：胚胎 pulse-chase

pregnant dams 在 E10.5/E11.5 接受 EdU，embryos 在 E12.5/E14.5/E15.5 收集。不同收集时间让同一早期 pulse 的 labeled progeny 在空间和状态上展开。论文用 RGC→Cajal-Retzius、NSC→late neuroblast 的 trajectories，以及 E14.5 dorsal pallium inside-out velocity 描述 cortical development。

release repository没有完整 embryo-specific analysis pipeline，因此 paper results 可由数据与 Methods理解，但不能仅靠当前 GitHub scripts 端到端重建所有 Fig. 6 panels。

### 11. 图 7：tumor splicing 与 newborn–resident interactions

mouse orthotopic renal carcinoma 中，SPTEdU-seq 区分 tumor/normal regions，并以 rMATS 找到 differential AS，包括 *Cttn*、*Tpm1* skipped exon 和 *Ush1c* retained intron。UTI enrichment 标注 proliferative tumor cells、TAM、invasive/mesenchymal-like populations，CellChat 推断 collagen、CD45、Spp1 signaling。human ccRCC 通过 inferCNV 指认 3p loss。

这些 tumor-specific splicing、human inferCNV 和部分 interaction scripts 未包含在 release；旧摘要中“all analysis code”因此是过度声明，已修正为“core pipeline code available, several application analyses absent”。

### 12. 代码架构和实际复现顺序

仓库主要分为：

1. `Upstream/Align/`：barcode parsing、linker split、STAR/Drop-seq、UTI counts；
2. `Upstream/Barcode_Degen/`：SEDAL bead barcode reconstruction；
3. `SPTT_MOB/`、`SPTT_Hippocampus/`：GMM tissue filtering、clustering、RCTD、co-embedding、velocity/rMATS；
4. `Trace-SPTT_IS/`：UTI-enriched stroke beads、clustering、AUCell、CytoTRACE、CellRank、CellChat；
5. `Benchmark/`：subsampling、gene-body、velocity 和 cross-platform realignment。

大多数 R scripts 需要修改 `/your/workdir/`，processed Figshare intermediates 也很重要。仓库没有 container/environment lock。`SPTT_barcode_UTI_summarise.py` 还有一个路径拼接细节：写 `utis.pkl` 时使用 `workdir + "utis.pkl"`，若 workdir 没有末尾 `/` 会产生错误路径；运行时应显式规范目录。

### 13. 实践检查清单

1. 记录 EdU dose、pulse window 与 collection time；“出生时间”由这三者定义。
2. 用 adjacent fluorescence 或 negative control 校准 UTI enrichment。
3. 先过滤低 UMI beads，再计算 UTI/UMI ratio。
4. 每个样本独立拟合 KDE/k-means/GMM，并检查空间 hotspot。
5. 区分 measured bead、deconvolved cell type 与 inferred trajectory。
6. barcode correction 路径必须匹配 chip decoding method。
7. benchmark 报告 tissue/protocol differences，不只报排名。
8. velocity 与 splicing 使用适配的 alignment，不从单一 DGE BAM 推断全部。
9. CellRank root、QC thresholds 和 CellChat distance parameters写入结果元数据。
10. 对 release 缺失的 application scripts，不把论文结果称为本地可复现。

### 证据边界

本文档依据本地 Cell Stem Cell 论文 Markdown、Fig. 1–7 图像、workspace-local CodeGraph 以及 GitHub commit `809b0e88c40fd6a2787ae4b3056c2333ad9d54de` 的直接源代码重新编写。本次未重跑 GSE283159、Figshare processed data、chip decoding、STAR/Drop-seq、rMATS、CellRank 或 CellChat；所有论文数值均作为论文证据呈现，不声明新的本地复现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPTEdU-seq Summary

**Paper**: SPTEdU-seq enables parallel optics-free newborn cell tracking and spatial total transcriptional dynamics in intact microenvironments
**Authors**: Haofu Niu, Shuang Zhang, Jizhong Mao et al. (Guoji Guo / Xiaoping Han labs, Zhejiang University)
**Journal**: *Cell Stem Cell* (2026-03-26) | DOI: 10.1016/j.stem.2026.03.001
**Code**: https://github.com/AritaZ-hang/SPTEdU-seq | GEO: GSE283159 | Figshare: 10.6084/m9.figshare.27923973

---

### Motivation & Novelty

Spatial transcriptomics has transformed our ability to map gene expression in tissue context, but two fundamental gaps persist. First, existing platforms capture only polyadenylated (protein-coding) transcripts via oligo-dT priming, missing the vast landscape of non-coding RNAs (lncRNAs, snRNAs, snoRNAs) and splicing intermediates — molecules increasingly recognized as key regulators of cellular plasticity, neural repair, and tumor progression. Second, these methods provide static snapshots; they cannot distinguish recently born (proliferating) cells from established ones, obscuring dynamic events like neurogenesis and glial reprogramming. Prior attempts to combine EdU proliferation labeling with transcriptomics (Div-seq, *Nature Neuroscience* 2016; TrackerSci, *Nature Biotechnology* 2020) sacrifice spatial context and require FACS that damages fragile cell types like reactive astrocytes. FISH-based spatial approaches are limited to pre-defined gene panels.

SPTEdU-seq addresses all three limitations simultaneously through three innovations:

1. **MATQ random-primer chemistry** (MATQ previously described in *Nature Methods* 2019) achieves unbiased full-length transcriptome capture including ncRNAs and splicing isoforms.
2. **Click chemistry-based optics-free EdU detection**: instead of fluorophores, azide-modified single-molecule tag probes are clicked to EdU-labeled DNA and co-captured on the sequencing chip. No imaging is needed; newborn cells are identified computationally from unique tag identifier (UTI) counts.
3. **10 μm resolution spatial chip** (pre-decoded via SEDAL ligation-based sequencing) provides near-single-cell spatial resolution.

The platform is uniquely capable of co-profiling newborn and resident cell transcriptomes simultaneously in intact tissue, enabling previously inaccessible analyses of newborn–resident cell interactions.

---

### Method Overview

SPTEdU-seq integrates five technical components into a single assay:

- **EdU pulse labeling** (IP injection at 50 mg/kg) incorporates the thymidine analog into proliferating cell DNA.
- **In situ reverse transcription** with random primers (10-cycle temperature ramp, Maxima H Minus RTase) + poly(A) tailing (terminal transferase, 37°C, 20 min) → full-length cDNA from all RNA species.
- **Click chemistry** (Cu(I)/L-ascorbic acid, 37°C): 5'-azide-modified tag probes attach to EdU. Each probe carries a unique tag identifier (UTI) — a 10-nt barcode sequence.
- **Spatial chip capture**: cDNA and cleaved tag probes co-hybridize to barcoded beads on a 6×6 mm silicon chip (10 μm pitch, 80% poly-T + 20% linker sequences).
- **Computational demultiplexing**: sequencing reads split by linker presence → transcriptome DGE matrix (Drop-seq pipeline) + UTI count matrix (per-barcode distinct tag sequences).

Newborn cells are identified by the **UTI/UMI ratio** (normalized EdU signal) through a three-step enrichment: kernel density thresholding → k-means separation → spatial GMM. The spatial GMM is the critical step — it uses x/y coordinates alongside ratio values to capture the clustered topology of proliferative niches.

For detailed computational pipeline see `doc_method.md`; for code-paper correspondence see `doc_code.md`.

---

### Evaluation

#### Benchmarking (Figure 2)

SPTEdU-seq was benchmarked against seven spatial transcriptomics platforms on the mouse olfactory bulb (MOB):

| Platform | Year | Bias | Notes |
|----------|------|------|-------|
| 10× Visium | 2019 | 3' poly-A | Standard platform, 55 μm spots; *Nature Methods* |
| Stereo-seq | 2022 | 3' poly-A | BGI DNB-chip, ultra-high density; *Cell* 2022 |
| Decoder-seq | 2023 | 3' poly-A | GEO: GSE235896; *Nature Biomedical Engineering* 2023 |
| Slide-seqV2 | 2021 | 3' poly-A | 10 μm beads; *Nature Biotechnology* 2021 |
| DBiT-seq | 2020 | 3' poly-A | Microfluidic barcode delivery; *Cell* 2020 |
| STRS | 2023 | 3' poly-A | GEO: GSE200481 |
| Patho-DBiT | 2024 | 3' poly-A | GEO: GSE274641 |

**SPTEdU-seq key metrics**:
- Median 12,403 genes / 210,583 UMIs per 100-μm bin (at 50% sequencing saturation)
- Mean 1,109 genes / 2,326 UMIs per 10-μm bin
- Outperforms all 7 platforms at equivalent sequencing depth when normalized to 100 μm
- Detects more ncRNA species (random vs poly-T capture)
- Highest unspliced RNA fraction among all platforms (~46% unspliced in cerebrum clusters vs 15-25% in scRNA-seq)
- Spearman ρ = 0.71 with scRNA-seq reference datasets (comparable to other platforms)
- LWHM lateral diffusion: 60–90 μm (vs Stereo-seq V1 >200 μm, V2 >100 μm)
- Identifies 4,627 AS events in 2,727 genes (≥2 splice-junction reads) / 2,630 events in 1,714 genes (≥10 reads)
- 12–13% intergenic reads (minimal gDNA contamination); strand specificity scores: 0.9559 / 0.9603

#### Biological Applications

**Ischemic stroke**: Mapped neural repair dynamics over 4 time points (uninjured; 0–3, 3–7, 10–14 dpi). Identified transit-amplifying astrocytes as intermediate state between reactive astrocytes and immature neurons, validated by CytoTRACE2 developmental potency scores and DPT pseudotime analysis. Discovered *Igfbp5*^+^ astrocyte subtype at 14 dpi, confirmed by IF staining. Revealed lncRNA *Meg3* and histone methylation genes (*Jarid2*, *Camkmt*) as acute-phase epigenetic regulators.

**Embryonic development**: Continuous lineage tracing of EdU-labeled cells (E10.5/E11.5 labeling, collection at E12.5/E14.5/E15.5). Reconstructed RGC → Cajal-Retzius cell and NSC → neuroblast trajectories. Inside-out RNA velocity pattern in E14.5 dorsal pallium confirmed cortical layer formation.

**Renal carcinoma**: Identified 808 AS events in tumor vs normal regions (mouse orthotopic model), including *Cttn* SE (pro-tumorigenic), *Tpm1* SE (motility enhancing), *Ush1c* RI (invasive). Human ccRCC: 3p chromosomal loss detected by inferCNV, consistent with pathological diagnosis.

---

### Reproducibility Rating: 3/5

**Justification**: The method requires substantial wet-lab expertise (click chemistry optimization, custom chip fabrication by Celatlas) and computational infrastructure (CUDA for potential large-scale processing, STAR/Drop-seq pipeline). Data is available (GEO: GSE283159, Figshare), and code is complete for all analytical steps. However, several barriers reduce practical reproducibility:

**Strengths**:
- Core upstream, stroke, MOB/hippocampus, UTI, velocity, communication, and benchmark code is available with clear module organization; several embryo/tumor/human analyses are not released
- All benchmarking data from public GEO accessions
- GEO raw data for replication available
- Figshare processed data enables running analysis without upstream pipeline

**Weaknesses**:
- Custom chip requires commercial partnership with Celatlas Gene Technology — not freely available
- `ratio_adjusted` formula now confirmed in `01_GMM_Filter.R:23-26` as `log1p(UTI/UMI)`, but the pipeline from raw FASTQ to `Total_map_meta.RDS` requires running scripts in specific order
- Processed data (Figshare) needed to run most scripts (raw data → processed intermediates not fully automated)
- Analysis scripts use hardcoded paths (`/your/workdir/`); require manual configuration
- Two different barcode correction pipelines (Slide-seqV2 degeneration vs tagGD) with different sample requirements, not clearly documented which to use when
- No containerized environment (no Docker/Singularity provided)

**Practical notes**:
1. Custom chips: Contact Celatlas Gene Technology. The modification for conventional poly(T) arrays (Figure 1B) is described in detail and uses standard Klenow extension — this is the more accessible starting point.
2. To run analysis scripts, first download processed data from Figshare and set `setwd()` and hardcoded paths in each R script.
3. For the UTI pipeline, run `01_GMM_Filter.R` first to compute `ratio_adjusted = log1p(UTI/UMI)` and save `Total_map_meta.RDS`, then run `UTI_Threshold.R` for the 3-step enrichment.
4. k-means in `UTI_Threshold.R` uses `set.seed(1)` — results are deterministic.
5. CellRank trajectory requires h5ad file from kb-python (`KB_python_adata.h5ad`) which is an intermediate file from the velocity pipeline, not in the repository.
6. Embryo analysis, tumor-specific splicing, human ccRCC inferCNV, pySCENIC, and GSVA scripts are absent from the repository — these analyses described in the paper cannot be reproduced from released code alone.
7. Paper states DPT root is "manually designated as C3" but code uses automated `diffmap[:,2].argmax()` — a minor methodological discrepancy.
8. Two barcode correction paths exist: Slide-seqV2 degeneration (MOB/cerebrum, SEDAL-decoded chips) vs tagGD (embryo/tumor/human, illumina-barcoded chips). Choose based on chip decoding method.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
