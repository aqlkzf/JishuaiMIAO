---
layout: default
permalink: /paper-atlas/redcat-c0b2dfa0/
title: "REDCAT"
nav: false
description: "REDCAT 是一个同一张组织切片上的全光学多模态成像流程，用 TPEF/SRS/SHG 直接测量红氧、脂质、蛋白、胶原和光谱化学状态，再用 CODEX 给细胞身份做高通量蛋白标注。它的核心不是新的深度学习模型，而是把光学代谢信号、细胞分割、配准、聚类和细胞类型注释串成单细胞/亚细胞尺度的组织代谢图谱。"
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
      <span>Technology Platforms</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>REDCAT</h1>
    <p>All-Optical Multimodal Mapping of Single Cell-Type-Specific Metabolic Activities via REDCAT</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2024.11.07.622511" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## REDCAT 方法中文解读

### 一句话概览

REDCAT 是一个同一张组织切片上的全光学多模态成像流程，用 TPEF/SRS/SHG 直接测量红氧、脂质、蛋白、胶原和光谱化学状态，再用 CODEX 给细胞身份做高通量蛋白标注。它的核心不是新的深度学习模型，而是把光学代谢信号、细胞分割、配准、聚类和细胞类型注释串成单细胞/亚细胞尺度的组织代谢图谱。

### 1. 生物学问题与建模目标

论文关注一个空间组学常见缺口：RNA 或蛋白标记可以识别细胞类型，但代谢状态常常不能从这些标记中一对一推出。REDCAT 的目标是在健康淋巴结、CLL/DLBCL 淋巴瘤和新鲜冷冻肝组织中，把实测的 NADH/FAD、脂质/蛋白、脂质不饱和度、SRS 光谱和胶原结构映射到 CODEX 定义的细胞类型与组织位置上。它能支持“某类细胞或某个区域呈现某种代谢/化学状态”的空间关联解释；不能单独证明肿瘤转化、核脂质功能或肝 zonation 梯度的因果机制。

### 2. 输入、输出与关键状态变量

| 元素 | 论文/代码名称 | 含义 | 证据来源 |
|---|---|---|---|
| 组织切片 | FFPE lymph node/lymphoma, fresh-frozen liver | 同一切片顺序成像 | `summary.md`, `doc_method.md` |
| 红氧信号 | $I_\mathrm{NADH}$, $I_\mathrm{FAD}$ | TPEF 自发荧光通道 | `claude_notes.md` |
| SRS 通道 | 2930, 2850, 3015, 2880 cm^-1 | 蛋白、脂质、不饱和和饱和脂质读数 | `doc_method.md` |
| 光谱向量 | $\mathbf{s}(x,y)\in\mathbb{R}^{51}$ | HSI 像素谱，用于 K-means | `claude_notes.md` |
| 细胞身份 | CODEX markers, Seurat, Astir, MaxFuse | 蛋白聚类和细胞类型注释 | `doc_method.md` |
| 输出 | cell-type metabolic maps | 细胞类型解析的红氧、脂质、光谱和胶原图 | `figure_analysis.md` |

### 3. 方法主流程

1. 在 FFPE 或新鲜冷冻组织上先采集 TPEF/SRS/SHG，得到 NADH/FAD、脂质/蛋白、脂质不饱和度、HSI 光谱和胶原信号。
2. 同一切片随后做 CODEX，并在 FFPE 情况下可继续做 H&E，保证代谢信号和蛋白身份来自同一物理组织。
3. 用 StarDist/QuPath 和 Mesmer 产生核/全细胞掩膜，经过大小、DAPI 强度和 CODEX 0.05/0.95 分位数缩放等 QC。
4. 用人工控制点和仿射变换把 SRS/TPEF 坐标配准到 CODEX 坐标，之后按细胞掩膜提取代谢比例。
5. 用 Seurat、Astir、MaxFuse、ScanPy 和 K-means 等现成工具做细胞类型、跨模态匹配和光谱聚类。
6. 在组织坐标中解释淋巴结 GC light/dark zone、淋巴瘤 tumor clusters、亚细胞脂滴/核光谱和肝 zonation。

### 4. 数学目标与直觉

红氧比例：

$$
R_\mathrm{redox}(x,y)=\frac{I_\mathrm{NADH}(x,y)}{I_\mathrm{FAD}(x,y)}
$$

论文将较高值解释为更还原的代谢状态，但这仍是光学 proxy，不能替代扰动实验或正交代谢组验证。

脂质/蛋白和不饱和/饱和脂质比例：

$$
R_{L/P}(x,y)=\frac{I_{2850}(x,y)}{I_{2930}(x,y)},\quad
R_{U/S}(x,y)=\frac{I_{3015}(x,y)}{I_{2880}(x,y)}
$$

