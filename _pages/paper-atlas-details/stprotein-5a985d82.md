---
layout: default
permalink: /paper-atlas/stprotein-5a985d82/
title: "STProtein"
nav: false
description: "STProtein 关注空间多组学里的一个不平衡问题：空间转录组数据相对丰富，而空间蛋白组数据更少、更贵。因此，论文希望用已有的空间 RNA 表达和空间信息来预测未知的空间蛋白表达，并进一步做空间区域聚类和生物学解释。 论文把 STProtein 分成三部分：构建特征图、图注意力自编码器模块、上游和下游任务。论文记号中，X 是 RNA 表达，X' 是重构 RNA，Z 是模型学到的 embedding；"
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
      <span>arXiv · 2026</span>
    </div>
    <h1>STProtein</h1>
    <p>STProtein: predicting spatial protein expression from multi-omics data</p>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" aria-selected="true" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" aria-selected="false" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" data-detail-panel="zh" lang="zh-CN" markdown="1">

## STProtein 方法中文解读

### 这篇论文要解决什么问题

STProtein 关注空间多组学里的一个不平衡问题：空间转录组数据相对丰富，而空间蛋白组数据更少、更贵。因此，论文希望用已有的空间 RNA 表达和空间信息来预测未知的空间蛋白表达，并进一步做空间区域聚类和生物学解释（`paper.md:10-23`）。

论文把 STProtein 分成三部分：构建特征图、图注意力自编码器模块、上游和下游任务（`paper.md:41-52`）。论文记号中，$X$ 是 RNA 表达，$X'$ 是重构 RNA，$Z$ 是模型学到的 embedding；在预测任务里，论文把 $Z$ 解释为预测得到的蛋白表达表（`paper.md:44-44`, `paper.md:195-209`）。

### 为什么已有方法不够

论文把多组学预测方法分为矩阵分解、概率模型和深度学习方法。totalVI 是基于变分自编码器的 RNA/蛋白联合建模方法，scArches 用迁移学习把预训练模型适配到新数据；Dengkw 和 cTP-net 也是蛋白表达预测相关基线（`paper.md:29-32`, `paper.md:226-229`, `paper.md:425-437`）。论文认为这些方法通常没有充分利用空间位置对组学特征的影响（`paper.md:32-38`）。在空间组学分析方法里，STAGATE 和 SpatialGlue 等方法能建模空间结构或多模态表示，但论文指出仍缺少“用转录组预测空间蛋白表达”的算法（`paper.md:35-38`）。

### STProtein 的核心思路

STProtein 的核心可以理解为：

```text
训练阶段：有 RNA + 蛋白 + 空间位置
  RNA 预处理 -> PCA 特征 X
  蛋白 CLR 归一化 -> 蛋白监督 Y
  空间/特征图 -> edge index
  GNN 编码器 -> embedding Z
  GNN 解码器 -> RNA 重构 X'
  损失 = beta1 * RNA 重构误差 + beta2 * 蛋白预测误差

预测阶段：新数据只有 RNA + 空间位置
  RNA 预处理 -> 图 -> 训练好的模型 -> Z
  把 Z 当作预测蛋白表达 Y'
  对 Z/Y' 做 mclust/leiden/louvain 聚类，得到空间蛋白域
```

这个流程对应论文的训练框架图和上下游任务图（`paper.md:47-52`, `paper.md:201-209`）。本工作区的 Figure 1 可见 RNA 表、空间信息、Feature Graph、Encoder、Embedding、Decoder，以及 `MSE(Y,Z)` 和 `MSE(X,X')` 两个损失分支；Figure 2 可见上游预测蛋白表和下游 mclust 聚类。

### 数据预处理

论文说明 RNA 侧先做 library-size normalization、log transform，选择 4,000 个高变基因，再做 PCA，并保留与蛋白数量一致的前 $k$ 个主成分；蛋白侧使用 CLR 归一化（`paper.md:55-58`）。

代码基本实现了这个方向：`main.py` 对 RNA 调用 `highly_variable_genes(... n_top_genes=4000)`、`normalize_total`、`log1p`、`scale` 和 PCA；对蛋白调用 `clr_normalize_each_cell` 并 scale（`STProtein_repo/STProtein/main.py:72-101`）。CLR 函数在 `model/utils.py` 中逐细胞计算 Seurat 风格的 CLR 变换（`STProtein_repo/STProtein/model/utils.py:86-106`）。

