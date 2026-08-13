---
layout: default
permalink: /paper-atlas/spotsweeper-d70eacfd/
title: "SpotSweeper"
nav: false
description: "空间转录组不仅测量表达量，还保留每个 spot 或细胞在组织中的位置。传统 QC 往往直接沿用单细胞 RNA 测序流程，例如固定阈值、全样本 MAD 阈值，以及 miQC（PLOS Computational Biology, 2021）。这些方法隐含地把整张组织切片当成同质样本：总 UMI 少、检测基因少或线粒体比例高，就更可能被判为低质量。 但在真实组织中，这些差异可能正是生物学。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SpotSweeper</h1>
    <p>SpotSweeper: spatially aware quality control for spatial transcriptomics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/boyiguo1/Manuscript-SpotSweeper" target="_blank" rel="noopener noreferrer" aria-label="Open code for SpotSweeper">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SpotSweeper：面向空间转录组的空间感知质量控制

### 1. 它要解决什么问题？

空间转录组不仅测量表达量，还保留每个 spot 或细胞在组织中的位置。传统 QC 往往直接沿用单细胞 RNA 测序流程，例如固定阈值、全样本 MAD 阈值，以及 miQC（*PLOS Computational Biology*, 2021）。这些方法隐含地把整张组织切片当成同质样本：总 UMI 少、检测基因少或线粒体比例高，就更可能被判为低质量。

但在真实组织中，这些差异可能正是生物学。例如脑白质以轴突和树突为主，本来就比富含细胞体的皮层区域检测到更少转录本。用全局阈值会沿着组织结构系统性删除正常 spot。另一方面，空间实验还会产生单细胞 QC 没有建模的区域性问题，例如：

- **dryspot**：透化液没有完整覆盖芯片，造成一整块区域 UMI 和检测基因数骤降；
- **hangnail**：解剖造成组织损伤，均值未必异常，但局部生物信号和自然变异被破坏。

SpotSweeper 的核心思想是：**不要把一个 spot 与整张切片比较，而要与它附近的组织比较；不要只找孤立异常点，还要识别跨多个 spot 的异常区域。**

### 2. 方法的两个分支

```text
SpatialExperiment + 空间坐标 + 三个 QC 指标
                    |
        +-----------+-----------+
        |                       |
        v                       v
   spot 级局部异常            区域级伪影
        |                       |
  局部 kNN 参考          +------+------+
  robust z-score         |             |
  三指标分别判定          v             v
  逻辑 OR 合并         dryspot       hangnail
        |             DBSCAN       多尺度局部方差
        |                         均值-方差校正
        |                         PCA + k-means
        +-----------+-------------+
                    v
              QC/伪影标记
                    v
          在聚类、差异表达前过滤
```

输入只需要空间坐标和常见 QC 汇总量：library size、detected genes、mitochondrial ratio。完成这些汇总后，SpotSweeper 不再依赖基因级表达矩阵。

### 3. spot 级局部异常检测

#### 3.1 为每个 spot 建立局部参照

对第 $i$ 个 spot，根据空间坐标找到 $k$ 个最近邻，记为 $\mathrm{NN}_k(i)$。对某个 QC 指标 $x$，计算邻域中位数

$$
m_i=\operatorname{median}\{x_j:j\in\mathrm{NN}_k(i)\},
$$

以及局部中位绝对偏差

$$
\mathrm{MAD}_i=\operatorname{median}\{|x_j-m_i|:j\in\mathrm{NN}_k(i)\}.
$$

然后计算 robust local z-score：

$$
z_i=\frac{0.6745(x_i-m_i)}{\mathrm{MAD}_i}.
$$

0.6745 用于把正态分布下的 MAD 调整到与标准差相近的尺度。论文 Methods 将其四舍五入为 0.675。

#### 3.2 三个指标分别判断，再合并

