---
layout: default
permalink: /paper-atlas/spatialde-6cd51db5/
title: "SpatialDE"
nav: false
description: "SpatialDE 解决的是：给定每个 spot/细胞的空间坐标和每个基因的表达，哪些基因的表达相似性会随空间距离而变化？它不要求先把组织切成离散区域，也不只寻找总体方差大的基因，而是为每个基因比较“含空间协方差的高斯过程模型”和“只有独立噪声的常数模型”。论文发表于 2018 年 Nature Methods（DOI 10.1038/nmeth.4636）。"
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
      <span>Spatially Variable Genes</span>
      <span>Nature Methods · 2018</span>
    </div>
    <h1>SpatialDE</h1>
    <p>SpatialDE: identification of spatially variable genes</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/nmeth.4636" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpatialDE 方法解读：把表达变异拆成“随距离协同变化”和“彼此独立的噪声”

SpatialDE 解决的是：给定每个 spot/细胞的空间坐标和每个基因的表达，哪些基因的表达相似性会随空间距离而变化？它不要求先把组织切成离散区域，也不只寻找总体方差大的基因，而是为每个基因比较“含空间协方差的高斯过程模型”和“只有独立噪声的常数模型”。论文发表于 2018 年 *Nature Methods*（DOI `10.1038/nmeth.4636`）。本工作区保留了论文 PDF 的本地 Markdown 转换、两张主图和官方 SpatialDE 仓库的本地代码快照；没有找到独立的 Supplementary Note/Table 文件。

### 1. 输入和输出

核心输入是：

- $N\times D$ 坐标矩阵 $X$；论文主要用二维坐标，但模型本身也可接收一维时间或更高维位置；
- $N\times G$ 的预处理表达矩阵，每列是一个基因；
- 可选的空间长度尺度网格。

`SpatialDE.run(X, exp_tab)` 对每个基因返回最佳长度尺度、空间与噪声参数、fraction of spatial variance（FSV）、似然比、$P$ 值和 q-value。第二阶段 `model_search()` 可把已显著基因分类成一般平滑、线性或周期模式；`aeh.spatial_patterns()` 则把显著基因聚为若干共享的空间表达图样。

这三个输出层级不能混为一谈：

1. `run()` 回答“是否存在空间依赖”；
2. `model_search()` 回答“更像哪一种核函数形状”；
3. AEH 回答“哪些基因共享一个潜在空间图样”。

### 2. 为什么普通 HVG 或聚类后 ANOVA 不够

HVG 方法只看表达总体方差，不关心高值是否聚集在相邻位置。两个基因可以拥有相同方差：一个在组织中形成连续层带，另一个在各 spot 随机跳动；只有前者是空间结构。先聚类再做 ANOVA 又把连续梯度强行切成离散组，而且检测结果依赖预先得到的分组。

SpatialDE 直接把“位置之间的距离”编码进协方差。只要相近位置的表达更相似，即使没有已知组织标签、模式不是离散边界，也可能被识别。

### 3. 高斯过程方差分解

对基因 $g$ 的预处理表达向量 $\mathbf y_g$，论文模型为

$$
\mathbf y_g\sim
\mathcal N\!\left(
\mu_g\mathbf 1,
\sigma_{s,g}^2\left(\Sigma_l+\delta_g I\right)
\right).
$$

从左到右读：$\mu_g\mathbf1$ 是全组织平均表达；$\Sigma_l$ 让不同位置之间产生空间相关；$I$ 只给每个位置独立方差；$\sigma_s^2$ 控制整体尺度；$\delta$ 是独立噪声相对空间方差的比率。

默认空间核是 squared exponential（SE）：

$$
[\Sigma_l]_{ij}=\exp\left(-\frac{\|\mathbf x_i-\mathbf x_j\|^2}{2l^2}\right).
$$

若两点距离等于 $l$，相关核值为 $e^{-1/2}\approx0.607$；距离为 $2l$ 时降到 $e^{-2}\approx0.135$。因此小 $l$ 表示局部斑块或窄层，大 $l$ 表示组织尺度的平滑趋势。它不是“单位距离内变化次数”；更准确地说，它是协方差衰减的特征空间尺度。

### 4. FSV 到底是什么

论文用 FSV 表示由空间成分解释的变异比例。若空间核已按统一尺度标准化，可以近似理解为

$$
\mathrm{FSV}\approx\frac{1}{1+\delta}.
$$

