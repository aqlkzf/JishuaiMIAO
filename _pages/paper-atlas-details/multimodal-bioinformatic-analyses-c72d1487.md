---
layout: default
permalink: /paper-atlas/multimodal-bioinformatic-analyses-c72d1487/
title: "Multimodal bioinformatic analyses"
nav: false
description: "这不是一篇提出单一算法的论文，而是一篇方法学综述。它讨论的核心问题是：当研究对象从简单的病例—对照比较扩展到多因素、时间序列、多批次、多组学、单细胞和空间数据时，分析者应如何从“逐个基因找差异”过渡到“研究调控关系、网络结构与具体生物情境”。 全文的主线可以概括为四层：先判断实验设计；再决定是否仍适合做基因或转录本层面的差异表达；若问题涉及协同变化，则转向共表达网络；"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Briefings in Bioinformatics · 2026</span>
    </div>
    <h1>Multimodal bioinformatic analyses</h1>
    <p>Multimodal bioinformatic analyses of genome-scale expression beyond gene-centric differential expression</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1093/bib/bbag152" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 超越基因中心差异表达：多模态表达分析的中文阅读指南

### 这篇综述在解决什么问题

这不是一篇提出单一算法的论文，而是一篇方法学综述。它讨论的核心问题是：当研究对象从简单的病例—对照比较扩展到多因素、时间序列、多批次、多组学、单细胞和空间数据时，分析者应如何从“逐个基因找差异”过渡到“研究调控关系、网络结构与具体生物情境”。

全文的主线可以概括为四层：先判断实验设计；再决定是否仍适合做基因或转录本层面的差异表达；若问题涉及协同变化，则转向共表达网络；若问题涉及调控方向与机制，则需要 GRN 以及染色质、TF 结合、扰动等多模态证据；最后，在单细胞和空间数据中，把网络进一步限定到细胞类型、状态、轨迹或组织邻域。

这篇文章的价值主要在方法选择和概念边界，不是提供新的基准结果。它列举了大量工具，但没有用统一数据重新运行这些方法。因此，文中的方法优劣应理解为作者综合已有文献后的导航，而不是同一实验条件下的排行榜。

### 第一层：实验设计先于统计工具

#### 成对比较

最简单的设计是一个因素、两个水平，例如对照与处理。DESeq2、edgeR 或 limma 等方法可以通过设计矩阵和对比检验寻找差异基因。但即使在这类设计中，也要区分基因、转录本、外显子和转录本使用比例。把转录本简单聚合到基因层可能掩盖异构体切换，也可能受转录本长度与读段归属不确定性影响。

综述还比较参数与非参数思路。NOISeq、SAMseq、Swish 等方法可在小样本、零膨胀或转录本不确定性场景中提供补充，但秩变换会丢失表达量幅度，并不自动优于负二项模型。方法选择应由计数分布、重复数、推断重复和研究尺度决定。

#### 多因素设计

如果表型同时受基因型、环境、药物、性别或批次影响，逐个做两两比较再取交集不能正确表示因素间的相互作用。合理模型需要把主效应、交互项、嵌套因素和随机效应写进设计矩阵。所谓“协同”“拮抗”或“加和”效应，本质上来自组合条件相对于各单因素效应的模型比较，而不是肉眼比较几个 DEG 列表。

图 2B 特别强调数据矩阵上方不应只有一个二元标签，而要保留多个因素的组合结构。若设计本身混杂，例如某批次只包含病例而另一批次只包含对照，任何批次校正都无法可靠区分技术与生物差异。

#### 时间序列设计

把时间当离散变量，适合时间点较少、只关心任一时间点是否变化的场景；把时间当连续变量，才能描述趋势、拐点、领先—滞后、周期和瞬时脉冲。Trendy 使用分段回归寻找断点，RAIN 与 MetaCycle 面向周期模式，ImpulseDE2 用脉冲或 sigmoid 型曲线描述瞬时与持续响应。

