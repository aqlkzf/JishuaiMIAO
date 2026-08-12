---
layout: default
permalink: /paper-atlas/smopca-eefac3b2/
title: "SMOPCA"
nav: false
description: "SMOPCA 同时接收多个模态的“特征 × 空间位点”矩阵和位点坐标，用一个共享低维矩阵解释各模态，再用空间核约束相邻位点的低维表示应当相关。模型输出连续嵌入；论文中的空间域标签是随后在该嵌入上运行 K-means 得到的，并不是 SMOPCA 类自身学习的结果。"
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
      <span>Domain Clustering</span>
      <span>Genome Biology · 2025</span>
    </div>
    <h1>SMOPCA</h1>
    <p>SMOPCA: spatially aware dimension reduction integrating multi-omics improves the efficiency of spatial domain detection</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/s13059-025-03576-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SMOPCA 方法解读：把空间邻近性写进多组学共同表示

### 一句话理解

SMOPCA 同时接收多个模态的“特征 × 空间位点”矩阵和位点坐标，用一个共享低维矩阵解释各模态，再用空间核约束相邻位点的低维表示应当相关。模型输出连续嵌入；论文中的空间域标签是随后在该嵌入上运行 K-means 得到的，并不是 SMOPCA 类自身学习的结果。

### 输入、输出与证据边界

- 输入：第 $k$ 个模态 $Y_k\in\mathbb{R}^{m_k\times n}$，其中列是同一组 $n$ 个位点；坐标 $s_i$ 组成 `pos`（$n\times2$）。代码要求“特征在前、位点在后”，与 AnnData 常见方向相反。
- 输出：共享的 $d$ 维位点表示。代码内部 `self.Z` 是 $d\times n$，`calculatePosterior()` 实际返回其转置，即 $n\times d$；这与函数 docstring 写的返回形状一致，但现有旧文档曾把赋值语句方向读反。三个教程仍再次 `.T`，因此教程变量 `z` 实际是 $d\times n$，随后又以 `z.T` 送入 K-means。
- 聚类：K-means 在类外执行，且教程直接指定类别数（模拟 28、tonsil 7、thymus 8）。因此结果不证明模型能自动选择空间域数。

### 模型怎样把多组学与空间连接起来

每个模态共享同一个潜在矩阵 $Z$：

$$Y_k=W_kZ+E_k,$$

其中 $W_k$ 是模态特异载荷，$E_k$ 是方差为 $\sigma_k^2$ 的噪声。约束 $W_k^TW_k=I$ 解决旋转/尺度不可辨识，也让载荷可由特征分解更新。

对 $Z$ 的每一行（一个潜在因子在所有位点上的取值），论文放置同一个高斯过程先验：

$$Z_l^T\sim\mathrm{MVN}(0,\Sigma),\qquad \Sigma_{ij}=k_\gamma(s_i,s_j).$$

默认核是 $\nu=3/2$ 的 Matérn 核。直观上，距离近的位点在先验中更容易有相似的潜在分数；数据似然仍可推翻这一倾向，所以空间平滑不是硬约束。`src/model.py:67-97` 构造完整的 $n\times n$ 核并做特征分解，因此内存为 $O(n^2)$、主计算约为 $O(n^3)$。

### 参数估计和后验融合

`estimateParams()` 对每个模态交替更新：

1. 固定噪声方差，以核的特征值/特征向量构造矩阵 $G$，取最大的 $d$ 个特征向量作为 $W_k$。
2. 固定 $W_k$，在扫描得到的区间中用 Brent 求根更新 $\sigma_k^2$。
3. 若显式设置 `estimate_gamma=True`，再以有界标量优化更新核长度尺度，并重建核。

后验均值把所有模态按 $\alpha_k/\hat\sigma_k^2$ 加权：噪声估计越小或人工权重越大，模态贡献越大。默认 $\alpha_k=1$；`omics_weight=True` 时按“最大特征数/本模态特征数”上调小模态。这个规则是启发式权重，不等于从数据自动学习模态重要性。

论文的方差比较不能简化成“加入任何模态都严格更稳定”。其推论带有权重条件（特别是比较基准模态时需满足相应 $\alpha_k\ge1$）；它说明在模型假设和该条件下后验协方差不增，而不保证真实聚类一定更准确。

### 从图 1 到图 5 应该怎样读

