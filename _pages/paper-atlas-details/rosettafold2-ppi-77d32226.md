---
layout: default
permalink: /paper-atlas/rosettafold2-ppi-77d32226/
title: "RoseTTAFold2-PPI"
nav: false
wide: true
description: "这项工作不是把任意两个蛋白交给 AlphaFold 再看结构是否“像一个复合物”，而是先从更深的跨物种序列数据中寻找共同进化信号，再用专门训练的快速网络 RF2-PPI 做大规模筛选，最后只对候选对运行 AlphaFold2。这样把约 1.91 亿个组合逐层缩小到可计算、可解释的高置信候选。"
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
      <span>Protein &amp; Sequence Models</span>
      <span>Science · 2025</span>
    </div>
    <h1>RoseTTAFold2-PPI</h1>
    <p>Predicting protein-protein interactions in the human proteome</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1126/science.adt1630" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for RoseTTAFold2-PPI">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/CongLabCode/RoseTTAFold2-PPI" target="_blank" rel="noopener noreferrer" aria-label="Open code for RoseTTAFold2-PPI">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RF2-PPI：在人类蛋白质组中筛选蛋白互作

### 一句话理解

这项工作不是把任意两个蛋白交给 AlphaFold 再看结构是否“像一个复合物”，而是先从更深的跨物种序列数据中寻找共同进化信号，再用专门训练的快速网络 RF2-PPI 做大规模筛选，最后只对候选对运行 AlphaFold2。这样把约 1.91 亿个组合逐层缩小到可计算、可解释的高置信候选。

### 为什么问题比普通二分类更难

人类蛋白质组约有两万个蛋白，两两组合接近两亿，而真实互作预计只有 7.4 万到 20 万，先验信噪比约为 1:1000。即使分类器在平衡测试集上看起来很好，少量假阳性也会淹没真正互作。因此论文在评估精度时把 3000 个正对各赋权 0.01、把 30000 个负对赋权 1，使评估更接近蛋白质组筛选的先验分布。这里报告的“90% precision”是这种基准和阈值校准下的期望精度，不等于每个预测都已被实验验证。

### 输入：成对 MSA 是共同进化证据

对候选蛋白 A、B，方法先分别找跨物种同源序列，再按物种把 A 的同源序列和 B 的同源序列拼成 paired MSA（pMSA）。如果两个蛋白长期直接互作，界面残基发生突变后，另一侧常出现补偿突变；跨物种成对排列让模型有机会读出这种协同变化。

标准序列库对真核蛋白覆盖不足。作者从 NCBI 基因组和约 30 PB 的 Sequence Read Archive 原始测序数据中，经质量过滤、剪接感知比对和参考引导组装，获得覆盖 21,415 个真核物种的 omicMSA。论文图 1 显示其 pMSA 平均深度约为 UniRef100 的七倍，而且物种和属层面的分类多样性明显更高；RF2-PPI 与 AF2 使用 omicMSA 后，精确率—召回率曲线均改善。

这一步有一个重要假设：同一物种内被配对的同源蛋白确实对应正确的互作伙伴。旁系同源很多、基因注释错误或物种覆盖不足时，配对会引入噪声。深 MSA 也不能补救缺乏跨物种保守性的瞬时互作、无序区介导互作或宿主—病原体互作。

### 训练集扩充：把单体内部的结构域接触变成学习样本

实验 PDB 复合物提供的 PPI 簇只有 13,231 个，规模不足。作者从约 5370 万个去冗余 AlphaFold Database 单体模型中识别多结构域蛋白，将结构域之间可靠的接触当作“像 PPI 界面一样”的训练例子：至少 25 个跨结构域的 6 Å 内接触，平均跨结构域 PAE 小于 8。经过筛选、30% 序列聚类并去除人类同源项后，得到 223,440 个 DDI 簇，约为 PDB PPI 簇的 17 倍。

论文训练混合物包含单体、正 DDI、负 DDI、正 PPI、负 PPI，比例为 2:1:1:1:1。正例教模型识别真实界面距离模式，负例则把跨链距离监督为大于 20 Å，迫使网络学习“没有界面”而非对任意两条链都拼出一个看似合理的结构。DDI 是数据蒸馏而非直接的实验互作证据；它把同一多结构域蛋白内部接触迁移到跨蛋白判断，仍存在分布差异。

### RF2-PPI 网络究竟输出什么

