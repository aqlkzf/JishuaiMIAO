---
layout: default
permalink: /paper-atlas/wemerfish-2cb4c113/
title: "weMERFISH"
nav: false
description: "weMERFISH 不是“直接测完整转录组”的成像技术。它先在完整斑马鱼胚胎中直接定位 495 个目标基因的单个 RNA 分子，再以这些实测基因为共同坐标，把同阶段单细胞 multiome 数据中的其余 RNA 和 ATAC 特征映射到空间。因而，495 个基因是直接成像证据，25,872 个基因和 294,954 个染色质区域是模型推断结果，两者不能混称为实测。"
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
      <span>Science · 2026</span>
    </div>
    <h1>weMERFISH</h1>
    <p>Whole-embryo spatial transcriptomics at subcellular resolution from gastrulation to organogenesis</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1126/science.adt3439" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## weMERFISH：从整胚单分子成像到空间多组学图谱

### 一句话理解

weMERFISH 不是“直接测完整转录组”的成像技术。它先在完整斑马鱼胚胎中直接定位 495 个目标基因的单个 RNA 分子，再以这些实测基因为共同坐标，把同阶段单细胞 multiome 数据中的其余 RNA 和 ATAC 特征映射到空间。因而，**495 个基因是直接成像证据，25,872 个基因和 294,954 个染色质区域是模型推断结果**，两者不能混称为实测。

### 1. 为什么要做整胚 MERFISH

胚胎发育同时改变细胞身份、位置和形态。切片型空间组学会打断三维几何；单细胞测序保留分子谱，却丢失原位位置；传统原位杂交又难以在同一胚胎中同时观察数百个基因。论文因此选择 50% epiboly、75% epiboly 和 6-somite 三个阶段，在完整胚胎尺度上追踪从原肠运动到早期器官发生的空间变化。

### 2. 三项实验改造

#### 2.1 把一级探针固定在凝胶中

一级 DNA 探针带 acrydite 修饰，杂交到 RNA 后共价接入覆盖胚胎的聚丙烯酰胺凝胶。RNA 后续即使降解，探针所标记的位置仍被凝胶保存。论文报告样品可稳定超过一个月，并可用 80% 至 100% formamide 去除荧光探针，支持 60 轮以上反复成像。

#### 2.2 把“识别基因”和“编码条形码”拆开

一级探针携带基因特异 readout 序列；可更换的 linker 探针再把这些序列接入 MERFISH 组合编码。因此，同一一级探针库既能按单基因 smFISH 读取，也能按组合条形码 MERFISH 读取，避免每次改变编码方案都重做整套一级探针。

#### 2.3 两级分支放大

厚胚胎的共聚焦成像信号较弱。两级分支结构为每个目标招募更多荧光分子，论文测得约三倍信号增强。这是湿实验放大；代码中的 Wiener 去卷积是后续图像处理，不能作为该化学放大本身的证据。

### 3. 495 个实测基因如何读出

探针集合包含 217 个转录因子、191 个形态发生相关基因和 59 个成熟细胞或细胞周期标志物；这些类别允许重叠。471 个基因进入 80-bit 码本，在 40 个杂交轮次、两个荧光通道中组合读取。另有 24 个高表达基因为避免分子拥挤，改用 12 轮顺序 smFISH。两部分合计 495 个直接测量基因。

论文用同一基因的 smFISH 与 MERFISH 结果交叉验证：*myod1* 和 *tbxta* 的逐细胞相关分别为 $R^2=0.924$ 和 $R^2=0.890$；独立胚胎间各基因总转录本数的相关为 $R=0.996$。这说明平台在所选基因上的定量一致性较好，但不是对全部推断基因的逐基因验证。

### 4. 从多轮图像到细胞乘基因矩阵

主代码位于 `weMERFISH/2ImageProcessing/MERFISH_PIPELINE.ipynb` 和 `ioMicro.py`。实际数据流是：

