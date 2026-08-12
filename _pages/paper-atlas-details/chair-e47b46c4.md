---
layout: default
permalink: /paper-atlas/chair-e47b46c4/
title: "ChAIR"
nav: false
description: "ChAIR 是一种单细胞三组学技术：在同一个细胞里同时测量 RNA 表达、开放染色质和染色质相互作用，从而把“调控元件是否开放”“它是否与启动子接触”“基因是否表达”放在同一条证据链上。 论文发表于 Nature Methods（2025），DOI 为 10.1038/s41592-025-02658-7。"
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
    <h1>ChAIR</h1>
    <p>Tri-omic single-cell mapping of the 3D epigenome and transcriptome in whole mouse brains throughout the lifespan</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## ChAIR 方法详解

### 一句话理解

ChAIR 是一种单细胞三组学技术：在同一个细胞里同时测量 RNA 表达、开放染色质和染色质相互作用，从而把“调控元件是否开放”“它是否与启动子接触”“基因是否表达”放在同一条证据链上。

论文发表于 *Nature Methods*（2025），DOI 为 `10.1038/s41592-025-02658-7`。

### 1. 它解决什么问题？

理解转录调控时，我们通常想知道三件事：

1. 哪些增强子或启动子处于开放状态？
2. 哪些远端调控元件在三维空间中与目标基因接触？
3. 这些结构和表观状态最终是否对应 RNA 表达？

过去常见的单细胞联合测量只能覆盖其中两类信息：

- RNA+ATAC 方法能同时看表达和开放性，却看不到染色质连接关系。论文引用的例子包括 ISSAAC-seq（*Nature Methods*, 2022）。
- RNA+Hi-C 方法能同时看表达和三维结构，但单细胞接触图稀疏、背景高，不容易准确定位开放的顺式调控元件和增强子–启动子连接。论文讨论的代表包括 GAGE-seq（*Nature Genetics*, 2024）。

ChAIR 的核心目标，是在同一细胞内把三者同时测出来，尤其富集与开放染色质有关的接触。

### 2. ChAIR 实际测到什么？

每个细胞产生三类数据：

- **ChAIR-RNA**：基因表达。
- **ChAIR-ATAC**：开放染色质片段与峰。
- **ChAIR-PET**：paired-end tags，表示染色质接触。

这里最重要的设计不是“再做一种单细胞 Hi-C”，而是让接触数据偏向开放染色质区域。代价是每个细胞的总接触数低于 scHi-C；收益是接触更直接地指向转录相关调控元件。正文报告超过 40% 的 ChAIR-PET 接触连接开放染色质位点（`paper.md:47-53`）。

### 3. 从细胞到三模态数据

```text
交联细胞/细胞核
  -> 原位限制性酶切
  -> A 尾化
  -> 生物素桥接 linker 近邻连接
  -> Tn5 tagmentation
  -> 10x Multiome 液滴与细胞条形码
  -> RNA 文库 --------------------------> ChAIR-RNA
  -> DNA 文库 -> 开放片段/峰 ------------> ChAIR-ATAC
              -> 连接两端的 paired tags -> ChAIR-PET
```

起始材料为 50,000–300,000 个交联细胞或细胞核。酶切和近邻连接保留空间接触，生物素用于捕获连接产物，Tn5 则把开放染色质信息编码进 DNA 文库。10x Multiome 同时为 DNA 和 RNA 分子加入细胞条形码（`paper.md:246-249`）。

单个微流控通道可生成约 6,000–10,000 个细胞的数据，16 通道满载可超过 100,000 个细胞（`paper.md:30-33`）。

> 本工作区没有 supplementary Markdown。论文把更细的逐步实验方案放在 Supplementary Information 中，因此本文只解释主文明确给出的步骤，不声称读过补充方案。

### 4. 原始数据如何处理？

#### RNA

ChAIR-RNA 由 Cell Ranger 生成细胞×基因计数矩阵。

#### DNA

论文描述的 ChAIR-DNA 路线为：

```text
ChIA-PIPE 风格 linker 处理与比对
  -> 从 Cell Ranger ARC 结果恢复细胞条形码
  -> 把条形码写回比对 reads
  -> 按坐标+细胞条形码去重
  -> 生成 ATAC fragments/peaks
  -> 生成逐细胞 PET 与接触距离特征
```

指定的 `ChAIR-PIPE` 快照能够直接核验其中的预处理/QC 子集：

