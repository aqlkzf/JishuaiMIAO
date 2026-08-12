---
layout: default
permalink: /paper-atlas/cellstaar-433c4fb5/
title: "cellSTAAR"
nav: false
description: "cellSTAAR 把单细胞染色质可及性同时用于“选择哪些非编码罕见变异进入集合”和“给哪些变异更高权重”，再用 ACAT 对多个不确定的 cCRE–gene 链接结果做稳健集成，从而提高非编码 RVAT 的功效并增强细胞类型层面的可解释性。"
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
      <span>Computational Tools</span>
      <span>Nature Methods · 2026</span>
    </div>
    <h1>cellSTAAR</h1>
    <p>cellSTAAR: incorporating single-cell-sequencing-based functional data to boost power in rare variant association testing of noncoding regions</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## cellSTAAR 方法详解

### 1. 它要解决什么问题？

cellSTAAR 面向一个很具体但长期棘手的问题：如何在全基因组测序（WGS）数据中，检验**非编码调控元件里的罕见变异集合**是否与表型相关。

单个位点检验很难发现罕见变异，因为携带者太少；因此通常要把一个基因相关区域内的多个变异聚合起来做 rare variant association test（RVAT）。但非编码区域又带来两层额外不确定性：

1. 同一个 enhancer/promoter 是否活跃，强烈依赖细胞类型。bulk ATAC-seq 把多种细胞平均后，可能把真正的细胞类型差异冲淡。
2. 一个调控元件究竟作用于哪个基因并不确定。距离、三维染色质接触、eQTL、表达—表观相关性等方法可能给出不同答案。

因此，cellSTAAR 的目标不是简单地“给 STAAR 加一个单细胞注释”，而是同时处理：

- **哪些变异应该进入某个细胞类型的检验集合；**
- **集合内哪些变异应该权重更高；**
- **同一调控元件可能链接到哪些基因。**

### 2. 现有方法为什么不够？

- Burden test（*Genetic Epidemiology*, 2010）把多个罕见变异按同方向聚合，面对效应方向相反时会损失功效。
- SKAT（*American Journal of Human Genetics*, 2011）允许效应方向和大小不同，但本身不解决细胞类型和调控元件—基因链接问题。
- ACAT（*American Journal of Human Genetics*, 2019）适合在相关的 p 值之间做稳健组合，但它是一种组合机制，不会自动构造生物学上合理的 variant set。
- STAAR（*Nature Genetics*, 2020）把多种功能注释加入 burden、SKAT 和 ACAT-V，并用 GLMM 处理群体结构与亲缘关系；不过原始 STAAR 并不使用单细胞 ATAC 数据来定义细胞类型特异的集合，也没有对多个 cCRE–gene 链接方案做外层集成。
- STAARpipeline（*Nature Methods*, 2022）提供可扩展的非编码 WGS 分析框架，但仍不能同时表达细胞类型异质性和链接方法的不确定性。

### 3. 核心思想：两个层次的“组合”

理解 cellSTAAR 最重要的一点，是分清内外两个统计层次。

#### 内层：固定一个链接方案后运行 STAAR-O

先固定：

> 一个表型 × 一个细胞类型 × 一个 cCRE 类别 × 一个基因 × 一个 element–gene linking 方法

在这个固定集合内，STAAR 利用两种 MAF 权重和多种功能注释，分别计算 burden、SKAT 和 ACAT-V，再通过 ACAT 得到一个 STAAR-O p 值。论文记作：

$$
P_{\mathrm{STAAR}-O}\equiv P_{\mathrm{cellSTAAR},m},
$$

其中 (m) 表示当前使用的链接方法。

#### 外层：跨链接方案组合

同一个 enhancer 可能通过距离、ABC、EpiMap、SCREEN-eQTL 或 SCREEN-3D 被链接到基因。cellSTAAR 不要求研究者事先赌定唯一正确的方法，而是用 ACAT 再组合这些 (P_{\mathrm{cellSTAAR},m})，得到最终的：

$$
P_{\mathrm{cellSTAAR}}.
$$

因此，内层处理的是“检验形式和功能权重的不确定性”，外层处理的是“调控元件—基因链接的不确定性”。

### 4. 从输入到输出的完整流程

