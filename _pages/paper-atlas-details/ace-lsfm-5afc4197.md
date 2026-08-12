---
layout: default
permalink: /paper-atlas/ace-lsfm-5afc4197/
title: "ACE_LSFM"
nav: false
description: "透明化脑组织的光片荧光显微镜（LSFM）能产生细胞分辨率、太体素规模的三维图像。困难不只是“找到细胞”：模型还要适应不同实验室、染色方式、分辨率和脑区；统计分析则要发现跨越传统脑区边界的局部或层状变化。 传统 ClearMap、MIRACL 等流程常按图谱 ROI 汇总细胞数，容易把 ROI 内部的局部效应平均掉。逐体素检验又面对海量多重比较。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>ACE_LSFM</h1>
    <p>A deep learning pipeline for three-dimensional brain-wide mapping of local neuronal ensembles in teravoxel light-sheet microscopy</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-024-02583-1" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ACE：在太体素光片显微数据中绘制全脑局部神经元集群

### 要解决的问题

透明化脑组织的光片荧光显微镜（LSFM）能产生细胞分辨率、太体素规模的三维图像。困难不只是“找到细胞”：模型还要适应不同实验室、染色方式、分辨率和脑区；统计分析则要发现跨越传统脑区边界的局部或层状变化。

传统 ClearMap、MIRACL 等流程常按图谱 ROI 汇总细胞数，容易把 ROI 内部的局部效应平均掉。逐体素检验又面对海量多重比较。ACE（artificial intelligence-based cartography of ensembles）把三维分割、图谱配准、TFCE 聚类统计和原生空间复核连接成一条端到端流程。

### 核心流程

```text
全脑 LSFM 切片
  -> 三维小块与强度归一化
  -> UNETR / 3D U-Net 分割
  -> Monte Carlo dropout：平均预测 + 逐体素不确定性
  -> 拼接为原生空间全脑分割图
  -> 体素化并配准/变换到 Allen 图谱空间
  -> 两组平均密度与差异热图
  -> 热图约束的 TFCE 置换聚类检验
  -> 显著集群及其体积、效应和脑区覆盖
  -> 把集群逆变换到每个样本原生空间
  -> 计数集群内神经元并做 Mann–Whitney 复核
```

### 三维分割与不确定性

论文用 18 只小鼠的 15,200 个独立 96³ 图像块训练模型，增强后为 30,400 个。标签由 Ilastik、MIRACL 和 FIJI 辅助生成，因此是“银标准”而非完全人工金标准。

主干模型是三维 UNETR：Transformer 编码器学习跨图像块的长距离关系，卷积解码器恢复空间分割。残差 3D U-Net 提供局部特征，并可与 UNETR 组成“集成的集成”。代码中可直接看到 MONAI UNETR/U-Net、96³ UNETR 输入、768 隐层、12 个注意力头、dropout 和百分位强度缩放。

测试时保持 dropout 开启，得到 $N$ 次随机预测。逐体素不确定性为

$$
\frac{1}{N}\sum_{n=1}^{N}y_n^2-\left(\frac{1}{N}\sum_{n=1}^{N}y_n\right)^2.
$$

论文使用 $N=50$，再平均预测概率。代码实现了同一方差公式，但把前向次数作为运行参数，因此“50 次”是配置而不是源代码常量。

### 从原生空间到图谱空间

ACE 把图像块预测拼回全脑体积，再把高分辨率细胞标签卷积、下采样为图谱分辨率的密度图。自发荧光通道通过 MIRACL/ANTs 与 Allen Reference Atlas 配准，包括刚体、仿射和非线性变换。相同变换将分割密度送到图谱空间，也可把显著集群逆变换回每只动物的原生空间。

### TFCE 聚类统计

ACE 不用固定的 ROI 边界定义效应，而用 threshold-free cluster enhancement：

$$
\mathrm{TFCE}(v)=\int_{h_0}^{h_v} e(h)^E h^H\,\mathrm{d}h.
$$

$e(h)$ 表示高度 $h$ 下支撑体素 $v$ 的空间范围。论文设置 $E=2$、$H=0.5$、步长 5，并做 1,000 次置换。一个关键但容易忽略的设计是：先根据两组差异热图选择候选空间，再在该邻接范围内做聚类检验。这提高了太体素数据上的灵敏度，但也意味着统计结果依赖该数据驱动掩膜及其阈值。

显著集群产生后，ACE 汇总体积、效应强度、中心位置和所跨脑区比例。图谱只负责解释集群位置，不预先规定集群边界。

