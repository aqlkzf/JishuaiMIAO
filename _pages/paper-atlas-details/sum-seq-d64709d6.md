---
layout: default
permalink: /paper-atlas/sum-seq-d64709d6/
title: "SUM-seq"
nav: false
wide: true
description: "SUM-seq 的本质是：先用样本索引给每个细胞核建立“第一重身份”，再大胆过载液滴并加入“第二重身份”，最后用两重身份同时恢复 RNA 与 ATAC，从而把许多样本和大量细胞压缩到一次高通量多组学实验中。"
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
      <span>Nature Methods · 2025</span>
    </div>
    <h1>SUM-seq</h1>
    <p>Single-cell ultra-high-throughput multiplexed chromatin and RNA profiling reveals gene regulatory dynamics</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/dbrg77/ISSAAC-seq" target="_blank" rel="noopener noreferrer" aria-label="Open code for SUM-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## SUM-seq 方法详解

### 1. 这篇论文要解决什么问题？

研究基因调控，通常需要同时回答两个问题：

1. 哪些染色质区域处于开放状态，可能包含增强子等调控元件？
2. 同一个细胞里，哪些基因正在被转录？

单细胞 ATAC-seq 回答第一个问题，单细胞 RNA-seq 回答第二个问题；如果能在同一个细胞核中同时测量两者，就有机会把“转录因子—开放调控区—靶基因”连接起来。但已有联合 RNA/ATAC 技术很难同时满足三个条件：大量细胞、许多样本和可接受的成本。

论文将现有方法的不足概括为：10x Multiome 和 ISSAAC-seq 的多组学数据质量较高，但通量和样本复用能力有限；SHARE-seq（*Cell*, 2020）和 Paired-seq（*Nature Structural & Molecular Biology*, 2019）可提高细胞通量；MultiPerturb-seq（*Nature Biotechnology*, 2024）可支持扰动复用，但这些方法往往在样本数、成本或数据复杂度之间作出取舍。单模态的 scifi-RNA-seq（*Nature Methods*, 2021）已经证明组合式流体索引可以实现超高通量，SUM-seq 的目标就是把这一思想扩展到联合 RNA/ATAC 测量（`paper.md:18-30,488-496`）。

### 2. SUM-seq 的核心创新

SUM-seq 全称是 single-cell ultra-high-throughput multiplexed sequencing。其关键不是简单“把更多细胞塞进 10x”，而是先给每个样本加第一层索引，再把所有样本混合并过载进液滴，在液滴内加第二层条形码。

一个细胞核的计算身份可以写成：

$$
k=(s,d)
$$

其中：

- $s$ 是第一轮样本身份；
- $d$ 是第二轮液滴条形码；
- $k$ 是最终用于归属 reads、连接 RNA 和 ATAC 的细胞键。

这不是论文展示的数学公式，而是对论文文字中“sample index–droplet barcode combination”的操作性表达（`paper.md:39`）。

为什么两层索引能提高通量？普通液滴法希望一个液滴只有一个细胞，过载会产生 doublet/multiplet。SUM-seq 允许一个液滴包含多个细胞核：只要这些细胞核来自不同的第一轮样本，即使它们共享同一个液滴码 $d$，仍可用不同的 $s$ 区分。

### 3. 从样本到双模态矩阵的完整流程

```text
多个生物样本/时间点/扰动条件
          |
          v
分离细胞核 + glyoxal 固定 + 可选冻存
          |
          +-------------------------------+
          |                               |
          v                               v
barcoded Tn5 给开放 DNA 加样本索引    barcoded oligo-dT RT 给 RNA 加样本索引
          |                               |
          +---------------+---------------+
                          v
                     混合全部样本
                          |
                          v
        对 cDNA/mRNA hybrid 再做 tagmentation、gap fill、ExoI
                          |
                          v
      高密度装载 10x 液滴，在液滴中加入第二层 droplet barcode
                          |
                          v
           联合预扩增，破乳后分成 ATAC 与 RNA 两份文库
                          |
               +----------+----------+
               |                     |
               v                     v
     ATAC：样本拆分、Chromap      RNA：样本拆分、STARsolo
     fragments、500-bp tiles      UMI、gene matrix
               |                     |
               +----------+----------+
                          v
        依据 (sample index, droplet barcode) 匹配两个模态
                          |
                          v
       WNN/MOFA/chromVAR/eGRN/伪时间/GWAS 等下游分析
```

