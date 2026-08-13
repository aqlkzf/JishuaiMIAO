---
layout: default
permalink: /paper-atlas/spagft-72a8e864/
title: "SpaGFT"
nav: false
description: "SpaGFT 不先假设空间基因一定是圆形热点、条带或梯度，而是把每个 spot、细胞或像素当作图节点，把分子表达当作图上的信号。相邻节点表达相似的组织结构，在图上变化缓慢，主要落在低频；快速交替或噪声更偏向高频。于是 SVG 识别、表达增强和功能组织单元（FTU）发现都能写成同一套图傅里叶运算。 论文 Figure 1 给出三条主线：从空间坐标构图并建立 Fourier modes（FM）；"
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
      <span>Spatially Variable Genes</span>
      <span>Nature Communications · 2024</span>
    </div>
    <h1>SpaGFT</h1>
    <p>Graph Fourier transform for spatial omics representation and analyses of complex organs</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-024-51590-5" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SpaGFT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/jxLiu-bio/SpaGFT" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpaGFT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpaGFT 方法解读：把空间组学信号搬到图频域

### 1. 这篇工作的核心视角

SpaGFT 不先假设空间基因一定是圆形热点、条带或梯度，而是把每个 spot、细胞或像素当作图节点，把分子表达当作图上的信号。相邻节点表达相似的组织结构，在图上变化缓慢，主要落在低频；快速交替或噪声更偏向高频。于是 SVG 识别、表达增强和功能组织单元（FTU）发现都能写成同一套图傅里叶运算。

论文 Figure 1 给出三条主线：从空间坐标构图并建立 Fourier modes（FM）；按低频 Fourier coefficients（FC）识别 SVG；再利用相似的频域模式组成可重叠的 tissue modules。主论文与补充 Note 1 共同给出公式和评测细节。

### 2. 输入输出

核心 Python API 接受 `AnnData`：行是空间节点，列是基因/蛋白，`adata.X`为标准化表达；坐标来自 `adata.obsm[spatial_key]`或 `adata.obs`列。

主要输出写回：

- `adata.var['gft_score']`和 `svg_rank`：基因空间平滑程度及排名；
- `cutoff_gft_score`、`pvalue`、`fdr`：SVG 两重筛选证据；
- `adata.varm['freq_domain_svg']`：每个基因的频域表示；
- FTU 的基因标签、伪表达与每个节点的二值支持矩阵；
- 低通增强后的表达矩阵。

### 3. 第一步：由坐标构建空间图

给定 $n$ 个节点坐标，代码用 KNN 建邻接图并经 `networkx.Graph`无向化（`SpaGFT/utils.py:14-68`）。默认邻居数为：

$$
K=\left\lceil\frac{\sqrt n}{2}\right\rceil,
$$

而 $n\leq500$时固定为 4（`SpaGFT/gft.py:269-285`）。令无向邻接矩阵为 $\mathbf A$、度矩阵为 $\mathbf D$，默认使用非归一化 Laplacian：

$$
\mathbf L=\mathbf D-\mathbf A.
$$

也可选择 $\mathbf I-\mathbf D^{-1/2}\mathbf A\mathbf D^{-1/2}$（`utils.py:55-66`）。邻居数决定什么尺度算“局部”：图太稀可能断开，太密会抹平窄小结构，因此它不是纯计算参数。

### 4. 图傅里叶基：频率是图上的粗糙度

对称 Laplacian 可分解为：

$$
\mathbf L=\mathbf U\boldsymbol\Lambda\mathbf U^T,
$$

其中 $\mathbf u_k$是 FM，$\lambda_k$是其图频率。因为：

$$
\mathbf u_k^T\mathbf L\mathbf u_k
=\frac12\sum_{i,j}A_{ij}(u_{k,i}-u_{k,j})^2=\lambda_k,
$$

小特征值对应邻居间变化小的平滑模式，大特征值对应快速振荡。实现不做完整 $n\times n$分解，而用 `eigsh(which='SM')`和 `eigsh(which='LM')`各取约 $\sqrt n$个低频/高频向量（`gft.py:302-329`），因此频域表示是任务导向的部分谱。

### 5. 把一个基因变换到图频域

对基因 $g$在所有节点上的 z-score 信号 $\mathbf f_g$：

$$
\widehat{\mathbf f}_g=\mathbf U^T\mathbf f_g.
$$

