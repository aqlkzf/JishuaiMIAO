---
layout: default
permalink: /paper-atlas/multimodal-lineage-tracing-review-8c032431/
title: "multimodal_lineage_tracing_review"
nav: false
description: "多模态谱系追踪的价值在于给终点组学加入可遗传的历史约束；可靠分析必须先匹配数据类型与问题，再把条形码缺失、树不确定性、祖先不可观测和模型假设一路传播到命运与基因程序结论，而不是把一棵推断树当作因果真相。"
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Nature Reviews Genetics · 2026</span>
    </div>
    <h1>multimodal_lineage_tracing_review</h1>
    <p>Computational approaches for multimodal lineage tracing</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41576-026-00969-9" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 多模态谱系追踪计算方法：如何把“祖先关系”与“当前状态”放进同一个分析框架

### 1. 这篇综述的真正主线

多模态谱系追踪同时测量两种本质不同的信息：遗传或人工条形码记录细胞“从哪里来”，转录组、染色质、甲基化或空间测量描述细胞“现在是什么状态”。综述的核心不是罗列软件，而是说明这两类信息怎样支持四级推断：

1. 从遗传标记恢复克隆或单细胞系统树；
2. 将谱系与分子状态结合，估计命运方向、转移率、增长和命运偏倚；
3. 从叶节点反推不可见祖先的表达或命运分布；
4. 找到与谱系或终末命运相关的基因程序。

每一级都以前一级为输入，因此树拓扑、分支长度、条形码缺失或跨模态匹配错误会向下游传播。不能把“有谱系信息”理解为自动拥有真实时间序列或因果机制。

### 2. 先分清数据：自然/人工，系统树/克隆

图 1 给出最实用的四象限。

#### 2.1 自然标记的回顾性追踪

SNV、CNV、线粒体变异、微卫星和甲基化表突变在细胞分裂中积累，可用于原生人体组织和肿瘤。它们不需预先工程化，但常见问题是变异稀少、覆盖不足、等位基因脱落和 CNV 覆盖旧事件。自然标记可以支持细粒度系统树，也可以只支持克隆划分，取决于信息量。

#### 2.2 人工标记的前瞻性追踪

CRISPR 等动态条形码在发育过程中持续编辑，字符状态的嵌套关系可支持树重建。静态病毒条形码通常只标识起始克隆，适合比较多个时间点的克隆组成和命运分布，但单次静态标签不告诉克隆内部的分叉顺序。

第一条方法选择原则因此是：若只有 clone ID，不应使用必须依赖内部节点和分支长度的“完整系统树”解释；若有动态条形码，也要先判断编辑是否饱和、是否存在同形突变和缺失。

### 3. 四个不可绕过的计算难点

#### 3.1 大规模树搜索

细胞数增加时可能树拓扑超指数增长，寻找全局最优树通常不可行。邻接法和距离法速度快，却压缩了每个字符的编辑过程；最大似然或贝叶斯模型能表达错误和时间，但更昂贵；简约法、贪心法、整数线性规划和分治法在可扩展性与最优性之间折中。

#### 3.2 离散树与连续状态的结构错配

谱系是离散、低维、树状的历史，组学是连续、高维、带噪的终点快照。相邻亲属可以因环境而进入不同状态，不同支系也可能收敛到相似状态。因此“表达相似”不能无条件修正树，“同克隆”也不能无条件当作同状态。

#### 3.3 祖先状态不可观测

单细胞测序通常摧毁样本，只测到树叶。内部节点表达、调控和命运潜能是模型外推。祖先重建应报告后验不确定性和对候选树的敏感性，而不应只输出一张看似确定的祖先表达热图。

#### 3.4 缺失、噪声与抽样不足

条形码脱落、等位基因脱落、测序错误、编辑热点、批次效应和稀有克隆漏采会同时影响树和状态。许多下游方法把一棵推断树当作固定真值，容易低估不确定性。稳妥分析应在 bootstrap 树、候选拓扑或不同缺失模型上重复下游结论。

### 4. 第一类任务：重建系统树

#### 4.1 自然变异方法

