---
layout: default
permalink: /paper-atlas/scipenn-ed4e7447/
title: "sciPENN"
nav: false
description: "sciPENN 的方法核心是：用一个带 RNN hidden embedding、蛋白均值/分位数 head 和可选 label head 的神经网络，从 CITE-seq 中学习 RNA 到蛋白的映射；再通过 measured-protein mask 实现 censored loss，使多个蛋白面板不完全重叠的 CITE-seq 数据集可以联合训练，并进一步完成缺失蛋白补全、scRNA-seq 蛋白预测、不确定性估计和标签转移。"
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
      <span>Nature Machine Intelligence · 2022</span>
    </div>
    <h1>sciPENN</h1>
    <p>A multi-use deep learning method for CITE-seq and single-cell RNA-seq data integration with cell surface protein prediction and imputation</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1038/s42256-022-00545-w" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## sciPENN 方法中文解读

### 这篇文章解决什么问题？

CITE-seq 能在单细胞层面同时测量 RNA 和细胞表面蛋白，但成本高；scRNA-seq 更常见，却没有蛋白信息。实际分析中还会遇到另一个问题：不同 CITE-seq 数据集测的抗体面板不完全相同，一个数据集有的蛋白，另一个数据集可能没有。因此，直接合并多个 CITE-seq 数据集会产生大量“结构性缺失”的蛋白值。

sciPENN 的目标是用一个深度学习框架同时处理这些任务：

- 用 CITE-seq 参考数据给 scRNA-seq 查询细胞预测蛋白表达；
- 合并多个蛋白面板不完全重叠的 CITE-seq 数据集；
- 给 CITE-seq 中未测量的蛋白做 imputation；
- 给预测和 imputation 提供分位数不确定性；
- 把 CITE-seq 和 scRNA-seq 细胞放到共同 embedding 空间；
- 在有参考标签时，把 CITE-seq 的细胞类型标签 transfer 到 scRNA-seq 查询细胞。

论文的摘要和引言明确把这些作为 sciPENN 的核心功能（`paper.md:12-27`），Fig. 1 也把多 CITE-seq 补全、scRNA-seq 蛋白预测、label transfer 和共同 embedding 画在同一个流程里（`paper.md:39-47`）。

### 为什么已有方法不够？

论文主要比较 Seurat 4 和 totalVI。Seurat 4 可以做 reference mapping 和 protein prediction，但论文指出它计算开销大，而且不能处理多个 CITE-seq 数据集蛋白面板不完全重叠的合并问题。totalVI 理论上可以处理更复杂的 multi-omics 整合，但论文认为当时这种部分重叠蛋白面板的多 CITE-seq 合并场景还没有被充分探索；在 COVID 大规模整合实验中，totalVI 的数据混合和 imputation 表现明显弱于 sciPENN（`paper.md:24-27`, `paper.md:142-168`）。

### 核心思想

sciPENN 的关键不是只做一个普通的 RNA -> protein 回归，而是把以下三个设计放在一起：

1. 用神经网络从 RNA 表达学习一个隐藏 embedding；
2. 输出蛋白均值、蛋白分位数和可选的细胞类型概率；
3. 对没有测量的蛋白使用 censored loss，让这些蛋白不参与 loss 和反向传播。

直观地说，多个 CITE-seq 数据集可以先合并成一个蛋白全集矩阵：测过的蛋白保留真实值，没测过的蛋白先填 0 作为占位符。训练时不能把这些 0 当真，所以 sciPENN 用一个 mask 只在真实测过的蛋白上计算 protein loss。训练完成后，再用模型预测值把这些缺失蛋白补回来。

### 输入和输出

论文记号中，第 *i* 个 CITE-seq 数据集包含 RNA 矩阵 **X**~*i*~ 和蛋白矩阵 **Y**~*i*~；可选的 scRNA-seq 查询数据是 **X**~*q*~（`paper.md:192-198`）。预处理后，模型训练用的是合并后的 **X**~train~ 和 **Y**~train~。

输出包括：

