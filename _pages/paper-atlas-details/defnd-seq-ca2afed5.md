---
layout: default
permalink: /paper-atlas/defnd-seq-ca2afed5/
title: "DEFND-seq"
nav: false
description: "肿瘤中的“细胞状态”和“基因组状态”通常由两套实验分别测量：单细胞 RNA 测序告诉我们细胞正在表达什么，单细胞 DNA 测序告诉我们细胞携带哪些拷贝数变异（CNV）或单核苷酸变异（SNV）。如果两种数据来自不同细胞，就只能在群体层面猜测某个基因组亚克隆对应什么转录表型；理想情况是对同一个细胞同时测 RNA 和 DNA。"
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
    <h1>DEFND-seq</h1>
    <p>Scalable co-sequencing of RNA and DNA from individual nuclei</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## DEFND-seq 方法详解

### 1. 它要解决什么问题？

肿瘤中的“细胞状态”和“基因组状态”通常由两套实验分别测量：单细胞 RNA 测序告诉我们细胞正在表达什么，单细胞 DNA 测序告诉我们细胞携带哪些拷贝数变异（CNV）或单核苷酸变异（SNV）。如果两种数据来自不同细胞，就只能在群体层面猜测某个基因组亚克隆对应什么转录表型；理想情况是对同一个细胞同时测 RNA 和 DNA。

早期联合测序已经证明了这种关联的价值，但扩展性不足：DR-seq（*Nature Biotechnology*, 2015）、G&T-seq（*Nature Methods*, 2015）、Simul-seq（*Nature Methods*, 2016）和 SIDR（*Genome Research*, 2018）依赖逐孔或人工操作；GoT（*Nature*, 2019）主要检测转录本中的靶向突变；sci-L3-RNA/DNA（*Molecular Cell*, 2019）用组合索引提高了通量，但覆盖有限，而且论文中的展示主要是细胞系 (`paper.md:21-27,367-373`)。

DEFND-seq 的目标是：使用已有的 10x Genomics Multiome 平台，一次处理数千个细胞核，并让每个细胞核的 RNA 与全基因组范围的 DNA 片段共享同一条形码。

### 2. 核心创新：先“拆核小体”，再走标准 10x 流程

常规 snATAC-seq 中，Tn5 主要进入开放染色质，因此读到的是可及性而不是均匀的基因组覆盖。DEFND-seq 在上机前用 lithium diiodosalicylate（LIS，二碘水杨酸锂）破坏核小体包装，使更多基因组区域可被 Tn5 接触，同时尽量保持细胞核完整并保护 RNA。

```text
细胞或组织
  -> 分离完整细胞核
  -> LIS 处理，去除/削弱核小体包装
  -> 清洗并保留 RNA
  -> Tn5 tagmentation
  -> 标准 10x Multiome 微滴与条形码珠
  -> 同一细胞核产生匹配的 RNA 库和 gDNA 库
```

对贴壁 BJ 成纤维细胞，论文使用含 12.5 mM LIS、Tris、NaCl、MgCl~2~、Igepal、蛋白酶抑制剂和 RNase 抑制剂的 DEFND buffer，在冰上处理 5 分钟，立即大量清洗，然后进入 10x Multiome (`paper.md:216-219`)。新鲜 GBM 组织直接在 DEFND buffer 中匀浆、过滤和清洗；冻存组织先经过蔗糖/iodixanol 密度纯化，再进行 5 分钟 DEFND 处理 (`paper.md:222-231`)。补充材料给出了组织和贴壁细胞的逐步配方与操作 (`supplementary_information.md:151-237`)。

这里有一个无法完全消除的折中：如果用蛋白酶彻底去除 DNA 结合蛋白，细胞核可能被破坏；如果为了保持细胞核而处理较温和，就可能残留染色质结构，使 Tn5 覆盖存在偏倚，进而影响 CNV 和 SNV (`paper.md:174-177`)。

### 3. 两条计算分支如何汇合？

```text
匹配的 Multiome FASTQ
  |
  +-- RNA 分支
  |     -> 提取 cell barcode / UMI
  |     -> STAR 比对到基因组和完整 gene body
  |     -> 条形码纠错、UMI 合并
  |     -> gene × nucleus 矩阵
  |     -> dropout 曲线选择高变基因
  |     -> Spearman 距离 -> Phenograph 聚类 -> UMAP
  |     -> cluster-vs-rest 二项检验 + BH FDR
  |
  +-- DNA 分支
        -> 样本拆分与 DNA 条形码提取
        -> cutadapt + BWA-MEM
        -> 比对质量和片段长度过滤
        -> 条形码纠错
        -> 重复片段合并 -> fragments.tsv
        -> SnapATAC2 分箱/QC
        -> GC、可比对性和参考细胞校正
        -> CNV、DNA 聚类、局部扩增检验
        -> GATK/Mutect2/Annovar SNV 分析

RNA barcode == DNA barcode
  -> 只保留两种模态匹配的细胞核
  -> 将 RNA 状态与 CNV/SNV 状态直接对应
```

