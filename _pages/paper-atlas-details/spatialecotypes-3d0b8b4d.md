---
layout: default
permalink: /paper-atlas/spatialecotypes-3d0b8b4d/
title: "SpatialEcotypes"
nav: false
description: "这篇工作想回答两个连续的问题： 在不同患者、癌种和空间转录组平台中，能否发现反复出现的多细胞空间组织模式？ 如果这些模式确实存在，能否不再依赖组织活检，而是从血浆 cfDNA 甲基化中估计它们？ 作者把第一个问题交给 Spatial EcoTyper，把第二个问题交给 Liquid EcoTyper。两者不是同一个模型：前者从空间表达数据中定义“空间生态型”（spatial ecotype, SE）并建立表达参考；"
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
      <span>Cell-Cell Communication</span>
      <span>Nature · 2026</span>
    </div>
    <h1>SpatialEcotypes</h1>
    <p>Non-invasive profiling of the tumour microenvironment with spatial ecotypes</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Spatial EcoTyper 与 Liquid EcoTyper 方法详解

### 先说结论：这套方法到底解决什么问题？

这篇工作想回答两个连续的问题：

1. 在不同患者、癌种和空间转录组平台中，能否发现反复出现的多细胞空间组织模式？
2. 如果这些模式确实存在，能否不再依赖组织活检，而是从血浆 cfDNA 甲基化中估计它们？

作者把第一个问题交给 **Spatial EcoTyper**，把第二个问题交给 **Liquid EcoTyper**。两者不是同一个模型：前者从空间表达数据中定义“空间生态型”（spatial ecotype, SE）并建立表达参考；后者以这些 SE 的组织表达估计为监督信号，学习由 CpG 甲基化预测 SE 相对水平。

最终输出也分三层：

- 发现阶段：得到跨样本复现的 SE，以及每个 SE 包含的细胞类型特异状态；
- 表达恢复阶段：给新细胞、空间位置或 bulk RNA-seq 样本估计 SE 标签或比例；
- 液体活检阶段：给 plasma cfDNA 甲基化样本估计 SE、非 SE 肿瘤成分和健康 cfDNA 背景的相对水平。

### 为什么已有方法还不够？

EcoTyper（Cell, 2021）已经能从表达数据中寻找跨肿瘤复现的细胞状态与生态系统，但不直接使用细胞的空间坐标。另一类空间域或空间 niche 方法会使用坐标，却往往针对单个样本，难以在不同患者、癌种和平台之间对齐同一种多细胞结构。更现实的限制是，无论单细胞还是空间转录组都需要组织，难以反复采样。

Spatial EcoTyper 的关键设计是：**不要把所有细胞混在一起比较，而是先对每一种细胞类型分别描述空间邻域，再融合不同细胞类型对邻域相似性的判断。** 这样既保留“同一种细胞在不同地理位置的状态变化”，又能寻找多个细胞类型共同构成的空间结构。

### 第一部分：Spatial EcoTyper 如何发现空间生态型？

#### 1. 输入数据

单个空间样本至少需要：

- 基因 × 细胞（或 spot）的表达矩阵；
- 每个细胞的二维坐标；
- 每个细胞的细胞类型标签。

对分辨率较低的 Visium 等数据，论文先借助匹配的 scRNA-seq 图谱和 CytoSPACE 获得单细胞尺度的重建结果。这个重建属于研究的数据预处理，不是本地 `spatialecotyper` R 包的核心实现。

#### 2. 把组织划分为空间邻域

算法在组织上放置规则网格。以每个网格中心为基准，收集指定半径内的细胞，形成 spatial neighbourhood（SN）。论文发现阶段使用 50 µm 半径；本地代码同时区分网格间距和生物学邻域半径，默认网格间距约为半径的 1.4 倍。

一个 SN 的重点不是总表达，而是“这里每一种细胞类型分别处于什么表达状态”。因此，算法在每个 SN 内按细胞类型聚合表达，得到细胞类型 $c$ 对应的邻域表达矩阵 $E^c$：行是基因，列是空间邻域。

#### 3. 每种细胞类型独立判断邻域是否相似

对每个细胞类型，算法先从 $E^c$ 提取主要表达变化，再计算邻域之间的相似性矩阵 $A^c$。直观上，$A^c_{ij}$ 越大，表示在细胞类型 $c$ 看来，邻域 $i$ 和邻域 $j$ 的表达状态越接近。

为什么要分细胞类型计算？因为一个空间生态系统并不是由总表达最高的细胞主导。巨噬细胞、成纤维细胞和 T 细胞可以各自提供一份对空间结构的判断，之后再共同决定哪些邻域属于同一生态型。

