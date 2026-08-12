---
layout: default
permalink: /paper-atlas/casei-3df7a48d/
title: "Casei"
nav: false
description: "空间组学不仅记录“某个细胞是什么状态”，还记录“哪些细胞在组织中相邻”。疾病、衰老或外界暴露可能主要改变相邻细胞之间的组织方式，而不明显改变全局细胞状态分布。若只训练细胞级分类器，模型回答的是“哪个细胞像疾病样本”；Casei 则把问题改写成：空间邻接图中的哪一条边最能区分实验条件？ 这个改写很关键。例如论文的半合成实验只重新排列局部细胞位置或细胞类型邻接关系，同时保持整个组织的表达谱分布不变。"
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
      <span>Cell-Cell Communication</span>
      <span>bioRxiv · 2026</span>
    </div>
    <h1>Casei</h1>
    <p>Decoding Condition-Specific Cellular Crosstalk in Spatial Omics via Bilinear Edge Classification</p>
    <a class="paper-detail__doi" href="https://doi.org/10.64898/2026.05.03.722470" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## Casei：用双线性边分类解码条件特异的空间细胞互作

### 1. 论文要解决什么问题

空间组学不仅记录“某个细胞是什么状态”，还记录“哪些细胞在组织中相邻”。疾病、衰老或外界暴露可能主要改变相邻细胞之间的组织方式，而不明显改变全局细胞状态分布。若只训练细胞级分类器，模型回答的是“哪个细胞像疾病样本”；Casei 则把问题改写成：**空间邻接图中的哪一条边最能区分实验条件？**

这个改写很关键。例如论文的半合成实验只重新排列局部细胞位置或细胞类型邻接关系，同时保持整个组织的表达谱分布不变。Annotatability、MELD 一类节点级条件关联方法在这种设定下缺少可利用的单细胞分布变化；Casei 直接给邻接边打分，因此能捕捉“细胞没变，但邻居关系变了”的信号。图 1 给出完整流程，图 2 用已知受扰动边作为真值检验这一设计。

### 2. 输入、输出与基本假设

第 $\ell$ 个空间样本包含：

- 表达矩阵 $X_\ell\in\mathbb{R}^{n_\ell\times d}$；
- 空间坐标 $S_\ell\in\mathbb{R}^{n_\ell\times 2}$（方法也可推广到 1D/3D）；
- 样本条件标签 $y_\ell\in\{1,\ldots,C\}$。

Casei 对每个样本独立构建空间 $k$ 近邻图 $G_\ell$。节点是细胞，边 $(i,j)$ 连接空间邻近细胞，并继承所在样本的条件标签 $c_{ij}=y_\ell$。因此监督信号来自样本条件，训练实例却是细胞对。

主要输出有三类：每条边的条件关联置信度、只保留高置信边的 condition-adjusted graph（条件调整图），以及每个条件的基因—基因互作矩阵 $M_c$。这里的“互作”应理解为条件相关的空间共现和跨邻居协调表达；论文明确说明，它不等同于直接配体—受体信号，更不能单独证明因果通信。

### 3. 方法流程

```text
多份空间组学样本
  ├─ 表达 X、坐标 S、样本条件 y
  ↓ 每个样本独立建空间 kNN 图
带条件标签的邻接边 (xi, xj, cij)
  ↓ 低秩双线性边分类器 + 交叉熵训练
每个 epoch 对真实条件的预测概率
  ↓ 跨 epoch 求均值并按条件内排序
高置信 condition-adjusted graph
  ├─ 细胞类型邻域富集
  ├─ 条件差异基因对
  ├─ 谱分解得到互作程序
  └─ interacting 与 bystander 细胞差异表达
```

#### 3.1 预处理与空间图

论文将每个细胞的计数归一化到 $10^4$ 后取 `log1p`，再根据坐标构建 $k$NN 图；默认 $k=5$。本地代码在 `casei/tools/_preprocessing.py:37-103` 实现这一路径，并可选取高变基因。每个样本单独生成 PyTorch Geometric `Data`，所有边都复制该样本的条件编码。这个设计避免把不同组织切片之间的细胞误连起来。

#### 3.2 为什么使用双线性分类器

对每个条件 $c$，模型学习低秩因子 $W_c\in\mathbb{R}^{d\times r}$，并定义

$$
M_c=W_cW_c^T,
$$

$$
\operatorname{score}_c(x_i,x_j)
=x_i^TM_cx_j
=x_i^T(W_cW_c^T)x_j
=(W_c^Tx_i)^T(W_c^Tx_j).
$$

$M_c$ 的第 $(k,m)$ 个元素描述：一个细胞中基因 $k$ 与其邻居中基因 $m$ 的协调表达，对条件 $c$ 的边分类有多大贡献。$W_cW_c^T$ 使矩阵对称、半正定并至多为秩 $r$；前向计算只需先把端点投影到 $r$ 维，不必为每条边显式计算完整 $d\times d$ 矩阵，复杂度从二次基因维度降为每边 $O(dr)$。

