---
layout: default
permalink: /paper-atlas/gwspade-e5df30fc/
title: "gwSPADE"
nav: false
wide: true
description: "gwSPADE 把一个空间 spot 看作多种潜在细胞类型的混合，把基因看作主题模型中的“词”。它与普通 LDA 的关键区别不是增加空间邻接关系，也不是引入单细胞参考，而是先计算基因权重，再让这些权重改变 Gibbs 采样时的计数：广泛、高频但区分度低的基因影响减弱，集中于少数潜在类型的基因影响增强。"
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
      <span>Deconvolution</span>
      <span>Nucleic Acids Research · 2025</span>
    </div>
    <h1>gwSPADE</h1>
    <p>gwSPADE: gene frequency-weighted reference-free deconvolution in spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1093/nar/gkaf966" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for gwSPADE">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/Cui-STT-Lab/gwSPADE" target="_blank" rel="noopener noreferrer" aria-label="Open code for gwSPADE">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## gwSPADE：给基因“重新分配发言权”的无参考空间解卷积

### 一句话理解

gwSPADE 把一个空间 spot 看作多种潜在细胞类型的混合，把基因看作主题模型中的“词”。它与普通 LDA 的关键区别不是增加空间邻接关系，也不是引入单细胞参考，而是先计算基因权重，再让这些权重改变 Gibbs 采样时的计数：广泛、高频但区分度低的基因影响减弱，集中于少数潜在类型的基因影响增强。

### 1. 它解决什么问题

10x Visium 等平台的一个 spot 往往覆盖多个细胞。参考型方法用 scRNA-seq 类型谱拆分 spot，但参考缺失、平台批次差异或未知亚型都会限制结果。STdeconvolve 用 LDA 做无参考分解，却把所有 UMI 对主题分配的作用看成相同；高频基因可能同时占据多个主题的 top gene，使潜在类型难以解释。

gwSPADE 只要求非负、最好为原始整数的 spot × gene 计数矩阵。它输出：

- $\theta\in\mathbb{R}^{D\times K}$：每个 spot 中 $K$ 个潜在类型的比例；
- $\beta\in\mathbb{R}^{K\times V}$：每个潜在类型对 $V$ 个基因的相对频率。

这里的“cell type”首先是统计主题。它必须通过已知空间结构、标志基因、组织学或独立真值去匹配生物学类型；无参考不等于自动得到有名称的真实细胞类型。

### 2. 从普通 LDA 到加权 LDA

对 spot $d$ 的第 $n$ 个 UMI，$z_{dn}$ 表示它被分配到哪个潜在类型，$w_{dn}=g$ 表示该 UMI 来自基因 $g$。普通 LDA 的折叠 Gibbs 条件概率可写成

$$
p(z_{dn}=k\mid -)\propto
(N_{dk}^{-dn}+\alpha_k)
\frac{N_{kg}^{-dn}+\eta}{N_k^{-dn}+V\eta}.
$$

$N_{dk}$ 是 spot $d$ 分给类型 $k$ 的 UMI 数，$N_{kg}$ 是类型 $k$ 中基因 $g$ 的 UMI 数。论文默认 $\alpha_k=1/K$，$\eta=0.01$。

gwSPADE 为每个 spot–gene 组合准备权重 $m_{dg}$。当一个 UMI 被移出旧主题或加入新主题时，相关统计量不再加减 1，而是加减 $m_{dg}$。于是采样概率由加权计数 $M$ 驱动：

$$
p(z_{dn}=k\mid -)\propto
(M_{dk}^{-dn}+\alpha_k)
\frac{M_{kg}^{-dn}+\eta}{M_k^{-dn}+V\eta}.
$$

若所有 $m_{dg}=1$，模型退化为普通 LDA。论文展开式 Eq. 6 的 topic–gene 分子把对 spot 的求和上限误写成了 $D$ 上的基因索引；C++ 实现按 topic、gene 跨 spot 累积，实际路径是正确的。

### 3. 七种权重与为什么 BDC 最重要

