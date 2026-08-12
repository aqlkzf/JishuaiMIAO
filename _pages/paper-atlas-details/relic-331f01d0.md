---
layout: default
permalink: /paper-atlas/relic-331f01d0/
title: "ReLiC"
nav: false
description: "细胞中有两千多个 RNA 相关蛋白参与剪接、翻译、定位和降解。传统交联实验能告诉我们“哪个蛋白接触哪条 RNA”，却不一定说明这种接触让 RNA 过程增强还是减弱。常规 CRISPR 筛选多依赖细胞生长或荧光等间接表型；Perturb-seq 一类单细胞方法虽然覆盖面广，但成本高、规模受限，而且更容易观测高表达 RNA。 ReLiC（RNA-linked CRISPR）把每个 CRISPR 扰动与可测序的 RNA 条形码绑定。"
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
    <h1>ReLiC</h1>
    <p>Decoding post-transcriptional regulatory networks by RNA-linked CRISPR screening in human cells</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02702-6" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ReLiC：把 CRISPR 扰动直接连接到 RNA 表型

### 它解决什么问题？

细胞中有两千多个 RNA 相关蛋白参与剪接、翻译、定位和降解。传统交联实验能告诉我们“哪个蛋白接触哪条 RNA”，却不一定说明这种接触让 RNA 过程增强还是减弱。常规 CRISPR 筛选多依赖细胞生长或荧光等间接表型；Perturb-seq 一类单细胞方法虽然覆盖面广，但成本高、规模受限，而且更容易观测高表达 RNA。

ReLiC（RNA-linked CRISPR）把每个 CRISPR 扰动与可测序的 RNA 条形码绑定。只要能把目标 RNA 过程转化成“不同样本池中的条形码丰度比”，同一套框架就能筛翻译、剪接、NMD 或药物反应的调控因子。

### 关键创新

普通慢病毒会在逆转录时打乱 sgRNA 与条形码的配对，而且随机整合会造成表达位置效应。ReLiC 使用 Bxb1 在固定基因组位点分三步整合：

```text
landing pad
   ↓
可由 doxycycline 诱导的 Cas9
   ↓
双 sgRNA + 模块化 RNA reporter + 随机 N20 条形码
```

在把文库导入细胞之前，研究者先用双端测序确定“sgRNA 对 ↔ RNA 条形码”的映射。每个基因有四对 sgRNA，每对 sgRNA 又对应多个独立条形码，因此同一扰动天然带有多层技术重复。文库覆盖 2,092 个 RNA 相关基因，加入对照后一共靶向 2,190 个基因，每对 sgRNA 的条形码中位数为 8。

### 从测序到基因命中的计算流程

```text
FASTQ
  ↓ 提取 reporter barcode、subpool barcode、UMI
按 barcode+UMI 聚合 reads
  ↓
只保留预先测得的 sgRNA-linked barcode
  ↓
按 reporter/subpool 和 sgRNA 汇总计数
  ↓
构建 treatment / control 的 MAGeCK 输入
  ↓
计算 sgRNA 与 gene 的 log2 fold change、P 值、FDR
  ↓
FDR < 0.05 且至少 3 条 sgRNA 方向一致
  ↓
候选调控基因 + 独立实验验证
```

代码中，Snakemake 工作流负责从 SRA/FASTQ 到条形码和 UMI 计数；`get_subpool_counts.R` 允许 subpool barcode 有有限错配并完成汇总；`get_mageck_input.R` 把处理组、对照组和 sgRNA/基因注释合并成 MAGeCK 表格。另一条随机 A/B 条形码分组流程用于检查同一 sgRNA 的独立条形码是否得到一致效应。

### 四种代表性读出

#### 1. 翻译：polysome ReLiC

研究者把带条形码的 β-globin RNA 按核糖体占据量分为上清、单核糖体、轻多核糖体和重多核糖体。对每个扰动比较重多核糖体/单核糖体（$H/M$）或轻多核糖体/单核糖体（$L/M$）条形码比值，就能找到改变翻译状态的基因。

结果包括 304 个使 $H/M$ 降低、37 个使其升高的基因。除了核糖体蛋白和翻译起始因子，蛋白酶体和 TRiC 伴侣蛋白亚基敲除也明显降低核糖体占据量，提示蛋白稳态能力会反向调节翻译。不同功能通路的“生长变慢—核糖体占据下降”关系并不相同，说明 ReLiC 不是简单的生长筛选。

#### 2. 剪接：isoform-specific ReLiC

同一个 β-globin reporter 可以用不同 RT-PCR 引物分别扩增内含子 1 保留、内含子 2 保留、外显子 2 跳跃以及总 RNA。对“特定 isoform / 总 RNA”的条形码比值进行筛选后，研究发现 SF3B 复合体不同亚基对内含子保留和外显子跳跃的影响并不完全相同，并在内源转录本中验证了部分事件。

#### 3. NMD

研究者构建提前终止密码子（PTC）和正常终止密码子（NTC）reporter，并用不同 subpool barcode 区分。比较 PTC/NTC 丰度可找出 NMD 因子，也能看到翻译起始因子如何在 mRNA 降解之前改变 PTC reporter 的稳定性。

