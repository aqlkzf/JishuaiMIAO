---
layout: default
permalink: /paper-atlas/lynx-72d6ee1d/
title: "LYNX"
nav: false
description: "空间组学常有两类困难：一是组织变化往往是连续梯度，而非几个边界清楚的簇；二是两种空间模态可能分辨率、特征数和噪声都不同。比如细胞分辨率 Xenium 与较粗的 DESI 代谢像素并不能逐点一一对应。LYNX 希望从配准后的两种模态中学到共同的空间流形，再在此基础上描述梯度、分区、分子动态和局部细胞组成/相互作用摘要。 它并不直接证明“谁通过哪一个配体-受体对作用于谁”。论文和代码中的 \\omega 是空间邻居残差的学习权重；"
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
      <span>bioRxiv · 2026</span>
    </div>
    <h1>LYNX</h1>
    <p>LYNX: a deep generative model for linking spatial dynamics and cell interactions in multimodal spatial data</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.64898/2026.07.09.737574" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for LYNX">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/azizilab/Lynx" target="_blank" rel="noopener noreferrer" aria-label="Open code for LYNX">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## LYNX：把空间梯度与局部相互作用放进同一个多模态表示

### 它要解决什么问题？

空间组学常有两类困难：一是组织变化往往是连续梯度，而非几个边界清楚的簇；二是两种空间模态可能分辨率、特征数和噪声都不同。比如细胞分辨率 Xenium 与较粗的 DESI 代谢像素并不能逐点一一对应。LYNX 希望从配准后的两种模态中学到共同的空间流形，再在此基础上描述梯度、分区、分子动态和局部细胞组成/相互作用摘要（`paper.md:36-56`）。

它并不直接证明“谁通过哪一个配体-受体对作用于谁”。论文和代码中的 $\omega$ 是空间邻居残差的学习权重；它可同时受局部组织组成与共表达结构影响（`paper.md:289-298,415-421`）。因此，把它解释成因果通信或配体-受体机制是不成立的。

### 输入、输出与核心想法

- 主模态 $x\in\mathbb{R}^{N\times G}$：通常是高分辨率/高通量数据，例如每个细胞的 RNA。
- 辅助模态 $u\in\mathbb{R}^{M\times P}$：可更粗，例如代谢像素；也可为组织图像 patch。
- 还需要：两张切片的配准坐标、空间邻居关系，以及主模态细胞的 cluster 标签。

输出包括辅助分辨率的 niche latent $z$、细胞分辨率表示、主模态重建、连续梯度/离散区域，以及按发送者细胞类型汇总的 $\omega$ 分数。

```text
x、u、配准坐标
  -> 异构图（细胞-细胞、patch-patch、细胞-patch 边）
  -> 用 GCN + 跨模态 GAT 得到 q_phi(z | x,u)
  -> 把 patch 的 z 沿 patch->cell 边平均下传到 z_cell
  -> 可选：kappa 基线 + omega 加权的邻居残差
  -> 负二项分布解码，重建原始 x
  -> latent 流形 -> 主图/伪时间梯度 -> 分区、特征和 omega 摘要
```

### 逐步理解

#### 1. 异构空间图不是“自动配准”

论文先假设模态已经注册到共同坐标系，再连接模态内和模态间的近邻（`paper.md:253-260`）。代码根据半径找跨模态近邻，并分别建立 ref→query、query→ref 两种边（`Lynx/models/dataset.py:232-297,310-327`）。所以配准质量与半径设定会直接影响后续结果。

#### 2. 共同的 niche 表示 $z$

`XtoZEncoder` 先分别对主模态和辅助模态做 GCN，再把主模态特征通过 GAT 聚合到辅助节点，输出 $z$ 的均值和方差（`Lynx/models/module.py:162-207`）。直观上，一个低分辨率 patch 的 $z$ 同时看到了该 patch 自己的特征和邻近细胞的转录组上下文。

#### 3. 从 patch 回到 cell：确定性 unpooling

每个细胞接收相连 patch 的 $z$ 平均值：

$$z_{\mathrm{cell},i}=\operatorname{mean}_{m\to i} z_m.$$

代码用 `scatter_mean` 完成它（`Lynx/models/vgae.py:111-115`）。这里不是再采样一个随机变量；给定 $z$ 和图，它就是确定的。这也解释了为何粗分辨率辅助数据仍能给每个细胞一个局部环境上下文。

