---
layout: default
permalink: /paper-atlas/supermap-7c5ad30c/
title: "SuperMap"
nav: false
wide: true
description: "SuperMap 要解决的是“对角整合”中最困难的情形：RNA、ATAC、蛋白或 DNA 甲基化分别测自不同细胞，既没有细胞一一对应，也没有相同特征空间。它不先猜哪两个细胞配对，而是把问题写成无链接回归：如果两个样本来自足够相似的生物系统，那么未观测的 ATAC 细胞 RNA 分布应与实际 RNA 样本分布相近；借助这种分布相等、变量间协方差和基因组先验，可以学习一个从 ATAC 特征到 RNA 特征的线性映射。"
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
      <span>PNAS · 2026</span>
    </div>
    <h1>SuperMap</h1>
    <p>Bridging unpaired single-cell multimodal data for integrative analyses with SuperMap</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1073/pnas.2505182123" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for SuperMap">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/chaodeng-aca/SuperMap" target="_blank" rel="noopener noreferrer" aria-label="Open code for SuperMap">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SuperMap：没有细胞配对，怎样学习跨模态映射

SuperMap 要解决的是“对角整合”中最困难的情形：RNA、ATAC、蛋白或 DNA 甲基化分别测自不同细胞，既没有细胞一一对应，也没有相同特征空间。它不先猜哪两个细胞配对，而是把问题写成**无链接回归**：如果两个样本来自足够相似的生物系统，那么未观测的 ATAC 细胞 RNA 分布应与实际 RNA 样本分布相近；借助这种分布相等、变量间协方差和基因组先验，可以学习一个从 ATAC 特征到 RNA 特征的线性映射。

本解读依据 PMC 正文、五张主图、补充 PDF `pnas.2505182123.sapp.pdf`，以及官方 R 包快照 `SuperMap_code/`。代码来源为 `https://github.com/chaodeng-aca/SuperMap`，commit `a6899ffcd0f1e55f4268a8896eec8f3d95881e42`，`DESCRIPTION` 版本 1.0.0。以下实现结论只对应这个固定快照。

### 1. 从普通回归到“无链接”回归

设观测 RNA 数据为 $Y\in\mathbb R^{n_s\times p}$，ATAC 数据为 $X\in\mathbb R^{n_t\times q}$。$n_s$ 与 $n_t$ 可以不同；每一行来自不同细胞，因此普通监督回归所需的 $(x_i,y_i)$ 配对不存在。令 $Y^*$ 表示 ATAC 细胞真正但未测到的 RNA。SuperMap 作两层假设：

$$
y\overset d= y^*,
$$

即两个相似样本的 RNA 细胞群具有近似相同的联合分布；同时假定跨模态关系近似线性：

$$
y^*=Bx+\epsilon.
$$

合起来就是论文的工作模型：

$$
y\overset d=Bx+\epsilon,
$$

其中 $B\in\mathbb R^{p\times q}$ 是要学习的峰—基因映射，误差均值为零且协方差 $\Sigma$ 取对角形式。符号 $\overset d=$ 表示分布相等，不是细胞逐行相等；因此算法不会输出原始 RNA 细胞与 ATAC 细胞的真实配对。

Figure 1 很清楚地画出了这个区别：输入矩阵沿“细胞”和“特征”两个方向都没有重叠，中间只学习 feature-space mapping，右侧才把映射用于填补、整合、调控分析和轨迹分析。

### 2. 为什么只匹配单变量分布还不够

若只让每个预测基因的直方图与观测 RNA 一样，很多不同的 $B$ 都可能满足要求。SuperMap 用三部分共同限制解：

1. **边缘分布项**：逐基因比较观测 RNA 的经验 CDF 与 $Bx+\epsilon$ 的预测 CDF。
2. **成对交互项**：匹配 RNA 的二阶矩与映射后 ATAC 的二阶矩，保留基因间协方差结构。
3. **基因组先验项**：远离基因 TSS 的峰系数受到更强惩罚。

可概括为：

$$
\min_{B,\Sigma>0}\sum_i f_i(\beta_i,\sigma_i)
+\frac w2\left\|\frac{Y^TY}{n_s}-\Sigma-B\frac{X^TX}{n_t}B^T\right\|_F^2
+\frac\lambda2\|D\circ B\|_F^2.
$$

$f_i$ 是第 $i$ 个响应特征的 CDF 差异；默认 $w=2$、$\lambda=10^{-4}$。代码 `nls_diag()` 用 logistic CDF 近似正态卷积，从而可以用非线性最小二乘求梯度友好的边缘项。

