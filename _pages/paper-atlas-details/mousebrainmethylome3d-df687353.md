---
layout: default
permalink: /paper-atlas/mousebrainmethylome3d-df687353/
title: "MouseBrainMethylome3D"
nav: false
description: "这项工作用 snmC-seq3 测 301,626 个单核甲基化组，用 snm3C-seq 同时测 176,003 个核的 DNA 甲基化与三维染色质接触，覆盖成年小鼠全脑 117 个解剖区域。作者先用 mCH/mCG 建立 4,673 个细胞—空间群组，再与 RNA、ATAC 和 MERFISH 图谱对齐；随后在细胞类型 pseudo-bulk 层面比较 compartment、TAD、远程接触、调控网络和转录异构体。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature · 2023</span>
    </div>
    <h1>MouseBrainMethylome3D</h1>
    <p>Single-cell DNA methylome and 3D multi-omic atlas of the adult mouse brain</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-023-06805-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MouseBrainMethylome3D：怎样把单细胞甲基化、三维染色质和脑空间统一起来

### 一句话理解

这项工作用 snmC-seq3 测 301,626 个单核甲基化组，用 snm3C-seq 同时测 176,003 个核的 DNA 甲基化与三维染色质接触，覆盖成年小鼠全脑 117 个解剖区域。作者先用 mCH/mCG 建立 4,673 个细胞—空间群组，再与 RNA、ATAC 和 MERFISH 图谱对齐；随后在细胞类型 pseudo-bulk 层面比较 compartment、TAD、远程接触、调控网络和转录异构体。

它的核心不是一种新聚类器，而是一套分层尺度：单细胞甲基化定义细胞身份，跨模态整合赋予共同命名和空间，聚合后的 3D genome 再解释细胞类型特异的基因调控。

### 1. 为什么脑图谱需要 mCG、mCH 和 3C 三种信号

mCG 常在活跃调控元件形成低甲基化区域；神经元还积累大量 mCH，基因体 mCH 通常与表达负相关。mCH 是成熟神经元较稳定的身份标记，比瞬时 RNA 状态更适合构建成年脑细胞分类。

但是 enhancer 可以隔着很远调控基因。只知道 DMR 与基因在线性基因组上靠近，不足以确认潜在靶点。snm3C-seq 在同一个核中同时记录甲基化与染色质接触，让作者可以问：某个细胞类型中，DMR 是否与基因形成接触，以及这种接触是否随基因体甲基化和 RNA 共同变化。

单核 3C 极度稀疏，所以论文并不是在每个单细胞中稳定调用 TAD 和 loop；它先为单细胞补全/嵌入，再把同类细胞聚合为 pseudo-bulk，主要结构分析发生在 subclass 或 cell-group 层面。

### 2. 数据规模和采样设计

成年雄性 C57BL/6 小鼠的 18 张 600 µm 冠状切片被分成 117 个区域。每个区域有 2—3 个重复，每个重复通常汇集至少 6 只动物。FANS 富集 NeuN+ 核，因此数据以神经元为主：snmC 中约 92%，snm3C 中约 78%。

这提升了稀有神经元类型的覆盖，却意味着全脑细胞比例不是无偏抽样。4,673 个最终 group 还包含解剖区域拆分信息，所以它不等于 4,673 个完全独立的分子 cell type；更高层的 274 subclasses 才是跨模态统一比较的主要单位。

### 3. 从 FASTQ 到可聚类甲基化张量

映射流程把 bisulfite reads 对齐到 mm10，生成逐细胞 ALLC 文件。QC 控制转换率、全局 mCH/mCG 和覆盖度。之后 ALLCools 把数据存成 MCDS：

```text
cell × genomic feature × methylation context
```

聚类使用 100 kb bins 的 mCH 和 mCG posterior fraction。粗 bin 牺牲局部调控分辨率，却能在每个核只覆盖约 6.5% cytosines 的情况下获得较稳健的细胞间距离。DMR 和基因组解释则在细胞聚合后使用更细尺度。

