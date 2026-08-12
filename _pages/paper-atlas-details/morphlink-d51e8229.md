---
layout: default
permalink: /paper-atlas/morphlink-d51e8229/
title: "MorphLink"
nav: false
description: "MorphLink 的目标不是把 H&E 图像和空间组学数据压进同一个黑箱嵌入，而是先从图像中提取可命名、可度量的结构特征，再用 Curve-based Pattern Similarity Index（CPSI）判断某个形态特征与某个基因、蛋白或其他分子测量是否具有相似的局部空间变化。最终结果是“什么组织结构发生了怎样的形态变化，并与哪种分子动态同位出现”。"
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
      <span>Segmentation &amp; Annotation</span>
      <span>Nature Communications · 2025</span>
    </div>
    <h1>MorphLink</h1>
    <p>Bridging cell morphological behaviors and molecular dynamics in multi-modal spatial omics with MorphLink</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-025-61142-0" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MorphLink 中文方法解读

### 一句话理解

MorphLink 的目标不是把 H&E 图像和空间组学数据压进同一个黑箱嵌入，而是先从图像中提取可命名、可度量的结构特征，再用 Curve-based Pattern Similarity Index（CPSI）判断某个形态特征与某个基因、蛋白或其他分子测量是否具有相似的局部空间变化。最终结果是“什么组织结构发生了怎样的形态变化，并与哪种分子动态同位出现”。

### 1. 输入、输出与分析单位

典型输入是同一组织切片上的 H&E 图像、空间测量点坐标，以及点乘分子的表达/丰度矩阵。对于 10x Visium，每个测量点对应一个以坐标为中心的图像 patch；其他空间平台也可按其测量位置构造相应 patch。

主要输出包括：

- 每个 patch 的多个二值结构 mask；
- 每个 mask 的组织布局特征和对象形状特征；
- 分子特征乘形态特征的 CPSI 矩阵；
- 局部子区域和边际曲线；
- 用代表性 patch、mask 高亮和箭头展示的形态—分子联动图。

因此 MorphLink 是解释与关联框架，不是细胞分割真值生成器，也不是因果推断模型。

### 2. 从整张切片到空间 patch

流程先检测组织区域、排除空白，再按固定网格或空间组学点坐标裁切 patch。`patch_split_for_ST()` 以每个点的像素坐标为中心截取固定大小图块；`patch_split_with_mask()` 则只保留组织覆盖比例超过阈值的网格块。

patch size 决定观察尺度：过小会遗漏基质、纤维束或细胞群组织，过大则把不同微环境混在一起。代码提供可视化测试，而不是自动保证最优尺度。

### 3. 无监督、空间感知的颜色分割

每个 patch 首先按 RGB 值做 K-means，默认约 10 个颜色簇。H&E 中苏木精和伊红对核、胞质与基质产生不同颜色，这使颜色簇可作为候选组织结构，但初始簇仍可能呈现椒盐噪声。

`refine_labels()` 检查像素的 8 邻域：若同类邻居不足阈值（默认 4），就把该像素改为邻域众数类别；迭代让局部标签更连续。随后 `merge_labels()` 比较簇的代表颜色，使用 RGB 中位数差的最大值作为距离，在阈值内合并相似簇。

直观例子：一个孤立深蓝像素若周围七个像素都属于粉色基质簇，会被修正为基质；但一片连续的深蓝核区域会保留。此步骤引入空间平滑，也意味着极小、真实的结构可能被删除。

### 4. 跨 patch 对齐 mask

单独对每个 patch 分割后，“簇 2”在一个 patch 可能是细胞核，在另一个 patch 可能是基质。MorphLink 使用颜色距离在 patch 间匹配候选簇，建立整张切片一致的 mask channel。严格和宽松两个阈值控制匹配，并用未匹配比例和新通道利用率过滤不稳定 mask。

输出的每个 channel 是一组跨 patch 二值 mask。用户仍需结合颜色、位置和代表性 patch 判断它主要对应核、CAF、stroma、纤维或其他结构；无监督颜色簇本身不携带细胞类型标签。

### 5. 两层可解释形态特征

#### 5.1 Mask-level：结构在 patch 中怎样分布

`Extract_Whole_Mask_Features()` 对每个 mask 计算约 10 个特征，包括结构面积、面积比例，以及前景/背景距离变换的均值、中位数、标准差和 IQR。面积描述“有多少”，距离变换描述结构的厚度、连续性、空隙和布局异质性。

