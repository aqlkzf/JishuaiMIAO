---
layout: default
permalink: /paper-atlas/scale-f7d7a79c/
title: "SCALE"
nav: false
description: "单细胞 ATAC-seq 的每一列是一个染色质可及峰，每一行是一个细胞。与 RNA 计数相比，它有两个更尖锐的问题：维度可达数万至近十万峰，但每个细胞只观测到极少数开放位点；同时，一个位点在单细胞中接近“观测到/未观测到”的二元状态。于是，大量 0 既可能是真正关闭，也可能是测序深度不足导致的漏检。 传统 PCA 偏向连续、近高斯结构；依赖细胞间相关性的聚类在大量并列 0 时也容易失真。"
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
      <span>scATAC — Single-Cell Chromatin &amp; DNA Methylation</span>
      <span>Nature Communications · 2019</span>
    </div>
    <h1>SCALE</h1>
    <p>SCALE method for single-cell ATAC-seq analysis via latent feature extraction</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-019-12630-7" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SCALE：用高斯混合先验的 VAE 同时完成 scATAC-seq 表示、聚类与插补

### 1. 为什么 scATAC-seq 需要专门的生成模型

单细胞 ATAC-seq 的每一列是一个染色质可及峰，每一行是一个细胞。与 RNA 计数相比，它有两个更尖锐的问题：维度可达数万至近十万峰，但每个细胞只观测到极少数开放位点；同时，一个位点在单细胞中接近“观测到/未观测到”的二元状态。于是，大量 0 既可能是真正关闭，也可能是测序深度不足导致的漏检。

传统 PCA 偏向连续、近高斯结构；依赖细胞间相关性的聚类在大量并列 0 时也容易失真。SCALE 的核心思路是：用适合二元数据的 VAE 学习可重建峰可及性的潜变量，再把普通 VAE 的单高斯先验换成 $K$ 分量高斯混合，使潜空间天然具有多个细胞群。

### 2. 输入、输出和整体数据流

输入是细胞×峰矩阵 $\mathbf X$，以及用户给定或估计的簇数 $K$。当前代码先把所有大于 1 的值截为 1，再过滤低质量细胞和低频峰，并可选取高变峰（`code/scale/dataset.py:132-173`）。因此活动实现明确使用二元输入，而不是把原始 read count 直接送进模型。

输出有三类：

1. 每个细胞的低维潜表示 $\mathbf z$，默认 10 维；
2. 软簇概率 $\gamma$ 或基于潜表示的硬聚类标签；
3. 解码器给出的每个细胞—峰开放概率，可用于去噪和插补。

流程可以概括为：

```text
稀疏细胞×峰矩阵
  -> 二值化、细胞/峰过滤、选峰
  -> Encoder: x -> mu_z, log(sigma_z^2) -> 重参数采样 z
  -> 在 GMM 潜空间计算每个簇的后验 gamma
  -> Decoder: z -> 每个峰的开放概率
  -> 联合 ELBO 训练
  -> z 用于可视化/聚类，decoder 输出用于插补
```

### 3. 生成模型：为什么 GMM 比单高斯更适合聚类

SCALE 引入离散簇变量 $c\in\{1,\ldots,K\}$，联合分布写为：

$$
p(\mathbf x,\mathbf z,c)=p(\mathbf x\mid\mathbf z)\,p(\mathbf z\mid c)\,p(c).
$$

各部分分别是：

$$
p(c)=\operatorname{Discrete}(\boldsymbol\pi),
$$

$$
p(\mathbf z\mid c=k)=\mathcal N(\boldsymbol\mu_k,\operatorname{diag}(\boldsymbol\sigma_k^2)),
$$

$$
p(\mathbf x\mid\mathbf z)=\operatorname{Bernoulli}(\boldsymbol\mu_x),
\qquad \boldsymbol\mu_x=\operatorname{Sigmoid}(Decoder(\mathbf z)).
$$

