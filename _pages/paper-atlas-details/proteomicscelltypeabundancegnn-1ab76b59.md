---
layout: default
permalink: /paper-atlas/proteomicscelltypeabundancegnn-1ab76b59/
title: "ProteomicsCellTypeAbundanceGNN"
nav: false
description: "这篇论文研究的是蛋白组数据中的细胞类型比例反卷积。 bulk proteomics 和 spatial proteomics 测到的是多个细胞混在一起后的蛋白丰度信号，因此研究者希望从一个混合样本中估计不同细胞类型的比例。论文指出，许多已有反卷积方法主要为转录组设计，常依赖转录本计数分布或高维基因表达特性，这些假设不适合连续强度值、维度更低且噪声/批次效应更明显的蛋白组数据。"
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
      <span>Deconvolution</span>
      <span>Advanced Science · 2025</span>
    </div>
    <h1>ProteomicsCellTypeAbundanceGNN</h1>
    <p>Deciphering Cell Type Abundance in Proteomics Data Through Graph Neural Networks</p>
    <a class="paper-detail__doi" href="https://doi.org/10.1002/advs.202502987" target="_blank" rel="noopener noreferrer">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GraphDEC 方法中文讲解

### 这篇论文要解决什么问题？

这篇论文研究的是蛋白组数据中的细胞类型比例反卷积。 bulk proteomics 和 spatial proteomics 测到的是多个细胞混在一起后的蛋白丰度信号，因此研究者希望从一个混合样本中估计不同细胞类型的比例。论文指出，许多已有反卷积方法主要为转录组设计，常依赖转录本计数分布或高维基因表达特性，这些假设不适合连续强度值、维度更低且噪声/批次效应更明显的蛋白组数据（`paper.md:38-46`, `paper.md:133-137`）。

论文也把 scpDeconv 作为已有蛋白组反卷积方法讨论：scpDeconv 使用自编码器和 domain adaptation，但论文认为它主要从单个样本中提取共享信息，没有建模样本之间的高阶拓扑关系。因此 GraphDEC 的核心动机是：不要把每个混合样本孤立预测，而是把样本放到相似性图上，用图神经网络传播邻域信息（`paper.md:44-46`, `paper.md:129-131`）。

### GraphDEC 的核心想法

GraphDEC 是一个基于图神经网络的细胞类型比例预测框架。它先用带标签的单细胞蛋白组数据构造伪 bulk 参考样本，再用自编码器把参考样本和目标样本投影到低维空间，基于低维表示计算样本之间的余弦相似性并构图。随后，GraphDEC 用多通道 GraphSAGE 风格 GNN 学习图上的样本表示，并同时优化三个目标：比例预测 MSE loss、triplet loss 和 domain adaptation loss。推理时，它先得到目标样本的初始比例预测，再用预测比例重新加权目标图边，最后做一次 refined prediction（`paper.md:50-65`, `paper.md:141-145`, `paper.md:179-271`）。

可以把整个流程理解成：

```text
带细胞类型标签的单细胞蛋白组数据
        |
        v
1. Mixup 构造伪 bulk reference / target
        |
        v
2. Autoencoder 学习低维表示 Z
        |
        v
3. 余弦相似性构造 reference / target / joint 三张图
        |
        v
4. 根据标签同质性对 reference 图边加权
        |
        v
5. 多通道 GraphSAGE/GNN 学习样本表示
        |
        +--> deconvolution head 预测细胞比例
        +--> triplet loss 拉近相似样本、推远不相似样本
        +--> domain discriminator 缓解 reference/target 批次差异
        |
        v
6. 初始预测目标样本比例
        |
        v
7. 用预测比例重新加权 target 图，再输出最终比例
```

本地读取的 Figure 1 图像也展示了这个流程：a/b 面板对应 mixup、AE 和图构建，c 面板对应三张图进入两层 GNN，并连接 triplet/deconvolution/domain adaptation 分支，d/e 面板对应 first-round prediction 和 refined prediction（`figure_analysis.md`；图注在 `paper.md:54-56`）。

### 第一步：构造伪 bulk 参考样本

GraphDEC 从带有真实细胞类型标签的单细胞蛋白组数据出发，随机抽取不同细胞类型的单细胞并混合成伪 bulk 样本。每个伪样本的细胞类型比例由被抽中细胞的类型计数决定，蛋白丰度则由这些细胞的蛋白表达聚合得到。论文记号为：

