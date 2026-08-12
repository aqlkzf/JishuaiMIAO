---
layout: default
permalink: /paper-atlas/vitessce-ebc00d83/
title: "Vitessce"
nav: false
description: "单细胞与空间组学实验常常同时产生多种对象和数据：细胞或细胞核、空间 spot、分子坐标、基因表达、蛋白丰度、染色质可及性、显微图像、分割掩膜、聚类和细胞类型注释。真正做探索时，研究者需要不断在“物理空间、表达空间、降维空间和基因组位置”之间切换。 论文指出，当时的工具大多只覆盖其中一部分： Cellxgene（bioRxiv，2021）、Cirrocumulus/Cumulus（Nature Methods，2020）和 Pagoda2…"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>Vitessce</h1>
    <p>Vitessce: integrative visualization of multimodal and spatially resolved single-cell data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Vitessce 方法详解

### 1. 它要解决什么问题？

单细胞与空间组学实验常常同时产生多种对象和数据：细胞或细胞核、空间 spot、分子坐标、基因表达、蛋白丰度、染色质可及性、显微图像、分割掩膜、聚类和细胞类型注释。真正做探索时，研究者需要不断在“物理空间、表达空间、降维空间和基因组位置”之间切换。

论文指出，当时的工具大多只覆盖其中一部分：

- Cellxgene（bioRxiv，2021）、Cirrocumulus/Cumulus（Nature Methods，2020）和 Pagoda2 所基于的方法（Nature Methods，2014）擅长大规模转录组矩阵、散点图和热图，但不以空间分割或基因组轨迹为核心。
- TissUUmaps 3（Heliyon，2023）和 Napari-SpatialData/SpatialData（Nature Methods，2024）面向空间数据，却不提供同等完整的非空间组学和基因组映射视图。

Vitessce 的目标不是再做一个新的聚类、降维或多模态对齐算法，而是提供一个统一的交互式可视化框架，把已经计算好的多模态结果放进同一个、可联动的分析界面中（`paper.md:21-27,46`）。

### 2. 核心思想

Vitessce 的关键不是某一种图，而是三个彼此解耦的层次：

1. **数据层**：数据集由若干文件定义；文件可以是 AnnData、MuData、SpatialData、OME-TIFF、OME-Zarr、CSV、JSON 等格式，并暴露抽象数据类型，例如表达矩阵、embedding、空间坐标、图像或细胞集合。
2. **视图层**：散点图、空间图、热图、基因组浏览器、分布图和控制视图是相互独立的 React 组件。
3. **协调层**：视图不直接互相调用，而是通过配置中的“协调类型”和“协调作用域”共享状态。

可以把协调作用域理解成一个有名字的共享变量。例如，两个视图都把 `featureSelection` 连接到作用域 `A`，那么它们读取和修改的是同一个“当前选择基因”。若另一个视图连接到作用域 `B`，它就保持独立。

这种设计带来两个重要结果：

- 联动关系可以用 JSON 保存、复制和通过 URL 分享。
- 新视图只需遵守协调和数据加载接口，不需要了解其他视图的内部实现。

### 3. 多模态数据如何被统一描述？

Vitessce 使用三个语义轴：

- 观测类型 $o$：cell、nucleus、spot、molecule 等。
- 特征类型 $f$：gene、protein、peak 等。
- 特征值类型 $v$：expression、count、intensity 等。

一个视图请求某种抽象数据类型时，还可以声明它关心的 $o/f/v$ 条件。补充材料给出了一个“部分匹配”规则。设视图为 $V$，文件为 $F$，请求的数据类型为 $d$，视图和文件的协调值映射分别为 $C_V$ 与 $C_F$：

$$
\operatorname{match}(V,d,F)=
[V.\mathrm{dataset}=\operatorname{dataset}(F)]\land
[d=\operatorname{datatype}(F)]\land
\bigwedge_{k\in\mathrm{keys}(C_V)}[C_F(k)=C_V(k)].
$$

