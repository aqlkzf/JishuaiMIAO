---
layout: default
permalink: /paper-atlas/spateo-85a978f6/
title: "Spateo"
nav: false
wide: true
description: "Spateo 不是一个单一的轨迹算法，而是一条面向三维、跨时间空间转录组的分析工具链。它先把连续二维切片对齐成三维点云和表面，再在复杂组织内部建立连续坐标轴；随后用空间加权回归估计配体—受体及下游转录调控的局部关联；最后利用不同发育阶段之间的形变学习“morphic vector field”，计算组织迁移、扩张、旋转、弯曲等形态量，并把这些量同基因表达相关联。 论文用 E9.5 和 E11."
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Cell · 2024</span>
    </div>
    <h1>Spateo</h1>
    <p>Spatiotemporal modeling of molecular holograms</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2024.10.011" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Spateo">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/aristoteleo/spateo-release" target="_blank" rel="noopener noreferrer" aria-label="Open code for Spateo">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spateo 方法解读：从连续切片重建三维胚胎，再把形态变化连接到分子模式

### 一句话理解

Spateo 不是一个单一的轨迹算法，而是一条面向三维、跨时间空间转录组的分析工具链。它先把连续二维切片对齐成三维点云和表面，再在复杂组织内部建立连续坐标轴；随后用空间加权回归估计配体—受体及下游转录调控的局部关联；最后利用不同发育阶段之间的形变学习“morphic vector field”，计算组织迁移、扩张、旋转、弯曲等形态量，并把这些量同基因表达相关联。

论文用 E9.5 和 E11.5 全鼠胚、果蝇胚胎以及多个公开空间组学数据展示这条链。核心价值是让数百万细胞的三维结构、空间信号和形态变化进入同一套坐标与分析接口；核心边界是这些步骤大多建立统计对应和候选机制，不是直接观测的细胞谱系或因果调控。

### 1. 四个阶段分别回答什么

#### 阶段一：连续切片如何成为三维“分子全息图”

输入是按顺序采集的二维 ST 切片，每个点包含空间坐标和表达特征。Spateo 为相邻切片估计软对应概率，同时学习刚性变换与高斯过程非刚性形变；对部分重叠区域加入离群成分，避免强迫无对应区域配对。相邻对齐之后，再用多切片联合 refinement 降低顺序累积误差，并可借助外部表面网格做 mesh correction。

输出不是新的表达矩阵，而是每个切片在共同三维坐标系中的坐标、软映射矩阵和形变场。基于这些坐标可以构建点云、表面网格和体素，进行任意角度虚拟切片与器官尺度测量。

#### 阶段二：弯曲、环状或空心结构怎样建立连续轴

传统的 x/y/z 坐标无法表示神经管、ZLI 环或蛇形脊髓中的“内—外”“背—腹”“头—尾”。Spateo 让用户在结构两端指定边界，之后在组织网格或邻接图上求解 Laplace/热方程：

$$
\nabla^2\psi=0,
$$

并以两端固定势值作为边界条件。得到的调和势 $\psi$ 沿复杂结构平滑变化，可作为相对坐标；再把势值等分即可生成层、列和网格。这是“digitization”的含义：不是图像数字化，而是把任意拓扑结构转换成连续、可比较的生物轴。

#### 阶段三：空间信号如何关联到靶基因

MuSIC（Multiscale Spatially-weighted Inference of Cell-cell communication）构造局部回归。对每个目标细胞，膜结合配体使用近距离邻域，分泌配体使用更大邻域；邻居配体表达经距离核加权，并可与目标细胞受体表达组合为 L:R 特征。目标基因计数用 Poisson、负二项或 Gaussian GLM 建模；每个细胞附近的数据权重不同，所以系数也可随空间位置变化。

带宽由校正 AIC 等准则搜索，模型用 IWLS 拟合并检查多重共线性。随后用 TF—gene 模型把可能的细胞间信号连接到细胞内转录调控。它回答的是“哪些已知配体/受体/TF 特征在某个局部区域能解释靶基因变化”，而不是通过干预证明信号链。

#### 阶段四：两个时点间的器官形变如何变成向量场

对齐两个发育阶段后，Spateo 从软对应关系得到空间位移样本，用高斯核/高斯过程平滑成连续三维向量场 $v(x)$。在任意位置都可以预测形态迁移方向，再沿场积分得到候选迁移轨迹。

向量场的 Jacobian $J=\partial v/\partial x$ 支持微分几何分析：

- divergence $\mathrm{tr}(J)$ 表示局部扩张或收缩；
- curl 表示局部旋转；
- acceleration $Jv$ 描述沿流线的速度变化；
- curvature 描述路径弯曲；
- torsion 描述三维路径扭转。

这些量是对重建形变场的数学描述。论文限制部分明确指出，当前 morphometric vector field 不显式建模基因表达动力学或 RNA velocity；把它们统一是未来工作。因此不能把形态场直接叫作转录动力学。

### 2. 对齐模型的直觉与实现

论文把移动切片 A 的点视为产生参考切片 B 数据的混合模型中心。对应概率同时考虑：

1. 变换后空间距离；
2. 基因表达相似度；
3. 可选的细胞类型、图像特征或增殖/凋亡先验；
4. 部分重叠时的均匀离群成分。

整体变换由旋转 $R$ 与平移 $t$ 表示，局部形变由 RBF 核高斯过程表示。变分分布将形变、混合权重、离群概率、噪声和对应变量分块，用 coordinate-ascent variational inference 迭代更新。诱导点和随机小批量降低大规模求解成本。

源码 `alignment/morpho_alignment.py` 的 `morpho_align()` 顺序处理切片列表。每对切片实例化 `Morpho_pairwise`，保存：

- `align_spatial_rigid`：刚性坐标；
- `align_spatial_nonrigid`：非刚性坐标；
- `align_spatial`：按 `mode` 选择最终输出；
- `VecFld_morpho`：形变场参数；
- `P`：软对应矩阵。

`SN-S` 虽在求对应时使用非刚性形变，最终返回刚性结果；`SN-N` 返回非刚性结果。这一区别很重要：不能看到“non-rigid”参与优化就假定输出必然是非刚性坐标。

多切片 refinement 与 mesh correction 是后续步骤，不等于 `morpho_align()` 单次相邻切片循环本身。论文规模与精度结论来自完整分析流程，不能只运行一个入口就认为复现了全鼠胚结果。