1. 读取多视野、多 z 层的 Nikon ND2 图像，以 DAPI 结构拼接视野并估计各轮漂移。
2. 对每轮信号做背景校正和去卷积，检测局部亮点。
3. 把不同轮次的亮点聚合成候选分子，与 80-bit 码本比较。代码先用较宽距离阈值解码，估计 z 方向畸变，再估计三维空间畸变，最后以更严格阈值重新解码。
4. 用核与膜信号进行三维细胞分割；表层 EVL 另作处理。每个 RNA 坐标再通过分割标签分配到细胞，并记录是否位于细胞核、距膜的三维和逐层二维距离。
5. 合并 471 个组合编码基因与 24 个顺序读取基因，形成细胞乘 495 基因计数矩阵，同时保留单分子坐标。

`ioMicro.py` 中的 `decoder`、`compute_drift_jakob`、`get_XH`、`load_library_v2` 和 `get_counts_per_cell` 分别对应漂移、坐标校正、码本组织和细胞归属等关键环节。代码使用研究现场的绝对 Windows/网络路径，且主要流程存在于 notebook 中；公开仓库因此是可核查的研究代码，而不是无需配置即可从原始数据一键运行的软件包。

### 5. 从 495 个基因定义空间细胞状态

每个阶段的两个胚胎分别处理后再对齐。代码按分割得到的细胞体积归一化，而不是仅按总 UMI 数归一化；随后进行 PCA、邻居图、UMAP 和 Leiden 聚类，并结合已知标志物及参考数据注释。论文在 6-somite 阶段报告 51 种空间细胞类型或状态；代码中的更多 Leiden 原始簇会合并到这些生物学标签，不能把原始簇数直接当作最终细胞类型数。

### 6. Tangram 如何生成空间“预测层”

Tangram 用 495 个面板基因中与 scMultiome 共有的基因比较两类细胞。设 $S_{ig}$ 为 multiome 细胞 $i$ 对基因 $g$ 的表达，$M_{jg}$ 为 weMERFISH 细胞 $j$ 的实测表达，模型学习非负映射权重 $P_{ij}$，使映射后的参考表达

$$
\hat M_{jg}=\sum_i P_{ij}S_{ig}
$$

尽量接近空间实测矩阵。主 notebook 调用 `tg.map_cells_to_space(..., mode="cells", density_prior="uniform")`，再用 `tg.project_genes()` 投射参考数据中的其他基因。得到的 25,872 个基因模式因此依赖共同基因、阶段匹配、批次差异和映射假设，不等同于 25,872 个基因都被原位成像。

同一批 scMultiome 细胞同时具有 RNA 和 ATAC 信息，学习到的 RNA 空间对应关系可进一步转移其 ATAC 表征，生成 294,954 个区域的空间可及性预测。RNA 是两种模态之间的桥梁；若某细胞状态在参考数据中缺失或表达相近，RNA 与 ATAC 的空间投射都会继承这一不确定性。

### 7. 论文如何使用图谱

- 直接测量与空间注释显示，基因常在多个相关组织表达，而细胞的组合表达提供更强位置识别能力。
- 预测 ATAC 图谱用于寻找组织特异或多个相关组织共享的候选调控元件；论文报告 128,338 个峰与 H3K4me1 信号重叠，73,036 个峰在 embryo proper 中富集。这里是关联和候选调控证据，不是增强子功能的直接扰动验证。
- 伪时间和 RNA velocity 把表达变化与细胞成熟、迁移方向联系起来。代码以核 RNA 近似 unspliced、总量减核量近似 spliced；所得箭头是动力学推断，不是活细胞轨迹。
- MERFISH-FATE 把固定胚胎的空间转录组与独立的整胚活体追踪数据做区域对应，区分维持、激活、抑制和混合变化。它不是对同一个被追踪细胞随后进行 MERFISH 测量。
- 组织边界分析显示，尖锐边界主要由局部表达状态改变形成，而不是依靠大量细胞跨边界排序。

