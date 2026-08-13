---
layout: default
permalink: /paper-atlas/scmultibench-1476a178/
title: "scMultiBench"
nav: false
description: "scMultiBench 的价值是把方法选择改写为一个有条件的问题：输入结构决定可用方法，任务决定该看哪些指标，数据和指标共同决定相对排名；任何脱离这些条件的“全局最佳方法”都超出了论文证据。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>scMultiBench</h1>
    <p>Multitask benchmarking of single-cell multimodal omics integration methods</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02856-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scMultiBench">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/PYangLab/scMultiBench" target="_blank" rel="noopener noreferrer" aria-label="Open code for scMultiBench">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scMultiBench：怎样读懂一个多模态单细胞整合基准

### 先说清楚：它不是一种新的整合算法

scMultiBench 是一个 **Registered Report 形式的多任务基准**。它把 40 种已有方法放进同一张实验地图：四类输入结构、七类下游任务、64 个真实数据集和 22 个模拟数据集。它要回答的不是“哪个模型永远最好”，而是：面对某种模态组合、批次结构和下游目标，哪些方法有资格参赛，哪些指标最相关，哪些方法在相同条件下相对更稳妥。

论文的 Stage 1 protocol 于 2024 年 7 月 30 日原则接受。预注册降低了看到结果后再改变主要问题和分析方案的空间，但不能自动消除软件版本、包装脚本、超参数、缺失指标或数据预处理带来的偏差。

### 第一步：先按输入结构分类

同样叫“多模态整合”，实际问题可能完全不同。

| 类别 | 观测结构 | 核心困难 |
|---|---|---|
| Vertical | 同一批细胞测到多个模态 | 融合互补信息，同时保留细胞差异 |
| Diagonal | 不同细胞或批次各自只有一种模态 | 没有逐细胞配对，需要跨模态对齐 |
| Mosaic | 配对块与单模态块混合，模态覆盖不完整 | 借助桥接数据连接未配对部分 |
| Cross | 多个批次都含多个模态 | 同时处理模态差异和批次效应 |

这一步不是标签游戏。方法是否需要配对细胞、共享特征、桥接批次或所有模态共同出现，会直接决定它能否运行。论文统计了 18 种 vertical、14 种 diagonal、12 种 mosaic 和 15 种 cross 方法；同一种方法可属于多个类别，因此这些数字不能相加成方法总数。

### 第二步：把“整合好不好”拆成七个任务

scMultiBench 分别评估降维、批次校正、聚类、分类、特征选择、缺失模态插补和空间配准。这样的拆分很重要：一个嵌入可以把批次混得很好，却也可能抹去真实细胞类型；插补矩阵与真值的数值相关性较高，也不保证下游分类最好。

- 降维与聚类关注细胞类型结构是否被保留，使用 cLISI、ARI、NMI、ASW、孤立标签等互补指标。
- 批次校正关注批次混合，同时必须与生物保持指标一起阅读；代码还把 batch ARI/NMI 反向为“越高越好”。
- 分类既可使用统一的 MLP，也可比较方法自带分类器。统一 MLP 在代码中是 `输入维度 → 128 → 类别数`，默认 Adam、10 个 epoch；查询集中训练参考集未出现的类别会被过滤，所以其分数不是开放集识别能力。
- 特征选择同时考察跨重复的稳定性、与已知标记的联系以及下游用途。选得多不等于选得准。
- 插补同时看结构误差、差异特征/高变特征一致性和下游分类，避免只用一个重构误差作结论。
- 空间配准使用标签转移与空间一致性指标，并另测运行时间和内存；它与普通联合嵌入不是同一个评价问题。

### 从数据到图表的实际流水线

本地代码不是一个可一键训练 40 种方法的统一框架，而是一组方法适配器、任务评测脚本和作图脚本：

1. 经过清洗和重注释的数据以 HDF5 等格式进入 `tools_scripts/<method>/`。
2. 各方法包装脚本按自身要求做预处理并输出联合嵌入、预测或插补矩阵。
3. `evaluation_pipelines/` 对输出运行聚类、分类、scIB 指标、特征选择、插补或空间指标。
4. `figure_script/bubbleplot/` 汇总指标和相对排名，生成论文中的气泡图与总排名图。

统一的是输入输出接口和下游评价入口，不是所有方法的内部预处理。例如 Portal 包装器分别选择 Seurat-v3 高变基因、取交集、总量归一化、`log1p`、缩放后做 30 维 PCA；GLUE 包装器则对 RNA 取 2,000 个高变基因和 100 维 PCA，对 ATAC 做 100 维 LSI，并建立基因—峰引导图。这些差异通常是方法运行需求的一部分，但也意味着“完全相同预处理下的纯模型比较”并不成立。