#### 4. 用 SNF 融合多个细胞类型的相似网络

Similarity Network Fusion（SNF）接收所有 $A^c$，迭代交换各网络中的邻域关系，得到统一的邻域相似矩阵 $A$。它表达的是：综合所有可用细胞类型后，哪些空间邻域具有相似的多细胞表达结构。

本地源码随后把融合矩阵进行秩归一化，放入 Seurat 对象，经过 PCA、近邻图和 Louvain 聚类，得到单个样本内的初始空间簇。UMAP 主要用于可视化，不是 SE 定义本身。

#### 5. 从单样本空间簇走向跨样本 SE

只在一个肿瘤内聚类还不能说明结构是“保守生态型”。因此作者进行了第二轮整合：

1. 对每个样本内的空间簇，分别计算各细胞类型的平均表达谱 $E'^c$；
2. 将所有样本的同一细胞类型表达谱按列拼接为 $E^{*c}$；
3. 再次计算细胞类型特异的簇间相似网络；
4. 再次用 SNF 融合为跨样本相似矩阵 $A^*$；
5. 对 $A^*$ 做 NMF，将不同样本的空间簇归入跨样本复现的 SE。

论文对 NMF rank 2–50 逐一进行 50 次运行，根据稳定性得到 11 个候选，随后去掉两个不满足保留条件的候选，最终报告九个 SE。这里要区分论文设置与软件默认值：本地包的默认 rank 和运行次数只是通用接口默认参数，并不等于论文的完整参数搜索。

### 第二部分：如何在新数据中恢复这些 SE？

发现 SE 后，作者为每种细胞类型学习一套 NMF 表达基矩阵。论文写作中的核心关系是

$$
G^c = W^c H^c,
$$

其中 $G^c$ 是细胞类型 $c$ 的基因表达，$W^c$ 是基因 × SE 的表达基，$H^c$ 是 SE × 细胞的系数或概率。论文正文对 $H^c$ 的维度有一处文字方向不一致，但矩阵乘法和本地实现都要求它按“SE × 细胞”理解。

#### 1. 训练表达基 $W^c$

训练时，已有发现结果给出了每个细胞属于哪个 SE。代码把这些标签构造成固定的 $H^c$，在 KL 散度目标下更新 $W^c$。每个 SE 会筛选具有区分力的基因；多次 NMF 运行的结果再聚合成更稳定的基矩阵。

#### 2. 给新细胞分配 SE

预测时固定 $W^c$，只更新新数据的 $H^c$。每个细胞取系数最大的 SE；论文要求最大预测概率超过 0.6，否则记为 `non-SE`。

这里存在一个重要的代码边界：本地 `RecoverSE` 的默认 `min.score=0`，不会自动执行论文的 0.6 阈值。要复现论文规则，调用时必须显式传入阈值，或者使用未随包提供的研究脚本。

#### 3. 从 bulk RNA-seq 估计 SE 比例

作者还把带 SE 标签的单细胞表达按随机混合比例汇总成 1,000 个 pseudo-bulk 样本。已知的混合比例作为固定系数，训练 bulk 表达基 $W^B$。对真实 bulk RNA-seq，固定 $W^B$ 并估计样本的 SE 系数，最后归一化为相对丰度。

这一步的意义是把昂贵的空间发现结果变成可在大型 bulk 队列上应用的参考模型。它恢复的是样本级 SE 组成，不会重建生态型在组织中的精确位置。

#### 4. 论文 LOOCV 与当前代码并不完全一致

论文描述的是标准 leave-one-sample-out：留出一个样本，用其余样本训练，再预测留出样本，并重复 20 次。当前 `LoocvPredict` 源码却把一个样本作为训练集、其余样本作为测试集。因此，代码提供了相近的交叉样本验证组件，但不能直接视为论文所写 LOOCV 的逐字实现。

### 第三部分：Liquid EcoTyper 如何从甲基化预测 SE？

#### 1. 输入与监督信号

模型输入为样本 × CpG 的甲基化矩阵 $X$。论文实际模型使用 38,431 个 CpG。监督目标不是空间坐标，而是先由 Spatial EcoTyper 从配对 tumour RNA-seq 中得到的 SE 相对水平。

由于大规模“同一患者、同时有 tumour 和 plasma 且有可靠 SE 真值”的数据不足，作者把肿瘤甲基化与健康人 cfDNA 甲基化按已知比例混合，模拟患者 cfDNA。健康 cfDNA 同时提供背景类别，避免模型把所有信号都强行解释为肿瘤 SE。