- \(\hat y(x;W)\)：给定 RNA 表达 *x* 的蛋白均值预测；
- \(\hat \sigma(x;W)\)：多个分位数预测，用来构造 prediction interval；
- \(\hat p(x;W)\)：细胞类型概率向量；
- hidden embedding：用于多数据集整合和可视化；
- imputed CITE-seq protein matrix：把参考数据中未测的蛋白补上；
- predicted scRNA-seq protein matrix：给查询 RNA 细胞预测所有参考蛋白。

论文把模型写成：

$$\hat y\left( {x;W} \right),\hat \sigma \left( {x;W} \right),\hat p\left( {x;W} \right) = S(x,W)$$

（`paper.md:237-240`）

### 计算流程

```text
多个 CITE-seq references + 可选 scRNA-seq query
        |
        v
预处理
  - 细胞/基因 QC
  - normalize_total + log1p
  - 取共同基因并选择 1000 HVGs
  - 按 batch 做 z-score scaling
  - 合并蛋白全集，未测蛋白先填 0
        |
        v
训练 sciPENN 神经网络
  - 输入块 + 3 个 FF blocks
  - RNNCell 更新隐藏状态
  - 蛋白均值 head
  - 蛋白分位数 head
  - 可选 detached cell-type head
  - protein mask 实现 censored loss
        |
        +--> 补全 CITE-seq 中未测蛋白
        +--> 给 scRNA-seq 预测蛋白和分位数
        +--> 输出 embedding 和可选标签转移
```

代码中，`sciPENN_API.py` 负责把这些步骤串起来：构造函数先调用 `preprocess` 和 dataloader，`train()` 建模训练，`impute()` 补全参考蛋白，`predict()` 预测 query 蛋白，`embed()` 导出隐藏空间（`sciPENN_API.py:15-109`）。

### 预处理细节

论文说，每个数据集会过滤表达 RNA 基因少于 200 个的细胞，以及表达细胞数少于 30 的基因（`paper.md:192-198`）。代码默认参数正是 `min_genes=200`、`min_cells=30`（`sciPENN_API.py:15-17`），实际过滤在 `Preprocessing.py:50-89`。

之后，论文要求做 cell-level normalization、log transform、共同基因选择、HVG 选择和 batch-wise z-score normalization（`paper.md:195-198`）。代码对应为：

- `scanpy.pp.normalize_total`：RNA 和 protein 训练集、query RNA；
- `scanpy.pp.log1p`：RNA/protein 训练集和 query RNA；
- CITE-seq RNA 用 inner join 合并，并与 query RNA 取共同基因；
- `scanpy.pp.highly_variable_genes(..., batch_key='batch', n_top_genes=1000)` 选 HVGs；
- 对 gene/protein 按 batch 使用 `scanpy.pp.scale`。

这些步骤对应 `Preprocessing.py:97-199`。

最后，多 CITE-seq 蛋白矩阵用 outer join 合并，缺失蛋白以 0 填充（`Preprocessing.py:201-216`）。这里的 0 不是生物学值，只是占位符。

### 网络结构

论文把网络描述成由 block 组成。input block 包含 BatchNorm、Dense、BatchNorm、PReLU 和 Dropout；feed-forward block 包含 Dense、BatchNorm、PReLU 和 Dropout（`paper.md:243-268`）。代码中的 `Input_Block` 和 `FF_Block` 直接实现了这些组件（`Layers.py:4-42`）。

主模型设置隐藏维度 512、dropout 0.25，使用一个 input block、三个 FF blocks 和一个 `RNNCell`（`Model.py:17-25`）。前向传播中，输入先通过 input block，然后 RNN hidden state 初始化/更新；每经过一个 FF block，就再次更新 hidden state（`Model.py:55-83`）。最终 hidden state 既作为 embedding，也被送入输出 head。

三个输出 head 分别是：

- protein mean：线性层输出每个蛋白的均值预测；
- protein quantiles：线性层输出 `protein x quantile` 形状；
- cell-type probability：有类别标签时，用线性层加 Softmax 输出类别概率。

一个重要细节是 label-transfer head 使用 detach。论文写作：

$$\frac{\partial }&#123;&#123;\partial W}}&#123;&#123;{\mathrm{detach}}}}_W\left( {g\left( W \right)} \right) = 0\,\forall g.$$

