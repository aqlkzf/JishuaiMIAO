---
layout: default
permalink: /paper-atlas/scviva-e1e22aa3/
title: "scVIVA"
nav: false
description: "scVIVA 处理一个很具体的问题：空间转录组里的细胞既有自身表达状态，也处在由其他细胞组成的微环境中。如果直接把邻域特征拼到细胞表达上，模型可能连与该细胞无关的空间结构也记住；如果完全忽略空间，又会错过由生态位诱导的细胞状态。scVIVA 的折中是：从细胞自身表达编码潜变量，再要求这个潜变量同时预测细胞表达和邻域摘要。因此，邻域只有在能够由该细胞的转录组预测时，才会进入表示。"
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
      <span>Representation Models</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>scVIVA</h1>
    <p>scVIVA: A Probabilistic Framework for Representation of Cells and Their Environments in Spatial Transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.06.01.657182" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scVIVA：让细胞状态只吸收“与自身转录组有关”的空间环境信息

scVIVA 处理一个很具体的问题：空间转录组里的细胞既有自身表达状态，也处在由其他细胞组成的微环境中。如果直接把邻域特征拼到细胞表达上，模型可能连与该细胞无关的空间结构也记住；如果完全忽略空间，又会错过由生态位诱导的细胞状态。scVIVA 的折中是：**从细胞自身表达编码潜变量，再要求这个潜变量同时预测细胞表达和邻域摘要**。因此，邻域只有在能够由该细胞的转录组预测时，才会进入表示。

### 1. 输入、输出与两阶段流程

对细胞 $n$，输入包括原始计数向量 $\boldsymbol{x}_n$、空间坐标 $\boldsymbol{y}_n$、粗粒度细胞类型 $c_n$，以及可选的样本或批次 $s_n$。论文实验用空间上最近的 $K=20$ 个细胞定义邻域（论文第 2.1 节；本地 `code/brain/params.py:45` 也设为 20）。

模型最终提供两类输出：

- 概率性的低维细胞表示 $\boldsymbol{z}_n$，用于整合、可视化、聚类和发现生态位依赖状态；
- 由生成模型得到的归一化表达估计，用于差异表达分析。

训练前先用不使用空间坐标的 scANVI 得到每个细胞的低维表达状态。然后 scVIVA 构造邻域摘要并训练第二个潜变量模型。本地脑数据配置中，scANVI 和 scVIVA 潜空间均为 10 维；这是该复现实验的配置，不是方法对所有数据的硬性限制。

### 2. 邻域怎样被压缩成 $\alpha_n$ 和 $\eta_n$

scVIVA 不把 20 个邻居逐个送入模型，而是形成两个互补摘要。

#### 2.1 细胞类型组成 $\boldsymbol{\alpha}_n$

$\boldsymbol{\alpha}_n$ 是一个 $T$ 维比例向量，记录邻居中各细胞类型的占比，并位于概率单纯形上。假设 20 个邻居中有 10 个 T 细胞、6 个 B 细胞、4 个巨噬细胞，则相应分量为 $(0.5,0.3,0.2)$。它回答“这个细胞周围是谁”。

#### 2.2 按细胞类型聚合的邻域表达 $\boldsymbol{\eta}_n$

仅知道组成还不够：同一种邻居也可能处于不同状态。scVIVA 取第一阶段得到的邻居低维表达嵌入，并按细胞类型分别求平均，得到 $\boldsymbol{\eta}_n\in\mathbb{R}^{T\times D}$。若某类细胞未出现在邻域中，该行设为零，其对应的高斯似然项不参与计算。它回答“每类邻居处于什么表达状态”。

本地 runner 将第一阶段潜表示放入 `adata.obsm["qz1_m"]`，再调用 `nichevi.nicheSCVI.preprocessing_anndata(..., k_nn=K_NN)` 生成 `neighborhood_composition`、邻居索引和按类型聚合的表达键（`code/brain/runner.py:201-248`）。这是论文邻域定义与本地代码之间最直接的桥。

### 3. 概率模型：一个编码器，三个预测方向

编码器仅从细胞观测表达（并结合批次条件）近似后验：

$$
q(\boldsymbol z_n\mid \boldsymbol x_n,s_n)=\mathcal N(\boldsymbol\mu_n,\operatorname{diag}(\boldsymbol\sigma_n^2)),
$$

