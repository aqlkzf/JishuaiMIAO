---
layout: default
permalink: /paper-atlas/mechanotranscriptomics-6d8c202e/
title: "MechanoTranscriptomics"
nav: false
wide: true
description: "这篇论文把空间转录组和图像力学连接起来：先从膜染色得到细胞轮廓，用 VMSI 从弯曲的细胞连接推断相对压力、连接张力和细胞应力，再把这些力学量与同一细胞的基因表达、细胞类型和空间位置联合建模。 论文发表于 Nature Methods（2025），DOI 为 10.1038/s41592-025-02618-1。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>MechanoTranscriptomics</h1>
    <p>A computational pipeline for spatial mechano-transcriptomics</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 空间力学—转录组学：从细胞轮廓推断组织力，再与空间表达联合分析

### 一句话理解

这篇论文把空间转录组和图像力学连接起来：先从膜染色得到细胞轮廓，用 VMSI 从弯曲的细胞连接推断相对压力、连接张力和细胞应力，再把这些力学量与同一细胞的基因表达、细胞类型和空间位置联合建模。

论文发表于 *Nature Methods*（2025），DOI 为 `10.1038/s41592-025-02618-1`。

### 1. 它要解决什么问题？

空间转录组告诉我们“哪个基因在什么位置表达”，但组织发育不仅受分子信号控制，也受细胞之间的张力、压力、应力和形变控制。传统分析通常有两个断点：

1. 表达分析把每个细胞当作相对独立的观测，只加入面积、圆度等局部形态特征；
2. 力学推断可以从细胞几何估计张力或压力，却缺少与单细胞空间表达联合统计的通用流程。

这使一些关键问题难以回答：

- 转录组定义的组织边界是否也具有特殊力学性质？
- 哪些配体—受体信号可能解释边界上的高张力？
- 去掉空间位置造成的混杂后，哪些基因仍与力学状态相关？
- 基因对压力或应力的响应是否可能是阈值型、带通型或带阻型，而非简单线性？

### 2. 既有方法为什么不够？

#### 空间组学的分辨率与覆盖度存在取舍

- 测序型空间技术可以覆盖更多转录本，但往往缺少精确的单细胞轮廓。
- seqFISH+（*Nature*, 2019）和 MERFISH（*Science*, 2018；*Scientific Reports*, 2019）能达到单细胞甚至亚细胞分辨率，但仍不会自动给出细胞连接张力和细胞压力。

#### 形态—表达整合通常不是组织力学

MUSE（*Nature Biotechnology*, 2022）等方法能整合形态与表达，但使用的多是细胞自身的面积、形状或图像特征。张力和应力是细胞群体耦合产生的量：一个连接的状态同时取决于两侧细胞和邻域拓扑，不能只把细胞逐个独立处理。

#### 传统力学反演各有局限

- chord inference 把连接看成直线，基本忽略压力对曲率的贡献；
- tangent inference 利用顶点角度，但仍不直接联合推断压力；
- 一些曲率法能同时估计压力和张力，却对分割噪声敏感；
- VMSI（*Physical Review X*, 2020）通过圆弧多边形铺砌同时拟合压力和张力，抗噪性更好，但原方法没有完成本文的空间转录组整合和统计分析层。

#### 普通线性回归会受到空间混杂

某个脑区可能同时具有特定细胞类型、特定表达和特定力学状态。若直接回归“表达 ~ 压力”，显著性可能只是“它们都位于同一区域”，而不是真正的力学关联。因此论文又加入了去除平滑空间趋势的 geoadditive structural equation model（gSEM）。

### 3. 整体流程

```text
膜染色图像 + seqFISH + 单细胞参考图谱
                    |
                    v
        细胞分割、人工修正、表达转移
                    |
                    v
        从 mask 构建细胞—顶点—连接图
        - 每条连接拟合圆弧或直线
        - 拆分四重及更高阶顶点
        - 修正凹顶点，使顶点几何满足 VMSI
                    |
                    v
               VMSI 力学反演
        q、p、theta 初始化 -> 联合优化
        -> 连接张力 -> 细胞应力张量
                    |
                    v
          力学量与转录组按细胞对齐
        - 组织边界与异型/同型张力
        - 方向性配体—受体分析
        - 普通线性回归与空间残差回归
        - weighted median + scHOT 非线性分析
                    |
                    v
       力学空间图、候选信号与基因模块
```

本文用 E8.5 小鼠胚胎 seqFISH 数据演示流程。原始面板测得 387 个基因，再借助小鼠原肠胚形成单细胞图谱扩展表达信息。作者选取两个胚胎的三个脑区数据集，研究神经嵴、前/中/后脑、颅间充质以及中脑—后脑之间的组织边界。