### 3. 基因组先验其实有“硬窗口 + 软惩罚”两层

`gene_peak_distance()` 先按链方向确定 TSS：正链用 start，负链用 end。只有同染色体且距离 TSS **小于 200 kb** 的峰—基因对进入模型；没有邻近峰的基因和没有邻近基因的峰会被删除。这是硬稀疏掩码，窗口外 $B_{ij}$ 固定为零。

窗口内再使用

$$
D_{ij}=\exp(d_{ij}/d_0),\qquad d_0=100\text{ kb},
$$

对远端系数施加更大的 L2 惩罚。因此“数据可以推翻先验”只适用于 200 kb 窗口内；窗口外长程增强子在当前实现中根本没有估计自由度。这是解释调控分数时必须保留的边界。

### 4. ADMM 怎样把难问题拆成可计算的两块

SuperMap 引入辅助参数，把边缘分布匹配和协方差匹配分开，再用 ADMM 强制两套参数趋于一致。每轮包含三步。

#### 4.1 成对结构更新

`pairwise_optim()` 计算

$$
R=Y^TY/n_s,\qquad r=X^TX/n_t,
$$

逐基因更新 $B$ 与对角 $\Sigma$。在固定其他列时，该子问题变成带 ADMM 惩罚和距离先验的岭回归，代码使用 `pracma::pinv()` 求伪逆，以应对附近峰少或矩阵秩不足。第一轮内部更新 6 次，后续每轮 5 次，这是公开实现的 warm-start 细节。

#### 4.2 边缘分布更新

`marginal_nls()` 为每个基因独立调用 `nls_diag()`，使用 `minpack.lm::nls.lm` 的 Levenberg–Marquardt 法求解 CDF 匹配；每个基因最多 300 次 NLS 迭代，误差方差下界为 $10^{-10}$、上界为该基因观测方差。各基因可通过 `foreach` 并行，`bigmemory` 用于避免工作进程复制大矩阵。

#### 4.3 对偶变量更新

代码执行

$$
U\leftarrow U+A-B,
$$

把边缘子问题与成对子问题的参数拉回一致。`supermap()` 默认外层迭代 10 次，$\rho=1$；输入先按列中心化，完成后恢复截距

$$
\hat b_0=\bar Y-\bar X\hat B.
$$

返回值是 `estimate_b`、`estimated_intercept`、`estimated_sigma` 和收敛记录，而不是低维神经网络 embedding。

### 5. 为什么拟合前要做 metacell

单细胞 RNA 和 ATAC 都高度稀疏。论文建议先按各自低维邻域用 Leiden 聚类，将相似细胞聚合为 metacell，再在 metacell 层拟合 $B$。这样分布和协方差更稳定，样本数也显著减少。

代码中的两种聚合并不相同：

- `metacell_matrix_RNA()` 对 cluster 内原始计数取均值，再计算 log-CPM；
- `metacell_matrix_ATAC()` 先把每个峰二值化为 0/1，再取均值，所以结果是 cluster 内“该峰可及的细胞比例”。

论文把这一步概括为聚合平均，但 ATAC 二值化是直接代码中更具体的实现。graining level 是数据分析选择，不是包内强制常数；Figure 3f 只说明作者测试的范围内结果较稳定，不能推广为任意聚合尺度都无影响。

### 6. 单细胞插补为什么还要再平滑

学习到 $\hat B$ 后，metacell 插补直接计算：

$$
\hat Y^*_{meta}=[1,X_{meta}]\hat B_{+},
$$

其中 $\hat B_+$ 包含截距。单细胞 ATAC 更噪，`smooth_knn_atac()` 先在 LSI 空间用 Seurat `FindNeighbors` 建默认 $K=50$ 的 SNN 图，再按 Jaccard 权重平滑二值 ATAC，最后乘映射矩阵。

论文公式令 $\alpha$ 表示自身权重，默认 $\alpha=0.5$。代码局部变量 `alpha=0.6` 的语义却是**邻居总权重**：它把邻居权重归一化到 0.6，并把自身设为 $1-\alpha=0.4$。所以不能简单说“代码 alpha=0.6 与论文 0.5 仅数值不同”；参数角色也被反向命名。实际固定快照运行的是 40% 自身 + 60% 邻居。

插补仍是线性预测加平滑，不是生成式模型，也不提供逐细胞预测区间。若两个样本的细胞类型组成或状态分布差异严重，$y\overset d=y^*$ 的前提失效，平滑不能挽救系统性偏差。