RF2-PPI 保留 RoseTTAFold2 的 MSA track 和 pair track，使用 4 个 extra-MSA block 与 12 个 main block，并移除昂贵的三维坐标生成路径。训练时在 MSA 与 pair 表示之间反复交换信息，并使用 recycling；论文图 2 报告其速度约比 AF2 快 20 倍，因此适合作为数千万候选的中间筛选器。

本地代码 `src/RoseTTAFoldModel.py` 的主要输出头是残基对距离/方向分布和 masked-token 预测，并没有文档旧版本所写的独立 `ppi_logit` 二分类头。推断脚本 `src/predict_list_PPI.py` 对距离 logits 做 softmax，累加接触阈值以内的距离 bins，得到每个跨链残基对的接触概率：

$$
p_{ij}^{contact}=\sum_{b < b_{contact}} \operatorname{softmax}(z_{ij})_b.
$$

随后仅保留两条链之间的矩阵块，并取全局最大值作为蛋白对分数：

$$
RF_{IntProb}=\max_{i\in A,\,j\in B} p_{ij}^{contact}.
$$

因此这个蛋白级分数的直观含义是“是否存在一个非常可信的跨链接触”，而不是界面所有接触的平均质量。一个特别高的残基对可支配最终分数，这也是解释中间概率和局部伪接触时必须保留的实现边界。脚本同时输出整个 $L_A\times L_B$ 接触概率矩阵，适合查看候选界面位置。

推断实现使用最多 128 条 latent MSA、1024 条 extra MSA，固定 recycling 三次，并用空模板特征运行，即公开脚本本身不依赖复合物模板。README 提醒约 5% 的蛋白对多次运行时标准差可能超过 0.1，主要出现在中间概率区；阈值附近的候选不应被视为确定标签。

### 全蛋白质组级联筛选

论文的正式流程如下：

1. 从 20,296 个蛋白出发，经结构域解析与保守性过滤保留 19,528 个蛋白、约 1.91 亿个组合。
2. 对定位在同一 cellular component 的 5380 万对和定位未知的 5740 万对先做快速 DCA。DCA 约比 RF2-PPI 快五倍，筛出 4360 万对；基准显示超过 80% 的高 RF2-PPI/AF2 候选能通过此预筛。
3. 运行 RF2-PPI，保留 $RF_{IntProb}>0.3$ 的约 190 万对。
4. 对剩余候选运行 AF2，生成三维模型并计算 $AF_{IntProb}$；阈值根据候选是否已有遗传或物理互作先验证据而变化。完全 de novo 的组合需要接近 0.99 的严格分数，带先验证据的组合可用较低阈值。
5. 结合 de novo、STRING 遗传关联和 UniProt/BioGRID/STRING 物理证据分支，并进行假阳性 hub 等过滤，得到最终集合。

正式论文报告 29,256 个预测在校准下达到约 80% 期望精度；更严格集合含 17,849 个预测，期望精度约 90%、估计召回率 8% 至 22%。其中 3,037 个有直系同源 PDB 模板，11,181 个已出现于主要 PPI 数据库，3,631 个未见于这些既有来源。旧工作区中的“1,191 个新互作、107/117 实验验证”来自不同版本，不能作为这篇 Science 正式版本的主结果。

### 怎样阅读四张主图

- 图 1 先建立问题先验与输入证据：数据库重叠很低；omicMSA 更深、更广，并提高不同网络的筛选性能。
- 图 2 解释训练和模型设计：AFDB 的 DDI 把训练规模扩大约 17 倍；RF2-PPI 用 MSA/pair tracks 和距离监督换取速度。AF2+omicMSA 的总体 AUCPR最高，但 RF2-PPI 在高精度区域兼顾召回和计算成本。
- 图 3 是结果漏斗而不是单个模型的输出：DCA、RF2-PPI、AF2 和先验证据共同决定最终 29,256/17,849 集合。图中精度曲线来自基准校准，不是逐对实验测量。
- 图 4 对 3,631 个数据库外预测做证据分层并展示结构假说。结构图和界面上的疾病变异能提出机制，但仍属于待实验检验的预测。

### 能做什么，不能做什么

这套方法最适合有足够同源序列、存在稳定共同进化界面的同物种蛋白对。它对跨膜蛋白互作表现出优势，也能用接触矩阵和 AF2 模型提出界面及疾病变异机制。相反，小界面、弱/瞬时互作和无序区介导互作更容易漏检；论文也明确指出这些类别在预测集合中不足。

