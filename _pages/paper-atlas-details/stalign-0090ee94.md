---
layout: default
permalink: /paper-atlas/stalign-0090ee94/
title: "STalign"
nav: false
description: "STalign 把稀疏空间坐标转换成可注册的组织密度图，直接优化全局 affine 与平滑可逆的 LDDMM 变换，并用背景/artifact mixture 和可选 landmark 处理部分重叠；它的强项是跨样本、跨平台和 atlas 的结构配准，边界是依赖共享形态、非凸初始化、栅格尺度与非一一细胞解释。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Communications · 2023</span>
    </div>
    <h1>STalign</h1>
    <p>STalign: Alignment of spatial transcriptomics data using diffeomorphic metric mapping</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-023-43915-7" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STalign 方法解读：把空间坐标转成图像，再用可微分同胚完成组织配准

### 1. STalign 对齐的不是细胞身份，而是组织结构

不同空间转录组切片可能来自不同个体、相邻切面或不同平台。它们会有整体平移、旋转、缩放、剪切，也会因切片、染色、组织形变产生局部弯曲、缺口和部分重叠。跨样本通常不存在逐细胞真对应，跨平台还可能没有相同基因面板。

STalign 因而把任务定义为几何配准：从源切片到目标切片学习一个平滑、可逆的坐标变换。对于单细胞分辨率数据，它主要使用细胞密度形成的组织轮廓；对于低分辨率 ST，可使用与该切片注册的高分辨率组织学图像。变换求出后，再把源细胞、表达、细胞类型或 atlas 标签带到目标坐标系。

### 2. 为什么先把点云栅格化

原始输入可以是一组细胞坐标 $(x_i,y_i)$。STalign 将离散点测度 $\rho$ 与 Gaussian 核平滑，得到连续密度图：

$$
I(x,y)=k^{1/2}*\rho.
$$

`rasterize()` 在规则网格上累积每个细胞的局部 Gaussian 贡献，输出源/目标图像和坐标轴。这样，优化规模取决于栅格像素而不是所有细胞对，且无需先猜测一一细胞匹配。`rasterize_with_signal()` 还可为每个信号生成通道，但论文的核心对齐强调密度或组织学结构。

栅格大小 `dx` 和 blur 决定可识别的空间尺度。网格太粗会丢失小结构，太细会放大分割噪声并增加显存/时间。密度结构本身若不共享——例如严重缺失、肿瘤形态差异或分割偏差——再精细的变换也没有可靠依据。

### 3. 总变换：先全局 affine，再局部 diffeomorphism

STalign 使用复合映射

$$
\phi^{A,v}(x)=A\varphi_1^v(x),
$$

其中 $A$ 是 affine 变换，处理平移、旋转、尺度与剪切；$\varphi_1^v$ 由时间变化速度场 $v_t$ 积分得到，处理局部非线性形变。代码 `v_to_phii()` 以特征线方式逐时间步积分逆变换，`LDDMM()` 同时优化 affine 参数 `L,T` 和速度场 `v`。

“diffeomorphic”表示在优化模型内变换平滑且可逆，尽量避免折叠或撕裂。这适合组织受到连续形变的情形，却不能通过变换创造一个真实孔洞、删除组织或让连通区域断开。拓扑差异应交给部分重叠模型或被视为不可对应区域，而不是强迫速度场解释。

### 4. 目标函数在权衡什么

核心目标可写成

$$
E(A,v,\theta)=M_\theta(\phi^{A,v}\cdot I^S,I^T)+R(v)+E_{points}.
$$

第一项比较变换后的源图和目标图；第二项惩罚不平滑速度：

$$
R(v)=\frac{1}{2\sigma_R^2}\int_0^1\int |Lv_t(x)|^2\,dx\,dt.
$$

实现中微分算子在 Fourier 域构造为 `LL`，其逆 `K=1/LL` 用于平滑速度梯度。较强正则带来更平滑、更保守的变换；追求很小的图像误差会允许更复杂局部形变。`a` 是速度场平滑尺度，代码的速度网格间距也与它相关，所以它同时影响变形自由度与计算分辨率。

STalign 还在每轮拟合线性 contrast function，把源强度转换到目标强度尺度。因此，它能对齐不同密度/染色对比，但不是完全对任意非线性成像差异不变。

### 5. 部分重叠如何避免被强行拉伸

目标像素由三成分 mixture 描述：真实匹配组织 $W_M$、背景 $W_B$、artifact/非对应组织 $W_A$。图像匹配误差只按 $W_M$ 加权；背景与 artifact 分别围绕自己的强度均值建模。代码初始化三类责任为 0.5/0.4/0.1，并在初始对齐后周期性更新 posterior responsibility。

这使缺失组织、撕裂或图像 artifact 不必全部由 diffeomorphism 解释。但它仍是强度 mixture，而不是对缺口生物来源的识别器。源/目标方向也重要：论文建议在部分匹配时把更完整切片作为 source，使缺失更容易由目标 background/artifact 权重处理。

### 6. landmark 的作用和代码边界