### 7. “对角整合”不是 SuperMap 自己发明新的对齐器

`diagonal_integration()` 把 ATAC 细胞的 imputed RNA 建成 Seurat `ACTIVITY` assay，用它替换粗糙 gene activity score；随后仍调用 Seurat 的 `FindTransferAnchors(reduction='cca')` 和 `TransferData`，再对两种模态做 PCA/UMAP。SuperMap 的贡献是提供更好的共同特征和 anchors，最终对齐算法仍是 Seurat CCA 管线。

Figure 3a–c 分别显示按模态和细胞类型着色的共同空间、FOSCTTM、标签转移与生物保留；Figure 3e 还展示把 SuperMap anchor 加到 BindSC 后的改善。这些结果支持“更好的链接可改善现有整合器”，而不是证明任何数据上 CCA 都能完美恢复真实细胞配对。

### 8. 调控分数与 epigenomic priming 的证据边界

对调控分析，论文先在 metacell 层生成 $(\hat Y^*,X)$ 配对，再计算标准化峰—基因回归系数作为 regulatory score。Figure 4 显示 eQTL 支持的峰—基因对在多个距离区间分数更高，并报告 eQTL 分类 ROC；但这仍是统计关联和外部证据富集，不能单独证明某个峰因果调控某基因。包的核心 `R/supermap.R` 返回映射和插补，标准化 regulatory-score 的完整复现实例主要位于分析材料而非一个独立导出函数。

Figure 5 在真正未配对的人胎脑 RNA/ATAC 数据中先整合细胞状态，再沿 Monocle3 轨迹比较 ATAC 预测表达与实测 RNA 的样条曲线。若 ATAC 预测曲线的极值早于 RNA，定义为正 temporal displacement，作为 epigenomic priming 候选。这个量表示沿所选轨迹的时间先后，不等于直接测得染色质改变导致转录改变；它依赖轨迹方向、平滑曲线和映射质量。

### 9. 五张主图应当怎样连起来读

- **Figure 1**：问题和算法。没有细胞/特征配对 → 分布匹配回归 → ADMM → 四类下游任务。
- **Figure 2**：映射与插补。配对数据被人为拆开用于训练，而真实配对只用于评价；还测试蛋白—ATAC、细胞比例不平衡、特征数与细胞数。
- **Figure 3**：imputed RNA 作为 anchors 改善 diagonal integration，并检验 metacell graining level。
- **Figure 4**：映射用于峰—基因调控评分，与 eQTL、Lasso 和 RUNX1 footprint 等证据对照。
- **Figure 5**：真正未配对胎脑数据中的细胞类型细化、轨迹和 priming 候选。

补充材料进一步显示：轻度比例不平衡时协方差尚可保持，严重不平衡会持续降低准确性；特征数或细胞数过少也会削弱映射估计；另有收敛、超参数和不同 graining level 分析。因此“对不平衡鲁棒”必须限定在论文测试范围，不能删掉相似生物系统这一前提。

### 10. 论文机制与固定代码快照

| 机制 | 代码入口 | 判断 |
|---|---|---|
| 200 kb TSS 硬窗口与距离矩阵 | `gene_peak_distance()` | Exact |
| 协方差、距离先验与 ADMM 惩罚更新 | `pairwise_optim()`, `pairwise_loss()` | Exact |
| logistic CDF 与逐基因 NLS | `nls_diag()`, `marginal_nls()` | Exact |
| 10 轮 ADMM、中心化和截距恢复 | `supermap()` | Exact |
| RNA log-CPM 与 ATAC 二值比例 metacell | `metacell_matrix_RNA/ATAC()` | Partial：ATAC 二值化是代码特化细节 |
| 单细胞 KNN 平滑 | `smooth_knn_atac()` | Partial：论文自身 0.5；代码自身 0.4、邻居 0.6 |
| 线性 missing-modality imputation | `imputation()` | Exact |
| Seurat CCA diagonal integration | `diagonal_integration()` | Exact；SuperMap 提供 anchor，不替代 Seurat |
| 标准化 regulatory score 全流程 | 核心包导出函数中 | Not found；主要在分析/vignette 路径 |

### 11. 复现时的最小检查清单

