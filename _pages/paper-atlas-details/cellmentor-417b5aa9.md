---
layout: default
permalink: /paper-atlas/cellmentor-417b5aa9/
title: "CellMentor"
nav: false
wide: true
description: "CellMentor 是一个 supervised non-negative matrix factorization（NMF）方法。它不是让降维表示保留“总体最大方差”，而是利用参考数据的 cell-type labels，直接要求同类细胞在 latent space 中更紧、易混淆的不同类型更远。"
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
      <span>Representation Models</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>CellMentor</h1>
    <p>CellMentor: cell-type aware dimensionality reduction for single-cell RNA-sequencing data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-67088-7" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CellMentor">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/petrenkokate/CellMentor" target="_blank" rel="noopener noreferrer" aria-label="Open code for CellMentor">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CellMentor 方法解读：用有标签参考集学习可迁移的细胞类型空间

### 一句话定位

CellMentor 是一个 supervised non-negative matrix factorization（NMF）方法。它不是让降维表示保留“总体最大方差”，而是利用参考数据的 cell-type labels，直接要求同类细胞在 latent space 中更紧、易混淆的不同类型更远。训练得到 gene-by-factor basis $W$ 后，新 query cells 通过 non-negative least squares 投影到同一空间，不重新拟合 basis。

这种设计适合“已有可靠 reference、希望分析新批次/新技术的同类细胞”的场景；它不是开放世界细胞类型发现器。query 中完全缺席于 reference 的类型、错误 reference labels 或极端 protocol mismatch 都可能破坏结果。

### 输入、输出和两个阶段

参考表达矩阵记为

$$
X_{ref}\in\mathbb{R}_{\ge0}^{m\times n},
$$

$m$ 是共同 genes，$n$ 是 reference cells；每个 reference cell 有已知 cell type。CellMentor 学习

$$
X_{ref}\approx WH_{ref},
$$

其中 $W\in\mathbb{R}_{\ge0}^{m\times k}$ 是 gene loadings / meta-genes，$H_{ref}\in\mathbb{R}_{\ge0}^{k\times n}$ 是每个 cell 的 factor usage。下游 clustering/UMAP 使用 $H$，而不是直接在原始 genes 上操作。

对 query cell $x_j$，固定 $W$，求

$$
h_j^*=\arg\min_{h_j\ge0}\|Wh_j-x_j\|_2^2.
$$

代码的 `project_data()` 使用 Lawson–Hanson NNLS，逐 cell 得到 $H_{query}$。因此 reference 与 query 共享同一坐标轴；query 不会反过来改变 $W$。

### 核心目标：重构与判别同时优化

论文目标函数可写为

$$
F(W,H)=\frac12\|X-WH\|_F^2
+\widetilde S_W-\widetilde S_B
+\gamma\sum_{ij}H_{ij}
+\frac\delta2\operatorname{tr}(W^TWM).
$$

#### 重构项

$\|X-WH\|_F^2$ 防止表示只追求分类而丢掉主要表达结构。它也是论文观察到 label 不完整时仍能保留部分细胞亚结构的原因之一，但不能保证未标注类型一定会自动分开。

#### within-class compactness

$$
\widetilde S_W=\frac1C\operatorname{tr}
\left((H-HA)\widetilde N(H-HA)^T\right).
$$

$A$ 把每个 cell 映射到同类 centroid，$H-HA$ 是 cell 到类中心的偏差。最小化此项使相同 reference label 的 cells 更紧。代码在 `calculate_loss()` 中明确计算 `H_diff <- H - H %*% A` 和带 $N$ 的 quadratic form。

#### between-class separation

$$
\widetilde S_B=\frac1{C(C-1)}\operatorname{tr}
\left((HBP)\overleftrightarrow\beta(HBP)^T\right).
$$

$B$ 汇总 class centroids，$P$ 编码 class pairs。目标中减去这一项，因此优化会增大不同类型中心的距离。$\beta$ 可给经常混淆的 class pair 更高权重。

#### sparsity 与 orthogonality

$\gamma\sum H_{ij}$ 让每个 cell 使用较少 factors；$\delta\operatorname{tr}(W^TWM)/2$ 惩罚不同 $W$ columns 的重叠，$M$ 是 off-diagonal ones。前者提升简洁性，后者减少 basis redundancy，但过强会牺牲 reconstruction 或连续状态。

#### 自适应权重的含义

论文定义 cell-specific $\alpha$：离本类中心远、且所属类错误率高的 cells 权重更大；class-pair $\beta$ 按中间 SingleR predictions 的 confusion 更新。目的不是把离群 cell 删除，而是把优化注意力放在难样本和易混类对上。

