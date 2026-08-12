---
layout: default
permalink: /paper-atlas/crochet-52cc337e/
title: "CROCHET"
nav: false
description: "CROCHET（ChaRacterization Of Cellular HEterogeneity in Tissues）是一套面向单细胞分辨率空间组学的端到端流程。它把原始多轮荧光图像依次变成配准、分割和质控后的单细胞特征表，再用基于径向分布函数（RDF）的空间富集分数衡量“哪些标记或细胞类型在给定距离内共同出现”，最后生成细胞邻域、受体—配体 immunoprint 和相邻切片的 3D 图谱。"
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
      <span>Atlases &amp; Resources</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>CROCHET</h1>
    <p>CROCHET: a versatile pipeline for automated analysis and visual atlas creation from single-cell spatialomic data</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.03.13.711472" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CROCHET：从循环多重成像到可比较的单细胞空间图谱

### 一句话理解

CROCHET（ChaRacterization Of Cellular HEterogeneity in Tissues）是一套面向单细胞分辨率空间组学的端到端流程。它把原始多轮荧光图像依次变成配准、分割和质控后的单细胞特征表，再用基于径向分布函数（RDF）的空间富集分数衡量“哪些标记或细胞类型在给定距离内共同出现”，最后生成细胞邻域、受体—配体 immunoprint 和相邻切片的 3D 图谱。

论文最值得学习的不是某个单独的神经网络，而是两层设计：第一层修复循环成像中特有的残留荧光、组织损伤和非特异结合；第二层把局部邻近关系除以组织本身的细胞密度，试图让不同组织之间的空间分数可以比较。

### 它解决什么问题？

CyCIF、CODEX、COMET 和 Xenium 等技术能保留细胞坐标并测量许多蛋白或 RNA，但从图像到生物结论仍要串联多个工具：格式转换、对焦、跨轮配准、背景扣除、分割、细胞注释、空间统计和可视化。循环染色还带来普通单轮成像没有的伪影：

- 染色/脱色轮次增加时，组织可能破损或细胞脱落；
- 漂白不完整会把上一轮信号带入下一轮；
- 红细胞、碎屑等结构可能在不同抗体轮次中反复产生高亮非特异信号；
- 传统邻居计数容易把“组织本来就密”误当成真正空间富集。

CROCHET 把这些问题组织成三个 meta-module，并给出 22 个方程描述关键步骤。

### 输入与输出

#### 输入

- 原始多通道、多 Z-plane 循环成像文件，例如 CZI；论文示范数据为 10 轮、每轮 5 通道的 CyCIF TMA。
- 每轮染色/漂白图像、曝光时间和光强等元数据。
- 可选的细胞表面标记、用户定义的细胞分型规则和空间分析半径。
- 论文声称也可处理成像型单细胞空间转录组（如 Xenium），但示范集中在 CyCIF。

#### 输出

- 标准 TIFF、最佳焦平面、配准与背景校正后的图像；
- 核/细胞 mask，以及每个细胞的强度、坐标、形态和亚细胞区室特征；
- 丢失组织、残留信号和非特异结合的质控标记；
- 细胞类型、单细胞和样本级空间富集分数、空间邻域；
- 受体—配体 immunoprint、Napari 交互图层和相邻切片 3D 重建。

### 完整流程

```text
原始多轮空间图像
        |
        v
Meta-module 1：格式统一 -> 对焦 -> 配准/背景 -> 分割 -> 特征提取
        |
        v
Meta-module 2：TMA core -> 强度归一 -> 组织损伤 -> 漂白残留 -> NSB
        |
        v
质量控制后的“细胞 × 标记 + 坐标”表
        |
        v
Meta-module 3：细胞分型 -> RDF 空间分数 -> immunoprint/邻域 -> 可视化/3D
```

### Meta-module 1：把图像变成单细胞表

#### 1. 格式标准化和自动对焦

OME Bio-Formats 把 161 种支持格式转换为单通道、单平面的 TIFF。对于多个 Z-plane，CROCHET 用归一化方差选择最清晰平面：

