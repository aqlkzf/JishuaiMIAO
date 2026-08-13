---
layout: default
permalink: /paper-atlas/mgw-b1e0d976/
title: "MGW"
nav: false
description: "MGW（Manifold Gromov-Wasserstein）解决的是这样一个问题：两张空间组学切片都带有二维坐标，但一个测量转录本、另一个可能测量代谢物，特征维数、单位和数值几何完全不同，不能直接计算“一个 RNA 点与一个代谢点的特征距离”。MGW 不强行把两种特征相加，而是分别学习“分子特征沿组织空间如何变化”的局部几何，再用 Gromov–Wasserstein（GW）最优传输匹配两个几何结构。"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>MGW</h1>
    <p>Riemannian Metric Learning for Alignment of Spatial Multiomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2025.12.09.693237" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MGW">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/raphael-group/MGW" target="_blank" rel="noopener noreferrer" aria-label="Open code for MGW">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MGW 中文方法解读：用可学习的黎曼几何对齐空间多组学

### 一句话理解

MGW（Manifold Gromov-Wasserstein）解决的是这样一个问题：两张空间组学切片都带有二维坐标，但一个测量转录本、另一个可能测量代谢物，特征维数、单位和数值几何完全不同，不能直接计算“一个 RNA 点与一个代谢点的特征距离”。MGW 不强行把两种特征相加，而是分别学习“分子特征沿组织空间如何变化”的局部几何，再用 Gromov–Wasserstein（GW）最优传输匹配两个几何结构。

它的关键不是普通配准中的旋转、平移或形变参数，而是从每种模态的空间—特征关系中学习一个位置依赖的度量张量。这个度量告诉我们：从某个位置向不同方向移动时，分子表型变化得有多快。两种模态都被“拉回”到共同的物理空间后，MGW 比较各自的测地线距离结构，最终输出软对应矩阵 $P$。

### 为什么现有距离不够

只按空间坐标配准，能限制细胞不要跨越整张切片，却会忽略组织边界和分子状态；只按特征配准，又可能把表达相似但相距很远的区域连接起来。Fused Gromov-Wasserstein（FGW）把空间成本和特征成本写成带权和，但需要调节权重 $\alpha$。更根本的问题是，RNA 与代谢物没有天然的一一维度对应，跨模态特征成本未必有清楚定义。

MGW 的思路是利用空间多组学共有的乘积结构。每个数据集都可写成空间坐标与模态特征的配对：

$$
\mathcal D_M=\{(s^i,X^i)\}_{i=1}^{n},\qquad
\mathcal D_N=\{(t^j,Z^j)\}_{j=1}^{m}.
$$

$s^i,t^j$ 都在二维或三维物理空间 $E$ 中，但 $X^i\in\mathcal M$、$Z^j\in\mathcal N$ 属于不同模态空间。MGW 不直接比较 $X$ 与 $Z$；它分别学习 $E\to\mathcal M$ 和 $E\to\mathcal N$ 的连续映射，再比较两个映射在共同底空间 $E$ 上诱导的几何。

### 算法第一步：把离散测量拟合成神经场

MGW 用两个多层感知机表示神经场：

$$
\varphi_\theta:E\to\mathcal M,\qquad
\psi_\eta:E\to\mathcal N.
$$

它们输入组织坐标，输出该位置的模态特征。训练目标是重建观测特征：

$$
\theta^*=\arg\min_\theta\frac1n\sum_i
\|\varphi_\theta(s^i)-X^i\|_2^2,
$$

另一模态对 $\psi$ 同理。这样，原本离散的“点×特征”矩阵变为可微的连续场。MGW 真正需要神经网络的原因不是做低维嵌入，而是要通过自动微分求空间方向上的雅可比矩阵。

当前代码的 `mgw_preprocess()` 先将二维坐标归一化到单位方形，再对特征做 PCA 或保留原始强度，并做 L2 行归一化。`mgw_align_core()` 为两种模态分别创建 `PhiModel`，默认宽度为 `(128,256,256,128)`、学习率 $10^{-3}$、训练 20,000 步。训练后保存的不是一个共同潜空间，而是两个从空间到各自特征空间的可微函数。

### 算法第二步：由雅可比得到拉回度量