先验是标准高斯。抽样得到的 $\boldsymbol z_n$ 被送入三个解码方向：

$$
\boldsymbol x_n\mid \boldsymbol z_n,s_n\sim\operatorname{Poisson}(f_x(\boldsymbol z_n,s_n)),
$$

$$
\boldsymbol\alpha_n\mid \boldsymbol z_n\sim\operatorname{Dirichlet}(f_\alpha(\boldsymbol z_n)),
$$

$$
\boldsymbol\eta_{nt}\mid \boldsymbol z_n,\alpha_{nt}>0
\sim\mathcal N(\boldsymbol\mu_{nt}(\boldsymbol z_n),\operatorname{diag}(\boldsymbol\sigma_{nt}^2(\boldsymbol z_n))).
$$

三种分布分别对应计数、组成比例和连续的邻域表达嵌入。训练共同优化表达 ELBO、细胞类型分类项和两个邻域重建项。论文把主要权重概括为分类权重 $\rho=20$ 与空间权重 $\beta=10$；本地活动配置实际向外部模型传入 `spatial_weight=10`、`niche_rec_weight=10`、`compo_rec_weight=10`（`code/brain/params.py:111-127`）。由于核心损失实现在本地仓库中不存在，不能据此断言三者在内部是相乘还是独立相加，也不能从 runner 验证 $\rho=20$ 的具体实现。

这个结构的关键不是“把空间强行塞进表示”，而是让 $z$ 从自身表达出发承担预测邻域的任务。若坐标被随机打乱后邻域与自身表达失去关系，模型没有理由稳定保留该随机空间标签；论文的细胞类型逐类坐标打乱实验正是检验这一点。

### 4. 从表示到生态位依赖细胞状态

训练后，研究者可在 $z$ 上进行 UMAP、聚类、跨切片整合，或用 Hotspot 按潜空间相似性寻找共变基因模块。论文中的三个主要应用是：

1. 小鼠脑：在兼顾批次混合和细胞类型保持的同时保留脑区相关状态，并从星形胶质细胞中找出丘脑、下丘脑和纹状体相关模块。
2. 乳腺癌：区分侵袭区与基质区中的内皮细胞状态，随后用 2-step DE 区分真正的内皮标志与邻近上皮信号。
3. 泛癌图谱：整合 18 张切片、8 种癌症中的 T 细胞，识别与不同肿瘤微环境相关的 CD8+ T 和 Treg 状态。

### 5. 2-step DE：为什么普通组间比较会误报邻居基因

空间测量可能把邻近细胞的分子错误分配给目标细胞。设目标细胞的两个状态为 $C1$ 和 $C2$，并令 $N1$ 为 $C1$ 周围、排除与目标同类型连接后的邻居集合。若只比较 $C1$ 与 $C2$，一个在 $N1$ 中很高的基因也可能被误判为 $C1$ 标志。

scVIVA 因此计算三个比较：$C1$ 对 $C2$、$N1$ 对 $C2$、$C1$ 对 $N1$。真正的局部标志应满足：它不但在 $C1$ 相对 $C2$ 上调，而且信号更像来自 $C1$ 本身：

$$
LFC_{C1\,vs\,C2}^{g}>LFC_{N1\,vs\,C2}^{g}.
$$

方法先用 $C1$ 对 $N1$ 的显著性构造“局部标志”训练标签，再以
$[LFC_{C1\,vs\,C2},LFC_{N1\,vs\,C2}]$ 为二维特征训练高斯过程分类器。分类器为每个基因输出局部标志概率 $p_g^{S_1}$，再用阈值 $\Delta$ 过滤邻域来源基因。论文 Methods E 和 Algorithm 1 给出了完整流程，并报告 DE 邻域使用 $k_{DE}=6$；这个实现主要在外部 `nichevi` 和分析 notebook 中，本地 runner 不能完整逐行验证。

一个直观例子是乳腺癌内皮细胞：普通 DE 可能把邻近上皮细胞的 `FOXA1`、`KRT7` 当作内皮信号；加入 $N1$ 后，这类基因会显示“邻居也很高”，从而被过滤，而 `ESM1` 等更符合局部内皮程序。论文还用两种细胞分割结果比较，2-step DE 的标志集合一致性高于普通比较。

