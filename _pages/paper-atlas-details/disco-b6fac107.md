---
layout: default
permalink: /paper-atlas/disco-b6fac107/
title: "DISCO"
nav: false
wide: true
description: "DISCO 不是一个单独的预测模型，而是一套“数据工程 + 统计整合 + 细胞注释 + 图谱交付”的资源构建系统。 公共单细胞 RNA 测序数据虽然很多，但直接合并会遇到四类问题： 处理流程不同：各研究采用不同的比对参考、基因注释和质控规则； 元数据不一致：组织、疾病、平台和样本类型的命名不统一； 细胞类型标签不一致：相同细胞可能使用不同名称，也未必映射到统一的 Cell Ontology；"
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
      <span>Nucleic Acids Research · 2022</span>
    </div>
    <h1>DISCO</h1>
    <p>DISCO: a database of Deeply Integrated human Single-Cell Omics data</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/JinmiaoChenLab/FastIntegration" target="_blank" rel="noopener noreferrer" aria-label="Open code for DISCO">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DISCO 方法详解：从公共单细胞原始数据到可查询的人类细胞图谱

### 1. 这篇论文真正解决什么问题？

DISCO 不是一个单独的预测模型，而是一套“数据工程 + 统计整合 + 细胞注释 + 图谱交付”的资源构建系统。

公共单细胞 RNA 测序数据虽然很多，但直接合并会遇到四类问题：

1. **处理流程不同**：各研究采用不同的比对参考、基因注释和质控规则；
2. **元数据不一致**：组织、疾病、平台和样本类型的命名不统一；
3. **细胞类型标签不一致**：相同细胞可能使用不同名称，也未必映射到统一的 Cell Ontology；
4. **批次规模过大**：传统 Seurat Integration 能输出校正后的基因表达，但难以扩展到数百万细胞和大量批次。

论文还指出，当时的 Human Cell Atlas Data Portal、PanglaoDB、Single Cell Portal 和 TISCH 等资源通常缺少以下一项或多项能力：跨研究整合后的表达矩阵、统一元数据/本体、以及把用户新数据投影到参考图谱的工具（`paper.md:20-29`）。当前转换版论文没有保留完整参考文献条目，因此这些资源的论文发表期刊和年份在本地证据中 **Not found**，不在此猜测。

DISCO 的目标是把这些环节串起来，最终输出：

- 统一处理、可下载的样本表达矩阵；
- 统一术语和本体映射后的元数据；
- CELLiD 给出的标准细胞类型；
- 一个全局图谱和组织、疾病、细胞类型子图谱；
- Online FastIntegration、Online CELLiD 和 CellMapper 三类在线工具。

论文报告的 2022 年版本包含超过 1800 万个细胞、4593 个样本、351 个项目，覆盖 107 个组织/细胞系/类器官、158 种疾病和 20 个平台（`paper.md:14-16,29,77`）。

### 2. 输入、变量形状与输出

#### 2.1 统一预处理

- 输入：FASTQ、SRA 或 BAM 格式的人类 scRNA-seq 原始数据，以及研究级元数据；
- 中间表示：基因-细胞计数矩阵 $X\in\mathbb{R}^{G\times C}$，其中 $G$ 是基因数，$C$ 是细胞数；
- 输出：统一到 hg38 和 Ensembl 93 的表达矩阵、细胞质控标记、样本元数据。

#### 2.2 CELLiD

论文层面的输入是：

- 一个待注释簇的平均表达向量 $x\in\mathbb{R}^{G}$；
- 参考表达矩阵 $R\in\mathbb{R}^{G\times K}$，每列代表一个参考细胞类型，$K$ 为候选类型数。

输出是最匹配的标准细胞类型，以及原始名称、Cell Ontology、层次树位置和来源数据集等信息。

#### 2.3 FastIntegration

输入是 $B$ 个批次/样本的 Seurat 对象或表达矩阵：

$$
\mathcal{X}=\{X_1,\ldots,X_B\},\qquad X_b\in\mathbb{R}^{G\times C_b}.
$$

主要中间变量包括：