1. 固定 commit `a6899ffcd0f1e55f4268a8896eec8f3d95881e42` 和包版本 1.0.0；记录 R、Seurat、Signac 与并行依赖版本。
2. 先确认两个样本来自相似生物系统，比较细胞组成和低阶分布；完全缺失的细胞状态没有可靠映射保证。
3. 明确响应模态 $Y$ 与预测模态 $X$ 的方向；$B$ 不是天然可逆映射。
4. 保存基因注释版本、TSS 定义、200 kb 窗口和实际保留的峰—基因对；长程调控不会进入模型。
5. 报告 metacell 数量/分辨率、ATAC 二值化、`ncore`、ADMM 收敛记录以及 KNN 实际 0.4/0.6 权重。
6. 用持出的真实 paired 数据评价时，确保配对信息没有泄漏到训练；真正未配对数据只能依赖间接生物验证。
7. 本次完成了正文、五张主图、补充 PDF 和 `R/supermap.R` 直接静态核验，但没有下载所有 GEO 数据、执行 R 包、重跑 60 核并行、全部 benchmark 或复现论文数值。因此代码—机制映射已确认，端到端数值复现为 `Not run`。

一句话总结：SuperMap 用“群体分布相同”替代“细胞逐一配对”，用边缘 CDF、协方差和局部基因组先验共同识别线性跨模态映射；它能为插补和现有整合器提供高质量链接，但效果建立在样本生物分布足够相似、局部线性与 200 kb 调控窗口这些明确假设上。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SuperMap — Summary

### Motivation & Novelty

#### Biological Problem
Single-cell genomics now routinely generates multiple measurement modalities — gene expression (scRNA-seq), chromatin accessibility (scATAC-seq), DNA methylation, and protein abundance — each capturing a distinct regulatory layer of cell biology. Integrative analyses of these modalities promise comprehensive views of cell states, regulatory mechanisms, and developmental dynamics. However, the vast majority of multimodal data is **unpaired**: RNA and ATAC are measured in different cells, from different samples, leaving no cell-wise correspondence and no shared feature space.

This unpaired nature blocks three key analyses:
1. **Imputation**: predicting what the RNA expression profile of an ATAC cell would look like
2. **Diagonal integration**: aligning cells from different modalities into a shared embedding for clustering, visualization, and label transfer
3. **Regulatory analysis**: associating peaks to genes to infer cis-regulatory interactions

#### Limitations of Existing Methods

| Method | Approach | Limitation | Journal | Year |
|--------|----------|------------|---------|------|
| Seurat | Gene activity score (sum ATAC in gene body) as RNA surrogate | Heuristic, biologically inaccurate; ignores actual regulatory potential | Nature Biotechnology | 2019-2023 |
| Signac | Gene activity score | Coarse approximation | Nature Methods | 2021 |
| MAESTRO | Gene activity score | Coarse approximation | Genome Biology | 2020 |
| GLUE | Prior knowledge graph (genomic proximity) | Data-independent; biases from fixed priors | Nature Methods | 2022 |
| scJoint | Gene activity score + transfer learning | Inherits gene activity score inaccuracies | Nature Computational Science | 2022 |
| BindSC | Mosaic integration with paired reference | Requires costly paired multimodal data | Nature Methods | 2022 |
| SeuratV5 | Mosaic integration | Requires paired reference | Nature Biotechnology | 2024 |
| StapMap | Mosaic integration | Requires paired reference | Nature Methods | 2024 |
| UnpairReg | Regulatory analysis from unpaired data | Limited to regulatory inference, not integration | Nature Methods | 2023 |

#### SuperMap's Unique Contributions

1. **Unlinked multivariate regression**: extends the univariate "unlinked regression" statistical framework (where observation pairings are unknown) to the multivariate setting with high-dimensional genomics data — a substantive methodological advance.

2. **Data-adaptive mappings without paired data**: learns B directly from unpaired marginal distributions and second moments, requiring no paired reference. Prior methods either use fixed biological heuristics or require paired training data.

3. **Unified framework for multiple downstream tasks**: a single learned coefficient matrix B enables imputation, integration, regulatory scoring, and trajectory analysis — previous methods address only one or two tasks.

4. **Two-level genomic-distance prior**: a hard 200 kb TSS window fixes all outside-window coefficients to zero; within that window, an exponential distance-weighted soft penalty lets the data determine coefficient strength.

---

### Method Overview

SuperMap formulates cross-modal mapping as a statistical learning problem:

$$\mathbf{y} \overset{d}{=} \mathbf{B}\mathbf{x} + \mathbf{\epsilon}$$

where $\mathbf{y}$ (RNA) and $\mathbf{x}$ (ATAC) are from different cells — the "distributional equality" $\overset{d}{=}$ replaces the usual cell-wise pairing.

