---
layout: default
permalink: /paper-atlas/covarnet-9ff62b2a/
title: "CoVarNet"
nav: false
description: "CoVarNet 的关键贡献是把“细胞亚群丰度的共变模式”转化为可解释的多细胞网络：NMF 给出可能一起出现的节点，特异相关性给出可信的边，最终得到可用于组织空间验证、表型关联和癌症重塑分析的 cellular modules。"
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
      <span>Atlases &amp; Resources</span>
      <span>Nature · 2025</span>
    </div>
    <h1>CoVarNet</h1>
    <p>Cross-tissue multicellular coordination and its rewiring in cancer</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41586-025-09053-4" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## CoVarNet 方法中文解读

### 这篇论文解决什么问题？

这篇 Nature 2025 论文研究的是：不同组织中的多种细胞类型是否会形成可重复的“多细胞协同模块”，以及这些模块在癌症中如何被重塑。作者整理了一个大型人类健康组织单细胞图谱，包含 35 个组织、706 个样本和 2,293,951 个高质量细胞，然后用 CoVarNet 从细胞亚群丰度的协方差中寻找跨组织重复出现的 cellular modules, 即 CMs（`paper.md:12-12`, `paper.md:27-47`）。

传统的细胞互作分析常常从配体-受体对或空间邻近关系出发。这类方法适合解释局部细胞通信，但论文认为它们不够适合系统刻画跨组织、跨多细胞类型的高阶组织结构（`paper.md:18-21`）。CoVarNet 的目标是从“哪些细胞亚群在不同样本中一起变多或变少”这个角度，构建可解释的多细胞网络。

### 核心思想

CoVarNet 把每个样本表示为一个“细胞亚群频率向量”。如果某些细胞亚群在很多样本中协同变化，并且这种协同关系不是泛泛地和所有细胞都相关，而是对特定细胞对更强，那么这些细胞亚群就可能构成一个 CM。

它不是只做 NMF，也不是只做相关网络，而是把两条证据合起来：

1. NMF 找“候选节点”：哪些细胞亚群在同一个潜在因子中权重最高。
2. 相关性和特异性找“候选边”：哪些细胞亚群对之间有显著且特异的协同变化。

最终，一个 CM 网络由 NMF 选出的候选节点和特异相关的边共同决定（`paper.md:259-263`）。

### 输入和输出

输入是细胞注释和样本信息。核心矩阵是：

- 行：细胞亚群；
- 列：样本；
- 值：某个细胞亚群在其所属大类细胞中的频率；
- 归一化：对频率矩阵做 min-max normalization，使不同大类细胞中亚群数量差异的影响降低（`paper.md:265-268`）。

输出包括：

- 每个 CM 的网络：节点是细胞亚群，边是特异相关的细胞亚群对；
- 每个样本的 CM 活性：来自 NMF 的系数矩阵；
- 每个样本的 CMT 标签：活性最高的 CM 对应的类型（`paper.md:310-313`）。

### 计算流程

```text
细胞注释表
  |
  v
按样本统计每个 cell subset 的数量
  |
  v
在 major cell type 内计算 subset frequency
  |
  v
min-max 归一化，得到 subset x sample 矩阵
  |
  +------------------------------+
  |                              |
  v                              v
NMF 分解频率矩阵              计算细胞亚群两两相关
每个 factor 取 top subsets    计算相关系数、FDR、specificity
作为候选节点                 作为候选边
  |                              |
  +--------------+---------------+
                 v
          构建 CM 网络
          删除孤立节点
                 |
                 v
      CM 活性、CMT 分类、空间映射、
      轨迹分析和癌症重塑分析
```

这个流程和论文 Fig. 2a 的可视化一致。代码中也能看到相应的可复用模块：频率计算和归一化在 `CoVarNet/R/CoVarNet.R:26-90`，相关性和 specificity 在 `CoVarNet/R/CoVarNet.R:155-204`，网络构建在 `CoVarNet/R/CoVarNet.R:222-322`。