$$
\widetilde{\sigma}=\frac{\sum_{p}(I_p-\bar I)^2}{\bar I}.
$$

分子是像素强度离散程度，分母校正整体亮度。图 2A 中 Z3 的数值 9519 高于 Z1 的 6922，视觉上也更清晰；这是示范，不是跨数据集焦点评测。

#### 2. 配准、背景和分割

论文复用 CycIFAAP，以重复核染色为锚点配准各轮图像并扣除背景。核由 Mask R-CNN 分割，细胞边界优先依据 E-Cadherin、CD45、CD44 等膜标记；没有合适膜标记时，从核向外扩张，直到遇到邻居或达到默认的 3 倍核大小。Cellpose 也被描述为替代选项。

每个细胞输出核、胞质和细胞表面区室的均值、方差、偏度、峰度，以及坐标、边界框、距组织边缘距离、大小、方向、圆度和 Haralick 纹理等。TMA core 通过细胞坐标上的 HDBSCAN 自动分离。

### Meta-module 2：循环成像伪影如何被识别？

#### 1. 曝光与光强归一化

不同轮次/通道的信号按光强和曝光时间校正：

$$
F^{norm}_{i,C,R}=\frac{F_{i,C,R}}{LI_{C,R}\,ET_{C,R}}.
$$

这使同一标记或通道跨轮比较更合理，但不能自动修复抗体批次差异或非线性饱和。

#### 2. 组织损伤检测

每轮都有 Hoechst 核信号，可与第一轮逐细胞比较。流程先删除核强度低于第一轮 50% 的细胞，再对强度比计算中位数和 MAD，识别偏离群体的骤降。被判定为丢失的细胞从该轮及后续轮次剔除。

论文的 Eq. 6 存在符号歧义：它写成 $\Delta r<3r_{MAD}$，若 $\Delta r$ 以中位数为中心，这会把接近零的大量正常细胞也判异常。生物学意图更像是“低于中位数至少 3 MAD”，即 $\Delta r<-3r_{MAD}$。没有公开代码，无法确定实际实现采用哪一个条件，因此此处保留为 `Not found / equation ambiguity`。

#### 3. 漂白残留递归校正

先用 Otsu 阈值分开前景和背景，估计漂白图像与染色图像的归一化信号差之比：

$$
C_{residue}=\frac{I_{diff}^{norm,bleached}}{I_{diff}^{norm,stained}}.
$$

再递归扣除上一轮的校正信号：

$$
F^{corr,norm}_{i,C,R}=F^{norm}_{i,C,R}-C_{residue}F^{corr,norm}_{i,C,R-1}.
$$

“递归”很重要：第 $R$ 轮依赖已经修正的第 $R-1$ 轮，而不是每轮都只减原始上一轮信号。

#### 4. 非特异结合（NSB）

对每个通道、轮次和亚细胞位置，若细胞强度排名超过默认 85% 分位，则记为高亮：

$$
\frac{Rank(I_{i,c,r,l})}{N}>T.
$$

只有同一细胞、同一通道、同一亚细胞区室连续 4 轮都高亮，当前标记才被判为 NSB 并移除。这个规则利用了“抗体已经换了，但人工高亮结构位置不变”的特征。它提高特异性，却仍可能删除确实在多轮标记上都强阳性的细胞；论文没有报告系统性的误删率。

### Meta-module 3：空间富集分数

#### 1. 从无标记 RDF 开始

对中心细胞 $i$，距离 $r$、厚度 $dr$ 的圆环内细胞密度为：

$$
g_i(r)=\frac{\sum_{j\in\Omega_{i,r}}dn_j}{2\pi N r\,dr}.
$$

这个量只描述组织几何，不使用标记或细胞类型。

#### 2. 连续表达如何变成权重？

对 log2 转换、Z-score 后的标记表达 $x_{a,i}$：

$$
w_{a,i}=\tanh\left(\frac{x_{a,i}+|x_{a,i}|}{2}\right).
$$

