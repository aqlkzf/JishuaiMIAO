---
layout: default
permalink: /paper-atlas/genecompass-6f89ff7c/
title: "GeneCompass"
nav: false
wide: true
description: "传统单细胞基础模型通常只使用单一物种的数据，并把基因表示成相对排名或表达分箱，因此难以学习跨物种、跨细胞类型的普适基因调控规律。GeneCompass 的目标是把人和小鼠的单细胞转录组放入同一个表示空间，同时把已有的调控知识注入预训练过程。 论文称 scCompass-126M 收集了超过 1.2 亿个细胞，质控后使用 101,768,420 个细胞。"
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
      <span>Cell Research · 2024</span>
    </div>
    <h1>GeneCompass</h1>
    <p>GeneCompass: deciphering universal gene regulatory mechanisms with a knowledge-informed cross-species foundation model</p>
    <div class="paper-detail__links"><a class="paper-detail__doi" href="https://doi.org/10.1038/s41422-024-01034-y" target="_blank" rel="noopener noreferrer" aria-label="Open DOI for GeneCompass">Open paper <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a><a class="paper-detail__code" href="https://github.com/xCompass-AI/GeneCompass" target="_blank" rel="noopener noreferrer" aria-label="Open code for GeneCompass">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## GeneCompass 方法说明（基于论文与代码）

### 1. 要解决的问题

传统单细胞基础模型通常只使用单一物种的数据，并把基因表示成相对排名或表达分箱，因此难以学习跨物种、跨细胞类型的普适基因调控规律。GeneCompass 的目标是把人和小鼠的单细胞转录组放入同一个表示空间，同时把已有的调控知识注入预训练过程。

论文称 scCompass-126M 收集了超过 1.2 亿个细胞，质控后使用 101,768,420 个细胞（`paper.md:199-210`）。代码仓库没有包含这些细胞矩阵、补充表格或预训练检查点，因此下面把“论文声称”“代码验证”和“解释性推断”分开说明。

### 2. 方法核心与创新点

GeneCompass 是一个 BERT 风格的双向 Transformer。每个细胞最多取按表达量排序的 2048 个基因；每个基因输入同时包含：

- 基因 ID；
- 归一化后的绝对表达值；
- 启动子序列嵌入；
- 基因共表达嵌入；
- 基因家族嵌入；
- PECA/GRN 调控嵌入；
- 人/小鼠物种信息和基因排名位置。

模型用 masked language modeling 同时预测被遮挡基因的 ID 和表达值。这样得到的最后一层基因向量可以用于同源性、GRN、扰动和药物任务，CLS 向量可以用于细胞类型分类。Fig. 1 的图像直接显示了四类先验、CLS、掩码位置以及 ID/表达双解码器。

### 3. 计算流程

```text
原始计数矩阵
  -> 细胞/基因质控与核心基因过滤
  -> 基因中值归一化，再做 log2(1+x)
  -> 对非零基因按表达量降序排列
  -> 截断或补零到 2048 个位置，并记录物种
  -> 拼接 ID、表达值和四类先验嵌入
  -> 线性投影、层归一化、GELU、位置嵌入（可加物种 CLS）
  -> 12 层 Transformer 自注意力编码
  -> ID 解码器 + 表达值解码器
  -> 基因上下文向量 / CLS 细胞向量
  -> 下游微调或零样本分析
```

代码中的 `preprocess.py:120-213` 实现了非零基因排序、2048 截断/补零和物种字段写入。论文给出的质控阈值包括：表达基因少于 200、样本少于 4 个细胞、蛋白编码或 miRNA 基因少于 7 个、线粒体比例超过 15%，以及样本内表达基因数超出均值三倍标准差（`paper.md:202-205`）。代码有相应的过滤辅助函数，但没有完整的数据获取流程。

### 4. 输入嵌入与跨物种处理

`knowledge_embeddings.py:62-127,183-214` 先查找普通基因 embedding，再追加表达值和四个先验向量，最后用投影网络压回 768 维。`utils.py:34-110` 按 ENSG/ENSMUSG ID 将先验矩阵对齐到 token 字典。若 `species=1`（小鼠），代码先通过 `homologous_index` 把 ID 映射到同源的人类对齐行，再索引先验矩阵（`knowledge_embeddings.py:146-149,192-214`）。模型随后加入 token-type 和绝对位置 embedding；配置启用 `use_cls_token=True` 时，`modeling_bert.py:361-410` 会在序列前放入物种索引的 CLS 向量。

### 5. Transformer 与预训练目标

主要配置为 12 层、12 个注意力头、隐藏维度 768、中间层 3072、GELU、0.02 dropout、最大位置 2048、LayerNorm epsilon (10^{-12})（`pretrain_genecompass_w_human_mouse_base.py:70-95`）。

论文定义被遮挡集合 (mathcal M) 上的表达均方误差：

\[
\mathscr L_{\exp}=\frac{1}{|\mathcal M|}\sum_{j\in\mathcal M}(\widetilde v_j-v_j)^2
\]

以及 ID 交叉熵：

\[
\mathscr L_{ID}=-\frac{1}{|\mathcal M|}\sum_{j\in\mathcal M}p(t_j)\log q(t_j)
\]

（`paper.md:223-235`）。论文展示的总损失公式在第二项再次写成 (\mathscr L_{ID})，与前文“表达值 MSE”的文字不一致。代码提供两个独立预测头，并在有效掩码位置计算：

\[
L_{code}=0.2L_{ID}+0.8L_{\exp}
\]

（`modeling_bert.py:788-805`）。因此这里以代码中的实际权重为实现事实，同时保留论文公式存在歧义这一缺口。