### 4. 从分割 mask 到 VMSI 拓扑

#### 4.1 分割与表达转移

论文的实验流程包括 Fiji 局部对比度增强、去噪、DAPI 核分割、自定义轻量 U-Net、以细胞核为种子的 watershed，以及对错误连接的人工修正。之后用 Jaccard overlap 把原分割中的表达转移到修正后的细胞。

归档代码并不完整复现这一上游流程。主接口通常接收已经分割好的 mask；`src/segment.py` 另有 Cellpose 包装器和一个自定义模型权重，但没有找到论文所述 TensorFlow/Keras U-Net 的训练代码。因此，最可靠的软件起点是“高质量、已修正的实例分割 mask”。

#### 4.2 构建细胞图

代码把 mask 转成三个表：

- cell 表：质心、面积、周长、惯性张量、邻居等；
- vertex 表：顶点坐标、相邻细胞、相邻顶点和连接；
- edge 表：连接像素、两端顶点和两侧细胞。

边界细胞和孔洞附近细胞会被特殊处理，因为它们缺少足够的几何约束。

### 5. 为什么要使用圆弧多边形铺砌？

在机械平衡下，两个细胞之间的压力差会让连接产生曲率。若只看直线连接，压力信息会丢失。CAP（circular arc polygon）表示为每条 $\alpha$–$\beta$ 连接拟合：

- 曲率中心 $\boldsymbol{\rho}_{\alpha\beta}$；
- 曲率半径 $R_{\alpha\beta}$。

若边界太平、太短，或圆弧拟合不优于直线，代码就用直线代替。

VMSI 还要求顶点是三重且凸的。代码会：

1. 沿邻居顶点最大方差方向递归拆分四重或更高阶顶点；
2. 移动凹顶点，直到三个连接之间的角都小于 $\pi$。

这不是无害的格式整理，而是模型假设的一部分：推断结果依赖修正后的几何。

### 6. VMSI 的核心变量和方程

对每个细胞 $\alpha$，模型使用：

- $\mathbf{q}_\alpha$：对偶几何坐标；
- $p_\alpha$：相对细胞压力；
- $\theta_\alpha$：参与半径约束的标量参数。

相邻细胞 $\alpha,\beta$ 的曲率中心为

$$
\mathbf{\rho}_{\alpha\beta}
=\frac{p_\beta\mathbf{q}_\beta-p_\alpha\mathbf{q}_\alpha}
{p_\beta-p_\alpha},
$$

半径为

$$
R_{\alpha\beta}
=\sqrt{
\frac{p_\alpha p_\beta\lvert\mathbf{q}_\alpha-\mathbf{q}_\beta\rvert^2}
{(p_\alpha-p_\beta)^2}
-\frac{\theta_\alpha-\theta_\beta}{p_\alpha-p_\beta}
}.
$$

直觉上，$p$ 给出压力差，$\mathbf{q}$ 和 $\theta$ 决定满足机械平衡的圆弧几何。算法的目标是找到一组参数，使理论圆弧尽量贴合分割图像中的真实连接像素。

### 7. 为什么优化要分两步？

若直接联合优化，容易落入平凡解，例如相邻细胞的 $p$ 和 $\mathbf{q}$ 变得相同。代码先做初始化：

1. 用细胞质心初始化 $\mathbf{q}$；
2. 根据连接切向和曲率中心的正交关系初始化 $p$；
3. 在固定 $p,\mathbf{q}$ 后估计并优化 $\theta$；
4. 再联合优化 $p,\mathbf{q},\theta$。

主目标函数是

$$
E_{p,q,\theta}
=\frac{1}{2n_e}
\sum_{(\alpha,\beta)}\sum_n
\left(
\lvert\mathbf{r}_{\alpha\beta}(n)-\mathbf{\rho}_{\alpha\beta}\rvert
-R_{\alpha\beta}
\right)^2.
$$

也就是让每条观测连接上的像素到预测曲率中心的距离尽可能接近预测半径。

代码包含 NLopt 的 augmented Lagrangian + L-BFGS 路径，并提供目标和约束的解析梯度；同时保留 MATLAB 优化路径。这里存在版本保真问题：2025 正文说所有优化使用 NLopt，但归档 notebook 00 说原始推断使用 MATLAB `fmincon`，并实际设置 `optimiser='matlab'`。归档对应的是 2023 bioRxiv 口径的 Zenodo V1.0，因此最终论文图究竟由哪条路径生成，当前证据无法确定。