代码 `R/WLDA.R::Weight_Term()` 实现七种选项：信息量（论文称 entropy）、inverse frequency、PMI、TF-IDF、BDC，以及 information×BDC、IF×BDC 两个组合。除 PMI/TF-IDF 外，单个基因在所有 spot 使用相同权重；随后都做 min–max 归一化。

#### BDC 的两阶段逻辑

BDC 不能只从全局基因频率直接得到。代码先用 `topicmodels::LDA` 的 VEM 拟合普通 LDA，得到初始 topic–gene 分布。对基因 $g$，把它在 $K$ 个主题中的值归一化为 $q_{kg}$，再计算

$$
\operatorname{BDC}_g=1+\frac{\sum_{k=1}^{K}q_{kg}\log q_{kg}}{\log K}.
$$

若一个基因均匀散布于全部主题，熵高，BDC 接近 0；若集中在少数主题，BDC 接近 1。随后再运行一次加权 Gibbs LDA。论文和代码只做“普通 LDA → BDC → 加权 LDA”这一轮，没有反复迭代更新权重。

代码中的 `tf_idf` 与论文 Eq. 10 不完全一致：其 `tf` 实际复用了 PMI 风格的负对数比值，再乘 IDF，而不是标准的 spot 内 term frequency。因此 TF-IDF 结果应按代码实现理解。推荐方案是 BDC，论文也显示 PMI 和 TF-IDF 通常较弱。

### 4. 一个小例子

假设两个潜在类型中，核糖体基因在二者初始概率都是 0.5，则 $q=(0.5,0.5)$，BDC 为 0；某标志基因的 $q=(0.95,0.05)$，BDC 约为 0.71。两个基因即使都有很多 UMI，后者在主题重新分配时产生更强的加权计数变化。模型不是简单删除高表达基因，而是优先保留“跨主题分布集中”的信号。

### 5. 代码实际怎样运行

入口 `WLDA(corpus, k, type="bdc")` 的调用链是：

1. `Weight_Term()` 生成与计数矩阵同形状的 `Weight_Mat`；BDC 若没有预拟合模型，就调用 `topicmodels::LDA()`。
2. `weightedLDA()` 把矩阵转换为文档/词元结构并随机初始化主题标签。
3. `keyATM_fit_LDA()` 进入 C++；`LDAweight::iteration_single()` 每轮打乱 spot 和 UMI 顺序，然后调用 `LDAbase::sample_z()`。
4. 默认运行 1500 次迭代，生成 $\theta$、代码中名为 `phi` 的 topic–gene 分布、top genes 和 perplexity。

最值得注意的是双计数系统。`n_dk`、`n_kv`、`n_k` 是加权计数，用于决定新主题；`n_dk_noWeight` 是原始 UMI 计数，用于最终 $\theta$ 的后验均值。因此权重改变分配过程，却不会把最终 spot 比例直接解释成“加权 UMI 比例”。论文用 $\beta$ 表示 topic–gene 分布、$\eta$ 表示其先验；C++ 变量 `beta` 实际对应论文的 $\eta$，R 输出 `phi` 才对应论文的 $\beta$。

### 6. K 不是模型自动给出的唯一答案

README 对多个 $K$ 分别拟合模型。`PerplexityPlot()` 同时画 perplexity 和平均比例低于 5% 的“稀有主题”数量，作者在 perplexity 肘部与稀有主题开始增多之间选择 $K$，并结合组织知识。这个过程是启发式模型选择，不是统计上唯一确定的真实细胞类型数；而且 BDC 本身依赖 $K$，每个候选 $K$ 都需要重新预拟合和计算权重。

### 7. 论文证据怎样读