真正执行 MCDS、posterior smoothing、CEF/DMR 和 ConsensusClustering 的主要引擎是外部 `ALLCools==1.0.8`。`wmb2023` 保存了 notebook 和配置，但不是所有算法源代码都在当前工作区，因此部分环节是“调用可见，内部实现需外部包”。

### 4. 四轮迭代共识聚类

作者不采用一次高 resolution Leiden 然后人工合并，而是反过来：先保守地欠分割，再对仍不均一的群逐轮细分。

每轮大致执行：

1. mCH/mCG 变异特征选择；
2. 降维和邻接图；
3. Leiden 用不同随机种子重复 200 次；
4. 共识结果训练分类器，检查 cluster 可预测性；
5. 达不到目标 accuracy 或仍异质的群进入下一轮。

`clustering/config/07.yaml` 直接显示第一轮 `leiden_resolution: 0.25`、`leiden_repeats: 200`、`target_accuracy: 0.95`、`min_cluster_size: 50`。后续轮次目标 accuracy 通常为 0.9，resolution 在 0.2—0.5 调整。

这种策略的直觉是：真正稳定的细胞群应当在抽样和随机初始化变化下仍可被分类器区分。它降低一次随机 Leiden 过分割的影响，但结果仍依赖 100 kb 特征、resolution、accuracy 阈值和最小群大小。

最终先得到 2,573 个分子 clusters，再按 dissection region 对足够大的群拆分成 4,673 个 cluster-by-spatial groups。因此空间信息是在最终细粒度分类中显式参与的。

### 5. 跨模态整合：为什么要把 mCH 反向

高基因体 mCH 通常对应低 RNA 表达。若直接把 mCH 与 RNA 做 CCA，同一 cell type 的信号方向相反。整合前把 mCH 符号反转，使“更活跃”在两种模态中指向一致。

RNA 图谱有 430 万细胞，不能对全部细胞直接拟合完整 CCA。作者用约 10 万参考细胞学习 loading，再把 query 投影到参考空间。这降低内存并允许迭代到 subclass/cluster 层级。最终所有 mC groups 对应到 4,669 个 RNA clusters，覆盖约 97.4% RNA cells，并获得 274 个共同 subclasses。

mC—ATAC 整合则把 hypomethylation 与 accessibility 对齐；MERFISH 整合把 mC 核映射到 6 张空间切片。对每个 mC 核，空间坐标来自相邻 MERFISH cells 的位置推断，因此是概率性空间赋值，不是对该核直接成像。

图 1/2 的统一标签是跨模态近邻和 overlap score 的产物，不表示不同实验中的单个细胞一一配对。

### 6. 为什么要对单细胞 3C 做补全

一个 snm3C 核平均只有有限长程 contacts，原始 contact matrix 大部分为零。scHiCluster 的核心补全依次做三步。

#### 6.1 Gaussian convolution

相邻 genomic bins 的接触信号通常相关，先对 contact matrix 做局部 Gaussian 平滑。代码默认 `pad=1`、`std=1`。主对角线在卷积前清零，避免 self-contact 压倒近邻结构。

#### 6.2 Random walk with restart

先把矩阵列归一化为转移矩阵 $P$，再迭代：

$$
Q_{t+1}=P\left[(1-r)Q_t+rI\right].
$$

代码默认 $r=0.5$、容差 0.01、最多 30 轮。restart 项保留局部来源，避免信号无限扩散。代码在 RWR 前再次清零对角线。

大染色体不一次构造完整稠密矩阵，而用重叠滑窗处理再拼接。窗口降低内存，但边界处依赖 mask 和 overlap 规则。

#### 6.3 SQRTVC normalization

RWR 后把矩阵对称化，并按节点度归一化：

$$
E'=D^{-1/2}(E+E^T)D^{-1/2}.
$$