直观上说：数据集和数据类型必须一致；视图提出的所有条件都必须被文件满足；文件可以带有额外信息。代码中的 `getMatchingLoader` 正是按 dataset、data type 建立索引，再用 `isMatch(fileCoordinationValues, viewCoordinationValues)` 做这种非对称匹配（`packages/vit-s/src/state/hooks.js:970-1003`）。

例如，三个矩阵可以分别表示 cell×gene、cell×peak 和 nucleus×gene。热图可以通过 observation type 与 feature type 精确选择其中一个；而基因列表只关心 feature type，因此可以同时服务于两个以 gene 为特征的热图（`supp.md:98-118`）。

### 4. 从配置到交互界面的完整流程

```text
外部完成的分析与数据文件
        +
版本化 Vitessce 配置
        |
        v
[1] 配置升级与校验
        |
        v
[2] 合并内置和插件注册表
        |
        v
[3] 初始化协调空间与数据加载器
        |
        v
[4] 按网格布局渲染独立视图
        |
        v
[5] 每个视图读取自己的协调作用域
        |
        v
[6] 按 dataset + data type + 协调条件匹配 loader
        |
        v
[7] 按需加载 Zarr 列/维度或多尺度图像 tile
        |
        v
[8] WebGL/SVG/Viv/HiGlass 渲染
        |
        v
用户交互更新共享作用域 -> 相关视图同步更新
```

#### 4.1 配置升级与校验

配置 schema 是版本化的。代码会把旧版本依次转换到新版本，再用最新 schema 校验；插件还会参与第二轮特定 schema 校验（`packages/schemas/src/view-config-versions.ts:53-85`; `packages/vit-s/src/VitS.js:114-175`）。因此，配置格式可以演进，同时尽量保持旧配置可用。

#### 4.2 插件注册

根组件把内置和用户插件的 view type、file type、joint file type 与 coordination type 合并（`packages/main/all/src/Vitessce.tsx:51-75`）。

- 视图插件：带名字的 React 组件。
- 文件插件：实现数据加载接口的类。
- 协调插件：新的语义属性和默认值。

这使 Vitessce 可以扩展到论文发表后出现的新格式或新分析任务。

#### 4.3 全局状态与协调

初始化后，配置和 loader 映射进入 Zustand store。`useCoordination` 根据视图配置的作用域名称读取当前值，并生成对应 setter（`packages/vit-s/src/state/hooks.js:163-205,474-503`）。

因此，所谓“多视图联动”在实现上不是 A 图通知 B 图，而是：

```text
A 图修改 scope X
       -> 中央 coordinationSpace[X] 更新
       -> 所有订阅 scope X 的视图重新渲染
```

#### 4.4 数据加载与缓存

`AbstractLoader` 规定了统一的异步 `load()` 接口（`packages/vit-s/src/data/AbstractLoader.js:10-40`）。视图的数据 hook 调用 `getMatchingLoader`，再执行具体 loader；返回结果还可以携带 URL 和初始协调值（`packages/vit-s/src/data-hook-utils.js:60-150`）。

AnnData/Zarr 的实现体现了“按需”思想：

- 常用的 obs/var 索引和列用 Promise 缓存，避免重复请求。
- `loadNumericForDims` 可以只读取 embedding 的指定维度。
- 具体 loader 把索引与所需数组组合成视图需要的数据结构。

对应代码位于 `packages/file-types/zarr/src/AnnDataSource.js:15-224` 和 `.../ObsEmbeddingAnndataLoader.js:14-51`。

#### 4.5 渲染

不同数据采用不同技术：deck.gl/WebGL 用于大规模散点、空间和热图；Viv 用于多尺度显微图像；HiGlass 用于基因组轨迹。热图的自定义 `HeatmapBitmapLayer` 安装 fragment shader，并把聚合尺度、纹理尺度和颜色范围作为 GPU uniform 传入（`packages/gl/src/HeatmapBitmapLayer.js:13-140`）。

### 5. 为什么它能支持大数据？

Vitessce 并不是只靠一种优化，而是针对不同表示选择不同策略：