内部的 $(x+|x|)/2$ 等价于 ReLU：负值变 0，正值保留；`tanh` 再让大正值逐渐饱和到 1。它是一种软阳性权重，比硬阈值保留更多强度信息。

#### 3. 加权 RDF 和密度归一化

标记 $a$ 的中心细胞与邻居标记 $b$ 的加权 RDF 为：

$$
g_{ab,i}(r)=\frac{N}{N_aN_b}\frac{w_{a,i}\sum_{j\in\Omega_{i,r}}w_{b,j}}{2\pi r\,dr}.
$$

单细胞空间分数把半径内加权 RDF 除以所有细胞的无权 RDF：

$$
S_{i,a,b}(r)=\frac{N^2}{N_aN_b}
\frac{w_{a,i}\sum_{j\in NN_{i,r}}w_{b,j}}
{\sum_{j\in NN_{i,r}}dn_j}.
$$

分母是局部总细胞数，所以在稠密区域中仅仅“邻居多”不会自动变成强富集。若用户希望把总体丰度也纳入，可用：

$$
S^{AD}_{i,a,b}(r)=S_{i,a,b}(r)\frac{N_aN_b}{N^2}.
$$

样本级分数对所有中心细胞求和。论文声称其在大距离处趋近 1 且不随细胞总数缩放，因此可跨样本比较。这个性质来自归一化形式；论文没有用跨组织金标准或模拟系统地验证其校准误差。

#### 4. 细胞类型、immunoprint 和邻域

细胞类型分数只需把 $w_{a,i}$ 换成 0/1 类型指示变量。Immunoprint 再同时要求细胞属于类型 $a$ 且表达标记 $m$，用同一分数框架衡量特定细胞界面上的受体—配体共分布，例如上皮—CD8 T 细胞界面的 PD1:PDL1。

要构建组织邻域，论文描述先对单细胞空间分数做 log2 归一化和 Z-score，PCA 降维、kNN 建图，再聚类并投回组织坐标。这里存在文本不一致：开头称 Louvain，后文明确调用 `scanpy.tl.leiden`；图 3 图注也写 Louvain。没有源代码，无法判定实际成图版本。

### 3D 相邻切片重建

每个细胞用三个用户指定半径下的点密度组成向量 $D_i=(d_{i1},d_{i2},d_{i3})$。相邻切片细胞与参考切片细胞通过余弦相似度配对：

$$
K(i,j)=\frac{\langle D_i,D_j\rangle}{\|D_i\|\,\|D_j\|}.
$$

候选配对用于估计旋转和平移的欧氏变换，并迭代到变换矩阵接近单位矩阵。它提供组织级对齐，但“相似局部密度”不等于同一真实细胞，论文也没有把它作为细胞谱系追踪。

### 三幅主图说明了什么？

#### 图 1：模块地图

从左到右把信号定量、质控清洗和空间分析串在一起，明确每个产物如何进入下一阶段。它证明流程设计完整，不证明每个模块都优于已有方法。

#### 图 2：成像质控示例

图 2A–D 展示自动对焦、Mask R-CNN 分割、强度分布和 HDBSCAN core 检测；图 2E 显示第 1–9 轮中红色损伤区域逐渐增多；图 2F 显示不同抗体轮次在相同位置重复高亮的 NSB。图像支持这些伪影确实存在且规则能标记示例，但论文没有报告灵敏度、特异度或与人工标注的系统比较。

#### 图 3：空间图谱产物

图 3 展示 Napari 多尺度查看、Flask 层级门控、$S^{AD}$ 与 $S$ 热图、五位小肠腺癌患者的 PD1:PDL1 immunoprint、空间邻域和两张相邻切片的 3D 对齐。它是功能演示；不能据此声称 P1/P2 一定适合某种免疫治疗，因为没有临床响应验证或统计显著性检验。

### 论文展示的评估范围