这里最重要的不是挑一个“时间序列工具”，而是先明确预期动力学。采样过稀会错过瞬时峰值，采样窗口太短无法识别周期，重复测量又要求处理同一受试者内部相关性。时间点数量增加也不等于独立生物重复增加。

#### 多批次设计

ComBat-seq、svaseq、RUV、PEER 等方法分别处理已知批次或潜在混杂。综述反复提醒过度校正：若批次与生物条件相关，算法可能把真实差异当作技术噪声删除。校正前应做方差归因、检查组别平衡；校正后要监测稳定参考基因、已知阳性信号和样本结构是否被不合理抹平。

图 2D 将批次校正、高变基因选择和矩阵分解放在同一设计框架中，提示这些操作不是彼此独立的“预处理按钮”。选择哪些变异来源进入潜变量，会直接改变后续网络和多组学整合。

### 第二层：从差异基因表转向共表达网络

基因共表达网络（GCN）把基因作为节点，把相关性或其他依赖度作为边。典型流程是：标准化表达矩阵，计算基因—基因邻接矩阵，阈值化或软阈值转换，再做聚类/社区检测得到模块。WGCNA 是加权相关网络的代表；ARACNE、CLR 使用互信息捕捉非线性依赖。

GCN 回答“哪些基因在这些样本中共同变化”，但不能单凭相关性判断调控方向。两个基因相关可能因为共同 TF、细胞组成、批次或第三条通路。即使互信息能捕捉非线性，它仍是无方向的统计依赖。

样本特异网络试图把群体网络拆解到个体。图 3B 展示 LIONESS/SWEET 类思路：分别构建聚合网络和加入/扰动某个样本后的网络，再通过差值和缩放估计该样本的边。这样可比较患者特异网络或疾病异质性，但单样本网络并非直接由一个样本稳定估计，它继承了总体网络、归一化和插值假设的不确定性。

样本量问题没有统一阈值。网络推断涉及成千上万条候选边，样本太少时相关系数非常不稳定。综述引用的经验结果依赖数据同质性、测序深度、标准化和评价金标准，不能把“20 个样本”之类数字视为普遍保证。

### 第三层：从共表达到调控网络

GRN 试图描述 TF 对靶基因的调控关系，比 GCN 多了方向、调控者身份或条件依赖。表达数据上的常见家族包括：

- 回归与集成学习：GENIE3、GRNBoost2 把每个靶基因作为预测目标，用其他基因或 TF 作为输入；dynGENIE3 扩展到时间序列。
- 概率图模型：以条件依赖描述边，并可结合模块和先验。
- 信息论方法：用互信息或多变量信息捕捉非线性关联。
- 动力学模型：ODE 或 NeuralODE 将调控作用写入随时间变化的表达模型。

这些方法输出的是候选调控边，不是因果事实。树模型中的特征重要性可由共同预测信号产生；概率条件依赖受遗漏变量影响；动力学模型又依赖采样密度和结构先验。可靠解释需要 TF 扰动、ChIP、motif、染色质可及性或其他独立证据。

### 第四层：为什么要引入多模态和先验知识

图 4A 列出可约束 GRN 的证据：遗传变异、结合 motif、DNA 甲基化、TF 结合、已知调控网络、蛋白互作、TF/基因敲除和染色质可及性。它们用于删去缺乏物理支持的候选边、调整边的先验概率，或估计转录因子活性（TFA）。

TFA 的关键动机是 TF 的 mRNA 水平不等于其活性。TF 可由磷酸化、核转位或配体结合激活，本身表达变化很小，却使一组靶基因同步改变。网络成分分析、TIGER、MERLIN+P+TFA 等方法利用已知 TF—靶标拓扑，从表达矩阵反推潜在 TF 活性及调控强度。

多模态 GRN 大致分为五类：