- 大规模散点图和热图：WebGL/deck.gl，把大量渲染计算交给 GPU。
- 大型表达矩阵：Zarr 分块；按需要的基因、列或维度读取。
- 多尺度图像与分割：根据当前视口、缩放级别和通道读取 tile。
- 基因组轨迹：按当前基因组窗口加载 tile。
- 重复数据访问：查询键与数据源缓存减少重复请求。

论文宣称散点图可显示数百万细胞、热图可显示数万特征，并支持多 GB 图像（`paper.md:52,134-146`）。但论文没有给出统一的竞争工具性能对照，因此这些更接近能力展示，而不是严格基准结论。

### 6. 论文如何证明它有用？

评估以多种真实用例为主，而不是单一指标：

- CITE-seq：同时查看 RNA 与蛋白标记，重现 NK 细胞的 CD56、*GZMB*、*GZMK*、*PRF1* 特征。
- smFISH：把显微图像、空间 RNA、细胞分割、细胞类型和表达分布放在一起。
- 三维成像质谱：把 3D 组织渲染、热图、蛋白 embedding 和脂质/代谢物 embedding 并列。
- 10x Multiome：把表达热图、染色质可及性轨迹、UMAP、基因列表和 peak 列表联动。
- CODEX 与 Visium：展示多通道图像、spot、分割和注释图层。
- 图像插值比较：四个空间视图保持相同中心和缩放，SIMPLE 方法产生的规则横向条纹因此很容易被发现（Extended Data Fig. 7）。

这些结果有力证明了“同一框架能组合多种视图和数据”的主张，但不能替代帧率、内存、网络开销或定量准确性评估。

### 7. 论文主张与代码验证

#### 已直接验证

- 配置版本升级和 schema 校验。
- 插件注册表合并。
- Zustand 协调状态与作用域 hook。
- 视图到文件 loader 的部分匹配。
- 通用异步 loader 接口。
- AnnData/Zarr 的缓存和子集读取。
- 自定义 GPU 热图层。

#### 部分验证

- Python 与 R widget/API：论文和补充材料描述充分，但实现位于独立仓库，不在当前主 `code source`。
- Viv 与 HiGlass：主仓库包含相关集成，有限代码审计没有逐行追踪所有 tile 请求路径。
- 论文图的预处理：由独立 `paper-figures` 仓库、Python/Jupyter/Snakemake 和外部数据管线完成。

#### Not found

- 在主 JavaScript 仓库中，一条命令自动下载所有原始数据、重建全部处理结果并复现所有论文图。
- 针对 Cellxgene、TissUUmaps 等工具的统一受控性能基准。

### 8. 如何正确理解 Vitessce

最容易产生的误解是把“integrative visualization”理解成“multimodal integration algorithm”。Vitessce 不负责学习共享潜空间，也不负责推断细胞类型或分割图像。它接收这些上游结果，并提供一个可扩展、可分享、可联动的视觉分析层。

它真正重要的设计是：

> 用统一的数据语义和 loader 接口解决“数据来自哪里”，用独立视图解决“如何画”，用命名协调作用域解决“哪些图应该一起变化”。

因此，Vitessce 更像单细胞与空间组学的“可视化运行时和组件系统”，而不是一种新的生物信息学模型。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Vitessce summary

### Problem

Single-cell and spatial experiments increasingly combine transcriptomics, proteomics, chromatin accessibility, microscopy, coordinates and derived annotations. The paper argues that visual analysis remains fragmented: transcriptomics-oriented tools such as Cellxgene (bioRxiv, 2021), Cirrocumulus/Cumulus (Nature Methods, 2020) and Pagoda2's underlying method (Nature Methods, 2014) emphasize matrices, scatterplots and heatmaps, while spatial tools such as TissUUmaps 3 (Heliyon, 2023) and Napari-SpatialData/SpatialData (Nature Methods, 2024) emphasize spatial representations. Neither group, as characterized by the paper, provides one coordinated surface spanning nonspatial, spatial, imaging and genome-mapped modalities (`paper.md:21-27,222-226`).

### Proposed framework

