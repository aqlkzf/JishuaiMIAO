---
layout: default
permalink: /paper-atlas/gnspade-5acc37a9/
title: "gnSPADE"
nav: false
description: "gnSPADE 把空间转录组的每个 spot 当成一篇“文档”、把 UMI count 展开成重复出现的“基因词元”，用 LDA topic 表示潜在细胞类型；它在 Gibbs 采样条件概率中再乘一个基因网络 MRF 项，鼓励同一 spot 内互为网络邻居的基因被分到同一 topic。输出的 spot×topic 矩阵解释为细胞类型比例，topic×gene 矩阵解释为潜在细胞类型的表达谱。"
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
      <span>Deconvolution</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>gnSPADE</h1>
    <p>gnSPADE: a reference-free deconvolution method incorporating gene network structures in spatial transcriptomics</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.08.26.672457" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## gnSPADE 中文方法解读

### 一句话理解

gnSPADE 把空间转录组的每个 spot 当成一篇“文档”、把 UMI count 展开成重复出现的“基因词元”，用 LDA topic 表示潜在细胞类型；它在 Gibbs 采样条件概率中再乘一个基因网络 MRF 项，鼓励同一 spot 内互为网络邻居的基因被分到同一 topic。输出的 spot×topic 矩阵解释为细胞类型比例，topic×gene 矩阵解释为潜在细胞类型的表达谱。

“reference-free”只表示不需要配对 scRNA-seq reference；方法仍需要选择基因、指定 topic 数 $K$，并提供或构造基因网络，最后还要用 marker/组织结构为匿名 topic 做生物学注释。

### 输入与输出

输入：

- $D\times V$ 空间 count 矩阵：行是 spots，列是 genes，元素是非负整数 token count。
- topic 数 $K$：假设的潜在细胞类型数。
- 基因网络 `neiPath`：gene → neighbors 的命名列表；可来自 STRING PPI、GRN 或跨 spot 相关网络。
- 超参数：$\alpha$、$\eta$（代码名 `beta`）、MRF 强度 $\lambda$、迭代数等。

输出：

- $\theta_{dk}$：spot $d$ 中 topic/cell type $k$ 的比例。
- $\beta_{kv}$（代码输出名 `phi`）：topic $k$ 对 gene $v$ 的概率。
- topic assignments $Z$、perplexity、log-likelihood 轨迹及稀疏 topic 诊断。

### 从 LDA 到基因网络 LDA

标准 LDA 假设

$$
\theta_d\sim\mathrm{Dirichlet}(\alpha),\qquad
\beta_k\sim\mathrm{Dirichlet}(\eta),
$$

每个 token 先从 $\theta_d$ 抽 topic $z_{dn}$，再从该 topic 的 $\beta_k$ 抽到观测基因 $w_{dn}$。折叠掉 $\theta$ 和 $\beta$ 后，标准 Gibbs 条件由“当前 spot 喜欢哪个 topic”和“当前 gene 喜欢哪个 topic”两个计数项组成。

gnSPADE 增加第三项：

$$
p(z_{dn}=k\mid\cdot)\propto
\frac{N_{dk}^{-dn}+\alpha}{N_{d\cdot}+K\alpha}
\frac{N_{vk}^{-dn}+\eta}{N_{\cdot k}^{-dn}+V\eta}
\exp\left(\lambda\frac{\sum_{j\in\mathcal N_{dv}}\mathbf 1[z_{dj}=k]}{|\mathcal N_{dv}|}\right).
$$

其中 $\mathcal N_{dv}$ 不是相邻 spot，而是同一 spot 内、其 gene identity 与当前 gene 在输入网络中相连的 token positions。网络邻居越多被分到 $k$，指数项越偏向 $k$；$\lambda=0$ 时退化为标准 LDA。

这点很容易误读：gnSPADE 名称中的“spatial”来自输入是空间 spots 和输出可画回坐标，代码没有 spot-to-spot spatial graph 或空间平滑 prior。MRF 完全作用于单个 spot 内的 gene-gene 关系。