难以从 identity 初始化的跨技术或部分切片可手工放置对应 landmark。`L_T_from_points()` 在少于 3 对点时只估计平移，至少 3 对点时用最小二乘求 affine；2D `LDDMM()` 还可加入

$$
E_{points}=\frac{1}{2\sigma_P^2}\sum_i
\|\phi(p_i^S)-p_i^T\|^2.
$$

`point_annotator.py` 提供交互式点标注。Landmark 是初始化/软约束，不是独立验证数据；用同一批点初始化再报告这些点的误差会高估泛化。

当前 commit 的 `LDDMM_3D_to_slice()` 虽保留 `pointsI/pointsJ` 参数，但 point transform 和 `EP` 代码在 1474–1508 行被注释，实际 3D-to-slice 优化没有激活 landmark penalty。不能把 2D 接口行为直接推广到该 3D 路径。

### 7. 优化流程怎样运行

典型流程是：

1. 栅格化 source 与 target，或准备组织学/atlas raster。
2. 以 identity 或 landmark affine 初始化 `L,T`。
3. 每轮构造 affine $A$，积分速度场得到变换，在 target 网格反向采样 source。
4. 拟合 contrast，计算 matching、velocity regularization 和可选 point loss。
5. 由 PyTorch autograd 更新 `L,T,v`；到 `diffeo_start` 后才更新非线性速度，并把 affine 步长降为原来的约十分之一。
6. 初始阶段以后更新 match/background/artifact responsibility。
7. 返回 `A,v,xv,WM,WB,WA`，再用 transform helpers 映射点或图像。

这是对每一对图像直接做数值优化，不是先用训练集训练神经网络、再对新切片前向推理。GPU 只加速该优化；每个新配准仍需重新求解，且非凸目标对初始化和超参数敏感。

### 8. 2D atlas 到 3D 的扩展应怎样理解

`LDDMM_3D_to_slice()` 将三维 atlas source 通过 affine 与三维速度场变换，再与二维 ST 切片对应的采样面比较。得到的变换可把 Allen CCF 区域标签 lift over 到切片，并把 ST 点放回 atlas 坐标。

论文用 marker gene 与预期脑区重合、跨 replicate 细胞类型组成一致性和区域边界扩张后的 entropy 变化验证 atlas 标注。它支持解剖合理性，但不等于每个细胞的 atlas 区域都是金标准。切面选择、atlas 个体差异、三维初始化以及当前无 3D landmark penalty 都会影响结果。

### 9. 如何读六张主图和补充证据

图 1 展示点云→density raster→affine/LDDMM→aligned coordinates。图 2 在 MERFISH 重复切片中显示空间基因的 cosine similarity 高于非空间基因；图 3–4 用 landmark 初始化跨 MERFISH/Visium，并从表达和 cell-type composition 评价。图 5 把切片接到三维 Allen atlas。图 6 扩展到 Xenium、STARmap、发育心脏、乳腺癌和 H&E。

补充 PDF 包含 landmark 定义、运行时间、更多对齐与统计图。运行时间跨 notebook 差异很大：例如 supplement 报告的 MERFISH–MERFISH 大迭代任务明显慢于若干 200-iteration 示例；因此不能用单个运行时间代表所有数据。仓库有教程和预计算输出，但没有一条命令重现全部论文统计与面板。

### 10. 当前代码快照与复现边界

本工作区代码锚定 commit `b2068edc98974efa54537eca194736e177bbe11d`。核心算法高度对应论文，但完整复现需下载/整理多个公开数据、重跑 notebook、重建基因与细胞类型统计及 atlas 评价。

还需保留以下边界：

- 坐标数组内部采用 row/column 约定，常与绘图 x/y 顺序相反；错误交换轴会产生看似合理但方向错误的变换。
- 插值使用 `grid_sample(..., align_corners=True)`；PyTorch 版本与 dtype/device 会影响数值和资源。
- mixture responsibility 并非从第 0 轮立即自由更新；代码只在对齐进入稳定阶段后周期更新。
- 默认 `niter=5000` 只是函数默认，论文教程针对不同任务使用不同迭代数和参数。
- 对齐准确度是组织尺度/mesoscopic 的，不应表述成跨样本单细胞一一配对。
- 旧 pipeline 记录曾标记 Publish complete，但本轮按用户要求只完成分析合同，不进行 README、commit 或 push。

### 11. 一句话把握 STalign

STalign 把稀疏空间坐标转换成可注册的组织密度图，直接优化全局 affine 与平滑可逆的 LDDMM 变换，并用背景/artifact mixture 和可选 landmark 处理部分重叠；它的强项是跨样本、跨平台和 atlas 的结构配准，边界是依赖共享形态、非凸初始化、栅格尺度与非一一细胞解释。

### 证据入口

- 论文与图注：`paper source/PMC10709594/paper.md`
- 三份补充材料：`supplementary/41467_2023_43915_MOESM1_ESM.pdf`、`MOESM2_ESM.pdf`、`MOESM3_ESM.pdf`
- 图逐项解释：`figure_analysis.md`
- 核心代码：`STalign/STalign/STalign.py`
- Landmark 工具：`STalign/STalign/point_annotator.py`
- 教程与预计算输出：`STalign/docs/notebooks/`、`STalign/docs/*_data/`
- 代码—论文映射：`doc_code.md`

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## STalign Summary