这减少测序覆盖和 bin 度数差异。补全值是计算推断的接触倾向，不是新增实验 reads；低覆盖区域可能被邻域结构过度平滑。

### 7. 三个基因组尺度分别回答什么

#### Compartment：100 kb

作者对 distance-normalized contacts 求相关矩阵和 PCA，用 CpG density 决定 PC 方向，得到 A/B compartment score。再跨 274 subclasses 比较 compartment 与 mCG/RNA 的关系。它描述大尺度活跃/不活跃染色质环境。

#### TAD boundary：25 kb

TopDom 调用边界。作者把单细胞边界聚合为 subclass boundary probability，用卡方检验寻找跨 subclasses 变化的 bins（FDR<0.001），并与长基因的 mCH/mCG 比较。边界概率是群体中边界出现频率，不是每个细胞都有同一条 TAD 边界。

#### Highly variable interactions：10 kb

对每条相互作用计算 subclasses 间 ANOVA F statistic，筛选 $F>3$、FDR<0.001 的 HVI。若 interaction anchor 与基因体重叠，再计算 contact strength 与 gene-body mCH 的 Pearson correlation。

由粗到细的三尺度不能互换：compartment 变化不等于 enhancer loop，10 kb HVI 也不必是经过实验验证的 enhancer—promoter contact。

### 8. 为什么所有相关前要 quantile normalization

不同脑区神经元的全局 mCH 差异很大。若直接做 PCC，一个 subclass 的整体高 mCH 可能让许多无关基因都看似相关。论文在 compartment、boundary、HVI 和 GRN 的跨 subclass 相关前，用 `qnorm` 沿 subclasses 归一化，尽量聚焦相对模式。

相关显著性通常通过在 sample 内打乱后建立 null distribution 并控制 FDR。这个设计比直接套正态检验稳健，但无法消除 cell composition、聚合细胞数和测序深度的全部影响。

### 9. DMR—TF—target 网络怎样构造

论文方法把三类 pairwise edges 相交：

- DMR→target：DMR 位于与基因相关的 HVI anchor，且 DMR mCG 与 target mCH 相关；
- TF→target：TF gene-body mCH 与 target gene-body mCH 相关；
- TF→DMR：TF mCH 与 DMR mCG 相关，且该 DMR 含该 TF 的富集 motif。

四个相关量的绝对值用几何平均形成 triple score：

$$
S_{all}=\sqrt[4]{|S_aS_bS_cS_d|}.
$$

接着 Taiji 的 personalized PageRank 用 inverted mCH 作为活性 node weight，用 inverted DMR mCG 加权 edge，得到 subclass-specific TF importance。

这是证据交叉筛选网络：3D contact 限制潜在 target，methylation 提供状态共变，motif 提供序列可能性。它仍不证明 TF 直接结合或调控方向，尤其 gene-body mCH 是表达代理而非 TF activity 的直接测量。

更重要的是，完整 GRN/SCENIC+/Taiji 构建代码不在 `wmb2023` 或 `scHiCluster` 中。论文给出详细方法和公式，但本地代码只能标为 `Not found`，不能声称已端到端核验图 5。

### 10. 异构体预测在问什么

作者从 SMART-seq 量化 transcript TPM 和 exon PSI，为每个基因收集两类特征：

- mC：exon、上下游 300 bp、基因内 DMR；
- 3C：基因内 HVI。

先用 `SelectKBest(f_regression)` 选最多 100 个特征，再以 RandomForestRegressor 做五折交叉验证。真实模型 PCC 与 sample 内打乱特征的 shuffled PCC 相比，用于判断基因内表观结构是否提供额外预测信息。

3C 特征总体比 mC 更能预测部分长神经元基因的 isoform/exon usage。这里仍是预测关联，不代表 contact 导致剪接；转录活性、基因长度或 cell-type identity 可能同时影响二者。

对应 random forest notebooks 不在本地仓库，因此图 6 方法可由论文核验，代码实现为 `Not found`。

### 11. 论文与代码对应关系

