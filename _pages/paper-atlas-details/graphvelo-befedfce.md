---
layout: default
permalink: /paper-atlas/graphvelo-befedfce/
title: "GraphVelo"
nav: false
wide: true
description: "GraphVelo 学到的不是一个全局神经网络，而是每个细胞在局部邻居位移基上的速度系数；它用流形几何约束修正上游 RNA velocity，再在共享邻域结构的其他表示中复用这组系数。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>GraphVelo</h1>
    <p>GraphVelo allows for accurate inference of multimodal velocities and molecular mechanisms for single cells</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-62784-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GraphVelo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xing-lab-pitt/GraphVelo" target="_blank" rel="noopener noreferrer" aria-label="Open code for GraphVelo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GraphVelo：把已有速度投影到细胞状态流形上

### 1. 先说清它是什么

GraphVelo 不是从原始计数中独立估计 RNA velocity 的新动力学模型。它是一个后处理层：输入来自 scVelo、dynamo、VeloVI 等方法的表达矩阵 $X$、速度矩阵 $V$ 和细胞邻居图，学习每个细胞的局部图系数 $\phi_{ij}$。这些系数一方面把原速度修正到数据流形的切空间中，另一方面可在 UMAP、ATAC 或其他共享邻域结构的表示中重建速度。

因此，GraphVelo 能改善或扩展输入速度，但不能消除上游 velocity 估计的识别假设和误差。

### 2. 核心几何：用 kNN 位移近似切空间

假设单细胞状态落在高维空间中的低维流形 $\mathcal M$上。对细胞 $i$，它到 k 个邻居的位移是

$$\delta_{ij}=x_j-x_i,\qquad j\in\mathcal N_i.$$

这些向量不必正交，但在局部可张成一个近似切空间。GraphVelo 将投影速度写为

$$\hat v_i=\sum_{j\in\mathcal N_i}\phi_{ij}\delta_{ij}.$$

代码对应 `graph_velocity.py:46-60`：`D = X[idx] - x`，然后 `v_ = w @ D`。$w$ 就是该细胞的 $\phi_i$。

### 3. 三项损失保留了什么

每个细胞独立求解：

$$
\mathcal L(\phi_i)=a\|\hat v_i-v_i\|^2-b\cos(\phi_i,\phi_i^{\mathrm{corr}})+r\|\phi_i\|^2.
$$

- 重建项让 $\hat v_i$ 近似输入速度的方向和模长；
- 余弦项让学到的邻居系数不要偏离传统 cosine-kernel 方向先验太多；
- L2 项防止系数在局部基病态时无限增大。

`regression_phi()` 在 `graph_velocity.py:59-116` 实现目标和解析梯度，再用 `scipy.optimize.minimize` 求解。`GraphVelo.train()` 的用户级默认是 $a=1,b=10,r=1$（`graph_velocity.py:297-318`）；底层 `regression_phi()` 和 `tangent_space_projection()` 单独调用时却默认 `b=0`。两组默认值不同，所以复现时应记录调用入口。

初值使用 cosine kernel 的局部值 `x0=C[i, idx]`。求解结果直接取 `res["x"]`，代码没检查 `res.success`；因此极端病态邻域的优化失败可能被静默接受。

### 4. cosine kernel 与密度校正

对邻居 $j$，方向先验是

$$
\phi_{ij}^{\mathrm{corr}}=\frac{v_i^T(x_j-x_i)}{\|v_i\|\,\|x_j-x_i\|}.
$$

`cos_corr()` 对零距离和零速度做了分母保护（`tangent_space.py:65-75`）。`density_corrected_transition_matrix()` 再从每行非零邻居权重中减去行均值（`117-126`）。这个矩阵是方向先验，不是已归一化的马尔可夫转移概率。

### 5. PCA 近似在做什么

默认 `approx=True`。代码先估计一个局部时间步 $dt_i$，构造短时未来状态

$$x_i'=x_i+v_i dt_i,$$

将负值截为 0，对 $x_i$ 和 $x_i'$ 做 `log1p`，在 $X$ 上拟合 PCA，最后计算