SCIPhI、SIEVE、CellPhy、ScisTree 以 SNV 为主；SCICoNE、MEDICC2 面向 CNV；SCARLET、COMPASS 联合 SNV 与 CNV；MethylTree 利用高频表突变。选择方法时，关键不是哪个算法“更新”，而是输入变异类别、错误模型、倍增/CNV 事件和所需输出是否匹配。

#### 4.2 动态条形码方法

图 2 从原始编辑条形码到字符矩阵，再分成三条路线：

- 距离法先计算细胞间距离，再聚类成树；
- 字符法直接最小化编辑代价或最大化似然；
- 谱系—转录组联合方法用表达消解相同条形码的歧义。

Cassiopeia 用贪心或整数线性规划搜索低简约代价树，并对不可逆编辑、回变或同形突变设置不同代价。STARTLE 对每个位点的重复独立编辑施加强约束。FRACTAL 用分治和分布式计算扩展到极大树。LAML、ConvexML、TiDeTree 进一步估计分支长度、时间或种群参数。

联合方法 LinTIMaT、LinRace 可以用转录组细化条形码无法区分的分支，但表达收敛会把无亲缘细胞拉近。表达信息应作为有模型边界的辅助证据，而不是覆盖条形码历史。

### 5. 第二类任务：定量命运图谱

综述图 3 把方法分为动态模型、优化模型、祖先重建和联合表征学习。四类输出不同，不能只用“trajectory method”概括。

#### 5.1 动态模型：参数可解释，但假设更重

ICE-FASE 从细胞类型标注树估计状态转移方向和时间，依赖进行性潜能限制。PATH/PATHpro、KCA 用 Markov 过程估转移率；Markov 假设意味着未来只依赖当前状态。PhyloVelo 在树约束下用单调表达基因估计速度，避免完全依赖剪接。CLADES 将 NeuralODE 与 Gillespie 过程结合，用纵向静态克隆推断克隆特异的分化与增长。

这类方法的优势是速率、方向和增长参数有生物含义；风险是平衡、Markov、单调、均匀增长、树时间或可辨识性假设不成立。连续向量或转移率是模型估计，不是直接观察的细胞移动。

#### 5.2 优化模型：寻找最一致的流，而非完整动力学

Carta 在不可逆转移和潜能收缩约束下平衡转移图复杂度与树上未观察转移。TROUPE 加入 multi-type Yule 增殖过程。CoSpar 以转移稀疏和局部相干约束静态克隆的命运；scTrace+ 加入多种转录相似性。LineageOT 和 moslin 用最优传输连接时间点，依赖质量守恒、代价函数和渐变状态假设。

优化目标给出的是在约束下最合适的耦合或流。不同正则化、距离、增殖校正会改变解；最优传输耦合也不是逐细胞真实祖先—后代配对。

#### 5.3 祖先状态重建：回答“过去可能是什么”

TreeVAE 在树上让潜在状态平滑演化，并生成内部节点表达及不确定性。TarCA 用概率祖先状态/共祖逻辑估计祖细胞数和后代命运分布。ICE-FASE 也可估祖先命运层级。输出最好解释为给定树、模型和叶节点数据的条件分布，而非复原出的真实祖细胞。

#### 5.4 联合表征学习：灵活，但机制性最弱

PORCELAN、ClonoCluster、LineageVAE、Deep Lineage、LCL、DestinyNet 学习同时保留谱系和表达信息的嵌入，用于聚类、命运/表达预测或调控因子评分。深度模型能捕捉非线性和跨模态模式，却需要更多数据，也可能把批次和克隆结构编码成捷径。预测准确不等于解释了命运原因。

### 6. 第三类任务：寻找谱系相关基因程序

图 4 区分两个常被混淆的问题。

- 谱系相关程序：哪些基因在特定系统树支系内持续高表达？Hotspot 可用树邻接寻找自相关模块，PhyloVision 用于交互查看，LMA 与随机树比较谱系 motif，PORCELAN/LCL/PATH 等寻找谱系—表达耦合。
- 命运相关程序：哪些基因在特定终末命运或命运偏倚出现前表达？CoSpar、PhyloVelo、Clonotrace、TarCA、DestinyNet 等从转移、速度、祖先或预测模型中评分。

