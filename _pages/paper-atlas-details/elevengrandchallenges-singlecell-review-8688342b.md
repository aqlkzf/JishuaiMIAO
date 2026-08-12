---
layout: default
permalink: /paper-atlas/elevengrandchallenges-singlecell-review-8688342b/
title: "ElevenGrandChallenges_singlecell_review"
nav: false
description: "这篇 Genome Biology 2020 文章不是提出一个新的算法，也不是发布一个软件包或标准 benchmark。它是一篇单细胞数据科学的路线图/综述型文章。摘要明确说，作者梳理了 11 个未来关键挑战，对每个挑战给出研究动机、已有工作和开放问题 。 因此，这里的“方法”不是某个可运行模型，而是一套问题分类框架： 单细胞测序已经从小规模实验进入大规模数据阶段。"
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
      <span>Representation Models</span>
      <span>Genome Biology · 2020</span>
    </div>
    <h1>ElevenGrandChallenges_singlecell_review</h1>
    <p>Eleven grand challenges in single-cell data science</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1186/S13059-020-1926-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 中文方法解读

### 这篇文章到底是什么

这篇 Genome Biology 2020 文章不是提出一个新的算法，也不是发布一个软件包或标准 benchmark。它是一篇单细胞数据科学的路线图/综述型文章。摘要明确说，作者梳理了 11 个未来关键挑战，对每个挑战给出研究动机、已有工作和开放问题 (`paper.md:9-12`)。

因此，这里的“方法”不是某个可运行模型，而是一套问题分类框架：

```text
单细胞测量数据
  -> 更细分辨率、更高不确定性、更高维度、更多模态
  -> 11 个挑战
       I-V: 单细胞转录组
       VI: 单细胞基因组
       VII-IX: 单细胞系统发育/肿瘤演化
       X-XI: 数据整合与工具验证
  -> 需要新的统计模型、可扩展算法、整合假设和 benchmark 基础设施
```

### 为什么会有这些挑战

单细胞测序已经从小规模实验进入大规模数据阶段。文章指出，微流控、组合索引和测序成本下降让一次实验测量几十万甚至上百万个细胞成为可能 (`paper.md:39`)。这带来两个直接后果：

1. 每个细胞可用的生物材料很少，所以测量噪声、缺失和偏差更严重 (`paper.md:45`, `paper.md:86-95`)。
2. 细胞数、特征数、实验类型、空间/时间信息和多组学信息同时增加，普通分析流程会遇到维度、规模和整合问题 (`paper.md:98-113`)。

文章把这些问题组织成三个反复出现的主题：分辨率、不确定性、扩展与整合。

### 三个贯穿全文的主题

#### 1. 分辨率不是固定的

单细胞数据既可以看成组织级别的图，也可以看成细胞类型图，还可以看成单细胞连续状态和轨迹。文章要求细胞地图能表示组织结构、连续状态、可变粒度和生物注释 (`paper.md:69-75`)。Fig. 1 的图像也正是从 tissue、cell types 到 single cells 的多层表示 (`figure_01.png`; `paper.md:78-83`)。

计算含义：不能只做一次固定聚类就结束。方法需要支持层级图、流形、轨迹、连续状态和可缩放的 atlas。

#### 2. 不确定性必须进入模型

单细胞实验的输入材料少，信号比 bulk 测序更不稳定。文章说，像 SNV calling 这种在 bulk 数据里相对常规的任务，在单细胞数据中也需要更谨慎的统计处理 (`paper.md:86-90`)。理想工具应该量化实验误差和偏差，并把这些不确定性传递到下游结果 (`paper.md:95`)。

计算含义：单细胞算法不能只输出一个硬标签或一个点估计。更好的方法应输出置信度、后验分布、误差模型或可以传播的不确定性。

#### 3. 规模与整合会持续变难

文章强调，更多细胞、更多特征、更宽的测量覆盖会形成持续的“维度灾难” (`paper.md:101-110`)。同时，多模态、空间和时间采样会迫使方法把 RNA、DNA、蛋白、甲基化、位置、时间点、个体和物种等信息连接起来 (`paper.md:113`)。

计算含义：单细胞数据科学的难点不只是“矩阵更大”，而是需要在高维、缺失、多批次、多模态条件下建立可解释、可检验的连接关系。

### 11 个挑战怎么理解

#### I. scRNA-seq 稀疏性和 imputation