每个 $|\hat f_{g,k}|$表示第 $k$个 FM 对该空间模式的贡献。`detect_svg()`先用 `sklearn.preprocessing.scale`标准化每个基因，再做矩阵乘法并取绝对值（`gft.py:331-340`）。若 `filter_peaks=True`，代码分别在低频、高频段把不超过该基因段内中位数的 FC 置零，再对每个基因做 L1 归一化（`342-354`）。所以实际 GFTscore 基于经过峰值筛选的相对 FC，而不是原始谱能量。

### 6. SVG 识别是“低频集中度 + 统计显著性”

论文定义低频加权分数：

$$
\operatorname{GFTscore}(g)
=\sum_k e^{-\lambda_k}\widetilde f_{g,k},
\qquad
\widetilde f_{g,k}=\frac{|\hat f_{g,k}|}{\sum_j|\hat f_{g,j}|}.
$$

实现还除以均匀频谱的期望加权分数，让分数具有相对基准（`gft.py:352-361`）。基因按分数降序后，Kneedle 在排名—分数曲线寻找肘点，默认敏感度 `S=6`（`373-382`）。

第二个门槛比较该基因低频 FC 与高频 FC，检验低频是否更大；随后用 Benjamini–Yekutieli 方法计算 FDR（`gft.py:394-404`）。实际 FTU 默认选择同时满足 Kneedle cutoff 和 `fdr < 0.05`的基因（`gft.py:676-681`）。因此高排名本身不是完整显著性判定。

直接代码暴露一个重要差异：`test_significant_freq()`若任一频段的非零 FC 数较少，会把相同样本重复拼接到最多三轮，再做单侧 `ranksums`（`utils.py:435-482`）。重复观测并没有增加独立信息，却会改变秩和检验的样本量与 p 值；这一做法未在论文公式中说明，复用显著性结果时应单独做敏感性检查。

### 7. 低通增强：保留原信号还是追求空间平滑

SpaGFT 将观测表达看成真实平滑信号加高频噪声，求解：

$$
\mathbf f_g^*=\arg\min_{\mathbf f}
\left(\|\mathbf f-\mathbf f_g\|_2^2+c\mathbf f^T\mathbf L\mathbf f\right).
$$

闭式解是：

$$
\mathbf f_g^*=\mathbf U(\mathbf I+c\boldsymbol\Lambda)^{-1}
\mathbf U^T\mathbf f_g.
$$

频率越高，乘子 $1/(1+c\lambda_k)$越小。`low_pass_enhancement()`实现这个滤波并把负重构值截为 0（`gft.py:81-115`）。实现只使用所计算的低频 FM，因此更准确地说是“低频子空间重构 + 衰减”，不是在完整谱上的精确闭式解。作者也提醒它对真正 SVG 更合理；把任意非空间基因强行平滑可能制造视觉结构。

### 8. 从 SVG 聚类到可重叠 FTU

`identify_ftu()`对 SVG 仅计算低频 FC，在基因频域表示上构建近邻图并做 Louvain 聚类（`gft.py:593-708`）。同一簇中的基因共享相似空间尺度和形状，构成一个候选组织模块。

对每个基因簇，代码把成员表达相加得到节点伪表达，再用 KMeans($k=2$)划分低/高节点，并通过中位数方向校正标签（`730-751`、`777-799`）。不同模块分别二值化，所以同一节点可以支持多个 FTU；这正是它与互斥空间域聚类的区别。

若给出一组 Louvain resolution，代码计算模块二值图之间的平均余弦重叠并选择重叠较小的分辨率（`709-761`）。最小重叠是一种模块可分辨性启发式，不保证对应唯一生物学层级；用户仍需结合标记基因和组织形态解释。

### 9. 端到端数据流

```text
AnnData 表达矩阵 + 空间坐标
        ↓ KNN 无向图
邻接 A → 度 D → Laplacian L
        ↓ 部分特征分解
低频/高频 FM 与频率 λ
        ↓ U^T f
每个基因的 FC 频谱
        ├─ 低频加权 + Kneedle + BY-FDR → SVG
        ├─ 1/(1+cλ) 低通 → 表达增强
        └─ SVG 低频谱 Louvain → 基因模块
                              ↓ 伪表达 + KMeans(2)
                         可重叠的 FTU 节点集合
```

### 10. 如何阅读论文验证

论文用来自多平台的 32 个数据集，并从文献候选中经 Allen Brain Atlas 原位杂交整理 458 个脑 SVG 基准。Supplementary Data 说明了 849 个候选到 458 个验证集合的来源；这个基准偏向已知组织/层特异标记，不能代表所有可能的空间变异形态。