它们把 SRS 通道转成可按细胞或区域汇总的代谢特征。

HSI 聚类：

$$
\min_{\{\mu_k\},c}\sum_{(x,y)}\|\mathbf{s}(x,y)-\mu_{c(x,y)}\|_2^2
$$

这个 K-means 目标把相似的 SRS 光谱归为化学状态。论文报告多个 8-cluster 分析，但 K 值选择、随机种子和 OriginPro 预处理细节没有公开。

### 5. 复现与实现注意点

`HAS_CODE=false`：当前工作区没有 REDCAT 公共代码仓库、notebook、原始/处理后矩阵、掩膜、控制点或作图脚本。`doc_code.md` 中所有项目级可执行实现均为 `MISSING` 或 `Not found`；Seurat、QuPath/StarDist、Mesmer、Astir、MaxFuse、ScanPy、scikit-image、ImageJ、GraphPad、OriginPro 只是在论文 Methods 中被文本支持。复现时最缺的是配准控制点和残差、HSI baseline/smoothing/normalization 设置、K-means 种子、MaxFuse notebook、PRM-SRS 参数和 figure statistics 脚本。

### 6. 结果如何解读

`figure_analysis.md` 显示，Fig. 2 支持健康淋巴结中 GC 区域和免疫细胞状态的代谢异质性；Fig. 3-4 支持淋巴瘤中红氧/脂质关系被扰动并出现 CLL、putative intermediate、DLBCL 相关光谱状态；Fig. 5 把分析推进到脂滴和核光谱异质性；Fig. 6 说明 REDCAT 可用于新鲜冷冻肝组织并观察 zone-dependent lipid/nuclear patterns。这些结果是技术平台可行性和发现导向案例，不是 cohort-scale benchmark。

### 7. 局限性与未验证部分

- 没有公开代码和数据包，项目级实现不可直接审计。
- 手工仿射配准没有 TRE/RMSE 分布，局部非刚性形变可能影响单细胞对应。
- HSI 谱段在 2700-3150 与 2800-3150 cm^-1 之间存在文本不一致。
- OriginPro、PRM-SRS、A-PoD、MaxFuse 和作图细节不足以完整复现。
- “intermediate CD20+ cells”“nucleolar lipid roles”“liver nuclear gradient”等结论更适合作为假设生成，而不是因果生物学结论。

### 8. 快速阅读路线

先读 `summary.md` 把握平台贡献和复现评分，再读 `doc_method.md` 理解公式、流程和关键假设；接着读 `figure_analysis.md` 对照六个主图；需要查代码证据时读 `doc_code.md`，重点是缺失项；最后读 `claude_notes.md` 查看完整证据 ledger、开放问题和发布级缺口。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## REDCAT — Summary

**Full title**: All-Optical Multimodal Mapping of Single Cell-Type-Specific Metabolic Activities via REDCAT
**Authors**: Li, Zhang, Enninful, Farzad, Rajbhandari, Nam, Qin, Villazon, Fung, Jang, Bai, Zhang, Stockwell, Fan, Xu, Ma, Shi
**Venue**: bioRxiv preprint, v2 posted 2025-10-11
**DOI**: 10.1101/2024.11.07.622511
**Paper type**: technology / experimental platform

### Motivation & Novelty

Metabolism is a functional state, but most spatial omics assays infer it indirectly from RNA/protein markers. REDCAT measures metabolic activity optically and then ties those measurements to cell identity on the same tissue section.

Existing approaches fall short:

| Category | Example | Journal | Year | Limitation |
|---|---|---:|---:|---|
| Fluorescence + MALDI single-cell metabolomics | SpaceM | Nature Methods | 2021 | Strong metabolite coverage but destructive and difficult in compact tissue. |
| High-throughput SpaceM | HT SpaceM | Cell | 2025 | Higher throughput but still MSI-based and not same-section high-plex protein imaging. |
| 3D OrbiSIMS / 3D-SMF | OrbiSIMS; 3D-SMF | Nature Methods; Science Advances | 2017; 2021 | High-resolution MSI, but destructive and limited for same-cell protein linkage. |
| scSpaMet | SIMS + protein profiling | Nature Communications | 2023 | Spatial metabolomics with protein context, but still mass-spectrometry based and destructive. |
| CODEX | Multiplex protein imaging | Cell | 2018 | High-plex cell typing but no direct metabolic readout. |
| MaxFuse | Cross-modal weakly linked integration | Nature Biotechnology | 2024 | Integrates modalities but needs measured features; does not itself acquire metabolism. |

REDCAT's v2 contribution is an all-optical, same-section platform that combines TPEF redox imaging, SRS protein/lipid/hyperspectral imaging, SHG collagen imaging, CODEX protein imaging, and downstream integration with Seurat, Astir, MaxFuse, and scRNA-seq reference labels. v2 expands the earlier lymph-node/lymphoma story to include collagen remodeling and fresh-frozen human liver zonation.

