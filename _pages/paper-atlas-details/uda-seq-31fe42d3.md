---
layout: default
permalink: /paper-atlas/uda-seq-31fe42d3/
title: "UDA-seq"
nav: false
description: "UDA-seq 的关键不是发明一个新的单细胞分析模型，而是把“第二轮组合索引”放到标准液滴条形码之后：先允许一个液滴装入多个固定细胞/细胞核，再把它们完整释放到 96/384 孔板中加入孔特异条形码。最终用“液滴条形码 + 孔条形码”的组合识别单细胞，从而在尽量复用 10x 等成熟化学体系的同时显著提高通量。"
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
      <span>Technology Platforms</span>
      <span>Nature Methods · 2025</span>
    </div>
    <h1>UDA-seq</h1>
    <p>UDA-seq: universal droplet microfluidics-based combinatorial indexing for massive-scale multimodal single-cell sequencing</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## UDA-seq 方法详解

### 一句话理解

UDA-seq 的关键不是发明一个新的单细胞分析模型，而是把“第二轮组合索引”放到标准液滴条形码之后：先允许一个液滴装入多个固定细胞/细胞核，再把它们完整释放到 96/384 孔板中加入孔特异条形码。最终用“液滴条形码 + 孔条形码”的组合识别单细胞，从而在尽量复用 10x 等成熟化学体系的同时显著提高通量。

### 1. 它要解决什么问题？

标准液滴单细胞测序为了避免双细胞，通常使用很稀的细胞悬液。结果是绝大多数液滴为空，真正装有细胞的液滴只占很小比例；做大样本队列、多组学或 CRISPR 筛选时，试剂和芯片成本迅速上升。

已有液滴组合索引工作证明了“一个液滴装多个细胞，再依靠额外索引拆分”的可行性，例如：

- 液滴组合索引 ATAC，*Nature Biotechnology*，2019；
- scifi-RNA-seq，*Nature Methods*，2021；
- SCITO-seq，*Nature Methods*，2021；
- FIPRESCI，*Genome Biology*，2023。

这些早期方法往往面向单一模态，或需要在进液滴前完成模态特异的预索引。预处理步骤越多，越容易增加操作时间，并影响脆弱核酸分子的稳定性。UDA-seq 的思路是：第一轮仍使用成熟的液滴试剂，第二轮索引放在破乳之后，因此同一框架可以扩展到 RNA、VDJ、ATAC 和 CRISPR guide 捕获。

### 2. 核心设计：两轮条形码

```text
固定/透化的细胞或细胞核
        |
        | Multiome 分支先做原位 Tn5 转座
        v
高密度装载到液滴系统
        |
        | 第 1 轮：液滴特异条形码
        | 一个液滴可以含多个细胞
        v
破乳并释放仍保持完整的细胞/细胞核
        |
        v
随机分配到 96/384 孔板
        |
        | 第 2 轮：孔特异 index PCR
        v
合并、纯化并构建不同模态的文库
        |
        v
测序后用“round-1 barcode + round-2 index”定义细胞
```

第一轮条形码不再要求唯一对应一个细胞，它更像经典组合索引中的一个“孔”。第二轮孔索引把共享第一轮条形码的细胞再次拆分。论文估计两轮组合可以产生约 960 万到 3,800 万种条形码组合，因此即使装载 50 万细胞，碰撞率也能保持较低。

这个设计成立有三个前提：

1. 固定细胞/细胞核在液滴反应和破乳后仍然完整；
2. 测序读段能够同时恢复两轮条形码；
3. 组合空间远大于装载细胞数。

Extended Data Fig. 2 的显微图显示 SNU16 细胞、PBMC 和肾脏细胞核在破乳后仍保持可辨认形态；物种混合实验则直接检验了条形码碰撞。

### 3. 从实验输入到测序输出

#### 3.1 3′/5′ RNA 分支

固定和透化后的细胞进入 Chromium 液滴系统，完成第一轮 RNA 条形码。破乳后将细胞分到孔板，通过独特的 Truseq-i5 index 完成第二轮 PCR。合并各孔产物后进行 cDNA 片段化、扩增和文库构建。

论文比较了三种破乳后处理方案，最终选择蛋白酶 K 路线：相对第一种方法多检测约 15% 的基因，同时比 SILANE 磁珠方案更简单。

#### 3.2 RNA + VDJ 分支

5′ RNA 文库完成后，从同一 cDNA 产物通过两轮嵌套 PCR 富集 TCR/BCR。细胞的 RNA 和 VDJ 结果通过相同的两轮细胞条形码配对。