- 图 1 是机制图：多模态矩阵经共享 $Z$ 汇合，坐标只通过核协方差进入，后验均值再供降维、聚类和差异分析使用。
- 图 2 展示模拟 CITE/SMAGE 和三模态 DLPFC 的聚类指标。它支持“在这些模拟设定中表现较好”，不能单独证明对任意噪声或任意模态数都占优。
- 图 3 的 tonsil 空间图、Moran's I/LISI 和标记物共同提供空间连续性与生物学一致性证据；但人工注释是参考而非无误真值，空间更平滑也不自动等于更正确。
- 图 4 在 Stereo-CITE-seq thymus 中比较空间域并展示标记物，支持皮质、髓质等区域的对应关系。
- 图 5 在 MISAR-seq 胚胎脑 RNA+ATAC 数据上比较嵌入和聚类。仓库没有覆盖该主结果的对应教程，因此属于论文报告、不是本地端到端复现实证。

### 非空间单细胞扩展的真正含义

论文把由同一批组学特征计算的 UMAP 坐标当作伪空间坐标。这里没有新增物理空间信息：核再次使用了数据自身形成的几何结构，因此提升更适合解释为流形正则化效果。它与表达/可及性信号并非独立证据，不能据此声称恢复了真实空间位置。

### 论文与代码的关键差异

1. 论文说默认自动学习长度尺度，`estimateParams()` 的代码默认却是 `estimate_gamma=False`；三个教程均显式打开它。
2. `f_gamma()` 在 `k==0` 时直接跳过，因此长度尺度目标不含第一个模态，与论文的全模态联合似然叙述不一致。
3. `estimateParams()` 的两个初值序列默认均为空，但立刻断言其长度等于模态数；无参数调用会失败。
4. 蛋白预处理调用 `clr_normalize_each_cell`，仓库没有定义或导入该函数，相关路径不能按代码原样运行。
5. `tsne` 核会原地执行 `self.pos *= length_scale`；重复建核会累计缩放坐标。
6. Gaussian 分支把参数写为 `gamma=1/length_scale`（另一分支为 $\exp(-d^2/length\_scale)$），其“length_scale”语义与常用 RBF 的 $1/(2\ell^2)$ 不同。
7. 默认 `intercept=True` 会为每个模态显式构造一个稠密 $n\times n$ 中心化矩阵；三个教程都关闭它。大数据时，这会在核矩阵之外再增加显著内存。
8. 仓库未发现自动化测试；三个 notebook 是使用示例，不能替代回归测试。

### 可复现的最小流程与结论边界

可靠复用至少需要：统一位点顺序并转置为特征×位点；自行完成 RNA/蛋白/ATAC 预处理；显式提供每个模态的 `sigma_init_list` 与 `sigma_xtol_list`；决定是否估计长度尺度；检查返回数组方向；最后独立选择 K-means 的 $K$。本地代码足以核对核心因子模型、核、交替估计和后验公式，但缺失 CLR、MISAR 主结果教程和自动测试，因此“核心实现可读”不等于“论文全部结果一键复现”。

### 直接证据

- 论文：`paper source/paper/auto/paper.md`（方法、定理、图 1–5 与数据/代码可用性）
- 图像：`paper source/paper/auto/images/`
- 核心实现：`src/model.py:13-256`
- 预处理：`src/utils.py:10-74`
- 推荐调用与聚类：`tutorial/*.ipynb`
- 代码快照：GitHub `cmhimself/SMOPCA`，提交 `9d59651d78149520661c57bab8a14d42446e6654`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SMOPCA Summary

**Full title**: SMOPCA: spatially aware dimension reduction integrating multi-omics improves the efficiency of spatial domain detection

**Authors**: Mo Chen, Ruihua Cheng, Jianuo He, Jun Chen, Jie Zhang

**Journal**: Genome Biology (2025) | **DOI**: 10.1186/s13059-025-03576-9

**Code**: https://github.com/cmhimself/SMOPCA | **License**: MIT

---

### Motivation & Novelty

#### Problem

Spatial multi-omics technologies (spatial-CITE-seq, Stereo-CITE-seq, MISAR-seq) simultaneously measure transcriptome, proteome, and/or epigenome with spatial coordinates. The key computational task is **spatial domain detection** — identifying tissue regions with coherent molecular profiles across modalities. Existing approaches either ignore spatial information (single-cell multi-omics methods like scMDC, TotalVI) or handle only one modality at a time (spatial methods like SpatialPCA).

#### Limitations of Existing Approaches

