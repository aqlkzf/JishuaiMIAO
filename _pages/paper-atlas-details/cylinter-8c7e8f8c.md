---
layout: default
permalink: /paper-atlas/cylinter-8c7e8f8c/
title: "CyLinter"
nav: false
description: "高通量多重组织成像（如 CyCIF、CODEX、mIHC）可以在单张组织切片中测量几十种蛋白，并把图像转换成“单细胞空间特征表”：每一行是一枚细胞，包含空间坐标、分割面积和各通道信号强度。 问题在于，这张表并不只包含生物学。组织折叠、灰尘和纤维、抗体聚集、气泡、失焦、照明不均、拼接或配准错误、循环成像中的组织脱落，以及过分割/欠分割，都会改变细胞的数值特征。它们可能在 UMAP 中形成看似清晰的簇，也可能把不同细胞类型混到同一簇里。"
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
      <span>Nature Methods · 2024</span>
    </div>
    <h1>CyLinter</h1>
    <p>Quality control for single-cell analysis of high-plex tissue profiles using CyLinter</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CyLinter 方法详解

### 1. 这篇论文解决什么问题？

高通量多重组织成像（如 CyCIF、CODEX、mIHC）可以在单张组织切片中测量几十种蛋白，并把图像转换成“单细胞空间特征表”：每一行是一枚细胞，包含空间坐标、分割面积和各通道信号强度。

问题在于，这张表并不只包含生物学。组织折叠、灰尘和纤维、抗体聚集、气泡、失焦、照明不均、拼接或配准错误、循环成像中的组织脱落，以及过分割/欠分割，都会改变细胞的数值特征。它们可能在 UMAP 中形成看似清晰的簇，也可能把不同细胞类型混到同一簇里。因此，“聚类分得开”并不等于“结果是真的”。

MCMICRO（Nature Methods，2022）等上游流程能够完成拼接、配准、分割和定量，但无法保证输出表中没有上述样本特异的伪影。传统单细胞 QC 通常只看数值分布，缺少回到原始组织图像核查的能力。CyLinter 的核心目标，就是把“数值门控”和“图像复核”绑定在一起。

### 2. CyLinter 的核心思想

CyLinter 是一个基于 Python 和 Napari 的人机协同 QC 工具。它不直接修复图像，而是判断哪些细胞记录不可信，并从空间特征表中删除这些行；之后还可以利用 metaQC 重新检查先前的删除决定。

每个样本需要四类输入：

1. 已拼接、配准的多通道 TIFF/OME-TIFF；
2. 细胞 ID 分割掩膜；
3. 细胞分割轮廓图；
4. 含细胞坐标和通道强度的 CSV 空间特征表。

另有一个实验 YAML 配置文件，用来描述样本、核染通道、排除的标记、各模块参数以及下游聚类设置。

```text
多通道图像 + 分割结果 + 单细胞特征表
                  │
                  ▼
       合并多样本为一个 DataFrame
                  │
                  ▼
 ROI/伪影筛选 ─► 核强度筛选 ─► 分割面积筛选
                  │
                  ▼
 跨循环稳定性筛选 ─► log 变换 ─► 通道离群值筛选
                  │
                  ▼
        metaQC：纠正人工筛选偏差
                  │
                  ▼
 PCA / UMAP或t-SNE / HDBSCAN / 热图 / 缩略图复核
                  │
                  ▼
       清洗后的多样本空间特征表 + QC 报告
```

当前代码在每个模块之后保存一个完整的 Parquet 检查点，因此既能记录进度，也能从指定模块恢复运行。

### 3. 各步骤到底做了什么？

#### 3.1 合并样本

`aggregateData` 读取每个样本的 CSV，加入样本、条件和重复信息，只保留所有样本共有的通道，然后按行合并成一个 pandas DataFrame。后续所有门控都在这个统一表上进行。

#### 3.2 ROI 与图像伪影筛选

用户在 Napari 中浏览通道并画 ROI：

- 负选择：圈出坏区域，删除其中的细胞；
- 正选择：圈出可用区域，只保留其中的细胞。

轻度受损的 CRC 图像适合负选择；TOPACIO 这类伪影遍布全片的样本，更适合正选择。代码将多边形 ROI 转换成布尔掩膜，再用每个细胞的质心坐标查询掩膜，最后按 `CellID` 删除对应行。

CyLinter 还有经典图像算法辅助找伪影。对每个下采样通道，它进行 8-bit 重标定、腐蚀、局部均值平滑、膨胀和局部对比度计算，再寻找局部极大值作为种子，利用 flood fill 生成候选区域。多个候选区域取并集、放大回原图后，落在掩膜内的细胞会被标记给用户复核。自动算法提供候选，最终决定仍由人控制。

#### 3.3 核强度门控

对细胞 $i$ 的核染强度 $D_i$，用户在对数直方图上选择上下界：

$$
L_D < \log(D_i) < U_D.
$$

过暗细胞常来自切片截断或失焦；过亮细胞可能来自染料饱和或组织折叠。高斯混合模型给出初始阈值，用户再通过图像中的细胞叠加点确认或修改。