### 4. 实验步骤为什么这样设计？

#### 4.1 固定与冻存

论文使用 3% glyoxal 固定细胞或细胞核 7 分钟，并针对不同细胞类型调整裂解流程。固定后可以使用甘油体系冻存，使不同时间采集的样本最终进入同一次 SUM-seq 实验。物种混合实验中，冻存前后的主要质量分布总体相近（`paper.md:261-273`; Extended Data Fig. 2j）。

但并非所有细胞类型都适合：PBMC 中的单核细胞容易结团，因此论文未能直接把完整 PBMC 作为应用场景。这说明 SUM-seq 的“可扩展”仍受样本物理性质限制（`paper.md:208`）。

#### 4.2 ATAC 的第一层样本索引

开放染色质由装载了条形码寡核苷酸的 Tn5 转座酶处理。Tn5 在切割开放 DNA 的同时，把 ATAC sample index 写入片段。每个生物样本使用自己的索引，因此混合以后仍可恢复样本身份（`paper.md:276-288`; Extended Data Fig. 1a）。

#### 4.3 RNA 的第一层样本索引

RNA 侧使用带条形码的 oligo-dT 引物进行原位逆转录，第一层 RNA sample index 因而进入 cDNA（`paper.md:291-294`; Extended Data Fig. 1b）。

一个重要优化是 12% PEG 8000。PEG 作为 crowding agent，在物种混合实验中使每细胞 UMI 约增加 2.5 倍、基因数约增加 2 倍。不过巨噬细胞实验中 PEG 曾产生沉淀，所以该实验未使用 PEG，RNA 复杂度也相对较低（`paper.md:53,68,294`）。

#### 4.4 混样与 cDNA/mRNA hybrid tagmentation

完成两种模态的样本索引后，所有样本被合并。RNA 产生的 cDNA/mRNA hybrid 还需要再次用 Tn5 处理，引入液滴条形码所需的引物结合位点；随后进行 gap fill 和 Exonuclease I 处理（`paper.md:297-309`）。

这一顺序很关键：必须先写入样本身份，再混样，再进入统一液滴流程。

#### 4.5 液滴过载与第二层条形码

混合后的细胞核按照 10x 单细胞 ATAC 流程进入 Chromium，但装载量远高于标准条件，因此一个液滴内常有多个细胞核。凝胶珠在液滴中加入 16 nt droplet barcode。RNA 和 ATAC 分子都携带该液滴身份（`paper.md:39,312-315`; Fig. 1a）。

单独使用 $d$ 无法区分同一液滴中的多个细胞核；SUM-seq 的可扩展性来自 $k=(s,d)$，而不是来自液滴码本身。

#### 4.6 为什么要防止 Tn5 barcode hopping？

残余的带样本索引 Tn5 或寡核苷酸可能被带入液滴，并在液滴中错误结合其他细胞核的 ATAC 片段，造成 barcode hopping。过载条件下，这会把一个细胞的信号错误归给同液滴的另一个细胞。

SUM-seq 使用两个互补策略：

1. 加入过量 blocking oligo，与残余寡核苷酸竞争片段结合；其 3′ inverted dT 阻止后续延伸。
2. 将液滴中的线性扩增从 12 个循环降到 4 个循环，减少错误片段被进一步放大的机会。