- `features`：用于寻找锚点的共享特征，代码默认 2000 个；
- `anchors`：跨数据集匹配的细胞对；
- `sample.tree`：决定批次递归合并顺序的树；
- `input.pca`：所有未整合数据共同计算一次的低维坐标，形状约为 $\left(\sum_b C_b\right)\times d$；
- $W$：查询细胞相对于锚点的权重矩阵；
- $X_{\mathrm{integrated}}$：批次校正后的表达矩阵。

输出是保留基因表达维度的批次校正矩阵/Seurat 对象，而不只是 UMAP 坐标。

#### 2.4 图谱和在线系统

输入是质控通过、元数据统一、细胞类型已标准化的样本；输出是全局/主题图谱、UMAP、聚类、细胞类型和基因表达视图，以及 RDS/表格下载。

### 3. 全流程：从原始数据到在线图谱

```text
公共研究
  FASTQ / SRA / BAM + 研究元数据
          |
          v
统一预处理
  格式转换 -> 按平台拆 barcode/UMI
  -> STAR 比对 hg38 -> featureCounts / Ensembl 93
          |
          v
细胞与样本质控
  线粒体表达 Z 分数 + 特征数 Z 分数
  -> 样本最小细胞数过滤
          |
          v
元数据统一
  8 个公共字段 + 26 个研究特异字段
  -> 受控词表 + Experimental Factor Ontology
          |
          +----------------------+
          |                      |
          v                      v
CELLiD 标准注释            FastIntegration 批次校正
  84 个注释数据集构建参考    磁盘暂存 -> 成对锚点
  -> 粗粒度相关性筛选         -> 样本合并树 + 一次 PCA
  -> 细粒度相关性重排         -> 递归表达校正 + 基因并行
          |                      |
          +-----------+----------+
                      v
图谱构建
  全局抽样 / 主题筛选
  -> PCA 前 50 PCs -> UMAP -> FastPG -> CELLiD
                      |
                      v
DISCO 交付
  图谱浏览 + 数据下载 + FastIntegration
  + CELLiD + CellMapper
```

### 4. 步骤一：统一原始数据处理

DISCO 只纳入能够获得原始 reads 的人类组织、类器官或细胞系数据。SRA 和 BAM 分别通过 SRA Toolkit 和 `bamtofastq` 转成 FASTQ（`paper.md:38-40`）。

拆分 barcode 和 UMI 时按平台选择工具：

- 10x Genomics：Cell Ranger 3.1；SC5P-PE 模式把 RNA read offset 从 26 改为 39，以去除 TSO 序列；
- Drop-seq：Drop-seq tools 2.4.0；
- BD Rhapsody、CEL-seq2、Seq-Well 等：UMI-tools。

随后用 STAR 把 reads 比对到 hg38，再用 featureCounts 2.0.2 按 Ensembl 93 计数。这里的关键思想不是“消除所有批次效应”，而是先消除因参考基因组、基因 ID 和计数流程不同造成的可避免差异，再进入统计整合。

### 5. 步骤二：细胞质控与元数据统一

论文分别对每个细胞的线粒体 mRNA 数和 unique feature 数拟合正态分布，并计算 $Z$ 分数。删除条件是：

$$
Z_{\mathrm{mitochondrial}}>1.64
$$

或

$$
\left|Z_{\mathrm{features}}\right|>1.64.
$$

质控后少于 500 个细胞的样本不参与整合，但仍作为低质量样本保留下载（`paper.md:40`）。

元数据被整理为 8 个公共字段：sample ID、project ID、sample type、disease status、tissue、platform、gender 和 cell number；另有 26 个研究特异字段。字段值使用受控词表或 EFO，本地论文还说明 sample type 被归为 18 类（`paper.md:42`）。

**缺失证据**：论文引用的 `QC.R` 位于当前不可用的 `DISCO_manuscript` 仓库，因此正态拟合方式、缺失值处理、分组粒度和边界条件在本地代码中 **Not found**。

### 6. 步骤三：CELLiD 的两阶段相关性注释

#### 6.1 参考库如何构建

作者收集了 84 个具有详细细胞类型标注的数据集，手工统一原始名称，将其映射到最接近的 Cell Ontology 类型，并建立细胞类型层次树（`paper.md:44-48`）。

#### 6.2 论文描述的算法

对每个输入簇平均表达 $x$：