### 完整计算流程

```text
ST count matrix
  ↓ 去掉 <1% spots 检出的基因；选 top 1000 overdispersed genes（论文步骤）
gene network
  ├─ STRING/GRN/通路：外部构造 neiPath
  └─ correlation：GenNeiPath(corpus, threshold)
  ↓
WRLDA(corpus, K, neiPath, lambda, iterations)
  ↓ R: Weight_Term → weightedLDA → keyATM_initialize
  ↓ C++: 建计数表 + 每个 spot 的邻居 token 索引
  ↓ 逐 token collapsed Gibbs：LDA conditional × MRF multiplier
  ↓
posterior theta / phi + perplexity
  ↓ 对多个 K 重复运行
结合低 perplexity 与 mean proportion <5% 的 rare topics 人工选 K
  ↓ marker/top genes + 空间位置解释匿名 topics
```

论文预处理要求删除少于 1% spots 检出的基因并保留前 1,000 个 overdispersed genes；这些步骤在本地包中 **Not found**。STRING 网络下载和过滤也不在包内。用户必须在调用 `WRLDA()` 前完成。

### 代码如何落地

R 入口 `R/MRFLDA.R:5-45` 设置默认 $\alpha=1/K$、`beta=0.01`、$\lambda=1$，构造 weight matrix 与 network，然后进入继承自 keyATM 的初始化/拟合框架。C++ `src/LDA_base.cpp:173-219` 在每次 token 更新时：

1. 从 $n_{kv},n_k,n_{dk}$ 删除旧 topic 计数；
2. `computeNeiProb()` 统计网络邻居的 topic 比例；
3. 计算标准 LDA 条件并乘 `exp(lambda*neiProb(k))`；
4. 抽新 topic 并把计数加回。

后验 spot proportions 使用

$$
\hat\theta_{dk}=\frac{n_{dk}+\alpha_k}{\sum_{k'}n_{dk'}+\sum_{k'}\alpha_{k'}},
$$

topic gene profile 同理用 topic-gene counts 加 `beta` 后按行归一化。Perplexity 由 `R/MRFLDA.R:131-138` 根据 $\theta\phi$ 对观测 counts 的似然计算。

### 两个影响实际运行的关键代码边界

#### 1. 默认调用实际上没有网络边

`GenNeiPath()` 自己的函数签名默认 `threshold=0.8`，但公开入口 `WRLDA()` 的默认是 `threshold=1`，并把它显式传入。网络条件为 `correlation > threshold`，相关系数不可能大于 1，因此在用户既不传 `neiPath`、也不改 threshold 时，邻接表为空，MRF 不生效，方法退化为 LDA。使用者必须显式提供 STRING/GRN 网络或把 threshold 调低。

#### 2. MRF 邻居 topic 使用初始化快照

初始化时 `LDA_base.cpp:144-145` 调用 `Z_vector = convertZ()`，把 Rcpp `Z` 复制到一个 C++ vector。`computeNeiProb()` 后续读的是这个 `Z_vector`（`LDA_base.h:36-55`），而每次 Gibbs 更新改变的是主 `Z`/局部 `doc_z`；源码中没有同步更新 `Z_vector[doc][position]`。因此邻居比例似乎始终来自初始 topic assignment，而不是论文公式要求的当前 Gibbs 状态。

这是严重的 paper-code mismatch：LDA 计数项会学习，但 MRF 项表现为固定的随机初始化偏置。除非存在本地未见的同步路径，否则不能声称代码精确实现了动态 MRF Gibbs。当前检索范围覆盖 `convertZ`、`Z_vector`、`sample_z` 和 iteration call path，未找到更新语句。

### 模型选择与注释

论文从 $K=2$ 起做 grid search。随着 $K$ 增大 perplexity 通常下降，但小 topic 增多；作者把跨 spots 平均比例低于 5% 定义为 rare cell type，并在二者之间折中。包只提供 `PerplexityPlot()` 可视化，没有自动 grid runner 或最优 $K$ 选择器，最终选择需要用户判断。

