---
layout: default
permalink: /paper-atlas/bmfm-rna-28bc8724/
title: "BMFM_RNA"
nav: false
wide: true
description: "单细胞转录组基础模型通常用掩码语言模型（MLM）预训练：遮住一部分基因，再让模型根据其余基因恢复被遮住的值。这个任务的损失可以很低，但它并不保证模型把“整颗细胞的状态”压缩进一个细胞级向量。模型可能只需利用局部基因相关性，就能预测某个被遮住的基因，而下游任务真正使用的 CLS 向量仍然很弱。"
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
      <span>Representation Models</span>
      <span>arXiv · 2025</span>
    </div>
    <h1>BMFM_RNA</h1>
    <p>BMFM-RNA: whole-cell expression decoding improves transcriptomic foundation models</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/BiomedSciAI/biomed-multi-omic" target="_blank" rel="noopener noreferrer" aria-label="Open code for BMFM_RNA">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## BMFM-RNA 方法详解

### 1. 这篇论文真正要解决什么问题？

单细胞转录组基础模型通常用掩码语言模型（MLM）预训练：遮住一部分基因，再让模型根据其余基因恢复被遮住的值。这个任务的损失可以很低，但它并不保证模型把“整颗细胞的状态”压缩进一个细胞级向量。模型可能只需利用局部基因相关性，就能预测某个被遮住的基因，而下游任务真正使用的 CLS 向量仍然很弱（`paper.md:14,40-49`）。

BMFM-RNA 的核心问题因此不是“怎样把重构误差降到最低”，而是：

> 怎样设计预训练任务，迫使一个低维细胞向量保留尽可能完整、可迁移的生物学信息？

论文给出两条互补路线：

1. **WCED（whole-cell expression decoding）**：只从 CLS 向量恢复整个基因词表的表达状态。
2. **HCE（hierarchical cross-entropy）**：利用 Cell Ontology 的层级关系，把粗粒度和细粒度细胞类型标签统一成一个叶节点概率模型。

### 2. 为什么已有方法不够？

以 scBERT（*Nature Machine Intelligence*, 2022）、Geneformer（*Nature*, 2023）、scGPT（*Nature Methods*, 2024）和 scFoundation（*Nature Methods*, 2024）为代表的转录组基础模型证明了大规模预训练的价值，但 MLM 目标本身允许一种“捷径”：每个被遮住的值都可以从大量上下文 token 中恢复，不必依赖全局细胞向量（`paper.md:14,49,1107-1110`）。

论文还指出两个更具体的问题：

- **零表达问题**：在 CELLxGENE 中，一颗细胞的非零基因中位数约为 1,700，而词表超过 60,000。把所有零都放进输入会造成极长序列；完全丢弃零又会损失“稳定沉默”这种细胞身份信息（`paper.md:22`）。
- **标签粒度不一致**：同类细胞在不同研究中可能标成“T cell”或更细的“CD8-positive, alpha-beta thymocyte”。平坦交叉熵把它们当互斥类别，忽略了祖先-后代关系（`paper.md:28`）。

scCello（NeurIPS 2024）通过对比学习引入本体结构；scPRINT 使用叶节点独立 sigmoid 和非归一化聚合。BMFM-RNA 选择不同方案：对所有叶节点做一次 softmax，再把后代叶节点的概率质量相加，使不同层级的节点处在同一概率尺度上（`paper.md:28,237-240,1116`）。

### 3. 整体计算流程

```text
单细胞基因计数 + 元数据
          |
          v
质控、log1p 归一化、基因选择、零/非零采样
          |
          v
多字段输入：基因身份 + 表达值 + 可选基因/细胞状态
          |
          v
双向 LLaMA 风格编码器
          |
          +-----------------------------+
          |                             |
          v                             v
第 0 个 token / CLS 向量             token 或 pooled 表征
          |                             |
          v                             v
WCED 全词表解码器                   细胞类型/组织/供体等分类头
          |                             |
          +-- 是否表达：BCE              +-- Cell Ontology 叶节点 logits
          +-- 非零表达量：MSE             +-- 后代叶掩码上的 HCE
          |                             |
          +-------------+---------------+
                        v
                  归一化加权多任务损失
```