- $X^{r} \in \mathbb{R}^{N_{r} \times p}$：reference 伪 bulk 数据；
- $X^{t} \in \mathbb{R}^{N_{t} \times p}$：target 伪 bulk 或真实目标数据；
- $Y^{r} \in \mathbb{R}^{N_{r} \times n}$：reference 样本的真实细胞类型比例标签；
- $p$ 是蛋白数量，$n$ 是细胞类型数量（`paper.md:143-145`）。

这个步骤的意义是为监督训练提供带标签的 reference 样本。论文在多个 benchmark 中都使用这种 reference-target 构造策略，例如从一个或多个单细胞蛋白组数据集生成 reference，再用同一 case 中剩余数据生成 target（`paper.md:69-80`, `paper.md:303-317`）。

### 第二步：自编码器投影到低维空间

GraphDEC 用 autoencoder 把 reference 和 target 蛋白丰度矩阵投影到共同低维空间。编码器第 $l$ 层为：

$$H^{(l)} = \phi\left( {W_{e}^{(l)}H^{(l - 1)} + b_{e}^{(l)}} \right),$$

其中 $\phi$ 是 ReLU，$H^{(0)}$ 初始化为 $X^r$ 或 $X^t$。编码器最后一层输出低维表示 $Z$。解码器再从低维表示重构输入：

$$H^{(m)} = \phi\left( {W_{d}^{(m)}H^{(m - 1)} + b_{d}^{(m)}} \right).$$

重构 loss 为：

$$L_{ae} = \frac{1}{c^{t}}\sum\limits_{i = 1}^{c^{t}}\sum\limits_{j = 1}^{p}\left( {X_{ij}^{t} - {\overset{\sim}{X}}_{ij}^{t}} \right)^{2}.$$

论文实现细节中写到 AE 结构为 `[input-16-input]`，Adam 学习率为 0.001（`paper.md:147-159`, `paper.md:269-271`）。

### 第三步：基于低维表示构图

AE 得到低维表示后，GraphDEC 用余弦相似性衡量样本之间的关系。reference 样本 $s_i$ 和 $s_j$ 的相似性为：

$$s_{(ij)}^{r} = \frac{Z_{:,i}^{r} \cdot Z_{:,j}^{r}}{\parallel Z_{:,i}^{r} \parallel_{2}{\parallel Z_{:,j}^{r} \parallel}_{2}}.$$

论文构造三类相似性矩阵和图：

- $S_r$ / reference graph：reference 样本内部关系；
- $S_t$ / target graph：target 样本内部关系；
- $S_{r+t}$ / joint graph：reference 和 target 拼接后的跨域关系（`paper.md:161-169`）。

图结构写作：

$$G = \left( {V,E} \right),$$

其中 $V = V_r \cup V_t$，边集合为：

$$E = E_{r} \cup E_{t} \cup E_{j}.$$

三类图在训练中分别进入 GNN，以学习不同视角下的样本表示（`paper.md:181-193`）。

### 第四步：根据标签同质性重新加权边

reference 样本有真实比例标签，因此 GraphDEC 用标签相似性来调整 reference 图边权。边 $(i,j)$ 的标签同质性为：

$$w_{i,j} = \frac{z_{i}^{label} \cdot z_{j}^{label}}{\parallel z_{i}^{label} \parallel_{2}{\parallel z_{j}^{label} \parallel}_{2}}.$$

如果 $w_{i,j} > 0.5$，边权设为 $1.5 \times s_{(ij)}^r$；否则设为 $0.8 \times s_{(ij)}^r$。论文称这个模块是无需训练的 heuristic，用来增强 GNN 校准能力（`paper.md:171-177`）。

在推理阶段，GraphDEC 还会先预测目标样本比例，再用这些预测比例重新加权 target 图，最后再预测一次得到最终比例（`paper.md:63-65`, `paper.md:269-271`）。

### 第五步：多通道 GraphSAGE/GNN

GraphDEC 使用 GraphSAGE 作为消息传递骨干。第 $k$ 层中，节点 $v$ 的邻居聚合为：

