---
layout: default
permalink: /paper-atlas/coordinatedcellularneighborhoods-251a016a/
title: "CoordinatedCellularNeighborhoods"
nav: false
wide: true
description: "这篇工作的核心不是再做一次“细胞分群”，而是把空间组织提升为一个新的分析单位：细胞邻域（cellular neighborhood, CN）。每个细胞根据其周围 10 个最近细胞的类型组成获得一个 CN 标签；随后，研究者比较不同患者中“哪些细胞类型位于哪些 CN、这些组合如何共同变化、CN 内细胞处于什么功能状态、不同 CN 的功能状态是否相关”。"
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
      <span>Cell · 2020</span>
    </div>
    <h1>CoordinatedCellularNeighborhoods</h1>
    <p>Coordinated Cellular Neighborhoods Orchestrate Antitumoral Immunity at the Colorectal Cancer Invasive Front</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1016/j.cell.2020.07.005" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for CoordinatedCellularNeighborhoods">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/nolanlab/NeighborhoodCoordination" target="_blank" rel="noopener noreferrer" aria-label="Open code for CoordinatedCellularNeighborhoods">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Coordinated Cellular Neighborhoods：从细胞邻居到组织级免疫结构

### 先说结论

这篇工作的核心不是再做一次“细胞分群”，而是把空间组织提升为一个新的分析单位：**细胞邻域（cellular neighborhood, CN）**。每个细胞根据其周围 10 个最近细胞的类型组成获得一个 CN 标签；随后，研究者比较不同患者中“哪些细胞类型位于哪些 CN、这些组合如何共同变化、CN 内细胞处于什么功能状态、不同 CN 的功能状态是否相关”。

因此，这套框架回答的是：

> 两个肿瘤可能含有相似的细胞类型，但这些细胞是否被组织进了不同的空间区室，并以不同方式协同？

论文在 35 位晚期结直肠癌患者的 140 个侵袭前沿区域中识别出 9 个生物学 CN，并提出 DII 高风险患者具有更强的肿瘤–免疫区室耦合、T 细胞与巨噬细胞 CN 的异常联系，以及不同的 CN 功能状态相关网络。但这些“耦合”和“通信”主要来自张量分解与相关性分析，是机制假设，不是因果证明。

### 来源边界

用户给出的 DOI `10.1016/j.cell.2020.10.021` 是一页勘误，只补充了一位遗漏作者。本文方法和结果的主证据来自其链接的原始 Cell 论文：DOI `10.1016/j.cell.2020.07.005`，PMCID `PMC7479520`。

### 为什么已有视角不够

| 已有工具/视角 | 论文中的作用 | 仍缺少什么 |
|---|---|---|
| 原始 CODEX（Cell, 2018） | 在保留空间坐标的同时进行高参数蛋白成像 | 原方案面向新鲜冷冻组织；本研究需要适配临床 FFPE 档案样本 |
| X-shift（Nature Methods, 2016） | 根据标志物表达识别细胞类型 | 得到的是“细胞是什么”，不是“组织由哪些空间区室组成” |
| histoCAT（Nature Methods, 2017）及成对接触分析 | 描述细胞表型和局部相互作用 | 成对接触在本队列中没有很好地区分 CLR 与 DII，难以表达更高阶的组织结构 |

这里并没有对这些方法做统一基准测试。论文的主张是“分析层级不足”：只统计细胞丰度或两两接触，会压平组织区室；CN 则把局部细胞组成变成可比较的组织级变量（`paper.md:7-29,82-104`）。

### 输入与输出

#### 输入

- 17 位 CLR 与 18 位 DII 患者，每位患者 4 个肿瘤侵袭前沿 TMA 区域；
- 56 个蛋白标志物的 FFPE-CODEX 图像；
- 每个细胞的二维坐标、标志物强度、患者/组织块编号；
- 经 X-shift 与人工核验得到的 28 个生物学细胞类型；
- 功能标志物 PD-1、Ki-67、ICOS 以及生存信息。

#### 输出

- 每个细胞的 CN 标签与 9 个生物学 CN；
- 每位患者的 CN 丰度、CN 内细胞类型频率和接触统计；
- CLR/DII 各自的 CN 模块、细胞类型模块和组织模块；
- CN 特异的功能状态、分类和生存关联；
- 基于 CCA 的 CN 相关网络。

### 一条主线看懂计算流程

