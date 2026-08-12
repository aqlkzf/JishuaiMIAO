---
layout: default
permalink: /paper-atlas/in-depth-3114145d/
title: "IN-DEPTH"
nav: false
description: "IN-DEPTH（IN-situ DEtailed Phenotyping To High-resolution transcriptomics）不是一种新的测序仪，而是一套“先在同一张 FFPE 切片上做高通量空间蛋白成像，再在原切片上做空间转录组”的实验与分析框架。它首先用蛋白标记确定细胞身份和组织结构，再把这些空间信息传递给 GeoMx、Visium HD、CosMx 或 Xenium 等转录组平台；"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Cancer Discovery · 2025</span>
    </div>
    <h1>IN-DEPTH</h1>
    <p>Same-Slide Spatial Multi-Omics Integration with IN-DEPTH Reveals Tumor Virus-Linked Spatial Reorganization of the Tumor Microenvironment</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1158/2159-8290.CD-25-0775" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## IN-DEPTH 中文方法解读：从同片蛋白—RNA测量到空间协同分析

### 一句话抓住方法

IN-DEPTH（IN-situ DEtailed Phenotyping To High-resolution transcriptomics）不是一种新的测序仪，而是一套“先在同一张 FFPE 切片上做高通量空间蛋白成像，再在原切片上做空间转录组”的实验与分析框架。它首先用蛋白标记确定细胞身份和组织结构，再把这些空间信息传递给 GeoMx、Visium HD、CosMx 或 Xenium 等转录组平台；随后用 SGCC（Spectral Graph Cross-Correlation，谱图交叉相关）量化两类细胞在不同空间尺度上的协同分布，并把这种空间排序与基因表达和通路变化联系起来。

这里应把两个层次分开：IN-DEPTH 的实验贡献是“同片、蛋白优先”的多模态测量；SGCC 的计算贡献是“把细胞空间图案编码到图频域，再比较两个图案的协同变化”。前者减少相邻切片带来的组织错位，后者回答哪些细胞群在全局组织区室或局部邻域中共同出现。

### 为什么必须蛋白优先

多数高通量空间 RNA 流程包含蛋白酶处理。若先做 RNA，再回头做抗体染色，蛋白表位和信号会明显受损。IN-DEPTH 将顺序反过来：先完成抗体染色、循环成像和细胞表型判定，再拆除流动池并光漂白，最后进入 RNA 探针杂交和捕获。论文用相邻切片的 RNA-only 流程作对照，报告多数平台组合的基因表达相关性超过 0.94；Orion–GeoMx 是明显例外（约 0.692）。反向的 Xenium→CODEX 实验则显示蛋白信号损失，支持“蛋白优先”是方法成立的关键，而不是可任意交换的步骤。

实验起点是 FFPE 切片的标准化抗原修复：pH 9 条件下约 97°C、20 分钟。之后根据平台完成 CODEX、SignalStar、Polaris 或 Orion 蛋白成像；作者还测试了长达 60 个循环的成像。完成蛋白图像后，组织经历流动池移除和约一小时光漂白，再进入下游空间转录组。图 1A 从左到右画出的正是四步逻辑：高通量蛋白成像、同片 RNA 探针、跨平台图像配准、多模态与 SGCC 分析。

### 从原始图像到可联合分析的数据

#### 1. 蛋白图像给出细胞身份和空间几何

循环成像得到多通道蛋白图。经过拼接、背景校正、分割和表型注释后，每个细胞拥有坐标、轮廓、蛋白强度和细胞类型。蛋白层因而不只是验证 RNA 的辅助数据：在 GeoMx 场景中，它直接指导 ROI 和细胞类型特异掩膜；在 CosMx、Xenium 等单细胞场景中，它又提供细胞边界与蛋白表型，用于和转录本归属对齐。

#### 2. 同片不等于天然同坐标，仍需配准

