---
layout: default
permalink: /paper-atlas/cytosignal-bfcda605/
title: "CytoSignal"
nav: false
wide: true
description: "CytoSignal 解决的是空间转录组里的细胞间通讯定位问题：给定每个空间位置的表达量和坐标，方法希望判断某个配体-受体相互作用在哪些具体位置活跃，而不是只在“某类细胞到某类细胞”这种粗粒度层面做推断。论文强调既有方法的两个主要不足：很多单细胞通讯方法没有使用空间邻近信息；很多空间通讯方法依赖预定义细胞群，或者没有为每个 LR pair 在每个空间位置单独给出预测；同时，接触依赖型信号和可扩散配体信号不应使用同一种邻域模型。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Genetics · 2026</span>
    </div>
    <h1>CytoSignal</h1>
    <p>CytoSignal detects locations and dynamics of ligand-receptor signaling at cellular resolution from spatial transcriptomic data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41588-026-02624-9" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CytoSignal">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/welch-lab/CytoSignal" target="_blank" rel="noopener noreferrer" aria-label="Open code for CytoSignal">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

#### 这篇论文要解决什么问题？

CytoSignal 解决的是空间转录组里的细胞间通讯定位问题：给定每个空间位置的表达量和坐标，方法希望判断某个配体-受体相互作用在哪些具体位置活跃，而不是只在“某类细胞到某类细胞”这种粗粒度层面做推断。论文强调既有方法的两个主要不足：很多单细胞通讯方法没有使用空间邻近信息；很多空间通讯方法依赖预定义细胞群，或者没有为每个 LR pair 在每个空间位置单独给出预测；同时，接触依赖型信号和可扩散配体信号不应使用同一种邻域模型（`paper.md:18-24`）。

CytoSignal 的核心思想很直接：如果某个位置正在接收某个信号，那么它附近应该有足够的配体信号，并且该接收位置本身应该有受体表达。于是，方法把每个位置的信号强度写成一个 LRscore，即局部配体量 `L` 和局部受体量 `R` 的乘积（`paper.md:201-249`）。

#### 方法输入和输出

输入包括：

- 空间转录组表达矩阵和每个细胞/spot/bead 的空间坐标。
- 配体-受体数据库，默认使用 CellPhoneDB v2，并区分 diffusion-dependent 与 contact-dependent 互作（`paper.md:279-282`）。
- 如果要做 VeloCytoSignal，还需要 spliced/unspliced RNA velocity 矩阵。
- 如果要做多样本差异信号分析，还需要多个 CytoSignal 对象和样本/细胞层面的协变量。

输出包括：

- 每个空间位置、每个 LR pair 的 LRscore。
- permutation/FDR 后的显著接收位置。
- 发送细胞和接收细胞的空间边。
- 空间梯度、SPARK-X 空间变异排序。
- 与某个信号相关的基因或 TF。
- 多样本差异 LR signaling 结果。
- VeloCytoSignal 的 LRvelo，即信号强度随时间增加或减少的局部估计。

#### 核心流程

```text
表达矩阵 + 空间坐标
        |
        v
构建 CytoSignal 对象 + 加载 LR 数据库
        |
        v
估计 epsilon-ball 半径和 Gaussian sigma
        |
        v
构建两类邻域
  - diffusion-dependent: epsilon-ball + Gaussian 权重
  - contact-dependent: Delaunay triangulation 邻接
        |
        v
邻域插补 ligand / receptor 信号
        |
        v
LRscore = L * R
        |
        v
空间 permutation + null LRscore + smoothing + FDR
        |
        +--> 显著位置 / 发送-接收边 / 梯度 / SPARK-X
        +--> 相关基因或 TF 的 sparse regression
        +--> 多样本 NEBULA 差异分析
        +--> VeloCytoSignal 的 product-rule velocity
```

