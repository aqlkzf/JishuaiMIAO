---
layout: default
permalink: /paper-atlas/siibra-c1dabd01/
title: "siibra"
nav: false
wide: true
description: "人脑数据横跨 MRI、连接组、组织学、细胞密度、受体密度和基因表达等尺度。真正困难的不是“有没有数据”，而是这些数据使用不同坐标空间、脑区术语、文件格式和云存储接口，并且解剖定位的可信度也不同。传统做法常把高分辨率数据降采样成宏观图，或在分析过程中丢失“这个数值属于哪个脑区/哪版图谱”的关系。 Siibra 的目标是建立一个可计算的多层次人脑图谱：保留数据的原始细节和来源，同时让研究者能够用统一的脑区或空间位置查询它们。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>siibra</h1>
    <p>Siibra: a software tool suite for realizing a Multilevel Human Brain Atlas from complex data resources</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-026-03159-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for siibra">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/FZJ-INM1-BDA/siibra-python" target="_blank" rel="noopener noreferrer" aria-label="Open code for siibra">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Siibra 方法详解

### 它解决什么问题？

人脑数据横跨 MRI、连接组、组织学、细胞密度、受体密度和基因表达等尺度。真正困难的不是“有没有数据”，而是这些数据使用不同坐标空间、脑区术语、文件格式和云存储接口，并且解剖定位的可信度也不同。传统做法常把高分辨率数据降采样成宏观图，或在分析过程中丢失“这个数值属于哪个脑区/哪版图谱”的关系。

Siibra 的目标是建立一个可计算的多层次人脑图谱：保留数据的原始细节和来源，同时让研究者能够用统一的脑区或空间位置查询它们。

### 核心创新

1. **内容与代码分离**：图谱、坐标空间、脑区、数据特征和远程资源由版本化 specification 描述，软件只负责解释这些描述。
2. **语义与空间定位统一**：数据既可关联到脑区名称，也可关联到点、包围盒、图像掩膜等空间对象，并保留定位不确定性。
3. **基础内容与动态内容并存**：稳定内容来自 configuration；运行时内容通过 live query 从 EBRAINS、Allen 等 API 获取。
4. **小文件与超大图像统一访问**：用户使用同一接口，底层根据资源选择普通下载、多分辨率裁剪或降采样。
5. **多种入口共享同一能力**：Python、HTTP API 和三维浏览器面向不同用户，但围绕同一组图谱对象和查询逻辑工作。

### 计算流程

```text
版本化配置                         云端 API
(空间、图谱、脑区、特征、URL)      (EBRAINS / Allen / 图像服务)
          |                              |
          v                              v
  按 @type 构建对象                   live query
          |                              |
          +--------------+---------------+
                         v
       Atlas / Space / Region / Location / Feature
                         |
       用户输入：脑区、坐标、包围盒、掩膜或体数据
                         |
            语义匹配 + 空间匹配 + 资格评估
                         |
                 找到相关数据特征
                         |
           懒加载、裁剪/降采样、解码、缓存
                         |
              NIfTI / DataFrame / NumPy
```

#### 第一步：从 specification 构建图谱对象

Specification 保存标识符、模态、外部元数据链接、解剖位置、数据 URL 和格式。代码中的 `build_type()` 把 `@type` 注册到具体工厂函数；`Factory` 再构建 Atlas、Space、Parcellation、Region、Feature 和 Volume。这样新增数据通常只需增加或修改配置，而不必把每个数据集写死进 Python 包。

#### 第二步：表达解剖定位

Siibra 区分两类定位：同一组织中依据细胞构筑识别脑区属于较强的内在定位；把其他个体的坐标投影到图谱属于外在定位，具有更大不确定性。代码要求一个特征至少具有脑区语义位置或空间位置，并将其封装为 `AnatomicalAnchor`。

#### 第三步：把脑区解析成图像/掩膜

给定脑区、参考空间和 labelled/statistical map 类型，系统在 map registry 中寻找匹配图。如果父脑区没有直接图像，代码还能递归合并已映射的子脑区。这使层次化脑区术语在地图不完整时仍可使用。

#### 第四步：跨坐标空间转换

Siibra 使用预计算的非线性微分同胚在 MNI、BigBrain 等空间之间转换位置。转换误差随区域和形变程度变化，不能把转换后的坐标当作精确的组织学对应。变换服务位于独立的 `hbp-spatial-backend`，不在本次获得的 Python 快照中。

#### 第五步：查询数据特征

用户提供“解剖概念 + 模态”，系统综合脑区层级、空间重叠、包含关系、坐标精度等信息，对候选特征进行资格评估。稳定特征从 configuration 延迟构建；动态特征由 live query 连接外部 API。

#### 第六步：按需获取数据