支系富集可能反映遗传背景或稳定记忆，命运富集可能出现在多个独立支系；两者都只是关联。要称为 fate-determining regulator，还需要干预实验或其他因果证据。

### 7. 如何实际选方法

图 5 的决策树可压缩成三个问题。

1. 输入是动态系统树、静态 clone ID，还是只有自然变异？先选择匹配的重建或克隆工具。
2. 是单时间点还是多时间点？单快照更依赖树上祖先/动态假设，多时间点静态克隆适合 OT、CoSpar、CLADES 等群体流方法。
3. 目标是树、转移率、命运偏倚、祖先表达、基因程序还是预测？不要用一个输出替代另一个。

同功能方法之间再比较：是否需要机制可解释参数，是否允许反向转移，是否显式建模增殖/抽样，能否传播树不确定性，数据量是否足以训练深度模型，以及软件/硬件能否复现。

### 8. 五张图的证据链

- 图 1：定义自然/人工 × 系统树/克隆四种数据制度。
- 图 2：解释动态条形码树重建，以及表达辅助细化树的机会和风险。
- 图 3：把命运映射分成动态、优化、祖先重建和联合学习四类。
- 图 4：分开谱系相关与命运相关基因程序。
- 图 5：把数据类型、采样设计和目标串成方法选择流程。

五张主图已从 PDF 页面和局部裁图逐一视觉检查。工作区没有独立补充文件；OCR 抽取了 9 个局部图像，部分图被拆成多个 panel，`figure_pages/` 的整页渲染用于核对图 1、4、5 的完整布局。表 1 的 OCR 存在排版噪声，因此方法名和分类以正文、表格及参考文献交叉核对，不能把 OCR 乱码当作原文结论。

### 9. 基准怎样做才不自证循环

模拟数据提供完整树、转移和表达真值，但只检验模拟器允许的机制。PhyloVelo/TedSim 等模拟器适合系统控制噪声与缺失，却可能偏爱共享假设的方法。真实数据更可信但真值不完整；秀丽隐杆线虫胚胎具有高分辨率谱系与转录图谱，是重要基准，鼠胚等谱系数据可作外部验证。

一个分层验证方案应先评估条形码恢复、树拓扑和分支支持，再在多棵可接受树上重复命运分析，随后用匹配缺失率和抽样瓶颈的模拟测试，最后用已知发育顺序、空间位置或遗传扰动验证生物结论。只报告下游预测 AUC 而不检查树，无法定位错误来源。

### 10. 综述的未来判断与边界

空间谱系追踪把祖先、状态和微环境放进同一组织坐标；多尺度模型希望连接基因调控、细胞命运和形态发生。综述也提出用谱系的历史约束增强 foundation model/virtual cell，但明确指出当前深度模型主要学习相关性，外推和因果解释仍不足。“AI virtual cell”在本文中是方向，不是已实现能力。

对人体材料，自然 mtDNA、甲基化和体细胞嵌合是重要桥梁，但分辨率和技术偏差仍限制临床普适性。未来算法需要同时处理百万细胞可扩展性、GPU/内存成本、欠采样校正、深层多组学和不同时间尺度的记录。

### 11. 最安全的一句话总结

多模态谱系追踪的价值在于给终点组学加入可遗传的历史约束；可靠分析必须先匹配数据类型与问题，再把条形码缺失、树不确定性、祖先不可观测和模型假设一路传播到命运与基因程序结论，而不是把一棵推断树当作因果真相。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Computational approaches for multimodal lineage tracing

### Review Scope

This Nature Reviews Genetics article surveys computational methods for analysing multimodal lineage-tracing data, where heritable lineage records are measured together with single-cell transcriptomic, epigenomic or spatial profiles. The review targets researchers who need to choose methods for lineage reconstruction, fate mapping, ancestral-state inference and lineage-associated gene programme discovery. Its coverage is broad rather than limited to one experimental system: it discusses natural somatic variants, synthetic CRISPR or static barcodes, single-snapshot and multi-timepoint designs, and emerging spatial lineage-tracing data.

The review discusses roughly 45 named computational methods or method families. I include the major named methods from the paper's tables and text below; classical background algorithms such as neighbour joining, maximum likelihood, UShER and generic bootstrap tests are treated as context rather than as application-specific methods.