普通 VAE 用一个标准高斯约束所有细胞，容易把本来多峰的细胞群压进同一连续云团。SCALE 让每个簇对应一个潜空间高斯分量：簇内细胞被吸引到同一分量附近，簇间则可由不同均值和方差分离。论文的消融结果表明，移除 GMM 后性能退化到接近普通 VAE，这支持“多峰先验而不仅是深网络”是聚类改进的重要来源。

### 4. 编码、重参数化与软簇分配

编码器从细胞的二元峰向量得到 $\boldsymbol\mu_z$ 与 $\log\boldsymbol\sigma_z^2$，然后采样：

$$
\mathbf z=\boldsymbol\mu_z+\boldsymbol\sigma_z\odot\boldsymbol\epsilon,
\qquad \boldsymbol\epsilon\sim\mathcal N(0,I).
$$

给定采样的 $z_i$，当前源码没有另设一个分类网络来预测 $c$，而是按 GMM 密度直接归一化：

$$
\gamma_{ik}=q(c=k\mid x_i)
\approx
\frac{\pi_k\mathcal N(z_i\mid\mu_k,\sigma_k^2)}
{\sum_{k'}\pi_{k'}\mathcal N(z_i\mid\mu_{k'},\sigma_{k'}^2)}.
$$

`code/scale/model.py:198-218` 就是这个计算。举例说，若一个细胞在三个分量下的未归一化联合密度为 $(0.1,0.7,0.2)$，归一化后 $\gamma$ 仍为 $(0.1,0.7,0.2)$，硬标签是第二簇，但训练保留了不确定性。源码使用重参数采样得到的 $z$，而不是均值 $\mu_z$ 计算 $\gamma$，所以训练期簇概率带有采样随机性。

### 5. ELBO 到底优化什么

论文最大化：

$$
\mathcal L_{ELBO}(x)=
\mathbb E_{q(z,c\mid x)}[\log p(x\mid z)]
-D_{KL}(q(z,c\mid x)\Vert p(z,c)).
$$

在代码中，它被展开为五部分：表达重建、$\log p(z\mid c)$、$\log p(c)$、$q(z\mid x)$ 熵和 $q(c\mid x)$ 熵（`code/scale/loss.py:49-84`）。重建项是二元交叉熵：

$$
-\sum_j[x_j\log\hat x_j+(1-x_j)\log(1-\hat x_j)].
$$

这既要求 decoder 解释观测到的开放峰，也惩罚错误预测大量关闭峰；GMM KL 部分则同时塑造连续潜空间和离散簇结构。

一个关键实现细节是：`model.py:125` 虽然创建了 KL warmup 迭代器，但使用 warmup 系数的损失行已被注释，活动代码在 `model.py:140-145` 从第一步起就以权重 1 加入 KL。因此不能把当前版本描述为“实际采用 KL 退火训练”。

### 6. 网络结构：论文设置与当前默认代码要分开

论文 Methods 给出的主模型编码器为 3200–1600–800–400 四层 ReLU，decoder 没有隐藏层，10 维潜变量直接连到峰输出并使用 Sigmoid；还描述了面向大数据的 quick mode：1024–128 两层编码器。

当前快照的 CLI 默认 `encode_dim=[1024,128]`，而高层 `SCALE_function` 还会把用户传入的 `latent` 和 `encode_dim` 覆盖为 10 与 `[1024,128]`（`code/scale/__init__.py:188-189`）。因此当前代码默认实际上是论文的 quick-mode 架构，而不是正文主模型的四层编码器。这是论文—代码版本差异，不应被抹平。

decoder 的线性直连具有额外解释性：某一潜维度到各峰的权重能指出该维度关联的开放区域。论文以偏离权重均值 2.5 个标准差作为 feature-associated peaks 的默认阈值，再做功能或 motif 富集。

### 7. 训练、初始化与聚类

当前模型的 GMM 参数并非只靠随机梯度从均匀初值学习。`model.py:220-228` 先用当前 encoder 编码所有细胞，再用 sklearn 的对角协方差 GaussianMixture 拟合潜表示，把均值和方差复制进模型参数。随后用 Adam、$5\times10^{-4}$ weight decay、最多 30,000 iteration 训练，并把梯度范数裁到 10（`model.py:111-157`）。