1. 矩阵分解：将表达近似分解为调控连接与 TF 活性，或提取跨组学共同潜因子。
2. 回归/机器学习：用 TF 活性和多组学特征预测靶基因，可逐基因或多任务联合学习。
3. 概率图模型：在先验网络约束下估计条件概率或精度矩阵。
4. 消息传递：PANDA、PUMA、SPIDER、EGRET 等在 motif、PPI、表达、表观遗传或基因型网络之间迭代协调一致性。
5. 深度学习：用图嵌入、CNN、NeuralODE 等学习非线性调控映射。

图 4的核心提醒是：多模态 GRN 不是一个统一模型。不同算法对配对样本、先验拓扑、标签、时序和样本量的要求完全不同。先验能减少搜索空间，也可能把数据库偏差固化到结果中。组织、细胞类型或条件不匹配的 motif/ChIP/PPI 先验，不一定比表达数据本身更可靠。

### 如何评价 GRN

若有已知正负边，可以计算 AUROC、AUPRC、F1 或 Matthews 相关系数。GRN 候选边极度不平衡，负边远多于真边，因此 AUROC 可能在真阳性恢复很差时仍显得较高；AUPRC 更强调精确率，但其基线随阳性比例变化，不能跨不同金标准直接比较。

“金标准”本身也不完整。ChIP 证明结合，不必然证明在该条件下调控表达；motif 只表示潜在结合位点；扰动会包含直接和间接效应。更稳健的评估应组合拓扑恢复、独立扰动、调控子富集、跨数据集稳定性与具体生物任务，而不是只报告一个全局分数。

DREAM 等社区挑战显示不同算法的错误具有互补性，集成网络常优于单个方法。这并不表示简单平均永远有效，而是提示 GRN 推断不确定性很高，边的共识和重复验证比单模型排名更值得关注。

### 单细胞与空间层面的新问题

单细胞 RNA-seq 可以推断细胞类型特异网络、轨迹相关调控和 regulon。SCENIC 把树模型候选边与 motif 富集结合，SCENIC+进一步整合 scRNA-seq、scATAC-seq 与增强子信息。但单细胞数据的零值、测序深度、细胞状态混合和伪时间假设都会影响边。成千上万个细胞也不能替代足够的独立个体，按细胞做显著性检验容易产生伪重复。

空间数据增加坐标、邻域和组织结构。分析目标从“某细胞类型的 GRN”扩展为“某空间区域或邻域中的 GRN”，并与细胞—细胞通信（CCC）连接。CellPhoneDB、NicheNet、CellChat 主要从配体—受体和靶基因程序推断通信；MultiGATE、CLARIFY、SpaGRN 等尝试联合空间、多组学、CCC 和调控网络。

空间邻近不等于信号传递，配体与受体共表达也不证明功能作用。较强的空间调控链需要分层证据：发送细胞有配体，接收细胞有受体，二者空间可接触，下游 TF 活性与靶基因程序一致，最好还有扰动验证。将所有层次压缩成一条“通信边”会掩盖证据强弱。

### 四张主图怎样串起全文

图 1 是整篇综述的路线图：A–D 从成对、多因素、时间和批次设计出发；E 是表达网络；F 是多模态 GRN；G–H 进入单细胞和空间网络。它说明分析复杂度的增长来自研究问题，而不是追逐更新的工具。

图 2 把四类设计与表达矩阵并列，提醒设计标签必须真实进入统计模型。图 3 从标准化矩阵到邻接矩阵、阈值和社区，再展示样本特异网络，以及相关、互信息、集成学习和概率模型四类边定义。图 4 则把先验证据与 TFA、回归、概率图、消息传递和深度学习对应起来，是选择多模态 GRN 方法时最实用的分类图。

### 实际选择方法时的顺序

第一步写清独立生物重复、因素、时间、批次、配对关系和模态是否来自同一细胞/样本。第二步明确目标是找变化特征、表达模块、调控边、TF 活性、细胞通信还是空间特异网络。第三步检查数据是否满足方法的样本量、时间分辨率、配对与先验要求。第四步预先定义验证：独立队列、扰动、染色质或已知生物标志。最后才选择具体软件，并在多个合理设定下检验稳定性。

