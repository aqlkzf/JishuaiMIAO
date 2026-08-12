---
layout: default
permalink: /paper-atlas/stamp-8736edb8/
title: "STAMP"
nav: false
description: "STAMP 把每个细胞或 spot 表示成若干“主题”的混合比例，同时为每个主题学习一个稀疏的基因模块；空间邻接关系用于推断主题比例，Gamma–Poisson 生成模型用于解释计数，因而低维表示既有空间结构，也能直接通过贡献基因理解。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>STAMP</h1>
    <p>Interpretable spatially aware dimension reduction of spatial transcriptomics with STAMP</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STAMP 方法详解：把空间转录组压缩成可解释的“空间主题”

### 一句话理解

STAMP 把每个细胞或 spot 表示成若干“主题”的混合比例，同时为每个主题学习一个稀疏的基因模块；空间邻接关系用于推断主题比例，Gamma–Poisson 生成模型用于解释计数，因而低维表示既有空间结构，也能直接通过贡献基因理解。

### 1. 它要解决什么问题？

空间转录组同时包含高维基因表达和组织坐标。常见流程通常先降维、再聚类、再做差异表达来解释聚类。这个流程有两个问题：

1. 聚类把每个 spot 强制分到一个类别，但真实组织中常有重叠的细胞状态或生物程序。
2. 许多空间图模型能利用坐标，却输出难以直接解释的黑箱 embedding，最后仍需聚类和差异分析。

传统可解释方法也不完整：NMF（*Nature*, 1999）和 LDA（*JMLR*, 2003）能给出基因载荷，但不使用空间信息；LDVAE 用非线性编码器和线性解码器改善表达能力，但也不显式建模空间；NSFH、SpiceMix 等空间可解释模型计算代价较高。STAMP 的目标是在一个模型中同时获得：空间感知、连续混合主题、可解释基因模块和大规模可训练性（`paper.md:18-27`）。

### 2. 输入和输出

#### 输入

- 计数矩阵 $X\in\mathbb{N}_0^{N\times G}$；
- 根据空间坐标构建的邻接矩阵 $A$；
- 可选的样本/批次标签；
- 可选的有序时间标签；
- 主题数 $K$ 和图传播层数 $l$。

代码要求邻接图已经存在于 `adata.obsp['spatial_connectivities']`。论文中，Visium 使用六邻居；其他平台通常使用约为总细胞数 $1/1000$ 的邻居数，并用 Seurat-v3 方法选择高变基因（`paper.md:471-510`）。

#### 输出

- $Z=\{z_{nk}\}$：每个细胞/spot 的主题比例，每行和为 1；
- $W=\{w_{kg}\}$：每个主题的基因模块分数，可用于基因排序；
- 多样本模式下的共享主题与批次偏移；
- 时间序列模式下随时间变化的主题基因模块。

关键点是：$Z$ 不是硬聚类。一个 spot 可以同时包含多个主题，因此能够表达重叠的空间模式。

### 3. 整体计算流程

```text
原始计数 + 空间坐标
  |
  |-- 过滤低质量细胞/基因，选择高变基因
  |-- 构建空间邻接图 A
  v
归一化图传播：X, SX, ..., S^l X
  |
  |-- 拼接原始表达和空间平滑表达
  |-- MLP 输出主题后验的位置与尺度
  v
每个细胞的主题比例 Z
  |
  |-- 稀疏 horseshoe 先验学习主题基因模块 W
  |-- 背景表达 R
  |-- 可选批次项 / 时间高斯过程
  v
Gamma–Poisson 重构计数
  |
  |-- Pyro SVI 最大化 ELBO
  v
空间主题图 + 基因模块排序 + 富集/整合/发育分析
```

### 4. 生成模型：表达量怎样由主题产生？

STAMP 假设基因 $g$ 在细胞 $n$ 中的计数满足 Gamma–Poisson：

$$
x_{ng}\sim\operatorname{GammaPoisson}(\mu_{ng},\alpha_g),
$$

