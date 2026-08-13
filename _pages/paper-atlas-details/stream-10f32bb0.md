---
layout: default
permalink: /paper-atlas/stream-10f32bb0/
title: "STREAM"
nav: false
wide: true
description: "STREAM 是一个用于单细胞轨迹推断、可视化和参考映射的工具。它关注的问题是：给定一次性测量到的单细胞转录组、qPCR 或染色质可及性数据，如何从中重建细胞分化过程中的分支轨迹、分叉点和伪时间，并且把这些结果以研究者容易理解的方式展示出来。 论文认为当时很多轨迹方法有三个不足。第一，主要面向 scRNA-seq，对 scATAC-seq 这类表观组数据支持不足。"
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
      <span>Nature Communications · 2019</span>
    </div>
    <h1>STREAM</h1>
    <p>Single-cell trajectories reconstruction, exploration and mapping of omics data with STREAM</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-019-09670-4" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for STREAM">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/pinellolab/STREAM" target="_blank" rel="noopener noreferrer" aria-label="Open code for STREAM">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STREAM 方法中文解读

### 1. 这篇论文要解决什么问题？

STREAM 是一个用于单细胞轨迹推断、可视化和参考映射的工具。它关注的问题是：给定一次性测量到的单细胞转录组、qPCR 或染色质可及性数据，如何从中重建细胞分化过程中的分支轨迹、分叉点和伪时间，并且把这些结果以研究者容易理解的方式展示出来。

论文认为当时很多轨迹方法有三个不足。第一，主要面向 scRNA-seq，对 scATAC-seq 这类表观组数据支持不足。第二，很多方法只给出细胞散点图、聚类图或伪时间排序，不容易看清不同细胞亚群如何沿分支连续变化。第三，如果有新的扰动样本或疾病样本，常见做法是把新旧细胞合并后重新建轨迹，这会改变原来的参考结构，导致参考伪时间和位置难以解释。STREAM 的目标就是把轨迹推断、分支可视化、marker 检测和新细胞映射合成一个端到端流程。论文的问题设定见 `paper.md:18-24`、`paper.md:47-50`。

### 2. STREAM 的输入和输出

对转录组或 qPCR 数据，STREAM 的输入是一个基因 x 细胞矩阵，矩阵值是经过文库大小归一化和 log2 转换后的表达量。对 scATAC-seq，论文不是直接用全基因组 peak 矩阵，而是先把可及区域转成 k-mer chromVAR z-score，再用 PCA 选出特征，送入后续轨迹流程。映射新细胞时，论文假设新细胞和参考细胞有相同的基因集合、相同实验协议、相同归一化/转换，并且已经处理批次效应，见 `paper.md:195-198`、`paper.md:353-356`、`paper.md:370-373`。

输出包括：

- 一个嵌入在低维空间中的 principal tree / principal graph。
- 每个细胞所属的分支、分支上的位置、到分支的距离。
- 从任意根节点出发的伪时间。
- flat tree、subway map、stream plot 等分支感知可视化。
- 分叉 marker、过渡 marker、叶端 marker。
- 把新细胞映射到固定参考轨迹上的结果。

代码中这些对象主要存放在 `AnnData` 结构里：特征矩阵和低维坐标在 `adata.obsm`，图和参数在 `adata.uns`，分支和伪时间在 `adata.obs`。直接代码证据见 `STREAM/stream/core.py:152-220` 和 `STREAM/stream/extra.py:196-273`。

### 3. 计算流程总览

```text
单细胞表达矩阵 / scATAC 派生特征矩阵
        |
        v
特征选择
  RNA/qPCR: 均值-方差 LOESS 选择 variable genes
  scATAC: k-mer chromVAR z-score -> PCA 特征
        |
        v
低维嵌入
  论文主线: MLLE
  代码还支持 spectral embedding / UMAP / PCA
        |
        v
初始树结构
  在低维空间聚类 -> 以聚类中心构建最小生成树
        |
        v
弹性主图拟合
  调用 ElPiGraph.R，并加 STREAM 图结构优化包装函数
        |
        v
投影与伪时间
  细胞投影到最近分支，按根节点计算路径长度
        |
        v
解释和应用
  flat tree / subway map / stream plot / marker 检测 / 新细胞映射
```