#### 3.3 RNA + ATAC Multiome 分支

细胞核先进行原位 Tn5 转座，再进入 10x Multiome 液滴完成 RNA/ATAC 第一轮标记。破乳、SILANE 纯化和孔索引 PCR 后，产物分别进入 ATAC 富集和 cDNA 富集流程，最终得到同一细胞的染色质开放性和基因表达。

#### 3.4 RNA + CRISPR guide 分支

表达 Cas9 的 SNU16 细胞接受 pooled sgRNA，再进行 3′ RNA UDA-seq，并从 cDNA 中富集 guide 序列。这样每个细胞同时具有转录组和扰动身份。

### 4. 从 FASTQ 到单细胞矩阵

```text
测序数据
  -> 按第 2 轮 post-index 分组
  -> 每个 index 单独运行 Cell Ranger / Cell Ranger ARC / Cell Ranger VDJ
  -> 拼接“post-index + 10x barcode”形成最终细胞 ID
  -> Demuxlet 利用供体 VCF 进行样本拆分
  -> Scrublet/Demuxlet 去除双细胞
  -> RNA/ATAC 质量控制
  -> 合并为队列级对象
  -> 不同生物学分支分析
```

肾脏和 PBMC 队列将多个供体混合后一次处理，因此需要自然遗传变异重新分配供体。RNA 常用阈值为基因数 >200、线粒体比例 <5%；肾脏 ATAC 要求 TSS enrichment >4、fragment >1,000，并只保留 RNA 和 ATAC 同时通过质控的细胞。

代码中可以直接验证这些步骤：

- `code/0_Preprocess/step1_mapping_for_RNA.sh:1-24`：循环 96 个 post-index，分别运行 `cellranger count`；
- `code/figure2/3_RNA_Seurat.R:3-31`：RNA 质控、2,000 个高变基因、PCA、邻居图、聚类和 UMAP；
- `code/figure2/3_ArchR_atac_part.R:13-43`：hg38、TSS ≥4、fragment ≥1,000、Arrow 文件和 ArchR 项目。

### 5. 三个主要下游应用

#### 5.1 肾脏 Multiome：从细胞图谱到临床表型

研究将 25 个疾病活检和 10 个健康对照的小块冷冻肾组织混合，在两个通道中完成 UDA-seq，得到 207,789 个同时通过 RNA/ATAC 质控的细胞。

分析分为四层：

1. Seurat 和 ArchR 构建 RNA、ATAC 细胞图谱；
2. WNN 和 Peak2Gene 连接两种模态；
3. Scissor 将供体临床表型、供体伪 bulk 表达和单细胞表达关联起来；
4. SCENIC+ 和 CellChat 产生调控网络与细胞通讯假设。

蛋白尿分析中，Scissor 使用二分类表型和 $\alpha=0.8$，并随机抽取一半细胞降低计算量。代码 `code/figure3/1_scissor.R:1-27` 与这一设置一致。

论文用下面的公式衡量某个亚群是否富集于 Scissor 阳性细胞：

