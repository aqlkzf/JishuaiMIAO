---
layout: default
permalink: /paper-atlas/giottosuite-46919789/
title: "GiottoSuite"
nav: false
wide: true
description: "Giotto Suite 解决的是空间组学数据“尺度、模态和格式不统一”的工程问题。它把转录本点、细胞/细胞核/spot/网格多边形、组织图像、表达矩阵、空间图和多组学结果组织到同一个 R 生态框架中，让研究者可以在不同空间单位和特征模态之间聚合、比较、整合和导出数据。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>GiottoSuite</h1>
    <p>Giotto Suite: a multiscale and technology-agnostic spatial multiomics analysis ecosystem</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02817-w" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GiottoSuite">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/giotto-suite/Giotto" target="_blank" rel="noopener noreferrer" aria-label="Open code for GiottoSuite">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Giotto Suite 方法中文解读

### 一句话概览

Giotto Suite 解决的是空间组学数据“尺度、模态和格式不统一”的工程问题。它把转录本点、细胞/细胞核/spot/网格多边形、组织图像、表达矩阵、空间图和多组学结果组织到同一个 R 生态框架中，让研究者可以在不同空间单位和特征模态之间聚合、比较、整合和导出数据。

### 1. 生物学问题与建模目标

空间组学实验会同时产生坐标、图像、分割边界、表达矩阵和多模态测量。生物学解释常常取决于“用哪个空间单位看”：细胞核、细胞、邻域、组织区域或伪 Visium spot 得到的结果可能不同。Giotto Suite 的目标不是学习一个新的生物学模型，而是提供一个可扩展的数据框架，使这些空间证据能被系统地表示、聚合、分析和复用。

它支持的解释包括空间聚类、细胞类型组成、亚细胞定位、RNA-蛋白空间相关、多组学整合和大规模空间图谱探索。它不能直接证明因果关系，也不能自动判断哪个分割结果是真实边界。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 特征类型 | `feat_type` | RNA、protein、ATAC、image intensity 等模态轴 | `doc_code.md` |
| 空间单位 | `spat_unit` | nucleus、cell、spot、bin、domain 等观察单位 | `doc_code.md` |
| 点数据 | `giottoPoints` | 转录本或其他点状空间特征 | `GiottoClass/R/classes-points.R:7-31` |
| 多边形 | `giottoPolygon` | 分割边界、网格、组织区域 | `GiottoClass/R/classes-polygons.R:7-34` |
| 图像 | `giottoLargeImage` | H&E、DAPI、IF 等 raster 图像 | `GiottoClass/R/classes-images.R:54-105` |
| 核心对象 | `giotto` | 统一存储矩阵、空间、图像、网络、降维和 multiomics 结果 | `GiottoClass/R/classes.R:330-386` |

### 3. 方法主流程

1. 读取原始平台输出：表达矩阵、转录本坐标、分割多边形、组织图像和元数据。
2. 用 `createGiottoObject()` 或平台导入函数创建 `giotto` 对象。
3. 按 feature type 和 spatial unit 组织数据，使同一对象能保存 RNA-at-cell、RNA-at-nucleus、protein-at-cell 等组合。
4. 用 `calculateOverlap()` 计算点/图像与多边形的空间重叠，再用 `overlapToMatrix()` 转成矩阵。
5. 对矩阵运行过滤、归一化、空间网络、PCA/UMAP、聚类和富集分析。
6. 对相邻切片或不同模态用 landmark 估计 affine transform，进行空间配准。
7. 对 RNA+protein 或 RNA+ATAC 等多组学数据运行 WNN，生成 integrated UMAP 和 integrated clusters。
9. 将结果导出到 Seurat、AnnData、SpatialExperiment、SpatialData、sf、terra、stars 等生态。

### 4. 数学目标与直觉

空间聚合可以理解为：

$$
M_{fu} = \sum_{p \in f} \mathbf{1}[p \cap u]
$$

其中 $f$ 是特征，$u$ 是空间单位，$p$ 是转录本点或图像像素/强度元素。这个矩阵把几何证据转成可分析的表达或强度矩阵。

配准使用 affine transform：

$$
\tilde{x}_{target} = A \tilde{x}_{source}
$$

它依赖人工或预存 landmarks。这个假设适合近似相邻切片对齐，但不能保证处理所有非线性组织形变。

WNN 部分用每个模态的 PCA/KNN 估计细胞特异的模态权重，再构建加权图。代码可验证的是 `runWNN()` 计算权重矩阵并存入 `multiomics` slot，`runIntegratedUMAP()` 再从该图生成 integrated kNN/UMAP。

### 5. 代码实现对照

| 论文步骤/概念 | 代码位置 | 实现行为 | 匹配程度 |
|---|---|---|---|
| 核心对象模型 | `GiottoClass/R/classes.R:330-386` | 定义表达、空间、图像、网络、multiomics 等 slot | 精确匹配 |
| 点/多边形/图像类 | `classes-points.R`, `classes-polygons.R`, `classes-images.R` | 用 terra-backed 结构存空间数据 | 精确匹配 |
| 空间聚合 | `GiottoClass/R/aggregate.R:248-320`, `1693-1738` | 计算 overlap 并转矩阵 | 精确匹配 |
| WNN 整合 | `Giotto/R/wnn.R:16-419` | 计算模态权重和 weighted graph | 精确匹配 |
| 大数据投影 | `Giotto/R/dimension_reduction.R:807-930`, `2763-2974` | 子集拟合 PCA/UMAP 并投影剩余单位 | 精确匹配 |
| GiottoDB | `Figure_6.R`, `aggregate.R:560-582` | 脚本使用 DB proxy，GiottoClass 委托 GiottoDB | 部分匹配，源码缺失 |

