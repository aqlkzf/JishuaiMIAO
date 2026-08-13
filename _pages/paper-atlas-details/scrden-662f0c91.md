---
layout: default
permalink: /paper-atlas/scrden-662f0c91/
title: "scRDEN"
nav: false
description: "scRDEN 面向单细胞 RNA-seq 的细胞亚群识别、拟时序轨迹推断和动态基因网络分析。文章的基本判断是：直接使用单个基因的表达量做轨迹推断容易受 dropout、噪声、细胞异质性和复杂分支结构影响；相对而言，细胞内基因对的表达排序关系更稳定，适合用来构造更鲁棒的轨迹特征。这个动机在摘要、引言和 Fig."
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
      <span>Dynamics, Fate &amp; Trajectory</span>
      <span>Scientific Reports · 2025</span>
    </div>
    <h1>scRDEN</h1>
    <p>scRDEN: single-cell dynamic gene rank differential expression network and robust trajectory inference</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41598-025-01969-1" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for scRDEN">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scRDEN 方法中文解读

### 这篇文章解决什么问题？

scRDEN 面向单细胞 RNA-seq 的细胞亚群识别、拟时序轨迹推断和动态基因网络分析。文章的基本判断是：直接使用单个基因的表达量做轨迹推断容易受 dropout、噪声、细胞异质性和复杂分支结构影响；相对而言，细胞内基因对的表达排序关系更稳定，适合用来构造更鲁棒的轨迹特征。这个动机在摘要、引言和 Fig. 1 中都有体现：作者强调将不稳定的基因表达值转成相对稳定的基因-基因交互和排序差异，再整合多种降维特征来推断细胞亚群、拟时序和动态网络（`paper source/nature_html/paper.md:12`, `paper source/nature_html/paper.md:24`, `paper source/nature_html/paper.md:27`, `paper source/nature_html/paper.md:33`）。

### 现有方法为什么不够？

文章把不足分成两类。

第一类是基因网络推断。Pearson 相关、细胞特异网络和其他 GRN 方法可以描述基因关系，但 Pearson 只能衡量线性关联，不能充分区分因果关系；细胞特异网络在异质性高、转变时间点不精确时也可能不稳定。作者认为，只看相关或单细胞网络还不够，还需要考虑细胞群体的分化顺序以及基因对结构在分化过程中的差异变化（`paper source/nature_html/paper.md:21`）。

第二类是拟时序推断。TSCAN、Monocle2、SLICER、scVelo 等方法都能重建轨迹，但文章指出许多方法依赖准确的细胞群识别，对噪声敏感，并且在多层分支、重叠分化路径等复杂过程上会遇到困难（`paper source/nature_html/paper.md:24`）。

### scRDEN 的核心思想

scRDEN 不直接把每个细胞表示成“基因表达向量”，而是先构造“基因对排序差异向量”：

1. 对表达矩阵做过滤、异常值平滑、log2 转换和高内在熵基因筛选。
2. 用 Pearson 相关和 WGCNA 硬阈值构造基因共表达图。
3. 在每个细胞内对基因表达排序。
4. 只对共表达图中的基因对计算排序差。
5. 把每个细胞表示成这些基因对的 rank-difference 特征。
6. 在这个新特征空间中做 PCA、t-SNE、UMAP，融合相似度网络，再进行谱聚类和拟时序推断。
7. 根据拟时序重新构造动态基因 rank differential expression network，并用 diversity 和 clustering coefficient 描述网络拓扑变化。

Fig. 1 的本地图像直观展示了这个流程：输入表达矩阵经过预处理，一路计算 Pearson 相关并阈值化成共表达网络，一路生成 rank matrix；两者合并成 rank differential expression network \(C\)，再经过降维、affinity matrix、network fusion、spectral clustering 和 trajectory inference，最后做富集分析和动态网络分析（`paper source/nature_html/paper.md:36`, `paper source/nature_html/paper.md:41`）。

### 计算流程逐步解释

