---
layout: default
permalink: /paper-atlas/spatial-ev-seq-54e0315d/
title: "Spatial-EV-seq"
nav: false
description: "传统组织 EV 分析通常先把组织消化、离心并分离囊泡。这样虽然能测 EV，却丢掉“它原来位于组织哪里、附近是什么细胞、可能影响谁”的信息。Spatial-EV-seq 的目标是同时得到 EV 的空间坐标、单个可分辨 EV 的表面蛋白组合，以及邻近区域的细胞类型和转录状态。 它把三个技术环节连成一条链： 第一步保留大致空间位置；第二步把约百纳米的 EV 放大成可成像的 RCA “DNA 纳米花”；"
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
      <span>Technology Platforms</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>Spatial-EV-seq</h1>
    <p>Spatially resolved profiling of extracellular vesicles in tissues with Spatial-EV-seq</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41587-026-03192-3" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for Spatial-EV-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/BuckyEv/Spatial-EV-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for Spatial-EV-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spatial-EV-seq 方法解读

### 它解决什么问题？

传统组织 EV 分析通常先把组织消化、离心并分离囊泡。这样虽然能测 EV，却丢掉“它原来位于组织哪里、附近是什么细胞、可能影响谁”的信息。Spatial-EV-seq 的目标是同时得到 EV 的空间坐标、单个可分辨 EV 的表面蛋白组合，以及邻近区域的细胞类型和转录状态。

### 核心创新

它把三个技术环节连成一条链：

```text
冻存组织切片
  -> 抗体捕获表面原位转印 EV
  -> 适配体识别 EV 表面蛋白
  -> padlock 连接 + phi29 RCA 放大
  -> 多通道荧光斑点与 EV 亚型
  -> 图像检测/解码
  -> 与相邻切片空间转录组做仿射配准
  -> 细胞类型、差异表达和配体–受体分析
```

第一步保留大致空间位置；第二步把约百纳米的 EV 放大成可成像的 RCA “DNA 纳米花”；第三步把 EV 图与空间转录组叠加，从而研究区域性的 EV–细胞关系。

### 实验与计算流程

1. **捕获**：约 80 µm 的冻存组织切片与抗体修饰玻片直接接触。低温准备减少扩散，37 °C、30 min 促进 EV 释放和抗体捕获。平均横向位移为 5.8 µm，测试组织的回收率约 60–70%。
2. **多蛋白识别**：CD63、EpCAM、PDL1 等蛋白的适配体同时充当 RCA 引物。不同荧光通道共定位后，形成单个 EV 的蛋白“身份证”。
3. **斑点检测**：每个通道先做 15×15 白顶帽背景抑制，再按像素强度众数设自适应阈值；图像切成 2,000×2,000 像素、重叠 15 像素的块，用 LoG 在 $\sigma=1$ 到 10 的 30 个尺度检测斑点并去重。
4. **空间配准**：DynamicISS 使用 SIFT、ORB、BRISK、AKAZE 或人工控制点估计仿射变换，以归一化互相关评价配准质量。
5. **细胞解释**：CellPose 分割细胞/细胞核，将 EV 类别分配给细胞；cell2location 生成 spot × cell type 丰度矩阵；DESeq2、clusterProfiler 和 stLearn 分析区域表达及细胞通讯。

### 关键定量结果

在每个 2,500-µm² 视野 0–700 个输入 EV 范围内，检测关系为

$$
y=0.7672x,\qquad R^2=0.9883.
$$

超过该范围后，RCA 产物聚集导致斑点合并。A375/U251 混合实验表明，方法能区分 EpCAM$^+$PDL1$^+$ 与 PDL1-only EV，并检测到约 7.2% 的稀有双阳性亚群。