### 3. digitization 如何从边界产生生物坐标

二维 `digitization/grid.py::digitize()` 要求用户提供感兴趣轮廓和四个角点。程序先分离两组相反边界，在掩膜内通过 Jacobi 式迭代解热方程，分别得到 layer 与 column 两个势场；每个细胞按像素坐标读取势值，`gridit()` 再将势区间离散为层/列/格。

三维案例使用网格或空间邻接图上的同类势函数。论文对 ZLI 的背—腹轴、头—尾轴和脊髓轴都有人工选择极点、阈值和裁剪：例如 ZLI 邻域使用固定的 x/y/z 距离阈值，先人工识别 Shh 阳性 ZLI，再构建内表面并指定 rostral/caudal 极点。因而 digitization 能适应复杂拓扑，但不是完全无监督；轴方向与结构提取受人工边界、网格质量和邻接关系影响。

### 4. CCI 模型如何读，才不会过度解释

MuSIC 提供 `niche`、`ligand`、`receptor`、`lr` 等模型。对配体模型，可把邻域表达写成

$$
L_i=\sum_k w_{ik}X_k,
$$

膜结合与分泌信号使用不同邻域。以 Poisson 模型为例，靶基因 $Y_i$ 满足

$$
Y_i\sim\mathrm{Poisson}(\lambda_i),\qquad
\log\lambda_i=X_i\beta.
$$

空间权重使每个目标位置的局部样本贡献不同。论文在 ZLI、MHB 和脊髓将轴变基因作为靶标，配体、受体和 TF 还经过表达细胞数过滤；许多距离、带宽和细胞数阈值是数据集专用选择。

模型的系数/显著性受以下因素共同决定：数据库先验、邻域定义、空间自相关、表达稀疏、多重共线性、分布族和带宽。即使预测效果好，也只能支持局部关联和候选信号效应。论文自己将它描述为 possible mechanistic interactions，并在局限中指出现有 GLM 不能表达复杂非线性和高阶组合调控。

### 5. 形态场怎样连接到基因

论文把 E9.5 到 E11.5 心脏的三维重建进行对齐，利用跨阶段形变得到 morphic field。场线预测单个早期区域到晚期区域的迁移，并用体积、表面积、长度、细胞密度、divergence、curl、curvature 等量描述不对称心脏发生。

随后针对每个基因，作者将表达变化与形态特征做回归/相关分析，筛选可能关联形态变化的基因；还对果蝇 CNS 和 midgut 做对应分析。这里“driver”仍是预测候选：同一重建误差会传递到位移、向量场、几何导数和基因排名，且研究没有逐候选进行遗传扰动验证。

本地 `morphofield_gp()` 并不是从零拟合一个独立时间模型；它要求 `adata.uns['VecFld_morpho']` 已由 `morpho_align()` 产生，然后在细胞或网格点上查询高斯核形变速度。当前欧氏核路径可用，`geodist` 查询路径明确抛出 `NotImplementedError`。

### 6. 论文图证据的主线

#### 图 1：工具链地图

图 1 将 Spateo 分为输入/预处理、3D 对齐重建、点云/网格/体素、digitization、CCI、形态度量、backbone、morphic field 和 viewer。它证明 Spateo 是多模块框架，而不是只做对齐的软件。

#### 图 2–3：大规模三维重建与对齐基准

E9.5 的 90 张和 E11.5 的 84 张切片被重建为全鼠胚分子全息图。基准覆盖 MERFISH 半脑（129 切片、930 万细胞）、OpenST 淋巴结（19 切片、约 100 万细胞）、猕猴皮层 Stereo-seq（119 切片、约 3,000 万细胞）、BARSeq 前脑（40 切片、约 120 万细胞）及鼠胚。指标包括有参考坐标时的 MAE 和无真值时的 contextual label consistency。模拟还分别测试非刚性、部分重叠、多切片 refinement 与下采样。

这些结果支持特定数据和参数下的准确性、扩展性与鲁棒性；它们不保证任意组织、任意切片间距或弱表达数据都会正确对齐。部分 benchmark 的“真值”来自模拟形变或外部 atlas，也不是直接的细胞对应真值。

#### 图 4–5：三维轴与信号网络

图 4 在模拟结构和猕猴皮层验证 digitization，并展示 ZLI、MHB、脊髓中的多尺度轴和 CCI 建模。图 5 聚焦 ZLI：Shh/Fgf/Wnt/Bmp/ephrin 等空间信号与局部靶基因/TF 网络被串联。图像表明系数具有空间异质性，但网络边是模型预测与数据库支持的组合，不等价于实验证实的直接调控。

#### 图 6：心脏形态发生

图 6 展示心脏三维结构、形态 backbone、E9.5→E11.5 形变场、迁移路径与几何属性，并将候选基因与不对称形态特征联系。主要证据是跨阶段重建的一致性和已有形态/基因知识的相容性，缺少真实细胞追踪。

#### 图 7：交互式浏览器

Spateo-viewer 将 h5ad 的坐标、表达和注释转换为 VTK/PyVista 数据，提供 Reconstructor 与 Explorer。viewer 是独立仓库/应用，不包含在当前 `spateo-release` 本地代码快照中，因此不能用核心包存在来证明在线服务当前可用。

#### 补图 S1–S10

补图覆盖数据质量与注释、旧数据重建比较、对齐模拟/参数/扩展性、digitization 与 CCI 验证、MHB/脊髓、心脏形态指标、果蝇迁移以及 viewer 跨平台展示。本次刷新已检查本地 163 个 OCR 图像与公式裁片，并以完整图注确认每组图的证据角色。

### 7. 复现性与代码边界

论文声明使用 Spateo 1.1.0；本地 `setup.py` 是 1.1.1。

当前快照覆盖论文核心：

- 对齐：`alignment/morpho_alignment.py`、`methods/morpho_class.py`；
- digitization：`digitization/grid.py` 与 `utils.py`；
- CCI：`tools/CCI_effects_modeling/`；
- 3D 模型与形态场：`tdr/`；
- 多平台 I/O、分割、预处理、绘图与测试。

但完整复现依赖未放在该快照中的外部资源：数百万细胞数据、Spateo-notebooks、Spateo-tutorials、viewer 仓库、参数化分析脚本和较重的 3D/GPU 依赖。论文数据页面与在线 viewer 的当前可达性也不应由本地文件推断。

