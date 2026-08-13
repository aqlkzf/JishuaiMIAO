---
layout: default
permalink: /paper-atlas/belayer-8097cfa0/
title: "Belayer"
nav: false
wide: true
description: "Belayer 面向具有明确层状结构的空间转录组，例如大脑皮层、皮肤和视网膜。它不把每层内的表达强行视为常数，也不要求整张组织上的表达处处平滑，而是用“分段线性”模型同时表达两类变化：层内沿相对深度连续上升或下降，跨层边界则允许发生不连续跳变。 方法的两个输出彼此依赖：一是每个 spot 的层标签/层边界，二是每个基因在每层中的截距和斜率。斜率大的基因表示层内梯度明显，边界两侧拟合值差大的基因表示离散层转换明显。"
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
      <span>Spatially Variable Genes</span>
      <span>Cell Systems · 2022</span>
    </div>
    <h1>Belayer</h1>
    <p>Belayer: Modeling discrete and continuous spatial variation in gene expression from spatially resolved transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cels.2022.09.002" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Belayer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/raphael-group/belayer" target="_blank" rel="noopener noreferrer" aria-label="Open code for Belayer">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Belayer 方法解读：同时刻画组织层边界与层内表达梯度

### 一句话定位

Belayer 面向具有明确层状结构的空间转录组，例如大脑皮层、皮肤和视网膜。它不把每层内的表达强行视为常数，也不要求整张组织上的表达处处平滑，而是用“分段线性”模型同时表达两类变化：层内沿相对深度连续上升或下降，跨层边界则允许发生不连续跳变。

方法的两个输出彼此依赖：一是每个 spot 的层标签/层边界，二是每个基因在每层中的截距和斜率。斜率大的基因表示层内梯度明显，边界两侧拟合值差大的基因表示离散层转换明显。Belayer 因而既是 layered tissue segmentation 方法，也是带组织几何约束的 spatially varying gene（SVG）排序方法。

### 为什么普通聚类或全局平滑不够

聚类方法擅长找离散区域，却常假定 cluster 内同质；Gaussian-process 或空间自相关方法能找连续变化，却可能把真实层边界平滑掉。在皮层中，细胞组成可在相邻层突变，同时同一层内部仍有位置梯度。Belayer 用每层仅两个参数的线性函数折中：模型比每 spot 独立估计稳定，又比 piecewise constant 保留更多连续结构。

这个优势依赖层状假设。若组织是斑块、分支、环形 niche 或多方向交错结构，强制嵌套层会把真实二维模式压成一条“深度”轴，结果不应解释为通用空间域发现。

### 生成模型：层内线性、层间可跳变

设组织被分为 $L$ 个有序区域 $R_1,\ldots,R_L$。对基因 $g$，Belayer 写成

$$f_g(x,y)=\sum_{\ell=1}^{L}\left(\alpha_{g,\ell}+\beta_{g,\ell}\Phi_\ell(x,y)\right)\mathbf{1}_{(x,y)\in R_\ell}.$$

$\Phi_\ell(x,y)$ 是该位置在第 $\ell$ 层中的相对深度；$\alpha_{g,\ell}$ 是基线，$\beta_{g,\ell}$ 是沿深度的梯度。相邻层各有自己的截距和斜率，因此边界处无需连续。

观测 UMI 用 Poisson 模型：

$$a_{ig}\sim\mathrm{Poisson}\left(C_i\exp(f_g(x_i,y_i))\right),$$

其中 $C_i$ 是 spot 总 UMI，作为 exposure 校正测序深度。源码 `svg.py` 的 `PoissonRegressor` 以 `y/exposure` 为响应、`sample_weight=exposure`，逐基因逐层输出交替排列的 intercept 和 slope。

这不是对原始计数做普通最小二乘。层边界搜索为了计算速度主要在 GLM-PC 上使用 Gaussian segmented-regression cost；边界确定后才对基因计数做 Poisson regression。论文的整体统计模型与实际两阶段近似需要区分。

### 为什么先做 GLM-PCA