### 第一步：构建频率矩阵

论文要求只保留合适的样本，并对每个样本计算细胞亚群在对应大类细胞中的频率。pan-tissue 分析中，最终矩阵包含 76 个非上皮细胞亚群和 510 个样本（`paper.md:265-268`）。

GitHub 包中的 `freq_calculate(meta)` 与这一步直接对应。它要求输入至少包含 `sampleID`、`majorCluster`、`subCluster` 三列。代码先统计 `subCluster x sampleID` 的计数表，再按 `majorCluster` 分组，对每个样本列除以该大类细胞的总数（`CoVarNet/R/CoVarNet.R:26-56`）。因此，这里的频率不是某个亚群占全样本细胞总数的比例，而是它在自己所属大类细胞中的相对比例。

`freq_normalize(mat_fq, normalize="minmax")` 接着对每个亚群的频率做行级 min-max 归一化（`CoVarNet/R/CoVarNet.R:69-90`）。代码还提供 z-score 模式，但论文主体方法写的是 min-max normalization（`paper.md:268-269`）。

### 第二步：NMF 找候选节点

论文用 NMF 对频率矩阵分解。具体说，作者使用 R 的 `NMF` 包和 nsNMF 方法，rank 从 2 到 20，运行 30 次得到 consensus output；pan-tissue atlas 选择的 rank 是 12（`paper.md:271-280`）。每个 factor 中权重最高的前 10 个细胞亚群作为该 CM 的候选节点（`paper.md:274-275`）。

当前 GitHub 包没有直接给出 rank 搜索、CCC 评估或 30 次 consensus 的完整脚本。包中的 `cm_network(NMFres, Corres, top_n=10, ...)` 是从已经得到的 NMF 结果开始：它读取 `basis(NMFres)`，按每个 CM 的权重排序，并保留 top `top_n` 亚群（`CoVarNet/R/CoVarNet.R:222-258`）。

这说明：GitHub 包实现了“给定 NMF 结果后如何构图”的可复用部分，但完整复现论文的 NMF 参数搜索还需要论文提到的其他分析代码。

### 第三步：特异相关细胞亚群对

CoVarNet 的边不是普通相关边，而是“特异相关”的边。论文先计算所有细胞亚群两两 Pearson correlation，得到相关矩阵 \(R\)。对任意一对亚群 \(i,j\)，论文定义背景集合：

$$
{S}_{ij}=\&#123;&#123;r}_{ik}| k\ne i\}\cup \&#123;&#123;r}_{kj}| k\ne j\}
$$

再定义 specificity：

$$
{\rm Spec}({r}_{ij})=\frac{| \{r\in {S}_{ij}| r\le {r}_{ij}\}| }{| {S}_{ij}| }
$$

直观理解：如果 \(r_{ij}\) 比大多数和 \(i\) 或 \(j\) 有关的其他相关系数都高，那么这对细胞亚群的相关性更“特异”（`paper.md:283-295`）。

代码中的 `pair_correlation(mat_fq, method="pearson")` 直接实现了这一步。它调用 `psych::corr.test` 计算相关系数和 p 值，用 `p.adjust(..., method="fdr")` 得到 FDR，然后对每个上三角元素构造背景 `bg`，并用 `mean(bg <= cor_mat[i, j])` 计算 specificity（`CoVarNet/R/CoVarNet.R:155-204`）。

specificity cutoff 的论文公式是：

$$
{\rm Cutoff}(n,N)=1-\frac{(n-1)\times 2-1}{(N-1)\times 2-1}
$$

其中 \(n\) 是每个 CM 假定包含的 subset 数量，\(N\) 是总 subset 数量（`paper.md:295-298`）。代码中对应为：

```r
spe_cutoff <- 1 - ((top_n - 1) * 2 - 1) / ((n_all - 1) * 2 - 1)
```

