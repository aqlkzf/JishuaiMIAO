---
layout: default
permalink: /paper-atlas/organoidmultiplexing-6dffd64a/
title: "OrganoidMultiplexing"
nav: false
description: "如果希望比较几十乃至上百个供体的皮层脑类器官，最直接的做法是为每个供体分别建系、培养、取样和测序。但这种方案同时放大了培养批次、人工操作和测序成本，而且不同细胞系的增殖速度并不相同：有的供体会逐渐占据混合物，有的则可能在后期几乎消失。 这篇论文的核心思想是：把多个遗传背景放进同一个实验流程，再利用天然遗传变异把每个单细胞“认领”回供体。这样，供体身份不再依赖物理分孔，而由测序读段中的 SNP 提供内部条形码。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>OrganoidMultiplexing</h1>
    <p>Multiplexing cortical brain organoids for the longitudinal dissection of developmental traits at single-cell resolution</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/GiuseppeTestaLab/organoidMultiplexing_release" target="_blank" rel="noopener noreferrer" aria-label="Open code for OrganoidMultiplexing">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Organoid Multiplexing 方法详解

### 1. 这项工作真正要解决什么问题

如果希望比较几十乃至上百个供体的皮层脑类器官，最直接的做法是为每个供体分别建系、培养、取样和测序。但这种方案同时放大了培养批次、人工操作和测序成本，而且不同细胞系的增殖速度并不相同：有的供体会逐渐占据混合物，有的则可能在后期几乎消失。

这篇论文的核心思想是：把多个遗传背景放进同一个实验流程，再利用天然遗传变异把每个单细胞“认领”回供体。这样，供体身份不再依赖物理分孔，而由测序读段中的 SNP 提供内部条形码。论文进一步追问两个问题：供体应当在类器官形成之前混合，还是在解离之后才混合；以及当不同供体生长不均衡时，一个实验最终还能可靠分析多少条细胞系。

### 2. 两种多路复用设计

#### 下游多路复用（downstream multiplexing）

各供体分别生成和培养类器官，到取样时才解离并合并细胞。优点是每个供体的培养过程彼此独立，实验逻辑直观；缺点是类器官数量、培养操作和批次仍随供体数增长，而且供体差异可能与培养容器或批次混杂。

#### 嵌合多路复用（mosaic multiplexing）

在类器官形成之前就混合不同供体来源的细胞，使多个遗传背景在同一类器官环境中共同发育。这样可以共享培养条件并显著压缩实验规模，但也引入了克隆竞争：不同供体的增殖、存活和分化能力会改变其后续比例。

两种设计最终都进入相同的单细胞建库、测序、基因型拆分和下游分析流程，因此可以直接比较“混合发生的时间点”是否系统性改变细胞组成或发育轨迹。

### 3. 如何把单细胞分配回供体

输入包括 Cell Ranger 生成的表达矩阵、每个液滴在变异位点上的参考/替代等位基因读段，以及由供体 bulk RNA-seq 构建的 VCF。论文同时运行 demuxlet、souporcell、Vireo 和 SCanSNP，再用加权共识整合它们的 singlet、doublet、低质量和未分配结果。

SCanSNP 对候选供体 \(g\) 的基本得分为：

$$
S_g=\sum_{i=1}^{n}\left(\frac{A_i a_{ig}}{t_i}+\frac{R_i r_{ig}}{T_i}\right).
$$

其中 \(A_i\) 和 \(R_i\) 是当前液滴在位点 \(i\) 上支持替代、参考等位基因的读段数，\(a_{ig}\) 和 \(r_{ig}\) 描述供体 \(g\) 的对应基因型，\(t_i\) 和 \(T_i\) 是队列层面的等位基因总量。最高分给出第一供体身份。

困难部分不只是找最高分，还要识别第二来源、doublet 和低质量液滴。论文用其他供体组训练模型预测第二身份，用“非最佳供体液滴”中的私有等位基因计数拟合负二项分布并取高分位阈值识别多供体阳性液滴，再用第一、第二身份的信号差及双成分高斯混合区分清晰与模糊分配。

这里必须保留一个复现边界：当前获得的代码仓库只消费 SCanSNP 和共识结果，没有包含 SCanSNP 核心实现及共识生成器；README 将它们指向外部仓库。

### 4. 从拆分结果到统一发育图谱

去除共识 doublet 和低质量液滴后，七个数据集进行合并、总量归一化、对数变换，并回归总 reads、线粒体比例等技术因素。高变基因按时间点、批次分别选择，并补入神经发育标志基因；这一步避免某一时间点或单一数据集主导全局特征空间。

全局分析先做 PCA，再以数据集为批次执行 Harmony。局部代码显示最多 20 次 Harmony 迭代，随后使用 15 个主成分构建 100 邻居图，并运行 Leiden 与 UMAP。细胞注释不是一次自动分类，而是结合聚类、标志基因、应激/缺氧评分及对异常群体的逐轮清理后人工整合。

图谱的关键观察是：细胞状态主要沿发育时间和细胞类型组织，不同供体及两种多路复用范式在全局嵌入中大体混合。这支持“嵌合设计不会造成强烈全局组成偏移”的结论，但不能理解为两种设计在所有分子层面完全等价。

