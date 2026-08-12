---
layout: default
permalink: /paper-atlas/spatiocad-9429241b/
title: "SpatioCAD"
nav: false
description: "SpatioCAD 不把 spot 中的基因计数直接当作可横向比较的“浓度”，而是用每个位置的总信号估计细胞密度，并让基因沿浓度差而不是绝对计数差在空间图上传播。真正有组织的空间图案需要较长时间才扩散到稳态，因此 characteristic diffusion time 越长，基因越靠前。 论文是 2026 年 bioRxiv 预印本，尚未经同行评审。"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>SpatioCAD</h1>
    <p>SpatioCAD: Context-aware graph diffusion model for pinpointing spatially variable genes in heterogeneous tissues</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.03.06.708087" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatioCAD：把细胞密度写进扩散过程的空间变异基因排序

### 一句话理解

SpatioCAD 不把 spot 中的基因计数直接当作可横向比较的“浓度”，而是用每个位置的总信号估计细胞密度，并让基因沿浓度差而不是绝对计数差在空间图上传播。真正有组织的空间图案需要较长时间才扩散到稳态，因此 characteristic diffusion time 越长，基因越靠前。

论文是 2026 年 bioRxiv 预印本，尚未经同行评审。以下解释以本地 42 页论文及补充、图/图注、CodeGraph 导航结果和 `code/SpatioCAD` 源码为证据。

### 1. SpatioCAD 要消除什么混杂

肿瘤区域往往细胞更多、UMI 总数更高。一个 housekeeping gene 即使每个细胞中的表达浓度完全不变，在高细胞密度 spot 中也会有更高总计数。只寻找“空间上高低有结构”的方法可能把这种 cellularity pattern 当成真正的基因调控。

设位置 $i$ 的基因量为 $x_i$，细胞密度代理为 $n_i$。真正应比较的是浓度 $x_i/n_i$。如果两个相邻位置满足

$$
\frac{x_i}{n_i}=\frac{x_j}{n_j},
$$

即使 $x_i\ne x_j$，它们也不应发生净扩散。这是 NAGD 与普通 count-based graph diffusion 的核心区别。

方法基于两个假设：有意义的空间信号在局部较平滑；有大尺度结构的信号比随机噪声更慢到达稳态。

### 2. 整体工作流

输入是 AnnData：`adata.X` 为 spot×gene 表达，`adata.obsm['spatial']` 为坐标。流程分两阶段：

1. 用标准图 Laplacian 的 Roughness Score 过滤高频噪声基因；
2. 用 cell-density-aware NAGD 计算剩余基因的 characteristic diffusion time，并跨多个 power transform 聚合排名。

输出主要是 `adata.var['robust_rank']` 和噪声标签。SpatioCAD 给的是相对排序，不直接给每个基因的正式 p 值或 FDR；论文中的 permutation p 值属于评估流程，而不是 `compute_SVG()` 的输出。

### 3. 空间图怎样构建

对 $N$ 个位置，默认

$$
k\approx\sqrt N,\qquad k'\approx0.5\log N.
$$

代码先在坐标空间找 kNN，只保留互为近邻的边。对边 $(i,j)$，以位置 $i$ 的第 $k'$ 个邻居距离作为局部尺度 $\sigma_i$，权重为

$$
a_{ij}=\exp\left(-\frac{d_{ij}^2}{\sigma_i\sigma_j}\right).
$$

互近邻减少单向长边，自适应尺度允许稠密区和稀疏区使用不同距离尺度。`model.py:71-103` 与论文图构造直接对应。

一个实现边界是 `local_scale_k` 由四舍五入得到；极小样本时可能为 0，代码将使用“自身距离”作为尺度并把零替换为 $10^{-5}$。论文面向的 Visium 规模不会触发典型问题，但小型测试数据需要保护。

### 4. 第一阶段：Roughness Score 过滤随机图案

普通扩散满足

$$
\frac{d\mathbf x(t)}{dt}=-L\mathbf x(t),
\qquad L=D-A.
$$

初始时刻的变化速率是 $-L\mathbf x(0)$，因此 Roughness Score 为

$$
RS_g=\lVert L\mathbf x_g(0)\rVert_2.
$$

局部连续图案在邻边两端变化小，RS 低；零散噪声在早期被快速平滑，RS 高。代码对全部基因的 RS 拟合 Gaussian mixture，候选分量数用 BIC 选择，把均值最高的分量视为 noise，再按 posterior probability 阈值打标签。