源码还有具体限制：`morphofield_gp()` 的 geodesic kernel 未实现；`compute_torsion()` 当前引用未定义的 `eps`，在曲率接近零的分支会触发错误；许多高级模块依赖 PyVista、VTK、Torch/JAX、MPI 或额外数据库。测试目录主要覆盖配置、I/O、分割与预处理，不能替代全流程千万细胞复现。

### 8. 论文明确写出的局限

1. 三维 ST 仍昂贵，限制大规模普及；
2. 当前空间加权回归是线性/广义线性框架，不能充分表示非线性、高阶 L:R 和组合调控；
3. 当前 morphometric vector field 不显式联合基因表达动力学或 RNA velocity。

此外，从实现和分析流程还能看出：连续切片质量、人工极点/裁剪、细胞注释、数据库先验、网格构造与正则参数都会逐级影响结论。结果最适合被表述为三维重建、局部关联与候选形态机制，而非直接的因果或谱系证明。

### 9. 最安全的结论

Spateo 的独特贡献不是某一个公式，而是把三维对齐、拓扑感知坐标、局部信号回归和形态向量场串成可扩展工具链，并在全胚尺度展示其价值。使用时应把每一级输出的证据类型分开：对齐是概率对应；digitization 是边界条件决定的相对坐标；CCI 是空间加权关联；morphic field 是跨阶段形变模型；基因排名是候选机制。保留这些边界，才能避免把“分子全息图”误读成直接成像的四维细胞谱系。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spateo: Spatiotemporal Modeling of Molecular Holograms

**Paper**: Spatiotemporal modeling of molecular holograms
**Authors**: Xiaojie Qiu, Daniel Y. Zhu, Yifan Lu, Jiajun Yao, Zehua Jing, et al.
**Journal**: Cell (2024)
**DOI**: 10.1016/j.cell.2024.10.011
**Received**: December 9, 2022 | **Revised**: May 29, 2024 | **Accepted**: October 8, 2024 | **Published**: November 11, 2024 | **Corrected online**: February 14, 2025
**Code**: https://github.com/aristoteleo/spateo-release (v1.1.0)
**Data**: http://spateodata.aristoteleo.com/
**Viewer**: http://viewer.spateo.aristoteleo.com/

---

### Motivation & Background

#### The Problem
Existing spatial transcriptomics (ST) methods are fundamentally 2D, yet tissues, organs, and embryos are inherently 3D entities with complex spatial organization. Serial sectioning of tissues results in critical loss of relative coordinate information between sections. Furthermore, no unified computational framework existed for performing 3D reconstruction combined with spatiotemporal analysis at whole-embryo scale with single-cell resolution.

Key challenges include:
1. **3D Reconstruction**: Tissue deformation, rotation, missing regions, and partial overlap between consecutive sections prevent accurate alignment at scale
2. **Spatial Digitization**: Existing methods (e.g., Belayer) limited to 2D shapes, cannot handle complex 3D structures like hollow neural tubes or serpentine spinal cords
3. **Cell-Cell Interaction (CCI)**: Current tools either ignore downstream effects or provide only global estimates, not cell-specific predictions in 3D
4. **Spatiotemporal Dynamics**: No framework to predict 4D morphogenesis (cell migration over time) and connect it to molecular drivers

#### Existing Approaches Compared
| Method | Year | Journal | Limitation |
|--------|------|---------|-----------|
| **PASTE** | 2022 | Nat Methods | Pairwise OT-based alignment; no partial overlap support; sequential error accumulation |
| **PASTE2** | 2023 | Genome Res | Partial alignment extension but still OT-based (expensive) |
| **moscot** | 2023 | bioRxiv (later Nat Methods) | OT-based spatial mapping; not designed for whole-embryo scale |
| **SLAT/scSLAT** | 2023 | Nat Commun | Graph-based alignment; limited scalability |
| **STalign** | 2023 | Nat Commun | Diffeomorphic alignment; computationally intensive |
| **SPACEL** | 2023 | Nat Commun | DL-based 3D reconstruction; requires cell-type labels |
| **sc3D** | 2023 | Nat Genet | 3D reconstruction from Slide-seq; requires extensive annotations |
| **Belayer** | 2022 | Cell Syst | Spatial digitization limited to 2D |
| **CellChat** | 2021 | Nat Commun | CCI inference not 3D-aware |
| **COMMOT** | 2023 | Nat Methods | CCI via OT; no intracellular signaling modeling |
| **ncem** | 2023 | Nat Biotechnol | Spatial graphs for CCI; global predictions only |

#### Novelty
Spateo is the **first unified framework** combining:
1. **Scalable partial non-rigid 3D alignment** using Gaussian processes (GP), variational Bayesian inference (VBI), and stochastic variational inference (SVI) with Nystrom approximation
2. **3D-aware spatial digitization** via Laplace equation solution ($\nabla^2 \psi = 0$) to create coordinate systems on arbitrary 3D structures
3. **Cell-specific spatially-weighted CCI modeling** via generalized linear models (GLM) with six kernel options and TF-target integration
4. **Morphometric vector fields** with analytical differential geometry (divergence, curl, acceleration, curvature, torsion) to connect morphogenesis with molecular dynamics

Demonstrated on:
- Whole mouse embryos (E9.5: 90 slices, 884,114 cells; E11.5: 84 slices, 6,319,756 cells) using Stereo-seq
- Drosophila embryos (S11, S13) for germband retraction analysis
- Multiple public datasets across 10+ ST platforms (STARMap Plus, BARseq, Slide-seq, MERFISH, OpenST, Visium, CosMx, Seq-Scope)

---

### Method Overview

#### Four-Stage Pipeline

##### Stage 1: 3D Alignment & Reconstruction

**Probabilistic Model**:
- Generative framework: slice A (model points) generates slice B (data points) through transformation $\tau$
- Two-component mixture: inliers (probability $\gamma$) + outliers (probability $1-\gamma$)
- Inlier generation: spot $s_n^B$ generated from transformed $s_m^A$ with weighted probability $\alpha_m$:
  $$\mathbf{x}_n^B \sim \mathcal{N}(\mathbf{x}_n^B | \tau(\mathbf{x}_m^A), \sigma^2 \mathbf{I}_D)$$
  $$\mathbf{z}_n^B \sim p(\mathbf{z}_n^B | \mathbf{z}_m^A)$$