`data_collator.py:42-80` 对输入做随机掩码：80% 替换为 mask token、10% 替换为随机 token、10% 保持原 token；被掩码的表达值置为 -1，未参与损失的位置标签设为 -100。论文规定掩码率为 15%，但当前文件从 Transformers collator 参数继承概率，未在此处硬编码 0.15。

### 6. 下游任务

1. **细胞类型注释**：论文在 CLS 细胞向量上增加全连接分类层，使用交叉熵；代码的 `BertForSequenceClassification` 实现了 dropout + linear 分类器（`modeling_bert.py:949-1042`）。
2. **跨物种注释**：论文把 GeneCompass 基因向量输入 CAME 异质图，使用细胞/基因节点更新和 label smoothing（`paper.md:310-331`）。本仓库没有找到 CAME 的本地训练实现，因此该部分代码证据为 `Not found`。
3. **GRN 推断**：论文使用基因向量余弦相似度并报告阈值 0.4，再交给 DeepSEM（`paper.md:334-343`）。仓库的 `EmbeddingGenerator.py:91-123` 会跨细胞平均隐藏向量，计算两两余弦值，并按排序保留 500,000 条边；`EmbeddingEvaluator.py:22-74` 调用 DeepSEM 并计算 AUPRC。这个 rank 截断与论文阈值描述不同。
4. **扰动预测**：论文通过删除/组合删除基因比较嵌入偏移，Fig. 5 显示 GeneCompass 相对 GEARS 的改进。仓库有 GEARS 派生模型，读取预先计算的 GeneCompass 张量并结合共表达/GO 图，但训练数据和完整命令不在仓库。
5. **剂量反应、基因表达和剂量敏感性**：论文分别把 GeneCompass 向量接入 CPA、DeepCE 或分类模型。仓库主要提供包装器和外部路径，不能在当前 checkout 中独立重跑。
6. **细胞命运**：Fig. 6 展示基于扰动嵌入偏移筛选 NR2F1/2、WT1、TCF21、GATA4 等候选因子，并进一步做实验验证。图像支持“模型提出候选、实验验证”的流程，但不等于模型单独证明了因果关系。

### 7. 结果、局限与证据范围

Fig. 2 直接显示同源基因的余弦相似度分布右移；Fig. 3 显示预训练数据规模增加时多数注释指标上升，GeneCompass 在展示的人/鼠数据集上通常优于基线，但跨物种数据对并非全部提升；Fig. 4-5 显示 GRN、剂量反应、表达预测、剂量敏感性和扰动任务的总体优势；Fig. 6 给出细胞命运候选与实验图像。

已经由代码逐行验证的内容包括：模型结构、先验拼接、同源映射、2048 输入、掩码行为、双解码器和损失权重。尚未找到的内容包括：scCompass-126M 数据、先验二进制文件、token/checkpoint、补充图表、CAME 训练代码以及完整下游数据。仓库示例还含有 `[local path omitted]`、`/home/wangx/...` 等作者环境绝对路径，复现需要重新构建数据和运行环境。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## GeneCompass Summary

### Problem

Most single-cell foundation models learn from one species and encode either gene ranks or binned expression, limiting cross-species regulatory interpretation. GeneCompass addresses this by pretraining a shared human/mouse model that combines transcriptomic context with curated regulatory priors.

### Proposed Method

GeneCompass is a 12-layer, 12-head, 768-dimensional BERT-style encoder trained on the scCompass-126M corpus. Each cell is represented by up to 2048 genes ranked by normalized expression, with absolute values, species information, and four prior channels: promoter sequence, gene regulatory network, gene family, and co-expression. A masked-language objective reconstructs both masked gene IDs and expression values. The paper describes a joint CE+MSE objective; the checked-in code uses `0.2 * ID_CE + 0.8 * expression_MSE` (`modeling_bert.py:794-805`).

### Evaluation and Results

The paper evaluates contextual gene embeddings and CLS cell embeddings across homology analysis, in silico deletion, single- and cross-species cell-type annotation, GRN inference, drug-dose response, gene-expression profiling, dosage sensitivity, perturbation prediction, and cell-fate regulator discovery. Figures show that GeneCompass generally improves annotation macro-F1/accuracy as corpus size grows, outperforms no-pretraining/TOSICA/Geneformer on the displayed human and mouse datasets, improves many CAME cross-species pairs, and yields favorable GRN AUPRC, dose-response R², expression RMSE, dosage-sensitivity AUC, and GEARS perturbation metrics. The cell-fate analysis nominates factors including NR2F1/2, WT1, TCF21, and GATA4, followed by experimental gonadal differentiation validation. These are paper/figure claims; raw result tables and supplementary figures are not present locally.

### Reproducibility

Code-paper fidelity is **medium**. The repository directly verifies architecture, prior embedding assembly, species homology remapping, 2048-token preprocessing, masking mechanics, dual decoder heads, and model-level loss weighting. It does not contain the 101M-cell corpus, prior embedding binaries, token/checkpoint files, supplementary datasets, or a self-contained CAME implementation. The GRN generator uses rank-based top-500,000 cosine edges (`EmbeddingGenerator.py:108-123`), whereas the paper describes optimizing a scalar threshold reported as 0.4 (`paper.md:337-343`). Downstream examples include external absolute paths and shell wrappers around DeepSEM/CPA/DeepCE, so a full end-to-end reproduction requires reconstructing the authors' data and runtime environment.

### Limitations and Interpretation

The model's cross-species representations are evidence of shared statistical structure, not proof that every learned edge is causal. Several reported gains are task- and dataset-dependent, and Fig. 3 visibly includes cross-species pairs with little or negative change. The paper's displayed combined-loss equation repeats the ID term, so the implementation is the authoritative source for the actual weighting. Supplementary evidence, raw figure data, and wet-lab details remain outside this workspace.

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