同一细胞组分过滤会降低计算量和假阳性，但也会遗漏转位、跨细胞器或注释错误的真实互作。预测出的结构兼容性与共同进化信号也不证明两者在特定组织、时间或生理条件下实际相遇。数据库外的 3,631 对是“未被主要来源收录”，不等同于全部从未有人实验研究。

### 本地代码的可复现边界

本地仓库与论文中 RF2-PPI 的核心网络、训练入口、paired-MSA 整理和批量推断相符，模型权重与 omicMSA 需另外下载。公开代码可以从已构建的两条单蛋白 MSA 生成 pMSA，并计算蛋白对分数和残基接触矩阵。

但仓库没有提供从 30 PB 原始数据重建 omicMSA 的完整流水线，也没有论文全筛选所需的 DCA 预过滤、AF2 级联、精度阈值校准、假阳性 hub 清理、最终网络分析和实验验证流程。因此“能运行 RF2-PPI”不等于“能从头复现 1.91 亿对的人类互作组”。此外，仓库固定在提交 `ffc86527838cc1b75b75002c0831941d58d8dfe5`；结论应以该快照和正式论文为边界。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RoseTTAFold2-PPI: Predicting Protein-Protein Interactions in the Human Proteome

**Authors**: Jing Zhang, Ian R. Humphreys, Jimin Pei, Jinuk Kim, Chulwon Choi, Rongqing Yuan, Jesse Durham, Siqi Liu, Hee-Jung Choi, Minkyung Baek, David Baker, Qian Cong

**Journal**: Science, 2025 | **DOI**: 10.1126/science.adt1630

