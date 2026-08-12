---
layout: default
permalink: /paper-atlas/cosmos-1006fbb5/
title: "COSMOS"
nav: false
description: "COSMOS 面向同一批 spot/细胞上同时测得的两种空间组学。它在共享空间邻接图上为两个模态各建一个 GCN encoder，用 Deep Graph Infomax（DGI）让局部节点表示保留全局组织信息；训练中途从两个模态表示计算每个细胞自己的 WNN 权重，将两路表示加权合成。论文还加入空间距离—嵌入距离正则，使空间相近的细胞倾向在联合表示中接近。"
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
      <span>Nature Communications · 2025</span>
    </div>
    <h1>COSMOS</h1>
    <p>Cooperative integration of spatially resolved multi-omics data with COSMOS</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s41467-024-55204-y" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## COSMOS 方法解读：用双通道 DGI、逐细胞 WNN 权重与空间正则整合配对空间多组学

### 一句话理解

COSMOS 面向同一批 spot/细胞上同时测得的两种空间组学。它在共享空间邻接图上为两个模态各建一个 GCN encoder，用 Deep Graph Infomax（DGI）让局部节点表示保留全局组织信息；训练中途从两个模态表示计算每个细胞自己的 WNN 权重，将两路表示加权合成。论文还加入空间距离—嵌入距离正则，使空间相近的细胞倾向在联合表示中接近。最终 embedding 用于空间域、UMAP 和 pseudo-spatiotemporal map（pSM），而不是直接生成或补全原始组学矩阵。

论文为 Zhou 等发表于 *Nature Communications*（2025）的 “Cooperative integration of spatially resolved multi-omics data with COSMOS”，DOI `10.1038/s41467-024-55204-y`。本工作区含 PMC 正文、四个主图和官方 Python 源码；acquisition 元数据记录上游 `https://github.com/Lin-Xu-lab/COSMOS.git` 提交 `56ea355be51e64d9253e2871b8bd447fdfd0d230`，`setup.py` 标记 1.0，源码头注明 2024-10-10。源码目录没有独立 `.git`，所以该提交只能由 acquisition 合同追溯，不能用外层 PaperCode 的提交号替代。

### 1. 输入契约：必须是配对的两个模态

COSMOS 的核心输入是两个行严格对齐的矩阵 $X^{(1)},X^{(2)}$ 和一套共享二维空间坐标。第 $i$ 行必须代表同一个 spot/细胞；它不是为两个模态中细胞集合不一致的 unpaired integration 设计的。`Cosmos.__init__()` 接受两个 AnnData，或两个 count matrix 加同一 `spatial_locs`。当前实现没有在构造阶段系统核验两份 AnnData 的 obs 顺序，因此调用者必须自己保证对齐。

`preprocessing_data()` 可选做总量归一化、log1p、各模态 HVG 和 PCA，并在第一模态的 `obsm["spatial"]` 上建立 kNN distance graph。这个图 $A$ 被两路 encoder 共用。默认 `do_norm=False`、`do_log=False`、`do_pca=False`，所以“调用 preprocessing”并不自动等于执行论文全部预处理；教程中的参数才决定具体数据进入模型的表示。

### 2. 两路 GCN 如何得到模态表示

对每个模态 $m\in\{1,2\}$，模型使用两层 GCN：

$$
H^{(m)}=\operatorname{Norm}\left(
\operatorname{PReLU}\left(
\operatorname{GCN}_2^{(m)}(
\operatorname{PReLU}(\operatorname{GCN}_1^{(m)}(X^{(m)},A)),A)
\right)\right).
$$

`GraphEncoderWNNit` 为两模态保留独立的第一、第二层参数，最后逐细胞 L2 normalize。共享的是空间边，而不是 encoder 权重。这样同一空间邻域中的两个模态都做消息传播，但可学习不同的分子特征变换。

GCN 本身主要聚合局部邻居。COSMOS 外面套 DGI，使表示还要能区分真实节点—全局 summary 对与被扰动的负对。论文 Fig. 1a 的两条 GCN、WNN、contrastive discriminator 和 spatial loss 对应当前训练主链。

### 3. DGI：让联合表示保留全局组织结构

给定联合正样本表示 $H^{\mathrm{int}}$，summary 是逐维平均后 sigmoid：

$$
s=\sigma\left(\frac1N\sum_i h_i^{\mathrm{int}}\right).
$$

判别器用可学习双线性矩阵 $M$：

$$
D(h_i,s)=\sigma(h_i^\top Ms).
$$

正样本来自真实两模态特征，负样本通过分别随机排列两份特征矩阵的节点行而得到，空间图保持不变。损失为

