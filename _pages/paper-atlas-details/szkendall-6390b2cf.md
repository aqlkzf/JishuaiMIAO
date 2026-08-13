---
layout: default
permalink: /paper-atlas/szkendall-6390b2cf/
title: "szKendall"
nav: false
description: "单细胞 Hi-C 接触矩阵极稀疏。零既可能是真正不存在接触的结构性零（SZ），也可能只是测序不足造成的 dropout。szKendall 不自己识别 SZ 或直接聚类，而是在已经给出 SZ/插补结果后计算细胞两两不相似度，供 PAM、层次聚类、UMAP/t-SNE 使用。 包把输入中所有零都视为 SZ。若 dropout 尚未插补，它也会被当成生物结构信号，因此结果直接依赖上游 HiCImpute/scHiCSRS 或其他 SZ 判别。"
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
      <span>Domain Clustering</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>szKendall</h1>
    <p>szKendall: spatial-structural-zero-aware dissimilarity measures for subtype discovery using single cell Hi-C data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-72186-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for szKendall">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/osu-stat-gen/szKendall" target="_blank" rel="noopener noreferrer" aria-label="Open code for szKendall">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## szKendall 方法解读：把“结构性零”当作三维基因组信号

### 核心问题

单细胞 Hi-C 接触矩阵极稀疏。零既可能是真正不存在接触的结构性零（SZ），也可能只是测序不足造成的 dropout。szKendall 不自己识别 SZ 或直接聚类，而是在已经给出 SZ/插补结果后计算细胞两两不相似度，供 PAM、层次聚类、UMAP/t-SNE 使用。

包把输入中所有零都视为 SZ。若 dropout 尚未插补，它也会被当成生物结构信号，因此结果直接依赖上游 HiCImpute/scHiCSRS 或其他 SZ 判别。

### 从接触矩阵到距离

每个 $n\times n$ 对称矩阵保留不含对角线的上三角，共 $N=n(n-1)/2$ 个 locus pair（LP）。LP 的 band 为 $|j-i|$。标准 Kendall 比较任意两个 LP 在两个细胞中的相对排序；szKendall 加入：

$$W^K_{\Delta}=(n-1-\Delta)^{-0.4},\quad \Delta=\big||j-i|-|v-u|\big|,$$

$$W^{SZ}_{|j-i|}=(1+|j-i|)^{-0.5}.$$

第一项让 band 差异更大的 LP 对获得更大 Kendall 权重；第二项在同一 LP 的 SZ 状态跨细胞不一致时加罚，并对短程接触给更高惩罚。

### 16 种 SZ 情形

比较两个 LP、两个细胞时有四个接触值，形成 16 种零/非零组合。`szkendall_cpp()` 将位置划为两细胞均非 SZ、仅细胞 1 为 SZ、仅细胞 2 为 SZ、两者均为 SZ并逐类累加：全非零用 band 加权 Kendall；单侧 SZ 加 SZ 罚分；交叉不一致加双罚分；共享相同 SZ 模式不增加距离。

输出是未归一化原始和，不同矩阵尺寸或 SZ 比例间不能直接比较绝对值；热图的 0–1 缩放只用于显示。

### API、计算与下游

`szKendall()` 接受矩阵、三维数组或矩阵列表，经 `bind_to_matrix()` 统一格式，同时返回 Euclidean、普通 Kendall 和选定 SZ 距离。细胞对由 `foreach` 并行，C++ 对 LP 对循环，最坏复杂度约 $O(M^2N^2)$。它适合染色体级粗分辨率分析，不能因使用 Rcpp 就推断为精细全基因组可扩展。

Euclidean 比较路径对 `mat_count` 每列标准化后再计算距离，不是原始 counts 的普通欧氏距离。包只产出距离，不自动选择聚类算法或簇数。

### 最关键的论文—代码断裂

论文定义：

- szKendall：$W^K=(n-1-\Delta)^{-0.4}$；
- szKendall1：$W^{K1}=(1+\Delta)^{-0.4}$，强调 band 相近的 LP 对；
- szKendall2：Kendall 权重恒为 1。

当前 API 只接受 `"szKendall"` 与 `"szKendall1"`。代码的 `szKendall1.diss()` 实际是“普通 Kendall + SZ 罚分”，对应论文 szKendall2；论文真正的 szKendall1 没有实现，也没有独立 `szKendall2`。`DESCRIPTION` 所称“two variants”与实现不一致，vignette 的 `szK1` 示例仍调用 `dist.method="szKendall"`。

所以论文三个变体的相对性能无法仅凭此快照复现。这是算法权重缺失，不是单纯命名差异。

### 图 1–5 的证据边界