```text
WGS 基因型 + 表型/协变量 + 稀疏 GRM
                    |
                    |      单细胞 ATAC-seq 的 .bed peaks / .bigwig tracks
                    |                         |
                    |            细胞类型功能注释 + 活跃位置集合
                    |                         |
ENCODE PLS/pELS/dELS + 多种 element-gene links
                    |                         |
                    +------> 基因 × 细胞类型的 variant set
                                      |
                         拼接细胞类型注释和通用功能注释
                                      |
                    每个 linking method 分别运行 STAAR/STAAR_cond
                                      |
                         六个距离窗口先做指数衰减 ACAT
                                      |
                   再与 ABC/EpiMap/SCREEN 等做外层 ACAT
                                      |
              每个基因 × 细胞类型 × 表型 × cCRE 类别的最终 p 值
```

#### 步骤 1：准备零模型

对于无亲缘样本，论文使用 GLM：

$$
g(\mu_i)=\alpha_0+{\boldsymbol X}_i^T{\boldsymbol\alpha}+{\boldsymbol G}_i^T{\boldsymbol\beta}.
$$

对于相关样本，加入随机效应：

$$
g(\mu_i)=\alpha_0+{\boldsymbol X}_i^T{\boldsymbol\alpha}+{\boldsymbol G}_i^T{\boldsymbol\beta}+b_i.
$$

检验目标始终是：

$$
H_0:{\boldsymbol\beta}={\boldsymbol 0}.
$$

稀疏 GRM 用来校正亲缘关系和剩余群体结构。代码不会自己拟合零模型；用户要先用 STAAR 包得到 `glm` 或 `glmmkin` 对象，再传给 `run_cellSTAAR()`。

#### 步骤 2：把 scATAC track 变成细胞类型功能权重

对每种细胞类型，cellSTAAR 读取 bigWig 的位置级 accessibility score；如果有重复样本，就按位置等权平均。论文把 score 转为 PHRED 排名：

$$
-10\log_{10}\left(\frac{\operatorname{rank}(-\mathrm{score})}{T}\right).
$$

可及性越强，PHRED 注释越高，变异在 STAAR 中可获得更高功能权重。这样做主要依赖排序，而不是不同 peak caller 的绝对分数尺度。

代码细节需要注意：`create_ct_annotations()` 会把零值/缺失值固定为 0.01，并用当前输出长度作排名分母；函数通常按染色体运行，所以不一定严格等同于论文写的全基因组 (T)。

#### 步骤 3：构造细胞类型特异的 variant set

论文把以下两个条件取并集：

- 位于该细胞类型的 ATAC peak 内；
- 位于该细胞类型 bigWig 非零分数的前 20%。

这个设计同时保留稳定的 peak 和 peak 附近高信号区域，减少对某个 peak-calling 阈值的依赖。

源码确实把 BED peak 展开到碱基层级，并与高分 track 位置取并集；但它先在含零向量上计算 0.8 分位数，再要求分数大于零。如果零值很多，实际保留集合可能大于“非零分数前 20%”。

#### 步骤 4：把 cCRE 链接到基因

论文用 ENCODE version 3 的三类互斥元件：

- PLS：promoter-like signature；
- pELS：proximal enhancer-like signature；
- dELS：distal enhancer-like signature。

对于 pELS/dELS，链接方式包括：

- 六个互斥距离窗口：基因内部、0–50 kb、50–100 kb、100–150 kb、150–200 kb、200–250 kb；
- ABC；
- EpiMap；
- SCREEN-eQTL；
- SCREEN-3D。

对于 PLS，只使用 0–4 kb、SCREEN-eQTL 和 SCREEN-3D。

在论文分析里，ABC/EpiMap/SCREEN 的 link 数据并不随细胞类型改变；细胞类型差异来自 ATAC 定义的活跃位置和功能权重。`create_cellSTAAR_mapping_file()` 最后保存稀疏的“变异位置 × 基因”逻辑矩阵。

#### 步骤 5：对每个链接方案运行 STAAR-O

在一个具体基因和细胞类型中，代码取出：

- 该 variant set 的基因型矩阵；
- 细胞类型 PHRED 注释；
- CADD、LINSIGHT、FATHMM 和 FAVOR aPC 等通用注释。

