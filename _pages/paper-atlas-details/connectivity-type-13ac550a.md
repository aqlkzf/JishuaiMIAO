---
layout: default
permalink: /paper-atlas/connectivity-type-13ac550a/
title: "Connectivity_Type"
nav: false
wide: true
description: "神经元通常按胞体所在脑区、形态、电生理或转录组分类，但这些属性并不直接描述它“可能连接到哪里”。电子显微镜可以识别真实突触，却还难以覆盖整个小鼠脑。本文提出一个折中方案：把已经配准到统一脑图谱的轴突和树突形态转成“潜在连接”特征，再用它区分神经元类型和亚型。 这里的连接不是实测突触。它表示单个神经元的轴突空间与群体树突区域发生重叠，因此更准确的名称是“潜在连接”。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Connectivity_Type</h1>
    <p>Connectivity of single neurons classifies cell subtypes in mouse brains</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/YunZhixi98/Connectivity_Type" target="_blank" rel="noopener noreferrer" aria-label="Open code for Connectivity_Type">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 用单神经元连接特征划分小鼠脑细胞亚型

### 论文要解决什么问题？

神经元通常按胞体所在脑区、形态、电生理或转录组分类，但这些属性并不直接描述它“可能连接到哪里”。电子显微镜可以识别真实突触，却还难以覆盖整个小鼠脑。本文提出一个折中方案：把已经配准到统一脑图谱的轴突和树突形态转成“潜在连接”特征，再用它区分神经元类型和亚型。

这里的连接不是实测突触。它表示单个神经元的轴突空间与群体树突区域发生重叠，因此更准确的名称是“潜在连接”。

### 数据与输出

研究汇总了 20,158 个 CCFv3 配准神经元，包括 9,298 个具有轴突的重建和 10,860 个新生成的树突重建。每个轴突神经元最终得到一个 150 维连接条形码；每一维表示该轴突与某个树突树突域的体素重叠量。

- `s-type`：按胞体所在解剖区域定义的类型。
- `m-type`：按单细胞形态特征聚类得到的类型。
- `c-feature`：轴突与各树突域的重叠特征。
- `c-type`：按连接特征区分出的连接亚型。

### 方法主线

```text
多来源神经元重建
  -> 重采样并配准到 CCFv3
  -> 在每个胞体类型内汇总 SWC 节点
  -> GMM 将节点分成 1–9 个空间簇（最大 BIC）
  -> 用 alpha-shape(alpha=0.4) 包围每个空间簇
  -> 含胞体的形状定义为树突域
  -> 把树突域和单神经元轴突体素化
  -> 计算轴突与所有树突域的重叠体积
  -> 得到 150 维连接条形码
  -> 类型比较、空间加权聚类和跨模态验证
```

#### 1. 建立统一坐标系

不同来源的轴突、树突和完整神经元分别按指定间距重采样，再映射到 25 μm 分辨率的 CCFv3。新产生的 DEN-SEU 树突先用 APP2 在六个背景阈值下生成候选，经过形态特征范围筛选和人工检查后保留 10,860 个重建。

#### 2. 从节点云学习树突域

作者把同一胞体区域内的 SWC 坐标汇总，用 Mclust 比较不同高斯混合模型。每个区域选择 BIC 最大的模型和 1–9 之间的簇数。随后用三维 α-shape 把每个簇包围起来；包含相应胞体的形状被视为树突域。

#### 3. 把空间重叠变成连接条形码

树突域和单神经元形状都被转换为三维掩膜。一个轴突与某个树突域重叠的体素数，就是对应的连接特征。75 个双侧树突域形成 150 维向量。这个向量描述“轴突可能接触哪些群体树突区域”，而不是具体突触或具体靶细胞。

#### 4. 比较形态与连接的区分能力

论文用 SVM、UMAP 以及 m/c-score 比较两类特征。m/c-score 同时考虑类间距离和类内距离：

$$
{\mathrm{m}}/{\text{c}}\,\text{score}=\exp\left(-\frac{2\times {\mathrm{Dist}}_{\mathrm{interclass}}}{\frac{1}{2}\times\left({\mathrm{Dist}}_{\mathrm{intraclass}(1)}+{\mathrm{Dist}}_{\mathrm{intraclass}(2)}\right)}\right).
$$

在 31 个胞体类型中，76% 的 c-score/m-score 小于 1；在形态特别相似的类型组合中，这一比例为 99%。图 2 和图 3 直观显示，加入连接特征后，许多形态混合的类型明显分开。

#### 5. 在同一脑区内寻找亚型

同一 s-type 内，作者同时考虑连接相似性和胞体位置。连接矩阵 $M_C$ 使用余弦相似度；胞体距离矩阵 $M_D$ 被转成高斯邻近度：

$$
M_{DA}=\exp(-M_D\times M_D).
$$

随后聚类 $M_C\odot M_{DA}$。这样，连接模式相似且在解剖上相邻的神经元更容易被分到同一亚型。论文还用 PCA、kNN、Jaccard 权重和 Louvain 分辨率扫描比较不同模态的模块性。