#### 4. $\kappa$ 与 $\omega$：内在状态和邻居残差

$\kappa$ 是按 cluster 建模的细胞基线；代码用 cluster embedding 定义其先验（`Lynx/models/vgae.py:132-147`）。随后计算 $\delta=z_{cell}-\kappa$ 并全局中心化，再用 $\omega$ 做入边加权平均，最后得到 `s_prime = kappa + msg`（`Lynx/models/vgae.py:149-155,479-499`）。

距离先验的 rate 为 $(1+d_{ij})^\alpha$（`Lynx/models/vgae.py:121-130`）：$\alpha$ 变大时，先验更偏好近邻。$\omega$ 的推断器结合源细胞表达、目标细胞表达和目标 $z_{cell}$ 产生正分数（`Lynx/models/module.py:339-378`）。HSIC 项试图避免邻居信息与 $\kappa$ 重复（`Lynx/models/vgae.py:241-252`）。

#### 5. 为什么只重建主模态？

解码器把交互更新后的 latent 变成基因组成，乘以细胞 library size 后用负二项分布重建 $x$（`Lynx/models/vgae.py:161-169`）。辅助 $u$ 的角色是条件先验/后验的锚点，而非在同一 decoder 中与 $x$ 等权重共同重建。这是它处理异分辨率和不共享 feature 的关键设计。

### 论文中的验证

作者展示了肝脏 Xenium–DESI、乳腺 Xenium–H&E、胸腺 Stereo-CITE-seq 和 3D 肝脏切片。图中能直接看到肝脏的对照梯度图与统计图、乳腺的分叉树、胸腺层状地图及 3D 堆叠展示（`figure_02.jpg`–`figure_05.jpg`）。肝脏参照来自抗体标记与反应扩散式代理轴，胸腺参照来自 marker-based CMA；指标包括 Spearman、RMSE、AP/ROC、聚类指标和 Moran’s I（`paper.md:539-581`）。

### 复现时应注意的边界

HTML 转换还丢失了部分公式；若要严谨重现 ELBO 或完整概率模型，应以 `article.source.xml` 或原始论文为准，而不是补猜 Markdown 中缺失的公式。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## LYNX — summary

LYNX is a conditional, heterogeneous-graph variational model for paired spatial modalities with unequal resolution or disjoint features. It learns a patch/niche latent conditioned on the auxiliary modality, deterministically transfers that context to primary cells, reconstructs the primary modality, and uses the learned manifold for gradients, zones, feature dynamics, and local edge-weight summaries (`paper.md:36-56,239-260`).

The paper targets two limits of common spatial workflows: discrete-domain analyses can miss continuous organization, and equal-weight multimodal integration can be brittle when modalities have different resolution, features, and technical artifacts (`paper.md:15-28`). LYNX addresses this with registered within-/cross-modal graph edges, cross-modal GAT inference, an auxiliary-conditioned latent prior, and an optional baseline-plus-neighbor-residual decoder. The edge score $\omega$ is distance regularized and aggregated by sender cell type, but it is not a ligand–receptor or causal estimate (`paper.md:289-298,415-421`).

The authors evaluate liver Xenium–DESI (60,562 cells and 9,564 metabolite pixels after preprocessing), breast Xenium–histology, mouse thymus Stereo-CITE-seq, and a serial-section 3D liver setting (`paper.md:430-466`). Figures visibly show comparative gradient maps, proxy-ground-truth benchmarks, branching breast trajectories, thymus layer maps, and auxiliary-modality ablations (`figure_02.jpg`–`figure_05.jpg`, `figure_13.jpg`). The paper evaluates liver with antibody-derived reference gradients and thymus with a marker-derived cortico-medullary axis, using Spearman correlation, RMSE, AP/ROC, clustering metrics, and Moran’s I (`paper.md:539-581`).

Reproducibility is promising but incomplete in this workspace: the package snapshot includes the central model, application scripts, tests, and documentation, and the paper points to a separate reproducibility repository (`paper.md:614-617`). This analysis verified the central code path statically, not by an end-to-end data run. Exact equation transcription is also limited because several math expressions were dropped during HTML conversion; consult `article.source.xml` or the canonical article before reproducing formula-level details.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