- 图 1：向量化、两权重、16 情形与距离工作流，直接对应主 C++ 函数。
- 图 2：三个模拟设置的距离块与 t-SNE；模拟 SZ 机制已知，不等于真实 SZ 已知。
- 图 3：ARI/WSS/ASW/MIS；MIS>1 是所用距离下的几何隔离，不是生物学“金标准”。
- 图 4：性能随 SZ 灵敏度/特异度误判下降，说明方法依赖上游 SZ 质量。
- 图 5：42 个 mESC 的三阶段分离；其 SZ“真值”由平滑与规则构造，并非直接观测。
- PFC L4/L5 结果在表 2；指定 $k=2$ 的 ARI=1 不证明会自动选择两个亚型。

### 其他实现边界

1. mESC 深度缩放与 SZ 构造未封装为主 API。
2. 未发现自动化测试；绑定数据和 vignette 不能替代回归测试。
3. 距离函数用 `<1e-5` 同时识别待计算/失败位置，注释承认错误处理待修；真实近零距离没有独立状态。
4. 默认注册 `detectCores()-1` 个核心，在共享机器应显式限制后端。

### 直接证据

- 论文/图：`paper source/paper/auto/paper.md`、`paper source/paper/auto/images/`
- 主接口：`code/R/szKendall_main.R:1-106`
- 两公开距离：`code/R/szKendall_function.R`、`code/R/szKendall1_function.R`
- 核心 16 情形：`code/src/szKendall-tau_function_cpp.cpp:263-500`
- 变体代码：同文件 `:509-718`
- 仓库：`https://github.com/osu-stat-gen/szKendall`（本地合同没有固定提交）

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## szKendall Summary

### Motivation & Novelty

#### Biological Problem
Single-cell Hi-C (scHi-C) measures the 3D chromatin organization of individual nuclei by capturing pairwise genomic contacts. Discovering cell subtypes from scHi-C data requires computing dissimilarity between cells' contact matrices. The fundamental challenge is that scHi-C contact matrices are extremely sparse (~1% coverage), and zero entries have two distinct biological meanings:

- **Structural zeros (SZs)**: genuine absence of contact due to 3D genome structure — biologically informative
- **Dropouts (DOs)**: technical zeros from insufficient sequencing depth — noise

#### Why Existing Methods Fall Short
All standard dissimilarity measures treat zeros uniformly:
- **Euclidean distance** (used in K-means): treats SZs and DOs identically; sensitive to sequencing depth differences
- **Kendall's tau** (Bioinformatics 2019, scHiCluster): ignores spatial structure of the 2D contact matrix; treats all zeros as equivalent
- **Smoothing methods** (HiCRep, Genome Research 2017; SCL, Bioinformatics 2019; GenomeDisco, Bioinformatics 2018): aim to denoise but destroy SZ information in the process
- **HiCImpute** (PLoS Computational Biology 2022): identifies SZs and imputes DOs, but downstream clustering still uses SZ-unaware distances

A concrete failure: L4 and L5 excitatory neurons in the human prefrontal cortex cannot be separated by K-means on Euclidean distance from raw scHi-C data, despite residing in distinct cortical layers with different 3D genome organization.

#### Unique Contributions
1. **First SZ-aware dissimilarity measure for scHi-C**: szKendall explicitly incorporates SZ status into the distance calculation
2. **Band-aware weighting**: accounts for the spatial structure of 2D contact matrices by weighting LP pairs based on their genomic distance difference
3. **Reduced magnitude dependence for SZ terms**: the SZ penalty uses status rather than count magnitude, but sequencing-depth invariance is not guaranteed because non-SZ rankings and upstream SZ calls can change with depth
4. **Three variants**: szKendall (band-aware), szKendall1 (alternative weighting), szKendall2 (SZ-only, no band weighting) — enabling systematic study of which components drive performance

---

### Method Overview

szKendall modifies Kendall's tau distance with two enhancements:

**Component 1 — Band-aware Kendall weighting**: For LP pairs where neither cell has a discordant SZ, the standard Kendall discordance is weighted by the absolute difference in band indices (genomic distance difference). The weight $W^K = (n-1-|diff|)^{-0.4}$ assigns lower weight to LP pairs with similar genomic distances, reducing the influence of chance discordances between similarly-distanced contacts.

**Component 2 — SZ discrepancy penalty**: When a given LP is an SZ in one cell but not the other, a penalty $W^{SZ} = (1+|j-i|)^{-0.5}$ is added. This penalty is larger for short-range contacts (near the diagonal), where contacts are biologically expected unless suppressed by a true structural zero.

The 16 possible SZ status combinations across two LPs and two cells are handled explicitly, with each case contributing a specific combination of weighted Kendall discordance and SZ penalties.

**Input requirements**: The user must provide SZ-annotated data — zeros in the input are treated as SZs, and DO positions should be replaced with imputed values (e.g., from HiCImpute or scHiCSRS) before calling szKendall.

**Output**: An M×M dissimilarity matrix (plus Euclidean and Kendall matrices for comparison), usable with PAM, hierarchical clustering, t-SNE, or UMAP.