但当前代码并不是无条件直接使用这个式子。`gower_scaling_factor()` 计算核矩阵的 Gower 尺度 $c_K$，`make_FSV()` 实际返回

$$
\mathrm{FSV}=
\frac{\hat\sigma_s^2 c_K}
{\hat\sigma_s^2 c_K+\delta\hat\sigma_s^2}
=\frac{c_K}{c_K+\delta}.
$$

当 $c_K=1$ 时才退化为 $1/(1+\delta)$。这使不同长度尺度核的方差解释更可比。FSV 大表示拟合后的协方差主要由空间项贡献，但它不等于分类准确率，也不能单独替代显著性：强度大但估计不稳定的模式，和强度较弱但证据稳定的模式，需要结合 $P$/q-value 与不确定度判断。

### 5. 如何高效拟合每个基因

对固定核 $\Sigma_l$，朴素高斯过程每个基因都要分解一个 $N\times N$ 协方差矩阵，代价约为 $O(N^3)$。SpatialDE 利用所有基因共享坐标和候选核：

1. 对每个候选长度尺度先计算 $\Sigma_l=U\operatorname{diag}(S)U^T$；
2. 缓存特征值 $S$、$U^T\mathbf1$ 等量；
3. 每个基因只需计算 $U^T\mathbf y_g$；
4. 在旋转后的对角空间中优化一个标量 $\log\delta$；
5. 给定 $\delta$，$\mu$ 与 $\sigma_s^2$ 有闭式估计。

代码 `factor()` 用 `numpy.linalg.eigh` 分解核并把负/过小特征值裁到 `1e-8`。`lbfgsb_max_LL()` 在 $\log\delta\in[-10,20]$ 上用 L-BFGS-B 优化，并检查两个边界。这样昂贵的特征分解按“核”做一次，随后复用于所有基因；不过预计算仍需要保存稠密 $N\times N$ 核并做特征分解，所以对数万细胞并不是线性可扩展方法。

### 6. 显著性检验的实际代码路径

`run()` 默认根据坐标距离构造 10 个对数均匀的 SE 长度尺度，从“最小非零距离的一半”覆盖到“最大距离的两倍”，并加入常数空模型。对每个基因：

1. 在 10 个 SE 模型中选择边际对数似然最大的模型；
2. 与只有均值和独立方差的 `const_fits()` 比较；
3. 计算代码中的 `LLR = max_ll_spatial - max_ll_const`；
4. 用 `1 - chi2.cdf(LLR, df=1)` 得到 $P$ 值；
5. 用 `util.qvalue()` 进行 q-value/FDR 调整。

这里有两个复现细节。

第一，很多文献把似然比统计量写作 $2(LL_1-LL_0)$，但当前代码把未乘 2 的 `LLR` 直接送入 $\chi_1^2$ 分布。这是该历史实现的直接行为，解释或复现应跟随代码而不是自动补上因子 2。

第二，`run()` 的默认备择只有 SE 核。线性核和周期核不参与主显著性检验；它们在显著基因的后续 `model_search()` 中参与模型分类。

### 7. 数据预处理不是可选装饰

论文模型假设近似高斯、各位置条件独立的残差噪声。原始测序计数既异方差，又常随每个 spot 的总计数变化。论文和 CLI 因此采用两步：

1. `NaiveDE.stabilize()` 对计数做方差稳定化；
2. `NaiveDE.regress_out(..., 'np.log(total_counts)')` 回归掉 log 总计数。

CLI 还过滤总计数低于 3 的基因和总计数不超过 5 的位置。核心 `run()` 本身不会检查或执行这些步骤；它明确假定 `exp_tab` 已恰当归一化。直接把原始计数传给 `run()` 可能把测序深度的空间变化当成生物空间信号。

预处理也决定了空模型为什么使用普通高斯均值/方差，而不是负二项计数分布。SpatialDE 不是在原始 UMI 层面直接建模计数。

### 8. 用 BIC 区分平滑、线性和周期模式

显著基因可以进一步比较三类核：

- SE 核：一般平滑空间变化；
- linear kernel：$K=XX^T/\max(XX^T)$，表示线性梯度；
- periodic kernel：$K_{ij}=\cos(2\pi\|x_i-x_j\|/p)$，$p$ 是周期。

`dyn_de()` 为模型记录参数数目 $M$，计算

$$
\mathrm{BIC}=-2LL+M\log N.
$$