聚类也有一个需要显式说明的边界：`evaluation_pipelines/clustering/SINFONIA.py` 用真实标签的类别数作为目标簇数，搜索 Leiden resolution。因此聚类指标衡量的是“已知簇数条件下的可分性”，不是完全无监督地同时发现簇数与簇结构。

### 排名分数究竟表示什么

不同指标量纲和方向不同，论文先把方向统一为高值较好，再在可比较的方法集合内排名。对某个数据集，可将方法在各指标上的名次记为 $r_{m,j}$，则总体思想是

$$
z_m = \operatorname{minmax}\!\left(\frac{1}{J_m}\sum_{j\in A_m} r_{m,j}\right),
$$

其中 $A_m$ 是该方法实际适用的指标集合。跨数据集时，先对每个指标汇总各数据集内的名次并缩放，再对这些“grand metric ranks”取平均、再次 min–max 缩放，得到总排名分数。论文图注说明，单个指标气泡展示的是 min–max 缩放后的原始值，而 overall/grand overall 展示的是名次聚合；二者不能混读为同一种绝对准确率。

这个设计减弱了极端原始值和量纲差异的影响，但代价是：分数是参赛方法集合中的**相对位置**。加入或删除方法、数据集或指标都可能改变分数；0.9 也不表示“90% 正确”。图中缺失值尤其重要：只输出邻接图的方法不能计算要求坐标嵌入的指标，某些任务或数据结构也不适用某些指标。缺失不是零分，但不同方法可能在不同指标集合中被汇总，因此跨行比较时必须先检查适用性。

### 论文结果应怎样使用

论文最稳定的结论不是某个冠军名单，而是明显的条件依赖：排名随数据集、模态组合、任务和指标变化；模拟数据表现也不能稳定替代真实数据表现。降维/聚类与批次校正之间常有生物保持—批次混合权衡；mosaic 方法受到桥接结构和共享特征影响；插补的矩阵保真度与下游用途可能脱钩；空间配准则需要独立的几何与可扩展性判断。

因此，Fig. 6 一类推荐图应当读作“在论文测试范围内的候选方法导航”。更稳妥的使用方式是：先按输入结构排除不适用方法，再按真正的下游任务查看相关指标，比较前三名或稳定候选，而不是机械选择一个总榜第一；最后在自己的数据上用生物保持、批次混合、运行成本和失败率做小规模验证。

### 代码证据支持到哪里

本地快照来自 `PYangLab/scMultiBench` 提交 `29c781fcd7f307cffc77774e35a01caa926d83d7`。直接代码可确认：方法包装器、HDF5 数据流、SINFONIA/Leiden 聚类、统一 MLP、scIB 薄包装、插补与空间评测脚本，以及作图/排名代码。它不能单独证明 40 个上游方法内部实现完全等同于论文作者版本，因为仓库主要保存调用包装器而非所有依赖源码，且没有一个中央锁文件固定全部 Python/R 环境。

还有三项关键复现边界：论文描述的 AdaSampling + Annotatability 重注释流程未在该仓库找到；SymSim2 模拟主要引用外部教程而非提供完整生成流水线；若干已处理大数据和结果依赖 Figshare/Zenodo/Shiny 等外部资产。因而本地仓库足以审计“怎样调用和怎样评分”的主要路径，却不足以仅凭当前文件从原始数据完整重建全部论文结果。

### 一句话结论

scMultiBench 的价值是把方法选择改写为一个有条件的问题：**输入结构决定可用方法，任务决定该看哪些指标，数据和指标共同决定相对排名；任何脱离这些条件的“全局最佳方法”都超出了论文证据。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scMultiBench — Summary

### Method / Paper Type
**Benchmark paper (Registered Report)** — not a new computational method. scMultiBench provides a systematic categorization and comprehensive benchmarking of existing single-cell multimodal omics integration methods.

---

### Motivation and Novelty

#### Biological Problem

Single-cell multimodal omics technologies (CITE-seq, SHARE-seq, 10x multiome, DOGMA-seq, TEA-seq) simultaneously profile multiple molecular layers — gene expression (RNA), surface protein abundance (ADT), and chromatin accessibility (ATAC) — in individual cells. These technologies have enabled unprecedented resolution in studying cell identity, cell-fate decisions, and disease mechanisms. However, the simultaneous explosion of computational integration methods has created a critical gap: researchers have no principled basis for choosing which method to use for a given dataset, modality combination, or analytical goal.

#### Limitations of Existing Approaches

Prior benchmark studies were limited in scope:
- **Cantini et al., *Nature Communications* (2021)** benchmarked joint multi-omics dimensionality reduction methods but focused on cancer and bulk/single-cell multi-omics.
- **Leng et al., *Genome Biology* (2022)** focused on deep learning multi-omics fusion methods for cancer.
- **Luecken et al., *Nature Methods* (2022)** benchmarked atlas-level single-cell data integration but focused on single-modality scRNA-seq.

