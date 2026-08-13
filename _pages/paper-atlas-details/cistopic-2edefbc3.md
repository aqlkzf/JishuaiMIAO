---
layout: default
permalink: /paper-atlas/cistopic-2edefbc3/
title: "cisTopic"
nav: false
wide: true
description: "单细胞 ATAC-seq 的矩阵极稀疏：行是候选调控区域，列是细胞，一个“0”既可能代表该区域在该细胞中关闭，也可能只是测序深度不足而没有读到。传统流程往往先降维/聚类细胞再找差异区域，或者先按已知 motif/cistrome 聚合区域再聚类细胞。前者把细胞状态与调控区域发现割裂，后者依赖预定义注释，难以发现新的 enhancer 组合。"
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
      <span>Nature Methods · 2019</span>
    </div>
    <h1>cisTopic</h1>
    <p>cisTopic: cis-regulatory topic modeling on single-cell ATAC-seq data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-019-0367-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for cisTopic">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/aertslab/cistopic" target="_blank" rel="noopener noreferrer" aria-label="Open code for cisTopic">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cisTopic：用主题模型同时理解细胞状态与顺式调控模块

### 核心问题

单细胞 ATAC-seq 的矩阵极稀疏：行是候选调控区域，列是细胞，一个“0”既可能代表该区域在该细胞中关闭，也可能只是测序深度不足而没有读到。传统流程往往先降维/聚类细胞再找差异区域，或者先按已知 motif/cistrome 聚合区域再聚类细胞。前者把细胞状态与调控区域发现割裂，后者依赖预定义注释，难以发现新的 enhancer 组合。

cisTopic 的关键想法是把 scATAC-seq 借用为文本主题模型：

| 文本模型 | cisTopic |
|---|---|
| 文档 | 细胞 |
| 词 | 可及调控区域 |
| 主题 | 协同开放的顺式调控程序 |
| 一个词在文档中出现 | 一个区域在细胞中可及 |

Latent Dirichlet Allocation（LDA）同时学习两个方向：每个细胞由哪些 topic 组成，以及每个 topic 由哪些区域组成。因此同一个模型既提供细胞表示，也提供可拿去做 motif/TF 分析的调控区域集合。

### 第一步：构造二值可及性矩阵

输入可以是单细胞 BAM 与候选区域 BED，也可以是已有的 region×cell 矩阵。单端数据若 read 的 5' 端落入区域就计数；双端数据任一端落入就计数。默认至少一个 fragment 即记为 1：

$$
X_{rc}=\mathbf 1(\operatorname{count}_{rc}\ge 1).
$$

R 代码在对象初始化时用 `1 * (count.matrix >= is.acc)` 生成稀疏二值矩阵，`is.acc=1` 为默认阈值。这里故意舍弃了 fragment 数量：模型关注某区域是否在细胞中出现，减少测序深度对频数的直接支配，但不会自动消除所有深度效应。

候选区域集合非常重要。论文先在聚合/批量 profile 上 call peaks，并在进入 cisTopic 前排除 blacklist。若 peak 集合包含伪影、漏掉细胞类型特异 enhancer，主题模型无法在后面补救。blacklist 过滤是外部预处理，不是 R 包内部自动执行。

对单细胞甲基化，论文也允许用每个 region/cell 的 beta value，默认 beta > 0.5 记为甲基化；这说明 LDA 框架不限于 ATAC，但本文最主要的验证来自 scATAC/scTHS 数据。

### LDA 生成过程：细胞和区域如何被 topic 连接

设 topic 数为 $T$、区域数为 $R$。对每个细胞 $c$：

$$
\theta^{(c)}\sim\operatorname{Dirichlet}(\alpha),
$$

其中 $\theta_t^{(c)}$ 表示 topic $t$ 对细胞 $c$ 的贡献。对每个 topic $t$：

$$
\phi^{(t)}\sim\operatorname{Dirichlet}(\beta),
$$

其中 $\phi_r^{(t)}$ 表示区域 $r$ 属于 topic $t$ 的概率。对细胞中每一个观察到的可及区域 token，先从 $\theta^{(c)}$ 采一个 topic，再从该 topic 的 $\phi^{(t)}$ 生成区域。

