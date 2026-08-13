---
layout: default
permalink: /paper-atlas/pivot-a56f602d/
title: "PIVOT"
nav: false
wide: true
description: "传统植物遗传筛选通常是“一株植物对应一个基因扰动”。这种模式耗时、占空间，而且在多倍体、基因家族高度冗余、突变致死或生命周期很长的物种中尤其困难。把很多候选基因混在一起送入叶片虽然能提高通量，却会产生新的归因问题：同一个细胞若同时收到多个扰动，就无法知道表型由哪个基因造成。"
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
      <span>Nature Biotechnology · 2026</span>
    </div>
    <h1>PIVOT</h1>
    <p>A single-cell screening platform accelerates functional genetics in plants</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## PIVOT：把一片叶子变成单细胞功能遗传筛选器

### 它解决什么问题？

传统植物遗传筛选通常是“一株植物对应一个基因扰动”。这种模式耗时、占空间，而且在多倍体、基因家族高度冗余、突变致死或生命周期很长的物种中尤其困难。把很多候选基因混在一起送入叶片虽然能提高通量，却会产生新的归因问题：同一个细胞若同时收到多个扰动，就无法知道表型由哪个基因造成。

PIVOT（protoplast isolation after virus overexpression *in planta*）的目标是同时做到两点：一片叶中覆盖大量细胞，并让每个细胞主要承载一个可追踪的基因查询。

### 核心创新

PIVOT 把两个模块接在一起。

第一，使用烟草花叶病毒衍生的 pTRBO 载体递送带条形码的基因。病毒的“超感染排斥”会阻止同类病毒再次占据已经感染的细胞，而病毒运动蛋白又能让最先建立的扰动向邻近细胞扩散。因此叶片形成大面积、彼此分开的单扰动区域，缓解了传统载体“高浓度多重感染、低浓度覆盖不足”的矛盾。

第二，把生物学表型转换成细胞表面的磁性分选标签。研究者让目标通路响应型启动子驱动一个包含信号肽、HaloTag、跨膜结构域和 mCherry 的报告器。通路被候选基因激活时，HaloTag 出现在细胞表面；制备原生质体后，用 HaloTag–生物素配体和链霉亲和素磁珠捕获这些细胞，这一步称为 MAPS（magnetic-activated protoplast sorting）。

### 从输入到输出

```text
选择候选 ORF 和通路响应型启动子
  ↓
每个 ORF 添加唯一 10-nt 条形码，克隆进含内含子的 pTRBO
  ↓
把验证后的质粒等量混池并转入农杆菌
  ↓
候选库与表面报告器共同注入 N. benthamiana 叶片
  ↓
pTRBO 复制和移动；超感染排斥维持近似“一细胞一查询”
  ↓
候选基因改变通路活性，阳性细胞表面表达 HaloTag
  ↓
叶片消化成原生质体，HaloTag 生物素化并结合磁珠
  ↓
MAPS 分成 bound 与 unbound 两群
  ↓
RNA → cDNA → 条形码扩增测序
  ↓
计算 bound/unbound 富集比，与 GFP 对照分布比较
  ↓
得到候选命中并做单基因验证
```

对扰动 $i$ 和重复 $r$，核心分数是

$$
E_{i,r}=\frac{\widetilde{B}_{i,r}}{\widetilde{U}_{i,r}},
$$

其中 $\widetilde{B}$ 和 $\widetilde{U}$ 分别是归一化后的 MAPS 结合群和未结合群条形码读数。论文的细胞因子筛选有四个生物学重复，并把每个 *Arabidopsis* ORF 的富集比与 52 个 GFP 对照的总体均值比较。

### 为什么要在 pTRBO 中放内含子？

这是一个容易忽略但很重要的工程细节。某些植物 ORF 在农杆菌中会发生泄漏表达并影响不同克隆的生长，从而在真正进入叶片前就改变文库组成。作者把内含子插入 pTRBO 运动蛋白区域，使其在农杆菌中不能正确表达、进入植物后再经剪接恢复功能。补充实验显示，这一设计减轻了 ORF 长度与农杆菌/叶片丰度之间的偏差。

### 细胞因子通路示范

研究者混合了 57 个 *Arabidopsis* ORF 与 55 个带不同条形码的 GFP 对照，用 TCSn 启动子报告细胞分裂素信号。PIVOT 找回了预期的正调控 type-B ARR，并把多个 CRF 排在高富集区域。随后独立叶斑成像和 RT–qPCR 支持 CRF5 与 CRF12 激活 TCSn。

CRF2 很能说明这种筛选的价值：它在池化筛选中富集最高，但高表达在局部叶片引起细胞死亡，使常规验证看起来像失败。把检测提前并改用较弱的 NOS 启动子后，TCSn 激活重新显现；系统性表达 CRF2 还使内源 *NbRR17* 转录约提高十倍。也就是说，单细胞层面的分离可以保留那些在密集组织中会因毒性而被遮蔽的信号。