topic 是无标签的。模拟数据用真实表达谱与 topic profile 的 Pearson correlation 匹配；真实数据则结合 top genes、marker、空间区域和组织知识注释。因此“reference-free”不等于“自动给出可靠细胞名称”。

### 五张主图支持什么

- Figure 1：展示 count matrix + gene network → topic model → expression profiles 与 spot proportions；图中的 Opt K 是工作流概念，不是一个自动代码模块。
- Figure 2：在 model-based simulation 中，gnSPADE 的 profile/proportion 对角相关更强，gene rank SCC 0.99 对 STdeconvolve 的 0.93，并有较低 RMSE。
- Figure 3：在 MERFISH 聚合的 MPOA 和 mouse kidney pseudo-ST 中比较 STdeconvolve、gnSPADE 和 SpiceMix；gnSPADE总体有更低 proportion RMSE 和更高 profile correlation。MPOA 的 gene-rank SCC 仅从 0.66 提升到 0.69，提示优势并非所有指标都巨大。
- Figure 4：在 mouse olfactory bulb、Visium brain 和 embryo 中展示 topic 空间图；这些真实数据没有逐 spot 细胞比例 ground truth，证据主要是与组织区/marker 的一致性。
- Figure 5：在 PDAC 中比较五种方法与组织学区域。作者报告 gnSPADE 的 cancer-related topic 在 cancer 区更高，但这仍是区域一致性而非单细胞比例真值验证。

### 代码覆盖与复现性

本地仓库提供 R 包主体、Rcpp/C++ sampler、后验输出和绘图辅助函数，但整体 fidelity 是 **Medium**：

- Exact/近似匹配：标准 LDA 条件、MRF 指数乘子、$\theta/\phi$ 后验、perplexity、默认 priors。
- Partial：论文动态 MRF 与代码静态 `Z_vector`；公开默认 threshold 导致无网络。
- Not found：overdispersion gene selection、STRING construction、simulation scripts、真实数据 benchmark pipeline、自动 $K$ 搜索。
- `DESCRIPTION` 只声明 Rcpp/RcppEigen，但运行代码还依赖 quanteda、tidyverse、topicmodels、slam、ggplot2、STdeconvolve 等，干净环境安装会缺依赖。
- 没有 vignette、示例数据、renv lockfile 或 tests。

因此该包能让人检查核心 sampler 并自行运行，但不能从仓库一键复现论文五张主图。尤其在修复/确认 `Z_vector` 同步之前，不能把网络项的实现视为与公式完全一致。

### 最终理解

gnSPADE 的方法思想清楚：用基因网络打破 LDA 的 gene-independence 假设，让功能相关基因帮助定义更连贯的潜在细胞类型。论文模拟和真实组织图支持这一方向，但实际代码的默认网络配置和邻居 topic 缓存直接影响核心创新是否真正生效。研究使用时应显式构造网络、检查 $K$ 与 topic 注释，并优先验证或修复 Gibbs 过程中 `Z_vector` 的更新。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## gnSPADE: A Reference-Free Deconvolution Method Incorporating Gene Network Structures in Spatial Transcriptomics