#### 3.4 分割面积门控

对分割面积 $A_i$ 使用类似规则：

$$
L_A < \log(A_i) < U_A.
$$

面积过小通常提示一个细胞被切成多个对象；面积过大则可能是多个细胞被合并。论文称该步骤为 `dnaArea`，当前代码名为 `areaFilter`。

#### 3.5 跨循环稳定性

循环成像会重复拍摄核染通道。若细胞在后期循环移动或脱落，其末次核信号会显著下降。代码计算：

$$
r_{i,c}=\log_{10}\left(\frac{D_{i,1}+0.001}{D_{i,c}+0.001}\right).
$$

稳定细胞的比值接近 0；脱落细胞通常形成正值尾部或独立峰。用户在直方图上保留稳定区间。

#### 3.6 信号变换与通道离群值

每个抗体通道按下式变换：

$$
x'_{i,m}=\log_{10}(x_{i,m}+0.001).
$$

之后 `pruneOutliers` 为每个样本、每个标记设置上下百分位阈值，删除极端尾部，并对保留值做 0–1 缩放。重要的是，极端值会重新叠加到组织图像上，避免把真实稀有细胞误当作伪影。

补充材料指出，图像背景扣除可能产生大量零值或近零值细胞；这些细胞会在 UMAP 边缘形成假簇。因此，上游“去背景”本身也需要被当作潜在混杂因素检查。

#### 3.7 metaQC 如何纠正人工偏差？

metaQC 从连续检查点中重建哪些细胞在哪一步被删除，把它们标记为 noisy，并与保留的 clean 细胞混合。数据按样本/通道变换和缩放后，被分块送入 UMAP 或 t-SNE，再用 HDBSCAN 聚类。

对一个簇 $C$：

$$
f_{clean}(C)=\frac{C\text{ 中原标记为 clean 的细胞数}}{|C|},
$$

$$
f_{noisy}(C)=\frac{C\text{ 中原标记为 noisy 的细胞数}}{|C|}.
$$

- 如果 $f_{clean}(C)$ 高于用户设定阈值，整个簇重新判为 clean；
- 否则，如果 $f_{noisy}(C)$ 高于阈值，整个簇判为 noisy；
- 两者都不满足时，保留原始人工标签；
- HDBSCAN 的离群点被视为 noisy。

最后，原先保留但被重判为 noisy 的细胞会被删除；原先删除但被重判为 clean 的细胞会从原始表中加回来。这不是只改标签，而是真正重建最终 DataFrame。

### 4. 实验结果说明了什么？

论文分析了七个 CyCIF、CODEX 和 mIHC 数据集。

#### CRC 数据

清洗前约 $9.8\times10^5$ 个细胞形成 22 个簇，其中多个簇实际由抗体聚集、纤维、细胞脱落或局部未染色驱动。CyLinter 删除约 23% 的细胞，其中约 16% 是分割错误。清洗后约 $9.3\times10^5$ 个细胞形成 78 个更具形态和标记一致性的簇。一个清洗前簇可拆成九个清洗后细胞群，说明原来的簇混合了多种生物状态。

#### TOPACIO 临床试验数据

清洗前约 300 万抽样细胞形成 492 个 HDBSCAN 簇，约 29% 无法聚类。CyLinter 最终删除 84% 的细胞，其中约 53% 来自正 ROI 选择；保留的约 300 万细胞形成 43 个可解释簇。论文没有发现删除比例与活检方式或治疗反应显著相关，但这不能保证所有潜在选择偏差都已消失。

#### 自动深度学习模型

补充材料训练了 ResNet34 编码器加 FPN 解码器的伪影分割模型。三次训练的 AP 为 0.30–0.33，ROC AUC 为 0.71–0.75。作者明确认为性能尚不足以替代人工，因此该模型应视为未来自动化方向，而不是当前 CyLinter 的成熟核心。

### 5. 这项工作的真正创新

CyLinter 的创新不在某个复杂损失函数，而在于把三种证据放进同一工作流：

1. 单细胞数值分布；
2. 细胞在原始组织中的位置和形态；
3. 无监督聚类对人工决定的反向审查。

它把显微学中的人工目视检查系统化、可记录化，并用检查点和 metaQC 降低主观性。对无法重新取材或重新成像的临床档案样本，这种“尽量挽救可用区域”的思路尤其重要。

### 6. 局限与复现边界

- 人工复核在超大数据集上仍然耗时，并存在审阅者差异。
- 严重受损样本可能需要删除大部分细胞，统计上“未发现组间偏差”不等于绝对无偏。
- CyLinter 删除不可靠细胞，但不修复原图或分割；空间串扰仍可能保留。
- 当前仓库快照是 v0.0.55，而论文使用 v0.0.46–v0.0.49；核心模块匹配，但不能假设逐行历史一致。
- 论文的 ResNet34–FPN 训练代码未在当前 `cylinter` 仓库中找到。
- 图表脚本位于独立的 `cylinter-paper` 仓库；完整数据在 Synapse、HTAN/HuBMAP 等外部资源中，TOPACIO 还需要试验赞助方许可。