论文以潜表示上的 K-means 和 t-SNE 展示结果；当前代码接口的默认后处理已变为 Leiden 和 UMAP，而 `model.py:83-102` 仍保留 K-means/GMM 硬分配。这意味着复现论文图时需要显式选择相应旧设置，不能只运行当前默认参数。

### 8. 插补为什么有用，又为什么不能当作真值

decoder 输出的是每个峰开放的概率。它把同一 GMM 分量中多个相似细胞的信息汇总到共同潜结构中，因此可提高漏检峰的估计并抑制随机噪声。论文用同类型细胞聚合的 meta-cell 和模拟 corruption 评估插补，报告 SCALE 通常有更高相关性并能在一定腐蚀水平下保持信号。

但插补值是模型估计，不是重新测量的染色质开放性。它受所选峰、$K$、训练收敛和 GMM 假设影响。当前代码还用采样的 $z$ 解码，因此重复插补可能带有随机差异；后续二值化又采用每细胞与每峰均值的双阈值。做差异可及性分析时应保留原始观测作为核对边界。

### 9. 五张主图如何连起来读

- **Fig. 1**：从稀疏细胞×峰矩阵，经 encoder 和 GMM 潜变量，再由 decoder 输出增强矩阵；这是全部机制的总图。
- **Fig. 2**：Forebrain 的嵌入和混淆矩阵；SCALE 的 10 维表示比多种基线更好分离参考细胞类型。
- **Fig. 3**：插补评估；上方按细胞类型比较与 meta-cell 的相关性，下方显示 marker 峰在潜空间中的恢复结构。
- **Fig. 4**：Pi-ATAC 乳腺肿瘤；只凭 scATAC 数据分离 CD45+ 与 Epcam+，并从类型特异峰中恢复免疫或肿瘤相关 motif。
- **Fig. 5**：完整、plate-related 和 plate-independent 特征的对比；说明潜维度既可能承载生物类型，也可能暴露批次或板间差异。

补充文件 `MOESM1` 共 23 页，包含参数敏感性、额外嵌入/聚类、稀疏性腐蚀、簇数估计、插补模拟、motif、批次和 8 万细胞扩展等结果；`MOESM2` 是 25 页 reporting summary，`MOESM3` 是 2 页同行评审材料。补图支持正文结论，但 SCALE 并不是专门设计的批次校正模型，论文也明确把自动识别/移除技术效应留作未来工作。

### 10. 论文—代码证据边界

| 项目 | 本地证据 | 状态 |
|---|---|---|
| GMM-VAE 联合分布和 ELBO | `code/scale/loss.py:49-84` | Exact |
| GMM 参数与 $q(c\mid x)$ | `code/scale/model.py:179-228` | Exact |
| 二值化、过滤和选峰 | `code/scale/dataset.py:132-173` | Exact（当前通用实现） |
| Sigmoid decoder 与 Bernoulli 重建 | `code/scale/model.py:28-80`; `loss.py:26-27` | Exact |
| 论文四层主编码器 | 论文 Methods；当前默认被覆盖为 `[1024,128]` | Partial |
| batch size 32 | CLI 为 32，高层 API 默认 64 | Partial |
| KL warmup | 创建但活动损失未使用 | Not active |
| 论文 K-means/t-SNE 默认流程 | 当前默认 Leiden/UMAP，旧方法仍部分保留 | Partial |

本地 `code/` 是非独立 Git 快照，不能据父仓库提交号声称它就是官方 SCALE 仓库的精确 commit。它足以核对模型、损失、预处理和 CLI，但环境依赖较旧，完整重现实验还需要论文数据、Homer/chromVAR 等下游工具及明确的历史参数设置。

### 证据入口

- 主论文：`paper source/PMC6783552/paper.md`
- 主图：`paper source/PMC6783552/images/41467_2019_12630_Fig*_HTML.jpg`
- 补充：`paper source/PMC6783552/41467_2019_12630_MOESM1_ESM.pdf`
- 模型：`code/scale/model.py`
- ELBO：`code/scale/loss.py`
- 预处理：`code/scale/dataset.py`
- CLI / 高层入口：`code/SCALE.py`、`code/scale/__init__.py`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SCALE Summary