在 4T1 乳腺癌模型中，PDL1 阳性 EV 富集区域与耗竭 CD8 T 细胞及免疫抑制表达程序相联系；PDL1 EV 稀疏区域更保留活化状态和抗 PD1 敏感性。这里最稳妥的解释是“区域空间关联”，因为 EV 和转录组来自相邻切片，不能直接证明某个 EV 导致某个细胞转变。

### 生物信息学与代码评价

论文对斑点检测和配准参数写得较具体，但官方代码并不完整。公开仓库只提供：

- stLearn 配体–受体/细胞通讯分析脚本；
- 无损 TIFF 压缩脚本。

仓库中 **Not found** 的关键部分包括 DynamicISS 斑点检测与解码、CellPose 的 EV-to-cell 分配、特征点/三点仿射配准和 PyQt5 GUI。因此，已有处理后数据时可以复现一部分下游通讯分析，但不能仅凭公开仓库从原始荧光图完整重建论文结果。

### 使用时必须注意

- 捕获抗体决定能看到哪一类 EV；anti-CD81 并不覆盖全部 EV。
- RCA 产物约为微米尺度，密度高时会合并。
- EV 图约 1 µm 分辨率，而本文空间转录组 spot 为 50 µm。
- 相邻切片的形变和配准误差会影响 EV–细胞对应关系。
- 当前证据适合发现空间关联和候选机制，若要证明因果关系仍需干预实验。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Spatial-EV-seq

### Problem

Isolation-based extracellular-vesicle assays lose tissue location and weaken links between EV phenotype, parental cells and recipient-cell state. Spatial-EV-seq is a technology platform that preserves an approximate tissue coordinate for captured EVs, profiles several surface proteins at single-punctum scale, and integrates those maps with adjacent-section spatial transcriptomics.

### Method in brief

An antibody-engineered glass surface contacts an 80-µm frozen tissue section and captures EVs during controlled blotting. Protein-binding DNA aptamers prime padlock ligation and phi29 rolling-circle amplification, converting each resolvable EV into a bright fluorescent nanoflower. Multichannel colocalization gives a protein subtype. Image processing detects and decodes puncta; affine registration aligns the EV map to an adjacent spatial-transcriptomics section. Cell2location estimates cell mixtures, DESeq2/clusterProfiler characterize EV-defined regions, and stLearn summarizes ligand–receptor interactions.

### Evidence and results

- Detection was linear from 0 to 700 EVs per 2,500-µm² frame, with $y=0.7672x$ and $R^2=0.9883$; higher densities produced RCA aggregation.
- EV transfer retained tissue geometry with a reported mean lateral displacement of 5.8 µm and roughly 60–70% recovery across tested tissues.
- Multiplex EpCAM/PDL1 profiling distinguished A375 and U251 EVs and detected a rare double-positive fraction around 7.2% in mixtures.
- In 4T1 breast tumors, PDL1-positive-EV-enriched regions aligned with exhausted CD8 T-cell programs and immune-privileged niches; depleted regions retained more activated states and anti-PD1 sensitivity.
- Clinical hepatocellular-carcinoma biopsy data provide a feasibility demonstration, not yet a prospective diagnostic validation.

### Strengths and limitations

The platform joins an experimentally clever spatial capture/RCA assay with interpretable multimodal maps. Controls address vesicle identity, nonspecific binding, displacement and dynamic range. Main limitations are capture-antibody selection bias, crowding of RCA products, adjacent-section rather than same-section integration, a large EV/transcriptome resolution mismatch, and primarily association-level biological inference.

### Reproducibility

**Rating: 2.5/5.** The paper provides unusually concrete image-processing parameters and public sequence data (`CRA039683`). The official GitHub repository is public, but it contains only a stLearn CCI wrapper and TIFF compression utility. The core DynamicISS spot detection/decoding, feature registration, affine GUI and CellPose EV-to-cell assignment implementations are **Not found** in the complete released snapshot. Thus downstream CCI can be reproduced given prepared inputs, while the raw-image-to-integrated-map pipeline cannot.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
