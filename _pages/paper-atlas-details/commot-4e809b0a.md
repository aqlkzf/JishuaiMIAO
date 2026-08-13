---
layout: default
permalink: /paper-atlas/commot-4e809b0a/
title: "COMMOT"
nav: false
description: "COMMOT 要解决的是空间转录组里的细胞-细胞通讯推断问题。传统基于 scRNA-seq 的通讯方法多半只看配体和受体表达，或者在细胞群层面打分；但真实通讯有两个关键约束：第一，配体和受体只能在有限空间范围内发生作用；第二，一个配体可能结合多个受体，一个受体也可能被多个配体竞争，所以不同分子和不同细胞之间的通讯不能完全独立地打分。"
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
      <span>Cell-Cell Communication</span>
      <span>Nature Methods · 2023</span>
    </div>
    <h1>COMMOT</h1>
    <p>Screening cell-cell communication in spatial transcriptomics via collective optimal transport</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41592-022-01728-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for COMMOT">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/zcang/COMMOT" target="_blank" rel="noopener noreferrer" aria-label="Open code for COMMOT">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## COMMOT 方法中文解读

### 这篇论文要解决什么问题？

COMMOT 要解决的是空间转录组里的细胞-细胞通讯推断问题。传统基于 scRNA-seq 的通讯方法多半只看配体和受体表达，或者在细胞群层面打分；但真实通讯有两个关键约束：第一，配体和受体只能在有限空间范围内发生作用；第二，一个配体可能结合多个受体，一个受体也可能被多个配体竞争，所以不同分子和不同细胞之间的通讯不能完全独立地打分（`paper.md:21-33`, `42-62`）。

论文提出 COMMOT，即 COMMunication analysis by Optimal Transport。它把空间位置、配体/受体表达、配体-受体数据库和分子竞争统一放进一个 collective optimal transport（COT，集体最优传输）模型中，用来推断每个发送细胞、接收细胞、配体、受体之间的通讯强度（`paper.md:56-62`, `190-204`）。

### 为什么已有方法不够？

论文指出，CellPhoneDB、ICELLNET、CellChat 等方法主要依赖配体/受体表达函数，部分方法考虑复合体或下游基因网络，但很多非空间方法会产生空间上不可能发生的假阳性通讯。Giotto、CellPhoneDB v3、stLearn、SVCA、MISTy、NCEM 等空间方法利用了邻域或空间信息，但通常更偏局部、按细胞对或邻域独立处理，忽略全局竞争关系（`paper.md:21-27`）。

COMMOT 的核心改进是：把多个配体、多个受体、多个细胞之间的竞争一起建模，而不是对每个配体-受体对分别求一个局部分数。这样，一个细胞或一种分子的“可用通讯容量”会被不同竞争对象共享，符合论文强调的生物物理直觉（`paper.md:27-33`, `45-62`）。

### 核心模型直觉

设空间数据里有 \(n_s\) 个细胞/spot，\(n_l\) 个配体，\(n_r\) 个受体。COMMOT 要求解一个四维张量：

$$
P^\ast \in \mathbb{R}_+^{n_l \times n_r \times n_s \times n_s}
$$

其中 \(P^\ast_{i,j,k,l}\) 表示发送 spot \(k\) 通过配体 \(i\) 和接收 spot \(l\) 的受体 \(j\) 发生通讯的强度（`paper.md:56-62`）。

这个张量有三个约束：

1. 如果配体 \(i\) 和受体 \(j\) 不在数据库的可结合集合 \(I\) 中，则对应通讯强度为 0。
2. 对每个配体和发送 spot，传输出去的总量不能超过该配体表达量。
3. 对每个受体和接收 spot，接收到的总量不能超过该受体表达量。

论文的优化目标是最小化传输成本，同时惩罚没有被传输的配体/受体质量（`paper.md:196-204`）。成本矩阵由空间距离构造，超过配体-受体空间作用范围的距离会被设成无穷大，所以远距离不允许通讯（`paper.md:204-204`）。

### 从输入到输出的计算流程

```text
空间表达矩阵 + 空间坐标 + 配体-受体数据库
        |
        v
过滤数据中不存在的配体/受体基因
        |
        v
构造配体表达矩阵 S、受体表达矩阵 D、
配体-受体可结合矩阵 A、空间距离矩阵 M、距离阈值 cutoff
        |
        v
求解四类 COT 子问题：
1. 所有配体 -> 所有受体
2. 单个配体 -> 所有受体
3. 所有配体 -> 单个受体
4. 单个配体 -> 单个受体
        |
        v
按权重合并每个配体-受体对的传输矩阵
        |
        v
输出 spot-by-spot CCC 矩阵、发送/接收总信号、
方向场、cluster-level 通讯、下游基因分析
```