### Field Landscape

Lineage tracing has moved from observing cells or labelling clones to recording heritable molecular marks that can be read out together with single-cell molecular states. The important computational shift is that lineage now provides historical information, whereas single-cell omics gives endpoint state snapshots. This creates a richer but harder inference problem: one must combine discrete, tree-structured ancestry with continuous, high-dimensional molecular profiles.

The field has evolved through three broad stages. First, natural somatic markers such as SNVs, CNVs, mtDNA variants, microsatellites and methylation epimutations enabled retrospective reconstruction of clonal histories, especially in human tissues and cancer. Second, synthetic lineage recorders, especially CRISPR-Cas9 evolving barcodes and lentiviral static barcodes, increased experimental control and scale. Third, multimodal single-cell profiling linked these lineage records to transcriptomic, chromatin, methylation and spatial states, making it possible to infer fate bias, growth, transition rates, ancestral molecular states and gene programmes.

The current bottleneck is no longer simply obtaining lineage labels. The harder problems are uncertainty-aware tree reconstruction, modality alignment, ancestral-state inference, benchmarking, and distinguishing predictive correlations from mechanistic or causal fate regulators.

### Method Taxonomy

The review organizes methods by analytical objective.

1. Phylogenetic reconstruction: infer clonal or tree relationships from natural variants, synthetic evolving barcodes, expression data, or barcode-plus-expression joint models.
2. Quantitative fate mapping: estimate transition directions, rates, fate bias, clone growth and population flow from lineage-resolved molecular data.
3. Ancestral state reconstruction: infer unobserved internal-node cell states, ancestral expression or progenitor fate distributions.
4. Lineage-transcriptome integrative learning: learn embeddings or deep models that jointly encode lineage and transcriptome structure for prediction or representation.
5. Gene programme discovery: identify genes or modules associated with lineage topology, fate outcomes, or inferred regulatory programmes.
6. Benchmarking and validation: evaluate models using simulations, real lineage-resolved datasets, tree-support metrics, and biological ground truth.

### Method Comparison

