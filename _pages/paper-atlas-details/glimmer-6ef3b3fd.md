---
layout: default
permalink: /paper-atlas/glimmer-6ef3b3fd/
title: "Glimmer"
nav: false
description: "Glimmer 不直接训练一个深度网络去“生成”空间表示，而是在物理空间的 k 近邻骨架上，为每个点的每条邻边学习权重，再用这些权重平滑原始分子特征。它试图在两种失败之间找到可调的中间态：只看表达会产生空间上破碎的“椒盐”聚类，只看距离又会把相邻但功能不同的细胞过度混合。 论文把这一框架用于两个尺度：组织尺度的空间区域识别，以及把 Xenium 转录本先聚合为小空间 bin、再做细胞尺度聚类的“无预先分割”分析。"
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
      <span>Domain Clustering</span>
      <span>bioRxiv · 2025</span>
    </div>
    <h1>Glimmer</h1>
    <p>Energy-Regularized Graph Learning for Multiscale Spatial Representation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1101/2025.08.22.671846" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Glimmer：用能量正则化学习空间邻接图

### 一句话理解

Glimmer 不直接训练一个深度网络去“生成”空间表示，而是在物理空间的 $k$ 近邻骨架上，为每个点的每条邻边学习权重，再用这些权重平滑原始分子特征。它试图在两种失败之间找到可调的中间态：只看表达会产生空间上破碎的“椒盐”聚类，只看距离又会把相邻但功能不同的细胞过度混合。

论文把这一框架用于两个尺度：组织尺度的空间区域识别，以及把 Xenium 转录本先聚合为小空间 bin、再做细胞尺度聚类的“无预先分割”分析。这里的“无分割”准确地说是聚类入口不依赖细胞边界；论文后续若要恢复细胞对象，仍使用 DAPI 核、Voronoi 区域和几何修正。

### 输入、输出与适用边界

输入是一个特征矩阵 $X\in\mathbb{R}^{n\times m}$ 和同一批观测的二维坐标。组织尺度通常先做总量归一化、`log1p`、最多 3,000 个高变基因和 50 维 PCA；亚细胞尺度则先把转录本聚合到约 $2\,\mu m$ 的 bin。输出不是新的神经网络参数，而是：

- 每个观测到其 $k$ 个空间近邻的权重矩阵；
- 由邻居加权得到的平滑特征 `X_emb_smooth`；
- 下游 Scanpy 邻接图、Leiden 聚类以及可选的空间多数投票标签。

Glimmer 只重加权候选邻边，并不会在空间 $k$NN 骨架之外发现远距离边。因此论文中“distal interactions”的措辞应理解为在现有局部邻域内相对较远的邻居，而不是任意远程连接。

### 核心目标函数

对点 $i$ 与其空间邻居 $j\in\mathcal N(i)$，论文定义特征距离

$$
Z_{ij}=\|\mathbf{x}_i-\mathbf{x}_j\|_2^2.
$$

本地代码把空间距离逐行缩放到 $[0,1]$：

$$
S_{ij}=\frac{d_{ij}-\min_{j'}d_{ij'}}{\max_{j'}d_{ij'}-\min_{j'}d_{ij'}+\epsilon}.
$$

所以 $S_{ij}=0$ 表示该点自己的最近邻，$S_{ij}=1$ 表示其候选邻域中最远的邻居。代码变量叫 `inv_dist`，但它并不是“距离的倒数”。

论文的优化变量是原始边参数 $W$，有效权重写成

$$
\widetilde W_{ij}=\sigma\!\left(W_{ij}e^{-\gamma S_{ij}}\right),
$$

并最小化

$$
\sum_{i,j\in\mathcal N(i)}
\left(
\widetilde W_{ij}Z_{ij}S_{ij}
-\alpha\log\widetilde W_{ij}
+\beta\widetilde W_{ij}^{2}
\right).
$$

三项的直觉是：第一项惩罚“分子差异大且空间较远”的高权边；对数屏障阻止有效权重坍缩到零；二次正则限制权重大小。$alpha$ 是最主要的尺度旋钮：小 $alpha$ 更强调分子相似性，大 $alpha$ 会把更多空间邻边推向较高权重。需要注意，$\beta\widetilde W^2$ 是二次收缩，不等同于会产生精确零值的稀疏惩罚。

