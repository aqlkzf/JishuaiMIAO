---
layout: default
permalink: /paper-atlas/spomialign-f932f36c/
title: "SPOmiAlign"
nav: false
description: "相邻组织切片上的转录组、蛋白组、代谢组或组织学图像通常没有共享分子特征，而且会有旋转、尺度变化、局部撕裂和不同采样分辨率。SPOmiAlign 的关键选择不是在基因空间里强行寻找共同维度，而是把问题改写成图像配准： 将空间组学渲染为空间结构图（spatial structural image, SSI），或直接使用配对 H&E/荧光图像； 用预训练 RoMa 稠密匹配模型寻找像素对应及置信度； 用高置信匹配估计全局与非刚性变换；"
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
      <span>bioRxiv · 2025</span>
    </div>
    <h1>SPOmiAlign</h1>
    <p>SPOmiAlign: A modality-agnostic framework for robust and scalable spatial multimodal alignment via feature matching</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2025.12.19.695434" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SPOmiAlign 中文方法解读：先把空间组学变成结构图，再做稠密图像匹配

### 核心问题

相邻组织切片上的转录组、蛋白组、代谢组或组织学图像通常没有共享分子特征，而且会有旋转、尺度变化、局部撕裂和不同采样分辨率。SPOmiAlign 的关键选择不是在基因空间里强行寻找共同维度，而是把问题改写成图像配准：

1. 将空间组学渲染为空间结构图（spatial structural image, SSI），或直接使用配对 H&E/荧光图像；
2. 用预训练 RoMa 稠密匹配模型寻找像素对应及置信度；
3. 用高置信匹配估计全局与非刚性变换；
4. 将源切片坐标变换到参考切片坐标系；
5. 当 spot 密度不同，再用最近邻 reassignment 建立可供纵向整合使用的观测对应。

本解读的论文证据来自 `paper source/paper/vlm/paper.md` 和其中主图 1–5/补充图文本；直接实现证据来自本地仓库快照 `SPOmiAlign/`，其 `.repo_source` 固定 commit 为 `3b2bae389c37ccc9cf7c8a5bb5b4ec71b14ec94c`。论文概念、当前代码和论文全部分析脚本并不完全等价，边界见末节。

### 1. SSI：为什么跨模态还能匹配

对第 $i$ 个空间位置，分子特征为

$$
\mathbf{x}_i=(x_{i1},\ldots,x_{iD})\in\mathbb{R}^D.
$$

论文默认把所有特征求和，得到一个标量强度：

$$
I_i=f(\mathbf{x}_i)=\sum_{d=1}^{D}x_{id}.
$$

再把 $I_i$ 画到坐标 $(u_i,v_i)$ 上形成灰度 SSI。这样 RNA、蛋白和代谢数据都被投影到同一种“组织轮廓与空间强弱纹理”语言，不需要共享基因。代码 `data_preprocessing.py` 的默认路径同样使用 `adata.X.sum(axis=1)`，并支持 `log1p`、分位数裁剪、灰度增强、圆形/方形 kernel、旋转翻转及显示尺度元数据。

这个抽象也有代价：不同基因组合只要总量相同，就会在单通道 SSI 中不可区分。论文明确承认 spot 大小需人工设置，且求和会压缩细粒度、模态特异的分子信息。SSI 的目标是提供几何结构线索，而不是保存组学表达的充分统计量。若数据自带 H&E 等图像，论文可以直接用图像配准，绕过 SSI。

### 2. RoMa 稠密对应：从两个图像得到匹配点

RoMa 是为一般图像对应预训练的模型。论文图 1 把它概括为 DINOv2 特征编码器、基于 Gaussian process 的 matching encoder 和 Transformer matching decoder。输出不是少量人工 landmark，而是稠密 warp 与每个候选对应的 certainty。

当前 `roma.py` 把图像内部缩放到 $1152\times864$，调用 `roma_outdoor(...).match()`，然后从 warp/certainty 中选匹配。RoMa 本体作为第三方代码被整包放在 `software/RoMa-main` 与 `software/Roma` 中；SPOmiAlign 并未训练新的生物图像基础模型，而是在预训练图像匹配器外增加空间组学渲染、边缘重加权、变换和坐标回写。

### 3. 边缘重加权和空间去冗余

弱纹理组织边缘容易被高置信内部区域淹没。论文用频域高通、边缘阈值和匹配置信度重加权描述这一环节。代码的实际步骤更具体：