例如 stroma 面积比例高表示基质占据更多 patch；stroma 像素距离 IQR 高表示基质宽度或连续程度变化更大。

#### 5.2 Object-level：mask 内对象是什么形状

连通组件检测把二值 mask 拆为单个核、聚集体或纤维束等对象。代码基于 region properties 计算面积、凸包面积、离心率、长短轴、方向、周长、solidity、extent 等，并在 patch 内汇总中位数、标准差、IQR 和分位数；还汇总对象中心间距离。

论文称每个 mask 可产生 10 个 mask-level 和 109 个 object-level 特征；通常 8–10 个 mask，合计约 1,000 个有名称的特征。数量会受有效对象、过滤和所用函数版本影响。

`Selective_Log_Transfer()` 比较原值和 $\log(x+1)$ 变换后的归一化离散度，选择能更好拉开样本的表示。该步骤是数据驱动变换，不改变特征的基本含义，但会改变数值尺度。

### 6. 为什么普通全局相关不够

两个特征可能只在肿瘤边缘、TLS 或某个脑区共同变化，而在全切片其他区域近乎恒定。全局 Pearson 相关会被大面积无关区域稀释，也可能因两个不同组织区的均值差而产生伪相关。

MorphLink 先分别对分子矩阵和图像特征聚类，再用 Jaccard 重叠把两套空间簇组合成子区域。代码 `combine_clusters()` 使用最小和最大重叠阈值处理匹配，使 CPSI 在局部相对一致的组织背景中计算。

### 7. CPSI：把二维空间模式压成可比较曲线

在每个子区域内，沿 $x$ 和 $y$ 方向划分区间。`calculate_summary_curves()` 对落入每个区间且达到 `min_spots` 的测量点取均值或中位数，从而将二维分布概括为两条边际曲线。

对一对特征，代码支持三类比较：

- `cor`：比较曲线相关，强调同升同降趋势；
- `diff`：比较绝对差异，强调数值接近；
- `var`：比较变化结构。

论文的 CPSI 将趋势相似与幅度相似结合，并按有效 $x/y$ 区间数加权：

$$
\operatorname{CPSI}_k
=w_k\operatorname{Sim}_x+(1-w_k)\operatorname{Sim}_y,
\qquad
w_k=\frac{t_x}{t_x+t_y}.
$$

最后按子区域包含的测量点比例汇总：

$$
\operatorname{CPSI}
=\sum_k\frac{|S_k|}{N}\operatorname{CPSI}_k.
$$

从左到右读：先在局部区域比较两个方向上的空间变化，再让覆盖更多测量点的区域对全局分数贡献更大。CPSI 高表示空间共变模式相似，并不说明基因表达导致形态改变。

### 8. 从一个高分链接回到可视证据

MorphLink 不停在 CPSI 排名。它选择目标形态特征的低、中、高值 patch，叠加对应 mask，并同时展示分子表达变化。这样读者可以核对“核 solidity 的 IQR 增加”究竟在图像上表现为何种核组织变化，而不是只看到一个抽象相关系数。

论文还对预定义生物过程基因集进行单侧 t-test：比较目标形态特征与该基因集的 CPSI，是否高于同一基因集与其他形态特征的 CPSI。这是集合级支持证据，但分数之间共享基因、空间点和特征，独立同分布假设并不严格成立。

### 9. 六张主图提供的证据

- 图 1：完整工作流，包括 patch、无监督 mask、连接组件、可解释特征、子区域、边际曲线、CPSI 和形态可视化。
- 图 2：在人膀胱癌中把 CD74 与核 solidity IQR（CPSI 0.580）联系起来，把 MYCL 与 CAF 面积（0.637）联系起来，分别解释抗原呈递和增殖相关区域的形态差异。
- 图 3：将 IGHM 与淋巴核最大聚集簇大小联系起来，区分 TLS 和弥散 TIL，展示组织层级特征而非单核形状。
- 图 4：在三份 HER2+ 乳腺癌样本中使用 stroma 像素距离 IQR，支持跨样本识别基质，并区分浸润癌与原位癌；同时以侵袭癌富集基因验证 CPSI。
- 图 5：在小鼠脑中把 NRN1 等神经发育表达模式与核方向 IQR 联系起来，展示方法对发育空间梯度的应用。
- 图 6：在带模糊伪影的斑马鱼黑色素瘤图像中比较深度特征和 MorphLink，后者用纤维束面积连接肿瘤/肌肉界面基因，支持其对局部染色伪影的一定稳健性。

