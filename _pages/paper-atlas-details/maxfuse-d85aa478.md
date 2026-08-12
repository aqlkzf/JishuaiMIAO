---
layout: default
permalink: /paper-atlas/maxfuse-d85aa478/
title: "MaxFuse"
nav: false
description: "MaxFuse 解决的是跨模态单细胞/空间组学整合问题。这里的难点不是简单批次校正，而是两个数据集测到的特征本来就不同。例如，一个数据集是 CODEX 空间蛋白，只有几十个抗体标记；另一个数据集是 scRNA-seq，有全转录组。两者之间能直接对应的特征很少，而且蛋白和 RNA 的相关性也不一定强。论文把这种情况称为弱链接特征场景（weakly linked features）。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Biotechnology · 2024</span>
    </div>
    <h1>MaxFuse</h1>
    <p>Integration of spatial and single-cell data across modalities with weakly linked features</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## MaxFuse 方法中文解释

### 1. 要解决的问题

MaxFuse 解决的是跨模态单细胞/空间组学整合问题。这里的难点不是简单批次校正，而是两个数据集测到的特征本来就不同。例如，一个数据集是 CODEX 空间蛋白，只有几十个抗体标记；另一个数据集是 scRNA-seq，有全转录组。两者之间能直接对应的特征很少，而且蛋白和 RNA 的相关性也不一定强。论文把这种情况称为弱链接特征场景（weakly linked features）（`paper.md:24-34`, `paper.md:88-100`）。

MaxFuse 的目标是：在只有少量弱对应特征的情况下，仍然为两个模态中的细胞建立可靠匹配，并生成一个共同嵌入空间。这个匹配可以进一步用于标签转移、空间基因表达推断、跨蛋白/RNA/ATAC 的空间投影等分析。

### 2. 输入形式

对两个模态分别记作 `Y` 和 `Z`。每个模态有两类矩阵：

- 全特征矩阵：包含该模态测到的所有可用特征，例如全部 RNA 高变基因或全部蛋白标记。
- 链接特征矩阵：两边列数相同且一一对应，例如蛋白 CD4 与 RNA 基因 `CD4`。

论文记号中，原始全特征矩阵是 `Y` 和 `Z`，链接特征矩阵是 `Y^o=f_y(Y)` 和 `Z^o=f_z(Z)`（`paper.md:130-134`）。代码中对应 `Fusor(shared_arr1, shared_arr2, active_arr1, active_arr2)`：`shared_arr*` 是链接特征，`active_arr*` 是全特征（`code/maxfuse/model.py:24-53`）。

### 3. 核心直觉

如果直接用少量蛋白-RNA 对应特征做匹配，信噪比可能很低。MaxFuse 的关键想法是：虽然跨模态链接很弱，但每个模态内部的全特征仍然能很好地描述细胞之间的相似性。因此可以先在每个模态内部用全特征建图，再用这个图去平滑弱链接特征，使链接特征更稳定。

平滑后，MaxFuse 用这些链接特征得到一批初始匹配。之后不再只依赖链接特征，而是用这些匹配作为锚点，在两边的全特征上学习 CCA 共同嵌入，再在共同嵌入中重新匹配。这个过程迭代多轮，逐步把全特征信息引入跨模态匹配。

### 4. 模糊平滑

论文的平滑公式是：

```text
S_Y(A; w) = w A + (1 - w) A_Y(A)
S_Z(B; w) = w B + (1 - w) A_Z(B)
```

其中 `A_Y(A)` 和 `A_Z(B)` 是每个细胞在同模态邻居图上的局部平均（`paper.md:138-141`）。直观地说，`w` 越小，越相信邻居平均；`w=1` 表示不平滑。

代码中有两种实现：

- `graph_smoothing`：按图邻居平均平滑（`code/maxfuse/utils.py:202-242`）。
- `centroid_shrinkage`：按聚类中心平滑（`code/maxfuse/utils.py:178-199`）。

两者都符合同一个形式：原始值乘以 `wt`，邻域或簇中心目标乘以 `1-wt`。

### 5. 初始匹配

第一阶段只使用平滑后的链接特征。MaxFuse 计算两边细胞之间的距离矩阵，然后解线性分配问题，让每个细胞最多匹配一个对侧细胞，得到初始 pivots（`paper.md:145-148`）。

代码路径是：

- `Fusor.find_initial_pivots` 取出每个 batch 的 shared arrays，并传入平滑参数（`code/maxfuse/model.py:580-657`）。
- `match_utils.get_initial_matching` 先去掉零方差列，做平滑和可选 SVD 去噪，再调用匹配函数（`code/maxfuse/match_utils.py:108-197`）。
- `match_utils.match_cells` 用 Pearson 相关距离并调用 `linear_sum_assignment`（`code/maxfuse/match_utils.py:66-105`）。

因此，初始匹配是对论文线性分配目标的直接代码实现。

### 6. 迭代 CCA 精炼