cisTopic 默认使用对称先验 $\alpha=50/T$、$\beta=0.1$。$\alpha$ 控制一个细胞的 topic 混合，$\beta$ 控制一个 topic 的区域分布。它们是正则化假设，不是从数据自动推断的生物学常数。

### 折叠 Gibbs 采样到底在更新什么

“折叠”表示把 $\theta$ 和 $\phi$ 积分掉，只迭代每个 region-in-cell token 的 topic 归属。去掉当前 token 后，把区域 $r$ 在细胞 $c$ 中分到 topic $t$ 的概率写为

$$
P(z_i=t\mid z_{-i},r,c)\propto
\frac{n_{-i,t}^{(r)}+\beta}{n_{-i,t}+R\beta}
\times
\frac{n_{-i,t}^{(c)}+\alpha}{n_{-i}^{(c)}+T\alpha}.
$$

第一项问“区域 $r$ 过去多常被 topic $t$ 使用”；第二项问“细胞 $c$ 过去多依赖 topic $t$”。两项相乘，使区域聚类和细胞表示在同一个迭代过程中相互约束。

本地 `runCGSModels()` 并没有自己重写采样内核。它把 R 稀疏矩阵逐列转换成 `lda` 包要求的 document list：每个细胞是一个 2×N 矩阵，第一行是从 0 开始的 region index，第二行是全 1 token count（`cistopic/R/RunModels.R:108-120`）。随后把 `alpha/t` 和 `beta` 传给 `lda.collapsed.gibbs.sampler()`（`:136-167,192-197`）。所以论文公式与本地包装层直接对应，但真正逐 token 的 C 采样代码属于外部 `lda` 依赖，不在这个仓库内。

并行计算是按不同 topic 数的候选模型分配，而不是把一个 Gibbs 链随意拆开；`clusterSetRNGStream` 为并行任务建立可复现随机流（`:127-144`）。

### 如何选择 topic 数

$T$ 必须由用户提供候选集合。R 函数默认尝试 `c(2,10,20,30,40,50)`，每个候选运行独立模型。论文分析主要根据采样后最后记录迭代的 log-likelihood 选择最大者，并检查 burn-in 后 log-likelihood 是否稳定。

代码 `selectModel()` 从每个模型提取最后的 log-likelihood（`RunModels.R:269-275`），`type="maximum"` 时选最大值（`:295-300`）。当前函数默认参数是 `type="derivative"`，更适合后加入的 WarpLDA 曲线；源码甚至会在 CGS 模型上提示改用 maximum（`:239-267`）。因此不能把当前默认 derivative 误写成 2019 论文的模型选择规则。

同样，`runCGSModels()` 当前默认 `iterations=500,burnin=250`，论文不同数据集曾显式使用 500+500 或 250+500 等配置。是否收敛应看每条链的 log-likelihood 轨迹，而不是相信默认迭代数对所有规模都足够。

### 两个核心输出矩阵

采样计数加先验并归一化后得到：

$$
\hat\theta_t^{(c)}=
\frac{n_t^{(c)}+\alpha}{n^{(c)}+T\alpha},
\qquad
\hat\phi_r^{(t)}=
\frac{n_t^{(r)}+\beta}{n_t+R\beta}.
$$

本地模型对象保存的是未归一化计数：`document_expects` 对应 topic×cell，`topics` 对应 topic×region。不同下游函数会按 Probability、Z-score 或 NormTop 等方式转换，不能把原始 count slot 直接称为已经归一化的概率。

#### topic–cell：用于细胞状态

每个细胞的 topic contribution 是低维表示，可用于 t-SNE/UMAP、聚类、轨迹与批次诊断。一个细胞可以同时有多个 topic，这使连续分化过程不必先切成互斥 cluster。论文在 2,755 个 FACS 分选造血细胞中选择 17 个 topic，topic contribution 重建已知分化路径，并揭示 topic 3 这类跨细胞共享的 promoter-rich 一般 topic。

#### region–topic：用于调控程序