这里必须区分论文机制与本地实现版本：`RunCSFNMF()` 接收 `const.alpha`/`const.beta`，构造 helper matrices；当前 `calculate_loss()` 用参数 alpha 和 beta 计算判别项。完整动态更新时序应以调用链和 package 版本为准，不能仅从数学描述推断每轮都重跑 SingleR。

### 非负乘法更新

`optimization_functions.R::update_w()` 实现

$$
W\leftarrow W\odot\frac{XH^T}{W(HH^T+\delta M)+\epsilon}.
$$

`update_h()` 将 supervised positive/negative constants 分开，并用论文 quadratic-form update 更新 $H$。`update_wh()` 交替更新 $W,H$，按相邻 loss 的相对变化与 maximum iterations 停止，同时保存最低 loss 状态信息。

乘法更新保持非负，但 NMF 是 non-convex；不同初始化可能收敛到不同局部解。因此 rank、initialization 与 validation selection 是方法本体的一部分，不是可忽略的工程细节。

### 自动 rank selection

CellMentor 不直接把细胞类型数设为 $k$。`SelectRank.R` 走两步：

1. **biwhitening**：用 non-square Sinkhorn–Knopp scaling 调整 rows/columns 方差，并在 Poisson 与 quadratic variance scaling 候选中选择更接近 Marchenko–Pastur（MP）noise distribution 的方案；
2. **eigenvector localization**：先计数超过 MP upper edge

$$
\lambda_+=(1+\sqrt{m/n})^2
$$

的 eigenvalues，再对相应 eigenvectors 检验其 components 是否服从 $N(0,1/m)$。代码以 KS-test $p\le0.01$ 计作 localized signal component。

直观上，随机噪声 eigenvector 的权重广泛、近似高斯；生物 program 往往集中在特定 gene subset，呈 localization。最终 $k$ 是通过 localization filter 的 components 数，而非所有越过 MP edge 的数量。

这是统计启发式，不是细胞类型数的无偏估计。极稀疏、强 library-size variation 或小样本都可能使 MP assumptions 偏离。

### 初始化策略

本地 `InitializeWH.R` 实现五类初始化：uniform、regulated、NNDSVD、gene clustering 和 cell clustering。

论文推荐 regulated meta-gene：先随机初始化 $H$，再把总 usage 信号加到与某 class 对应的 factor/cells 上，给 supervised optimization 一个类特异起点。本地实现对 `i in seq_len(k)` 取 `types[i]`；因此若 $k$ 大于 cell types 数，需警惕越界/空类型行为，不能假设每个 factor 都有独立 class seed。

NNDSVD 用 sparse SVD/irlba fallback 构造非负因子，并把极小值抬到 machine epsilon，避免 multiplicative updates 的“零锁定”。初始化敏感性分析中，论文称 initialization 是影响最大的 hyperparameter，regulated 默认最稳健。

### 参数选择和实际执行链

四个主要参数为 $\alpha,\beta,\gamma,\delta$。论文描述分层 grid search：先选全局 sparsity/orthogonality，再调整判别 constraints，以 validation clustering accuracy/NMI 选择模型。公开包中的 `GridSearch.R` 与 `RunCSFNMF()` 实现训练、projection 和 performance calculation。

标准流程是：

1. reference/query 取 common genes，并做一致 preprocessing；
2. 创建 CSFNMF object，保留 reference labels；
3. 自动或手动选择 rank；
4. 初始化 $W,H$；
5. grid search / supervised factorization；
6. 固定 $W$，NNLS 投影 query；
7. 用完整 $H_{query}$ 做 neighbor graph、clustering、annotation 或 UMAP visualization。

UMAP 只是展示。论文的 ARI 是在完整 reduced representation 上进行 graph clustering 后计算，不是在二维 UMAP coordinates 上聚类。

### 如何读 benchmark

#### 模拟数据

Figure 2 使用 Splatter，6 cell types、每 batch 1,000 cells，逐步增加难度。无 batch effect 时 CellMentor mean ARI 约 0.96；四 batches 条件报告在模拟中维持很高表现。模拟知道真 labels，最适合检验监督目标，但生成机制不等于真实 scRNA-seq 全部复杂性。

Figure 3 测试 reference mismatch：缺失类型、不完整 labels、随机/相关 mislabeling、判别 genes batch perturbation、1% rare type。结果说明在研究设定中 graceful degradation，但不能转写成“50% 任意错误 labels 都安全”。尤其 rare type 成功的前提是 reference 中已有该类型标签。

#### 真实 reference-query pairs