### 5. 丰度变化与发育轨迹

#### Milo 邻域差异丰度

Milo 在细胞图上构造局部邻域，并把某一时间点与另外两个时间点的平均值比较：

$$
CT_n=T_n-\frac{T_x+T_y}{2}.
$$

本地 notebook 使用 10% 邻域抽样、\(k=20\)、\(d=20\)，建立 early、mid、late 三个对比。时间点之间存在明显富集和耗减邻域，而 mosaic 与 downstream 的主图比较没有显示显著邻域。这一“未检出差异”依赖样本量、图结构和阈值，不能被放大为生物学上的绝对相同。

#### 谱系与伪时间

流程以 PAGA 图组织细胞类型连接，删除低权重边，把连接强度转换为距离，再从 TOP2A 最丰富的增殖根群到各终末群寻找最短路径。每条谱系内部重新计算 diffusion map 和 DPT；经核对的迁移神经元 notebook 直接选择 TOP2A 最大的细胞作为 DPT 根。

为了防止“某供体细胞更多”伪装成“该供体发育更靠前”，论文只保留细胞数足够的供体，并在时间点间平衡抽样，重复随机抽样 50 次。tradeSeq 分析先裁掉 DPT 的 1% 和 99% 极端值，再以 8 个 knots 拟合基因表达随伪时间的广义加性模型，并用起点—终点检验寻找谱系驱动基因。

### 6. 等位基因特异表达

SCanSNP pileup 模式提供每个细胞的参考和替代等位基因读段层。分析按细胞类型聚合读段，对覆盖足够的位点检验替代/参考比例是否偏离 0.5，之后进行 Benjamini–Hochberg 多重校正。效应量定义为：

$$
\beta=\frac{\text{Alt reads}}{\text{Alt reads}+\text{Ref reads}}.
$$

论文采用至少 20 条读段及 \(q<0.05\) 的条件。本地 notebook 能直接追踪到聚合、二项检验、FDR 和比例计算，不过调用的是已弃用的 `scipy.stats.binom_test`，在新环境复现时应迁移到兼容接口并验证返回值语义。

### 7. 为什么“混入多少条线”不等于“回收多少条线”

论文把成像估计的类器官总体积与 Census-seq 的供体比例连接起来。若等效直径为 \(d_t\)，总细胞数按球体体积和固定密度估计：

$$
V_t=\frac{4\pi}{3}\left(\frac{d_t}{2}\right)^3,\qquad n_t=0.000767495V_t.
$$

供体 \(i\) 在时间 \(t\) 的细胞数与相邻时间段增长比分别为：

$$
n_{it}=r_{it}n_t,\qquad g_i=\frac{n_{i,t+1}}{n_{it}}.
$$

这里 \(r_{it}\) 来自 Census-seq。实测结果显示供体增长差异很大，晚期混合物可能由少数供体主导，因此模拟不能假定所有细胞系等速扩增。

经代码核对的 Monte Carlo 设置为：初始 20,000 个细胞，混合 2–20 个供体，每种设置 10,000 次循环，最终可测 100,000 个细胞；若目标稀有细胞类型占 5%，希望每个供体至少得到 100 个该类型细胞，则可反推供体所需的最低总细胞比例。模拟从经验增长率分布抽样，计算终点供体比例并统计超过阈值的供体数。论文再用 \(N=aI^b+c\) 描述投入线数 \(I\) 与平均可回收线数 \(N\) 的次线性关系。

因此，mosaic 设计的规模优势来自减少独立培养和共享处理，但其上限由克隆漂移决定。图中 100 条或 1,000 条线的时间节省是基于模型的项目规划，不是已经完成的等规模实验。

### 8. 如何理解验证结果

拆分工具使用带已知身份的合成混合物和 CellPlex 标记数据评估。图和代码均显示，高质量 singlet 对多数工具并不难；差异主要集中在不平衡混合物、doublet、低质量和未分配细胞。SCanSNP 在这些场景中表现较稳，共识策略则把多工具分歧显式化，而不是假装分歧不存在。

生物学验证形成另一条证据链：免疫荧光显示预期的神经祖细胞和神经元标志；整合图谱恢复发育状态；Milo 检出时间变化而未检出强范式变化；轨迹分析显示阶段性和部分供体相关偏移；ASE 分析说明遗传效应可能依赖细胞类型和覆盖深度。这些结果共同支持方法可用于纵向比较，但并未提供大规模新 eQTL 发现所需的统计功效。

### 9. 复现时建议的阅读与执行顺序

1. 先读仓库 README，确认 Docker 镜像、Cell Ranger 输入和 notebook 执行顺序。
2. 将外部 SCanSNP 与共识工作流固定到明确版本，生成与 notebook 期待字段一致的身份表。
3. 先复现合成混合物和 CellPlex benchmark，再进入生物学分析；否则拆分误差会传播到细胞比例、轨迹和 ASE。
4. 按时间点/批次重建 HVG、Harmony 和注释，保存每一步的 AnnData schema。
5. 分别复现 Milo、DPT/tradeSeq 与 ASE，并核对论文阈值和 notebook 中更严格的展示过滤条件。
6. 最后连接成像与 Census-seq，重新估计增长率分布并进行敏感性分析，尤其检查细胞密度、测序容量、5% 稀有类型和 100-cell 阈值。

