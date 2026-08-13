---
layout: default
permalink: /paper-atlas/mousemapper-43b895fa/
title: "MouseMapper"
nav: false
description: "MouseMapper 面对的是几十万张切片、数十万亿体素的全身光片显微镜数据。它的目标不是在一块裁剪图里找到一个目标，而是沿整只小鼠保持三维连续性，同时回答三个问题：神经在哪里、免疫细胞簇在哪里、这些结构属于哪个器官或组织。 因此 MouseMapper 不是一个单独网络，而是由 Nerve-Module、Immune-Module 和 Tissue-Module 组成的流水线，再由量化与图分析把三类输出合并。"
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
      <span>Representation Models</span>
      <span>Nature · 2026</span>
    </div>
    <h1>MouseMapper</h1>
    <p>A deep-learning framework reveals whole-body perturbations at cell level</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-026-10535-2" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for MouseMapper">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/erturklab/mouseMapper" target="_blank" rel="noopener noreferrer" aria-label="Open code for MouseMapper">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MouseMapper：把整只透明小鼠变成可比较的神经、炎症与解剖地图

### 方法要解决的不是“小图分割”

MouseMapper 面对的是几十万张切片、数十万亿体素的全身光片显微镜数据。它的目标不是在一块裁剪图里找到一个目标，而是沿整只小鼠保持三维连续性，同时回答三个问题：神经在哪里、免疫细胞簇在哪里、这些结构属于哪个器官或组织。

因此 MouseMapper 不是一个单独网络，而是由 Nerve-Module、Immune-Module 和 Tissue-Module 组成的流水线，再由量化与图分析把三类输出合并。论文用高脂饮食（HFD）肥胖模型展示它如何发现眶下神经分支减少和器官特异的 CD68 阳性炎症簇变化。

### 从实验样本到计算输入

作者使用 vDISCO 透明化和光片荧光显微镜（LSFM）成像。Uchl1-eGFP 报告小鼠显示外周神经，Cd68-eGFP 报告小鼠显示单核/巨噬细胞相关信号；自发荧光（AF）和碘化丙啶（PI）通道提供器官与组织边界。1.1× 扫描覆盖全身，4× 扫描提供更细轴突和细胞结构。

这些输入并非普通二维图片。论文的 9 个 1× Uchl1 全身扫描包含约 10.926 万亿体素，10 个 1× Cd68 扫描包含约 10.779 万亿体素；完整训练、推理和量化依赖 HPC。代码因而用 Zarr 分块、Dask 懒加载和三维滑动窗口，避免把整只动物一次装入内存。

### 三个模块与一条公共主线

```text
全身 LSFM 体数据
  ├─ Nerve-Module  -> 神经二值掩膜 -> 密度与神经图
  ├─ Immune-Module -> CD68 掩膜   -> 三维连通簇与大小类别
  └─ Tissue-Module -> 器官图 + 软组织图
                         ↓
           按器官/组织定位并比较 chow 与 HFD
```

三个模块共享的关键思想是：训练时使用人工三维标注，推理时在全身数据上逐块预测并拼接，最后用解剖掩膜把结构变化放回具体器官和组织。

### Nerve-Module：从血管基础模型迁移到神经

#### 为什么 VesselFM 能用于神经

神经和血管都是细长、分支、跨大尺度延伸的三维结构。作者以预训练的 3D 血管分割基础模型 VesselFM 为起点，用 VR 标注的神经体数据微调。论文使用 learning without forgetting（LwF）：

$$
\mathcal L
=\mathcal L_{\text{nerve-seg}}
+\lambda\mathcal L_{\text{distill}},
$$

其中第一项是 nerve segmentation 的 Cross Entropy + Dice loss，第二项是微调模型与冻结 VesselFM 输出之间的 KL divergence；$\lambda=0.4$。直观上，模型既要学会神经标签，又不能完全忘掉预训练中对细长三维结构的表示。

论文训练 patch 为 $128^3$，初始学习率 $10^{-3}$，SGD，训练 1,250 epochs。训练/测试时按 0.5 与 99.5 百分位裁剪强度再做 min–max 归一化。最终 Nerve-Module 报告 voxel Dice 0.7494，并在不同标记、分辨率和人胚数据上测试泛化。

#### 全身推理如何落地