1. **粗粒度阶段**：对所有重叠基因计算 $x$ 与每个参考类型 $r_k$ 的 Spearman 相关系数 $\rho(x,r_k)$；
2. 保留 $\rho>0.6$ **或** 排名进入前 5 的参考类型；
3. **细粒度阶段**：在保留类型中选 3000 个高变基因；
4. 用这些基因重新计算 Spearman 相关；
5. 报告最高相关的类型，并组装名称、本体、层次树和来源信息。

该方法没有训练损失函数，也没有参数学习；它是“参考库 + 两次排序/筛选”的确定性注释流程。

#### 6.3 本地代码实际做了什么

`FastIntegration/R/CELLiD.R:3-49` 验证了两轮 Spearman 相关的核心思路，但不是论文描述的完整实现：

- 输入矩阵每一列被独立处理，调用者需要在外部先完成聚类/求平均；
- 要求重叠基因数严格大于 2000；
- 第一轮只取前 5，没有 $\rho>0.6$ 的额外保留规则；
- 第二轮按参考矩阵行方差选 2000 个基因，而非论文的 3000 个；
- 返回前 2 个标签及相关系数，不组装 Cell Ontology 和完整报告。

因此，CELLiD 的代码-论文对应关系是 **Partial**，不能标成 Exact。

### 7. 步骤四：FastIntegration 如何扩展 Seurat

论文给出的动机是：Harmony 整体表现较好，但不返回批次校正后的基因表达，妨碍差异表达和调控网络等下游分析；Seurat 能返回校正表达，但在大量细胞和批次下扩展性不足（`paper.md:55-57`）。

FastIntegration 的代码主路径为：

```text
OneStopIntegration
  -> BuildIntegrationFile
  -> FastFindAnchors -> FindAnchorsPair
  -> FastIntegration
     -> FastPairwiseIntegrateReference
        -> FastRunIntegration
           -> FastFindWeights
```

#### 7.1 把大对象拆到磁盘

`BuildIntegrationFile`：

1. 检查并修正重复细胞名；
2. 默认选择 2000 个整合特征；
3. 记录每个对象的细胞数、累计 offset 和 `nFeature_RNA` 中位数；
4. 把每个 Seurat 对象保存为独立 RDS；
5. 在固定目录 `FastIntegrationTmp/{raw,anchors,others,inte}` 中保存中间文件。

直接证据：`FastIntegration/R/FastFindAnchors.R:237-290`。

这一步用更多磁盘 I/O 换取较低的同时驻留内存。后一句是设计解释，不是论文独立验证的性能结论。

#### 7.2 并行寻找数据集间锚点

`FindAnchorsPair` 对每一对数据集：

- 合并两边的 variable features，取出现频率最高的 2000 个；
- 分别 ScaleData；
- 运行 30 维 CCA 并做 L2 归一化；
- 调用 Seurat 内部 `FindAnchors`，默认 `k.filter=100`、`k.anchor=5`、`dims=1:30`。

数据集对之间通过 `pbmclapply` 并行（`FastFindAnchors.R:79-94,166-233`）。

#### 7.3 建立样本合并树

当样本数少于 `sample.cut=50` 时，代码用锚点数构造相似度：

$$
S_{ij}=\frac{A_{ij}}{\min(n_i,n_j)},
$$

其中 $A_{ij}$ 是数据集 $i,j$ 的锚点数，$n_i,n_j$ 是细胞数，然后交给 Seurat 的 `BuildSampleTree`（`FastFindAnchors.R:103-132`）。

当样本数不少于 50 时，代码改用各样本平均表达之间的相关矩阵建树，并缩小需要比较的样本对范围（`FastFindAnchors.R:28-77`）。因此，“FastBuildSampleTree”是图 3B 的模块标签，而不是本地仓库中的同名函数。

#### 7.4 低维空间只计算一次

代码把选定特征拼接后统一 ScaleData 和 RunPCA，把 `raw_pca.rds` 保存下来，后续每次合并都复用（`FastFindAnchors.R:134-162`）。论文说这里可以用 PCA 或 Harmony，但当前固定提交中只找到 PCA 路径，没有 Harmony 实现。

#### 7.5 沿合并树递归校正表达