#### 2. 二值 CpG 集合层

模型学习二值矩阵 $W^B$，把 38,431 个 CpG 分配给 400 个 CpG 集合。对每个样本，先计算每个集合内 CpG 的平均甲基化，再经连续权重和输出层得到组成预测。

这种设计的直觉类似基因集模型：单个 CpG 容易缺失或受技术噪声影响，而一组协同 CpG 的平均更稳定；二值成员关系也让每个学到的集合可以被直接导出和解释。

#### 3. 输出为什么必须是“组成”？

输出包括可评估的 SE、非 SE 肿瘤成分和健康背景。模型通过 sigmoid 得到非负值，再按行归一化，使各部分加和为 1。因此输出表示相对组成，不是绝对 cfDNA 浓度，也不是肿瘤中每个空间区域的物理面积。

#### 4. 损失函数在优化什么？

论文的主损失更关注跨患者的相对排序：如果真实 SE7 在患者 A 高于患者 B，预测也应保持这种趋势。因此它以相关性为核心，而不是要求模拟 tumour 与真实 plasma 在数值上逐点相等。另一个惩罚项约束 CpG 集合大小，防止所有集合无限扩张；论文使用的权重为 $lambda=\sqrt{10}$。

训练使用 PyTorch 2.2.0、NAdam、学习率 0.001、dropout 0.5，共 40 个 epoch，并在十个训练/验证划分上选择模型形成 ensemble。这些细节来自论文 Methods；本地 R 包中没有找到 Liquid EcoTyper 的 PyTorch 实现，因此无法用源码再次核对网络前向传播、训练循环或模型文件。

### 怎样理解论文的验证链？

这篇工作的证据不是一次测试，而是逐步推进：

1. **空间发现是否稳定：** 改变邻域半径、聚类 resolution 和 NMF rank，并观察跨运行/跨平台稳定性；
2. **细胞状态能否恢复：** 用交叉样本预测、F1 分数、空间共定位和独立平台验证；
3. **bulk 比例能否恢复：** 使用 pseudo-bulk、留一癌种和配对 bulk/单细胞或 Visium 数据；
4. **Liquid 模型是否学对对象：** 在 115 个模拟测试样本中检查各 SE 相关性、SE 间协方差、CpG 集合关联和定向消融；
5. **真实 plasma 是否对应 tumour：** 在 23 位患者的配对 plasma、tumour ST、tumour methylation 和部分 PBMC 数据中比较；
6. **是否有临床关联：** 在 78 位 ICI 治疗前 melanoma 患者中检验 response 和 survival，并在另一个十人队列中做支持性复现。

这种设计支持“模型捕获了跨模态一致的 SE 信号”。它尚不能证明 SE 导致治疗反应，也不能替代大规模、前瞻性、多中心的临床验证。

### 论文证据、代码证据与尚缺证据

#### 论文直接支持

- 132 个肿瘤、十个癌种、六种 ST 平台和九个最终 SE；
- Spatial 与 Liquid 两部分的数学定义、研究参数及评估结果；
- plasma 与 tumour 的配对验证以及 ICI 结局关联。

#### 本地源码直接验证

- 单样本空间邻域、细胞类型特异相似网络、SNF 和 Louvain 聚类；
- 跨样本表达谱整合、第二次网络融合和 NMF 聚类；
- NMF 表达基训练、单细胞恢复、pseudo-bulk 和 bulk deconvolution；
- `RecoverSE` 阈值默认值和当前 `LoocvPredict` 的实际折叠方向。

#### 当前缺失

- Liquid EcoTyper 的 PyTorch 源码和训练/推理脚本；
- 从原始研究数据到全部图表的端到端分析流程；
- 本地 Supplementary Methods/表格 Markdown；
- 覆盖核心 R 函数的测试与本次环境中的运行验证。

因此，最稳妥的复现结论是：**Spatial EcoTyper 的主要算法组件可以从作者 R 包中审计和复用；Liquid EcoTyper 与整篇论文的完整结果链目前只能依据论文描述和图像，不能由本地代码快照独立复现。**

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## SpatialEcotypes: paper and code summary

### In one sentence

Spatial EcoTyper integrates cell-type-specific spatial expression networks across tumours to discover recurrent multicellular spatial ecotypes (SEs), and the paper's separate Liquid EcoTyper model learns CpG sets that estimate those tissue-derived SEs from plasma cfDNA methylation.

### Why this paper matters