- Generative probability considers gene expression similarity, spatial proximity, cell proliferation/apoptosis scores, and cell-type labels

**Transformation Model**:
$$\tau(\mathbf{x}) = \mathcal{R}(\mathbf{x}) + \mathbf{f}(\mathbf{x})$$
- Rigid component: $\mathcal{R}(\mathbf{x}) = \mathbf{x}\bar{\mathbf{R}}^{\top} + \mathbf{t}$ (rotation + translation)
- Non-rigid component: $\mathbf{f}(\mathbf{x}) = \mathcal{GP}(\mu, k)$ with squared exponential kernel
  $$k(\mathbf{x}, \mathbf{x}') = \exp(-\beta \|\mathbf{x} - \mathbf{x}'\|^2)$$

**Optimization**:
- **Mean-field variational inference**: Factorized posterior $q(\mathbf{C}, \mathbf{E}, \mathbf{f}) = q(\mathbf{C})q(\mathbf{E})q(\mathbf{f})$
- **Coordinate Ascent Variational Inference (CAVI)**: Iteratively update $q(\mathbf{C})$, $q(\mathbf{E})$, $q(\mathbf{f})$ until ELBO convergence
- **Nystrom approximation**: Reduce GP complexity from $O(N^3)$ to $O(NK^2)$ using $K$ inducing points
- **Stochastic Variational Inference (SVI)**: Minibatch updates for scalability to 8M+ cells

**Multi-slice Refinement**:
- After pairwise alignment of all consecutive slices, jointly refine using left/right neighborhood slices
- Reduces sequential error accumulation (critical for 90+ slices)

**Mesh Correction**:
- Incorporates external reference shape (e.g., Allen Mouse Brain CCF v3) using Markov Random Field (MRF) discrete optimization
- Enhances 3D reconstruction accuracy when anatomical priors available

**Output Formats**:
1. Point cloud model from aligned cells
2. Surface mesh via marching cube algorithm
3. Voxel model by voxelization
4. Virtual slicing at arbitrary angles

---

##### Stage 2: Spatial Domain Digitization

**Method**: Graph potential function approach solving Laplace equation:
$$\nabla^2 \psi = 0$$
with Dirichlet boundary conditions, solved via Jacobi iteration.

**Applications**:
- **Multi-scale axes**: Define arbitrary coordinate systems (e.g., dorsal-ventral, rostral-caudal, inner-outer) on complex 2D/3D structures
- **Subcellular resolution**: Nucleus vs. cytoplasm enrichment analysis
- **Tissue level**: Layer-wise digitization (e.g., cortical layers, spinal cord D-V axis)
- **Organ level**: Whole-organ gradient characterization (e.g., ZLI, MHB, heart chambers)

**Advantages over Belayer**:
- Generalizes to arbitrary 3D topologies (hollow tubes, serpentine structures)
- No limitation to simple 2D shapes

---

##### Stage 3: Cell-Cell Interaction (CCI) Modeling

**Framework**: Spatially-weighted generalized linear models (GLM) for L:R interactions.

**Three Model Types**:
1. **Ligand model**: Predict ligand expression from local niche
2. **L:R model**: Predict receptor-mediated effects on target genes
3. **Niche model**: Joint ligand-receptor niche effects

**Core Equation** (Poisson regression):
$$\log(\mu_{i,g}) = \beta_0 + \sum_{l=1}^L \beta_l \cdot \text{SpatialKernel}_l(\mathbf{x}_i) \cdot E_{l}(\mathbf{x}_i) + \text{Ridge}$$
where:
- $\mu_{i,g}$: Expected expression of target gene $g$ in cell $i$
- $E_l(\mathbf{x}_i)$: Spatially-weighted ligand expression at cell $i$
- $\text{SpatialKernel}$: Six options (Gaussian, Epanechnikov, uniform, triangular, cosine, quartic)

**Ridge Regularization**:
$$\text{Loss} = -\log\mathcal{L} + \lambda \sum_{l=1}^L \beta_l^2$$

**TF-Gene Models**: Extend to intracellular signaling by modeling:
$$\text{Target}_g \sim \text{Ligand}_l + \text{TF}_1 + \ldots + \text{TF}_k$$
to identify transcription factors mediating L:R effects.

**Spatial Kernel Functions**:
- Gaussian: $K(d) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp(-\frac{d^2}{2\sigma^2})$
- Epanechnikov: $K(d) = \frac{3}{4}(1 - (\frac{d}{h})^2)$ for $d \leq h$
- Uniform, triangular, cosine, quartic variants

**Outputs**:
- Cell-specific L:R interaction effects (not global averages)
- Region-specific signaling landscapes (e.g., p2 vs. p3 in ZLI)
- TF regulators of ligands and downstream targets

---

##### Stage 4: Morphometric Vector Fields

**Concept**: Predict 4D cell migration paths from multi-timepoint 3D reconstructions.

**Two Approaches**:

1. **GP-based Analytical Vector Field** (same framework as 3D alignment):
   - Map cells from time $t_1$ to $t_2$ via $\tau(\mathbf{x})$
   - Directly returns analytical vector field from GP posterior
   - Smooth, differentiable

2. **SparseVFC** (from Dynamo):
   - Learns vector field from discrete optimal transport mappings
   - Alternative when analytical solution unavailable

**Differential Geometry Quantities** (all analytically derived from $\tau$):

| Quantity | Formula | Biological Meaning |
|----------|---------|-------------------|
| **Jacobian** | $J = \nabla \mathbf{v}$ | How migration along one axis influences other axes |
| **Divergence** | $\text{div}(\mathbf{v}) = \nabla \cdot \mathbf{v}$ | Tissue expansion ($>0$) or shrinkage ($<0$) |
| **Curl** | $\text{curl}(\mathbf{v}) = \nabla \times \mathbf{v}$ | Degree of rotational movement |
| **Acceleration** | $\mathbf{a} = \frac{d\mathbf{v}}{dt}$ | Rate of change in migration velocity |
| **Curvature** | $\kappa = \frac{\|\mathbf{v} \times \mathbf{a}\|}{\|\mathbf{v}\|^3}$ | Degree of path bending |
| **Torsion** | $\tau_{\text{torsion}} = \frac{(\mathbf{v} \times \mathbf{a}) \cdot \dot{\mathbf{a}}}{\|\mathbf{v} \times \mathbf{a}\|^2}$ | Degree of 3D twisting |