- Fig. 2 的模型模拟提供明确真值：BDC 在主题谱、spot 比例和 RMSE 上优于普通 LDA；图中的基因秩 SCC 从 0.88 提高到 0.99。
- Figs. 3–4 把单细胞 MERFISH 数据聚合为模拟 spot，再与已知类型比例比较。BDC 的总体优势稳定，但稀有类型仍难。
- Fig. 5 在 MOB、Visium 小鼠脑和 DBiT-seq 胚胎中以解剖层、*Cck*、*Hpca*、*Plp1* 等外部结构做解释性验证。真实数据没有完整 spot 级细胞比例真值，因此不能把空间吻合称为精确恢复。
- Fig. 6 的 PDAC-A 分析比较组织学区域与多种方法；gwSPADE-BDC 的癌症主题在癌区比例更高，并以 *TFF3*、*CRISP3*、*PNLIPRP1* 解释若干主题。
- Fig. 7 是另一份 NT-PDAC 数据的二次分解：先用参考型方法筛选 ductal 比例超过 60% 的 spot，再用 gwSPADE-BDC 无参考分成五个亚型并做 GO 富集。因此整个发现流程并非“从原始组织到亚型完全无参考”。CT1 至 CT5 的功能解释分别侧重肌原纤维/肌动蛋白、外泌体/黏附与迁移、胶原/基底膜和血管、离子转运、消化酶与 NO 信号；这些是富集和组织学关联提出的候选解释，未经独立功能实验验证。

### 8. 适用范围与边界

gwSPADE 的优点是输入简单、无需单细胞表达参考，并能输出可解释的主题基因谱。边界同样清楚：

- 模型完全不使用 spot 邻接或坐标，空间仅用于结果展示和后验验证；
- 结果依赖过度离散基因筛选、$K$、随机种子与参考前置 LDA；
- 稀有细胞类型和相似谱类型仍容易合并或混淆；
- 无参考主题没有天然标签，marker/组织学匹配仍引入外部知识；
- 固定对称 $\alpha=1/K$ 偏好稀疏混合，未必适合高度不均衡组织；
- topic 模型给出统计成分，不能证明每个主题等同于一种纯细胞类型。

### 9. 可复现性审计

工作区 `gwSPADE/` 与官方 `Cui-STT-Lab/gwSPADE` 提交 `f188aa8856f945c71f70e817694e5b5c300e0b46` 逐文件一致，核心 R/C++ 实现可直接核查。`gwSPADE_code/` 是重复副本，不应作为第二套独立实现。

公开代码仍不能复现论文全部图表：只提供 MOB、MPOA 和示例脚本；模型模拟生成、鼠肾、脑、胚胎、PDAC、竞争方法、RMSE 与 Diebold–Mariano 检验脚本不完整或缺失；分析脚本含硬编码路径；没有锁定依赖环境或正式测试。`Analysis/MPOA.R` 还把 spot 索引用于 `phi`，从矩阵语义看应是 `theta`。因此核心算法的 paper–code 匹配度高，但完整基准与生物学结论只能部分复现。

### 证据来源

本解读依据 `paper source/gkaf966/gkaf966.md`、本地 `paper.pdf` 与全部七幅主图的直接视觉复核，以及官方一致快照 `gwSPADE/R/`、`gwSPADE/src/`、`gwSPADE/Analysis/`。论文主张、图中观察、代码事实与作者的生物学推断均按各自证据层级表述。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## gwSPADE: Gene Frequency-Weighted Reference-Free Deconvolution in Spatial Transcriptomics

