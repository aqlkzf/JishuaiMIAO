---
layout: default
permalink: /paper-atlas/scepi2-seq-1b88d27f/
title: "scEpi2-seq"
nav: false
description: "scEpi²-seq 把“抗体定位的组蛋白修饰片段”和“同一片段上的 CpG 甲基化”装进同一个单细胞、单分子读出中，并额外利用片段起点间距推断核小体周期结构。它的关键价值不是简单叠加两种组学，而是能在同一批细胞中讨论复制时序、染色质环境与甲基化维持速度之间的关系。"
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
    <h1>scEpi2-seq</h1>
    <p>Single-cell multi-omic detection of DNA methylation and histone modifications reconstructs the dynamics of epigenomic maintenance</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-025-02847-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scEpi2-seq">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/cgeisenberger/taps-manuscript" target="_blank" rel="noopener noreferrer" aria-label="Open code for scEpi2-seq">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scEpi²-seq 方法与实现解析

### 一句话定位

scEpi²-seq 把“抗体定位的组蛋白修饰片段”和“同一片段上的 CpG 甲基化”装进同一个单细胞、单分子读出中，并额外利用片段起点间距推断核小体周期结构。它的关键价值不是简单叠加两种组学，而是能在同一批细胞中讨论复制时序、染色质环境与甲基化维持速度之间的关系。

### 整体流程

```text
组蛋白修饰抗体
      ↓
pA–MNase 定位并切割标记核小体
      ↓
384 孔单细胞分选（FUCCI 实验同时记录荧光）
      ↓
末端修复 + A 尾 + 细胞条形码/UMI/T7/Illumina 接头
      ↓
整板混池 → TAPS 化学转换
      ↓
IVT → 逆转录 → PCR → 双端测序
      ↓
比对位置：组蛋白修饰与切点
C/T 状态：CpG 甲基化
片段起点距离：核小体间距
```

抗体先把 pA–MNase 固定到目标修饰附近。加入钙离子后，MNase 切下相邻 DNA。每个孔内接头包含单细胞 barcode、UMI、T7 启动子和 Illumina 序列，因此后续可以混池。TAPS 将 5mC 转换成最终测序中的 T，而未甲基化 C 保留为 C；这与亚硫酸氢盐测序的读出方向不同。TAPS 无法区分 5mC 与 5hmC，因此论文把信号解释为“主要来自 5mC”，而不是化学上的绝对专一。

### 从 reads 到联合表型

论文方法描述了 Cutadapt、`bwa mem` 与 `SingleCellMultiOmics` 的处理链。上游代码中的 `TAPSMolecule`/`TAPSCHICMolecule` 负责上下文判断、共识碱基和 BAM 标签；手稿仓库中的 R 代码再解析这些表格或标签。

同一原始分子经 IVT/PCR 产生多个拷贝。实现按 cell barcode、UMI、read-one 起点和方向等键分组，在碱基质量阈值与多数票规则下形成共识。于是每个 CpG 可记作甲基化计数 \(m\) 或未甲基化计数 \(u\)：

\[
\text{methylation beta}=\frac{m}{m+u}.
\]

同一片段的比对起点给出抗体靶向染色质的位置；两个切点的距离在约 90、180、270 bp 处出现周期带，对应核小体尺度的组织结构。

需要注意：两个仓库之间的接口在源码语义上吻合，但没有一份随论文发布的命令清单证明该数据集具体使用了哪些完整参数。因此这里是“源码支持的连接”，不是已经复跑验证的运行轨迹。

### 质量控制如何建立可信度

作者使用四类互补证据：

1. 甲基化 lambda spike-in 检查 TAPS 转换，约 95%。
2. 空孔比真实细胞少几个数量级的 reads，说明背景低。
3. 组蛋白信号与 ENCODE ChIP-seq、既有 sortChIC 比较，并计算 FRiP：

\[
   \mathrm{FRiP}=\frac{\text{落在相应 peaks 内的 reads}}{\text{全部比对 reads}}.
   \]

4. CpG 甲基化与 WGBS 在 10 kb bin 和单 CpG 层面比较。

K562 共处理 2,660 个细胞，保留 1,981 个；通过 QC 的细胞通常覆盖超过 50,000 个 CpG，FRiP 为 0.72–0.88，单 CpG 与 WGBS 的相关性超过 0.8。RPE-1 共处理 3,420 个细胞，保留 1,716 个；FRiP 为 0.83–0.88，基因组尺度与 WGBS 的相关性超过 0.9。RPE-1 中还出现过度 MNase 消化群体，论文通过较低 FRiP 和异常平均甲基化将其排除。

### 复制耦联的甲基化维持

FUCCI 的 Geminin/Cdt1 荧光为每个细胞提供周期位置。论文使用 Wanderlust 把二维荧光轨迹转成 integrated cell-cycle progression，再把既有 scEdU-seq 的 S 期进程对齐到 0.4–0.8 区间。之后按复制时序、组蛋白修饰和细胞周期对甲基化做滚动窗口/LOESS 平滑。

结果显示：S 期复制会造成几百分点的甲基化下降，随后逐渐恢复。早复制、H3K36me3 富集区域较快恢复；晚复制的 H3K9me3/H3K27me3 区域在进入 G1 后仍可继续维持修复。把甲基化变化再按 MNase 切点距离分层后，约 90/180/270 bp 的周期结构说明“离标记核小体多远”也与恢复动力学相关。