最终模型使用 12 层、隐藏维度 384 的双向 LLaMA 变体；训练数据是约 620 万颗 CELLxGENE 细胞和 19,362 个蛋白编码基因（`paper.md:253-265,286-321`）。

### 4. 输入表示：怎样保留连续表达值和零？

对细胞-基因矩阵 $M\in\mathbb{R}^{N\times G}$，每个输入至少包含基因身份和表达值，也可以加入扰动状态、组织、疾病等字段（`paper.md:897-900`）。

论文支持 MLP 和周期激活两种连续值编码，最终预训练 checkpoint 使用周期编码：

$$
v_i=2\pi c_i x_i,
\qquad
f_i(x_i)=\operatorname{concat}[\sin(v_i),\cos(v_i)],
$$

然后再投影：

$$
f_{i,\mathrm{final}}
=W_2\,\phi(W_1f_i(x_i)+b_1)+b_2.
$$

零表达使用专门 token。关键不是把全部零塞进输入，而是让 WCED 在输出侧仍然监督整个词表。也就是说，**输入长度可以受控，但训练目标仍覆盖输入基因和非输入基因**（`paper.md:903-943`）。

### 5. WCED：把 CLS 变成信息瓶颈

#### 5.1 任务定义

设编码器只看到细胞表达谱的一部分，输出 CLS 表征 $h_{\mathrm{CLS}}$。WCED 的浅层解码器从这个单一向量预测所有基因的两类输出：

- $a_g$：基因 $g$ 是否表达的 logit，用二元交叉熵；
- $\hat{x}_g$：基因 $g$ 非零时的归一化表达值，用均方误差。

这与 MLM 的差异在于：MLM 可利用每个 token 的局部上下文；WCED 则要求一个向量承担全词表恢复任务。因此，若组织、细胞类型、状态或技术因素对全局表达模式有帮助，它们就更有动力被写入 $h_{\mathrm{CLS}}$。

#### 5.2 代码中实际发生什么？

直接源码支持如下链路：

1. `SCBaseFieldDecoder` 根据配置建立 `<field>_wced` 解码器，并把输出宽度设成目标字段的词表大小（`models/predictive/layers.py:542-597`）。
2. `WCEDFieldSource` 固定读取 `<field>_wced`，可先选择检测或定量输出通道，再固定选择 token 0（`training/losses/sources.py:174-244`）。
3. 它按 `label_set` 选择相应的全词表或子集标签（`training/losses/sources.py:246-255`）。
4. MSE 和 is-zero BCE 是独立 objective（`training/losses/objectives.py:131-220,371-418`）。

因此，“从第 0 个 token/CLS 做全词表监督”是代码可验证行为，不只是论文示意图。

#### 5.3 一个容易误解的结果

在严格匹配的 1% 数据实验中，MLM 的重标定 MAE 约为 0.65，WCED 约为 0.90；但 WCED 的下游 F1、Avg Bio、Avg Batch 分别高 0.128、0.149、0.064（`paper.md:43-49`）。

这说明：

- 更好的局部重构器不一定产生更好的全局表征；
- 预训练损失和下游表征质量可能方向相反；
- WCED 的价值在于改变信息必须流经的位置，而不只是改变损失函数名字。

这是作者提出并由消融实验支持的机制解释，不是数学定理。

### 6. HCE：让不同粒度标签共享一个概率空间

#### 6.1 只预测叶节点

把 Cell Ontology 表示成有向无环图 $\mathcal{G}=(\mathcal{V},E)$，叶节点集合为 $\mathcal{L}$。模型只输出叶节点 logits：