- 示范数据来自 10 轮、5 通道、20×、0.33 μm/pixel 的 CyCIF TMA；主要展示 5 个 core。
- 论文提到 Mask R-CNN 在其训练数据上达到 96.9% accuracy 和 0.83 Dice，但没有给出跨组织泛化基准。
- 与 MCMICRO、SIMPL 和 TRACERx-PHLEX 的关系主要在补充功能表中比较，没有共享数据集上的定量速度、准确率或资源消耗对照。
- 对 Xenium 等其他平台的适用性是架构主张，正文没有对应的多平台验证结果。

### 可复现性与证据边界

这是当前工作区最重要的限制：

- 论文“Code Availability”只写软件和成图代码可用，没有仓库 URL、版本或 commit。
- 当前 PaperCode 工作区没有代码目录，因此所有实现细节只能标为 `paper-described`，不能标为代码验证的 Exact。
- 示例 SBA 图像和元数据需通过 MD Anderson Data Cloud 申请，不是直接公开下载。
- 模型权重、完整环境、默认参数配置和一键运行入口均 `Not found`。
- 论文写 Python/Scanpy，却在邻域方法结尾提到 “Seurat functions”；这可能是文本残留，无法用源码裁决。

因此可复现性应评为较低（约 2/5）：数学定义足够支持独立重实现，但无法验证作者实际成图代码是否逐式遵循论文，也无法一键复现示范结果。

### 如何正确理解 CROCHET 的贡献？

最可信的贡献是一个覆盖循环成像关键伪影、空间定量和可视化的统一设计，以及密度归一化 RDF 分数与 immunoprint 的明确数学定义。最需要进一步证据的，是“跨平台通用”“跨组织分数直接可比”和“临床匹配免疫治疗”等更广泛主张。

对研究者而言，CROCHET 提供的是一张很好的方法蓝图：先把成像质量问题显式建模，再把组织几何作为空间共定位的基线。要把蓝图变成可依赖的软件，还需要公开可版本化代码、测试数据、参数契约、跨平台基准和空间分数的统计校准。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CROCHET: ChaRacterization Of Cellular HEterogeneity in Tissues

### Paper Information

- **Title**: CROCHET: a versatile pipeline for automated analysis and visual atlas creation from single-cell spatialomic data
- **Authors**: Behnaz Bozorgui, Guillaume Thibault, Chunyu Yuan, Zeynep Dereli, Huamin Wang, Michael J. Overman, John N. Weinstein, Anil Korkut
- **Affiliations**: MD Anderson Cancer Center (Bioinformatics & Computational Biology, Anatomical Pathology, GI Medical Oncology); Oregon Health & Science University (Biomedical Engineering)
- **Journal**: bioRxiv (Preprint)
- **Year**: 2026
- **DOI**: 10.64898/2026.03.13.711472

### Motivation & Novelty

#### Problem

Spatial omics technologies (CyCIF, CODEX, COMET, Xenium) generate unprecedented detail on tissue composition at single-cell resolution, but the transformation from raw multiplexed images to biologically interpretable spatial atlases faces multiple analytical bottlenecks. Key unsolved challenges include: (1) artifact correction in cyclic imaging (residual fluorescence, tissue damage, non-specific binding), (2) spatial metrics that are confounded by tissue density variations, making cross-sample comparison unreliable, and (3) fragmented tool ecosystems that require manual stitching of independent processing, QC, and analysis software.

#### Limitations of Existing Approaches

- **MCMICRO** (*Nature Methods*, 2022): Scalable image processing pipeline but lacks integrated spatial analysis and artifact correction modules
- **SIMPLI** (*Nature Communications*, 2022): Single-cell identification from multiplexed images but limited spatial quantification beyond basic phenotyping
- **TRACERx-PHLEX** (*Nature Communications*, 2024): Deep cell phenotyping with spatial analysis but designed primarily for lung cancer TRACERx cohort rather than as a general-purpose pipeline
- **Conventional spatial metrics**: Point-density-based methods (nearest-neighbor counts, binary adjacency) fail to account for tissue density heterogeneity and cannot compare across different tissue types

#### Unique Contributions