Figure 4 包括 pancreas、PBMC、melanoma；CellMentor 平均 ARI 0.710，与 rssNMF/CASSL/SIDA 同一梯队，而非在所有数据上独占第一。pancreas 中 16 个原标 alpha cells 落入 beta region，并由 SingleR score 支持，说明 latent space 能暴露潜在 annotation inconsistency，但不能仅凭 embedding 宣布原标签错误。

跨 10X/Smart-seq2 的 Tabula Muris transfer 检验技术迁移；若 protocol 或 sequencing depth 差异远超训练范围，固定 $W$ 也可能失败。

### 论文—代码映射

| 机制 | 本地代码 | 程度 | 边界 |
|---|---|---|---|
| supervised NMF loss | `R/optimization_functions.R::calculate_loss` | Exact | helper matrices 的构造分散在其他文件 |
| multiplicative W/H updates | `update_w`, `update_h`, `update_wh` | Exact | 局部最优且受初始化影响 |
| rank selection | `R/SelectRank.R` | Exact | MP/localization assumptions 需满足 |
| 五种初始化 | `R/InitializeWH.R` | Exact | regulated 是默认建议，不保证所有数据最佳 |
| fixed-W NNLS projection | `R/project_data.R` / package projection functions | Exact | query 不更新 basis |
| grid search | `R/GridSearch.R` | Exact | 计算成本取决于参数范围 |
| 论文全部 benchmarks/figures | separate `CellMentor_paper` repo | Not found locally | 当前包不等于完整复现仓库 |

### 最稳妥的结论

CellMentor 的优势是把 reference annotation 直接写入 factorization objective，并用固定、非负、可解释的 gene basis 把 query 映射进同一空间。它特别适合稳定 cell-type identity 的 reference transfer，而不适合把未知状态发现、trajectory preservation 或 reference-free integration 当作主要目标。使用时应同时检查 reconstruction、label quality、query novelty、batch/technology mismatch，并与 unsupervised embedding 和 marker expression 交叉验证，避免把监督产生的清晰分群误当成独立生物证据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CellMentor: Summary

### Motivation & Novelty

**Biological problem**: Single-cell RNA sequencing generates high-dimensional gene expression profiles for thousands of individual cells. A critical step is dimensionality reduction — transforming 20,000+ gene dimensions into a compact representation suitable for clustering and cell type identification. The challenge is that technical noise (batch effects, dropout, sequencing depth variation) often dominates the variance structure, causing standard methods to produce embeddings where cell types are poorly separated.

**Limitations of existing approaches**:
- **PCA** (Seurat, Nat. Biotechnol. 2024): captures maximum variance, which is dominated by batch effects; cannot incorporate prior biological knowledge; assumes linear relationships
- **Harmony** (Nat. Methods 2019): corrects batch effects but is not optimized for cell type discrimination; struggles with closely related cell types
- **scVI/scANVI** (Nat. Biotechnol. 2022): deep learning requiring extensive compute; lacks interpretability; not specifically optimized for cell type identification
- **CASSL** (Appl. Intell. 2023): semi-supervised, applies supervision post-hoc to clustering results
- **rssNMF** (PeerJ 2020): uses marker genes for graph regularization — indirect supervision
- **LIGER** (Cell 2019): uses dataset labels (not cell type labels) to guide shared/specific factor learning

**Unique contributions**:
1. First fully supervised NMF that directly incorporates cell type labels into the factorization objective through discriminative constraints
2. Novel rank selection combining biwhitening (Sinkhorn-Knopp) with eigenvector localization to filter technical noise dimensions
3. Transfer learning paradigm: learn W from labeled reference, project unlabeled query via NNLS — enables cross-batch and cross-technology analysis without retraining

---

### Method Overview

CellMentor is a two-phase supervised NMF framework:

**Decomposition phase** (reference): Factorizes labeled reference data $X_{ref} \approx W \cdot H_{ref}$ using a supervised objective that simultaneously minimizes within-class variation ($\tilde{S}_W$) and maximizes between-class separation ($\tilde{S}_B$), plus reconstruction fidelity, sparsity, and orthogonality terms. The rank $k$ is determined automatically via biwhitening + eigenvector localization. Hyperparameters are selected by grid search evaluated on a held-out validation split.

**Projection phase** (query): Applies the learned $W$ matrix to new query data via per-cell NNLS, producing $H_{query}$ — cell embeddings in the same biologically meaningful latent space.

**Key technical components**:
- Supervised NMF objective with 5 terms (reconstruction, within-class, between-class, sparsity, orthogonality)
- Biwhitening rank selection using random matrix theory (Marchenko-Pastur distribution)
- Eigenvector localization filter (KS test, $p < 0.01$) to distinguish biological from technical dimensions
- 5 initialization strategies; regulated meta-gene initialization as default
- Variable gene selection via SingleR marker genes (not standard HVG)
- RMSD scaling per cell

