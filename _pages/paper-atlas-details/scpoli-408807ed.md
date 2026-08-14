---
layout: default
permalink: /paper-atlas/scpoli-408807ed/
title: "scPoli"
nav: false
wide: true
description: "人口规模的单细胞图谱把多个研究、样本、个体和技术条件放在一起。数据整合既要去除批次差异，又要保留细胞类型和状态等生物信号；同时，建好的参考图谱还应能快速接收新查询数据。传统 CVAE 使用随条件数量增长的 one-hot 条件向量，难以解释每个样本的作用；一些参考映射方法在加入新数据时必须重新训练或共享参考细胞。"
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
      <span>Integration &amp; Multi-modal</span>
      <span>Nature Methods · 2023</span>
    </div>
    <h1>scPoli</h1>
    <p>Population-level integration of single-cell datasets enables multi-scale analysis across samples</p>
    <div class="paper-detail__links"><a class="paper-detail__code" href="https://github.com/theislab/scPoli_reproduce" target="_blank" rel="noopener noreferrer" aria-label="Open code for scPoli">Code <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a></div>
  </header>

  <div class="paper-detail__tabs" role="tablist" aria-label="Paper notes language">
    <button class="is-active" type="button" role="tab" id="paper-detail-tab-zh" aria-selected="true" aria-controls="paper-detail-panel-zh" data-detail-tab="zh">中文方法解读</button>
    <button type="button" role="tab" id="paper-detail-tab-en" aria-selected="false" aria-controls="paper-detail-panel-en" tabindex="-1" data-detail-tab="en">English Summary</button>
  </div>

<article class="paper-detail__panel" id="paper-detail-panel-zh" role="tabpanel" aria-labelledby="paper-detail-tab-zh" tabindex="0" data-detail-panel="zh" lang="zh-CN" markdown="1">

## scPoli 方法详解

### 要解决的问题

人口规模的单细胞图谱把多个研究、样本、个体和技术条件放在一起。数据整合既要去除批次差异，又要保留细胞类型和状态等生物信号；同时，建好的参考图谱还应能快速接收新查询数据。传统 CVAE 使用随条件数量增长的 one-hot 条件向量，难以解释每个样本的作用；一些参考映射方法在加入新数据时必须重新训练或共享参考细胞（`paper.md:30-39`）。

### 核心思想

scPoli 是半监督条件变分自编码器（CVAE）加原型网络：

1. 用固定维度、可学习的条件嵌入表示样本/研究/批次，而不是 one-hot 向量。
2. 在潜空间中为每个细胞类型保存一个原型（该类型细胞潜向量的平均值）。
3. 用原型损失把有标签细胞拉向对应原型，因此可以用最近原型进行标签转移。
4. 用细胞到最近原型的距离作为未知细胞的“不确定性”代理（`paper.md:48-68,290-415`）。

### 输入、输出与计算流程

输入是表达/计数向量 **x**、条件标签 **c**（样本、研究或其他批次协变量）和可选的细胞标签 **a**。输出包括细胞潜表示 **z**、条件嵌入 **s**、细胞类型原型 **p**、重建表达和预测标签（符号定义见 `paper.md:240-244`）。

```text
参考细胞 (x, c, a)
       |
       +--> 查找条件嵌入 s(c)，与 x 拼接
       |
       +--> CVAE 编码器 q(z|x,c) --> z --> 解码器 p(x|z,c)
       |                         |
       |                         +--> 按标签计算原型 p_k = mean(z)
       |                         +--> CVAE 损失 + eta * 原型损失
       |
       +--> 保存网络权重、条件嵌入和原型
                |
查询细胞 (x_q, c_q)
       |
       +--> 冻结参考编码器/解码器，只学习新的查询条件嵌入
       +--> 在潜空间找最近原型 --> 标签和距离不确定性
```

CVAE 的生成分布为

$$p_\theta(\mathbf{x}|\mathbf{c})=\int p_\theta(\mathbf{x}|\mathbf{z},\mathbf{c})p_\theta(\mathbf{z}|\mathbf{c})\,d\mathbf{z},$$

训练使用重建负对数似然加 KL 项的 ELBO（`paper.md:246-287`）。计数数据使用负二项似然；scATAC-seq 片段计数使用 Poisson 似然。

### 原型、标签转移和不确定性

标签为 (k) 的原型是

$$\mathbf{p}_k=\frac{1}{|\mathscr{K}(k)|}\sum_{i\in\mathscr{K}(k)}\mathbf{z}_i.$$

有标签细胞的原型损失为细胞到其类别原型的距离平均值；论文使用 Minkowski 距离（(p=2) 时是欧氏距离），也支持粗粒度和细粒度多组标签。未标注细胞先用 Louvain 聚类形成未标注原型，但这些原型不参与原型损失（`paper.md:304-374`）。

查询细胞的预测标签和不确定性分别是

$$a_i^{(\mathrm{pred})}=\arg\min_k d(\mathbf{z}_i,\mathbf{p}_k),\qquad u_i=\min_k d(\mathbf{z}_i,\mathbf{p}_k).$$

论文没有固定的全局阈值，而是观察每个数据集的不确定性分布后选择分位数；因此阈值需要人工检查，不能直接跨数据集复用（`paper.md:390-415,222`）。

