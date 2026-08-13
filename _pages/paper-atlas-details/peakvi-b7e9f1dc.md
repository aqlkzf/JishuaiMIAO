---
layout: default
permalink: /paper-atlas/peakvi-b7e9f1dc/
title: "PeakVI"
nav: false
description: "PeakVI 把极度稀疏的单细胞 ATAC 峰矩阵看成“是否至少观察到一次开放事件”的二值结果。它用变分自编码器学习细胞的生物学状态，同时把测序深度和区域本身易被检测的程度拆成两个技术因子；因此同一个模型既能给出用于聚类和整合的低维表示，也能给出逐细胞、逐区域的去噪开放概率。"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Cell Reports Methods · 2022</span>
    </div>
    <h1>PeakVI</h1>
    <p>PeakVI: A deep generative model for single-cell chromatin accessibility analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.crmeth.2022.100182" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for PeakVI">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/scverse/scvi-tools" target="_blank" rel="noopener noreferrer" aria-label="Open code for PeakVI">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PeakVI 中文方法解读

### 一句话理解

PeakVI 把极度稀疏的单细胞 ATAC 峰矩阵看成“是否至少观察到一次开放事件”的二值结果。它用变分自编码器学习细胞的生物学状态，同时把测序深度和区域本身易被检测的程度拆成两个技术因子；因此同一个模型既能给出用于聚类和整合的低维表示，也能给出逐细胞、逐区域的去噪开放概率。

### 1. 输入、输出与问题设定

输入是细胞乘区域的矩阵 $X\in\mathbb{N}^{N\times K}$。$x_{ij}$ 是细胞 $i$ 在区域 $j$ 上的片段数，但似然只使用指示量 $\mathbf{1}(x_{ij}>0)$。可选的批次标签 $s_i$ 以及其他已知协变量也可以注册到模型中。

模型产生两类互补输出：

1. 潜变量 $z_i$：用于 UMAP、聚类、近邻图、数据整合和参考映射；
2. 生物学开放概率 $y_{ij}$：用于去噪矩阵和单区域差异可及性分析。

这里必须区分“区域在生物学上开放的概率”与“实验最终观察到片段的概率”。PeakVI 正是通过下面的分解将二者分开。

### 2. 三因子 Bernoulli 观测模型

论文把观察概率写成

$$
p(x_{ij}>0)=y_{ij}\,\ell_i\,r_j.
$$

- $y_{ij}\in[0,1]$：由细胞状态决定的开放概率；
- $\ell_i\in[0,1]$：细胞特异的检测/文库深度因子；
- $r_j\in[0,1]$：区域特异的检测因子，例如峰宽和序列偏好造成的差异。

从左到右读：区域首先要在该细胞中开放（$y_{ij}$），随后要被有效切割（$r_j$），最后对应片段还要被捕获和测序（$\ell_i$）。例如 $y_{ij}=0.8$、$\ell_i=0.5$、$r_j=0.6$ 时，真正观察到该区域的概率只有 $0.8\times0.5\times0.6=0.24$。因此一个零值不能直接解释为染色质关闭。

本地代码在 `PEAKVAE.get_reconstruction_loss()` 中对 $p\cdot d\cdot f$ 计算二元交叉熵，其中 `p` 对应 $y_{ij}$，`d` 对应 $\ell_i$，`f=sigmoid(region_factors)` 对应 $r_j$。

### 3. 编码器、潜变量与解码器

编码器 $f_z$ 根据细胞的峰向量近似后验：

$$
(\mu_i,\sigma_i)=f_z(x_i),\qquad
q(z_i\mid x_i)=\mathcal N(\mu_i,\sigma_i),\qquad
z_i\sim q(z_i\mid x_i).
$$

解码器把潜变量与批次/协变量映射回所有区域的开放概率：

$$
y_{ij}=\bigl(g_z(z_i,s_i)\bigr)_j.
$$

本地实现中，`PEAKVAE.inference()` 调用 `z_encoder` 得到分布 `qz` 和样本 `z`，并由独立的 `d_encoder` 产生一个确定性的细胞因子 `d`；`PEAKVAE.generative()` 再由 `z_decoder` 生成 `px`。默认不把批次送入编码器，但解码器会接收批次，这使潜空间更倾向于保留跨批次共享的生物学变化，而将已知技术条件交给生成端解释。当前代码也允许通过 `encode_covariates` 和 `deeply_inject_covariates` 改变协变量注入方式。

### 4. 训练目标

训练最大化边际似然的证据下界，等价地最小化 Bernoulli 重构损失与后验到标准正态先验的 KL 散度：