其中

$$
\mu_{ng}=l_n\sum_k z_{nk}\beta_{kg},
\qquad
l_n=\sum_g x_{ng}.
$$

$l_n$ 是观测到的文库大小；$z_{nk}$ 是细胞 $n$ 中主题 $k$ 的比例；$\beta_{kg}$ 是主题 $k$ 对基因 $g$ 的归一化贡献。直观上，每个细胞的表达谱是多个主题表达谱的加权和，再乘以该细胞的测序深度（`paper.md:180-204`）。

### 5. 主题比例：为什么能表达重叠状态？

STAMP 先在无约束空间中采样主题 logits，再用 softmax 映射到概率单纯形：

$$
\widetilde{\mathbf z}_n\sim
\operatorname{Normal}(0,\mathbf U\mathbf U^{\mathsf T}+\sigma\mathbf I),
\qquad
z_{nk}=\operatorname{softmax}_k(\widetilde z_{nk}).
$$

低秩加对角协方差允许主题相关。例如肝细胞程序和造血程序可能在同一空间区域同时出现，但仍可由不同主题比例表示。代码在训练初期暂时把协方差固定为单位结构；损失停滞后才开始学习主题相关性，以避免多个主题过早塌缩成相同模式（`sctm/model.py:435-462`; `sctm/stamp.py:370-403`）。

### 6. 可解释性的核心：结构化 regularized horseshoe

主题基因嵌入写成

$$
\beta_{kg}=\operatorname{softmax}_g(w_{kg}+r_g),
$$

其中 $r_g$ 是所有主题共享的背景表达，$w_{kg}$ 是真正用于解释主题的基因模块分数。STAMP 对 $w_{kg}$ 使用三级稀疏先验：

$$
\delta_g,\tau_k,\lambda_{kg}\sim\operatorname{HalfCauchy}(1),
$$

- $\delta_g$：基因级开关。接近 0 时，基因 $g$ 在所有主题中都被压缩；
- $\tau_k$：主题级开关。接近 0 时，整个主题受到压缩；
- $\lambda_{kg}$：局部开关。决定某个基因是否属于某个主题；
- $c$：regularized horseshoe 的上限控制，避免弱识别参数无限增大。

因此，模型不是在训练后才从 embedding 中“找 marker”，而是在生成模型中直接学习稀疏、可排序的主题基因模块（`paper.md:225-258`; `sctm/model.py:337-433,759-775`）。

### 7. 空间信息怎样进入模型？

定义加入自环并对称归一化后的传播矩阵：

$$
\widetilde A=A+I,
\qquad
S=\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}.
$$

STAMP 不在 GPU 上反复进行完整 GNN 消息传递，而是提前计算

$$
[X,SX,\ldots,S^lX],
$$

然后交给普通 MLP，得到 $q_\phi(Z\mid X,A)$ 的均值和尺度。这样，图传播可在训练前完成，后续能用标准 mini-batch SVI，避免整张图常驻 GPU（`paper.md:342-369`; `SUPP_MD:217-263`）。

一个很重要的设计是保留原始 $X$。作者发现只输入平滑后的 $S^lX$ 会过度平滑主题，因此默认 `sign` 模式拼接原始和各阶平滑特征。增加图层数会提高 Moran's $I$、产生更平滑的空间边界，但不一定带来更好的生物分辨率。

代码还做了中位文库大小归一化和 `log1p`。此外，`sctm/utils.py:46-57` 在加入一个单位矩阵时将预计算度数加 2，这一细节没有在论文中解释，精确复现时应保留代码行为。

### 8. 多样本和时间序列扩展

#### 多样本/多技术

STAMP 用基因级批次项和主题级批次强度构造

$$
w^{batch}_{skg}=\tau^{batch}_k\otimes\delta^{batch}_{sg}.
$$