初始匹配只利用了弱链接特征，所以只是一个起点。第二阶段用当前匹配对齐两边细胞，在全特征空间上拟合 CCA，得到两个模态的共同低维坐标。然后对这些 CCA 坐标再次做同模态平滑，并重新解线性分配问题。重复多轮后，匹配会逐步吸收两边全特征的信息（`paper.md:152-160`）。

代码路径是：

- `Fusor.refine_pivots` 在 active arrays 上运行精炼（`code/maxfuse/model.py:760-865`）。
- `get_refined_matching_one_iter` 执行一轮 CCA、平滑、重新匹配（`code/maxfuse/match_utils.py:200-270`）。
- `get_refined_matching` 按 `n_iters` 重复多轮（`code/maxfuse/match_utils.py:273-390`）。
- `utils.cca_embedding` 负责按当前匹配拟合 CCA，并返回两边所有细胞的 CCA 坐标（`code/maxfuse/utils.py:448-495`）。

### 7. 过滤、传播和最终输出

精炼之后，MaxFuse 会按匹配距离过滤掉质量较差的 pairs，只保留 refined pivots（`paper.md:168`）。代码在 `filter_bad_matches` 中按距离分位数过滤，并在保留 pivots 上重新拟合最终 CCA，然后用最终嵌入中的 Pearson 相关给匹配打分（`code/maxfuse/model.py:998-1127`）。

由于 pivots 只覆盖一部分细胞，MaxFuse 还会做传播：对没有进入 pivot 的细胞，在同模态内找到最近的 refined-pivot 邻居，然后继承这个邻居的跨模态匹配（`paper.md:170`）。代码中的 `propagate` 完成这个步骤（`code/maxfuse/model.py:1128-1243`），最近邻搜索在 `graph.get_nearest_neighbors` 中实现（`code/maxfuse/graph.py:20-60`）。

最终输出有两类：

- 匹配关系：通过 `get_matching` 返回 pivot-only 或 full-data matching，并可按方向去重，例如每个 CODEX 细胞保留一个最佳 RNA 匹配（`code/maxfuse/model.py:1244-1329`）。
- 共同嵌入：通过 `get_embedding` 返回最终 CCA 坐标（`code/maxfuse/model.py:1331-1409`）。

### 8. 批处理和 metacell

大规模空间数据不能直接做完整的 `n_y x n_z` 分配。MaxFuse 用 batching 把数据分成多个 batch pair，分别运行匹配，再汇总 pivots 并在全数据上做最终嵌入和剪枝（`supp.md:283-302`）。代码中的 `split_into_batches` 提供 `max_outward_size`、`matching_ratio` 和 `metacell_size` 等参数（`code/maxfuse/model.py:118-172`, `code/maxfuse/model.py:203-290`）。

metacell 的作用是把相似细胞聚合，降低稀疏性和规模。论文记号允许对任一模态做 metacell，但也建议通常只对高信噪比、能细分细胞状态的模态做。公共代码实现中，`metacell_size > 1` 时主要对 `arr1` 聚合（`paper.md:134`, `code/maxfuse/model.py:490-518`）。

### 9. 空间和三模态分析

论文中的空间分析并不是一个单独的“空间预测模型”。它先用 MaxFuse 匹配 CODEX 细胞和 scRNA-seq 细胞，然后把匹配到的 RNA 表达或细胞类型转移到 CODEX 空间位置上。吨腭 CODEX-scRNA 分析中，Archive 脚本运行 MaxFuse 并保存 full matching 和 UMAP（`code/Archive/tonsil/code/benchmark/method_running/mf_full.py:45-177`），GC 边界附近的基因表达曲线是下游分析脚本绘制的。

HuBMAP 三模态分析也是在 pairwise MaxFuse 基础上扩展：先做 CODEX-snRNA 和 snRNA-snATAC 两个 pairwise alignment，再通过 RNA 作为中介链式连接 pivots，最后用 gCCA 得到三模态嵌入（`paper.md:104-114`, `paper.md:226-230`）。代码证据存在于 Archive notebook，例如 `get_matched_indices` 和 `gcca_init/gcca_refine`（`code/Archive/hubmap/code/analysis/CL_tri-integration.ipynb:1875-1942`, `:2160-2268`）。但这些不是公共包中的正式 API。

### 10. 代码可信度结论

公共包对 pairwise MaxFuse 主算法支持很强：输入结构、batching、图构建、平滑、初始线性分配、CCA 迭代、过滤、传播、方向性剪枝和最终嵌入都能在源码中找到直接实现。

需要保守看待的部分是包装层级：空间表达转移、hold-out protein spatial prediction、三模态 gCCA 不是公共包中的单个函数，而是基于 MaxFuse 输出的 Archive 脚本或 notebook 工作流。因此这篇论文的代码匹配总体应标为 Partial，而不是完全 Exact。

本次 Author pass 没有重跑数值实验，也没有再生成图。所有判断基于论文、补充材料、本地图片和源码行级阅读。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## MaxFuse Summary

### Paper