`model_search()` 将候选结果与主检验的最佳 SE 结果合并，选择 BIC 最低的类别，并由 BIC 差异计算近似模型后验权重。线性/周期标签是候选核之间的相对选择，不证明组织存在严格物理周期；边界、有限视野和噪声都可能让视觉相似的模式得到不同分类，论文也明确指出周期模式在边缘情况下受噪声影响。

### 9. Automatic Expression Histology（AEH）

AEH 不聚类 spot，而是聚类显著基因。它假设 $C$ 个潜在空间图样 $\boldsymbol\mu_k$ 各自受同一 SE 高斯过程先验约束，每个基因由隐藏变量 $z_{gk}$ 分配到一个图样，并在图样周围加入独立噪声：

$$
\mathbf y_g=\sum_{k=1}^C z_{gk}\boldsymbol\mu_k+\boldsymbol\epsilon_g.
$$

`spatial_patterns()` 先对每个基因跨位置中心化和标准化，因此聚类关注图样形状而不是绝对表达量。`fit_patterns()` 随机初始化成员概率与图样，交替更新：

- $r_{gk}$：基因属于图样 $k$ 的后验责任度；
- $m_k$：该图样在所有位置的后验均值；
- $\pi_k$：图样混合比例；
- $\sigma_e^2$：通过优化变分下界估计的噪声。

用户必须给出图样数 $C$ 和长度尺度 $l$；论文示例在嗅球、乳腺癌和 seqFISH 中都设 $C=5$，长度尺度依数据集给定。AEH 结果因此不是自动确定聚类数，也不是组织切片的细胞类型真值。随机初始化还意味着应固定随机种子或重复运行检查稳定性。

### 10. 主图如何支撑结论

#### 图 1：方法机制，不是 benchmark

图 1a 把每个位置的表达画成空间曲面；1b 对比无空间协方差、短长度尺度、长长度尺度和独立噪声；1c 显示 AEH 从多个基因反推出少量隐藏组织图样和基因—图样归属。它说明模型的三层结构，但没有给出检验校准或外部准确率。

#### 图 2：两种技术、两类应用

嗅球数据中 SpatialDE 报告 67 个 FDR<0.05 的 SV 基因，空间依赖最高解释约 70% 变异；其中包括周期及一般平滑模式。图 2b-c 把基因表达与 H&E 组织形态并列，图 2d 展示五个 AEH 图样。seqFISH 的 249 个候选基因中，方法报告 32 个 SV 基因，包括 5 个线性与 8 个周期模式；图 2g 展示 Htr3a、Foxj1、Sst、Mog、Myl4、Ndnf 等不同形状，图 2h 展示 AEH 图样。

这些结果说明同一框架可用于测序 spot 与成像细胞，并能发现连续、周期和局部模式。它们不是在完整转录组上统一比较所有技术：seqFISH 面板本来只有 249 个预选基因，不能把 32/249 当作全基因组发现率。

正文还报告乳腺癌 115 个、MERFISH 140 probes 中 91 个 SV 基因；这些证据来自文字和补充图引用，本地未保留对应补充图，不能声称已在本工作区视觉核验。

### 11. 论文—代码对应关系

| 机制 | 状态 | 直接代码证据 |
|---|---|---|
| SE 空间核与长度尺度 | Exact | `Python-module/SpatialDE/base.py:24-43` |
| 线性和周期核 | Exact | `Python-module/SpatialDE/base.py:46-59` |
| 核特征分解与数值裁剪 | Exact | `Python-module/SpatialDE/base.py:63-79` |
| 边际似然与 $\delta$ 优化 | Exact | `Python-module/SpatialDE/base.py:90-183` |
| Gower 校正 FSV | Exact | `Python-module/SpatialDE/base.py:63-73`, `205-216` |
| 多长度尺度拟合与 BIC | Exact | `Python-module/SpatialDE/base.py:319-409` |
| 常数空模型、LLR、$P$/q-value | Exact/Convention | `Python-module/SpatialDE/base.py:219-317`, `412-436`；LLR 未乘 2 |
| 方差稳定与回归总计数 | Exact/External | `Python-module/SpatialDE/scripts/spatialde_cli.py:29-46` 调用外部 NaiveDE |
| AEH 变分更新 | Exact | `Python-module/SpatialDE/aeh.py:12-227` |
| AEH 基因标准化和输出 | Exact | `Python-module/SpatialDE/aeh.py:230-268` |
| 论文全部补充 benchmark | Partial | 分析 notebooks/CSV 留存较多，但独立 Supplementary Note/Table 未找到 |