**Morphogenic Gene Identification**:
- Compute Spearman/Pearson correlation between gene expression and each differential geometry quantity
- Genes with high correlation ($|\rho| > \text{threshold}$, FDR $< 0.05$) = "morphogenic genes"
- Gene set enrichment analysis (GSEA) for pathway identification

---

### Key Findings

#### 1. ZLI (Zona Limitans Intrathalamica) Signaling Organization (E11.5)

**Digitization**:
- Dorsal-ventral (D-V) axis: Captures roof plate -> ZLI -> basal plate gradient
- Rostral-caudal (R-C) axis: Reveals p2 (thalamus) -> ZLI -> p3 (prethalamus) domains

**Gene Expression Polarity**:
- **p2 region**: Wnt family ligands (Wnt3a, Wnt8b, Wnt1) except Wnt7b
- **p3 region**: Wnt7b, Sema5b, Notch-like ligands (Dlk1, Dll2, Dll3), TF Foxd1
- **ZLI**: Shh (does NOT extend to roof plate where Fgf8 is expressed)
- **Roof plate**: Fgf8 effects on Sufu and Gli3 (Shh-repressor complex) -- potential mechanism controlling ZLI dorsal extension

**CCI Landscape**:
- **Bmp/Wnt -> Stemness factors in p2**: Id1, Tead1, Mycn, Otx1, Cited2, Ybx1 (pluripotency maintenance genes)
- **TF-gene modeling**: Sox2 -> Bmps; Smad4 (Bmp transducer) -> Id1
- **Feedback regulation**: Wnts -> Axin2, Nkd1 (negative feedback regulators) in p2
- **Basal plate**: Gdf11 -> early neuronal markers (Dcx, Thsd7a)
- **Validated interactions**: Consistent with perturbation studies (Guglielmi et al. 2021, Hayward et al. 2008, Park et al. 2015)

#### 2. Midbrain-Hindbrain Boundary (MHB) & Spinal Cord

**MHB**:
- Fgf family (Fgf8, Fgf17) enriched in boundary neuroectoderm
- Ptn effects on synaptic plasticity genes (Gap43), axon growth genes (Rtn1)
- Cdh2 region-exclusive effects on Tox, Abcc4 (validated by previous studies)

**Spinal Cord** (D-V axis digitization):
- **TF gradients**: Lhx family (Lhx1, Lhx5, Lhx9), Dbx1, Gbx2 (all critical for spinal development)
- **Slit2 enrichment**: Dorsal end
- **TF-gene prediction**: Lhx factors + homeobox genes -> Slit2 (analogous to cranial Slit2 regulation)
- **Slit2 targets**: Adhesion and cytoskeletal dynamics genes (consistent with axon guidance role)

#### 3. Heart Asymmetrical Organogenesis (E9.5 -> E11.5)

**3D Reconstruction**:
- Five major structures: LV, RV, OFT, RA, LA reconstructed at both timepoints
- E9.5 heart: 74 slices; E11.5 heart: 64 slices
- High structural similarity between E9.5 and E11.5 (similarity score $>0.9$)
- Dramatic increase in surface area, volume, cell number; constant cell density

**Morphometric Vector Field Analysis**:

| Structure | Highest Differential Geometry Feature | Interpretation |
|-----------|--------------------------------------|----------------|
| **RA (right atrium)** | Acceleration | Rapid expansion (2nd heart field origin, late integration) |
| **RV & LA** | Curl | High rotational movement during formation |
| **LV (left ventricle)** | Lowest divergence | Mature, limited differentiation capacity (1st heart field) |

**Morphogenic Genes Identified** (correlation with curl/acceleration/divergence):
- **Migration markers**: Tbx2, Bmp2 (known cell migration factors)
- **AV canal development**: Multiple genes critical for atrioventricular canal maturation
- **Heart tube development**: Tdgf1 (anterior heart tube)
- **Chamber-specific**:
  - Angpt1: Right atrial morphogenesis
  - Pitx2: Left-right asymmetry formation
  - Hey2: Ventricular formation
- **GSEA terms**: Muscle cell migration, cardiac atrium morphogenesis, cardiac RV morphogenesis

**Asymmetry Hypothesis**:
- RA/RV/LA (2nd heart field origin) show high curl/acceleration due to late integration and progenitor state
- LV (1st heart field origin) mature, low divergence reflects limited contribution to other structures

#### 4. Drosophila Germband Retraction (S11 -> S13)

**Organogenesis Modes**:
1. **Migration/movement**: CNS, amnioserosa, muscle
2. **Fusion/convergence**: Midgut (multiple pieces fuse)
3. **Expansion**: Hindgut, salivary gland (cell growth-driven)

**Backbone Analysis** (A-P axis principal curve):
- **Head**: Dfd
- **Thorax**: Scr, Antp
- **Abdomen**: Ubx, Abd-A, Abd-B (classic Hox expression pattern)
- Interpolated expression matches BDGP in situ database

**Morphometric Vector Field**:
- **High curl/acceleration at tail**: Strong germband contraction
- **Morphogenic genes**: peb/hnt, cad, Abd-B, otp, CG2930, CG31463
- **GO enrichment**: Germband extension, embryonic hindgut morphogenesis

**Cell Co-localization**:
- Muscle strongly co-localizes with midgut and hindgut (not neural cells)
- Suggests critical role of muscle in hindgut/midgut migration

**Curl-correlated genes**: Neo, Fkh, COX8 (hindgut/midgut migration and germband retraction)

---

### Benchmarking & Validation

#### Quantitative Benchmarks

**Datasets Tested**:

| # | Dataset | Platform | Slices | Cells | Ground Truth |
|---|---------|----------|--------|-------|-------------|
| 1 | Mouse hemibrain | MERFISH | 129 | 9.3M | Allen CCF v3 |
| 2 | Human metastatic lymph node | OpenST | 19 | 1M | None (CLC score) |
| 3 | Macaque cortex | Stereo-seq | 119 | 30M | None (CLC score) |
| 4 | Mouse forebrain | BARseq | 40 | 1.2M | Allen CCF v3 |
| 5 | Mouse embryo E9.5 | Stereo-seq | 90 | 884,114 | None (CLC score) |
| 6 | Mouse embryo E11.5 | Stereo-seq | 84 | 6,319,756 | None (CLC score) |