每个 topic 的高分区域形成候选 cistrome，可做 motif enrichment、ChIP-seq overlap、GREAT 和跨物种比较。这里的“同 topic”是统计共现，不是证明区域之间物理接触或由同一个 TF 直接调控。论文再用 motif、独立 ChIP-seq、RNA regulon 和跨物种证据验证这些解释。

### 区域打分与二值 topic

为了从连续 region-topic 分布提取高置信区域，包提供 NormTop 等分数，再按 topic 拟合 gamma 分布并用尾部概率阈值二值化。`getRegionsScores()` 对分数做 topic 内缩放；`binarizecisTopics()` 默认 `thrP=0.99` 并用 `fitdist(...,"gamma",method="mme")` 估计阈值（`cistopic/R/BasicTopicOperations.R:16-51,73-151`）。

这一步把“区域属于 topic 的相对强度”转成 region set，方便 RcisTarget。0.99 是软件默认，不代表论文所有数据集都用同一阈值；论文不同分析使用 0.975–0.99 等选择。motif enrichment 的结论同时依赖区域 universe、cisTarget 数据库版本和阈值。

### dropout 的概率预测

LDA 可以给即使 $X_{rc}=0$ 的位置一个预测可及概率：

$$
P(r\mid c)=\sum_{t=1}^{T}\hat\phi_r^{(t)}\hat\theta_t^{(c)}.
$$

本质是 region-topic 与 topic-cell 概率矩阵相乘。本地 `predictiveDistribution()` 对两侧加 $\beta$/$\alpha$ 平滑后相乘。补充图 15 把低覆盖二值矩阵、预测概率矩阵与高覆盖模拟真值并排展示，说明 topic 共享结构能找回部分 dropout。

但这个输出是模型概率，不是观测 read。它可能把同一 topic 常见区域补给当前细胞，也可能平滑掉真实稀有差异；不能把预测矩阵当作新的独立测量来做无校准的显著性检验。

### 主图与补充证据怎样支持方法

#### 图 1：方法与造血分化

图 1a 从 binary matrix 经 LDA 同时输出 cell clustering 与 enhancer clustering，是论文的核心因果链。模拟 benchmark 显示低至约 3,000 reads/cell 时 cisTopic 的 ARI 更稳健；真实 2,755 个 FACS 造血细胞中，它恢复细胞类型与连续分化。topic 10 的细胞、区域和 motif 三层视图把 pDC 状态连接到 PU.1/IRF 调控信号。

#### 图 2：脑组织异质性与跨物种调控

人脑 34,520 个细胞和小鼠脑 3,034 个细胞的 topic-cell 空间识别主要神经/胶质群，并细分 ExL23、ExL4、ExL56 等皮层层次。区域 topic 的 motif、bulk signature、RNA 证据和 human-to-mouse lift-over 支持调控解释。胶质 topic 的跨物种保守更强，而神经亚型差异更大；这说明 topic 相似性需要在物种和区域映射背景下解释。

#### 图 3：SOX10 knockdown 动态

598 个 melanoma 细胞跨 0–72 h knockdown 的 topic contribution 描绘状态变化。topic 14、11、12 的区域在 knockdown 后失去可及性，富集 SOX motif，并与独立 SOX10 ChIP-seq peak 高度重叠。图中 cell-topic、region-topic、motif 和 ChIP 四层证据共同支持“SOX10 调控程序”，而不仅是 topic 标签命名。

#### 补充材料的作用

本地 `paper_supp1.pdf` 包含 Supplementary Figures 1–15 和 notes：采样收敛、不同 read depth/数据类型 benchmark、Mouse Cell Atlas 扩展、造血和脑 topic 验证、SOX10 cofactor 以及 dropout 预测。`paper_supp2.pdf` 是 Nature Research reporting summary，记录数据来源、软件版本和 R 3.4.3/Bioconductor 3.6 环境。补充材料是本地 PDF，未转换为 Markdown；本次通过 PDF 文本直接核对，图像级细节仍以原 PDF 为边界。

### 本地代码覆盖与版本边界