物种混合图中，ATAC collision rate 从较差条件的 9.4% 降至优化条件的 3.8%，RNA collision rate 为 0.1%（`paper.md:56,315`; Fig. 1c,d; Extended Data Fig. 2a）。这是 SUM-seq 最重要的“隐藏工程技巧”之一：过载带来通量，阻断与少循环负责控制过载的副作用。

#### 4.7 分离 RNA 与 ATAC 文库

液滴反应结束后，两种模态先联合预扩增，再把产物均分为两份，分别用 ATAC 或 RNA 特异性引物扩增（`paper.md:318-321`）。论文还给出了 Illumina 和 Aviti 平台的 read/index cycle 配置（`paper.md:324-327`），Extended Data Fig. 1 展示了完整寡核苷酸结构和最终文库片段分布。

### 5. 计算流程的关键点

#### 5.1 ATAC 分支

论文描述的 SUM-seq ATAC 预处理包括（`paper.md:333,336-342`）：

1. bcl-convert 将碱基信号转成 FASTQ，并按 i7 sample index 拆分，允许 1 个 mismatch。
2. Chromap 比对到参考基因组并生成带细胞条形码的 fragments。
3. ArchR 在 500-bp genomic bins 中统计每个细胞的片段，形成 tile matrix。
4. 按 fragments、TSS enrichment、promoter ratio、FRIP、每液滴最大细胞核数等条件过滤。
5. MACS2 对细胞组调用 peaks，再合并成 consensus peakset。

物种混合中，若超过 90% ATAC fragments 来自一个物种，则把该细胞判为 singlet。

#### 5.2 RNA 分支

论文描述的 SUM-seq RNA 预处理包括（`paper.md:345-348`）：

1. bcl2fastq 或 bcl-convert 生成 FASTQ。
2. 把 i5 droplet cell barcode 与 Read2 中的 sample index、UMI 组织到可拆分的读段结构中。
3. 使用 Je 按 sample index 拆分，允许 2 个 mismatch。
4. STARsolo 比对并生成 gene-expression matrix。
5. 每个样本用 EmptyDrops 或 UMI rank curve 拐点进行 cell calling。
6. 根据线粒体/核糖体比例及各数据集阈值过滤，再跨样本合并 feature-by-cell matrices。

物种混合中，超过 80% RNA UMIs 来自一个物种时判为 singlet。

#### 5.3 两种模态如何连接？

ATAC 和 RNA 都先恢复样本身份 $s$，再恢复液滴身份 $d$，最后用相同的 $(s,d)$ 合并。这一步是 SUM-seq 与单样本 ISSAAC-seq 的本质区别。

如果只用 droplet barcode 做交集，在液滴过载条件下，不同样本但共享液滴的细胞核就会被混淆。因此 sample index 不是普通的测序 library index，而是最终单细胞身份的一部分。

### 6. 如何从双模态数据推断调控动态？

#### 6.1 联合嵌入

ATAC peak matrix 经 TF–IDF 和 SVD，RNA matrix 经深度归一化/对数变换和 PCA；两种低维表示用于构建 weighted nearest-neighbor（WNN）图和共同 UMAP（`paper.md:357-366`）。

#### 6.2 MOFA 与 TF motif activity

巨噬细胞实验把 RNA 的 4,000 个高变基因和 ATAC 的 cisTopic topics 输入 MOFA。作者只选择与极化状态/时间相关、但与 UMI/fragment depth 不强相关的因子（`paper.md:375-381`）。

开放染色质中的 TF motifs 来自 HOCOMOCO v12，ArchR/chromVAR 计算每个细胞的 bias-corrected motif accessibility（`paper.md:384-393`）。因此可以沿 MOFA factor 观察 TF 活性的时间变化。

#### 6.3 eGRN

GRaNIE 使用 31 个至少含 25 个细胞的 cluster 作为 pseudobulk samples，先构建 TF–peak，再构建 peak–gene 连接；阈值分别为 FDR <0.2 和 FDR <0.1（`paper.md:423-426`）。