直接让约 15,000 个基因参与每个候选边界的回归非常昂贵。Belayer先对计数做 Poisson GLM-PCA，并取 $K=2L$ 个 factors。论文 Proposition 2 给出结构理由：$L$ 段线性函数的列空间秩最多为 $2L$，因此在理想模型下，这些 components 足以保留分段线性结构。

代码固定 `npc=2*nlayers`、Poisson family、penalty 10，并缓存 factors。这个结论是模型内的秩上界，不意味着真实数据必然只需要 $2L$ 个维度；若存在层结构之外的细胞状态、批次或局部 niche，它们可能被压缩或反过来干扰边界。

### 几何核心：把二维弯曲层变成一维深度

若层边界弯曲，笛卡尔 $x$ 或 $y$ 不能代表层深。论文借助 conformal-map 思路，用其实部 $u=\mathrm{Re}\,\Phi$ 作为 harmonic coordinate：

$$\Delta u=0,$$

并在相邻边界上指定不同 Dirichlet 温度。离散到 Visium 六邻接或方格四邻接图后，内部点满足

$$L_Iu_I=-D^Tu_B.$$

代码 `harmonic.interpolate_two_boundaries()` 和 `interpolation_using_list()` 用 graph Laplacian 与 conjugate gradient 求解。边界温度间距由相邻边界的中位 partial Hausdorff distance 设置，使不同层的 depth 单位更接近物理距离。

首层和末层只在一侧有生物学层边界，另一侧的切片外缘未必与层平行。代码因此用单边 heat diffusion 定义深度，并在所有内部点温度达到边界温度的 1% 时停止，避免扩散到稳态后丢失方向。

严格说，本地实现求的是图上的 harmonic interpolation，未显式构造完整复解析函数；“conformal map”是论文的几何解释。非规则采样、缺洞和错误边界都会影响离散 Laplacian 的深度。

### 三条边界识别路径

#### R 模式：近平行但整体旋转的层

对 0° 到 90°、步长 5° 的角度旋转坐标；每个角度把深度轴分成 150 个 bucket，再运行一维 segmented-regression DP。DP 递推是