$$
\mathcal L_i=
-\sum_j\log\operatorname{Ber}\!\left(\mathbf 1(x_{ij}>0);y_{ij}\ell_i r_j\right)
+\beta\,D_{\mathrm{KL}}\!\left(q(z_i\mid x_i)\,\|\,\mathcal N(0,I)\right).
$$

`PEAKVAE.loss()` 逐细胞计算这两项。`PEAKVI.train()` 使用 AdamW，并支持 KL warm-up；当前快照默认最多 500 epochs、学习率 $10^{-4}$、batch size 128，并以验证集重构损失执行早停。这些是当前软件默认值，不应误写成所有论文实验都使用的固定超参数。

### 5. 归一化开放概率如何得到

论文关心的是去掉技术因子后的 $y_{ij}$。当前 API `PEAKVI.get_normalized_accessibility()` 默认返回解码器的 `px`，即逐细胞逐区域的开放概率，而不会乘回细胞因子或区域因子。调用者可以：

- 用 `transform_batch` 在指定批次条件下解码；
- 用 `use_z_mean=True` 使用后验均值，或采样潜变量；
- 只返回 `region_list` 指定的区域；
- 用 `threshold` 稀疏化大矩阵；
- 用 `normalize_cells=True` 或 `normalize_regions=True` 把相应技术因子乘回去。

因此“normalized”在这里不是普通的总量缩放，而是显式选择保留或移除生成模型中的技术因子。

### 6. 单区域差异可及性

给定两组细胞 $C_A$ 和 $C_B$，PeakVI 从各自后验中抽取潜变量、解码开放概率，并估计每个区域的组均值 $Y_{C_A,j}$ 与 $Y_{C_B,j}$。论文采用绝对差

$$
\Delta_j=Y_{C_B,j}-Y_{C_A,j}
$$

作为效应量；相比低概率处极不稳定的比值，它能直接表示开放概率增加或减少了多少。论文进一步计算差异概率 $p_{DA}$，并用 $\delta=0.05$ 定义具有实际幅度的变化。

当前 `PEAKVI.differential_accessibility()` 令 `use_z_mean=False`，通过统一的 `_de_core` 对后验采样结果做 Bayesian model comparison。返回表同时包含 `prob_da`、`bayes_factor`、`effect_size`、FDR 判定，以及模型估计和原始二值观察的两组概率。这里的 Bayesian/FDR 结论依赖模型拟合、分组和批次设定，不能把概率阈值当作传统检验的 $p$ 值。

### 7. 图证据如何支撑方法

- 图 1A 直接画出 $y_{ij}\ell_i r_j$ 的三因子模型；图 1B 显示 $r_j$ 随区域宽度变化，图 1C 显示 $\ell_i$ 随片段数上升并趋于饱和，说明两个因子确实吸收预期的技术效应。图 1D 的人工稀疏化实验检验去噪稳定性。
- 图 2 比较潜空间的生物学分离与批次混合。论文报告 replicate-batch 配置在细胞类型分离（9.04）和批次富集（1.85，越低越好）之间取得较好平衡。
- 图 3 检验逐区域 DA。技术重复间，模型效应的平均相关为 0.95，而经验效应为 0.66；空比较中论文报告 PeakVI 无阳性，而 GLM 和 Wilcoxon 分别产生 910 和 6,761 个调用。与 bulk ATAC 的效应相关中，PeakVI 为 0.74。
- 图 4 展示参考映射和从 DA 区域解释细胞状态：模型不仅形成可用的潜空间，也能把单区域概率用于细胞类型/状态注释。

这些结果证明的是论文所测试数据和设置下的性能，不保证任意峰集、极小群体或未建模批次上仍然成立。

### 8. 论文与本地代码的对应关系

本地代码快照：scvi-tools commit `206cc19ca89d985245ca204fbc86772e5c2446d0`。

| 论文机制 | 本地实现 | 对应程度 |
|---|---|---|
| 注册峰矩阵、批次和协变量 | `src/scvi/model/_peakvi.py::PEAKVI.setup_anndata` | Exact |
| $q(z_i\mid x_i)$ 与重参数采样 | `src/scvi/module/_peakvae.py::PEAKVAE.inference` / `z_encoder` | Exact |
| $y_{ij}=g_z(z_i,s_i)$ | `PEAKVAE.generative` / `z_decoder` | Exact |
| $\ell_i$ 的辅助网络 | `d_encoder` 产生 `d` | Exact（当前实现为确定性网络输出） |
| $r_j$ 的可学习参数 | `region_factors` 经 sigmoid 约束到 $[0,1]$ | Exact |
| Bernoulli 似然与 KL | `get_reconstruction_loss`、`loss` | Exact |
| 去噪开放概率 | `PEAKVI.get_normalized_accessibility` | Exact；旧文档/API 名称可能不同 |
| 单区域 Bayesian DA | `PEAKVI.differential_accessibility` 调用 `_de_core` | Partial：用户接口与论文输出一致，统计内核是当前 scvi-tools 的共享实现 |
| 论文全部基准、预处理与作图脚本 | 当前通用 scvi-tools 快照 | Not found；仓库不是论文实验的冻结复现包 |