这篇综述最值得保留的结论不是“哪个工具最好”，而是没有一个方法适用于所有数据制度。简单设计中的 DE 仍然有效；网络和多模态方法提供更丰富的机制假设，但代价是更多假设、更复杂的验证和更高的过拟合风险。单细胞与空间分辨率提高了可提问的精度，却没有自动解决因果性、独立重复和金标准稀缺问题。

### 证据与范围边界

本文是叙述性方法综述，不是系统综述、Meta 分析或统一 benchmark。作者未报告可复现的文献检索式、纳入排除流程或偏倚评估，也没有关联代码仓库或新算法实现。因此本工作区只做论文和图的深读，不应生成 `doc_code.md`、代码提交号或“论文代码完全匹配”等结论。

本地证据包括 PMC 全文和四张主图；文章没有独立补充材料。表 1和表 2以内嵌 HTML 表格存在于全文，而不是 Markdown 管道表，因此简单的 `grep '^|'` 为零不代表表格缺失。软件版本、维护状态和最新文档可能随时间变化，真正采用工具前应另行核对官方文档和当前仓库。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Multimodal Bioinformatic Analyses of Genome-Scale Expression Beyond Gene-Centric Differential Expression

### Review Scope

This 2026 Briefings in Bioinformatics review surveys how genome-scale expression analysis is moving beyond gene-by-gene differential expression (DE) toward study-design-aware, network-based, multimodal, single-cell, and spatial regulatory analysis. Its target audience is computational biologists and omics analysts who need to choose an analysis strategy for transcriptomic or multi-omic expression studies.

The review is not a benchmark or a new method paper. It is a methodological landscape review. It covers roughly 60 named tools or method families when DE, batch correction, matrix factorization, GCN/GRN, multimodal GRN, single-cell, cell-cell communication, and spatial GRN methods are counted together. The densest method coverage is in Table 1 (expression-only GCN/GRN tools) and Table 2 (multimodal/prior-informed GRN tools).

### Field Landscape

The review frames conventional DE as the historical default for expression analysis: compare conditions, identify genes or transcripts with significant expression changes, and interpret those hits through pathways or biomarkers. It argues that this workflow remains useful but becomes incomplete when the study question involves interacting factors, time, batches, hidden covariates, cell states, spatial neighborhoods, or regulatory mechanisms.

The first turning point is design complexity. Pairwise comparisons can support standard DE, but multifactorial experiments require explicit interaction terms, time-series experiments require discrete or continuous temporal models, and multi-batch studies require careful handling of known and latent confounders. The second turning point is systems-level modeling: GCN and GRN methods replace isolated gene lists with relationships among genes, regulators, and modules. The third turning point is multimodality, where expression is combined with chromatin accessibility, DNA methylation, TF-binding priors, PPI, perturbation evidence, or spatial coordinates to improve regulatory interpretation. The final turning point is resolution: single-cell and spatial data let analysts ask cell-type-specific, trajectory-specific, niche-specific, and joint CCC-GRN questions, but they also increase sparsity, dependence, and validation difficulty.

### Method Taxonomy

The review's taxonomy has four layers:

| Layer | Main Question | Representative Categories |
|---|---|---|
| Study design and DE | What expression features change under a design? | Pairwise DE, multifactorial DE, time-series DE, multi-batch correction, transcript/exon usage |
| Expression networks | Which genes covary or regulate each other from expression data? | GCN, sample-specific GCN, expression-only GRN |
| Multimodal/prior-informed GRN | How can prior knowledge and other omics constrain regulatory inference? | Matrix factorization/TFA, regression/ML, PGM, message passing, deep learning |
| High-resolution inference | How do regulatory programs vary by cell state and tissue context? | Single-cell GRN, spatial GRN, CCC, joint CCC-GRN |

### Key Findings