### Motivation and Novelty

STalign addresses a practical bottleneck in spatial transcriptomics: comparing tissue sections across samples, platforms, and atlases requires spatial coordinates to be aligned first. Rigid or affine alignment can handle global rotation and translation, but it cannot correct local tissue deformation, tears, and partial overlap. Gene-expression-based alignment can also be limited when platforms have different gene panels or sensitivity.

The paper's novelty is to adapt large deformation diffeomorphic metric mapping (LDDMM) to spatial transcriptomics. STalign rasterizes cell coordinates or uses registered histology images, then solves a smooth invertible image-registration problem with an affine component, a diffeomorphic velocity field, a contrast transform, and mixture weights for matched tissue, background, and artifacts.

### Method Overview

For single-cell-resolution ST data, STalign converts cell coordinates into a smoothed raster image. The source image $I^S$ is aligned to the target image $I^T$ by optimizing:

$$
E(A,v,\theta)=M_\theta(\phi^{A,v}\cdot I^S,I^T)+R(v),
$$

where $\phi^{A,v}(x)=A\varphi_1^v(x)$ combines affine alignment and a diffeomorphic flow. Optional landmark points can initialize and guide difficult alignments. A Gaussian mixture model separates target pixels into matching, background, and artifact components, allowing partial tissue matches without forcing impossible deformations.

After optimization, the learned transform is applied back to original cell coordinates or atlas grids. This enables spatial comparison of gene expression, cell-type composition, or anatomical annotations at matched locations.

### Evaluation

The paper evaluates STalign in several increasingly difficult settings:

| Setting | Dataset | Main Result |
|---|---|---|
| Within-technology alignment | MERFISH mouse brain replicates | STalign reduces landmark RMSE relative to supervised affine alignment and achieves median cosine similarity 0.73 for spatially patterned genes. |
| Cross-technology alignment | MERFISH-to-Visium mouse brain | Spatially patterned shared genes show median cosine similarity 0.55 after alignment; non-spatial genes are much lower. |
| Cross-resolution cell types | MERFISH clusters vs Visium deconvolved cell types | Matched cell types show median proportional cosine similarity 0.75. |
| 2D-to-3D atlas alignment | MERFISH mouse brain to Allen CCF | Lifted-over regions recapitulate marker-gene enrichment and replicate-consistent cell-type composition. |
| Generalization examples | Xenium, STARmap, ISS heart, breast cancer, H&E | Visual overlays show improved structural correspondence after nonlinear alignment. |

Compared methods include PASTE (Nature Methods, 2022), GPSA (Nature Methods, 2023), ST Utility / landmark-based affine workflows (BMC Genomics, 2020), and Tangram (Nature Methods, 2021). The paper's key distinction is real-space structural alignment using a diffeomorphic image-registration framework, rather than purely affine alignment or expression-manifold mapping.

### Code Assessment

The cloned repository matches the core paper method well. `STalign/STalign.py` implements rasterization, 2D `LDDMM()`, 3D-to-slice `LDDMM_3D_to_slice()`, mixture weights, contrast fitting, landmark support, and transform application. Tutorial notebooks cover the paper's main use cases, including MERFISH-MERFISH, MERFISH-Visium, Xenium-H&E, and Allen atlas alignment.

The main gap is result-level reproducibility. The repository is packaged as a toolkit with tutorials and example data, not as a single workflow that regenerates every paper figure statistic from raw public downloads. Evaluation statistics such as cosine similarity distributions, STdeconvolve cell-type matching, entropy tests, and all paper panels would require additional reconstruction.

### Limitations

STalign assumes that cell density or registered image intensity captures shared tissue structure. It is best suited to single-cell-resolution ST data or spatial assays with a registered high-resolution histology image. Poor cell segmentation can degrade the structural proxy used for alignment.

Because the objective is nonconvex, initialization can matter. Landmark points are useful for partial matches and difficult cross-technology cases. The LDDMM formulation also preserves topology, so it cannot explain holes or disconnected tissue correspondences solely through deformation. The paper recommends using the more complete tissue section as source when partial overlap is present.

At single-cell scale, there is generally no true one-to-one cell correspondence across sections. The appropriate interpretation is mesoscopic alignment accuracy, evaluated by spatial gene patterns, landmarks, cell-type composition, and atlas-region consistency.

### Reproducibility Rating

**Rating: 4 / 5.**

The code is public, compact, and closely matches the mathematical method. The repository includes install instructions, tutorial notebooks, example data, and precomputed aligned outputs for several scenarios. Core algorithmic behavior is transparent in a single implementation file.

The rating is not 5 because the repository does not provide a complete figure-reproduction pipeline for all reported benchmark statistics. A user can run the method and follow tutorials, but reproducing every paper result requires reconstructing evaluation scripts and downloading multiple large public datasets.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