它包含 S4 对象、BAM/矩阵/甲基化输入、CGS 包装、模型选择、预测分布、region score/binarization、降维和 RcisTarget/AUCell/GREAT 接口。

**直接覆盖**：二值矩阵、LDA 文档格式转换、$\alpha=50/T$、$\beta=0.1$、CGS 调用、log-likelihood 模型选择、topic/cell 与 topic/region 矩阵、预测概率、gamma 二值化及下游可视化。

**外部依赖**：真正 collapsed Gibbs 更新在 `lda` 1.4.2；motif enrichment 依赖 RcisTarget 数据库；AUCell、rGREAT、Rtsne 等计算来自各自包。论文全套原始数据预处理和所有 benchmark 脚本并未作为一个可一键执行的现代环境封装。

**论文之后的代码**：`runWarpLDAModels()` 使用 `text2vec` 的 WarpLDA，是后续为大数据扩展的后端，不是论文 Methods 描述的 CGS 实验。pycisTopic 是现代 Python successor，也不等于这份 R commit。解释论文结果时应以 CGS 路径为主。

### 最容易误解的几点

1. topic 不是细胞类型。一个 topic 可以是广泛 promoter 程序、连续状态、技术批次或特定调控模块，需要外部证据命名。
2. region-topic 共现不是 enhancer-enhancer 物理互作，也不是 TF→region 的直接因果证明。
3. 二值化降低 fragment count 的影响，却丢弃强度信息；极低深度细胞仍可能受检测率影响。
4. 最大 log-likelihood 只是在候选 $T$ 和当前采样设置中选择，不保证生物学上唯一正确的 topic 数。
5. $P(r\mid c)$ 是平滑预测，不是补测的数据；下游差异分析要防止把模型相关性当作新增观测。
6. 旧 R 包依赖 2018 年前后的 R/Bioconductor 与数据库版本，当前环境重跑需要锁定历史依赖或迁移到新实现后重新验证数值。

cisTopic 最重要的贡献，是让“哪些细胞共享状态”和“哪些区域共享调控程序”成为同一个概率模型的两个投影。它从稀疏二值可及性中得到可解释的双向表示，但可靠解释仍依赖收敛检查、topic 数敏感性、测序深度诊断，以及 motif、ChIP、转录组或扰动数据的独立验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## cisTopic — Summary

**Paper**: "cisTopic: cis-regulatory topic modeling on single-cell ATAC-seq data"
**Authors**: Carmen Bravo González-Blas, Liesbeth Minnoye, et al. (Aerts lab, KU Leuven)
**Journal**: Nature Methods, 2019
**DOI**: 10.1038/s41592-019-0367-1
**Code**: https://github.com/aertslab/cistopic (R, deprecated; pycisTopic is successor)

---

### Motivation & Novelty

#### Biological Problem

Single-cell ATAC-seq (scATAC-seq) profiles chromatin accessibility in individual cells, providing a direct readout of active enhancers and regulatory programs without the ambiguity of RNA-based surrogates. However, the data is far sparser than scRNA-seq: a typical cell has reads at only 1–5% of candidate regulatory regions, compared to ~10–30% of genes in scRNA-seq. This extreme sparsity makes both cell clustering and enhancer categorization difficult.

#### Limitations of Prior Methods

| Method | Approach | Limitation |
|---|---|---|
| LSI (Cusanovich et al., *Science* 2015) | TF-IDF + SVD on accessibility matrix | Poorly handles very low coverage; PC1 correlates with read depth |
| chromVAR (Schep et al., *Nat Methods* 2017) | TF motif enrichment per cell | Requires pre-defined motif cistromes; loses enhancer-level resolution |
| scABC (Zamanighomi et al., *Nat Commun* 2018) | Landmark-based clustering | Underpowers at low coverage; number of landmarks ≠ true cell types |
| BROCKMAN (de Boer & Regev, *BMC Bioinformatics* 2018) | k-mer decomposition | No region-level output; computationally expensive |
| SCRAT (Ji et al., *Bioinformatics* 2017) | Cistrome enrichment (ENCODE DNase) | Depends on pre-defined cistromes; cannot discover novel regulatory programs |
| Cicero (Pliner et al., *Mol Cell* 2018) | Co-accessibility graph | Designed for ordering, not unsupervised clustering |