每一步把较大的当前矩阵作为 reference，筛选连接两棵子树的 anchors，在共享 PCA 空间中寻找最近锚点并计算权重 $W$。代码的核心更新可写为：

$$
X_{\mathrm{integrated}}
=X_{\mathrm{query}}
-\left(X_{\mathrm{query,anchor}}-X_{\mathrm{reference,anchor}}\right)W.
$$

随后将校正后的 query 与 reference 按列拼接，继续向合并树上层传播（`FastIntegration/R/FastIntegration.R:74-228,232-275`）。

这个公式是对代码的直接重述，不是论文中的编号公式；论文没有给出正式目标函数或损失。

#### 7.6 按基因块并行

`OneStopIntegration` 把待整合特征固定分成 20 块，用 20 个 worker 并行执行整合，再把结果按行拼接成 Seurat 对象（`FastIntegration/R/OneStop.R:18-49`）。

值得注意的实现细节：

- 20 个块和 20 个 worker 是硬编码，不受 `max.cores` 控制；
- 如果调用者显式传入非空 `feature.to.integration`，代码不会创建后面使用的 `idx`，存在未定义变量风险（`OneStop.R:18-27`）；
- 查询细胞超过 10 万时，表达校正进一步按约 2 万细胞分块（`FastIntegration.R:186-200`）；
- 锚点超过 10 万时，每个 query cell 最多保留 10 个高分锚点（`FastIntegration.R:161-166`）；
- 代码大量调用 `Seurat:::` 和 `getFromNamespace` 的非导出接口，实际兼容性可能比 `DESCRIPTION` 中的 `Seurat >= 4.0.0` 更窄。

### 8. 步骤五：构建图谱与 CellMapper

图谱选择规则为：

- 组织/疾病子图谱：整合相应样本的全部细胞；
- 细胞类型子图谱：按 CELLiD 预测类型选择细胞；
- 全局图谱：每个样本抽 1000 个细胞，并尽量在样本内各簇之间均分。

整合后先做 PCA，取前 50 个 PC 做 UMAP，用 FastPG 聚类，最后用 CELLiD 标注簇（`paper.md:65`）。论文报告一张全局图谱、23 张组织图谱、3 张疾病图谱和 1 张 B/plasma cell 图谱（`paper.md:77-79`）。

CellMapper 把目标子图谱每个簇下采样到 500-1000 个细胞，然后以 CCA 而非 Seurat 默认 PCA 空间寻找 reference anchors，把用户 query 投影到图谱（`paper.md:67-69`）。

**缺失证据**：图谱驱动脚本、随机种子、UMAP/FastPG 详细参数、输入清单、最终图谱对象和 CellMapper 源码均不在本地 FastIntegration 快照中。

### 9. 论文如何评估，证据有多强？

论文的主要量化结果是资源规模和可运行规模，而不是完整的算法 benchmark：

- 报告 FastIntegration 可在一周内整合超过 400 万个细胞（`paper.md:57,91`）；
- 报告前述 1800 万细胞、4593 样本和图谱覆盖；
- 图 1 展示公共数据快速增长与组成不均衡；
- 图 2 展示 DISCO 全链路架构；
- 图 3 展示 CELLiD 和 FastIntegration 流程。

本地证据没有提供：

- 运行时间/内存曲线、硬件配置和可复现的 400 万细胞 benchmark；
- CELLiD 混淆矩阵、准确率、留出集或人工标注对照；
- FastIntegration 与 Seurat/Harmony 的本论文内定量对比表；
- 消融实验或参数敏感性分析。

因此，“规模达到多少”属于**论文声明**；“核心代码如何执行”可以由本地源码验证；

### 10. 代码-论文一致性与复现边界

#### 已直接验证

- RDS 磁盘暂存与固定中间文件协议；
- `pbmclapply` 并行成对锚点；
- 样本树构造；
- 一次 PCA、后续复用；
- 沿合并树做加权表达校正；
- 固定 20 个基因块并行；
- CELLiD 的两轮相关性骨架。

#### 部分一致

- CELLiD：论文阈值/基因数/输出与本地函数不同；
- FastIntegration 图 3B：本地有 PCA，无 Harmony；样本树逻辑没有同名 `FastBuildSampleTree` 函数。

#### MISSING / Not found