$$
L_{\mathrm{DGI}}=-\frac1N\sum_i
\left[\log D(h_i,s)+\log(1-D(\tilde h_i,s))\right].
$$

`modulesWNN.py::DeepGraphInfomaxWNN` 直接实现 summary、bilinear discriminator 和正负 log loss；`corruptionWNNit()` 做行排列。DGI 最大化的是局部节点与全局 summary 的可判别一致性，不是显式重建基因，也不是监督分类。

论文指出所用数据的细胞状态较连续，简单 shuffle 足够；若数据是彼此高度分离的清晰类型，负样本可能过于容易，作者也将更复杂的 adversarial/cluster-based corruption 留作未来工作。

### 4. WNN：权重是逐细胞、逐模态的

两个 encoder 输出并非简单平均。对每个细胞，WNN 比较“使用同模态邻居预测该模态表示”和“使用另一模态邻居预测该模态表示”的效果，得到 within- 与 cross-modality affinity ratio。两模态得分经 logistic/softmax 形式转成权重：

$$
w_i^{(1)}=\frac{e^{r_{1,2}(i)}}
{e^{r_{1,2}(i)}+e^{r_{2,1}(i)}},qquad
w_i^{(2)}=1-w_i^{(1)}.
$$

联合表示为

$$
h_i^{\mathrm{int}}=w_i^{(1)}h_i^{(1)}+
w_i^{(2)}h_i^{(2)}.
$$

权重随细胞变化：某个区域的 RNA 更可预测时，RNA 可占更大权重；另一处可能由 ATAC/蛋白主导。Fig. 3d 的 violin plot 就是在不同脑区展示 RNA 与 ATAC 权重分布。权重表达的是局部表示可预测性，不应直接解释成“这个模态对生物机制的因果贡献百分比”。

当前 `pyWNN.py` 从各模态的 20-neighbor 图估计带宽与亲和性，并在两模态各自 200-neighbor union 上产生 WNN graph；`GraphEncoderWNNit.forward()` 实际只取 `obsm["Weights"]` 融合表示。

### 5. WNN 不是每轮都更新

WNN 计算为 $O(N^2)$ 且独立于反向传播。训练初始令 $w^{(1)}=w^{(2)}=0.5$，先优化 DGI；达到 `wnn_epoch` 或 pre-WNN patience 后，将两路 GCN embedding `detach()` 到 CPU，计算一次 WNN 权重，然后固定到训练结束。源码通过把 `wnn_epoch=0`、`max_patience_bef=total_epoch` 阻止第二次刷新。

这形成一个明显的时间顺序：

1. 等权融合预训练；
2. 用当前 encoder 表示估计一次逐细胞权重；
3. 固定权重继续优化 encoder。

因此 WNN 与 encoder 不是完全联合迭代到自洽，也不是可微层。`max_patience_bef` 太小会在表示未成熟时锁定权重，太大可能过拟合后才计算。论文基于五个数据集建议 5–30，常用 10；API 默认 `wnn_epoch=100`、`min_stop=100`、seed 42，而论文 Methods 的统一设置是 `wnn_epoch=500`、`min_stop=200`、seed 20。复现论文必须采用教程/Methods 参数，不能只依赖 API 默认值。

### 6. 空间正则：论文目标与当前加速实现要分开

论文希望空间距离 $D_{ij}^s$ 大时，不强迫 embedding 相近；空间很近时，则惩罚过大的 embedding 距离 $D_{ij}^e$。归一化后的目标写成

$$
L_{\mathrm{sp}}=\frac1{|\mathcal P|}\sum_{(i,j)\in\mathcal P}
D_{ij}^{s}(1-D_{ij}^{e}),
$$

总损失为

$$L=L_{\mathrm{DGI}}+\alpha L_{\mathrm{sp}}.$$

非加速分支用 `torch.cdist` 计算全部细胞对，符合上述意图。论文对 $N>5000$ 随机抽 1,000,000 对以近似 $O(N^2)$ 项，并报告 $\alpha$ 通常在 0–0.1 内较合适。

但是当前 `cosmos.py:234-246` 的加速分支存在关键代码风险：它独立抽取 `cell_random_subset_1` 和 `_2` 来取得 $z_1,z_2$，却对坐标 `c1,c2` 都使用 `_1`。因此每一对坐标实际上相同，`sp_dists` 理论上为 0，空间 penalty 退化为 0。`regularization_acceleration=True` 是 API 默认，而且数据大于 5000 时无论该参数如何都会进入此分支。这个判断来自直接源码，不是论文声明；本次没有运行 GPU 实验测量其对已发表结果的影响。

