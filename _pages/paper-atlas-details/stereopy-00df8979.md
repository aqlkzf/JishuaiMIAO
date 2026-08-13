---
layout: default
permalink: /paper-atlas/stereopy-00df8979/
title: "Stereopy"
nav: false
description: "空间转录组分析过去多以单张切片为单位：一个 AnnData、一套预处理和一组结果。但真正的生物问题常涉及多条件、多时间点或连续三维切片。Stereopy 的贡献分两层。第一层是工程框架：用 MSData 管理多个样本，用 MSDataPipeLine（论文称 MSS，multi-sample scope）决定哪些样本独立处理、哪些样本合并处理，并追踪结果依赖。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>Stereopy</h1>
    <p>Stereopy: modeling comparative and spatiotemporal cellular heterogeneity via multi-sample spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-58079-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Stereopy">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/STOmics/Stereopy" target="_blank" rel="noopener noreferrer" aria-label="Open code for Stereopy">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Stereopy：从多样本容器到比较、时间与三维生态位分析

### 这篇论文是一套框架，而不是一个单模型

空间转录组分析过去多以单张切片为单位：一个 AnnData、一套预处理和一组结果。但真正的生物问题常涉及多条件、多时间点或连续三维切片。Stereopy 的贡献分两层。第一层是工程框架：用 `MSData` 管理多个样本，用 `MSDataPipeLine`（论文称 MSS，multi-sample scope）决定哪些样本独立处理、哪些样本合并处理，并追踪结果依赖。第二层是面向多样本的算法：CCD 比较细胞群落，TGPI 识别时空基因模式，NicheReg3D 从连续切片重建三维细胞生态位并研究通信/调控。

因此不能把 Stereopy 简化成“又一个批次整合器”。它还包括 I/O、预处理、聚类、注释、可视化和 GPU/并行入口；论文 Fig. 1–2 展示框架与性能，Fig. 3–5 分别对应比较、时间和三维案例。

### MSData 与 MSS：多样本分析如何不丢上下文

`StereoExpData`/AnnData 类对象保存单样本表达、细胞/基因元数据和空间坐标；`MSData` 保存多个此类对象及样本名、切片关系和多样本结果。当前源码 `stereo/core/ms_data.py:641` 定义 `MSData`，`stereo/core/ms_pipeline.py:25` 定义 `MSDataPipeLine`。

MSS 的关键不是简单 `concat`。在 `isolated` 模式，算法分别作用于各样本，可由 joblib 并行；在 `integrate` 模式，选定 scope 的样本先进入联合数据视图，算法结果再与 scope、参数和依赖关系一起记录。相应分支在 `ms_pipeline.py:88-151`。这使“同一参数独立运行”和“联合估计一个跨样本结果”成为显式选择。

该框架仍不能自动消除批次效应。是否整合、采用何种校正、不同样本细胞类型标签是否可比，仍需研究者判断。

### CCD：群落是细胞类型混合，而不是一个表达簇

Cell Community Detection 的输入首先是每个细胞的位置和已有细胞类型注释。它不是从原始表达直接发现 cell type，而是在多尺度滑动窗口中统计局部组成：