设 $J_\varphi(s)$ 是神经场在位置 $s$ 的雅可比矩阵。其列表示沿不同空间方向移动时，各特征如何变化。MGW 定义拉回度量：

$$
g^M(s)=J_\varphi(s)^\top J_\varphi(s),\qquad
g^N(t)=J_\psi(t)^\top J_\psi(t).
$$

若空间位移为 $v$，局部长度平方为 $v^\top g(s)v$。例如，某方向跨过肿瘤—基质边界时大量基因同时变化，该方向会被度量拉长；沿着分子状态稳定的组织带移动，长度则较短。于是“远近”不再只由像素距离决定，而由模态特征在空间中的变化速度和方向共同决定。

代码中的 `pullback_metric_field()` 使用 `vmap(jacrev(...))` 批量计算雅可比，再用 `einsum('nfd,nfe->nde', J, J)` 得到每个点的 $J^\top J$。实现还用所有位置的典型平均特征值对度量做全局缩放，并加上 $\epsilon I$（默认量级 $10^{-2}$）避免退化。这个稳定化意味着即使神经场在某个方向几乎没有梯度，距离仍保持正定。

### 算法第三步：在离散组织图上近似测地线

连续黎曼测地线是连接两点的最短曲线，但直接求解代价高。MGW 在空间坐标上构建 $k$ 近邻图，把相邻点之间的边权改成局部黎曼弧长，再用全点对最短路近似测地距离。

论文的边长写作：

$$
w_{ij}=\frac12\sqrt{\Delta_{ij}^\top g_i\Delta_{ij}}+
\frac12\sqrt{\Delta_{ij}^\top g_j\Delta_{ij}},
$$

其中 $\Delta_{ij}=s^i-s^j$。对所有边赋权后，Dijkstra 最短路产生模态内距离矩阵 $D_M$ 和 $D_N$。这一步把局部特征梯度积累成全局组织距离：一条欧氏直线若穿过剧烈变化的边界，可能比绕着同一分子区室走更“长”。

当前快速代码采用稍有不同的中点度量近似：先取 $G_m=(G_i+G_j)/2$，再算 $\sqrt{\Delta^\top G_m\Delta}$。它与论文两个平方根取平均并非代数等价，只在网格足够细、度量变化平缓时趋近。实现还将距离按上三角的 99% 分位数归一化，平方后再除以最大值；这对数值稳定很重要，但论文正文没有完整写出。

### 算法第四步：用 GW 匹配内部距离结构

有了两个模态内部的测地距离，MGW 不需要跨模态逐点成本。它寻找耦合矩阵 $P\in\Pi(a,b)$，使第一模态中任意两点的距离与它们在第二模态中对应点的距离尽量一致：

$$
P^*=\arg\min_{P\in\Pi(a,b)}
\sum_{ii'jj'}
\left(d_M(s^i,s^{i'})^2-d_N(t^j,t^{j'})^2\right)^2
P_{ij}P_{i'j'}.
$$

$P_{ij}$ 是点 $i$ 与点 $j$ 之间的软匹配质量。GW 比较的是“点对关系是否保持”，而不是 $X^i$ 和 $Z^j$ 是否能放进同一个坐标系。代码通过 OTT-JAX 的 `QuadraticProblem` 与 `GromovWasserstein` 求解器计算 $P$。之后可做重心投影，例如把代谢物强度投影到 Visium 点上，或把转录特征投影到 MSI 网格上。

论文称 MGW 不需要 FGW 那种空间—特征权重超参数，这个说法应精确理解为：目标函数中没有手工混合两种成本的 $\alpha$。MGW 仍有神经网络宽度、训练步数、$k$NN 邻居数、度量稳定项、熵正则和求解容差等超参数；“hyperparameter-free cost”不等于整个算法完全无超参数。

### 跨模态前为什么还需要 CCA

两种模态中并非所有变化都共享。例如代谢组存在与 RNA 无关的技术或生化方向。若神经场拟合所有特征，拉回度量会被模态特异变化主导。论文因此增加“alignment-informative feature”预处理：先做一个粗配准 $\hat P$，把一侧特征重心投影到另一侧，再用 CCA 寻找最大相关的成分，最后用这些共同变化方向训练 MGW。