```text
原始 scRNA-seq 表达矩阵
        |
        v
基因过滤 + 异常值平滑 + log2(A0+1) + 内在熵特征基因选择
        |
        v
高质量表达矩阵 E_{m,n}
        |
        +------------------------------+
        |                              |
        v                              v
Pearson 相关矩阵 R                 每个细胞内的基因排序矩阵 C0
        |                              |
显著性检验 + 取绝对值 + WGCNA 硬阈值 b0
        |                              |
        v                              |
共表达图 B --------------------------+
        |
        v
对共表达基因对计算 rank difference，得到矩阵 c
        |
归一化 c，并保留变异系数 top 1% 的基因对
        |
        v
PCA / t-SNE / UMAP 降维，分别构造细胞相似度网络
        |
        v
迭代融合相似度网络，得到融合矩阵 E
        |
        v
谱聚类 + 根据起始簇的中心距离给簇赋拟时序
        |
        v
细胞簇、分支轨迹、动态基因排序差异网络
```

#### 1. 表达矩阵预处理

文章描述了四个预处理步骤：按基因名去除线粒体、spike-in 和核糖体基因，并保留在超过 10% 细胞中表达的基因；把超出 \([\mu-4\sigma,\mu+4\sigma]\) 的异常表达值平滑到边界；做 log2 转换；再用内在熵模型选择高质量特征基因（`paper source/nature_html/paper.md:130`, `paper source/nature_html/paper.md:138`）。

log 转换公式是：

$$
A_1=\log_2(A_0+1)
$$

这里加 1 是为了保持 0 表达值在 log 变换后的合理性（`paper source/nature_html/paper.md:133`, `paper source/nature_html/paper.md:138`）。需要注意的是，内在熵阈值 \(I\) 是人工选择阈值，主文没有给出每个数据集的固定取值。

#### 2. 构造基因共表达网络

scRDEN 对筛选后的表达矩阵 \(E_{m,n}\) 计算基因之间的 Pearson 相关矩阵 \(R_{m,m}\)（`paper source/nature_html/paper.md:144`, `paper source/nature_html/paper.md:147`）。随后：

- 对相关矩阵做显著性检验，保留 \(p < 0.01\) 的相关基因；
- 对相关系数取绝对值，因为方法不区分正相关和负相关的方向，而是把绝对大小当作相关强度；
- 用 WGCNA 计算合适的 hard threshold \(b_0\)，保留超过阈值的基因对，得到二值共表达网络 \(B\)（`paper source/nature_html/paper.md:152`, `paper source/nature_html/paper.md:155`, `paper source/nature_html/paper.md:160`, `paper source/nature_html/paper.md:163`）。

这里的 \(B\) 更适合理解为“候选基因对过滤器”，不是严格的因果调控网络。

#### 3. 构造基因对排序差异特征

scRDEN 的关键步骤是把表达量转为排序差异。对每个细胞，将筛选后的基因按表达量从低到高排序，得到 rank matrix \(C_0\)（`paper source/nature_html/paper.md:174`, `paper source/nature_html/paper.md:177`）。然后，只对共表达图 \(B\) 中有边的基因对 \((g_k,g_l)\)，计算它们在细胞 \(t\) 中的 rank difference：

$$
c_{gt}=(C_0)_{g_k t}-(C_0)_{g_l t}
$$

矩阵 \(c\) 的行是基因对，列是细胞（`paper source/nature_html/paper.md:185`, `paper source/nature_html/paper.md:190`）。接着，作者对 \(c\) 做 min-max 归一化，并选择变异系数 top 1% 的基因对进入后续分析，以降低内存开销并突出变化较强的基因对（`paper source/nature_html/paper.md:193`, `paper source/nature_html/paper.md:198`）。

#### 4. 多降维空间相似度融合

得到基因对 rank-difference 矩阵后，scRDEN 不只依赖一种降维方法，而是分别使用 t-SNE、PCA 和 UMAP 生成低维特征，并在每个空间中计算细胞间欧氏距离（`paper source/nature_html/paper.md:204`, `paper source/nature_html/paper.md:207`）。

