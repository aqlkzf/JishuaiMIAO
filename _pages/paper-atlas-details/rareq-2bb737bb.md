---
layout: default
permalink: /paper-atlas/rareq-2bb737bb/
title: "RareQ"
nav: false
description: "稀有细胞群的困难不只是“细胞少”。标准聚类往往优先解释占比大的结构：分辨率太低时，小群被并入大群；分辨率太高时，又会产生大量没有生物学意义的小碎片。RareQ 的出发点是：一个可信的小群即使规模小，其成员在 k 近邻图中也应形成相对紧密、与外部连接较少的局部拓扑。 因此，RareQ 先在细胞近邻图上衡量局部紧密程度，再用高紧密度邻域引导标签传播，最后通过一组尺寸、连通性和距离规则合并不稳定的小群。"
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
      <span>Domain Clustering</span>
      <span>Nature Communications · 2026</span>
    </div>
    <h1>RareQ</h1>
    <p>Cell neighborhood topology directs rare cell population identification</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-026-71180-x" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for RareQ">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xiaolab-xjtu/RareQ" target="_blank" rel="noopener noreferrer" aria-label="Open code for RareQ">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RareQ：从邻域拓扑中识别稀有细胞群

### 1. RareQ 要解决什么问题

稀有细胞群的困难不只是“细胞少”。标准聚类往往优先解释占比大的结构：分辨率太低时，小群被并入大群；分辨率太高时，又会产生大量没有生物学意义的小碎片。RareQ 的出发点是：一个可信的小群即使规模小，其成员在 k 近邻图中也应形成相对紧密、与外部连接较少的局部拓扑。

因此，RareQ 先在细胞近邻图上衡量局部紧密程度，再用高紧密度邻域引导标签传播，最后通过一组尺寸、连通性和距离规则合并不稳定的小群。它输出的是**每个细胞的聚类标签**，而不是一个独立的“稀有/非稀有”二分类标志；哪些输出群被称为稀有群，仍需结合群大小、标记基因和实验背景判断。

### 2. 输入、输出和真正的适用边界

核心函数 `FindRare()` 的输入不是原始计数矩阵，而是一个已经完成降维并保存 kNN 结果的 Seurat 对象。代码从 `assay.nn` 邻居槽读取近邻编号和距离。因此完整数据流是：

1. 对 RNA、ATAC、蛋白或空间表达数据做相应预处理；
2. 构建 PCA、LSI、sPCA 或 WNN 等低维表示；
3. 用 Seurat `FindNeighbors(..., return.neighbor = TRUE)` 构建 kNN 图；
4. `FindRare()` 在这个图上计算局部拓扑并返回聚类标签。

论文展示了 scRNA-seq、CITE-seq、scATAC-seq、WNN 多组学和 Xenium 空间数据，但 RareQ 本身并不联合建模不同模态，也不直接使用空间坐标。它消费的是上游表示所产生的邻居图，所以结果会继承上游降维、批次校正和图构建的偏差。

### 3. Q 值：概念公式与代码实现

论文用内部连接和外部连接解释邻域质量：

$$
Q = \frac{|IC|}{|IC| + |OC|},
$$

其中 $IC$ 表示候选邻域内部的连接，$OC$ 表示从该邻域指向外部的连接。$Q$ 越高，说明这个局部集合越像一个自洽的小群，而不是大群边缘的随机碎片。

代码中的精确定义更具体。对细胞 $i$，先取它的前 $k$ 个邻居组成集合 $S_i$，再查看集合内每个细胞自己的近邻表，统计这些有向近邻是否仍落在 $S_i$ 中。也就是说，代码衡量的是“细胞 $i$ 的邻居集合内部有多紧密”，而不只是细胞 $i$ 与其邻居直接相连多少。

当集合大小达到 $k$ 时，分母为 $k|S_i|$；很小的集合会用 `max(|S_i|, 5)^2` 归一化。这一至少为 5 的分母会惩罚极小集合，避免两三个细胞仅凭互为近邻就得到过高 Q 值。这是论文概念公式没有充分展开、但会实际影响结果的实现细节（`RareQ/R/utils.R`、`RareQ/R/FindRare.R`）。

一个小例子：若 $S_i$ 有 6 个细胞，每个成员考察 6 条近邻边，总共有 36 个可能的内部命中；若其中 27 条仍指向 $S_i$，则代码意义下的局部紧密度约为 $27/36=0.75$。若集合只有 3 个细胞，即使存在 9 次内部命中，分母仍至少为 $25$，得分为 $0.36$，不会被轻易认作稳定稀有群。