切片虽然相同，但拆装流动池、重复成像和平台坐标系变化仍会造成旋转、平移、缩放及局部形变。代码中的 tonsil 和 DLBCL 配准脚本使用 SIFT 提取关键点，以 KNN 匹配配合 Lowe 比率阈值 0.7 筛选对应点，再用 `estimateAffinePartial2D` 估计仿射变换并保存正、逆矩阵。随后蛋白图像和细胞类型掩膜被变换到 GeoMx 坐标系。补充表 13 汇总了 SIFT 参数。

这一点也界定了“同片”的真实含义：它消除了相邻切片在细胞组成上的不可恢复差异，但并不消除跨仪器图像配准。最终质量仍依赖共同形态特征、匹配点和人工检查。

#### 3. 转录组提供功能状态

GeoMx 给出 ROI 或细胞类型掩膜层面的全转录组信号，CosMx/Xenium 给出单细胞或近单细胞转录本。IN-DEPTH 因而把“蛋白层可靠的细胞身份和空间位置”与“RNA 层更丰富的功能程序”连接起来。图 2 用 tonsil 展示了这一用途：蛋白图定义 T、B、髓系和内皮细胞，RNA 层验证细胞类型基因程序，并以同片细胞计数作为四种去卷积方法的参照。

### SGCC 到底在算什么

#### 1. 将不规则组织变成图信号

先把组织划为规则空间 bin，或在单细胞分析中用滑动窗口汇总邻域。每个 bin 是图的一个节点，相邻 bin 之间连边。对某一细胞类型，节点值可以是该 bin 内的细胞数、比例或平滑后的丰度，于是得到图信号 $x$；另一细胞类型得到 $y$。

普通 Pearson 相关只比较同一位置的数值，不知道两个位置在组织图上是否相邻，也无法区分“大尺度共同占据同一组织区室”和“小尺度紧邻”。SGCC 先利用图拉普拉斯矩阵的特征向量，把空间信号投影到图傅里叶域：

$$
L=U\Lambda U^\top,\qquad \hat{x}=U^\top x,\qquad \hat{y}=U^\top y.
$$

$U$ 是由组织图决定的空间基底。小特征值对应在相邻节点上变化缓慢的低频模式，即大的组织区室；较高频率对应更局部、更快速的空间变化。

#### 2. 在频域比较两个细胞图案

BioGSP 教程中的 `runSGCC()` 对两个谱信号做能量归一化的相似性计算，并排除表示整体均值的 DC 分量。直观地，它比较的是：去掉“样本里总共有多少细胞”后，两类细胞是否在相同空间尺度上共同起伏。可用归一化内积理解：

$$
\mathrm{SGCC}(x,y)=
\frac{\sum_{k\in K}\hat{x}_k\hat{y}_k}
{\sqrt{\sum_{k\in K}\hat{x}_k^2}\sqrt{\sum_{k\in K}\hat{y}_k^2}},
$$

其中 $K$ 不包含 DC 分量，并可限制在选定频带。值越高，两个图案在该尺度越协同；低值表示它们的空间组织不同或被其他空间结构稀释。注意，SGCC 是空间共变指标，不是细胞通信或因果作用的直接证明。

#### 3. 多尺度与带宽选择

补充方法把图傅里叶变换、谱图小波变换（SGWT）和 SGCC 串联起来。低频成分描述全局组织结构，带通小波把信号定位到较局部尺度；Kneedle 算法用于选择截止带宽。论文图 3 的分析流程是：细胞先分箱，图傅里叶编码得到低频系数，再进行交叉相关，并按 SGCC 对 ROI 排序。这个排序随后作为连续空间因子，与 RNA 基因和通路变化关联，而不是把高低 SGCC 预先当成天然生物分组。

### 论文中怎样使用 SGCC

在 tonsil 中，作者比较 CD4 T 细胞与 BCL6 阳性/阴性 B 细胞的空间图案。SGCC 从低到高的排序对应生发中心暗区、明区及 T–B 细胞关系的连续变化；RNA 程序进一步解释这种几何变化对应哪些细胞内在状态和细胞间功能。