一个细节是：代码中 PCA 维度使用 `adata_omics2.n_vars-1`，而论文文字说 $k$ 是蛋白数量（`STProtein_repo/STProtein/main.py:92-101`; `paper.md:55-58`）。这属于接近但不完全一致的实现细节。

### 特征图构建

论文讨论两种图：

- SN spatial-neighbor graph：如果两个 spot 的欧氏距离小于半径 $r$，就连边，默认 $r=2$（`paper.md:64-68`）。
- KNN feature graph：为每个 spot 选择 top-$k$ 近邻，默认 $k=3$（`paper.md:70-70`）。

论文选择 KNN，并在参数敏感性实验里报告 $k=3$ 效果最好（`paper.md:238-241`, `paper.md:621-643`）。

但代码里有一个重要差异：`Cal_Spatial_Net` 实际读取的是 `adata.obsm["spatial"]`，再用 `kneighbors_graph(spatial, ...)` 或 `radius_neighbors_graph(spatial, ...)` 建图（`STProtein_repo/STProtein/model/utils.py:15-25`）。`main.py` 的活跃路径对训练和测试 RNA/蛋白对象都调用 `model="KNN", n_neighbors=3`（`STProtein_repo/STProtein/main.py:103-117`）。所以，论文文字说 KNN 用于 PCA embedding，而当前顶层代码实现更像是在空间坐标上做 KNN。

### 图自编码器和损失函数

论文把核心模块称为 graph attention autoencoder，包含 graph attention layer、encoder、decoder 和 loss function（`paper.md:73-76`）。图注意力层基于 GATv2，并给出线性变换、注意力打分、softmax 归一化、邻居聚合和多头平均的公式 Eq. 1-5（`paper.md:79-123`）。编码器是两层图注意力层加 ReLU 和线性层，公式 Eq. 6-8（`paper.md:126-147`）；解码器把 embedding 映射回 RNA 重构，公式 Eq. 9-11（`paper.md:150-174`）。

损失函数是多任务学习形式：

$$\mathbf{L}_{\mathrm{rna}}=\sum_{i=1}^{N}\left\|x_i-\hat{x}_i\right\|^2$$

$$\mathbf{L}_{\mathrm{protien}}=\sum_{i=1}^{N}\left\|y_i-\hat{y}_i\right\|^2$$

$$\mathbf{L}_{\mathrm{total}}=\beta_1\mathbf{L}_{\mathrm{rna}}+\beta_2\mathbf{L}_{\mathrm{protien}}$$

这些公式来自 `paper.md:177-191`。代码中的 `train_STProtein` 对应实现是：

```python
loss = w1 * F.mse_loss(x1, x1_rec) + w2*F.mse_loss(target, z)
```

位置是 `STProtein_repo/STProtein/model/train.py:23-31`。`main.py` 传入 `weights=[5,3]` 和 `n_epochs=12000`，与论文的 $\beta_1=5,\beta_2=3$ 和 12000 epoch 一致（`STProtein_repo/STProtein/main.py:119-126`; `paper.md:238-241`）。

### 代码和论文不完全一致的地方

最重要的差异是 GATv2。论文强调 STProtein 基于 GATv2，并在 Appendix E 报告 GATv2 优于 GCN、SAGE、Transformer 和 GAT（`paper.md:79-123`, `paper.md:584-612`）。代码确实定义了 `GATv2Conv_Encoder` 和 `GATv2Conv_Decoder`（`STProtein_repo/STProtein/model/model.py:74-115`），但是顶层 `STProtein` 默认构造函数使用的是 `SAGEConv_Encoder` 和 `SAGEConv_Decoder`（`STProtein_repo/STProtein/model/model.py:180-187`），而 `train_STProtein` 没有传入 GATv2 override（`STProtein_repo/STProtein/model/train.py:7-14`）。因此，当前顶层训练脚本不能视为论文 GATv2 路径的精确复现。

第二个差异是 weight decay。论文写的是 `1e-4`（`paper.md:238-241`），但 `main.py` 传的是 `0.001`，训练函数默认值又是 `1e-5`（`STProtein_repo/STProtein/main.py:119-126`, `STProtein_repo/STProtein/model/train.py:7-21`）。

第三个差异是迁移预测代码路径。代码实现了 `Transfer_STProtein` 和 `train_Transfer_STProtein`（`STProtein_repo/STProtein/model/model.py:198-218`, `STProtein_repo/STProtein/model/train.py:42-70`），但 `main.py` 中对应调用被注释掉；活跃路径是直接把测试 RNA 特征和图输入训练好的 `model`，取 `test_z` 作为预测蛋白（`STProtein_repo/STProtein/main.py:130-156`）。