对每个降维视图，方法会：

- 对每个细胞找最近的 \(k\) 个邻居，默认 \(k=30\)；
- 用局部平均距离和两细胞距离定义 \(\varepsilon_{i,j}\)；
- 用指数函数把距离转成相似度 \(W_{i,j}\)；
- 把 \(W\) 归一化为 \(P\)，并构造只保留局部邻居的稀疏核 \(S\)（`paper source/nature_html/paper.md:215`, `paper source/nature_html/paper.md:220`, `paper source/nature_html/paper.md:223`, `paper source/nature_html/paper.md:231`, `paper source/nature_html/paper.md:239`, `paper source/nature_html/paper.md:247`）。

然后，三个视图的相似度矩阵通过迭代更新互相融合，直到达到最大迭代次数或状态矩阵不再变化，最后求平均得到融合矩阵 \(E\)（`paper source/nature_html/paper.md:252`, `paper source/nature_html/paper.md:255`, `paper source/nature_html/paper.md:260`, `paper source/nature_html/paper.md:263`）。

#### 5. 谱聚类和拟时序

对融合矩阵 \(E\)，scRDEN 构造 Laplace 矩阵 \(L=D-E\)，计算特征值和 eigengap，再用 eigengap 规则确定谱聚类的簇数 \(p\)（`paper source/nature_html/paper.md:268`）。

拟时序不是对每个细胞连续排序，而是更接近“簇级别排序”：

1. 根据先验生物知识选择起始簇 \(d_1\)；
2. 计算每个簇在 t-SNE 空间中的中心；
3. 计算每个簇中心到起始簇中心的欧氏距离；
4. 按距离排序，给同一簇内所有细胞分配相同拟时序（`paper source/nature_html/paper.md:268`, `paper source/nature_html/paper.md:271`, `paper source/nature_html/paper.md:279`, `paper source/nature_html/paper.md:284`）。

这是理解 scRDEN 的一个重要细节：它的主文公式描述的是 cluster-level pseudotime，而不是细胞级连续轨迹。

#### 6. 动态基因排序差异网络

有了拟时序后，scRDEN 选择一部分关键基因，在每个 pseudo-time 上计算这些基因之间的 rank-difference 网络 \(H^{pt}\)，再对网络做对称化（`paper source/nature_html/paper.md:290`, `paper source/nature_html/paper.md:293`, `paper source/nature_html/paper.md:298`）。为了可视化，文章丢弃低于 0.2 的边，但也明确说最优阈值选择仍是开放问题（`paper source/nature_html/paper.md:298`）。

随后，文章用 diversity 和 clustering coefficient 描述网络拓扑。diversity 是边权的 scaled Shannon entropy，clustering coefficient 衡量某个节点邻居之间连接的紧密程度（`paper source/nature_html/paper.md:301`, `paper source/nature_html/paper.md:306`, `paper source/nature_html/paper.md:314`, `paper source/nature_html/paper.md:322`, `paper source/nature_html/paper.md:327`）。

### 实验和结果怎么理解？

文章使用五个 GEO 数据集：AT2、DC、Fibroblast、Germline 和 Dentate gyrus（`paper source/nature_html/paper.md:44`, `paper source/nature_html/paper.md:360`）。主文重点展示三个案例。

**Female fetal germ cells.** scRDEN 在 666 个细胞上得到四个簇，并给出 \(C1 \rightarrow C2 \rightarrow C3 \rightarrow C4\) 的单向轨迹；Fig. 2 的本地图像显示了标签 t-SNE、聚类 t-SNE、marker heatmap、GO 富集、NANOG/DDX4 相关 heatmap 和四个动态网络。文章称 NANOG 相关连接早期高、后期下降，而 DDX4 相关连接后期增强（`paper source/nature_html/paper.md:53`, `paper source/nature_html/paper.md:56`）。

