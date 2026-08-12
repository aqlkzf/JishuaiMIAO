---
layout: default
permalink: /paper-atlas/aneuploidy-driver-genes-breast-cancer-fb4ab463/
title: "Aneuploidy_Driver_Genes_Breast_Cancer"
nav: false
description: "基底样乳腺癌（BLBC）的染色体臂拷贝数改变（CNA）很常见，但一条染色体臂同时改变许多基因；仅凭复发频率不能判断究竟哪一个基因带来选择优势。本文先在 METABRIC、TCGA 和单细胞数据中找出 BLBC 特异的染色体臂改变，再在小鼠体内逐基因功能筛选。 CRISPR-KOALA 将同一类体内筛选做成双向操作： 敲除分支使用普通 20-bp sgRNA；"
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
      <span>Data Sources &amp; Technologies</span>
      <span>Nature · 2026</span>
    </div>
    <h1>Aneuploidy_Driver_Genes_Breast_Cancer</h1>
    <p>Aneuploidy selects for the acquisition of driver genes in breast cancer</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## 方法解读：非整倍体如何获得乳腺癌驱动基因

### 要解决的问题

基底样乳腺癌（BLBC）的染色体臂拷贝数改变（CNA）很常见，但一条染色体臂同时改变许多基因；仅凭复发频率不能判断究竟哪一个基因带来选择优势。本文先在 METABRIC、TCGA 和单细胞数据中找出 BLBC 特异的染色体臂改变，再在小鼠体内逐基因功能筛选（`paper.md:36-62`）。

### 核心创新：CRISPR-KOALA

CRISPR-KOALA 将同一类体内筛选做成双向操作：

```text
BLBC CNA 图谱
  -> 选择 10 条高特异、高复发的染色体臂
  -> 缺失臂：20-bp sgRNA 敲除候选抑癌基因
     扩增臂：14-bp dead-guide RNA + PP7/PCP–P65–HSF1 激活候选癌基因
  -> 乳腺导管内递送到 Cas9 易感小鼠
  -> 肿瘤形成、gRNA 测序、富集与 MAGeCK 分析
  -> 高/低穿透率 CNA 驱动基因
```

敲除分支使用普通 20-bp sgRNA；激活分支以 14-bp dgRNA 保留 Cas9 靶向但消除切割，并通过 PP7 适配体招募转录激活模块（`paper.md:50-56`）。图 1 的可视化把 CNA 选择、文库构建、乳腺导管注射、肿瘤测序和 KO/激活两个分支串成一条流程（`images/figure_01.png`）。

### 如何选 CNA、如何判定命中

每条染色体臂的特异性分数，是该臂上“改变比例比所有亚型均值高 1.645 个标准差”的基因所占比例；分数为 1 表示该臂所有基因都满足条件（`paper.md:44`）。文章结合该分数与患者中的出现比例筛选候选臂（Extended Data Fig. 1，`images/figure_06.jpg`）。

对十个臂的 3,752 个基因，作者构建 5 个 KO 和 4 个激活文库；小鼠肿瘤终点的 gRNA 富集是主要读出，MAGeCK 则补充较低穿透率或亚克隆的命中（`paper.md:62-82`）。图 2 显示从文库到测序、按染色体坐标的命中散点图、命中基因/邻近基因对照，以及人源模型验证（`images/figure_02.png`）。

### 主要结论

- 每个 CNA 通常并非只有一个基因起作用，而是有 1–2 个主导驱动基因和多个较低穿透率驱动基因（`paper.md:65,91`）。
- 直接调控这些驱动基因可缩短肿瘤潜伏期；不同驱动基因造成相异的转录状态，但小鼠肿瘤整体与人 BLBC 对应（`paper.md:97-117`；`images/figure_03.png`）。
- 若直接给到驱动改变，肿瘤获得额外非整倍体的需求下降；图 4 的 driver 组 FGA 与染色体改变轨迹更稀疏（`paper.md:120-137`；`images/figure_04.png`）。这支持“CNA 受选择是为了获得其中的驱动基因”这一模型。

### PLGRKT 例子