### 训练和评估

参考构建先只优化 CVAE，再初始化原型并优化

$$\mathcal{L}_{\mathrm{CVAE}}+\eta\mathcal{L}_{\mathrm{prototype}}.$$

查询映射冻结参考网络，只为查询条件增加嵌入；若查询无标签，只优化 CVAE 项。论文默认使用 Adam、学习率 0.001，预训练/微调 epoch 比例为 0.9（`paper.md:377-388`）。评估包括 scIB 的生物保留和批次校正指标，以及 weighted/macro F1 标签转移指标（`paper.md:472-511`）。

论文在六个数据集上比较 scVI、scANVI、MARS、Seurat v3、Symphony 和线性 SVM；scPoli 的平均整合分数比 scANVI 高 5.06%，原型损失是生物保留改进的主要来源（`paper.md:71-94`）。HLCA 核心数据含 584,884 个细胞、166 个样本；PBMC 图谱含约 780 万个细胞、2,375 个样本（`paper.md:97-123,517-526`）。

### 如何理解样本嵌入

样本嵌入可以在 PCA 空间中按研究、实验、疾病或其他元数据着色，从而帮助发现批次来源和跨样本的表达模式。PBMC 结果中，PC1 与数据集、测序 assay、疾病分别有 0.97、0.86、0.59 的 adjusted (R^2)（`paper.md:184-201`）。这不是保证每个轴都有生物学含义：复杂数据中嵌入可能主要反映技术差异，论文建议结合数据集背景谨慎解释（`paper.md:204-225`）。

### 代码可复现性边界

`scPoli_reproduce` 的 `revision/stability/stability.py` 明确执行参考模型构建、保存、`load_query_data` 查询手术、分类、`get_latent` 和 scIB 指标计算（`stability.py:90-229`）；`revision/computational/main.py` 提供 100 epoch/80 预训练的规模计时驱动（`main.py:7-34`）。但仓库 README 说明核心实现已迁移到外部 scArches，当前快照不包含 CVAE 网络、条件嵌入、原型更新或不确定性函数的源码（`README.rst:4-7,32-34`）。因此这些内部行为在本文档中标为 **External/Not found**，不能把复现实验脚本误当成完整模型实现。

</article>
<article class="paper-detail__panel" id="paper-detail-panel-en" role="tabpanel" aria-labelledby="paper-detail-tab-en" tabindex="0" data-detail-panel="en" lang="en" markdown="1" hidden>

## scPoli at a glance

### Problem

Population-scale single-cell atlases mix samples, studies and technical conditions. Standard conditional generative models use one-hot condition vectors that grow with the number of conditions and are difficult to interpret; reference methods often require retraining or sharing the reference cells for annotation (`paper.md:30-39`).

### Method

scPoli is a semi-supervised conditional variational autoencoder with two additions: fixed-dimensional learnable condition embeddings and latent-space cell-type prototypes. The embeddings provide sample/covariate representations, while prototypes add a supervised distance loss, nearest-prototype label transfer and a distance-based uncertainty score (`paper.md:48-68,234-415`). Reference training stores the encoder/decoder, condition embeddings and prototypes; query mapping freezes reference weights and learns only new query embeddings (`paper.md:377-388`).

### Evidence and evaluation

Across six benchmark datasets, scPoli reports a 5.06% advantage over scANVI in mean integration score and attributes biological-conservation gains to prototype loss. Weighted and macro F1 scores evaluate query classification, with scPoli leading among methods that jointly integrate and classify (`paper.md:71-94`). On the HLCA core (584,884 cells, 166 samples), scPoli preserves biology at similar batch correction to scANVI and yields interpretable sample embeddings; query mapping reports 75% accuracy in the healthy HLCA example (`paper.md:97-123,517-520`). The PBMC atlas scales to 7.8 million cells from 2,375 samples, with sample PC1 associated with dataset (adjusted (R^2=0.97)), assay ((0.86)) and disease ((0.59)) (`paper.md:184-201,523-526`). The method also uses Poisson likelihood for scATAC-seq and supports cross-species integration (`paper.md:454-458,541-550`).

### Reproducibility

Rating: **3/5 (orchestration reproducible; core implementation external)**. The GitHub snapshot is pinned to commit `ba31a7d2ffc9b26dfd56c86ef9adf66e44b2f737` and contains benchmark/revision scripts. Direct code verifies model construction, reference/query training, model surgery, latent extraction, classification reports and scIB metric selection (`revision/stability/stability.py:90-229`; `revision/computational/main.py:7-34`). However, `scPoli_reproduce` explicitly says the core code moved to scArches and is not maintained (`README.rst:4-7,32-34`), so CVAE internals, prototype updates and uncertainty code are **External/Not found** locally. Cluster-local data paths and notebooks make the scripts non-portable without environment/data reconstruction.

### Limitations

The output is a lower-dimensional integrated object rather than corrected counts. Performance depends on diverse reference samples and harmonized cell labels. Uncertainty has no universal threshold and must be inspected/thresholded per dataset; sample embeddings can reflect technical rather than biological variation (`paper.md:204-225`).

</article>
</section>

<script defer src="{{ '/assets/js/paper-atlas-detail.js' | relative_url | bust_file_cache }}"></script>