源码有重要细化：`model.py:138-149` 不是对 log-normalized abundance 直接算 RS，而是先把表达二值化为“是否非零”，再除以该基因出现的 spot 数。这样 RS 更接近表达位置的粗糙度，弱化表达量偏差；论文方法文字没有明确写出这一步。

默认也不完全一致：代码测试 `range(1,10)`，即 1–9 个分量，而论文写 1–10；代码 `probability_threshold=0.95`，论文文字为 0.9。结果复现必须记录实际值。

### 5. 第二阶段：Node-Attributed Graph Diffusion

普通扩散从绝对量差 $x_i-x_j$ 出发，最后趋向均匀信号；在细胞密度不均的组织中，这个稳态不合适。NAGD 的边流由浓度差驱动，并令稳定状态满足

$$
x_i^*\propto n_i.
$$

源码先从每个 spot 的归一化表达和得到 $n_i$，将其 Winsorize 到 1%–99% 分位并除以最小值，保证 $n_i\ge1$。然后做变量替换

$$
\hat x_i=\frac{x_i}{\sqrt{n_i}}.
$$

对边权使用

$$
\tilde a_{ij}=a_{ij}\frac{n_i+n_j}{2n_in_j},
$$

再由 `compute_node_attributed_laplacian()` 构造对称 NAGD Laplacian。代码分两步实现，看起来与论文 Eq. 9 不同，但展开后等价：对角项是 density-weighted loss，非对角项是 $N^{1/2}\tilde A N^{1/2}$。

稳态在 $\hat x$ 空间沿 $\sqrt n$ 方向；还原后即 $x^*\propto n$。因此“所有基因都向与密度成比例的同类稳态收敛”，扩散时间才可跨基因比较。

### 6. 用谱分解直接求 characteristic diffusion time

令 NAGD Laplacian 的非零特征对为 $(\lambda_s,v_s)$。初始信号在第 s 模式上的系数为

$$
\theta_s=v_s^\top\hat x(0).
$$

该模式随时间按 $e^{-\lambda_st}$ 衰减。若把“变化率足够小”定义为低于 $\epsilon=e^{-c}$，每个模式给出时间界，代码取最大值：

$$
t^*=\max_s\frac{\log(\lambda_s|\theta_s|)+c}{\lambda_s}.
$$

直觉上，慢特征值模式对应大尺度平滑结构；若基因在这些模式上的投影大，它会长时间保留空间图案，$t^*$ 大。随机高频噪声很快消失，$t^*$ 小，但它在进入 NAGD 前通常已由 RS 过滤。

代码只求最小的 50 个非零 eigenmodes，以 sparse `eigsh` 避免全矩阵分解；`compute_diff_time()` 在 log 前加 $10^{-12}$ 防止零投影。默认 `cutoff_error=10`，示例 notebook 使用 15，后者会系统性改变绝对时间，但最终排序可能较稳定。

### 7. 为什么做三种 power transform

对表达分别使用 $p\in\{1,1.5,2\}$：

$$
x^{(p)}=x^p,
$$

并在每次变换后把每个基因跨 spot 归一到总和 1。较大 p 强调峰值，p=1 保留原相对形状。每个 p 独立得到 diffusion-time rank。

最终不是平均排名，而是：对每个基因先把三个名次从好到坏排序成 tuple，再按 tuple lexicographic sort。例如 A 的名次 $(2,50,60)$ 变为 $(2,50,60)$，B 的 $(10,11,12)$ 变为 $(10,11,12)$；A 因最好名次 2 排在 B 前。这种规则优先“至少一种尺度下非常突出”的基因，而非三种变换都稳定靠前。用户应理解它是一种 rank aggregation 选择，不是统计显著性。

噪声基因被放回结果并统一赋 `max_non_noise_rank+1`，所以它们之间没有细分顺序。

### 8. 可选的 SVG 图案聚类

`cluster_gene()` 用 100 个 NAGD eigenmodes，把 top SVG 投影成 spectral diffusion profile，再 K-means 聚类。`compute_cluster_patterns()` 在每个位置计算 cluster genes 的表达投票：至少 20% cluster genes 非零时显示平均信号。

这一步帮助把 SVG 分成共同空间域，但 cluster 数默认 6 是用户参数，不是数据自动证明的真实组织区室。图案投票还使用 `layers['counts']`；该层只有通过 `read_h5ad()` 才自动创建，如果用户直接以 `SpatioCAD(adata)` 构造对象，需自行确认该 layer 存在。