### 4. 从 Q 值到初始社区

`FindRare()` 先让每个细胞拥有独立标签，然后按邻域 Q 值传播标签。直观上，每个细胞寻找邻域中 Q 最高的成员，并采用该成员的标签；随后 C++ 投票内核反复根据邻居标签更新，直到收敛或达到 `max_iter`。

这一步相当于让局部拓扑紧密的细胞成为“吸引中心”：处在同一紧密邻域中的细胞逐渐获得相同标签。实现中的平局并不是随机解决：R 端最高 Q 平局取最小邻居索引；C++ 端若所有候选标签都只出现一次，则取第一个邻居标签。因此邻居顺序在极端平局情况下可能影响结果。

### 5. 为什么初始社区还不能直接作为结果

标签传播会产生许多小社区，其中既有真实稀有群，也有噪声和大群边缘碎片。RareQ 随后进行多轮筛除与合并：

- 数据规模相关阈值使用总细胞数的 1% 和 3%；
- 连通性低于 0.5 或细胞数少于 5 的社区先被视为不稳定；
- 后续还会检查簇间边数、簇内紧密度、近邻距离变化和簇大小；
- 代码包含 0.6、0.65、0.8、0.85 等硬编码阈值，以及针对极小簇的距离突变规则；
- `Q_cut` 和 `ratio` 参与决策，但并不是决定最终标签的全部参数。

因此，RareQ 不是由一个单一目标函数或一个 Q 阈值完全决定的模型。论文将其概括为 Q 引导的传播与递归合并，而公开实现是一个包含多条经验规则的确定性流程。这也是代码—论文匹配评为 **medium** 而不是 exact 的主要原因。

### 6. 可选的 ConsensusRare

`ConsensusRare()` 重复扰动低维嵌入、重新构建近邻图并调用 `FindRare()`，然后统计任意两个细胞在多次运行中共同聚类的频率，得到共识矩阵，最后用 Ward.D2 层次聚类并按多次运行中最常见的簇数切树。

这里有两个重要边界：

1. 代码通过打乱嵌入行的数值再恢复原始行名来形成扰动，并用索引排序把标签映射回原细胞；它不是一个概率生成模型。
2. 共识矩阵是细胞数乘细胞数的稠密矩阵，且代码用嵌套循环写入。因此其内存和时间至少含有 $O(N^2)$ 部分。论文图 3 展示的百万级可扩展性应谨慎理解为核心 RareQ 流程的能力，不能无条件外推到对百万细胞运行 `ConsensusRare()`。

### 7. 代码中容易忽略的辅助行为

`CreateObject()` 在只有低维嵌入时，会生成随机的虚拟计数矩阵来满足 Seurat 对象构造要求。后续若明确在 PCA 等 reduction 上建立近邻，虚拟计数不会决定 kNN 图；但对象创建本身在未设随机种子时并非逐位可重复。复现实验时应记录随机种子、Seurat 版本、使用的 reduction、维度数和 `FindNeighbors` 参数，而不能只记录 RareQ 的 `k`、`Q_cut` 与 `ratio`。

### 8. 如何读论文八幅主图

- 图 1 给出 Q 的拓扑直觉和从近邻图、Q 计算、传播到合并的总体流程。
- 图 2 在模拟数据和 20 个真实 scRNA-seq 数据集上比较 F1、precision、recall、NMI 等指标，支持 RareQ 对稀有群检测的总体竞争力。
- 图 3 展示 140 万小鼠脑细胞上的运行时间和内存可扩展性；这是核心流程的重要工程证据，但不等于稠密共识矩阵也能同规模运行。
- 图 4 说明 RNA、ATAC 与 WNN 表示均可先转成近邻图再交给 RareQ；证据支持“图接口通用”，而不是 RareQ 内部完成多模态融合。
- 图 5 至图 7 分别在气道上皮、B 淋巴瘤和阿尔茨海默病数据中展示小群及其标记特征，属于生物学一致性验证。
- 图 8 在 Xenium 小鼠脑数据中识别海马 CA2/CA3 等小区域，验证主要依赖解剖位置和标记基因一致性，并非独立实验金标准。

### 9. 证据强度与复现判断