### 6. 图应该怎样连起来读

- Figure 1 是机制总图：先构造 $\alpha$、$\eta$，再由细胞表达编码 $z$，用三个解码方向约束表示。
- Figure 2 验证表示性质：既保留细胞类型/脑区信息，又在坐标打乱后不应继续记住无关空间结构。
- Figure 3 把该表示用于星形胶质细胞的区域性基因模块。
- Figure 4 把表示聚类与 2-step DE 串联，展示乳腺癌侵袭生态位及邻域污染过滤。
- Figure 5 展示跨癌种、跨切片整合后的 T 细胞生态位状态。
- 补图 S1–S7 已嵌入同一份 `paper.md`：S1 扩展打乱检验，S2–S4 展示脑数据 Hotspot 模块，S5–S6 展示乳腺癌模块、重分割和反向 DE，S7 扩展泛癌结果。

当前 VLM 导出的若干图片文件是局部裁剪，因此具体面板数值应同时核对论文 caption 和 `figure_analysis.md`，不能只凭单个裁剪图推断整张主图。

### 7. 论文—本地代码对应与复现边界

| 机制或设置 | 本地证据 | 状态 |
|---|---|---|
| $K=20$ 空间近邻 | `code/brain/params.py:45`；`runner.py:244-248` | Exact |
| 第一阶段 scANVI、10 维、Poisson | `code/brain/params.py:28-36` | Exact（脑数据配置） |
| 邻域组成与按类型表达键 | `code/brain/runner.py:201-255` | Exact |
| 调用 `nichevi.nicheSCVI` 及三个权重 | `code/brain/runner.py:264-287`；`params.py:111-127` | Exact（API 参数） |
| 1000 epochs、batch 1024、lr $5\times10^{-4}$ | `code/brain/params.py:55-58`；`runner.py:289-300` | Exact（脑数据配置） |
| Dirichlet/Gaussian 解码器内部实现与总损失组合 | 外部 `nichevi` 类未包含在本地快照 | Not found |
| 论文的 $\rho=20$ 如何在代码中生效 | 本地只见 `linear_classifier=True` | Partial |
| 2-step DE 完整 GP/lvm-DE 实现 | 论文有算法；本地以 notebook/外部 API 为主 | Partial |

本地仓库是 `scVIVA-reproducibility` 分析快照，包含脑、乳腺癌、泛癌 runner、notebook、基线和部分结果，但不包含核心 `nicheSCVI` 类源码；提交哈希也未记录。部分参数文件还带作者机器的硬编码数据路径。因此它足以核对实验调用和多数超参数，但不是一个仅靠当前目录即可从零重建模型内部实现的自包含软件包。

### 8. 最容易误解的三点

1. **$z$ 不是邻域本身的嵌入。** 编码器从目标细胞表达得到 $z$；邻域是训练时要求 $z$ 预测的辅助目标。
2. **生态位组成与生态位表达不是一回事。** $\alpha$ 表示“有哪些类型”，$\eta$ 表示“这些类型处于什么状态”，二者缺一都会丢信息。
3. **2-step DE 不是简单多做一次 DE。** 它显式构造异型邻居对照，并把两条 LFC 轴交给概率分类器，目标是识别信号究竟来自目标细胞还是其空间邻居。

### 证据入口

- 论文及内嵌补图：`paper source/paper/vlm/paper.md`
- 图像目录：`paper source/paper/vlm/images/`
- 复现代码：`code/`
- 逐图分析：`figure_analysis.md`
- 详细数学与流程：`doc_method.md`
- 论文—代码证据表：`doc_code.md`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scVIVA Summary

### Paper Information
- **Full title**: scVIVA: A Probabilistic Framework for Representation of Cells and Their Environments in Spatial Transcriptomics
- **Authors**: Nathan Levy, Florian Ingelfinger, Artemii Bakulin, Giacomo Cinnirella, Pierre Boyeau, Boaz Nadler, Can Ergen, Nir Yosef
- **Affiliation**: Weizmann Institute of Science; UC Berkeley
- **Journal**: bioRxiv preprint (2025)
- **DOI**: 10.1101/2025.06.01.657182
- **Code**: github.com/LevyNat/scVIVA-reproducibility; model in scvi-tools

---

### Motivation & Novelty