Earlier tumour-ecosystem studies could resolve cell states but often ignored spatial context; spatial niche methods generally did not harmonize heterogeneous samples, cancers and assay platforms; and tissue profiling still required an invasive biopsy. The paper connects these problems in one analytical arc: discover conserved ecosystems from spatial transcriptomics, recover them in expression datasets at scale, then estimate them non-invasively from methylation. Its closest named predecessor is EcoTyper (Cell, 2021), which defined clinically distinct cell states and ecosystems from non-spatial expression data.

### Method at a glance

Spatial EcoTyper first partitions each tissue into spatial neighbourhoods. Within every neighbourhood it aggregates expression separately for each cell type, computes cell-type-specific neighbourhood similarities, and fuses those networks with similarity network fusion. Louvain clustering yields sample-level spatial clusters. Across samples, cluster-level cell-type profiles are concatenated, their similarity networks are fused again, and NMF groups the clusters into conserved SE candidates. The reported study selected 11 candidates and removed two that failed its criteria, leaving nine SEs.

For downstream recovery, each cell type receives an SE-specific NMF basis. A new cell or spot is projected onto the fixed basis and assigned to its maximum-scoring SE when the paper's probability threshold is met; pseudo-bulk mixtures similarly train an expression basis for deconvolving SE proportions from bulk RNA-seq.

Liquid EcoTyper is a distinct paper-described model. It takes sample-by-CpG methylation values, learns 400 binary CpG sets over 38,431 CpGs, averages methylation within each set, and transforms the set scores into relative levels of SEs, non-SE tumour content and healthy cfDNA background. Training uses simulated cfDNA mixtures with RNA-derived SE composition as targets, a correlation-oriented loss, a set-size penalty, ten train/validation splits and an ensemble of selected models.

### Principal findings

- The study assembled 132 spatially profiled tumours across ten cancer types and six platforms, alongside matching single-cell atlases, and reported nine recurring SEs with distinct spatial positions, cell-state assemblies and biological programs.
- The integrated spatial embedding visibly follows tumour-to-stroma geography, while cross-sample cluster similarity and cell-state marker panels provide interpretable structure for the nine SEs.
- Expression-based recovery transferred SE signatures to single-cell, spatial and bulk RNA-seq datasets; paired bulk/Visium and cross-platform evaluations support positive concordance, although performance varies by SE and cohort.
- Liquid EcoTyper recovered SE ordering in 115 held-out simulated melanoma cfDNA profiles and was compared with paired tumour measurements from 23 patients. The paper also reports proof-of-principle analyses across 13 carcinoma types.
- In pretreatment plasma from 78 patients with metastatic melanoma, liquid- and tissue-derived ICI response-association patterns were highly concordant ($r=0.97$). Higher SE7 was associated with durable benefit and longer survival, whereas higher SE4 was associated with no durable benefit and shorter survival. A ten-patient external cohort supplies supportive, but small, replication.

These are cohort associations, not evidence that SEs cause therapeutic response or that the reported thresholds constitute a clinically validated decision rule.

### What the local code verifies

The author-linked `spatialecotyper` R package (version 1.0.4; snapshot commit `7748a5c0064d0445d8fef887854bc65f6f03e00d`) directly implements the central Spatial EcoTyper components: neighbourhood construction, cell-type network fusion, within- and cross-sample clustering, NMF basis training, cell-state recovery, pseudo-bulk generation and bulk deconvolution. The match is **medium fidelity** overall because these reusable functions do not constitute the complete study analysis.

Two reproducibility differences are material. First, the current `LoocvPredict` implementation trains on one sample and tests on all others, whereas the paper describes training on all but one held-out sample. Second, `RecoverSE` defaults to `min.score=0`, while the paper uses a 0.6 assignment cutoff. The package defaults for NMF rank and run count also should not be mistaken for the paper's parameter sweep.

### Reproducibility assessment

**Rating: 3/5 (partial reproduction support).** The public R package, direct source, vignettes, pretrained assets and repository provenance make the Spatial EcoTyper algorithm inspectable and reusable. However, no Liquid EcoTyper training or inference source was found locally, no complete manuscript workflow or figure-generation pipeline is present, no covering test suite was found, and no local supplementary Markdown was acquired. The code was inspected statically but not executed in this analysis. Therefore, the spatial/expression method is substantially auditable, while the liquid-biopsy results and exact end-to-end study remain paper-only evidence.

### Recommended reading order

1. `doc_method.md` for the complete input-to-output algorithm and equations.
2. `figure_analysis.md` for image-grounded interpretation of the main and Extended Data figures.
3. `doc_code.md` for exact paper–code matches, mismatches and missing implementation.
4. `Chinese method notes` for a learning-oriented Chinese explanation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