### 9. 图和实验结果怎样读

#### Figure 1：方法图

A 展示空间图、density 与标准扩散早期变化，用 RS 筛掉噪声；B 展示 NAGD 使信号收敛到 density-proportional steady state，并以扩散时间排名。这里的“cell density”在代码里实际上是归一化表达总和代理，并非显微镜直接计数。

#### Figure 2：模拟

两种 tissue layouts 各含五个 domain，高密度 E 为 tumor core；900 个 background、200 个 SVG，并比较有无 50 个 noise genes。FDR=0.1 时，全局 power 报告为 0.99/0.98；在最困难的高密度 E，SpatioCAD 为 0.96/0.78，其余方法低于 0.3。模拟是按 cell-density×spatial-variability 的生成机制构造，优势最直接支持与该机制匹配的场景。

#### Figure 3–5：乳腺癌

Figure 3 用 UMI-rich tumor regions、RS mixture、housekeeping negatives 说明 density confounding；Figure 4 比较表达量偏差和功能多样性，并展示低表达候选如 `CHIT1`、`SLC5A1`、`ERN2`；Figure 5 与 STMiner 比较 reconstruction MAE、Moran's I、permutation evidence 和代表图案。top-1000 统一比较便于方法间对齐，却不等于所有方法的最佳显著性阈值。

#### Figure 6–7：肺癌

结果重复显示较少 housekeeping overlap、较低 abundance correlation 和更连续的图案；SpatioCAD score 与表达 rank 的 Spearman 为 -0.30，仍不是严格为零。代表基因的功能解释属于候选生物学关联，不是机制验证。

#### Figure 8 与补充：胶质瘤

SpatioCAD 聚类图案划分 tumor core、invasive margin 与 reactive/peritumoral zones，并在另外两份恶性胶质瘤样本中复现主要结构。Supplementary Figs. 1–26 位于同一 42 页 PDF 后半部分，覆盖模拟失败案例、表达 cluster、富集、更多肿瘤图和 k/k' 参数分析。本地还保留 `_page_34` 至 `_page_41` 的补充页图像。

### 10. 代码—论文对应

| 机制 | 本地代码 | 状态 |
|---|---|---|
| MNN 与自适应 Gaussian 权重 | `model.py:71-103` | Exact |
| RS=$\|Lx\|_2$ | `model.py:138-150` | Partial：代码二值化并按出现 spot 数归一 |
| BIC-GMM 噪声过滤 | `model.py:152-215` | Partial：1–9、0.95 与论文不同 |
| density 估计与裁剪 | `utils.py:96-112` | Exact/实现细节 |
| NAGD Laplacian | `model.py:271-282`, `utils.py:40-66` | Exact algebraic equivalent |
| spectral $t^*$ | `utils.py:68-94` | Exact |
| 三个 power 与 lexicographic rank | `model.py:255-310` | Exact |
| SVG 图案聚类 | `model.py:331-431` | Exact/可选扩展 |
| 正式 gene-level p/FDR | 核心类无此输出 | Not found；论文 permutation 仅用于评估 |

### 11. 使用前检查清单

1. `adata.X` 是原始 counts、已归一化还是 log 值？是否与 `preprocess()` 的假设一致？
2. cell-density proxy 是否主要反映细胞数，而不是测序深度或平台技术偏差？
3. MNN 图是否连通，边界/稀疏区域是否形成孤立 component？多个零 eigenvalues 会影响谱解释。
4. RS 的二值化、GMM 分量范围和 posterior threshold 是否记录？
5. `cutoff_error`、eigenmode 数和 power transforms 是否与复现目标一致？
6. 是否检查排名对 top-k、图参数和密度估计的敏感性？
7. 是否把 `robust_rank` 误写成 p 值或 FDR 控制结果？
8. housekeeping、Moran's I 和重构误差是否只是辅助验证，而非真实 SVG 金标准？
9. 是否有独立切片/病人验证候选基因与组织区室？
10. 使用 cluster patterns 前，`layers['counts']` 是否真实存在且未被原地修改？