The main consensus is that method choice should start from study design and biological question, not from tool popularity. Pairwise DE is appropriate for simple contrasts but can be misleading in multifactorial or time-series designs when interactions, batch factors, and temporal dependencies are ignored. Rank-based or non-parametric methods can help in some count regimes, but they trade sensitivity and expression-magnitude information for robustness.

For network analysis, the review separates co-expression from regulation. Correlation and mutual information can identify coordinated genes, while regression, ensemble learners, probabilistic models, and message-passing methods attempt to infer regulatory direction or context-specific regulatory programs. It repeatedly cautions that expression-only relationships are not causal evidence. Motifs, chromatin accessibility, TF binding, perturbation, eQTL, PPI, and known GRN priors can improve GRN plausibility, but they also introduce prior bias and dependency on compatible data.

For validation, the review highlights the imbalance problem in GRN benchmarks: AUROC can look favorable when true negatives dominate, whereas AUPRC better stresses true-positive recovery but cannot be compared naively across datasets with different positive/negative ratios. DREAM-style community networks and BEELINE-style single-cell benchmarks show that no single inference assumption wins universally.

For single-cell and spatial omics, the review's strongest point is that higher resolution does not automatically solve regulatory inference. Single-cell data amplify sparsity and trajectory/topology assumptions; spatial data add tissue context but make joint modeling of CCC and cell-specific GRNs harder. The field is moving toward models such as SCENIC+, MultiGATE, CLARIFY, and SpaGRN that connect regulatory programs with chromatin, spatial coordinates, and ligand-receptor signaling.

### Method Comparison Table

Inclusion rule: this table covers the major named tools emphasized in the review's method tables and narrative. It excludes many cited background papers that are examples of biological applications rather than general analysis methods.