在 DLBCL 中，作者先在 17 例 EBV 阳性和 13 例 EBV 阴性样本上完成 CODEX–GeoMx。蛋白层显示 EBV 阳性肿瘤中调节性 T 细胞和 CD68+CD163+ 巨噬细胞增加、MHC II 降低，CD4 T 细胞功能障碍评分升高。SGCC 随后分别分析肿瘤—巨噬细胞和巨噬细胞—CD4 T 细胞轴，并用三元图整合三组两两关系。结果支持 EBV 状态与免疫抑制性空间组织相关，但不能仅凭 SGCC 宣称这些细胞关系“驱动”了功能障碍。

单细胞 CODEX–CosMx 分析把 bin 替换为滑动窗口，在每个 FOV 内计算肿瘤、巨噬细胞和 T 细胞信号。作者观察到 C1Q 巨噬细胞特征与 CD4 T 细胞功能障碍相关，并在独立 CosMx 队列验证。图 7 再围绕 LMP1 阳性肿瘤细胞的 20 µm 邻域，比较附近 C1Q 巨噬细胞、差异表达及 Squidpy 推断的配体—受体对，提出 EBI3/IL-27 受体—STAT3 轴作为候选机制。它来自空间邻近、表达和计算推断的联合证据，尚不是扰动实验确证的因果通路。

### 论文、图和代码如何对上

仓库按论文图组织分析脚本，而不是一个从原始数据到全部图表的一键软件包。SIFT 配准可以在 Python 源码中直接追踪：脚本设置 10,000 个 SIFT 特征，以 BFMatcher 做二近邻匹配、0.7 比率过滤，再估计仿射矩阵。单细胞 SGCC 脚本则先创建空间信号，调用 `runSpecGraph()`、`runSGWT()` 和 `runSGCC(..., return_parts=TRUE)`，再按 SGCC 分组做差异表达。

核心 SGCC 数值实现不在本仓库内，而由外部 R 包 BioGSP 提供；仓库中的 `tutorial/sgcc_tutorial.md` 是调用入口和算法说明。因此，本地代码能证明论文如何组织输入、调用 SGCC、排序样本和执行下游分析，却不能独立审计 `runSGCC()` 内部的所有数值细节。复现完整结果还需要匹配 BioGSP 版本和原始/处理后数据。

还有一个应明确保留的版本差异：论文单细胞方法描述将 SGCC 的顶部和底部 25% 作为高低组，而当前提交的 CosMx 脚本用顶部和底部三分之一分组。它不会改变“按 SGCC 排序再比较极端组”的总体逻辑，但会改变入组样本数及差异表达结果，复现时必须选择论文口径或代码口径并记录。

### 复现边界

本工作区固定代码提交为 `056fa7a59dc8eb7d200e34b3d313a1910e318dff`。仓库保留了大量逐图 R/Python 脚本和协议，但多个脚本含原作者服务器的绝对路径，环境和数据入口也未统一封装；它应视为公开分析源码快照，而不是开箱即用的流水线。论文数据由 Zenodo 记录提供，实验协议另见项目协议站点，SGCC 依赖 BioGSP。没有这些外部数据、包版本和路径改写，不能声称已端到端复现论文数值。

因此，最稳妥的阅读结论是：IN-DEPTH 的直接证据支持蛋白优先的同片实验顺序在多种平台组合上保持 RNA 质量，并展示其对细胞身份引导和跨模态验证的价值；SGCC 提供了把空间图案与功能状态关联的尺度感知排序。EBV、LMP1、C1Q 巨噬细胞、CD4 T 细胞功能障碍和 IL-27–STAT3 之间的关系是有多队列、多模态支持的关联模型，但其中的方向性与因果性仍需功能扰动实验验证。

### 建议阅读顺序