本地实现 `casei/models/__init__.py:55-116` 为每个条件保存形状为 `(classes, genes, rank)` 的 $W$，用两次 `einsum` 直接计算所有边的低秩双线性分数。`get_active_weights()` 才显式构造 $W_cW_c^T$ 供解释分析使用。

#### 3.3 训练与 training-dynamics confidence

模型用边条件标签做多分类交叉熵，并对 $W$ 加 $L_1$、$L_2$ 正则。论文默认 $r=64$、$\lambda_{L1}=10^{-5}$、$\lambda_{L2}=10^{-4}$。关键并不是只取最后一个 epoch 的预测，而是在每个 epoch $e$ 记录模型赋给该边真实标签的概率：

$$
\operatorname{confidence}(x_i,x_j)
=\frac{1}{E}\sum_{e=1}^{E}p^{(e)}(c_{ij}\mid x_i,x_j).
$$

直觉是：真正具有条件特征的边会在训练过程中持续被正确识别；偶然或模糊的边则概率较低或波动较大。平均训练轨迹比最终一次预测保留了更多连续变化信息。代码 `casei/tools/_training.py:40-102` 在每个 epoch 训练后，对同一批训练图做 softmax，收集真实类别概率并最终求均值。这里没有独立验证集，因此该分数应作为**条件内相对排序**，而不是校准后的绝对概率。

#### 3.4 从边分数到可解释组织结构

训练结束后，Casei 在每个条件内按置信度排序，论文默认保留前 5% 边，得到 condition-adjusted graph。它仍是原空间邻接图的子图，只是去除了不稳定或缺乏条件特异性的边。下游分析包括：

1. 在调整图上做细胞类型 neighborhood enrichment，比较哪些细胞类型对在特定条件下富集；
2. 计算两个条件的差异互作矩阵

   $$
   \Delta=M_{c_1}-M_{c_2},
   $$

   并从 $\Delta^+=\max(\Delta,0)$ 中提取条件 $c_1$ 更强的基因对；
3. 对对称矩阵 $\Delta^+$ 做特征分解，按特征向量的绝对载荷选基因，形成可做 GO/KEGG 富集的互作程序；
4. 对指定细胞类型对，把至少连接一条高置信边的细胞标为 `Interacting`，其余标为 `Bystander`，再用 Wilcoxon 检验寻找互作相关表达变化。

本地代码分别在 `casei/tools/_analysis.py:15-87`、`casei/enrichment/__init__.py:30-183` 和 `casei/plotting/interaction_drivers.py:20-212` 实现这些步骤。

### 4. 论文如何验证 Casei

#### 4.1 有真值的半合成基准

论文以小鼠器官发生 seqFISH 数据为基础，构造局部位置打乱、局部细胞类型富集、两类细胞位置交换、两类细胞共定位增强等扰动。受扰动细胞相连的边构成真值，评价指标是按 Casei 置信度排序后的边级 AUROC。图 2 显示，Casei 在四个主要扰动上优于 Node Mean、GCN、GAT、GraphSAGE，以及三种用 sum、concat、product 聚合端点特征的 edge-MLP；补充实验还包括全组织位置置换和局部配体—受体表达诱导。

#### 4.2 三个真实空间组学场景

- **人动脉粥样硬化 Xenium（12 个斑块、4 个健康样本）**：图 3 显示健康调整图以 endothelial–endothelial 等互作为主，斑块转为 macrophage 主导；吸烟者斑块相对偏向 VSMC 中心结构。健康差异互作矩阵中，ITLN1 与 LUM 等基因对成为主要信号。
- **人肝纤维化 MERFISH（3 个健康、4 个纤维化样本，300 个基因）**：图 4 的健康调整图突出 hepatocyte–hepatocyte 和 hepatocyte–macrophage 邻域，指向纤维化时肝小叶分区和窦周生态位的破坏；A2M、CD4、IL4R 及 ECM 相关基因对支持这一解释。
- **小鼠脑衰老 MERFISH**：图 5 显示 aged brain 的 CC/ACO 区域富集 oligodendrocyte–microglia 和 oligodendrocyte–oligodendrocyte 边，脑室区从年轻时 NSC–neuroblast–ependymal 结构转向炎症性 ependymal–ependymal 模式；interacting/bystander 分析进一步找到 Lyz2、B2m、H2-K1、C4b、Apod 和 Klk6 等相关变化。

这些结果支持 Casei 能发现“同一细胞类型对内部只有部分边发生重排”的结构，但真实数据结果仍是观察性关联，而非直接机制验证。

### 5. 论文与公开代码的对应和差异

核心方法匹配度为 **medium-high**：图构建、$W_cW_c^T$ 双线性模型、交叉熵、跨 epoch 置信度、调整图、差异基因对、互作程序和 interacting/bystander 分析均能在源码中定位。

需要特别注意三类差异：

- 论文 Supplementary Table 2 给出 100 epochs、学习率 $10^{-3}$、保留 top 5%；包内默认值分别是 50、`1e-4`、top 10%。复现论文需显式覆盖参数。
- 论文 Eq. 2/14 写成 `exp[-score]`，源码把正的双线性值直接作为 logits 交给 `CrossEntropyLoss`。双线性结构相同，但符号约定并非逐字实现。
- 当前克隆包没有半合成扰动生成器、七个基线实现和三组真实数据的完整制图脚本。README 指向外部 atherosclerosis reproducibility notebook，但它不在本工作区，因此不能据此声称完整复现。

