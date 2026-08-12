---
layout: default
permalink: /paper-atlas/tessa-38a5dd5d/
title: "TESSA"
nav: false
description: "空间转录组中的细胞/spot 不仅处在不同坐标，也可能处在分化、发育或肿瘤进展的不同阶段。一个基因可以随伪时间变化，却呈现斑块状或非单调的组织分布；只用空间距离的 SVG 方法未必能捕获它。反过来，只做伪时间差异分析又忽略组织位置。 TESSA 将这两种相关结构放入同一个方差分量模型：Stage 1 先找至少具有空间或轨迹效应的 unified TSVG（uTSVG），Stage 2 再分别判断它是 TVG、SVG，还是两者兼有。"
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
      <span>Spatially Variable Genes</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>TESSA</h1>
    <p>TESSA: A unified model to detect trajectory-preserved and spatially-variable genes in spatial transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.09.06.674654" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## TESSA 方法解读：同时检验空间变化与轨迹变化

### 1. 为什么仅找 SVG 不够

空间转录组中的细胞/spot 不仅处在不同坐标，也可能处在分化、发育或肿瘤进展的不同阶段。一个基因可以随伪时间变化，却呈现斑块状或非单调的组织分布；只用空间距离的 SVG 方法未必能捕获它。反过来，只做伪时间差异分析又忽略组织位置。

TESSA 将这两种相关结构放入同一个方差分量模型：Stage 1 先找至少具有空间或轨迹效应的 unified TSVG（uTSVG），Stage 2 再分别判断它是 TVG、SVG，还是两者兼有。Figure 1 用平滑和斑块两种伪时间空间布局说明动机，Figure 2 展示完整模型和两阶段检验。

### 2. 输入、输出和必要前提

输入包括基因 × spot 的计数矩阵、每个 spot 的二维坐标、一个或多个名为 `lineage*` 的伪时间列、可选协变量、以及用于估计伪时间的 signature genes。`CreateTessaObject()`按 spot 名称对齐表达和元数据，并要求 signature gene 列表非空（`TESSA_code/R/TESSA.R:59-115`）。

输出按 lineage 保存：

- Stage 1：每个基因的 uTSVG 原始/BY 校正 p 值，以及需要 LOO 的 signature genes；
- Stage 2：每个候选基因的 `TVG_pvs(_adj)`和 `SVG_pvs(_adj)`；
- 多 lineage 结果可用 `get_Test1_result()`与 `get_Test2_result()`汇总。

TESSA 本身不是通用轨迹发现器。正常运行需要用户先给出有生物学意义的 signature genes 和 lineage；LOO 时才在内部用 PCA + Slingshot 重新估计被测试基因对应的伪时间。

### 3. 预处理如何接近高斯模型假设

原始计数不满足线性混合模型的正态、近似同方差假设。`NormalizeVST()`先从跨基因均值—方差关系估计负二项离散度 $\phi$：

$$
\operatorname{Var}(Y)\approx\operatorname{E}(Y)+\phi\operatorname{E}(Y)^2,
$$

再计算 $\log(Y+1/(2\phi))$，并逐基因回归掉总 library size；多样本时也回归 `Sample_ID`（`TESSA.R:118-135`）。`data_preprocess()`还过滤低总计数 spot、线粒体基因和低检出率基因，并把坐标与 lineage 伪时间做 min-max 缩放（`155-217`）。

实现对二维坐标整体使用一个全局最小值和最大值，对所有 lineage 列也整体缩放（`175-179`），而不是分别缩放每一列。这是确定的代码行为，可能影响不同轴/lineage 的相对数值尺度。

### 4. 核心模型：把表达协方差分成三部分

对基因 $g$在 $n$ 个 spot 上的标准化表达 $\mathbf y_g$：

$$
\mathbf y_g=\mathbf X\boldsymbol\beta_g+
\boldsymbol\gamma_g(t)+\boldsymbol\alpha_g(s)+\boldsymbol\varepsilon_g,
$$