### 4. 特征选择：先让轨迹依赖有信息的维度

转录组数据中，STREAM 先选择 variable genes。论文描述的方法是：对每个基因计算所有细胞中的均值和标准差，用 LOESS 拟合均值-标准差关系，然后选择显著高于拟合曲线的基因，见 `paper.md:195-198`。代码中的 `select_variable_genes` 正是这样做的：计算 `mean_genes` 和 `std_genes`，用 LOWESS 拟合，计算点到曲线的距离或选择 top-N，最后把选中的表达矩阵保存到 `adata.obsm['var_genes']`，把基因名保存到 `adata.uns['var_genes']`，见 `STREAM/stream/core.py:855-927`。

scATAC-seq 部分的思路不同。因为单细胞 ATAC 数据非常稀疏，论文先筛选可变开放区域，再用 chromVAR 对 DNA k-mer 计算可及性偏差 z-score。论文实验中使用 k=7 的 k-mer，把细胞 x k-mer z-score 矩阵标准化后做 PCA，选择 top 15 PCs 并去掉第一个主成分，再进入 STREAM 轨迹推断，见 `paper.md:151-154`、`paper.md:370-373`。代码中可以直接验证 PCA 特征选择和去掉第一主成分的实现：`select_top_principal_components` 会保存 PCA 坐标、方差解释率和最终 `top_pcs`，见 `STREAM/stream/core.py:1009-1114`。但 chromVAR/k-mer 原始特征构建不是 Python 核心包中的直接实现，而是论文和教程层面的工作流。

### 5. MLLE：把细胞嵌入到适合建树的低维空间

论文主线使用 Modified Locally Linear Embedding (MLLE)。普通 LLE 的想法是，每个高维细胞向量 \(x_i\) 可以由邻居 \(x_j\) 的线性组合近似：

$$min\left\Vert {x_i - \mathop {\sum}\limits_{j \in J_i} {w_{ji}x_j} } \right\Vert,s.t.\mathop {\sum}\limits_{j \in J_i} {w_{ji}} = 1$$

然后在低维空间中找到 \(t_i\)，让同样的邻居重构关系尽量保持：

$$min\left\Vert {t_i - \mathop {\sum }\limits_{j \in J_i} w_{ji}t_j} \right\Vert^2,s.t.TT^T = I$$

MLLE 的改进是，在每个邻域里使用多个线性独立的权重向量，而不是只使用一个权重向量，从而提高稳定性：

$$min\,\mathop {\sum }\limits_{i = 1}^N \mathop {\sum }\limits_{l = 1}^{s_i} \left\Vert {t_i - \mathop {\sum }\limits_{j \in J_i} w_{ji}^{(l)}t_j} \right\Vert^2,s.t.TT^T = I$$

这些公式在 `paper.md:207-234`。代码中，`dimension_reduction(..., method='mlle')` 调用 scikit-learn 的 `LocallyLinearEmbedding(method='modified')`，并保存 `trans_mlle`、`X_mlle`、`X_dr`，见 `STREAM/stream/core.py:1116-1241`。

需要注意一个代码-论文差异：论文说邻域大小默认是细胞数的 10%，通常 3 个 MLLE 分量足够，见 `paper.md:234`；但代码函数默认是 `n_neighbors=50`、`nb_pct=None`，只有显式传入 `nb_pct` 时才按比例设置邻居数，见 `STREAM/stream/core.py:1116-1189`。此外，代码 API 默认 `method='se'`，不是 MLLE。因此复现论文主线时，需要显式指定 MLLE 及相关参数。