论文最突出的结果是 M1 极化中的调控切换：早期以 STAT1 homodimer（GAF）为主，随后 STAT1/STAT2/IRF9 组成的 ISGF3 持续增强。STAT1、STAT2 和 IRF9 regulons 共享 601 个基因（`paper.md:94-135`; Figs. 2–3; Extended Data Fig. 7）。

#### 6.4 CRISPR 轨迹与 GWAS

CRISPRi/a 屏幕使用 PAGA、Leiden 和 diffusion pseudotime 描述分化轨迹，再用 AUCell 和 regulon network 比较扰动状态（`paper.md:411-432`）。巨噬细胞 eGRN 还与 stratified LDSC 结合，将开放区域与免疫疾病遗传力关联，并分析 *CD40*、*IL27* 等位点（`paper.md:441-453`）。

### 7. 论文用什么证明 SUM-seq 有效？

#### 物种混合基准

- 16 个 sample indices；100,000 个双重索引细胞核装入一个 10x channel。
- 只处理 20% droplets，仍得到 6,215 个人源和 7,607 个鼠源双模态细胞。
- 优化后 ATAC/RNA collision rates 为 3.8%/0.1%。
- 多细胞核液滴的标准化质量分布与单细胞核液滴相近。
- 约 90% ATAC fragments 和 70% RNA UMIs 可分配到细胞（`paper.md:50-59`; Fig. 1）。

#### 巨噬细胞极化

- 18 个样本、150,000 个装载细胞核、51,750 个通过 QC 的双模态细胞。
- 分离 M1/M2 轨迹，解析 early/sustained/late responses。
- 连接 TF motif activity、regulon activity 和免疫疾病相关开放区域（`paper.md:62-147`; Figs. 2–3）。

#### T helper 细胞

- 3 位供体、多种 Th subsets 与 restimulation 条件。
- 保留 48,153 个 RNA/ATAC 双模态细胞。
- 表达 signature 与 TF motif activity 共同支持亚群身份及刺激响应（`paper.md:150-173`; Fig. 4）。

#### 54-plex CRISPRi/a

- 约 150,000 个装载细胞核，恢复 56,652 个双模态细胞。
- 解析 *GATA2* knockdown 和 *NR4A2* overexpression 对分化轨迹和 regulon 的影响（`paper.md:176-196`; Fig. 5）。

### 8. 局限与正确解读

- RNA 复杂度低于 10x Multiome 和 ISSAAC-seq；SUM-seq 的优势是通量与复用，而不是每细胞最深的转录组。
- 某些细胞类型会结团。
- $(s,d)$ 仍可能发生同样本同液滴碰撞，需要实验设计和 QC 控制。
- chromVAR motif activity 是 motif 可及性的代理，不等同于直接测量 TF 结合。
- eGRN 与 GWAS peak–gene links 是统计推断，不代表每条边都已实验验证。

### 9. 固定代码快照到底覆盖了什么？

可以直接验证的内容包括：

- ISSAAC droplet RNA 中 16-nt cell barcode + 10-nt UMI 的构造；
- STARsolo gene matrix；
- Chromap ATAC fragments；
- aggregate-peak-by-cell sparse matrix；
- 单样本 ISSAAC 流程中按 droplet barcode 连接 RNA/ATAC。

在已搜索快照中明确 **Not found**：

1. SUM-seq sample-index demultiplexer；
2. `(sample index, droplet barcode)` 的跨模态 join；
3. SUM-seq 500-bp tile-matrix 实现。

因此，代码—论文整体保真度为 **low**。该快照适合解释 SUM-seq 继承自 ISSAAC-seq 的单样本基础处理，但不能被描述为 SUM-seq 完整实现。源码行级映射见 `doc_code.md`。

### 10. 一句话理解