- 论文引用的 `DISCO_manuscript` 仓库（获取时 GitHub API 返回 404）；
- `QC.R`、CellMapper、论文级总控脚本；
- CELLiD 参考矩阵、本体和层次树资源；
- 图谱输入/输出、元数据整理文件、随机种子；
- React/Redux 前端、Java/Spring Boot 后端、MySQL/Redis 配置；
- 环境锁文件、测试、端到端示例、预期输出和 benchmark 记录。

本地 `FastIntegration` 固定在提交 `ebf9b6d133628655a9a5d0fb45be2202e43aad2c`，但其 README 已说明项目不再维护，功能迁移到了新的 DISCO toolkit。综合判断：**FastIntegration 方法子集有较强静态代码证据，但整个 DISCO 系统的代码-论文一致性为低，复现性约 2/5。**

### 11. 如何正确理解这项工作

DISCO 的核心创新不应只概括为“一个更快的 Seurat”。它把以下层次连接为一个可复用资源：

1. 统一原始 reads 处理，先减少可避免的技术不一致；
2. 统一元数据和 Cell Ontology，使跨研究检索和分组有共同语义；
3. CELLiD 用参考相关性统一细胞类型；
4. FastIntegration 在保留校正表达矩阵的同时扩大可处理规模；
5. 全局/主题图谱和在线工具把静态资源变成可查询参考。

合理的解释是：DISCO 的价值来自这些组件的组合，而不是单个指标。不能从架构图推出注释准确率，也不能从静态代码推出四百万细胞的实际运行时间。

### 12. 可检验的新问题（非论文结论）

- 图 1 所示的组织/平台不均衡是否会让全局图谱和 CELLiD 参考偏向高频来源？
- 磁盘暂存节省的峰值内存，是否会在不同存储介质上被 I/O 延迟抵消？
- 论文的“相关系数大于 0.6 或前五名、3000 基因”规则与代码的“仅前五名、2000 基因”规则，在同一批 cluster averages 上会产生多少标签差异？

这些是由图像和代码差异引出的后续假设，不是论文已经证明的结果。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DISCO: Deeply Integrated Human Single-Cell Omics Data

### Problem

Public single-cell RNA-seq data had grown rapidly, but study-specific processing, inconsistent gene identifiers, heterogeneous metadata, nonstandard cell-type labels, and batch effects made cross-study analysis difficult. The paper argues that existing resources such as the Human Cell Atlas Data Portal, PanglaoDB, Single Cell Portal, and TISCH generally lacked one or more of three capabilities: integrated batch-corrected atlases, harmonized metadata and cell ontology, and tools for projecting a user's data onto hosted references (`paper.md:20-29`). The converted paper does not retain the bibliography entries needed to assign those named resources reliable venues and years.

### What DISCO Contributes

DISCO is both a processed data resource and an analysis platform. The reported 2022 release contains more than 18 million cells from 4,593 samples in 351 projects, covering 107 tissues/cell lines/organoids, 158 diseases, and 20 platforms. It standardizes raw-read processing and metadata, reannotates cells with CELLiD, integrates datasets with FastIntegration, and exposes one global atlas plus 27 thematic sub-atlases (`paper.md:14-16,29,65,77-79`).

Three online workflows complete the resource:

- **FastIntegration** integrates selected public or uploaded datasets and returns batch-corrected gene expression.
- **CELLiD** assigns standardized cell types by coarse-to-fine correlation with a curated reference.
- **CellMapper** projects uploaded data onto a selected atlas with CCA-based reference mapping.

### High-Level Method

```text
public raw reads + study metadata
  -> common hg38/Ensembl 93 processing
  -> cell/sample QC + controlled metadata vocabulary
  -> CELLiD standardized cluster labels
  -> FastIntegration batch-corrected expression
  -> global and thematic atlases
  -> interactive exploration, online query tools, and downloads
```

Raw reads are converted and demultiplexed with platform-appropriate tools, aligned to hg38 with STAR, and counted against Ensembl 93 with featureCounts. Cells with mitochondrial $Z>1.64$ or absolute unique-feature $Z>1.64$ are removed; samples with fewer than 500 surviving cells are excluded from integration but remain downloadable (`paper.md:38-42`).