### 10. 当前证据边界

可以直接验证多数下游分析参数及计算路径，但缺少转换后的补充方法、源数据表、完整原始/中间输入，以及本地 SCanSNP/共识实现。因此最合理的结论是：方法与下游分析逻辑可追踪，代码—论文匹配度中等，但当前材料还不是一键式端到端复现包。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Organoid multiplexing for longitudinal single-cell studies

### Paper at a glance

- **Paper:** *Multiplexing cortical brain organoids for the longitudinal dissection of developmental traits at single-cell resolution*
- **DOI:** `10.1038/s41592-024-02555-5`
- **Journal / year:** *Nature Methods*, 2025
- **Primary contribution:** two donor-multiplexing designs for cortical brain organoids, combined with genotype-based single-cell demultiplexing, developmental trajectory analysis, allele-specific analysis, and a model of experimental scalability.

### Problem

Longitudinal organoid experiments are expensive and vulnerable to line-to-line culture variability. Growing every donor separately increases handling and batch burden, but mixing donors creates a second problem: each sequenced cell must be assigned back to its genetic source. Existing demultiplexing tools can disagree most strongly on doublets, low-quality cells, and imbalanced mixtures—the same conditions that become important when donor lines expand at different rates.

### Proposed approach

The study evaluates two designs:

1. **Downstream multiplexing:** donor-specific organoids are cultured separately and pooled after dissociation.
2. **Mosaic multiplexing:** donor cells are mixed before organoid formation, allowing multiple genotypes to develop in a shared organoid environment.

Cells are assigned to donors using genotype-aware tools, including the authors' SCanSNP method, and a weighted consensus across SCanSNP, demuxlet, Vireo, and souporcell. The assigned cells are then integrated into a developmental atlas using Scanpy/Harmony, tested for neighborhood abundance changes with Milo, ordered along diffusion-pseudotime trajectories, modeled with tradeSeq, and examined for allele-specific expression. Imaging and Census-seq measurements are combined with Monte Carlo simulation to estimate how unequal growth limits the number of recoverable donor lines and affects experimental duration.

### Main findings

- Both multiplexing designs yield cortical-organoid cell states and developmental trajectories dominated more strongly by time and cell identity than by multiplexing paradigm.
- SCanSNP and the multi-tool consensus handle difficult assignment categories more plausibly than several individual tools in the displayed synthetic and CellPlex benchmarks, particularly for doublets and imbalanced mixtures.
- Integrated single-cell analyses recover expected progenitor, neuronal, and glial populations, time-associated abundance changes, lineage trajectories, genotype-associated shifts, and cell-type-dependent allele-specific signals.
- Donor lines show marked growth heterogeneity. Mixtures can drift far from their initial balance, so increasing the starting number of lines produces a sublinear increase in lines recoverable at adequate cell depth.
- Under the paper's growth and sampling assumptions, mosaic multiplexing substantially reduces projected time relative to maintaining downstream donor-specific organoids. These timing gains are simulations rather than observed end-to-end trials at 100- or 1,000-line scale.

### Evidence and implementation match

The acquired repository is a paper-linked, notebook-first analysis release. It contains direct implementation evidence for:

- harmonizing outputs from multiple demultiplexing tools and measuring synthetic assignment accuracy;
- Harmony integration and neighborhood/Leiden/UMAP construction;
- Milo neighborhood differential-abundance testing;
- diffusion pseudotime, lineage distributions, and tradeSeq trajectory tests;
- per-cell-type allele aggregation, binomial testing, false-discovery correction, and allelic proportion calculation;
- imaging-derived growth calculations and the 2–20-line Monte Carlo recoverability experiment.

The match is **medium fidelity**, not a complete executable reproduction. The central SCanSNP engine and consensus-call generator are referenced as external repositories and are not present in the acquired `code source`. The repository relies heavily on large notebooks and paper-specific intermediate files, and the local acquisition lacks converted supplementary methods and source-data tables.

### Reproducibility assessment

**Rating: 3/5 (moderate).** Strengths include a public paper-linked repository at a pinned commit, explicit notebook ordering, a named Docker image, public data accessions, and direct code for most downstream analyses. Reproduction remains constrained by external core-demultiplexing implementations, absent raw/intermediate inputs in this workspace, notebook-scale execution state, and missing supplementary Markdown. The materials are strong enough to trace the analysis logic and many parameters, but not to rerun the complete study from the current workspace alone.

### Practical takeaway

The paper's most reusable idea is not simply pooling organoids. It is the combination of early donor mixing, genetic reassignment of individual cells, consensus-aware quality control, and explicit modeling of unequal donor expansion. That combination converts organoid multiplexing from a batching convenience into a framework for longitudinal population-scale developmental studies—provided that clonal imbalance and assignment uncertainty are measured rather than assumed away.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
