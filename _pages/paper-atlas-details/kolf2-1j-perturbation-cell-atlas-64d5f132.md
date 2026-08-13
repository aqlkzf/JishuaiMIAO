---
layout: default
permalink: /paper-atlas/kolf2-1j-perturbation-cell-atlas-64d5f132/
title: "KOLF2_1J_Perturbation_Cell_Atlas"
nav: false
description: "人诱导多能干细胞（hiPSC）能分化成多种细胞类型，但我们仍不知道大多数基因在“维持多能性”这件事中承担什么功能。过去的大规模 Perturb-seq 多集中在癌细胞系；hiPSC 中既缺少覆盖全表达基因组、又有足够单细胞深度的功能图谱。 作者在参考细胞系 KOLF2.1J 中，用 CRISPRi 扰动 11,692 个表达基因，获得超过 250 万个质控后的单细胞，并同步测量细胞适应度。"
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
      <span>Perturbation Resources</span>
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>KOLF2_1J_Perturbation_Cell_Atlas</h1>
    <p>A genome-scale CRISPRi perturbation atlas of human induced pluripotent stem cells</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/y-doctor/KOLF2.1J_Perturbation_Cell_Atlas" target="_blank" rel="noopener noreferrer" aria-label="Open code for KOLF2_1J_Perturbation_Cell_Atlas">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## KOLF2.1J 全基因组 CRISPRi 扰动图谱：方法详解

### 这篇文章解决什么问题？

人诱导多能干细胞（hiPSC）能分化成多种细胞类型，但我们仍不知道大多数基因在“维持多能性”这件事中承担什么功能。过去的大规模 Perturb-seq 多集中在癌细胞系；hiPSC 中既缺少覆盖全表达基因组、又有足够单细胞深度的功能图谱。

作者在参考细胞系 KOLF2.1J 中，用 CRISPRi 扰动 11,692 个表达基因，获得超过 250 万个质控后的单细胞，并同步测量细胞适应度。最终产品不是一个单纯的算法，而是四层资源：每个基因的转录表型、强扰动清单、基因功能相关网络/细胞状态地图，以及全基因组 A-to-I RNA 编辑调控筛选。

### 核心思想

难点在于：细胞数巨大、每个 sgRNA 的细胞数不同、非靶向对照本身也可能有异常，而且“扰动是否强”不能只看一个指标。

作者因此采用双重证据：

1. **Energy distance（Edist）**：看一个扰动后的整个人群分布，是否整体偏离对照，属于“全局状态变化”。
2. **差异表达（DE）**：看具体哪些基因发生变化，属于“局部、可解释的转录变化”。

只有两项都显著的扰动才进入下一步。随后把靶向同一基因的多个 sgRNA 合并，再重复一次 Edist 和 DE；这相当于用多个独立 guide 检查表型一致性。

### 完整计算流程

```text
Cell Ranger 表达矩阵 + sgRNA 分配
  ↓
只保留恰好一个 sgRNA 的细胞；去掉零表达基因和 MAD 异常细胞
  ↓
构造“核心 NTC 对照”
  fitness 中间 50% guide → 2,000 HVG → PCA → Harmony
  → isolation forest 去掉偏离正常状态的 NTC 细胞
  ↓
过滤弱扰动
  平均敲低 >30%；每个 sgRNA ≥25 个细胞；单细胞确实有靶基因抑制
  ↓
sgRNA 层面双检验
  Edist：同批次 400 个核心 NTC，10,000 次置换
  DE：抽取 85% 细胞形成 3 个 pseudo-replicate，用 DESeq2 比较 NTC
  ↓
按靶基因合并 sgRNA，重复双检验
  ↓
得到 1,665 个 strong perturbations
  ↓
选择 2,189 个 feature genes，计算每个扰动的平均表达向量
  ↓
Pearson 相关 → HDBSCAN 功能模块
  → spectral embedding + MDE 二维可视化 → Leiden 标注
```

### 为什么要特别清理 NTC？

NTC guide 理论上不靶向基因，但仍可能因脱靶、技术噪声或细胞状态异常产生表型。作者先用 fitness 筛掉异常 NTC guide，再用 Harmony 后的 PCA 表示和 isolation forest 去掉 30% 的离群 NTC 细胞。这样能让基线更稳定，但也可能删掉真实的对照异质性，因此这是一个需要迁移时重新校准的经验步骤。

### Edist 与 DESeq2 如何互补？

Edist 对整个表达分布敏感，但细胞数少时距离值可能偏大；DESeq2 能指出具体变化基因，但依赖 pseudo-bulk 构造和显著性阈值。作者每个扰动抽取 85% 细胞，生成三个 pseudo-replicate，并从同批 NTC 中抽同样数量的细胞。除此之外，他们用 NTC-vs-NTC 检验估计每批次的“假 DEG 数”上限，而不是盲目采用统一 DEG 数阈值。

这种“全局距离 + 局部差异基因 + 同靶多 guide 再检验”的组合，是 PASTA 流程最值得复用的部分。

### 如何从强扰动构建功能地图？

作者把每个 strong perturbation 的细胞求平均，得到一个 1,665 × 2,189 的扰动—特征基因矩阵。特征基因来自每个扰动最强的上/下调基因与高变基因的并集。然后计算扰动之间的 Pearson 相关：如果敲低两个基因引起相似的转录反应，它们可能处于同一蛋白复合物、通路或细胞功能模块。

HDBSCAN 在原始相关矩阵上给出 30 个保守模块；MDE 负责把高维关系画到二维，Leiden 用于给二维图分区。二维图直观，但会失真，而且 Leiden 参数还被调到尽量符合 HDBSCAN，所以真正更可靠的证据仍是相关矩阵和已知 CORUM/PPI 富集。