None of these covered the full breadth of: (1) distinct multimodal data configurations, (2) diverse downstream tasks beyond dimension reduction, and (3) the broad range of currently available methods.

#### Unique Contributions

1. **Four-category taxonomy** for single-cell multimodal omics integration: vertical, diagonal, mosaic, and cross — a principled classification based on cell matching and batch structure.
2. **Seven-task evaluation** covering the full analytical workflow: dimension reduction, batch correction, clustering, cell type classification, feature selection, imputation, and spatial registration.
3. **Largest benchmarking scope**: 40 methods, 64 real datasets from 21 sources, 22 simulated datasets, 9 modality/technology combinations.
4. **Decision-tree guidelines** (Fig. 6) providing scenario-specific method recommendations based on data structure, task, and computational efficiency.
5. **Registered Report design** — protocol peer-reviewed and accepted before data collection, eliminating publication bias.
6. **Interactive Shiny app** for community exploration of results: http://shiny.maths.usyd.edu.au/scMultiBench/

---

### Method Overview

#### Algorithmic Framework

scMultiBench is an evaluation framework, not a new integration method. Its computational contributions are:

1. **Standardized I/O protocol**: All methods receive preprocessed HDF5 files; all methods output HDF5 embedding files.
2. **Unified evaluation pipeline** across 7 tasks, with appropriate metrics per task.
3. **Robust ranking strategy**: Two-level rank-then-normalize aggregation (per-dataset → across datasets), resistant to metric scale differences.
4. **Fair comparison infrastructure**: 5-fold cross-validation for supervised methods, standardized Leiden clustering with automatic resolution tuning, consistent MLP classifier for cross-method classification comparison.

#### Key Technical Components

**Data reannotation**: Uses AdaSampling (*IEEE Trans. Cyber.*, 2019) and Annotatability (*Nature Computational Science*, 2024) to correct or remove mislabeled cells — a critical step to reduce annotation bias from original publications.

**Simulation**: Extended SymSim (*Nature Communications*, 2019) to simulate paired RNA+ATAC and RNA+ADT data, generating 22 synthetic datasets that provide known ground-truth cell type labels.

**Clustering**: SINFONIA package with automatic Leiden resolution tuning to match true cell type count. Verified robust across k-means, Leiden, and Louvain (rank correlations > 0.9, Supp Fig. 9).

**MLP classifier**: 2-layer network (input → 128 → C cell types), Adam optimizer, 10 epochs. Simple and fast; enables fair cross-method comparison of integration quality independently of classification model choice.

#### Biological Assumptions

- Cell type labels from original publications are used as ground truth after reannotation.
- Batch effects are operationalized as sample-of-origin labels.
- Integration quality is proxied by how well cell type structure is preserved (cell-type-aware metrics) vs. how well batch effects are removed (batch-aware metrics).

---

### Evaluation

#### Datasets

**64 real datasets** from 21 sources:
- CITE-seq: PBMC (multiple donors/batches), BMMC, lung tissue
- 10x multiome: BMMC, mouse embryo, PBMC, human neocortex
- SHARE-seq: mouse skin
- SNARE-seq: mouse brain
- DOGMA-seq / ASAP-seq / TEA-seq: human PBMC (tri-modal)
- Spatial: Visium (human DLPFC, mouse tumor), Xenium (breast cancer), Stereo-seq (drosophila), MERFISH (mouse brain), Spatial ATAC-RNA (mouse embryo)

**22 simulated datasets**: 3/5-cell-type systems with 2-5K cells per dataset; all modality combinations covered

Dataset scale: 1,541 to 167,780 cells; up to 344,592 ATAC peaks per dataset

#### Metrics per Task

| Task | Metrics |
|------|---------|
| Dimension reduction | cLISI, CT, MU |
| Batch correction | kBET, iLISI, ARI_batch, NMI_batch, ASW_batch, GC, PCR |
| Clustering | ARI_cellType, NMI_cellType, ASW_cellType, iF1, iASW |
| Classification | OCA, ACA, Spec, Sens, F1 |
| Feature selection | MO, MC + clustering/classification on top-K features |
| Imputation | sMSE, pFCS, pDES + clustering/classification on imputed data |
| Spatial registration | LTARI, PAA, SCS, CT_SR, MU_SR |

#### Key Results

**Vertical integration (RNA+ADT)**:
- Best overall: Seurat WNN (*Cell* 2021), Multigrate (*Nature Biotechnology* 2023), Matilda (*Nucleic Acids Research* 2023), UnitedNet (*Nature Communications* 2023)
- Feature selection: MOFA+ (*Genome Biology* 2020) for reproducibility; Matilda and scMoMaT (*Nature Communications* 2023) for cell-type-specific markers

