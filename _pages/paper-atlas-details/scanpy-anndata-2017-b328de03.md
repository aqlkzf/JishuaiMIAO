---
layout: default
permalink: /paper-atlas/scanpy-anndata-2017-b328de03/
title: "Scanpy_AnnData_2017"
nav: false
wide: true
description: "这篇 Genome Biology（2018）论文要解决的是单细胞转录组分析在大规模数据上的可用性问题。论文认为，Seurat（Nature Biotechnology, 2015）、Monocle（Nature Biotechnology, 2014）、SCDE/PAGODA（Nature Methods, 2014）、MAST（Genome Biology, 2015）、Cell Ranger（Nature Communicatio…"
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
      <span>Computational Tools</span>
      <span>Genome Biology · 2018</span>
    </div>
    <h1>Scanpy_AnnData_2017</h1>
    <p>Scanpy / AnnData: large-scale single-cell gene expression data analysis</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/scverse/scanpy" target="_blank" rel="noopener noreferrer" aria-label="Open code for Scanpy_AnnData_2017">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Scanpy / AnnData 方法解读

### 它要解决什么问题？

这篇 *Genome Biology*（2018）论文要解决的是单细胞转录组分析在大规模数据上的可用性问题。论文认为，Seurat（*Nature Biotechnology*, 2015）、Monocle（*Nature Biotechnology*, 2014）、SCDE/PAGODA（*Nature Methods*, 2014）、MAST（*Genome Biology*, 2015）、Cell Ranger（*Nature Communications*, 2017）、scater（*Bioinformatics*, 2017）和 scran（*F1000Research*, 2016）已经提供了许多实用步骤，但难以把完整流程扩展到百万级细胞（`paper.md:20`）。

### 核心想法：数据容器加共享图

Scanpy 不是提出一个新的损失函数或预测模型；它将常见单细胞步骤组织成可扩展的 Python 工作流。AnnData 是中心数据容器：

```text
表达矩阵 X（细胞 x 基因）
 + obs：细胞注释
 + var：基因注释
 + uns：非结构化结果与参数
 -> 一个可持续补充分析结果的对象
```

论文强调 AnnData 支持稀疏矩阵和 HDF5 backed 模式，因此无需把整个对象读入内存；Scanpy 函数默认原地写入，也允许非破坏性变换（`paper.md:41`）。另一个关键点是只计算一次细胞邻域图，再让聚类、可视化和随机游走相关步骤复用它，减少计算和彼此不一致的表示（`paper.md:43`）。

### 计算流程

Figure 1 中的 PBMC 示例给出了最清晰的流程（`paper.md:28-30`）：

```text
原始计数和注释
  -> 回归混杂因素、归一化、高变基因
  -> 低维表示与邻域图
  -> Louvain 聚类 -> 差异基因排序 -> cluster marker
  -> tSNE / 力导向图 / diffusion map 可视化
  -> 选择根细胞 -> diffusion pseudotime -> 分支轨迹
```

输入是细胞 x 基因矩阵及其注释；输出可以包括细胞分群、marker 基因、二维可视化、扩散伪时间和分支轨迹。论文只描述模块和工作流，没有给出可复现的数学公式、优化目标或全部参数，不能从本文补写这些细节。

### 结果怎样支持可扩展性？

作者报告：在 2,700 个 PBMC 的 Seurat 改编教程中，各步骤快 5-90 倍；与 Cell Ranger R 在 68,579 个 PBMC 上比较时快 5-16 倍；还在八核服务器上用数小时处理了 130 万个 E18 小鼠脑细胞，且没有下采样（`paper.md:35`）。

### 代码对应关系与边界

当前快照是 Scanpy `main`（`9df46b48096ae330349ac4c5bca89354e05d37a9`），不是 2017/2018 年的发布版本。当前 `highly_variable_genes` 会将特征选择结果写进 `adata.var`（`src/scanpy/preprocessing/_highly_variable_genes.py:738-759,827-844`），当前邻域函数会把距离和连接矩阵写进 `adata.obsp`（`src/scanpy/neighbors/__init__.py:275-302`）；这说明了 AnnData 驱动的设计仍然存在。

但不能把今天的 API 当作论文实现：当前可视化代码是 UMAP，而论文展示的是 tSNE、Fruchterman-Reingold 和 diffusion map；当前聚类是 Leiden，而论文使用 Louvain（`doc_code.md`）。论文实际演示链接指向独立的 `theislab/scanpy_usage` 仓库（`paper.md:69-80`），该仓库及论文年代的代码并未获得。因此，历史版本的 tSNE、Louvain、DPT、marker 排序和具体参数均标为 `Not found`，而不是推测为已验证实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Scanpy / AnnData: Large-Scale Single-Cell Analysis

### Problem

In 2018, single-cell workflows had useful components in Seurat, Monocle, SCDE/PAGODA, MAST, Cell Ranger, scater, and scran, but the authors argue that these frameworks did not handle datasets reaching or exceeding one million cells while retaining an integrated analysis workflow (`paper.md:20`).

### What the Paper Introduces

Scanpy is a Python toolkit for preprocessing, visualization, graph clustering, marker-gene ranking, diffusion pseudotime, trajectory analysis, and related workflows. AnnData is its annotated matrix contract: an expression matrix plus cell, gene, and unstructured annotations, supporting sparse storage and HDF5 backing (`paper.md:26,41`). The key design decision is to reuse a single neighborhood graph across downstream methods instead of recomputing incompatible representations (`paper.md:43`).

### Evaluation

The paper reports a Seurat-derived 2,700-PBMC tutorial with 5-90x per-step speedups, a 68,579-PBMC Cell Ranger comparison with 5-16x speedups, and analysis of 1.3 million E18 mouse-brain cells without subsampling in a few hours on eight cores (`paper.md:35`). Figure 1 visually connects preprocessing, embeddings, Louvain groups, marker ranking, and diffusion pseudotime, and includes the large-cell clustering view. These are author-reported demonstrations; this workspace did not rerun them.

### Reproducibility Assessment

**Rating: 2/5.** The article supplies public Scanpy/AnnData repositories and links six demonstration/benchmark workflows in `theislab/scanpy_usage` (`paper.md:65-80`). This workspace acquired the current public Scanpy `main` source, but not a paper-era release or the linked usage repository/data. The modern snapshot still illustrates AnnData mutation, feature selection, PCA, and neighbor-graph conventions, but it uses UMAP and Leiden where the paper reports tSNE and Louvain. Consequently, `doc_code.md` makes no Exact historical source matches; historical implementation details, parameters, runtime setup, and the notebooks required to rerun the published benchmarks remain `Not found` in the acquired evidence.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