论文还报告乳腺癌、鼠胚、tonsil、空间 CITE-seq 等扩展分析，并将 CPSI 与相关、SSIM 和 RMSE 比较。本工作区没有收录在线补充材料，因此这些补充图表不能在本地逐页复核。

### 10. 论文与本地代码对应

本地包为 MorphLink 1.0.7，来源 `https://github.com/jianhuupenn/MorphLink`；未保留可验证 commit。

| 论文步骤 | 本地实现 | 对应程度 |
|---|---|---|
| 组织区与 patch 提取 | `tissue_seg_util.py`、`tissue_patch_util.py` | Exact |
| K-means 颜色分割 | `mask_util.segment_patches` | Exact |
| 邻域修正和颜色合并 | `refine_and_merge_util.py` | Exact；文件内存在重名 `merge_labels` 定义，后定义覆盖前定义 |
| 跨 patch mask 匹配 | `mask_util.py` | Exact |
| Mask-level 特征 | `Extract_Whole_Mask_Features` | Exact |
| 连通组件与 object-level 特征 | `cc_util.py`、`Extract_CC_Features` | Partial：文件内多个重名版本，运行时以后定义为准 |
| 选择性 log 变换 | `Selective_Log_Transfer` | Exact |
| 子区域组合 | `pattern_similarity.combine_clusters` | Exact |
| CPSI 曲线与汇总 | `calculate_summary_curves`、`pattern_similarity` | Partial：源码包含重复函数定义和多个 metric/pooling 选项，需以实际调用参数固定行为 |
| 代表性 patch 可视化 | `tutorial_util.py`、`illustrate_util.py` | Exact |
| 论文全部统计与多数据集复现 | package + tutorial | Partial/Not found：教程覆盖核心流程，完整论文分析脚本和补充材料未全部收录 |

### 11. 使用边界

1. 颜色分割受染色、扫描仪、切片和 patch size 影响；跨研究分析通常仍需要染色归一化。
2. 无监督 mask 需要人工解释，颜色相似不保证相同细胞类型或组织成分。
3. CPSI 将二维图案压缩为两条边际曲线；旋转、复杂环形或高度局部的模式可能在压缩中丢失。
4. 子区域来自两种模态的聚类，阈值变化会改变局部背景和最终 CPSI，应进行敏感性分析。
5. 高 CPSI 是空间共现，不控制所有组织组成、空间自相关和多重检验，也不是因果链接。
6. MorphLink 偏重局部、可解释形态；论文也承认对需要全局组织结构的聚类任务，深度图像特征可能更合适。
7. 本地源码存在重复函数定义且缺乏自动测试；发布包能运行不等于每条论文分析路径已冻结复现。

### 证据入口

- 论文与图注：`paper source/paper/paper.md`
- 本地主图：`paper source/paper/_page_*_Figure_2.jpeg`
- 核心编排：`MorphLink_package/MorphLink/main_functions.py`
- 分割与 mask：`mask_util.py`、`refine_and_merge_util.py`
- 特征：`extract_hancraft_features_util.py`、`cc_util.py`
- CPSI：`pattern_similarity.py`
- 教程：`tutorial/tutorial.md`、`tutorial/tutorial.ipynb`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MorphLink: Bridging Cell Morphological Behaviors and Molecular Dynamics in Multi-Modal Spatial Omics

### Publication Information
- **Journal**: Nature Communications (2025)
- **DOI**: https://doi.org/10.1038/s41467-025-61142-0
- **Authors**: Jing Huang, Chenyang Yuan, Jiahui Jiang, et al.
- **Corresponding Authors**: Linghua Wang, Jian Hu
- **GitHub**: https://github.com/jianhuupenn/MorphLink

### Core Problem and Motivation

#### The Gap in Current Spatial Omics Analysis
Multi-modal spatial omics data provides both morphological (H&E histology images) and molecular (gene expression, protein abundance, chromatin accessibility) perspectives on cellular behavior. However:

> "Current analytical methods primarily focus on clustering and classification, and do not adequately examine the relationship between cell morphology and molecular dynamics." (Paper, Page 1)

#### Limitations of Existing Approaches
1. **Deep learning features lack interpretability**: "Image features from neural networks are often not transparent, making biological interpretation difficult." (Paper, Methods section)

2. **Nuclei-focused tools miss critical structures**: "Tools like QuPath, CellVit, and Hover-Net primarily focus on nuclear structures and often overlook other non-nuclei structures, such as the extracellular matrix and collagen fibers." (Paper, Page 2)