### 12. 最简心智模型与使用边界

把每个基因想成一列沿地图测得的温度。SpatialDE 问的不是“温度是否波动大”，而是“相邻测点是否共同偏高或偏低”。它为多个候选空间尺度分别造一张“距离应产生多大相关”的模板，先把每张模板分解一次，再快速检查所有基因。若某个空间模板比独立噪声模型更能解释数据，就给出显著性和 FSV；随后才用不同模板给模式命名，或让 AEH 把形状相近的基因合并成隐藏组织图样。

可靠使用至少要确认：输入已做方差稳定与深度回归；坐标单位与长度尺度一致；q-value 而非原始 $P$ 值用于批量发现；FSV 与显著性分别解释；AEH 的 $C$、$l$ 和随机种子经过敏感性检查。对于大规模单细胞空间数据，还要预先评估稠密核矩阵的 $O(N^2)$ 内存和 $O(N^3)$ 特征分解边界。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialDE: Identification of Spatially Variable Genes

### Paper Information
- **Title**: SpatialDE: identification of spatially variable genes
- **Authors**: Valentine Svensson, Sarah A Teichmann, Oliver Stegle
- **Publication**: Nature Methods (2018)
- **DOI**: 10.1038/NMETH.4636

### 1. Motivation and Novelty

#### 1.1 Biological Context

Spatial resolution of gene expression is crucial for determining the functions and phenotypes of cells in multicellular organisms. Spatial expression variation can reflect:
- **Cell-cell communication** between adjacent cells
- **Position-specific states** that depend on tissue location
- **Cell migration patterns** where cells move to specific locations to perform functions

#### 1.2 Limitations of Existing Approaches

Prior to SpatialDE, researchers faced significant limitations in analyzing spatial transcriptomics data:

1. **Highly Variable Gene (HVG) methods** (Brennecke et al. 2013):
   - Designed for conventional scRNA-seq
   - **Ignore spatial information** completely
   - Cannot distinguish between spatial and non-spatial variability
   - Example: A gene highly expressed in one region may not be detected as spatially variable

2. **ANOVA-based approaches**:
   - Require **a priori cell annotations** or clustering
   - Can only detect **discrete group differences**
   - **Miss continuous spatial patterns** (e.g., gradients, periodic patterns)
   - Depend on clustering quality, which may not capture spatial structure

3. **Computational inefficiency**:
   - Existing Gaussian process (GP) methods scale $O(N^3)$ in number of cells
   - Prohibitive for spatial transcriptomics datasets with hundreds to thousands of locations

#### 1.3 Key Innovations

SpatialDE introduces three major innovations:

**Innovation 1: Spatial Variance Decomposition**
- Explicitly models spatial and non-spatial variance components
- Quantifies **Fraction of Spatial Variance (FSV)** for each gene
- Enables identification of genes with localized expression patterns

**Innovation 2: Efficient Computation**
- Adapts algebraic tricks from statistical genetics (Lippert et al. 2011)
- Reduces complexity through precomputation and eigendecomposition
- Makes transcriptome-wide analysis feasible in minutes

**Innovation 3: Pattern Classification and Clustering**
- **Model selection** using BIC to classify spatial patterns:
  - General spatial trends (squared exponential kernel)
  - Linear gradients (linear kernel)
  - Periodic patterns (cosine kernel)
- **Automatic Expression Histology (AEH)**: Spatial clustering of genes
  - Groups genes with similar spatial patterns
  - Identifies tissue structures without histological annotation

#### 1.4 Significance

SpatialDE addresses a critical gap in spatial transcriptomics analysis:
- **Unsupervised**: No need to define spatial regions manually
- **Non-parametric**: Captures complex, non-linear expression patterns
- **Statistically rigorous**: Likelihood ratio test with FDR correction
- **Widely applicable**: Works with any spatially-resolved data (sequencing, imaging, temporal)

---

### 2. Method Overview

#### 2.1 Core Statistical Framework

SpatialDE uses **Gaussian Process (GP) regression** to model spatial gene expression. For a given gene with expression levels $y = (y_1, ..., y_N)$ across spatial coordinates $X = (x_1, ..., x_N)$:

$$P(y \mid \mu, \sigma_s^2, \delta, \Sigma) = N(y \mid \mu \cdot 1, \sigma_s^2 \cdot (\Sigma + \delta \cdot I))$$