#### Biological Problem
Cells in multicellular tissues don't act independently — their function is shaped by neighboring cells (the "niche"). Spatial transcriptomics (ST) technologies such as MERFISH and 10X Xenium measure transcriptomes alongside physical coordinates, enabling the study of niche effects. However, most computational tools for ST still embed cells ignoring their spatial context.

#### Limitations of Existing Approaches
- **scVI** (Lopez et al., *Nature Methods* 2018): Spatially unaware; no niche encoding
- **Harmony** (Korsunsky et al., *Nature Methods* 2019): Batch correction only; ignores spatial context
- **ENVI** (Haviv et al., *Nature Biotechnology* 2024): Spatially-aware but requires paired scRNA-seq (hard to obtain)
- **simVI** (Dong et al., *bioRxiv* 2023): Spatially-aware but limited multi-sample integration and batch correction
- **BANKSY** (Singhal et al., *Nature Genetics* 2024): Performs well on spatial benchmarks but a-priori concatenates cell + niche features, cannot filter niche properties unrelated to the cell's transcriptome; embedding persists niche signal even after shuffling spatial coordinates
- **Nicheformer** (foundation model): Ignores spatial coordinates during training; poor spatial benchmarks

#### Unique Contributions
1. **Niche-filtered representation**: z captures only niche properties that are *predictable* from the cell's own transcriptome, filtering out niche variation irrelevant to cell state
2. **Multi-sample batch correction**: Works with ST data only (no paired scRNA-seq); integrates across samples/slides
3. **Two-step DE procedure**: Uses GP classifier to filter out spurious DE signals caused by molecule misassignment in ST segmentation errors
4. **Scales to 10M cells**: Niche features precomputed; training comparable speed to spatially-unaware models

---

### Method Overview

#### Core Framework
scVIVA is a variational autoencoder (VAE) that models each cell's expression as a function of a latent variable z that encodes both intrinsic cell state and niche context.

**Two-stage pipeline:**
1. **Stage 1**: Train scANVI (spatially-unaware VAE with linear classifier) to get clean 10-D cell state embeddings
2. **Stage 2**: Precompute niche features (K=20 spatial NN) → cell-type composition α ∈ Δ^{T-1} and niche expression η ∈ R^{T×D} (per-type averaged scANVI embeddings)
3. **Stage 3**: Train nicheSCVI with combined objective: reconstruct cell expression (Poisson) + predict niche composition (Dirichlet) + predict niche expression (Gaussian) + classify cell type (cross-entropy)

**Four neural networks:**
- Encoder q(z|x,s): raw counts + batch → latent z (N_LAYERS=1, N_HIDDEN=128)
- Expression decoder p(x|z,s): latent z → Poisson rates (G-dimensional)
- Composition decoder p(α|z): latent z → Dirichlet parameters (T-dimensional)
- Niche expression decoder p(η_t|z): latent z → Gaussian μ,σ per cell type (one per type, D-dimensional)

**Total loss**: $\mathcal{L} = \mathcal{L}_{ELBO} + 20 \cdot \mathcal{L}_{type} + 10 \cdot \mathcal{L}_{niche}$

**Key design principle**: By training z to predict both cell expression AND neighborhood properties, z implicitly learns niche-dependent gene programs. The Dirichlet and Gaussian niche decoders make this a discriminative prediction of the niche from the cell's latent state — only niche variation that correlates with the cell's own transcriptome is captured.

**Important implementation detail**: Despite the paper describing η as "average gene expression state," the implementation uses **scANVI latent embeddings** (10-dimensional) averaged per cell type, not raw gene counts (300–1100 genes). This is architecturally cleaner — latent embeddings are noise-reduced and dimensionality-matched to z — but means the model predicts latent niche context, not raw transcript levels directly. This choice is disclosed in Methods B: "we leverage a low dimensional gene expression embedding."

#### Downstream Capabilities
1. **Cell embeddings**: z used for UMAP, clustering, integration across samples
2. **Gene module discovery**: Hotspot applied to scVIVA latent space to find spatially co-regulated genes
3. **Differential expression**: 2-step procedure using lvm-DE + GP classifier to filter spatially-spurious DE

---

### Evaluation