#### 4. 药物遗传学

在 homoharringtonine（HHT）处理和 DMSO 对照间比较 reporter 条形码，GCN1 成为最突出的命中。后续 RNA-seq、qPCR、免疫印迹、polysome 和 ribosome profiling 证据表明，GCN1 参与感知或传递 HHT 造成的核糖体碰撞信号，并影响 GCN2 与 ZAK 下游反应。

### 如何理解统计量？

对条形码或 sgRNA $i$，核心效应可以写成：

$$
r_i(A/B)=\log_2\frac{c_{i,A}}{c_{i,B}},
$$

其中 $c$ 是经过过滤和聚合后的计数。MAGeCK 对多条 sgRNA 进行基因层面汇总并给出置换检验 $P$ 值和 FDR。论文还要求至少三条 sgRNA 的方向一致，避免单条 sgRNA 或少数条形码造成假阳性。

### 优点与局限

ReLiC 的优势是灵活、规模大、RNA 表型直接，而且一个 sgRNA 对拥有多个独立条形码，便于内部复现。公开仓库也很完整，包含 Snakemake、容器、SRA 下载、分析脚本、源数据和逐图代码映射。

局限同样明确：它需要预先构建 landing-pad 细胞；单个 reporter 只能代表特定 RNA 上下文；敲除效应可能同时影响生长与多种通路；文库不是全基因组；完整复现需要 Apptainer、大量 SRA 数据、约 50 GB 空间和较强算力。代码中也没有找到一个统一函数，在所有实验中完整封装“FDR < 0.05 且三条 sgRNA 一致”的判定，因此最终命中规则需要结合论文和各分析脚本理解。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ReLiC

### Problem

Thousands of RNA-associated proteins regulate splicing, translation and decay, but interaction assays do not reveal functional consequences. Conventional CRISPR screens rely on indirect growth or fluorescence phenotypes, while pooled single-cell transcriptomic screens are costly, difficult to scale and biased toward abundant RNAs. ReLiC provides a pooled, direct RNA readout that can be reconfigured for different post-transcriptional processes.

### Approach

ReLiC uses iterative Bxb1-mediated integration to place inducible Cas9, dual sgRNAs and a modular RNA reporter at a defined genomic locus. Each reporter carries a random $N_{20}$ barcode whose sgRNA linkage is established by paired-end sequencing. The study targeted 2,092 known RNA-associated genes (2,190 genes including controls), with four sgRNA pairs per gene and a median of eight barcodes per sgRNA pair. Sequencing reporter barcodes after biochemical separation, isoform-selective amplification or drug treatment converts each RNA phenotype into a pooled treatment/control count comparison analyzed with MAGeCK.

The same framework supports several assays: polysome fractions for ribosome occupancy; selective RT-PCR for retained-intron and skipped-exon isoforms; paired premature- and normal-stop reporters for NMD; and drug-versus-control sequencing for chemogenomic effects. Gene hits generally require FDR $<0.05$ and at least three concordant sgRNAs.

### Main findings

- Polysome ReLiC found 304 knockouts decreasing heavy-polysome/monosome ratios and 37 increasing them. It recovered core ribosome and initiation machinery and connected proteasome and TRiC chaperonin loss to reduced ribosome occupancy.
- The relationship between growth fitness and ribosome occupancy differed across molecular pathways, showing that the assay was not simply measuring slower growth.
- Isoform-specific screens resolved different effects of SF3B complex subunits on intron retention and exon skipping and confirmed selected events in endogenous transcripts.
- NMD screens recovered core surveillance factors and showed that translation-initiation regulators alter premature-stop reporter stability.
- A homoharringtonine screen identified GCN1 as a major drug-dependent regulator. Follow-up RNA-seq, qPCR, immunoblotting, polysome and ribosome-density evidence connected GCN1 to GCN2- and ZAK-mediated responses to ribosome collisions.

### Evidence and reproducibility

The public repository is unusually complete: it includes a top-level reproduction entry point, Snakemake workflows, container references, SRA acquisition, barcode/UMI processing, MAGeCK adapters, analysis scripts, panel-level source data and a figure-to-code map. Direct inspection found high paper–code fidelity for the computational workflow. A full rerun was not attempted because it requires Apptainer, large SRA downloads, approximately 50 GB of disk and substantial compute. One extended-data polysome panel remains notebook-based, and the paper's FDR-plus-three-concordant-sgRNA rule is distributed rather than encapsulated in one universal function.

### Limitations

ReLiC requires engineered landing-pad cell lines and iterative cloning. Reporter assays provide a targeted view and do not guarantee that every endogenous transcript responds identically. The screened library covers RNA-associated proteins rather than the entire genome, knockout phenotypes can be pleiotropic, and essential-gene effects require careful separation from the RNA phenotype. Selected findings are strongly validated, but pooled hits remain discovery evidence until tested in endogenous contexts.

**Reproducibility rating: 4/5.** Analysis code, data links, containers and figure provenance are public and well mapped; the deduction reflects the heavy full-run requirements and the unavoidable absence of executable wet-lab construction.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