### 8. 图应该怎样读

Fig. 1 是从化学设计、整胚成像到定量验证的证据链；Figs. 2–3 展示实测表达和空间细胞类型；中间几幅图把实测层与 multiome 推断层连接起来；后两幅图讨论 MERFISH-FATE 与边界形成。工作区的最终编号以 Science 正文和图注为准；视觉复核使用公开预印本 PDF，其中后半部分版式与最终论文重新编排，预印本 Fig. 7 对应最终论文 Figs. 7–8。

### 9. 三个代码仓库各自负责什么

| 本地目录 | 上游仓库 | 作用 |
|---|---|---|
| `weMERFISH/` | `yinan-wan0/weMERFISH` | 主方法：探针设计、图像处理、细胞注释、Tangram RNA/ATAC 映射 |
| `sc-schier-merfisheyes/` | `kresnajenie/sc-schier-merfisheyes` | 单细胞多模态 MERFISHEYES 三维浏览器 |
| `sm-merfisheyes-wi/` | `Bogdan-Bintu-Lab/sm-merfisheyes-wi` | 单分子空间浏览器，依赖外部对象存储数据 |

浏览器仓库是数据展示层，不能作为主实验与分析算法的 `code source`。本工作区现以 `weMERFISH/` 为主代码目录，并把另外两个仓库记录为附加可视化实现。

### 10. 可复现边界

公开代码能核查码本、漂移校正、解码、分割、细胞注释与 multiome 映射的主要实现，但尚不足以无条件重现整篇论文：原始 ND2 数据和专用成像条件体量大；notebook 含绝对路径和预计算中间文件；仓库没有统一环境锁定与自动测试；MERFISH-FATE 配准、CellChat 以及部分最终作图/统计代码未在主仓库中定位到。因此最稳妥的结论是：核心计算路径有直接代码对应，端到端复现仍需作者数据、环境整理和缺失分析步骤。

### 证据边界

本文依据工作区 `paper.md` 的 Science 正文与图注、公开预印本 PDF 的逐图视觉复核，以及上述三个固定提交的本地代码。论文陈述、代码实现、视觉观察和推断结果在文中分开标注；未在公开代码中找到的步骤不按“已复现”处理。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## weMERFISH — Summary

### Motivation & Novelty

**Biological problem**: Vertebrate embryonic development is orchestrated by thousands of genes whose precise spatiotemporal expression patterns determine tissue identity, cell fate, and organ morphogenesis. Understanding these patterns requires measuring many genes simultaneously with subcellular resolution across entire embryos in 3D — capturing not just which genes are expressed, but where in the embryo, where within the cell, how patterns change over time, and what chromatin elements control them. This was technically impossible before weMERFISH.

**Why existing methods fell short**:

- **Sequencing-based spatial transcriptomics** (Tomo-seq, *Nature Methods* 2014; Stereo-seq, *Cell* 2022): covers the full transcriptome in principle, but with low per-cell capture (<10%), poor spatial resolution (not single-cell), and requires serial sectioning for 3D reconstruction — destroying the embryo and losing z-information.
- **2D MERFISH / seqFISH+** (*Nature* 2019 seqFISH+, standard MERFISH platforms): provides subcellular resolution and >50% capture efficiency, but restricted to 2D tissue sections, so incompatible with 3D whole-embryo imaging at scales of hundreds of micrometers.
- **3D MERFISH** (Bintu lab, *Science* 2023): extended MERFISH to thick (up to ~120 μm) samples using spinning disk confocal, but lacked signal amplification for deeper tissues, had no flexible codebook design, and was not applied to whole embryos.
- **cycleHCR** (*Nature Methods* 2022): multiplexed in situ hybridization for 3D samples, but limited number of genes in fewer rounds; not MERFISH-level multiplexing.
- **Classic in situ hybridization databases** (ZFIN, *Zebrafish Information Network*): one gene per experiment, not co-registered across genes, cannot reveal combinatorial expression.
- **Computational mapping** (Tomo-seq→MERFISH, Daniocell 2024 *Nature*): maps scRNA-seq onto sparse spatial references, but low spatial resolution reference limits positional accuracy.