$$
\mathbf{z}\in\mathbb{R}^{|\mathcal{L}|},
\qquad
s_i=\operatorname{softmax}(\mathbf{z})_i.
$$

任意内部节点 $v$ 的概率是其所有后代叶节点的概率和：

$$
p(v)=\sum_{i\in\mathcal{D}(v)\cap\mathcal{L}}s_i.
$$

于是，一个粗标签无需被强行映射到某个具体叶节点。它监督的是整个后代子树的概率质量。

#### 6.2 HCE 推导

若真实标签为 $l$，定义二元掩码 $\mathbf{w}\in\{0,1\}^K$：当叶节点 $i$ 是 $l$ 的后代时 $w_i=1$。则

$$
p(l)=\frac{\sum_{i=1}^{K}w_i e^{z_i}}
{\sum_{j=1}^{K}e^{z_j}},
$$

$$
\mathcal{L}_{\mathrm{HCE}}
=-\log p(l)
=-\log\left(\sum_iw_ie^{z_i}\right)
+\log\left(\sum_je^{z_j}\right).
$$

如果标签未知或无法映射，本样本的掩码为空，损失贡献设为零（`paper.md:213-234`）。

#### 6.3 代码是否真的实现了论文公式？

是，核心数值实现可以直接对应公式：

- `weighted_logsumexp` 计算带后代掩码的稳定 log-sum-exp；
- `hce_loss` 用“掩码 log-sum-exp - 全体 log-sum-exp”，取负均值；
- 标签最后一维是有效标志，空标签先临时替换以避免 `log(0)`，再把样本贡献乘零；
- `HCEObjective.compute` 通过 `classification_loss(..., "hce", ...)` 调用该实现。

源码位置是 `training/metrics/metric_functions.py:172-219,266-280` 和 `training/losses/objectives.py:545-619`。这是与论文 Eqs. 1-3 的直接实现匹配。

Cell Ontology 侧，`LabelOntology.get_label_dictionary()` 对叶节点排序并建立列索引；`find_leaves()` 返回某节点可达的所有叶节点（`datasets/label_ontology/ontology.py:61-96`）。

#### 6.4 推理方式

论文支持两种读法：

1. **全局叶节点 argmax**：选择概率最大的叶节点，并报告它的祖先链；
2. **贪心层级解码**：从根开始，每一步选择概率质量最大的子节点。

$$
v_{t+1}=\arg\max_{u\in\operatorname{children}(v_t)}p(u).
$$

论文默认使用第一种。代码中直接验证了叶节点 argmax 和后代掩码；完整的根到叶贪心遍历在本次限定搜索中 **Not found**（`paper.md:243-250`）。

### 7. 多任务损失怎样合并？

每个 `LossTask` 把一个数据源和一个 objective 绑定起来。若活跃任务集合为 $\mathcal{A}$，代码计算：

$$
L=\frac{\sum_{t\in\mathcal{A}}\alpha_tL_t}
{\sum_{t\in\mathcal{A}}\alpha_t}.
$$

返回 `None` 或 NaN 的任务被跳过（`training/losses/task.py:74-152`; `training/losses/utils.py:76-105`）。这意味着论文表中的权重是活跃任务间的相对权重，而不是简单未归一化加和系数。

论文报告两种 multitask checkpoint 都使用 HCE 权重 1.0，并同时训练表达、组织、组织大类和供体任务（`paper.md:286-321`）。WCED 模型先用重构任务 warm-up，再加入 HCE；MLM multitask 直接训练 8 个 epoch（`paper.md:268-277`）。

### 8. 结果应该怎样理解？

#### 8.1 HCE 为什么能“补救”MLM？

没有 HCE 时，WCED F1 为 0.877，MLM 为 0.742。加入 HCE 后，MLM 的 F1 增加 0.129、Avg Bio 增加 0.222，基本追平 WCED；WCED 的 F1 几乎不变，但 Avg Batch 增加 0.083（`paper.md:90-96`）。