其中：

$$
\boldsymbol\gamma_g(t)\sim N(0,\tau_t\mathbf K_t),\quad
\boldsymbol\alpha_g(s)\sim N(0,\tau_s\mathbf K_s),\quad
\boldsymbol\varepsilon_g\sim N(0,\tau_e\mathbf I).
$$

边际协方差为：

$$
\mathbf V_g=\tau_t\mathbf K_t+	au_s\mathbf K_s+	au_e\mathbf I.
$$

$\tau_t>0$表示相近伪时间的 spot 有协同表达，即 TVG；$\tau_s>0$表示相近空间位置有额外协同表达，即 SVG。两种效应是加性的：高度相关的空间和伪时间核可能使分量拆分不稳定，因此 Stage 2 的解释依赖两个核包含足够不同的信息。

### 5. 空间核和时间核如何构造

两者都使用经 min-max 归一化的平方距离高斯核：

$$
K_{ij}=\exp\left[-\frac{\operatorname{MinMax}(d_{ij}^2)}{h}\right].
$$

对应代码是 `gaussian_distance_normalized_kernel()`（`TESSA.R:222-236`）。多样本时，空间核按样本分别计算后组成块对角矩阵，表示不同切片没有直接空间邻接；时间核则跨样本共同计算，让相同进展阶段可以跨样本相似（`247-279`）。两种核都加 $10^{-9}\mathbf I$抖动以改善数值稳定性。

带宽不是从坐标距离直接选，而是对每个样本的基因表达用 Sheather–Jones（平均样本 spot 数 <5000）或 normal-reference bandwidth，再取全体中位数，且同一个带宽用于空间与时间核（`291-323`）。这是实现的重要建模选择。

### 6. Stage 1：联合问“空间或轨迹效应是否存在”

Stage 1 检验：

$$
H_0^{(1)}:\tau_s=\tau_t=0.
$$

`Test1()`把空间核、时间核和误差核相加，通过固定效应投影构造二次型矩阵，再对所有基因计算：

$$
Q_g=\frac{\mathbf y_g^T\mathbf P\mathbf V\mathbf P\mathbf y_g}
{\mathbf y_g^T(\mathbf I-\mathbf H)\mathbf y_g}(n-p).
$$

实现位于 `TESSA.R:333-385`：先求协变量伪逆、投影核矩阵的特征值，再用 Davies 方法计算加权卡方尾概率；若 Davies 返回负数则用 Liu 近似回退，最后做 BY 校正。Stage 1 阳性只能说明至少一种结构存在，不能直接称作 TVG 或 SVG。

### 7. “double dipping”从哪里来

若用 signature gene $g$参与 PCA/Slingshot 得到伪时间 $\hat t$，再用同一个 $g$检验它与 $\hat t$ 的关联，就等于让被检验数据参与构造自己的解释变量。即使真实无轨迹效应，也会产生偏小 p 值。Figure 3 的模拟显示朴素 Slingshot 版本在 Stage 1 和 TVG 检验中明显膨胀 I 类错误，而 SVG 检验不直接使用基因推导的时间核，受影响较小。

TESSA 的 LOO 只针对既属于 signature genes、又在初检中达到指定阈值的候选：删掉 $g$，用其余 signature genes 重新 PCA + Slingshot，重建 $\mathbf K_t^{(-g)}$，再检验 $g$（`TESSA.R:420-487`）。最后把校正后的单基因 p 值替换回完整向量并重新做 BY 校正。

这比把所有计数随机拆成两份更保留信号，但其有效性依赖“删除单个基因不会摧毁真实轨迹”。若某个驱动基因几乎独自定义轨迹，LOO 得到的不是同一个估计问题。

### 8. Stage 2：分别定位 TVG 与 SVG

Stage 2 对候选基因逐分量检验：

$$
H_{0,t}^{(2)}:\tau_t=0,\qquad
H_{0,s}^{(2)}:\tau_s=0.
$$