1. 对源图灰度图做二维 FFT；
2. 乘以一个同时抑制低频并衰减极高频的权重，因此更接近带通，而不是纯高通；
3. 逆变换后取幅值并归一化；
4. 对 $E^{1.2}$ 使用 Otsu 自动阈值得到二值边缘；
5. 将 certainty 乘以 $0.9E+0.1$；
6. 在 $3\times3$ 窗口做 max-pooling NMS，使候选不只集中在少数纹理区域；
7. 按重加权置信度取最多 5,000 对匹配点。

这里还有一个实现边界：`edge_full` 的参考图一侧为零，随后 `certainty_weighted[:, :W]=0`，所以当前主路径只用源图侧边缘驱动筛选。论文写成同时考虑两侧边缘的对称公式时，不能直接视作代码逐项实现。

### 4. 几何变换：全局形变与局部形变

SPOmiAlign 支持 affine、homography、非刚性和 `affine+bspline`。默认推荐的两阶段理解是：

1. 用匹配点最小二乘拟合 $2\times3$ affine matrix，先消除旋转、平移、缩放和剪切；
2. 在 affine 后的残差上估计平滑位移场，修正切片局部拉伸和弯曲；
3. 将像素空间变换通过渲染元数据逆映射回原始 h5ad 坐标。

虽然函数名叫 `fit_bspline_transform`，当前实现并没有按论文公式优化 B-spline 控制点。它先把匹配位移写入像素网格，对未知位置用 OpenCV Telea inpainting 补洞，再以 `sigma=15` 的 Gaussian blur 平滑，最后交给 `SimpleITK.DisplacementFieldTransform`。这实现了平滑非刚性变换的功能目标，但不是标准 B-spline 基函数拟合，因而属于 paper–code 实现差异。

代码还会在参考图小于源图时自动放大参考图，并直接覆盖输入图像文件。该副作用对可审计复现很重要：运行前应保留只读原图或副本，并记录 render metadata、原始尺寸和变换方向。

### 5. Reassignment：配准不等于一一对应

坐标变换后，高分辨率切片可能在一个低分辨率 spot 周围有多个点。代码先比较两张切片的平均内部最近邻距离；距离较大者被判定为低分辨率。随后从高分辨率点查询最近的低分辨率点，并过滤过远匹配。

当前简单实现的阈值是低分辨率切片内部最近邻距离的最大值 $d_{\max}$ 的两倍，而论文公式将两张切片的平均距离合成为尺度 $D$。两者并不相同。一个低分辨率 spot 对应 $k$ 个高分辨率点时，代码可将其表达除以 $k$ 后复制，从而守恒总量；这是一种数据重排规则，不是新的生物测量，也不能制造原本不存在的细胞级信息。

所谓“一对一 spot correspondence”还需谨慎解释：输出可以让每个高分辨率位置拥有一行对应观测，但多个高分辨率位置仍可来源于同一个低分辨率 spot。它是 many-to-one mapping 的展开，不是严格双射。

### 6. 主图如何支撑结论

- **图 1**：展示 SSI/图像输入、RoMa 稠密匹配、top-5,000 correspondences、warping 和 reassignment。它支持算法流程，不支持准确率结论。
- **图 2**：Slide-seq 和 MERFISH 到 Allen CCF 的配准，以 Dice 与 marker 到区域边界的 FWHM 评估。Atlas 切片索引由人工检查选择，因此“fully automated”主要指给定参考切片后的配准/注释流程，而不是完整的 3D atlas section selection 全自动。
- **图 3**：不同小鼠的 RNA/ATAC 切片借助配对 H&E 对齐，与 ELD、STAlign 和 unaligned 比较；PCC、cosine 和 mismatch 依赖 harmonized cell-type labels，也同时受标注/聚类质量影响。
- **图 4**：RNA、蛋白、代谢三张相邻脑切片的对齐，并用跨模态 biomarker 的 bivariate Moran's $I$ 和下游 SpatialGLUE 域识别评估。SpatialGLUE 是外部下游工具，不属于 SPOmiAlign 核心代码。
- **图 5**：在对齐后的多组学中提出小脑 molecular layer 的 IML/OML 分层，并用 RNA、蛋白、脂质趋势支持。该发现是“配准 + 外部整合 + 聚类/差异分析”的复合结果，不能单独归因于配准算法。论文也提示 MALDI $m/z$ 注释不能严格区分同分异构体。

图中秒级速度、Dice 和相关指标只对论文选定数据、参考图、硬件、参数和比较实现成立。它们不证明任意组织或任意跨模态组合都具有同样精度。

### 7. 复现和版本边界

#### 7.1 本地快照与论文/README 已发生漂移