### 聚类和评价

论文上游任务用 RMSE 评价蛋白预测，公式在 Eq. 15（`paper.md:446-453`）。代码中 `RMSE` 把真实值和预测值拉平成数组，然后计算均方误差开方（`STProtein_repo/STProtein/main.py:28-32`, `STProtein_repo/STProtein/main.py:137-141`）。

下游聚类使用 NMI、AMI、FMI、ARI、Homogeneity、V-measure、F1-Score 和 Jaccard 等指标（`paper.md:232-235`, `paper.md:456-568`）。代码中，`main.py` 打印 Jaccard、F-measure、MI、NMI、AMI、V-measure、homogeneity/completeness、ARI 和 FMI（`STProtein_repo/STProtein/main.py:191-210`）。本地 `metric.py` 实现了 TP/TN/FP/FN、precision、recall、F-measure 和 Jaccard（`STProtein_repo/STProtein/metric.py:390-423`）。

聚类方法方面，论文比较 mclust、leiden 和 louvain，并说 mclust 在多数情况下更好（`paper.md:206-209`, `paper.md:646-655`）。代码的 `tool = 'mclust'` 是默认路径（`STProtein_repo/STProtein/main.py:159-170`），`utils.py` 也支持 mclust/leiden/louvain 三种方法（`STProtein_repo/STProtein/utils.py:12-88`）。

### 实验结果和图像证据

论文报告 STProtein 在 mouse spleen、mouse thymus 和 human lymph node 三个数据集上的 RMSE 都优于 totalVI、scArches、Dengkw、cTP-net（`paper.md:212-220`, `paper.md:247-250`）。下游聚类方面，论文说 STProtein 在多数指标上表现更好，但也承认某个表中 NMI 和 AMI 低于 Dengkw 和 scArches（`paper.md:253-259`）。

Figure 5-7 是三套数据上的空间聚类可视化。它们可以支持“空间模式可视化比较”，但不能单独证明数值优势；数值结论应以论文表格和指标文本为准。Figure 4 是 $\beta_1,\beta_2$ 权重敏感性热图，支持论文选择 5:3 权重的解释（`paper.md:658-663`）。

生物学案例集中在 mouse spleen。Figure 3 显示原始 ground truth 只有 RpMPhi、B cell、T cell，而 STProtein 结果显示 RpMPhi、MZMPhi、MMMPhi、B cell、T cell 五类；Figure 8-10 展示 marker spatial maps 和新的 marker-gene annotation（`paper.md:291-313`, `paper.md:687-714`）。这些图像支持论文的解释框架，但“发现新的 macrophage subset”仍是论文层面的生物学解释，本次分析没有重新运行实验或做独立生物学验证。

### 复现性和缺口

- 代码是研究脚本快照，不是可直接安装运行的包。
- `main.py` 有硬编码本地数据路径和本地 `R_HOME`（`STProtein_repo/STProtein/main.py:45-67`, `STProtein_repo/STProtein/main.py:159-162`）。
- 没有找到专门复现 SN-vs-KNN 或单损失 ablation 的脚本/config；只看到 Radius 图的注释代码和合并损失实现。
- 本次没有 rerun benchmark、ablation 或 marker-gene case study。
- 如果要严格复现论文结果，需要先确认到底应该使用 GATv2 还是当前默认 SAGEConv，并统一 weight decay、图构建依据和数据路径。

</article>
<article class="paper-detail__panel" data-detail-panel="en" lang="en" markdown="1" hidden>

## STProtein Summary

### Overview

STProtein is a graph-neural-network framework for predicting spatial protein expression from spatial transcriptomics and paired spatial multi-omics training data. The paper motivates the method by the scarcity and cost of spatial proteomics relative to spatial transcriptomics, then proposes using RNA expression plus spatial/graph structure to infer protein expression and support downstream spatial-domain discovery (`paper.md:10-23`).

The method has three main parts: feature-graph construction, a graph autoencoder block, and upstream/downstream tasks (`paper.md:41-52`). In the paper's formulation, normalized RNA $X$ is encoded into an embedding $Z$, the decoder reconstructs RNA $X'$, and $Z$ is treated as the predicted protein expression table for transfer prediction (`paper.md:44-44`, `paper.md:195-209`).

### Method in Brief

