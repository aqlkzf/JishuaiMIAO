---
layout: default
permalink: /paper-atlas/scmultiomics-cardiovascular-review-740fdc75/
title: "scMultiomics_Cardiovascular_Review"
nav: false
description: "这篇 2023 年 Nature Cardiovascular Research 综述不是提出一个新算法，而是回答三个连续问题：心脏和血管组织为什么需要单细胞分辨率；RNA、染色质、蛋白、空间和扰动技术各自能回答什么；怎样把这些观测连接到心血管发育、心肌病、心肌梗死和动脉粥样硬化机制。"
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
      <span>Nature Cardiovascular Research · 2023</span>
    </div>
    <h1>scMultiomics_Cardiovascular_Review</h1>
    <p>Current and future perspectives of single-cell multi-omics technologies in cardiovascular research</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s44161-022-00205-7" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 心血管单细胞多组学综述：如何选择技术、理解输出与避免过度推断

### 综述的核心问题

这篇 2023 年 *Nature Cardiovascular Research* 综述不是提出一个新算法，而是回答三个连续问题：心脏和血管组织为什么需要单细胞分辨率；RNA、染色质、蛋白、空间和扰动技术各自能回答什么；怎样把这些观测连接到心血管发育、心肌病、心肌梗死和动脉粥样硬化机制。

论文题为 *Current and future perspectives of single-cell multi-omics technologies in cardiovascular research*，DOI `10.1038/s44161-022-00205-7`。其证据时间窗主要截至 2022 年，因此本文将“综述当时的判断”与 2026 年的当前技术状态明确分开。

### 1. 为什么心血管组织特别难做单细胞

心脏不是“心肌细胞的均一集合”。心肌细胞、成纤维细胞、内皮细胞、周细胞、平滑肌细胞、免疫细胞、脂肪细胞和神经相关细胞共同组成组织。bulk RNA-seq 把它们混合平均，稀有或相反方向的细胞特异变化会被抵消。

但完整心肌细胞体积大、脆弱，胶原丰富的心肌难以温和解离。于是方法选择本身会改变观察到的细胞组成：

- scRNA-seq 捕获完整细胞和胞质 RNA，对单核/中间型巨噬细胞等群体更有利；
- snRNA-seq 可用于冷冻组织并减少大型心肌细胞的解离损伤，但偏向核内转录本，可能低估胞质富集基因；
- 同一心脏的 scRNA 与 snRNA 结果不能简单当作无偏重复，二者更适合互补验证。

因此，心血管单细胞图谱的第一个问题不是“聚类算法选什么”，而是样本制备是否系统性漏掉某些细胞。

### 2. 捕获策略：灵敏度、规模和偏差的交换

#### 微流控/独立反应室

C1 Fluidigm 把细胞放入可成像的 IFC 反应室，能在裂解前检查细胞，但通量较低。10x Chromium 将细胞、带条形码的 gel bead 和油相形成 GEM，在一个液滴中加入 cell barcode 和 UMI，适合数万细胞。

图 2a、2b 的关键差异不是品牌，而是“物理单室”与“概率液滴封装”。液滴法必须面对 doublet/multiplet；所谓一滴一细胞一珠是目标设计，而不是每个液滴都实际满足的事实。

#### 组合索引

sci-RNA-seq/SPLiT-seq 反复执行 split → barcode → pool。若三轮分别有 $B_1,B_2,B_3$ 个条形码，理论组合数为：

$$
N_{\mathrm{barcode}}=B_1B_2B_3.
$$

但可安全回收的细胞数必须明显低于组合总数，否则两个细胞得到同一组合的碰撞概率迅速上升。这是生日悖论式约束。组合索引可扩展到百万细胞，代价通常是单细胞检测灵敏度较低、流程更复杂。

图 2c–e 实际是同一 split-pool 流程的连续部分，不是两个“未知附加面板”：第一轮逆转录条形码、pool/第二轮条形码、再次 pool/第三轮条形码。

### 3. scRNA-seq：从计数矩阵到心脏细胞状态

标准输入是 cell × gene UMI count matrix。图 4 将计算流程串成：比对/计数 → QC → normalization/feature selection → dimension reduction/data correction → clustering、trajectory、annotation、communication 和 network inference。