### 6. 初始树结构和 ElPiGraph 拟合

Elastic principal graph 的优化是贪心式的，容易受初始值影响，所以 STREAM 先构造一个初始树。论文说，在 MLLE 空间中用 affinity propagation 聚类，阻尼系数设为 0.75，然后用 Kruskal 算法在 exemplar 上建最小生成树，作为 ElPiGraph 的初始树，见 `paper.md:237-240`。

代码实现了这个框架，但更通用：`seed_elastic_principal_graph` 支持 affinity propagation、spectral clustering 和 k-means，然后在聚类中心之间计算距离并构建最小生成树，见 `STREAM/stream/core.py:1784-1920`。一个重要差异是，代码默认 `clustering='kmeans'`，而不是论文文字中的 affinity propagation；如果要严格按论文描述运行，需要显式设置 `clustering='ap'`。

如果要在更高维的 MLLE 空间中学习轨迹，论文提出先在较低维度 \(L\) 中建图，再把图映射回 \(H\) 维空间：前 \(L\) 个坐标来自低维图，剩余坐标由分配到该节点的细胞均值或最近邻推断，边保持不变，见 `paper.md:243`。代码中的 `infer_initial_structure` 实现了这一点，见 `STREAM/stream/core.py:1731-1782`。

### 7. 弹性主图目标函数与图结构优化

STREAM 的 principal graph 是一个嵌入到数据空间中的无向图。论文的能量函数包括三部分：数据点到最近图节点的近似误差、边长拉伸惩罚、星形结构弯曲惩罚，同时还有 trimming radius 和拓扑复杂度控制：

$$\begin{array}{l}U^\phi \left( {X,G} \right) = \frac{1}&#123;&#123;|X|}}\mathop {\sum }\limits_{j = 1}^{\left| V \right|} \mathop {\sum }\limits_{i:P\left( i \right) = j} {\mathrm{min}}\left( \left\Vert {X_i - \phi \left( {V_j} \right)^2,R_0^2} \right\Vert \right)\\ + \mathop {\sum }\limits_{E^{(i)}} \left[ {\lambda + \alpha \left( {\max \left( {2,{\mathrm{deg}} \left( {E^{\left( i \right)}\left( 0 \right)} \right),{\mathrm{deg}} \left( {E^{\left( i \right)}\left( 1 \right)} \right)} \right) - 2} \right)} \right]\left( {\phi (E^{\left( i \right)}\left( 0 \right)) - \phi (E^{\left( i \right)}\left( 1 \right))} \right)^2\\ + \mu \mathop {\sum }\limits_{S_{}^{(j)}} \left( {\phi (S_{}^{\left( j \right)}(0)) - \frac{1}&#123;&#123;{\mathrm{deg}}(S^{\left( j \right)}(0))}}\mathop {\sum }\limits_{i = 1}^&#123;&#123;\mathrm{deg}}(S^{\left( j \right)}(0))} \phi (S_{}^{\left( j \right)}(i))} \right)^2\end{array}$$

其中 \(R_0\) 是 trimming radius，\(\lambda\) 控制边拉伸，\(\mu\) 控制星形结构的弯曲，\(\alpha\) 控制拓扑复杂度和分支倾向。论文默认参数是 \(R_0=\infty\)、\(\alpha=0.02\)、\(\mu=0.1\)、\(\lambda=0.02\)，见 `paper.md:252-269`。代码中的 `elastic_principal_graph` 使用这些默认值，并调用外部 `ElPiGraph.R::computeElasticPrincipalTree`，见 `STREAM/stream/core.py:1923-2054`。