Figure 2 比较 SVG 检出准确性与速度；Figure 3 评估低通增强对空间域识别的帮助；Figure 4 用淋巴结展示 T 区、B 区、germinal center 及其重叠；Figure 5 将框架扩展到 CODEX 扁桃体；后续图展示把 FC 作为可解释特征或正则项嵌入 SpaGCN、TACCO、Tangram 和 CAMPA。这里的库直接覆盖 GFT/SVG/增强/FTU 核心，机器学习改造主要在 notebook 或外部实验代码中，并非统一的稳定 API。

### 11. 论文—代码对应与边界

| 环节 | 本地证据 | 判断 |
|---|---|---|
| KNN 与 Laplacian | `SpaGFT/utils.py:14-68` | Exact |
| 部分谱分解与 GFT | `SpaGFT/gft.py:302-340` | Exact |
| GFTscore 与 Kneedle | `SpaGFT/gft.py:342-382` | Exact |
| 低/高频统计与 BY-FDR | `SpaGFT/utils.py:435-482`, `gft.py:394-404` | Partial：存在未说明的样本复制 |
| 低通表达增强 | `SpaGFT/gft.py:15-115` | Partial：只重构已算出的低频子空间 |
| FTU 基因聚类与节点二值化 | `SpaGFT/gft.py:593-820` | Exact |
| 命令行报告与绘图 | `source/spatial/spg.py` | Exact/Partial：独立于安装包 API |
| SpaGCN 集成 | notebook/文档 | Partial |
| TACCO、Tangram、CAMPA 修改 | 论文描述和实验材料，核心库无通用函数 | Not found in library |

### 12. 最容易误读的四点

1. “低频”由当前样本的空间图定义，不同组织拓扑的 FM 坐标不能直接逐维比较。
2. GFTscore 偏好平滑大尺度模式；真实的中高频、稀有小结构可能被降权。
3. 低通增强会把图拓扑假设写入表达，不能当成无偏恢复的原始观测。
4. FTU 是共享频谱的基因模块及其高伪表达节点集合，不等同于已验证的解剖学功能单位。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpaGFT -- Paper Summary

### Full Title
Graph Fourier transform for spatial omics representation and analyses of complex organs