代码中的默认 “CCA feeler” 以空间为主做小规模粗 GW，再通过 `project_informative_features()` 完成重心投影和 CCA。对同一模态的时序 Stereo-seq，论文采用联合 PCA 而不是 CCA；Visium–Xenium 使用各自 100 个 PCA 成分再取 40 个 CCA 成分；转录组—代谢组示例常使用 3 个典型相关成分。因此 MGW 的“任意模态”能力仍依赖一个合理假设：两种模态在空间上确实存在可识别的共同结构。

### 四组实验各自证明什么

#### 小鼠胚胎时序 Stereo-seq

作者对齐 E9.5 到 E13.5 的相邻时间点，用迁移距离衡量空间真实性，以细胞类型 AMI 衡量生物一致性。图 3 表明 MGW 在这两者之间取得较好平衡，并能利用分子几何打破单纯空间 GW 在近似对称胚胎上的翻转解。这里是同模态时序对齐，主要检验新成本，而不是最困难的跨模态场景。

#### 结直肠癌 Visium–Xenium

两张切片来自同一供体，但 Visium 测约 18,000 个基因、Xenium 只测 422 个靶基因。图 4用共同基因余弦相似度和归一化迁移距离评估。特征方法可得到更高余弦相似度，却产生约四分之一切片尺度的迁移；空间方法迁移小但表达对应弱。MGW 报告平均余弦相似度 0.671、迁移约 1.4%，体现其目标是兼顾两者，而不是单独最大化某一指标。

#### 肾癌转录组–代谢组

ccRCC 实验对齐 Visium 与 AFADESI-MSI，并把对齐结果送入与 SpatialMeta 相同的 VAE 和评测流程。图 5显示 MGW 在 Moran's I 和 PAS 等空间连续性指标上表现最好。这里的结论受下游 VAE、预处理和三次随机种子共同影响，不能把所有提升都归因于单个 GW 求解步骤。

#### 人脑纹状体转录组–代谢组

作者将 MALDI-MSI 的多巴胺及代谢产物投影到 Parkinson 病患者的 Visium 切片，用已发表的多巴胺相关神经元标签评估。图 6和补充图 S7–S9 报告 AUROC/AUPRC；例如 MGW 对双衍生化多巴胺的 AUROC 为 0.995、AUPRC 为 0.907。它证明投影能恢复已知空间标志，但仍是单个公开切片上的基准，不等同于跨患者临床验证。

### 论文与代码的一致及不一致处

核心数学主链路可以在源码中逐项找到：`models.py` 训练坐标到特征的神经场；`geometry.py` 计算 $J^\top J$、构建 $k$NN 图和 Dijkstra 距离；`mgw.py` 组织预处理、两套度量和成本归一化；`gw.py` 调用 OTT-JAX 输出耦合。因而它不是只有概念图而没有实现的论文。

但当前未固定提交的代码快照与论文附录存在版本边界：

- 论文附录写 SiLU/SWISH，主入口 `PhiModel` 使用 Softplus；SiLU 出现在另一个 `PhiModelFFN` 中。
- 论文边长是两端弧长的平均，快速路径使用平均度量下的一次平方根。
- 论文写 GW 内外容差 $10^{-8}$，主入口默认是 $10^{-7}$。
- 论文写权重衰减 $10^{-4}$ 与 EMA 0.995；默认 `train_phi()` 是普通 Adam+MSE，包含 AdamW、EMA 和 Huber 的 `train_phi_pro()` 并非 `mgw_align_core()` 的默认路径。
- 代码额外执行单位方形坐标归一化、度量全局缩放、距离 99% 分位数及最大值归一化，论文只部分描述这些数值细节。

这些差异不推翻“神经场→拉回度量→图测地线→GW”的方法结构，却会影响精确数值复现。报告结果时应标明使用的是论文参数还是当前仓库默认入口。

### 复现与证据边界

代码版本只能记录为未固定的本地快照，不能编造提交号。仓库提供 Python 模块、实验脚本和大型 notebook，但没有统一锁定的环境文件或一键重现全部图表的入口。运行需要 PyTorch、JAX/OTT-JAX、SciPy、scikit-learn、Scanpy 等，并要自行取得 Stereo-seq、10x CRC、Mendeley 人脑和 Zenodo ccRCC 数据。