**Biological assumptions**:
- Cell types form distinct clusters in gene expression space
- A labeled reference dataset is available with accurate annotations
- Reference and query share the same gene space (or sufficient overlap)
- Cell type-specific gene programs are transferable across batches/technologies

---

### Evaluation

#### Simulated data (Splatter v1.26.0)

**Setup**: 10 simulations of increasing difficulty (6 cell types, 2-4 batches, 1000 cells/batch), 5 random seeds each. Metrics: ARI and NMI on full reduced-dimensional space (not UMAP).

**Without batch effects** (2 batches):
- CellMentor: mean ARI = 0.96 (range 0.73–1.0)
- CASSL: mean ARI = 0.89
- PCA/Seurat: mean ARI = 0.719
- scANVI: mean ARI = 0.57 (range 0.48–0.803)
- CellMentor maintained high performance even in simulation 10 (most difficult); most methods dropped below ARI=0.5

**With batch effects** (4 batches):
- CellMentor: ARI = 1.0 across all simulations
- Harmony: mean ARI = 0.78, dropping to 0.16 in hardest scenarios
- PCA/Seurat: mean ARI = 0.67

**Challenging scenarios**:
- Novel cell type (excluded from reference): partial separation maintained
- Merged reference labels: underlying biological variation partially preserved
- Random mislabeling (5–50%): ARI ≥ 0.9 at 50% mislabeling
- Correlated mislabeling (10–90%): ARI ≈ 0.8 at 50%, 0.75 at 90%
- Rare cell type (1% of cells): CellMentor successfully clustered; PCA, Harmony, scANVI failed

#### Real datasets

**Three tissue pairs** (Baron/Muraro pancreas, Zheng/Ding PBMC, Tirosh/Jerby-Arnon melanoma):
- CellMentor average ARI = 0.710 (comparable to rssNMF 0.724, CASSL 0.723, SIDA 0.710)
- Outperforms PCA (0.660) and other established methods
- Notable finding: identified 16 potentially misannotated alpha cells in Muraro dataset (confirmed by SingleR as beta cells)

**Cross-technology transfer** (Tabula Muris, 10 tissues, 10X → Smart-seq2):
- CellMentor: highest average ARI = 0.805
- Second-best PCA/Seurat: 0.671
- Best in 5/10 tissues, competitive in remaining 5

#### Computational performance

- Runtime competitive with other NMF-based approaches
- Memory scales linearly with dataset size
- Decomposition phase is the bottleneck; projection is fast
- Default parameter ranges eliminate need for extensive tuning

---

### Reproducibility

**Rating: 3/5**

**Justification**: The R package is well-structured and installable, with toy datasets and a vignette. However, the analysis scripts for reproducing paper figures are in a separate repository (`CellMentor_paper`), not included in the main package. The paper's full grid search parameter ranges (γ∈{0,0.001,0.01,0.1,0.5,1}, δ∈{0,0.1,0.5,1,2,5}) differ from the code defaults (γ=0.1, δ=1), making exact reproduction of benchmarks non-trivial.

**Strengths**:
- R package with proper S4 class structure, documentation, and tests
- Toy datasets included for quick testing
- Apache-2.0 license
- Zenodo archive for the specific version used in the paper
- All real datasets are publicly available (GEO accessions provided)

**Weaknesses**:
- Key discrepancy: adaptive α/β weights described in paper are not implemented in code (scalar α, uniform β)
- Analysis scripts in separate repository (`CellMentor_paper`) not cloned here
- Default grid search ranges narrower than paper's reported ranges
- Simulated datasets generated with Splatter require specific random seeds for exact reproduction
- R package requires many Bioconductor dependencies (SingleR, BiocParallel, SingleCellExperiment)

**Environment setup**:
```r
# Install from GitHub
devtools::install_github("petrenkokate/CellMentor")

# Key dependencies
BiocManager::install(c("SingleR", "BiocParallel", "SingleCellExperiment"))
install.packages(c("Seurat", "Matrix", "RMTstat", "nnls", "skmeans", "aricode"))
```

**Common pitfalls**:
- Cell reordering by type is required before object creation (handled automatically by `CreateCSFNMFobject`)
- Variable gene selection via SingleR can be slow for large datasets; use `num_cores > 1`
- NNDSVD initialization may fall back to irlba if sparsesvd returns fewer components than requested
- The `best_state` tracking in `update_wh()` is computed but not used — final state is returned, not best state

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