然后调用外部 STAAR 包。论文的 variant-level 因果概率权重写作：

$$
\hat{\pi}_{jk}=\frac{\operatorname{rank}(A_{jk})}{T},
$$

并使用 Beta(1,25) 与 Beta(1,1) 两种 MAF 权重。对应的 burden 和 SKAT 统计量为：

$$
Q_{\mathrm{Burden},l,k}=\left(\sum_{j=1}^{P}\hat{\pi}_{jk}w_{jl}S_j\right)^2,
$$

$$
Q_{\mathrm{SKAT},l,k}=\sum_{j=1}^{P}\hat{\pi}_{jk}w_{jl}^{2}S_j^{2}.
$$

这些统计量连同 ACAT-V 先在注释和 MAF 权重间组合，再合成当前链接方式的 STAAR-O p 值。

#### 步骤 6：条件分析

论文对已知 GWAS lipid signals 做 LD pruning 后进行条件分析。包内实现要求用户先提供 conditioning variants；`run_cellSTAAR()` 会寻找测试区域前后 ±1 Mb 的候选位点，将落在当前 variant set 内的 conditioning variant 从被检验矩阵中移除，然后调用 `STAAR_cond(method_cond="naive")`。

因此，条件检验本身在包里，但论文使用的 GWAS Catalog 筛选和 LD pruning 流程不在这个仓库快照中。

#### 步骤 7：链接方法的外层 ACAT

增强子六个距离窗口先按距离终点做指数衰减：

$$
w_d=\exp(-\lambda\,\mathrm{end}_d),\quad \lambda=10^{-5}.
$$

默认权重大约是 41.4%、25.1%、15.2%、9.2%、5.6%、3.4%，距离越近权重越高。六个距离 p 值先合成一个 distance p 值，再与 ABC、EpiMap、SCREEN-eQTL、SCREEN-3D 等权 ACAT。PLS 则在三个链接方式间等权组合。

代码会删除缺失 component p 值并重新归一化剩余权重，因此部分链接方式没有结果时仍可能给出 omnibus p 值。

### 5. 实验如何验证？

#### 模拟

模拟比较了 burden、SKAT、ACAT-V、STAAR 和 cellSTAAR。作者用 10,000 个个体和 5-kb 区域：

- 用 (10^8) 次重复评估 (10^{-3}) 到 (10^{-6}) 的一类错误，cellSTAAR 基本保持 nominal；
- 用 (10^4) 次重复评估功效，改变因果变异比例（5%、15%、35%）和效应方向比例（50%、80%、100% 正向）。

在报告的设置中，cellSTAAR 的功效持续高于对照。这一优势同时来自：更干净的细胞类型注释、优先保留因果变异的活跃集合、以及多个 linking method 的 ensemble。

#### TOPMed 与 UK Biobank

作者分析 LDL-C、高 LDL-C、HDL-C 和 triglycerides：TOPMed Freeze 8 约 6 万人为 discovery，UKB 约 18–19 万人为 replication，并使用 19 种 CATlas 细胞类型。

关键结果包括：

- 条件分析在 APOA1、CETP、APOE 等脂质相关区域发现并复制信号；
- APOE 附近同一 pELS 信号会因 linking method 不同而链接到 APOE、APOC2 或 APOC4；
- 显著性集中在 hepatocyte、fetal hepatoblast、fetal hepatic endothelial、adipocyte 等脂质相关细胞类型；
- 三个 bulk liver ATAC 样本没有恢复 Fig. 2 中的强信号；
- Fig. 3 中相关肝细胞类型在 TOPMed 和 UKB 都位于 enrichment 排名的前端；
- 用 Tabula Sapiens scRNA-seq 和 IHW 加权后，发现数反而略有减少，说明“高表达”不等同于“该基因的罕见调控变异与脂质相关”。

### 6. 应该怎样解释一个显著结果？

一个显著的 `cellSTAAR_pvalue` 表示：

> 在给定表型、细胞类型、cCRE 类别和基因下，多个链接方案的集合中存在稳健的罕见变异关联证据。

它不表示：

- 已经确定唯一的 causal variant；
- 已经确定唯一的 target gene；
- 富集最高的 cell type 就是唯一 causal cell type。