| Method | Year | Journal | Category | Key Innovation | Limitations | Data Types |
|---|---:|---|---|---|---|---|
| SCIPhI | 2018 | Nature Communications | Natural-variant phylogeny | Joint mutation calling and phylogeny inference | SNV coverage/dropout sensitivity | scDNA-seq SNVs |
| SIEVE | 2022 | Genome Biology | Natural-variant phylogeny | Joint SNV and cell-tree inference | Requires informative SNVs | scDNA-seq SNVs |
| CellPhy | 2022 | Genome Biology | Natural-variant phylogeny | Probabilistic scDNA phylogeny | Scaling and sequencing-error dependence | scDNA-seq SNVs |
| ScisTree | 2020 | Bioinformatics | Natural-variant phylogeny | Maximum-likelihood perfect phylogeny | Perfect-phylogeny assumptions can break | Noisy single-cell genotypes |
| SCICoNE | 2025 | Bioinformatics | CNV phylogeny | Copy-number event history reconstruction | Coarse CNV resolution | scDNA/scRNA CNVs |
| MEDICC2 | 2022 | Genome Biology | CNV phylogeny | Copy-number phylogenies with genome-doubling awareness | Needs reliable CNV profiles | CNV data |
| SCARLET | 2020 | Cell Systems | SNV+CNV phylogeny | Copy-number-constrained mutation-loss inference | Cancer-focused assumptions | SNV+CNV |
| COMPASS | 2023 | Nature Communications | SNV+CNV phylogeny | Joint mutation and copy-number phylogeny | Amplicon/data design dependence | Amplicon scDNA |
| MethylTree | 2025 | Nature Methods | Epimutation phylogeny | Frequent DNA methylation epimutations as lineage markers | Epimutation model dependence | Single-cell methylation |
| GAPML | 2021 | Annals of Applied Statistics | Synthetic-barcode phylogeny | Maximum-likelihood CRISPR lineage trees | Model and scale constraints | Evolving barcodes |
| DCLEAR | 2022 | BMC Bioinformatics | Synthetic-barcode phylogeny | Distance-based reconstruction | Distance summaries may lose edit process detail | Evolving barcodes |
| ConvexML | 2026 | Systematic Biology | Synthetic-barcode phylogeny | Fast branch-length estimation under irreversible mutations | Depends on fixed topology/irreversibility assumptions | Evolving barcodes |
| LAML | 2025 | Genome Biology | Synthetic-barcode phylogeny | Time-scaled trees with mixed missing data | Requires statistical model fit | Evolving barcodes |
| TiDeTree | 2022 | Proceedings B | Synthetic-barcode phylogeny | Bayesian time and population parameter inference | Computational/model assumptions | Evolving barcodes |
| Cassiopeia | 2020 | Genome Biology | Synthetic-barcode phylogeny | Parsimony/ILP under CRISPR edit constraints | Ambiguous identical barcodes and dropout | Evolving barcodes |
| STARTLE | 2023 | Cell Systems | Synthetic-barcode phylogeny | Star-homoplasy model for CRISPR lineage tracing | Strong edit-process constraints | Evolving barcodes |
| FRACTAL | 2022 | Nature Biotechnology | Scalable phylogeny | Divide-and-conquer reconstruction for huge trees | Complexity of distributed setup | Natural variants or barcodes |
| GEMLI | 2024 | Nature Communications | Expression-only lineage | Gene-expression memory-based lineage prediction | Phenotypic convergence can mimic ancestry | scRNA-seq |
| CellTreeQM | 2025 | arXiv | Expression-only lineage | Metric-learning phenotypic phylogenies | Validation still limited | scRNA-seq embeddings |
| LinTIMaT | 2020 | Nature Communications | Barcode+expression phylogeny | Joint barcode parsimony and expression coherence | Similar expression need not mean shared ancestry | Barcode+scRNA-seq |
| LinRace | 2023 | Nature Communications | Barcode+expression phylogeny | Models asymmetric division and latent state hierarchy | Generative assumptions may be system-specific | Barcode+scRNA-seq |
| ICE-FASE | 2022 | Cell | Dynamic fate mapping | Transition direction/timing and progenitor counts | Assumes constant editing/mutation rate and potency restriction | Labelled phylogeny |
| PATH/PATHpro | 2024 | Nature Genetics | Dynamic fate mapping | Markov transition rates, heritability, plasticity and gene modules | Near-equilibrium and Markov assumptions | Labelled phylogeny |
| KCA | 2016 | Cell Systems | Dynamic fate mapping | Markovian transition-rate inference | Limited to simpler transition models | Labelled phylogeny |
| PhyloVelo | 2024 | Nature Biotechnology | Dynamic fate mapping | Lineage-informed RNA velocity from monotonic genes | Sensitive to tree and monotonic-expression assumptions | Phylogeny+scRNA-seq |
| CLADES | 2025 | Nature Communications | Dynamic fate mapping | Clone-specific growth and differentiation dynamics | Needs longitudinal static clone data and prior directions | Static barcodes+scRNA-seq |
| Carta | 2026 | Nature Methods | Optimization fate mapping | Infers differentiation maps with unobserved transitions | Irreversibility/potency assumptions | Labelled phylogeny |
| TROUPE | 2025 | bioRxiv | Optimization fate mapping | Multi-type Yule model for transition and growth rates | Preprint; model assumptions on proliferation | Labelled phylogeny |
| Clonotrace | 2025 | bioRxiv | Optimization fate mapping | Clone embeddings, pseudotime and fate genes | Preprint; similarity assumptions | Static barcodes+scRNA-seq |
| CoSpar | 2022 | Nature Biotechnology | Optimization fate mapping | Sparse and locally coherent fate bias inference | Objective and regularization dependence | Static barcodes+scRNA-seq |
| scTrace+ | 2025 | Cell Systems | Optimization fate mapping | Combines lineage and multi-faceted transcriptomic similarity | Depends on state/clone factorization | Static barcodes+scRNA-seq |
| LineageOT | 2021 | Nature Communications | Optimal transport | Temporal cell couplings using lineage and expression distances | Gradual-change and distance assumptions | Phylogeny+scRNA-seq |
| moslin | 2024 | Genome Biology | Optimal transport | Multi-timepoint lineage-aware cell mapping | Gradual-change and scalability limits | Phylogeny+scRNA-seq |
| TarCA | 2024 | Nature Methods | Ancestral state/fate mapping | Coalescent inference of progenitor number and lineage-specific genes | Conditions on inferred tree; uncertainty can be underrepresented | Labelled phylogeny |
| TreeVAE | 2021 | ICML workshop | Ancestral expression | VAE reconstruction of ancestral transcriptomes | Smooth latent-evolution assumption | Phylogeny+scRNA-seq |
| PORCELAN | 2025 | Nature Communications | Integrative learning | Learns lineage-expression representations and lineage-associated genes | Less mechanistic than explicit dynamic models | Phylogeny+scRNA-seq |
| ClonoCluster | 2023 | Cell Genomics | Integrative learning | Clone-informed transcriptome clustering | Clonal origin may not align with state | Static barcodes+scRNA-seq |
| LineageVAE | 2024 | Bioinformatics | Integrative learning | Latent Wiener-process model for state directions, ancestral expression and TF activity | Latent dynamics may be hard to validate | Static barcodes+scRNA-seq |
| Deep Lineage | 2024 | bioRxiv | Integrative learning | Deep prediction of future expression, fate and perturbation | Data-hungry; interpretability limited | Static barcodes+scRNA-seq |
| LCL | 2024 | bioRxiv | Integrative learning | Contrastive lineage-aware latent space | Preprint; contrastive objective assumptions | Static barcodes+scRNA-seq |
| DestinyNet | 2026 | Patterns | Integrative learning | Transferable multi-task fate clustering and flow | Needs robust transfer validation | Static/evolving barcodes+scRNA-seq |
| Hotspot | 2021 | Cell Systems | Gene programmes | Graph-based gene modules using phylogeny as adjacency | Finds association, not necessarily causality | Phylogeny+scRNA-seq |
| PhyloVision | 2022 | Cell Reports Methods | Gene programmes | Interactive lineage-expression visualization | Exploratory rather than inferential | Phylogeny+scRNA-seq |
| LMA | 2024 | Developmental Cell | Gene programmes | Over-represented lineage motif detection | Depends on null-tree design | Labelled phylogeny |
| Hirsch et al. | 2025 | Cell Systems | Gene programmes | OU-process adaptive expression tests | Evolutionary model assumptions | Phylogeny+scRNA-seq |