### 原生空间复核

显著集群经阈值化、膨胀和三维连通域分离后，被逆变换到每个样本。流程在原始分割图中计数每个集群内的神经元，并用双侧 Mann–Whitney $U$ 检验比较两组。这样可以检查图谱空间显著性是否也对应原生高分辨率数据中的细胞数差异。

### 实验结果

- 相比优化后的 Ilastik，ACE 的平均 DSC 提高 0.17，HD95 从 9.60 ± 6.78 降到 4.76 ± 3.47。
- 检测任务中，ACE 的 F1 为 0.75 ± 0.08，Cellfinder 为 0.55 ± 0.15。
- 在未见过的跨中心数据上，ACE DSC 为 0.73 ± 0.02，Ilastik 为 0.45 ± 0.12；召回率分别为 0.78 ± 0.09 和 0.35 ± 0.15。
- 冷诱导觅食和运动实验显示，ACE 能找到 ROI 汇总可能遗漏的局部或层状神经元集群。

### 复现边界

代码与论文核心链条的匹配度为**中等**：分割、MC dropout、不确定性、配准/体素化、TFCE 和原生空间验证均有直接实现；但本地快照是当前 MIRACL `master`，不是论文冻结版本。训练权重、GPU/容器、Allen 图谱资源和太体素样例数据需外部获取。当前代码中的相关性/集群连接分析接口会提示不可用并跳过，因此论文该部分不能由此快照完整复现。总体复现评分为 **3/5**。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## ACE for brain-wide LSFM neuronal-ensemble mapping

### What problem does it solve?

Teravoxel light-sheet microscopy can image cellular activity across an intact cleared brain, but analysis is difficult at two levels. Neuron segmentation must generalize across laboratories, labeling protocols and heterogeneous brain regions, while statistical analysis must find focal or laminar effects without averaging them away inside atlas ROIs or performing an underpowered voxel-by-voxel correction.

ACE—artificial intelligence-based cartography of ensembles—is an end-to-end MIRACL workflow that combines 3D deep-learning segmentation, voxel-wise uncertainty, atlas registration and threshold-free cluster-wise permutation statistics. Atlas labels are used for localization after discovery; they do not define the tested cluster boundaries.

### Method in brief

ACE divides LSFM volumes into 3D patches and predicts neuronal soma masks with an optimized UNETR, a residual 3D U-Net, or their ensemble. Fifty Monte Carlo-dropout predictions are averaged in the paper, and their voxel-wise variance supplies an uncertainty map. Whole-brain segmentations are voxelized, registered and warped into Allen atlas space. Group difference maps guide an adjacency/search mask, after which TFCE and 1,000 permutations identify significant spatial clusters. Those clusters are inverse-warped to each subject, where neurons are counted and compared between groups with a Mann–Whitney test.

### Evidence and results

The models were trained on 15,200 unique 96³ patches from 18 mouse brains and evaluated on 12,160 held-out patches plus 1,824 unseen patches from different centers and acquisition conditions. Compared with optimized Ilastik, ACE improved average DSC by 0.17 and reduced HD95 from 9.60 ± 6.78 to 4.76 ± 3.47. Its detection F1 was 0.75 ± 0.08 versus 0.55 ± 0.15 for Cellfinder. On an unseen dataset, DSC was 0.73 ± 0.02 versus 0.45 ± 0.12 for Ilastik. Main figures show close prediction/ground-truth overlap, uncertainty around ambiguous boundaries, broad regional robustness, focal cold-induced activation and subject-specific native-space cluster validation.

ACE was applied to cold-induced food seeking and locomotion. It recovered localized or laminar ensembles that coarse ROI analysis could overlook, illustrating the practical value of data-driven cluster boundaries.

### Reproducibility

The inspected MIRACL repository directly contains the ACE orchestration, UNETR/U-Net construction, percentile normalization, sliding-window inference, Monte Carlo variance, voxelization/registration wrappers, MNE TFCE permutation statistics and native-space validation. Overall paper–code fidelity is **medium**: the core computational chain is present, but the snapshot is current `master` rather than a paper-tagged release, trained weights and large example inputs are external, and the cluster-correlation interface currently reports that correlation is unavailable.

Reproducibility rating: **3/5**. The open-source pipeline and documentation are substantial, but faithful execution requires MIRACL containers, GPU hardware, atlas assets, trained weights and teravoxel datasets. Silver-standard labels and a heatmap-derived statistical mask are important methodological dependencies, and inappropriate TFCE/mask parameters can change false-positive or false-negative behavior.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