cellSTAAR 的价值恰恰是保留并量化这些不确定性，为后续 locus-level 分析和实验验证提供优先级。

### 7. 代码可复现性与隐藏细节

本 workspace 的代码是 `edvanburen/cellSTAAR` commit `e37bd94dea4155a0ad98a0f5f97f1367e96d2bf2`，R 包版本 1.0.1。核心包与论文的匹配度为 **medium**：映射、STAAR/STAAR_cond 调用和 ACAT 聚合均可直接对应，但整篇分析不是一键复现。

需要特别留意：

- `run_cellSTAAR()` 虽然接受 `rare_maf_cutoff`，但后段把它重新设为 0.01，非默认输入不会生效；
- 少于两个变异的 gene/cell-type set 不运行 STAAR；
- STAAR/STAAR_cond 的异常被空 `tryCatch` 吞掉，结果表现为 NA，诊断信息不足；
- 包内没有 TOPMed/UKB 全流程脚本、scRNA/IHW 实现、论文作图脚本或数值单元测试；
- 论文另行引用 Zenodo 的 analysis code，而本 workspace 获取的是核心 GitHub R 包；
- 精确复现仍需受控访问的 TOPMed/UKB 数据、正确的 GDS/GRM/null model、CATlas 数据和上游 QC。

论文报告的计算资源也不低：19 个细胞类型的 HDL-C 分析在 TOPMed 上使用 100 cores 耗时 14.41 h、峰值内存 41.52 GB；UKB 上耗时 156.8 h、峰值内存 62.07 GB。

### 8. 一句话总结

cellSTAAR 把单细胞染色质可及性同时用于“选择哪些非编码罕见变异进入集合”和“给哪些变异更高权重”，再用 ACAT 对多个不确定的 cCRE–gene 链接结果做稳健集成，从而提高非编码 RVAT 的功效并增强细胞类型层面的可解释性。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## cellSTAAR

**Paper:** *cellSTAAR: incorporating single-cell-sequencing-based functional data to boost power in rare variant association testing of noncoding regions*
**Journal/year:** *Nature Methods* (2026)
**DOI:** `10.1038/s41592-025-02919-5`

### Problem

Rare noncoding variants are individually underpowered and difficult to group into biologically meaningful tests. Candidate cis-regulatory elements (cCREs) are often active only in particular cell types, but bulk epigenomic assays average across cells. Their target genes are also uncertain: distance, chromatin contact, expression correlation and eQTL evidence can assign the same element to different genes. Existing gene-centric RVATs generally do not address both cell-type heterogeneity and element–gene-link uncertainty at once.

### Limits of existing approaches

- Burden tests (*Genetic Epidemiology*, 2010) and SKAT (*American Journal of Human Genetics*, 2011) aggregate rare variants but do not by themselves use rich cell-type functional information.
- ACAT (*American Journal of Human Genetics*, 2019) flexibly combines dependent p-values but is a combination mechanism rather than a cell-type-aware noncoding RVAT.
- STAAR (*Nature Genetics*, 2020) improves power by incorporating multiple functional annotations and GLMMs for related, multi-ancestry samples, but the original framework does not model scATAC-defined cell-type variant sets or ensemble uncertainty across cCRE–gene links.
- STAARpipeline (*Nature Methods*, 2022) scales noncoding WGS analysis, yet uses regulatory definitions/linking choices that do not capture the full cell-type and link-method variability targeted here.

### Proposed method

cellSTAAR extends STAAR in three ways:

1. It converts single-cell ATAC-seq bigWig tracks into cell-type-specific PHRED-ranked variant annotations, which up-weight variants active in a chosen cell type.
2. It creates cell-type-specific gene-centric variant sets by retaining ENCODE PLS/pELS/dELS bases that fall in an ATAC peak or a high positive accessibility-track region.
3. It runs STAAR-O separately under multiple element–gene links, then uses ACAT to produce a robust omnibus p-value.

Enhancers use six distance windows plus ABC, EpiMap, SCREEN-eQTL and SCREEN-3D; the distance windows are first combined with exponential decay. Promoters use 0–4 kb, SCREEN-eQTL and SCREEN-3D. Each link-specific STAAR-O p-value already combines burden, SKAT and ACAT-V across MAF and functional-annotation weights. The outer combination therefore addresses a distinct uncertainty: which element–gene mapping should define the variant set.