论文随后用

$$
\mathbf{x}'_i=\eta\sum_{j\in\mathcal N(i)}\widetilde W_{ij}\mathbf{x}_j+(1-\eta)\mathbf{x}_i
$$

生成平滑表示。组织尺度常用 $k=50,\eta=0.1$；亚细胞 bin 常用 $k=15,\eta=0.2$。$alpha$ 并没有一个跨数据集固定的最佳值：论文示例从 melanoma 的 100、cerebellum 的 120、tonsil 的 1,000 到区域基准的 5,000。

### 从数据到区域的完整流程

```text
原始 counts / 蛋白特征 / 转录本 bin
        │
        ├─ 常规预处理与 PCA（或直接使用给定特征）
        ▼
物理坐标上的 kNN 候选图
        │
        ├─ 计算平方特征距离 Z
        ├─ 计算逐点归一化空间距离 S
        ▼
Adam 优化每条候选边的 W（10,000 epochs, lr=1e-4）
        │
        ▼
邻居加权平滑 → X_emb_smooth
        │
        ├─ Scanpy 邻接图 + Leiden
        └─ 可选：10 个空间近邻的标签多数投票
```

Fig. 1 的图示正好对应这条链：输入特征和坐标、均匀邻接骨架、能量最小化重加权、得到优化特征。Fig. 2 的 melanoma 扫参图显示平均权重随 $\alpha$ 呈 S 形变化；在 $\alpha=100$ 附近，CD8 T 和单核/巨噬细胞出现空间相关的 R1/R2 状态，同时仍保留分子差异。这个结果支持“可调平衡”，但不是一个自动选择超参数的算法。

### 亚细胞分支到底做了什么

Xenium 分支先把转录本聚合为细小 bin，令每个 bin 具有基因计数与中心坐标；再以 $k=15,\alpha=200,\eta=0.2$ 运行 Glimmer，并在平滑表示上做 Leiden。bin 标签可映射回转录本。Fig. 4 比较了 Glimmer、Baysor、Cellpose、Xenium 默认分割和 FICTURE；图中 gene purity 与簇均值表达的 cosine distance 支持 Glimmer 在该评测中的簇纯度和分离度优势。

但论文明确说该基准评估的是 clustering purity，而不是 segmentation quality。因此不能把 Fig. 4 解读成已经证明 Glimmer 的细胞边界比所有分割方法更准确。后续的细胞恢复还引入 DAPI 核位置、凸包、Voronoi 区域、cluster-aware 拆分、小片段合并和几何过滤，这些是附加后处理，不是核心能量目标本身。

### 论文结果应怎样读

- Fig. 3：在 5 个有区域标注的 MERFISH 数据和 5 个无区域真值的 Slide-seq 数据上，论文分别使用 ARI/NMI/完整性/同质性与 CAS/MLAMI/NASW/CNMI。汇总柱状图中 Glimmer 总分最高；但总分经过平台内归一化，不能当作原始指标的统一绝对尺度。
- Cerebellum：Glimmer 得到 OL、GL、Purkinje–Bergmann 和 ML 四层，Neurod1、Calb1、Plp1、Nxph1 等同图标记支持这些注释。标记一致性是生物学支持，不是独立盲测标签。
- Fig. 5：tonsil 中的暗区/亮区分别显示 AICDA/CXCR4 与 CD83/CXCL13 等模式，并衔接差异表达和 CellChat。后两步是在 Glimmer 区域上做的下游分析，不能反过来证明区域识别在所有数据上都正确。

### 代码与论文的对应关系

核心实现位于 `Glimmer_code/glimmer/model.py`：`compute_loss` 对应目标函数，`train_neighbor_weights` 构建空间 kNN、训练 $W$ 并写出平滑特征。`glimmer/utils.py` 提供 $\alpha$ 扫描与空间标签平滑；`glimmer/segment.py` 承担 bin/Voronoi/几何修正；`benchmarking/` 和 notebooks 保存主要图与基准流程。