本地 provenance 固定仓库 commit `3b2bae...`，但 README 的当前 manuscript title 与工作区论文标题不同。README 主要推荐 `new/Code/*.py`，而本快照没有 `new/` 目录；旧工作区 quick usage 又指向不存在的 `SPOmiAlign.py`。实际可见核心 CLI 是 `SPOmiAlign/SPOmiAlign/align_h5ad_to_h5ad_square.py`，并且 README 给出的路径层级与本工作区嵌套结构不完全一致。因此文档命令不能未经核对直接复制运行。

#### 7.2 论文端到端分析未全部包含在核心包

代码能定位 SSI、RoMa matching、变换、坐标回写和 reassignment，但 CCF reference section 的选择、Allen annotation volume 的完整检索流程、Grounding DINO ROI、SpatialGLUE integration 以及全部论文统计/作图并非一个统一可运行入口。仓库含 demo 和大量第三方 RoMa 副本，但没有证据表明当前 commit 与论文全部结果的精确环境、模型权重和输入资产被锁定。

#### 7.3 运行依赖和副作用

RoMa 推理依赖 GPU/模型权重和较重环境；环境文件只能声明依赖，不能证明当前机器已复现。`auto_upscale_reference` 会覆盖参考图；不同 CLI/重复文件（仓库根、包内、`resource/`）可能实现不同 reassignment 逻辑。复现时必须记录实际入口、文件哈希、变换方向、渲染参数、权重来源和输出元数据。

### 8. 可验证的复现路径

最低限度应先选一个论文 case：固定两张输入及参考/源方向；使用实际存在的 CLI；保存 SSI 与 render metadata；核对 top matches 和 overlay；禁用或隔离覆盖输入的行为；检查变换后的坐标是否仍处于目标范围；记录 reassignment 的丢弃率与 many-to-one 分布。随后再分别验证 Dice/PCC/Moran's $I$，不要把视觉 overlay 当作唯一证据。

因此，本工作区可以确认 SPOmiAlign 的核心思想和主要实现路径，也能指出论文公式与代码的差异；但当前快照尚不能支持“论文所有数值已端到端复现”的声明。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SPOmiAlign — Paper Summary

### Motivation & Novelty

Spatial multi-omics technologies enable joint profiling of transcriptomics, proteomics, and metabolomics across tissue sections, but integrative analysis requires precise spatial alignment of data generated from adjacent sections on different platforms. This is challenging because modalities have fundamentally different signal characteristics (sparse gene counts vs. continuous spectral intensities vs. dense optical images), spatial resolutions, and geometric distortions from tissue processing.

**Limitations of existing approaches:**
- **STAlign** (*Nature Communications*, 2023): diffeomorphic alignment of spatial transcriptomics — relies on shared gene features; minutes-to-hours runtime for iterative optimization
- **ELD** (*Nature Methods*, 2024): deep learning landmark detection for image registration — automated but struggles with weakly textured tissue boundaries
- **PASTE / PASTE2** (*Nature Methods*, 2022; *Genome Research*, 2023): optimal transport-based alignment — requires shared gene panels; computationally expensive
- **SLAT** (*Nature Communications*, 2023): graph-based heterogeneous slice alignment — needs cell-type or gene feature overlap
- **Manual landmark annotation** (Langlieb et al., *Nature*, 2023): gold standard for CCF registration — labor-intensive, subjective, not scalable

**Unique contributions of SPOmiAlign:**
1. **Modality-agnostic framework**: converts any spatial omics data to Spatial Structural Images (SSIs) via simple feature summation, enabling cross-modal alignment without shared molecular features
2. **Dense feature matching via pretrained RoMa model**: leverages a computer vision foundation model (DINOv2 + GP + Transformer) for robust correspondence without iterative optimization
3. **Edge enhancement matching**: Fourier-based edge detection + confidence reweighting improves alignment at weakly textured tissue boundaries
4. **2-3 orders of magnitude faster**: ~10 seconds vs. minutes-to-hours for existing methods
5. **Fully automated CCF registration**: no manual landmarks needed; automated anatomical annotation retrieval from the Allen Brain Atlas

---

### Method Overview

SPOmiAlign is a four-component pipeline: **Imaging → Section Matching → Section Warping → Reassignment**.

1. **Imaging**: Spatial omics profiles are converted to Spatial Structural Images (SSIs) by summing all D features per spot into a scalar intensity, then rasterizing onto a grayscale image. Alternatively, paired histological images (H&E, Nissl) are used directly.