先看论文图 1 理解实验顺序，再看图 2 理解蛋白信息如何指导 RNA 分析；随后结合补充材料“SGCC Methods”和图 3掌握图频域逻辑。图 4–5 展示多细胞尺度的 DLBCL 应用，图 6–7展示单细胞验证与候选信号轴。代码层先读 `tutorial/sgcc_tutorial.md`，再读 tonsil/DLBCL 的 SIFT 配准脚本和 `src/06_figure_6_scSGCC/` 下的单细胞脚本，即可把论文方法、图和实际调用路径连起来。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## IN-DEPTH: Same-Slide Spatial Multi-Omics Integration

**Paper:** Same-Slide Spatial Multi-Omics Integration with IN-DEPTH Reveals Tumor Virus-Linked Spatial Reorganization of the Tumor Microenvironment
**Journal:** Cancer Discovery (AACR), 2025
**DOI:** 10.1158/2159-8290.CD-25-0775
**Authors:** Yiu, Chang, Yeo, Qiu, Wu et al. (co-first); Jiang, Ma (co-senior)
**Code:** https://github.com/SizunJiangLab/IN-DEPTH
**Data:** Zenodo 10.5281/zenodo.14530077 and 10.5281/zenodo.18379155

---

### Motivation & Novelty

#### Biological Problem

Tissues are spatially organized ecosystems where cell composition, neighbor identity, and position jointly determine function. While spatial transcriptomics and spatial proteomics have each individually transformed tissue biology, combining both modalities on the same tissue section has remained technically challenging:

1. **Protease incompatibility**: Most spatial transcriptomics platforms (CosMx, Xenium, VisiumHD) require protease digestion for RNA probe hybridization, which irreversibly destroys protein epitopes needed for immunofluorescence staining.
2. **Sequential slides lose spatial fidelity**: Even adjacent 5 μm FFPE sections can differ in cell composition, morphology, and microenvironment due to sectioning variation.
3. **Limited plex in co-detection methods**: Existing co-staining approaches like spatial CITE-seq (*Nature Biotechnology*, 2023, Liu et al.) typically detect <10 proteins and <3,000 genes, limiting biological resolution.
4. **Computational integration introduces noise**: Methods like SpatialGlue (*Nature Methods*, 2024), MaxFuse (*Nature Biotechnology*, 2023), and MARIO (*Nature Methods*, 2023) that integrate data from separate slides must computationally match cells/spots across sections, introducing registration artifacts and topological noise.

#### What's New

**IN-DEPTH (IN-situ DEtailed Phenotyping To High-resolution transcriptomics)** addresses all these limitations:

- **Protein-first strategy on the same slide**: Perform high-plex spatial proteomics (CODEX/PhenoCycler; 20–40 markers) first, then directly apply spatial transcriptomics to the same section — no computational cross-slide integration.
- **Commercial platform compatibility**: Demonstrated across 11 combinations of proteomics platforms (CODEX, SignalStar, Polaris, Orion) × transcriptomics platforms (GeoMx, VisiumHD, CosMx, Xenium), achieving R ≥ 0.94 gene-gene concordance in 10 of 11 combinations.
- **FFPE compatibility**: All experiments performed on formalin-fixed paraffin-embedded (FFPE) tissues, the clinical standard.
- **SGCC**: A new graph signal processing-based computational framework for quantifying spatially coordinated functional state changes between interacting cell populations.

#### Key Compared Methods (with journals/years)

| Method | Limitation Addressed |
|---|---|
| PANINI (*STAR Protocols*, 2022) | Limited to RNA+protein imaging, <5 plex RNA |
| Spatial CITE-seq (*Nature Biotechnology*, 2023) | Requires specialized microfluidics; low protein plex |
| DBiT-seq / spatial CITE (*Nature Biotechnology*, 2023) | Not compatible with FFPE; low protein plex |
| SpatialGlue (*Nature Methods*, 2024) | Cross-slide integration, registration artifacts |
| MaxFuse (*Nature Biotechnology*, 2023) | Requires cell-level matching across slides |
| CIBERSORTx, MuSiC (*Nature Commun.*, 2020, 2019) | Deconvolution without spatial ground truth reference |