### 8. 从压力得到张力和应力

#### 8.1 连接张力

Young–Laplace 关系为

$$
T_{\alpha\beta}=(p_\alpha-p_\beta)R_{\alpha\beta}.
$$

代码使用代入半径方程后的等价形式。因为整体尺度没有外部标定，张力是相对值、任意单位，适合在同一数据集内比较边界与非边界连接。

#### 8.2 细胞应力张量

论文用 Batchelor 公式把压力和各连接的张力组合成二维应力张量：

$$
\sigma_\alpha
=-p_\alpha\delta
+\sum_{\{\beta\}_\alpha}
\frac{T_{\alpha\beta}}{2A_\alpha}
\int_{r_{\alpha\beta}}\mathrm{d}r\,
\hat{\mathbf{r}}_{\alpha\beta}\otimes\hat{\mathbf{r}}_{\alpha\beta}.
$$

之后把张量转成特征：两个特征值、方向和各向异性；下游 notebook 再由特征值构造 stress magnitude。

需要注意：源码明确说明 `compute_stresstensor` 使用小角度近似，而正文公式展示的是完整线积分。因此应力部分是“物理思想一致、实现存在近似”的 Partial 匹配。

### 9. 如何定义组织边界？

设细胞 $i$ 的邻居集合为 $N$，两个组织类别为 $A,B$。边界概率定义为

$$
L
=\frac{1}{N}\sum_{j\in N}[j\in A]
\times
\frac{1}{N}\sum_{j\in N}[j\in B].
$$

如果一个细胞的邻居大约一半来自 $A$、一半来自 $B$，$L$ 就较高。论文用 $L>0.15$ 定义边界细胞，并用细胞邻接图上的最短步数表示离边界距离。

连接再分为：

- 边界上的异型连接：两侧属于不同组织；
- 同型连接：两侧属于同一组织；
- 边界附近或远离边界的连接。

三个数据集中，异型边界张力比同型张力高约 12–35%。补充表的六个比较中五个 $P<0.05$；dataset 1 的“boundary vs neural crest”为 $P=0.052045693$，不能概括成所有比较都显著。

### 10. 如何寻找边界的分子候选机制？

对发送细胞 $\alpha$ 的配体 $L$ 和接收细胞 $\beta$ 的受体 $R$，相互作用势定义为

$$
P_{L\to R,\alpha,\beta}=L_\alpha R_\beta.
$$

再用 Wilcoxon rank-sum 统计量比较异型和两种同型连接，取两次比较中较小的统计量作为保守的方向性 interaction likelihood。

结果把 ephrin–Eph、Wnt5a–Fzd5 等排在前列。ephrin/Eph 在生物学上确实可能通过 RhoA—肌球蛋白收缩和黏附差异提高边界张力，但本文的计算只提供表达关联和空间互补模式，没有直接测量受体活化或肌动蛋白—肌球蛋白活动。因此正确表述是“候选机制”。

### 11. 如何控制空间混杂？

普通模型为

$$
g_i=\beta_{\mathrm{linreg}}q_i+\epsilon_i,
$$

其中 $g_i$ 是基因表达，$q_i$ 是取对数后的压力或应力大小。

gSEM 先分别拟合表达和力学量的二维空间平滑项：

$$
x_i=f^x(\mathbf{c}_i)+\epsilon_i^x,
$$

再用去掉平滑空间趋势后的残差回归：

$$
r_i^g=\beta_{\mathrm{spatial}}r_i^q+\epsilon_i.
$$

R helper 的实现与这个定义直接对应：对 predictor 和 response 各拟合一个二维 thin-plate GAM，然后 `lm(r_Y ~ r_X)`。

这能减少“二者都位于同一区域”造成的假关联，但仍不是因果模型，也不能排除所有细胞类型、发育状态或测量误差造成的混杂。

### 12. 如何发现非线性关系？

细胞按压力或应力大小排序，在排序轴上计算局部 weighted median：

$$
a^*=\arg\min_a\sum_i w_i\lvert g_i-a\rvert.
$$

随后 scHOT 通过打乱细胞排名进行 permutation test，筛选显著变化的表达曲线，再用层次聚类和 dynamicTreeCut 得到曲线模块。

论文全量分析使用：

- 3,000 个高变基因；
- 三角权重窗口 span 0.1；
- 每个基因 200 次置换；
- BH 校正阈值 $P_{\mathrm{adj}}\leq0.1$。

归档 notebook 04 是演示版本：只随机抽取 100 个基因，并使用 `span=0.25`。因此 notebook 映射了算法，但不是论文全量参数的直接复现。

曲线包括：