论文是 2025 年 12 月发布的 bioRxiv 预印本，尚未经过期刊同行评审。结果数字来自作者基准实验；最稳妥的结论是：MGW 提供了一个有明确几何解释的跨模态空间对齐成本，并在四类公开任务上展示了空间真实性与特征一致性的平衡；其推广性、运行成本和对预处理/版本的敏感性仍需更多独立复现。

### 阅读顺序

先看图 1理解输入—学习几何—输出耦合，再看图 2和算法 1串起四个步骤。随后读附录 C.3–C.6核对架构、测地线、GW 和 CCA。代码层按 `mgw/mgw.py` → `mgw/models.py` → `mgw/geometry.py` → `mgw/gw.py` → `mgw/util.py` 的顺序阅读。最后用图 3–6区分同模态时序、不同技术转录组以及真正的转录组—代谢组任务，避免把所有基准混成同一种验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MGW: Manifold Gromov-Wasserstein

**Full title**: Riemannian Metric Learning for Alignment of Spatial Multiomics
**Authors**: Peter Halmos, Yufan Xia, Benjamin J. Raphael (Princeton)
**Venue**: bioRxiv, December 2025 | DOI: 10.64898/2025.12.09.693237
**Code**: https://github.com/raphael-group/MGW

---

### Motivation & Novelty

#### Biological Problem

Spatial multiomics technologies — Visium, Xenium, Stereo-Seq (transcriptomics), MALDI-MSI/AFADESI-MSI (metabolomics), spatial ATAC-Seq (epigenomics) — each profile a different molecular layer of the same tissue. Studying joint biology requires aligning datasets from different measurement modalities. The core challenge: transcriptomic and metabolomic feature spaces are **incomparable** — different dimensionalities (18,000 genes vs. 200 metabolites), different scales, different geometric structures.

#### Limitations of Existing Approaches

- **STAlign** (*Nature Communications*, 2023): aligns using spatial coordinates alone; ignores feature content entirely
- **PASTE / PASTE2** (*Nature Methods*, 2022; *Genome Research*, 2023): Fused Gromov-Wasserstein (FGW) requires a trade-off hyperparameter α ∈ (0,1) between spatial and feature costs; cannot extend to incomparable modality spaces
- **SCOT / SCOTv2** (*Journal of Computational Biology*, 2022): single-cell GW using Euclidean feature distances; no spatial information; distances from raw expression are not geometry-preserving
- **moscot TranslationProblem** (*Nature*, 2025): flexible OT framework but uses Euclidean feature costs; doesn't learn cost structure
- **SpatialMeta** (*Nature Communications*, 2025): learns joint embeddings after pre-alignment via STAlign (spatial-only); presupposes pre-aligned cells

**Universal limitation**: all existing OT-based multimodal alignment methods use either raw Euclidean feature distances (incomparable across modalities) or spatial distances alone — none learn a geometry-preserving cost from the data.

#### MGW's Contributions

1. **Hyperparameter-free cross-modal alignment**: GW on Riemannian pull-back distances; no α to tune
2. **Modality-specific metric learning**: neural fields learn geometry of each modality space rather than using raw distances
3. **Geometric invariances**: invariant to spatial rigid-body transformations (P2) and feature isometry/scaling (P3); robust to coordinate representation choices
4. **Product-space unification**: exploits the shared Euclidean base E of spatial multiomics to make heterogeneous modality distances comparable

---

### Method Overview

MGW views each spatial omics dataset as a smooth function from physical space E ⊂ ℝ² to a feature space. It:

1. **Learns neural fields** φ: E→M and ψ: E→N — MLPs mapping spatial coordinates to features (MSE loss, 20,000 steps)
2. **Computes Riemannian pullback metrics** g^M(x) = Jφ(x)^T Jφ(x) at each spatial point via automatic differentiation — the Jacobian encodes local feature anisotropy
3. **Builds kNN graphs** weighted by Riemannian arc-lengths → computes all-pairs Riemannian geodesic distances via Dijkstra APSP
4. **Solves GW OT** on these Riemannian distance matrices — matching cells whose modality-specific distance structures are most similar

**Key biological assumption**: spatial gene expression and other molecular modalities vary smoothly and continuously across tissue, making implicit neural field representation biologically appropriate.