**Metrics**:
- **Mean Absolute Error (MAE)**: Distance from ground-truth Allen CCF v3 (for MERFISH, BARseq)
- **Contextual Label Consistency (CLC) Score**: Measures both label and spatial consistency of cell-type mapping across slices (for datasets without ground truth)

**Statistical Results** (Spateo vs. alternatives, from Figure 3 bar plots):

| Dataset | Comparison | p-value | Metric |
|---------|-----------|---------|--------|
| MERFISH hemibrain (129 slices, 9.3M cells) | Spateo vs. PASTE | $p = 8.2 \times 10^{-3}$ | Pairwise MAE |
| OpenST lymph node (19 slices, 1M cells) | Spateo vs. PASTE2 | $p = 2.0 \times 10^{-20}$ | CLC score |
| OpenST lymph node (19 slices, 1M cells) | Spateo vs. SLAT | $p = 8.3 \times 10^{-20}$ | CLC score |
| Macaque cortex (119 slices, 30M cells) | Spateo vs. SLAT | $p = 8 \times 10^{-77}$ | CLC score |

Spateo consistently achieved the **lowest MAE** (for datasets with ground truth) and **highest CLC score** (for datasets without ground truth) across all benchmarked datasets.

#### Simulation Benchmarks (STARMap Plus)

Three simulation types:
1. **Non-rigid distortion**: Spateo maintains low MAE across distortion levels; PASTE/SLAT fail at higher distortions
2. **Partial alignment** (ratio crop): Spateo correctly aligns overlapping regions; SPACEL/PASTE2/STAlign show misalignment
3. **Multi-slice refinement**: Spateo accuracy improves with more slices; other methods accumulate errors

#### Computational Efficiency & Scalability

Benchmarked on NVIDIA A100 (40 GB VRAM) with CUDA 12.5 driver.

| Method | GPU/CPU | Runtime Scaling | Memory Scaling | Notes |
|--------|---------|----------------|----------------|-------|
| **Spateo** | GPU (PyTorch 2.0) | Sub-linear; under 1 hour for large datasets | Sub-linear | Scales to 500K+ cells per slice pair |
| **PASTE** | GPU (PyTorch 2.0) | Rapid growth; >>1 hour | High | Requires downsampling to 10K cells |
| **PASTE2** | CPU only (no GPU version) | Very slow; hours per slice pair | High | Requires downsampling to 5K cells |
| **moscot** | GPU (JAX 0.4.13) | Moderate growth | Moderate | Requires downsampling to 20K cells |
| **SLAT** | GPU (PyTorch 2.0) | Moderate growth | Moderate | Requires downsampling to 20K cells |
| **STalign** | GPU (PyTorch 2.0) | Moderate growth | Moderate | -- |
| **SPACEL** | CPU (no GPU for alignment) | Slow | Moderate | Requires downsampling to 20K cells |

Key observations from Figure 3F:
- Spateo processes large datasets (hundreds of thousands of cells) in **under 1 hour** on A100 40GB
- OT-based methods (PASTE, PASTE2, moscot) require aggressive downsampling (5K--20K cells/slice) due to memory and runtime limitations, while Spateo operates on full-resolution data
- PASTE2 is particularly slow due to its brute-force overlap ratio search, spending hours on a single slice pair with only a few thousand cells

Spateo achieves **10--20x speedup** via SVI + Nystrom approximation.

#### CCI Model Validation (CosMx NSCLC dataset)

**Benchmark**: Predict target gene expression from L:R interactions.

**Performance**:
- Spearman/Pearson $R^2 > 0.8$ consistently (best among methods)
- More consistent results for same-family ligands/receptors (e.g., WNT family) vs. global models
- Robust across multiple FOVs and across datasets from different platforms (Visium, MERFISH, Seq-Scope, OpenST, Slide-Tags)

**Comparison**: Outperforms COMMOT (Nat Methods 2023), ncem (Nat Biotechnol 2023) in prediction accuracy and spatial consistency.

#### Digitization Validation

**Simulation**: Creates uniform "layers" and "columns" in complex topologies (superior to Belayer, Cell Syst 2022).

**Real data** (MERFISH mouse brain):
- Recapitulates cortical layers for laminar neuron enrichment
- Higher accuracy than Belayer in layer assignment

**Multi-scale gradients**:
- Identifies rostral-caudal (R-C) markers in mouse brain: Cntnap2, Epha7, Nr2f1 (validated markers)
- Subcellular: Nucleus vs. cytoplasm enrichment (e.g., ribosomal proteins vs. nuclear TFs)

---

### Spateo-viewer: Interactive 3D Browser

**Architecture**:
- Web-based application ("Google Earth for ST")
- Technology stack: VTK (Visualization Toolkit), PyVista, Vuetify, trame
- Data format conversion: h5ad (single-cell genomics) -> vtk (computer vision)

**Two Main Modules**:

1. **Reconstructor**:
   - Interactive slice alignment
   - 3D point cloud -> surface mesh generation
   - Domain cleanup and organ-specific mesh reconstruction
   - Export to AnnData for downstream analysis

2. **Explorer**:
   - 3D volumetric analysis (length, width, height, surface area, cell density)
   - 4D morphogenesis animation (multi-timepoint data)
   - Visualization in 2D/3D physical space or reduced expression space (UMAP)
   - Gene expression overlay on 3D structures

**Features**:
- Lightweight vtk files for fast rendering
- Modular and extendable (users can add custom analysis modules)
- Freely accessible at http://viewer.spateo.aristoteleo.com/

---

### Software Ecosystem & Integration

#### Spateo Package Components

1. **Data Preprocessing**:
   - Flexible API for multiple ST formats (Stereo-seq, Visium, MERFISH, Slide-seq, etc.)
   - Single-cell segmentation
   - Basic 3D exploration

2. **Core Functions**:
   - 3D alignment (rigid, non-rigid, partial, multi-slice refinement, mesh correction)
   - Digitization (2D/3D arbitrary axes)
   - CCI modeling (ligand, L:R, niche models + TF-gene models)
   - Morphometric vector fields (GP-based or SparseVFC)
   - Differential geometry (divergence, curl, acceleration, curvature, torsion)
   - Spatial domain detection
   - Spatially variable gene detection
   - 3D interpolation (MLP-based or GP-based)

3. **Spateo-viewer**:
   - Web browser for interactive 3D visualization
   - Reconstructor and Explorer modules