### Motivation & Novelty

**Biological problem**: Single-cell ATAC-seq (scATAC-seq) measures open chromatin accessibility at single-cell resolution, revealing which genomic regions are accessible to transcription factors in individual cells. Each cell has only 1–2 opportunities to capture any given locus, so scATAC-seq data is far sparser (>95% zeros) and more binary than scRNA-seq. This creates two compounding difficulties for standard analysis: (1) dimensionality reduction methods designed for continuous count distributions (PCA, scVI) are poorly suited to binary data, and (2) clustering based on cell-cell correlation (SC3, scABC) becomes ill-defined when most pairwise distances are dominated by missing values.

**Limitations of existing approaches**:
- **PCA**: Linear, assumes Gaussian-like distributions, loses structure in sparse binary data
- **chromVAR** (*Nat. Methods*, 2017): Groups peaks by TF motif, sacrifices individual peak resolution
- **scABC** (*Nat. Commun.*, 2018): Requires high-depth landmark cells; Spearman correlation ill-defined for high-sparsity data
- **cisTopic** (*Nat. Methods*, 2019): LDA topic model, good clustering but no continuous latent embedding for downstream imputation
- **scVI** (*Nat. Methods*, 2018): VAE for scRNA-seq using negative binomial likelihood; single Gaussian prior underfits multimodal sparse data

**SCALE's unique contributions**:
1. First VAE-based method specifically designed for binary scATAC-seq data, using Bernoulli likelihood instead of count-based distributions
2. GMM prior over latent space, providing a structured multimodal prior that simultaneously enforces cluster structure and improves sparse data fitting
3. Interpretable latent features: each dimension of the 10-D latent space connects directly to peaks via decoder weights, enabling identification of cell-type-specific and batch-related features
4. Joint framework for clustering, denoising, and imputation in a single model

---

### Method Overview

SCALE combines a Variational Autoencoder (VAE) with a Gaussian Mixture Model (GMM) prior. The core innovation is replacing the standard single-Gaussian VAE prior $\mathcal{N}(0, \mathbf{I})$ with a $K$-component GMM in latent space:

$$p(\mathbf{z}|c) = \mathcal{N}(\mathbf{z}|\mu_c, \sigma_c^2\mathbf{I}), \quad p(c) = \text{Discrete}(c|\pi)$$

where cluster assignments $c$ are inferred as soft weights $\gamma = q(c|\mathbf{x})$ during training.

**Key technical components**:
- **Encoder**: 2-layer MLP (1024→128→10) outputs $\mu_z$, $\log\sigma_z^2$ for reparameterized sampling. (Paper describes a 4-layer 3200-1600-800-400 architecture as the default, but the released code defaults to 2-layer; the paper refers to this as "quick mode".)
- **Decoder**: Single linear layer (10→P peaks) with Sigmoid activation — one of the sparsest possible decoders, forcing the latent dimensions to be maximally informative
- **Loss**: ELBO with 5 terms: binary reconstruction + log p(z|c) + log p(c) - H[q(z|x)] - H[q(c|x)]
- **GMM initialization**: sklearn GMM fitted on initial encoder outputs before gradient training begins
- **Post-training**: K-means or Leiden clustering on latent codes; optional imputation + binarization

See `doc_method.md` for full mathematical derivations and `doc_code.md` for implementation details.

---

### Evaluation

**Datasets** (7 total):
| Dataset | Cells | Platform | Cell types |
|---------|-------|----------|------------|
| Leukemia | ~600 | sci-ATAC | 6 (Mono, LMPP, LSC×2, Blast×2) |
| GM12878/HEK293T | ~500 | microfluidics | 2 |
| GM12878/HL-60 | ~500 | microfluidics | 2 |
| InSilico | ~900 | computational mix | 6 |
| Splenocyte | ~2,000 | sci-ATAC | multiple |
| Forebrain | ~2,000 | sci-ATAC | 8 |
| Breast Tumor (Pi-ATAC) | ~1,200 | Pi-ATAC | 2 (Epcam+, CD45+) |
| Mouse atlas (large) | ~80,000 | sci-ATAC | 30 reference |