```text
FFPE 组织
  -> 56-marker CODEX 图像
  -> 分割细胞，得到标志物与 (x,y)
  -> X-shift + 人工合并：28 个生物学细胞类型
  -> 每个细胞取包含自身的 10 个最近细胞
  -> 形成局部细胞类型组成向量
  -> MiniBatchKMeans 分 10 类
  -> 去掉成像伪影类：得到 9 个 CN
  -> 患者 × CN × 细胞类型的联合组成
       ├─ Delaunay 接触与 CN mixing
       ├─ 非负 Tucker 分解
       ├─ CN 特异功能富集/分类/生存
       └─ 两两 CN 的 CCA + 置换检验
```

### 第一步：把每个细胞变成一个“局部窗口”

对第 $s$ 个细胞，算法按 $(x,y)$ 欧氏距离寻找 10 个最近细胞，**其中包含中心细胞自身**。然后统计这 10 个细胞中各细胞类型的频率，得到局部组成向量 $\mathbf{x}_s$。

需要注意两个容易混淆的“10”：

1. 每个空间窗口包含 10 个细胞；
2. MiniBatchKMeans 把窗口分成 10 个初始类别。

聚类可简写为

$$
z_s=\arg\min_{m\in\{1,\ldots,10\}}
\lVert\mathbf{x}_s-\boldsymbol{\mu}_m\rVert_2^2.
$$

这只是对论文 MiniBatchKMeans 步骤的数学重述，并非论文编号公式。每个中心细胞继承窗口类别；富集成像伪影的类别随后被删除，所以最终是 9 个生物学 CN（`paper.md:90-104,550-552`）。

代码直接支持这一过程：`Neighborhood Identification.ipynb` 的抽取代码第 12–44 行调用最近邻，第 80–114 行构建局部计数并执行 `MiniBatchKMeans(n_clusters=10, random_state=0)`。代码没有删除零距离邻居，因此确实包含中心细胞。

### 第二步：为什么还要算两两接触

论文先用 Delaunay 三角剖分定义直接相邻细胞。对类型 $i,j$，接触似然与相对频率为

$$
L_{ij}=\frac{N_{ij}N_t}{N_iN_j},
\qquad
R_{ij}=\frac{N_{ij}}{N_i}.
$$

$N_{ij}$ 是 $i$–$j$ 边数，$N_t$ 是总边数，$N_i,N_j$ 是相应类型参与的边数。`app_CRC_contacts.R:307-365,622-647` 直接实现了 Delaunay 边、对称化和这一似然公式。

但论文观察到，CLR 与 DII 的主导两两接触没有显著差异。这恰好说明“邻居 A–B 是否接触”不足以描述由许多细胞共同组成的空间区室，于是分析转向 CN。

### 第三步：把患者表示成 CN × 细胞类型矩阵

对每位患者，统计每个 CN 中每种细胞类型的频率。由于滤泡 CN-5 基本只在 CLR 中存在，张量分析将它排除，避免患者组差异被这个已知结构主导。

把所有患者叠起来，得到非负三维张量

$$
\mathcal{X}^{(g)}\in\mathbb{R}_{+}^{P_g\times C\times N},
$$

其中 $P_g$ 是组 $g$ 的患者数，$C$ 是细胞类型轴，$N$ 是 CN 轴。代码中的后两轴顺序是 CN × CT；只要因子解释同步交换，这只是轴顺序不同。

### 第四步：非负 Tucker 分解到底在分什么

模型近似为

$$
\mathcal{X}^{(g)}\approx
\mathcal{G}^{(g)}\times_1A^{(g)}\times_2B^{(g)}\times_3C^{(g)}.
$$

可以把它理解为：

- CN 因子把经常共同变化的 CN 组合成 **CN 模块**；
- CT 因子把共同变化的细胞类型组合成 **CT 模块**；
- 核张量 $\mathcal{G}$ 描述某个 CN 模块和某个 CT 模块在一个 **组织模块** 中耦合多强。

论文用重构误差的视觉肘点选择秩 $(2,6,6)$：2 个组织模块、6 个 CN 模块、6 个 CT 模块；Figure S6 的曲线在 6 附近出现明显弯折。`tensor_decomposition_cleaned_up.ipynb` 的抽取代码第 36–110 行构造组内张量、按患者归一化、扫描秩并调用 Tensorly 的 `non_negative_tucker`。

这里最重要的边界是：分解得到的是共变结构。把某个因子命名为“肿瘤区室”“免疫区室”或“粒细胞区室”依赖载荷与图像的生物学解释，不等于模型直接发现了调控通路。