1. **Spatial enrichment score** (Eqs. 12-18): An RDF-based, expression-weighted metric that normalizes by local tissue density, enabling direct comparison of spatial co-arrangements across heterogeneous tissue types. The sample-level score converges to 1 at large distances, providing a natural reference scale for cross-tissue comparison.
2. **Immunoprint framework** (Eq. 20): Combines cell-type identity with biomarker expression to quantify receptor-ligand interactions (e.g., PD1:PDL1) on specific cell-type interfaces, visualized as cohort-level heatmaps analogous to genomic oncoprints.
3. **Automated QC pipeline**: Novel modules for lost tissue detection (3-MAD outlier detection on nuclear staining ratios), recursive bleach correction (estimating carryover fraction from bleached images), and rank-based non-specific binding removal (4-cycle consistency criterion).
4. **3D tissue reconstruction**: Density-profile-based cell matching across adjacent tissue slices with iterative Euclidean transformation.
5. **End-to-end integration**: Modular architecture supporting 161 image formats, multiple segmentation methods (Mask R-CNN, Cellpose), interactive cell typing (Flask app), and layered visualization (Napari).

### Method Overview

CROchet is organized into three meta-modules:

**Meta-Module 1 (Signal Quantification)**: Converts raw multiplexed images from vendor-specific formats to standardized TIFF, selects optimal focal planes via normalized variance, registers multi-cycle images using SIFT/ORB keypoint detection, segments nuclei with Mask R-CNN, defines cell boundaries using membrane markers (or 3x nuclear expansion fallback), and extracts per-cell intensity, spatial, and morphological features from four subcellular zones.

**Meta-Module 2 (Quality Control)**: Automates TMA core detection (HDBSCAN), intensity/exposure normalization, lost tissue detection (nuclear staining ratio monitoring with 3-MAD criterion), residual fluorescence correction (recursive bleach subtraction using OTSU-estimated carryover coefficients), and non-specific binding removal (rank-based detection requiring high-intensity persistence across 4 consecutive cycles in the same channel/compartment).

**Meta-Module 3 (Downstream Analysis)**: Provides interactive hierarchical cell typing via a Flask application, computes spatial enrichment scores at single-cell and sample levels using expression-weighted radial distribution functions (with optional abundance normalization), generates immunoprints for receptor-ligand interaction mapping across patient cohorts, performs neighborhood detection via Leiden clustering on PCA-reduced spatial scores, offers Napari-based interactive visualization, and reconstructs 3D tissue maps from adjacent slices.

See doc_method.md for full mathematical formulation (22 equations) and algorithm walkthrough.

### Evaluation

#### Demonstration Dataset

- CyCIF tissue microarray (TMA) from Dereli et al. (bioRxiv, 2025): 10 cycles, 5 fluorescence channels per cycle, Hoechst nuclear staining, 20x magnification (0.33 um pixel size)
- 5 TMA core scenes used for workflow demonstration; full TMA cohort used for mean properties
- Small Bowel Adenocarcinoma tissue

#### Demonstrated Capabilities

- **Focus evaluation** (Fig. 2A): Normalized variance correctly selects sharpest Z-plane (Z3, variance=9519 vs Z1=6922)
- **Segmentation** (Fig. 2B): Mask R-CNN detects nuclei and cell boundaries; cell annotations show bounding boxes for individual cells
- **Tissue damage detection** (Fig. 2E): Progressive tissue loss across 9 cycles clearly visualized; red-marked damaged regions increase in later cycles; correlation plots show deviation from first-cycle baseline
- **Spatial enrichment scores** (Fig. 3C-D): Heatmaps show distinct patterns between abundance-dependent ($S^{AD}$) and density-normalized ($S$) scores, demonstrating that normalization reveals spatial co-arrangements independent of overall expression
- **Immunoprint** (Fig. 3E): PD1:PDL1 interaction patterns across 5 bowel adenocarcinoma patients show patient-specific immune checkpoint co-distributions on tumor-immune interfaces, with highest scores on Epithelial_KI67-/EAL_CD8+T and Epithelial_KI67+/EAL_CD8+T interfaces
- **Neighborhood analysis** (Fig. 3F): Louvain/Leiden clustering identifies spatially distinct tissue neighborhoods enriched for KI67+ epithelial cell interactions
- **3D reconstruction** (Fig. 3G): Adjacent tissue slices aligned and rendered with CD68 expression as color map