The fundamental limitation is that these methods either cluster cells first then find regions, or aggregate regions first then cluster cells. Neither **co-optimizes** both simultaneously.

#### cisTopic's Unique Contributions

1. **Joint optimization**: Simultaneously infers cell states (via topic-cell distributions) and cis-regulatory modules (via region-topic distributions) from a single model.
2. **Probabilistic framework**: Bayesian LDA with collapsed Gibbs sampling provides principled uncertainty quantification and handles sparsity naturally via Dirichlet priors.
3. **Dropout imputation**: The predictive distribution $P(r|c)$ recovers accessibility at regions with zero reads but non-zero probability based on topic composition.
4. **Scalability**: Parallelized across topic-count models; WarpLDA engine (post-paper) handles 80k+ cells.
5. **Downstream integration**: Built-in interface to RcisTarget (motif enrichment), AUCell (signature enrichment), rGREAT (pathway analysis), and dimensionality reduction tools.

---

### Method Overview

cisTopic applies **Latent Dirichlet Allocation (LDA)** — a Bayesian topic model originally developed for text corpora — to single-cell epigenomics data. The analogy is:

| Text Mining | cisTopic |
|---|---|
| Document | Cell |
| Word | Regulatory region |
| Topic | Cis-regulatory topic (co-accessible enhancer program) |
| Word frequency | Chromatin accessibility (binary) |

**Key components**:
1. **Binary accessibility matrix** (R×C): 1 if region accessible in cell, 0 otherwise
2. **Collapsed Gibbs Sampler**: iteratively assigns each accessible region-in-cell to a topic; integrates out topic and region distributions analytically
3. **Hyperparameters**: α = 50/T (topic sparsity in cells), β = 0.1 (region sparsity in topics)
4. **Model selection**: test T ∈ {5–50} topics; select by highest log-likelihood
5. **Output**: θ (topic-cell, T×C) and φ (region-topic, T×R) distribution matrices

See `doc_method.md` for mathematical derivation and `doc_code.md` for code-paper mapping.

**The cisTopic R package** (`cistopic/`) implements 4 core steps:
1. `createcisTopicObjectFromBAM()` → binary accessibility matrix
2. `runCGSModels()` → LDA models (parallel over topic counts)
3. `selectModel()` → best model by log-likelihood
4. Downstream: `getRegionsScores()` → `binarizecisTopics()` → `topicsRcisTarget()` / `runtSNE()`

---

### Evaluation

#### Datasets

| Dataset | Cells | Regions | Organism | Source |
|---|---|---|---|---|
| Simulated hematopoietic (from bulk) | 650 | MACS2 peaks | Human (hg19) | GSE74912 |
| FACS-sorted hematopoietic scATAC-seq | 2,755 | 488,825 | Human (hg19) | GSE96772 |
| Human brain scTHS-seq | 34,520 | 287,381 | Human (hg38) | GSE97942 |
| Mouse brain scATAC-seq | 3,034 | 139,504 | Mouse (mm10) | GSE100033 |
| sciATAC-seq Mouse Cell Atlas | 80,254 | 436,206 | Mouse | Cusanovich 2018 |
| SOX10 KD melanoma scATAC-seq | 598 | 78,262 | Human (hg19) | GSE114557 |
| snmC-seq human neurons | 2,784 | 28,342 bins | Human | Luo 2017 |

#### Metrics

**Primary metric**: Adjusted Rand Index (ARI) comparing inferred cell clusters to FACS-sorted ground truth labels.

**Compared methods**: LSI (*Science* 2015), chromVAR (*Nat Methods* 2017), scABC (*Nat Commun* 2018), BROCKMAN (*BMC Bioinformatics* 2018), SCRAT (Ji et al., *Bioinformatics* 2017), Cicero (*Mol Cell* 2018).

#### Key Results

1. **Simulated hematopoietic data**: At 50k reads/cell (high coverage), all methods perform similarly. At 3k reads/cell (low coverage), cisTopic (ARI ≈ 0.8) substantially outperforms LSI (ARI ≈ 0.5), chromVAR, scABC, and BROCKMAN. cisTopic is most robust to depth variation.