### 第五步：区分“细胞总量变化”和“CN 功能状态变化”

如果 DII 中某类 T 细胞整体更多，那么某个 CN 内它更多可能只是总量的结果。论文因此拟合

$$
Y_{n,c}=\beta_0+\beta_1X+\beta_3Y_c+e,
$$

其中 $Y_{n,c}$ 是细胞类型 $c$ 在 CN $n$ 内的对数频率，$X$ 是患者组，$Y_c$ 是该细胞类型的整体对数频率，加入 $10^{-3}$ 伪计数。$\beta_1$ 回答的是：控制整体丰度后，这个细胞类型是否仍在某个 CN 中额外富集（`paper.md:560-562`）。

随后论文比较只用整体频率的 L1 逻辑回归与加入 CN 特异频率的模型，并通过重复留出评估 AUC。CN 信息提高了组别分类表现。但这是同一小队列内的重复抽样比较，不是外部验证。

### 第六步：生存结果应怎样理解

在 18 位 DII 患者、13 个死亡事件中，CN-9 内 PD-1$^+$CD4$^+$ T 细胞频率与总体生存显著相关（Cox 模型 $p=0.006$）；整体 PD-1$^+$CD4$^+$ 频率或 CN-9 总量本身不显著（`paper.md:166-176`）。这说明“某种细胞位于哪里”可能比“有多少这种细胞”更有信息。

但它仍是小样本、经候选特征筛选后的队列内关联，不能直接称为经验证的临床生物标志物，也不能推出 PD-1$^+$CD4$^+$ T 细胞导致更长生存。

### 第七步：CCA 为什么被称为“通信”

对任意两个 CN，分别取其中 ICOS$^+$、Ki-67$^+$、PD-1$^+$ CD8$^+$ T 细胞和 Ki-67$^+$ Treg 的患者级频率。CCA 在两个多变量矩阵中寻找相关最大的投影，再用 5,000 次置换构造零分布。若观察相关高于 90% 的置换值，就在两个 CN 之间连边（`paper.md:178-192,578-580`）。

`cca_cleaned_up.ipynb` 直接实现了一维 CCA 和 5,000 次置换。代码变量 `p=np.mean(obs>perms)` 实际保存“观察值高于置换值的比例”，即论文所述超越概率的补量；阈值 `p>0.9` 仍与图中的连边规则一致。

“通信”在这里必须读作**跨患者功能状态的相关代理**。它没有测配体–受体、细胞迁移或信号方向，因此不能说明谁向谁发送了什么分子信号。

### 结果串起来后的生物学图景

- Figure 4：九个 CN 与组织影像相符；除滤泡 CN-5 外，其他 CN 的丰度在两组中大体保守。
- Figure 5：CLR 的肿瘤与免疫模块较分离；DII 中二者更耦合，并出现独立粒细胞区室。
- Figure 6：CN 特异功能状态比整体频率包含更多组别信息；CN-9 内 PD-1$^+$CD4$^+$ T 细胞与 DII 生存相关。
- Figure 7：DII 中 CN-1 的增殖 CD8$^+$ T 细胞与 CN-4 的 Treg 呈负相关，CCA 网络也发生重排。

这些结果共同支持一个**假设模型**：较差预后的 DII 组织中，肿瘤区室与免疫区室的组织边界和功能关联发生改变，T 细胞与巨噬细胞相关 CN 可能参与免疫抑制。但论文没有通过空间干预或分子机制实验验证这条因果链。

### 代码能复现到哪里

总体 paper–code fidelity 为 **medium**：

- **Exact：** R 脚本中的 Delaunay 接触似然核心公式；
- **Notebook：** 10-cell CN 识别、Tucker 分解、CN mixing；
- **Partial：** 差异富集 notebook 有未解析的变量/导入名；CCA 统计量命名与论文 p 值方向相反但阈值逻辑一致；
- **MISSING：** 本地没有外部 Mendeley 单细胞输入表；
- **Not found：** CODEX 图像预处理/X-shift、L1 重复留出、功能状态改变分数、Cox 生存、测试、锁定环境、完整启动器和完整作图流程。

因此，这个工作区足以学习算法结构并核对多个核心实现，但尚不能宣称端到端复现论文结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Coordinated Cellular Neighborhoods

### Source note