这条流程的关键不是把 RNA 和 DNA 在最后“按相似性拼接”，而是在实验阶段就让两种文库继承同一个细胞核条形码。因此，一个 RNA UMAP 上的细胞可以直接查询其 DNA 拷贝数或覆盖到的等位基因。

### 4. RNA 分支

#### 4.1 从 reads 到表达矩阵

RNA read 通过 STAR 比对。由于细胞核中未剪接 RNA 很多，基因计数不仅覆盖外显子，也覆盖内含子、内含子–外显子连接和外显子–外显子连接。每条 read 被转换成“基因 + cell barcode + UMI”地址，再进行条形码纠错与 UMI 合并，得到表达矩阵 (`paper.md:264-267`)。

保留的 `DropSeqPipeline8` 代码能静态对应 barcode/UMI 提取、poly(A) 修剪、STAR/SAMtools、gene address 和 UMI/barcode collapse (`code/DropSeqPipeline8/clipper.py:11-68`; `code/DropSeqPipeline8/DropSeqPipeline8.py:93-203`)。但这里没有论文样本的实际命令、参考文件、环境或运行输出，所以它是 Partial，而不是已验证的端到端复现。

#### 4.2 高变基因、聚类和差异表达

论文按基因相对 dropout 曲线的偏离程度选择高变基因，然后计算 Spearman 相关距离，使用 Phenograph 聚类并以 UMAP 可视化；每个 cluster 的富集基因通过 cluster-vs-rest 二项检验和 Benjamini–Hochberg 校正得到 (`paper.md:270-273`)。

这些步骤在 `cluster_diffex2018` 中有直接静态实现：

- dropout 特征选择：`clusterdiffex/distance.py:70-168`；
- Spearman、Phenograph、UMAP 串联：`scripts/cluster_diffex.py:217-267`；
- 二项检验、log2 effect 和 BH FDR：`clusterdiffex/diffex.py:139-245,248-340`。

代码能说明算法怎样连接，但没有论文样本的参数文件或结果重跑，因此“源码匹配”不等于“论文图已复现”。

### 5. DNA 预处理分支

#### 5.1 比对与片段过滤

论文先用 Cell Ranger ATAC `mkfastq` 拆分样本，以 cutadapt 去除标准接头 `CTGTCTCTTATACACATCT`，再用 BWA-MEM 比对 (`paper.md:276-279`)。`dna10x.py` 静态连接了这些步骤，并要求样本表、参考基因组、10x whitelist、最大 insert size、最低比对分数比例和 barcode 位置 (`code/dna10x/dna10x.py:16-33,50-100`)。

论文保留 alignment score 大于 read length 的 90%、insert size 小于 1 kb 的 read pair。代码中的条件是参数化的 `score/rlen > minscore` 和 `abs(isize) < insert_size` (`code/dna10x/address.py:8-58`)。

#### 5.2 条形码纠错中的隐藏差异

论文把 Hamming distance 为 1 的 whitelist 候选记为：

$$
P_{alt}=f_{alt}10^{-q/10},
$$

其中 $f_{alt}$ 是候选条形码在数据中的频率，$q$ 是疑似错误碱基的质量分数；最高候选超过 0.975 时替换 (`paper.md:279`)。

源码实际上使用：

$$
p_{edit}=\max(0.0005,10^{-q/10}),\qquad L_{alt}=f_{alt}p_{edit},
$$

然后把所有候选 $L_{alt}$ 归一化，再用 0.975 阈值 (`code/dna10x/error_correct.py:9-44`)。也就是说，代码增加了论文未写出的错误概率下限 `0.0005`，而且阈值作用在归一化后的候选分数上。这是重要的 Partial 匹配边界。

#### 5.3 输出 `fragments.tsv`

通过过滤的 paired reads 被转换为“染色体、起点、终点、校正后的 cell barcode”，相同地址被折叠并计数，最后按染色体位置写成 Cell Ranger 风格的 `fragments.tsv` (`code/dna10x/count_dna.py:47-81`; `code/dna10x/dna10x.py:115-132`)。