**Pre-processing**: For heterogeneous modalities, CCA preprocessing identifies jointly correlated feature subspaces before metric learning. For same-technology data, joint PCA suffices.

For implementation details, see `doc_method.md` and `doc_code.md`.

---

### Evaluation

#### Datasets

| Dataset | Technology | Task |
|---|---|---|
| Stereo-Seq mouse embryo E9.5-13.5 | Spatial transcriptomics | Unimodal spatiotemporal alignment (ablation) |
| 10x CRC (Visium + Xenium) | Two transcriptomic technologies | Cross-platform alignment, same tissue |
| Human striatum/Parkinson's (MALDI-MSI + Visium) | Metabolomics + transcriptomics | Dopamine metabolite projection |
| ccRCC (AFADESI-MSI + Visium) | Metabolomics + transcriptomics | Joint embedding quality |

#### Metrics

- **Migration distance**: average cell displacement under coupling, % of slide extent (↓ better)
- **AMI** (adjusted mutual information): cell-type concordance of projected labels (↑ better)
- **Cosine similarity**: gene expression agreement between aligned cells (↑ better)
- **Moran's I**: spatial autocorrelation of projected features (↑ better)
- **PAS** (proportion of abnormal spots): spatial continuity metric (↓ better)
- **AUROC/AUPRC**: precision of dopamine metabolite localization (↑ better)

#### Key Results

**Stereo-Seq mouse embryo** (Fig. 3, Table 3): MGW achieves the best balance of spatial realism and feature coherence. Migration 7.7–17.2% vs. feature-only GW (43–49%) and spatial-only GW (diverges to 46% for late time points due to spatial symmetry). MGW breaks symmetry by learning the feature metric. AMI 0.338–0.393 vs. spatial GW 0.236–0.345.

**CRC Visium-Xenium** (Fig. 4, Table 4): MGW achieves mean cosine 0.671 with only 1.4% migration — uniquely combining feature-level agreement (comparable to feature-only methods: 0.665–0.744) with spatial realism (comparable to spatial-only PASTE2: 0.1%). All other methods achieve one but not both.

**Striatum dopamine transfer** (Fig. 6, Table 1): MGW AUROC/AUPRC: 0.991/0.846 (3MT), 0.995/0.907 (DA double), 0.994/0.882 (DA single), 0.951/0.455 (DOPAC double). All other methods AUROC ~0.5–0.67 — near-chance. MGW is the only method that correctly localizes biologically meaningful signals.

**ccRCC metabolomics** (Fig. 5, Table 2): MGW achieves highest average Moran's I (0.684 ± 0.013) and lowest PAS (0.380), substantially outperforming SpatialMeta (0.548 / 0.706), which was designed specifically for this task.

---

### Reproducibility

**Rating: 3/5** — code is available and datasets are public, but environment setup is non-trivial and some experimental details differ from code defaults.

**Strengths**:
- GitHub repository with modular Python package (`mgw/`)
- All 4 datasets publicly accessible (Stereo-Seq via MOSTA, 10x Genomics, Mendeley, Zenodo)
- Demo notebooks for two experiments
- Clean API: `mgw_align(A, B, **params)` convenience wrapper

**Weaknesses / Pitfalls**:
- No `pyproject.toml` or `setup.py` — dependencies must be resolved manually. Core deps: PyTorch, OTT-JAX, scipy, sklearn, scanpy, squidpy, anndata
- **Activation mismatch**: paper claims SiLU; code uses Softplus in `PhiModel` (the main pipeline model)
- Geodesic cost normalization (two-step 99th percentile + max) is not documented in paper
- `train_phi_pro` (with EMA, Huber loss, cosine annealing) is available but not the default
- GW solver is JAX-based — requires JAX-compatible GPU; may conflict with PyTorch CUDA device management
- Mouse embryo data requires downloading 5 separate `.h5ad` files from MOSTA database (~10GB each)
- ccRCC evaluation requires SpatialMeta's Zenodo release (accession 14986870) for fair comparison
- No conda/pip environment file provided

**Common pitfalls**:
1. Float64 is set globally (`torch.set_default_dtype(torch.float64)`), which doubles memory usage
2. APSP geodesic computation is O(N² log N) — must downsample to ≤10,000 cells for feasibility
3. CCA feeler may fail if modalities have no joint structure (e.g., very different biological conditions)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