#### Exact

- `wmb2023` 的 01—08 聚类工作流与 YAML 参数；
- 四轮欠分割式 ConsensusClustering 框架；
- mC—ATAC、mC—RNA、mC—MERFISH notebook 路由；
- scHiCluster 的 Gaussian、RWR、滑窗与 SQRTVC；
- compartment、domain、loop/diff 的软件模块。

#### Partial

- ALLCools 承担 MCDS、posterior mC、DMR、CEF、CCA 等核心内部实现，但不在两个 clone 中；
- cloud Zarr/CoolDS 输入规模巨大且依赖外部存储；
- mC 到 MERFISH 的空间坐标是集成推断；
- pseudo-bulk CoolDS 的完整生成/运行环境没有作为单一可复现入口。

#### Not found

- 图 5 的完整 GRN、cisTarget/SCENIC+ 与 Taiji PageRank pipeline；
- 图 6 的 RandomForest isoform prediction notebooks；
- 从原始 FASTQ 到全部正文图的一键工作流。

因此，聚类与 scHiCluster 核心数值实现可直接审计；最具机制解释性的 GRN 和 isoform 分支反而是主要复现缺口。

### 12. 阅读边界

1. 4,673 groups 含空间拆分，不等于 4,673 个独立 cell types。
2. MERFISH 坐标来自跨模态近邻，不是对 methylome 核直接定位。
3. 单细胞 3C 补全会平滑稀疏矩阵，pseudo-bulk 结构不是逐细胞确定事实。
4. 跨 subclass PCC 和 GRN triple 是关联证据，不是扰动因果。
5. isoform RandomForest 预测不能证明 3D contact 控制剪接。
6. NeuN 富集和成年雄鼠设计限制对非神经元、性别和发育阶段的外推。

在这些边界内，这项工作最可靠的贡献是建立了全脑、细胞类型统一命名的甲基化—三维基因组资源，并展示了不同基因组尺度如何与细胞身份和空间组织共同变化。

### 源证据入口

- 图谱规模与分类：`paper source/PMC10719113/paper.md:14-68`
- DMR、空间与 3D 结果：`paper source/PMC10719113/paper.md:70-118`
- GRN 与 isoform：`paper source/PMC10719113/paper.md:120-162`
- 聚类与整合方法：`paper source/PMC10719113/paper.md:178-302`
- 3D、GRN、isoform 方法：`paper source/PMC10719113/paper.md:302-362`
- 共识聚类参数：`wmb2023/clustering/config/07.yaml`
- scHiCluster 补全：`scHiCluster/schicluster/impute/impute_chromosome.py:19-170`
- 跨模态 notebooks：`wmb2023/integration/` 与 `wmb2023/merfish/`
- 主图：`paper source/PMC10719113/images/`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## MouseBrainMethylome3D — Summary

### Motivation & Novelty

#### Biological Problem

The mammalian brain's molecular diversity arises from the interplay of gene expression, DNA methylation, and 3D chromatin organization across millions of cells. While single-cell transcriptomics has catalogued cell types comprehensively (e.g., Zhang et al. 2023 *Nature*, ref. 6), the epigenomic dimension remains less well-characterized at brain-wide scale. DNA methylation — particularly non-CpG methylation (mCH) in neurons — is a stable cell-identity mark that is established post-mitotically and maintained throughout lifespan, making it ideal for characterizing mature cell types independent of short-term transcriptional states. Understanding how DNA methylation patterns at gene bodies and regulatory elements relate to 3D chromatin organization and gene expression is fundamental to decoding the gene regulatory logic of the brain.

#### Limitations of Existing Approaches

