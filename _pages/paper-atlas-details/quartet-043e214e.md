---
layout: default
permalink: /paper-atlas/quartet-043e214e/
title: "Quartet"
nav: false
description: "同一批病人样本的 DNA、RNA、蛋白和代谢物，常常不是在同一天、同一仪器、同一实验室完成测量。直接比较这些绝对定量值时，批次、平台和实验流程带来的偏移，可能比真正的生物差异还大。于是会出现两个问题： 横向整合：同一种组学的多个批次能否合并，而不是按批次聚类？ 纵向整合：不同组学合在一起后，能否找回真实的样本分组和跨组学关系？"
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
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>Quartet</h1>
    <p>Multi-omics data integration using ratio-based quantitative profiling with Quartet reference materials</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Quartet：用共同参考物把多组学“绝对量”变成可比较的相对量

### 这篇论文究竟要解决什么问题？

同一批病人样本的 DNA、RNA、蛋白和代谢物，常常不是在同一天、同一仪器、同一实验室完成测量。直接比较这些**绝对定量值**时，批次、平台和实验流程带来的偏移，可能比真正的生物差异还大。于是会出现两个问题：

1. **横向整合**：同一种组学的多个批次能否合并，而不是按批次聚类？
2. **纵向整合**：不同组学合在一起后，能否找回真实的样本分组和跨组学关系？

以往可用 ComBat、Harmony、RUVg 或 z score 做批次校正，但论文强调：如果没有一个能判断“答案是否正确”的参照，仅看 PCA 图很难客观比较这些方法。Quartet 的核心价值不是又提出一个通用机器学习模型，而是建立了可用于质量控制的**参考材料 + 评价真值 + 相对定量流程**。

### Quartet 参考体系提供了什么“真值”？

材料来自一个家庭的淋巴母细胞系：同卵双胞胎 D5、D6，父亲 F7 和母亲 M8。论文同时制备 DNA、RNA、蛋白和代谢物参考物，并在多实验室、多平台、多批次中测量（`paper.md:42-62`）。因此有两类很实用的真值：

- **样本真值**：四个人应能分开；从遗传关系看，两个女儿又应更接近。
- **特征真值**：DNA、RNA、蛋白之间存在中心法则方向的关联，可用于检验跨组学相关性是否稳定。

这比“算法给出了一个聚类结果”更严格：结果可以和已知的家庭结构、跨层分子关系作比较。

### 新意：每个批次都带一个共同参照 D6

设 $X_{f,s,b}$ 为批次 $b$ 中样本 $s$ 的特征 $f$ 的 log2 定量值。D6 在同一批次有 $n_{D6,b}$ 个技术重复。论文的 Ratio 变换为：

$$R_{f,s,b}=X_{f,s,b}-\frac{1}{n_{D6,b}}\sum_{r=1}^{n_{D6,b}}X_{f,D6_r,b}.$$

也就是：**每一个特征，减去同批次 D6 的平均值**。在 log2 空间里，减法等价于原始空间里的“样本值 / 参考值”。

一个直观小例子：某蛋白在批次 A 中，F7 的 log2 强度为 12，D6 平均为 10，得到 $R=2$；在批次 B 中，仪器整体偏高 3，F7 为 15、D6 为 13，仍得到 $R=2$。绝对值从 12 变成 15，但相对 D6 的差异不变。这正是该设计希望抵消的共同批次偏移。

本地代码可直接验证这一点：`src/prepare_data/dataL_absolute_ratio.r:15-40` 遍历每种组学和每个批次，在第 32 行对所有特征减去 D6 列的逐特征均值。

```text
多组学原始/标准化矩阵 + 批次与样本标签
                  │
        每个批次都测 D6 参考物
                  │
  每个特征：study sample − 同批次 D6 平均
                  │
              Ratio 矩阵
           ┌──────┴──────┐
           │             │
横向：批次可比性     纵向：跨组学整合
SNR、DEF-RMSE        相关性、ARI、相似矩阵 SNR
```

### 横向整合怎么评估？

论文比较六条路径：Absolute、Ratio、ComBat、Harmony、RUVg、z score（`paper.md:567-607`）。Absolute 是常规预处理后直接合并；Ratio 是先做 D6 相对化。对应代码 `utils/batch_correct_func_fix.r:1-66` 确实提供这些分支。

重要指标之一是 SNR。它比较不同供体之间的距离与同一供体技术重复之间的距离，并按 PC1/PC2 解释方差加权：

$$\mathrm{SNR}=10\log_{10}\left(\frac{\text{平均供体间距离}}{\text{平均技术重复内距离}}\right).$$

SNR 越高，说明既能区分 D5/D6/F7/M8，又不会把技术重复拉得很散。本地 `utils/calSNR.r:7-45` 实际执行 PCA、构造 Inter/Intra 成对距离并返回 `10*log10(inter/intra)`。

另一个指标是 DEF 的 RMSE：把整合后得到的 log2 fold change 与参考数据集的 fold change 相比，越小越一致（`paper.md:501-510`）。快照中找到了计算 t 检验与 log2FC 的 `utils/def_analysis.r:16-56`，但**未找到**单独计算 RMSE 的本地函数。

### 纵向整合怎么评估？

纵向整合有两条输出路线。

