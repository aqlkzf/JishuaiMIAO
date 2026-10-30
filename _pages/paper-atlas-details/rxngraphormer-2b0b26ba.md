---
layout: default
permalink: /paper-atlas/rxngraphormer-2b0b26ba/
title: "RXNGraphormer"
nav: false
wide: true
description: "RXNGraphormer 先用图神经网络和 Transformer 把反应物、产物及其变化编码成可迁移表示，再分别接回归头或自回归序列解码器，从而把反应性能预测和合成规划连接到同一套预训练表示体系中。"
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
      <span>Computational Tools</span>
      <span>Nature Machine Intelligence · 2025</span>
    </div>
    <h1>RXNGraphormer</h1>
    <p>A unified pre-trained deep learning framework for cross-task reaction performance prediction and synthesis planning</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/licheng-xu-echo/RXNGraphormer" target="_blank" rel="noopener noreferrer" aria-label="Open code for RXNGraphormer">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## RXNGraphormer 方法详解

### 1. 这篇论文要解决什么问题？

有机反应机器学习通常分成两类任务：

- **反应性能预测**：输入反应，输出收率、反应活性或选择性等连续数值，本质上是回归问题。
- **合成规划**：输入反应物预测产物，或输入产物预测反应物，本质上是分子序列生成问题。

这两类任务的输出形式、损失函数和推理方式不同。论文摘要把这种差异称为数值回归与序列生成之间的方法学分歧，并提出一个核心问题：能否先学习通用的反应表示，再把它同时迁移到性能预测和合成规划？

RXNGraphormer 的回答是：用图神经网络学习分子内部的原子和键模式，用 Transformer 类注意力学习更大范围的反应上下文，再通过预训练把编码器迁移给不同任务的输出头。

### 2. 为什么已有方法不够？

论文参考文献反映了两条相对独立的技术路线。例如，Schwaller 等人在 *Machine Learning: Science and Technology*（2021）中研究深度学习反应收率预测；Tu 和 Coley 在 *Journal of Chemical Information and Modeling*（2022）中研究用于逆合成和反应预测的 permutation-invariant graph-to-sequence 模型。前者代表数值预测范式，后者代表序列生成范式。

这里不能把论文没有写出的批评强加给这些具体工作。能够从摘要直接确认的局限是：

1. 回归模型需要输出一个数值，序列模型需要逐 token 生成 SMILES。
2. 两者通常使用不同模型结构和训练目标，难以共享知识。
3. 单个反应数据集往往规模有限，性能任务尤其需要从大规模反应数据中迁移表示。
4. 模型不仅要识别分子内部官能团，还要理解反应物、产物以及它们变化之间的关系。

RXNGraphormer 的创新重点不只是“再做一个 GNN”或“再做一个 Transformer”，而是把预训练得到的反应图编码器迁移给回归和生成两种任务。

### 3. 总体框架

```text
大规模反应数据
    |
    | 真实反应 + 虚构反应
    v
反应分类预训练
    |
    +--> 反应物图编码器 ----+
    |                       +--> 真实/虚构二分类
    +--> 产物图编码器 ------+
    |
    +==================== 迁移预训练编码器 ====================+
    |                                                         |
    v                                                         v
反应性能预测                                               合成规划
反应物图 + 产物图 + 可选中间图                         输入侧分子图
    |                                                         |
    v                                                         v
分别编码并汇聚                                            图编码 + 注意力编码
    |                                                         |
    v                                                         v
[r, p, |r-p|] 与可选 z                                  Transformer 自回归解码
    |                                                         |
    v                                                         v
回归 MLP -> 收率/活性/选择性                             Top-k 产物或反应物 SMILES
```

代码中的统一入口是 `RXNGraphormer` 工厂，它根据 `classification`、`regression` 或 `sequence_generation` 返回不同模型（`model.py:1264-1364`）。因此，“统一”并不意味着所有任务使用完全相同的头和损失，而是共享图表示、注意力模块和预训练迁移机制。