Prior to this work:
- **snmC-seq2** (Luo et al. 2018, *Nat. Commun.*) and **Liu et al. 2021** (*Nature*) profiled methylomes in subregions of the mouse brain but lacked whole-brain coverage.
- **snm3C-seq** (Lee et al. 2019, *Nat. Methods*) jointly profiled methylome and 3D genome but had not been applied at brain-wide scale.
- **BICCN transcriptomic atlas** (Zhang et al. 2023, *Nature*) provided RNA-based taxonomy for millions of cells but had no epigenomic counterpart.
- **snATAC-seq atlas** (Li et al. 2021, *Nature*, ref. 11) provided chromatin accessibility but not methylation or 3D genome.
- No study had integrated all five molecular modalities (mCH, mCG, chromatin conformation, accessibility, expression) in a brain-wide, single-cell framework.

#### Unique Contributions

1. **Scale**: 477,629 nuclei (301,626 methylomes + 176,003 joint m3C profiles) from 117 dissected regions — the largest single-cell epigenome dataset of the brain.
2. **Dual-technology**: snmC-seq3 for high-throughput methylomes + snm3C-seq for joint methylome+3D genome, enabling simultaneous profiling of two epigenomic dimensions.
3. **Multi-omic integration**: Five modalities (mCH, mCG, Hi-C, ATAC, RNA) integrated into a single cell-type taxonomy of 4,673 groups and 274 subclasses.
4. **GRN construction**: Brain-wide gene regulatory network connecting TFs, DMRs, and target genes via epigenetic evidence.
5. **Isoform prediction**: First demonstration that intragenic methylation and 3D contacts predict alternative isoform expression across brain cell types.
6. **Spatial mapping**: MERFISH integration assigns each nucleus a spatial coordinate within the CCF atlas.
7. **Public resource**: Interactive browser at mousebrain.salk.edu; data at NeMO Archive and GEO.

---

### Method Overview

#### Framework

The study applies a two-stage analysis framework:

**Stage 1 (Cellular)**: Single-cell methylome profiles are stored as MCDS tensors (cell × genomic bin × mCH/mCG) and processed through 4 rounds of iterative ConsensusClustering. Leiden clustering is run 200 times per round with different random seeds; results are merged based on classification accuracy. This produces 4,673 cell groups (and 274 cross-modality annotated subclasses after integration with scRNA-seq data from the BICCN).

**Stage 2 (Genomic)**: Cells are aggregated into pseudo-bulk profiles (BaseDS at base resolution; CoolDS at 100kb/25kb/10kb). Analyses operate on these tensors: DMR calling, compartment/TAD/interaction analysis with scHiCluster, GRN construction, and isoform prediction.

#### Key Technical Components

- **snmC-seq3**: Improved library preparation enabling higher throughput than snmC-seq2
- **Iterative CCA integration** with downsampling (100k reference cells) for memory-efficient alignment of methylome with RNA/ATAC/MERFISH data
- **scHiCluster**: Two-step contact imputation (Gaussian convolution + RWR + SQRTVC) to recover signal from sparse single-cell Hi-C matrices
- **GRN**: Three-edge-type network (DMR–target, TF–target, TF–DMR with motif enrichment) scored by geometric mean of four PCC values; Taiji PageRank for TF importance
- **Random forest isoform prediction**: Intragenic mC and 3C features predict alternative splicing at cell-group resolution

#### Biological Assumptions

- mCH is inversely correlated with gene expression in neurons (high mCH = silenced)
- mCG hypomethylation at DMRs marks active regulatory elements
- Cell type identity is stable in post-mitotic neurons and reflected in both modalities
- 3D contacts captured by snm3C-seq are representative of the regulatory landscape despite sparse coverage

---

### Evaluation

#### Datasets

| Dataset | Cells/Profiles | Purpose |
|---|---|---|
| snmC-seq3 (this study) | 301,626 methylomes | Primary clustering |
| snm3C-seq (this study) | 176,003 joint profiles | 3D genome + methylome |
| BICCN scRNA-seq (Zhang et al. 2023) | 4.3M cells, 5,200 clusters | Cross-modality integration + annotation |
| BICCN snATAC-seq (Li et al. 2021) | 2.3M cells | mC–ATAC integration |
| CEMBA MERFISH (this study) | 266,903 cells, 500 genes, 6 slices | Spatial validation |
| AIBS whole-brain MERFISH (companion) | 3.9M cells, 51 slices | Spatial atlas |
| BICCN SMART-seq (Zhang et al. 2023) | 195,680 cells, full-length | Isoform quantification |