需要注意：`dna10x` README 的示例命令没有提供源码声明为必需的 `--minscore` 参数，因此示例本身不能直接运行 (`code/dna10x/README.md:19-25`; `code/dna10x/dna10x.py:25`)。

### 6. 从 fragments 到 CNV

论文用 SnapATAC2 导入 `fragments.tsv`，生成 `h5ad`、每核唯一片段数、TSS enrichment、duplication rate 和 100-kb/1-Mb tile matrix (`paper.md:291-294`)。这一部分不在三套保留代码中。

当样本中有可靠的二倍体/低噪声细胞时，校正逻辑是：

1. 去掉没有 GC 值或 mappability < 0.95 的 bin；
2. 选择 50 个最低 CV 的 BJ 细胞，或 GBM 中低于中位 CV 的非肿瘤细胞；
3. 计算这些细胞的中位覆盖参考；
4. 用参考校正每个细胞；
5. 再除以体细胞染色体 bin 的中位校正覆盖并乘 2，得到估计 copy number (`paper.md:297`)。

BJ 100-kb profile 随后用 HMMcopy 四状态模型（0、1、2、3 copies）分段，并使用论文列出的特定参数 (`paper.md:303`)。冻存 GBM 因二倍体细胞太少，改用 GC 0.3–0.6 区间的局部中位数与 LOWESS 校正，再以 Chr. 2 定标 (`paper.md:315`)。

本地 `supplementary_protocol.txt` 的文件名容易误导：它不是实验协议，而是 Fig. 3 的源数据矩阵，包含 1 行表头和 1,044 个细胞核数据行，每行有 cluster 加 27,580 个基因组 bin。它证明热图背后保留了大规模矩阵，但没有提供生成矩阵的命令。

### 7. DNA 聚类、局部扩增和 SNV

新鲜 GBM 的 DNA profile 先选择跨细胞 CV 高于中位数的 100-kb bins，再做 PCA，取前 20 个主成分进行 UMAP 和 Phenograph。RNA/DNA 同时呈现肿瘤与非肿瘤标志的 cluster 被判断为 multiplet 并移除。DNA cluster 之间的局部 CNV 用 Mann–Whitney $U$ 检验和 BH 校正比较 (`paper.md:306-309`)。

本地 `supplementary_table4.xlsx` 实际是 Source Data Fig. 5：

- `Fig. 5a-l`：748 个细胞核的 DNA/RNA cluster、两套 UMAP 坐标，以及 *MDM2*、*EGFR*、*PDGFRA* amplification ratio；
- `Fig. 5m`：678,687 行 *EGFR*/*PDGFRA* 区域的 base-position pileup count。

它们是图的处理后数据，不是可执行分析脚本。

SNV 分支对新鲜 GBM 使用匹配 PBMC germline：MarkDuplicates、BQSR、Mutect2、GnomAD、1000 Genomes panel of normals、污染估计、`FilterMutectCalls` 和 ANNOVAR (`paper.md:312`)。冻存 GBM 没有匹配 germline，因此使用 tumor-only Mutect2，并取 Illumina 与 Element Aviti 两个平台独立 call 的交集，再与 COSMIC 比对 (`paper.md:318-321`)。这些流程均未在三套代码快照中找到直接实现。

### 8. 论文结果怎样支持方法？

- Fig. 1 直接显示 LAND 破坏了 ATAC 的核小体周期性，unique fragments 随测序深度继续增加，TSS enrichment 和 100-kb CV 更低，同时 cDNA 完整性优于 xSDS。
- BJ DEFND-seq 在约 140 万 reads/核时报告 100-kb CV 0.6、1-Mb CV 0.38；混合物种实验分析 7,900 个细胞核，RNA 与 DNA 的物种归属一致，mixed-species collision rate 为 5.2% (`paper.md:65,79`)。
- 在相同低测序深度下，DEFND-seq 的 transcript 和 fragment 中位数高于论文采用的 sci-L3 对照，但比较使用了不同细胞系，而且 sci-L3-RNA/DNA 的 gDNA 深度没有报告，因此不能视为完全公平的 benchmark (`paper.md:82`)。
- BJ 数据发现约 2% 的稀有亚群具有 Chr. 7q 部分扩增，并伴随该区域基因表达富集 (`paper.md:96-99`)。
- 新鲜 GBM 中，*EGFR* 与 *PDGFRA* 的局部扩增对应不同 RNA/DNA 肿瘤状态；覆盖充分的细胞还显示 *EGFR* p.D1082N 和 *MAP2K3* p.D24N (`paper.md:108-150`)。
- 冻存超过 4 年的 GBM 仍获得 1,821 个细胞核，并检测到 *PTEN* 缺失、*MYCN*/*CDK4* 扩增以及跨平台交集得到的 *PREX1* 候选突变 (`paper.md:153-159`)。