实际复现应先修复/验证该索引，再比较结果；仅将 `regularization_acceleration=False` 对小数据有效，超过 5000 仍会走当前加速分支。不能在未验证运行路径时声称本地默认代码确实施加了论文空间正则。

### 7. 训练输出和数据对象

标准调用是：

```python
model = Cosmos(adata1=adata_rna, adata2=adata_atac)
model.preprocessing_data(..., n_neighbors=10)
embedding = model.train(...)
weights = model.weights
```

`train()` 返回 `N×z_dim` embedding，并在对象上保存 `weights`。函数签名中的 `embedding_save_filepath` 和 `weights_save_filepath` 当前没有用于自动写 TSV；若工作流需要文件，调用者必须显式保存。这是 API 文档/签名与行为的差异。

主包也不直接完成 domain segmentation、UMAP 或 pSM。教程将 embedding 放进 AnnData，再调用 Scanpy Leiden/Louvain、UMAP、diffusion map/DPT。结果依赖手动聚类 resolution 和 DPT root cell，因此这些 downstream 选择必须与 embedding 学习参数一起报告。

### 8. pSM 是怎样来的

Pseudo-spatiotemporal map（pSM）不是 COSMOS 训练目标中的时间变量。它是在联合 embedding 上使用 Scanpy diffusion map 和 diffusion pseudotime，手动选 root 后得到的排序。论文用 pSM 研究视觉皮层和脑区空间进程，并将基因表达与 pSM 做 Pearson correlation，$P<10^{-10}$ 的基因称为 pSM-associated genes。

所以 pSM 表示联合分子—空间流形上的相对顺序，不是实验时间、RNA velocity 或谱系追踪。root 选择、邻居图和 embedding 质量会改变方向。Fig. 3f/h/i 用脑区 pSM、基因热图和空间基因图支持连续组织轴，但不证明细胞真实从一个空间位置迁移到另一个位置。

### 9. 如何读四个主图

- Fig. 1 是方法与输出契约：双通道 GCN、逐细胞 WNN、DGI 判别、空间 loss，之后才是 domain、UMAP、pSM 和关联基因。
- Fig. 2 在模拟视觉皮层数据检验 domain 与连续空间结构，并比较基线；它同时用于展示全局信息保留。
- Fig. 3 在 P22 spatial ATAC–RNA mouse brain 上展示 COSMOS 的 ARI、模态权重、UMAP、pSM 及 pSM-associated genes。COSMOS ARI 0.63 是该数据/标注/参数组合的结果，不是通用保证。
- Fig. 4 在 DBiT-seq RNA–protein、spatial-CITE-seq 或其他配对多组学中检验方法跨 assay 的适用性。

视觉域与 Allen Brain Atlas/人工标注的吻合、ARI 及连续 pSM 各回答不同问题。不能仅凭更平滑的空间图判断模型更准确；过强 $\alpha$ 也会用空间连续性压过真实分子边界。

### 10. 论文—代码对应

| 机制 | 本地证据 | 判断 |
|---|---|---|
| 配对双组学 + 共享空间图 | `Cosmos.__init__()`, `preprocessing_data()` | Exact |
| 双 GCN encoder | `cosmos.py::GraphEncoderWNNit` | Exact |
| DGI summary/discriminator/loss | `modulesWNN.py` | Exact |
| 特征 shuffle 负样本 | `corruptionWNNit()` | Exact |
| 逐细胞 WNN 权重及加权融合 | `pyWNN.py`, `GraphEncoderWNNit.forward()` | Exact 主机制；一次 detach 更新 |
| 训练时序 | `Cosmos.train()` | Exact：等权预训练、一次 WNN、固定权重 |
| 空间正则 | `cosmos.py:231-260` | Partial：全量分支匹配；默认/大数据加速分支疑似退化 |
| domain/UMAP/pSM | `Tutorials/*.ipynb` | Notebook：不是核心 API |
| 自动文件输出 | `train()` 的 path 参数 | Not found：参数未被使用 |
| 论文全 benchmark | 正文、教程与外部数据 | Partial：无统一 runner/锁定环境，基线依赖外部实现 |

### 11. 版本与复现边界

- acquisition 合同记录 upstream commit `56ea355…`；当前 snapshot 无独立 `.git`，不能现场复核该 commit。
- `setup.py` 为 1.0，模块头为 2024-10-10；没有依赖锁文件。
- 教程依赖 Scanpy、PyTorch、PyG、pyWNN 路径和外部数据；版本差异可改变邻居、聚类和随机性。
- 论文使用的若干参数与 `train()` 默认值不同。
- 空间正则加速索引风险是数值复现的硬边界；在修复并重跑前，只能确认非加速公式与论文一致，不能确认默认训练结果。
- 基线比较、processed data 和 pSM root/cluster resolution 分散在外部数据和 notebooks；本次未重跑论文所有图表。