**Vertical integration (RNA+ATAC)**:
- Best overall: scBridge (*Nature Communications* 2023) (single batch); scJoint (*Nature Biotechnology* 2022) (multi-batch)

**Diagonal integration**:
- Single batch: scBridge (*Nature Communications* 2023) (DR/clustering), GLUE (*Nature Biotechnology* 2022) (batch correction)
- Multi-batch: scJoint (*Nature Biotechnology* 2022) (DR/clustering), GLUE (batch correction)

**Mosaic integration**:
- StabMap (*Nature Biotechnology* 2023) best for DR/clustering/classification across most modality combinations
- MultiVI (*Nature Methods* 2023) and Cobolt (*Genome Biology* 2021) best for (RNA, RNA+ATAC, ATAC) data specifically
- scMoMaT (*Nature Communications* 2023) and Multigrate (*Nature Biotechnology* 2023) best for batch correction

**Imputation**:
- totalVI (*Nature Methods* 2021) and StabMap best for ADT imputation (clustering + structural similarity)
- MultiVI best for ATAC/RNA imputation from multiome data
- Structural similarity does NOT predict downstream performance

**Cross integration**:
- RNA+ADT: totalVI best overall
- RNA+ATAC, ADT+ATAC, RNA+ADT+ATAC: Multigrate best overall
- Trade-off confirmed: scMDC (*Nature Communications* 2022) strong in DR/clustering/classification but weak in batch correction; scMoMaT strong in batch correction but weaker in other tasks

**Spatial registration**:
- PASTE center alignment (*Nature Methods* 2022) and PASTE2 (*Genome Research* 2023) best overall
- SPIRAL (*Genome Biology* 2023) competitive under LTARI/PAA but low SCS; scales to largest datasets
- Linear methods (PASTE family) better suited for adjacent serial sections; SPIRAL/GPSA (*Nature Methods* 2023) offer nonlinear alignment but lower spatial coherence

**Cross-cutting findings**:
1. **Task-dependence**: No method dominates across all tasks. Researchers must identify their primary goal before selecting a method.
2. **Metric-dependence**: Rankings differ substantially between DR/clustering metrics and batch correction metrics — reflecting a genuine biological trade-off, not a measurement artifact.
3. **Deep learning advantage**: 26/40 methods use deep learning; these consistently rank at the top in diagonal and cross integration.
4. **Simulation caveat**: Methods performing well on simulated data often underperform on real data. Simulated datasets lack the latent structure complexity of biological systems.
5. **Classifier independence**: For most methods, the simple MLP classifier and method-specific classifiers produce similar rankings, confirming that integration quality is the bottleneck.
6. **Robustness**: Most methods are stable to random seeds; data perturbation (removing ~20% of cell types) produces more variability than seed changes.

---

### Reproducibility

**Rating: 3 / 5**

**Justification**: The evaluation pipeline code is complete and well-organized (GitHub, archived on Zenodo 10.5281/zenodo.15385334). The Shiny app makes results interactively explorable. However, full reproduction requires:

1. **Processed datasets from figshare** (10.6084/m9.figshare.29035586.v1) — original datasets are publicly available but the cleaned/reannotated versions are the actual inputs
2. **The AdaSampling + Annotatability reannotation step is not in the repo** — requires separate installation and execution
3. **SymSim2 simulation code not in repo** — references external scDART tutorial
4. **Computational scale**: 40 methods × 86 datasets × 7 tasks requires significant GPU/CPU time. Hardware-specific results (RTX3090, AMD Ryzen) may not reproduce exactly on different hardware.
5. **Method versions are pinned**: All 40 methods have specific version numbers documented in Supp Notes, enabling consistent reproduction.

**Environment setup**:
- Python methods: scvi-tools, scib, anndata, scanpy, sinfonia, PyTorch
- R methods: Seurat (v5.0.2), rliger (v2.0.1), StabMap (v0.1.8), MOFA2 (v1.6.0), Conos (v1.5.2)
- Multiple conda environments required (different Python versions per method)

**Data availability**: All 64 real datasets from public repositories (GEO, ArrayExpress, Zenodo); processed inputs on figshare; results accessible via interactive Shiny app.

**Practical notes**:
- Start from the figshare-distributed processed datasets to skip the reannotation step
- Run each method independently (they are standalone wrappers) then aggregate metrics
- For large spatial datasets (D62: 167K cells), the 10-fold partitioning strategy is required to avoid OOM
- For methods requiring fragment files (Signac-based ATAC processing), the P0_BrainCortex sample uses `CreateGeneActivityMatrix` (Seurat) as a fallback when fragment files are unavailable

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