#### Integration with Aristotle Ecosystem

- **Dynamo** (v1.4.1): RNA velocity vector field analysis in expression space
- **Dynast**: Dynamic analysis of single-cell transcriptomics (upcoming)
- Unified software ecosystem for predictive single-cell genomics

#### Companion Resources

- **Code**: https://github.com/aristoteleo/spateo-release (v1.1.0)
- **Notebooks**: https://github.com/aristoteleo/Spateo-notebooks (reproduce all figures)
- **Tutorials**: https://github.com/aristoteleo/Spateo-tutorials
- **Documentation**: https://spateo-release.readthedocs.io/
- **Data repository**: http://spateodata.aristoteleo.com/
- **Viewer**: http://viewer.spateo.aristoteleo.com/
- **Spateo-viewer code**: https://github.com/aristoteleo/spateo-viewer

---

### Reproducibility Assessment

**Rating**: 4/5

#### Strengths
1. **Code Availability**:
   - Well-organized Python package on GitHub (v1.1.0)
   - Comprehensive API documentation
   - Modular architecture for extensibility

2. **Data Availability**:
   - Processed data at http://spateodata.aristoteleo.com/
   - Raw data referenced from Cheng et al. 2024 (bioRxiv)
   - Drosophila data (S11, S13) included in package via `spateo.sample_data.drosophila()`
   - All public datasets with DOIs/accessions provided

3. **Documentation**:
   - Extensive tutorials and workflows at readthedocs
   - Separate notebook repositories for figure reproduction
   - Method details in STAR Methods section
   - Interactive Spateo-viewer tutorials

4. **Methodological Transparency**:
   - Full mathematical derivations in paper + supplement
   - Algorithm pseudocode available
   - Hyperparameter robustness analysis (Figure S4E)

#### Limitations
1. **Heavy Dependencies**:
   - PyTorch, GPyTorch, POT (Python Optimal Transport), PyVista, VTK, trame, kornia, opencv-python
   - Installation complexity may be barrier for some users
   - GPU required for large-scale analyses (but CPU fallback available)

2. **Computational Resources**:
   - Large GPU memory needed for whole-embryo datasets (benchmarked on A100 40GB VRAM)
   - Some analyses require significant RAM (though much less than PASTE)

3. **Parameter Tuning**:
   - Multiple hyperparameters (kernel bandwidth, inducing points $K$, ridge $\lambda$, etc.)
   - Default values provided but optimal settings may vary by dataset

4. **Experimental Protocol**:
   - SBFI (Serial Block-Face Imaging) methodology described in separate paper (Cheng et al. 2024)
   - Some users may not have access to similar tissue sectioning quality

---

### Technical Implementation Details

#### Key Algorithms & Tricks

1. **Nystrom Approximation for GP**:
   - Select $K$ inducing points (much smaller than $N$ total cells)
   - Approximate kernel matrix: $\mathbf{K}_{NN} \approx \mathbf{K}_{NK} \mathbf{K}_{KK}^{-1} \mathbf{K}_{KN}$
   - Reduces complexity from $O(N^3)$ to $O(NK^2)$

2. **Stochastic Variational Inference**:
   - Minibatch updates instead of full-batch
   - Natural gradient descent for faster convergence
   - Critical for scaling to 8M+ cells

3. **Multi-slice Refinement Strategy**:
   - Initial pairwise alignment (consecutive slices)
   - Refinement: For slice $i$, jointly consider slices $i-k, \ldots, i-1, i, i+1, \ldots, i+k$
   - Minimizes error accumulation compared to sequential alignment

4. **Mesh Correction via MRF**:
   - Discrete optimization problem on surface mesh
   - Energy function balances data term (alignment fit) and smoothness term (mesh regularity)
   - Graph-cuts or belief propagation for optimization

5. **Spatial Kernel Selection**:
   - Six kernel options allow flexibility for different interaction ranges
   - Bandwidth $h$ controls effective interaction distance (default: median nearest-neighbor distance)

6. **Ridge Regularization in CCI**:
   - Prevents overfitting when many ligands/receptors
   - Cross-validation for optimal $\lambda$ (or use default 0.1)

#### Benchmark Method Versions

| Method | Package | Version |
|--------|---------|---------|
| PASTE | paste-bio | 1.4.0 |
| PASTE2 | (from GitHub) | commit 517d6584 |
| moscot | moscot | 0.3.4.dev3+gf71976 |
| SLAT | scSLAT | 0.2.2 |
| STalign | STalign | 1.0 |
| SPACEL | SPACEL | 1.1.8 |
| Spateo | spateo-release | 1.1.0 |

Hardware: NVIDIA A100 40GB, CUDA 12.5 driver. Spateo, PASTE, SLAT, STalign use PyTorch 2.0.0; moscot uses JAX 0.4.13 + ott-jax 0.4.4; PASTE2 and SPACEL alignment run on CPU only.

---

### Limitations & Future Directions

#### Current Limitations (from authors)

The paper explicitly states three limitations:

1. **Sequencing Cost**: The cost of emergent spatial transcriptomics still prevents large-scale 3D ST studies. The rapid development of cost-effective open-sourced technologies such as Seq-Scope, OpenST, and novaST, and commercial platforms such as Singular Genomics' G4X (characterized by large FOVs), may democratize this technology in the near future.

2. **CCI Model Linearity**: The current spatially-aware regression model assumes linear/additive effects of L:R interactions. Graph neural networks (GNNs) could be developed to capture nonlinear and higher-order L:R interactions and combinatorial gene regulations in a spatially resolved manner.

3. **Vector Field vs. Gene Expression Dynamics**: The current morphometric vector field approach does not explicitly model gene expression dynamics or RNA velocity. These could be unified into a single learning task to learn reaction-diffusion-like spatiotemporal models linking physical morphogenesis with molecular kinetics.

#### Additional Practical Limitations

4. **Multi-omics Integration**: Current version primarily designed for transcriptomics; extending to spatial proteomics, chromatin accessibility, lineage tracing is ongoing.

#### Future Opportunities

1. **Multi-view Spatiotemporal Atlases**:
   - Combine RNA metabolic labeling (scNT-seq), Perturb-seq, lineage tracing
   - Enable perturbation-resolved, lineage-resolved spatiotemporal dynamics