SUM-seq 的本质是：**先用样本索引给每个细胞核建立“第一重身份”，再大胆过载液滴并加入“第二重身份”，最后用两重身份同时恢复 RNA 与 ATAC，从而把许多样本和大量细胞压缩到一次高通量多组学实验中。**

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## SUM-seq Summary

### Problem

Joint single-cell measurement of chromatin accessibility and gene expression can connect regulatory elements, transcription factors and target genes, but existing assays rarely combine high cell throughput, many-sample multiplexing and reasonable cost. Single-modality combinatorial-indexing methods scale well, while droplet multiomic methods such as 10x Multiome and ISSAAC-seq are comparatively low throughput. SHARE-seq (*Cell*, 2020) and Paired-seq (*Nature Structural & Molecular Biology*, 2019) increase multiomic cell throughput, and MultiPerturb-seq (*Nature Biotechnology*, 2024) supports multiplexed perturbations, but the paper argues that scalability or multiplexing is purchased at lower data complexity (`paper.md:18-30,488-496`).

### Proposed Technology

The paper introduces **single-cell ultra-high-throughput multiplexed sequencing (SUM-seq)**, a two-stage combinatorial-indexing assay for paired RNA and ATAC profiling in single nuclei. It combines the fluidic indexing concept of scifi-RNA-seq (*Nature Methods*, 2021) with the single-plex multiomic chemistry of ISSAAC-seq (*Nature Methods*, 2022).

Each biological sample first receives modality-specific indices: barcoded Tn5 labels accessible DNA, and a barcoded oligo-dT primer labels RNA during reverse transcription. Samples are then pooled and deliberately overloaded into a droplet microfluidic channel, where a second droplet barcode is added. A nucleus is identified operationally by the pair

$$
(\text{sample index},\ \text{droplet barcode}).
$$

This permits multiple nuclei per droplet while retaining single-nucleus resolution, provided different first-round samples do not collide within the same droplet. After joint pre-amplification, the library is split into ATAC and RNA fractions. The paper's preprocessing pipeline assigns sample indices, demultiplexes droplet barcodes, maps reads, generates RNA gene-expression and ATAC tile/peak matrices, and matches modalities using the composite barcode (`paper.md:36-47,282-348`).

Two engineering choices are central. A blocking oligonucleotide competes with residual Tn5 oligos that could transfer barcodes inside overloaded droplets, and droplet amplification is reduced from 12 cycles to 4. In the optimized species-mixing benchmark, the reported collision rate is 3.8% for ATAC fragments and 0.1% for RNA UMIs (`paper.md:53-59`; Fig. 1; Extended Data Fig. 2).

### Evaluation and Biological Applications

#### Scalability and quality

In a 16-index human K562/mouse NIH-3T3 experiment, 100,000 dual-barcoded nuclei were loaded into one 10x channel at about sevenfold standard loading. Processing 20% of droplets yielded paired data for 6,215 human and 7,607 mouse cells, about 70% recovery of the processed input. PEG during reverse transcription increased RNA complexity by roughly 2.5-fold in UMIs and twofold in genes. Approximately 90% of mapped ATAC fragments and 70% of RNA UMIs were assigned to cells. Quality remained broadly stable across droplets containing one to six or more nuclei, and aggregate signal resembled ENCODE RNA/ATAC tracks (`paper.md:50-59`; Fig. 1; Extended Data Figs. 1–2).

SUM-seq's ATAC complexity is comparable to lower-throughput platforms and its benchmark library complexity exceeds the displayed ultra-high-throughput comparisons. Its RNA complexity, however, remains below 10x Multiome and ISSAAC-seq, an explicit throughput-versus-depth tradeoff (`paper.md:59,208`; Extended Data Fig. 2k).

#### Macrophage polarization