| Method | Year | Journal | Category | Key Innovation | Limitations | Data Types |
|---|---:|---|---|---|---|---|
| DESeq2 | 2014 | Genome Biology | DE | Moderated negative-binomial RNA-seq DE | Pairwise/design formula quality determines validity | Bulk RNA-seq |
| edgeR | 2010 | Bioinformatics | DE | Negative-binomial DE with quasi-likelihood extensions | Requires careful normalization/design specification | Bulk RNA-seq, transcript-level workflows |
| limma | 2015 | Nucleic Acids Research | DE / batch handling | Linear modeling and removeBatchEffect workflows | Linear assumptions; over-correction risk | RNA-seq, microarray |
| NOISeq | 2015 | Nucleic Acids Research | Non-parametric DE | Data-quality-aware signal-to-noise DE | Can show false positives in small benchmarks | RNA-seq |
| SAMseq | 2013 | Statistical Methods in Medical Research | Non-parametric DE | Rank-based count DE | Can lose expression magnitude and sensitivity | RNA-seq |
| Swish | 2019 | Nucleic Acids Research | Transcript-level DE | Uses inferential replicates | Requires compatible quantification uncertainty | RNA-seq transcript counts |
| EBSeq-HMM | 2015 | Bioinformatics | Time-series DE | HMM for ordered expression states | Pattern space can scale poorly with many time points | Ordered RNA-seq |
| Trendy | 2018 | BMC Bioinformatics | Time-series DE | Segmented regression and breakpoint discovery | Needs enough ordered samples to fit trends | Ordered expression |
| RAIN | 2014 | Journal of Biological Rhythms | Rhythmic expression | Non-parametric umbrella-shaped rhythm detection | Assumption-constrained; overdispersion sensitivity | Time-series expression |
| MetaCycle | 2016 | Bioinformatics | Rhythmic expression | Consensus rhythm detection across three algorithms | Developed largely from microarray-era methods | Time-series expression |
| ImpulseDE2 | 2018 | Nucleic Acids Research | Time-series DE | Negative-binomial impulse/sigmoid model | Requires temporal sampling that supports model fit | Time-course RNA-seq |
| ComBat-seq | 2020 | NAR Genomics and Bioinformatics | Batch correction | Count-aware RNA-seq batch adjustment | Depends on known batch labels and balanced design | RNA-seq counts |
| svaseq | 2014 | Nucleic Acids Research | Latent confounders | Surrogate variables in RNA-seq models | Can struggle when batch and biology are entangled | RNA-seq |
| PEER | 2010 | PLoS Computational Biology | Latent confounders | Bayesian factor model for expression variation | Latent factors need interpretation and tuning | Expression, eQTL |
| MOFA+ | 2020 | Genome Biology | Matrix factorization | Shared latent factors across modalities | Factor interpretation and missingness handling matter | Multi-omics, single-cell multiome |
| WGCNA | 2008 | BMC Bioinformatics | GCN | Weighted co-expression modules | Correlation is not causality; sample-size sensitive | Bulk expression |
| ARACNE | 2006 | BMC Bioinformatics | GCN/GRN | Mutual-information network reconstruction | Large sample needs; indirect-edge filtering assumptions | Expression |
| CLR | 2007 | PLoS Biology | GCN | Context-likelihood transformation of MI | Best suited to larger datasets | Expression |
| CEMiTool | 2018 | BMC Bioinformatics | GCN | Automated co-expression modules | Module quality depends on preprocessing | Expression |
| BONOBO | 2024 | Genome Research | Sample-specific GCN | Bayesian sample-specific co-expression | More complex inference than aggregate networks | Expression cohorts |
| LIONESS | 2019 | iScience | Sample-specific GCN | Interpolates sample-specific networks from aggregate/perturbed networks | Sensitive to aggregate-network construction | Expression cohorts |
| SWEET | 2023 | Briefings in Bioinformatics | Sample-specific GCN | Size-adjusted sample-specific weighted correlation | Still inherits correlation-network limitations | Expression cohorts |
| GENIE3 | 2010 | PLoS ONE | GRN | Tree ensembles for regulator-target prediction | Can aggregate weak subtree signals; no direct causality | Expression |
| GRNBoost2 | 2019 | Bioinformatics | GRN | Stochastic gradient boosting for scalable GRNs | Regression association, not causal proof | Bulk and single-cell expression |
| dynGENIE3 | 2018 | Scientific Reports | Time-dependent GRN | Extends GENIE3 to time-series dynamics | Needs time-course data and assumptions about dynamics | Time-series expression |
| Inferelator | 2022 | Bioinformatics | GRN | Scalable regression/ODE GRN inference with priors | Prior and model specification affect results | Bulk/single-cell expression, chromatin priors |
| MERLIN-P / MERLIN+P+TFA | 2017/2025 | NAR / preprint | Prior-informed GRN/TFA | Probabilistic prior-constrained GRNs with TFA | Older MERLIN variants deprecated; prior dependence | Expression plus motif/ChIP/knockout priors |
| TIGER | 2024 | npj Systems Biology and Applications | TFA | Flexible regulatory-network modeling for TF activity | Relies on GRN/prior quality | Expression plus regulatory priors |
| PANDA | 2013 | PLoS ONE | Message passing GRN | Iteratively reconciles motif, PPI, and expression networks | Requires informative prior networks | Expression, motif, PPI |
| PUMA | 2020 | Bioinformatics | Message passing | Adds miRNA-mRNA associations to PANDA-style inference | Prior availability and interpretation constraints | Expression, miRNA priors |
| SPIDER | 2021 | npj Systems Biology and Applications | Message passing | Uses epigenetic information for GRN construction | Prior compatibility required | Expression, ChIP/DNase/epigenetic data |
| EGRET | 2022 | Genome Research | Genotype-specific GRN | SNP/eQTL-informed individual networks | Genotype/eQTL priors needed | Expression, SNP/eQTL, motif, PPI |
| DRAGON | 2023 | Nucleic Acids Research | Multimodal PGM | Gaussian graphical modeling across omics | Linear/Gaussian assumptions can miss nonlinear regulation | Methylation, expression |
| AMuSR | 2019 | PLoS Computational Biology | Multitask GRN | Multi-study regulatory network inference | Needs related studies and regulatory priors | Expression plus prior knowledge |
| PSIONIC | 2019 | Nature Communications | Patient-specific GRN | Chromatin-informed transcriptional programs | MATLAB implementation; chromatin prior dependence | Expression, chromatin accessibility |
| NetREX-CF | 2022 | Communications Biology | ML GRN/TFA | Collaborative filtering reconciles incomplete TF data | Depends on incomplete prior structure | Expression, TF priors |
| DeepFGRN | 2024 | Briefings in Bioinformatics | Deep learning GRN | Directed graph embedding predicts regulatory type/direction | Supervised labels and generalization are limiting | GRN graph, expression/prior data |
| PHOENIX | 2024 | Genome Biology | NeuralODE GRN | Biologically informed regulatory dynamics | Requires dynamic/time-series framing and priors | Time-series expression, GRN priors |
| PIDC | 2017 | Cell Systems | Single-cell GRN | Multivariate information for single-cell networks | Captures co-expression more than regulation | scRNA-seq |
| SCENIC | 2017 | Nature Methods | Single-cell GRN | Tree-based GRN plus motif regulons | Computational cost scales with genes; motif dependence | scRNA-seq, motifs |
| SCENIC+ | 2023 | Nature Methods | Single-cell multiome GRN | Links scRNA-seq, scATAC-seq, enhancers, and GRNs | Multiome data and regulatory priors needed | scRNA-seq, scATAC-seq |
| CellPhoneDB | 2025 | Nature Protocols | CCC | Ligand-receptor communication from single-cell multiomics | CCC inference can remain correlative | scRNA-seq/multiomics |
| NicheNet | 2025 | Nature Protocols | CCC | Infers active ligands from target-gene programs | Requires ligand-target prior networks | Transcriptomics |
| CellChat | 2025 | Nature Protocols | CCC | Systematic CCC inference from single-cell transcriptomics | Pseudo-bulk/cell-type aggregation assumptions | scRNA-seq |
| MultiGATE | 2025 | Nature Communications | Spatial multi-omics GRN | Graph learning for paired spatial RNA/ATAC regulatory inference | Limited to paired sequencing-based spatial multiomics in the review | Spatial RNA-seq, spatial ATAC-seq |
| CLARIFY | 2023 | Bioinformatics | Joint CCC/GRN | Refines cell-cell interaction and GRN from spatial transcriptomics | Young task area; validation remains difficult | Spatial transcriptomics |
| SpaGRN | 2025 | Cell Systems | Joint CCC/GRN | Spatially informed regulatory paths and regulons | Spatial/task-specific assumptions | Spatial transcriptomics |