**Paper**: Xie, A. & Cui, Y. bioRxiv, 2025.08.26.672457 (2025).
**DOI**: [10.1101/2025.08.26.672457](https://doi.org/10.1101/2025.08.26.672457)
**Code**: [https://github.com/Cui-STT-Lab/gnSPADE](https://github.com/Cui-STT-Lab/gnSPADE) (R package with C++ backend, GPL-3.0)

---

### Motivation & Novelty

#### Biological Problem

Spatial transcriptomics (ST) technologies such as 10x Visium and DBiT-seq profile gene expression at multicellular resolution, where each captured spot contains a mixture of cell types. **Deconvolution** — estimating the proportions of constituent cell types within each spot — is essential for downstream analysis including cell-type-specific spatial gene expression, cell-cell communication inference, and spatial domain detection. Most deconvolution methods require a **single-cell RNA-seq (scRNA-seq) reference** to define cell-type expression signatures, but such references may be unavailable, incomplete, or poorly matched to the ST tissue.

#### Limitations of Existing Approaches

**Reference-based methods** depend on external scRNA-seq data whose cell-type composition, batch effects, or biological context may not align with the ST sample:

| Method | Journal & Year | Limitation |
|--------|---------------|------------|
| **RCTD** | *Nature Biotechnology*, 2022 | Requires matched scRNA-seq reference; sensitive to reference quality |
| **Cell2location** | *Nature Biotechnology*, 2022 | Requires scRNA-seq reference; computationally heavy (variational inference) |
| **SPOTlight** | *Nucleic Acids Research*, 2021 | NMF-based; requires scRNA-seq reference for seeding |
| **CARD** | *Nature Biotechnology*, 2022 | Requires scRNA-seq reference; spatial smoothing adds assumptions |

**Existing reference-free methods** avoid the reference dependency but have their own limitations:

| Method | Journal & Year | Limitation |
|--------|---------------|------------|
| **STdeconvolve** | *Nature Communications*, 2022 | LDA-based; assumes gene independence within each cell type (bag-of-words), ignoring gene-gene interactions |
| **SpiceMix** | *Nature Genetics*, 2023 | NMF + HMRF on spots; not specifically optimized for cell-type deconvolution; spatial smoothing operates on spot neighbors rather than gene relationships |
| **SMART** | *Genome Biology*, 2023 | Semi-supervised; requires known marker genes as input |
| **CARD-free** | *Nature Biotechnology*, 2022 | Marker-gene-required variant; not fully reference-free |

#### Unique Contributions

1. **Gene network-enhanced topic model**: Extends LDA by incorporating a Markov random field (MRF) over gene-gene interaction networks on the latent cell type assignment layer, encouraging functionally related genes (connected in PPI networks, GRNs, or co-expression networks) to be co-assigned to the same cell type
2. **Reference-free with respect to scRNA-seq**: Requires the ST count matrix and a gene network; code can construct a correlation network, but `WRLDA()` passes a default threshold of 1, yielding no edges under the strict `cor > threshold` rule unless the user changes it.
3. **Flexible network input**: Supports protein-protein interaction (PPI) networks from STRING, gene regulatory networks, or user-defined co-expression networks
4. **Principled model selection**: Grid search over the number of cell types $K$ with perplexity-based evaluation and rare cell type filtering

---

### Method Overview

#### Generative Model

gnSPADE builds on Latent Dirichlet Allocation (LDA), treating each spot as a "document" and each gene's expression count as a "word." The generative process is:

1. For each cell type $k \in \{1, \ldots, K\}$, draw a gene distribution $\boldsymbol{\beta}_k \sim \text{Dir}(\eta)$
2. For each spot $d \in \{1, \ldots, D\}$:
   - Draw cell type proportions $\boldsymbol{\theta}_d \sim \text{Dir}(\alpha)$
   - For each gene token $n \in \{1, \ldots, N_d\}$:
     - Draw a cell type assignment $z_{d,n} \sim \text{Mult}(\boldsymbol{\theta}_d)$
     - Draw the observed gene $w_{d,n} \sim \text{Mult}(\boldsymbol{\beta}_{z_{d,n}})$

The key extension over standard LDA is the **MRF regularization** on the cell type assignments $z_{d,n}$. Given a gene network $G = (V, E)$ where vertices are genes and edges connect functionally related gene pairs, the MRF adds an edge potential that favors assigning connected genes to the same cell type.

#### MRF-Enhanced Collapsed Gibbs Sampling

gnSPADE integrates out $\boldsymbol{\theta}$ and $\boldsymbol{\beta}$ analytically (collapsed Gibbs sampling) and samples each $z_{d,n}$ from:

$$P(z_{d,n} = k \mid \mathbf{z}_{-(d,n)}, \mathbf{w}, \alpha, \eta, \lambda) \propto \left( n_{d,k}^{-(d,n)} + \alpha \right) \cdot \frac{n_{k,w_{d,n}}^{-(d,n)} + \eta}{\sum_{v} n_{k,v}^{-(d,n)} + V\eta} \cdot \exp\left( \lambda \cdot \frac{\sum_{j \in \mathcal{N}(n)} \mathbf{1}[z_{d,j} = k]}{|\mathcal{N}(n)|} \right)$$

where:
- $n_{d,k}^{-(d,n)}$ = count of tokens in spot $d$ assigned to cell type $k$, excluding position $(d,n)$
- $n_{k,v}^{-(d,n)}$ = count of gene $v$ assigned to cell type $k$, excluding $(d,n)$
- $\mathcal{N}(n)$ = neighbors of gene $w_{d,n}$ in the gene network $G$
- $\lambda$ = MRF coupling strength (default $\lambda = 1$)

The first two factors are the standard collapsed LDA full conditional. The third factor is the **MRF potential**: it upweights cell type $k$ when a larger fraction of the gene's network neighbors (within the same spot) are already assigned to $k$. This encourages co-regulated or physically interacting genes to cluster into the same cell type.

#### Computational Pipeline

1. **Gene selection**: Remove genes detected in $<1\%$ of spots; retain top 1000 overdispersed genes (variance-to-mean ratio)
2. **Gene network construction**:
   - **Option A (default)**: Pairwise Pearson correlation across spots; threshold at user-specified cutoff to create binary adjacency matrix (code default `threshold=1` effectively disables this; users must set a lower value like 0.8)
   - **Option B (recommended)**: PPI network from STRING database; subset to selected genes
   - **Option C**: User-supplied adjacency matrix (e.g., from GRN inference)
3. **Count discretization**: Round normalized counts to integers for the multinomial likelihood
4. **MRF-enhanced collapsed Gibbs sampling**: Run for a specified number of iterations (default: 1500)
5. **Parameter estimation**: Compute posterior point estimates from the final iteration's topic assignments for $\hat{\boldsymbol{\theta}}_d$ (cell type proportions per spot) and $\hat{\boldsymbol{\beta}}_k$ (gene expression profiles per cell type). Note: the code uses single-sample estimates from the last iteration, not averaged post-burn-in statistics
6. **Model selection**: Repeat for a grid of $K$ values; select $K$ that minimizes perplexity while avoiding excess rare cell types (mean proportion $<5\%$)

#### Hyperparameters

| Parameter | Default | Role |
|-----------|---------|------|
| $\alpha$ | $1/K$ | Dirichlet prior on cell type proportions (sparse) |
| $\eta$ | $0.01$ | Dirichlet prior on gene distributions (sparse) |
| $\lambda$ | $1$ | MRF coupling strength |
| Iterations | 1500 | Total Gibbs sampling iterations |
| Thinning | 5 | Store theta/phi every $n$ iterations for convergence diagnostics |

#### Implementation

gnSPADE is implemented as an R package built on the **keyATM** framework (keyword-assisted topic model). The performance-critical Gibbs sampler is written in C++ via Rcpp/RcppEigen. The main entry function is `WRLDA()`, which accepts the expression matrix, gene network adjacency, and hyperparameters.

---

### Evaluation

#### Simulated Data

**Model-based simulation**: Generated data from the LDA generative model with $K = 4$ cell types, 100 genes, and 1000 spots. gnSPADE consistently recovered the true proportions with higher accuracy than STdeconvolve across varying noise levels.

**Model-free simulation (MERFISH-derived)**: Used real single-cell MERFISH data to construct pseudo-ST spots with known ground-truth proportions:

| Dataset | Technology | Genes | Cell Types | Spots | Source |
|---------|-----------|-------|------------|-------|--------|
| MPOA Brain | MERFISH | 135 | 9 | 3,072 | Moffitt et al., *Science*, 2018 |
| Mouse Kidney | MERFISH | 307 | 8 | 2,472 | He et al., *PNAS*, 2021 |

#### Real ST Data

| Dataset | Technology | Selected $K$ | Key Finding |
|---------|-----------|-------------|-------------|
| Mouse Olfactory Bulb (MOB) | Spatial Transcriptomics | 9 | Better alignment with granule cell layer (GL) than STdeconvolve |
| Mouse Brain | 10x Visium | 14 | Superior identification of ventricular zones and fiber tracts vs SMART |
| Mouse Embryo | DBiT-seq | 13 | Resolved tissue compartments in developing embryo |
| Human PDAC | 10x Visium | 20 | Compared with STdeconvolve, SpiceMix, CARD-free, and SMART |

#### Metrics

- **Pearson Correlation Coefficient (PCC)**: Correlation between estimated and true cell type proportions
- **Spearman Correlation Coefficient (SCC)**: Rank-based correlation, robust to non-linear relationships
- **Root Mean Square Error (RMSE)**: Absolute deviation from ground truth proportions
- **Diebold-Mariano (DM) test**: Statistical test for whether one method's predictions are significantly better than another's

#### Key Results

| Comparison | Result |
|-----------|--------|
| gnSPADE vs STdeconvolve (model-based sim.) | gnSPADE achieves higher PCC and lower RMSE across all simulation settings |
| gnSPADE vs STdeconvolve (MPOA, 9 types) | gnSPADE: PCC improvement in majority of cell types; DM test significant |
| gnSPADE vs SpiceMix (MPOA, Kidney) | gnSPADE outperforms SpiceMix on both datasets in PCC and RMSE |
| gnSPADE vs STdeconvolve (MOB, real data) | gnSPADE produces sharper spatial patterns, better GL layer delineation |
| gnSPADE vs SMART (Mouse Brain, real data) | gnSPADE better resolves ventricular zones and fiber tracts without requiring marker genes |
| Effect of gene network | PPI-based network outperforms correlation-based network; both outperform no-network (standard LDA) |
| Network coupling | The paper establishes that $\lambda=0$ reduces to standard LDA; no source-grounded sensitivity range was found in the main paper |

#### Benchmarked Methods

| Method | Journal & Year | Type |
|--------|---------------|------|
| **STdeconvolve** | *Nature Communications*, 2022 | Reference-free (LDA) |
| **SpiceMix** | *Nature Genetics*, 2023 | Reference-free (NMF + HMRF) |
| **RCTD** | *Nature Biotechnology*, 2022 | Reference-based |
| **Cell2location** | *Nature Biotechnology*, 2022 | Reference-based |
| **SPOTlight** | *Nucleic Acids Research*, 2021 | Reference-based |
| **CARD** | *Nature Biotechnology*, 2022 | Reference-based |
| **CARD-free** | *Nature Biotechnology*, 2022 | Marker-required |
| **SMART** | *Genome Biology*, 2023 | Semi-supervised (marker-assisted) |

---

### Reproducibility

#### Rating: 4/5

**Strengths**:
- R package publicly available on GitHub with clear installation instructions
- Built on the established keyATM package framework, inheriting well-tested C++ Gibbs sampling infrastructure
- Main function `WRLDA()` is well-documented with sensible default hyperparameters
- Gene network construction is flexible: supports STRING PPI, correlation-based, or user-supplied networks
- C++ backend (Rcpp/RcppEigen) ensures computational efficiency for the Gibbs sampler
- All real ST datasets used in evaluation are from publicly available sources

**Potential Blockers**:
- No `renv` lockfile or conda environment specification for exact dependency reproduction
- No example notebooks or vignettes included in the repository
- Supplementary data files referenced but not bundled with the package
- Simulation scripts not included; users cannot directly reproduce simulation benchmarks
- STRING PPI network download and preprocessing steps not fully automated within the package
- Model selection (grid search over $K$) requires manual specification of the search range

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