### 4. 输入如何变成图？

每个反应侧的 SMILES 被转换成 PyTorch Geometric 图。主要字段包括：

- `x`：原子类别特征；
- `edge_index`：键连接关系；
- `edge_attr`：键特征；
- `mol_index`：每个原子属于哪一个分子；
- `y`：回归或分类标签；
- `tgt_token_ids`、`tgt_lens`：序列生成的目标 token 和长度。

序列任务由 `RXNG2SDataset` 读取配对的 source/target 文本，将 source 转成图、target 转成 token（`data.py:296-376`）。性能任务由 `RXNDataset` 或 `MultiRXNDataset` 处理，之后用 `PairDataset` 对齐反应物和产物，或用 `TripleDataset` 再加入第三个中间图（`data.py:381-464,488-622`）。

论文预览没有公开 1300 万条反应的完整清洗、去重、划分和负样本比例。因此，代码能证明“数据如何进入模型”，但不能证明本地配置完整复现了论文的数据构造。

### 5. 图编码器：学习分子内部结构

代码为每个原子定义九类离散特征嵌入，包括元素类型、度、形式电荷、杂化、手性、芳香性、价态、氢原子数和 R/S 信息（`model.py:352-386`）。设第 (i) 个原子的第 (k) 类特征为 (x_{i,k})，初始表示可以写成：

\[
h_i^{(0)}=\operatorname{Reduce}_k E_k(x_{i,k}),
\]

其中 `Reduce` 在代码中可以是求和或求平均。随后使用多层 GCN、GIN 或 GAT 做消息传递：

\[
h^{(l+1)}=\operatorname{GNN}_l(h^{(l)},\mathcal{E}).
\]

每层包含批归一化、激活和 dropout，最后可以选择 `last`、`concat`、`max`、`sum`、`mean` 等 jumping-knowledge 方式得到原子表示（`model.py:388-445`）。

一个重要的代码级复现风险是：图编码器显式调用 `F.dropout(..., training=True)`（`model.py:417-425`）。只要 `drop_ratio > 0`，即使外部执行了 `model.eval()`，这部分 dropout 仍可能保持开启，使推理结果具有随机性。这是直接代码行为，不是论文结论。

### 6. Transformer：学习反应上下文

图神经网络先得到原子表示，随后 `RXNGEncoder` 有两种上下文化方式（`model.py:447-527`）：

1. 用注意力池化把原子聚合成分子表示，再送入标准 Transformer encoder；
2. 把原子序列补齐到统一长度，使用带图距离/相对位置信息的注意力编码器。

这一步对应论文摘要中“GNN 识别分子内模式、Transformer 建模分子间相互作用”的描述。需要注意，完整论文方法不可访问，所以“分子间相互作用”的精确定义和理论解释无法从当前证据恢复；代码可以确认的是实际张量如何被池化、补齐并送入注意力层。

### 7. 预训练阶段

图 2 显示，预训练任务把真实反应和虚构反应送入反应分类器。代码中的 `SPLITClassifierTrainer` 分别加载反应物图和产物图，得到两个编码向量，再组合反应物、产物和绝对差向量进行二分类，使用平均交叉熵损失（`train.py:20-221`）。

若记反应物向量为 (r)、产物向量为 (p)，则核心变化向量为：

\[
d=|r-p|.
\]

分类器可以使用 (d)、([r;p]) 或 ([r;p;d])。当前预训练配置选择 `all`，即使用三者拼接；配置还给出 256 维嵌入、4 层 GCN、4 层 Transformer、2 个注意力头、AdamW、Noam 学习率调度和 20 个 epoch（`config/pretrain_parameters.json:1`）。

但是以下内容仍然是 **MISSING / Not found**：