Where:
- $\mu$ is the mean expression level (fixed effect)
- $\sigma_s^2$ is the spatial variance component
- $\Sigma$ is the **spatial covariance matrix** encoding spatial dependencies
- $\delta \cdot I$ represents **independent observation noise** (non-spatial variation)

**Key insight**: The ratio $\text{FSV} = \frac{1}{1 + \delta}$ quantifies the fraction of variance explained by spatial effects.

#### 2.2 Spatial Covariance Functions

SpatialDE implements multiple covariance kernels to capture different spatial patterns:

##### Squared Exponential (SE) Kernel - General Spatial Trends
$$\Sigma_{i,j} = k(x_i, x_j) = \exp\left(-\frac{|x_i - x_j|^2}{2 \cdot l^2}\right)$$

- Models smooth, continuous spatial variation
- **Length scale** $l$ determines how rapidly covariance decays with distance
- Small $l$: localized expression patterns
- Large $l$: broad spatial trends

##### Linear Kernel - Linear Gradients
$$K_{i,j} = \frac{x_i \cdot x_j}{\max(x_i \cdot x_j)}$$

- Captures directional expression gradients (e.g., anterior-posterior axis)

##### Cosine Kernel - Periodic Patterns
$$\Sigma_{i,j} = \cos\left(2 \pi \frac{\sqrt{|x_i - x_j|^2}}{p}\right)$$

- Identifies repeating spatial structures
- **Period** $p$ determines the wavelength of oscillation
- Example: Bilateral symmetry in tissues

#### 2.3 Statistical Inference

##### Parameter Estimation
The marginal log-likelihood to maximize:

$$LL = -\frac{1}{2} \left[ N \log(2\pi) + \log(|\sigma_s^2 \cdot (\Sigma + \delta \cdot I)|) + (y - \mu \cdot 1)^T (\sigma_s^2 \cdot (\Sigma + \delta \cdot I))^{-1} (y - \mu \cdot 1) \right]$$

**Optimization strategy**:
1. **Closed-form solutions** for $\mu$ and $\sigma_s^2$ given $\delta$ and $l$
2. **Grid search** over length scale $l$ (typically 10 values from $l_{\min}$ to $l_{\max}$)
3. **Gradient-based optimization** (L-BFGS-B) for $\delta$

##### Significance Testing
Compare alternative model (spatial + noise) vs. null model (noise only):

**Null model** (equation 4):
$$P(y \mid \mu, \sigma^2) = N(\mu \cdot 1, \sigma^2 \cdot I)$$

**Test statistic**: Log-likelihood ratio (LLR)
$$\text{LLR} = \log L(\text{spatial model}) - \log L(\text{null model})$$

**P-value**: Analytically computed using $\chi^2$ distribution with 1 degree of freedom

**Multiple testing correction**: Q-value method (Storey & Tibshirani 2003) to control FDR

#### 2.4 Model Selection via BIC

After identifying significant spatially variable (SV) genes, classify their spatial patterns using **Bayesian Information Criterion**:

$$\text{BIC} = \log(N) \cdot M - 2 \cdot LL$$

Where $M$ is the number of hyperparameters:
- Null model: $M = 1$
- Const model: $M = 2$
- Linear: $M = 3$
- SE/Periodic: $M = 4$

The model with **lowest BIC** is selected as the best fit.

#### 2.5 Automatic Expression Histology (AEH)

AEH is a spatial clustering method that identifies sets of genes marking distinct spatial patterns.

**Generative model**:
Let $Y = (y_1, ..., y_G)$ be the expression matrix of $G$ SV genes, and $\mu = {\mu_1, ..., \mu_K}$ be $K$ underlying spatial patterns.

$$P(Y, \mu, Z, \sigma_e^2, \Sigma) = P(Y \mid \mu, Z, \sigma_e^2) \cdot P(\mu \mid \Sigma) \cdot P(Z)$$

Where:
- $Z$ is a binary indicator matrix: $z_{g,k} = 1$ if gene $g$ belongs to pattern $k$
- $P(Y \mid \mu, Z, \sigma_e^2)$: Likelihood of observing gene expression given patterns
- $P(\mu \mid \Sigma)$: Spatial GP prior on patterns $\mu_k \sim N(0, \Sigma)$
- $P(Z)$: Uniform prior over pattern assignments