本地 `mouseMapper/Nerve_Module/inference/sliding_window_inferer_zarr.py` 实现 Zarr/Dask 懒加载、重叠三维窗口、边界 padding 和输出拼接。实际窗口大小由推理入口与可用显存决定；仓库示例并不等同于论文训练 patch 的固定 $128^3$，不要混淆训练与推理尺寸。

推理得到神经掩膜后，`quantification_nerve.py` 逐 z-slice 累加：

$$
\text{nerve density}
=\frac{\text{nerve-positive voxels}}
{\text{mask voxels}}.
$$

分母可为整身、组织或器官掩膜。代码直接保存 nerve voxel 与 mask voxel 计数；比值和组间统计可在下游完成。论文还把器官掩膜向外延伸 500 μm，以包含紧邻器官的神经，并对头部和四肢做了部分人工边界修订。

### Tissue-Module：形状与纹理分开处理

器官和软组织需要不同分辨率。内部器官的整体形状在下采样后仍清楚，因此先把 AF/PI 通道下采样到约 $59\times59\times60$ μm/voxel，用 3D U-Net 分割 27 个内部器官。器官模型使用 8 只标注小鼠、五折交叉验证和 5 模型 ensemble。

脂肪、肌肉、骨和骨髓依赖高分辨率纹理，因此器官掩膜上采样回原分辨率后，先排除内部器官，再对剩余全分辨率体数据运行软组织滑窗模型。器官图和组织图合并后形成论文所说的 31 个器官/组织类别。

这不是一个“31 类单头网络”。31 类地图是低分辨率器官分支和全分辨率组织分支的组合结果。代码 `Tissue_Module/utils.py`、`Organ_Segmentation.ipynb` 和公共滑窗脚本反映了这种操作式流水线。

### Immune-Module：分割之后还要把信号变成炎症簇

Immune-Module 同样微调 VesselFM，但冻结 encoder、只微调 decoder。论文的训练 patch 为 $128^3$，SGD、channel-wise z-score normalization、五折交叉验证；最佳模型用初始学习率 0.01 微调 500 epochs，报告 voxel Dice 0.7878。

二值 CD68 掩膜还不是 Figure 5 的最终读数。论文用 cc3d 做三维 connected components，为每个 component 保存位置、体积、质心和形状；按质心分配到器官/组织，丢弃不在解剖掩膜内的候选和细长的血管/神经样伪阳性。

真正的大小类别按分割体素数定义：

- small：小于 50 voxels；
- medium：50–500 voxels；
- large：大于 500 voxels。

这些阈值不是细胞数，也不是模型学习出的类别。作者选择它们，使三类各自约占全体 CD68 分割体积的 30%。随后在每个器官/组织内比较三类所占比例。

本地 `Immune_Module/cut_volume_and_extract_blobs_zarr.py` 把 Zarr 切成可并行处理的 patch，并把局部坐标还原为全局坐标；`blobanalysis.py` 计算 volume、center of mass、bounding box、compactness 和 sphereness 等几何量。论文中最终的解剖过滤、大小统计与组间检验是这些底层对象之上的分析步骤。

### 神经图：为什么密度下降还不够

神经密度只能告诉我们“总体信号少了”，不能区分神经变细和分支丢失。MouseMapper 对分割掩膜做 skeletonization 和 depth map，分块提取图后合并边界节点。每个图节点/边带有半径或厚度信息，节点 degree 用于识别叶节点：degree=1 的节点是末端候选。

`graph_postprocessing.py:get_end_nodes()` 直接从 VTP 的 lines 建 NetworkX 图，记录 `end_nodes` 和节点 degree；`preprocess_masks()` 用距离变换与 watershed 向外生长器官标签，再把图节点映射到器官。

Figure 3 中 HFD 小鼠眶下神经的 endings、edges 和 vertices 减少，而最大厚度没有显著下降。这组合证据更符合 arborization/分支复杂度丢失，而不是单纯整体变细。

### 五张主图怎样连成一条证据链

#### Figure 1：先证明信号能在全身连续可见

图 1 展示 vDISCO 后的 Uchl1-eGFP 神经和 Cd68-eGFP 免疫信号。HFD 小鼠的免疫信号在肝脏和内脏脂肪等区域更突出。该图主要是成像与研究设计证据，不是分割准确率评估。

#### Figure 2：三个模块如何合流

图 2a 是全系统：神经、组织、免疫模块进入 Quantification-Module。图 2b-c 展示 VR 标注、网络输出和 TP/FP/FN。图 2d 明确画出器官图与组织图合并为 mouse map，支持“两级 Tissue-Module”解释。