位置在 `CoVarNet/R/CoVarNet.R:276-279`。

最终，边需要同时满足：

- correlation > `corr`，默认 0.2；
- FDR <= `pval_fdr`，默认 0.05；
- specificity >= 自动 cutoff。

代码位置是 `CoVarNet/R/CoVarNet.R:270-279`。

### 第四步：构建 CM 网络

每个 NMF factor 给出候选节点，特异相关模块给出候选边。CoVarNet 对每个 CM 取这些节点的诱导子图，并删除没有边连接的孤立节点（`paper.md:304-307`）。

代码中 `cm_network` 的主要步骤是：

- 用过滤后的边构建全局无向图；
- 对每个 CM，用 top NMF subsets 与全局图顶点取交集；
- 构建子图；
- 删除 degree 为 0 的节点；
- 返回 global network、each CM network、原始 NMF 结果、过滤后的 CM 组件和注释表（`CoVarNet/R/CoVarNet.R:282-322`）。

需要注意一个缺口：论文还说会计算 connectivity score，并用 10,000 次节点标签 permutation test 评估显著性（`paper.md:307`）。这个步骤在论文和扩展图中出现，但在当前检查的 GitHub 包文件中没有找到直接实现。

### 第五步：CM 活性和样本分类

论文用 NMF 的 coefficient matrix 表示每个样本的 CM 活性，并将样本分配给活性最高的 CM，形成 CMT 标签（`paper.md:310-313`）。

代码中 `gr.distribution(nmf_res, ...)` 读取 `scoef(nmf_res)`，对每个样本列用 `which.max` 找到最高活性的 CM，然后生成 `CMT01`、`CMT02` 等标签，并绘制热图（`CoVarNet/R/plot.R:151-266`）。

对于新 scRNA-seq 样本，`sc_cm_recover(ref, mat_fq)` 固定参考 NMF 的 \(W\) 矩阵，只更新新样本的 \(H\) 系数矩阵，从而恢复新样本中的 CM abundance（`CoVarNet/R/CoVarNet.R:336-387`）。

### 空间、轨迹和癌症扩展

论文把 CMs 映射到空间转录组数据。方法上，作者先用 cell2location 估计每个 spot 中细胞亚群丰度，再用 NMF 权重聚合出 CM activity（`paper.md:346-355`）。包中 `st_cm_recover` 实现了后半部分：对每个 CM，把 spot 中组件亚群丰度乘以权重再求和，并用 99th percentile 缩放（`CoVarNet/R/CoVarNet.R:399-416`）。

空间统计方面，包中有两个直接对应论文概念的函数：

- `colocalization`：用 spot 之间的亚群频率相关性计算 CM 内部共定位分数（`CoVarNet/R/CoVarNet.R:429-451`）；
- `bvMoranI`：用 bivariate Moran's I 计算空间聚集关系（`CoVarNet/R/CoVarNet.R:464-517`）。

乳腺绝经轨迹分析中，论文使用 CM12 细胞亚群频率、z-score normalization、Scanpy neighbors/Leiden、PHATE 和 Palantir pseudotime（`paper.md:481-488`）。包中 `freq_reduction` 和 `pseudotime` 提供了通用 PHATE/Palantir 辅助函数（`CoVarNet/R/CoVarNet.R:532-580`），`gr.phate` 和 `gr.trajectory` 提供可视化（`CoVarNet/R/plot.R:470-595`）。

癌症扩展中，论文将 CoVarNet 应用于 pan-cancer atlas，识别 cancer-associated CMs，并强调肿瘤进展中同时存在健康组织特异 CM 的丢失和 cCM02 的出现（`paper.md:158-181`, `paper.md:496-571`）。包中的相关性和网络构建函数可以支持这类分析的核心构图步骤，但完整 pan-cancer 数据整理、TOSICA 注释、TCGA 验证和 pre-invasive lesion 分析不在当前 GitHub 包快照中。

### 图像证据如何支持方法