```text
WGS + phenotype/covariates + sparse GRM
              +
cell-type scATAC peaks/tracks + ENCODE cCREs + gene links
              |
cell-type annotations and active gene-centric variant sets
              |
STAAR-O per gene x cell type x cCRE class x linking method
              |
distance-decay ACAT -> cross-link ACAT
              |
one cellSTAAR p-value per gene/cell type/trait/cCRE class
```

### Evaluation

#### Simulations

The authors compared burden, SKAT, ACAT-V, STAAR and cellSTAAR using coalescent-simulated sequence data, 10,000 individuals and 5-kb test regions. Type-I error used (10^8) replicates at thresholds (10^{-3})–(10^{-6}) and remained near nominal. Power simulations varied causal-variant proportions and effect directions; cellSTAAR was consistently more powerful in the reported settings because its simulated cell-type annotations were less diluted and its variant sets preferentially retained causal variants.

#### TOPMed and UK Biobank

The method was applied to LDL-C, high LDL-C, HDL-C and triglycerides using TOPMed Freeze 8 for discovery (about 60,000 individuals, phenotype dependent) and UK Biobank WGS for replication (about 180,000–190,000). Nineteen CATlas cell types were analyzed.

At the paper's Bonferroni discovery threshold of (3.01\times10^{-7}) and replication (P<0.05), conditional analyses recovered or extended associations at lipid-related loci including APOA1, CETP and APOE. At the APOE locus, pELS evidence varied across APOE, APOC2 and APOC4 depending on the link method, and strong results concentrated in lipid-relevant single-cell types while three bulk-liver ATAC comparisons were weak. Genome-wide enrichment similarly ranked fetal hepatoblasts, fetal hepatic endothelial cells and hepatocytes near the top in both TOPMed and UKB. An attempted scRNA-seq/IHW extension slightly reduced rather than increased discoveries.

### Interpretation

cellSTAAR's main contribution is not a new causal-gene resolver. It is a robust association-testing layer that preserves uncertainty: a significant omnibus p-value means that the gene/cCRE/trait combination has evidence under the ensemble, while locus-specific experiments are still needed to establish the causal variant and gene. Cell-type rankings are useful biological prioritization signals, not proof that a cell type is causal.

### Reproducibility

**Reproducibility rating: 3/5 (moderate).**

The archived GitHub snapshot is a usable R package (version 1.0.1, commit `e37bd94dea4155a0ad98a0f5f97f1367e96d2bf2`) containing the central functions for annotation construction, cCRE/gene mapping, STAAR/STAAR_cond execution and ACAT aggregation. Direct source review supports a **medium** paper–code match: Exact 3, Partial 3, Inferred 1, Not found 2.

Important qualifications:

- the package is not the full TOPMed/UKB analysis workflow; cohort preprocessing, 19-cell-type drivers, result tables, scRNA/IHW code and figure scripts are absent and the paper cites a separate Zenodo archive;
- tests contain no numerical assertions;
- zero/missing track values are fixed to 0.01 and PHRED ranks use the current function-output length;
- the variant-set 0.8 quantile is calculated before zero scores are excluded, which can differ from “top 20% of nonzero scores”;
- `run_cellSTAAR()` accepts `rare_maf_cutoff` but resets it to 0.01 before testing; and
- STAAR errors are converted to missing result rows without preserving diagnostic messages.

The core algorithm can be reused with correctly prepared GDS genotypes, null models, annotations and ATAC/link resources, but exact reproduction of the manuscript requires controlled-access TOPMed/UKB data and the separately archived analysis layer.

### Main limitations

- No gold-standard enhancer–gene linking exists; ACAT improves robustness but cannot identify the true target gene.
- Available single-cell resources cover limited tissues/cell types and may contain noisy or unreplicated measurements.
- Choosing candidate cell types remains phenotype dependent.
- Runtime is substantial: the reported 19-cell-type HDL-C analyses required 14.41 h/41.52 GB for TOPMed and 156.8 h/62.07 GB for UKB using 100 cores.
- Gene-expression side information from unmatched healthy scRNA-seq data did not materially improve discovery, showing that additional single-cell modalities must be context appropriate.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