#### Figure 3：全身筛查定位到眶下神经

全身神经密度比较把显著变化定位到 head；随后对三叉神经眶下支做局部图分析。末端、边和顶点显著减少，厚度不显著改变。这里的局部结果来自全身筛查后的重点区域，不应说成所有外周神经都一致退化。

#### Figure 4：结构改变是否有功能和分子对应

HFD 小鼠 whisker nuisance score 降低，连接到眶下感觉功能。DISCO-MS 对小鼠三叉神经节做蛋白组分析，并在人类 lean/obese 三叉神经节数据中检查相似通路；actin cytoskeleton、axon guidance、complement/innate immune 等变化把结构表型连接到分子层。人鼠结果是通路层的对应，不等同于每个蛋白一一复制。

#### Figure 5：炎症不是全身均匀增加

三维 CD68 component 被分成 small/medium/large 并定位到具体组织。HFD 改变多种器官/组织中的 cluster 比例，但方向和显著性并不完全相同。图支持“器官特异的炎症重塑”，比笼统的“全身炎症都升高”更准确。

### 论文与本地代码的匹配边界

本地代码包含 Nerve、Immune、Tissue、graph 和滑窗推理模块，核心数据流与论文直接对应。

仓库不是单命令复现包：训练与分析分散在 Python、notebook、Voreen/pi2 外部工具和模型权重之间；论文全套统计、蛋白组与行为分析也不都在此代码目录。模型 ZIP/视频中的小文件是 Git LFS pointer，而非实际权重或视频内容，因此不能声称工作区可离线端到端重跑论文。

### 最容易误读的四点

1. 31 类解剖图来自 27 器官与软组织分支组合，不是单一 31 类网络。
2. immune cluster 大小是体素阈值，不是细胞数。
3. 神经 endings/edges/vertices 依赖分割、骨架化和分块图合并，误差会逐级传播。
4. “无需重训练的泛化”只在论文测试的标记、分辨率和组织范围内成立；论文也要求新组织的 CD68 结果经目视与 VR Dice>60% 验证。

因此，使用 MouseMapper 时应同时报告输入标记与分辨率、所用模型/权重、滑窗与归一化设置、解剖掩膜生成方式，以及后处理阈值。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MouseMapper Summary

### Motivation & Novelty

MouseMapper targets a real limitation in whole-body pathology imaging: you could see intact mouse bodies, but you could not consistently quantify nerves, immune clusters, and organ context across the same specimen. Prior methods cited by the paper were narrower: DeepMACT (Cell, 2019) for metastasis, DELiVR (Nature Methods, 2024) for whole brain, AIMOS (Nature Communications, 2020) for a handful of organs, and SCP-Nano (Nature Biotechnology, 2025) for specific targeting tasks. MouseMapper’s novelty is the combination of a foundation-model-derived nerve segmenter, an immune-cell blob pipeline, and a tissue/organ atlas for body-wide normalization.

### Method Overview

The workflow is straightforward: clear and image the mouse, segment nerves and immune cells with separate models, map structures to organs and tissues, and turn segmentations into density or graph-based readouts. The paper’s strongest design choice is modularity. It lets the same raw body scan support nerve arborization analysis, immune-cluster analysis, and organ-localized quantification.

### Evaluation

The paper validates the system on obesity in Uchl1-eGFP and Cd68-eGFP mice, plus human trigeminal ganglia for the proteomics bridge. Figure 2 establishes segmentation quality and generalization using voxel Dice for nerves and immune cells, including a reported nerve Dice of 0.7494 and immune Dice of 0.7878. Figure 3 shows reduced nerve density and infraorbital arborization through density, endings, edges, vertices, and thickness metrics. Figure 4 ties that phenotype to whisker stimulation deficits, differentially regulated proteins, and pathway enrichment in trigeminal ganglia. Figure 5 shows tissue-specific inflammation remodeling via small, medium, and large CD68 cluster proportions across organs.

### Reproducibility

Rating: 3/5.

The code is real and organized, but it is closer to an operational repo than a turnkey library. Core inference paths are present, and the repo documents checkpoint loading and preprocessing. What is missing from the visible tree is a clean end-to-end training/evaluation harness for all reported benchmarks, so reproducing the paper exactly would still require notebook work, data access, and some setup churn.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