Vitessce is an open-source, client-side visualization framework for multimodal and spatially resolved single-cell data. It embeds independent views—scatterplots, heatmaps, spatial/image layers, distributions, set controls and genome tracks—in a configurable grid. Views are linked indirectly through named **coordination scopes** stored in a serializable configuration. If multiple views use the same scope for a property such as selected feature, cell set, zoom or spatial target, an update is reflected across those views.

The framework separates three concerns:

1. **Data organization:** datasets expose abstract data types through files in formats such as AnnData, MuData, SpatialData, OME-TIFF/OME-Zarr, CSV and JSON.
2. **Rendering:** independent React views use WebGL/deck.gl, Viv, HiGlass, SVG or other web technologies.
3. **Coordination:** named scopes connect view state without direct component-to-component dependencies.

A view's request is matched to a loader by dataset, abstract data type and a partial comparison of observation/feature/value coordination properties. This is what allows several modalities or multiple representations of the same modality to coexist. Vitessce visualizes precomputed results; segmentation, dimensionality reduction and multimodal integration are generally upstream operations (`paper.md:46,119-131`).

### Implementation highlights

The paper-archived JavaScript release `v3.4.6` closely matches the described architecture. Direct source verification found:

- recursive versioned configuration upgrades and schema validation;
- merging of built-in and plugin view/file/coordination registries;
- a Zustand store for serializable coordination state;
- scoped React getter/setter hooks for independent views;
- partial view-to-file loader matching;
- shared loader/data-source interfaces with cached AnnData/Zarr subset reads;
- a custom deck.gl heatmap layer with shader-side aggregation and colormapping.

Core JavaScript fidelity is high. Python/R wrappers and manuscript preprocessing live in separate official repositories, so they are documented as partial rather than treated as part of the primary code snapshot.

### Evaluation and results

The paper is evaluated through heterogeneous demonstrations rather than a uniform head-to-head benchmark. The figures show:

- multimodal CITE-seq inspection reproducing known natural-killer-cell RNA/protein markers;
- linked smFISH images, transcripts, segmentations and expression summaries;
- volumetric multimodal mass-spectrometry imaging beside a heatmap and modality-specific embeddings;
- joint gene-expression, chromatin-accessibility and genome-track exploration for 10x Multiome;
- multiplexed CODEX and Visium spatial views;
- coordinated small multiples revealing horizontal streak artifacts from SIMPLE image-pyramid interpolation.

The paper states that scatterplots can display millions of cells and heatmaps tens of thousands of features, with multiscale image/genome data loaded on demand (`paper.md:52,134-146`). However, it does not report a controlled performance comparison against the named viewers, and static screenshots do not establish frame rate, memory or network behavior.

### Strengths

- One domain model for observation, feature and value types across modalities.
- Coordination is declarative and shareable because state lives in the configuration.
- Rendering, data loading and upstream bioinformatics are cleanly separated.
- Client-side operation allows deployment from static web servers or object storage.
- Plugin boundaries cover new views, file formats and coordination properties.
- The paper's diverse figures provide convincing qualitative evidence of composability.

### Limitations

- Vitessce does not perform preprocessing, integration, segmentation or dimensionality reduction by default.
- Cross-modal correctness depends on shared identifiers, declared types and upstream processing.
- The paper emphasizes use cases, not controlled accuracy or performance metrics.
- Complete manuscript reproduction requires separate Python/R packages, the `paper-figures` workflows, processed datasets and external portals.
- A single end-to-end command rebuilding all figure assets was **Not found** in the inspected primary JavaScript repository.

### Reproducibility assessment: 4/5

The core framework is strongly reproducible: source is MIT-licensed, the paper cites an archival Zenodo release, and the official `v3.4.6` snapshot directly implements the central configuration, coordination, loading and rendering mechanisms. The score is reduced because the paper's full demonstrations span several repositories and externally hosted processed datasets, and because the main repository alone does not recreate every manuscript use case.

### Bottom line

Vitessce's main contribution is not a new multimodal learning algorithm; it is a reusable architecture for making heterogeneous single-cell outputs jointly explorable. Its key idea is to combine an extensible file/view registry with a serializable named-scope coordination model, allowing independent visual components to share state while retaining format, rendering and deployment flexibility.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