Fig. 2 是最重要的方法图。它清楚展示了 CoVarNet 的两条分支：NMF 选节点，specificity correlation 选边，最后形成 CM networks 和 sample activities（`images/figure_02.png`, caption `paper.md:59-64`）。

Fig. 3 展示空间验证：CM05 在 Peyer's patch 相关区域更集中，CM02/CM03 更偏向肠道黏膜免疫结构；后续面板展示 CellPhoneDB 和 cytokine response 证据（`images/figure_03.png`, `paper.md:82-114`）。

Fig. 4 展示 phenotype 分析：脾脏 CM05/CM06 随年龄呈相反趋势，乳腺 CM12 与绝经和 fibroblast trajectory 相关（`images/figure_04.png`, `paper.md:120-155`）。

Fig. 5 展示癌症重塑：健康 CM 活性下降，同时 cancer-associated cCM02 随肿瘤进展增强（`images/figure_05.png`, `paper.md:158-181`）。

### 代码复现边界

当前 GitHub 包与论文的核心 CoVarNet 构图方法匹配度为 **中等**：

- 直接匹配：频率矩阵、min-max normalization、Pearson/FDR/specificity、specificity cutoff、CM 网络构建、孤立节点删除、CM/CMT 可视化、scRNA-seq 和 spatial recovery、colocalization/Moran's I、PHATE/Palantir 辅助函数。
- 部分匹配：NMF 结果消费和 top subset 选择，但缺少论文中的 rank scan、CCC 选择和 30 次 consensus 运行脚本。
- 未找到：connectivity score 的 10,000 次 permutation test；CellPhoneDB/CellChat；Immune Dictionary cytokine enrichment；DIALOGUE；SCENIC；TCGA 和 pre-invasive lesion 完整分析。

论文也明确写到 GitHub 仓库提供 CoVarNet source code，其他 analysis code 在 Zenodo（`paper.md:586-589`）。因此，当前本地包更适合复用 CoVarNet 核心方法，而不是单独复现整篇论文的所有结果。

### 一句话总结

CoVarNet 的关键贡献是把“细胞亚群丰度的共变模式”转化为可解释的多细胞网络：NMF 给出可能一起出现的节点，特异相关性给出可信的边，最终得到可用于组织空间验证、表型关联和癌症重塑分析的 cellular modules。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## CoVarNet Summary

### Paper

**Cross-tissue multicellular coordination and its rewiring in cancer**. Nature 2025. DOI: `10.1038/s41586-025-09053-4`.

The paper studies how diverse cell types coordinate across human tissues and how those multicellular organizations change in cancer. The authors curate a pan-tissue single-cell atlas of 2,293,951 cells from 706 healthy samples across 35 tissues, then use CoVarNet to identify recurring cellular modules (CMs) from covariance in cell-subset frequencies (`paper.md:12-12`, `paper.md:27-47`).

### Motivation

Existing ligand-receptor and spatial-neighborhood approaches can describe local cell-cell interactions, but the paper argues that they do not fully capture higher-order tissue-level coordination across many cell types and tissues (`paper.md:18-21`). CoVarNet is designed to infer recurrent co-occurring modules from single-cell abundance patterns, then map and test those modules in spatial, phenotypic and cancer contexts (`paper.md:56-57`, `paper.md:187-193`).

### Method In Brief

CoVarNet starts from a cell-subset-by-sample frequency matrix. Frequencies are calculated within each broad cell type and min-max normalized to make subsets comparable across lineages and samples (`paper.md:265-268`; `CoVarNet/R/CoVarNet.R:26-90`).

The algorithm has two parallel branches:

- NMF on the frequency matrix prioritizes top-weighted subsets as candidate CM nodes (`paper.md:271-275`; `CoVarNet/R/CoVarNet.R:237-258`).
- Pairwise Pearson correlations identify candidate edges, using correlation coefficient, FDR and a specificity score that measures how high a subset-pair correlation is relative to correlations involving either member (`paper.md:283-301`; `CoVarNet/R/CoVarNet.R:155-204`).