### 6. 阅读与使用时的边界

Casei 最适合回答“哪些空间邻接边的联合表达模式与条件相关”，其优势来自边级监督和可直接检查的双线性权重。置信度依赖样本规模、类别平衡和训练设置，应优先看条件内排名及阈值敏感性；论文也用 3%–7% 保留比例验证部分邻域富集结果的稳定性。细胞分割错误可能把相邻细胞的转录本错误分配，从而人为放大跨细胞协调表达。最后，空间共现可以来自共同微环境或组织结构约束，不能自动解释为直接信号传递。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Casei Summary

### Motivation And Novelty

Casei targets condition-specific tissue reorganization in spatial omics. The paper argues that disease, fibrosis, aging, and environmental exposure can alter the relationships between neighboring cells even when individual cell states or cell type frequencies do not fully explain the change. Instead of asking which cells are condition-associated, Casei asks which spatial graph edges are condition-associated.

The main novelty is the combination of edge-level supervised learning, a bilinear gene-gene interaction architecture, and training-dynamics confidence. The bilinear form forces the classifier to use coordinated expression across neighboring cells, so learned weights can be interpreted as condition-specific cross-cell gene-pair contributions. The confidence score then filters the spatial graph to the edges that consistently support a condition label across training epochs.

Compared methods include MELD (Nature Biotechnology, 2021), Annotatability (Nature Computational Science, 2024), GraphCompass (Bioinformatics, 2024), Squidpy neighborhood enrichment (Nature Methods, 2022), STAGATE (Nature Communications, 2022), HoloNet (Briefings in Bioinformatics, 2023), SpaGCN (Nature Methods, 2021), plus GCN (ICLR, 2017), GAT (ICLR, 2018), and GraphSAGE (NeurIPS, 2017) baselines. The paper's central limitation claim is that node-centric or full-graph methods can miss condition-associated subsets of edges within the same cell type pair.

### Method Overview

Casei takes spatial omics samples with expression matrices, coordinates, sample IDs, and condition labels. For each sample, it builds a k-nearest-neighbor spatial graph. Every graph edge inherits the sample's condition label and becomes a training instance.

For each condition $c$, Casei learns a low-rank matrix factor $W_c$ and scores each edge by:

$$
score_c(x_i,x_j)=x_i^T(W_cW_c^T)x_j.
$$

The model is trained with edge-level cross-entropy. During training, Casei records the probability assigned to each edge's true condition label at every epoch and averages these probabilities into a confidence score. The top confidence-ranked edges form a condition-adjusted graph.

Downstream analysis uses this graph for cell-type neighborhood enrichment, UMAP/spatial edge overlays, differential gene-pair matrices, eigendecomposition-based interaction programs, and interacting-vs-bystander differential expression.

### Evaluation

The synthetic benchmark uses mouse organogenesis seqFISH-like data with known perturbations. Casei achieves the strongest AUROC in the four main perturbation cases and remains strong in supplementary perturbations. These experiments provide the cleanest evidence because perturbed edges are known.

In human atherosclerosis Xenium data, Casei finds a shift from endothelial-dominated control interactions to macrophage-dominated plaque interactions, with smoker plaques showing VSMC-centered interactions. In human liver fibrosis MERFISH data, Casei identifies healthy hepatocyte-hepatocyte and hepatocyte-macrophage niches that are diminished in fibrosis. In mouse brain aging MERFISH data, Casei highlights region-specific glial rewiring, including aged oligodendrocyte-microglia interactions and young ventricular-lineage interactions.

The real-data analyses are biologically plausible and well connected to spatial figures, enrichment heatmaps, gene-pair networks, and interaction-driver genes. They remain observational: Casei identifies condition-associated co-localization and coordinated expression, not direct signaling or causality.

### Code And Reproducibility

The public `nitzanlab/casei` package implements the core algorithm: preprocessing to per-sample kNN graphs, the low-rank bilinear `W @ W^T` model, training-dynamics confidence, confidence graph storage, differential gene-pair analysis, interaction-program enrichment, neighborhood enrichment comparison, and interacting-vs-bystander DE.

Important gaps:

- Package defaults differ from the paper: code defaults are 50 epochs, learning rate `1e-4`, and top 10% edge retention, while the paper reports 100 epochs, learning rate `1e-3`, and top 5%.
- The code uses raw bilinear logits in PyTorch cross-entropy, not the paper's printed `exp[-score]` sign convention.
- The cloned package does not contain the synthetic perturbation generator, seven baseline implementations, or complete scripts for the atherosclerosis, liver fibrosis, and brain aging figures. The README links an external reproducibility tutorial for atherosclerosis.

Reproducibility rating: **3/5**.

The core method is reusable and source-level verifiable, but full paper reproduction is incomplete from the acquired package alone. A reader can apply Casei and reproduce the main algorithmic mechanics, but would need external notebooks/scripts and exact parameter overrides to reproduce the full benchmark and biological figure set.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