**Fibroblast reprogramming.** scRDEN 在 355 个细胞上得到四个簇和两个分支：\(C3 \rightarrow C1 \rightarrow C2\) 以及 \(C3 \rightarrow C1 \rightarrow C4\)。Fig. 3 显示了两条黑色分支箭头、marker heatmap、富集条形图、Ube2c/Birc5 相关 heatmap 和动态网络。文章解释 Birc5、Ube2c 等有丝分裂相关模块随分化下降，符合 MEF 退出细胞周期的生物学背景（`paper source/nature_html/paper.md:70`, `paper source/nature_html/paper.md:73`）。

**Dentate gyrus.** 这是大规模、多批次、多分支案例。文章称数据有 11,926 个细胞、两个 batch，并先用 Harmony 去除 batch effect，再用 scRDEN 得到八个簇和四条发育轨迹（`paper source/nature_html/paper.md:87`）。Fig. 4 的本地图像显示了密集 t-SNE、八簇聚类图、四条分支、marker heatmap、GO 富集、Cst3/Fabp7 heatmap 和多时间点动态网络。文章把四条分支解释为 pyramidal、granule、oligodendrocyte 和 astrocyte 方向的成熟过程（`paper source/nature_html/paper.md:90`）。

### 评估结果

文章用 Monocle2 和 TSCAN 作为轨迹推断基线，使用 Bubble Sort Index、POS 和加噪后的 robust score 评估轨迹准确性和鲁棒性（`paper source/nature_html/paper.md:104`）。主文称 scRDEN 在五个无噪数据集上整体优于两个基线，但 DC 数据集的 POS 略低于 Monocle2 和 TSCAN；在 5%、10%、20% Gaussian noise 下，scRDEN 的 robust score 整体约高 20%（`paper source/nature_html/paper.md:104`）。Fig. 5 的本地图像中，红色 scRDEN 柱在多个 robust-score 面板里明显较高，并展示了 Dentate gyrus、Fibroblast、Germline 三个数据集的运行时间拆分。

### 复现性和当前缺口

这次工作区是 paper-only：没有本地代码仓库，没有 `doc_code.md`，也没有本地 supplementary markdown。文章提供了五个 GEO accession（`paper source/nature_html/paper.md:360`），并链接了一个 supplementary DOCX（`paper source/nature_html/paper.md:476`），但该 DOCX 没有被转换为本地可引用的 `SUPP_MD`。

主文中仍缺少一些复现 scRDEN 所需的细节：

- 内在熵阈值 \(I\) 的数据集取值；
- WGCNA hard threshold \(b_0\) 的具体取值；
- 相似度参数 \(\mu\)；
- PCA/t-SNE/UMAP 的维度、随机种子和其他参数；
- 相似度融合最大迭代次数；
- 起始簇选择的完全自动化规则；
- Fig. 5 benchmark 的原始脚本和表格。

因此，当前可以可靠解释论文方法和图中主张，但不能代码级验证实现，也不能直接复现所有图。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scRDEN Summary

### Paper

**scRDEN: single-cell dynamic gene rank differential expression network and robust trajectory inference** was published in *Scientific Reports* in 2025. The paper introduces a rank-based method for single-cell trajectory inference and dynamic gene-pair network analysis. Its central claim is that converting noisy single-cell expression values into more stable gene-gene rank relationships improves trajectory robustness while preserving interpretable gene-network dynamics (`paper source/nature_html/paper.md:12`, `paper source/nature_html/paper.md:27`).

### Problem

Single-cell trajectory methods often depend on expression-level distances, accurate population detection, and noise-sensitive dimensionality reductions. The paper argues that existing pseudotime methods can struggle with high noise, overlapping differentiation paths, and multi-branch systems (`paper source/nature_html/paper.md:24`). It also argues that correlation-based and cell-specific gene-network approaches do not fully capture differentiation order and may be sensitive to heterogeneity or transition timing (`paper source/nature_html/paper.md:21`).

### Method