#### Comparative Results

**Cell-type taxonomy**: All 4,673 mC cell groups matched to 4,669 (90%) transcriptomic clusters covering 97.4% (4.19M) of all RNA cells. Integration overlap scores were high within subclasses.

**mC–ATAC alignment**: Dissection region alignment score 0.89 ± 0.11 — indicating strong concordance in cellular diversity across both epigenomic modalities.

**Spatial mapping**: Imputed spatial coordinates closely matched dissection region boundaries, with fine-scale laminar structure recovered (e.g., cortical L2/3, L5, L6 layers resolved).

**3D genome**: 83,518 bins with significantly variable TAD boundaries (FDR < 0.001). Compartment scores negatively correlated with mCG in neuronal long genes implicated in neurodevelopment. Long genes (>100 kb) enriched for gene-body domain boundaries at TSS and TTS.

**GRN**: 1.04 × 10^7 TF–DMR–target triples (830 TFs, 20,101 genes, 291,752 DMRs). Example validation: EGR1–Nab2 triple with known biological feedback loop; FOXP2 motifs enriched in negatively correlated DMRs consistent with its known repressor function.

**Isoform prediction**: chromatin conformation features (3C) outperformed mC features for predicting alternatively spliced genes (e.g., Nrxn1, Nrxn2, Nrxn3, Ntrk2, Oxr1).

---

### Reproducibility

**Rating: 2.5 / 5**

**Justification**: The raw data (snmC-seq3/snm3C-seq FASTQs, processed Zarr tensors) are publicly available through NeMO Archive and GEO (GSE213262). The core analysis notebooks (wmb2023 repository) provide step-by-step clustering and integration workflows. However, substantial barriers exist:

**Strengths**:
- Raw data fully available (NeMO + GEO)
- Analysis notebooks (wmb2023) cover clustering, integration, MERFISH steps
- scHiCluster package (v1.3.2) is installable from GitHub
- ALLCools (v1.0.8) is a published PyPI package
- Interactive browser provides data visualization without local computation

**Weaknesses**:
- GRN construction code (Fig 5) is NOT in wmb2023 or scHiCluster repos — requires ALLCools GRN module + SCENIC+ + Taiji framework, none of which are included
- Isoform prediction notebooks (Fig 6) are also absent from wmb2023
- Pseudo-bulk Zarr tensors are hosted on Google Cloud and are large (hundreds of GB to TB scale) — local reproduction requires significant storage and download bandwidth
- Cloud infrastructure (SkyPilot, GCP) required for full-scale analysis; local reproduction of the full pipeline would require weeks of compute time
- snmC-seq3 protocol is in Supplementary Methods (PDF) but not as a citable open protocol

**Practical notes**:
- Environment setup: `pip install allcools==1.0.8 schicluster` should install the two core packages
- For clustering reproduction: download wmb2023 repo + set up ALLCools + access Zarr data from Google Cloud or download processed MCDS tensors
- For 3D genome: scHiCluster can process raw contacts; imputed matrices are also on Google Cloud
- Common pitfall: ALLCools generates intermediate files (ALLC, BaseDS) that require bgzip/tabix — ensure samtools + tabix are in PATH
- The PNCC QC step is non-standard and requires plate metadata — important for removing doublets/debris
- PMC package download for this paper requires extended timeout (>300s) due to the large package size (~125 MB); the standard 300s timeout in `pmc_jats2md.py` may need to be increased
- The GRN construction and isoform prediction sections of the paper are the most computationally intensive; their code is not publicly available in the repos — expect to need to contact the authors or wait for ALLCools documentation updates

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