- **SpatialPCA** (*Nature Communications*, 2022): Models spatial dependencies for transcriptomics only; naive concatenation of modalities ignores their different noise levels and informativeness.
- **SpaVAE** (*Nature Methods*, 2024): Deep generative model for spatial omics, but architecturally limited to 2 modalities — requires network redesign for 3+.
- **SpatialGlue** (*Nature Methods*, 2024): Graph neural network with dual attention for spatial multi-omics, but caps at 2 modalities (3 with the extended SpatialGlue_3M variant, never 4+).
- **MEFISTO** (*Nature Methods*, 2022): Factor analysis supporting arbitrary modalities with spatial patterns, but computationally expensive and empirically less competitive.
- **scMDC** (*Nature Communications*, 2022), **TotalVI** (*Nature Methods*, 2021), **Seurat WNN** (*Cell*, 2021), **BREM-SC** (*Nucleic Acids Research*, 2020), **CiteFuse** (*Bioinformatics*, 2020): Multi-omics integration methods that assume cell independence, discarding spatial structure.

#### Unique Contributions

1. **First PCA-based model for spatial multi-omics**: Extends probabilistic PCA with a Gaussian process prior to handle $K \geq 2$ modalities natively — no architectural changes needed for 3, 4, or more modalities.
2. **Closed-form solutions**: Unlike deep learning alternatives, SMOPCA derives analytical MLE solutions for loading matrices $W_k$, making it computationally efficient and theoretically principled.
3. **Conditional variance result**: Under the theorem's model and weighting condition (including the relevant $\alpha_k\geq1$ comparison), integrated posterior covariance does not increase relative to the selected single-modality analysis; this is not an unconditional accuracy guarantee.
4. **Optional length-scale learning**: The paper describes marginal-likelihood estimation of $\gamma$. Code supports it, but its default is off and its objective skips modality 0; all three tutorials explicitly enable it.
5. **Applicability to single-cell data**: Using UMAP pseudo-coordinates as spatial proxy, SMOPCA extends to non-spatial multi-omics data.

---

### Method Overview

SMOPCA is a factor analysis model where each modality $Y_k = W_k Z + E_k$ shares a common latent factor matrix $Z$, with modality-specific loading matrices $W_k$ and noise variances $\sigma_k^2$. Each latent factor follows a multivariate normal prior with a kernel-based covariance matrix encoding spatial proximity (Matérn kernel, $\nu=3/2$, by default).

**Inference pipeline**:
1. Construct spatial kernel matrix $K$ and its eigen decomposition
2. Alternate between estimating $W_k$ (closed-form via spectral decomposition) and $\sigma_k^2$ (Brent root-finding) for each modality
3. Optionally learn length scale $\gamma$ via marginal likelihood optimization
4. Compute posterior mean of $Z$ as the final $n \times d$ embedding returned by `calculatePosterior()`
5. Apply K-means clustering on the embedding

**Key design choices**: Orthonormality constraint $W_k^T W_k = I_d$ ensures identifiability and enables closed-form solutions. Eigen decomposition of the kernel matrix is reused throughout, avoiding direct matrix inversion.

See doc_method.md for full mathematical derivation and doc_code.md for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Technology | Modalities | Spots/Cells | Source |
|---|---|---|---|---|
| PBMC, SLN111-D1/D2, SLN208-D1/D2 | CITE-seq | RNA + protein | 3.7K-8.9K | 10X / TotalVI repo |
| PBMC3K, PBMC10K | SMAGE-seq | RNA + ATAC | 3K, 10K | 10X |
| 12× DLPFC simulated | SRTsim (3 modalities) | Simulated 3-omics | 3-4K each | LIBD |
| Human tonsil | spatial-CITE-seq | RNA + protein | 2,491 | GEO GSE213264 |
| Mouse thymus | Stereo-CITE-seq | RNA + protein | 4,697 | Zenodo |
| Mouse brain E15.5 | MISAR-seq | RNA + ATAC | 1,949 | Zenodo |
| Mouse brain P22 | Spatial ATAC-RNA-seq | RNA + ATAC | 9,215 | Zenodo |

#### Metrics

- **AMI, NMI, ARI**: Clustering accuracy vs ground-truth labels (when available)
- **Moran's I**: Spatial autocorrelation of cluster assignments (higher = smoother)
- **LISI**: Local mixing of cluster labels (lower = less mixing = better)
- **McFadden pseudo-R²**: Predictive power of latent representations for true labels

#### Key Results