SpatioCAD 的核心思想是先定义符合细胞密度异质性的稳态，再比较各基因离这个稳态“有多远、要多久”。这一设计对 tumor-like density confounding 很有针对性；同时它仍依赖 density proxy、图结构和排名超参数，且当前证据来自预印本，使用时应把排名与统计显著性严格区分。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatioCAD: Context-Aware Graph Diffusion Model for Spatially Variable Gene Identification

Hao Wen, Qunlun Shen, Shuqin Zhang. *bioRxiv*, 2026. DOI: 10.64898/2026.03.06.708087

### Motivation & Novelty

#### Biological Problem
Identifying spatially variable genes (SVGs) in spatial transcriptomics data is essential for discovering region-specific molecular markers and understanding tissue architecture. However, heterogeneous tissues — particularly tumors — exhibit dramatic cell density variation across regions, creating a major confound: genes with uniform per-cell expression appear spatially variable at the spot level simply due to varying cellularity. This leads to widespread false positives in SVG detection, with housekeeping genes frequently misidentified as SVGs.

#### Limitations of Existing Approaches
- **SpatialDE** (*Nature Methods*, 2018) and **SPARK-X** (*Genome Biology*, 2021) test spatial variance without modeling cell density, misinterpreting density-driven heterogeneity as biological signal. SPARK-X identifies nearly all genes (including background) as spatially significant in heterogeneous tissues.
- **SpaGFT** (*Nature Communications*, 2024) uses graph Fourier transform but shows scenario-dependent performance, likely because its sensitivity depends on alignment between spatial patterns and graph Laplacian eigenvectors.
- **Sepal** (*Bioinformatics*, 2021) models diffusion to a uniform steady state, which fundamentally fails when the true steady state should be proportional to cell density.
- **STMiner** (*Cell Genomics*, 2025) addresses cellularity via optimal transport but is computationally prohibitive ($\sim$42,000 seconds vs 43 seconds for SpatioCAD on breast cancer data) and sensitive to expression outliers — its performance drops to near-zero when noise genes are present.
- All methods except SpatioCAD and STMiner show strong **expression-level bias**, systematically favoring highly expressed genes (Spearman $R = 0.71$–$0.92$) and missing low-abundance transcripts with important biological roles.

#### Unique Contributions
1. **Node-Attributed Graph Diffusion (NAGD) model**: Generalizes standard graph diffusion by driving signal flow based on *concentration gradients* ($x_i/n_i - x_j/n_j$) rather than absolute differences, explicitly decoupling spatial patterns from cell density variation.
2. **Characteristic diffusion time $t^*$**: A closed-form metric for spatial variability derived from the NAGD spectral decomposition. Theoretically guaranteed to be universally comparable across genes because all normalized signals converge to the same steady state (proportional to cell density).
3. **Expression-unbiased detection**: SpatioCAD achieves Spearman $R = -0.04$ (breast cancer) and $R = -0.30$ (lung cancer) between spatial variability and expression level, enabling discovery of low-abundance SVGs missed by all other methods.
4. **Roughness Score noise filtering**: A graph-diffusion-derived metric that adaptively removes high-frequency noise genes before SVG ranking, preventing them from confounding downstream analysis.
5. **975× speedup over STMiner**: $O((k+m)GN)$ complexity through sparse eigensolving and analytical $t^*$, completing in under 1 minute for typical Visium datasets.

---

### Method Overview

SpatioCAD is a two-stage computational framework:

**Stage 1 — Noise Filtering**: Constructs a mutual k-nearest neighbor spatial graph with adaptive Gaussian kernel weights. Computes a Roughness Score (RS) for each gene based on signal variation during initial diffusion — structured genes have low RS (locally consistent), noise genes have high RS. A Gaussian Mixture Model with BIC-optimized components adaptively thresholds noise genes.

**Stage 2 — SVG Ranking**: For remaining genes, builds the NAGD Laplacian $\mathbf{L}_{ND}$ that incorporates per-spot cell density as node attributes and communication channel weights. Performs partial spectral decomposition (50 eigenmodes) and computes the characteristic diffusion time $t^*$ via a closed-form expression. To enhance robustness across the expression dynamic range, applies power transforms ($p \in \{1, 1.5, 2\}$) and aggregates rankings via lexicographic ordering.

Optional downstream: SVGs can be clustered by spatial diffusion profiles (K-means on spectral embedding) to identify distinct spatial gene modules, enabling functional dissection of tissue regions.

See doc_method.md for mathematical derivations and doc_code.md for implementation details.

---

### Evaluation