#### 6. 与其他尺度和模态比较

Neuron-beta 衡量单神经元投射与群体尺度投射的一致性：

$$
\text{Neuron-beta}=\frac{\mathrm{Cov}(M,S)}{\mathrm{Var}(M)}.
$$

研究还将连接亚型与转录组、电生理和形态结构比较。结果通常不是完全重合，而是说明连接提供了一个互补的分类维度。

### 主要结果如何理解？

连接特征能区分许多形态相似的神经元，并在 CP、MOs、视觉丘脑和丘脑—皮层通路中产生具有空间或投射差异的亚型。最重要的结论不是“连接取代其他细胞类型”，而是连接信息补充了胞体位置、形态、分子和电生理分类。

### 局限与复现性

潜在连接依赖空间重叠，可能把没有形成突触的邻近结构计为连接。结果还受样本不均衡、重建完整性、配准误差、GMM 和 α-shape 参数影响。

公开代码能够验证形态特征、相似度、空间高斯权重、PCA/kNN/Jaccard/Louvain 和 Neuron-beta 等下游逻辑，但多数 notebook 使用缺失的 `Materials` 目录和硬编码 Windows 路径。APP2/mBrainAligner 调度、Mclust、α-shape/binvox 以及原始重叠矩阵生成脚本没有在仓库中找到，因此目前无法从原始数据一键重现完整连接条形码流程。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Connectivity of single neurons classifies cell subtypes in mouse brains

### Overview

This Nature Methods 2025 study introduces a whole-brain framework for classifying mouse neurons by potential connectivity. It aggregates 20,158 CCFv3-registered neuron reconstructions, learns population-level dendritic arbor domains, and represents each axon-bearing neuron by its spatial overlap with those domains. The resulting 150-dimensional connectivity barcode defines connectivity features (`c-features`) and connectivity subtypes (`c-types`).

### Why connectivity features?

Conventional neuron typing uses soma anatomy, morphology, electrophysiology or molecular state. Morphology alone can leave anatomically distinct neuron groups strongly overlapping, while synapse-resolved electron microscopy has not scaled to the whole mouse brain. The proposed compromise uses registered axonal and dendritic geometry to infer connection opportunities at single-neuron resolution.

The method pools SWC nodes within anatomical soma types, fits Gaussian mixture models, wraps node clusters in 3D α-shapes and retains soma-containing shapes as dendritic domains. Voxel overlap between one neuron's axonal arbor and every dendritic domain forms its connectivity barcode. Within an anatomical region, cosine connectivity similarity can be multiplied by a Gaussian affinity derived from soma distance before clustering.

### Main evidence

- The database combines 9,298 neurons with axons and 10,860 dendritic reconstructions; 26,205 axonal and 20,158 dendritic arbors are analyzed.
- Adding connectivity PCs sharply reduces SVM overlap among MOp, SUB and VPL neurons that overlap in morphology space.
- Across 31 soma types, 76% of c-score/m-score entries are below one; among morphology-similar cohorts, 99% are below one. Wilcoxon comparisons of classification overlap favor connectivity features for both s-types ($P=2.5\times10^{-7}$) and c-types ($P<2.2\times10^{-16}$).
- Connectivity similarity is more strongly related to soma geography than morphology similarity, motivating distance-weighted subtype clustering.
- Case studies resolve spatially and projection-distinct subtypes in CP, MOs and thalamic nuclei, and show partial correspondence with transcriptomic, electrophysiological and mesoscale projection structure.

### Interpretation and limitations

The output is a potential-connectivity map, not a measured synaptic connectome. Axon–dendrite spatial overlap can overestimate connection probability, and pooled dendritic domains do not identify specific postsynaptic cells. Results depend on reconstruction completeness, multisource sampling, registration quality, GMM/α-shape choices and regional sample density. The authors frame c-types as a complementary axis rather than a replacement for transcriptomic, electrophysiological or morphology-based types.

### Reproducibility

Code is public at `YunZhixi98/Connectivity_Type`, and the analyzed snapshot is commit `76486222ab37977fc1fb3c0f1c6f58288201feec`. The repository directly supports several downstream computations: SWC morphology helpers, feature similarities, Gaussian spatial weighting, PCA/kNN/Jaccard/Louvain analysis and Neuron-beta. Overall code-paper fidelity is **medium**.

Independent end-to-end rerunning is currently difficult. The repository consists mainly of figure notebooks with hard-coded Windows paths to an absent `Materials` directory. Scripts for APP2/mBrainAligner orchestration, Mclust GMM fitting, α-shape/binvox voxelization and raw overlap-matrix generation were not found. The Zenodo data resource may supply large inputs, but environment setup and upstream workflow reconstruction are still required. Reproducibility rating: **2.5/5**—substantial downstream logic is inspectable, while the core raw-to-barcode pipeline is incomplete.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