An 18-sample M0/M1/M2 time course loaded 150,000 nuclei in one channel and retained 51,750 paired profiles. Joint WNN embeddings separated M1 and M2 trajectories. MOFA resolved early, sustained and late response factors; chromVAR connected these factors to changing TF motif accessibility. The key mechanistic result is a transition from early STAT1-homodimer activity to a sustained STAT1/STAT2/IRF9 (ISGF3) program. A GRaNIE eGRN recovered 44 polarization-associated TFs, with 601 genes shared among the STAT1, STAT2 and IRF9 regulons (`paper.md:62-135`; Figs. 2–3; Extended Data Figs. 3–7).

Stratified LDSC linked macrophage/eGRN accessible regions to immune traits. ISGF3-associated peaks remained enriched for autoimmune diseases, and the analysis prioritized disease-linked loci including rs4810485 near *CD40* and rs153109 within *IL27* (`paper.md:138-147,441-453`; Fig. 3; Extended Data Fig. 8).

#### Primary T cells and CRISPR screens

SUM-seq profiled differentiated human T-helper subsets from three donors, retaining 48,153 paired nuclei. Expression signatures and chromatin-derived motif activity distinguished subset identity and restimulation-responsive versus subset-specific TF programs (`paper.md:150-173`; Fig. 4).

A 54-plex arrayed CRISPRi/a experiment loaded roughly 150,000 nuclei and recovered 56,652 paired profiles across days 0, 4, 12 and 18. Pseudotime and regulon analyses associated *GATA2* knockdown with altered mesodermal/neuronal trajectories and *NR4A2* overexpression with an ectoderm-like fate, demonstrating compatibility with condition-rich perturbation screens (`paper.md:176-196`; Fig. 5; Extended Data Figs. 9–10).

### Main Contributions

- Two-stage sample/droplet indexing extends combinatorial indexing to joint RNA/ATAC profiling.
- Deliberate droplet overloading raises throughput to hundreds of samples and potentially million-cell scale.
- Blocking oligo plus reduced cycling controls Tn5 barcode hopping in multinucleated droplets.
- The paired output supports time-resolved TF activity, eGRN inference, genetic-variant interpretation and arrayed perturbation screens.
- Glyoxal fixation and cryopreservation permit asynchronous sample collection.

### Limitations

- Some cell types, especially monocytes in PBMC preparations, are prone to clumping during the protocol.
- RNA gene/UMI complexity is lower than lower-throughput 10x Multiome or ISSAAC-seq, although ATAC complexity is competitive.
- A composite barcode can still collide when multiple nuclei from the same first-round sample enter one droplet; dataset-specific maximum-nuclei and QC filters are required.
- eGRN edges and GWAS peak–gene assignments are computational inferences and are not individually validated causal interactions.

### Reproducibility and Code-Paper Match

**Workspace reproducibility rating: 2/5.**

The article gives detailed chemistry, sequencing layouts, software versions, dataset-specific QC thresholds and data accessions. It explicitly cites a SUM-seq preprocessing repository and a separate analysis repository (`paper.md:333,468-477,496`). However, the fixed code snapshot in this workspace is commit `713eaa492baf11c6cbb8bc68768e59304c20e79f` of **ISSAAC-seq**, not the cited SUM-seq pipeline.

The snapshot directly verifies the single-plex baseline: construction of a 16-nt droplet barcode plus 10-nt RNA UMI, STARsolo gene matrices, Chromap ATAC fragments, aggregate-peak sparse matrices and a droplet-barcode-only RNA/ATAC join. Overall code-paper fidelity is therefore **low** for the 2025 SUM-seq method. The following defining components are **Not found** in the searched snapshot:

- SUM-seq sample-index assignment/demultiplexing implementation;
- explicit cross-modality join by `(sample index, droplet barcode)`;
- the named SUM-seq 500-bp tile-matrix implementation.

Accordingly, the repository is useful for understanding ISSAAC-seq/basic preprocessing and for validating the inherited droplet layer, but it must not be presented as a complete implementation of SUM-seq. See `doc_code.md` for direct source lines and `figure_analysis.md` for all 15 visually inspected figures.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