---

### Method Overview

IN-DEPTH consists of two components:

#### 1. Experimental Workflow (IN-DEPTH Protocol)

A sequential same-slide workflow:
1. **Standardized antigen retrieval**: 97°C, pH 9.0, 20 min — optimized to be compatible with downstream RNA hybridization
2. **Spatial proteomics** (e.g., CODEX): 20–40 antibody panel, cyclic oligo-reporter imaging, whole-slide imaging
3. **Flow cell removal + photobleaching**: Gentle stripping leaves slide in "naked" state
4. **Spatial transcriptomics** (e.g., GeoMx, CosMx): RNA probe hybridization proceeds on same slide; cell-type masks derived from proteomics guide ROI selection or transcript assignment

The critical biological assumption: spatial proteomics chemistry is tolerated by RNA quality (confirmed by R ≥ 0.94 concordance), while the converse (protease treatment) is not tolerated by proteins.

#### 2. Computational Framework (SGCC)

**Spectral Graph Cross-Correlation (SGCC)** quantifies how two cell populations are spatially coordinated across tissue scales:

- Cell type abundances are represented as graph signals on a spatial tissue graph (60×60 bin grid)
- Graph Fourier Transform (GFT) projects signals to frequency domain
- Spectral Graph Wavelet Transform (SGWT) decomposes into low-frequency (global tissue domains) and band-pass (local cell-cell interaction) components
- Cosine similarity between spectral coefficients yields an SGCC score ∈ [-1, +1]
- SGCC scores rank ROIs/FOVs by spatial co-occurrence; treated as a continuous factor for identifying spatially covarying genes (via ImpulseDE2 or edgeR)

SGCC outperforms bivariate Moran's I, cross-variogram, Pearson correlation, and local spatial cross-correlation index (LSCI) in discriminating fine spatial pattern differences.

#### Biological Assumptions

1. Protein expression in cyclic immunofluorescence is stable across imaging cycles (verified by PLVAP consistency across 60 cycles)
2. Spatial organization of cells reflects underlying biology (not just technical variation)
3. Same-slide protein and RNA measurements are spatially aligned and co-registered

---

### Evaluation

#### Technical Validation (IN-DEPTH Workflow)

| Platform Combination | Tissue | Gene-Gene Concordance (R) |
|---|---|---|
| CODEX-GeoMx | Tonsil | 0.938, 0.952 |
| SignalStar-GeoMx | DLBCL | >0.94 |
| CODEX-VisiumHD | Periodontal | >0.94 |
| CODEX-CosMx | DLBCL | >0.94 |
| CODEX-Xenium | PCNSL/Tonsil | 0.970 |
| CODEX-VisiumHD (60 cycles) | Brain | 0.966 |
| Orion-GeoMx | — | 0.692 (outlier) |

Total RNA capture and sequencing quality metrics (Q30, reads mapped to probe set) comparable between IN-DEPTH and control slides across all tested combinations.

#### Biological Application: DLBCL TME

**Cohort**: 30 patients (17 EBV+, 13 EBV-) for CODEX-GeoMx; 39 patients (22 EBV+, 17 EBV-) for CODEX-CosMx
**Platforms**: CODEX PhenoCycler Fusion + GeoMx DSP (30 plex protein + >18,000 gene hWTA + 14 EBV gene spike-in)

**Key findings:**