**Unique contributions of weMERFISH**:
1. First whole-embryo (3D) MERFISH platform — images entire 120-200 μm thick zebrafish embryos at subcellular resolution.
2. Three key innovations over prior MERFISH: (a) probe anchoring via acrydite-polyacrylamide gel (60+ round stability), (b) codebook flexibility via gene-specific linker probes (switch between smFISH and MERFISH without reordering probes), (c) two-level branching DNA signal amplification (3× signal increase for deep-tissue imaging).
3. First genome-wide spatial atlas combining spatial transcriptomics + scMultiome imputation + ATAC accessibility at embryo scale.
4. MERFISH-FATE: first integration of whole-embryo in vivo cell tracking with multiplexed spatial transcriptomics to reveal gene expression dynamics during morphogenesis.

---

### Method Overview

**Platform**: weMERFISH images zebrafish embryos at three developmental stages (50% epiboly, 75% epiboly, 6-somite stage) using MERFISH with spinning disk confocal.

**Experimental pipeline**:
- 495 genes targeted: 471 via 80-bit MERFISH (40 hybridization rounds, 2 fluorescence channels), 24 highly expressed genes via sequential smFISH (12 rounds).
- Primary probes carry an acrydite group for covalent crosslinking into polyacrylamide gel + gene-specific readout sequences used by linker probes for combinatorial coding.
- Signal amplification: 2-level branching DNA tree achieves 3× signal increase, enabling single-molecule detection through 200 μm of cleared tissue.
- 40 rounds of hybridization–image–strip cycles per embryo; final round uses membrane + DAPI staining for 3D cell segmentation.

**Image processing**:
- Tile stitching: cross-correlation of DAPI z-stacks across field-of-view grid.
- Drift correction: DAPI nuclear feature matching across rounds.
- Background correction → Wiener deconvolution → local maxima detection with 3D Gaussian fitting.
- Two-pass MERFISH decoding with iterative Z-distortion then XYZ-distortion correction (accounts for optical aberrations in thick tissue).

**Cell segmentation**: Cellpose cyto2 deep learning model on DAPI + membrane channels; EVL surface cells handled separately using *krt4* expression. Per-cell 3D Euclidean Distance Transform computes subcellular membrane distance for every transcript.

**Genome-wide imputation**: Tangram (mode="cells", uniform prior) maps scMultiome cells (simultaneous scRNA-seq + scATAC-seq) to MERFISH spatial grid using shared 495 genes as anchors, then projects 25,872 RNA genes and 294,954 ATAC peaks into spatial context.

**Evidence boundary**: only the 495-gene panel is directly imaged. The 25,872-gene expression atlas and 294,954-region accessibility atlas are Tangram-derived spatial predictions; their validity depends on shared genes, stage matching, reference coverage, and batch effects.

**Cell type annotation**: Leiden clustering (resolution=5) of volume-normalized expression followed by correlation to URD pseudotime cell states and manual curation → 51 annotated cell types at 6-somite stage.