### 证据入口

- 正文/Methods：`paper source/PMC11696235/paper.md`
- 四个主图：`paper source/PMC11696235/images/*Fig*_HTML.jpg`
- 主流程、GCN、空间 loss：`COSMOS/COSMOS/cosmos.py`
- DGI：`COSMOS/COSMOS/modulesWNN.py`
- WNN：`COSMOS/COSMOS/pyWNN.py`
- 教程下游：`COSMOS/Tutorials/*.ipynb`
- 包元数据：`COSMOS/setup.py`

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## COSMOS Summary

### Motivation and Novelty

COSMOS addresses paired spatial multi-omics data, where two molecular assays are measured at the same spatial positions. Existing spatial methods such as SpaGCN (Nature Methods, 2021) and SpaceFlow (Nature Communications, 2022) focus on single-omics spatial structure, while multi-omics methods such as GLUE (Nature Biotechnology, 2022), WNN (Cell, 2021), MIRA (Nature Methods, 2022), and totalVI (Nature Methods, 2021) do not explicitly model shared tissue geometry. The paper also argues that CellCharter (Nature Genetics, 2024) and SpaMultiVAE (Nature Methods, 2024) concatenate modalities in ways that can miss modality-specific complementary signal, while SpatialGlue (Nature Methods, 2024) is less stable and less efficient in the tested settings.

The novelty is a two-channel Deep Graph Infomax model: each modality is encoded by its own graph convolutional branch on a shared spatial KNN graph, the branch embeddings are fused with cell-specific WNN modality weights, and a spatial regularization term encourages the integrated embedding to respect tissue proximity.

### Method Overview

COSMOS takes two paired omics matrices and shared spatial coordinates. It builds a spatial neighbor graph, learns a GCN/DGI embedding for each modality, computes WNN weights from the learned modality embeddings, and forms a weighted integrated embedding. The DGI objective contrasts real integrated embeddings against embeddings from permuted feature matrices, using a global summary vector. A tunable spatial penalty controlled by $\alpha$ favors embeddings where spatially close cells remain close in latent space.

The integrated embedding is used for downstream domain segmentation, UMAP visualization, pseudo-spatiotemporal map generation by Scanpy DPT, and pSM-associated gene analysis. These outputs should be interpreted as computational summaries of spatial tissue organization, not direct measurements of temporal dynamics.

### Evaluation

On two simulated spatial multi-omics datasets, COSMOS achieved the highest reported ARI among tested methods: 0.84 on simulated STARmap mouse visual cortex and 0.63 on simulated Stereo-seq mouse olfactory bulb. These simulations were designed so each modality alone lost different anatomical separability, making them a direct test of complementary integration.

On real mouse brain RNA+ATAC data, COSMOS reached ARI 0.63 against manual anatomical labels, outperforming SpaceFlow on RNA, SpaceFlow on ATAC, WNN, SpatialGlue, and CellCharter. Modality weights were region-specific, with ATAC contributing more to cortical layers and RNA contributing more to several non-layer regions.

On DBiT-seq RNA+protein mouse embryo brain, the evidence is mainly qualitative: COSMOS produced smoother regions that matched RNA and protein marker patterns, and modality weights aligned with marker-defined clusters.

### Code and Reproducibility

The official repository implements the core COSMOS model in a compact Python package. The main algorithmic components match the paper: paired two-omics input, spatial KNN graph construction, two separate GCN branches, DGI discriminator/loss, WNN fusion, one-time WNN refresh, spatial regularization, and tutorial-level downstream clustering/UMAP/DPT.

Important caveats:

- The package defaults are not the same as paper/tutorial settings; reproduction should use the explicit tutorial parameters.
- The accelerated spatial regularization branch appears to pair coordinates incorrectly, which may weaken the intended Eq. 8 spatial penalty when acceleration is enabled.
- Full benchmark reproduction is not packaged as a single all-baselines workflow. Tutorials cover COSMOS-side analyses for several datasets, but processed data and baseline comparisons depend on external resources.
- The train method exposes embedding/weight output path arguments but does not write those files automatically.

Reproducibility rating: **3 / 5**. The core model is available and readable, and tutorials support key analyses, but exact paper-level reproduction requires external processed data, notebook execution, baseline method setup, and attention to the spatial-regularization implementation caveat.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