- 单调或 sigmoid 型；
- 只在中间力学范围高表达的 band-pass 型；
- 中间低、两端高或相反的 band-stop 型。

这些模式是统计现象。要证明真实的机械感受“滤波器”，仍需用光遗传控制收缩、活体 mRNA 成像等实验直接扰动。

### 13. 论文得到什么结论？

#### 力学反演本身

在具有真实压力和张力标签的模拟组织上，Python VMSI 的推断值与真值 Spearman 相关系数超过 0.96，并对顶点噪声、欠分割、图像大小和压力差变化具有较强鲁棒性。

#### 组织边界

转录组定义的组织边界与较高异型连接张力重合；平行切片也能恢复中脑—后脑边界的高张力。Cellular Potts 模拟表明，在该模型内，仅提高异型张力就足以维持边界或促使混合细胞分选。

#### 分子与基因模块

- LR 分析提出 ephrin/Eph 等可能解释高边界张力；
- gSEM 在控制平滑空间趋势后找到组织依赖的 mechano-associated genes；
- 非线性分析发现阈值型、带通型和带阻型表达模块。

### 14. 如何理解归档代码的可复现性？

#### 匹配较强的部分

- mask 到细胞/顶点/连接图；
- 圆弧拟合；
- 四重顶点拆分和凸性修正；
- $p,\mathbf{q},\theta$ 初始化与联合优化；
- Young–Laplace 张力；
- 压力、张力、近似应力和形态特征输出；
- 边界、LR、gSEM 和非线性分析的 notebook 映射。

#### 仍缺失或不确定的部分

- Zenodo `10.5281/zenodo.13975228` 是 V1.0、bioRxiv 时代归档，与 2025 最终代码是否完全一致未验证；
- 正文 NLopt 与 notebook MATLAB 的优化器口径冲突；
- 论文所述轻量 U-Net 训练代码未找到；
- Jaccard 表达转移和图谱插补实现未找到；
- Cellular Potts 模拟代码未找到；
- 平行切片的 Gaussian smoothing 和 local weighted Spearman/scHOT 实现未找到；
- `reproduce_data/` 只有外部 Dropbox 链接和 LR 表，没有 notebook 所需的完整 CSV/TIF 输入；

### 15. 最合适的使用方式

把这套方法看成两层：

1. **TensionMap/VMSI 力学层**：输入高质量分割 mask，输出相对压力、连接张力、应力和形态特征；
2. **空间统计层**：把这些特征与同一细胞的表达、位置和邻接关系联合起来，做边界、通信、空间残差和非线性分析。

第一层在归档源码中相对完整；第二层更像一组研究 notebook 和数据约定。若要真正复现论文，应先取得外部数据，明确最终论文使用的代码版本和优化器，再把 notebook 的演示参数恢复为正文的全量设置，并逐项验证主图和补充图。当前分析只完成静态、源代码和图像证据核验，**未运行 runtime/reproduction**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## A computational pipeline for spatial mechano-transcriptomics

**Nature Methods (2025)** · DOI `10.1038/s41592-025-02618-1`

### Problem

Spatial transcriptomics can locate molecular programs in tissue, but most analysis treats cell morphology as a local, cell-autonomous feature and does not recover mechanically coupled quantities such as cell–cell junction tension, intracellular pressure or cellular stress. Conversely, force-inference methods reconstruct mechanics from cell geometry but do not provide a general statistical framework for relating those forces to spatial gene expression.

### Why existing approaches are insufficient

- Sequencing-based spatial methods may cover the transcriptome but often lack true single-cell or subcellular morphology.
- Image-based methods such as seqFISH+ (*Nature*, 2019) and MERFISH (*Science*, 2018; *Scientific Reports*, 2019) resolve cells and transcripts but still require a separate mechanics layer.
- Morphology–expression methods such as MUSE (*Nature Biotechnology*, 2022) integrate cell shape and transcriptional state, yet mainly use local morphometrics rather than globally coupled tissue forces.
- Earlier force-inference methods either neglect pressure, require very precise junction geometry or are sensitive to noise. VMSI (*Physical Review X*, 2020) jointly infers pressure and tension from circular-arc polygon tilings, but did not itself provide the paper's full spatial transcriptomic integration.
- Ordinary linear regression cannot distinguish a genuine mechanics association from a smooth spatial trend shared by gene expression and tissue mechanics.

### Proposed framework

The paper builds a single-cell spatial mechano-transcriptomics workflow:

```text
membrane image + seqFISH + gastrulation atlas
  -> corrected cell segmentation
  -> circular-arc topology and VMSI force inference
  -> pressure, junction tension, stress tensor and morphometrics
  -> cell-type boundary and LR analyses
  -> linear, geoadditive and nonlinear gene–mechanics models
```