代码中，`spatial_communication` 是主要入口。它会过滤配体-受体表，构造 `CellCommunication` 模型，运行 COT，然后把每个配体-受体对、每条通路、总通讯矩阵写入 AnnData 的 `.obsp`；同时把每个细胞/spot 的发送信号和接收信号写入 `.obsm`（`COMMOT_repo/commot/tools/_spatial_communication.py:251-504`）。

### 最优传输求解器如何工作？

论文把 COT 重写成一个 unnormalized optimal transport 问题，加入传输矩阵和未匹配质量的熵正则项，再用 Sinkhorn 迭代求解。当 \(\epsilon_p=\epsilon_\mu=\epsilon_\nu\) 时，论文给出 \(f\) 和 \(g\) 的迭代更新，并用

$$
\hat{P}^\ast=e^{(f\oplus g-C)/\epsilon}
$$

重建传输矩阵。论文明确说研究中的结果使用这个等正则系数形式（`paper.md:207-229`）。

代码中，`cot_sparse` 会把配体/细胞和受体/细胞展平，构造稀疏块状成本矩阵，只保留允许结合且在空间阈值内的项，然后调用 `unot` 求解（`COMMOT_repo/commot/_optimal_transport/_cot.py:233-337`）。`unot_sinkhorn_l1_dense` 和 `unot_sinkhorn_l1_sparse` 直接实现了 \(f,g\) 的 Sinkhorn 更新，并返回 `exp((f+g-C)/eps)` 形式的传输矩阵（`COMMOT_repo/commot/_optimal_transport/_unot.py:136-187`, `288-342`）。

一个重要的代码细节是：实现会先按 `max(S.sum(), D.sum())` 归一化配体/受体总质量，求解后再缩放回去；稀疏成本矩阵也会按最大有限成本缩放。这是代码中的数值实现行为，不是论文主文中单独强调的建模假设（`COMMOT_repo/commot/_optimal_transport/_cot.py:267-337`）。

### 下游分析做什么？

COMMOT 不只输出通讯矩阵，还提供几个下游分析模块。

**空间信号方向。** 给定 spot-by-spot 通讯矩阵 \(S\)，论文构造发送方向场 \(V^s\) 和接收方向场 \(V^r\)，用 top-k 发送/接收对象的空间位移方向加权求和（`paper.md:232-237`）。代码中的 `communication_direction` 会把这些方向场写入 `.obsm['commot_sender_vf-*']` 和 `.obsm['commot_receiver_vf-*']`（`COMMOT_repo/commot/tools/_spatial_communication.py:507-657`）。

**cluster-level CCC。** 论文把 spot 级矩阵 \(S\) 聚合成 cluster-by-cluster 矩阵 \(S^{cl}\)，并用标签置换计算 p 值（`paper.md:238-242`）。代码中的 `summarize_cluster` 和 `cluster_communication` 实现了这个流程；另一个 `cluster_communication_spatial_permutation` 会在置换空间位置后重新计算 COT，用来避免简单标签置换可能低估跨 cluster 通讯的问题（`COMMOT_repo/commot/tools/_spatial_communication.py:208-231`, `659-971`）。

**下游基因分析。** 论文先用接收信号 \(r_i=\sum_jS_{j,i}\) 作为 cofactor，通过 tradeSeq 找到随通讯信号变化的基因；再用随机森林把潜在下游基因作为输出，把通讯信号和高度相关基因作为输入特征，用通讯信号的特征重要性衡量其独特影响（`paper.md:259-265`）。代码中 `communication_deg_detection` 调用 R/tradeSeq，`communication_impact` 和 `_utils/_similarity.py` 中的 tree-based 函数实现了树模型打分（`COMMOT_repo/commot/tools/_downstream_analysis.py:32-182`, `235-446`; `COMMOT_repo/commot/_utils/_similarity.py:85-158`）。

需要注意：论文说随机森林里使用 Gini importance；本地代码返回的是基于 feature importance 排名的归一化分数，而不是直接输出原始 Gini importance，所以这一点是部分匹配。

### 图像和实验结果说明什么？

本地读取的 11 张图显示了从方法示意到多数据集应用的完整输出形态。Fig. 1 展示 COT 如何处理多配体/多受体竞争和距离约束。Fig. 2-5 展示皮肤、MERFISH、STARmap、seqFISH+、Slide-seqV2、Visium 等数据上的接收信号图、方向场、cluster-level 热图、下游基因热图和 LR-pair impact 热图。Extended Data Fig. 1 展示 PDE 模拟验证和 COMMOT 相对 pairwise OT 的优势。Extended Data Fig. 6 展示 Dpp/Wg 信号在 subsampling 下的方向、cluster-level 通讯和下游基因鲁棒性（`figure_analysis.md`; `paper.md:449-494`）。

论文还报告 COMMOT 在模拟数据上优于相关 OT 变体，在多种空间技术上捕捉到符合已知生物学的通讯活动，并在多数比较数据集中比 CellChat、Giotto、CellPhoneDB 有更强的下游靶基因相关性（`paper.md:65-68`, `151-160`）。

### 复现和代码匹配情况