Siibra 不随软件分发所有数据，而只保存元数据和指针。第一次请求时才下载或读取资源，并建立本地缓存。普通图像可直接返回；超大多分辨率图像会按可行区域裁剪或降采样，同时更新空间元数据。最终暴露为 NIfTI、pandas DataFrame、NumPy 数组等常用对象。

#### 第七步：压缩稀疏概率图

Julich-Brain 等概率图若每个脑区都保存完整 3D 体积，会形成巨大的稀疏 4D 数组。论文采用“3D 体素索引 + 非零脑区权重列表”的结构，只保存实际存在的权重，从而降低下载和内存成本。

### 论文如何验证？

这不是单一指标的算法竞赛，而是系统级验证：论文展示从全脑到细胞尺度的连续浏览、脑区的多模态画像、显微图像的可复现提取，以及皮层下图谱的解剖评估。扩展图还量化了坐标变换误差，并比较不同洲访问云服务的响应时间。

### 代码与论文的一致性

`siibra-python` v1 快照直接验证了配置工厂、解剖锚点、脑区地图查询、子区合并和懒加载等核心机制，整体一致性为 **中高**。但完整工具套件分布在多个仓库：API、浏览器和空间变换后端没有纳入本次代码快照；逐图复现代码主要托管在在线文档中。

### 使用时最重要的限制

- 跨个体、跨空间的坐标变换是近似关系，不是解剖学真值。
- 结果依赖外部数据集、API 和网络可用性；论文显示欧洲以外的延迟可能明显增大。
- Siibra 统一的是访问、格式与解剖上下文，并不会消除原始数据的偏差、个体差异或定位不确定性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Siibra — summary

### Problem

Modern brain data span macroscopic MRI, microscopic histology, connectivity, molecular measurements and gene expression, but differ in spatial scale, coordinate system, anatomical terminology, format and storage system. Conventional workflows often reduce high-resolution measurements to coarse derivatives or lose the link between data and atlas labels. Siibra aims to keep distributed data at useful detail while making them spatially and semantically interoperable.

### Contribution

Siibra is a modular tool suite—Python library, HTTP API and interactive 3D viewer—that connects reference atlases and coordinate spaces to anatomically anchored datasets in cloud resources. It realizes a Multilevel Human Brain Atlas within EBRAINS, spanning MNI/freesurfer-scale representations and microscopic BigBrain content.

The key design is separation of content from code. Versioned configuration specifications define foundational atlas objects and resource pointers; live queries add dynamic content from repository APIs. Users query with brain regions or spatial objects, siibra qualifies semantic/spatial matches, and requested data are lazily fetched, optionally cropped/downscaled, cached, and returned in standard objects such as NIfTI images, pandas DataFrames or NumPy arrays.

### Evidence and demonstrations

The paper is evaluated through end-to-end scientific use cases rather than a single benchmark score. Demonstrations include cross-scale navigation from whole-brain maps to cellular histology, multimodal profiles of cortical areas, reproducible extraction of microscopic patches, and anatomical comparison of subcortical maps. Extended analyses quantify nonzero coordinate-warping error and show substantial geographic variation in cloud response times. The main and extended figures visually support the architecture, spatial continuity, heterogeneous feature integration and sparse-map representation.

### Code–paper match

The acquired `siibra-python` v1 snapshot matches the core architecture well. Direct source evidence verifies specification-type factory dispatch, construction of atlas/space/parcellation objects, anatomical-anchor extraction, registry-based regional map retrieval with descendant fallback, and lazy feature loading. Fidelity is **medium-high** rather than high because the full suite is split across repositories: `siibra-api`, `siibra-explorer`, and the external spatial-transformation backend were not included in the analyzed snapshot.

### Reproducibility

- Paper, data URLs, software repositories and v1 documentation/examples are openly available.
- Each paper figure is associated with executable code or persistent resources in the online documentation.
- The local workspace preserves the full Nature HTML-derived paper, 12 figures, and the `siibra-python` v1 source at commit `e8c32d6d995c52a61c560a7de98d5dd0cea72bc5`.
- A completely offline reproduction is not contained in this snapshot: many results depend on live EBRAINS/Allen/image resources, separate suite repositories, and online figure examples.

### Limitations

Coordinate transformations are approximate and region-dependent; anatomically transferred coordinates should not be treated as histological ground truth. Distributed-cloud latency can be high outside Europe. The atlas's usefulness also depends on curation quality, stability of external APIs, and continued availability of linked data. Siibra harmonizes access and anatomical context but does not eliminate biological variability or uncertainty in cross-subject localization.

**Reproducibility rating: 4/5.** The software, content and examples are unusually open and well linked, but full execution remains dependent on evolving remote services and multiple repositories rather than a single frozen bundle.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