CELLiD uses a reference assembled from 84 annotated datasets. For each cluster-average profile, it first computes Spearman correlations across overlapping genes and retains cell types with correlation above 0.6 or in the top five. It then selects 3,000 variable genes among retained types, recomputes correlations, and chooses the best cell type (`paper.md:44-52`).

FastIntegration modifies Seurat integration for scale. It stores expression objects as temporary files, parallelizes pairwise anchor finding with `pbmcapply`, constructs the sample tree with matrix operations, computes PCA or Harmony once, reuses that representation for anchor weighting, and parallelizes corrected-expression calculation by gene blocks (`paper.md:55-65`; Figure 3B). The pinned code directly verifies disk-backed RDS staging, parallel anchors, a single PCA, iterative weighted expression correction, and 20 gene chunks. It does not implement the paper's optional Harmony branch.

Atlas construction integrates all relevant cells for tissue/disease atlases, predicted cells for cell-type atlases, and 1,000 cells per sample for the global atlas. The paper then applies PCA, the top 50 PCs for UMAP, FastPG clustering, and CELLiD labels (`paper.md:65`).

### Evidence and Evaluation

The paper's main quantitative evidence is scale and resource coverage, not a controlled method benchmark. It reports that FastIntegration integrated more than four million cells in one week and that DISCO delivers the corpus/atlas counts above (`paper.md:57,91`). Figure 1 shows the rapid growth and uneven composition of source studies; Figure 2 shows the end-to-end resource architecture; Figure 3 shows CELLiD and FastIntegration workflows.

Important evaluation limits are:

- no runtime curve, memory profile, hardware specification, comparator table, or reproducible four-million-cell benchmark protocol is provided locally;
- no CELLiD accuracy metric, confusion matrix, held-out evaluation, or comparison with manual annotation is shown in the three main figures;
- the paper cites an earlier Seurat/Harmony benchmark, but the converted source has no extracted bibliography or result table for it;
- architecture diagrams support component relationships, not effectiveness or causal benefit.

The resource scale is therefore a paper-reported result, while algorithmic quality and runtime are not independently verified in this workspace.

### Code-Paper Match

Overall whole-system fidelity is **low**, although four key FastIntegration behaviors have exact source support. The local code is the paper-cited FastIntegration repository at commit `ebf9b6d133628655a9a5d0fb45be2202e43aad2c`; it is related utility code, not the missing full manuscript workflow.

The included `CELLiD` function is only partial evidence for the manuscript algorithm: it keeps the top five types without the paper's `>0.6` alternative, selects 2,000 rather than 3,000 high-variance genes, and returns two labels/scores rather than the ontology-rich report (`FastIntegration/R/CELLiD.R:3-49`). The original `DISCO_manuscript` repository cited for QC, CELLiD, and CellMapper returned 404 during acquisition.

### Reproducibility

**Reproducibility rating: 2/5 (partial method code, incomplete system evidence).**

Available:

- a commit-pinned FastIntegration R package with core integration source;
- the paper markdown and all three main figures;
- explicit preprocessing, QC, CELLiD, integration, atlas, and application descriptions.

MISSING / **Not found**:

- the cited `DISCO_manuscript` repository, `QC.R`, CellMapper, and end-to-end atlas drivers;
- CELLiD reference matrices, ontology/hierarchy assets, atlas inputs/outputs, and metadata-curation artifacts;
- React/Redux frontend, Java/Spring Boot backend, MySQL/Redis schema and deployment;
- a lockfile or fully pinned environment, tests, runnable manuscript example, expected outputs, random seeds, benchmark data, and hardware/runtime logs.

The FastIntegration source also depends on multiple unexported Seurat internals, and the repository README says the package is no longer supported. The code was read statically but was not installed or executed. Reproducing the reported DISCO release or its performance is not possible from this snapshot alone.

### Bottom Line

DISCO's main contribution is the integration of data engineering, metadata/ontology harmonization, scalable expression correction, standardized cell annotation, and reference-atlas delivery into one human single-cell resource. The paper clearly specifies the conceptual workflow and reports unusually large scale for its time. The available code substantiates the central FastIntegration design, but missing manuscript/application code, data assets, and quantitative evaluation artifacts limit both whole-system verification and practical reproduction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