因此，本地代码足以理解并核查 CyLinter 的核心 QC 算法，但不足以一键复现论文全部图表与数值结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CyLinter

### Problem

High-plex tissue imaging converts multichannel microscopy into single-cell spatial feature tables, but those tables inherit defects from tissue preparation, staining, acquisition, image stitching/registration, segmentation and feature extraction. Folds, debris, antibody aggregates, blur, illumination defects, tissue loss and segmentation errors can create spurious UMAP/HDBSCAN clusters or merge biologically distinct cells. Because the error is spatial and morphological, table-only QC cannot reliably distinguish rare biology from technical artifacts.

Upstream pipelines such as MCMICRO (Nature Methods, 2022) stitch, register, segment and quantify multiplex images, but even correctly processed outputs still contain specimen- and image-specific artifacts. Generic single-cell QC methods do not retain a direct visual link to the tissue, while methods aimed at spatial crosstalk such as REDSEA address a different residual problem and do not replace artifact QC.

### Proposed method

CyLinter is a Python/Napari human-in-the-loop QC pipeline for multiplex tissue images and their cell-level feature tables. For every specimen it uses the multichannel image, segmentation mask, segmentation outlines and spatial feature CSV. It aggregates samples into one dataframe, then applies linked image/table modules:

1. manual negative or positive ROI selection, with optional classical automatic artifact masks;
2. nuclear-intensity gating for dim or oversaturated cells;
3. segmentation-area gating for over- and undersegmentation;
4. cross-cycle DNA-ratio filtering for unstable/lost cells;
5. `log10(x + 0.001)` marker transformation;
6. per-marker percentile pruning for residual outliers;
7. optional metaQC, which embeds and clusters a mixture of retained and redacted cells to restore likely false removals and delete likely missed artifacts.

Every threshold can be checked by overlaying selected cells on the source image. The current code writes a Parquet checkpoint after every module, supports restart from a named module, and returns a cleaned pooled feature table plus a persistent QC report.

### Evaluation and main results

The study analyzes seven multiplex-imaging datasets spanning CyCIF, CODEX and mIHC, including 25 archival TNBC specimens from the TOPACIO clinical trial, a whole-slide CRC specimen, a 123-core TMA, HNSCC, tonsil and two large-intestine datasets.

- Pre-QC CRC data contained 22 clusters, several directly driven by antibody aggregates, debris, cell loss or uneven labeling. CyLinter removed about 23% of cells—about 16% because of segmentation errors—and the post-QC dataset contained roughly $9.3\times10^5$ cells in 78 mostly coherent clusters. One noisy pre-QC cluster separated into nine post-QC populations with distinct morphology and spatial distribution.
- TOPACIO was substantially more damaged: pre-QC analysis produced 492 HDBSCAN clusters with about 29% of cells unclustered. CyLinter removed 84% of cells, including about 53% through positive ROI selection, leaving about $3.0\times10^6$ cells in 43 interpretable clusters. Redaction was not significantly associated with biopsy type or treatment response.
- A separate proof-of-concept ResNet34–FPN artifact model achieved average precision 0.30–0.33 and ROC AUC 0.71–0.75. The authors judged this insufficient for general automation, so human review remains central.

The figures show a consistent chain from localized image defects to distorted cell measurements, spurious/mixed pre-QC clusters and cleaner post-QC cell populations. They also show the main residual limitation: segmentation-driven spatial crosstalk can remain after CyLinter filtering.

### Reproducibility

**Reproducibility rating: 3/5.**

The acquired official repository has **medium paper–code fidelity**. Direct source inspection verifies the CLI/YAML interface, ordered restartable pipeline, sample aggregation, ROI/artifact masking, intensity/area/cycle filters, marker transformation, outlier pruning and metaQC row restoration/removal. However:

- the snapshot is CyLinter v0.0.55 at commit `a95766aab1e73f8a5b73972afd2b1591c4fbe245`, whereas the paper reports v0.0.46–v0.0.49;
- the paper's `dnaIntensity` and `dnaArea` stages are named `intensityFilter` and `areaFilter` in current code;
- dependencies are largely unpinned;
- the ResNet34–FPN training/evaluation code is not present in the acquired package;
- manuscript figure scripts are in a separate `cylinter-paper` repository;
- the large datasets are external, and TOPACIO access requires sponsor permission.

Thus the software's core QC logic is inspectable and substantially reproducible, but exact paper-wide numerical/figure reproduction is not turnkey from this workspace alone.

### Limitations

- Human review scales poorly for very large studies and can introduce reviewer bias, although metaQC and the QC report are designed to expose/correct it.
- Aggressive cleaning may discard most cells in severely damaged archival material; the absence of measured association with clinical groups does not prove that every biological bias has been removed.
- CyLinter filters cell records rather than repairing images or segmentation, so spatial crosstalk and other upstream errors may persist.
- The classical automatic detector contains image-dependent heuristics and the paper does not provide a broad cross-platform sensitivity analysis.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