### 两条重要的平行分析

#### 细胞适应度

MAGeCK 比较 day 6/day 14 与质粒库中的 guide 丰度，并标准化为

$$\mathrm{Fitness}\,\mathrm{score}=Z=(X-\mu)/\sigma.$$

其中 $X$ 是 log2 fold change。day 14 能发现更多随时间积累的必需基因效应。

#### A-to-I RNA 编辑

作者把约 1450 亿条 reads 按细胞 barcode 和扰动拆分：96 个原始 BAM 被分解、重并为 24,051 个扰动级 BAM，再用 RNAEditingIndexer 计算 Alu editing index。每个 sgRNA 的 AEI 在同批 NTC 中标准化，基因层面取 guide 均值，并用 100,000 次置换检验。该分支发现 DBR1 敲低显著提高 RNA 编辑，并通过后续实验验证其机制。

### 结果为什么可信？

- 扰动和特征基因相关性能够恢复 CORUM 蛋白复合物。
- 适应度结果与独立 hiPSC CRISPRi 研究显著相关。
- ZBTB41、RNF7、DBR1 都经过代谢示踪、RNA-seq、显微成像、蛋白互作或免疫印迹等正交实验验证。
- 代码仓库包含 QC、pseudo-bulk DESeq2、Edist/相关、HDBSCAN/MDE 以及完整 BAM-to-AEI 工具，而不仅是画图脚本。

### 使用时要注意

这是一张“单一遗传背景、单一培养状态下的深图谱”。它对 KOLF2.1J 很有价值，但不能直接代表所有供体或分化状态。NTC 清理、固定 2,189 个特征基因、HDBSCAN/MDE 参数都会影响地图形状。仓库也不是一键运行：大规模数据在 SRA/Figshare，RNA 编辑脚本依赖特定 SLURM 环境，最终图表逻辑分散在大型 notebook 中。因此最合适的使用方式是把它作为高质量参考和假设生成器，再在目标细胞背景中验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## KOLF2.1J perturbation cell atlas

### Problem

Functional genomics in human induced pluripotent stem cells has lagged behind cancer-cell screens, leaving most gene functions and pluripotency-specific interactions unmapped. This paper builds a deeply sampled reference atlas in one widely used hiPSC line and asks whether perturbation-induced single-cell transcriptomes can recover functional modules and expose new regulators.

### Resource and computational contribution

The study targets 11,692 expressed genes with CRISPRi and profiles more than 2.5 million single cells, alongside day-6/day-14 fitness measurements. Its PASTA-style analysis first constructs a clean NTC reference, filters low-coverage or weakly repressed guides, and calls perturbation strength using two complementary tests: energy distance for global transcriptome shifts and pseudobulk DESeq2 for gene-local shifts. The tests are repeated after guide profiles are pooled by target gene, producing 1,665 strong perturbations.

Strong perturbations are represented by mean profiles over 2,189 selected feature genes. Pearson correlations, HDBSCAN and a spectral/MDE visualization organize these profiles into functional modules. CORUM-linked genes are substantially more correlated than unrelated pairs, and the resulting map recovers known complexes and pluripotency-related programs. The atlas prioritizes ZBTB41 as a mitochondrial-metabolism regulator and RNF7 as a pluripotency regulator; metabolic tracing, protein-interaction assays, RNA-seq and imaging provide orthogonal validation.

The authors also reuse the dataset as a genome-scale A-to-I editing screen. Roughly 145 billion reads are demultiplexed from Cell Ranger BAMs into 24,051 perturbation-specific BAMs, quantified by RNAEditingIndexer and tested with batch-standardized AEI statistics. This identifies DBR1 as a strong regulator and links its perturbation to increased editing and altered cell state.

### Evaluation and evidence

- Scale: 11,692 genes, three guides per gene, 478 NTC guides and >2.5 million filtered cells.
- Technical coverage: 88% of perturbations have >25 cells; 80% exceed 30% mean knockdown.
- Biological recovery: perturbation and feature-gene correlations enrich known CORUM complexes; 30 HDBSCAN modules include mitochondrial translation, Mediator, SAGA, Integrator and pluripotency programs.
- Fitness validity: KOLF2.1J fitness effects correlate with an independent hiPSC CRISPRi study ($r=0.713$, $P<0.0001$).
- Context specificity: comparison with K562 and a multi-line hiPSC atlas shows both shared machinery and strong cell-type/genetic-background dependence.
- Experimental validation: ZBTB41, RNF7 and DBR1 receive focused orthogonal follow-up rather than remaining computational candidates.

### Reproducibility

Reproducibility is **4/5**. The public repository contains reusable QC, differential-expression, Edist/correlation, clustering/MDE and RNA-editing utilities, extensive figure notebooks, derived web-atlas data and the deployed browser. Raw reads are in SRA (PRJNA1173491), and the aggregated AnnData is on Figshare. Direct code-paper fidelity is medium-high.

The main deductions are operational rather than conceptual: there is no portable single-command workflow, several final parameters are notebook-selected rather than encoded in one configuration, the RNA-editing branch contains site-specific SLURM paths, and the full analysis requires very large external inputs and compute. The linked supplementary PDF was not converted locally, so this analysis uses the complete Nature HTML paper, all 14 local figure images and direct code reads.

### Limitations

The atlas is exceptionally deep but centered on one cell line and culture state. Control pruning can remove genuine heterogeneity; fixed feature selection can miss perturbation-specific effects; HDBSCAN and tuned 2D Leiden/MDE summaries do not define unique biological boundaries. The strongest use of the resource is therefore hypothesis generation and contextual comparison, followed by targeted validation—as demonstrated for ZBTB41, RNF7 and DBR1.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