$$
\mathbf f_w=[p_1,p_2,\ldots,p_K],\qquad
p_k=\frac{\#\{\text{window }w\text{ 中类型 }k\text{ 的细胞}\}}{\#\{w\text{ 中全部细胞}\}}.
$$

`stereo/algorithm/ccd/sliding_window.py:114-149` 将坐标离散到子窗口，合并为不同大小的窗口，并把计数归一成组成向量。多个窗口尺寸能同时看大组织区和窄边界。低细胞数窗口按

$$
n_w<\bar n-c\,s_n
$$

过滤；代码 `:151-154` 的 `min_cells_coeff` 可配置，论文实例常用 $c=2$，不能把它理解为不可改变的算法常数。

极其弥散或到处出现的 cell type 会主导组成向量却不能定义组织域。CCD 因此把每种类型栅格化，计算 Shannon entropy 与 scatteredness（连通块数量相对占据像素的指标），再按阈值剔除。当前实现位于 `stereo/algorithm/ccd/metrics.py:8-91` 及 `community_clustering_algorithm.py:195-204`；旧文档把它指向 `community_detection.py` 且声称固定 log2，并不够精确，实际调用 `skimage.measure.shannon_entropy`。

来自所有样本、所有尺度的有效窗口特征被联合送入 Leiden、谱聚类或层次聚类。每个细胞通常被多个窗口覆盖，最终标签由覆盖它的窗口社区多数投票产生（`sliding_window.py:157-204`）。这样跨切片的相同标签才有共同特征空间含义，但结果仍依赖预先注释、窗口尺度、群落数/分辨率和切片坐标单位。

论文在胚胎脑、成年脑和 WT/ob/ob/UMOD-KI 肾脏中以组织连贯性、S-Dbw、SD index、Moran's I、运行时间和生物标志评价 CCD（`paper.md:201-215`）。90×/35×速度优势是论文 benchmark 结果，不是核心包中的自动测试。

### 共现：为什么 $P(B\mid A)$ 不对称

对于类型 A 的 $N_A$ 个细胞，若其中 $C$ 个在给定距离带内至少邻近一个 B，则

$$
P(B\mid A)=\frac{C}{N_A}.
$$

它一般不等于 $P(A\mid B)$：普遍分布的内皮细胞可能出现在很多细胞周围，但内皮周围不一定同样富集某个稀有类型。`stereo/algorithm/co_occurrence.py:21-107` 用 Numba 并行计算距离带和条件概率。多样本加权、组间差值在上层结果处理中完成，故基础单样本公式是 Exact，而完整组间比较属于 Partial mapping。

### TGPI：先问连续变化，再加入空间形状

Temporal Gene Pattern Identification 面向有序时间点或轨迹中的同一细胞群。对相邻时间 $t,t+1$，它分别做单尾检验，得到下降方向 $P_l(t)$ 与上升方向 $P_g(t)$。论文强调 permutation test 以降低参数假设风险，但代码 `time_series_analysis.py:89-153` 还支持 Wilcoxon，并默认更快的 t-test；复现论文分析时必须显式选择统计方法。

连续上/下调排序使用 False Positive Risk score：

$$
\mathrm{FPR}=1-\prod_t(1-P_t).
$$

代码 `time_series_analysis.py:176` 精确实现该公式，却把枚举名写成 `fdr`。它不是 Benjamini–Hochberg FDR，不应按多重检验校正解释。

更复杂的模式由两类特征共同表达。时间特征用方向符号乘相邻时间变化的置信强度：

$$
f_{temporal,t}=\operatorname{sign}(P_l-P_g)\max(1-P_l,1-P_g).
$$

空间特征先将每个时间点的基因表达栅格化，再 normalize、log1p、scale 并做 PCA（`time_series_analysis.py:233-261`）。最终

$$
\mathbf f=\operatorname{concat}(\mathbf f_{temporal},\alpha\mathbf f_{spatial,1:q})
$$

进入 fuzzy C-means（`:182-231,263-313`）。每个基因对多个模式具有 membership，而不是被硬分配后完全丢失不确定性。固定随机种子 `20240523` 有助于复现；空间权重 $\alpha$、PCA 维数、栅格大小和 cluster 数都会改变结果。

Fig. 4 用 E9.5–E16.5 小鼠胚胎脑展示 TGPI/PAGA；补充比较显示 TGPI 相比 Mfuzz 更能同时富集时间相关和空间差异基因（`paper.md:217-266`）。这说明加入空间特征在该数据上有用，不证明所有非单调模式都能被唯一识别。

### NicheReg3D：先找边界，再分析细胞通信

连续二维切片需先经 ST-GEARS 和人工修正对齐成三维坐标；Stereopy 本身的 niche 步骤假设该对齐已足够可靠。对于目标细胞类型 $T$ 的细胞 $i$，在其邻域内计算异类型比例

$$
D_i=\frac{\#\{\text{非 }T\text{ 邻居}\}}{\#\{\text{全部邻居}\}},
$$

以及邻居类型熵 $S_i$。边界判定为

$$
i\in B_T \quad\Longleftrightarrow\quad D_i>\theta S_i.
$$

`stereo/algorithm/get_niche.py:52-123` 把二维位置与 `position_z` 连接，在三维中查邻居，计算 shift、base-2 entropy 和边界，再从其他类型中选择最近细胞组成 niche。熵底数会改变量纲，因此论文阈值与代码阈值必须配套使用。

对 niche 内 sender/receiver，CellPhoneDB 风格模块按配体和受体表达计算活动并置换检验；代码的比较使用 `>=` 而不是论文公式中的严格 `>`。论文随后把受体连接到转录因子和靶基因：在 NicheNet v2 的约 380 万条调控网络中令边距离为权重倒数，再用 Dijkstra 找最短信号路径。这里存在重要边界：当前核心 `stereo/` 包可以找到 niche、细胞通信和一般 GRN 模块，却没有找到论文 NicheReg3D 专用的 Dijkstra receptor→TF 路径实现及相应 NicheNet v2 网络。Fig. 5h–i 的这一步不能仅靠已定位包源码重建，属于 Not found/论文专用流程，而非 Exact code match。

Fig. 5 在 59 张胚胎心脏切片上研究 VCM 等细胞的三维 niche；通信与调控结果依赖上游 3D 对齐、细胞注释、L–R 数据库和网络先验，不能解释成直接物理结合或实验证实的调控因果。

### 五幅主图怎样串起来

- Fig. 1 是软件和生物问题地图：多样本容器、比较、时间、三维分析以及可视化。
- Fig. 2 说明 MSData/MSS 的联合与独立 scope、并行执行和 GPU 加速，并用胚胎数据比较耗时。
- Fig. 3 用肾脏多条件数据展示 CCD 群落、细胞类型共现和一致/条件特异 marker；它回答“组织结构如何随条件变化”。
- Fig. 4 从胚胎脑时间序列提取 TGPI 模式并结合轨迹，回答“同一细胞群的基因何时、在哪里变化”。
- Fig. 5 从连续心脏切片重建 niche、L–R 通信和候选调控路径，回答“边界细胞可能接受何种三维微环境信号”。

主图位于 `paper source/PMC12012134/images/`，逐面板解释见 `figure_analysis.md`。PMC 目录还保存多个 MOESM 补充 PDF；正文 Markdown 内含对 Supplementary Tables/Figs 的锚点和描述，但没有单独转换出的 supplement Markdown。本次核对了正文中的补充引用与本地 PDF 的存在，不声称所有 MOESM 附件已逐表重算。

### GPU 和性能声明的边界

论文报告 GPU 版本的 SingleR、Leiden、Louvain 和 UMAP，并比较 CPU/GPU 时间。当前仓库是一个持续演化的大型工具箱，存在 GPU 可选依赖与相关算法入口，但并非所有论文性能脚本和硬件环境都被封装成测试。核心 CCD 共现还主要依赖 Numba/CPU 并行。因而“支持 GPU”与“所有 Stereopy 算法自动在 GPU 上加速”是两回事。

### 代码版本与复现范围

核心容器、CCD、TGPI、niche 和通信实现均可直接审计，仓库还包含测试与教程。但论文数据需从 MOSTA、GEO、Zenodo等外部来源取得，ST-GEARS/BatchEval、专用 Dijkstra–NicheNet 流程、全部 benchmark 汇总和部分图表脚本不在已定位核心路径中。依赖范围较宽，GPU 结果还受 CUDA、RAPIDS/torch 和硬件版本影响。因此工作区支持高可信的代码—论文映射，不等于已在本机端到端重跑五幅主图。

### 最稳妥的实践原则

用 CCD 前先验证 cell type 注释与窗口尺度；用 TGPI 时明确时间顺序、统计检验和空间权重；用 NicheReg3D 时先量化切片配准误差，并把 L–R/GRN 路径当作候选机制。Stereopy 的强项是把这些分析放进同一多样本工作流，而不是替代每一步的实验设计与独立验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Stereopy: Comprehensive Multi-Sample Spatial Transcriptomics Framework

**Paper**: Stereopy: modeling comparative and spatiotemporal cellular heterogeneity via multi-sample spatial transcriptomics
**Journal**: *Nature Communications* 16, 3758 (2025)
**DOI**: 10.1038/s41467-025-58079-9
**Authors**: Shuangsang Fang, Mengyang Xu, et al. (BGI Research, 37 authors)
**Code**: https://github.com/STOmics/Stereopy (MIT license)
**PMCID**: PMC12012134

---

### Motivation & Novelty

#### The Problem

Modern spatially resolved transcriptomics (SRT) technologies — Stereo-seq (*Cell*, 2022), Slide-seq (*Science*, 2019), MERFISH (*Science*, 2015), seqFISH+ (*Nature*, 2019) — generate large multi-sample datasets spanning multiple conditions, timepoints, or 3D sections. Biologically meaningful questions require comparing disease vs. healthy samples, tracking cell-type emergence across embryonic stages, or understanding how 3D niche composition regulates gene expression. However, existing frameworks were built for single-sample analysis:

- **Scanpy** (*Genome Biol.*, 2018) — AnnData-based, single-sample
- **Seurat** (*Cell*, 2021) — SeuratObject, single-sample, R
- **Giotto** (*Genome Biol.*, 2021) — GiottoObject, ST-focused but single-sample, R
- **Squidpy** (*Nat. Methods*, 2022) — single-sample SRT analysis
- **MuData/Muon** (*Genome Biol.*, 2022) — multimodal but not multi-sample SRT-focused

Multi-sample methods like PRECAST (*Nat. Commun.*, 2023), BASS (*Genome Biol.*, 2022), GraphST (*Nat. Commun.*, 2023) perform spatial domain detection but lack comprehensive frameworks for comparison, temporal analysis, and 3D integration. Cell-cell communication tools (CellPhoneDB, NICHES) operate on 2D single-cell data and don't leverage 3D niche structure.

#### What's New

Stereopy contributes three things:

1. **Framework-level innovation**: `MsData` container + `MSS` controller + multi-sample transformer that unifies storage, scope management, and result tracking across an arbitrary number of samples/modalities. This is an infrastructure contribution analogous to how AnnData revolutionized single-cell analysis.

2. **Three domain-specific algorithms**:
   - **CCD** (Cell Community Detection): sliding-window convolution across multiple kernel sizes + joint multi-slice clustering + majority voting — outperforms Giotto SDI (*Genome Biol.*, 2021), SpaGCN (*Nat. Methods*, 2021), GraphST, BANKSY (*Nat. Genet.*, 2024), PRECAST, BASS in S-Dbw/SD/Moran's I while being 90× faster than Giotto SDI
   - **TGPI** (Temporal Gene Pattern Identification): novel FPR score combining p-values across timepoints + spatiotemporally concatenated features for fuzzy C-means clustering — more correlated with pseudotime than Mfuzz (*Bioinformation*, 2007)
   - **NicheReg3D**: adaptive 3D border detection via centroid shift + entropy → precise niche extraction → L-R communication → Dijkstra shortest-path signaling to TFs — identifies more complete L-R pairs than CellPhoneDB (*Nature*, 2022) and NICHES (ref. 50, spatially resolved CCC tool) by using true 3D niches

3. **GPU acceleration**: Re-implemented Python versions of SingleR, Leiden, Louvain, UMAP with GPU support

---

### Method Overview

See `doc_method.md` for full derivations. At a high level:

**Framework**: `MSData` stores $N$ `StereoExpData` objects (each an AnnData-based single sample). The `MSDataPipeLine` (MSS controller) dispatches algorithms in either `integrate` mode (merged data) or `isolated` mode (per-sample parallel via joblib). Results are scoped by sample name for traceability.

**CCD**: Tissue is scanned with sliding windows of configurable sizes. Each window becomes a feature vector of cell-type percentages. All windows from all slices are jointly clustered (Leiden/Spectral/Hierarchical). Final cell labels come from majority voting over overlapping windows.

**TGPI**: Statistical tests (permutation/t-test/Wilcoxon) between consecutive timepoints in a branch yield per-gene tendency features. FPR score = $1-\prod(1-P_i)$ identifies monotone regulators. Temporal + spatial PCA features are concatenated and clustered via fuzzy C-means.

**NicheReg3D**: Adaptive border detection (centroid shift $D_i > \theta \cdot S_i$) identifies the true boundary cells of each cell type. L-R communication is scored as mean ligand+receptor expression with permutation-based p-values. Dijkstra shortest paths in the NicheNet v2 (3.8M interactions) network connect receptors to downstream TFs. GRNs are inferred with SpaGRN/SCENIC.

---

### Evaluation

#### Datasets

| Analysis | Dataset | Technology | Size |
|---|---|---|---|
| CCD benchmarking | Mouse embryo whole brain | Stereo-seq | Single sample |
| CCD multi-sample | Adult mouse brain (3 slices) | Stereo-seq | ~3 consecutive coronal sections |
| Comparative (co-occurrence) | WT + *ob/ob* diabetic kidney | Slide-seq v2 | 2 samples |
| Comparative (CCD) | WT + UMOD KI kidney | Slide-seq v2 | 2 samples |
| Temporal | Mouse embryo brain E9.5–E16.5 | Stereo-seq (MOSTA) | 8 timepoints |
| 3D (NicheReg3D) | Mouse embryonic heart | Stereo-seq | 59 serial 2D sections |

#### Key Results

**CCD vs. baselines** (Supplementary Tables 1-2):
- Lower S-Dbw and SD validity scores than all competitors (Giotto SDI, SpaGCN, GraphST, PRECAST, BASS, BANKSY)
- Higher Moran's I (spatial autocorrelation) for community labels
- Speed: 31 s + 684 MB for kidney (UMOD KI+WT); 214 s + 25,716 MB for adult brain (3 slices)
- 90× faster than Giotto SDI, 35× faster than SpaGCN
- Accuracy comparable to BANKSY but faster/less memory

**TGPI vs. Mfuzz** (*Bioinformation*, 2007):
- Higher F-score (ANOVA test between timepoints) for most clusters
- Higher Pearson correlation with pseudotime
- 6/8 gene clusters enriched for significant GO terms vs. 3/8 for Mfuzz (p=0.05 cutoff)
- Successfully identified *Foxg1* (known forebrain TF) as top upregulated gene in forebrain trajectory

**NicheReg3D vs. CellPhoneDB + NICHES**:
- Stereopy identifies the most specific L-R pairs in all VCM-niche cases except ACM-VCM (Supplementary Fig. 27)
- Identified *Vcan-Itgb1* (FM→VCM) with communication score 0.293, p=0.00 — consistent with literature on VCM extracellular matrix
- 3D niche pruning reveals VCMs as primary signal receivers, contradicting cluster-level assumption that ACMs dominate communication
- Co-regulation of *Pdlim5*+ and *Mllt10*+ regulons via Ilk pathway identified as cardiac muscle development regulator

**Performance** (Fig. 2g-h):
- Stereopy outperforms Seurat, Giotto, Scanpy in preprocessing, PCA, neighbor finding, UMAP, clustering, marker gene identification for multi-sample data (merged dataset comparison)
- GPU mode further reduces time for computationally intensive steps (dimensionality reduction, clustering)

#### Biological Findings

1. **Kidney disease** (*ob/ob* vs. WT): Co-occurrence of Podocytes with GC cells is higher in *ob/ob*; *Spp1* is a conditional marker in UMOD KI medulla (associated with kidney stones); *Apoe* conditional marker connected to macrophage-related glomerular disorders

2. **Brain development** (E9.5-E16.5): *Foxg1* top upregulated forebrain gene; *Tead1* identified as key TF of cortical hem disappearance; *Tead1*-regulated genes drop from 338 at E12.5 to 7 at E13.5, with GO terms shifting from forebrain development to neuroblast proliferation

3. **Cardiac development** (mouse embryonic heart): VCM niche composition: ~28% ACM, 27% blood, 23% EC, 13% EP, 9% FM; collective *Vim-Cd44*, *Calm1-Ryr2*, *Igf2-Igf2r* L-R pairs implicated in CM proliferation/differentiation; *Itgb1*-stimulated GRN shows *Pdlim5* and *Mllt10* co-regulation of cardiac muscle contraction genes

---

### Reproducibility

**Rating: 3/5**

**What's provided**:
- Full package code at https://github.com/STOmics/Stereopy (MIT license)
- Zenodo archive: 10.5281/zenodo.14722436 (paper version)
- Tutorial notebooks: `docs/source/Tutorials(Multi-sample)/`
- Data: Stereo-seq MOSTA datasets at StomicsDB; Slide-seq v2 at Marshall et al. (*iScience*, 2022)

**What's missing / hard to reproduce**:
- **Dijkstra signaling path**: Core NicheReg3D algorithm is only in tutorial notebooks, not in the installable package — researchers cannot call it as a standard function
- **Benchmarking code**: Scripts for S-Dbw/SD/Moran's I comparison of CCD vs. baselines are not provided; results in Supplementary Tables 1-2 cannot be independently replicated without reconstructing the benchmarking pipeline
- **Python ≥3.8, <3.9 requirement**: Narrow Python version window (pyproject.toml) limits compatibility with modern environments (Python 3.10-3.12 common in 2025)
- **ST-GEARS alignment**: Required for NicheReg3D but is a separate external tool; alignment parameters and manual curation steps not documented
- **GPU requirements**: Some algorithms require CUDA-compatible GPU; CPU fallback performance not benchmarked

**Strengths**: Code is actively maintained, extensively documented at stereopy.readthedocs.io, and has multiple tutorial notebooks for each analysis type. The main algorithms (CCD, TGPI, GetNiche) are cleanly implemented and match the paper descriptions.

**Practical notes**:
- Install with `pip install stereopy`; GPU variants require specific PyTorch CUDA extras
- GEF/GEM formats from Stereo-seq require `stereo.io.read_gef()` / `read_gem()` readers
- For NicheReg3D, download NicheNet v2 weighted network from Zenodo (3.8M rows, ~300MB)
- Common pitfall: `MSData` requires all samples to share the same gene set; use `MSData.integrate()` before joint algorithms

---

### Strengths and Weaknesses

**Strengths**:
- Genuinely solves the multi-sample management problem for SRT — fills a gap that Scanpy/Seurat cannot
- All three algorithms (CCD, TGPI, NicheReg3D) are novel with clear mathematical formulations
- Numba JIT acceleration for co-occurrence gives major speedup over pure Python
- CCD is exceptionally memory-efficient (independent of gene expression matrix — uses only positions + cell types)
- Flexible scope/mode design allows both exploratory and reproducible analysis workflows

**Weaknesses**:
- Python ≥3.8, <3.9 restriction severely limits adoption in 2025 environments
- Dijkstra signaling path not packaged — users must manually extract code from tutorials
- NicheReg3D depends on external alignment (ST-GEARS), batch evaluation (BatchEval), and database (NicheNet v2); the "pipeline" is a collection of steps, not an end-to-end callable function
- TGPI defaults to t-test (not the permutation test the paper recommends for robustness)
- Benchmarking methodology for speed comparisons uses merged multi-sample data for other tools (unfair to Scanpy/Seurat which were not designed for multi-sample use)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