scRNA-seq 中有大量 0，但文章提醒不要把所有 0 都简单叫作 dropout，因为有些是技术原因导致的未检测，有些是真正没有表达 (`paper.md:119-125`)。作者认为应优先使用能直接建模稀疏性和噪声的统计模型；当下游算法无法处理稀疏数据时，才考虑 imputation (`paper.md:153-156`)。

文章把 imputation 分成模型型、平滑型、重构型和外部参考型 (`paper.md:156-177`)。Fig. 2 显示 observed points 通过 denoising/imputation manifold 向估计流形移动 (`figure_02.png`; `paper.md:128-133`)。关键风险是循环性：如果只用同一个数据集内部的信息补值，可能放大假信号，造成差异表达或基因网络推断中的假阳性 (`paper.md:183-195`)。

#### II. 更灵活的差异表达框架

单细胞差异分析不应只比较平均表达。Fig. 3 把 mean、variability 和 pseudotime 三类差异分开显示 (`figure_03.png`; `paper.md:136-141`)。文章指出，当前很多方法仍假设待比较细胞群已知，但真实流程通常先聚类或注释细胞，再做差异分析，这会带来细胞类型分配不确定性和“重复使用数据”的问题 (`paper.md:207-213`)。

计算含义：需要能处理样本内/样本间变异、伪时间变化、分布变化、混杂因素和细胞分配不确定性的统计框架。

#### III. 把单细胞映射到参考 atlas

细胞类型和状态分类是很多下游分析的基础。没有 atlas 时，研究者常用无监督聚类，再人工标注；这既耗时，也限制可重复性 (`paper.md:222-231`)。atlas 的目标是提供稳定参考，让新细胞能映射到不同分辨率的细胞类型、状态和过渡状态上 (`paper.md:231-246`)。

计算含义：atlas mapping 不只是分类器问题。它还要支持多分辨率、不确定性、规模扩展，以及 RNA 之外的 DNA、蛋白等测量类型 (`paper.md:246-249`)。

#### IV. 泛化 trajectory inference

文章把 trajectory 定义为细胞在连续状态空间中可能经历的路径，pseudotime 是由这条路径诱导出的顺序 (`paper.md:252-255`)。常见方法从 gene-by-cell count matrix 出发，经过特征选择或降维，再用聚类、最小生成树、图拟合、随机游走、扩散、optimal transport 或概率潜变量模型推断轨迹 (`paper.md:258`)。

难点在于把 trajectory 推断推广到转录组之外。甲基化、染色质可及性、蛋白组等数据的特征定义、细胞数、稀疏性和距离度量都不同 (`paper.md:261-267`)。

#### V. 空间分辨测量中的模式发现

空间转录组或空间蛋白组会保留细胞或转录本的空间坐标，等于增加了一类要整合的特征空间 (`paper.md:270-276`)。文章指出，已有方法可以按表达聚类或做空间差异表达，但当时还没有方法能在整合空间和表达信息时编码组织异质性的先验知识 (`paper.md:279-285`)。

计算含义：空间方法需要同时利用表达、坐标、组织结构先验、显微图像中的形态信息和表达不确定性。

#### VI. scDNA-seq 中的错误和缺失

scDNA-seq 的目标是以单细胞分辨率追踪体细胞演化，但 whole-genome amplification 会引入错误和偏差 (`paper.md:305-311`)。文章区分了 allele imbalance、allele dropout 和 site dropout 三类主要问题 (`paper.md:330-333`)。Fig. 5 用谱系树和叶节点突变 profile 中的问号展示了缺失和不确定观测 (`figure_05.png`; `paper.md:314-319`)。

计算含义：variant caller 需要显式误差模型、不确定性估计、跨细胞信息整合，甚至把 mutation calling 和 lineage tree inference 联合起来做 (`paper.md:333-342`)。

#### VII. 系统发育模型的规模扩展

肿瘤系统发育模型要面对越来越多细胞和越来越多 genomic sites (`paper.md:369-372`)。文章指出，树拓扑搜索空间会随 taxa 数量超指数增长，并且大多数 scoring criteria 下的系统发育推断是 NP-hard；当 MSA 超过约 20 个单细胞时，穷举搜索已不可行 (`paper.md:375`)。

计算含义：这个挑战的核心是可扩展搜索、启发式优化、并行化、误差建模和位点选择，而不是简单地把矩阵读入内存。