### 9. 代码匹配和复现结论

总体代码忠实度为 **medium**：Exact 6、Partial 3、Not found 4。

能由直接源码支持的核心内容包括 RNA 预处理、dropout 特征选择、Phenograph/UMAP、二项/BH 差异表达，以及 DNA 的 trimming/alignment、过滤、barcode correction 和 `fragments.tsv` 生成。不能由三套快照直接支持的内容包括 SnapATAC2、HMMcopy、DNA-level PCA/UMAP/Phenograph、GATK/Mutect2/Annovar 和论文样本的端到端运行配置。

因此最准确的理解是：

- 实验协议较完整，且进入标准 10x Multiome 后的操作具有较强可移植性；
- 论文提供 GEO、Zenodo、图像和大量 source data；
- 三套源码确实覆盖若干关键模块；
- 但整个计算分析是由多个外部软件、数据库和未保留的 study-specific glue code 组成，本工作区没有验证任何端到端运行。

DEFND-seq 的价值主要在技术设计：用一个短而关键的核小体去除步骤，把广泛部署的 RNA/ATAC 商业平台转化为高通量 RNA/gDNA 联合测量平台。它对“同一肿瘤细胞的基因组亚克隆与转录状态如何对应”给出了有说服力的实验展示，但完整计算复现仍需要补齐外部流程和样本级配置。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## DEFND-seq Summary

### Problem

Single-cell RNA sequencing identifies cell state, whereas single-cell DNA sequencing identifies genomic alterations. Studying both in the same cell is especially valuable in heterogeneous tumors, where a rare genetic subclone may correspond to a distinct transcriptional phenotype. Earlier joint assays were constrained by manual multiwell handling—DR-seq (*Nature Biotechnology*, 2015), G&T-seq (*Nature Methods*, 2015), Simul-seq (*Nature Methods*, 2016) and SIDR (*Genome Research*, 2018)—or by targeted mutation readouts. The scalable sci-L3-RNA/DNA assay (*Molecular Cell*, 2019) used split-pool barcoding but had limited coverage and was demonstrated mainly in cell lines (`paper.md:21-27,367-373`).

### Proposed Technology

DEFND-seq—DNA and expression following nucleosome depletion sequencing—jointly profiles nuclear RNA and broadly sampled genomic DNA from the same nucleus. Nuclei are treated with lithium diiodosalicylate to disrupt nucleosome packing while retaining nuclear integrity and RNA, then tagmented and processed with the standard 10x Genomics Chromium Single-Cell Multiome ATAC + Gene Expression workflow. Shared barcodes link the resulting RNA and gDNA libraries back to the same nucleus (`paper.md:12,27,33`).

The central experimental finding is that lithium diiodosalicylate-assisted nucleosome depletion (LAND) produces a non-nucleosomal fragment profile, higher library complexity, more uniform genomic coverage and better cDNA integrity than crosslinking/SDS depletion. Once nuclei are prepared, no modification of the 10x equipment or Multiome protocol is required (`paper.md:47-65`; Fig. 1 image).

### Analysis Overview

```text
cells/tissue
  -> isolate nuclei
  -> LIS nucleosome depletion
  -> Tn5 + 10x Multiome droplet barcoding
  -> matched RNA and gDNA libraries

RNA: STAR -> barcode/UMI count matrix -> variable genes
     -> Spearman/Phenograph -> UMAP -> differential expression

DNA: cutadapt/BWA -> barcode correction -> fragments.tsv
     -> SnapATAC2 tiles/QC -> bias correction -> CNVs/DNA clusters
     -> GATK/Mutect2/Annovar -> SNVs

matched barcodes -> genotype–phenotype relationships per nucleus
```

The retained code has a **medium** paper-code match: Exact 6, Partial 3, Not found 4. `DropSeqPipeline8` supports RNA preprocessing/count orchestration; `cluster_diffex2018` supports dropout-based feature selection, Phenograph/UMAP and binomial/BH differential expression; `dna10x` supports DNA demultiplexing, trimming/alignment, filtering, barcode correction and collapsed `fragments.tsv` output. SnapATAC2, HMMcopy, DNA-level clustering, GATK/Mutect2/Annovar and study-specific execution manifests are external or Not found in the three snapshots. No path was runtime-validated (`doc_code.md`).

### Evaluation and Main Results