2. **Cross-species Comparisons**:
   - Spatially-resolved evolutionary atlases
   - Compare 3D organ structures across species (e.g., four-chamber heart in mammals vs. single-chamber in invertebrates)

3. **Clinical Applications**:
   - Developmental disorders (congenital heart defects, neural tube defects)
   - Cancer spatial heterogeneity and metastasis
   - Organoid development and tissue engineering

4. **Enhanced Vector Field Models**:
   - Directly link morphometric dynamics with gene regulatory networks
   - Predict morphological outcomes from gene perturbations

---

### Biological Insights Summary

#### ZLI Organizer (E11.5 Mouse Brain)
- **Shh domain**: Does NOT extend to roof plate (Fgf8+ region)
- **Fgf8 -> Sufu/Gli3**: Potential mechanism limiting ZLI dorsal extension (Shh-repressor complex)
- **p2 (thalamus)**: Wnt/Bmp -> stemness factors (Id1, Tead1, Mycn, Sox2-mediated feedback)
- **p3 (prethalamus)**: Wnt7b -> Foxd1, Sema5b, Notch ligands
- **TF network**: Sox2 -> Bmps; Smad4 -> Id1 (intercellular/intracellular signaling integration)

#### Heart Asymmetrical Morphogenesis
- **RA (2nd heart field)**: Highest acceleration -> rapid expansion during late integration
- **RV/LA (2nd heart field)**: High curl -> rotational movement during chamber formation
- **LV (1st heart field)**: Lowest divergence -> mature, limited differentiation capacity
- **Morphogenic genes**: Pitx2 (L-R asymmetry), Hey2 (ventricular formation), Angpt1 (RA morphogenesis), Tbx2/Bmp2 (cell migration)

#### Drosophila Germband Retraction
- **Tail contraction**: High curl + acceleration at posterior germband
- **Midgut convergence**: Muscle co-localization drives fusion
- **Hindgut/salivary gland expansion**: Neo, Fkh, COX8 correlated with curl
- **Hox gradients**: Dfd (head), Scr/Antp (thorax), Ubx/Abd-A/Abd-B (abdomen) along A-P axis

#### Spinal Cord D-V Patterning
- **Lhx family + Dbx1/Gbx2**: Define dorsal-ventral domains
- **Slit2 (dorsal enrichment)**: Regulated by Lhx factors (cranial-spinal analogy)
- **Slit2 targets**: Adhesion/cytoskeletal genes for axon guidance

---

### Citations & Cross-references

**Key Methods Cited**:
- PASTE (Zeira et al., Nat Methods 2022)
- PASTE2 (Liu et al., Genome Res 2023)
- moscot (Klein et al., bioRxiv 2023, later Nat Methods)
- SLAT (Xia et al., Nat Commun 2023)
- STalign (Clifton et al., Nat Commun 2023)
- SPACEL (Xu et al., Nat Commun 2023)
- sc3D (Sampath Kumar et al., Nat Genet 2023)
- Belayer (Ma et al., Cell Syst 2022)
- CellChat (Jin et al., Nat Commun 2021)
- COMMOT (Cang et al., Nat Methods 2023)
- ncem (Fischer et al., Nat Biotechnol 2023)
- Dynamo (Qiu et al., Cell 2022)

**Key Datasets**:
- Mouse embryo E9.5/E11.5 Stereo-seq (Cheng et al. 2024, bioRxiv)
- Mouse embryo E8.5/E9.0 Slide-seq (Sampath Kumar et al., Nat Genet 2023)
- Human gastrulating embryo Stereo-seq (Xiao et al., Cell 2024)
- Mouse hemibrain MERFISH (Zhang et al., Nature 2023)
- Macaque cortex Stereo-seq (Chen et al., Cell 2023)
- Drosophila embryo Stereo-seq (Wang et al., Dev Cell 2022, bioRxiv 2024)

**Validation References**:
- Shh/Gli3/Sufu pathway (Chiang et al., Nature 1996; Pearse et al., Dev Biol 1999)
- ZLI/thalamus development (Kiecker & Lumsden, Nat Rev Neurosci 2005; Martinez-Ferre & Martinez, Front Neurosci 2012)
- Wnt/BMP signaling (Guglielmi et al., Nat Commun 2021; Hayward et al., Development 2008; Park et al., Cell 2015)
- Heart development (de Boer et al., Dev Biol 2012; Rivera-Feliciano & Tabin, Dev Biol 2006; Tessari et al., Circ Res 2008)
- Spinal cord patterning (Pierani et al., Neuron 2001; Pillai et al., Development 2007)
- Drosophila germband (Moreno & Morata, Nature 1999; Frank & Rushlow, Development 1996)

---

### Conclusion

Spateo represents a **transformative computational framework** for 3D spatiotemporal transcriptomics, enabling the first whole-embryo-scale reconstruction and analysis at single-cell resolution. By unifying:
1. Scalable non-rigid 3D alignment (up to 8M+ cells)
2. Multi-scale spatial digitization (subcellular to whole-embryo)
3. Cell-specific CCI modeling (intercellular + intracellular integration)
4. Morphometric vector field analysis (physical morphogenesis <-> molecular dynamics)

Spateo shifts spatial biology from **descriptive** (where are genes expressed?) to **predictive** (how do cells migrate? what drives morphogenesis?).

The framework is:
- **General**: Works across species (mouse, Drosophila), platforms (Stereo-seq, MERFISH, Visium, etc.), and modalities
- **Scalable**: 10--20x faster than existing methods; handles whole-embryo datasets on A100 40GB GPU
- **Accurate**: Consistently outperforms state-of-the-art in alignment ($p < 0.01$ across all benchmark datasets), CCI prediction ($R^2 > 0.8$), and digitization benchmarks
- **Interpretable**: Differential geometry quantities have direct physical meanings
- **Accessible**: Open-source package (v1.1.0) + interactive web viewer + extensive documentation + processed data repository

**Impact**: Spateo enables researchers to study organ ecology at a molecular level in 3D space over time, with broad applications in:
- Developmental biology (organogenesis, morphogenesis)
- Regenerative medicine (tissue engineering, organoid development)
- Disease modeling (congenital disorders, cancer spatial heterogeneity)
- Evolutionary biology (cross-species organ structure comparisons)

The Aristotle ecosystem (Spateo + Dynamo + Dynast) establishes a unified platform for **dynamic, quantitative, and predictive single-cell and spatial genomics**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