- library size：$z_i<-3$ 时标为低质量；
- detected genes：$z_i<-3$ 时标为低质量；
- mitochondrial ratio：$z_i>3$ 时标为低质量；
- 任一指标命中，就把该 spot 标为 local outlier。

为什么这样能减小偏差？假设白质整体 UMI 较低。全局阈值会把大量白质 spot 一起删除；局部方法比较的是一个白质 spot 与附近白质 spot，只有相对邻域仍异常低的点才会被标记。

#### 3.3 邻域大小

规则网格可由邻域阶数 $c$ 推出邻居数：

$$
K_{\mathrm{hex}}(c)=3c(c+1),\qquad
K_{\mathrm{grid}}(c)=4c(c+1).
$$

论文推荐：

- 六边形 Visium：三阶邻域，$k=36$；
- 方形 STOmics/VisiumHD：三阶邻域，$k=48$；
- 非规则的测序型平台：默认约 $k=36$；
- Xenium、MERFISH、STARmap 等成像型平台：约 $k=50$ 或更大。

Extended Data Fig. 1 明确标注 Visium 的一至五阶分别是 6、18、36、60、90，因此 $k=36$ 才是三阶。论文 Results 中有一句把 $k=18$ 写成“third-order”，应视为文字/参数不一致。

### 4. 区域级伪影检测

#### 4.1 dryspot：在低计数空间中聚类

dryspot 的特点是大块区域 library size 和 detected genes 同时很低，但线粒体比例未必变化。SpotSweeper 在

$$
(\log_2\text{library size},\ \log_2\text{detected genes})
$$

二维空间中运行 DBSCAN，论文使用 `eps=0.5`、`minPts=20`。低计数密度簇被映射回组织空间后形成 dryspot 区域。相比直接设置 library-size 阈值，这一步利用两个指标的联合结构，并避免把所有生物学低计数区域一概删除。

#### 4.2 hangnail：寻找“异常平坦”的线粒体比例

hangnail 更难，因为它的平均 library size、detected genes 和 mitochondrial ratio 可能与正常区域相似。论文观察到，损伤区域丢失了正常组织应有的空间变化，表现为线粒体比例的局部方差异常低。

对每个 spot、每个尺度 $k$，计算

$$
S_i^2(k)=\frac{1}{k-1}\sum_{j\in\mathrm{NN}_k(i)}(x_j-\bar{x})^2,
\qquad
\bar{x}=\frac{1}{k}\sum_{j\in\mathrm{NN}_k(i)}x_j.
$$

默认使用一至五阶邻域。随后：

1. 在每个尺度上计算线粒体比例的局部方差；
2. 用稳健线性回归和 IRLS 校正局部均值与局部方差的关系，保留残差；
3. 将多尺度校正方差送入 PCA；
4. 在前两个主成分上进行 $k=2$ 的 k-means；
5. 把平均局部方差更低的簇自动标为伪影。

多尺度的意义是同时观察小范围和大范围的“平坦化”。只用很小的邻域容易产生零散假阳性；Extended Data Fig. 7 显示，使用到第四至第七阶时与默认一至五阶高度重合，而只用一至二阶会增加大量额外 spot。

### 5. 论文如何验证？

#### DLPFC 中的空间偏差

在 12 张 Visium 人脑 DLPFC 切片中，固定阈值平均删除 layer 1、layer 3 和白质的 9.34%、4.70% 和 9.74%。SpotSweeper 对应只删除 0.21%、0.28% 和 0.40%，相对固定阈值多保留 1,670 个高质量 spot。

作者还用 Walktrap、PRECAST、BayesSpace 和 BANKSY 检查局部异常：被 SpotSweeper 标记的 spot 与一阶邻居共享聚类标签的比例明显更低，说明这些点在空间上确实更不协调。

#### 系统性 Visium barcode 偏差

SpotSweeper 在 43 个来自不同人脑和小鼠脑数据的样本中反复找到相同六个低 library-size 坐标。这些位置对应的 barcode 有共享序列特征；GTGT 相关 barcode 的 UMI 分布也更低。这支持平台 barcode 偏差的假设，但属于关联证据，不能仅凭图证明具体分子机制。