代码中对应的主流程是 `findNN()`、`imputeLR()`、`inferIntrScore()`，之后用户再显式运行 `inferSignif()` 和可选的 `rankIntrSpatialVar()`（`CytoSignal/R/wrappers.R:36-180`; `CytoSignal/R/analysis.r:449-540`; `CytoSignal/R/analysis.r:755-826`）。

#### 两类邻域：为什么要分开？

论文把每个位置 `i` 的邻域分为两类（`paper.md:210-216`）：

```math
{\mathscr{N}}_i^{DT}
```

表示 Delaunay triangulation 的直接邻居，用于接触依赖型信号；

```math
{\mathscr{N}}_i^\varepsilon
```

表示半径 `r` 内的 epsilon-ball 邻居，用于可扩散配体。

对 diffusion-dependent 互作，配体可以从周围细胞扩散到接收位置，所以 CytoSignal 用 Gaussian kernel 给邻居加权：

```math
w_G(k,i)=\frac{\exp[-d(k,i)^2/(2\sigma^2)]}{\sigma\sqrt{2\pi}}
```

再按发送细胞自己的 epsilon-ball 归一化：

```math
\widetilde{w}_G(k,i)=
\frac{w_G(k,i)}
{\sum_{m\in{\mathscr{N}}_k^\varepsilon}w_G(k,m)}
```

对 contact-dependent 互作，信号只应来自直接接触或近邻位置，所以使用 Delaunay 邻接和均匀权重。论文还推导了 Gaussian sigma 的上界：

```math
\sigma \le \frac{t}{\sqrt{-2\log\varepsilon}}
```

代码中 `inferEpsParams()` 直接实现了这个缩放公式，`findNNGauEB()` 负责 epsilon-ball 和 Gaussian 权重，`findNNDT()` 负责 Delaunay 邻接（`CytoSignal/R/analysis.r:11-195`; `CytoSignal/src/mat_exp.cpp:14-25`）。

需要注意一个实现细节：论文只说明 index cell 被包括在邻域里，并用近似 0 的自距离避免除零；代码默认 `self.weight="auto"` 时，会把自权重设为 `gauss_vec_cpp(1e-9, sigma) * 5` 后再归一化（`CytoSignal/R/analysis.r:72-80`）。这是一个实际参数行为，不能只从论文公式看出来。

#### LRscore 怎样计算？

对 diffusion-dependent 互作，论文定义：

```math
L_i=\sum_{k\in{\mathscr{N}}_i^\varepsilon}l_k\widetilde{w}_G(k,i), \quad R_i=r_i
```

最终：

```math
LRscore_i=L_iR_i
```

对 contact-dependent 互作，`L_i` 来自 Delaunay 邻域，`R_i` 默认仍是接收位置自己的受体表达（`paper.md:219-267`）。

代码实现是矩阵化的：

- `imputeNiche()` 用表达矩阵乘邻接权重矩阵，得到插补后的 ligand/receptor 矩阵（`CytoSignal/R/analysis.r:264-322`）。
- `inferScoreLR()` 归一化插补矩阵、检查有效 LR pair，然后调用 C++ 后端（`CytoSignal/R/LRscores.r:32-98`）。
- `inferScoreLR_cpp()` 对复合物中的 ligand subunits 求和、receptor subunits 求和，再逐位置相乘（`CytoSignal/src/utils_velo.cpp:14-39`）。

另一个重要细节是：当 `norm.method != "none"` 时，代码会在 product backend 之前对 ligand/receptor 矩阵做 Delaunay 平均（`CytoSignal/R/LRscores.r:61-68`）。论文把这一点描述为对每个细胞的 LRscore 在 Delaunay 邻域内取算术平均（`paper.md:270-273`）。两者目标一致，但代码执行位置更具体。

#### 显著性和空间 smoothing

论文的统计检验流程是：打乱细胞空间位置，重复 CytoSignal 的计算流程，得到 null LRscore 分布，再把 observed LRscore 与 null 分布比较，并做 spatial FDR（`paper.md:276-282`）。

代码把这个过程拆成几步：