这个流程的每一步都可能制造“看似生物学”的结构：

- doublet 形成混合表达型，可能被误标为新细胞类型；
- ambient RNA 让细胞带上并非自身产生的转录本；
- 高 mitochondrial fraction 在受损细胞中常见，但心脏本身代谢旺盛，统一阈值会误删真实心肌细胞；
- batch correction 太弱会保留批次，太强会抹掉疾病或基因型差异；
- cluster label 多为依据 marker 的“最佳解释”，需要原位或功能证据验证。

综述用 HCM/DCM 说明疾病变化既包括心肌细胞 NPPA/NPPB、ANKRD1 等应激程序，也包括 POSTN、NOX4、COL1A1 等成纤维细胞激活程序。图 3 是细胞类型/marker 参考图，不是新的病例对照统计分析；不能从该图本身推导 marker 的普适诊断性能。

### 4. 轨迹和细胞通信：提出机制，不是直接观察机制

trajectory inference 按表达相似性把横截面细胞排序为 pseudotime。Palantir、Slingshot、scVelo 等能描述从静息到激活或分化的连续结构，但：

$$
\text{pseudotime}\neq\text{真实时间},\qquad
\text{邻近状态}\neq\text{谱系祖先后代}.
$$

综述特别谨慎地指出，体外 TGF-β1 成纤维细胞转化是否等价于体内推断的 myofibroblast 轨迹仍不确定。即使 knockout 支持候选基因影响激活，也不自动验证整条体内轨迹。

CellChat、CellPhoneDB、SingleCellSignalR 等用 ligand/receptor 表达和数据库预测通信。它们发现的是“分子条件与已知配体—受体关系相容”的候选边，并不证明蛋白已经分泌、受体活化或空间上真实接触。Litvinuková 等使用空间证据进行正交验证，正说明预测需要额外证据。

### 5. scATAC-seq：从开放染色质到候选调控关系

Tn5 更容易插入 nucleosome-free 区域，scATAC-seq 得到 fragment/peak × cell 的稀疏矩阵。心血管应用主要有两类：

1. ChromVAR 等根据 motif 在开放峰中的偏离推断 TF motif activity；
2. Cicero、ArchR Peak2Gene 或 ABC 把 distal CRE 与候选靶基因连接，并优先解释 GWAS 风险位点。

关键证据边界是：

- motif enrichment 不能区分共享相似 motif 的 TF，也不等同于 TF 蛋白活性；
- co-accessibility/peak–gene correlation 不是物理接触或因果调控；
- nearest gene 常不是靶基因，但 distal correlation 也仍需 3D chromatin、eQTL 或 CRISPR 验证。

综述引用 CAD 位点与 TBX2、PRDM16 等远端候选基因的例子，价值在于缩小候选空间，而不是宣布已确定唯一致病基因。

### 6. 真正的 multi-omics：同细胞联合测量与事后对齐不同

#### RNA + chromatin

sci-CAR、Paired-seq、SHARE-seq、SNARE-seq、ASTAR-seq 和 10x Multiome 在同一细胞或细胞核内联合读取 RNA 与 ATAC。其优势是配对关系来自实验条形码，不必先假设两个独立数据集的细胞一一对应；代价是每个模态灵敏度、成本和流程复杂度的权衡。

“同细胞配对”仍不等于开放染色质直接导致同一时刻的 RNA：调控具有时间延迟，且开放性只是转录条件之一。

#### RNA + protein

CITE-seq/REAP-seq 用 DNA-barcoded antibody 读表面蛋白；inCITE-seq/NEAT-seq 扩展到核蛋白，NEAT-seq 还联合 ATAC。它们测量的是预定义抗体 panel，不是无偏蛋白组；抗体特异性、非特异结合和组织解离造成的膜损伤仍是主要限制。

RNA 与蛋白不一致不仅是测量噪声，也来自 translation、degradation、alternative splicing 和 post-translational modification。因此蛋白模态是独立信息源，而不是简单用于“验证 RNA”。

### 7. 空间技术：补回解离丢失的组织语境

综述区分 imaging-based（MERFISH、seqFISH、in situ sequencing）与 sequencing-based（Visium、Slide-seq、DBiT-seq、Seq-Scope）路线。其共同权衡是空间分辨率、基因覆盖、检测灵敏度、面积和成本。