这里的强结论是复制时序与局部染色质环境共同预测维持速度；它不是干预实验，所以不能仅凭这些图宣称某个组蛋白修饰直接造成甲基化恢复变慢。

### 小鼠肠道中的两层调控

H3K27me3 片段先汇总到 50 kb bin，进入 Signac/Seurat 的 TF-IDF、SVD/LSI、UMAP 和图聚类。粗分群得到吸收、分泌和免疫三类，再细分为七个亚群。CpG 调用则被导出为 BisMark 输入，交给 MethSCAn 选择可变甲基化区域并进行 PCA/UMAP/Leiden 聚类。

DMR 比较要求两个条件中至少覆盖 25 个 CpG 且校正后 \(P<0.001\)，再用 Ward.D2 对高排名区域和细胞群进行层次聚类。视觉上，H3K27me3 能较细地解析谱系，而 5mC 主要形成两个更粗的簇；但 DMR 并不完全跟随 H3K27me3 亚群，说明在 facultative heterochromatin 中，CpG 甲基化提供了非冗余的调控层。

### 代码对应关系

- `taps-manuscript/scripts/estimate_conversion.py`：lambda spike-in 共识与转换率统计。
- `taps-manuscript/scripts/split_bam_by_cellbarcode.py`：按 BAM tag 拆分单细胞 BAM，用于 FRiP。
- `taps-manuscript/code/EDF_1_to_3_functions.R`：FRiP 与 SCMO 甲基化字段解析。
- `taps-manuscript/code/Figure_2.R`：FUCCI、scEdU、复制时序与甲基化的合并和平滑。
- `taps-manuscript/code/Figure_3.R`：切点距离、周期进程与甲基化比例。
- `taps-manuscript/code/EDF_and_Figure_4_*.R`：肠道 H3K27me3 聚类、MethSCAn 输入和 DMR 图。
- `SingleCellMultiOmics/singlecellmultiomics/molecule/taps.py`：TAPS 上下文与分子级甲基化调用。
- `SingleCellMultiOmics/.../bamtagmultiome.py`：选择 TAPS–ChIC 分子类型并输出标签。

### 复现边界

可读源码足以理解主要算法并重写若干步骤，但不足以从 FASTQ 一键生成全部图。主要障碍是：R 脚本含作者工作站绝对路径；若干 RDS/TSV 中间对象未发布；Figure 1 引用了仓库外的 `dist_1d.cpp`；没有完整工作流、容器或环境锁；未找到论文实际使用的 Wanderlust 调用，MethSCAn 的完整执行也不在手稿仓库中。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper

**Single-cell multi-omic detection of DNA methylation and histone modifications reconstructs the dynamics of epigenomic maintenance**
Nature Methods 22, 2042–2051 (2025)
DOI: `10.1038/s41592-025-02847-4`

### Core contribution

The study introduces scEpi²-seq, a plate-based assay combining antibody-targeted pA–MNase chromatin profiling with TAPS chemistry. Each sequenced molecule can report the targeted histone-mark context, CpG methylation and nucleosome-scale cut spacing while preserving a single-cell barcode and UMI. This enables direct analysis of epigenetic relationships in the same cells rather than post hoc integration of separate assays.

### Main findings

- In K562 cells, 1,981 of 2,660 profiles pass QC, with more than 50,000 CpGs per cell, FRiP of 0.72–0.88, approximately 95% conversion, and single-CpG agreement with WGBS above Pearson `r=0.8`.
- In FUCCI RPE-1 cells, 1,716 of 3,420 profiles pass QC, with FRiP of 0.83–0.88 and genome-wide TAPS/WGBS correlation above 0.9.
- Methylation transiently declines during S phase. Recovery extends into G1 in late-replicating H3K27me3/H3K9me3 domains and varies with distance to marked nucleosomes.
- In mouse intestine, H3K27me3 resolves absorptive, secretory and immune lineages and subtypes. CpG methylation forms a different partition and identifies DMRs that provide information beyond H3K27me3.

### Code and data

The workspace contains the manuscript analysis repository `taps-manuscript` at commit `a2ace7a89ddb6b7396fec3e38125042fbb52ec98` and the paper-named upstream `SingleCellMultiOmics` snapshot at commit `22eaa5afa9585c0fe91ce1ac48b821e2380a09fa`.

### Reproducibility assessment

**Overall: 3/5 (medium).** Major calculations and figure transformations are inspectable, and the conversion/FRiP utilities are explicit. A clean raw-data rerun is not currently possible from the snapshots alone: figure scripts use absolute workstation paths and unpublished intermediate objects; an end-to-end workflow and environment lock are absent; and the exact Wanderlust and MethSCAn manuscript invocations were not found. The work is therefore well supported for method understanding and partial reimplementation, but not for bit-for-bit reproduction without reconstruction.

### Recommended reading order

1. `doc_method.md` for the assay and analysis logic.
2. `figure_analysis.md` for the evidence carried by all ten figures.
3. `doc_code.md` for exact paper-to-code matches and gaps.
4. `Chinese method notes` for a Chinese implementation-grounded explanation.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