### 6. 结果如何解读

Figure 1 说明框架和包结构；Figure 2 证明同一数据可在 nucleus/cell/neighborhood/domain 等尺度分析；Figure 3 展示相邻多模态切片配准和 RNA-蛋白空间相关；Figure 4 强调分割策略会显著改变下游注释；Figure 5 展示 WNN 多组学整合；Figure 6 展示大规模 Stereo-seq 数据的数据库、HDF5 和投影式处理。

这些结果支持“Giotto Suite 是一个灵活的空间多组学分析生态”。但它们主要是可行性和工作流展示，不是对所有模块的速度/内存/准确率系统 benchmark。

### 7. 局限性与未验证部分

- 论文引用 Giotto Suite 4.2.1，本地克隆的 `Giotto` 是 4.2.3。
- 主图脚本存在，但依赖外部大数据、路径设置、可选包、预构建对象和 landmarks。
- 转换器存在，但多尺度层级结构和图像信息不一定能无损往返。
- 输出更适合作为空间生物学假设生成和工作流工程，不应直接当作因果验证。

### 8. 快速阅读路线

1. `summary.md`：快速了解论文目的、贡献和复现性。
2. `doc_method.md`：理解完整计算框架和数学直觉。
3. `doc_code.md`：查看论文步骤与本地源码的对应关系。
4. `figure_analysis.md`：按主图理解每个实验支持什么结论。
5. `claude_notes.md`：查证据表、开放问题和缺失代码证据。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Giotto Suite Summary

### Motivation and Novelty

Giotto Suite targets a practical bottleneck in spatial biology: modern assays generate heterogeneous evidence at incompatible scales, including transcript points, segmentation polygons, spatial spots, tissue domains, images, adjacent sections, and multiple molecular modalities. Existing tools often handle one platform, one spatial unit, or one ecosystem well, but researchers need an extensible framework that can represent, aggregate, compare, integrate, and export many spatial data types.

The novelty is a technology-agnostic R software ecosystem centered on feature types and spatial units. Giotto Suite stores points, polygons, images, matrices, reductions, networks, and multiomics results in a unified framework, then supports downstream workflows for multiscale analysis, segmentation comparison, multimodal registration, WNN integration, large-data projection, and interoperability.

### Method Overview

Giotto Suite is a data framework and workflow ecosystem rather than a new predictive model. Its core steps are:

1. Ingest raw platform outputs: expression matrices, transcript coordinates, segmentation polygons, images, metadata, and annotations.
2. Convert them into Giotto subobjects such as `exprObj`, `giottoPoints`, `giottoPolygon`, and `giottoLargeImage`.
3. Organize data by feature type and spatial unit.
4. Aggregate spatial evidence with `calculateOverlap()` and `overlapToMatrix()`.
5. Run preprocessing, spatial networks, PCA/UMAP, clustering, enrichment, spatial statistics, registration, WNN integration, or deconvolution.
6. Scale large data with database/HDF5/projection workflows where available.
7. Export to AnnData, Seurat, SpatialExperiment, SpatialData, sf, terra, stars, and related ecosystems.

### Evaluation

The paper demonstrates Giotto Suite across several spatial technologies and biological use cases:

| Area | Evidence | Interpretation |
|---|---|---|
| Multiscale spatial units | MERFISH breast cancer and mouse brain examples | Giotto can compare nucleus/cell/neighborhood/domain and subcellular localization. |
| Multimodal registration | Xenium, Visium, H&E, IF breast cancer data | Registered modalities can be jointly visualized and quantified. |
| Segmentation sensitivity | Original vs Baysor and other segmentation methods | Segmentation changes cell counts, polygon areas, and annotation composition. |
| Multiomics integration | RNA+protein and RNA+ATAC examples | WNN integration can produce integrated spatial clusters. |
| Scalability | Stereo-seq MOSTA embryo workflow | DB/HDF5/projection paths support large spatial maps and clusters. |
| Interoperability | Seurat, AnnData, SpatialExperiment, SpatialData, R-spatial converters | Broad ecosystem bridges are implemented, but not guaranteed lossless. |

Compared methods/tools discussed include original Giotto (Genome Biology 2021), SpatialData (Nature Methods 2025), Squidpy (Nature Methods 2022), Voyager/SpatialFeatureExperiment, Seurat/WNN (Cell 2019/2021), Cellpose, Baysor, Mesmer, StarDist, and registration/deconvolution tools such as spatialDWLS.

### Reproducibility

Rating: **4 / 5**.

Positive evidence: public package code and manuscript scripts are available; key framework functions have direct code matches; main figures have corresponding scripts; object model, WNN, converters, overlap operations, and projection functions are locally verifiable.

Limitations: the acquired package is `Giotto` 4.2.3 while the paper cites 4.2.1; GiottoDB source is not included in this workspace; manuscript scripts are not fully self-contained and require external datasets, local path setup, optional packages, and sometimes manual landmarks or prebuilt outputs. The paper demonstrates scalability but does not provide a controlled runtime/memory benchmark against alternatives.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