- In BJ fibroblasts, DEFND-seq at about 1.4 million reads per nucleus achieved reported coverage CVs of 0.6 for 100-kb bins and 0.38 for 1-Mb bins. The DNA library's genomic-region composition resembled bulk WGS (`paper.md:65`; Fig. 2 image).
- In a 7,900-nucleus human/mouse mixture, RNA and DNA species assignments were concordant. The mixed-species collision rate was 5.2%, corresponding to an implied multiplet rate of about 12.4%; apparent transcript-level cross-talk was 10.6% for mouse and 7.1% for human (`paper.md:79`; `supplementary_information.md:42-48`).
- At matched low read depths, DEFND-seq detected more median transcripts than sci-L3-RNA/DNA: 316 versus 194 at 415 reads per cell and 101 versus 68 at 130 reads per cell. Against sci-L3-WGS, DEFND-seq reported more median unique fragments at both 1.15 million reads (731,814 versus 660,700) and 130,000 reads (114,314 versus 97,300), though the comparison used different cell lines and sci-L3-RNA/DNA gDNA depth was unavailable (`paper.md:82`).
- BJ data revealed a rare approximately 2% subpopulation with partial Chr. 7q amplification and focal *HAS2* amplification, accompanied by expression enrichment of genes in the amplified region (`paper.md:96-99`; Fig. 3 image).
- Fresh GBM yielded roughly 800 analyzed nuclei with a median of 8,800 transcripts and about 1.4 million unique DNA fragments per nucleus. Joint analysis linked *EGFR* and *PDGFRA* focal amplifications to distinct DNA/RNA tumor states and identified covered *EGFR* p.D1082N and *MAP2K3* p.D24N variants (`paper.md:108-150`; Figs. 4–6 images).
- A GBM sample cryopreserved for more than four years yielded 1,821 nuclei, recovering a small non-neoplastic oligodendrocyte population plus transformed populations carrying *PTEN* deletion and *MYCN*/*CDK4* amplification. Independent Illumina and Element sequencing was used to intersect variant calls, identifying a candidate *PREX1* p.T1469M mutation (`paper.md:153-159`; Extended Data Figs. 2–4 images).
- The authors report experiments with more than 4,500 nuclei per 10x lane and an estimated library-preparation cost of about US$0.56 per cell in the 7,900-nucleus experiment (`paper.md:167-168`).

### Reproducibility

**Rating: 3/5 — strong protocol and data availability, partial computational reproducibility.**

Strengths:

- stepwise tissue and adherent-cell DEFND protocols are present in the supplement (`supplementary_information.md:151-237`);
- all ten main/extended figure images and publisher source-data artifacts were acquired;
- sequencing/count matrices are deposited at GEO `GSE224149`, and GBM fragment files are on Zenodo (`paper.md:346-349`);
- the three paper-named repositories are retained at fixed commits;
- the Fig. 3 source matrix and Fig. 5 workbook expose substantial processed data behind the CNV figures.

Gaps:

- no single environment or workflow connects wet-lab outputs to all published figures;
- no study-specific inputs, configs, commands, outputs or tests were used to validate execution;
- the retained repositories omit direct implementations of the paper's downstream CNV and SNV workflows;
- many required tools and resources are external, including commercial Cell Ranger inputs, SnapATAC2, HMMcopy, GATK databases and patient-matched germline data;
- `dna10x` contains a hidden barcode-error probability floor/normalization not stated in the paper, and its README example omits a required CLI parameter (`doc_code.md`).

### Limitations

DEFND-seq's main biological limitation is the need to disrupt chromatin without destroying nuclei: residual DNA-binding structure may bias Tn5 access and therefore CNV/SNV inference. Nuclear aggregation produced a higher-than-expected multiplet rate, and some sample types may require LIS concentration optimization. SNV sensitivity remains coverage-limited, tumor-only calling is weaker without a matched normal, and sequencing the DNA modality deeply is costly. Several benchmark comparisons are not fully controlled because assays used different cell lines or incompletely reported sequencing depths (`paper.md:167-177`; `paper.md:82`).

### Bottom Line

DEFND-seq is a practical technology innovation: a short nucleosome-depletion step repurposes a widely installed commercial RNA/ATAC platform into a high-throughput RNA/gDNA co-assay. The paper provides convincing image and source-data evidence that the assay can connect copy-number and covered single-nucleotide variation to transcriptional state in fresh and archived tumors. Reproduction of the wet-lab handoff is comparatively well specified; reproduction of the full computational analysis remains modular, externally dependent and not end-to-end verified.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