- `permuteLR()` 根据数据规模决定 permutation 轮数，并存储 ligand/receptor 的 null 矩阵（`CytoSignal/R/LRscores.r:143-223`）。
- `inferNullScoreLR()` 用同一个 LR product backend 计算 null LRscore（`CytoSignal/R/LRscores.r:336-383`）。
- `smoothScoreLR()` 用 Gaussian epsilon-ball graph 同时平滑真实 score 和 null score（`CytoSignal/R/LRscores.r:385-483`）。
- `inferSignif()` 计算 p value，执行 spatialFDR 或 BH FDR，并过滤低读数或显著细胞数不足的互作（`CytoSignal/R/analysis.r:449-540`）。

因此，在实际使用 R package 时，`inferIntrScore()` 只完成 score/null/smoothing，显著位置需要继续调用 `inferSignif()`。

#### 信号相关基因怎么找？

论文希望回答：当某个 LR signaling 在某些空间位置显著时，哪些基因或 TF 与这个信号相关？方法把 LRscore 作为响应变量，同时把候选基因表达和 cluster label 作为解释变量，用 sparse regression 找预测性基因/TF（`paper.md:321-333`）。

代码里有两种入口：

- 如果用户提供 TF 列表，`inferIntrDEG()` 直接用这些 TF 做后续回归。
- 如果没有提供 TF，`gene_select_group_by_permute()` 会在每个互作和 cluster 内比较 permutation-significant 与 insignificant 细胞，做 one-sided Wilcoxon，并取显著基因（`CytoSignal/R/select_gene.R:3-79`）。

之后 `refine_score()` 会去掉低质量基因和组成该 LR pair 的基因，把 cluster label 作为协变量加入模型，并用 `glmnet::cv.glmnet()` 在 alpha 0.5 到 1.0 之间交叉验证，提取非零系数基因和 cluster（`CytoSignal/R/select_gene.R:162-255`; `CytoSignal/R/select_gene.R:456-560`）。

本 workspace 没有论文中用于 Stereo-seq 的具体 TF list、GOrilla 手工设置文件和最终 GO/REVIGO 选择文件；所以这里能验证的是 package 里的通用实现，而不是每张论文图的精确再现脚本。

#### VeloCytoSignal 的思想

VeloCytoSignal 把 RNA velocity 引入 LRscore。论文先写：

```math
S=(L_s+L_u)(R_u+R_s)
```

然后用乘法求导：

```math
\frac{dS}{dt}=
(L_s+L_u)\frac{d(R_u+R_s)}{dt}
+
(R_u+R_s)\frac{d(L_s+L_u)}{dt}
```

也就是说，如果 ligand 或 receptor 的表达正在增加，那么这个 LR interaction 的强度也可能正在增加；反之则可能下降（`paper.md:336-357`）。

代码中 `addVelo()` 接收 spliced/unspliced velocity 矩阵并对齐到 CytoSignal 对象；`imputeVeloLR()` 对 velocity 做邻域插补；`inferIntrVelo()` 分别计算 diffusion/contact 的 LR velocity；C++ 函数 `inferVeloLR_cpp()` 实现的正是 `ligand * receptor_velocity + ligand_velocity * receptor`（`CytoSignal/R/objects.r:790-835`; `CytoSignal/R/LRvelo.r:25-255`; `CytoSignal/src/utils_velo.cpp:44-79`）。

VeloVAE 的训练和速度推断参数在论文 Methods 中描述，但不属于这个 R package 的实现范围。这个 package 消费的是已经算好的 velocity 矩阵。

#### 多样本差异 signaling

多样本扩展的目标是比较不同样本、年龄、疾病状态、细胞类型等协变量下 LR signaling 是否变化。论文使用未归一化/未缩放的 LRscores，把 imputation 得到的小数 score 转成整数型 count-like 响应，然后用 NEBULA 风格的负二项模型做差异分析（`paper.md:375-378`）。

代码中：