公开仓库覆盖核心 Q 计算、标签传播、合并、共识流程以及多种数据教程；主图和补充材料也提供了广泛评估。因此核心方法具备较好的可检查性。限制在于：最终结果依赖多条硬编码经验规则，公开仓库中未找到一套可一键重建所有论文基准图的完整脚本，而且主论文网页导出的 Markdown 正文不完整，很多方法和评估细节需要从补充材料核验。

综合判断：**核心机制可复现，完整论文结果复现仍为 partial**。使用者应优先复现近邻图构建和关键数据集结果，并对 `k`、上游 embedding、邻居数、`Q_cut`、`ratio` 及合并阈值相关敏感性进行检查。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Answer First

RareQ identifies candidate rare cell populations from the topology of a precomputed cell k-nearest-neighbor graph. Its useful idea is that a biologically coherent small population should form a locally compact neighborhood rather than merely contain few cells. The public implementation realizes this idea with a neighborhood compactness score, Q-guided label propagation, and several rounds of heuristic filtering and merging. The central method is implemented and inspectable, but reproducing every paper benchmark remains partial because many evaluation details are supplement-heavy and the repository does not expose one end-to-end script for all reported figures.

### Inputs and Outputs

The core `FindRare()` function expects a Seurat object containing an `assay.nn` neighbor object. RNA, ATAC, protein, WNN, or spatial information must first be converted into a low-dimensional representation and kNN graph by upstream tooling. RareQ then returns one cluster label per cell. It does not return a separate rare-cell flag; rarity must be interpreted from cluster size, topology, markers, and biological context.

### Method

For each cell, RareQ takes its first k neighbors and measures how many directed neighbor links from members of that set remain inside the set. This implementation-level score is a concrete version of the paper's internal-versus-outward connectivity Q. Very small sets are penalized through a denominator floor. Cells initially have singleton labels and adopt labels associated with high-Q neighbors; a C++ majority-vote routine continues propagation. The resulting fragments are filtered and merged using dataset-size thresholds, connectivity, edge counts, distance jumps, `Q_cut`, `ratio`, and multiple hard-coded cutoffs.

`ConsensusRare()` optionally repeats the analysis after perturbing embeddings and builds a co-clustering matrix. Its dense N-by-N consensus matrix introduces an O(N²) memory/time component, so the paper's million-cell scalability evidence for the core workflow should not be extended uncritically to the consensus wrapper.

### Evidence and Results

The paper evaluates simulated PBMC settings and 20 real scRNA-seq datasets using F1, precision, recall, and NMI, and compares RareQ with established rare-cell methods. Figure 3 reports execution on roughly 1.4 million mouse-brain cells with favorable runtime and memory behavior for the core workflow. Further case studies cover RNA/protein, RNA/ATAC and WNN-derived graphs, airway epithelial cells, B-cell lymphoma, Alzheimer's disease glia, and Xenium mouse-brain spatial data. These examples support broad graph-interface applicability and biological plausibility. They do not show that RareQ itself performs native multimodal integration or spatial modeling: those structures are created upstream.

The public code matches the paper at the level of kNN topology, Q-like compactness, propagation, refinement, and tutorial data flows. Fidelity is **medium**, because the final labels depend on more hard-coded, size-specific rules than the high-level paper description suggests. Spatial validation is primarily anatomical and marker-based rather than an independent experimental ground truth.

### Reproducibility

Rating: **4/5 for inspecting and rerunning the core method; partial for regenerating the complete publication**.

Strengths include a public R package, readable core functions, a C++ voting kernel, tutorials for several upstream representations, local main figures, and extracted supplementary information. Important limitations are the threshold-heavy refinement logic, missing one-command benchmark reconstruction, incomplete main-article text in the exported Nature Markdown, and an auxiliary `CreateObject()` helper that creates random dummy counts unless the seed is controlled. A robust rerun should record the upstream embedding, dimensions, Seurat and RareQ versions, neighbor parameters, random seed, `k`, `Q_cut`, and `ratio`.

### Evidence Pointers

- Paper and supplement: `paper.md`, `paper source/supp/MOESM1.txt`
- Main figures: `paper source/images/fig1.png` through `fig8.png`
- Core algorithm: `RareQ/R/FindRare.R`
- Q implementation: `RareQ/R/utils.R`, `RareQ/R/functions.R`
- Consensus wrapper: `RareQ/R/ConsensusCluster.R`
- Voting kernel and tutorials: `RareQ/src/knn_vote.cpp`, `RareQ/Tutorials/`

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