### Open Problems

1. Causal GRN validation remains hard. Expression-only edges can reflect correlation, indirect regulation, confounding, or shared cell-state effects. Perturbation and chromatin priors help, but ground truth is sparse and biased toward well-studied systems.
2. Study-design-aware method selection is still under-specified. The review explains why pairwise, multifactorial, time-series, and multi-batch designs require different assumptions, but analysts still need practical decision frameworks that combine design matrix, sample size, modality, and biological question.
3. Multimodal integration is limited by prior quality and assay compatibility. Priors can remove implausible edges, but they can also propagate database bias or fail in contexts where regulatory programs are condition-specific.
4. Single-cell and spatial analyses face pseudo-replication and dependence. More cells or spots do not necessarily mean more independent biological replicates, and cell-level models can overstate evidence when donor/sample structure is ignored.
5. Joint CCC-GRN modeling is immature. Spatial papers increasingly ask how ligand-receptor signaling changes cell-specific regulons, but methods and benchmarks for this coupled task are still early.

### Bottom Line

This review is most useful as a roadmap for moving from "which genes changed?" to "which regulatory systems changed, under which design assumptions, and with which supporting modality?" Its central message is conservative and practical: start from the biological design and data regime, use network and multimodal methods only when their assumptions match that regime, and treat inferred regulatory edges as hypotheses unless supported by independent prior, perturbation, chromatin, spatial, or validation evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