For each NMF factor, CoVarNet connects top node candidates through specifically correlated edges and removes isolated nodes, producing one CM network per factor (`paper.md:304-307`; `CoVarNet/R/CoVarNet.R:282-322`). CM activity in samples is taken from the NMF coefficient matrix, and samples are assigned a CMT label by their most abundant CM (`paper.md:310-313`; `CoVarNet/R/plot.R:151-190`).

### Main Results

Applying CoVarNet to the healthy pan-tissue atlas identified 12 CMs. The paper reports that 67 of 76 non-epithelial subsets participated in at least one CM, 17 subsets appeared in multiple CMs, and the CMs showed distinct tissue preferences (`paper.md:70-79`). Fig. 2 visually supports this: the workflow panel shows the NMF-node plus specificity-edge design, the network panel shows 12 CM graphs, and the heatmap/table panels summarize tissue prevalence and hypothesized roles (`images/figure_02.png`; caption `paper.md:59-64`).

The authors validate and interpret CMs through multiple downstream analyses:

- GTEx bulk RNA-seq recovery supports that CMT-like signals can be detected outside the discovery scRNA-seq atlas (`paper.md:73-73`, `paper.md:316-337`; `images/figure_08.jpg`).
- Spatial transcriptomics and Xenium support spatial organization of intestinal CMs, with CM05 linked to Peyer's-patch-associated structure and CM02/CM03 to mucosal immune modules (`paper.md:82-114`; `images/figure_03.png`).
- Spleen ageing analysis shows opposite trends for CM05 and CM06, with CM05-associated regulons increasing with age (`paper.md:120-140`; `images/figure_04.png`).
- Breast CM12 analysis links specialized fibroblast dynamics to a menopausal trajectory using PHATE and Palantir-style pseudotime (`paper.md:143-155`; `CoVarNet/R/CoVarNet.R:532-580`).
- Pan-cancer analysis shows loss of tissue-specific healthy CM activity and emergence of a cancer-associated cCM02 ecosystem during tumour progression (`paper.md:158-181`; `images/figure_05.png`).

### Reproducibility And Code-Paper Match

The paper provides curated data on Zenodo and an interactive resource, and states that CoVarNet source code is on GitHub while other analysis code is on Zenodo (`paper.md:580-589`). The local GitHub package snapshot is commit `e59b314941e73c8a6eb008ee537cfd461c7e10bd` and contains reusable R functions for the CoVarNet core, plotting, scRNA-seq/spatial recovery and PHATE/Palantir trajectory helpers (`CoVarNet/README.md:1-25`; `CoVarNet/R/CoVarNet.R:26-580`; `CoVarNet/R/plot.R:23-595`).

Code-paper fidelity for the GitHub package is **medium**. The core frequency, correlation/specificity, specificity cutoff, network construction, visualization, spatial-statistics and trajectory-helper logic are directly matched. However, the probed package does not contain the paper's full atlas construction, BBKNN/scIB benchmarking, NMF rank scan and 30-run consensus script, connectivity-score permutation test, CellPhoneDB/CellChat communication analysis, Immune Dictionary cytokine enrichment, DIALOGUE/SCENIC workflows, TCGA validation or full pan-cancer analysis scripts. Those missing pieces should be treated as paper-described or external-analysis-code claims, not verified behavior of the GitHub package snapshot.

### Practical Takeaway

CoVarNet is best understood as a network-building layer over sample-level cell-subset abundance. It turns abundance covariance into interpretable multicellular module graphs by combining latent co-occurrence factors with specificity-filtered pairwise correlations. The available package is useful for reproducing or reusing that core layer when supplied appropriate frequency matrices and NMF/correlation objects, but reproducing the entire Nature analysis requires additional data, preprocessing workflows and external analysis code beyond the probed package.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