**Inference**: Variational Bayes (mean-field approximation)
1. **E-step**: Update posterior assignments $Q(Z)$ given current patterns $\mu$
2. **M-step**: Update patterns $\mu$ given current assignments $Z$
3. Iterate until convergence (ELBO maximization)

**Output**:
- Spatial patterns $\overline{\mu}_k$ representing tissue structures
- Gene-pattern assignments for biological interpretation

#### 2.6 Computational Efficiency

**Key optimization**: Eigendecomposition precomputation

For each kernel $\Sigma$:
1. Compute eigendecomposition: $\Sigma = U S U^T$
2. Transform data: $\text{UTy} = U^T y$, $\text{UT1} = U^T 1$
3. All likelihood evaluations use transformed space

**Complexity**:
- Eigendecomposition: $O(N^3)$ (done once per kernel)
- Per-gene likelihood: $O(N)$ after precomputation
- **Total**: $O(K \cdot N^3 + G \cdot N)$ for $K$ kernels and $G$ genes

This is drastically faster than naive $O(G \cdot K \cdot N^3)$ complexity.

---

### 3. Evaluation Strategy

#### 3.1 Datasets

SpatialDE was evaluated on diverse spatial transcriptomics platforms:

##### Dataset 1: Mouse Olfactory Bulb (Spatial Transcriptomics)
- **Technology**: Spatial Transcriptomics (Ståhl et al. 2016)
- **Resolution**: 100 μm spots (10-100 cells per spot)
- **Data**: 262 spots, 14,859 genes
- **Biological structure**: Well-defined anatomical layers visible in H&E staining

##### Dataset 2: Breast Cancer Biopsy (Spatial Transcriptomics)
- **Technology**: Spatial Transcriptomics
- **Data**: Human breast cancer tissue
- **Biological challenge**: Heterogeneous tumor microenvironment

##### Dataset 3: Mouse Hippocampus (seqFISH)
- **Technology**: Sequential barcoded fluorescence in situ hybridization
- **Resolution**: Single-cell, subcellular precision
- **Data**: 249 genes in dorsal-ventral hippocampus axis
- **Biological focus**: Cell-type composition along developmental axes

##### Dataset 4: Human Osteosarcoma Cells (MERFISH)
- **Technology**: Multiplexed error-robust FISH (Moffitt et al. 2016)
- **Resolution**: Single-cell
- **Data**: 140 genes in cultured cells
- **Biological discovery**: Spatial dependency in cell culture (unexpected)

##### Dataset 5: Frog Development (Temporal RNA-seq)
- **Technology**: Time-course RNA-seq (Owens et al. 2016)
- **Data**: *Xenopus* embryo development (1D "spatial" data)
- **Purpose**: Demonstrate temporal applicability

#### 3.2 Evaluation Metrics

##### Primary Metric: Spatially Variable Genes Detected
- **FDR threshold**: 0.05 (Q-value corrected)
- **Comparison**: SpatialDE vs. HVG methods (Seurat/ScanPy)

**Results summary**:
- Mouse OB: 67 SV genes (SpatialDE) vs. 3,497 HVGs; overlap = 40 genes
- Breast cancer: 115 SV genes vs. 3,503 HVGs; overlap = 34 genes
- seqFISH: 32 SV genes vs. 58 HVGs; overlap = 5 genes
- MERFISH: 91 SV genes (65% of all genes)

**Key finding**: SpatialDE identifies **distinct gene sets** from HVG methods, capturing spatial patterns missed by variance-only approaches.

##### Fraction of Spatial Variance (FSV)
- Quantifies spatial contribution to total variance
- Mouse OB: Up to **70% FSV** for top SV genes
- Interpretation: Genes with high FSV have expression primarily determined by spatial location

##### Length Scale Characterization
- **Localized patterns**: Small length scales (e.g., 150 μm in OB)
- **Broad patterns**: Large length scales (e.g., 1.8 mm periodicity for bilateral genes)

#### 3.3 Biological Validation

##### Mouse Olfactory Bulb
**Canonical markers identified**:
- *Penk*, *Doc2g*, *Kctd12* (highlighted in Ståhl et al.)
- Granule cell layer markers: *Kcnh3*, *Nrgn*, *Mbp*

**Novel periodic patterns discovered**:
- **Bilateral symmetry**: 1.8 mm period (hemisphere spacing)
- **Neuron density patterns**: *Slc17a7* (vesicular glutamate transporter) with 1.1 mm period

**AEH validation**: 5 canonical expression patterns perfectly matched H&E-stained tissue structures.