**Code**: [github.com/CongLabCode/RoseTTAFold2-PPI](https://github.com/CongLabCode/RoseTTAFold2-PPI)

---

### Motivation & Novelty

The human interactome (estimated 74,000-200,000 PPIs among ~200 million protein pairs) remains largely uncharacterized. Experimental methods (Y2H, AP-MS) have limited coverage and high false-positive rates — only 3,988 PPIs are confidently supported by all three major databases (UniProt, BioGRID, STRING). Computational approaches combining coevolutionary analysis with deep-learning structure prediction have mapped interactomes in bacteria (Humphreys et al., *Science*, 2021) and yeast (Zhang et al., *Nature Structural & Molecular Biology*, 2023), but face two critical bottlenecks in humans: (1) shallow coevolutionary signals due to the short evolutionary history of many human-specific proteins, and (2) the prohibitive computational cost of screening 200 million pairs with methods like AlphaFold2 (Jumper et al., *Nature*, 2021).

**Two key innovations** overcome these limitations:

1. **omicMSAs**: By mining 30 petabytes of raw genomic data from NCBI SRA and assembling protein sequences from 21,415 eukaryotic species (including 18,991 without prior protein annotations), the authors create multiple sequence alignments 7-fold deeper than those from UniRef100. These omicMSAs dramatically strengthen coevolutionary signals for human proteins.

2. **RoseTTAFold2-PPI (RF2-PPI)**: A deep-learning network derived from RoseTTAFold2 (Baek et al., *Science*, 2023), optimized for fast PPI prediction by removing the 3D structure track and training on a 17-fold expanded dataset of domain-domain interactions extracted from 200 million AFDB predicted structures (Varadi et al., *Nucleic Acids Research*, 2024). RF2-PPI is 20x faster than AF2 while achieving comparable or superior accuracy for PPI detection.

Compared to prior work:
- **AlphaFold-multimer** (Evans et al., *bioRxiv*, 2022) and **AlphaFold3** (Abramson et al., *Nature*, 2024) optimize for complex structure quality, not PPI discrimination — they perform substantially worse at distinguishing true PPIs from random pairs at the 1:1000 signal-to-noise ratio of de novo screens
- **ColabFold** (Mirdita et al., *Nature Methods*, 2022) improves MSA construction but uses metagenomic data poorly suited for multicellular eukaryotes
- **RF2-lite** (Humphreys et al., *bioRxiv*, 2024) is fast but significantly less accurate than RF2-PPI (1.7x improvement in AUCPR)

---

### Method Overview

The approach combines large-scale genomic data mining with a hierarchical computational pipeline:

1. **omicMSA construction**: Assemble protein sequences from draft genomes and unassembled reads of 21,415 eukaryotic species using splicing-aware aligners; build paired MSAs 7-fold deeper than conventional approaches
2. **DCA prefilter**: Direct Coupling Analysis rapidly reduces 111M candidate pairs to 44M (5x faster than RF2-PPI)
3. **RF2-PPI screening**: A two-track (MSA + Pair) neural network with 4+12 attention blocks, 3 recycles, trained on PDB PPIs + AFDB DDIs + negatives. Produces interaction probabilities from distogram predictions
4. **AF2 structural modeling**: High-accuracy 3D models for ~2M RF2-PPI candidates
5. **Precision estimation + hub removal**: FDR-inspired calibration using screened negative controls; grid-searched cutoffs to achieve target precision

An evidence-guided parallel branch incorporates genetic associations and experimental evidence from databases, allowing lower prediction thresholds. See `doc_method.md` for full algorithmic details and `doc_code.md` for code-paper mapping.

---

### Evaluation

#### Benchmark Design
- **Positive controls**: 3,000 PPIs confidently supported by UniProt, BioGRID, and STRING
- **Negative controls**: 30,000 random protein pairs with no interaction evidence
- **Metric**: Precision-recall curves with $w_p = 0.01$ down-weighting to simulate 1:1000 proteome-wide signal-to-noise

#### Key Results

| Metric | Value |
|---|---|
| Predicted PPIs (90% precision) | 17,849 |
| Predicted PPIs (80% precision) | 29,256 |
| Previously unreported PPIs | 3,631 |
| Estimated recall | 8-22% (at 90% precision) |
| RF2-PPI AUCPR improvement over RF2-lite | 1.7x |
| RF2-PPI speed vs AF2 | ~20x faster |

#### Comparison Against Other Methods
- **RF2-PPI + omicMSA** slightly outperforms **ColabFold pipeline** in overall AUCPR
- **RF2-PPI** shows substantially better recall at high precision (80-90%) than all alternatives
- **AF2 + omicMSA** achieves best overall performance but is 20x slower
- **AFmm and AF3** perform worse at 1:1000 signal-to-noise (better at 1:10)
- RF2-PPI shows advantage in detecting **weak/transient interactions** (small interfaces)

#### Biological Validation
- Predicted PPIs enriched in transmembrane protein interactions (hard to detect experimentally)
- 4,950 PPIs with disease-associated variants at interfaces → molecular mechanism hypotheses
- Novel predictions: GPCR-effector interactions, innate immunity regulators, mitochondrial assembly factors
- 404 multi-protein complexes reconstructed, including:
  - Tubulin polyglutamylase (TPG) complex with 3 new subunits
  - GPI-GnT complex with ARV1 as additional subunit
  - MKS transition zone complex with TMEM138
- 139 additional components predicted for known complexes (Complex Portal database)

#### Database Precision Estimates
Using the overlap between AI predictions and external databases, the authors estimate precision of existing resources: PDB orthologous templates (~100%), STRING high-confidence (49-100%), UniProt (21-57%), HuRI (17-47%), BioGRID (6-16%), STRING genetic (1-3%).

---

### Reproducibility

**Rating: 3/5** (Partial reproducibility)

#### Strengths
- RF2-PPI model code and trained weights released on GitHub and Zenodo
- omicMSAs, training datasets, and predicted PPIs shared at conglab.swmed.edu/humanPPI
- Colab notebook provided for using omicMSAs with AF2
- Clear supplementary methods with inline DCA code

#### Weaknesses
- **Full pipeline not released**: omicMSA construction bioinformatics pipeline, DCA prefilter, AF2 integration, precision estimation, cutoff optimization, and hub removal are NOT in the GitHub repository
- **Training data not directly in repo**: Dataset preparation scripts absent; users must download from external servers
- **EMA not documented**: Exponential moving average (decay=0.99) used in training but not mentioned in paper
- **Junction trimming discrepancy**: Paper describes excluding 10 residues at chain boundary for interaction scoring; released inference code does not implement this
- **Computational resources**: Screening 200 million pairs required massive compute (thousands of GPU-hours); not feasible for most labs

#### Practical Notes
- Environment: Python 3.9, PyTorch 1.12.1, CUDA
- Model weights: ~150MB (RF2-PPI.pt)
- Inference requires paired MSAs in a3m format (generate with `generate_protein_pair_MSA.py`)
- GPU memory: fits proteins up to ~750 residues (crop size 256 for training)
- ~5% of predictions show >0.1 std in interaction probability across runs (noted in README)

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