The preprocessing pipeline selects 4,000 highly variable genes, normalizes/log-transforms RNA, applies PCA, and CLR-normalizes protein counts (`paper.md:55-58`). The feature graph is described as a KNN graph with default $k=3$ (`paper.md:61-70`, `paper.md:621-643`). The graph autoencoder is described as GATv2-based, with two graph layers in encoder/decoder and a multi-task loss combining RNA reconstruction and protein prediction (`paper.md:73-191`). The paper uses Adam, learning rate `1e-4`, 12,000 epochs, ReLU, and loss weights $\beta_1=5$, $\beta_2=3$ (`paper.md:238-241`).

After training on paired RNA/protein data, the model is applied to target RNA-only data to predict protein expression. The predicted protein embedding is then clustered, with mclust, leiden, and louvain considered and mclust selected in the paper's sensitivity discussion (`paper.md:195-209`, `paper.md:646-655`).

### Key Findings Reported by the Paper

- Upstream prediction: STProtein reports the best RMSE among totalVI, scArches, Dengkw, cTP-net, and STProtein on mouse spleen, mouse thymus, and human lymph node datasets (`paper.md:212-220`, `paper.md:247-250`).
- Downstream clustering: the paper reports broad improvement across clustering metrics, while noting at least one case where NMI and AMI are lower than Dengkw and scArches (`paper.md:253-259`).
- Ablation: the paper reports that KNN feature graphs and the combined RNA+protein loss outperform SN graph and single-loss variants on mouse spleen (`paper.md:262-288`).
- Case study: the paper uses mouse spleen marker maps and STProtein clusters to argue that it can identify additional macrophage subsets, especially MZMPhi and MMMPhi, beyond the original three-label annotation (`paper.md:291-313`, `paper.md:687-714`).

### Code Availability and Match

Code is available in the workspace snapshot from `https://github.com/zhaorui-bi/STProtein` at commit `d94baad81263b1266b429781ec0d4c1933d5c70b`. The overall code-paper fidelity is **medium**.

Verified matches include preprocessing, active KNN graph calls, the weighted MSE objective, direct target prediction through the trained model, mclust-based clustering, RMSE, and clustering metrics (`STProtein_repo/STProtein/main.py:72-170`, `STProtein_repo/STProtein/model/train.py:7-39`, `STProtein_repo/STProtein/utils.py:12-88`, `STProtein_repo/STProtein/metric.py:390-423`).

Important mismatches:

- The paper centers GATv2, and GATv2 modules exist, but the active `train_STProtein` path instantiates `STProtein` with default SAGEConv encoder/decoder (`paper.md:79-123`; `STProtein_repo/STProtein/model/model.py:74-115`, `STProtein_repo/STProtein/model/model.py:180-187`, `STProtein_repo/STProtein/model/train.py:7-14`).
- The paper describes KNN over PCA embeddings, while the graph utility constructs KNN or radius graphs from `adata.obsm["spatial"]` (`paper.md:70-70`; `STProtein_repo/STProtein/model/utils.py:15-25`).
- The paper states weight decay `1e-4`; the active script passes `0.001`, and the helper default is `1e-5` (`paper.md:238-241`; `STProtein_repo/STProtein/main.py:119-126`; `STProtein_repo/STProtein/model/train.py:7-21`).
- No dedicated script/config was found for the reported SN-vs-KNN or single-loss ablations in the inspected source scope.

### Reproducibility Notes

The repository is a research-script snapshot rather than a turn-key package. `main.py` contains hard-coded local data paths and sets a local `R_HOME` for mclust (`STProtein_repo/STProtein/main.py:45-67`, `STProtein_repo/STProtein/main.py:159-162`). Baseline scripts exist under `STProtein/Benchmarking/`, but this pass did not reproduce benchmark tables because data paths, local environments, and run orchestration are not packaged.

Figures 1-2 visibly support the training and transfer workflows; Figures 5-7 provide qualitative benchmark visualizations; Figures 3 and 8-10 support the mouse spleen biological case study. Numeric benchmark claims should be read from the paper tables/text, not inferred from the images alone (`figure_analysis.md`).

### Known Gaps

- No supplementary markdown was available.
- No benchmark or ablation experiments were rerun.
- No dedicated ablation driver/config for SN graph or single-loss variants was found.
- Biological discovery claims were summarized from paper text and local figures, not independently validated.
- Implementation mismatches should be resolved before treating the GitHub snapshot as an exact reproduction of the paper's reported GATv2 model.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