### Citation
Chang Y, Liu J, Jiang Y, Ma A, Yeo YY, Guo Q, McNutt M, Krull JE, Rodig SJ, Barouch DH, Nolan GP, Xu D, Jiang S, Li Z, Liu B, Ma Q. Graph Fourier transform for spatial omics representation and analyses of complex organs. *Nature Communications* **15**, 7467 (2024). DOI: [10.1038/s41467-024-51590-5](https://doi.org/10.1038/s41467-024-51590-5)

### Problem Statement

Spatial omics technologies generate multi-resolution data (subcellular, cellular, multicellular) capturing molecular profiles in tissue context. Understanding functional tissue units (FTUs) -- recurring multicellular regions with specific physiologic functions -- requires bridging cell-centric (spatial domains, neighborhoods) and gene-centric (SVGs, expression imputation) analyses. Existing approaches have three key limitations:

1. **Pre-defined pattern assumptions**: Methods like SPARK assume radial hotspot, curve belt, or gradient streak patterns, missing irregular spatial organizations
2. **Black-box representations**: Graph neural network methods produce task-specific embeddings without interpretable features
3. **Scalability**: Many SVG detection tools cannot handle large-scale datasets efficiently

### Core Idea

SpaGFT applies **graph signal processing** to spatial omics data. The key insight is that spatially organized biological signals (e.g., gene expression patterns defining tissue regions) are **smooth signals on a spatial graph** -- they vary slowly across neighboring cells/spots. In the frequency domain obtained via Graph Fourier Transform (GFT), these signals concentrate in the low-frequency band. This property enables:

- SVG detection as a **k-bandlimited signal recognition** problem
- Expression imputation via **low-pass filtering** in the frequency domain
- FTU identification by **clustering genes with similar frequency signatures**
- Integration into ML frameworks as an **explainable regularizer**

### Mathematical Framework

#### Graph Construction
Given $n$ spots with spatial coordinates, construct a KNN graph $G = (V, E)$ with $K = \sqrt{n}$ neighbors. The unnormalized Laplacian:

$$L = D - A$$

where $A$ is the binary adjacency matrix and $D$ is the degree matrix.

#### Spectral Decomposition and GFT
Eigen-decompose $L = U \Lambda U^T$ where columns of $U$ are **Fourier modes (FMs)** and eigenvalues $\lambda_k$ are frequencies. The smoothness of the $k$-th FM equals $\lambda_k$ (proven via quadratic form $\mu_k^T L \mu_k = \lambda_k$).

The Graph Fourier Transform of a gene signal $f_g$:

$$\hat{f}_g = U^T f_g$$

Each coefficient $\hat{f}_g^k$ measures the contribution of FM $\mu_k$ to the gene's spatial pattern.

#### SVG Detection (GFTscore)
Genes are scored by their concentration in low-frequency FMs:

$$\text{GFTscore}(f_g) = \sum_{k=1}^{n} e^{-\lambda_k} \tilde{f}_g^k$$

where $\tilde{f}_g^k = |\hat{f}_g^k| / \sum_i |\hat{f}_g^i|$ are normalized FCs. The exponential weighting emphasizes low-frequency contributions. SVGs are determined by: (1) GFTscore above the Kneedle algorithm inflection point, and (2) significantly higher low-frequency FCs than high-frequency FCs (Wilcoxon rank-sum test, FDR < 0.05).

#### Gene Expression Enhancement
For an observed signal $f_g = \bar{f}_g + \epsilon_g$, the enhanced signal minimizes:

$$f_g^* = \arg\min_f \left[ \|f - f_g\|^2 + c \cdot f^T L f \right]$$

Closed-form solution via low-pass filter:

$$f_g^* = U (I + c\Lambda)^{-1} U^T f_g$$

The filter $(I + c\Lambda)^{-1}$ attenuates high-frequency (noisy) components.

#### FTU Identification
SVGs are clustered in the Fourier coefficient space using Louvain algorithm. Each SVG cluster defines an FTU by computing pseudo-expression and applying KMeans(k=2) to identify high-expression spots. The optimal resolution minimizes average pairwise overlap between FTUs.

### Key Results

#### SVG Detection Benchmarking
- **31 datasets** (30 Visium + 2 Slide-seqV2, human/mouse brain)
- **458 curated benchmark SVGs** from 5 publications, validated via Allen Brain Atlas ISH
- SpaGFT achieved highest median Jaccard Index across grid search and independent tests
- **100x faster** than SPARK, SpatialDE, MERINGUE, SpaGCN, scGCO; 2x faster than SPARK-X on Visium (but slower on Slide-seqV2)

#### Gene Expression Enhancement
- 16 human brain datasets with annotated spatial domains
- SpaGFT outperformed Sprod, SAVER-X, scVI, netNMF-sc, MAGIC, DCA in ARI
- Works across technologies: Visium, SPOTS, CODEX

#### Biological Applications
1. **Human lymph node (Visium)**: Identified 1,346 SVGs in 9 clusters. Three FTUs mapped to T cell zone, B cell zone, and germinal center. Overlapping spots revealed polyfunctional regions (614 GC-B, 158 GC-T, 93 B-T, 26 tri-zone spots).

2. **Human tonsil (CODEX)**: 49-plex CODEX at 0.37 um/pixel. SpaGFT on downsampled 200x200 pixel images identified secondary follicle heterogeneity -- mantle zones (CD20+/BCL-2+), GC T follicular helper cells (PD-1+/CD57+), FDC/macrophage networks. Captured morphological, cellular, and molecular variability.

3. **ML framework integration**:
   - SpaGCN: +7.8-42.6% ARI improvement (8/10 datasets) via FC feature concatenation
   - TACCO: 8.7-14.9% L2 error reduction via topological OT regularization
   - Tangram: 7.4-15.9% Pearson correlation improvement via frequency-domain constraints
   - CAMPA: Faster convergence + identification of rare subcellular organelles (Cajal bodies at 0.16% pixels/cell, Set1/COMPASS at 0.10%) via entropy regularization

### Limitations (Acknowledged by Authors)

1. Focuses on low-frequency signals; medium/high-frequency biological signals (analogous to fMRI working memory vs acute stimuli) remain unexplored
2. Computational complexity is $O(n^2)$; could be reduced to $O(n \log n)$ with fast GFT algorithms
3. Different tissue topologies yield incomparable FM spaces (analogous to batch effects in scRNA-seq)
4. CODEX image analysis requires expert knowledge for region pre-selection; automated detection needed

### Significance

SpaGFT provides the first systematic application of graph signal processing to spatial omics, bridging signal processing theory with computational biology. It offers:
- **Interpretability**: FMs and FCs have clear mathematical meaning (spatial smoothness at different scales)
- **Generality**: Works across subcellular (4i), cellular (CODEX), and multicellular (Visium) resolutions
- **Composability**: Integrates into existing ML pipelines as features or regularizers
- The curated 458-gene SVG benchmark for mouse/human brain is a standalone contribution

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