- Title: Integration of spatial and single-cell data across modalities with weakly linked features
- DOI: 10.1038/s41587-023-01935-0
- PMID: 37679544
- Journal: Nature Biotechnology
- Method: MaxFuse
- Analysis type: paper+code

### Fast Overview

MaxFuse is a cross-modal single-cell and spatial-omics integration method for settings where modalities share only weakly linked features. The key example is targeted protein measurement, such as CODEX or CITE-seq protein panels, integrated with transcriptome or chromatin-accessibility data. The paper argues that many existing integration methods rely on numerous strongly correlated anchors, while spatial proteomics often has only 30-100 markers and weak RNA-protein correspondence (`paper.md:24-34`, `paper.md:88-100`).

The method starts with weak linked features, smooths them using within-modality all-feature neighborhood structure, obtains initial matches by linear assignment, then iteratively refines those matches through CCA coembedding, smoothing, and reassignment. It filters low-quality pivots, propagates matches to non-pivot cells, and outputs both cross-modal matching and a joint embedding (`paper.md:40-52`, `paper.md:130-172`).

### Novelty

- Uses all features indirectly even when only a few weakly linked features are shared.
- Converts weak linked features into a better initialization by fuzzy smoothing over all-feature neighborhood graphs.
- Iteratively improves matching by learning CCA embeddings from current pivots, smoothing those embeddings, and rematching.
- Produces both pivot matches and propagated full-data matches, with directional pruning for task-specific transfer.
- Extends the pairwise framework to spatial and tri-modal applications through matched-cell transfer and pivot chaining/gCCA.

### Main Results

- CITE-seq PBMC benchmarks show MaxFuse leading or near-leading across cell-type matching accuracy, embedding quality, FOSCTTM, and FOSKNN, including reduced antibody panels (`paper.md:56-70`; local Fig. 2).
- Additional ground-truth datasets include CITE-seq BMC, Ab-seq BMC, ASAP-seq PBMC, and TEA-seq PBMC; the paper reports broad gains in weak protein-RNA and protein-ATAC linkage settings and comparable performance under stronger RNA-ATAC linkage (`paper.md:74-84`; local Fig. 3).
- Tonsil CODEX plus scRNA-seq integration transfers transcriptomic information into spatial CODEX coordinates, recovering GC-boundary-associated gene patterns and improving cell-type annotation against CELESTA/Astir baselines (`paper.md:88-100`; local Fig. 4).
- HuBMAP CODEX/snRNA/snATAC analysis chains pairwise alignments through RNA and uses gCCA to map RNA expression, gene activity, and TF motif enrichment onto tissue locations (`paper.md:104-114`, `paper.md:226-230`; local Fig. 5).

### Code And Reproducibility

The public package closely matches the pairwise MaxFuse core. `Fusor` stores linked/shared arrays and active/all-feature arrays, builds batches and graphs, performs initial matching, CCA refinement, filtering, propagation, final matching, and embedding (`code/maxfuse/model.py:24-53`, `:118-172`, `:443-657`, `:760-865`, `:998-1409`). Utility files implement smoothing, SVD, CCA, correlation distance, and graph operations (`code/maxfuse/match_utils.py:66-390`, `code/maxfuse/utils.py:178-527`, `code/maxfuse/graph.py:20-253`).

Public tutorials demonstrate CITE-seq and tonsil protein-RNA workflows (`code/docs/tutorials.rst:1-7`). Manuscript-specific tonsil and HuBMAP analyses are present in `Archive/`, sometimes with development-era naming and notebook-local helper code (`code/Archive/tonsil/code/benchmark/method_running/mf_full.py:45-177`, `code/Archive/hubmap_nature/CL_0719production.py:87-256`, `code/Archive/hubmap/code/analysis/CL_tri-integration.ipynb:1875-2268`).

Code-paper match: **Partial overall**. The reusable pairwise algorithm is implemented directly and strongly. Spatial transfer, hold-out protein prediction, and tri-modal gCCA are supported as manuscript workflows or notebooks, not as stable public package APIs. No numerical rerun was performed in this Author pass.

### Data Notes

The paper states all datasets are public, listing links for CITE-seq, Ab-seq, TEA-seq, ASAP-seq, tonsil CODEX/scRNA-seq, retina multiome, PBMC multiome, mouse brain multiome, and cerebral cortex multiome (`paper.md:330-332`). Code availability points to the MaxFuse GitHub repository (`paper.md:334-336`). The acquired workspace contains code source metadata for `https://github.com/shuxiaoc/maxfuse` at commit `2900b260b697deec678060ea653015291c4dc5cb`.

### Key Gaps

- `claude_notes.md` was absent; navigation used `session_summary.md`, `pipeline_state.json`, `scratch/evidence_index.json`, CodeGraph, and direct source reads.
- No packaged public API was found for tri-modal chaining/gCCA.
- No packaged public API was found for spatial gene/protein imputation; those analyses use matches plus downstream aggregation/plotting.
- The code was not executed and figures were not regenerated.
- The acquired code directory does not retain a nested `.git`; use the workspace sidecar commit metadata rather than parent-repo git state.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