$$v_i^{PCA}=\frac{P(x_i')-P(x_i)}{dt_i}.$$

实现在 `graph_velocity.py:274-285`。这不是对原速度简单右乘 PCA loading，因为中间有截断和非线性 `log1p`。

论文用“中位数”描述 $dt$，但 `_estimate_dt()` 先将所有邻居距离取均值得到一个标量，再对该标量取 `np.median`（`tangent_space.py:39-44`）；中位数在此没有作用，实际是“平均邻居距离/速度模长”。对零速度没有保护，可能生成无穷大 $dt$。

### 6. 为什么同一组 $\phi$ 能投影到其他表示

学习完 $\phi_{ij}$ 后，对任意目标表示 $y$，`project_velocity()` 计算

$$\hat v_i^{(y)}=\sum_{j\in\mathcal N_i}\phi_{ij}(y_j-y_i),$$

实现在 `graph_velocity.py:320-358`。这是局部线性嵌入式的系数复用：保留“沿哪些邻居方向运动以及权重多大”，替换的是邻居位移基。

论文用 Whitney embedding/homeomorphism 说明其几何动机，但代码不检验源表示与目标表示是否同胚、邻域是否保持或映射是否可逆。因此“可投影到任意表示”是调用能力，不是数据上自动成立的数学保证。

### 7. 多组学和全基因速度是怎样扩展的

多组学模式下，GraphVelo 从 `adata.uns['WNN']['indices']` 取联合邻居，而不是普通 RNA kNN（`graph_velocity.py:262-271`）。`mo.py` 包含 RNA PCA、ATAC LSI 和 WNN 工具，但这只建立联合邻域；ATAC 速度仍来自将同一 $\phi$ 应用到 ATAC/基因活性位移。

MacK score 判断某基因的速度符号是否与伪时间邻居的表达变化符号一致。代码先对每个细胞计算 k 个邻居的符号一致比例，再对细胞取平均得到基因分数（`utils.py:448-487`）。选出可信 MacK genes 后，GraphVelo 可把它们学到的局部运动系数应用到更大的基因表达空间。这是流形上的速度扩展，不等于为每个新基因拟合了独立的剪接动力学参数。

### 8. 五张主图的证据链

- **图 1**：方法流程、切空间投影、表示间速度转换，以及全基因、病毒和多组学应用的总览。
- **图 2**：在已知轨迹的模拟分叉/环状系统上比较方向、模长和误差，支持 TSP 比纯 cosine kernel 更能保留定量速度。
- **图 3**：展示 MacK 选择和全基因速度扩展，以及后续状态/稳态分析。
- **图 4**：在病毒—宿主数据中建立病毒因子速度趋势、相关通路和虚拟扰动。虚拟扰动是模型预测，不是实验干预证据。
- **图 5**：将 RNA 与染色质可及性动力学相比，展示耦合/解耦和转录因子的先后关系。时序先后和 Jacobian 关联不自动等于已确认的分子因果。

### 9. 复现和使用边界

1. 必须先有可用的上游速度、表达 layer 和邻居索引。
2. `approx=True` 会删除任一细胞速度为 NaN 的整个基因（`graph_velocity.py:246-259`）。
3. TSP 先创建 $n\times n$ 稠密矩阵 `E`，最后才转 CSR；因此虽然结果稀疏，训练阶段仍有 $O(n^2)$ 内存峰值（`graph_velocity.py:170,190-193,317`）。
4. `n_jobs=None` 会使用全部 CPU，在共享机器上应显式限制。
5. 代码快照包含大量数据集 notebook，但本次是源码/论文/图证据审计，未重跑全部实验。

### 10. 一句话总结

GraphVelo 学到的不是一个全局神经网络，而是每个细胞在局部邻居位移基上的速度系数；它用流形几何约束修正上游 RNA velocity，再在共享邻域结构的其他表示中复用这组系数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GraphVelo: Accurate Inference of Multimodal Velocities and Molecular Mechanisms

### Paper Information
- **Title**: GraphVelo allows for accurate inference of multimodal velocities and molecular mechanisms for single cells
- **Authors**: Yuhao Chen, Yan Zhang, Jiaqi Gan, Ke Ni, Ming Chen, Ivet Bahar, Jianhua Xing
- **Journal**: Nature Communications, vol. 16, 2025-08-22
- **DOI**: 10.1038/s41467-025-62784-w
- **GitHub**: https://github.com/xing-lab-pitt/GraphVelo

---

### Motivation & Novelty

#### Biological Problem

RNA velocity — estimating the rate of gene expression change from spliced/unspliced transcript ratios — enables reconstruction of cellular dynamics from snapshot single-cell data. Despite its impact, the framework has three fundamental limitations:

1. **Erroneous velocities for MURK genes**: Genes with Multiple Rate Kinetics (transcription bursts, miRNA-mediated rapid degradation) violate constant-rate assumptions, leading to incorrect or sign-inverted velocity estimates. Bergen et al. (Mol. Syst. Biol., 2021) documented that these failures are common.

2. **Loss of velocity magnitude**: The cosine kernel method used to project velocities to 2D embeddings is mathematically proven to completely lose magnitude information (Li et al., CSIAM Trans. Appl. Math., 2021). A visually correct UMAP arrow field does not imply accurate high-dimensional velocity estimation.

3. **Non-generalizable to other modalities**: Multi-omics sequencing captures chromatin accessibility (scATAC), protein levels, and viral transcripts alongside RNA, but no systematic method extends velocity to these modalities. Existing attempts (MultiVelo, Li et al., Nat. Biotechnol., 2023) lack rigorous geometric foundations.

#### Limitations of Existing Methods

| Method | Limitation | How GraphVelo Addresses It |
|---|---|---|
| scVelo (Nat. Biotechnol. 2020) | Constant degradation rate; MURK genes fail; magnitude lost in projection | TSP preserves magnitude; MacK genes filter unreliable estimates |
| VeloVI (Nat. Methods 2024) | Probabilistic but still splicing-based; no multi-omics | Whitney embedding extends to any modality |
| MultiVelo (Nat. Biotechnol. 2023) | RNA and ATAC results inconsistent; no rigorous manifold basis | WNN-based unified manifold; consistent velocities across modalities |
| CellDancer (Nat. Biotechnol. 2024) | Per-cell kinetics but single modality; relay model assumptions | GraphVelo is model-free; any input velocity works |
| UniTVelo (Nat. Commun. 2022) | Unified time but still splicing-based | Agnostic to velocity source |
| DeepVelo (Genome Biol. 2024) | Deep learning but single modality | Plugin approach works with any method's output |

#### Unique Contributions

1. **Tangent space projection (TSP)**: Projects RNA velocity onto the data manifold's tangent space, preserving both magnitude and direction simultaneously.

2. **Representation-invariant velocity transformation**: The same learned φ coefficients transfer velocities between any homeomorphic representations (gene space → PCA → UMAP → ATAC space → viral space), justified by the Whitney Embedding Theorem.

3. **MacK gene framework**: Principled selection of manifold-consistent kinetic genes for extending velocity to the full transcriptome.

4. **Seamless dynamo integration**: GraphVelo-corrected velocities feed directly into dynamo's differential geometry pipeline (Jacobian, LAP, in silico perturbation), enabling quantitative gene regulatory network inference.

---

### Method Overview

#### Algorithmic Framework

GraphVelo is a **post-processing plugin** that takes any RNA velocity vector as input and outputs a manifold-consistent refinement. The core insight: a velocity vector that truly describes cell state dynamics must lie in the tangent space of the cell manifold — a constraint violated by all existing methods.

**Three mathematical components:**

1. **Local tangent space approximation**: k-nearest neighbors in gene/PCA space define an overcomplete basis for the local tangent plane via displacement vectors $\boldsymbol{\delta}_{ij} = \mathbf{x}_j - \mathbf{x}_i$.

2. **Optimization-based projection**: Coefficients $\phi_{ij}$ minimize a three-term loss:
   $$\mathcal{L}(\phi_i) = a\|\mathbf{v}_i - \sum_j \phi_{ij}\delta_{ij}\|^2 - b\cos(\phi_i, \phi_i^{corr}) + \lambda\|\phi_i\|^2$$
   balancing magnitude preservation (term 1), directional prior from cosine kernel (term 2), and regularization (term 3).

3. **Whitney embedding-based velocity transfer**: The same $\phi_{ij}$ apply velocity inference to any homeomorphic representation:
   $$\mathbf{v}_\parallel(\mathbf{y}_i) = \sum_{j \in \mathcal{N}_i} \phi_{ij}(\mathbf{y}_j - \mathbf{y}_i)$$

**Practical pipeline:**
```
Input velocities (scVelo/VeloVI/dynamo/etc.)
    → PCA denoising (clip → log1p → 30-PC projection)
    → Cosine kernel C^corr (directional prior)
    → TSP optimization (parallelized per-cell L-BFGS-B)
    → MacK gene selection (manifold-consistent kinetics)
    → Full-genome velocity extension via Whitney embedding
    → Downstream: dynamo vector field → Jacobian → perturbation
```

#### Key Technical Components

1. **PCA-space optimization** (default): Reduces from ~2000 gene dimensions to 30 PCs before TSP optimization. Uses log1p-normalized counts with cell-specific adaptive time steps to ensure the extrapolated future state remains on the manifold.

2. **MacK (Manifold-consistent Kinetics) score**: Per-gene metric measuring fraction of neighbors where velocity sign agrees with pseudotime-based expression change. Used to select high-confidence "seed" genes for whole-genome extension.

3. **Weighted Nearest Neighbors (WNN)**: For multi-omics data, cell neighborhoods are defined in the combined RNA+ATAC space, enabling a single coherent manifold for velocity inference.

4. **DTW distance for decoupling analysis**: Dynamic time warping between GAM-smoothed chromatin and RNA velocity temporal trends identifies genes with decoupled epigenetic and transcriptional dynamics.

---

### Evaluation

#### Synthetic Benchmarks

| Dataset | Setup | GraphVelo vs. Cosine Kernel |
|---|---|---|
| 3D sphere bifurcation (n=2000) | Known ground truth; added orthogonal noise | GraphVelo: normal component ~0, cosine ~0 (both good). RMSE: **GraphVelo wins significantly** (p<0.05); cosine loses magnitude entirely |
| dyngen linear (n=1000, 100 genes) | Linear topology; three metrics | Cosine similarity: similar; RMSE: **GraphVelo better**; Accuracy: **GraphVelo better** |
| dyngen cyclic | Cyclic topology | GraphVelo TSP+cosine term outperforms TSP without cosine term |
| dyngen bifurcating | Bifurcating topology | GraphVelo robustly correct at all noise levels (Supp. Fig. 1a-c) |
| Speed scaling (PCA space) | Ground truth speed correlation | **GraphVelo high correlation**, cosine kernel fails completely (Supp. Fig. 1d) |

#### Real-World Benchmarks

**CBC score comparison** (5 datasets: FUCCI, pancreatic endocrinogenesis, dentate gyrus, intestinal organoid, hematopoiesis):
- GraphVelo consistently improved CBC scores vs. input scVelo velocity
- Compared against: scVelo, VeloVI (Nat. Methods 2024), UniTVelo (Nat. Commun. 2022), DeepVelo (Genome Biol. 2024), CellDancer (Nat. Biotechnol. 2024)
- GraphVelo achieves "noticeably improved" CBC against all methods
- Trade-off: slightly lower velocity consistency score than over-smoothed methods, but this reflects preserved biological heterogeneity

**Erythroid differentiation** (mouse gastrulation, n=9,815 cells, Pijuan-Sala et al., Nature 2019):
- Vector field-based pseudotime Spearman correlation with embryonic time: high (Fig. 3d)
- Correctly infers velocities for MURK genes Smim1 and Hba-x (scVelo fails)
- GO enrichment of top MacK genes: heme biosynthetic process, IL-12 signaling

**Human bone marrow** (n=5,780 cells, Setty et al., Nat. Biotechnol. 2019):
- Recovered 3-branch differentiation (erythroid/monocyte/CLP) where scVelo could not
- CellRank terminal states match known biology (Fig. 3k)

**HCMV infection** (n=1,454 moDC cells, Costa et al., Nat. Commun. 2024):
- MacK scores for viral genes significantly higher than CellRank pseudotime kernel or random predictor (Welch's t-test p<0.05, Fig. 4d)
- Pseudotime-viral RNA% correlation: GraphVelo > scVelo

**SHARE-seq mouse hair follicle** (multi-omics):
- Both RNA and ATAC velocities predict 3 correct terminal states
- MultiVelo: inconsistent between modalities; all other methods fail to capture all 3 fates (Fig. 5b)
- DTW distance: identified cell cycle-dependent decoupled genes enriched in cell cycle processes

#### Spatial Transcriptomics

Mouse coronal hemibrain (bin60, n=7,765 bins):
- Coherent velocity fields with anatomically structured transitions
- Sharper transcription speed in dentate gyrus (neurogenic region) vs. uncorrected dynamo

---

### Key Biological Discoveries

#### Erythroid Development — Kinase Activation Cascade
- Sequential TF activation: Gata2 → Gata1 → Klf1 (confirmed by Jacobian analysis)
- Gata1 represses Gata2 (negative feedback); Spi1 (PU.1) represses Gata1
- In silico: inhibiting Gata1 or upregulating Spi1 reverses erythropoiesis direction
- Car2 and Fth1: high peak velocity amplitude consistent with complex enhancer regulation (Lee et al., Cell Rep., 2017)

#### HCMV Host-Virus Dynamics
- First inference of RNA velocity for viral genes (no introns) via Whitney embedding
- UL122 shows overshooting kinetics → identified negative autoregulation of its own promoter
- Viral genes clustered into acceleration/deceleration modules along infection axis
- Jacobian: viral factors systematically silence IFN/NFκB signaling
- In silico viral knockout: UL123 inhibition has largest total viral RNA reduction effect

#### SARS-CoV-2 Infection Fates
- Vector field topology: initial state (low viral load) → two terminal states + saddle point
- Cluster M (interferon-producing) identified as attractor = abortively infected state
- Abortive vs. apoptotic lineages: distinct pathways (interferon vs. unfolded protein response)
- ERBB2 inhibition pathway enriched in productive infection lineage

#### Multi-omics Hair Follicle Dynamics (SHARE-seq)
- Most cell cycle-dependent (CCD) genes show decoupled chromatin/RNA dynamics: chromatin stays open while transcription decreases along differentiation (DTW analysis)
- Pioneer TF discovery: Lef1 first opens Wnt3 chromatin, then activates Wnt3 transcription; Hoxc13 shares same mechanism
- Novel root cells identified via LAP: Shh-Runx1 signaling axis mediates fate conversion
- Validated in independent dataset (Joost et al., Cell Stem Cell, 2020)

---

### Reproducibility Assessment

**Rating: 4/5**

#### Strengths
- Complete Python package on PyPI (`pip install graphvelo`); version 0.1.11 associated with this paper
- All 24 analysis notebooks provided with dataset download links
- All datasets publicly accessible; explicit download URLs in Methods §Data availability
- Documentation at https://graphvelo.readthedocs.io; Zenodo archive: 10.5281/zenodo.15852884

#### Practical Blockers
- Requires dynamo-release for downstream vector field analyses (separate install, complex setup)
- Multi-omics analysis requires SCARlink for LSI preprocessing (paper deviates from MultiVelo's default)
- Hyperparameter sensitivity (a, b, λ) not systematically characterized beyond default values
- Some notebooks use dataset-specific pre-processing not fully standardized

#### Environment Setup
```bash
conda create -n graphvelo python=3.8
pip install graphvelo
pip install dynamo-release  # for downstream analyses
pip install scvelo          # for velocity preprocessing
pip install dtaidistance    # for multi-omics DTW
```

#### Common Pitfalls
- **kNN must be pre-computed** before `GraphVelo()` init — run `dyn.tl.neighbors()` or `scv.pp.neighbors()` first
- **Multi-omics**: set `mo=True` and ensure `adata.uns['WNN']` exists before training
- **CBC score**: use `basis='raw'` to match paper methodology; default `basis='pca'` differs
- **MacK score**: requires a pseudotime key (`tkey`) in `adata.obs` — latent time or DPT/Palantir pseudotime
- **Dynamo compatibility**: GraphVelo was tested with dynamo ≥1.0; ensure `velocity_S` layer key matches dynamo convention

#### Strengths and Weaknesses

**Strengths:**
- Mathematically rigorous foundation (Zwanzig-Mori projection, Whitney embedding)
- Agnostic to velocity input method — works with any existing RNA velocity tool
- Scalable: parallel optimization + Numba JIT
- Validated across diverse biological systems and data modalities
- Enables downstream quantitative analysis impossible before (velocity magnitude, multi-modal Jacobian)

**Weaknesses:**
- Requires pre-existing RNA velocity from another method — cannot replace velocity estimation entirely
- UMAP velocity projections less accurate (UMAP is not a continuous transformation)
- MacK score requires pseudotime — circular dependency if pseudotime is velocity-derived
- Multi-omics pipeline requires multiple external tools and careful preprocessing
- No uncertainty estimates for φ coefficients

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