- 论文中精确的虚构产物生成规则；
- 真实样本与虚构样本比例；
- 1300 万条反应的过滤和切分；
- 论文所有实验是否都使用当前 JSON 默认值；
- 补充材料中的完整预训练策略。

仓库存在候选函数 `gen_truth_false_rxn_smi` 和 notebook 调用，但由于论文方法正文不可访问，不能把它们标记为论文算法的 Exact 对应。

### 8. 下游任务一：反应性能预测

#### 8.1 基本双编码器路径

`RXNGRegressor` 分别编码反应物和产物，并对 Transformer 输出做均值汇聚，得到 (r) 和 (p)。之后构造：

\[
d=|r-p|,
\]

并根据 `split_merge_method` 选择：

\[
d, \quad [r;p], \quad [r;p;d].
\]

选中的向量进入多层线性回归头，输出一个标量（`model.py:215-243`）。四个可见回归配置使用 `rct_pdt`，也就是直接拼接 ([r;p])，同时启用可选中间信息。

#### 8.2 可选中间图分支

当 `use_mid_inf=True` 时，模型还接收第三个图 (z)。它可以通过全连接层、一维卷积或注意力与主反应向量融合，然后由 `mid_decoder` 输出结果（`model.py:170-213,245-283`）。公共预测 API 调用 `gen_mech_mid_smi` 生成该输入，并将反应物、产物和中间图组成 triple batch（`eval.py:299-340`）。

代码候选实现会进行原子映射、识别断裂/形成的键并生成机制相关中间结构（`midgen/midmol.py:110-165`）。但当前论文预览没有给出 delta-mol 的正式定义，因此只能说“代码实现了一个机制中间图分支”，不能说它与论文 delta-mol 算法完全一致。

#### 8.3 优化和评价

回归训练器支持 L1 或 L2/MSE，当前可见 benchmark 配置使用 L2。预训练编码器可使用缩放后的较小学习率，新加入的回归模块使用基础学习率；训练还包含梯度裁剪和学习率调度（`train.py:528-531,626-698`）。

评价指标是：

- (R^2)：预测解释目标方差的程度；
- MAE：预测值与真实值的平均绝对误差。

对于收率任务，评价代码可先把输出截断到 ([0,1])，再乘以 100（`eval.py:181-188`）。因此比较论文数值时必须确认是否启用了该后处理。

### 9. 下游任务二：正向合成和逆合成

`RXNG2Sequencer` 的主要模块是（`model.py:978-1045`）：

1. 原子图编码器；
2. 标准注意力或相对位置注意力编码器；
3. token embedding；
4. Transformer decoder；
5. 词表投影层。

训练时，目标序列右移并在开头加入 `_SOS`。模型逐位置预测 token，损失为忽略 `_PAD` 的交叉熵：

\[
\mathcal{L}_{seq}=-\sum_t \log p(t_t\mid t_{<t},G_{src}),
\]

并同时统计非 padding token 的准确率（`model.py:1104-1134`）。

推理时使用 greedy search 或 beam search，可配置 beam size、temperature、最短/最长长度和返回候选数（`model.py:1136-1246`）。`SeqEval` 把生成 token 还原成 SMILES，进行分子规范化，再计算累计 Top-k exact-match accuracy（`eval.py:51-91`）。这个指标回答“真实答案是否出现在前 k 个候选中”，但不直接衡量合成可行性、路线多样性或实验成功率。

预训练迁移方式也能从代码确认：逆合成使用预训练分类器的产物编码器初始化 source encoder，正向合成使用反应物编码器（`train.py:820-878`）。

### 10. 反应嵌入

`RXNEMB` 可加载预训练或微调模型，分别提取反应物和产物表示，并根据模型设置生成 ([r;p;d])、(d) 或 ([r;p]) 形式的反应嵌入（`rxn_emb.py:10-110`）。