2. **Section Matching**: Dense pixel-wise correspondences between reference and source images are computed using the pretrained RoMa model (DINOv2 backbone, GP matching, Transformer decoder). An edge enhancement module upweights boundary correspondences using Fourier-based edge detection. Top 5000 correspondences are selected after spatial uniformization via 3×3 grid NMS.

3. **Section Warping**: A two-stage strategy estimates geometric transforms: affine for global alignment, followed by B-spline deformation for local non-rigid correction. Transforms are applied to all source spot coordinates.

4. **Reassignment**: For multi-modal integration, nearest-neighbor mapping establishes one-to-one spot correspondence across sections with different spatial resolutions. Distance-based filtering excludes non-overlapping regions, and 1/k profile normalization corrects for resolution differences.

See `doc_method.md` for detailed mathematical formulation and algorithm walkthrough. See `doc_code.md` for code-paper mapping and implementation details.

---

### Evaluation

#### Datasets

| Dataset | Modalities | Platform | Resolution | Use Case |
|---------|-----------|----------|------------|----------|
| Slide-seq mouse brain (IDs 29, 43) | Spatial transcriptomics | Slide-seq V2 | ~10 μm | Omic-to-CCF registration |
| MERFISH sagittal (section 008) | Spatial transcriptomics | MERFISH | Single-cell | Omic-to-CCF registration |
| MISAR-seq (S1, S2) | Transcriptomics + ATAC-seq | MISAR-seq | ~25 μm | Omic-to-omic cross-sample |
| Mouse brain tri-omics | Transcriptomics + proteomics + metabolomics | MAGIC-seq, PLATO, MALDI-MSI | Variable | Trimodal alignment + integration |
| ANHIR benchmark | Histological images | Multiple stains | Variable | Non-rigid image registration |

#### Metrics

- **Dice coefficient**: spatial overlap of anatomical region masks (CCF registration)
- **FWHM**: spatial deviation of marker expression from CCF region boundaries (40-70 μm, comparable to expert manual alignment)
- **PCC / Cosine similarity**: spatial concordance of cell-type distributions across modalities
- **Bivariate Moran's I**: spatial co-localization of cross-modal biomarker pairs
- **NMI / ARI**: clustering agreement for trimodal integration quality
- **Runtime**: SPOmiAlign ~10 seconds vs. STAlign minutes-to-hours (2-3 orders of magnitude faster)

#### Key Results

- **CCF registration**: Dice > 0.91 for top 10 brain regions (Slide-seq ID 29); FWHM 40-70 μm for marker genes
- **Cross-sample alignment**: highest PCC and cosine similarity (0.7-0.8) across cell types; fewest mismatch spots
- **Trimodal alignment**: highest mean bivariate Moran's I across all biomarker pairs
- **Integration quality**: NMI and ARI consistently highest when alignment performed with SPOmiAlign
- **Biological discovery**: identified inner molecular layer (IML) and outer molecular layer (OML) substructures in cerebellar molecular layer, supported by concordant transcriptomic, proteomic, and metabolomic signatures

#### Compared Methods

| Method | Journal | Year |
|--------|---------|------|
| STAlign | *Nature Communications* | 2023 |
| ELD | *Nature Methods* | 2024 |
| SpatialGLUE (downstream) | *Nature Methods* | 2024 |
| PASTE | *Nature Methods* | 2022 |
| SLAT | *Nature Communications* | 2023 |

---

### Reproducibility

**Rating: 4/5**

**Strengths:**
- Code publicly available on GitHub with conda environment specification
- All datasets used are publicly available with explicit download URLs
- Clear pipeline with well-separated modules (rendering → matching → warping → reassignment)
- RoMa is a pretrained model — no training required, deterministic alignment
- Runtime is fast (~10 seconds), making reproduction practical
- Comprehensive CLI with configurable parameters

**Weaknesses:**
- Grounding DINO for CCF annotation transfer is not included in the codebase — must be run externally
- SpatialGLUE downstream integration is external; full trimodal analysis workflow not end-to-end
- Some parameters (spot radius, threshold percentile) require dataset-specific tuning
- SSI construction uses only summation (not PCA/RGB alternatives mentioned in paper)
- bioRxiv preprint — not yet peer-reviewed

**Practical Notes:**
- Requires GPU with ≥4 GB VRAM for RoMa inference (CUDA required)
- Python 3.12 + PyTorch 2.7.1 + romatch 0.1.2 — use provided `SPOmiAlign.yml` for environment
- Input: h5ad files with `obsm['spatial']` and expression in `X`
- Output: transformed h5ad with updated coordinates + visualization PNGs
- For CCF registration, matched Nissl atlas section index must be provided manually

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