论文还提出几类单细胞特定图优化：控制过度分支、剪掉 trivial branches、把分叉点移动到更高密度区域、在分叉附近增加节点细化、延伸叶端节点以减少终端投影误差，见 `paper.md:272-293`。代码中有直接包装函数：`prune_elastic_principal_graph`、`optimize_branching`、`shift_branching`、`extend_elastic_principal_graph`，分别调用 `ElPiGraph.R` 的 `CollapseBrances`、`fineTuneBR`、`ShiftBranching` 和 `ExtendLeaves`，见 `STREAM/stream/core.py:2056-2485`。因此，Python 包能验证 STREAM 对这些操作的调用和参数组织，但底层图语法算子本身在外部 R 包中，不在这个 Python 源码快照里。

### 8. 分支、投影和伪时间

拟合图之后，STREAM 会把复杂图压缩成分支级别的 flat tree。`extract_branches` 从叶节点开始遍历，把连续的 degree-2 节点压缩成一条分支；`construct_flat_tree` 给状态标上 S0、S1 等标签，并记录分支节点、方向、长度和颜色，见 `STREAM/stream/extra.py:86-111`、`STREAM/stream/extra.py:275-299`。

细胞投影的逻辑也很清楚。`project_cells_to_epg` 先找每个细胞最近的图节点，再在包含该节点的候选分支中，把细胞投影到分支线段上，选择距离最小的分支，并保存：

- `branch_id`：细胞所属分支。
- `branch_id_alias`：用 S 状态表示的分支标签。
- `branch_lam`：细胞在分支上的弧长位置。
- `branch_dist`：细胞到分支的垂直距离。

然后 `calculate_pseudotime` 从每个可能的根节点做 BFS，把根到当前分支前缀路径长度加上分支内位置，得到根特异的伪时间列，见 `STREAM/stream/extra.py:196-273`。这正是 flat tree、subway map、stream plot 和 mapping 共享的底层坐标系统。

### 9. 三种可视化为什么重要

STREAM 的可视化不是附加图，而是方法的一部分。

Flat tree plot 把 3D 或更高维空间中的树映射到 2D，并尽量保持分支长度；细胞按照分支内伪时间和到分支的距离放置，见 `paper.md:296-299`。代码用 spring layout 初始布局，再根据真实分支长度调整边，并按 `branch_lam` 和 `branch_dist` 放置细胞，见 `STREAM/stream/extra.py:301-358`、`STREAM/stream/core.py:2488-2668`。

Subway map plot 从用户指定的根节点开始，用 BFS 重新排列分支，使横轴表示从根出发的伪时间距离，见 `paper.md:302-305`。代码中有根节点、分支偏移、BFS 顺序和绘图逻辑，见 `STREAM/stream/extra.py:360-448`、`STREAM/stream/extra.py:571-591`、`STREAM/stream/core.py:2670-2848`。

Stream plot 则把每条分支上的细胞数量或表达量转换为流线宽度和颜色。论文描述了滑动窗口计数、分叉附近平滑过渡、归一化宽度、插值和 Savitzky-Golay 平滑，见 `paper.md:308-311`。代码中可以看到窗口计数、分支连接处处理、polygon 构造和图像裁剪渲染，见 `STREAM/stream/extra.py:594-840`、`STREAM/stream/core.py:3140-3265`。

### 10. Marker 检测

STREAM 的 marker 检测也是沿分支定义的。

Diverging genes 用于找分叉后不同分支之间差异表达的基因。论文先把表达缩放到 [0,1]，用默认 log2 fold-change > 0.25 过滤，再对足够大的分支使用 Mann-Whitney U 检验并标准化成 Z-score，小样本则只报告 fold-change，见 `paper.md:314-338`。代码实现见 `STREAM/stream/core.py:3461-3657`。

Transition genes 用于找某一分支上随伪时间单调变化的基因。论文比较分支起始 20% 和末端 80% 细胞的平均表达，再计算表达与伪时间的 Spearman 相关，默认阈值是 log2 fold-change 0.25 和 Spearman 0.4，见 `paper.md:341-344`。代码实现见 `STREAM/stream/core.py:3267-3400`。

