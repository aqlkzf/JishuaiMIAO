---
layout: default
permalink: /paper-atlas/rt-t-amp-merfish-256c6204/
title: "RT_T_AMP_MERFISH"
nav: false
description: "传统高分辨率 FISH 成像通常要给每条 RNA 配许多探针，因此很难识别短 RNA 或只相差很短片段的异构体；测序法覆盖广，但空间分辨率与单分子定位较弱。本文将原位扩增 RT&T-AMP 与 MERFISH 结合，在完整小鼠脑切片中输出“每个分子在何处、属于哪个基因/异构体”的空间坐标和身份。 RT&T-AMP 先把原始 RNA 原位变成许多仍留在原位置的 RNA 拷贝：poly-T 引物从 poly-A 尾开始逆转录；"
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
      <span>Cell · 2026</span>
    </div>
    <h1>RT_T_AMP_MERFISH</h1>
    <p>Whole-transcriptome-scale isoform-resolved spatial imaging of single cells in tissues</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RT&T-AMP-MERFISH：全转录组、异构体分辨的空间成像

### 它解决什么问题？

传统高分辨率 FISH 成像通常要给每条 RNA 配许多探针，因此很难识别短 RNA 或只相差很短片段的异构体；测序法覆盖广，但空间分辨率与单分子定位较弱（`paper.md:25-35`）。本文将原位扩增 RT&T-AMP 与 MERFISH 结合，在完整小鼠脑切片中输出“每个分子在何处、属于哪个基因/异构体”的空间坐标和身份。

### 核心新意

RT&T-AMP 先把原始 RNA 原位变成许多仍留在原位置的 RNA 拷贝：poly-T 引物从 poly-A 尾开始逆转录；逆转录酶产生 CCC 末端；带 T7 启动子的模板转换寡核苷酸接入；T7 聚合酶再转录生成局部 RNA amplicon（`paper.md:39-43`）。因此，即使每个靶标只有较少编码探针，也能产生可辨识的信号。图 1 的流程图和 1/5 探针对照直接展示了这个逻辑。

### 从组织到结论的计算流程

```text
组织 RNA
 -> RT + 模板转换 + T7 扩增
 -> 编码探针 + 多轮三色 MERFISH 成像
 -> 每一 bit 的图像堆栈和 fiducial 漂移校正
 -> 滤波/反卷积/像素条码解码/空白条码过滤
 -> 单分子坐标
 -> 细胞分割或空间像素汇总
 -> 基因模块、细胞类型、空间差异、LR 邻近和异构体使用分析
```

为避免信号拥挤，约 23,000 个基因分成两次背靠背的 90-bit、HD4/HW4 MERFISH 运行；总计 60 个三色轮次（`paper.md:47-49`）。异构体实验用第三次运行，合计约 33,000 条目标序列（`paper.md:91-93`）。

### 解码在做什么？

每个像素跨 bit 的强度组成向量 $x_p$。在通用 MERlin 实现中，先扣背景并按 bit 缩放，再做 L2 归一化：

$$
\tilde{x}_p=\frac{(x_p-b)/s}{\lVert(x_p-b)/s\rVert_2}。
$$

随后寻找最近的归一化 codeword，只有距离和强度都通过阈值才接受；相邻的已解码像素再汇成一个分子（`MERlin/merlin/util/decoding.py:85-196,230-346`）。论文报告使用 CuPy 加速 90-bit 距离计算；仓库确有可选 GPU 分支，但默认关闭，且没有论文实际运行配置，故不能把它当成该研究的精确复现（`decode.py:86-88,268-273`）。

### 异构体指标如何读？

若同一基因的第 $i$ 个异构体分数为 $p_i$，被检测的异构体数为 $N$，作者计算

$$
H=-\sum_i p_i\log_2p_i,\qquad H_{norm}=H/\log_2N.
$$

$H_{norm}=0$ 表示一个异构体几乎独占，$H_{norm}=1$ 表示使用均匀（`paper.md:299-303`）。图 5-7 进一步把异构体空间图、细胞类型富集和转录本结构并列，从而显示脑区和细胞类型特异的异构体使用。

### 证据边界与可复现性

论文描述了 Dark Sectioning + Cellpose-SAM 3D 分割、SimpleElastix CCF 配准、Hotspot、Scanpy、ALLCools、LR 和异构体下游分析（`paper.md:249-309`）。本工作区提供的 MERlin 快照只验证了通用 codebook/像素解码路径；论文专用图像、codebook、参数 JSON、CCF/Cellpose-SAM 与下游脚本均为 **MISSING** 或 **Not found**。因此它适合学习通用 MERFISH 解码，而不能在此处端到端复现论文。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## RT&T-AMP-MERFISH

RT&T-AMP-MERFISH is an imaging-based spatial-transcriptomics technology designed to bridge a gap between targeted, high-resolution imaging and broad but lower-resolution sequencing. It uses in situ poly-T reverse transcription, template switching, and T7 transcription to make a local RNA amplicon, allowing MERFISH to use few probes even for short isoform-specific sequence (paper.md:25-35,39-43).

The study combines two 90-bit MERFISH runs to image about 23,000 genes in four mouse-brain sections, and three runs to image about 33,000 sequences including about 10,000 isoforms (paper.md:47-53,91-93). It reports reproducible gene counts, agreement with bulk RNA-seq, spatial gene modules, cell-type/regional DE and ligand-receptor proximity analyses, plus structure- and cell-type-specific isoform use. The main quantitative isoform summary is normalized Shannon entropy (paper.md:299-303).

Figure evidence supports the chemistry (Fig. 1), molecule/bit-stack decoding and gene-level agreement (Fig. 2), spatial modules (Fig. 3), cell/LR analyses (Fig. 4), and isoform-resolved maps (Figs. 5-7). A key interpretation boundary is that colocalized ligand-receptor pairs are spatial-proximity observations, not direct causal evidence of signaling.

### Reproducibility

The workspace includes a generic `MERlin` framework snapshot (commit `0f96cc5`). It directly supports codebook access and generic pixel decoding, including an optional GPU nearest-distance branch. However, paper-specific codebooks, raw images, task JSONs, enabled parameters, CCF registration, Cellpose-SAM workflow, and downstream Hotspot/Scanpy/ALLCools/LR/isoform scripts are MISSING or Not found in the searched snapshot. Thus code-paper fidelity is low for end-to-end reproduction and partial only for the generic decoding layer.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