The requested DOI `10.1016/j.cell.2020.10.021` is a correction notice that adds an omitted author. This analysis uses the linked original Cell research article, **“Coordinated Cellular Neighborhoods Orchestrate Antitumoral Immunity at the Colorectal Cancer Invasive Front”** (2020), DOI `10.1016/j.cell.2020.07.005`, PMCID `PMC7479520`, as the scientific source.

### Problem

Multiplexed imaging can identify cell types, marker states, and pairwise contacts while retaining spatial coordinates, but those views do not directly describe how tissue-scale regions are organized and coordinated. In this cohort, pairwise cell-contact patterns alone did not distinguish the two immune architectures well (`paper.md:82-90`). The paper therefore asks whether higher-order **cellular neighborhoods (CNs)**—local regions defined by characteristic cell-type mixtures—reveal clinically relevant tumor–immune organization.

### Contribution

The study combines an FFPE-adapted CODEX assay with a multiscale computational framework:

1. phenotype cells from 56-marker images;
2. summarize the 10 nearest cells around every cell as a local cell-type-composition vector;
3. cluster those windows into CNs;
4. compare group-specific CN–cell-type organization with non-negative Tucker decomposition;
5. test CN-specific functional-marker enrichment, classification, survival association, and inter-CN correlations.

After discarding an artifact cluster, the analysis identifies nine biological CNs, including follicle, T-cell-enriched, macrophage-enriched, bulk-tumor, tumor-boundary, and granulocyte-enriched compartments (`paper.md:88-104,550-558`). The novelty is not merely spatial clustering: it jointly analyzes cell types and tissue regions, then treats CN functional states and their cross-patient correlations as hypotheses about coordinated tissue behavior.

### Evidence and main results

- **Cohort/assay:** 17 CLR and 18 DII patients, four invasive-front regions per patient, 140 regions total, profiled with a 56-marker FFPE-CODEX panel (`paper.md:33-39,57-59`).
- **CN conservation:** all non-follicular CN frequencies were broadly similar across groups; follicle CN-5 was strongly enriched in CLR. Image overlays support correspondence between CN maps and tissue structures (`paper.md:98-104`; Figure 4).
- **Higher-order organization:** rank-$(2,6,6)$ non-negative Tucker decomposition suggested separate immune and tumor compartments in CLR, versus coupled tumor/immune organization and a distinct granulocyte compartment in DII (`paper.md:108-128`; Figure 5).
- **Added spatial information:** repeated-holdout classifiers using CN-specific functional-cell frequencies outperformed overall-frequency-only models (`paper.md:156-164`; Figure 6F). This is an internal comparison, not an external benchmark.
- **Clinical association:** in 18 DII patients with 13 deaths, PD-1$^+$CD4$^+$ T-cell frequency within granulocyte-enriched CN-9 was associated with overall survival ($p=0.006$); overall PD-1$^+$CD4$^+$ frequency and CN-9 abundance alone were not significant (`paper.md:166-176`; Figure 6J/K).
- **Communication hypothesis:** CCA/permutation graphs and the CN-1/CN-4 correlation differed between CLR and DII (`paper.md:178-194`; Figure 7). These correlations are proxies for coordination, not proof of signaling or causality.

### Limitations

The cohort is small and deliberately selected from opposite immune-architecture extremes. Cell segmentation/typing and functional-marker gating require manual validation; tissue quality, autofluorescence, marker-panel limits, and the need for well-defined CNs affect transferability. The paper explicitly states that larger samples are needed for conclusive biological interpretation of Tucker and CCA results (`paper.md:210-212`). Feature-associated survival has not been independently validated here.

### Reproducibility

**Rating: 2/5; code-paper fidelity: medium.** The first-party repository snapshot contains the main neighborhood-identification, Tucker, mixing, differential-enrichment, CCA, contact, and Voronoi components. Direct reads verify the 10-cell windows, MiniBatchKMeans, rank-$(2,6,6)$ Tensorly calls, Delaunay likelihood calculation, and 5,000-permutation CCA structure.

However, the external Mendeley single-cell input is **MISSING** from this workspace. Tests, an environment lockfile, an executable end-to-end launcher, CODEX preprocessing/X-shift code, L1 repeated-holdout and alteration-score code, Cox survival code, and a complete figure workflow were **Not found**. The generalized differential-enrichment notebook is **Partial** because it contains unresolved variable/import names. No results were rerun, so reproducibility here means static paper–code correspondence, not successful numerical reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