合理解释是：WCED 通过架构瓶颈间接学习细胞类型信息，HCE 则直接提供这类监督。因此 HCE 对原本缺少全局表征压力的 MLM 帮助更大。

#### 8.2 哪些生物信号可学？

检测任务明显比表达量定量容易：基因家族中位 ROC-AUC 为 0.86（WCED）和 0.88（MLM），但能在定量上优于验证集均值基线的基因少于 2%（`paper.md:55-64`）。

控制稀疏性后，身份相关基因更容易成为 winner；细胞周期和解离反应基因不富集。论文把这解释为“上下文可预测性”：如果某基因表达量与稳定的整体转录程序共变，模型可以从其余基因推断它；若它主要受瞬时、空间、时间或实验过程驱动，单个静态快照可能缺少必要信息。

#### 8.3 下游表现

- 十个 scEval 数据集上，MLM MULTITASK / WCED MULTITASK 的加权整合分数为 0.747 / 0.748，scGPT 为 0.730（`paper.md:104-110`）。
- 九个 scEval 数据集微调后，相比冻结表征分类器平均 F1 增加 0.028-0.039（`paper.md:116-125`）。
- Sci-Plex3 药物机制任务中，WCED concat CLS 的 AUC 为 0.871，Avg Bio 为 0.355；AUC 接近更大模型，Avg Bio 在报告比较中最高（`paper.md:130-147`）。

这些结果支持“WCED 表征更有用”，但不能推出“WCED 能准确预测任意基因表达量”。论文恰恰强调，大多数基因的精确定量仍接近简单基线。

### 9. 论文结论、代码事实与研究假设要分开

#### 论文直接报告

- WCED 在匹配实验中下游表征优于 MLM，尽管重构误差更高。
- HCE 显著改善 MLM 表征，并支持多粒度细胞类型预测。
- 上下文可预测性比基因功能类别更能解释定量可学性。

#### 代码直接验证

- WCED loss 输入固定选择 token 0，并对齐全词表/子集标签。
- HCE 数值公式与论文 Eqs. 1-3 匹配。
- 本体叶节点映射、分类头和归一化加权多任务损失均有直接源码。

#### 作者解释或待检验假设

- WCED 的提升来自最大信息瓶颈，而不是其他优化差异。
- 静态转录组中的“不可学边界”可能来自数据生成过程本身。
- 时间、空间或表观组学可能让这条边界变得可穿透。

这些假设适合生成后续实验，但不应写成已经由代码或当前基准证明的事实。

### 10. 复现状态与缺口

代码快照固定在 commit `8b5694a922be7ccb1d3ee5c280c4dcef2eb95df9`，核心 WCED、HCE、本体和多任务损失实现可直接追踪。复现完整论文仍有明确缺口：

- **Not found**：对应论文两个 multitask checkpoint 的精确 Hydra 配置；
- **Not found**：把发布权重与论文表格绑定的 checkpoint 哈希；
- **Not found**：一条从数据到全部图表的端到端命令；
- **Not found**：完整的贪心根到叶本体遍历实现；
- 本地缺少论文 Figure 4 图像；Supplementary Figure 8 本地图只含 UMAP，没有 caption 所说的 marker dot plot。

本次分析没有下载模型、运行训练或重算基准。CodeGraph 和证据索引只用于导航；方法判断来自论文原文、七张本地图像和直接源码行。

### 11. 最值得记住的三点

1. **训练损失低不等于细胞表征好。** 目标函数必须约束下游实际使用的向量。
2. **WCED 的关键是信息路径。** 全词表监督必须通过单个 CLS 瓶颈，而不是分散在 token 表征中。
3. **HCE 的关键是归一化叶分布。** 粗标签的概率是后代叶概率质量，而不是一组互不归一的独立分数。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## BMFM-RNA Summary

### Problem