| Finding | Evidence |
|---|---|
| EBV+ DLBCL: elevated Tregs, CD68+CD163+ macrophages, reduced CD68+ macrophages | Log2 fold enrichment analysis, Wilcoxon test |
| EBV+ DLBCL: CD4 T cell dysfunction elevated (not CD8) | Protein dysfunction score + RNA GSVA, one-sided Wilcoxon, p<0.05 |
| Immune-rich CD4T neighborhood motif (Motif 1) enriched in EBV+ | K-means k=5, Wilcoxon |
| EBV+ macrophages: 1.91x more CD68+CD163+ vs EBV- | Negative binomial regression, p<0.05, 95% CI [1.64, 2.25] |
| EBV+ macrophages: reduced HLA-DR, elevated PD-L1 with tumor density | Protein correlation analysis |
| C1Q macrophage signature positively correlated with CD4T dysfunction | Spearman correlation (single-cell CosMx + GeoMx) |
| LMP1+ tumor neighbors: log10 FC = 2.00 more C1Q+ macrophages vs EBV- | OLS regression, 95% CI [1.91, 2.10] |
| IL-27/STAT3 axis: EBI3-IL27RA/IL6ST/STAT3 enriched in LMP1+ tumor-macrophage pairs | Squidpy L-R, Wilcoxon, p<0.05 |

**Cross-cohort validation**: C1Q macrophage findings validated in independent CosMx-only validation cohort (55 EBV+ and 41 EBV- FOVs from three clinical sites).

---

### Reproducibility

**Rating: 4/5**

**Justification:** All analysis code is publicly available on GitHub with organized per-figure scripts. Data is deposited on Zenodo (two separate deposits). Experimental protocols are available at sizunjianglab.github.io/IN-DEPTH with video tutorials. The SGCC package is publicly available on CRAN as `BioGSP`.

**Strengths:**
- Complete 11-step CODEX image processing pipeline with scripts (Python)
- Per-figure R scripts matching manuscript figures
- BioGSP CRAN package for SGCC reproducibility
- Interactive cost calculator for experimental planning (Supp Table 12)
- Multiple independent validation cohorts (DLBCL) and tissue types (tonsil, kidney, brain, periodontal, uterine)

**Weaknesses / Practical Notes:**
- **SGCC implementation gap**: Paper figure scripts use simplified GFT-only implementation (`1-SpaGFT_preload_function.R`) rather than the full SGWT-based BioGSP package. Running BioGSP may give slightly different SGCC scores.
- **Data download**: Data on Zenodo requires account; raw CODEX OME-TIFFs are large (multi-GB per TMA). Processed AnnData objects (h5ad) are more accessible.
- **Hardcoded paths**: Several Python scripts contain absolute server paths (e.g., `[local path omitted]`) that must be updated.
- **Mesmer interior_threshold discrepancy**: Paper says 0.05, code uses 0.2; regenerating segmentation results will differ from original.
- **R environment**: Requires GitHub-sourced `gasper` and `kneedle` packages; use `renv` or document R version explicitly.
- **Compute**: Mesmer segmentation requires CUDA GPU (TensorFlow); CODEX pipeline designed for NFS-mounted cluster storage.

---

### Strengths and Weaknesses

#### Strengths
1. **True same-slide co-measurement** eliminates a major confound in spatial multi-omics
2. **Platform-agnostic design**: demonstrated on 11 combinations spanning major commercial platforms
3. **FFPE compatibility**: directly applicable to clinical biobank specimens
4. **SGCC provides mechanistic interpretability**: spatial co-variation quantified at multiple scales simultaneously
5. **Validated in three independent DLBCL cohorts** from different institutions

#### Weaknesses
1. **Protein-first order**: limits compatibility with RNA-first protocols (some optimizations still needed for Orion-GeoMx)
2. **SGCC complexity**: requires eigendecomposition and graph construction; not trivially scalable to very large datasets
3. **SGCC implementation divergence**: published paper figures and CRAN package use different implementations
4. **Modest RNA yield reduction** with extended imaging (60 cycles): ~2.5-fold reduction in total RNA counts, though gene correlation preserved
5. **Tissue integrity constraint**: extended photobleaching and cyclic imaging place upper bounds on tissue usability for additional modalities

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