**Metrics**: ARI (Adjusted Rand Index), NMI (Normalized Mutual Information), Micro-F1 score

**Comparative methods**: scABC (*Nat. Commun.*, 2018), cisTopic (*Nat. Methods*, 2019), scVI (*Nat. Methods*, 2018), SC3 (*Nat. Methods*, 2017), PCA, TF-IDF, Cicero (*Mol. Cell*, 2018)

**Key results**:
- SCALE achieves best or near-best clustering on all 6 benchmark datasets (ARI: 0.668 on Forebrain vs. 0.448 for scVI, 0.315 for scABC)
- Best denoising/imputation: highest Pearson correlation of imputed cells with cell-type meta-cells across all datasets
- Robust to data corruption: moderate ARI drop at ≤60% dropout rate; drops from 0.668 → 0.448 at 30% corruption, while scABC drops from 0.315 → 0.222
- Correctly separates Epcam+ / CD45+ tumor cells without protein labels (matching Pi-ATAC ground truth)
- Improves chromVAR motif detection: 105 significant motifs on imputed vs. 52 on raw Forebrain data
- Mouse atlas (80K cells): F1=0.419, scales to large datasets in ~1.5h, ~2 GB memory

**Biological validation**:
- Leukemia: LSC cells cluster near LMPP (biologically expected — LSCs share stem cell phenotype)
- Forebrain: EX1/EX2/EX3 excitatory neurons cluster together; T-cell subpopulations neighbor each other in UMAP
- Breast Tumor: CD45+ cells enriched for Runx1, Pu.1-Irf, Irf8 (immune TF motifs); Epcam+ cells enriched for Ets1, Nrf2 (cancer-related TF motifs)
- Batch effect detection: features 2,3,4,5,8,10 capture plate-related variation; features 1,6,7,9 capture biological cell type

---

### Reproducibility Rating: 3/5

**Justification**: Code is clean, well-structured, and installable. Core model and loss functions are exact. However:
- **Architecture discrepancy**: The paper's main figure describes a 4-layer encoder (3200-1600-800-400), but the released code defaults to 2-layer [1024, 128] — the paper's "quick mode"
- **Training details**: KL warmup code exists but is commented out (inoperative)
- **Data not bundled**: All 7 datasets must be downloaded from GEO/ArrayExpress separately
- **Newer API changes**: `SCALE_function` in `__init__.py` hardcodes encoder architecture regardless of user input; default clustering method changed from K-means to Leiden

**Setup**:
```bash
git clone https://github.com/jsxlei/SCALE
pip install -e .
# Install: torch, scanpy, anndata, sklearn, scipy, umap-learn
```

**Data access**:
- Leukemia: GSE74310 | GM12878/HEK293T, GM12878/HL-60: GSE68103 | InSilico: GSE65360
- Forebrain: GSE100033 | Splenocyte: E-MTAB-6714 | Breast Tumor: GSE112091
- Mouse atlas: http://atlas.gs.washington.edu/mouse-atac

**Common pitfalls**:
1. `SCALE_function` ignores user-provided `encode_dim` and `latent` — lines 188-189 overwrite them
2. For paper results, use CLI (`SCALE.py`) not `SCALE_function` to ensure correct batch_size=32
3. The `utils.py:reassign_cluster_with_ref` uses `sklearn.utils.linear_assignment_` which is removed in newer sklearn versions — use `scipy.optimize.linear_sum_assignment` instead
4. Default clustering (Leiden) may give different results than paper (K-means); use `--cluster_method kmeans` for reproducibility

**Strengths**: Simple clean codebase; AnnData integration; supports multiple input formats (h5ad, mtx, csv, txt); GPU support built-in
**Weaknesses**: No batch correction beyond feature disentanglement; number of clusters K must be user-specified; architecture discrepancy between paper and code creates confusion

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