#### Quantitative Benchmarks

The paper focuses on pipeline demonstration rather than formal benchmarking. No direct quantitative comparisons with MCMICRO, SIMPLI, or TRACERx-PHLEX are presented beyond a supplementary comparison table. The Mask R-CNN segmentation model reports 96.9% accuracy and 0.83 Dice score on its training data (HER2+ breast cancer TMA), but cross-tissue generalization is not formally evaluated.

### Reproducibility

**Rating: 2/5**

**Justification**:
- (-) Code is stated as available but **no repository URL** is provided; GitHub search finds no public repo under the Korkut Lab organization
- (-) Data is available "upon request" through MD Anderson Data Cloud, not as open-access download
- (-) No formal benchmarks or comparison experiments that others could replicate
- (-) Mask R-CNN model trained on specific HER2+ breast cancer data; weights not publicly available
- (+) Mathematical formulation is complete and detailed (22 equations) — sufficient for reimplementation
- (+) Dependencies are all open-source (scanpy, OpenCV, Napari, Flask, Cellpose, HDBSCAN)
- (+) Modular design means individual components could be replaced

**Practical Notes**:
- **Environment**: Python-based with standard scientific computing stack (NumPy, SciPy, scikit-learn, scanpy, OpenCV, Napari, Flask)
- **Hardware**: GPU required for Mask R-CNN segmentation; rest is CPU-feasible
- **Dependencies**: CycIFAAP pipeline for registration/background; OME Bio-Formats for image conversion
- **Key parameters to set**: focus variance threshold, tissue loss intensity threshold (default 50%), MAD multiplier (default 3), NSB percentile threshold (default 85%), RDF bin size, neighborhood radius, Leiden resolution

### Strengths

1. **Comprehensive scope**: True end-to-end pipeline from raw images to spatial atlas, covering preprocessing, QC, analysis, and visualization in a single framework
2. **Novel spatial metric**: RDF-based spatial enrichment score with density normalization is theoretically sound and addresses a real limitation of existing point-density metrics
3. **Immunoprint concept**: Creative application of spatial scores to receptor-ligand interaction mapping across patient cohorts — directly clinically relevant for immunotherapy biomarker discovery
4. **Detailed math**: 22 equations fully specifying every computational step; sufficient for independent reimplementation
5. **Interactive components**: Flask-based cell typing app and Napari visualization are practical tools for biologists without programming expertise

### Weaknesses

1. **No public code**: Despite claiming code availability, no repository URL exists. This is the most significant limitation for a methods paper.
2. **No comparative benchmarks**: Comparison with MCMICRO/SIMPLI/TRACERx-PHLEX is limited to a supplementary feature table rather than quantitative performance comparison on shared datasets
3. **Limited validation scope**: Demonstration on a single CyCIF dataset (Small Bowel Adenocarcinoma). Claims of broad applicability to CODEX, Xenium, etc. are not validated
4. **Segmentation model**: Mask R-CNN trained specifically on HER2+ breast cancer — generalization to other tissue types and imaging conditions is untested
5. **Louvain/Leiden inconsistency**: Main text references Louvain clustering, methods section describes Leiden; likely Leiden is used (scanpy.tl.leiden)
6. **Seurat reference in Python pipeline**: The neighborhood analysis methods paragraph references "Seurat functions" despite the pipeline being Python/scanpy-based — this appears to be a copy-paste error from R documentation
7. **3D reconstruction simplicity**: Cosine similarity on 3-distance density profiles is a coarse matching criterion that may not capture fine structural features
8. **No statistical tests on spatial scores**: The paper does not report significance testing for spatial enrichment scores or immunoprints (e.g., permutation tests, confidence intervals)
9. **Eq. 6 sign ambiguity**: The tissue loss detection equation as written ($\Delta r < 3r_{mad}$) would flag most cells; the intended condition is likely $\Delta r < -3r_{mad}$ (below-median deviation)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