#### Datasets
| Dataset | Platform | Spots | Genes (filtered) | Source |
|---|---|---|---|---|
| Simulated (×2 scenarios) | — | 1,079 | 1,150 | SRTsim ZINB |
| Human breast cancer | 10X Visium | 4,992 | 17,633 | 10X Genomics |
| Human lung cancer | 10X Visium | 3,858 | 17,269 | 10X Genomics |
| Diffuse midline glioma (DMG1) | 10X Visium | 4,337 | 15,448 | GEO: GSE194329 |

#### Simulation Results
- SpatioCAD achieved statistical power of 0.99 (Scenario 1) and 0.98 (Scenario 2) at FDR=0.1, vs second-best STMiner at 0.87/0.88.
- In the tumor core domain (high cell density), SpatioCAD was the only method with meaningful detection (0.96/0.78 power), all others < 0.3.
- STMiner's power dropped to near-zero upon noise gene introduction; SpatioCAD maintained stable performance.

#### Real Data — Key Metrics
| Metric | SpatioCAD | STMiner | SpatialDE | SpaGFT | SPARK-X | Sepal |
|---|---|---|---|---|---|---|
| HK gene overlap (breast) | 26 | **2** | 191 | 216 | 368 | 88 |
| Expression bias MAD (breast) | **0.013** | 0.102 | 0.187 | 0.371 | 0.404 | 0.359 |
| Shannon entropy (breast) | **2.518** | 2.318 | 2.393 | 1.867 | 1.449 | 2.013 |
| Spearman R (breast) | **-0.04** | -0.58 | 0.71 | 0.83 | 0.90 | 0.92 |
| Spatial coherence MAE (breast) | **3.15** | 4.95 | — | — | — | — |
| Moran's I (breast) | **0.25** | 0.15 | — | — | — | — |
| Permutation-significant SVGs (breast) | **246** | 70 | — | — | — | — |
| Runtime — breast (seconds) | **43** | 41,983 | — | — | — | — |
| Runtime — lung (seconds) | **40** | 23,410 | — | — | — | — |

#### Biological Validation
- **Breast cancer**: SpatioCAD identified functionally relevant low-abundance SVGs — ZNF878 (zinc finger protein, DCIS pattern), GNG13 (chemokine receptor signaling, invasive region), CHIT1 (macrophage marker, focal DCIS), SLC5A1/SGLT1 (glucose transporter, proliferating regions), ERN2 (ER stress sensor), GRB14 (cell cycle regulator) — all missed by expression-biased methods.
- **Lung cancer**: Identified NOX4 (pulmonary fibrogenesis), KCP (anti-fibrotic BMP signaling), NSG1 (lung adenocarcinoma staging), SLC1A6 (survival predictor).
- **Glioma**: Six SVG clusters recapitulated tumor core (OLIG2, AURKA), tumor periphery/immune response (BCL2A1, S100A8), invasive zone (SPP1, TIMP1), white matter (PLP1, MAG), gray matter (ALDOC, NDRG2), and neuronal layer (NEFL, NEFM). GO/KEGG enrichment confirmed cell cycle dominance in the tumor cluster.

---

### Reproducibility

**Rating: 4/5**

**Strengths**:
- Code publicly available at https://github.com/kotone-429/SpatioCAD with MIT license
- Compact codebase (~593 lines), clean API, example notebook with complete workflow
- All three real datasets publicly accessible (10X Genomics, GEO)
- Standard dependencies (scanpy, scipy, scikit-learn)
- Fast runtime (< 1 minute for typical Visium datasets)

**Weaknesses**:
- No `setup.py` or `pyproject.toml` — manual dependency installation required
- No version pinning for dependencies
- No formal test suite
- Minor bug: `compute_cluster_patterns()` mutates `adata.layers['counts']` in-place for sparse matrices
- Code defaults differ from paper in a few places (noise threshold 0.95 vs 0.9, GMM range 1-9 vs 1-10)
- Simulation code not included in the repository

**Practical Notes**:
- Environment setup: `pip install scanpy[leiden] scipy numpy pandas anndata matplotlib scikit-learn`
- Input: standard AnnData h5ad with `obsm['spatial']` (10X Visium format)
- The notebook uses `cutoff_error=15.0` (stricter than the code default of 10.0)
- Preprocessing is built-in: `scad.preprocess()` handles filtering, normalization, and log-transform
- For non-Visium data, spatial coordinates must be in `adata.obsm['spatial']`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