**MERFISHEYES**: online atlas (https://schier.merfisheyes.com) allows interactive 3D visualization of all 25,872 imputed gene expression patterns and ATAC accessibility at all three stages.

The main method code is in `weMERFISH/`. The local `sc-schier-merfisheyes/` and `sm-merfisheyes-wi/` directories are two separate viewer implementations and must not be treated as the primary analysis pipeline.

**MERFISH-FATE**: integrates MERFISH spatial data with whole-embryo live-imaging cell tracking (light-sheet microscopy) by geometric registration of embryo positions across stages, enabling tracking of transcriptional changes during gastrulation.

---

### Evaluation

**Platform validation** (Figure 1):
- smFISH vs MERFISH per-cell correlation: R² = 0.924 (*myod1*), R² = 0.890 (*tbxta*); slope ~0.55-0.60 (50-60% recovery).
- Inter-replicate reproducibility: log-log R = 0.996 for total transcript counts per gene.
- False positive rate: <1 transcript/gene/cell (blank barcode + correlation filter).
- Spatial domain boundaries reproducible to within 20-30 μm (1-2 cell diameters) between replicate embryos.

**Cell type resolution** (Figure 3):
- 51 distinct cell types at 6-somite stage; at 50% and 75% epiboly, 15-30 cell clusters.
- Spatial information resolves sub-clusters invisible in scRNA-seq: adaxial cells split into 3 spatial subtypes; tailbud into 4 progenitor zones; hindbrain into individual rhombomeres (R1-R7).
- ~3% variation in cell number per cluster between replicate embryos.

**Genome-wide imputation accuracy** (Section 6, figs S12-S17):
- Tangram outperformed other imputation methods (figs S12-S14).
- Comparison against 105 ZFIN in situ hybridization images: high concordance for both measured (MERFISH) and imputed genes (figs S15-S16).
- Reduced accuracy for low-expression/low-variability genes (fig S17).

**Chromatin accessibility** (Figure 5):
- 128,338 of 294,954 ATAC peaks overlap H3K4me1 ChIP-seq peaks (active/primed enhancers).
- For 48 genes co-expressed in notochord and prechordal plate: ~70-80% of nearby ATAC peaks tissue-specific → supports combinatorial dedicated-enhancer model.

**MERFISH-FATE** (Figures 7-8):
- *tbxta* shown to be a composite of suppression (old margin cells) and activation (new margin cells) — not maintained, as static snapshots suggest.
- Notochord-somite boundary: <4% of cells cross between the two progenitor populations; sharp gene expression boundary (transition within 30 μm) emerges through transcriptional change, not cell sorting.
- Lineage restriction (≤5/56 mixed lineages) precedes molecular boundary at sphere stage.

---

### Reproducibility Rating: 3/5

**Rationale**: The data and platform are impressively characterized and publicly available, but full reproduction of the complete pipeline requires specialized equipment and expertise.

**Positive factors**:
- All image processing code released at https://github.com/yinan-wan0/weMERFISH (archived Zenodo).
- Processed data (cell-level expression, spatial coordinates, ATAC accessibility) available on Dryad.
- MERFISHEYES browser provides interactive access to the atlas without needing to run any code.
- Three web tools released (MERFISHEYES, sm-MERFISHEYES, sc-MERFISHEYES).
- All analysis steps in documented Jupyter notebooks with actual outputs shown.

**Limiting factors**:
- No `requirements.txt` or `pyproject.toml` — dependency versions must be inferred from notebook imports.
- All code in Windows-path notebooks (hardcoded paths like `U:\Scientific Data\...`); direct re-execution requires path updates.
- Raw image data (terabytes of .nd2 files) not deposited — full pipeline reproduction requires re-imaging.
- Probe library design requires purchasing custom oligos (~495 × 30 probes each + linker probes).
- The branching amplification oligos are custom-synthesized — not commercially available off-shelf.
- MERFISH-FATE live-imaging registration code not in main repo.
- CellChat analysis code not in main repo.
- Pre-computed background models (cy3_bM.npz, cy5_bM.npz) and PSF (psf_cy5.npy) are instrument-specific — labs with different microscopes must measure their own.

**Practical notes**:
- To reproduce the analysis from processed data: straightforward using the annotation notebooks + Tangram.
- To reproduce from raw images: requires Nikon .nd2 files and updating hardcoded Windows paths.
- The `seqint.pyx` Cython extension must be recompiled on Linux (instructions in README).
- Cellpose cyto2 model is widely available and GPU-accelerated; segmentation step should be portable.
- Recommend starting with the Dryad data deposit + annotation notebooks for the most accessible entry point.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