**Key technical components**:
- **Objective**: minimize mismatch of marginal CDFs (per gene) + covariance structure (cross-gene) + genomic-distance penalty
- **ADMM optimization**: decouples into three alternating subproblems — pairwise covariance update (closed-form ridge regression), marginal CDF update (parallel per-gene NLS), dual variable update
- **Metacell denoising**: Leiden clustering aggregates cells into ~150-200 metacells for model fitting, reducing noise while preserving feature relationships
- **KNN smoothing**: imputes at single-cell resolution by borrowing information from K=50 nearest neighbors (Jaccard-weighted SNN)
- **Sparsity from biology**: only peak-gene pairs within 200kb are estimated, reducing parameters by ~100-1000×

**Computational complexity**: linear in sample size (due to metacell reduction), parallel NLS for marginal subproblem. R implementation using `bigmemory` and `foreach/doParallel` for scalability.

See `doc_method.md` for mathematical derivations and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets
- **10X Multiome PBMC**: human PBMCs, ~14 cell types, simultaneous RNA+ATAC (used as pseudo-unpaired)
- **10X Multiome BMMC** (GSE194122): human bone marrow, ~18 cell types
- **SHARE-seq mouse skin** (GSE140203): mouse skin, ~16 cell types; low sequencing depth
- **scNMT-seq mouse embryos** (GSE121708): RNA + DNA methylation
- **ASAP-seq PBMC** (GSE156478): protein (227 antibodies) + ATAC
- **sciRNA-seq3 + sciATAC-seq3 human fetal cerebrum** (GSE156793, GSE149683): genuinely unpaired, 89-122 days post-conception

#### Imputation Performance (RNA from ATAC)
- 10X PBMC: SuperMap Pearson ≈ 0.80, closely matches paired regression (gold standard), outperforms Signac/MAESTRO/UnpairReg by >0.3 (Figure 2B)
- Marker gene imputation: largest advantage vs competing methods (Figure 2C)
- Protein from ATAC: Pearson ≈ 0.65 (Figure 2D) — no existing method for comparison

#### Diagonal Integration
- FOSCTTM on PBMC: SuperMap ≈ 0.05, ~2-4× lower than Seurat/BindSC/scJoint (Figure 3B)
- Label transfer ACC/ARI/NMI: SuperMap consistently best on PBMC and BMMC; second on SHARE-seq (Figure 3C)
- As add-on to BindSC: improves Acc from 0.70 to 0.92 on PBMC (Figure 3E)
- Robust to metacell graining level 25-105 (Δ across metrics < 0.01) (Figure 3F)

#### Regulatory Analysis
- eQTL-supported peak-gene pairs have consistently higher regulatory scores across all distance bins (Figure 4D)
- AUC for eQTL prediction: SuperMap 0.634 vs Lasso 0.542 (using paired data) (Figure 4E)
- Validates CCL4 regulatory elements; RUNX1 TF footprint confirmed (Figure 4F-G)

#### Biological Discovery
- Fetal cerebrum: ATAC "Astrocytes/Oligodendrocytes" split into correct subtypes; radial glial cell population identified (Figure 5A-B)
- Epigenomic priming detected: ATAC-predicted RNA leads measured RNA by >3 pseudotime units for multiple neuronal genes (Figure 5E-F)
- EOMES+ nIPCs identified as trajectory root — previously annotated as "Unknown" (Figure 5H)

---

### Reproducibility Rating: 4/5

**Justification**: SuperMap is well-implemented as an R package on GitHub (`chaodeng-aca/SuperMap`) with working vignettes for both 10X Multiome and ASAP-seq datasets. All main figures are reproducible from publicly available datasets (GEO accessions provided). Key hyperparameters (λ, ρ, w, d0, window size, K, graining level) are reported and match the code defaults.

**Deductions**:
- R-only implementation limits accessibility for Python-oriented bioinformaticians
- Core single-file R implementation (708 lines) has minimal documentation for internal functions
- Benchmark comparison code is in separate vignette HTML files, not as a standalone reproducible pipeline
- Supplementary PDF (39MB) contains extended methods details not in the main paper, but was not OCR-converted for this analysis

**Environment setup**: standard R + Bioconductor packages. `devtools::install_github('chaodeng-aca/SuperMap')` should work on R≥4.0. The Seurat/Signac dependency stack requires careful version management (Seurat v5 has breaking API changes).

**Practical notes**:
- Run on metacell data (not single cells) to fit the model — critical for computational feasibility
- `ncore=60` default assumes a server environment; reduce for desktop use
- `bigmemory` requires shared filesystem access across parallel workers

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