3. **Manual pathologist assessment is subjective**: "Efforts to assess the relationship between cell morphology and omics measurements largely depend on manual examination by pathologists, which are prone to errors and inter-reader variability." (Paper, Page 2)

### MorphLink Framework: Three Primary Goals

1. **Extract comprehensive morphological measurements** with high interpretability in a label-free manner
2. **Efficiently quantify relationships** between cell morphological and molecular features in a spatial context
3. **Visually demonstrate** how cellular behavior changes from both morphological and molecular perspectives

### Technical Innovation

#### 1. Unsupervised Spatially-Aware Image Segmentation

**K-means Pixel Clustering with Spatial Refinement**:

The segmentation process involves three steps:

**Step 1: K-means clustering** (default k=10)
- Cluster pixels based on RGB color values
- Extracts each pixel's three-channel color values $(r_p, g_p, b_p)$

**Step 2: Spatial voting refinement**
For pixel $v$ assigned to cluster $c(v)$:

$$c(v)' = \begin{cases} c(v) & \text{if } \sum_{i=1}^{8} I(c(u_i) = c(v)) \ge t \\ \text{mode}(\{c(u_1), c(u_2), \ldots, c(u_8)\}) & \text{otherwise} \end{cases}$$

where $t=4$ (default threshold) controls cluster integrity.

**Step 3: Color-based cluster merging**
Merge clusters if color distance < $\alpha$ (default=30):

$$\text{dis}(\text{cluster}_i, \text{cluster}_j) = \max(|\text{med}(\mathbf{r_i}) - \text{med}(\mathbf{r_j})|, |\text{med}(\mathbf{g_i}) - \text{med}(\mathbf{g_j})|, |\text{med}(\mathbf{b_i}) - \text{med}(\mathbf{b_j})|)$$

#### 2. Comprehensive Feature Extraction (~1000 interpretable features)

**Mask-Level Features** (10 features per mask):
- Area of structure
- Area proportion (ratio to patch)
- Distance transform statistics (mean, median, std, IQR) for both foreground and background pixels

**Object-Level Features** (109 features per mask):
From connected component detection using the Spaghetti algorithm:
- Shape properties: area, bbox_area, convex_area, eccentricity, equivalent_diameter, extent, filled_area, major_axis_length, minor_axis_length, orientation, perimeter, solidity
- Summary statistics: median, std, IQR, quantiles (0, 25, 50, 75, 100)
- Pairwise distance statistics between detected objects

**Total Features**: With 8-10 masks typical per H&E image, approximately 1000 interpretable features.

#### 3. Curve-based Pattern Similarity Index (CPSI)

The novel metric for quantifying spatial pattern similarity:

**Subregion Division**:
Using Jaccard index to merge overlapping clusters from gene expression and image feature clustering:
$$\frac{n(\mathbf{s_{1i}} \cap \mathbf{s_{2j}})}{n(\mathbf{s_{1i}} \cup \mathbf{s_{2j}})} > \beta$$
(default $\beta = 0.2$)

**Marginal Curve Calculation**:
For feature $\mathbf{f}$ within a subregion, divide into $t_x$ intervals:
$$t_x = \left\lceil \frac{\max(x) - \min(x)}{l} \right\rceil$$

Generate curve vectors:
$$\text{curve}_x = (m_{1x}, m_{2x}, ..., m_{t_x,x})$$

where $m_{ix}$ is the median feature value in interval $i$.

**Similarity Quantification**:
$$\text{CPSI}(\mathbf{f_1}, \mathbf{f_2}) = w \times \text{Similarity along X} + (1 - w) \times \text{Similarity along Y}$$

where:
$$\text{Similarity along X} = \rho(\text{curve}_{1x}, \text{curve}_{2x}) + \left(1 - \frac{||\text{curve}_{1x} - \text{curve}_{2x}||_1}{t_x}\right)$$

and weight:
$$w = \frac{t_x}{t_x + t_y}$$

**Global CPSI**:
$$\text{Global CPSI}(\mathbf{f_1}, \mathbf{f_2}) = \sum_{k=1}^{K} \frac{C(s_k)}{N} \times \text{CPSI}_k(\mathbf{f_1}, \mathbf{f_2})$$

### Biological Validation and Applications

#### Application 1: Human Bladder Cancer - Tumor Heterogeneity