$$\hat p\left( {x;W} \right) = {\mathrm{Dense3}}\left( &#123;&#123;&#123;&#123;\mathrm{detach}}}}_W\left( {g\left( {x;W} \right)} \right)} \right).$$

（`paper.md:271-280`）

代码中对应的是 `self.celltype_out(h.detach())`（`Model.py:68`）。含义是：细胞类型分类器可以学习如何从 embedding 分类，但分类 loss 不会反向更新上游 embedding 网络。这样模型的主要表示仍由蛋白预测/imputation 任务驱动。

### Loss 设计

#### 蛋白均值和分位数 loss

论文把 protein loss 写成均方误差加 quantile loss：

$$\begin{array}{l}L_&#123;&#123;\mathrm{prot}}} = {\mathrm{SE}}\left( {y,\hat y} \right) + L_&#123;&#123;\mathrm{quantile}}}\left( {y,\hat \sigma } \right),\\ L_&#123;&#123;\mathrm{quantile}}}\left( {y,\hat \sigma } \right) = \frac{1}{k}\mathop {\sum}\limits_{q \in Q} {L_q} \left( {y,\hat y_q} \right).\end{array}$$

（`paper.md:286-289`）

代码中 `mse_quantile` 先计算每个蛋白的 squared error 和 quantile loss，再相加（`Losses.py:11-35`）。`quantile_loss` 使用 prediction-truth 的符号来给 over-prediction 和 under-prediction 不同权重，最后对 quantile 维度平均（`Losses.py:43-55`）。API 默认分位数是 `[0.1, 0.25, 0.75, 0.9]`（`sciPENN_API.py:58-62`）。

#### 细胞类型 loss

论文用 categorical cross entropy：

$$L_&#123;&#123;\mathrm{type}}} = - {\mathrm{log}}\left( {\widehat &#123;&#123;\mathrm{Pr}}}\left( {C = c_{\mathrm{t}}} \right)} \right).$$

总 loss 是：

$$L = L_&#123;&#123;\mathrm{prot}}} + L_&#123;&#123;\mathrm{type}}}.$$

（`paper.md:292-301`）

代码中，如果用户提供 `type_key`，就用 `cross_entropy`；否则用 `no_loss`，也就是不做 label transfer 训练（`sciPENN_API.py:63-66`, `Losses.py:4-9`, `Losses.py:69-71`）。所以 label transfer 是可选功能，不是每次训练都一定启用。

#### Censored loss

这是 sciPENN 处理部分重叠蛋白面板的核心。论文强调：合并矩阵中填入的 0 只是占位符，不能作为真实蛋白值参与训练。对每个细胞 *i*，只对它真实测过的蛋白集合 \(P_i\) 计算 protein loss：

$$L_i = \frac{1}{p}\mathop {\sum}\limits_{j \in P_i} {L_{ij}}$$

（`paper.md:304-313`）

代码实现路径很清楚：

- `Preprocessing.py:211-216` 建立每个数据集的 measured-protein boolean mask；
- `Samplers.py:20-29` 根据细胞属于哪个数据集，为 minibatch 中每个细胞选择 mask；
- `DataLoader.py:20-24` 把 mask 放进 batch；
- `Losses.py:28-35` 用 `loss = loss * bools` 把未测蛋白的 loss 置零。

需要保留一个实现差异：论文公式从概念上说只平均测过的蛋白，而代码是先 mask 再 `loss.mean()`，所以未测蛋白虽然不产生梯度贡献，但它们的 0 仍然进入平均分母。这是 `doc_code.md` 中标为 Partial 的原因。

### Imputation 和 prediction

对 CITE-seq reference 的缺失蛋白，论文使用：

$$Y_j \leftarrow \left( {1 - b_j} \right) \cdot \hat y\left( {X_j;W} \right) + Y_j$$

（`paper.md:213-222`）

代码中的 `fill_predicted` 基本就是这条公式：

```python
return (1. - bools) * predicted.cpu().numpy() + array
```

（`Model.py:206-208`）

因此，已经测过的蛋白保留真实值，没测过的蛋白用预测值补上。`impute()` 还会把请求的分位数写入 AnnData layers（`Model.py:145-174`）。

对 scRNA-seq query，论文说要预测所有蛋白，并用 \(\arg\max \hat p(X_j;W)\) 得到细胞类型标签（`paper.md:225-231`）。代码中 `predict()` 创建完整 protein matrix，把所有预测均值写入 `X`，把分位数写入 layers，并在有类别 head 时写入 `transfered cell labels`（`Model.py:210-251`）。

### 评估结果如何理解？

论文通过多个场景评估 sciPENN：

- PBMC -> MALT：sciPENN 在蛋白预测和 prediction interval coverage 上整体优于对照方法（Fig. 2, `paper.md:53-76`）。
- Monocyte -> monocyte：三种方法相关性都不错，但 sciPENN 的 RMSE 和 uncertainty coverage 更好（Fig. 3, `paper.md:79-99`）。
- PBMC train/test：sciPENN 能恢复 CD8 subtype marker 的蛋白表达趋势，并在 L3/L2 label transfer 上优于 Seurat 4（Fig. 4, Extended Data Fig. 2, `paper.md:102-122`, `paper.md:448-453`）。
- PBMC -> H1N1：sciPENN 和 totalVI 相关性接近，但 sciPENN 的 RMSE 和 uncertainty coverage 更好（Fig. 5, `paper.md:125-139`）。
- Haniffa/Sanger COVID CITE-seq：这是最能体现 censored loss 的场景。sciPENN 能把两个大 CITE-seq 数据集混到共同 embedding 中，并且对模拟缺失蛋白的 imputation 优于 totalVI（Fig. 6, `paper.md:142-168`）。
- Runtime：Extended Data Fig. 4 显示 sciPENN 的运行时间曲线远低于 totalVI 和 Seurat 4（`paper.md:464-469`）。

### 代码复现边界

本 workspace 获取的是 `https://github.com/jlakkis/sciPENN`，也就是算法包本身。代码与核心方法的匹配度是 **medium**：预处理、网络结构、分位数输出、detach label head、imputation 公式、prediction 和 mask-based censored loss 都能在源码中找到。

但是论文和 Reporting Summary 都说明，复现论文所有分析需要另一个仓库 `https://github.com/jlakkis/sciPENN_codes`（`paper.md:334-337`, `MOESM2_ESM.md:34-40`）。这个仓库本次没有获取。因此，本 workspace 可以验证 sciPENN 方法实现，但不能验证论文所有 benchmark 脚本、figure 生成脚本和 totalVI/Seurat 4 wrapper。

另一个限制是，workspace-local CodeGraph 数据库存在但索引为 0 files / 0 nodes / 0 edges，所以代码证据全部来自直接源码阅读，而不是 CodeGraph 查询。

### 一句话总结

sciPENN 的方法核心是：用一个带 RNN hidden embedding、蛋白均值/分位数 head 和可选 label head 的神经网络，从 CITE-seq 中学习 RNA 到蛋白的映射；再通过 measured-protein mask 实现 censored loss，使多个蛋白面板不完全重叠的 CITE-seq 数据集可以联合训练，并进一步完成缺失蛋白补全、scRNA-seq 蛋白预测、不确定性估计和标签转移。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## sciPENN Summary

### Problem

sciPENN targets CITE-seq/scRNA-seq integration when researchers want protein-level information but only have RNA for some cells or have multiple CITE-seq references with partially overlapping antibody panels. CITE-seq is costly, and combining multiple CITE-seq datasets is complicated by batch effects and proteins that are measured in one dataset but absent in another (`paper.md:12-27`).

### Prior Method Limitations

The paper compares mainly with Seurat 4 (*Cell*, 2021) and totalVI (*Nature Methods*, 2021). The paper argues that Seurat 4 and totalVI can support protein prediction from a CITE-seq reference, but Seurat 4 is computationally expensive and cannot merge multiple CITE-seq datasets with non-overlapping panels; totalVI can in principle address the multi-panel problem, but the paper says this setting had not been explored and totalVI struggled in the authors' large COVID integration evaluation (`paper.md:24-27`, `paper.md:145-168`, `paper.md:349-350`).

### Proposed Method

sciPENN, single-cell imputation Protein Embedding Neural Network, is a deep learning framework that learns from one or more CITE-seq references to:

- predict protein expression for scRNA-seq query cells,
- impute missing proteins in CITE-seq references,
- estimate prediction/imputation uncertainty with quantile outputs,
- integrate CITE-seq and scRNA-seq cells in a shared embedding,
- optionally transfer cell-type labels from reference cells to query cells.

The key method idea is a neural network with an input block, feed-forward blocks, an RNN hidden state, protein mean and quantile heads, and an optional detached cell-type head (`paper.md:36-47`, `paper.md:237-280`). For partially overlapping CITE-seq panels, sciPENN uses a censored protein loss so unmeasured proteins do not contribute to training loss (`paper.md:304-313`).

### Method At A Glance

```text
Reference CITE-seq matrices + optional query scRNA-seq
        |
        v
QC, normalization, HVG selection, batch scaling
        |
        v
Merge protein union and zero-fill missing entries as placeholders
        |
        v
Train neural network with masked protein loss and optional label loss
        |
        +--> impute missing reference proteins
        +--> predict query proteins and quantile intervals
        +--> output embedding and optional transferred labels
```

The acquired package implements this core workflow in `sciPENN_API.py`, `Preprocessing.py`, `Network/Model.py`, `Network/Layers.py`, `Network/Losses.py`, and `Data_Infrastructure/` loaders/samplers.

### Evaluation

The paper evaluates sciPENN across multiple CITE-seq/scRNA-seq scenarios:

- PBMC reference to MALT query: sciPENN has the strongest or most consistent prediction performance and better prediction-interval coverage than totalVI (`paper.md:53-76`; Fig. 2).
- Monocyte train/test split: all methods correlate well, but sciPENN has lower RMSE and better interval coverage; random splits show small variation (`paper.md:79-99`, `paper.md:440-445`; Fig. 3, Extended Data Fig. 1).
- PBMC train/test and label transfer: sciPENN recovers marker protein trends and outperforms Seurat 4 for L3 and L2 cell-type label transfer (`paper.md:102-122`, `paper.md:448-453`; Fig. 4, Extended Data Fig. 2).
- PBMC reference to H1N1 query: sciPENN and totalVI have similar correlations, but sciPENN has lower RMSE and substantially better interval coverage (`paper.md:125-139`; Fig. 5).
- Haniffa/Sanger COVID CITE-seq integration: sciPENN mixes the two large datasets and outperforms totalVI for simulated missing-protein imputation (`paper.md:142-168`; Fig. 6).
- Runtime: sciPENN is visually much faster than totalVI and Seurat 4 in the runtime comparison (`paper.md:180`, `paper.md:464-469`; Extended Data Fig. 4).

### Code And Reproducibility

Mode: `paper+code`. The acquired code is `https://github.com/jlakkis/sciPENN` at commit `34afb2008a076e13c40965a76d3dd31d0c331652`. It is the installable sciPENN package and matches the core algorithm with **medium** overall paper-code fidelity.

Verified code matches include preprocessing thresholds/HVG selection, protein-panel merging, the input/FF/RNN architecture, detached label head, quantile outputs/loss, missing-protein imputation update, query prediction, and the measured-protein mask path. The censored-loss implementation is conceptually aligned but only **Partial** algebraically because code masks losses and then applies a tensor-wide `mean()`, so zeroed unmeasured proteins remain in the denominator (`doc_code.md`).

Important gap: the paper states that all analyses can be reproduced using a separate repository, `https://github.com/jlakkis/sciPENN_codes` (`paper.md:334-337`; `MOESM2_ESM.md:34-40`). That repository was not acquired here. Therefore this workspace verifies the algorithm package, not the exact benchmark scripts or figure-generation workflows. CodeGraph also indexed zero files for this workspace, so final code claims rely on direct source reads only.

### Reproducibility Rating

**3/5 for this workspace.** The core package is available and strongly maps to the method, but exact paper-figure reproduction requires the separate analysis-code repository and MOESM1 Supplementary Note 1 was not available in readable markdown here. The documented gaps are publishable because they are provenance limitations, not unsupported upgraded claims.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