图 3 展示 USPTO-50k 反应类型之间的距离矩阵和若干反应转化例子。矩阵出现明显块结构，支持论文“没有显式反应类型监督也能形成类型相关聚类”的结论。

这里的证据层级是：

- **论文图像证据**：存在类型相关距离结构；
- **代码证据**：可以生成反应嵌入并用于距离分析；
- **未验证部分**：本地没有所需权重和数据，未复现矩阵、类别顺序或数值。

### 11. 评价结果应如何理解？

论文摘要声称在 8 个 benchmark 和 3 个外部真实数据集上达到 state-of-the-art。当前可访问图像能够确认：

- 图 4 包含四个回归 benchmark 的预测-真实散点图和多模型比较；
- 图 5 包含三个外部验证设置；
- 多数散点围绕对角线分布，定性上支持预测与真实值一致。

仓库明确命名了四个回归数据集：Buchwald-Hartwig、Suzuki-Miyaura、C-H functionalization 和 asymmetric thiol addition；还包含 USPTO-50k、USPTO-480k、USPTO-full 和 USPTO-stereo 等序列任务配置。

但完整结果表、baseline 定义、数据划分、误差条和统计检验均不在订阅预览中。因此，不能从低分辨率图像抄写或猜测精确数值，也没有在本地独立验证 state-of-the-art 排名。

### 12. 论文与代码的对应程度

总体评价为 **medium**：

- **Exact**：统一任务工厂、原子图编码器、Transformer 上下文化、双编码器回归、图到序列生成、评价代码。
- **Partial**：分类预训练基础设施、反应嵌入生成与论文聚类结果之间的对应。
- **Notebook**：虚构反应、delta-mol、回归结果和嵌入距离的演示存在于 notebook，但不能替代论文方法证据。
- **Not found / MISSING**：精确预训练策略、论文版虚构反应构造、论文版 delta-mol 定义，以及完整 benchmark 数值与统计流程。

### 13. 复现边界

当前仓库快照有源代码、配置、命令行入口和 notebook，但 `dataset/` 与 `model_path/` 只包含下载说明。要完整复现仍需要：

1. 从外部归档下载数据和模型权重；
2. 固定 PyTorch、PyTorch Geometric、RDKit、OpenNMT 相关组件和反应映射依赖；
3. 获得完整论文和补充方法；
4. 明确虚构反应、delta-mol 和 1300 万反应预训练数据的精确构造；
5. 检查并处理强制开启 dropout 带来的推理随机性。

### 14. 可进一步检验的假设

以下是根据代码提出的后续实验假设，不是论文声称的结果：

- 关闭强制 dropout 后，序列任务的重复推理稳定性可能提高。
- 分别消融 (d=|r-p|)、中间向量 (z) 和预训练迁移，可以量化三者对不同回归数据集的贡献。
- 比较预训练前后、微调前后的反应嵌入，可能揭示“反应类型结构”与“性能结构”之间如何变化。

### 15. 一句话理解

RXNGraphormer 先用图神经网络和 Transformer 把反应物、产物及其变化编码成可迁移表示，再分别接回归头或自回归序列解码器，从而把反应性能预测和合成规划连接到同一套预训练表示体系中。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## RXNGraphormer

### Problem

Reaction-performance prediction and synthesis planning are commonly treated as different machine-learning problems. Performance prediction produces numerical values such as yield, reactivity, or selectivity, whereas forward synthesis and retrosynthesis generate molecular sequences. The paper argues that this regression-versus-generation divide makes it difficult to build one representation that transfers across both task families.

### Proposed Approach

RXNGraphormer is a pre-trained reaction framework that combines graph neural networks for atom/bond and intramolecular structure with Transformer-style attention for broader reaction context. A reaction classifier is pre-trained on real and fictitious reaction pairs, after which its graph encoders are transferred to:

- a regression branch for reaction performance;
- a graph-to-sequence branch for forward synthesis or retrosynthesis;
- an embedding interface for reaction-space analysis.