$\delta^{batch}_{sg}$ 使用小尺度 Student-$t$ 先验：大多数基因批次效应应较小，但重尾允许少数基因有较大偏差。最终，共享基因模块与批次项一起进入主题基因分布（`paper.md:261-276`）。

#### 时间序列

每个 $w_{kg}$ 在时间上变成一条函数，并使用 Matern-$3/2$ 核：

$$
\kappa(t,t')=\widetilde\sigma^2
\left(1+\frac{\sqrt3|t-t'|}{l}\right)
\exp\left(-\frac{\sqrt3|t-t'|}{l}\right),
\qquad l=1.
$$

只有八个时间点，因此代码使用完整协方差和 Cholesky 分解，不需要稀疏 GP 的诱导点。虽然代码保留了看似可学习的 length-scale 参数，实际计算会把它覆盖为 1，与论文设定一致（`sctm/model.py:463-499,789-822`）。

### 9. 推断与训练

STAMP 用均值场变分分布近似全局参数后验，并用空间 MLP 近似细胞级 $Z$ 后验。优化目标是 ELBO：

$$
\mathcal L=
\mathbb E_q[\log p(X,\Theta,Z)-\log q(\Theta,Z)].
$$

代码使用 Pyro `SVI`、`TraceMeanField_ELBO` 和梯度裁剪 AdamW。论文实验的主要设置为图层数 1、batch size 256、学习率 0.01、梯度范数上限 1；当不同数据集大小差异很大时采用逆频率加权采样；主题协方差在损失停滞 5 个 epoch 后才释放学习（`SUPP_MD:253-263`）。

需要注意：补充材料报告 early-stop patience 为 30，而代码默认值是 20。要复现实验，应使用论文 notebook/脚本的显式参数，不能只依赖类默认值。

### 10. 论文中最有说服力的结果

- **模拟重叠模式：** STAMP 恢复五个可重叠主题，硬聚类方法会拆分或合并这些模式。
- **海马 Slide-seq V2：** 模块 coherence 中位数 0.162、diversity 0.90，均为比较方法中最高；CA1、CA2、CA3、DG、V3、MH、LH 等区域与 marker 表达一致。
- **CosMx 肺癌：** 15 个主题进一步分出 tumor、tumor interior、tumor edge、两个 fibroblast 和 CAF；CAF 位于肿瘤边缘外侧，并富集炎症、纤维化和伤口修复信号。
- **多切片与多技术整合：** 在相邻脑切片、Visium/Stereo-seq/Slide-seq V2 嗅球数据和 12 个 DLPFC 切片中，STAMP 同时保留组织层次并减少批次分离。
- **胚胎时间序列：** 超过 54 万细胞、E9.5–E16.5 八个时间点；40 个主题追踪器官发育，并将空间重叠的造血和肝细胞程序通过不同基因模块分开。

图像证据的共同特点是：主题空间图、已知解剖和高排名 marker 三者相互支持，而不是只依赖 UMAP 或聚类标签。

### 11. 代码与论文的一致性

代码仓库为 `JinmiaoChenLab/scTM`，本地固定在 commit `0099ab268c712c91f398a2862db59b1dc793f69b`。核心一致性为 **high**：Gamma–Poisson、logistic-normal、horseshoe、批次项、时间 GP、SGC 预计算、Pyro SVI 和输出接口都能在直接源码中找到。

主要注意事项：

1. 图度数处理存在论文未说明的实现细节；
2. early-stop 默认值与实验报告不同；
3. 没有索引到核心模型自动化测试；
4. GitHub 中有多个教程 notebook，但论文所说的完整复现脚本和预处理数据位于 Zenodo，本次未将该归档纳入工作区；
5. 本次做了静态源码核对，没有重新训练 54 万细胞的模型。

### 12. 如何正确解读 STAMP 结果？

建议同时检查四件事：

1. 主题比例是否在空间上形成可信结构；
2. 主题的高分基因是否组成连贯模块；
3. marker 表达是否与主题空间分布一致；
4. 改变主题数和图层数后结论是否稳定。

不要把平滑的主题图自动解释为新的细胞类型，也不要把通路富集当作因果机制。时间序列主题描述的是离散时间点之间平滑变化的群体程序，不等同于单细胞谱系追踪。

### 结论

STAMP 最重要的创新不是单独提出一种 topic model 或一种图卷积，而是把空间预计算、概率主题模型、结构化稀疏基因模块、多批次校正和时间 GP 组合成一个可扩展框架。它特别适合这样的研究问题：空间模式可能重叠、需要直接查看贡献基因、数据跨切片/技术/时间点，并且规模大到完整图神经网络难以训练。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## STAMP summary

### What problem does STAMP solve?

Spatial transcriptomics combines high-dimensional gene counts with tissue coordinates, but common dimension-reduction choices force an awkward tradeoff. Classical interpretable methods such as NMF (*Nature*, 1999) and LDA (*JMLR*, 2003) produce gene-loadings that can be inspected, yet they ignore spatial neighborhoods. Spatial graph or probabilistic methods can use coordinates, but their latent embeddings are often interpreted only after clustering and differential expression, or they become costly on large datasets. STAMP addresses this gap by producing spatially organized, continuous topics together with a ranked gene module for every topic (`paper.md:18-27`).

### Core idea

STAMP is a Bayesian deep topic model built around a Gamma–Poisson count likelihood. Each cell or spot has topic proportions $z_{nk}$ that sum to one, and each topic has sparse gene scores $w_{kg}$. A regularized horseshoe prior encourages genes to participate in only a subset of topics and topics to use limited gene sets. Spatial information enters the amortized variational encoder through precomputed simplified graph convolutions: the model feeds $[X,SX,\ldots,S^lX]$ to an MLP instead of training a full message-passing GNN on the entire graph (`paper.md:174-369`).

The same framework supports three regimes:

- **Single sample:** spatial topics and sparse gene modules.
- **Multiple samples/technologies:** gene-wise and topic-wise batch offsets separate technical variation from shared biology.
- **Time series:** every topic–gene score varies across time under a Matern-$3/2$ Gaussian process with fixed length scale 1.

The main outputs are continuous cell-by-topic proportions and gene-by-topic scores. A dominant topic can be used for visualization, but the mixture representation is important because spatial patterns may overlap.

### Computational workflow

```text
counts + spatial coordinates
  -> quality control / HVG selection / spatial-neighbor graph
  -> normalized graph propagation [X, SX, ..., S^lX]
  -> MLP variational encoder q(Z | X, A)
  -> Pyro generative topic model with sparse gene modules
  -> mini-batch SVI maximizing the ELBO
  -> topic maps + ranked gene modules
  -> marker, enrichment, integration or developmental analysis
```

Precomputing graph propagation is the central scaling trick. It lets STAMP train with ordinary mini-batches while retaining spatially smoothed and original expression features. The authors used one graph layer in the reported experiments; more layers visibly increase Moran's $I$ and smoothness but risk over-smoothing.

### Evaluation and main evidence

The paper compares STAMP mainly with NMF, LDA, LDVAE, NSFH and SpiceMix, and adds DeepST, PRECAST and STAligner for integration benchmarks. Evaluation combines module coherence, module diversity, scIB integration metrics, known-marker rankings, tissue anatomy and downstream enrichment (`paper.md:390-468`).

- **Simulated overlapping patterns:** STAMP recovers five overlapping topics that hard clustering methods split or merge, illustrating the difference between mixtures and one-label-per-spot clusters.
- **Slide-seq V2 hippocampus (39,220 spots):** STAMP has the highest median module coherence (0.162) and diversity (0.90), separates CA1/CA2/CA3, DG, V3, medial and lateral habenula, and ranks established markers highly. Topic maps visually agree with marker expression (`paper.md:50-67`).
- **CosMx lung cancer (93,206 spots):** 15 topics resolve tumor, tumor interior, tumor edge, two fibroblast states and a CAF program. The CAF topic lies outside and co-occurs most strongly with the tumor edge; its downstream analysis enriches cytokine, fibrosis and wound-healing pathways (`paper.md:70-87`).
- **Paired Visium brain sections:** shared topics align cortical layers and internal brain structures across anterior and posterior sections while retaining layer marker modules (`paper.md:90-104`).
- **Cross-technology olfactory bulb (148,087 cells):** STAMP mixes Visium, Stereo-seq and Slide-seq V2 batches better than displayed alternatives and gives the top shown aggregate batch-correction score (0.65), while recurring spatial topics match olfactory layers (`paper.md:107-124`).
- **Twelve DLPFC sections:** STAMP leads the displayed aggregate biological-conservation and batch-correction results and preserves cortical layering (`paper.md:127`).
- **Embryo time series (>540,000 cells, E9.5–E16.5):** 40 topics track organs and tissues through development. Time-varying modules distinguish spatially overlapping hematopoiesis and hepatocyte programs and reveal expected heme/erythrocyte versus lipid/lipoprotein processes (`paper.md:130-150`).

Extended Data Figure 7 shows STAMP remaining below 12 hours at the largest plotted scale, while NSFH grows beyond 24 hours. The paper reports all analyses on a Titan V GPU with 12 GB memory (`paper.md:168,525-528`).

### Code-paper match

The paper-cited GitHub repository `JinmiaoChenLab/scTM` was acquired at commit `0099ab268c712c91f398a2862db59b1dc793f69b`. The match is **high** for the core method:

- `sctm/stamp.py` implements AnnData setup, spatial feature preparation, SVI training and outputs.
- `sctm/model.py` implements the Gamma–Poisson likelihood, logistic-normal topics, horseshoe hierarchy, batch offsets, time-series covariance and variational guide.
- `sctm/utils.py` implements graph propagation and the Matern-$3/2$ kernel.
- `sctm/layers.py` implements the amortized topic encoders.

Important implementation details are documented in `doc_code.md`. In particular, topic covariance learning is delayed until the loss plateaus, the time-series length scale is effectively fixed to one, and the default library early-stop patience (20) differs from the 30 epochs reported for experiments. The graph normalization code also increments degree by two while adding one identity matrix, an unexplained code-level detail.

### Reproducibility assessment: 4/5

Strengths:

- Open-source Python package with a compact, direct implementation of the paper model.
- Repository provenance pinned to a commit.
- Installation metadata, documentation, simulated data and multiple large tutorial notebooks are present.
- Paper data and reproduction scripts are reported at Zenodo `10.5281/zenodo.8201825`.

Gaps:

- The Zenodo reproduction archive was not acquired into this workspace, so a full paper-wide rerun is not locally assembled.
- No automated tests covering the core STAMP model were indexed.
- Exact experiment arguments are distributed across the paper, supplement and notebooks; package defaults alone do not reproduce every figure.
- The supplementary OCR is readable but has several `??` substitutions in formula-heavy passages; primary Nature HTML and direct code were used for exact equations.
- No end-to-end training benchmark was run during this analysis because the full datasets, legacy environment and paper scripts are substantial.

### Limitations

The authors identify three major method gaps: no direct normal-versus-disease or mutant-versus-wild-type comparative topic model, no ability to inject prior pathways/cell-type knowledge into the modules, and no spatial multi-omics/image/mosaic-data extension (`paper.md:153-165`). More generally, smooth spatial topics can look compelling even when their gene modules are weak, so both views should be inspected. The time-series topics capture smooth population-level programs across discrete stages; they do not establish single-cell lineage or causal developmental transitions.

### Bottom line

STAMP's contribution is the combination of four properties that are rarely available together: spatial awareness, continuous overlapping topics, directly interpretable sparse gene modules and mini-batch scalability. Its strongest evidence comes from repeated agreement between topic maps, anatomy and marker genes across single samples, batches, technologies and developmental time. The code substantially implements the described model, with a few documented default and normalization details that matter for exact reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