#### Dataset 1: MERFISH Mouse Brain
- **Data**: 6 coronal sections from 2 mice, 250k cells, 1100 genes (Zhang et al., *Nature* 2023)
- **Metrics**: scIB (silhouette, iLISI, kBET, graph connectivity, cLISI)
- **Cell-type benchmark (Fig 2B)**: scVIVA comparable to scANVI; both outperform BANKSY (even with Harmony correction) and Nicheformer
- **Region-preservation benchmark (Fig 2C)**: scVIVA and BANKSY best at capturing niche information; simVI shows limited improvement over scANVI
- **Shuffling experiment (Fig 2D-E)**: After shuffling cell coordinates within type, scVIVA LISI distributions collapse to random (like scANVI); BANKSY still retains shuffled niche signal — demonstrating scVIVA filters niche-irrelevant variation

#### Dataset 2: Xenium Human Breast Cancer
- **Data**: 280k cells, 313 genes; Proseg re-segmentation → 279k cells (Janesick et al., *Nature Communications* 2023)
- **Key result**: 2-step DE on endothelial cells in invasive vs. stromal regions identifies ESM1, SNAI1, KDR as true endothelial markers of angiogenesis. Simple DE misidentifies FOXA1 (epithelial), KRT7 (epithelial) as spurious endothelial genes
- **Validation**: Jaccard index comparison between original and re-segmented DE results shows higher consistency with 2-step method
- **Biological finding**: Invasive niche endothelial cells exhibit endothelial-to-mesenchymal transition (EndMT) signature; stromal endothelial cells express mature vascular markers (EDN1, CAVIN2, CLDN5)

#### Dataset 3: Vizgen MerScope Pan-Cancer Atlas
- **Data**: 18 tumor slices, 8 cancer types, 10 million cells, 550 genes (Vizgen MERSCOPE FFPE)
- **Annotation**: Proseg re-segmentation → 10.37M cells; coarse cell types via Louvain + manual; resolVI for full propagation
- **T cell analysis**: Hotspot on scVIVA latent identifies 4 T cell gene modules: Treg (FOXP3/CD25/CTLA4), central memory (CCR7/CD28/KLF2), effector CD8+ (NKG7/GZMH/GZMK), exhausted CD8+ (PDCD1/LAG3/HAVCR2)
- **Key finding**: Tumor-adjacent Tregs upregulate immunosuppression markers (FOXP3, TIGIT, CCR8); lymphoid-adjacent Tregs upregulate migratory receptors (CCR7, CXCR4). Consistent across all 8 cancer types.
- **CD8+ T cell finding**: Exhausted CD8+ T cells largely restricted to tumor-rich niches across all cancer types; lymphoid-adjacent CD8+ T cells retain migratory potential (CCR7, CXCR4, GZMK)

---

### Reproducibility

**Rating: 3/5**

**Justification**: The reproducibility repository provides complete analysis scripts with hyperparameters, benchmark comparisons, and dataset links. However, the core model source code (nicheSCVI / niche-VI) is NOT in the repo — it lives in an archive GitHub repo (github.com/YosefLab/niche-VI) and is now integrated into scvi-tools. Reproducing results requires installing the right version of scvi-tools or the archived nichevi package, which adds friction.

**Strengths:**
- Full hyperparameter specification in params.py (no hyperparameter ambiguity)
- All datasets are publicly available (CellXGene, 10X Genomics, Vizgen)
- Model is in scvi-tools → well-maintained, installable
- Training code covers all 3 case studies with exact configurations

**Weaknesses:**
- Core model source code not included in reproducibility repo (external dependency)
- Preprocessing scripts for raw data → h5ad not included (especially the 10M cell Vizgen dataset)
- DE analysis/figure generation notebooks are partial — some figures use notebook-specific code
- Trained model checkpoints included but reference data paths are hardcoded to author's machine

**Practical notes:**
1. Install: `pip install scvi-tools` (current version) or clone github.com/YosefLab/niche-VI for archive
2. Data download: brain (CellXGene portal), breast (10X Genomics), pancancer (Vizgen MERSCOPE FFPE)
3. Requires GPU ≥ 8GB VRAM for large datasets (10M cells needs multiple GPUs)
4. Common pitfall: nichevi package not in PyPI; must install from GitHub or use scvi-tools integration
5. Common pitfall: data paths in params.py hardcoded to `/home/nathanlevy/sda/Data/` — must update

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