心肌梗死的空间多组学例子把组织分为 uninjured、transition、injured 区域，并将空间表达与单核 RNA/ATAC 结合。重要的是，空间 spot 往往包含多细胞；“某信号位于损伤区”不自动等于某一细胞类型内上调，需要 deconvolution 或更高分辨率证据。

论文发表于 2023 年，其中关于分辨率、FFPE 兼容性和商业平台的数字是当时快照，不应未经当前文档核验直接当作 2026 年采购或实验决策依据。

### 8. Cell Village 与单细胞 eQTL

图 5 的 Cell Village 将不同遗传背景的 donor/cell line 混合培养和共同测序，再用 genotype 把细胞分回 donor。这样可减少不同 donor 分批处理造成的 batch effect，并提高 population-scale QTL 的通量。

其统计设计核心不是单纯增加细胞数，而是 donor 数、每 donor 的目标 cell type 数和测序深度之间的平衡。综述引用的设计结论是：固定预算下，cell-type-specific eQTL 往往从“更多 donor、每细胞较浅”获得更高功效。但它依赖效应大小、细胞比例和 demultiplexing 质量，不是所有任务的普遍最优策略。

自然遗传变异可作为 donor barcode，但近亲、遗传差异不足、doublet 或低覆盖会降低身份判定可靠性。

### 9. CRISPR 与机器学习：从关联走向功能，但仍有边界

Perturb-seq/CROP-seq 把 sgRNA 与单细胞 RNA 输出关联，Spear-ATAC 则读染色质状态。相比纯观察数据，它们更接近因果干预；但 guide efficiency、off-target、细胞存活选择和 iPSC-CM 成熟度会影响结论外推。

综述列举 VAE、NMF、optimal transport、batch correction 和跨模态 alignment。算法应按问题选择：

- VAE 适合非线性低维表示和 count likelihood；
- LIGER/NMF 便于分离 shared 与 dataset-specific factor；
- SCOT 用 optimal transport 对齐无配对模态；
- Waddington-OT 需要时间序列分布来推断群体转移。

低维空间中的漂亮混合不能单独证明整合正确；应检查 marker 保留、batch removal、rare state、donor 泛化和已知生物学是否同时成立。

### 10. 面向心血管问题的方法选择

| 科学问题 | 优先方法 | 关键补充/风险 |
|---|---|---|
| 冷冻成人心脏细胞图谱 | snRNA-seq | 用 scRNA 或空间方法补免疫/胞质偏差 |
| 新鲜组织免疫生态 | scRNA-seq | 记录解离应激与难回收心肌细胞 |
| CAD 风险位点到细胞类型 | scATAC + eQTL/ABC | motif、Peak2Gene 需功能验证 |
| 同细胞调控—表达耦合 | RNA+ATAC multiome | 接受每模态深度下降和时间延迟 |
| 表面状态与转录 | CITE-seq | 靶向 panel、抗体和膜完整性限制 |
| 心梗区域结构 | 空间转录组 + 单细胞参考 | spot mixture 与 deconvolution 不确定性 |
| 发育/激活过程 | 时间采样 + trajectory/OT | 横截面 pseudotime 不等于谱系 |
| 基因功能 | Perturb-seq/CROP-seq | guide 和体外模型外推边界 |
| population eQTL | pooled donors/Cell Village | donor 数优先，严格 genotype demultiplexing |

### 11. 这篇综述没有充分覆盖什么

原文对 spatial deconvolution、single-cell methylome、3D genome、无偏质谱单细胞蛋白组和 CRISPRa/base-editing 等覆盖有限或未覆盖；对 multi-omics benchmark、批次校正过度整合和 donor-level validation 也缺少系统比较。因此它适合作为截至 2022 年的技术地图和心血管案例入口，不是当前方法性能排行榜。

### 证据入口