### Key Findings

The review's central conclusion is that no single method is generally best. Method choice depends on the type of lineage record, whether data are clonal or phylogenetic, whether there are multiple time points, and whether the goal is tree reconstruction, transition-rate inference, ancestral expression, fate prediction or gene programme discovery.

Several consensus points emerge. First, phylogenetic reconstruction is foundational but uncertain; downstream biological claims should not ignore tree uncertainty. Second, static barcodes and evolving barcodes support different questions: static barcodes are often better for clone-level fate bias over time, whereas evolving barcodes support tree-aware dynamics and ancestral inference. Third, dynamic models are interpretable but assumption-heavy, optimization models are useful for population flow but less mechanistic, and deep learning methods are flexible but harder to interpret. Fourth, gene programme discovery must distinguish lineage association from causal fate regulation.

The review also argues that spatial lineage tracing, multi-scale modelling and AI-enabled virtual-cell frameworks are promising future directions, but current models remain limited by dropout, under-sampling, insufficient benchmarks and weak causal grounding.

### Open Problems

1. Tree uncertainty propagation: many fate and gene-programme tools condition on a single inferred tree, which can produce overconfident downstream conclusions.
2. Cross-modal geometry mismatch: lineage trees, barcode matrices, transcriptomes, chromatin, methylation and spatial coordinates require different mathematical representations.
3. Unobserved ancestors: internal-node expression, cell type and progenitor fate distributions are inferred, not measured, and need uncertainty-aware validation.
4. Dropout and sparse sampling: allelic dropout, barcode dropout, clone under-sampling and rare-state loss reduce both tree accuracy and fate-mapping power.
5. Benchmarking: simulations provide ground truth but are model-dependent; real datasets with known lineage are rare and incomplete.
6. Causality: deep learning and foundation models may predict fate without explaining why a cell commits to that fate.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