#### VIII. 把多种变异纳入系统发育模型

当 SNV、indel、CNV 和结构变异都可测时，肿瘤演化模型应尽量整合多类信号 (`paper.md:381-384`)。但文章也指出 scDNA-seq indel caller 当时尚不可用，CNV-aware phylogeny 又会遇到机制和计算复杂度问题 (`paper.md:387-399`)。

计算含义：更完整的模型不一定总是更好。文章明确提醒，多现象整合会增加计算成本，需要判断哪些现象真的会影响最终树结构，哪些轻量模型足以回答特定问题 (`paper.md:396-402`)。

#### IX. 整合模型推断肿瘤异质性的群体遗传参数

Fig. 4 展示了肿瘤从发生、取样、治疗到转移的时空演化，包含 subclone competition、immune detection、therapy、metastasis、mutation types 和 theoretical subclone phylogeny (`figure_04.png`; `paper.md:294-305`)。文章希望估计突变和突变组合的 fitness，以及 mutation、birth、death rates 等参数 (`paper.md:405-411`)。

计算含义：需要把系统发育、群体遗传学、空间位置、时间点、微环境、治疗压力和单细胞误差模型结合起来 (`paper.md:420-450`)。

#### X. 跨样本、实验和测量类型的数据整合

文章说，整合的核心是用生物学上有意义的方式连接不同来源的数据 (`paper.md:456-459`)。Fig. 6 把整合分成 1S、+S、+X+S、+M1C、+M+C 和 +all 六种场景 (`figure_06.png`; `paper.md:322-327`)。

计算含义：不同整合场景对应不同假设。跨样本可能需要 batch correction；跨实验可能需要 reference atlas；同一细胞多模态要建模模态间依赖；不同细胞多模态要证明细胞之间如何匹配才合理 (`paper.md:462-501`)。

#### XI. 工具验证和 benchmarking

文章认为分析工具应产生预期结果，并对测序噪声和技术偏差保持鲁棒 (`paper.md:504-507`)。但 ground-truth benchmark 数据很少，尤其是演化过程相关的单细胞群体数据 (`paper.md:510-513`)。模拟数据便宜且可控，但模拟器本身也要能真实反映生物过程和技术误差 (`paper.md:516-525`)。

计算含义：benchmark 不是最后一步附加评估，而是单细胞方法学本身的基础设施。文章最终建议建立社区支持的 benchmark 平台，包含模拟数据、真实 ground truth 和统一指标 (`paper.md:531-534`)。

### 图像证据如何支持全文

- Fig. 1 支持“多分辨率细胞地图”。
- Fig. 2 支持“稀疏数据的 denoising/imputation 不是直接恢复真值”。
- Fig. 3 支持“差异分析目标不止平均表达”。
- Fig. 4 支持“肿瘤演化需要时间、空间、治疗和 clone 信息整合”。
- Fig. 5 支持“scDNA-seq lineage inference 受缺失和 amplification bias 影响”。
- Fig. 6 支持“数据整合有多种不同问题形态”。

### 本工作区的可复现性状态

- `MODE=paper-only`，没有代码仓库。
- `doc_code.md` 按流程跳过，不能推断代码实现。
- `SUPP_MD=none`。文章只链接了一个 Additional file 1 DOCX，内容说明为 review history (`paper.md:1142-1148`)。
- `paper.md:1-1200` 中没有发现 display equations 或 formal optimization objectives。
- 六张本地图像已直接检查，并在 `figure_analysis.md` 中记录。

这篇文章最适合被当成单细胞数据科学的问题地图：它告诉研究者哪些地方需要更好的统计假设、可扩展算法、跨模态整合和系统 benchmark，而不是提供一个可以直接运行的新模型。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### What This Paper Is

**Eleven grand challenges in single-cell data science** is a Genome Biology 2020 review/perspective article that organizes open computational problems in single-cell data science. It is not a new algorithm or software release. The abstract says the paper outlines eleven challenges, reviews prior work, and formulates open problems for researchers, newcomers, and students (`paper.md:9-12`).

### Problem

Single-cell sequencing turned biology into a high-resolution, high-volume data problem. The paper points to microfluidics, combinatorial indexing, and falling sequencing costs as enabling experiments with hundreds of thousands to millions of cells (`paper.md:39`). The resulting data need methods that are computationally efficient and statistically sound (`paper.md:42`), but single-cell assays also increase measurement uncertainty, matrix dimensionality, and modality complexity (`paper.md:45`).