The mechanics core fits circular arcs to cell junctions, repairs fourfold and concave vertices, optimizes VMSI variables $\mathbf{q}$, $p$ and $\theta$, derives junctional tension through Young–Laplace, and computes a per-cell stress tensor. The statistical layer then identifies tissue boundaries, compares heterotypic and homotypic tensions, ranks directional LR interactions, removes smooth spatial effects with a geoadditive structural equation model (gSEM), and tests nonlinear weighted-median expression profiles with scHOT.

### Evaluation and main findings

- Synthetic tissues with known mechanics yielded inferred pressure and tension correlations above Spearman $\rho=0.96$ across changes in pressure differential, image size, vertex noise and undersegmentation.
- In three E8.5 mouse embryo brain-region datasets, heterotypic junctions at transcriptomically defined boundaries had approximately 12–35% higher tension than homotypic junctions. Five of six reported pairwise tests had $P<0.05$; one dataset 1 comparison was borderline at $P=0.052045693$.
- A parallel midbrain–hindbrain section 12 μm away recovered elevated boundary tension and greater local mechanical coherence near the boundary.
- Cellular Potts simulations showed that the measured heterotypic tension differences were sufficient, within the model, to maintain boundaries and drive sorting from mixed initial conditions.
- Directional LR analysis highlighted ephrin–Eph pairs and other developmental signals as candidate molecular determinants of elevated boundary tension.
- Linear analysis found shared pressure- and stress-associated genes; gSEM retained a smaller, tissue-dependent set after removing smooth spatial trends, including genes with known or plausible mechanobiological roles such as Slc9a3r2, Lima1, Crabp2 and Apba2.
- Nonlinear analysis identified sigmoid, band-pass and band-stop-like expression profiles across pressure or stress rankings, motivating experimental tests of thresholded mechanosensitive regulation.

### What the code snapshot contains

The Zenodo archive at version DOI `10.5281/zenodo.13975228` contains:

- a substantial Python VMSI implementation with mask processing, CAP fitting, NLopt/MATLAB optimization, tension, pressure, stress and morphometric export;
- six downstream notebooks mapping mechanics execution, boundary analysis, expression analysis, LR analysis, nonlinear scHOT and gSEM;
- Python/R helper functions and pinned conda environments;
- executed notebook outputs and links to external per-dataset inputs.

Core mechanics fidelity is strong, but overall paper–code fidelity is **medium**. Important qualifications are:

- the Zenodo V1.0 archive identifies itself with the 2023 bioRxiv manuscript, not explicitly with the final 2025 code state;
- the paper says all optimization used NLopt, while notebook 00 says original inference used MATLAB `fmincon` and invokes MATLAB;
- the source computes stress with a documented small-angle approximation;
- the exact TensorFlow/Keras lightweight U-Net training code, expression remapping/imputation, Cellular Potts simulations and serial-plane local-correlation analysis were not found;
- required reproduction matrices and segmentation images are not bundled, only linked externally;
- nonlinear and gSEM notebooks are demonstrations over 100-gene subsets, and some saved settings differ from the paper's full analysis.

### Limitations

- Mechanical inference depends strongly on staining, segmentation and junction-curvature quality.
- VMSI assumes quasi-static mechanical equilibrium, threefold convex vertices and a valid 2D CAP representation.
- Tension and pressure are relative rather than calibrated physical measurements.
- Fixation and 2D sectioning may distort morphology or omit out-of-plane forces.
- gSEM reduces smooth spatial confounding but does not establish causality.
- LR products and nonlinear expression curves nominate mechanisms; they do not directly measure signaling activity or mechanochemical feedback.

### Reproducibility assessment

**2.5/5 — partially reproducible from the archived snapshot.** The force-inference core is inspectable and closely matches the paper, and the analysis notebooks provide a useful downstream map. However, final-publication version fidelity is unresolved, key inputs and several analysis components are external or absent, notebook demonstration settings differ from the reported full analysis, and no runtime or numerical reproduction was performed in this workspace.

### Bottom line

The paper's main contribution is not a new force-inference equation alone, but a general integration pattern: convert cell geometry into interpretable mechanical variables, register those variables to spatial expression in the same cells, and analyze the joint system while accounting for tissue boundaries, spatial confounding and nonlinear responses. The biological results support elevated heterotypic tension as a robust signature of embryonic compartment boundaries and identify plausible molecular programs associated with that mechanical state, while leaving causal validation to future perturbation experiments.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