1. **Simulation I** (CITE-seq + SMAGE-seq with simulated coordinates): SMOPCA outperforms all 9+ competing methods (scMDC, SpatialPCA, TotalVI, Seurat, etc.) across AMI, NMI, ARI on all 7 datasets.
2. **Simulation II** (3-modality): SMOPCA outperforms PCA+K-means, SpatialPCA, SpaVAE, and SpatialGlue_3M on 12 DLPFC sections with statistically significant differences (paired t-test).
3. **Spatial-CITE-seq tonsil**: Achieves highest Moran's I and lowest LISI. Cluster annotations match known tonsil biology (GC zones, T cell zones, crypt epithelia). DE analysis identifies known markers (CD3/CD4 in T cells, CD21/IgM in GC B cells).
4. **Stereo-CITE-seq thymus**: Best Moran's I and LISI scores among 9 methods. Identifies expected thymic zones (medulla, cortex, capsule).
5. **MISAR-seq brain**: Best AMI/NMI/ARI and highest pseudo-R² among all methods. Latent embeddings clearly separate brain regions (forebrain, midbrain, hindbrain) that other methods entangle.
6. **Single-cell data with UMAP coordinates**: SMOPCA with pseudo-spatial coordinates outperforms non-spatial methods, demonstrating the value of UMAP-derived spatial regularization.
7. **Robustness**: Insensitive to kernel choice (Matérn, Gaussian, Cauchy), ν parameter, number of components, normalization method, and gene selection strategy.

#### Compared Methods (with citations)

| Method | Type | Journal | Year |
|---|---|---|---|
| SpatialPCA | Spatial dim. reduction | Nature Communications | 2022 |
| SpaVAE | Spatial deep generative | Nature Methods | 2024 |
| SpatialGlue | Spatial graph neural net | Nature Methods | 2024 |
| MEFISTO | Spatial factor analysis | Nature Methods | 2022 |
| scMDC | Multi-omics deep clustering | Nature Communications | 2022 |
| TotalVI | Multi-omics VAE | Nature Methods | 2021 |
| Seurat WNN | Weighted nearest neighbor | Cell | 2021 |
| BREM-SC | Bayesian random effects | Nucleic Acids Research | 2020 |
| CiteFuse | CITE-seq integration | Bioinformatics | 2020 |
| chromVAR | TF accessibility inference | Nature Methods | 2017 |
| cisTopic | ATAC topic modeling | Nature Methods | 2019 |
| PeakVI | ATAC deep generative | Cell Reports Methods | 2022 |
| SCALE | ATAC latent features | Nature Communications | 2019 |

---

### Reproducibility

**Rating: 4/5** (Good)

#### Strengths

- **Complete code**: Core model is 257 lines of clean Python, fully self-contained in one class
- **Tutorials**: 3 Jupyter notebooks covering simulation, spatial-CITE-seq, and Stereo-CITE-seq with full outputs
- **Data availability**: Preprocessed datasets on Zenodo (DOI: 10.5281/zenodo.15187362); raw data from public repositories (GEO, 10X, Zenodo)
- **PyPI package**: `pip install SMOPCA` for easy installation
- **Dependencies**: Standard scientific Python stack (numpy, scipy, scikit-learn, scanpy)
- **Simple API**: 3 method calls (init → estimateParams → calculatePosterior)
- **Fast**: Much faster than deep learning alternatives; no GPU required

#### Weaknesses

- **Missing CLR function**: `clr_normalize_each_cell` referenced in `utils.py` but not defined — Stereo-CITE-seq tutorial depends on it
- **R dependencies**: SVG selection (SPARK), DE analysis (Seurat FindMarkers), LISI computation, and pseudo-R² require R packages not included in the Python package
- **γ estimation default mismatch**: Code defaults to `estimate_gamma=False` but paper says "automatic by default"
- **γ objective mismatch**: the implementation excludes modality 0 from length-scale optimization
- **Required arguments have empty defaults**: calling `estimateParams()` without per-modality sigma initializers/tolerances fails its length assertion
- **No automated tests**: the three notebooks demonstrate selected workflows but do not cover regressions or all main-paper datasets
- **Preprocessing pipeline fragmented**: Different tutorials use different preprocessing; no unified pipeline script
- **No MISAR-seq tutorial**: The most complex dataset (ATAC + RNA) lacks a tutorial
- **Hyperparameter sensitivity**: `gamma_init` and `gamma_bound` vary across tutorials without guidance on how to choose them

#### Practical Notes

- **Environment**: Python 3.10 + pinned dependencies (numpy 1.23.5, scipy 1.10.0, scikit-learn 1.2.1, scanpy 1.9.1)
- **Memory**: Kernel matrix is $O(n^2)$; for 10K spots, expect ~800 MB. Not suitable for Visium HD or Slide-seq scale data without approximations.
- **Runtime**: Fast for typical spatial datasets (seconds to minutes for n < 5000). The $O(n^3)$ eigen decomposition becomes the bottleneck for larger datasets.
- **Gotcha**: Input matrices must be features × spots (not the usual spots × features convention in scanpy). Transpose before passing to SMOPCA.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