**Nuclei-Antigen Presentation Linkage**:
- CD74 (antigen presentation gene) linked to IQR of nuclear solidity
- CPSI = 0.580
- P-value = $3.1 \times 10^{-34}$ (35 antigen-presenting genes)
- Biological interpretation: "The loosening and opening of chromatin are typically associated with an increase in transcriptional activity, including the activation of genes involved in antigen presentation."

**CAF-Tumor Proliferation Linkage**:
- MYCL (proliferation marker) linked to CAF area
- CPSI = 0.637
- P-value = $1.7 \times 10^{-4}$ (46 tumor proliferation genes)
- Biological interpretation: Increased CAF region surrounding tumor cells supports tumor growth and invasion

#### Application 2: Immune Diversity Characterization

**TLS vs Diffuse TIL**:
- IGHM linked to largest cluster size of lymphoid nuclei aggregation
- CPSI = 0.483
- P-value = $1.0 \times 10^{-3}$ (28 TLS-enriched genes)
- TLS regions show significantly larger feature values (p = $3.2 \times 10^{-9}$)

#### Application 3: Multi-Sample HER2+ Breast Cancer

**Stromal Pattern Detection**:
- IQR of stroma pixel distance consistently identifies stromal regions across 3 samples
- Discriminates invasive cancer vs. cancer in situ:
  - A1: p = $1.0 \times 10^{-2}$
  - G2: p = $4.3 \times 10^{-2}$
  - H1: p = $2.3 \times 10^{-7}$

#### Application 4: Mouse Brain Neurology

**Neuronal Development**:
- NRN1 (neuron development gene) linked to IQR of nuclei orientation
- CPSI = 0.625
- P-value = $1.46 \times 10^{-22}$ (30 neuron development genes)
- Captures radial migration of neuronal cells during development

### Robustness Against Image Artifacts

Analysis of zebrafish melanoma dataset with blurriness artifacts:
- Deep learning features (HIPT, ResNet) identified blurred regions as separate clusters (artifacts)
- MorphLink features showed robustness, correctly identifying biological structures
- Fiber bundle area feature: CPSI = 0.73 (average) for interface-enriched genes
- P-value = $1.34 \times 10^{-10}$

### CPSI Metric Evaluation

Comparison with traditional metrics:
- **Correlation**: Limited to linear relationships
- **SSIM** (Structural Similarity Index Measure): Sensitive to local patterns but not spatial context
- **RMSE** (Root Mean Squared Error): Measures absolute differences

CPSI advantages:
1. Automatic tissue subregion separation
2. Efficient curve summarization for spatial pattern capture
3. Robust to batch effects for multi-sample analysis

### Datasets Analyzed

| Dataset | Platform | Tissue | Application |
|---------|----------|--------|-------------|
| Human bladder cancer | 10x Visium | Bladder tumor | Tumor heterogeneity |
| HER2+ breast cancer | Spatial Transcriptomics | Breast tumor | Multi-sample analysis |
| Human breast tumor | 10x Visium | Breast | Validation |
| Mouse brain | 10x Visium | Brain | Neurology |
| Mouse embryo | 10x Visium | Embryo | Development |
| Zebrafish melanoma | 10x Visium | Melanoma | Artifact robustness |
| Human tonsil | Spatial CITE-seq | Tonsil | Tri-modality |
| TCGA H&E images | H&E only | Breast | Cross-study normalization |

### Key Advantages Over Existing Methods

| Aspect | Traditional Deep Learning | MorphLink |
|--------|---------------------------|-----------|
| Feature interpretability | Black box | Clear biological meaning |
| Training requirement | Annotated images | Label-free (unsupervised) |
| Structure coverage | Nuclei-focused | Comprehensive (nuclei, stroma, CAFs, etc.) |
| Spatial analysis | Global patterns | Local + global patterns |
| Batch effect robustness | Sensitive | Robust |
| Multi-sample scalability | Limited | Efficient |

### Limitations

> "A limitation of MorphLink is that it mainly focuses on capturing local tissue morphology, in contrast to deep neural network features that capture global tissue structures. Therefore, image features from MorphLink may have limitations in clustering tasks that require the identification of global patterns." (Paper, Discussion)

### Summary

MorphLink provides a systematic, interpretable, and scalable framework for linking cell morphology with molecular dynamics in spatial omics. The novel CPSI metric enables quantitative assessment of morphology-molecular relationships with statistical significance testing. The method has been validated across diverse tissue types, species, and spatial omics platforms, demonstrating its utility for understanding tumor heterogeneity, immune diversity, and developmental processes.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