检验某个核 $\mathbf K_{alt}$时，先用 `gaston::lmm.aireml`拟合只包含另一个核的约化模型，构造其协方差 $\mathbf V_0$和 GLS 投影 $\mathbf P_0$，然后计算：

$$
Q=\frac12\mathbf y^T\mathbf P_0\mathbf K_{alt}\mathbf P_0\mathbf y.
$$

代码再用有效 Fisher 信息得到缩放系数和自由度，以缩放卡方分布求 p 值（`TESSA.R:588-633`）。`run_Test2_lineage()`分别测试 `kernel_S`和 `kernel_T`，并对两组 p 值各自做 BY 校正（`643-703`）。

LOO 只在 TVG 检验且基因属于 double-dipping 候选时重估伪时间；SVG 检验继续使用原对象（`668-690`），与论文的误差来源判断一致。

### 9. 多 lineage 与多样本的含义

`build_kernelMatrix()`为每个名称含 `lineage` 的元数据列单独建一组空间/时间核；`run_Test1()`和 `run_Test2()`也逐 lineage 独立运行。它不是在一个模型中联合估计所有 lineage 的：

$$
\mathbf V\ne\sum_l\tau_{t,l}\mathbf K_{t,l}+\tau_s\mathbf K_s+\tau_e\mathbf I.
$$

因此一个基因可在多个 lineage 中分别显著，跨 lineage 的多重检验范围也需由分析者明确。多样本的 block-diagonal 空间核与共享时间核是合理的集成假设，但仍要求样本间伪时间方向和尺度可比。

### 10. 完整运行图

```text
counts + (x, y) + lineage pseudotime + signature genes
    ↓ CreateTessaObject / data_preprocess
VST expression + scaled metadata
    ↓ build_kernelMatrix
sample-block spatial Ks + cross-sample temporal Kt + I
    ↓ Stage 1 Test1
uTSVG candidates: tau_s or tau_t nonzero
    ↓ signature candidate LOO
delete gene → PCA → Slingshot → rebuild Kt → replace p-value
    ↓ Stage 2 Test2
TVG p-values + SVG p-values
    ↓ lineage-wise BY correction and downstream domains/pathways
```

### 11. 论文验证应怎样理解

Figure 3–5 的负二项模拟把 oracle pseudotime、朴素 Slingshot、LOO、count splitting 与 SPARK 分开比较。主要证据是：LOO 把 Stage 1/TVG 的 I 类错误拉回约 0.05，同时比数据拆分保留更多功效；朴素版本的高 power 不能视为优势，因为伴随假阳性膨胀。

Figure 6–8 分析 PDAC、LUAD、STARmap 小鼠皮层和多样本人 DLPFC。uTSVG 特征在若干空间域任务中比仅用 SPARK SVG 得到更高 ARI，并揭示与肿瘤进展、免疫与皮层层次相关的区域/通路。这些是特定数据与下游算法的结果，不保证任何新数据上都优于 SVG 特征。

### 12. 论文—代码对应与边界

| 环节 | 本地证据 | 判断 |
|---|---|---|
| 对象与 spot 对齐 | `TESSA.R:59-115` | Exact |
| VST/QC/缩放 | `TESSA.R:118-217` | Exact |
| 时空高斯核 | `TESSA.R:222-323` | Exact |
| Stage 1 Davies/Liu score test | `TESSA.R:333-405` | Exact |
| Stage 1 LOO | `TESSA.R:420-493` | Exact |
| Stage 2 分量检验 | `TESSA.R:588-633` | Exact |
| Stage 2 TVG LOO 与 BY | `TESSA.R:643-703` | Exact |
| SVD/求逆后端 | `src/funcs.cpp:1-16` | Exact；薄封装 |
| 论文完整模拟与基准脚本 | R 包未提供 | Not found |
| 真实数据全部预处理/签名基因选择 | 教程和随附 PDAC 对象仅覆盖一部分 | Partial |