**Paper**: Xie A, Steele NG, Cui Y. *Nucleic Acids Research* 53(18), gkaf966 (2025).
**DOI**: [10.1093/nar/gkaf966](https://doi.org/10.1093/nar/gkaf966)
**Code**: [https://github.com/Cui-STT-Lab/gwSPADE](https://github.com/Cui-STT-Lab/gwSPADE)

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) technologies such as 10x Visium capture gene expression at multicellular resolution, where each spatial spot contains a mixture of 5–50 cells of potentially different types. Accurately decomposing these mixtures into cell type proportions ($\theta$) and transcriptional profiles ($\beta$) is critical for understanding tissue organization, cell-cell interactions, and disease progression. For example, in pancreatic cancer tissue, identifying which spots contain cancer cells vs. normal ductal epithelium directly impacts downstream analyses of tumor microenvironment composition.

#### Limitations of Existing Approaches

- **Reference-based methods** (RCTD, *Nature Biotechnology* 2022; Stereoscope, *Communications Biology* 2020; Cell2location, *Nature Biotechnology* 2022; SPOTlight, *Nucleic Acids Research* 2021; CARD, *Nature Biotechnology* 2022) rely on external single-cell RNA-seq references, which may not be available, may introduce batch effects, and cannot discover novel cell types or sub-cell-types.
- **STdeconvolve** (*Nature Communications* 2022), the leading reference-free method based on Latent Dirichlet Allocation (LDA), treats all genes equally. High-frequency housekeeping genes dominate multiple deconvolved cell types — for example, in PDAC data, gene *S100A6* appeared in the top 10 most frequent genes of 13 out of 20 deconvolved cell types under STdeconvolve, reducing discriminative power.
- **SpiceMix** (*Nature Genetics* 2023) uses NMF with spatial graph priors (HMRF) but lacks a built-in criterion for selecting the number of cell types, often fails in regions without spatial continuity, and produces overly sparse profiles when K is large.
- **CARDfree** (*Nature Biotechnology* 2022) is described as "reference-free" but still requires a **marker gene list** as input, limiting its unsupervised applicability. It can only identify as many cell types as specified in the marker list.
- **SMART** (*Genome Biology* 2024) is semi-reference-based, employing keyword-assisted LDA that relies on marker gene lists and directly assigns deconvolved cell types based on provided markers.

#### Unique Contributions

gwSPADE introduces **gene frequency weighting** into the LDA topic model for spatial transcriptomics deconvolution. The key insight is borrowed from information retrieval: down-weight ubiquitous/high-frequency genes while up-weighting rare, discriminative genes. Seven weighting schemes are evaluated, with **Balanced Distributional Concentration (BDC)** emerging as the best-performing approach. gwSPADE requires only a gene count matrix — no reference data, no marker gene lists — and produces both cell type proportions and transcriptional profiles per spot. Additionally, gwSPADE can perform **sub-cell-type deconvolution** on spots dominated by a single cell type, enabling discovery of functionally distinct subtypes without reference information.

**Interpretation boundary**: the inferred topics are unlabeled statistical components, not automatically verified cell types. Real-data labels require marker, anatomy, histology, or other external evidence. In the NT-PDAC subtype workflow, the >60% ductal spots were themselves selected using an earlier reference-based deconvolution, so the complete workflow is not reference-free from raw tissue to subtype.

---

### Method Overview

#### Algorithmic Framework

1. **Gene Selection**: Remove genes appearing in <1% of spots, then select ~1000 overdispersed genes using a GAM-based variance test (via STdeconvolve). The paper recommends ~1000 genes (~10% of total), finding that 500 genes increases variability while 2000 genes provides no additional accuracy.
2. **Weight Matrix Construction**: Compute per-gene (or per-gene-per-spot) weights using one of seven schemes. For BDC, an initial standard LDA model (Variational EM via `topicmodels` R package) is fitted to estimate $\beta$ (topic-word distribution), then BDC weights are computed from the entropy of each gene's distribution across topics. All weights are min-max normalized to $[0,1]$.
3. **Weighted Collapsed Gibbs Sampling**: Run a modified LDA where raw integer counts $N_{gdk}$ are replaced with weighted counts $M_{gdk} = m(w^g) \cdot N_{gdk}$ in the collapsed Gibbs conditional probability. The C++ backend (Rcpp/RcppEigen) iterates 1500 times (default), shuffling document and token order each iteration.
4. **Output Estimation**: After sampling, estimate $\theta$ (spot-by-cell-type proportions) from **unweighted** counts $N_{dk}$ and $\beta$ (cell-type-by-gene profiles) from posterior counts. The weights guide the sampler toward better assignments, but final estimates use standard Bayesian posterior means.
5. **K Selection**: Grid search over K values (e.g., K=2 to 20), selecting based on perplexity (lower = better) and the number of rare cell types (mean proportion <5%). Optimal K is at the "elbow" in the perplexity curve, supplemented by biological prior knowledge.

#### Key Technical Components

- **BDC weighting**: Adapts supervised term weighting from text classification; genes uniformly expressed across topics get weight $\approx 0$, genes specific to few topics get weight $\approx 1$. In PDAC, BDC reduced *S100A6*'s dominance from 13 to 5 deconvolved cell types.
- **Two-stage estimation**: Standard LDA (VEM) → BDC weights → Weighted LDA (Gibbs). A single round without iteration.
- **Dual count system**: C++ maintains weighted counts (for sampling) and unweighted counts (for posterior) in parallel.

#### Biological Assumptions

- Each spot is a mixture of $K$ discrete cell types (topics).
- Gene expression within a cell type follows a multinomial distribution.
- Overdispersed genes are informative for deconvolution.
- High-frequency genes are less discriminative for cell type identity (analogous to stop words in NLP).
- Spots are independent (no spatial information incorporated).

---

### Evaluation

#### Datasets

| Dataset | Platform | Resolution | Genes | Spots/Cells | K |
|---------|----------|-----------|-------|-------------|---|
| Model-based simulation | Synthetic (Dirichlet) | — | 100 | 1,000 spots | 4 |
| MPOA (mouse preoptic area) | MERFISH → 100µm² grids | Single-cell aggregated | 135 | 3,072 grids | 9 |
| Mouse Kidney (MK) | MERFISH → grids | Single-cell aggregated | 307 | 2,472 grids | 8 |
| Mouse Olfactory Bulb (MOB) | ST platform | Spot (~200µm) | ~1,000 OD | ~262 spots | 7 |
| Mouse Brain | 10x Visium | 55µm | ~1,000 OD | ~2,702 spots | 13 |
| Mouse Embryo E11 | DBiT-seq | 25µm | ~1,000 OD | ~1,000 spots | 13 |
| Human PDAC (PDAC-A) | ST (microarray) | Spot | 1,379 (CARDfree markers) | ~428 spots | 20 |
| NT-PDAC (sub-cell-type) | ST | Spot | — | Subset (>60% ductal) | 5 |

#### Metrics

- **PCC** (Pearson Correlation Coefficient) between deconvolved and ground truth transcriptional profiles (per matched cell type)
- **SCC** (Spearman Correlation Coefficient) for gene expression rankings within matched cell types
- **RMSE** of deconvolved cell type proportions per spot: $\text{RMSE} = \sqrt{\sum_{k=1}^{K} (\hat{\theta}_k - \theta_k)^2 / K}$
- **Diebold–Mariano test** for statistical significance of RMSE improvements between methods (one-sided)

#### Comparative Results

| Method | Type | Journal/Year |
|--------|------|-------------|
| STdeconvolve | Reference-free (LDA) | *Nature Communications*, 2022 |
| SpiceMix | Reference-free (NMF+HMRF) | *Nature Genetics*, 2023 |
| CARDfree | Marker-gene-based (NMF+CAR) | *Nature Biotechnology*, 2022 |
| SMART | Semi-reference (keyword-LDA) | *Genome Biology*, 2024 |

**Key Results**:
- **Model-based simulation**: gwSPADE-BDC improves gene profile SCC from 0.88 (STdeconvolve) to 0.99, and proportion RMSE from ~0.15 to ~0.05 (Diebold–Mariano $P < 2.2 \times 10^{-16}$).
- **MERFISH simulations**: Consistent improvements across MPOA (9 types) and MK (8 types); DM $P < 2.2 \times 10^{-16}$ for both.
- **Real ST data**: On MOB, mouse brain, and embryo, gwSPADE-BDC shows clearer spatial patterns matching known anatomical structures (layers, hippocampus, fiber tracts).
- **Human PDAC**: gwSPADE-BDC identifies cancer clone cells with significantly higher proportions in cancer-annotated regions ($t$-test $P = 2.2 \times 10^{-16}$). In contrast, SpiceMix assigned higher cancer proportions even to non-cancerous areas.
- **Sub-cell-type analysis**: Ductal cells in NT-PDAC (spots with >60% ductal proportion) deconvolved into 5 functionally distinct subtypes with GO enrichment: CT1 (myofibril, actin cytoskeleton — myofibroblast-like invasive phenotype), CT2 (extracellular exosome, focal adhesion — ECM remodeling and migration), CT3 (collagen trimer, basement membrane — fibroblast-like ECM/angiogenesis), CT4 (ion transmembrane transport — sodium homeostasis), and CT5 (serine-type endopeptidase, digestion — acinar-like protease secretion). CT1 enriched in tumor cells invading smooth muscle wall; CT2 in poorly differentiated regions; CT5 in well-differentiated histology.

#### Biological Validation

- **MOB**: Deconvolved cell types match the 5 known layers (GCL, MCL, OPL, GL, ONL); marker gene *Cck* correctly identified as top gene for GL (vs. *Beta-s* from STdeconvolve, which does not align with GL).
- **Mouse brain**: Hippocampal marker *Hpca* and oligodendrocyte marker *Plp1* correctly enriched in their respective deconvolved types.
- **Mouse embryo**: Cell type matching erythrocyte coagulation regions in H&E staining; K=13 matches the original authors' identified spatial features.
- **PDAC**: Ductal terminal marker *TFF3*, centroacinar marker *CRISP3*, and acinar marker *PNLIPRP1* identified from deconvolved cell type profiles. gwSPADE-BDC also reduced *S100A6* dominance from 13 cell types (STdeconvolve) to 5.

---

### Limitations

- **No spatial information**: gwSPADE treats spots as independent, unlike SpiceMix (HMRF, *Nature Genetics* 2023) or SONAR (*Nature Communications* 2023). Future extensions incorporating spatial priors may further improve performance.
- **Depends on gene selection**: Performance is sensitive to the number and choice of overdispersed genes. Too many genes cause poor topic separation; too few miss rare cell types.
- **Dataset size dependency**: Like standard LDA, performance degrades with very few spots or genes. The posterior contraction rate depends on the corpus size.
- **Single-round BDC**: BDC weights come from a standard LDA pre-fit. Iterating the LDA→BDC→weighted LDA cycle might further improve weights, but this is not explored.
- **Fixed α**: Unlike some LDA implementations, gwSPADE does not estimate the Dirichlet hyperparameter $\alpha$, which may limit adaptability to highly unbalanced cell type distributions.

---

### Reproducibility

#### Rating: 3.5/5

#### Strengths
- R package with full source code on GitHub; also archived on Zenodo.
- Core C++ Gibbs sampler (Rcpp/RcppEigen) is well-structured and efficient.
- Example data (MOB from STdeconvolve) included; MPOA simulation data (`.rds` files) provided.
- Dependencies are standard R packages (STdeconvolve, topicmodels, quanteda).

#### Blockers
- **Hardcoded paths** in `Analysis/` scripts (`setwd('~/Desktop/2022-2023/wLDA/')`) — not portable.
- **Missing analysis scripts**: Only MOB and MPOA scripts provided; Mouse Kidney, Mouse Brain, Mouse Embryo, PDAC, and NT-PDAC scripts absent.
- **Missing evaluation code**: RMSE computation and Diebold-Mariano test not implemented in the repository (likely done in separate analysis scripts not committed).
- **Missing simulation code**: Model-based simulation generation code not provided.
- **Missing benchmarking code**: Scripts for running SpiceMix, SMART, and CARDfree not included.
- **Bug in MPOA.R**: Line 109 uses `$phi[spots, ]` where `$theta[spots, ]` is intended.
- No unit tests, no `renv` lockfile — dependency versions not pinned.

#### Source audit (2026-07-19)

The local primary package `gwSPADE/` was compared file-for-file with official repository commit `f188aa8856f945c71f70e817694e5b5c300e0b46` and matched. `gwSPADE_code/` is a duplicate snapshot, not an independent implementation. All seven main figures were visually re-inspected from the local conversion/PDF.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