Transcriptomic foundation models often use masked language modeling (MLM), which can reach low reconstruction loss without putting a global cell state into the pooled embedding. BMFM-RNA asks whether a stronger information bottleneck produces more useful cell representations, and whether Cell Ontology supervision can make labels at multiple granularities consistent (`paper.md:14,22,28`).

### Proposed Method

Whole-cell expression decoding (WCED) reconstructs the full gene vocabulary from one CLS embedding. It has separate binary detection and nonzero-expression quantification objectives. A hierarchical cross-entropy (HCE) head predicts leaf-node Cell Ontology logits; probabilities for a coarse label are the normalized sum of descendant-leaf probabilities (`paper.md:17-22,183-234`). These objectives are composed with metadata heads in a weighted multitask loss.

The direct code snapshot supports this design: WCED output/label extraction is implemented in `training/losses/sources.py:159-294`, configurable field and classification decoders in `models/predictive/layers.py:520-624`, ontology leaf/descendant lookup in `datasets/label_ontology/ontology.py:11-96`, HCE numerics and dispatch in `training/metrics/metric_functions.py:172-219` and `training/losses/objectives.py:545-619`, and normalized task aggregation in `training/losses/task.py:74-152` plus `training/losses/utils.py:76-105`.

### Main Findings

- In matched 1% pretraining, MLM has lower rescaled MAE (about 0.65 versus 0.90 for WCED), yet WCED improves F1 by 0.128, Avg Bio by 0.149, and Avg Batch by 0.064 (`paper.md:40-49`).
- Gene-level analysis finds detection easier than quantitative expression: median family ROC-AUC is 0.86 for WCED and 0.88 for MLM, while fewer than 2% of genes beat a null quantitative predictor (`paper.md:52-64`).
- HCE closes the MLM/WCED representation gap: MLM gains +0.129 F1 and +0.222 Avg Bio, while WCED F1 remains essentially unchanged (`paper.md:90-96`).
- Across ten scEval batch-integration datasets, MLM MULTITASK and WCED MULTITASK score 0.747 and 0.748 versus scGPT 0.730 (`paper.md:104-110`).
- WCED concatenated CLS embeddings reach MoA AUC 0.871 and Avg Bio 0.355 on Sci-Plex3, close to much larger foundation models and highest in the reported Avg Bio comparison (`paper.md:130-147`).

### Evaluation

The study uses CELLxGENE pretraining, CZ CELLxGENE and scEval benchmarks, held-out-batch fine-tuning, and Sci-Plex3 drug mechanism-of-action classification. Reported models use a 384-dimensional hidden size, 12 layers, 10% CELLxGENE data (about 6.2M cells), and HCE plus expression objectives (`paper.md:265,286-321`). The local image set visually supports the architecture, gene-level learnability plots, ontology roll-up, fine-tuning bars, MoA curves/UMAPs, Alzheimer UMAP, and software architecture; the paper Figure 4 image is missing locally (`figure_analysis.md`).

### Reproducibility

**Rating: 3/5 (core implementation available; manuscript-run packaging incomplete).** The paper links the open-source repository and the snapshot is pinned to commit `8b5694a922be7ccb1d3ee5c280c4dcef2eb95df9`. Core WCED, HCE, ontology, decoder, and weighted-loss behavior matches direct source. However, the exact Hydra configurations and checkpoint hashes for the reported MLM/WCED multitask runs were not identified, and no single command reproducing every paper table/figure was found in the bounded search. Paper Figure 4 is absent from local image assets, and Supplementary Figure 8's local file does not include the captioned marker dot plot. No training, dataset download, or checkpoint execution was performed in this analysis.

### Limitations

The gene universe is human protein-coding genes and evaluation is scRNA-seq focused. HCE depends on Cell Ontology-compatible labels and its top-down interpretation is heuristic on a DAG with shared descendants. Most quantitative gene-level prediction remains near a null baseline; WCED improves representations but does not remove this information limit (`paper.md:159-171`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