### 9. 使用边界

1. 峰集合的构建、细胞质控和低覆盖区域过滤发生在模型之前；输入质量问题不会被 VAE 自动消除。
2. 批次校正只针对提供并正确指定的协变量。若批次与生物学条件完全混杂，模型不能凭空识别二者。
3. 输出是模型后验下的概率估计，不是实际测得的新片段；“去噪”不等于确认每个零值都是假阴性。
4. $y$、$\ell$、$r$ 的乘积分解存在统计识别上的依赖，论文用因子与已知技术量的关系提供经验验证，但这不是逐样本的因果证明。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PeakVI: Summary

**Paper**: PeakVI: A deep generative model for single-cell chromatin accessibility analysis
**Authors**: Tal Ashuach, Daniel A. Reidenbach, Adam Gayoso, Nir Yosef
**Journal**: Cell Reports Methods **2**, 100182 (2022)
**DOI**: 10.1016/j.crmeth.2022.100182
**Code**: https://github.com/scverse/scvi-tools

---

### Motivation & Novelty

#### Biological Problem

scATAC-seq measures chromatin accessibility at single-cell resolution, generating a sparse count matrix where each value indicates fragments from a cell that mapped to a genomic "peak." The data presents three compounding challenges: (1) extreme sparsity — only 5–15% of accessible regions are detected per cell due to limited transposase sensitivity; (2) binary underlying biology — a region is either open or closed, making count modeling inappropriate; and (3) systematic confounders — region width and library size distort measurements in ways unrelated to biology.

#### Why Existing Methods Fall Short

| Method | Limitation | Journal/Year |
|--------|-----------|-------|
| cisTopic | Uses LDA; does not correct batch effects | *Nature Methods* 2019 |
| LSA (Signac, ArchR) | Linear dimensionality reduction; no batch correction; sensitive to library size | — |
| chromVAR | Aggregates to motif scores; loses single-region resolution | *Nature Methods* 2017 |
| Cicero | Aggregates to gene activity scores; loses single-region resolution | *Molecular Cell* 2018 |
| SCALE | VAE with GMM; does not account for technical confounders; overfits due to data dimensionality | *Nature Communications* 2019 |
| ArchR (Wilcoxon), Signac (GLM) | DA tests not optimized for scATAC; numerical instability in sparse data; inflated significance | *Nature Genetics* 2021, *Nature Methods* 2021 |

#### Unique Contributions

1. **Three-factor Bernoulli model**: Explicitly separates biological accessibility ($y_{ij}$), cell-specific library effects ($\ell_i$), and region-specific biases ($r_j$) — allowing interpretable denoising
2. **Batch-corrected VAE**: Achieves better balance of cell-type separation and batch mixing than all compared methods (enrichment score 9.04 cell-type vs. 1.85 batch for replicate-batch configuration)
3. **Single-region differential accessibility**: The pDA metric (Bayesian probability of differential accessibility) avoids false positives from sparse data (0 false-positive DA regions in null comparison vs. 910 for GLM, 6761 for Wilcoxon) while achieving higher correlation with bulk ATAC ground truth (0.74 vs. 0.48/0.52)
4. **scArches compatibility**: Supports projection of query data onto a reference atlas

---

### Method Overview

PeakVI is a VAE-based generative model for scATAC-seq data. The core insight is that the probability of observing a fragment in a region decomposes multiplicatively:

$$q_{ij} = y_{ij} \cdot \ell_i \cdot r_j$$

where $y_{ij}$ is the true biological accessibility (learned by the VAE), $\ell_i$ is a cell factor (estimated by an auxiliary network from the raw data), and $r_j$ is a region factor (a learnable parameter updated via gradient descent).

**Architectural components**:
- **Encoder** $f_z$: Maps raw counts → latent distribution $\mathcal{N}(\mu_i, \sigma_i)$ via FCLayers with LayerNorm + LeakyReLU + Dropout(0.1). Hidden/latent dimensions scale as $\sqrt{K}$ and $K^{1/4}$ respectively.
- **Decoder** $g_z$: Maps latent $z_i$ + batch annotation $s_i$ → accessibility probabilities $y_{ij} \in (0,1)$ via FCLayers + Sigmoid. No dropout.
- **Cell factor network** $f_\ell$: Maps raw counts → scalar $\ell_i \in (0,1)$ via a deterministic network with Sigmoid output.
- **Region parameters**: K-dimensional learnable vector, sigmoid-constrained to (0,1), initialized to 0.5.