Leaf genes 用于找叶端分支特异的基因。论文计算叶分支平均表达的 Z-score，再做 Kruskal-Wallis 和 Conover 事后检验，见 `paper.md:347-350`。代码实现见 `STREAM/stream/core.py:3770-3914`，Conover 检验来自 `STREAM/stream/scikit_posthocs.py`。

### 11. 新细胞映射：固定参考轨迹，不重新建图

STREAM 的 mapping 是论文的重要创新之一。给定参考细胞 \(Y\) 和新细胞 \(X\)，方法先找到新细胞在参考细胞中的邻居，计算 MLLE 风格权重，再用参考嵌入坐标 \(v_j\) 加权得到新细胞低维坐标：

$$x\prime _i = \mathop {\sum }\limits_{j \in J_i} v_j \times w_{ji}$$

公式见 `paper.md:353-359`。代码中的 `map_new_data` 会读取参考对象中的特征选择和降维参数，复用 variable genes 或 PCA transform，复制参考 `epg` 和 `flat_tree`，把新细胞映射到 MLLE/UMAP/PCA 空间，再投影到参考分支并计算伪时间，最后返回 reference+new 的合并 `AnnData`，见 `STREAM/stream/core.py:4036-4183`。

这个设计的优点是参考结构不被新细胞改变，适合分析遗传扰动、疾病状态或刺激条件。论文 Fig. 2 把 `Gfi1`、`Irf8` 和双敲除 GMP 细胞映射到野生型血液分化轨迹上，图像中红色扰动细胞叠加在灰色参考树上，直观显示不同扰动偏向不同分支。限制也很明确：mapping 不能产生参考树中不存在的新命运分支。如果新细胞到分支的距离明显大于参考细胞，就提示需要合并重建轨迹或扩大参考状态空间，见 `paper.md:364-367`。

### 12. 评估结果怎么理解？

论文用多种数据验证 STREAM。鼠血液 scRNA-seq 中，STREAM 重建了淋巴、髓系和红系分支，并用 marker 表达支持；小鼠 GMP 扰动数据中，mapping 显示不同转录因子敲除把细胞推向不同分支；斑马鱼 qPCR 和 inDrop 数据中，STREAM 恢复了多个血液谱系，并用 FACS/荧光标记细胞映射验证；scATAC-seq 中，STREAM 用 k-mer 可及性特征恢复人骨髓造血层级，并把 k-mer 映射到 GATA1、CEBPA 等转录因子 motif，见 `paper.md:41-174`。

论文还和 10 个轨迹方法比较。合成数据中评估分叉数和伪时间相关性；真实数据中用 marker 表达和分支 precision/recall/F1 评估，方法定义见 `paper.md:376-435`。因此这些 benchmark 数值是论文/图像证据，不是本次代码审计复跑得到的结果。

### 13. 复现性和局限

代码层面，STREAM 核心流程与论文高度匹配：feature selection、MLLE、seed tree、ElPiGraph 包装、投影、伪时间、可视化、marker 检测和 mapping 都有直接源码证据。但复现时需要注意几个问题：

- Python API 默认值和论文文字不完全一致，尤其是降维默认方法和初始聚类默认方法。
- 底层图语法操作依赖外部 `ElPiGraph.R`，不在这个 Python 仓库中。
- 仓库有教程 notebooks，但没有在核心 Python 包中找到完整论文 benchmark 的复现脚本。

论文自身也承认，STREAM 仍主要面向树状或线性轨迹；循环、断连图、更复杂拓扑、百万级细胞规模和更广泛多组学整合都需要进一步发展，见 `paper.md:183-186`。因此，STREAM 最适合解释有分支分化结构、可用 principal tree 描述的单细胞过程；如果真实生物过程包含周期、多个不连通状态或参考中不存在的新命运，结果需要谨慎解释。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## STREAM Summary