### 能做到多大规模？

模拟实验中，1:10,000 的少数成员可以被观察和测序检测。作者据此估计单片叶可支持约 $10^4$–$10^5$ 个候选。但是不要把它理解成已经完成了十万基因的无缺失筛选：在 46 万和 460 万成员等效模拟中，少数条形码出现明显脱落，需要增加叶片、重复和测序深度。本文真正完成的生物学筛选是 112 个构建体。

### 主要限制

- 较长 ORF 在叶片中的代表性降低；获得性功能筛选需要按长度分池、补齐长度或使用更均一的扰动形式。
- 候选蛋白、通路和报告器必须能在异源宿主中正常工作。
- 表型必须能通过启动子、蛋白/小分子传感器等方式转成表面 HaloTag 信号。
- MAPS 得到的是两个细胞群的池化测序，不是带单细胞索引的 scRNA-seq。
- 没有找到公开分析代码。Geneious Prime 的条形码匹配参数、低计数过滤、归一化脚本和统计绘图代码均为 **Not found**；只能根据论文和补充表重建总体分析。

### 如何评价这项技术？

PIVOT 最强的贡献不是复杂算法，而是把病毒生态机制、合成表面报告器、原生质体磁分选和条形码测序组合成可扩展的植物功能遗传工作流。现有证据有力支持其组件机制和 112 成员示范筛选；对更大规模、不同植物物种、不同通路及敲低/敲除扰动的普适性，仍需要后续实验验证。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## PIVOT paper summary

### What problem does it solve?

Whole-plant genetic screens are slow and resource-intensive, and gene redundancy or lethal phenotypes can conceal function. Existing pooled delivery in plants also faces a density trade-off: low *Agrobacterium* concentration gives sparse transformed cells, while high concentration introduces multiple queries into one cell and breaks genotype–phenotype assignment. PIVOT converts an intact leaf into a pooled single-cell screening substrate while retaining one dominant viral query per cell.

### What is new?

PIVOT (protoplast isolation after virus overexpression *in planta*) integrates two engineered modules:

1. A TMV-derived pTRBO vector uses viral superinfection exclusion and movement to spread barcoded perturbations across leaf tissue while limiting secondary infection of the same cell.
2. A pathway-responsive promoter drives a surface HaloTag reporter. After protoplasting, reporter-positive cells are biotinylated, captured with streptavidin magnetic beads by MAPS and identified by sequencing perturbation barcodes from bound and unbound fractions.

This is an experimental screening technology, not a scRNA-seq assay: phenotypes are resolved at the protoplast level, but sequencing is pooled by sorted fraction.

### Demonstration and main results

The authors used *Nicotiana benthamiana* as a heterologous host and screened 57 barcoded *Arabidopsis thaliana* ORFs together with 55 barcoded GFP controls for activation of the cytokinin-responsive TCSn promoter. For each barcode and replicate, the screen uses normalized MAPS bound reads divided by normalized unbound reads, followed by comparison with the GFP-control distribution.

The component experiments show broad pTRBO-mediated tissue coverage with separated fluorescent territories, visual detection of a 1:10,000 minority member and quantitative rare-barcode detection in larger simulated libraries. MAPS enriches HaloTag-positive protoplasts from mixtures as dilute as 1:100 and distinguishes weak, medium and strong promoters. The 112-member screen recovers expected positive type-B ARR regulators and prioritizes several cytokinin response factors. Individual assays support CRF5 and the previously little-characterized CRF12 as TCSn activators. CRF2, the highest-enrichment screen hit, caused toxicity under dense/high expression; earlier or weaker expression restored reporter activation, illustrating a setting where cell-level screening can expose a candidate obscured in whole tissue.

### Limits and interpretation

The platform has three important constraints. First, larger ORFs are depleted during viral delivery, so gain-of-function libraries should be length-matched, padded or stratified. Second, the query and reporter must function in a heterologous host and the phenotype must be convertible into a surface-reporter signal. Third, the headline 10⁴–10⁵-candidate-per-leaf capacity is an engineering estimate supported by mock-library experiments; very large simulations show barcode dropout, and the biological screen itself contains 112 constructs and four replicates.

### Reproducibility assessment: 3/5

The paper provides detailed wet-lab protocols, processed count tables, raw sequencing data at SRA BioProject `PRJNA1433054`, and reporter/vector identifiers at Addgene. All main and Extended Data figures and the Supplementary Information are locally available in this workspace. However, no public analysis-code repository was found. Barcode demultiplexing is described as performed in Geneious Prime, statistics in GraphPad Prism, and exact scripts/settings for filtering, normalization, tests and plots are **Not found** in the code-availability section, article HTML or paper Markdown. The broad analysis can be reconstructed from prose and tables, but exact computational reproduction is incomplete.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