- `generateCBlist_for_cpuRead.v2.py:8-84`：按 FASTQ 顺序恢复 10x barcode。
- `addCBZB_givenCBlist.py:25-56`：写入 `CB` 和用于去重的 `ZB` 标签。
- `statCB_PET.py:7-44`：统计每个 barcode 的 PET、cis/trans、>1 kb 和 >8 kb 接触。
- `mergeCBstats.1genome.arg.R:13-72`：合并逐 barcode 统计。
- `extract_summary_cpu10x_1genome.sh:23-202`：生成测序、比对、重复和 cis/trans QC 汇总。
- submission shell 的 `941-1042` 行：生成 fragments、索引和 MACS2 peaks。

但是该仓库依赖 Slurm、外部 ChIA-PIPE/CPU、多个 Singularity 镜像和本地路径；底部示例循环中大多数 DNA 流程调用被注释。因此它不是开箱即用的完整复现入口。

### 5. 质量控制

论文为不同数据设置不同阈值（`paper.md:264-271`）：

| 数据 | nCount_RNA | nCount_ATAC | 线粒体比例 | rRNA 比例 |
|---|---:|---:|---:|---:|
| K562 | >500 | >200 | <20% | <50% |
| Patski | >1,200 | >1,200 | <20% | <50% |
| 脑 P2/P11 | >800 | >600 | <20% | <50% |
| 脑 P95/P365/P730 | >200 | >100 | <20% | <50% |

DoubletFinder 参数为 `pN=0.25, pK=0.09, nExp=0.054, PCs=1:30`。最终获得 222,698 个高质量脑细胞，注释为 121 个细胞类型、45 个细胞群和 7 个大类（`paper.md:88-94`）。这些 cell-calling 与 DoubletFinder 脚本未在指定代码快照中找到。

### 6. 如何从 PET 得到可比较的环？

显著环至少需要 3 个 PET，并且两个 anchor 都要有 ChAIR-ATAC peak 支持。为校正测序深度和 anchor 覆盖度，论文定义：