#### 跨平台泛化

测序型数据覆盖 Visium、Slide-seqV2、Stereo-seq 和 VisiumHD；成像型数据覆盖 Xenium、MERFISH 和 STARmap。图像显示，局部 z-score 能把不同空间域的分布拉回相近中心。对成像平台，更准确的结论是“可用且通常与全局方法相当或略好”，而不是每个域都绝对优于所有基线。

#### 区域伪影与下游影响

DBSCAN 找到已知 dryspot 后，BayesSpace 不再把伪影当作独立组织域。多尺度方差识别 hangnail 后，canonical layer-6 marker（如 `NR4A2`、`SEMA3E`）的差异表达排序明显提升，说明伪影删除能改善下游生物学解释。

### 6. 如何理解它的创新与局限？

SpotSweeper 的创新在于把空间位置真正放进 QC 参照系，而不是设计复杂的基因表达模型。它简单、可解释，并与 `SpatialExperiment`/Bioconductor 工作流兼容。论文还报告约每 1,000 个 spot、每个指标 1 秒，并测试到 400,000 个 spot。

需要注意的局限：

- 区域伪影主要在已知 dryspot/hangnail 样本上展示，缺少大规模盲测基准；
- 多个平台只有单个示例数据集；
- 邻域大小仍需与分辨率和平台匹配；
- hangnail 当前依赖线粒体比例，不适合缺乏线粒体基因的成像面板；
- 成像平台的改进较小，且不同空间域的基线排名并不一致。

### 7. 当前代码快照能验证到什么程度？

固定快照 `Manuscript-SpotSweeper` commit `1e72779e549e7dad26702275e3421d3ffa3bab9c` 是论文分析/复图脚本仓库，不是完整的 SpotSweeper 包源码。README 也把真正的方法包链接到另一个仓库。

当前快照可以直接验证：

- 脚本对 UMI、detected genes、mitochondrial ratio 分别调用 `localOutliers()`；
- 三个输出 flag 用逻辑 OR 合并；
- 可见区域 helper 包含多尺度 kNN、稳健均值-方差校正、PCA、二类 k-means 和低方差簇标注。

当前快照不能直接验证：

- `SpotSweeper::localOutliers()` 的本地实现未找到，因此 robust z-score 的公式级实现不能标为 Exact；
- 多个脚本调用 `findArtifacts(n_rings=...)`，但唯一可见本地 helper 的参数叫 `n_order`，可能是包版本/API 漂移或调用了外部包函数；
- 可见 helper 将原始线粒体比例和计数加入 PCA，并把全部 PC 送入 k-means，而论文写的是校正后的多尺度方差和前两个 PC，因此只能算 Partial match。

因此，这篇论文的方法逻辑和应用证据较清楚，但当前固定代码快照的复现完整度应评价为中等，而不是把它误当成完整包实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpotSweeper

### Problem

Standard spatial transcriptomics QC commonly reuses single-cell rules: fixed cutoffs, whole-sample MAD thresholds or models such as miQC (*PLOS Computational Biology*, 2021). Those approaches assume that low library size, few detected genes or high mitochondrial ratio have the same meaning everywhere. In spatial tissue, however, these metrics follow real anatomy—for example, white matter naturally contains fewer transcripts than soma-rich cortical layers—so global rules can selectively delete valid biological domains. Existing workflows also did not specifically identify spatially extended preparation artifacts such as incomplete permeabilization or damaged tissue (`paper.md:21-27,78-107`).

### Proposed Method

SpotSweeper is an R/Bioconductor QC framework with two branches:

1. **Spot-level local outliers.** For each QC metric, it compares a spot with its $k$ spatial nearest neighbors using a robust local z-score. Defaults flag library size or detected genes below −3 and mitochondrial ratio above +3, then combine metric-specific calls.
2. **Regional artifacts.** Dryspots are detected by DBSCAN in log2 library-size/detected-gene space. Hangnails are detected from first- through fifth-order local mitochondrial-ratio variances, robustly corrected for their mean–variance relationship, reduced by PCA and separated with two-cluster k-means; the lower-variance cluster is labeled artifact.

The novelty is not a new expression model, but a spatial reference frame for QC: an observation is judged against nearby tissue, and tissue-wide damage is identified from multiscale loss of local variability (`paper.md:33-75,223-269`).

### Evaluation and Main Findings

The paper evaluates fixed thresholds, global MAD rules, miQC and SpotSweeper across DLPFC Visium sections and then tests broader generalization on Visium breast/ovarian cancer, Slide-seqV2, Stereo-seq, VisiumHD, Xenium, MERFISH and STARmap data.

- In 12 DLPFC sections, fixed thresholds removed averages of 9.34%, 4.70% and 9.74% of spots from layer 1, layer 3 and white matter. SpotSweeper reduced these averages to 0.21%, 0.28% and 0.40%, retaining 1,670 additional high-quality spots relative to the fixed rules.
- Flagged local outliers were less likely to share their clustering label with first-order neighbors under Walktrap, PRECAST, BayesSpace and BANKSY, consistent with local spatial discordance.
- The method revealed six Visium coordinates with repeatedly low library size across 43 human and mouse samples; shared barcode motifs and k-mer associations suggest a platform barcode bias.
- Across sequencing-based technologies, local z-score distributions were visibly better aligned across spatial domains. Imaging-platform results support feasibility and comparable or modest improvement, not uniform superiority in every domain.
- DBSCAN recovered a known dryspot, while multiscale variance separated known hangnail regions; removing these artifacts improved spatial clustering and ranking of canonical layer-6 marker genes.
- Reported scaling is approximately one second per 1,000 spots per metric, with tests up to 400,000 spots on one CPU (`paper.md:95-190,383-386`).

### Strengths and Limitations

Strengths include a simple interpretation, compatibility with `SpatialExperiment`, minimal dependence on gene-level expression after QC summaries are computed, geometry-aware neighborhood defaults, and a broad collection of tissue/platform demonstrations. The figure evidence strongly shows that global QC calls can follow anatomy and that local normalization reduces that structure.

Limitations include selected known-artifact examples rather than a large blinded artifact benchmark, mostly single datasets for several technologies, dependence on neighborhood choice, reliance on mitochondrial ratio for the current hangnail model, and smaller gains on imaging platforms. The paper also contains a neighborhood wording inconsistency: Extended Data explicitly labels Visium `k=36` as third order, whereas one Results sentence calls `k=18` third order.

### Reproducibility Assessment: 3/5

The paper provides public data locations, source data, a Bioconductor package and a manuscript code repository, and reports that SpotSweeper 1.3.3 was used. This workspace fixes the manuscript repository at commit `1e72779e549e7dad26702275e3421d3ffa3bab9c` and contains broad platform/figure scripts.

The code-paper match is **medium**, not high. This snapshot explicitly describes itself as analysis/figure-reproduction code and links the method package separately. It calls `localOutliers()` throughout, but the local implementation of that package function is **Not found**, so the robust-z formula cannot be marked Exact from this code. A visible regional helper matches neighborhood conversion, robust regression, PCA, k-means and low-variance annotation, but its PCA inputs/PC usage differ from the prose. Multiple scripts also call `findArtifacts(n_rings=...)` while the visible helper exposes `n_order`, leaving an unresolved package/API/version ambiguity. No dependency lockfile or fully bundled processed-data environment makes the snapshot directly runnable end to end (`doc_code.md`).

The available code and data are sufficient to understand and likely reconstruct the study with external acquisition and the correct package version, but this fixed manuscript snapshot alone is not a self-contained implementation of SpotSweeper.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