See `doc_method.md` for full mathematical derivation and `doc_code.md` for implementation details.

---

### Evaluation

#### Datasets
1. **Simulated data (Sim1/2/3)**: 150 cells × 3 subtypes, varying proportions of common SZs (32%/4.2%/1.8% for ST3). Based on 3D coordinates of chromosome 19 from K562 cell (GEO: GSE80006).
2. **mESC real data**: 42 cells (21 real + 21 simulated), 3 cell-cycle stages (G1 n=30, early-S n=4, late-S/G2 n=8), chromosome 1 at 1 Mb resolution. From scHi-CSim (Journal of Molecular Cell Biology 2023), original data GEO: GSE94489.
3. **Human prefrontal cortex**: sn-m3C-seq data, L4 (n=131) and L5 (n=180) excitatory neurons. From Lee et al. (Nature Methods 2019).

#### Metrics
- **ARI** (Adjusted Rand Index): clustering accuracy vs. ground truth
- **WSS%**: within-cluster sum of squares / total SS (lower = tighter clusters)
- **ASW** (Average Silhouette Width): cohesion and separation (higher = better)
- **MIS** (Minimum Isolation Score): separation/diameter ratio per cluster (>1 = isolated)

#### Results

**Simulations**:
- Sim1 (high SZ): szKendall achieves ARI ≈ 1.0, MIS >> 1. K-means also achieves ARI ≈ 1.0 but fails WSS% and MIS.
- Sim2 (moderate SZ): szKendall ARI ~0.8-0.9; Euclidean/Kendall ARI ~0.
- Sim3 (low SZ, 1.8% common): szKendall ARI ~0.5-0.7; Euclidean/Kendall ARI ~0. **No non-SZ-aware method achieves MIS > 1 in any dataset.**
- Robustness: szKendall maintains superiority even at 60% sensitivity / 40% specificity in SZ detection.

**mESC real data**:
- szKendall and szKendall1 achieve **ARI = 1.0** at k=3 (perfect cell-cycle stage recovery).
- Euclidean and Kendall achieve ARI ≈ 0.

**Prefrontal cortex**:
- All three szKendall variants achieve perfect L4/L5 separation (ARI = 1.0 at k=2) using HiCImpute-processed data.
- Euclidean on imputed data suggests a 4-cluster structure (two sub-subtypes per group); szKendall finds no support for >2 clusters, suggesting the 4-cluster structure may be an artifact of Euclidean distance.

#### Variant Comparison
szKendall and szKendall1 consistently outperform szKendall2, confirming that band-aware weighting (not just SZ penalty) is important. The underperformance of szKendall2 (constant Kendall weight) demonstrates that spatial context in the weighting scheme contributes independent signal beyond SZ status alone.

---

### Reproducibility

**Rating: 2.5/5**

**Justification**: The R package is well-structured with documented functions, three input formats, and bundled real/simulated datasets. The core algorithm is implemented in C++ (Rcpp) for performance. However, there is a significant discrepancy between the paper's description of szKendall1 and the code implementation (see doc_code.md), which could confuse users trying to reproduce the paper's variant comparison.

**Strengths**:
- R package available on GitHub (osu-stat-gen/szKendall) with vignette
- Bundled datasets: PFC data, simulated data (Sim1/2/3), 100-replicate versions
- Three input formats (list/array/matrix) for flexibility
- Parallel computation via foreach/doParallel
- All evaluation metrics (ARI, ASW, MIS, WSS%) implemented in the package

**Weaknesses**:
- **szKendall1 naming mismatch**: The code's `szKendall1.diss()` does not implement the paper's szKendall1 ($W^{K1} = (1+|diff|)^{-0.4}$). The code uses unweighted Kendall + SZ penalty, which corresponds to the paper's szKendall2. This makes it impossible to reproduce the paper's szKendall1 results using the published code.
- **szKendall2 not separately implemented**: The paper's szKendall2 (constant Kendall weight + SZ penalty) is effectively what the code calls szKendall1, but there is no separate szKendall2 function.
- **SZ detection not included**: The package does not perform SZ detection; users must run HiCImpute or scHiCSRS separately. This dependency is not clearly documented in the main function.
- **Computational cost**: O(M² × N²) complexity limits applicability to chromosome-level analysis at coarse resolution. Genome-wide analysis at fine resolution is not feasible without algorithmic improvements.
- **mESC preprocessing**: The sequencing depth scaling procedure (Section 4.4) is described in the paper but not implemented as a package function.

**Environment**: R ≥ 3.5, tested on macOS 15.5 and Windows 11. Requires Rcpp compilation. Install via `devtools::install_github("osu-stat-gen/szKendall")`.

**Data availability**: All datasets bundled in the package. Original data: GEO GSE94489 (mESC), GitHub dixonlab/scm3C-seq (PFC), GEO GSE80006 (K562 3D coordinates).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