**Training**: AdamW (lr=1e-4, wd=1e-3), KL annealing over 50 epochs, early stopping on validation reconstruction loss (patience=50 epochs, max 500 epochs), best checkpoint saved.

**Downstream uses**:
- Batch-corrected latent space for clustering/UMAP
- Denoised accessibility estimates ($y_{ij}$) for DA analysis
- Reference-based annotation via scArches transfer learning
- *De novo* cell annotation via DA + pathway enrichment (Enrichr/ARCHS4)

---

### Evaluation

#### Datasets
1. **Hematopoiesis** (Satpathy et al. 2019, *Nat. Biotechnol.*; GEO:GSE129785): Bone marrow + blood, multiple cell types, multiple batches of unsorted PBMCs; FACS-based ground-truth labels
2. **10x PBMC Multiomic**: Joint scRNA + scATAC from single PBMCs; used for cross-modality validation
3. **10x PBMC (query)**: Used as unlabeled query for transfer learning demonstration
4. **Bulk ATAC-seq** (Calderon et al. 2019, *Nat. Genet.*; GEO:GSE118189): Sorted immune cells; ground truth for DA evaluation

#### Key Metrics & Results

| Task | Metric | PeakVI Best Config | Best Competitor |
|------|--------|-------------------|-----------------|
| KNN consistency with scRNA | Fraction neighbors shared (K=50) | **PeakVI** (marginal best) | cisTopic (close second) |
| Cell-type separation | Enrichment score | 9.04 (replicate-batch) | LSA 9.1 (no batch correction) |
| Batch mixing | Enrichment score (lower=better) | **1.85** (replicate-batch) | chromVAR 1.57 (worse cell sep.) |
| DA null comparison (NK replicates) | False positives | **0** | GLM: 910, Wilcoxon: 6,761 |
| DA biological (B vs NK) | % overlap with bulk ATAC | 86% (both PeakVI and Wilcoxon) | GLM: 65.6% |
| DA effect correlation with bulk | Pearson r | **0.74** | Wilcoxon: 0.52, GLM: 0.48 |
| DA reproducibility | Pearson r (b1 vs b2) | **0.95** | empirical: 0.66 |
| Robustness to sparsity | MSE at 90% corruption | 0.17 (MSE from corrupted indices) | — |

#### Biological Validation
- $r_j$ correlates with region width (wider = higher probability; most regions ~0.5)
- $\ell_i$ saturates at 1 for well-covered cells, decreasing for low-coverage cells
- De novo annotation correctly identifies B cell, NK, CD4+ T, regulatory T, and pDC clusters from hematopoiesis data
- Correctly distinguishes naive vs. memory B cells via differential accessibility (TCL1A, YBX3 for naive; AIM2, CD80 for memory)

---

### Reproducibility

**Rating: 4/5**

**Justification**: PeakVI is fully implemented in the scvi-tools package (`pip install scvi-tools`) with ongoing maintenance. API is stable and well-documented. The main analysis scripts are archived on Zenodo (DOI:10.5281/zenodo.4728534). Data is publicly available on GEO and 10x Genomics website.

**Practical setup**:
```python
import scvi
import anndata

adata = anndata.read_h5ad("your_data.h5ad")
scvi.model.PEAKVI.setup_anndata(adata, batch_key="batch")
model = scvi.model.PEAKVI(adata)
model.train()

# Get batch-corrected latent representation
latent = model.get_latent_representation()
adata.obsm["X_peakvi"] = latent

# Differential accessibility
da = model.differential_accessibility(
    groupby="cell_type", group1="B_cells", group2="NK_cells"
)
```

**Strengths**:
- Clean Python API integrated with scanpy/AnnData ecosystem
- Automatic architecture scaling (no hyperparameter tuning needed for n_hidden, n_latent)
- Hyperparameter stability validated empirically (Table S1)
- scArches compatibility for reference-based analysis

**Weaknesses / Pitfalls**:
- Requires peaks to be called upstream (not an end-to-end pipeline); for multi-dataset integration, peaks must be defined jointly
- For very large datasets (>200K cells), memory requirements scale with K × batch_size
- The analysis scripts on Zenodo use older API; check scvi-tools documentation for current syntax
- Default n_layers_encoder=2 differs from the 3-layer encoder illustrated in the STAR Methods figure

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