- `mergeCytoSignal()` 合并多个 CytoSignal 对象，传播样本 metadata 和每个位置的 cluster/坐标/total counts，并重新计算 diffusion/contact 的 count-like LRscore（`CytoSignal/R/nebula.R:258-453`）。
- `runNEBULA()` 分别对 diffusion 和 contact 的 LRscore 矩阵运行 `nebula::nebula()`，使用 `total_counts` 作为 offset，并对每个协变量输出 logFC、SE、p value 和 FDR（`CytoSignal/R/nebula.R:633-718`）。

论文里的 scDesign3 simulation 生成脚本、PLA benchmark orchestration、runtime/memory benchmark 脚本不在本次克隆的 package 中；这些结果只能作为论文和图像证据，而不是本 workspace 里已验证的可运行代码路径。

#### 评价结果怎么理解？

Figure 2 和 Figure 3 展示了 CytoSignal 在 Slide-seq、Slide-tags 和 Stereo-seq 数据上可以生成每个位置的 LRscore、显著位置、发送/接收边、梯度和相关基因/GO 结果。图像中 diffusion 与 contact 的空间边长度和空间分布明显不同，符合方法设计（`figure_analysis.md`）。

Figure 4 和 Extended Data Figures 1-7 是最重要的验证部分：论文用 Visium HD 邻近切片和 PLA 实验构建 protein-proximity ground truth，并把 CytoSignal 与 NICHES、LIANA+、SpatialDM、stLearn 等方法比较。AUC/AUPRC 图显示 CytoSignal 在多个 cluster 和 LR pair 中表现更稳定；Extended Data Fig. 6/7 还显示 smoothing 和默认参数对性能有贡献（`paper.md:102-131`; `figure_analysis.md`）。

Figure 5 支持多样本差异 signaling：模拟和真实重复数据里的 false-positive/false-negative rate 较低，并在年轻/老年小鼠脑数据中发现免疫相关 signaling 增强（`paper.md:137-154`）。Figure 6 支持 VeloCytoSignal：Alb-FcRn 和 Wnt5a-Antxr1 的 LRvelo 箭头与后续时间点的平均 LRscore 趋势一致（`paper.md:160-177`）。

#### 可复现性和代码匹配

本 workspace 的代码来源是 GitHub `welch-lab/CytoSignal`，commit `cf2a804454f2fc2628476ae74456f9c2f9124131`。核心 R package 对 LRscore、significance、associated genes、LRvelo 和 multisample NEBULA 的实现匹配度是 medium-high，详见 `doc_code.md`。

主要限制是：论文明确说主图 notebook 在另一个 `cytosignal-figure` GitHub 仓库（`paper.md:399-402`），而本 workspace 没有获取该仓库；补充材料也没有 markdown/OCR 版本。因此，主图再现、PLA benchmark、runtime benchmark 和 scDesign3 simulation 只能记录为缺失或外部证据，不能写成已在本 package 中验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

#### Overview

CytoSignal is a Nature Genetics 2026 method for detecting where ligand-receptor (LR) signaling is active in spatial transcriptomic data and how that signaling changes over time. The paper targets a common limitation of cell-cell communication methods: many infer signaling between cell groups rather than at individual tissue positions, and many do not distinguish contact-dependent interactions from diffusible ligand signaling (`paper source/nature_html/paper.md:18-24`).

#### Proposed Method

The central output is an LRscore for every spatial location and every LR pair. For diffusion-dependent interactions, CytoSignal uses an epsilon-ball neighborhood and Gaussian distance weights to aggregate ligand signal, while receptor expression is taken at the receiving location. For contact-dependent interactions, it uses Delaunay-triangulation neighbors. The score is the product of local ligand and receptor signal, followed by Delaunay/Gaussian smoothing, spatial permutation, p value calculation, FDR correction, and optional SPARK-X spatial-variability ranking (`paper source/nature_html/paper.md:201-282`; `CytoSignal/R/analysis.r:11-322`; `CytoSignal/R/LRscores.r:32-483`).