整体匹配度评为 **中等**。主算法、主要参数和主要应用脚本都能找到，但有一个会影响数学解释的中央差异：训练损失使用 $\sigma(W e^{-\gamma S})$，训练完成后代码却把 `sigmoid(W)` 存为最终权重并用于平滑，没有重新乘空间衰减。与此同时，邻居加权和没有除以权重和，所以它不是归一化加权平均，表示尺度会随 $k$ 和权重总量变化。这两点都应以代码实际行为为准，不能把论文公式无条件当成运行时实现。

其他实现边界包括：

- `NearestNeighbors` 通常把自身放在第 1 位；代码平滑时跳过第 0 列，但训练损失仍包含该自边。
- `batch=True` 只分块计算特征距离，完整的 $n\times k$ 权重和距离张量仍驻留设备内存，并不是完整的小批量训练。
- `spatial_smooth` 的标签多数投票只使用空间坐标；函数接收的 embedding 仅被复制进临时表，不参与投票。
- 论文建议以平均权重区间辅助选 $\alpha$，代码提供曲线和阈值，但没有自动验证跨数据集最优值。

### 复现判断

仓库固定在提交 `1e074dcbd5c0f2937ccc34d9570ceaff9fe6ed52`，包含 Python 包、区域基准脚本、亚细胞脚本和对应主图 notebooks，足以追踪绝大多数方法步骤。数据均声明来自公开来源，但脚本依赖预先下载的数据与特定目录结构，notebook 也保存了大量结果状态；完整复现仍需要按补充表获取数据、重建环境并核对各数据集参数。最稳妥的使用方式是显式传入 `k`、`log_barrier_w`、`neighbor_weight` 和设备参数，不依赖函数默认值。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## Glimmer: Energy-Regularized Graph Learning for Multiscale Spatial Representation

Glimmer is an unsupervised spatial-omics representation method that learns edge weights on a physical $k$-nearest-neighbor scaffold. It targets the trade-off between expression-only embeddings, which can fragment tissue into spatially incoherent clusters, and fixed spatial smoothing, which can erase local molecular heterogeneity. The paper contrasts this with fixed-kernel methods (BANKSY, SPIN, SpatialPCA, GraphPCA) and task-sensitive GNN methods (STAGATE, GraphST, SpaceFlow).

For each observation and spatial neighbor, Glimmer combines squared feature distance with row-normalized physical distance. A sigmoid-activated edge parameter is optimized with a feature-distance term, a log barrier that prevents weights from vanishing, and a quadratic penalty. The learned graph then smooths PCA or other input features; Scanpy neighbors and Leiden clustering operate on the resulting embedding. The same core function is used for tissue domains ($k=50$, usually neighbor interpolation 0.1) and transcript-bin clustering ($k=15$, interpolation 0.2), while the log-barrier coefficient is tuned by dataset.

The paper evaluates five annotated MERFISH slices and five unlabeled Slide-seq samples against BANKSY, SCAN-IT, SPIN, SpaceFlow, and GraphST. It reports the best aggregate normalized score, leading ARI/NMI on MERFISH and CAS/MLAMI on Slide-seq while remaining comparable on NASW/CNMI. Case studies identify canonical cerebellar layers, melanoma immune states, CODEX spleen regions, and tonsil germinal-center zones. In Xenium lymph node patches, bin-level Glimmer clustering shows higher marker-gene purity and inter-cluster cosine distance than Cellpose-, Xenium-, Baysor-, and FICTURE-based alternatives. That benchmark explicitly assesses clustering purity, not cell-segmentation accuracy.

The public repository includes the core package, regional/subcellular benchmark scripts, and notebooks corresponding to the main analyses (`.repo_source` records commit `8b73fdeb3ef6fbf7906a82fce34c985eb17472b6`). Core paper-code fidelity is **medium**: the loss and pipeline are present, but the implementation exports `sigmoid(raw W)` rather than the paper's spatially decayed $\widetilde W=\sigma(We^{-\gamma S})$, and its neighbor sum is not normalized by total weight. Other reproducibility limits are dataset-specific tuning, prearranged data paths, large stateful notebooks, and a “batch” option that only batches feature-distance construction rather than the full optimization. The paper PDF and all five main figures were inspected; no separate supplementary markdown or extracted image directory is present.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