2. **FACS-sorted hematopoietic (2,755 cells)**: cisTopic correctly recovers 8 cell types. ARI comparison (descending): cisTopic > chromVAR > Cicero > SCRAT > LSI > BROCKMAN > scABC.

3. **Human brain (34,520 cells)**: Identifies major cell types (excitatory, inhibitory neurons, glia) + subpopulations of excitatory neurons linked to cortical layers (ExL23, ExL4, ExL56) and interneurons from distinct ganglionic eminences.

4. **Mouse brain (3,034 cells)**: Identifies 4 excitatory neuron subpopulations + previously unannotated interneurons. Validated by FACS bulk epigenomic signatures and cross-species conservation with human topics.

5. **SOX10 KD (598 cells, 4 timepoints)**: Identifies 3 topics (14, 11, 12) enriched for SOX10 motif that lose accessibility during knockdown. Overlap with SOX10 ChIP-seq: P < 2.2×10⁻¹⁶.

6. **Regulatory validation**: Topics enriched for expected TF motifs (GATA1/2 in megakaryocyte-erythroid progenitors, EBF1 in CLPs, PU.1+IRF in pDCs) confirm biological coherence of learned topics.

7. **Cross-species conservation**: Glial cell type topics (oligodendrocytes, astrocytes, microglia) are strongly conserved between human and mouse; neuronal subtypes show more divergence.

---

### Reproducibility

**Rating: 3/5**

#### Justification
- **Code available**: R package at GitHub (`aertslab/cistopic`), v0.3.0. However, the package is now deprecated in favor of pycisTopic (Python).
- **Data available**: Most datasets are from public GEO accessions. Novel melanoma scATAC-seq data deposited at GSE114557.
- **Environment**: R 3.4.3, Bioconductor 3.6. Full dependency list in DESCRIPTION/data analysis section. The `lda` R package (v1.4.2) is a critical but old dependency.
- **Key practical issue**: cisTarget feather databases (motif enrichment) are large (2–10GB) and require separate download from https://resources.aertslab.org/cistarget/

#### Environment Setup
```r
# Install from GitHub (R < 4.0 recommended for compatibility)
devtools::install_github("aertslab/cisTopic")

# Bioconductor dependencies
BiocManager::install(c("AUCell", "RcisTarget", "GenomicRanges", "ChIPseeker"))

# Optional
install.packages(c("Rtsne", "umap", "destiny", "fitdistrplus", "text2vec"))

# Download cisTarget databases (hg19, mm9):
# https://resources.aertslab.org/cistarget/
```

#### Common Pitfalls
1. **R version**: cisTopic was developed for R 3.4.x. On R ≥ 4.0, some dependencies may need updating.
2. **`lda` package**: The CGS implementation requires `lda` R package (Chang 2015) — not the general "lda" text mining package but specifically `CRAN lda`.
3. **Burn-in verification**: Always plot `logLikelihoodByIter()` to confirm LL has stabilized before the burn-in cutoff. Default `burnin=250` may be too short for large datasets.
4. **Memory**: For 80k+ cell datasets, use `keepBinaryMatrix=FALSE` and `returnType='selectedModel'` to avoid holding all models in RAM simultaneously.
5. **blacklisting required**: Must be done externally before creating the cisTopic object; the package does not perform blacklisting.
6. **Deprecated**: For new projects, use [pycisTopic](https://pycistopic.readthedocs.io/) instead.

#### Strengths
- Conceptually elegant — clean LDA formulation with rigorous probabilistic foundation
- Produces biologically interpretable outputs at both cell and region levels
- Effective at low coverage where other methods fail
- Scalable (WarpLDA engine for large datasets)

#### Weaknesses
- R package deprecated; Python successor required for modern use
- Number of topics T must be specified as a range; computational cost grows with range
- No built-in scRNA-seq integration (multi-modal analysis requires external tools)
- cisTarget database dependencies are large and species-limited (hg19, mm9 primarily)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