STREAM is a trajectory-inference and visualization framework for single-cell omics data. The paper targets a gap in earlier pseudotime tools: many were designed mainly for transcriptomic data, offered limited branch-aware visualization, and lacked a way to map new cells onto an already inferred reference trajectory without recomputing and potentially distorting the reference (`paper.md:18-24`, `paper.md:47-50`).

The method takes normalized single-cell expression or derived accessibility features as input and outputs an inferred principal tree, cell-to-branch assignments, root-specific pseudotime, visualizations, marker features, and optional mapping of new cells. For transcriptomic data, STREAM selects informative genes with a mean-variance LOESS procedure, embeds cells with MLLE, seeds a tree from clusters and an MST, fits an elastic principal graph with ElPiGraph, then projects cells to graph branches (`paper.md:195-269`; `STREAM/stream/core.py:855-1241`, `STREAM/stream/core.py:1784-2054`, `STREAM/stream/extra.py:196-273`). The code also supports spectral embedding, UMAP, and PCA; two defaults differ from paper prose: `dimension_reduction` defaults to spectral embedding and `seed_elastic_principal_graph` defaults to k-means unless affinity propagation is requested (`STREAM/stream/core.py:1116-1241`, `STREAM/stream/core.py:1784-1881`).

The main novelty is the combination of elastic principal graph trajectory reconstruction with branch-aware visual analytics and mapping. Flat tree plots preserve branch geometry in 2D, subway maps reorganize trajectories from a selected root, and stream plots summarize branch density, cell-type composition, and gene or feature expression along pseudotime (`paper.md:296-311`; `STREAM/stream/core.py:2488-3265`, `STREAM/stream/extra.py:301-840`). STREAM also detects diverging, transition, and leaf markers with branch-aware statistical tests (`paper.md:314-350`; `STREAM/stream/core.py:3267-3914`). Its mapping procedure reuses reference features/transforms and the fixed reference graph before projecting new cells and computing pseudotime, which supports perturbation or condition comparisons (`paper.md:353-367`; `STREAM/stream/core.py:4036-4183`).

The paper evaluates STREAM on mouse, zebrafish, and human hematopoiesis datasets, including scRNA-seq, qPCR, and scATAC-seq. It reports recovery of known lineage structures, mapping of genetic perturbations, marker-gene consistency, competitive performance against 10 trajectory methods on synthetic and real benchmarks, and reconstruction of a human scATAC hematopoietic hierarchy from k-mer chromVAR features (`paper.md:41-174`). The six local figures visually support those claims: they show the workflow, mapping of perturbation/sorted validation cells, density-level stream plots, benchmark tables, marker-gene precision/recall analyses, and scATAC k-mer motif interpretation.

Code availability is strong for the core package: the acquired GitHub snapshot at commit `d20cc1faea58df10c53ee72447a9443f4b6c8e03` contains the Python package, graph/plot/marker/mapping APIs, tests, and tutorial notebooks. The paper states STREAM is available as web app, Bioconda package, and GitHub command-line package, with analyses reproducible using Bioconda and Supplementary Data notebooks (`paper.md:444-447`). In this workspace, no supplementary markdown is available, and direct scripts for reproducing the full multi-method benchmark figures were not found in the package source. Low-level graph grammar operations are also delegated to external `ElPiGraph.R` functions, so the Python repo verifies wrapper behavior but not the underlying R implementation.

Limitations are explicit. The paper notes that STREAM, like many trajectory tools, is still centered on tree/linear structures and needs further work for cyclic, disconnected, or more complex topologies; million-cell scale and broader multi-omics integration remain open challenges (`paper.md:183-186`). Mapping is also limited to fates already represented in the reference graph: new branches cannot be introduced by the mapping step, and large projection distances should be treated as evidence that the reference may not cover the new cells (`paper.md:364-367`). Overall code-paper fidelity is high for the core STREAM workflow, medium for exact reproduction of manuscript defaults/benchmarks, and explicitly partial for external ElPiGraph.R internals and supplementary notebook-dependent analyses.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