$$M_{n,\ell}=\min_{n'<n}\left[M_{n',\ell-1}+c(n'+1,n)\right],$$

其中 $c$ 是该区间的多维线性回归误差。选择 $L$ 层总损失最小的角度和 breakpoints。代码随后直接拟合每基因的 Poisson 分段函数，因此 R 是当前 CLI 中最完整的端到端路径之一。

旋转搜索只适合近似平行、可由单一全局方向展开的层。bucket 化提高速度，但边界精度被限制在 bucket 尺度。

#### A 模式：已有近似层边界

输入来自组织学或先验标注的近似边界点。代码补齐规则网格，求 harmonic depth，再沿该 depth 做一维 DP；因此先验只提供大致几何，最终 breakpoints 仍由表达损失调整。A 模式随后也输出层标签和基因系数。

这一路径使用额外人工/组织学信息。论文在非轴对齐 DLPFC 切片的比较中也承认，对完全无监督聚类基线而言这种比较偏向 Belayer。不能把 A 模式更高 ARI 全部归因于表达模型。

#### L 模式：未知的直线边界

L 模式枚举组织外边界点之间的候选直线。首先对两条候选边界之间的区域预计算 Gaussian loss；随后在圆周端点上使用类似 Nussinov RNA folding 的嵌套 DP。状态 $M_{n,m,\ell}$ 表示圆周段 $T_{n,m}$ 内放置 $\ell-1$ 条嵌套边界的最优代价，复杂度为 $O(b^4L)$，其中 $b$ 是外边界候选点数。

论文报告 DLPFC 的 region-cost 预计算在 100 节点集群约需 20 小时，DP 本身约 $5L$ 分钟。本地 CLI 支持分 batch 预计算和加载 loss，但推断出边界后在“fitting expression function”处主动 `raise Exception`；所以当前 L 模式不是端到端基因函数输出。tutorial/手工步骤可以继续，但 CLI 合同必须标为 Partial。

### 层数如何选择

Belayer 需要用户给定或通过不同 $L$ 的 loss curve 观察 elbow。代码没有可靠的自动层数选择器。层数过少会把不同边界合并并让斜率吸收跳变；层数过多会把连续梯度切碎成伪边界。论文比较通常使用已知/人工层数或基于曲线选择，因此不能把层数视为完全数据驱动的输出。

### 从系数得到 SVG

拟合后可按不同问题排序：

- $\max_\ell|\hat\beta_{g,\ell}|$：任一层内梯度最大的基因；
- $|\hat\beta_{g,\ell}|$：指定层的梯度；
- 相邻层边界处两条直线的预测值差：离散跳变；
- piecewise linear 对 piecewise constant 的 likelihood ratio；
- 各层绝对斜率总和。

源码 `compute_discontinuity()` 在相邻层 depth 端点的中点计算两条拟合直线差。斜率排序、LRT 与图形输出主要出现在 tutorial notebook/论文分析流程，而非统一 CLI 命令。基因预筛选也很重要：CLI 使用 `q=0.85, threshold=0`，即保留至少约 15% spots 非零的基因；低表达稀有 marker 可能因此不进入回归。

### 图 1–2：方法图怎样读

图 1从左到右是输入 SRT 与可选近似边界、将每层展开成 vertical strip 的 $\Phi_\ell$、最后输出层与分段直线。关键不是把整张组织旋转一次，而是每层都有自己的相对深度坐标。

图 2a 显示稀疏二维 UMI 经相近深度 binning 后更容易观察趋势；binning 主要用于展示与稳定汇总，不是 Poisson 回归的唯一输入。图 2b 以两条弯曲边界固定温度，等温线成为相对深度。它说明“距离”是沿层结构传播的 harmonic coordinate，而非到某条直线的普通欧氏距离。

### 图 3–4：DLPFC 证据

图 3在 12 个 human DLPFC Visium 切片上比较人工皮层层标签。Donor 1 的近平行切片使用旋转路径，Donor 2/3 的弯曲切片使用近似边界/harmonic path；Belayer 的 ARI 整体高于 BayesSpace、stLearn 和 SCANPY。后两组含边界先验，解释时必须保留监督优势。

图 4以 128 个已知 cortical markers 评价 SVG 排序。sample 151508 中 maximum-slope AUPRC 约 0.032，Layer 3 slope 约 0.116，高于全局方法的对应曲线。NEFH/NEFM 与 HPCAL1 的拟合示例展示：层特异斜率能发现被全局汇总稀释的梯度。低绝对 AUPRC 也提醒已知 marker 集合不完备，排名不是“真实 SVG”二元金标准。

### 图 5–6：跨组织案例

图 5的 day-14 mouse skin wound 有 epidermis、dermis、hypodermis。Belayer 对人工层标注的 ARI 约 0.633，高于 stLearn 约 0.564，并展示 Retnla、Trdn 等层内斜率。720 spots 的小样本说明低参数模型可用，但人工标注和边界先验仍参与评价。

图 6在 mouse somatosensory cortex Slide-seqV2 上用 RCTD cell-type annotation 作为层参照，展示 Belayer 层与 Camk2n1、Cplx2 梯度。这里“ground truth”是另一计算方法的标签而非组织学真值；Slide-seq 稀疏性还需要 notebook 中的 pseudocount/预处理约定。

### 论文与代码的对应边界

Exact 的核心包括：`2L` Poisson GLM-PCA；R 模式 angle sweep 和 bucket DP；A 模式 graph-harmonic depth；L 模式候选边界预计算与 circular DP；逐层 Poisson regression；边界 discontinuity。固定代码 commit 为 `4a60f3c2a6d0725d2f3f4c749cb3576ec04a75f9`。

Partial/Notebook 包括：命令帮助仍提到 X 轴对齐模式，但 parser choices 不含 X 且分支直接异常；帮助中 S/A 名称不一致，实际近似边界分支是 A；L 模式在基因拟合前异常退出；CLI Step 3/4 末尾明确未完成；SVG 多种 ranking 和模型选择依赖 tutorial。论文讨论的 Gaussian-process MAP 正则化是理论联系，当前主流程未实现该先验优化。

Not found 包括完整模拟生成、所有 ARI/AUPRC benchmark 和基线运行脚本、自动层数选择与可安装包环境合同。仓库提供三类示例数据与 notebook，但不等于一条命令重现论文全部图。

### 使用时最重要的限制

1. 只适用于存在全局有序层的组织；局部斑块结构可能被误拟合。
2. A 模式依赖边界先验，错误或不完整的边界会扭曲 harmonic depth。
3. 斜率大小受 depth 尺度影响；partial Hausdorff normalization 使其更可比，但不同平台仍需谨慎。
4. Poisson 模型未显式处理过度离散、零膨胀和空间相关残差。
5. 层数是用户选择，改变 $L$ 会同时改变 GLM-PCA 维数、边界和 SVG 排名。
6. SVG 排名是描述性证据，不能单独证明调控机制或细胞内表达梯度；细胞组成变化也可产生同样图形。
7. L 模式计算昂贵且当前 CLI 不完整，复现需遵循 notebook/集群预计算流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Belayer: Modeling Discrete and Continuous Spatial Variation in Gene Expression from Spatially Resolved Transcriptomics

**Authors**: Cong Ma, Uthsav Chitra, Shirley Zhang, Benjamin J. Raphael
**Journal**: Cell Systems, 2022
**DOI**: [10.1016/j.cels.2022.09.002](https://doi.org/10.1016/j.cels.2022.09.002)
**Code**: [github.com/raphael-group/belayer](https://github.com/raphael-group/belayer) (Zenodo: 10.5281/zenodo.6970061)

---

### Motivation & Novelty

#### Problem

Spatially resolved transcriptomics (SRT) data from layered tissues — such as the cerebral cortex (6 layers), skin (3 layers), and retina (10 layers) — exhibit both **discrete** changes in gene expression at layer boundaries (due to cell type transitions) and **continuous** gradients within layers (due to morphogen signaling and positional identity). Existing computational methods address only one of these phenomena:

- **Clustering methods** (BayesSpace, *Nature Biotechnology* 2021; SpaGCN, *Nature Methods* 2021; stLearn, *bioRxiv* 2020) assign spots to discrete clusters but assume constant expression within each cluster, missing intra-layer gradients.
- **Spatially varying gene (SVG) methods** (SpatialDE, *Nature Methods* 2018; SPARK, *Nature Methods* 2020; HotSpot, *Cell Systems* 2021) model continuous expression variation via Gaussian processes but do not account for sharp discontinuities at layer boundaries.

No existing method jointly models discrete and continuous spatial variation.

#### Unique Contributions

1. **Piecewise linear expression model**: Gene expression is modeled as a piecewise linear function of tissue depth — linear within each layer (capturing gradients via slope $\beta_{g,\ell}$) with allowed discontinuities at boundaries (captured by intercept differences). Only 2 parameters per gene per layer prevents overfitting with sparse SRT data.

2. **Conformal maps for curved tissues**: Uses tools from complex analysis — specifically conformal maps and harmonic functions (the heat equation) — to transform curved layer boundaries into axis-aligned coordinates. This is the first application of conformal maps to SRT analysis.

3. **Dynamic programming algorithms**: Three exact algorithms for different boundary geometries:
   - Rotation sweep for parallel boundaries
   - Harmonic interpolation + 1D DP for supervised boundaries
   - Nussinov-like circular DP for arbitrary linear boundaries (analogous to RNA folding)

4. **GLM-PCA dimensionality reduction with theoretical guarantee**: Shows (Proposition 2) that piecewise linear expression functions are preserved under GLM-PCA with $K = 2L$ components, formalizing the ad hoc dimensionality reduction commonly used in SRT analysis.

---

### Method Overview

Belayer models the expression of each gene $g$ at position $(x,y)$ in an $L$-layered tissue as:

$$f_g(x,y) = \sum_{\ell=1}^{L} (\alpha_{g,\ell} + \beta_{g,\ell} \cdot \Phi_\ell(x,y)) \cdot \mathbf{1}_{(x,y) \in R_\ell}$$

where $\Phi_\ell$ is the relative depth (computed via conformal maps/heat equation) and $\alpha_{g,\ell}, \beta_{g,\ell}$ are the intercept and slope. UMI counts follow a Poisson model: $a_{i,g} \sim \text{Poisson}(C_i \cdot \exp(f_g(\Phi(x_i,y_i))))$.

The pipeline consists of: (1) GLM-PCA dimensionality reduction ($K = 2L$ components), (2) layer boundary identification via dynamic programming (three algorithms for different boundary types), (3) per-gene Poisson regression to fit piecewise linear expression functions, and (4) gene ranking by slope magnitude or boundary discontinuity.

See `doc_method.md` for full algorithmic details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Datasets

| Dataset | Technology | Species/Tissue | Spots | Genes | Ground Truth |
|---|---|---|---|---|---|
| DLPFC (12 slices) | 10X Visium | Human dorsolateral prefrontal cortex | ~4,000/slice | ~15,000 | Manual annotation (6 layers + WM) |
| Skin wound | 10X Visium | Mouse skin (day 14 post-op) | 720 | 32,245 | Manual annotation (3 layers) |
| Somatosensory cortex | Slide-SeqV2 | Mouse somatosensory cortex | 1,642 | 2,349 | RCTD cell type annotations |

#### Layer Identification (ARI)

On DLPFC Donor 1 (4 axis-aligned slices), Belayer achieves noticeably higher ARI compared with BayesSpace, stLearn, SCANPY, and SpaGCN across all samples. On Donors 2-3 (8 slices with curved boundaries using supervised conformal maps), Belayer also outperforms, though this comparison is acknowledged as generous since Belayer uses manual boundary annotations for conformal map construction. On skin wound data, Belayer achieves ARI = 0.633 vs. stLearn's 0.564, and unlike stLearn, predicts spatially continuous layer boundaries consistent with the manual annotation.

#### Spatially Varying Gene Identification (AUPRC)

On DLPFC sample 151508, Belayer's maximum-slope ranking achieves AUPRC = 0.032 vs. SpatialDE (0.017), SPARK (0.029), and HotSpot (0.029) for identifying 128 known cortical marker genes. Layer-specific ranking dramatically improves performance: Layer 3 slope achieves AUPRC = 0.116, suggesting that layer-aware analysis captures biologically meaningful variation missed by global SVG methods.

On somatosensory cortex Slide-SeqV2 data, Belayer achieves AUPRC = 0.06 vs. SpatialDE (0.024), SPARK (0.049), and HotSpot (0.061).

#### Biological Discoveries

- **DLPFC**: *NEFM* (largest Layer 3 slope) is a known cortical marker and neuronal damage biomarker; *HPCAL1* (4th largest) is involved in neuronal signaling but not previously annotated as a cortical marker
- **Skin wound**: *Retnla* (largest hypodermis slope) encodes an effector molecule in wound healing; *Trdn* (largest dermis slope) encodes a muscle contraction protein involved in healing response
- **Somatosensory cortex**: *Camk2n1* (4th largest slope) has known spatiotemporal regulation patterns; *Cplx2* (5th) is linked to cognitive dysfunction in schizophrenia

---

### Reproducibility

**Rating: 3/5** — Partially reproducible

#### Strengths
- Code repository available via Zenodo with example datasets for all three analyses
- Tutorial notebook demonstrates complete workflow for all three datasets
- Dependencies are standard (numpy, scipy, sklearn, glmpca, networkx)

#### Weaknesses
- **CLI pipeline incomplete**: Steps 3-4 are explicitly unfinished in the command-line interface; some post-layer workflows are available only in the tutorial notebook
- **Mode L terminates early**: Code raises Exception before gene fitting in Mode L
- **No evaluation scripts**: ARI, AUPRC computations not provided; simulation code (Splatter-based) absent
- **No automated model selection**: Number of layers $L$ requires manual visual inspection of loss curves
- **Mode X not implemented**: Simplest axis-aligned case raises Exception
- **No requirements.txt or setup.py**: Dependencies must be inferred from imports

#### Practical Notes
- GLM-PCA computation is the slowest step for Mode R/A (~minutes per dataset)
- Mode L requires cluster parallelization for practical use (~20 hours on 100-node cluster for DLPFC)
- Slide-SeqV2 data requires pseudocount=1 (only shown in notebook, not documented in CLI)
- Pre-computed GLM-PCA results are cached to disk, avoiding recomputation across runs

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