##### Breast Cancer Biopsy
**Disease-relevant genes**:
- **Extracellular matrix**: Collagens (enriched via reactome "Collagen formation", $P = 3.38 \times 10^{-14}$)
- **Autophagy**: *TP53INP2* in surrounding tissue
- **Immune response**: *CXCL9*, *CXCL13* (cytokines), *IL12RB1*, *IL21R* (interleukin receptors)

**Comparison to ANOVA clustering**:
- SpatialDE uniquely identified **29 genes** not detected by clustering + ANOVA
- These genes had localized expression (small length scales) missed by discrete clustering

**Comparison to HVG methods**:
- Immune genes (*CXCL9*, *CXCL13*) had low rankings in mean-variance or dropout-based HVG methods

##### Mouse Hippocampus (seqFISH)
**Top SV genes**:
- *Mog*, *Myl4*, *Ndnf*: Distinct region of low expression (visible in tissue)
- **Pattern classification**: 5 linear, 8 periodic patterns

**AEH patterns**: Clearly separated cell populations and developmental axes

##### MERFISH Cell Culture
**Unexpected spatial dependency**:
- 65% of genes spatially variable in confluent cell culture
- Identified proliferating vs. resting subpopulations (*THBS1*, *CENPF*)
- **Biological insight**: High confluence induces spatial gene expression patterns

**Negative controls**: Control probes were NOT detected as SV, confirming statistical calibration.

#### 3.4 Statistical Calibration

##### Permutation Tests
- Randomized spatial coordinates: No false positives at FDR < 0.05
- Confirms proper null distribution

##### Simulations
- Tested on simulated data with known spatial patterns
- **Power analysis**: High sensitivity for moderate spatial effects
- **Type I error**: Well-controlled at nominal FDR levels

##### Comparison to Prior Methods
**Advantages over existing GP methods**:
- **Speed**: 10-100× faster due to precomputation
- **Versatility**: Multiple kernel functions for pattern discovery
- **Integration**: AEH combines significance testing and clustering in unified framework

**Complementarity to HVG methods**:
- SpatialDE excels at **localized patterns** (small length scales)
- HVG methods capture **global variance** (cell-type differences)
- Overlap is small (5-40 genes), indicating **orthogonal information**

#### 3.5 Computational Performance

**Benchmarking** (Supplementary Fig. 2):
- Mouse OB (262 spots, ~15K genes): **Few minutes** on standard laptop
- Scales linearly with number of genes after precomputation
- Memory efficient: Eigendecomposition dominates memory usage

**Comparison to alternatives**:
- GPy/GPflow implementations: ~10× slower
- Stan-based Bayesian inference: 100× slower, not practical for transcriptome-wide analysis

---

### 4. Key Insights and Contributions

#### 4.1 Methodological Contributions
1. **First statistical test** explicitly designed for spatial transcriptomics
2. **Principled variance decomposition** into spatial vs. non-spatial components
3. **Pattern discovery** through kernel selection (linear, periodic, general)
4. **Automatic histology** without manual annotation

#### 4.2 Biological Insights
1. **Periodic gene expression** reflects tissue symmetry and structural organization
2. **Localized immune responses** in tumor microenvironment detectable spatially
3. **Cell culture artifacts**: Spatial patterns emerge even in supposedly uniform cultures
4. **Length scale diversity**: Genes operate at multiple spatial scales (100 μm - 2 mm)

#### 4.3 Practical Impact
- **Enables hypothesis-free discovery** of spatial patterns in new tissues
- **Complements clustering** by identifying continuous gradients
- **Applicable beyond sequencing**: Works with imaging-based methods (FISH, MERFISH)
- **Temporal extension**: Demonstrated on developmental time-course data

#### 4.4 Limitations and Future Directions

**Current limitations** (acknowledged in paper):
1. **Edge cases in periodic detection**: Noise can mask significance for borderline patterns
2. **Platform-agnostic model**: Does not explicitly model technology-specific noise
3. **Independent spots assumption**: Ignores local cell density variations
4. **Manual length scale selection** for AEH

**Proposed extensions**:
1. Incorporate **tissue makeup** and **cell density** into model
2. Platform-specific noise models for spatial transcriptomics vs. imaging
3. Combine with **cell position clustering** methods
4. Extension to **3D spatial data** (aligned serial sections, *in situ* sequencing)

---

### 5. Software Implementation