The direct implementation shows that “unified” means shared representation components and transfer, not one identical output head. Regression separately encodes reactants and products, merges their pooled vectors and absolute difference, optionally incorporates a third intermediate/delta-mol graph, and predicts a scalar. Synthesis planning encodes the source-side molecular graph and autoregressively decodes target SMILES with a Transformer decoder.

### What the Paper Shows

The abstract reports training on 13 million reactions and state-of-the-art performance across eight benchmark datasets plus three external realistic datasets. The five accessible figures provide qualitative support:

- Figs. 1-2 show the shared pre-training and downstream regression/sequence architecture.
- Fig. 3 shows block structure in USPTO-50k reaction-embedding distances, supporting reaction-type-related organization without explicit type labels.
- Fig. 4 shows predicted-versus-true agreement across four regression benchmark families and comparisons with multiple alternatives.
- Fig. 5 shows three external validation settings.

The full methods, result tables, complete legends, and supplementary text are not included in the acquired subscription preview. Therefore, exact baseline definitions, numerical improvements, split protocols, and statistical comparisons are **Not found** and are not reconstructed from the low-resolution figures.

### Code-Grounded Method

The repository implements a common `RXNGraphormer` factory for classification, regression, and sequence generation. Atom features are embedded and processed by configurable GCN/GIN/GAT layers; pooled or padded states then pass through Transformer or relative-position attention layers. The main objectives and metrics are:

- binary cross-entropy-style two-class training through `CrossEntropyLoss` for pre-training classification;
- L1 or MSE regression loss, with R2 and MAE evaluation;
- padding-masked token cross-entropy for sequence training;
- canonicalized top-k exact-match accuracy for synthesis generation.

Pre-trained reactant/product encoders are transplanted into the regression model. For sequence tasks, the product encoder initializes retrosynthesis and the reactant encoder initializes forward prediction. The repository also provides checkpoint-loading APIs, reaction embedding extraction, public prediction functions, configurations, and a demonstration notebook.

### Evaluation Coverage

The repository names four regression datasets: Buchwald-Hartwig, Suzuki-Miyaura, C-H functionalization, and asymmetric thiol addition. It also includes USPTO-50k sequence training configuration and evaluation configurations for USPTO-480k, USPTO-full, and USPTO-stereo. These artifacts are consistent with the task scope shown in the paper, but the exact composition of all eight claimed benchmarks cannot be verified from the preview alone.

No benchmark was rerun in this workspace. The checked-in `dataset/` and `model_path/` directories contain download instructions; the required datasets and trained checkpoints are hosted externally.

### Code-Paper Match and Reproducibility

**Code-paper fidelity: medium.** The released source directly matches the visible high-level architecture, downstream task branches, transfer mechanism, losses, and evaluation APIs. The match cannot be rated high because the paper's detailed methods are unavailable and three central procedures remain unverified as published-method matches:

- the exact 13-million-reaction pre-training recipe;
- the exact fictitious-product/reaction generation procedure;
- the exact delta-mol graph definition and construction.

Candidate implementations and notebook calls exist for fictitious reactions and mechanism-derived intermediate graphs, but the inaccessible paper method prevents an Exact correspondence claim.

**Reproducibility rating: 3/5.** Source code, configurations, CLI entry points, and asset locations are available, but data/weights are external, dependency/runtime reproduction was not performed, and critical method details are absent from the acquired source. A further code-level caveat is that graph-layer dropout is called with `training=True`, so non-zero-dropout configurations may remain stochastic during evaluation.

### Bottom Line

RXNGraphormer's main contribution is a transferable graph-plus-Transformer reaction representation that supports both scalar performance prediction and molecular sequence generation. The visible figures and direct code strongly support that architectural contribution. The advertised scale and benchmark superiority remain paper claims rather than independently verified results in this workspace because the full article, supplement, data, and weights were not locally available.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