The paper extends this core score in three directions. First, signaling-associated genes/TFs are inferred by selecting genes from significant versus insignificant locations and fitting sparse regression with cluster covariates (`paper source/nature_html/paper.md:321-333`; `CytoSignal/R/select_gene.R:3-560`). Second, VeloCytoSignal combines ligand and receptor RNA velocity using the product rule to estimate whether interaction strength is increasing or decreasing at a location (`paper source/nature_html/paper.md:336-357`; `CytoSignal/R/LRvelo.r:25-255`; `CytoSignal/src/utils_velo.cpp:44-79`). Third, multisample differential signaling is implemented with count-like LRscores and a NEBULA negative-binomial regression wrapper over sample and spot covariates (`paper source/nature_html/paper.md:375-378`; `CytoSignal/R/nebula.R:258-718`).

#### Evaluation

The paper demonstrates the method on Slide-seq, Slide-tags, Stereo-seq, Visium HD, and mouse-brain multisample datasets. Figures 2 and 3 show per-location LRscore maps, significant-location overlays, sender/receiver edge plots, gradients, and associated-gene GO outputs for interactions such as Sema3a-PlexinA4/Nrp1, Efnb1-Epha4, Dll1-Notch1, and Fgf8-Fgfr1 (`paper source/nature_html/paper.md:53-99`; `figure_analysis.md`).

The major validation is paired Visium HD and proximity ligation assay (PLA), where PLA provides spatial protein-proximity measurements for five LR pairs. The figure set shows CytoSignal prediction maps, PLA/binarized PLA panels, and AUC/AUPRC comparisons against NICHES, LIANA+, SpatialDM, and stLearn; Extended Data Figures 1-7 support false-positive/false-negative, distance-distribution, parameter, and smoothing checks (`paper source/nature_html/paper.md:102-131`; `figure_analysis.md`).

For multisample analysis, the paper uses scDesign3 simulations and real replicate checks to show low false-positive and false-negative rates, then identifies age-associated signaling changes in a mouse Parkinson's disease model (`paper source/nature_html/paper.md:137-154`). For temporal dynamics, VeloCytoSignal is shown on Stereo-seq mouse embryo time points with Alb-FcRn and Wnt5a-Antxr1 examples, where LRvelo arrows and observed mean LRscore trajectories align (`paper source/nature_html/paper.md:160-177`).

#### Code-Paper Match

The cloned R package at commit `cf2a804454f2fc2628476ae74456f9c2f9124131` implements the core method with medium-high fidelity. Exact package-backed matches were verified for neighborhood construction, Gaussian kernel parameter inference, LRscore product scoring, permutation/null scoring, score smoothing, significance filtering, SPARK-X ranking, associated-gene regression helpers, LRvelo product-rule scoring, and multisample NEBULA analysis (`doc_code.md`).

Important implementation details include `findNN()` creating Gaussian, Delaunay, and raw slots; `inferIntrScore()` computing scores and null scores but leaving `inferSignif()` and SPARK-X ranking as separate calls; default Gaussian self-weight behavior multiplying the near-zero-distance self weight by 5 in `"auto"` mode; and normalized LRscore computation applying Delaunay averaging before the product backend (`CytoSignal/R/wrappers.R:36-180`; `CytoSignal/R/analysis.r:64-85`; `CytoSignal/R/LRscores.r:61-68`).

#### Reproducibility Notes

The paper states that CytoSignal/VeloCytoSignal are available in the GitHub R package and that main-figure notebooks are in a separate `cytosignal-figure` repository (`paper source/nature_html/paper.md:399-402`). This workspace contains only the package repository, not the figure-notebook repository. Package vignettes provide runnable core workflows for single-dataset and multisample analyses, but local code for PLA benchmark orchestration, runtime/memory benchmarking, and scDesign3 simulation generation was not found in the cloned package.

No supplementary markdown was available, and no supplementary PDF OCR was run in this Author phase. Figure and benchmark claims therefore remain paper/figure evidence unless they are also backed by direct package source lines in `doc_code.md`.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