#### 5.1 Package Information
- **Language**: Python 3
- **Installation**: `pip install spatialde`
- **Repository**: https://github.com/Teichlab/SpatialDE
- **License**: MIT

#### 5.2 Main API Functions

##### `SpatialDE.run(X, exp_tab, kernel_space=None)`
Perform SpatialDE significance test.

**Inputs**:
- `X`: $(N \times 2)$ matrix of spatial coordinates
- `exp_tab`: $(N \times G)$ expression table (normalized)
- `kernel_space`: Dictionary specifying kernels and parameters

**Outputs**: DataFrame with columns:
- `g`: Gene name
- `pval`: P-value from likelihood ratio test
- `qval`: FDR-corrected Q-value
- `FSV`: Fraction of spatial variance
- `l`: Fitted length scale
- `model`: Best kernel (SE/linear/PER)

##### `SpatialDE.model_search(X, exp_tab, DE_results, kernel_space=None)`
Classify spatial patterns using BIC-based model selection.

**Outputs**: Pattern classification (linear, periodic, general) for each SV gene.

##### `SpatialDE.fit_patterns(X, exp_tab, SV_genes, n_patterns, length_scale)`
Automatic Expression Histology via spatial clustering.

**Outputs**:
- Spatial patterns $\mu_k$
- Gene-to-pattern assignments

#### 5.3 Data Preprocessing

**Required normalization** (implemented in companion `NaiveDE` package):
1. **Variance-stabilizing transformation**: Anscombe's transformation for negative binomial counts
2. **Regress out total count effects**: Ensure spatial covariance is not confounded by sequencing depth

---

### 6. Reproducibility and Resources

#### 6.1 Data Availability
- All datasets available at GitHub repository
- Figshare archive: https://figshare.com/articles/software/SpatialDE/17065217
- Original data from cited publications

#### 6.2 Analysis Notebooks
Provided in `Analysis/` directory:
- `MouseOB/`: Olfactory bulb analysis
- `BreastCancer/`: Tumor microenvironment
- `SeqFISH/`: Hippocampus single-cell
- `MERFISH/`: Cell culture spatial patterns
- `Frog/`: Temporal development

#### 6.3 Comparison Scripts
- `Comparison/`: Benchmarking against Stan, GPy, HVG methods
- Simulation code for statistical calibration

---

### 7. Citation and Impact

#### 7.1 Citation
```
Svensson, V., Teichmann, S.A. & Stegle, O.
SpatialDE: identification of spatially variable genes.
Nat Methods 15, 343–346 (2018).
https://doi.org/10.1038/nmeth.4636
```

#### 7.2 Impact Areas
- **Spatial transcriptomics analysis** (primary application)
- **Single-cell imaging** (seqFISH, MERFISH)
- **Developmental biology** (temporal patterns)
- **Cancer research** (tumor microenvironment)
- **Neuroscience** (brain tissue organization)

---

### 8. Mathematical Summary

#### Core Equations

**GP Model** (Equation 1):
$$P(y \mid \mu, \sigma_s^2, \delta, \Sigma) = N(y \mid \mu \cdot 1, \sigma_s^2 \cdot (\Sigma + \delta \cdot I))$$

**SE Kernel** (Equation 2):
$$\Sigma_{i,j} = \exp\left(-\frac{|x_i - x_j|^2}{2 \cdot l^2}\right)$$

**Log-likelihood** (Equation 3):
$$LL = -\frac{1}{2} \left[ N \log(2\pi) + \log(|\sigma_s^2 (\Sigma + \delta I)|) + (y - \mu)^T (\sigma_s^2 (\Sigma + \delta I))^{-1} (y - \mu) \right]$$

**Null Model** (Equation 4):
$$P(y \mid \mu, \sigma^2) = N(\mu \cdot 1, \sigma^2 \cdot I)$$

**BIC**:
$$\text{BIC} = \log(N) \cdot M - 2 \cdot LL$$

**FSV**:
$$\text{FSV} = \frac{\sigma_s^2 \cdot \text{Gower}(\Sigma)}{\sigma_s^2 \cdot \text{Gower}(\Sigma) + \delta \cdot \sigma_s^2}$$

---

### Conclusion

SpatialDE represents a foundational advance in spatial transcriptomics analysis, providing the first statistically rigorous, computationally efficient method for identifying and characterizing spatially variable genes. Its combination of hypothesis-free pattern discovery, automatic histology, and broad applicability has made it an essential tool in the spatial omics toolkit.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