$$
{\mathrm&#123;&#123;VC}{\rm{\_}}{sqrt{\rm{\_}}score}}}=n/\sqrt{x\times y},
$$

其中 $n$ 是环的 PET 数，$x,y$ 是两个 anchor 的 piled-up read counts。后续聚合环分析使用 PET ≥3、`VC_sqrt_score ≥0.001`（`paper.md:286-295`, `328-331`）。

这个归一化非常关键，因为它把“某个环 PET 多”与“两个 anchor 本身 reads 就很多”区分开。

**代码状态：** 指定快照中未找到 `VC_sqrt` 实现。逐 barcode PET QC 不能替代 anchor 归一化。

### 7. 为什么要做 RNA-adjusted gene-centric PET？

直接使用所有 PET 时，细胞类型分群效果较差，因为接触数据太稀疏。论文把 PET 限定到活跃基因的启动子（TSS ±3 kb）和 gene body，并用 RNA 调整：

$$
{\rm{adjusted}}\,&#123;&#123;\mathrm{PET}}\; {\mathrm{count}}}
=\frac&#123;&#123;{\mathrm{RNA}}}}&#123;&#123;{\mathrm{RNA}}}_{\min }}
\times {\mathrm&#123;&#123;PET}&#123;&#123;\_}}\rm{count}}}.
$$

其中 RNA 是归一化 UMI，$&#123;&#123;\mathrm{RNA}}_{\min}}$ 是所有细胞中最小的非零归一化 UMI。之后进行 30 维 PCA 和 UMAP（`paper.md:412-424`）。

直觉上，它把“某基因周围的接触”转成以活跃基因为中心的特征，使稀疏 PET 更容易与细胞身份对应。Extended Data Figure 4 清楚显示：all-PET UMAP 混杂，而 gene-centric PET 分群明显改善。

**代码状态：** 指定快照中未找到 RNA-adjusted gene-centric PET 的实现。

### 8. CIS：怎样衡量一种特征能否区分细胞身份？

论文先以 RNA marker 定义细胞身份，再考察 5 类与 marker gene 相关的特征：

- 转录 $T$
- gene-body ATAC $A$
- promoter ATAC $P$
- enhancer ATAC $E$
- promoter-associated loop $L$

对单模态特征，例如转录：

$$
{\rm{mono}}&#123;&#123;\mathrm&#123;&#123;NFM}}_&#123;&#123;mn}}}}
=\frac&#123;&#123;T}_&#123;&#123;mn}}}&#123;&#123;\sum}_{i=1}^{m}{T}_&#123;&#123;in}}}.
$$

对组合特征，例如 $L\times A\times P\times E$：

$$
{\rm{multi}}&#123;&#123;\mathrm{NFM}}}_&#123;&#123;mn}}
=\frac&#123;&#123;L}_&#123;&#123;mn}}\times {A}_&#123;&#123;mn}}\times {P}_&#123;&#123;mn}}\times {E}_&#123;&#123;mn}}}
&#123;&#123;\sum }_{i=1}^{m}\left({L}_&#123;&#123;in}}\times {A}_&#123;&#123;in}}\times {P}_&#123;&#123;in}}\times {E}_&#123;&#123;in}}\right)}.
$$

CIS 本质上是“对角线的本细胞型信号”除以“非对角背景”。如果一种特征只在正确的细胞群中很强，CIS 就高。

结果显示，loop 与 ATAC 组合后的 3D 表观组特征常比 RNA 更有细胞型特异性。例如 OPC 为 4.04 对 2.17，MFOL 为 12.18 对 2.38，MOL 为 6.40 对 3.56（`paper.md:94`）。

**代码状态：** 指定快照中未找到 NFM 或 individual/group CIS 实现。

### 9. 如何识别细胞型特异性增强子？

候选增强子需要：

1. 在对应细胞群中有特异 ATAC peak；
2. 位于目标基因 2 Mb 范围内的同染色体接触；
3. 至少 3 个 PET 支持 promoter–enhancer 连接。

论文得到 562 个高质量细胞型特异性增强子（`paper.md:473-476`）。Extended Data Figure 5 显示其中 57.65% 位于 distal intergenic 区域，且增强子到目标 marker gene 的中位距离为 117,526 bp，远大于到最近基因的 20,238 bp。这说明仅按“最近基因”分配增强子会产生系统性错误，而接触信息能提供更直接的目标指派。

### 10. 空间信息从哪里来？

ChAIR 本身没有空间坐标。作者使用 ChAIR-RNA 作为桥梁，把 P95 ChAIR 细胞映射到 Stereo-seq bin50：

```text
ChAIR-RNA 细胞身份
   <-> Seurat FindTransferAnchors / TransferData
Stereo-seq 解剖位置
   -> 把空间标签转移给同细胞的 ATAC/PET 特征
```

转移后还用 Allen Brain Atlas 原位杂交图验证 marker 表达，只保留符合预期的细胞类型（`paper.md:518-521`）。Figure 3 显示，RNA 信号可能跨多个区域，而 loop 和组合 3D 表观组信号更集中于正确脑区。

**代码状态：** README 只列出 Seurat 依赖；未找到空间转移脚本。

### 11. HiCSR 为什么出现？

某些细胞类型可用 reads 太少，作者用预训练 HiCSR 增强 contact map。原始矩阵先做：

$$
{X}^{c}={\log }_{2}(1+{M}^{c}),
$$

$$
{T}^{c}=\frac{2{X}^{c}}{\max_{i,j}{X}_{i,j}^{c}}-1,
$$

把每条染色体缩放到 [−1,1]，再输入 `input_size=40, output_size=28` 的预训练模型。输出通过高深度 mouse-brain DNase Hi-C 参考矩阵重新标定并写回 `.mcool`（`paper.md:479-515`）。

**代码状态：** 指定快照中未找到 HiCSR 调用、反缩放或 `toCooler` 写回实现。

### 12. Megacontact 是什么？

论文把 >2 Mb 的染色质接触称为 ultralong megacontact，并按每个细胞中这类接触的比例排序（`paper.md:524-527`）。

要注意一个正文歧义：数据处理段写了“over 20 Mb”，但 megacontact 的方法、结果和主图都使用 >2 Mb。分析 megacontact 时应以 >2 Mb 为准。

作者发现：

```text
短程接触多
  -> TAD 更突出
  -> 开放性高、转录活跃
  -> 折叠密度低、核体积大

megacontact 多
  -> compartment 更突出
  -> 开放性低、转录较弱
  -> 折叠密度高、核体积小
```

Extended Data Figure 6 与影像核体积比较得到：megacontact ratio $R=-0.94$，folding density $R=-0.93$，transcription $R=0.84$，accessibility $R=0.89$。

### 13. 分化时为什么不同细胞方向相反？

在 OPC -> MOL 分化中，megacontact 增加，基因组更致密；在 DGNBL -> DGGRC 等神经元分化中，megacontact 下降，基因组更松散。

这说明 megacontact 不是简单的“成熟度越高越多”，而是一个反映细胞谱系特定核结构重塑的坐标。

更有意思的是，尽管全局折叠方向相反，局部 marker gene 的三模态顺序相似：PET 变化领先于 promoter ATAC 和 RNA。论文据此提出“先建立调控接触，再开放启动子，最后激活转录”的时序模型（Figure 4；`paper.md:135-161`）。

### 14. Megacontact 与衰老

作者把 megacontact ratio 与实际年龄以及 SCALE 计算的 transcriptomic age 比较。45 个细胞群中，36 个同时与两种年龄正相关，其中 29 个 Pearson 相关系数大于 0.5（`paper.md:187-204`）。

这种关系高度依赖细胞类型和脑区：

- CBGRC 随年龄增加 megacontact 和 folding density，RNA 活性下降。
- TEGLU 相对稳定。
- 一些祖细胞或胆碱能神经元呈弱相关或负相关。

因此 megacontact 更像“细胞类型特异的核结构年龄指标”，不是适用于所有脑细胞的统一时钟。

### 15. 这篇论文最值得学习的三点

#### 1. 同细胞测量比跨数据集整合更有因果解释力

RNA、ATAC 和 PET 来自同一个细胞，避免了把不同细胞、不同批次甚至不同实验的模态硬拼在一起。它仍不能证明因果，但能显著缩短解释链。

#### 2. 稀疏接触数据必须围绕生物问题重构特征

all-PET 太稀疏时，作者没有只追求更复杂的通用降维，而是构造 gene-centric PET、metacell、CIS 和 megacontact fraction。这些特征分别服务于细胞身份、调控特异性和核结构状态。

#### 3. 局部调控与全局折叠需要分开理解

不同谱系的全局 megacontact 方向可以相反，但局部调控接触仍可能先于开放和表达。全局核架构与局部 enhancer–promoter 调控不是同一个尺度的问题。

### 16. 复现边界

当前 `ChAIR-PIPE` commit `53291b3b0d76c46cb8acdf0e43a132821b656687` 对预处理/QC 有直接价值，但不能独立复现整篇论文。明确未找到的实现包括：

- `VC_sqrt`；
- RNA-adjusted gene-centric PET counts；
- CIS/NFM；
- HiCSR；
- Seurat 下游聚类、注释与空间转移；
- Harmony；
- Monocle3。

仓库 README 列出这些软件不等于提供了相应分析脚本。综合评价是：实验与分析思想清晰，数据公开，预处理代码部分可核验，但核心下游分析代码覆盖不足，复现性约 **2/5**。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## ChAIR

**Paper:** *Tri-omic single-cell mapping of the 3D epigenome and transcriptome in whole mouse brains throughout the lifespan*
**Journal/year:** *Nature Methods*, 2025
**DOI:** `10.1038/s41592-025-02658-7`

### Problem

Most knowledge about how 3D genome folding and chromatin state regulate transcription comes from bulk or separately measured single-cell modalities. Joint RNA+ATAC approaches can connect expression to accessibility but cannot observe chromatin connectivity; joint RNA+Hi-C approaches measure genome structure but have difficulty identifying accessible cis-regulatory elements and enhancer–promoter contacts because contact maps are sparse and noisy (`paper.md:21-24`). Examples cited by the paper include ISSAAC-seq (*Nature Methods*, 2022) on the RNA+ATAC side and GAGE-seq (*Nature Genetics*, 2024) on the RNA+3D-genome side.

### What ChAIR introduces

ChAIR (chromatin accessibility, interaction and RNA profiles) is a droplet-based single-cell tri-omic technology that measures:

- `ChAIR-RNA`: gene expression,
- `ChAIR-ATAC`: accessible chromatin, and
- `ChAIR-PET`: chromatin contacts enriched at open chromatin loci.

Crosslinked cells or nuclei undergo restriction digestion, biotin-linker proximity ligation and Tn5 tagmentation before 10x Multiome droplet barcoding. The design yields RNA and DNA libraries from the same cells; DNA reads support both accessibility and paired-end contact analysis (`paper.md:30-33`, `246-261`). A microfluidic channel can process roughly 6,000–10,000 cells, and the authors report capacity above 100,000 cells with 16 channels.

### Computational overview

```text
RNA library -> Cell Ranger -> RNA matrix -> Seurat/Harmony annotation
DNA library -> ChIA-PIPE/ChAIR-PIPE -> cell barcodes + deduplication
            -> ATAC fragments/peaks
            -> PET contacts and distance spectra
            -> normalized loops + gene-centric PET features
RNA + ATAC + PET -> CIS, enhancer links, trajectories, 3D models and spatial transfer
```

The central analytical ideas are:

1. Normalize accessible-locus loops with `VC_sqrt_score = n/sqrt(xy)`.
2. Construct RNA-adjusted gene-centric PET features from promoter/gene-body contacts.
3. Combine transcription, gene-body/promoter/enhancer accessibility and loops into normalized feature matrices and a cell identity score (CIS).
4. Use the fraction of ultralong contacts (>2 Mb, “megacontacts”) as a single-cell axis of genome compaction, differentiation and aging.
5. Transfer spatial labels from Stereo-seq through ChAIR-RNA, because ChAIR itself has no native spatial coordinates.

### Evaluation and main findings

#### Technical validation

K562 and Patski mixing experiments show that ChAIR recovers all three modalities with reproducible ensemble profiles. ChAIR-RNA and ChAIR-ATAC are comparable with related assays. ChAIR-PET captures fewer total contacts per cell than scHi-C, as expected from targeting open chromatin that covers only about 1–5% of the genome, but more than 40% of its contacts overlap accessible loci (`paper.md:47-53`). Extended Data Figure 1 visually shows much higher ATAC-peak overlap for ChAIR contacts than the Hi-C-based comparisons.

#### Whole-brain lifespan atlas

After QC, the study analyzes 222,698 cells from whole mouse brains at P2, P11, P95, P365 and P730. RNA-guided integration identifies 121 cell types, 45 cell groups and seven broad classes (`paper.md:88-94`). The atlas captures coordinated RNA, accessibility and 3D-genome remodeling from infancy through aging.

#### Cell identity and spatial specificity

Gene-centric PETs cluster cell classes better than all PETs, and tri-modal integration improves separation further. Across 23 groups with sufficient data, composite loop×ATAC features often have higher CIS than transcription alone. Reported examples include OPC 4.04 versus 2.17, MFOL 12.18 versus 2.38 and MOL 6.40 versus 3.56 (`paper.md:94`). Stereo-seq transfer shows that loop and composite 3D epigenomic features can also be more anatomically specific than RNA.

#### Regulatory timing and enhancers

Across cell cycle and multiple differentiation lineages, gene-associated PET signals change before promoter accessibility and RNA. This supports a temporal model in which distal contacts form before promoter opening and transcription activation, although the evidence is observational rather than a perturbation test. ChAIR identifies 562 cell-type-specific enhancers by combining accessibility with at least three PET-supported promoter–enhancer contacts within 2 Mb (`paper.md:97-100`, `473-476`).

#### Megacontacts, nuclear properties and aging

High megacontact fractions are associated with greater genome folding density, lower chromatin accessibility, reduced transcription and smaller nuclear volume. Imaging-linked Extended Data Figure 6 reports correlations of −0.94 with nuclear volume for megacontact ratio, −0.93 for folding density, +0.84 for transcription and +0.89 for accessibility. Megacontact direction depends on lineage—rising during oligodendrocyte maturation but falling during several neuronal maturation trajectories—yet it generally rises with age in mature brain-cell groups. Overall, 36 of 45 groups show positive correlation with both chronological and transcriptomic age, and 29 of those have Pearson correlation >0.5 (`paper.md:187-204`).

### Limitations

- ChAIR-PET has fewer contacts per cell than scHi-C; metacells, pseudobulk aggregation and HiCSR enhancement are used to compensate (`paper.md:207-216`).
- ChAIR has no intrinsic spatial readout; spatial specificity depends on external Stereo-seq transfer and marker validation.
- The proposed contact -> accessibility -> transcription sequence is temporal association, not direct causal perturbation.
- The main text contains a contact-bin ambiguity: the preprocessing paragraph says “over 20 Mb,” whereas megacontact methods/results and figures use >2 Mb.
- Several analyses rely on external reference datasets, pretrained models and software.
- No supplementary Markdown was acquired in this workspace; this analysis does not claim coverage of the step-by-step supplementary protocol or supplementary figures.

### Reproducibility assessment: 2/5

The paper provides a public data accession (`PRJCA024774`) and links ChAIR-PIPE plus a separate ChAIR-Viewer repository (`paper.md:542-551`). The supplied `ChAIR-PIPE` snapshot is fixed at commit `53291b3b0d76c46cb8acdf0e43a132821b656687`.

Direct source reads verify useful preprocessing/QC components: ordered barcode recovery, CB/ZB tag injection, barcode-aware deduplication, per-barcode PET/cis/trans counts, ATAC fragment/peak generation and merged QC summaries. However, the repository is Slurm/site-specific, depends on external ChIA-PIPE and large tool images, contains hard-coded paths, and its checked-in example leaves most DNA-processing calls commented.

Crucially, the supplied snapshot contains no located implementation of `VC_sqrt`, RNA-adjusted gene-centric PET counts, CIS/NFM, HiCSR enhancement, or the Seurat/Harmony/Monocle downstream analyses. It therefore supports preprocessing/QC but not full reproduction of the paper's central analytical results. See `doc_code.md` for the line-level match assessment.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