scRDEN first filters and smooths a scRNA-seq expression matrix, applies a log2 transform, and selects high intrinsic-entropy genes (`paper source/nature_html/paper.md:130`, `paper source/nature_html/paper.md:138`). It then builds a Pearson/WGCNA co-expression graph and, for each co-expressed gene pair, computes the within-cell rank difference between the two genes (`paper source/nature_html/paper.md:144`, `paper source/nature_html/paper.md:160`, `paper source/nature_html/paper.md:174`, `paper source/nature_html/paper.md:185`). The normalized rank-difference matrix is reduced with PCA, t-SNE, and UMAP; cell similarities from these views are fused through a similarity-network-fusion-style update before spectral clustering and cluster-distance pseudotime assignment (`paper source/nature_html/paper.md:204`, `paper source/nature_html/paper.md:252`, `paper source/nature_html/paper.md:268`, `paper source/nature_html/paper.md:284`).

After trajectory inference, scRDEN reconstructs dynamic rank-differential networks for selected genes at assigned pseudo-times and summarizes topology changes with diversity and clustering coefficient (`paper source/nature_html/paper.md:290`, `paper source/nature_html/paper.md:298`, `paper source/nature_html/paper.md:327`). Fig. 1 visually supports this workflow, showing expression preprocessing, co-expression graph construction, rank-differential matrix construction, similarity fusion, spectral clustering, trajectory inference, enrichment, and network analysis.

### Results

The paper applies scRDEN to five GEO datasets: AT2, DC, Fibroblast, Germline, and Dentate gyrus (`paper source/nature_html/paper.md:44`, `paper source/nature_html/paper.md:360`). The main case studies are:

- **Female fetal germ cells:** scRDEN reports a four-cluster unidirectional trajectory \(C1 \rightarrow C2 \rightarrow C3 \rightarrow C4\), marker-gene enrichment, and NANOG/DDX4-associated dynamic network changes (`paper source/nature_html/paper.md:53`, `paper source/nature_html/paper.md:56`; Fig. 2 image).
- **Fibroblast reprogramming:** scRDEN reports four clusters and two branches \(C3 \rightarrow C1 \rightarrow C2\) and \(C3 \rightarrow C1 \rightarrow C4\), with Ube2c/Birc5-linked modules decreasing along differentiation (`paper source/nature_html/paper.md:70`, `paper source/nature_html/paper.md:73`; Fig. 3 image).
- **Dentate gyrus:** after Harmony batch handling, scRDEN reports eight clusters and four developmental branches in a large 11,926-cell dataset (`paper source/nature_html/paper.md:87`, `paper source/nature_html/paper.md:90`; Fig. 4 image).

For benchmarking, the paper compares scRDEN with Monocle2 and TSCAN using Bubble Sort Index, POS, and robust score under Gaussian noise. It claims scRDEN performs best overall on five noiseless datasets, with DC POS as a noted exception where scRDEN is slightly below Monocle2 and TSCAN; under perturbation, it reports scRDEN's robust score as about 20% higher overall (`paper source/nature_html/paper.md:104`). Fig. 5 visually supports the comparative robustness and runtime narrative, but raw benchmark scripts or tables are not present locally.

### Reproducibility

**Data availability.** The paper lists GEO accessions GSE52583, GSE60783, GSE67310, GSE86146, and GSE104323 (`paper source/nature_html/paper.md:360`).

**Code availability.** Not found in the acquired paper markdown. Acquisition found no GitHub URL and normalized this workspace to paper-only. `doc_code.md` is intentionally skipped.

**Supplementary material.** The paper links a supplementary DOCX (`paper source/nature_html/paper.md:476`), but no local supplementary markdown was acquired.

**Major implementation gaps.** The main text does not fully specify several dataset-specific choices: intrinsic-entropy threshold \(I\), WGCNA hard threshold \(b_0\), empirical similarity parameter \(\mu\), dimensionality-reduction settings, random seeds, maximum fusion iterations, and complete operational rules for choosing starting clusters beyond marker/prior biological knowledge.

**Reproducibility rating: 2/5.** The algorithm is described with many equations and the input datasets are public, but the workspace lacks code, runnable scripts, parsed supplementary material, and exact parameter settings needed to reproduce the figures directly.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