代码还存在需要运行前审查的细节：`CreateTessaObject()`的协变量索引方向可疑（`TESSA.R:95-98`）；Stage 2 构造 $\mathbf V_0$时循环中使用整个 `model.l$tau` 向量乘每个核（`604-608`），多核约化模型下可能发生 R 的回收规则。这些不会改变论文公式，却是复现结果时必须测试的实现风险。

### 13. 证据入口

- 主论文、方法、补充说明和扩展图：`paper.pdf`、`paper source/paper/paper.md`
- 图像：`paper source/paper/_page_*_Figure_*.jpeg`
- 核心 R 实现：`TESSA_code/R/TESSA.R`
- C++ 数值薄封装：`TESSA_code/src/funcs.cpp`
- 详细公式和逐图解读：`doc_method.md`、`figure_analysis.md`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## TESSA: A Unified Model to Detect Trajectory-Preserved and Spatially-Variable Genes in Spatial Transcriptomics

**Paper**: Wu Y, Su H, Steele N, Xie Y, Cui Y (2025). bioRxiv, 2025.09.06.674654.
**Code**: [https://github.com/Cui-STT-Lab/TESSA](https://github.com/Cui-STT-Lab/TESSA) (R package, GPL-3.0)

---

### Motivation & Novelty

#### Biological Problem
Spatial transcriptomics (ST) enables measurement of gene expression while preserving spatial context. A fundamental task is detecting **spatially variable genes (SVGs)** — genes whose expression patterns vary across tissue regions. However, biological processes like embryonic development, cell differentiation, and tumor progression are not only spatially heterogeneous but also **temporally dynamic**. Genes associated with developmental trajectories (pseudotime) may exhibit spatial patterns that conventional SVG methods fail to capture, because these methods rely on direct spatial variability rather than the underlying temporal dynamics.

**Concrete example**: In PDAC tissue, tumor progression from normal acinar → PaNIN → ductal carcinoma creates a pseudotime gradient that maps onto spatial regions. TVGs whose expression changes along this trajectory display spatial patterns mediated through the developmental process, not through direct spatial proximity. Standard SVG methods miss these trajectory-mediated spatial patterns.

#### Limitations of Existing Approaches
- **SVG detection methods** (e.g., SPARK, *Nature Methods*, 2020; SpatialDE, *Nature Methods*, 2018; nnSVG, *Nature Communications*, 2023) focus exclusively on spatial variability without modeling transcriptional changes along developmental stages
- **Pseudotime-based DE methods** (e.g., TradeSeq, *Nature Communications*, 2020; PseudotimeDE, *Genome Biology*, 2021; TSCAN, *Nucleic Acids Research*, 2016) were designed for scRNA-seq without spatial context
- **Double-dipping problem**: When using estimated pseudotime for hypothesis testing, the same data is used twice (for pseudotime estimation and for testing), leading to inflated type I errors. Existing corrections like Countsplit (*Biostatistics*, 2024) and DataThinning (*JMLR*, 2024) lose signal power through data splitting

#### Unique Contributions
1. **Unified statistical model** to detect both temporally variable genes (TVGs) and spatially variable genes (SVGs) in ST, termed TSVGs
2. **Two-stage testing framework**: Stage 1 identifies unified TSVGs (uTSVGs); Stage 2 dissects them into TVGs and SVGs
3. **Leave-One-Out (LOO) strategy** for double-dipping correction that maintains higher power than data-splitting approaches
4. **Multi-sample integration** for cross-sample TSVG detection

### Method Overview

TESSA decomposes gene expression variance into temporal, spatial, and noise components using a **linear mixed-effect model** with variance components:

$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \gamma(t) + \alpha(s) + \epsilon$$

where $\gamma(t) \sim \text{MVN}(0, \tau_t \mathbf{K}_t)$ captures temporal effects via a pseudotime kernel, $\alpha(s) \sim \text{MVN}(0, \tau_s \mathbf{K}_s)$ captures spatial effects via a spatial kernel, and $\epsilon \sim \text{MVN}(0, \tau_\varepsilon \mathbf{I})$ is residual noise. The marginal distribution is $\mathbf{y} \sim \text{MVN}(\mathbf{X}\boldsymbol{\beta}, \mathbf{V})$ with $\mathbf{V} = \tau_s \mathbf{K}_s + \tau_t \mathbf{K}_t + \tau_\varepsilon \mathbf{I}$.

#### Computational Pipeline
1. **Input**: Raw gene expression matrix (genes × spots), spatial coordinates, pseudotime (from Slingshot or user-defined), signature gene names
2. **Preprocessing**: MinMax scaling of coordinates/pseudotime → spot QC (≥10 counts) → MT gene removal → gene QC (≥10% expression rate) → VST normalization (Anscombe NB transform + library size regression)
3. **Kernel construction**: Gaussian kernels on MinMax-normalized pairwise distance matrices; bandwidth via Sheather-Jones (<5000 spots) or normal reference rule; spatial kernel is block-diagonal for multi-sample
4. **Stage 1 (Overall Test)**: Score test for $H_0: \tau_t = \tau_s = 0$ using Davies' method / Liu's approximation → identifies uTSVGs
5. **Stage 2 (Individual Tests)**: Variance component score tests for $H_0: \tau_s = 0$ (SVG) and $H_0: \tau_t = 0$ (TVG), using AIREML for null model estimation + scaled chi-square approximation
6. **LOO correction**: For signature genes only — remove test gene from signature set, re-estimate pseudotime via Slingshot, rebuild temporal kernel, re-test
7. **FDR control**: Benjamini–Yekutieli correction (conservative, valid under arbitrary dependence)

#### Key Assumptions
- Gene expression follows a multivariate normal distribution (after VST normalization)
- Spatial and temporal effects are additive and separable
- Gaussian kernel with a single bandwidth (rule-of-thumb selection) captures relevant correlations
- No single signature gene dominates pseudotime estimation (LOO assumption)

### Evaluation

#### Datasets
| Dataset | Technology | Spots/Cells | Genes | Application |
|---------|-----------|-------------|-------|-------------|
| PDAC S2A | 10x Visium | 3,142 | 17,943 | Pancreatic cancer progression |
| LUAD TD8 | 10x Visium | 1,760 | 36,601 | Lung adenocarcinoma |
| STARmap Mouse Cortex | STARmap | 3,190 (3 samples) | 166 | Visual cortex layers |
| Human DLPFC | 10x Visium | 18,033 (4 samples) | 33,538 | Dorsolateral prefrontal cortex |

#### Simulation Results (NB Scenario)

**Stage 1 Overall Test — Type I Error (FDR = 0.05)**:

| Method | Dispersion 0.7 | Dispersion 1 | Dispersion 1.5 |
|--------|---------------|-------------|----------------|
| TESSA-oracle | 0.046 | 0.051 | 0.051 |
| TESSA-slingshot | 0.225 | 0.220 | 0.223 |
| TESSA-slingshot-LOO | 0.051 | 0.048 | 0.052 |
| TESSA-slingshot-countsplit | 0.113 | 0.087 | 0.065 |
| SPARK | 0.054 | 0.051 | 0.053 |

**Stage 2 TVG Test — Type I Error**:

| Method | Dispersion 0.7 | Dispersion 1 | Dispersion 1.5 |
|--------|---------------|-------------|----------------|
| TESSA-slingshot | 0.140 | 0.147 | 0.137 |
| TESSA-slingshot-LOO | 0.052 | 0.063 | 0.050 |
| TESSA-slingshot-countsplit | 0.083 | 0.071 | 0.067 |

**Detection power**: TESSA-slingshot-LOO achieves highest AUC-ROC among non-oracle methods for both uTSVG and TVG detection. SPARK has near-zero power for TVG detection (not designed for it). Countsplit has lowest power due to signal attenuation from data splitting.

#### Comparative Methods
| Method | Type | Journal, Year |
|--------|------|---------------|
| SPARK (Gaussian) | SVG detection | *Nature Methods*, 2020 |
| Countsplit | Double-dipping correction | *Biostatistics*, 2024 |
| DataThinning | Double-dipping correction | *JMLR*, 2024 |
| SeuratPCA | Domain detection (downstream) | *Cell*, 2019 |
| SpatialPCA | Domain detection (downstream) | *Nature Communications*, 2022 |
| Slingshot | Pseudotime estimation | *BMC Genomics*, 2018 |

#### Key Findings
- **PDAC**: 6,956 uTSVGs (vs 7,205 SPARK SVGs, 6,309 overlap); uTSVGs captured PaNIN region (domain 6) and lymphoid aggregation (domain 10) that SPARK SVGs missed; TVGs enriched in immune activation pathways (NF-κB, immunodeficiency), SVGs in immune regulation (PD-L1, leukocyte migration)
- **LUAD**: 4,938 uTSVGs (vs 2,240 SPARK SVGs); identified TLS (domain 6) and tumor subclones; lineage-specific TVGs revealed three distinct trajectories — stromal (L1), macrophage/TAM (L2), adaptive immune (L3) — via GO enrichment
- **Mouse Cortex**: 110 uTSVGs (vs 63 SPARK SVGs); domain detection ARI 0.62 vs 0.49 (+27%)
- **Human DLPFC**: 1,519 uTSVGs (vs 685 SPARK SVGs); ARI 0.49 vs 0.45 (+9%)

### Limitations

1. **Scalability**: Kernel matrix operations require $O(n^2)$ storage and $O(n^3)$ inversion — becomes prohibitive for large datasets (>10K spots per sample). The paper acknowledges this and proposes nearest-neighbor approximation (as in nnSVG) for future work.
2. **Single kernel per type**: Uses one Gaussian kernel with a single bandwidth, unlike SPARK's 10-kernel Cauchy combination. May miss diverse spatial patterns with different length scales.
3. **Lineage-independent testing**: Each lineage is tested independently rather than jointly modeling all lineages ($\mathbf{V} = \sum_i \tau_{t_i} \mathbf{K}_{t_i} + \tau_s \mathbf{K}_s + \tau_\varepsilon \mathbf{I}$). Acknowledged as future work.
4. **Signature gene dependency**: Pseudotime quality depends on user-curated signature genes, requiring domain expertise. No automated gene selection is provided.
5. **LOO assumption**: Assumes no single signature gene dominates pseudotime estimation. If one gene drives the trajectory, LOO removal fundamentally changes the pseudotime structure.

### Data Availability

| Dataset | Accession |
|---------|-----------|
| PDAC | dbGaP PRJNA1124001; images at Zenodo 13379726 |
| LUAD | GEO GSE189487 |
| Mouse Cortex | [GitHub/BASS-Analysis](https://github.com/zhengli09/BASS-Analysis/tree/master/data) |
| Human DLPFC | [GitHub/HumanPilot](https://github.com/LieberInstitute/HumanPilot) |

### Reproducibility

**Rating: 4/5**

#### Strengths
- Complete R package with S4 class design, exported functions, and tutorial
- Example PDAC dataset included in package (`data/PDAC_S2A.rda`)
- Clear installation instructions via `devtools::install_github`
- All real datasets referenced with accession numbers (dbGaP, GEO, GitHub)
- Tutorial Rmd with step-by-step workflow

#### Potential Blockers
- Signature gene selection requires domain expertise (not automated)
- Pseudotime estimation quality depends on user-defined signature genes
- PDAC raw data requires dbGaP access (controlled access)
- No benchmarking scripts included in the repository
- Simulation code not provided in the package
- DESCRIPTION file has placeholder text (development state)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