PLGRKT 是 chr9p 的主要激活命中。cDNA 过表达也能促进肿瘤，且不能激活纤溶酶原的突变体仍具促癌作用，说明该效应不依赖经典的细胞表面纤溶/ECM 功能（`paper.md:146-166`）。文章进一步观察到 PLGRKT 在线粒体定位、应激下维持线粒体动力学、降低 OXPHOS、提高糖酵解补偿并增强 ROS 解毒（`paper.md:169-202`；`images/figure_05.png`, `figure_15.jpg`–`figure_17.jpg`）。

### 本地代码能与论文对应到哪里？

现有快照只覆盖人单细胞 CNA 的一小段：

| 论文环节 | 本地代码证据 | 结论 |
|---|---|---|
| scRNA-seq 整合 | scVI 预处理/训练：`brca_integration.py:9-55`；CellAssign、scANVI、UMAP：`57-96` | 部分对应 |
| FGA 与 CNA 调用 | inferCNVpy 输出阈值、FGA：`cna_arm_analysis.Rmd:11-76`；臂水平调用与克隆性：`80-280` | 对应单细胞分析环节 |
| CRISPR-KOALA、MAGeCK、CNA 特异性、WGS、PLGRKT 下游 | 已检索 `blbc_cna/` 两个实质文件与 README | `Not found` |

代码还缺少原始 H5AD、marker matrix、inferCNVpy 的运行步骤、元数据、环境文件和可移植路径。因此它不能重现论文的主筛选，也不能直接端到端重跑所含单细胞分析。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Aneuploidy selects for the acquisition of driver genes in breast cancer

### Takeaway

This *Nature* (2026) study argues that recurrent chromosome-arm CNAs in basal-like breast cancer (BLBC) are selected because they alter particular driver genes, not merely because whole-arm aneuploidy is advantageous. It introduces CRISPR-KOALA, an in vivo pooled platform that can knock out genes on deleted arms or activate genes on gained arms (`paper.md:36-62`).

### Why existing approaches were insufficient

Association studies can identify recurrent CNAs but cannot resolve the causal gene(s) among many co-altered loci; conventional in-vitro screens can also miss context-dependent drivers. The study therefore couples subtype-specific CNA selection with in vivo functional screening (`paper.md:36,79-91`).

### What the paper adds

CRISPR-KOALA uses 20-bp sgRNAs for knockout and 14-bp dead-guide RNAs plus a PP7/PCP–P65–HSF1 activator for gene activation (`paper.md:50-56`). Across ten recurrent BLBC arms, the authors screened 3,752 genes in 471 mice, sequenced 1,478 tumours, and identify a hierarchy of dominant and lower-penetrance drivers (`paper.md:62-82`). Figure 1 visually depicts the subtype-selection, library, intraductal injection, and tumour-latency flow; Figure 2 shows the post-screen ranking and validation (`images/figure_01.png`, `images/figure_02.png`).

Selected perturbations accelerated tumour onset, while cross-species transcriptional analyses linked mouse driver tumours to human basal-like tumours (`paper.md:97-117`). WGS results support the model that directly perturbing a CNA driver reduces the need to accumulate aneuploidy (`paper.md:120-137`; `images/figure_04.png`). PLGRKT is developed as a chr9p oncogene whose reported phenotype involves mitochondrial localization, stress resilience, glycolytic compensation, and ROS detoxification rather than its canonical plasminogen role (`paper.md:163-202`; `images/figure_05.png`).

### Evaluation evidence

Evidence spans two mouse BLBC genetic backgrounds, human MCF10A/4T1 experiments, METABRIC/TCGA analyses, WGS, transcriptomics, and a human scRNA-seq analysis. Key figures directly inspected include all main and Extended Data figures (`images/figure_01.png`–`figure_17.jpg`); their visual results are indexed in `figure_analysis.md`.

### Reproducibility assessment: 2/5

The acquired GitHub snapshot (`blbc_cna`, commit `9747824c878aa0e63046371de0f00c1b1402c510`) partially supports the paper's human single-cell component: scVI/scANVI integration and CellAssign annotation (`brca_integration.py:9-96`), plus inferCNVpy-output FGA, arm-call, and clonality analysis (`cna_arm_analysis.Rmd:11-280`). It does **not** contain the CRISPR-KOALA library/screen, gRNA deconvolution, MAGeCK, CNA-specificity, WGS, transcriptomic, or PLGRKT analysis code. Raw data, environment specification, marker matrix, inferCNVpy execution, and portable paths are also `Not found` in this snapshot. No supplementary Markdown was acquired.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