### Core Roadmap

The paper's central contribution is a challenge taxonomy rather than a method pipeline:

| Area | Challenges | Core issue |
|---|---:|---|
| Recurring themes | prelude | resolution, uncertainty, scaling, integration (`paper.md:54-113`) |
| Transcriptomics | I-V | sparsity, differential patterns, atlas mapping, trajectories, spatial measurements (`paper.md:116-287`) |
| Genomics | VI | errors and missing data in scDNA-seq variant identification (`paper.md:288-353`) |
| Phylogenomics | VII-IX | scalable tumor phylogenies, multi-variation models, population-genetic parameter inference (`paper.md:354-452`) |
| Overarching | X-XI | cross-sample/multi-modal integration and benchmarking (`paper.md:453-536`) |

### Main Technical Ideas

The paper's computational message is that single-cell methods need to handle three recurring constraints:

1. **Resolution is variable.** Cell-state maps should support zooming from tissues and cell types to continuous single-cell trajectories and intermediate states (`paper.md:69-75`). Fig. 1 visualizes this as graph and manifold representations (`figure_01.png`; caption `paper.md:78-83`).
2. **Uncertainty must be quantified.** Single-cell measurements start from little material, so routine tasks such as SNV calling and expression analysis need error-aware statistical treatment (`paper.md:86-95`).
3. **Scaling and integration are unavoidable.** More cells, more modalities, spatial/temporal context, and broader feature spaces create a persistent curse-of-dimensionality and integration problem (`paper.md:98-113`).

### Challenge Highlights

- **Sparsity and imputation**: scRNA-seq zeros can be technical or biological, so the paper prefers explicit sparse count models where available and treats imputation as a risky fallback when downstream methods cannot handle sparse data (`paper.md:119-156`). Fig. 2 shows denoising/imputation as movement toward an estimated manifold, not direct recovery of truth (`figure_02.png`; `paper.md:128-133`).
- **Differential expression**: single-cell data expose differences in mean, variability, distributions, and pseudotime dynamics, but standard pipelines often ignore clustering/assignment uncertainty (`paper.md:204-216`). Fig. 3 illustrates mean, variability, and pseudotime targets (`figure_03.png`; `paper.md:136-141`).
- **Reference atlases and trajectories**: atlas mapping should reduce manual annotation and support stable multi-resolution references (`paper.md:222-249`), while trajectory inference must generalize beyond transcriptomics to other modalities with different feature definitions and sparsity (`paper.md:252-267`).
- **Spatial and tumor modeling**: spatial assays add coordinates and morphology as features (`paper.md:270-285`); tumor scDNA-seq adds variant calling, clone reconstruction, spatial sampling, selection, and treatment dynamics (`paper.md:294-305`, `paper.md:405-450`).
- **Integration and benchmarking**: Fig. 6 and Challenge X separate integration into six scenarios across samples, experiments, modalities, and references (`paper.md:322-327`, `paper.md:456-477`). Challenge XI calls for realistic simulators, curated ground truth, robust metrics, and community benchmarking platforms (`paper.md:504-536`).

### Evaluation and Evidence

There is no original benchmark, no reported new dataset, and no algorithmic performance table. The paper supports its claims through a structured review of prior methods, conceptual figures, and tables listing existing approaches. The most concrete evaluation agenda appears in Challenge XI: tools should pass quality-control tests, be robust to sequencing noise and technological biases, and be compared against benchmark data or simulations with known ground truth (`paper.md:504-528`).

### Reproducibility and Workspace Status

- **Mode**: paper-only.
- **Code**: `MISSING`; no paper-owned code repository was acquired, and `doc_code.md` is intentionally skipped.
- **Supplement**: `MISSING` as local markdown. The article links an Additional file 1 DOCX described as review history (`paper.md:1142-1148`), but this workspace has `SUPP_MD=none`.
- **Figures**: six local figures were inspected and analyzed in `figure_analysis.md`.
- **Equations**: `Not found`; no display equations or formal optimization objectives were found in `paper.md:1-1200`.

For researchers, this paper is most useful as a map of open methodological problems: it names where single-cell data science needs better statistical models, scalable algorithms, data integration assumptions, and benchmark infrastructure.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