$$h_{N(v)}^{(k)} = \frac{1}{|N_{k}&#123;&#123;(v)}|}}\sum\limits_{u \in N_{k}{(v)}}h_{u}^{(k - 1)},$$

然后把上一层自己的表示和邻居聚合表示拼接后更新：

$$h_{v}^{(k)} = \sigma\left( {W_{k} \cdot \text{concat}\left( {h_{v}^{(k - 1)},h_{N(v)}^{(k)}} \right)} \right).$$

这一步让样本表示不只依赖自身蛋白丰度，还能吸收相似样本的邻域信息（`paper.md:195-203`）。

GraphDEC 还融合不同 GNN 层的表示：

$$M_{v} = \sum\limits_{l = 1}^{L}s_{v}^{l} \times h_{v}^{l},$$

论文设置 $L=2$。同时，它使用多通道架构，每个通道是一个独立初始化的 GraphSAGE 模型，最后把不同通道输出拼接：

$$Z_{GNN} = {\lbrack M_{v}^{1},M_{v}^{2},\text{…},M_{v}^{C}\rbrack}.$$

这样做的目的，是让不同通道从同一张图中学习互补的结构视角（`paper.md:205-215`）。

### 第六步：三个训练目标

#### 1. 细胞比例预测 MSE loss

GNN 表示 $z_{GNN}^{i}$ 输入 MLP deconvolution head，并经过 Softmax 得到比例向量：

$$p_{i} = {Softmax}\left( &#123;&#123;MLP}\left( z_{GNN}^{i} \right)} \right).$$

预测 loss 为：

$$L_{dec} = {||}Y^{r} - p_{i}{||}_{2}^{2}.$$

它监督模型从 reference 样本的 GNN 表示预测真实细胞类型比例（`paper.md:221-233`）。

#### 2. Triplet loss

GraphDEC 为每个 anchor 样本选择最相似样本作为 positive，最不相似样本作为 negative，让 anchor 靠近 positive、远离 negative：

$$\begin{matrix}
{L_{tri} = \sum\limits_{i = 1}^{r + t}\max\left( {\frac{z_{i,:}^{r + t} \cdot z_{neg_{i},:}^{r + t}}{|z_{i,:}^{r + t}{||}z_{neg_{i},:}^{r + t}|} - \frac{z_{i,:}^{r + t} \cdot z_{pos_{i},:}^{r + t}}{|z_{i,:}^{r + t}{||}z_{pos_{i},:}^{r + t}|} + m,0} \right)/{(r + t)}}
\end{matrix}$$

论文设置 margin $m=0.3$（`paper.md:235-243`, `paper.md:269-271`）。

#### 3. Domain adaptation loss

为了缓解 reference 和 target 的批次差异，GraphDEC 将 GNN 表示送入两层 domain discriminator：

$$\begin{matrix}
{d^{r} = {Dom}{(z_{GNN}^{r})}}
\end{matrix}$$

$$\begin{matrix}
{d^{t} = {Dom}{(z_{GNN}^{t})}}
\end{matrix}$$

domain loss 为：

$$\begin{matrix}
{L_{dom} = \log{(1 - d_{GNN}^{t})} + \log{(d_{GNN}^{r})}}
\end{matrix}$$

最终训练目标是：

$$L = L_{dec} + \alpha \cdot L_{tri} + \beta \cdot L_{dom}.$$

论文给出的权重为 $\alpha=0.01$，$\beta=1$（`paper.md:245-271`）。

### 训练与推理

论文实现细节描述每个 epoch 包含两步：第一步把 reference/target 数据和 reference/target 图输入 GraphDEC，计算 triplet、MSE、domain adaptation 三类 loss；第二步把 reference/target 数据和 joint graph 输入模型，只计算 triplet loss 和训练集预测 loss。训练总共 3000 iterations，至少训练 1500 iterations，验证指标 100 次不提升则 early stopping（`paper.md:269-271`）。

推理阶段先用 target data + target graph 得到初始比例预测，再用初始预测重新加权 target graph，最后再次通过 GraphDEC 得到最终细胞比例（`paper.md:269-271`）。

### 实验结果如何支持方法？

在七个蛋白组 reference-target benchmark 中，论文报告 GraphDEC 平均 CCC 为 80.7%，比第二名 CellDART 高 15 个百分点，RMSE 为 0.029，优于 Tangram 的 0.056（`paper.md:69-82`）。本地查看 Figure 2 可见 GraphDEC 在 CCC/RMSE boxplot 中整体领先，Murine_cellline 的混淆矩阵和散点图也显示较强对角线趋势，消融图显示去掉 GNN 的性能下降最明显（`figure_analysis.md`）。

在跨物种蛋白组数据中，论文报告 GraphDEC 平均 CCC 为 93%，比 Tangram 高 26.4 个百分点。Figure 3 显示不同物种/数据集在 UMAP 上明显分离，同时 GraphDEC 的预测散点比 Tangram 更贴近对角线，支持其跨批次/跨物种任务上的优势（`paper.md:84-95`; `figure_analysis.md`）。

在转录组数据中，GraphDEC 不依赖 Poisson 或 Negative Binomial 等分布假设，论文报告平均 CCC 为 79.6%，比 Cell2location 高 15 个百分点（`paper.md:97-110`）。在真实 spatial proteomics 中，论文报告 GraphDEC 在 tonsil 和 PDAC 数据上分别达到 21% 和 39.7% 平均 CCC，虽然绝对值低于模拟数据，但仍优于基线（`paper.md:112-125`）。

### 代码可复现性需要特别注意

当前检查到的代码目录是 `scpDeconv`，不是 GraphDEC 的完整实现。它包含与论文部分概念相关的 baseline 代码：伪 bulk mixup、自编码器式重构、DANN/domain adaptation 预测头、CCC/RMSE/PCC 评估函数。但直接源码检查没有找到 GraphDEC 的核心图构建、边重加权、GraphSAGE/多通道 GNN、triplet loss 或 target graph refinement 代码（`doc_code.md`）。

因此，阅读这篇论文时应把方法理解为 paper-described GraphDEC；阅读代码时应把当前仓库视为 scpDeconv baseline/data-availability evidence。不能把这个 `scpDeconv` 仓库当作 GraphDEC 完整实现来引用。

### 局限性

GraphDEC 依赖合适的单细胞蛋白组 reference。如果目标数据包含 reference 中没有覆盖的细胞类型，或真实空间样本的比例组合远超 reference 多样性，预测精度会受限。论文也承认真实 spatial proteomics 的 CCC 低于模拟和跨物种任务，并把原因归结为 reference 多样性不足和真实空间组成更复杂（`paper.md:125-137`）。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## Summary

### Paper

**Deciphering Cell Type Abundance in Proteomics Data Through Graph Neural Networks** introduces **GraphDEC**, a graph neural network method for estimating cell-type proportions from bulk and spatial proteomics data. The paper was published in *Advanced Science* in 2025 (DOI: `10.1002/advs.202502987`; `paper.md:23-30`).

### Problem

Bulk and spatial proteomics measure mixed signals from multiple cells, so they obscure cell-type composition. Transcriptomics deconvolution methods often rely on assumptions or input distributions that do not fit proteomic intensity data, and the proteomics-specific baseline scpDeconv is described as modeling individual samples while missing higher-order relationships among samples (`paper.md:38-46`).

### Proposed Method

GraphDEC uses annotated single-cell proteomics as a reference, constructs pseudo-bulk reference samples with known cell-type ratios, projects reference and target samples into latent space with an autoencoder, builds reference/target/joint sample-similarity graphs, and trains a multi-channel GraphSAGE-style GNN. The model combines a deconvolution MSE loss, triplet loss, and domain adaptation loss, then uses a first target prediction to re-weight target graph edges before a refined final prediction (`paper.md:50-65`, `paper.md:143-177`, `paper.md:179-271`).

### Results

The paper reports that GraphDEC outperformed broad transcriptomics and proteomics baselines across seven proteomics reference-target datasets, achieving average CCC 80.7% and RMSE 0.029 (`paper.md:69-82`). It also reports strong cross-species performance with average CCC 93% across eight datasets (`paper.md:84-95`), transcriptomics generalization with average CCC 79.6% (`paper.md:97-110`), and leading but lower absolute performance on real spatial proteomics data: 21% average CCC on human palatine tonsil and 39.7% on mouse PDAC (`paper.md:112-125`). Local figure reads support the architecture, benchmark, ablation, cross-species, transcriptomics, and spatial result patterns (`figure_analysis.md`).

### Reproducibility And Code Match

The checked code directory is `scpDeconv`, not a verified GraphDEC implementation. It contains pseudo-bulk mixup, autoencoder-style reconstruction, a DANN-style domain adaptation predictor, and CCC/RMSE/PCC helpers, but direct source reads found no GraphDEC graph construction, edge re-weighting, GraphSAGE/multi-channel GNN, triplet loss, or two-pass target graph refinement (`doc_code.md`). Overall code-paper fidelity for GraphDEC implementation is **low**; the repository should be cited as baseline/reference/data-availability evidence only.

### Practical Limitations

The method depends on relevant single-cell proteomic references and may lose accuracy when target cell types or spatial mixtures are poorly represented in the reference. The paper also reports that real spatial proteomics CCC values are lower than synthetic pseudo-bulk and cross-species settings, likely because real spatial composition is more complex and reference diversity is limited (`paper.md:125-137`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