$$
{\mathrm{Enrichment}}_{i}={\log }_{2}\left(\frac&#123;&#123;P}_{i}}&#123;&#123;{Ex}}_{i}}+{\mathrm{pseudo}}&#123;&#123;\_}}{\mathrm{value}}\right),
$$

其中 $P_i$ 是亚群 $i$ 在表型阳性细胞中的实际比例，$Ex_i$ 是期望比例，`pseudo_value=0.000001`。最高且大于 0 的亚群被定义为表型富集亚群。

需要注意：`code/figure3/2_enrichment_freq.R:2-24` 只计算了实际比例与期望比例的比值，没有实现论文中的 $\log_2$ 和 pseudo-value，因此这里只能算 **Partial** 匹配。

#### 5.2 女性衰老 PBMC：RNA + VDJ

38 位 20–65 岁女性供体被分成 10 人和 28 人两个 pool。质控和供体拆分后保留 132,712 个细胞，其中 126,616 个高置信细胞用于 27 类细胞注释。

SCIPAC 将连续年龄、供体伪 bulk 表达和单细胞表达联合建模。代码 `code/figure5/6_SCIPAC_Aging.R:17-125` 可以验证供体聚合、TMM 归一化、单细胞/伪 bulk 联合预处理和 Gaussian SCIPAC。随后对 CD4 naive 细胞进行 Harmony 校正和重聚类，发现随年龄增加的 ITGB1/PREX1 阳性亚群。

#### 5.3 CRISPR 扰动：RNA + guide

研究使用 255 条 sgRNA 靶向 46 个 bromodomain 相关基因。50,000 个细胞进入一个通道，恢复 38,000 个细胞，31,487 个带有 sgRNA；严格分配后保留 12,644 个具有唯一或优势 guide 的细胞。

优势 guide 的论文定义是：其 UMI 数超过该细胞中其他 guide UMI 数之和。如果各 guide 比例之和为 1，则等价于最大比例大于 0.5。代码使用更严格的 0.51：

- `code/figure6/1_calculate_dominate_sgRNA.R:3-15`：计算每个细胞中 guide 的归一化比例；
- `code/figure6/2_assign_dominate_sgRNA.R:2-12`：保留最大比例 >0.51 的 guide；
- `code/figure6/3_scmageck_lr.R:1-15`：用 `Control` 作为负对照并进行 100 次 permutation。

### 6. 结果应该怎样理解？

论文给出的关键技术证据包括：

- 10,000 个整细胞实验得到 6,245 个高质量细胞，碰撞率 1.23%，低于仅用第一轮条形码时的 6.29%；
- 300,000 个 GEM-X PBMC 装载后保留 150,018 个高质量细胞，并识别到低于 0.1% 的稀有状态；
- 35 个肾活检样本得到超过 20 万个双模态高质量细胞；
- 成本图在 100,000 细胞假设下显示 scRNA 和 Multiome 文库构建费用分别约降低 8.4 倍和 8.8 倍，但测序费用不变。

生物学结果——蛋白尿相关 podocyte、肾损伤相关 EC-GC、衰老相关免疫状态和 SNU16 亚群差异——说明大规模数据能够支持稀有群体发现。SCENIC+、CellChat 和 scMAGeCK 的网络或选择分数仍属于计算推断，需要额外实验验证，不能直接当作机制证明。

### 7. 代码与论文的一致性

总体评价为 **medium fidelity**：Exact 6，Partial 5，Inferred 0，Notebook 0，Not found 2。

直接匹配较强的部分包括 Cell Ranger 分 index 映射、Seurat RNA 流程、Scissor、CellChat、SCIPAC、CD4-naive 重聚类、优势 sgRNA 分配和 scMAGeCK。

主要缺口是：

- **Not found**：可执行的顶层 workflow、环境文件、测试和随仓库提供的数据；
- **Not found**：把测序输出拆成 post-index FASTQ 的步骤；
- 多个脚本依赖 `/p300s/`、`/xtdisk/` 或用户目录中的外部 RDS/PKL；
- 通用预处理脚本存在 `SNG_POSTERIOR` 未正确写入、`SNG`/`type` 字段不一致的问题；
- ArchR 脚本后段引用未定义的 `projHeme6`；
- SCENIC+ 脚本从外部预构建的 `scplus_obj.pkl` 开始，没有提供论文描述的完整 pycisTopic、motif enrichment 和 `build_grn` 过程。

因此，仓库适合核对许多下游参数和图表分析，但不能不经修改地复现从原始数据到全部结果的完整流程。静态文件名之间的连接只能说明潜在数据依赖，不能当作真实运行顺序。

### 8. 最重要的认识

UDA-seq 的创新点是把液滴系统从“单细胞隔离器”改造成“第一轮组合索引器”。它牺牲第一轮条形码的唯一性，再用第二轮孔索引恢复单细胞分辨率。这样做把通量提升与成熟多模态化学体系连接起来，特别适合大队列、微量临床样本和 pooled perturbation screening；但成功落地仍依赖细胞完整性、第二轮 FASTQ 拆分、样本 multiplexing、受控数据访问和大量未打包的计算中间文件。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## UDA-seq Summary

### Problem

Droplet single-cell assays are convenient and robust but deliberately waste most droplets to avoid loading more than one cell. Existing droplet-plus-combinatorial-indexing approaches increase throughput, yet many use modality-specific pre-indexing protocols, adding handling time and making it difficult to apply one workflow across RNA, chromatin, immune-receptor, and perturbation assays. UDA-seq addresses this by moving the extra index **after** established droplet barcoding.

### Proposed Technology

UDA-seq—universal droplet microfluidics-based combinatorial indexing—overloads fixed cells or nuclei into a standard droplet system. The droplet barcode is round 1. Cells/nuclei are then released intact, randomly distributed into 96 or 384 wells, and assigned a well-specific PCR index in round 2. The combined droplet and well barcodes identify individual cells even when several cells shared the first droplet.

This post-indexing architecture reuses modality-specific first-round chemistries and was demonstrated for 3′/5′ RNA, RNA+VDJ, RNA+ATAC Multiome, and RNA+CRISPR guide capture. It is a platform design rather than a new machine-learning model; established tools such as Cell Ranger, Demuxlet, Seurat, ArchR, Scissor, SCENIC+, CellChat, SCIPAC, scRepertoire, and scMAGeCK perform downstream analysis.

### Main Evidence

- Species-mixing experiments recovered 6,245 high-quality cells from 10,000 loaded whole cells with a 1.23% collision rate, versus an estimated 6.29% using the first-round barcode alone. Nuclei experiments reported 2.11% collision for three-species RNA and 0.67% for two-species Multiome.
- A GEM-X 5′ RNA+VDJ run loaded 300,000 fixed PBMCs, recovered 170,000 cells, and retained 150,018 after QC. The resulting atlas resolved 44 states, including populations below 0.1% abundance.
- In 35 frozen kidney biopsies (25 disease, 10 healthy), two Multiome UDA-seq channels produced 207,789 cells passing both RNA and ATAC criteria. Joint analysis identified rare proteinuria-associated podocytes and renal-impairment-associated glomerular capillary endothelial cells, followed by hypothesis-generating SCENIC+ and CellChat analyses.
- In 38 female PBMC donors aged 20–65, UDA-seq recovered 152,357 cells and retained 132,712 after QC/demultiplexing; 126,616 high-confidence cells formed a 27-cell-type atlas. SCIPAC recovered expected immune-aging patterns and highlighted an age-expanded ITGB1/PREX1-positive CD4-naive subcluster.
- A pooled CRISPR experiment used 255 sgRNAs targeting 46 bromodomain genes. Of 38,000 recovered cells, 31,487 contained sgRNA; 12,644 passed stringent dominant-guide assignment, giving a mean of 44 cells per guide and 233 per target gene. scMAGeCK and differential expression exposed subgroup-specific perturbation effects.
- Extended Data cost tables model approximately 8.4-fold lower scRNA library-construction cost and 8.8-fold lower Multiome library-construction cost at 100,000 cells. Sequencing costs are unchanged, so the saving is specifically from fewer droplet-kit reactions/channels.

### Why Existing Approaches Are Insufficient

The paper contrasts UDA-seq with early droplet combinatorial-indexing and pre-indexing methods such as scifi-RNA-seq. Those approaches are less universal across modalities and can require extra pre-indexing operations before fragile molecular targets enter droplets. UDA-seq's post-indexing is simpler to graft onto existing kits, but unlike pre-indexing it does not automatically label samples before pooling; this study relies on donor genotypes for deconvolution. The paper also notes that OAK-seq uses a similar overloading/unpacking strategy but focuses mainly on in-vitro systems.

### Limitations

- UDA-seq requires intact fixed cells/nuclei after round-1 droplet chemistry. It is incompatible with platforms that lyse cells inside droplets for barcoding.
- Built-in sample multiplexing is absent. Genetic deconvolution requires informative donor variation and is unsuitable for repeated samples from the same donor unless another hashing strategy is added.
- Clinical human-genetics data are controlled access, and many downstream results are associative rather than mechanistically validated.
- Cost comparisons use an assumed 100,000-cell scenario and do not reduce sequencing expense.
- The explicit collision-rate equation is not provided; Methods only cite the SCITO-seq formula.

### Reproducibility and Code-Paper Match

**Reproducibility: 3/5. Overall code-paper fidelity: medium.**

The GitHub snapshot (commit `ed627e05f7efd1e56b695a50afa7b22a43099ce8`) contains direct matches for per-index Cell Ranger mapping, Seurat RNA analysis, Scissor, CellChat, SCIPAC, CD4-naive reclustering, dominant-sgRNA assignment, and scMAGeCK. It is useful for verifying downstream parameters and figure analyses.

It is not a self-contained executable reproduction package. No bundled data, environment, tests, or top-level workflow establishes end-to-end order. Static RDS/PKL filenames are not runtime traces; many scripts depend on `/p300s/`, `/xtdisk/`, or home-directory paths. Generic preprocessing contains inconsistent metadata fields, one ArchR script references an undefined object, the round-2 FASTQ demultiplexing step is absent, and SCENIC+ scripts begin from a prebuilt external object. These gaps are documented rather than treated as evidence against the experimental platform itself.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