#### 1. 跨组学特征关系是否稳定

论文先为生物学上可连接的特征对计算每个批次组合的 Pearson 相关；$r\ge0.5$ 且 $P<0.05$ 为正，$r\le-0.5$ 且 $P<0.05$ 为负；若某个方向在超过 70% 的组合中重复出现，就保留，并以保留值的均值作为参考相关性（`paper.md:471-486`）。

`src/corr/Corr_reference.r:143-203` 直接实现了批次数过滤、相关/P 值阈值、70% 一致性过滤和均值汇总。图 4 的本地图像也能看到，Ratio 的跨批次关系比 Absolute 更贴近单批次关系。

#### 2. 能否恢复真实样本分组

论文把每种组学的高变特征输入 SNF、iClusterBayes、MOFA+、MCIA、intNMF；用 ARI 评价聚类标签与四个 Quartet 成员标签的一致性，并由样本相似矩阵计算另一种 SNR（`paper.md:609-645`）。本地 `utils/integrate_func.r:6-220` 有这五个方法的分发函数；`src/vertical/ARI_multibatch_scenario_integration.r:193-216` 把聚类数设为 4，计算 ARI，并保存 affinity matrix。

图 5 的关键阅读方式是：不要只看某个算法的柱子高不高，而要比较同一算法下 Absolute 与 Ratio。图中 Ratio 在所示质量和采样情景下的 ARI 普遍接近 1，Absolute 则更容易下降。

### 结果应如何理解？

图 3 显示 Ratio 后跨批次散点更贴近对角线、CV 更低、PCA 更按供体而不是批次分开，SNR 更高。图 4 显示跨组学相关更稳定。图 5 显示纵向样本分类更稳。图 6 则把这种稳定性接到遗传学解释：多组学整合可恢复四人/三类家系结构，并连接 D5 与 D6 的分子差异。

这支持的结论是：**在同时测量共同参考物的 Quartet 控制体系中，Ratio 设计能增强跨批次和跨组学的可比性。** 它不是“任何数据集都必然更好”的定理。尤其是本地实现自己注明 Ratio 分支不能用于 unbalanced 情形（`batch_correct_func_fix.r:33`），所以缺少同批次共同参考物、严重不平衡或不同临床队列时，都应重新验证。

### 代码复现边界与一个明确差异

代码是 Zenodo 的源文件快照，缺少 `data/`、生成的 `res/` 和补充材料 Markdown，因此不能在当前工作区端到端复现图中的数字。还有一个已核实的差异：论文对 SNF 写的是 $K=\mathrm{round}(n^2)$、alpha=0.5、$T=10$（`paper.md:618-622`）；快照 `DoSNF()` 却使用 `K=floor(sqrt(n))+1`、`sigma=0.5`、`t=200`（`utils/integrate_func.r:138-152`）。因此 SNF 是**部分匹配**，不能把快照参数当作论文图的已证实配置。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Quartet: ratio-based multi-omics profiling

### Problem

Multi-omics integration has no easy ground truth when measurements are collected across laboratories, platforms, batches, and modalities. Absolute quantitative profiles can be dominated by technical offsets, confounding both within-omics batch correction and cross-omics clustering/correlation analysis.

### Contribution

Published in *Nature Biotechnology* (2024), this atlas/resource establishes matched DNA, RNA, protein, and metabolite reference materials from a family quartet: monozygotic twins D5/D6 and parents F7/M8. It pairs those materials with **ratio-based quantitative profiling**: within every batch, express each feature relative to concurrently measured D6. The pedigree supplies sample-class truth; expected DNA→RNA→protein relations provide feature-level truth.

### Method in brief

The paper compares direct absolute integration with D6-relative ratio matrices and conventional horizontal approaches (ComBat, Harmony, RUVg, z score). It then evaluates vertical integration with SNF, iClusterBayes, MOFA+, MCIA, and intNMF. Key readouts are PCA-based SNR for donor-versus-replicate separation, RMSE of differential features, ARI for Quartet labels, and reproducibility of signed cross-omics correlations.

The local archive confirms the main operational steps: `dataL_absolute_ratio.r` subtracts each batch's feature-wise D6 mean; `calSNR.r` implements PC-weighted inter/intra SNR; `batch_correct_func_fix.r` exposes the horizontal alternatives; and `integrate_func.r` dispatches the five vertical methods. The paper and code disagree on SNF parameterization, so that portion is a partial—not exact—match.

### Evidence and results

Direct reads of Figures 1–6 show the intended benchmark geometry, variable wet-lab quality, stronger batch-pair agreement and donor separation after ratio scaling, more stable cross-omics correlations, and high Quartet-label ARI in the displayed ratio analyses. The paper's controlled experiments support ratio scaling as a useful design for this reference setting; they do not eliminate the need to validate other cohorts, designs, or missing-reference cases.

### Reproducibility

The paper points to Zenodo code, and this workspace has a source-only archive snapshot. The ratio/SNR/correlation/integration code paths are inspectable, but raw `data/`, generated `res/` artifacts, supplementary Markdown, and a code-repository commit are absent. It cannot be rerun end-to-end here. `doc_code.md` records five exact and two partial paper-code links, with missing execution artifacts explicitly retained as **Not found**.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