本地 GitHub 包对核心方法的匹配度是 **medium-high**。核心 API、COT 稀疏构造、等正则 Sinkhorn 求解、方向场、cluster-level CCC、tradeSeq 下游基因分析和树模型 impact 分析都有直接源码证据（详见 `doc_code.md`）。

但不能说本 workspace 可以完整复现论文所有图。论文的 Code availability 写明：开源软件在 GitHub，复现实验结果的代码在 Zenodo（`paper.md:295-298`）。本 workspace 只获取了 GitHub 包，未获取 Zenodo 复现实验脚本。另外，Supplementary Information 没有转换成本地 markdown，所以补充推导不可直接核验；论文中的 F005 加权 cosine distance 在图里出现，但本地 GitHub 包里没有找到完全对应的实现。

综合判断：本 workspace 足以解释和核验 COMMOT 的核心算法包实现，但不足以独立复现论文全部结果图。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## COMMOT Summary

COMMOT (COMMunication analysis by Optimal Transport) is a method and Python package for inferring cell-cell communication (CCC) from spatial transcriptomics or spatially annotated single-cell data. The core problem is that ligand-receptor communication is spatially constrained and competitive: many ligands and receptors can bind multiple partners, and a cell or molecule species has finite interaction capacity, so independent pairwise scores can overstate interactions or miss competition (`paper.md:21-33`, `42-62`).

The proposed method is collective optimal transport (COT). It estimates a transport tensor \(P_{i,j,k,l}\), where ligand \(i\) from sender spot \(k\) communicates with receptor \(j\) at receiver spot \(l\), while enforcing admissible ligand-receptor pairs, finite ligand/receptor marginal capacities, and spatial distance cutoffs (`paper.md:56-62`, `190-204`). The optimization is rewritten as an entropy-regularized unnormalized OT problem and solved with a Sinkhorn-style iteration in the equal-regularization case used for the study (`paper.md:207-229`).

In the local code, the main package path matches this design at medium-high fidelity. The public API filters ligand-receptor pairs, builds ligand/receptor expression matrices, distance/cost cutoffs, runs sparse COT, writes pair/pathway/total communication matrices to AnnData, and stores sender/receiver summaries (`COMMOT_repo/commot/tools/_spatial_communication.py:251-504`). The OT backend constructs sparse block costs and dispatches to unnormalized OT (`COMMOT_repo/commot/_optimal_transport/_cot.py:233-337`), while the equal-regularization Sinkhorn updates are directly implemented in dense and sparse solver functions (`COMMOT_repo/commot/_optimal_transport/_unot.py:136-187`, `288-342`).

COMMOT is more than the COT matrix. The paper and package add downstream analyses: spatial signaling direction vector fields (`paper.md:232-237`; `COMMOT_repo/commot/tools/_spatial_communication.py:507-657`), cluster-level CCC summaries and permutation p-values (`paper.md:238-242`; `COMMOT_repo/commot/tools/_spatial_communication.py:208-231`, `659-971`), graph-based grouping of communication networks (`paper.md:253-253`; `COMMOT_repo/commot/tools/_downstream_analysis.py:449-562`), and downstream gene analysis with tradeSeq plus tree/correlation-based impact scoring (`paper.md:259-265`; `COMMOT_repo/commot/tools/_downstream_analysis.py:32-182`, `235-446`).

The evaluation spans PDE simulations, human epidermis, MERFISH, STARmap, seqFISH+, Slide-seqV2, Visium breast cancer, Visium mouse brain, and subsampling robustness. The local figure images show the method schematic, simulation comparisons to PDE/pairwise OT, direction fields, cluster-level CCC heatmaps, CCC-induced clustering, signaling-dependent gene heatmaps, LR-pair impact heatmaps, and robustness plots (`figure_analysis.md`; paper anchors `paper.md:65-68`, `85-91`, `97-108`, `120-160`, `449-494`). The paper reports that COMMOT outperforms related OT variants in simulations and generally has stronger downstream-target correlation than CellChat, Giotto, and CellPhoneDB in the compared datasets (`paper.md:65-68`, `151-160`).

Reproducibility is good for the package-level method and incomplete for full paper-result reproduction. The paper states that the open-source software is at GitHub and reproduction code is available separately on Zenodo (`paper.md:295-298`). The local package includes toy tests for COT output, direction vectors, and cluster summaries, but not the full analysis scripts. The exact implementation of the paper's F005 weighted cosine-distance metric for subsampled vector fields was not found in `COMMOT_repo/commot` or tests; only adjacent vector-field similarity utilities were found. Supplementary derivations are also unavailable as markdown because `SUPP_MD=none`.

Overall reproducibility rating: **3.5/5**. The core GitHub package strongly covers the algorithmic workflow and downstream utilities, with line-verifiable source for the main method. Missing Zenodo reproduction scripts, missing local supplementary derivations, and the absent exact F005 implementation prevent claiming full figure/result reproducibility from this workspace alone.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