### Method Overview

```
FFPE or fresh-frozen section
  -> TPEF-SRS-SHG imaging
  -> CODEX multiplex protein imaging
  -> H&E after flow-cell removal when applicable
  -> StarDist/QuPath and Mesmer segmentation
  -> affine SRS-CODEX registration
  -> per-cell NADH/FAD, lipid/protein, unsaturated/saturated ratios
  -> Seurat/Astir/MaxFuse cell typing
  -> HSI K-means, PRM-SRS lipid subtype, collagen analysis
  -> lymph node, lymphoma, and liver interpretation
```

The computational core is not a new trainable model. It is a conventional image-analysis and integration workflow around direct optical measurements: ratios, K-means clusters, affine transforms, Seurat clusters, Astir posterior labels, and MaxFuse cross-modal matching.

### Evaluation

The paper is an application-driven technology demonstration, not a benchmark. It reports biological consistency and discovery-oriented case studies rather than accuracy metrics such as registration TRE, segmentation IoU, or cell-typing F1.

| Dataset | Main evidence | Figure(s) | Metric / readout |
|---|---|---|---|
| Healthy human lymph node FFPE | GC light-zone B cells show higher NADH/FAD and unsaturated/saturated lipid than dark-zone B cells; macrophage/monocyte and Tfh regions show high redox. | Fig. 2, Extended Figs. 1-2 | Per-cluster and per-cell ratios; MaxFuse cell-type maps. |
| Lymphoma FFPE with CLL/DLBCL | Tumor tissue disrupts normal lipid-redox relationships; three tumor clusters show distinct metabolic states and spatial organization. | Fig. 3, Extended Figs. 3-5 | CODEX clusters, UMAP tumor clusters, violin plots, high-ratio spatial maps. |
| Lymphoma transformation HSI ROI | SRS-HSI clusters 4/6/8 are lipid-rich; intermediate CD20+ cells have spectra distinct from CLL and DLBCL; T cells near CLL accumulate lipid. | Fig. 4, Extended Figs. 6-7 | K-means spectral clusters, cell-type enrichment heatmaps, spectra. |
| Lymph node vs lymphoma subcellular spectra | CLL has large LD clusters; DLBCL has smaller LDs, higher cholesterol/triglyceride ratios, nucleolar/perinuclear lipid signals, and more complex nuclear spectra. | Fig. 5, Extended Fig. 8 | PRM-SRS subtype ratios; percent nuclei with >=3 clusters. |
| Lymph node vs lymphoma extracellular matrix | Lymphoma collagen fibers are thinner, shorter, more curved, less aligned, and spectrally altered. | Extended Fig. 9 | SHG morphology and SRS collagen spectra. |
| Fresh-frozen human liver | LDs and NADH/FAD vary by liver zone; LDs appear in hepatocytes, CD141+ cells, CD45+ immune cells, and CD68+ Kupffer cells; nuclear 2883/2960 ratio increases moving away from the central vein. | Fig. 6, Extended Figs. 10-11 | Zone markers, LD area fraction, cell-type spectra, nuclear spectra. |

### Reproducibility

**Rating: 2 / 5**

- Wet-lab protocol detail is useful but specialized: picoEmerald SRS/TPEF/SHG hardware, modified multiphoton microscope, PhenoCycler-Fusion, careful same-section handling, and pathologist-reviewed tissues.
- Computation uses known packages, but no paper-specific repository, notebooks, raw data, processed matrices, control points, segmentation masks, spectra, or figure-generation scripts are released.
- v2 improves methodological specificity for MaxFuse and HSI calibration, including 5000 HVGs, feature SD > 0.01, smoothing weight 0.3, R6G calibration, and 0.8 quantile thresholding.
- Key details remain missing: exact OriginPro baseline/smoothing settings, exact K-means seeds and K selection policy, exact registration control points and residuals, exact reference dataset URL, and exact PhenoCycler protocol URL.

### Main Limitations

- Exploratory sample scale: one normal lymph node, one lymphoma specimen with a rare Richter transformation pattern, and one liver ROI demonstration.
- No public code/data release and no formal quantitative reproducibility package.
- Manual affine control points and proprietary OriginPro preprocessing are major implementation bottlenecks.
- HSI spectral range remains internally inconsistent: v2 workflow says 2700-3150 cm^-1 with 51 channels, while Methods state 2800-3150 cm^-1 with 51 steps.
- Biological claims about tumor-induced metabolic remodeling, nucleolar lipid roles, and liver nuclear gradients are hypothesis-generating, not mechanistically validated by perturbation or orthogonal metabolomics.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