- 全文：`paper source/paper/vlm/paper.md`
- 图 1、2、3、5：`paper source/paper/vlm/images/`
- 图 4：本地 `paper.pdf` 第 8 页（OCR 未单独抽图，已直接目视核对）
- 方法分类：`doc_method.md`
- 综述综合：`summary.md`
- 深读笔记：`reading_notes.md`
- 图表核对：`figure_analysis.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Current and Future Perspectives of Single-Cell Multi-Omics Technologies in Cardiovascular Research

**DOI**: 10.1038/s44161-022-00205-7
**Journal**: Nature Cardiovascular Research
**Year**: 2023
**Authors**: Wilson Lek Wen Tan, Wei Qiang Seow, Angela Zhang, Siyeon Rhee, Wing H. Wong, William J. Greenleaf, Joseph C. Wu (Stanford)

---

### Review Scope

- **Topic**: Single-cell and single-cell multi-omics technologies applied to cardiovascular research
- **Time period**: 2009 (first scRNA-seq) through 2022
- **Methods reviewed**: ~50+ experimental technologies + ~30 computational tools
- **Target audience**: Cardiovascular researchers adopting single-cell methods; computational biologists entering the cardiac field
- **Scope**: Experimental platforms (capture, library prep), computational analysis pipelines, cardiovascular applications (heart failure, atherosclerosis, development), and future directions

---

### Field Landscape

Single-cell RNA sequencing was first described in 2009 (Tang et al.). The field evolved from profiling hundreds of cells (C1 Fluidigm, Smart-seq2) to tens of thousands (10x Chromium, 2016) to millions (sci-RNA-seq3, 2019). Cardiovascular research adopted scRNA-seq to overcome the "averaging effect" of bulk RNA-seq, which masked heterogeneous cell populations in complex cardiac tissue.

Key turning points:
- **2015**: scATAC-seq introduced chromatin accessibility at single-cell resolution
- **2017**: CITE-seq enabled simultaneous protein + RNA profiling
- **2018–2020**: Multi-omics joint profiling (sciCAR, SNARE-seq, SHARE-seq, 10x Multiome)
- **2019**: Spatial transcriptomics (Visium, Slide-seq) added spatial context
- **2020–2022**: Large-scale human cardiac atlases (Litvinuková, Tucker, Koenig, Chaffin, Reichart)
- **2022**: Spatial multi-omics of myocardial infarction (Kuppe et al.)

---

### Method Taxonomy

#### Dimension 1: Capture Strategy
| Strategy | Examples | Throughput | Sensitivity |
|---|---|---|---|
| Microfluidic droplet | 10x Chromium, C1 Fluidigm | 10K–100K cells | High (~2,000–5,000 genes/cell) |
| Combinatorial indexing | sci-RNA-seq3, SPLiT-seq | 100K–millions | Low (~25% of 10x) |
| Hybrid | dsciATAC-seq | High | Improved |

#### Dimension 2: Omics Layer
| Layer | Key Methods | Cardiovascular Application |
|---|---|---|
| Transcriptome | scRNA-seq, snRNA-seq | Cell-type atlas, disease states |
| Epigenome | scATAC-seq, sci-ATAC-seq | TF inference, CRE mapping, GWAS |
| Proteome | CITE-seq, REAP-seq, NEAT-seq | Surface/nuclear protein quantification |
| Spatial | Visium, MERFISH, Seq-Scope | Tissue architecture, MI zones |
| Multi-omics | 10x Multiome, SHARE-seq, NEAT-seq | Regulatory-expression coupling |
| Perturbation | Perturb-seq, CROP-seq, Spear-ATAC | Gene function screens |

#### Dimension 3: Cardiovascular Application
- Cell-type clustering & atlas construction
- Disease gene expression perturbation (HCM, DCM, MI, atherosclerosis)
- Intercellular cross-talk (CellChat, CellPhoneDB)
- Trajectory inference (Monocle3, Palantir, scVelo)
- TF activity inference (ChromVAR)
- CRE mapping & GWAS variant prioritization (Cicero, ArchR Peak2Gene)
- Single-cell eQTL (pooled experiment design)
- ML-based analysis (autoencoders, optimal transport)
- CRISPR screens (Perturb-seq, CROP-seq)

---

### Key Findings

1. **snRNA-seq vs scRNA-seq complementarity**: snRNA-seq is necessary for cardiomyocytes and other fragile cell types, but scRNA-seq captures immune cells (monocytes, intermediate macrophages) better. Both are needed for complete cardiac cell-type coverage.

2. **Large-scale cardiac atlases**: Studies of 79–881K cells/nuclei from 5–79 donors have established reference landscapes for healthy and diseased human hearts (HCM, DCM, MI, atherosclerosis).

3. **Fibroblast heterogeneity in disease**: Activated fibroblasts (POSTN+, NOX4+, COL1A1+) are a major disease-associated population in HCM/DCM. Genotype-specific fibroblast programs exist (LMNA vs TTN vs PKP2-DCM).

4. **scATAC-seq reveals TF regulatory grammar**: Cell-type-specific TF motifs (MEF2A/NKX2-5 in cardiomyocytes, TCF21 in fibroblasts) are conserved across species. SMC-to-fibromocyte transdifferentiation in atherosclerosis is accompanied by TF motif switching.

5. **GWAS variant prioritization**: scATAC-seq enables cell-type-specific mapping of CAD GWAS variants to CREs. Peak2Gene links variants to distal target genes (e.g., PRDM16, TBX2) rather than nearest genes.

6. **Spatial multi-omics of MI**: Three-zone pattern (uninjured, transition, injured) with distinct cardiomyocyte subtypes; TGF signaling enriched at injury site; hypoxia pathway evenly distributed.

7. **Single-cell eQTL**: Cell-type-specific eQTLs are missed by bulk RNA-seq. Pooled experiment design (Cell Village) enables population-scale studies. Statistical power optimized by sequencing more samples at lower depth per cell.

---

### Open Problems

1. **Heart tissue dissociation**: Cardiomyocytes and other cell types are damaged by enzymatic dissociation, forcing reliance on snRNA-seq with its cytoplasmic RNA bias. No universal solution exists.

2. **Alternative splicing and RNA diversity**: Short-read scRNA-seq cannot capture full-length transcripts, alternative splicing isoforms, or poly-A-negative lncRNAs. Long-read integration (Nanopore, PacBio) is needed but expensive.

3. **Protein-mRNA discordance**: Up to 95% of multi-exon genes undergo alternative splicing; proteins undergo post-translational modifications invisible to transcriptomics. Multi-omics proteomics (CITE-seq, NEAT-seq) is needed but technically challenging for solid tissues.

4. **Spatial resolution vs. sensitivity trade-off**: High-resolution methods (Seq-Scope: 0.6 μm) sacrifice sensitivity; NGS-based methods (Visium) have lower resolution (~55 μm spots). Optimal balance not yet achieved.

5. **Single-cell eQTL scaling**: Requires hundreds of donors for statistical power. Pooled designs help but introduce demultiplexing complexity.

6. **CRISPR screen optimization for cardiac cells**: iPSC-CM differentiation adds complexity; guide RNA delivery efficiency and off-target effects require careful optimization.

---

### Method Comparison Table

| Method | Year | Journal | Category | Key Innovation | Limitations | Data Types |
|---|---|---|---|---|---|---|
| 10x Chromium scRNA-seq | 2016 | Nat Protoc | Transcriptomics | ~$0.04/cell, 10K–100K cells | Requires fresh single-cell suspension | RNA |
| C1 Fluidigm | 2014 | Nat Methods | Transcriptomics | IFC chip, microscopy-compatible | Low throughput (~800 cells) | RNA |
| sci-RNA-seq3 | 2019 | Nature | Transcriptomics | Millions of cells, no FACS | ~25% gene detection vs 10x | RNA |
| SPLiT-seq | 2018 | Science | Transcriptomics | Split-pool, no specialized equipment | Low sensitivity | RNA |
| snRNA-seq | 2018+ | Various | Transcriptomics | Works on frozen/fixed tissue | Cytoplasmic RNA bias | RNA (nuclear) |
| scATAC-seq (10x) | 2015 | Nature | Epigenomics | Chromatin accessibility, Tn5 tagmentation | Sparse signal per cell | ATAC |
| sci-ATAC-seq3 | 2020 | Science | Epigenomics | Millions of nuclei, ligation-based indexing | Complex protocol | ATAC |
| dsciATAC-seq | 2019 | Nat Biotechnol | Epigenomics | Droplet + combinatorial hybrid | Complex | ATAC |
| sciCAR | 2018 | Science | Multi-omics | Joint RNA+ATAC, plate-based | Lower sensitivity | RNA + ATAC |
| Paired-seq | 2019 | Nat Struct Mol Biol | Multi-omics | Avoids DNA/RNA heteroduplexes | Complex | RNA + ATAC |
| SHARE-seq | 2020 | Cell | Multi-omics | Both ATAC ends sequenced | Complex | RNA + ATAC |
| 10x Multiome GEX+ATAC | 2021 | Cell | Multi-omics | Commercial, easy workflow | Cost | RNA + ATAC |
| CITE-seq | 2017 | Nat Methods | Proteomics | Hundreds of proteins via DNA-barcoded antibodies | Nonspecific binding in solid tissue | RNA + protein |
| REAP-seq | 2017 | Nat Biotechnol | Proteomics | DNA-labeled antibodies + droplet | Same as CITE-seq | RNA + protein |
| inCITE-seq | 2021 | Nat Methods | Proteomics | Intranuclear proteins, lightly fixed | Limited to nuclear proteins | RNA + nuclear protein |
| NEAT-seq | 2022 | Nat Methods | Proteomics | Nuclear protein + ATAC + RNA | Moderate nonspecific binding improvement | RNA + ATAC + nuclear protein |
| PLAYR | 2016 | Nat Methods | Proteomics | Mass cytometry, RNA + protein | Limited by metal isotope tags | RNA + protein |
| 10x Visium | 2019+ | Various | Spatial | NGS-based, paraffin-compatible | ~55 μm resolution, not single-cell | Spatial RNA |
| Slide-seq | 2019 | Science | Spatial | 10 μm resolution | Lower sensitivity | Spatial RNA |
| DBiT-seq | 2020 | Cell | Spatial | Deterministic barcoding | Complex | Spatial RNA + protein |
| Seq-Scope | 2021 | Cell | Spatial | 0.6 μm resolution | Sensitivity trade-off | Spatial RNA |
| MERFISH | 2015 | Science | Spatial | ~10,000 genes, imaging-based | Requires specialized equipment | Spatial RNA |
| seqFISH | 2019 | Nature | Spatial | ~10,000 genes, subcellular | Requires specialized equipment | Spatial RNA |
| Perturb-seq | 2016 | Cell | CRISPR+scRNA | Genome-scale CRISPR + scRNA readout | Requires optimization | RNA + perturbation |
| CROP-seq | 2017 | Nat Methods | CRISPR+scRNA | Droplet-based CRISPR screen | Same | RNA + perturbation |
| Spear-ATAC | 2021 | Nat Methods | CRISPR+ATAC | Perturb + scATAC-seq | Same | ATAC + perturbation |
| scVI | 2018 | Nat Commun | ML/DL | VAE for scRNA-seq, scalable | Black-box | RNA |
| DCA | 2019 | Nat Commun | ML/DL | Deep count autoencoder, denoising | Requires training | RNA |
| SAUCIE | 2019 | Nat Methods | ML/DL | Multitask: clustering+batch+imputation | Complex | RNA |
| BERMUDA | 2019 | Genome Biol | ML/DL | Transfer learning batch correction | Requires paired clusters | RNA |
| LIGER | 2020 | Nat Protoc | Integration | NMF, shared + dataset-specific factors | Hyperparameter sensitivity | RNA/multi-omics |
| SCOT | 2020 | J Comput Biol | Integration | Optimal transport, geometry-preserving | Scalability | Multi-omics |
| Waddington-OT | 2019 | Cell | Trajectory | OT for reprogramming trajectories | Requires time-course data | RNA |
| CellChat | 2021 | Nat Commun | Cell-cell comm | Statistical ligand-receptor inference | Relies on curated database | RNA |
| CellPhoneDB | 2020 | Nat Protoc | Cell-cell comm | Multi-subunit complex interactions | Same | RNA |
| Cicero | 2018 | Mol Cell | CRE mapping | Co-accessible CRE prediction | Correlation ≠ causation | ATAC |
| ChromVAR | 2017 | Nat Methods | TF inference | TF motif enrichment from ATAC | Motif ≠ TF activity | ATAC |
| ArchR Peak2Gene | 2021 | Nat Genet | CRE mapping | CRE-gene links from scATAC | Correlation-based | ATAC |

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
